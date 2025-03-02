import os
import re
import requests
from bs4 import BeautifulSoup
import json
from config import request_setting
from utils.error import error_report


class Filmarks:
    def __init__(self):
        self.url = "https://filmarks.com"

    def get_id(self, name: str):
        try:
            search_url = self.url + "/search/animes?q=" + name

            page = requests.get(
                search_url, headers=request_setting.real_headers, timeout=request_setting.timeout
            ).content

            soup = BeautifulSoup(page, "lxml")
            js_cassette_element = soup.select_one(".p-contents-grid .js-cassette")
            if js_cassette_element:
                data_mark = js_cassette_element.get("data-mark")
                data = json.loads(data_mark)
                anime_series_id = data.get("anime_series_id")
                anime_season_id = data.get("anime_season_id")
                
                if anime_series_id and anime_season_id:
                    return f"{anime_series_id}/{anime_season_id}"
                else:
                    return "Error"
            else:
                return "Error"
        except Exception as e:
            error_report(e, os.path.abspath(__file__))
            return "Error"

    def get_score(self, local_id: str):
        if local_id == "Error":
            return "None"

        try:
            search_url = self.url + "/animes/" + local_id

            page = requests.get(
                search_url, headers=request_setting.real_headers, timeout=request_setting.timeout
            ).content

            soup = BeautifulSoup(page, "lxml")


            fm_score = soup.find("div", attrs={"class": "c2-rating-l__text"}).string
            if fm_score == "-":
                score = -1
            else:
                score = float(fm_score) * 2


            title = soup.find("h2", attrs={"class": "p-content-detail__title"})
            title_text = title.get_text(strip=True) if title else "Unknown Title"


            og_description = soup.find("meta", attrs={"property": "og:description"})
            count = 0
            if og_description:
                content = og_description.get("content", "")

                match = re.search(r"レビュー数：(\d+)件", content)
                if match:
                    count = int(match.group(1))

            return title_text, score, count, local_id
        except Exception as e:
            error_report(e, os.path.abspath(__file__))
            return "Error"