import asyncio
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel
from tortoise.exceptions import DoesNotExist

from config import settings
from models.db_model import IdLink, Score, BangumiData, BangumiTags
from models.request_model import IdRequest, ScoreRequest, QueryRequest
from models.response_model import ScoreResponse, IdResponse, QueryResponse, BangumiDataResponse
from routers.id_task_queue import add_id_task
from routers.score_task_queue import add_score_task
from services.response_wrap import warp_id_wait, warp_id_success_db, warp_score_success_db, warp_score_wait
from services.task_scheduler import task_results
from utils.logger import logger


class TaskModel(BaseModel):
    def __init__(self, task_id, **data: Any):
        super().__init__(**data)
        task_id: int

async def process_id(request: IdRequest) -> IdResponse:
    try:
        db_res = await IdLink.get(bangumi_id=request.bangumi_id)
        return warp_id_success_db(db_res, request.title)
    except DoesNotExist:
        task_event = asyncio.Event()
        task_future = asyncio.Future()
        await add_id_task(request, task_event, task_future)
        await task_event.wait()
        return await task_future

async def process_score(request: ScoreRequest) -> ScoreResponse:
    try:
        db_res = await Score.get(bangumi_id=request.bangumi_id)
        return warp_score_success_db(db_res, request.title)
    except DoesNotExist:
        task_event = asyncio.Event()
        task_future = asyncio.Future()
        # 如果任务重复，将之前的任务id给现在
        await add_score_task(request, task_event, task_future)
        await task_event.wait()
        return await task_future

async def process_bangumi(bangumi_id: int) -> BangumiDataResponse:
    try:
        # 查询BangumiData
        bangumi_data = await BangumiData.get(id=bangumi_id)

        # 查询BangumiTags
        bangumi_tags = await BangumiTags.filter(bangumi_id=bangumi_id)

        # 提取标签名称并放入列表
        tag_names = [tag.tag for tag in bangumi_tags]

        # 将标签列表加入到响应数据中
        return BangumiDataResponse(
            status=200,
            data=bangumi_data,
            tags=tag_names
        )
    except:
        return BangumiDataResponse(
            status=404
        )

async def process_query(request: QueryRequest) -> QueryResponse:
    bangumi_id = request.bangumi_id
    try:
        in_bangumi_db = await BangumiData.exists(id=bangumi_id)
        in_id_db = await IdLink.exists(bangumi_id=bangumi_id)
        in_score_db = await Score.exists(bangumi_id=bangumi_id)
        if not in_bangumi_db:
            return QueryResponse(status=404, message="bangumi id 不存在")
        if in_bangumi_db and in_id_db and in_score_db:
            bangumi_data, id_data, score_data = await asyncio.gather(
                process_bangumi(bangumi_id),
                IdLink.get(bangumi_id=request.bangumi_id),
                Score.get(bangumi_id=request.bangumi_id)
            )
            return QueryResponse(
                status=200,
                bangumi_data=bangumi_data,
                id_data=warp_id_success_db(id_data),
                score_data=warp_score_success_db(score_data)
            )
        else:
            bangumi_data = await process_bangumi(bangumi_id)
            id_data = await process_id(IdRequest(
                title=bangumi_data.data.name,
                bangumi_id=bangumi_id
            ))
            date = bangumi_data.data.date
            current_date = datetime.now()
            date_diff = (current_date.date() - date).days
            if date_diff <= 180:
                delete_day = 7
            elif date_diff <= 365:
                delete_day = 14
            else:
                delete_day = 30
            score_data = await process_score(ScoreRequest(
                title=bangumi_data.data.name,
                bangumi_id=bangumi_id,
                myanimelist_id=id_data.myanimelist_id,
                anilist_id=id_data.anilist_id,
                filmarks_id=id_data.filmarks_id,
                anikore_id=id_data.anikore_id,
                delete_day=delete_day
            ))
            return QueryResponse(
                status=200,
                bangumi_data=bangumi_data,
                id_data=id_data,
                score_data=score_data
            )

    except Exception as e:
        logger.error(f"query 错误 {bangumi_id}: {e}", exc_info=settings.logger_exc_info)
        return QueryResponse(status=500, message=e)