import logging

import httpx
from bs4 import BeautifulSoup

from config import settings
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

async def get_score(local_id: str):
    if local_id == "Error":
        return "Error"
    if local_id == "NoFound":
        return "NoFound"

    try:
        score_url = f"{BASE_URL}/anime/{local_id}"

        async with httpx.AsyncClient() as client:
            response = await client.get(score_url, timeout=settings.timeout)

        soup = BeautifulSoup(response.text, "lxml")

        title = soup.select_one("h1.title-name")
        score = soup.select_one("div.score-label")
        count = soup.select_one("span[itemprop='ratingCount']")

        return {
            "name": title.get_text(strip=True) if title else "Unknown Title",
            "score": float(score.get_text(strip=True)) if score and score.get_text(strip=True) != "N/A" else -1,
            "count": int(count.get_text(strip=True)) if count else 0,
            "id": local_id,
        }
    except Exception as e:
        logger.error(f"动画检索分数错误 {local_id}: {e}", exc_info=settings.logger_exc_info)
        return "Error"
