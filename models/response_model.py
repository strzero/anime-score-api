from datetime import datetime

from pydantic import BaseModel
from typing import Optional, Dict, List
from uuid import UUID

from models.db_model import BangumiData, BangumiTags, BangumiData_Pydantic



class IdResponse(BaseModel):
    status: Optional[int] = None
    message: Optional[str] = None
    task_id: Optional[UUID] = None
    bangumi_id: Optional[int] = None
    title: Optional[str] = None
    myanimelist_id: Optional[str] = None
    anilist_id: Optional[str] = None
    filmarks_id: Optional[str] = None
    anikore_id: Optional[str] = None
    myanimelist_useradd: Optional[int] = 0
    anilist_useradd: Optional[int] = 0
    filmarks_useradd: Optional[int] = 0
    anikore_useradd: Optional[int] = 0
    verification_count: Optional[int] = 0

class ScoreResponseSingle(BaseModel):
    status: Optional[int] = None
    message: Optional[str] = None
    id: Optional[str] = None
    title: Optional[str] = None
    score: Optional[float] = None
    count: Optional[int] = None

class ScoreResponse(BaseModel):
    status: Optional[int] = None
    message: Optional[str] = None
    task_id: Optional[UUID] = None
    bangumi_id: Optional[int] = None
    title: Optional[str] = None
    update_time: Optional[datetime] = None
    myanimelist: Optional[ScoreResponseSingle] = ScoreResponseSingle()
    anilist: Optional[ScoreResponseSingle] = ScoreResponseSingle()
    filmarks: Optional[ScoreResponseSingle] = ScoreResponseSingle()
    anikore: Optional[ScoreResponseSingle] = ScoreResponseSingle()

class BangumiDataResponse(BaseModel):
    status: Optional[int] = None
    message: Optional[str] = None
    data: Optional[BangumiData_Pydantic] = None
    tags: Optional[List] = None

    class Config:
        arbitrary_types_allowed = True

class QueryResponse(BaseModel):
    status: Optional[int] = None
    message: Optional[str] = None
    id_data: Optional[IdResponse] = None
    score_data: Optional[ScoreResponse] = None
    bangumi_data: Optional[BangumiDataResponse] = None

class NormalResponse(BaseModel):
    status: Optional[int] = None
    message: Optional[str] = None

