import asyncio
from typing import List

from fastapi import HTTPException, APIRouter
from tortoise.exceptions import DoesNotExist

from models.db_model import IdLink, IdLink_Pydantic
from models.request_model import IdRequest, ScoreRequest
from services.process_request import process_id, process_score

router = APIRouter()

@router.post("/get_id")
async def get_id(requests: List[IdRequest]):
    tasks = []
    for request in requests:
        tasks.append(process_id(request))

    return await asyncio.gather(*tasks)

@router.post("/get_score")
async def get_id(requests: List[ScoreRequest]):
    tasks = []
    for request in requests:
        tasks.append(process_score(request))
    await asyncio.gather(*tasks)

    return requests[0].title