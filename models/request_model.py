from typing import Optional

from pydantic import BaseModel, Field
from pydantic.v1 import root_validator


class IdRequest(BaseModel):
    title: str = 'NoSetTitle'
    bangumi_id: int

class ScoreRequest(BaseModel):
    title: str = 'NoSetTitle'
    bangumi_id: int
    myanimelist_id: Optional[str] = None
    anilist_id: Optional[str] = None
    filmarks_id: Optional[str] = None
    anikore_id: Optional[str] = None
    delete_day: int = 7

class QueryRequest(BaseModel):
    bangumi_id: int
