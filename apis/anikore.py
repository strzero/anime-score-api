import logging

import httpx
from bs4 import BeautifulSoup

from config import settings
from models.response_model import ScoreResponseSingle
from utils.client import client

# 获取 logger 实例
logger = logging.getLogger(__name__)

BASE_URL = "https://www.anikore.jp"

async def get_id(name: str):
    try:
        # search_url = BASE_URL + "/anime_title/" + name
        search_url = f"{BASE_URL}/anime_title/{name.replace(' ', '+')}/"
        response = await client.get(
            search_url,
            headers=settings.real_headers,
            timeout=settings.timeout,
            follow_redirects=True
        )
        page = response.content

        soup = BeautifulSoup(page, "lxml")

        id_url = soup.find("div", attrs={"class": "l-searchPageRanking_unit"})
        if not id_url:
            return "NoFound"
        id_url = id_url.a["href"]
        ani_id = id_url[7: len(id_url) - 1]
        return ani_id
    except Exception as e:
        logger.error(f"anikore ID错误 {name}: {type(e).__name__} - {e}", exc_info=settings.logger_exc_info)
        return "Error"

async def get_score(local_id: str) -> ScoreResponseSingle:
    if local_id == "NoFound":
        return ScoreResponseSingle(status=400,message='输入NoFound')

    try:
        score_url = BASE_URL + "/anime/" + local_id
        response = await client.get(
            score_url,
            headers=settings.real_headers,
            timeout=10.0,
            follow_redirects=True
        )
        page = response.content

        soup = BeautifulSoup(page, "lxml")

        score = soup.find(
            "div",
            attrs={"class": "l-animeDetailHeader_pointAndButtonBlock_starBlock"},
        ).strong.string
        score = float(score) * 2

        title = soup.find(
            "div", attrs={"class": "l-animeDetailHeader_imageBlock"}
        ).find_next_sibling("h1").text.strip()

        count_span = soup.find(
            "span", attrs={"class": "l-animeDetailHeader_pointAndButtonBlock_starBlock_count"}
        ).find("a")
        count = count_span.get_text(strip=True) if count_span else "0"

        return ScoreResponseSingle(
            status=200,
            id=local_id,
            title=title,
            score=score,
            count=count
        )
    except Exception as e:
        logger.error(f"anikore Score错误 {local_id}: {e}", exc_info=settings.logger_exc_info)
        return ScoreResponseSingle(status=500,message=str(e))
