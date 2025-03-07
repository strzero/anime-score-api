from pydantic import BaseModel
from typing import Optional
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

class ScoreRequestSingle(BaseModel):
    status: Optional[int] = None
    message: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None
    score: Optional[float] = None
    count: Optional[int] = None

class ScoreRequest(BaseModel):
    status: Optional[int] = None
    message: Optional[str] = None
    task_id: Optional[UUID] = None
    bangumi_id: Optional[int] = None
    title: Optional[str] = None
    myanimelist: Optional[ScoreRequestSingle] = None
    anilist: Optional[ScoreRequestSingle] = None
    filmarks: Optional[ScoreRequestSingle] = None
    anikore: Optional[ScoreRequestSingle] = None