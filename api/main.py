import asyncio
import logging
from datetime import datetime, timedelta
from fastapi import FastAPI
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from config.fastapi_setting import origins
from data import myanimelist, anilist, filmarks, anikore
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from config.db_setting import AsyncSessionLocal
from models import IdLink, Score

# 设置日志记录
log_file_path = "logs.log"  # 或者从 config.fastapi_setting 导入
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TitleRequest(BaseModel):
    title: str
    bangumi_id: int

class IdRequest(BaseModel):
    title: str
    myanimelist: str
    anilist: str
    filmarks: str
    anikore: str
    bangumi_id: int
    delete_day: int

async def process_title(title: TitleRequest):
    myanimelist_task = myanimelist.get_id(title.title)
    anilist_task = anilist.get_id(title.title)
    filmarks_task = filmarks.get_id(title.title)
    anikore_task = anikore.get_id(title.title)

    myanimelist_id, anilist_id, filmarks_id, anikore_id = await asyncio.gather(
        myanimelist_task, anilist_task, filmarks_task, anikore_task
    )

    return {
        "title": title.title,
        "myanimelist": myanimelist_id,
        "anilist": anilist_id,
        "filmarks": filmarks_id,
        "anikore": anikore_id,
    }


async def process_id_request(id_req: IdRequest):
    logger.info(f"Processing ID request for: {id_req.title}")
    return {
        "myanimelist": await myanimelist.get_score(id_req.myanimelist),
        "anilist": await anilist.get_score(id_req.anilist),
        "filmarks": await filmarks.get_score(id_req.filmarks),
        "anikore": await anikore.get_score(id_req.anikore),
    }

async def run_tasks_with_delay(tasks):
    results = []
    for task in tasks:
        results.append(asyncio.create_task(task))  # 启动任务但不等待
        await asyncio.sleep(1)  # 每秒启动一个新任务
    return await asyncio.gather(*results)

@app.post("/get_id_nodb")
async def get_id_nodb(titles: List[TitleRequest]):
    logger.info(f"Received titles for ID processing: {[title.title for title in titles]}")
    tasks = [process_title(title) for title in titles]
    return await run_tasks_with_delay(tasks)

@app.post("/get_score_nodb")
async def get_score_nodb(ids: List[IdRequest]):
    logger.info(f"Received IDs for score processing: {[id_req.title for id_req in ids]}")
    tasks = [process_id_request(id_req) for id_req in ids]
    return await run_tasks_with_delay(tasks)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@app.post("/get_id")
async def get_id(titles: List[TitleRequest], db: AsyncSession = Depends(get_db)):
    results = []

    for item in titles:
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
        async with db.begin_nested():
            stmt_lock = select(IdLink).where(IdLink.bangumi_id == item.bangumi_id).with_for_update()
            try:
                await db.execute(stmt_lock)
            except NoResultFound:
                pass

            # Call external API using title if bangumi_id is not found
            api_result = await get_id_nodb([item])
            new_record = IdLink(
                bangumi_id=item.bangumi_id,
                myanimelist_id=api_result[0]['myanimelist'],
                anilist_id=api_result[0]['anilist'],
                filmarks_id=api_result[0]['filmarks'],
                anikore_id=api_result[0]['anikore'],
                user_add=0  # Ensure user_add is set to 0 for new records
            )
            db.add(new_record)
            await db.commit()

            results.append(new_record)

    return results

@app.post("/get_score")
async def get_score(ids: List[IdRequest], db: AsyncSession = Depends(get_db)):
    results = []

    for item in ids:
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

        # 加锁以避免重复请求
        async with db.begin_nested():
            stmt_lock = select(Score).where(Score.bangumi_id == item.bangumi_id).with_for_update()
            try:
                await db.execute(stmt_lock)
            except NoResultFound:
                pass

            # 调用外部 API 获取评分数据
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
