from sympy.printing.codeprinter import requires
from tortoise.exceptions import DoesNotExist

from models.request_model import IdRequest, ScoreRequest
from routers.id_task_queue import add_id_task
from routers.score_task_queue import add_score_task
from services.check_database import check_database_id, check_database_score
from utils.logger import logger


async def process_id(request: IdRequest):
    try:
        db_res = await check_database_id(request)
        return db_res
    except DoesNotExist:
        await add_id_task(request)
        return 901


async def process_score(request: ScoreRequest):
    try:
        db_res = await check_database_score(request)
        return db_res
    except DoesNotExist:
        await add_score_task(request)
        return 901