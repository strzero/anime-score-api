from models.db_model import IdLink, Score
from tortoise.exceptions import DoesNotExist
from datetime import datetime, timedelta

async def save_id_db(id_data):
    # 提取 id_data 中的各个字段
    bangumi_id = id_data.get('bangumi_id')
    myanimelist_id = id_data.get('myanimelist')
    anilist_id = id_data.get('anilist')
    filmarks_id = id_data.get('filmarks')
    anikore_id = id_data.get('anikore')

    if any(value == 'Error' for value in [myanimelist_id, anilist_id, filmarks_id, anikore_id]):
        return

    try:
        # 尝试查找是否已存在该 bangumi_id 的记录
        id_link, created = await IdLink.get_or_create(bangumi_id=bangumi_id)

        # 更新字段值
        id_link.myanimelist_id = myanimelist_id
        id_link.anilist_id = anilist_id
        id_link.filmarks_id = filmarks_id
        id_link.anikore_id = anikore_id
        id_link.user_add = 0
        id_link.verification_count = 0

        # 保存更新后的记录
        await id_link.save()
    except DoesNotExist:
        # 如果找不到记录，则创建新记录
        await IdLink.create(
            bangumi_id=bangumi_id,
            myanimelist_id=myanimelist_id,
            anilist_id=anilist_id,
            filmarks_id=filmarks_id,
            anikore_id=anikore_id,
            user_add=0,
            verification_count=0
        )


async def save_score_db(score_data):
    # 提取 score_data 中的各个字段
    bangumi_id = score_data.get('bangumi_id')
    delete_day = int(score_data.get('delete_day'))

    myanimelist = score_data.get('myanimelist')
    anilist = score_data.get('anilist')
    filmarks = score_data.get('filmarks')
    anikore = score_data.get('anikore')

    if any(value == 'Error' for value in [myanimelist, anilist, filmarks, anikore]):
        return

    # 当前时间作为 update_time
    update_time = datetime.now()
    # 计算 expire_time，expire_time = update_time + delete_day 天
    expire_time = update_time + timedelta(days=delete_day)

    try:
        # 尝试查找是否已存在该 bangumi_id 的记录
        score, created = await Score.get_or_create(bangumi_id=bangumi_id)

        # 更新字段值
        score.update_time = update_time
        score.expire_time = expire_time
        score.myanimelist_name = myanimelist.get('name')
        score.myanimelist_score = myanimelist.get('score')
        score.myanimelist_count = myanimelist.get('count')
        score.myanimelist_id = myanimelist.get('id')

        score.anilist_name = anilist.get('name')
        score.anilist_score = anilist.get('score')
        score.anilist_count = anilist.get('count')
        score.anilist_id = anilist.get('id')

        score.filmarks_name = filmarks.get('name')
        score.filmarks_score = filmarks.get('score')
        score.filmarks_count = filmarks.get('count')
        score.filmarks_id = filmarks.get('id')

        score.anikore_name = anikore.get('name')
        score.anikore_score = anikore.get('score')
        score.anikore_count = anikore.get('count')
        score.anikore_id = anikore.get('id')

        # 保存更新后的记录
        await score.save()
    except DoesNotExist:
        # 如果找不到记录，则创建新记录
        await Score.create(
            bangumi_id=bangumi_id,
            update_time=update_time,
            expire_time=expire_time,
            myanimelist_name=myanimelist.get('name'),
            myanimelist_score=myanimelist.get('score'),
            myanimelist_count=myanimelist.get('count'),
            myanimelist_id=myanimelist.get('id'),
            anilist_name=anilist.get('name'),
            anilist_score=anilist.get('score'),
            anilist_count=anilist.get('count'),
            anilist_id=anilist.get('id'),
            filmarks_name=filmarks.get('name'),
            filmarks_score=filmarks.get('score'),
            filmarks_count=filmarks.get('count'),
            filmarks_id=filmarks.get('id'),
            anikore_name=anikore.get('name'),
            anikore_score=anikore.get('score'),
            anikore_count=anikore.get('count'),
            anikore_id=anikore.get('id')
        )