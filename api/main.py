from fastapi import FastAPI, HTTPException
from typing import List
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from config.fastapi_setting import origins
from data import myanimelist, anilist, filmarks, anikore

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
    myanimelist_id, anilist_id, filmarks_id, anikore_id = await asyncio.gather(
        myanimelist.get_id(title.title),
        anilist.get_id(title.title),
        filmarks.get_id(title.title),
        anikore.get_id(title.title)
    )
    return {
        "title": title.title,
        "myanimelist": myanimelist_id,
        "anilist": anilist_id,
        "filmarks": filmarks_id,
        "anikore": anikore_id,
    }

async def process_id_request(id_req: IdRequest):
    myanimelist_score, anilist_score, filmarks_score, anikore_score = await asyncio.gather(
        myanimelist.get_score(id_req.myanimelist),
        anilist.get_score(id_req.anilist),
        filmarks.get_score(id_req.filmarks),
        anikore.get_score(id_req.anikore)
    )
    return {
        "myanimelist": myanimelist_score,
        "anilist": anilist_score,
        "filmarks": filmarks_score,
        "anikore": anikore_score,
    }

@app.post("/get_id_nodb")
async def get_id_nodb(titles: List[TitleRequest]):
    tasks = [process_title(title) for title in titles]
    return await asyncio.gather(*tasks)

@app.post("/get_score_nodb")
async def get_score_nodb(ids: List[IdRequest]):
    tasks = [process_id_request(id_req) for id_req in ids]
    return await asyncio.gather(*tasks)

@app.post("/get_id")
async def get_id(titles: List[TitleRequest]):
    # 待补充数据库逻辑
    return await get_id_nodb(titles)

@app.post("/get_score")
async def get_score(ids: List[IdRequest]):
    # 待补充数据库逻辑
    return await get_score_nodb(ids)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)