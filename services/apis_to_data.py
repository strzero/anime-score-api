import asyncio

from apis import myanimelist, anilist, filmarks, anikore
from models.request_model import IdRequest, TitleRequest

async def get_four_id(title: TitleRequest):
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


async def get_four_score(id_req: IdRequest):
    logger.info(f"开始执行网站爬取 {id_req.title}")

    myanimelist_task = myanimelist.get_score(id_req.myanimelist)
    anilist_task = anilist.get_score(id_req.anilist)
    filmarks_task = filmarks.get_score(id_req.filmarks)
    anikore_task = anikore.get_score(id_req.anikore)

    myanimelist_score, anilist_score, filmarks_score, anikore_score = await asyncio.gather(
        myanimelist_task, anilist_task, filmarks_task, anikore_task
    )

    return {
        "myanimelist": myanimelist_score,
        "anilist": anilist_score,
        "filmarks": filmarks_score,
        "anikore": anikore_score,
    }