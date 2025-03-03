import asyncio
import logging
from datetime import datetime, timedelta
from fastapi import FastAPI
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import config.fastapi_setting
from config.fastapi_setting import origins
from data import myanimelist, anilist, filmarks, anikore
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from models import IdLink, Score
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+aiomysql://root:so6666@localhost:3306/anime-score"
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

logging.basicConfig(
    filename=config.fastapi_setting.log_file_path,
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
    logger.info(f"开始执行网站爬取 {id_req.title}")
    return {
        "myanimelist": await myanimelist.get_score(id_req.myanimelist),
        "anilist": await anilist.get_score(id_req.anilist),
        "filmarks": await filmarks.get_score(id_req.filmarks),
        "anikore": await anikore.get_score(id_req.anikore),
    }

@app.post("/get_id_nodb")
async def get_id_nodb(titles: List[TitleRequest]):
    logger.info(f"尝试从网页获取ID数据： {[title.title for title in titles]}")
    tasks = [
        asyncio.create_task(process_title(title), name=f"get_id:{title.bangumi_id}")
        for title in titles
    ]
    results = await asyncio.gather(*tasks)
    return results

@app.post("/get_score_nodb")
async def get_score_nodb(ids: List[IdRequest]):
    logger.info(f"尝试从网页获取评分数据： {[id_req.title for id_req in ids]}")
    tasks = [
        asyncio.create_task(process_id_request(id_req), name=f"get_score:{id_req.bangumi_id}")
        for id_req in ids
    ]
    results = await asyncio.gather(*tasks)
    return results

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@app.post("/get_id")
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
                user_add=0,
                verification_count=0
            )
            db.add(new_record)
            await db.commit()

            results.append(new_record)

    return results

@app.post("/get_score")
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

        # 加锁以避免重复请求
        logger.info(f"数据库无该条Score数据： {item.title}")
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

@app.get("/task_status")
async def task_status():
    tasks = asyncio.all_tasks()
    filtered_tasks = [task for task in tasks if task.get_name().startswith("get")]
    return [{"name": task.get_name(), "done": task.done()} for task in filtered_tasks]

clients = []

@app.websocket("/ws/task_status")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)

    try:
        while True:
            await asyncio.sleep(1)  # 每秒钟推送一次更新信息

            # 获取所有任务
            tasks = asyncio.all_tasks()

            # 筛选出name以"get"开头的任务
            filtered_tasks = [
                task for task in tasks if task.get_name().startswith("get")
            ]

            # 获取任务数量
            filtered_task_count = len(filtered_tasks)

            # 任务信息
            task_status = [{"name": task.get_name(), "done": task.done()} for task in filtered_tasks]

            # 向 WebSocket 客户端推送筛选后的任务状态以及数量
            await websocket.send_json({
                "task_status": task_status,
                "get_task_count": filtered_task_count
            })

    except WebSocketDisconnect:
        clients.remove(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)