import asyncio
import uuid

from pydantic import BaseModel
from tortoise.exceptions import DoesNotExist

from models.request_model import IdRequest, ScoreRequest
from routers.id_task_queue import add_id_task
from routers.score_task_queue import add_score_task
from services.check_database import check_database_id, check_database_score
from services.task_scheduler import task_results

class TaskModel(BaseModel):
    def __init__(self, task_id):
        task_id: int

async def process_id(request: IdRequest):
    try:
        db_res = await check_database_id(request)
        return db_res
    except DoesNotExist:
        task_uuid = await add_id_task(request)

        for i in range(40):
            if task_uuid in task_results:
                return task_results[task_uuid]
            await asyncio.sleep(0.5)

        return TaskModel(task_id=task_uuid)

async def process_score(request: ScoreRequest):
    try:
        db_res = await check_database_score(request)
        return db_res
    except DoesNotExist:
        task_uuid = await add_score_task(request)

        for i in range(40):
            if task_uuid in task_results:
                return task_results[task_uuid]
            await asyncio.sleep(0.5)

        return TaskModel(task_id=task_uuid)
