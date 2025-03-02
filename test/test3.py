import sys
import os
from concurrent.futures import ThreadPoolExecutor

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from external.myanimelist import MyAnimeList
from external.anilist import AniList
from external.filmarks import Filmarks
from external.anikore import Anikore

name = 'ババンババンバンバンパイア'

def get_score_from_myanimelist():
    myanimelist = MyAnimeList()
    return f"myanimelist: {myanimelist.get_score(myanimelist.get_id(name))}"

def get_score_from_filmarks():
    filmarks = Filmarks()
    return f"filmarks: {filmarks.get_score(filmarks.get_id(name))}"

def get_score_from_anilist():
    anilist = AniList()
    return f"anilist: {anilist.get_score(anilist.get_id(name))}"

def get_score_from_anikore():
    anikore = Anikore()
    return f"anikore: {anikore.get_score(anikore.get_id(name))}"

with ThreadPoolExecutor() as executor:
    results = executor.map(lambda f: f(), 
                           [get_score_from_myanimelist, 
                            get_score_from_filmarks, 
                            get_score_from_anilist, 
                            get_score_from_anikore])

for result in results:
    print(result)