import os
import httpx
import json
from config import request_setting
from utils.error import error_report

BASE_URL = "https://graphql.anilist.co"

async def get_id(name: str):
    query = """
    query ($search: String) {
        Media (search: $search, type: ANIME) {
            id
        }
    }
    """
    variables = {"search": name}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                BASE_URL,
                json={"query": query, "variables": variables},
                timeout=request_setting.timeout,
            )
        data = response.json().get("data", {}).get("Media", {})
        return str(data.get("id", "Error"))
    except Exception as e:
        error_report(e, os.path.abspath(__file__))
        return "Error"

async def get_score(local_id: str):
    if local_id == "Error":
        return "None"

    query = """
    query ($id: Int) {
        Media (id: $id, type: ANIME) {
            title {
                romaji
                english
                native
            }
            averageScore
            stats {
                scoreDistribution {
                    amount
                }
            }
        }
    }
    """
    variables = {"id": int(local_id)}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                BASE_URL,
                json={"query": query, "variables": variables},
                timeout=request_setting.timeout,
            )
        data = response.json().get("data", {}).get("Media", {})

        title = data.get("title", {}).get("english") or data.get("title", {}).get("native") or data.get("title", {}).get("romaji", "Unknown Title")
        score = (data.get("averageScore", -1) / 10) if data.get("averageScore") is not None else -1
        count = sum(item["amount"] for item in data.get("stats", {}).get("scoreDistribution", []))

        return title, score, count, local_id
    except Exception as e:
        error_report(e, os.path.abspath(__file__))
        return "Error"