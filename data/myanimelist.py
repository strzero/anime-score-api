import os
import httpx
from bs4 import BeautifulSoup
from config import request_setting
from utils.error import error_report

BASE_URL = "https://myanimelist.net"

async def get_id(name: str):
    search_url = f"{BASE_URL}/search/all?q={name}&cat=anime"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                search_url, headers=request_setting.real_headers, timeout=request_setting.timeout
            )

        soup = BeautifulSoup(response.text, "lxml")
        anime_link = soup.select_one("div.title a.hoverinfo_trigger")

        if not anime_link:
            return "Error"
        return anime_link["id"][18: len(anime_link["id"])]
    except Exception as e:
        error_report(e, os.path.abspath(__file__))
        return "Error"

async def get_score(local_id: str):
    if local_id == "Error":
        return "None"

    score_url = f"{BASE_URL}/anime/{local_id}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(score_url, timeout=request_setting.timeout)

        soup = BeautifulSoup(response.text, "lxml")

        title = soup.select_one("h1.title-name")
        score = soup.select_one("div.score-label")
        count = soup.select_one("span[itemprop='ratingCount']")

        return {
            "title": title.get_text(strip=True) if title else "Unknown Title",
            "score": float(score.get_text(strip=True)) if score and score.get_text(strip=True) != "N/A" else -1,
            "count": int(count.get_text(strip=True)) if count else 0,
            "id": local_id,
        }
    except Exception as e:
        error_report(e, os.path.abspath(__file__))
        return "Error"