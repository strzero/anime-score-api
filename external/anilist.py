import os

import requests
import json
from config import request_setting
from utils.error import error_report


class AniList:
    def __init__(self):
        self.api_url = "https://graphql.anilist.co"

    def get_id(self, name: str):
        try:
            query = """
            query ($id: Int, $search: String) {
                Media (id: $id, search: $search,type: ANIME) {
                    id
                    title {
                        romaji
                    }
                    meanScore
                    averageScore
                    stats {
                        scoreDistribution {
                            amount
                            score
                        }
                    }
                }
            }
            """
            variables = {"search": name}

            anl_id = requests.post(
                self.api_url,
                json={"query": query, "variables": variables},
                timeout=request_setting.timeout,
            )
            return str(json.loads(anl_id.content)["data"]["Media"]["id"])
        except Exception as e:
            error_report(e, os.path.abspath(__file__))
            return "Error"

    def get_score(self, local_id: str):
        if local_id == "Error":
            return "None"

        try:
            query = """
            query ($id: Int) {
                Media (id: $id, type: ANIME) {
                    id
                    title {
                        romaji
                        english
                        native
                    }
                    meanScore
                    averageScore
                    stats {
                        scoreDistribution {
                            amount
                            score
                        }
                    }
                }
            }
            """
            variables = {"id": int(local_id)}
            anl_score = requests.post(
                self.api_url,
                json={"query": query, "variables": variables},
                timeout=request_setting.timeout,
            )


            data = json.loads(anl_score.content)["data"]["Media"]

            if data["title"].get("english"):
                title = data["title"]["english"]
            elif data["title"].get("native"):
                title = data["title"]["native"]
            else:
                title = data["title"]["romaji"]

            score = (
                data["meanScore"] + data["averageScore"]
            ) / 20 if data["meanScore"] and data["averageScore"] else (
                data["meanScore"] / 10 if data.get("meanScore") else data["averageScore"] / 10
            )

            count = sum(item["amount"] for item in data["stats"]["scoreDistribution"])

            return title, score, count, local_id
        except Exception as e:
            error_report(e, os.path.abspath(__file__))
            return "Error"

