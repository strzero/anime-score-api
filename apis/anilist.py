import logging

import httpx

from config import settings
from utils.client import client

# 获取 logger 实例
logger = logging.getLogger(__name__)

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
        response = await client.post(
            BASE_URL,
            json={"query": query, "variables": variables},
            timeout=settings.timeout,
        )
        # logger.info(f"X-RateLimit-Remaining: {response.headers.get('X-RateLimit-Remaining')}")
        data = response.json().get("data", {})
        if not data:
            logger.error("anilist API速率限制")
            return "Error"
        media = data.get("Media", {})
        if not media:
            return "NoFound"
        return str(media.get("id", "Error"))
    except Exception as e:
        logger.error(f"anilist ID错误 {name}: {type(e).__name__} - {e}", exc_info=settings.logger_exc_info)
        return "Error"

async def get_score(local_id: str):
    if local_id == "Error":
        return "Error"
    if local_id == "NoFound":
        return "NoFound"

    try:
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

        response = await client.post(
            BASE_URL,
            json={"query": query, "variables": variables},
            timeout=settings.timeout,
        )
        data = response.json().get("data", {})
        if not data:
            logger.error("anilist API速率限制")
            return "Error"
        media = data.get("Media", {})
        if not media:
            return "NoFound"

        title = (
            media.get("title", {}).get("english") or
            media.get("title", {}).get("native") or
            media.get("title", {}).get("romaji", "Unknown Title")
        )
        score = (media.get("averageScore", -1) / 10) if media.get("averageScore") is not None else -1
        count = sum(item["amount"] for item in media.get("stats", {}).get("scoreDistribution", []))
        return {
            "name": title,
            "score": score,
            "count": count,
            "id": local_id,
        }
    except Exception as e:
        logger.error(f"动画检索分数错误 {local_id}: {e}", exc_info=settings.logger_exc_info)
        return "Error"
