import os

import requests
from bs4 import BeautifulSoup
from config import request_setting
from utils.error import error_report

class MyAnimeList:
    def __init__(self):
        self.url = "https://myanimelist.net"

    def get_id(self, name: str):
        try:
            # search_url = self.url + "/anime.php?q=" + name + "&cat=anime"
            search_url = self.url + "/search/all?q=" + name + "&cat=anime"

            page = requests.get(
                search_url, headers=request_setting.real_headers, timeout=request_setting.timeout
            ).content

            soup = BeautifulSoup(page, "lxml")
            mal_id = (
                soup.find("div", attrs={"class": "title"})
                .find("a", attrs={"class": "hoverinfo_trigger fw-b fl-l"})
                .get("id")
            )
            mal_id = mal_id[18 : len(mal_id)]

            return mal_id
        except Exception as e:
            error_report(e, os.path.abspath(__file__))
            return "Error"

    def get_score(self, local_id: str):
        if local_id == "Error":
            return "None"

        try:
            score_url = self.url + "/anime/" + str(local_id)
            page = requests.get(score_url, timeout=request_setting.timeout).content
            page_text = page.decode('utf-8', errors='replace')
            soup = BeautifulSoup(page_text, "lxml")

            mal_score = soup.find("div", attrs={"class": "score-label"}).string.strip()

            title_div = soup.find("h1", attrs={"class": "title-name"})
            title_text = title_div.get_text(strip=True) if title_div else "Unknown Title"

            count_span = soup.find("span", attrs={"itemprop": "ratingCount"})
            count = count_span.get_text(strip=True) if count_span else "0"

            if mal_score == "N/A":
                mal_score = -1

            return title_text, float(mal_score), int(count), local_id

        except Exception as e:
            error_report(e, os.path.abspath(__file__))
            return "Error"