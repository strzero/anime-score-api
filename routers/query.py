import asyncio
import string
from typing import List, Union, Dict

from fastapi import APIRouter
from uuid import UUID

from models.request_model import IdRequest, ScoreRequest, QueryRequest
from models.response_model import IdResponse, ScoreResponse, QueryResponse
from services.request_process import process_id, process_score, TaskModel, process_query

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

@router.post("/query")
async def query(requests: List[QueryRequest], response_model=QueryResponse):
    tasks = []
    for request in requests:
        tasks.append(process_query(request))

    results = await asyncio.gather(*tasks)
    return {request.bangumi_id: result for request, result in zip(requests, results)}

@router.get("/query/{bangumi_id}", response_model=QueryResponse)
async def query_single(bangumi_id: int):
    return await process_query(QueryRequest(bangumi_id=bangumi_id))