import logging

import httpx

from config import settings
from models.response_model import ScoreResponseSingle
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

async def get_score(local_id: str) -> ScoreResponseSingle:
    if local_id == "NoFound":
        return ScoreResponseSingle(status=400,message='输入NoFound')

    try:
        query = """
        query ($id: Int) {
            Media (id: $id, type: ANIME) {
                title {
                    romaji
                    english
                    native
                }
                id
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
            return ScoreResponseSingle(status=500,message='API速率限制')
        media = data.get("Media", {})
        if not media:
            return ScoreResponseSingle(status=500,message='No Media')

        title = (
            media.get("title", {}).get("english") or
            media.get("title", {}).get("native") or
            media.get("title", {}).get("romaji", "Unknown Title")
        )

        if media.get("averageScore") is None:
            return ScoreResponseSingle(
                status=204,
                message="无评分",
                title=title
            )
        score = media.get("averageScore") / 10



        count = sum(item["amount"] for item in media.get("stats", {}).get("scoreDistribution", []))

        return ScoreResponseSingle(
            status=200,
            id=local_id,
            title=title,
            score=score,
            count=count
        )
    except Exception as e:
        logger.error(f"anilist Score错误 {local_id}: {e}", exc_info=settings.logger_exc_info)
        return ScoreResponseSingle(status=500,message=str(e))
