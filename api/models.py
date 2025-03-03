from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class IdLink(Base):
    __tablename__ = "id_link"
    bangumi_id = Column(Integer, primary_key=True, index=True)
    myanimelist_id = Column(String)
    anilist_id = Column(String)
    filmarks_id = Column(String)
    anikore_id = Column(String)
    user_add = Column(TINYINT)


class Score(Base):
    __tablename__ = 'score'

    bangumi_id = Column(Integer, primary_key=True, index=True)
    update_time = Column(DateTime, nullable=False)
    expire_time = Column(DateTime, nullable=False)
    myanimelist_name = Column(String, nullable=True)
    myanimelist_score = Column(Float, nullable=True)
    myanimelist_count = Column(Integer, nullable=True)
    myanimelist_id = Column(String, nullable=True)
    anilist_name = Column(String, nullable=True)
    anilist_score = Column(Float, nullable=True)
    anilist_count = Column(Integer, nullable=True)
    anilist_id = Column(String, nullable=True)
    filmarks_name = Column(String, nullable=True)
    filmarks_score = Column(Float, nullable=True)
    filmarks_count = Column(Integer, nullable=True)
    filmarks_id = Column(String, nullable=True)
    anikore_name = Column(String, nullable=True)
    anikore_score = Column(Float, nullable=True)
    anikore_count = Column(Integer, nullable=True)
    anikore_id = Column(String, nullable=True)