import json
from readFile import readFile
from typing import Any

class configs ():

    config: dict[str, Any] = {} 

    apichannels: list[str] = []
    apicomments: list[str] = []
    apis: list[str] = []

    def __init__(self):
        self.config = json.loads(readFile("config.json"))
        self.apis = self.config["apis"]
        
        for i in self.apis:
            self.apichannels.append(i)
            self.apicomments.append(i)
