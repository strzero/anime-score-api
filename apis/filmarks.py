import json
import logging
import re

import httpx
from bs4 import BeautifulSoup

from config import settings
from models.response_model import ScoreResponseSingle
from utils.client import client

# 获取 logger 实例
logger = logging.getLogger(__name__)

BASE_URL = "https://filmarks.com"

async def get_id(name: str):
    search_url = f"{BASE_URL}/search/animes?q={name}"
    try:
        response = await client.get(
            search_url, headers=settings.real_headers, timeout=settings.timeout
        )

        soup = BeautifulSoup(response.text, "lxml")
        js_cassette_element = soup.select_one(".p-contents-grid .js-cassette")

        if not js_cassette_element:
            return "NoFound"

        data = json.loads(js_cassette_element.get("data-mark", "{}"))
        anime_series_id = data.get("anime_series_id")
        anime_season_id = data.get("anime_season_id")

        return f"{anime_series_id}/{anime_season_id}" if anime_series_id and anime_season_id else "Error"
    except Exception as e:
        logger.error(f"filmarks ID错误 {name}: {type(e).__name__} - {e}", exc_info=settings.logger_exc_info)
        return "Error"

async def get_score(local_id: str) -> ScoreResponseSingle:
    if local_id == "NoFound":
        return ScoreResponseSingle(status=400,message='输入NoFound')

    try:
        search_url = f"{BASE_URL}/animes/{local_id}"

        response = await client.get(
            search_url, headers=settings.real_headers, timeout=settings.timeout
        )

        soup = BeautifulSoup(response.text, "lxml")

        title_element = soup.select_one("h2.p-content-detail__title")
        title = title_element.get_text(strip=True) if title_element else "Unknown Title"

        score_element = soup.select_one("div.c2-rating-l__text")
        if score_element and score_element.text != "-":
            score = float(score_element.text) * 2
        else:
            return ScoreResponseSingle(
                status=204,
                message="无评分",
                title=title
            )


        og_description = soup.select_one("meta[property='og:description']")
        count = 0
        if og_description:
            match = re.search(r"レビュー数：(\d+)件", og_description.get("content", ""))
            if match:
                count = int(match.group(1))

        return ScoreResponseSingle(
            status=200,
            id=local_id,
            title=title,
            score=score,
            count=count
        )
    except Exception as e:
        logger.error(f"filmarks Score错误 {local_id}: {e}", exc_info=settings.logger_exc_info)
        return ScoreResponseSingle(status=500,message=e)
