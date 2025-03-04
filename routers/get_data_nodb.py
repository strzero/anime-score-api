from typing import List
from fastapi import APIRouter

from models.request_model import IdRequest, TitleRequest
from services.apis_to_data import get_four_id, get_four_score
from utils.logger import logger
router = APIRouter()

@router.post("/get_id_nodb")
async def get_id_nodb(titles: List[TitleRequest]):
    logger.info(f"尝试从网页获取ID数据： {[title.title for title in titles]}")
    results = []
    for title in titles:
        results.append(await get_four_id(title))
    return results

@router.post("/get_score_nodb")
async def get_score_nodb(ids: List[IdRequest]):
    logger.info(f"尝试从网页获取评分数据： {[id_req.title for id_req in ids]}")
    results = []
    for id_req in ids:
        results.append(await get_four_score(id_req))
    return results