import asyncio
from datetime import datetime
from typing import List
from pydantic import BaseModel
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from models.db_model import Score
from routers.query import query
from utils.logger import logger
import aiocron

class QueryRequest(BaseModel):
    bangumi_id: int

async def renew_data():
    while(True):
        logger.info("定时检查数据是否过期...")
        now = datetime.utcnow()
        
        expired_scores = await Score.filter(expire_time__lt=now).all()
        
        if not expired_scores:
            logger.info("无过期数据")
            return
        query_list = [QueryRequest(bangumi_id=score.bangumi_id) for score in expired_scores]
        logger.info("开始更新数据")
        
        async with in_transaction():
            await Score.filter(Q(expire_time__lt=now)).delete()
        
        result = await query(query_list)
        logger.info("数据更新执行完毕")

        asyncio.sleep(3600)