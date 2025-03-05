from pydantic import BaseModel

class IdRequest(BaseModel):
    title: str
    bangumi_id: int

    def __hash__(self):
        return hash(self.bangumi_id+1)

    def __eq__(self, other):
        if isinstance(other, IdRequest):
            return self.bangumi_id+1 == other.bangumi_id+1
        return False


class ScoreRequest(BaseModel):
    title: str = "NoSetTitle"
    myanimelist_id: str
    anilist_id: str
    filmarks_id: str
    anikore_id: str
    bangumi_id: int
    delete_day: int = 7

    def __hash__(self):
        return hash(self.bangumi_id+2)

    def __eq__(self, other):
        if isinstance(other, IdRequest):
            return self.bangumi_id+2 == other.bangumi_id+2
        return False