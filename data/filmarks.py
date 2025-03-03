import os
import re
import httpx
import json
from bs4 import BeautifulSoup
from config import request_setting
from utils.error import error_report

BASE_URL = "https://filmarks.com"

async def get_id(name: str):
    search_url = f"{BASE_URL}/search/animes?q={name}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                search_url, headers=request_setting.real_headers, timeout=request_setting.timeout
            )

        soup = BeautifulSoup(response.text, "lxml")
        js_cassette_element = soup.select_one(".p-contents-grid .js-cassette")

        if not js_cassette_element:
            return "Error"

        data = json.loads(js_cassette_element.get("data-mark", "{}"))
        anime_series_id = data.get("anime_series_id")
        anime_season_id = data.get("anime_season_id")

        return f"{anime_series_id}/{anime_season_id}" if anime_series_id and anime_season_id else "Error"
    except Exception as e:
        error_report(e, os.path.abspath(__file__))
        return "Error"

async def get_score(local_id: str):
    if local_id == "Error":
        return "None"

    search_url = f"{BASE_URL}/animes/{local_id}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                search_url, headers=request_setting.real_headers, timeout=request_setting.timeout
            )

        soup = BeautifulSoup(response.text, "lxml")

        score_element = soup.select_one("div.c2-rating-l__text")
        score = float(score_element.text) * 2 if score_element and score_element.text != "-" else -1

        title_element = soup.select_one("h2.p-content-detail__title")
        title = title_element.get_text(strip=True) if title_element else "Unknown Title"

        og_description = soup.select_one("meta[property='og:description']")
        count = 0
        if og_description:
            match = re.search(r"レビュー数：(\d+)件", og_description.get("content", ""))
            if match:
                count = int(match.group(1))

        return {
            "title": title,
            "score": score,
            "count": count,
            "id": local_id,
        }
    except Exception as e:
        error_report(e, os.path.abspath(__file__))
        return "Error"