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
async def confirm(bangumi_id: int):
    try:
        await IdLink.filter(bangumi_id=bangumi_id).update(
            verification_count=F('verification_count') + 1
        )
        return NormalResponse(status=200)
    except Exception as e:
        logger.error(f"confirm 错误 {bangumi_id}: {e}", exc_info=settings.logger_exc_info)
        return NormalResponse(status=500)

@router.post("/revoke_confirm/{bangumi_id}")
async def revoke_confirm(bangumi_id: int):
    try:
        await IdLink.filter(bangumi_id=bangumi_id).update(
            verification_count=0
        )
        return NormalResponse(status=200)
    except Exception as e:
        logger.error(f"confirm 错误 {bangumi_id}: {e}", exc_info=settings.logger_exc_info)
        return NormalResponse(status=500)


@router.post("/update/{bangumi_id}")
async def update_id_link(bangumi_id: int, anikore_id: str = None, myanimelist_id: str = None,
                         anilist_id: str = None, filmarks_id: str = None):
    try:
        # 先收集更新的字段
        update_fields = {}
        if anikore_id is not None:
            update_fields['anikore_id'] = anikore_id
        if myanimelist_id is not None:
            update_fields['myanimelist_id'] = myanimelist_id
        if anilist_id is not None:
            update_fields['anilist_id'] = anilist_id
        if filmarks_id is not None:
            update_fields['filmarks_id'] = filmarks_id

        # 如果字段为空，直接返回 400
        if any(value == "NoFound" for value in update_fields.values()):
            return NormalResponse(status=400)

        # 执行更新操作
        if update_fields:
            await IdLink.filter(bangumi_id=bangumi_id).update(
                **update_fields, user_add=1
            )

        # 获取更新后的记录
        updated_record = await IdLink.get(bangumi_id=bangumi_id)

        # 检查更新后的四个 id 是否都为 "NoFound"
        if any(getattr(updated_record, field) == "NoFound" for field in
               ['myanimelist_id', 'anilist_id', 'filmarks_id', 'anikore_id']):
            return NormalResponse(status=400)

        return NormalResponse(status=200)

    except Exception as e:
        logger.error(f"update_id_link 错误 {bangumi_id}: {e}", exc_info=settings.logger_exc_info)
        return NormalResponse(status=500)
