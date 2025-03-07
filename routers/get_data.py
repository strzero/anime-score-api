import asyncio
import string
from typing import List, Union, Dict

from fastapi import APIRouter
from uuid import UUID

from models.request_model import IdRequest, ScoreRequest
from models.response_model import IdResponse, ScoreResponse
from services.request_process import process_id, process_score, TaskModel

router = APIRouter()

@router.post("/get_id", response_model=Dict[int, IdResponse])
async def get_id(requests: List[IdRequest]):
    tasks = []
    for request in requests:
        tasks.append(process_id(request))

    results = await asyncio.gather(*tasks)
    return {request.bangumi_id: result for request, result in zip(requests, results)}

@router.post("/get_score", response_model=Dict[int, ScoreResponse])
async def get_score(requests: List[ScoreRequest]):
    tasks = []
    for request in requests:
        tasks.append(process_score(request))

    results = await asyncio.gather(*tasks)
    return {request.bangumi_id: result for request, result in zip(requests, results)}