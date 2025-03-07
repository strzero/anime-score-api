from models.db_model import IdLink, Score
from models.request_model import IdRequest, ScoreRequest


async def check_database_id(request: IdRequest):
    return await IdLink.get(bangumi_id=request.bangumi_id)

async def check_database_score(request: ScoreRequest):
    return await Score.get(bangumi_id=request.bangumi_id)