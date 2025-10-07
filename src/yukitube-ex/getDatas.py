import json
import os
import requests
import urllib.parse
import datetime
from fastapi import Request
from typing import Any, Optional

from apiRequests import apirequest, apichannelrequest, apicommentsrequest
from APItimeoutError import APItimeoutError
from configs import configs

configs.init()
config, apicomments, apichannels = configs.config, configs.apicomments, configs.apichannels

def getBBSInfo(request: Request) -> str:
    return json.dumps([
        None,
        os.environ.get('RENDER_EXTERNAL_URL'),
        str(request.scope["headers"]),
        str(request.scope['router'])[39:-2]
    ])


number = 1

def getVideoData(videoid: str) -> list[Any]:
    # global logs
    # t = json.loads(apirequest(r"api/v1/videos/"+ urllib.parse.quote(videoid)))
    # if not t.get("formatStreams") or len(t["formatStreams"]) == 0:
    #     return "error"

    global number

    url = "https://ytstream-download-youtube-videos.p.rapidapi.com/dl"

    querystring = {"id": videoid}

    apikey: Optional[str] = ""
    if not config["apikey"] == "":
        apikey = config["apikey"]
    else:
        apikey = os.environ.get("apikey")

    headers: dict[str, Optional[str]] = {
        "x-rapidapi-key": apikey,
        "x-rapidapi-host": "ytstream-download-youtube-videos.p.rapidapi.com"
    }

    res: dict[str, Any] = json.loads(requests.get(url, headers=headers, params=querystring).text)

    redirectedUrl = requests.get(
        res["formats"][0]["url"],
        allow_redirects=False).headers["Location"]

    # return res.json()["formats"][0]["url"]
    # return [[{"id":i["videoId"],"title":i["title"],"authorId":i["authorId"],"author":i["author"]} for i in t["recommendedVideos"]],list(reversed([i["url"] for i in res["formats"]]))[:2],t["descriptionHtml"].replace("\n","<br>"),t["title"],t["authorId"],t["author"],t["authorThumbnails"][-1]["url"]]

    returnData: list[Any] = [
        [],
        [redirectedUrl],
        res["description"].replace("\n", "<br>"),
        res["title"],
        res["channelId"],
        res["channelTitle"],
        ""
    ]
    return returnData


def get_search(q: str, page: Optional[int]) -> list[Any]:
    errorlog: list[str] = []
    pageInt: int = 1
    if not page is None : pageInt = page
    try:
        response = apirequest(
            fr"api/v1/search?q={urllib.parse.quote(q)}&page={pageInt}&hl=jp")

        t = json.loads(response)

        results: list[Any] = []
        for item in t:
            try:
                results.append(parseSearch(item))
            except ValueError as ve:
                # エラー詳細をログに記録して、処理を続ける
                errorlog.append(f"Error processing item: {str(ve)}")
                continue  # エラーが発生した場合、そのアイテムをスキップ
        return results

    except json.JSONDecodeError:
        raise ValueError("Failed to decode JSON response.")
    except Exception as e:
        errorlog.append(f"API request error: {str(e)}")
        return [{"error": "API request error."}]


def parseSearch(i: dict[str, Any]) -> dict[str, Any]:
    if i["type"] == "video":
        return {
            "title": i["title"],
            "id": i["videoId"],
            "authorId": i["authorId"],
            "author": i["author"],
            "length": str(datetime.timedelta(seconds=i["lengthSeconds"])),
            "published": i["publishedText"],
            "type": "video"
        }
    elif i["type"] == "playlist":
        if not i["videos"]:
            raise ValueError("Playlist is empty.")
        return {
            "title": i["title"],
            "id": i["playlistId"],
            "thumbnail": i["videos"][0]["videoId"],
            "count": i["videoCount"],
            "type": "playlist"
        }
    else:  # type = "channel" またはその他
        thumbnail_url = (
            i["authorThumbnails"][-1]["url"]
            if i["authorThumbnails"][-1]["url"].startswith("https")
            else "https://" + i["authorThumbnails"][-1]["url"]
        )
        return {
            "author": i["author"],
            "id": i["authorId"],
            "thumbnail": thumbnail_url,
            "type": "channel"
        }


def getChannel(channelid: str) -> list[Any]:
    global apichannels
    t = json.loads(
        apichannelrequest(r"api/v1/channels/" +
                          urllib.parse.quote(channelid)))

    if t["latestVideos"] == []:
        print("APIがチャンネルを返しませんでした")
        apichannels.append(apichannels[0])
        apichannels.remove(apichannels[0])
        raise APItimeoutError("APIがチャンネルを返しませんでした")
    return [
        [
            {"title": i["title"],
             "id": i["videoId"],
             "authorId": t["authorId"],
             "author": t["author"],
             "published": i["publishedText"],
             "type": "video"} for i in t["latestVideos"]
        ], {
            "channelname": t["author"],
            "channelicon": t["authorThumbnails"][-1]["url"],
            "channelprofile": t["descriptionHtml"]
        }]


def getPlaylist(listid: str, page: str) -> list[Any]:
    t = json.loads(apirequest(r"/api/v1/playlists/" +
                              urllib.parse.quote(listid) +
                              "?page="+urllib.parse.quote(page)))["videos"]
    return [
        {
            "title": i["title"],
            "id": i["videoId"],
            "authorId": i["authorId"],
            "author": i["author"],
            "type": "video"}
        for i in t]


def getComments(videoid: str) -> list[Any]:
    t = json.loads(apicommentsrequest(r"api/v1/comments/" +
                                      urllib.parse.quote(videoid) +
                                      "?hl=jp"))["comments"]
    return [
        {"author": i["author"],
         "authoricon": i["authorThumbnails"][-1]["url"],
         "authorid": i["authorId"],
         "body": i["contentHtml"].replace("\n", "<br>")}
        for i in t]


def getReplies(videoid: str, key: str) -> dict[str, Any]:
    t = json.loads(apicommentsrequest(
          fr"api/v1/comments/{videoid}?hmac_key={key}&hl=jp&format=html"))["contentHtml"]
    return t


def getLevel(word: str) -> int:
    for i1 in range(1, 13):
        with open(f'Level{i1}.txt', 'r', encoding='UTF-8', newline='\n') as f:
            if word in [i2.rstrip("\r\n") for i2 in f.readlines()]:
                return i1
    return 0
