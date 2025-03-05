from tortoise.exceptions import DoesNotExist

from models.request_model import IdRequest, ScoreRequest
from services.check_database import check_database_id
from utils.logger import logger


async def process_id(request: IdRequest):
    try:
        db_res = await check_database_id(request)
        return db_res
    except DoesNotExist:

        return "检索中"


async def process_score(request: ScoreRequest):
    return None