import asyncio

from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise

from config.settings import DATABASE_CONFIG
from models.db_model import IdLink
from models.request_model import ScoreRequest
from services.get_web_data import get_four_id, IdRequest, get_four_score

async def init():
    await Tortoise.init(config=DATABASE_CONFIG)

async def main():
    # name_request = TitleRequest(title="Ave Mujica", bangumi_id=454684)
    # result = await get_four_id(name_request)
    # print(result)
    # title_request = IdRequest(
    #     title=name_request.title,
    #     bangumi_id=name_request.bangumi_id,
    #     delete_day=7,
    #     myanimelist=result.get("myanimelist"),
    #     anilist=result.get("anilist"),
    #     filmarks=result.get("filmarks"),
    #     anikore=result.get("anikore")
    # )
    # score = await(get_four_score(title_request))
    # print(score)

    await init()

    print(await IdLink.get(bangumi_id=294).values())

    await Tortoise.close_connections()


asyncio.run(main())