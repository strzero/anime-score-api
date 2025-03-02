from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from external.myanimelist import MyAnimeList
from external.anilist import AniList
from external.filmarks import Filmarks
from external.anikore import Anikore

app = FastAPI()


from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
origins = [
    "http://localhost:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      
    allow_credentials=True,     
    allow_methods=["*"],        
    allow_headers=["*"],        
)

class TitleRequest(BaseModel):
    title: str

class IdRequest(BaseModel):
    title: str
    myanimelist: str
    anilist: str
    filmarks: str
    anikore: str

myanimelist = MyAnimeList()
anilist = AniList()
filmarks = Filmarks()
anikore = Anikore()

@app.post("/get_id")
async def get_id(titles: List[TitleRequest]):
    results = []

    with ThreadPoolExecutor() as executor:
        for title in titles:
            myanimelist_id = executor.submit(myanimelist.get_id, title.title)
            anilist_id = executor.submit(anilist.get_id, title.title)
            filmarks_id = executor.submit(filmarks.get_id, title.title)
            anikore_id = executor.submit(anikore.get_id, title.title)

            results.append({
                "title": title.title,
                "myanimelist": myanimelist_id.result(),
                "anilist": anilist_id.result(),
                "filmarks": filmarks_id.result(),
                "anikore": anikore_id.result(),
            })

    return results

@app.post("/get_score")
async def get_score(ids: List[IdRequest]):
    results = []

    with ThreadPoolExecutor() as executor:
        for id_request in ids:
            myanimelist_score = executor.submit(myanimelist.get_score, id_request.myanimelist)
            anilist_score = executor.submit(anilist.get_score, id_request.anilist)
            filmarks_score = executor.submit(filmarks.get_score, id_request.filmarks)
            anikore_score = executor.submit(anikore.get_score, id_request.anikore)

            results.append({
                "myanimelist": myanimelist_score.result(),
                "anilist": anilist_score.result(),
                "filmarks": filmarks_score.result(),
                "anikore": anikore_score.result(),
            })

    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
