import json
import os
import requests
import urllib.parse
import datetime

from apiRequests import apirequest, apichannelrequest, apicommentsrequest
from APItimeoutError import APItimeoutError


def get_info(request):
    global version
    return json.dumps([
        version,
        os.environ.get('RENDER_EXTERNAL_URL'),
        str(request.scope["headers"]),
        str(request.scope['router'])[39:-2]
    ])


number = 1


def get_data(videoid):
    # global logs
    # t = json.loads(apirequest(r"api/v1/videos/"+ urllib.parse.quote(videoid)))
    # if not t.get("formatStreams") or len(t["formatStreams"]) == 0:
    #     return "error"

    global number

    url = "https://ytstream-download-youtube-videos.p.rapidapi.com/dl"

    querystring = {"id": videoid}

    apikey = os.environ.get("apikey")

    headers = {
        "x-rapidapi-key": apikey,
        "x-rapidapi-host": "ytstream-download-youtube-videos.p.rapidapi.com"
    }

    res = json.loads(requests.get(url, headers=headers, params=querystring).text)

    redirectedUrl = requests.get(
        res["formats"][0]["url"],
        allow_redirects=False).headers["Location"]

    # return res.json()["formats"][0]["url"]
    # return [[{"id":i["videoId"],"title":i["title"],"authorId":i["authorId"],"author":i["author"]} for i in t["recommendedVideos"]],list(reversed([i["url"] for i in res["formats"]]))[:2],t["descriptionHtml"].replace("\n","<br>"),t["title"],t["authorId"],t["author"],t["authorThumbnails"][-1]["url"]]
    return [
        [],
        [redirectedUrl],
        res["description"].replace("\n", "<br>"),
        res["title"],
        res["channelId"],
        res["channelTitle"],
        ""
    ]


def get_search(q, page):
    errorlog = []
    try:
        response = apirequest(
            fr"api/v1/search?q={urllib.parse.quote(q)}&page={page}&hl=jp")

        t = json.loads(response)

        results = []
        for item in t:
            try:
                results.append(load_search(item))
            except ValueError as ve:
                # エラー詳細をログに記録して、処理を続ける
                errorlog.append(f"Error processing item: {str(ve)}")
                continue  # エラーが発生した場合、そのアイテムをスキップ
        return results

    except json.JSONDecodeError:
        raise ValueError("Failed to decode JSON response.")
    except Exception as e:
        errorlog.append(f"API request error: {str(e)}")
        return {"error": "API request error."}


def load_search(i):
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


def get_channel(channelid):
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


def get_playlist(listid, page):
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


def get_comments(videoid):
    t = json.loads(apicommentsrequest(r"api/v1/comments/" +
                                      urllib.parse.quote(videoid) +
                                      "?hl=jp"))["comments"]
    return [
        {"author": i["author"],
         "authoricon": i["authorThumbnails"][-1]["url"],
         "authorid": i["authorId"],
         "body": i["contentHtml"].replace("\n", "<br>")}
        for i in t]


def get_replies(videoid, key):
    t = json.loads(apicommentsrequest(
          fr"api/v1/comments/{videoid}?hmac_key={key}&hl=jp&format=html"))
    ["contentHtml"]
    return t


def get_level(word):
    for i1 in range(1, 13):
        with open(f'Level{i1}.txt', 'r', encoding='UTF-8', newline='\n') as f:
            if word in [i2.rstrip("\r\n") for i2 in f.readlines()]:
                return i1
    return 0
