import asyncio
from typing import List

from fastapi import APIRouter

from models.db_model import IdLink_Pydantic, IdLinkIn_Pydantic, Score_Pydantic
from models.request_model import IdRequest, ScoreRequest
from services.process_request import process_id, process_score

router = APIRouter()

@router.post("/get_id", response_model=List[IdLink_Pydantic])
async def get_id(requests: List[IdRequest]):
    tasks = []
    for request in requests:
        tasks.append(process_id(request))

    return await asyncio.gather(*tasks)

@router.post("/get_score", response_model=List[Score_Pydantic])
async def get_id(requests: List[ScoreRequest]):
    tasks = []
    for request in requests:
        tasks.append(process_score(request))

    return await asyncio.gather(*tasks)