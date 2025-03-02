import os

import requests
from config import request_setting
from bs4 import BeautifulSoup

from utils.error import error_report


class Anikore:
    def __init__(self):
        self.url = "https://www.anikore.jp"

    def get_id(self, name: str):
        try:
            search_url = self.url + "/anime_title/" + name
            page = requests.get(
                search_url, headers=request_setting.real_headers, timeout=request_setting.timeout
            ).content
            soup = BeautifulSoup(page, "lxml")

            id_url = soup.find("div", attrs={"class": "l-searchPageRanking_unit"}).a[
                "href"
            ]
            ani_id = id_url[7 : len(id_url) - 1]
            return ani_id
        except Exception as e:
            error_report(e, os.path.abspath(__file__))
            return "Error"

    def get_score(self, local_id: str):
        try:
            if local_id == "Error":
                return "None"

            score_url = self.url + "/anime/" + local_id
            page = requests.get(
                score_url, headers=request_setting.real_headers, timeout=10
            ).content
            soup = BeautifulSoup(page, "lxml")

            score = soup.find(
                "div",
                attrs={"class": "l-animeDetailHeader_pointAndButtonBlock_starBlock"},
            ).strong.string
            score = float(score) * 2

            title = soup.find(
                "div", attrs={"class": "l-animeDetailHeader_imageBlock"}
            ).find_next_sibling("h1").text.strip()

            count_span = soup.find(
                "span", attrs={"class": "l-animeDetailHeader_pointAndButtonBlock_starBlock_count"}
            ).find("a")
            count = count_span.get_text(strip=True) if count_span else "0"

            return title, score, int(count), local_id
        except Exception as e:
            error_report(e, os.path.abspath(__file__))
            return "Error"