from datetime import datetime

from pydantic import BaseModel
from typing import Optional, Dict
from uuid import UUID

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
    user_add: Optional[int] = None
    verification_count: Optional[int] = None

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
    data: Optional[Dict] = None
    tags: Optional[Dict] = None

class NormalResponse(BaseModel):
    status: Optional[int] = None
    message: Optional[str] = None