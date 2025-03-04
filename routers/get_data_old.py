from datetime import datetime, timedelta
from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from models.db_model import IdLink, Score
from models.request_model import IdRequest, TitleRequest
from routers.get_data_nodb import get_id_nodb, get_score_nodb
from utils.database_old import get_db
from utils.logger import logger

router = APIRouter()

@router.post("/get_id")
async def get_id(titles: List[TitleRequest], db: AsyncSession = Depends(get_db)):
    logger.info(f"尝试从数据库获取ID数据： {[title.title for title in titles]}")
    results = []

    for item in titles:
        logger.info(f"尝试从数据库获取ID数据： {item.title}")
        # Check existing IDs in id_link
        stmt = select(IdLink).where(IdLink.bangumi_id == item.bangumi_id)
        result = await db.execute(stmt)
        record = result.scalars().first()

        if record:
            if record.user_add == 1:
                # Skip if user_add is 1
                results.append(record)
                continue
            else:
                # Return existing record
                results.append(record)
                continue

        # Locking mechanism
        logger.info(f"数据库无该条ID数据： {item.title}")
        api_result = await get_id_nodb([item])
        new_record = IdLink(
            bangumi_id=item.bangumi_id,
            myanimelist_id=api_result[0]['myanimelist'],
            anilist_id=api_result[0]['anilist'],
            filmarks_id=api_result[0]['filmarks'],
            anikore_id=api_result[0]['anikore'],
            user_add=0,
            verification_count=0
        )
        db.add(new_record)
        await db.commit()

        results.append(new_record)

    return results

@router.post("/get_score")
async def get_score(ids: List[IdRequest], db: AsyncSession = Depends(get_db)):
    logger.info(f"尝试从数据库获取评分数据： {[id_req.title for id_req in ids]}")
    results = []

    for item in ids:
        logger.info(f"尝试从数据库获取评分数据： {item.title}")
        # 查询 score 表中的数据
        stmt = select(Score).where(Score.bangumi_id == item.bangumi_id)
        result = await db.execute(stmt)
        record = result.scalars().first()

        if record:
            # 如果数据存在，构建返回格式
            results.append({
                "bangumi_id": record.bangumi_id,
                "myanimelist": {
                    "name": record.myanimelist_name,
                    "score": record.myanimelist_score,
                    "count": record.myanimelist_count
                },
                "anilist": {
                    "name": record.anilist_name,
                    "score": record.anilist_score,
                    "count": record.anilist_count
                },
                "filmarks": {
                    "name": record.filmarks_name,
                    "score": record.filmarks_score,
                    "count": record.filmarks_count
                },
                "anikore": {
                    "name": record.anikore_name,
                    "score": record.anikore_score,
                    "count": record.anikore_count
                },
                "update_time": record.update_time,
                "expire_time": record.expire_time
            })
            continue

        logger.info(f"数据库无该条Score数据： {item.title}")
        score_data = await get_score_nodb([item])

        # 获取当前时间和过期时间
        update_time = datetime.utcnow()
        expire_time = update_time + timedelta(days=item.delete_day)

        # 创建新的 score 记录
        new_record = Score(
            bangumi_id=item.bangumi_id,
            update_time=update_time,
            expire_time=expire_time,
            myanimelist_name=score_data[0]['myanimelist']['name'],
            myanimelist_score=score_data[0]['myanimelist']['score'],
            myanimelist_count=score_data[0]['myanimelist']['count'],
            myanimelist_id=item.myanimelist,
            anilist_name=score_data[0]['anilist']['name'],
            anilist_score=score_data[0]['anilist']['score'],
            anilist_count=score_data[0]['anilist']['count'],
            anilist_id=item.anilist,
            filmarks_name=score_data[0]['filmarks']['name'],
            filmarks_score=score_data[0]['filmarks']['score'],
            filmarks_count=score_data[0]['filmarks']['count'],
            filmarks_id=item.filmarks,
            anikore_name=score_data[0]['anikore']['name'],
            anikore_score=score_data[0]['anikore']['score'],
            anikore_count=score_data[0]['anikore']['count'],
            anikore_id=item.anikore
        )

        db.add(new_record)
        await db.commit()

        result = score_data[0]
        result.update({'update_time': update_time, 'expire_time': expire_time})

        # 添加到结果列表
        results.append(result)

    return results