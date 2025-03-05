from models.request_model import IdRequest, ScoreRequest
from services.get_web_data import get_four_score, get_four_id


async def id_task_action(request: IdRequest):
    return await get_four_id(request)

async def score_task_action(request: ScoreRequest):
    return await get_four_score(request)