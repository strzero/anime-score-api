from pydantic import BaseModel

class IdRequest(BaseModel):
    title: str
    bangumi_id: int

class ScoreRequest(BaseModel):
    title: str
    myanimelist: str
    anilist: str
    filmarks: str
    anikore: str
    bangumi_id: int
    delete_day: int