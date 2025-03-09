from pydantic import BaseModel
from typing import List
from fastapi import APIRouter
from tortoise.expressions import F

from config import settings
from models.db_model import IdLink, Score
from models.response_model import NormalResponse
from utils.logger import logger

router = APIRouter()

@router.post("/confirm/{bangumi_id}")
async def confirm(bangumi_id: int):
    try:
        await IdLink.filter(bangumi_id=bangumi_id).update(
            verification_count=F('verification_count') + 1
        )
        return NormalResponse(status=200)
    except Exception as e:
        logger.error(f"confirm 错误 {bangumi_id}: {e}", exc_info=settings.logger_exc_info)
        return NormalResponse(status=500, message=str(e))

@router.post("/revoke_confirm/{bangumi_id}")
async def revoke_confirm(bangumi_id: int):
    try:
        await IdLink.filter(bangumi_id=bangumi_id).update(
            verification_count=0
        )
        return NormalResponse(status=200)
    except Exception as e:
        logger.error(f"confirm 错误 {bangumi_id}: {e}", exc_info=settings.logger_exc_info)
        return NormalResponse(status=500, message=str(e))


@router.post("/update/{bangumi_id}")
async def update_id_link(bangumi_id: int = None, myanimelist_id: str = None, anilist_id: str = None,
                         filmarks_id: str = None, anikore_id: str = None):
    try:
        if myanimelist_id:
            await IdLink.filter(bangumi_id=bangumi_id).update(myanimelist_id=myanimelist_id, myanimelist_useradd=1)
        if anilist_id:
            await IdLink.filter(bangumi_id=bangumi_id).update(anilist_id=anilist_id, anilist_useradd=1)
        if filmarks_id:
            await IdLink.filter(bangumi_id=bangumi_id).update(filmarks_id=filmarks_id, filmark_useradd=1)
        if anikore_id:
            await IdLink.filter(bangumi_id=bangumi_id).update(anikore_id=anikore_id, anikore_useradd=1)

        await Score.filter(bangumi_id=bangumi_id).delete()

        return NormalResponse(status=200)

    except Exception as e:
        logger.error(f"update_id_link 错误 {bangumi_id}: {e}", exc_info=settings.logger_exc_info)
        return NormalResponse(status=500, message=str(e))
