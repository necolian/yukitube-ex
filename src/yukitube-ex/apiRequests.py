import time
import requests
import json

from APItimeoutError import APItimeoutError
from configs import configs

config = configs.config

[apis, apicomments, apichannels] = [configs.apis, configs.apicomments, configs.apichannels]


def is_json(json_str: str) -> bool:
    result = False
    try:
        json.loads(json_str)
        result = True
    except json.JSONDecodeError:
        pass
    return result


def apirequest(url: str) -> str:
    global apis
    global config
    starttime = time.time()
    for api in apis:
        if time.time() - starttime >= config["max_time"] - 1:
            break
        try:
            res = requests.get(api+url, timeout=config["max_api_wait_time"])
            if res.status_code == 200 and is_json(res.text):
                print(api+url)
                return res.text
            else:
                print(f"エラー:{api}")
                apis.append(api)
                apis.remove(api)
        except:
            print(f"タイムアウト:{api}")
            apis.append(api)
            apis.remove(api)
    raise APItimeoutError("APIがタイムアウトしました")


def apichannelrequest(url: str) -> str:
    global apichannels
    global config
    starttime = time.time()
    for api in apichannels:
        if time.time() - starttime >= config["max_time"] - 1:
            break
        try:
            res = requests.get(api+url, timeout=config["max_api_wait_time"])
            if res.status_code == 200 and is_json(res.text):
                return res.text
            else:
                print(f"エラー:{api}")
                apichannels.append(api)
                apichannels.remove(api)
        except:
            print(f"タイムアウト:{api}")
            apichannels.append(api)
            apichannels.remove(api)
    raise APItimeoutError("APIがタイムアウトしました")


def apicommentsrequest(url: str) -> str:
    global apicomments
    global config
    starttime = time.time()
    for api in apicomments:
        if time.time() - starttime >= config["max_time"] - 1:
            break
        try:
            res = requests.get(api+url, timeout=config["max_api_wait_time"])
            if res.status_code == 200 and is_json(res.text):
                return res.text
            else:
                print(f"エラー:{api}")
                apicomments.append(api)
                apicomments.remove(api)
        except:
            print(f"タイムアウト:{api}")
            apicomments.append(api)
            apicomments.remove(api)
    raise APItimeoutError("APIがタイムアウトしました")

