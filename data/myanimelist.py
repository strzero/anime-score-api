import os
import httpx
from bs4 import BeautifulSoup
from config import settings
import logging

# 获取 logger 实例
logger = logging.getLogger(__name__)

BASE_URL = "https://myanimelist.net"

async def get_id(name: str):
    search_url = f"{BASE_URL}/search/all?q={name}&cat=anime"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                search_url, headers=settings.real_headers, timeout=settings.timeout
            )

        soup = BeautifulSoup(response.text, "lxml")
        anime_link = soup.select_one("div.title a.hoverinfo_trigger")

        if not anime_link:
            logger.error(f"未搜索到动画: {name}")
            return "Error"
        return anime_link["id"][18: len(anime_link["id"])]
    except Exception as e:
        logger.error(f"动画检索ID中错误 {name}: {e}", exc_info=True)
        return "Error"

async def get_score(local_id: str):
    if local_id == "Error":
        return "None"

    score_url = f"{BASE_URL}/anime/{local_id}"
    try:
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
        logger.error(f"动画检索分数中错误 {local_id}: {e}", exc_info=True)
        return "Error"
