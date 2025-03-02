from fastapi import FastAPI
from typing import List
from concurrent.futures import ThreadPoolExecutor
from data.myanimelist import MyAnimeList
from data.anilist import AniList
from data.filmarks import Filmarks
from data.anikore import Anikore
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from config.fastapi_setting import origins

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


# 初始化数据源对象
myanimelist = MyAnimeList()
anilist = AniList()
filmarks = Filmarks()
anikore = Anikore()

# 全局线程池配置
executor = ThreadPoolExecutor()


@app.on_event("shutdown")
def shutdown_event():
    executor.shutdown(wait=False)


# 平台配置常量
PLATFORMS_ID = [
    ('myanimelist', myanimelist.get_id),
    ('anilist', anilist.get_id),
    ('filmarks', filmarks.get_id),
    ('anikore', anikore.get_id),
]

PLATFORMS_SCORE = [
    ('myanimelist', myanimelist.get_score, 'myanimelist'),
    ('anilist', anilist.get_score, 'anilist'),
    ('filmarks', filmarks.get_score, 'filmarks'),
    ('anikore', anikore.get_score, 'anikore'),
]


def process_results(futures, result_handler):
    """通用结果处理函数"""
    results = {}
    for *keys, future in futures:
        try:
            result = future.result()
        except Exception:
            result = None
        results = result_handler(results, keys, result)
    return results


@app.post("/get_id_nodb")
async def get_id_nodb(titles: List[TitleRequest]):
    titles_list = [t.title for t in titles]

    # 提交所有任务
    futures = []
    for title in titles_list:
        for platform, method in PLATFORMS_ID:
            future = executor.submit(method, title)
            futures.append((title, platform, future))

    # 处理结果
    results = {}
    for title, platform, future in futures:
        try:
            result = future.result()
        except Exception:
            result = None
        if title not in results:
            results[title] = {'title': title}
        results[title][platform] = result

    return list(results.values())


@app.post("/get_score_nodb")
async def get_score_nodb(ids: List[IdRequest]):
    # 提交所有任务
    futures = []
    for idx, req in enumerate(ids):
        for platform, method, field in PLATFORMS_SCORE:
            id_value = getattr(req, field)
            future = executor.submit(method, id_value)
            futures.append((idx, platform, future))

    # 处理结果
    results = [{} for _ in ids]
    for idx, platform, future in futures:
        try:
            results[idx][platform] = future.result()
        except Exception:
            results[idx][platform] = None

    return results


# 保留原始接口（示例未修改部分）
@app.post("/get_id")
async def get_id(titles: List[TitleRequest]):
    return await get_id_nodb(titles)


@app.post("/get_score")
async def get_score(ids: List[IdRequest]):
    return await get_score_nodb(ids)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)