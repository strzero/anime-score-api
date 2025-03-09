from fastapi import APIRouter

from models.request_model import QueryRequest
from models.response_model import NowResponse
from routers.query import query
from utils.client import client
from utils.logger import logger

router = APIRouter()

# 查询Bangumi数据和相关的标签
@router.get("/now")
async def anime_now():
    try:
        response = await client.get("https://api.bgm.tv/calendar")
        data = response.json()
        query_list = [QueryRequest(bangumi_id=item['id']) for sublist in data for item in sublist["items"]]
        return await query(query_list)
    except Exception as e:
        logger.error(e)
        return NowResponse(
            status_code=500,
            message=str(e)
        )