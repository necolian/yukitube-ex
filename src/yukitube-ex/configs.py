import json
from readFile import readFile
from typing import Any

class configs:
    config: dict[str, Any] = {}
    apichannels: list[str] = []
    apicomments: list[str] = []
    apis: list[str] = []

    @classmethod
    def init(cls):
        cls.config = json.loads(readFile("config.json"))
        cls.apis = cls.config["apis"]
        cls.apichannels = list(cls.apis)
        cls.apicomments = list(cls.apis)
        