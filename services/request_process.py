import asyncio
import uuid
from typing import Any

from pydantic import BaseModel
from tortoise.exceptions import DoesNotExist

from models.db_model import IdLink, Score
from models.request_model import IdRequest, ScoreRequest
from models.response_model import ScoreResponse
from routers.id_task_queue import add_id_task
from routers.score_task_queue import add_score_task
from services.response_wrap import warp_id_wait, warp_id_success_db, warp_score_success_db, warp_score_wait
from services.task_scheduler import task_results

class TaskModel(BaseModel):
    def __init__(self, task_id, **data: Any):
        super().__init__(**data)
        task_id: int

async def process_id(request: IdRequest):
    try:
        db_res = await IdLink.get(bangumi_id=request.bangumi_id)
        return warp_id_success_db(db_res, request.title)
    except DoesNotExist:
        task_uuid = await add_id_task(request)

        for i in range(40):
            if task_uuid in task_results:
                return task_results[task_uuid]
            await asyncio.sleep(0.5)

        return warp_id_wait(task_uuid)

async def process_score(request: ScoreRequest):
    try:
        db_res = await Score.get(bangumi_id=request.bangumi_id)
        return warp_score_success_db(db_res, request.title)
    except DoesNotExist:
        task_uuid = await add_score_task(request)

        for i in range(40):
            if task_uuid in task_results:
                return task_results[task_uuid]
            await asyncio.sleep(0.5)

        return warp_score_wait(task_uuid)
