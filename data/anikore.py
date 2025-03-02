import os
import httpx
from bs4 import BeautifulSoup
from config import request_setting
from utils.error import error_report

BASE_URL = "https://www.anikore.jp"

async def get_id(name: str):
    try:
        search_url = BASE_URL + "/anime_title/" + name
        async with httpx.AsyncClient() as client:
            response = await client.get(
                search_url,
                headers=request_setting.real_headers,
                timeout=request_setting.timeout,
                follow_redirects = True
            )
            page = response.content

        soup = BeautifulSoup(page, "lxml")

        id_url = soup.find("div", attrs={"class": "l-searchPageRanking_unit"}).a[
            "href"
        ]
        ani_id = id_url[7: len(id_url) - 1]
        return ani_id
    except Exception as e:
        error_report(e, os.path.abspath(__file__))
        return "Error"

async def get_score(local_id: str):
    try:
        if local_id == "Error":
            return "None"

        score_url = BASE_URL + "/anime/" + local_id
        async with httpx.AsyncClient() as client:
            response = await client.get(
                score_url,
                headers=request_setting.real_headers,
                timeout=10.0,
                follow_redirects = True
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

        return title, score, int(count), local_id
    except Exception as e:
        error_report(e, os.path.abspath(__file__))
        return "Error"