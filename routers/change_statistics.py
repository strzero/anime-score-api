from pydantic import BaseModel
from typing import List
from fastapi import APIRouter
from tortoise.expressions import F

from config import settings
from models.db_model import IdLink
from models.response_model import NormalResponse
from utils.logger import logger

router = APIRouter()

@router.post("/confirm/{bangumi_id}")
async def get_bangumi_data(bangumi_id: int):
    try:
        await IdLink.filter(bangumi_id=bangumi_id).update(
            verification_count=F('verification_count') + 1
        )
        return NormalResponse(status=200)
    except Exception as e:
        logger.error(f"confirm 错误 {bangumi_id}: {e}", exc_info=settings.logger_exc_info)
        return NormalResponse(status=500)

