from fastapi import APIRouter

from models.db_model import Info
from utils.logger import logger

router = APIRouter()

@router.get("/db_time")
async def db_time():
    try:
        time = await Info.filter(variable='time').first()
        return time.value
    except Exception as e:
        logger.error(f"获取数据库时间时出错: {e}")
        return "Error"
