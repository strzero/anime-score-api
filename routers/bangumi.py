import asyncio
from typing import List

from fastapi import APIRouter

from models.db_model import BangumiData, BangumiData_Pydantic
from models.request_model import IdRequest, ScoreRequest
from services.process_request import process_id, process_score

router = APIRouter()

@router.get("/bangumi", response_model=BangumiData_Pydantic)
async def bangumi_single(id):
    try:
        return await BangumiData.get(id=id)
    except:
        return "NoFound"