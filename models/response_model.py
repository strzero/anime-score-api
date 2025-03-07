from pydantic import BaseModel
from typing import Optional

from uuid import UUID


class IdResponse(BaseModel):
    status: Optional[int] = None
    task_id: Optional[UUID] = None
    bangumi_id: Optional[int] = None
    title: Optional[str] = None
    myanimelist_id: Optional[str] = None
    anilist_id: Optional[str] = None
    filmarks_id: Optional[str] = None
    anikore_id: Optional[str] = None
    user_add: Optional[int] = None
    verification_count: Optional[int] = None

    class Config:
        from_attributes = True



class ScoreRequest(BaseModel):
    bangumi_id: Optional[int] = None
    title: Optional[str] = None
    update_time: Optional[str] = None
    expire_time: Optional[str] = None
    myanimelist_name: Optional[str] = None
    myanimelist_score: Optional[int] = None
    myanimelist_count: Optional[int] = None
    myanimelist_id: Optional[str] = None
    anilist_name: Optional[str] = None
    anilist_score: Optional[int] = None
    anilist_count: Optional[int] = None
    anilist_id: Optional[str] = None
    filmarks_name: Optional[str] = None
    filmarks_score: Optional[int] = None
    filmarks_count: Optional[int] = None
    filmarks_id: Optional[str] = None
    anikore_name: Optional[str] = None
    anikore_score: Optional[int] = None
    anikore_count: Optional[int] = None
    anikore_id: Optional[str] = None
