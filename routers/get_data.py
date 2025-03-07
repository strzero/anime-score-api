import asyncio
import string
from typing import List, Union, Dict

from fastapi import APIRouter
from uuid import UUID

from models.db_model import IdLink_Pydantic, IdLinkIn_Pydantic, Score_Pydantic
from models.request_model import IdRequest, ScoreRequest
from models.response_model import IdResponse
from services.process_request import process_id, process_score, TaskModel

router = APIRouter()

@router.post("/get_id", response_model=Dict[int, IdResponse])
async def get_id(requests: List[IdRequest]):
    tasks = []
    for request in requests:
        tasks.append(process_id(request))

    results = await asyncio.gather(*tasks)
    return {request.bangumi_id: result for request, result in zip(requests, results)}

@router.post("/get_score", response_model=Dict[int, Union[Score_Pydantic, TaskModel]])
async def get_id(requests: List[ScoreRequest]):
    tasks = []
    for request in requests:
        tasks.append(process_score(request))

    results = await asyncio.gather(*tasks)
    return {request.bangumi_id: result for request, result in zip(requests, results)}