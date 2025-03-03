from pydantic import BaseModel

class TitleRequest(BaseModel):
    title: str
    bangumi_id: int

class IdRequest(BaseModel):
    title: str
    myanimelist: str
    anilist: str
    filmarks: str
    anikore: str
    bangumi_id: int
    delete_day: int