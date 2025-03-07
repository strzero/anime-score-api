import logging

import httpx
from bs4 import BeautifulSoup

from config import settings
from models.response_model import ScoreResponseSingle
from utils.client import client

# 获取 logger 实例
logger = logging.getLogger(__name__)

BASE_URL = "https://myanimelist.net"

async def get_id(name: str):
    search_url = f"{BASE_URL}/search/all?q={name}&cat=anime"
    try:
        response = await client.get(
            search_url, headers=settings.real_headers, timeout=settings.timeout
        )

        soup = BeautifulSoup(response.text, "lxml")
        anime_link = soup.select_one("div.title a.hoverinfo_trigger")

        if not anime_link:
            return "NoFound"
        return anime_link["id"][18: len(anime_link["id"])]
    except Exception as e:
        logger.error(f"myanimelist ID错误 {name}: {type(e).__name__} - {e}", exc_info=settings.logger_exc_info)
        return "Error"

async def get_score(local_id: str) -> ScoreResponseSingle:
    if local_id == "NoFound":
        return ScoreResponseSingle(status=400,message='输入NoFound')

    try:
        score_url = f"{BASE_URL}/anime/{local_id}"

        response = await client.get(score_url, timeout=settings.timeout)

        soup = BeautifulSoup(response.text, "lxml")

        title = soup.select_one("h1.title-name")
        score = soup.select_one("div.score-label")
        count = soup.select_one("span[itemprop='ratingCount']")

        if score.get_text(strip=True) == "N/A":
            return ScoreResponseSingle(
                status=204,
                message="无评分"
            )

        return ScoreResponseSingle(
            status=200,
            id=local_id,
            title=title.get_text(strip=True),
            score=float(score.get_text(strip=True)),
            count=int(count.get_text(strip=True))
        )

    except Exception as e:
        logger.error(f"myanimelist Score错误 {local_id}: {e}", exc_info=settings.logger_exc_info)
        return ScoreResponseSingle(
            status=500,
            message='全局错误'
        )
