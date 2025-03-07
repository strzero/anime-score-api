from models.db_model import IdLink, Score
from tortoise.exceptions import DoesNotExist
from datetime import datetime, timedelta

from models.response_model import IdResponse, ScoreResponse
from utils.logger import logger


async def save_id_db(res: IdResponse):
    if res.status // 100 != 2:
        return

    try:
        id_link, created = await IdLink.get_or_create(bangumi_id=res.bangumi_id)

        id_link.myanimelist_id = res.myanimelist_id
        id_link.anilist_id = res.anilist_id
        id_link.filmarks_id = res.filmarks_id
        id_link.anikore_id = res.anikore_id
        id_link.user_add = 0
        id_link.verification_count = 0

        await id_link.save()
    except DoesNotExist:
        logger.error("save id to db error: DoesNotExist", res)


async def save_score_db(res: ScoreResponse, delete_day: int):
    if res.status // 100 != 2:
        return

    update_time = datetime.now()
    expire_time = update_time + timedelta(days=delete_day)

    try:
        score, created = await Score.get_or_create(bangumi_id=res.bangumi_id)

        score.update_time = update_time
        score.expire_time = expire_time

        myanimelist = res.myanimelist
        if myanimelist.status // 100 == 2:
            score.myanimelist_title = myanimelist.title
            score.myanimelist_score = myanimelist.score
            score.myanimelist_count = myanimelist.count
            score.myanimelist_id = myanimelist.id

        anilist = res.anilist
        if anilist.status // 100 == 2:
            score.anilist_title = anilist.title
            score.anilist_score = anilist.score
            score.anilist_count = anilist.count
            score.anilist_id = anilist.id

        filmarks = res.filmarks
        if filmarks.status // 100 == 2:
            score.filmarks_title = filmarks.title
            score.filmarks_score = filmarks.score
            score.filmarks_count = filmarks.count
            score.filmarks_id = filmarks.id

        anikore = res.anilist
        if anikore.status // 100 == 2:
            score.anikore_title = anikore.title
            score.anikore_score = anikore.score
            score.anikore_count = anikore.count
            score.anikore_id = anikore.id

        await score.save()
    except DoesNotExist:
        logger.error("save score to db error: DoesNotExist", res)