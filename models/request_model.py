from pydantic import BaseModel

class IdRequest(BaseModel):
    title: str = 'NoSetTitle'
    bangumi_id: int

class ScoreRequest(BaseModel):
    title: str = 'NoSetTitle'
    bangumi_id: int
    myanimelist_id: str
    anilist_id: str
    filmarks_id: str
    anikore_id: str
    delete_day: int = 7

class QueryRequest(BaseModel):
    bangumi_id: int