from pydantic import BaseModel
from typing import List
from fastapi import APIRouter

from models.db_model import BangumiData, BangumiData_Pydantic, BangumiTags_Pydantic, BangumiTags
from models.request_model import IdRequest, ScoreRequest
from models.response_model import BangumiDataResponse
from services.request_process import process_id, process_score, process_bangumi

router = APIRouter()

# 查询Bangumi数据和相关的标签
@router.get("/bangumi/{bangumi_id}", response_model=BangumiDataResponse)
async def get_bangumi_data(bangumi_id: int):
    return await process_bangumi(bangumi_id)