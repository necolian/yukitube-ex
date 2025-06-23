import json
import requests
import urllib.parse
import time
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi import Response, Cookie, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.responses import RedirectResponse as redirect
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Union
from fastapi.templating import Jinja2Templates

from APItimeoutError import APItimeoutError
from readFile import readFile
from check_cokie import check_cokie
from getDatas import get_data, get_search, get_channel
from getDatas import get_playlist, get_comments, get_level, get_info
from cache import cache

config = json.loads(readFile("./config.json"))
apis = readFile("./src/apis").splitlines()

url = requests.get(r'https://raw.githubusercontent.com/mochidukiyukimi/yuki-youtube-instance/main/instance.txt').text.rstrip()

apichannels = []
apicomments = []
[[apichannels.append(i), apicomments.append(i)] for i in apis]


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/css", StaticFiles(directory="./src/pages/assets/css"), name="static")
app.add_middleware(GZipMiddleware, minimum_size=1000)
template = Jinja2Templates(directory="./src/pages/templates").TemplateResponse


@app.get("/", response_class=HTMLResponse)
def home(response: Response,
         request: Request,
         yuki: Union[str] = Cookie(None)):

    if check_cokie(yuki):
        response.set_cookie("yuki", "True", max_age=60 * 60 * 24 * 7)
        return template("home.html", {"request": request})

    print(check_cokie(yuki))
    return template("index.html", {"request": request})


@app.get('/watch', response_class=HTMLResponse)
def video(v: str,
          response: Response,
          request: Request,
          yuki: Union[str] = Cookie(None),
          proxy: Union[str] = Cookie(None)):

    if not(check_cokie(yuki)):
        return redirect("/")

    response.set_cookie(key="yuki", value="True", max_age=7*24*60*60)
    videoid = v
    t = get_data(videoid)

    # if (t == "error"):
    #   return template("error.html",{"request": request,"status_code":"502 - Bad Gateway","message": "ビデオ取得時のAPIエラー、再読み込みしてください。","home":False},status_code=502)

    response.set_cookie("yuki", "True", max_age=60 * 60 * 24 * 7)
    return template('video.html', {
        "request": request,
        "videoid": videoid,
        "videourls": t[1],
        "res": t[0],
        "description": t[2],
        "videotitle": t[3],
        "authorid": t[4],
        "authoricon": t[6],
        "author": t[5],
        "proxy": proxy})

    # return RedirectResponse(t)


@app.get("/search", response_class=HTMLResponse)
def search(q: str,
           response: Response,
           request: Request,
           page: Union[int, None] = 1,
           yuki: Union[str] = Cookie(None),
           proxy: Union[str] = Cookie(None)):

    # クッキーの検証
    if not check_cokie(yuki):
        return redirect("/")
    response.set_cookie("yuki", "True", max_age=60 * 60 * 24 * 7)

    try:
        results = get_search(q, page)

        # resultsがdict型の場合の処理
        if isinstance(results, dict):
            error_detail = results.get("error", "Unknown error occurred.")
            raise HTTPException(
                status_code=500,
                detail=f"Search API error: {error_detail}")
            return template("APIwait.html", {
                "request": request
            }, status_code=500)

        # 検索成功時のテンプレスキーマに結果を渡す
        return template("search.html", {
            "request": request,
            "results": results,
            "word": q,
            "next": f"/search?q={q}&page={page + 1}",
            "proxy": proxy})

    except HTTPException as e:
        # HTTP例外としてハンドリング
        raise e
    except Exception as e:
        # 他の予期しない例外を処理
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/hashtag/{tag}")
def hashtag(tag: str,
            response: Response,
            request: Request,
            page: Union[int, None] = 1,
            yuki: Union[str] = Cookie(None)):

    if not(check_cokie(yuki)):
        return redirect("/")

    return redirect(f"/search?q={tag}")


@app.get("/channel/{channelid}", response_class=HTMLResponse)
def channel(channelid: str,
            response: Response,
            request: Request,
            yuki: Union[str] = Cookie(None),
            proxy: Union[str] = Cookie(None)):

    if not(check_cokie(yuki)):
        return redirect("/")
    response.set_cookie("yuki", "True", max_age=60 * 60 * 24 * 7)

    t = get_channel(channelid)
    return template("channel.html", {
        "request": request,
        "results": t[0],
        "channelname": t[1]["channelname"],
        "channelicon": t[1]["channelicon"],
        "channelprofile": t[1]["channelprofile"],
        "proxy": proxy})


@app.get("/answer", response_class=HTMLResponse)
def set_cokie(q: str):
    t = get_level(q)
    if t > 5:
        return f"level{t}\n推測を推奨する"
    elif t == 0:
        return "level12以上\nほぼ推測必須"
    return f"level{t}\n覚えておきたいレベル"


@app.get("/playlist", response_class=HTMLResponse)
def playlist(list: str,
             response: Response,
             request: Request,
             page: Union[int, None] = 1,
             yuki: Union[str] = Cookie(None),
             proxy: Union[str] = Cookie(None)):

    if not(check_cokie(yuki)):
        return redirect("/")
    response.set_cookie("yuki", "True", max_age=60 * 60 * 24 * 7)

    return template("search.html", {
        "request": request,
        "results": get_playlist(list, str(page)),
        "word": "",
        "next": f"/playlist?list={list}",
        "proxy": proxy})


