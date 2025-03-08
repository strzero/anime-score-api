from pydantic import BaseModel
from typing import List
from fastapi import APIRouter

from models.db_model import BangumiData, BangumiData_Pydantic, BangumiTags_Pydantic, BangumiTags
from models.request_model import IdRequest, ScoreRequest
from models.response_model import BangumiDataResponse
from services.request_process import process_id, process_score

router = APIRouter()

# 查询Bangumi数据和相关的标签
@router.get("/bangumi/{bangumi_id}", response_model=BangumiDataResponse)
async def get_bangumi_data(bangumi_id: int):
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