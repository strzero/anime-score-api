from models.request_model import IdRequest, ScoreRequest
from services.webdata_get import get_four_score, get_four_id
from services.db_save import save_id_db, save_score_db


async def id_task_action(request: IdRequest):
    res = await get_four_id(request)
    await save_id_db(res)
    return res

async def score_task_action(request: ScoreRequest):
    res = await get_four_score(request)
    await save_score_db(res, request.delete_day)
    return res