@app.get("/info", response_class=HTMLResponse)
def viewlist(response: Response,
             request: Request,
             yuki: Union[str] = Cookie(None)):

    global apis, apichannels, apicomments

    if not(check_cokie(yuki)):
        return redirect("/")
    response.set_cookie("yuki", "True", max_age=60 * 60 * 24 * 7)

    return template("info.html", {
        "request": request,
        "Youtube_API": apis[0],
        "Channel_API": apichannels[0],
        "Comments_API": apicomments[0]})


@app.get("/api/info")
def infoApi(request: Request):
    return {
        "Youtube_API": apis[0],
        "Channel_API": apichannels[0],
        "Comments_API": apicomments[0]
    }


@app.get("/suggest")
def suggest(keyword: str):
    return [i[0] for i in json.loads(
        requests.get(
            r"http://www.google.com/complete/search?client=youtube&hl=ja&ds=yt&q=" +
            urllib.parse.quote(keyword)).text[19:-1])[1]]


@app.get("/comments")
def comments(request: Request, v: str):
    return template("comments.html", {
        "request": request,
        "comments": get_comments(v)
    })


@app.get("/thumbnail")
def thumbnail(v: str):
    return Response(content=requests.get(
        fr"https://img.youtube.com/vi/{v}/0.jpg")
                    .content,
                    media_type=r"image/jpeg")


@app.get("/bbs", response_class=HTMLResponse)
def view_bbs(request: Request,
             name: Union[str, None] = "",
             seed: Union[str, None] = "",
             channel: Union[str, None] = "main",
             verify: Union[str, None] = "false",
             yuki: Union[str] = Cookie(None)):

    if not(check_cokie(yuki)):
        return redirect("/")

    return HTMLResponse(
        requests.get(
            fr"{url}bbs?name={urllib.parse.quote(name)}&seed={urllib.parse.quote(seed)}&channel={urllib.parse.quote(channel)}&verify={urllib.parse.quote(verify)}",
            cookies={"yuki": "True"}).text)


@cache(seconds=5)
def bbsapi_cached(verify, channel):
    return requests.get(
        fr"{url}bbs/api?t={urllib.parse.quote(str(int(time.time()*1000)))}&verify={urllib.parse.quote(verify)}&channel={urllib.parse.quote(channel)}",
        cookies={"yuki": "True"}).text


@app.get("/bbs/api", response_class=HTMLResponse)
def bbs_api(request: Request,
            t: str,
            channel: Union[str, None] = "main",
            verify: Union[str, None] = "false"):

    print(fr"{url}bbs/api?t={urllib.parse.quote(t)}&verify={urllib.parse.quote(verify)}&channel={urllib.parse.quote(channel)}")
    return bbsapi_cached(verify, channel)


@app.get("/bbs/result")
def write_bbs(request: Request,
              name: str = "",
              message: str = "",
              seed: Union[str, None] = "",
              channel: Union[str, None] = "main",
              verify: Union[str, None] = "false",
              yuki: Union[str] = Cookie(None)):

    if not(check_cokie(yuki)):
        return redirect("/")

    t = requests.get(fr"{url}bbs/result?name={urllib.parse.quote(name)}&message={urllib.parse.quote(message)}&seed={urllib.parse.quote(seed)}&channel={urllib.parse.quote(channel)}&verify={urllib.parse.quote(verify)}&info={urllib.parse.quote(get_info(request))}",
                     cookies={"yuki": "True"},
                     allow_redirects=False)

    if t.status_code != 307:
        return HTMLResponse(t.text)
    return redirect(f"/bbs?name={urllib.parse.quote(name)}&seed={urllib.parse.quote(seed)}&channel={urllib.parse.quote(channel)}&verify={urllib.parse.quote(verify)}")


@cache(seconds=30)
def how_cached():
    return requests.get(fr"{url}bbs/how").text


@app.get("/bbs/how", response_class=PlainTextResponse)
def view_commonds(request: Request, yuki: Union[str] = Cookie(None)):

    if not(check_cokie(yuki)):
        return redirect("/")

    return how_cached()


@app.get("/load_instance")
def instances():
    global url
    url = requests.get(r'https://raw.githubusercontent.com/mochidukiyukimi/yuki-youtube-instance/main/instance.txt').text.rstrip()


@app.exception_handler(404)
def notFoundPage(request: Request, __):
    return template("error.html", {
        "request": request,
        "status_code": "404 - Not Found",
        "message": "未実装か、存在しないページです。",
        "home": True},
        status_code=404)


@app.exception_handler(500)
def waitPage(request: Request, __):
    return template("APIwait.html", {"request": request}, status_code=500)


@app.exception_handler(APItimeoutError)
def APIwait(request: Request, exception: APItimeoutError):
    return template("APIwait.html", {"request": request}, status_code=500)


uvicorn.run(app, port=3000, host="0.0.0.0")
