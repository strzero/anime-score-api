import asyncio

from apis import myanimelist, anilist, filmarks, anikore
from models.request_model import ScoreRequest, IdRequest
from models.response_model import IdResponse
from utils.logger import logger

async def get_four_id(request: IdRequest) -> IdResponse:
    myanimelist_task = myanimelist.get_id(request.title)
    anilist_task = anilist.get_id(request.title)
    filmarks_task = filmarks.get_id(request.title)
    anikore_task = anikore.get_id(request.title)

    myanimelist_id, anilist_id, filmarks_id, anikore_id = await asyncio.gather(
        myanimelist_task, anilist_task, filmarks_task, anikore_task
    )

    if any(value == 'Error' for value in [myanimelist_id, anilist_id, filmarks_id, anikore_id]):
        return IdResponse(
            status=500
        )

    return IdResponse(
        status=200,
        message='成功从网站抓取数据',
        bangumi_id=request.bangumi_id,
        title=request.title,
        myanimelist_id=myanimelist_id,
        anilist_id=anilist_id,
        filmarks_id=filmarks_id,
        anikore_id=anikore_id
    )


async def get_four_score(request: ScoreRequest):

    myanimelist_task = myanimelist.get_score(request.myanimelist_id)
    anilist_task = anilist.get_score(request.anilist_id)
    filmarks_task = filmarks.get_score(request.filmarks_id)
    anikore_task = anikore.get_score(request.anikore_id)

    myanimelist_score, anilist_score, filmarks_score, anikore_score = await asyncio.gather(
        myanimelist_task, anilist_task, filmarks_task, anikore_task
    )

    return {
        "title": request.title,
        "bangumi_id": request.bangumi_id,
        "delete_day": request.delete_day,
        "myanimelist": myanimelist_score,
        "anilist": anilist_score,
        "filmarks": filmarks_score,
        "anikore": anikore_score,
    }