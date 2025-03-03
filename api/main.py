import asyncio
import logging
from fastapi import FastAPI
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from config.fastapi_setting import origins
from data import myanimelist, anilist, filmarks, anikore

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

class IdRequest(BaseModel):
    title: str
    myanimelist: str
    anilist: str
    filmarks: str
    anikore: str

async def process_title(title: TitleRequest):
    logger.info(f"Processing title: {title.title}")
    return {
        "title": title.title,
        "myanimelist": await myanimelist.get_id(title.title),
        "anilist": await anilist.get_id(title.title),
        "filmarks": await filmarks.get_id(title.title),
        "anikore": await anikore.get_id(title.title),
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

@app.post("/get_id")
async def get_id(titles: List[TitleRequest]):
    return await get_id_nodb(titles)

@app.post("/get_score")
async def get_score(ids: List[IdRequest]):
    return await get_score_nodb(ids)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
