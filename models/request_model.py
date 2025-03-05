from pydantic import BaseModel

class IdRequest(BaseModel):
    title: str
    bangumi_id: int

    def __hash__(self):
        return hash(self.bangumi_id)

    def __eq__(self, other):
        if isinstance(other, IdRequest):
            return self.bangumi_id == other.bangumi_id
        return False


class ScoreRequest(BaseModel):
    title: str
    myanimelist: str
    anilist: str
    filmarks: str
    anikore: str
    bangumi_id: int
    delete_day: int

    def __hash__(self):
        return hash(self.bangumi_id)

    def __eq__(self, other):
        if isinstance(other, IdRequest):
            return self.bangumi_id == other.bangumi_id
        return False