"""
max_api_wait_time = 10
max_time = 20
apis = [f"https://invidious.catspeed.cc/",f"https://youtube.privacyplz.org/",r"https://invidious.jing.rocks/",r"https://inv.nadeko.net/",r"https://invidious.nerdvpn.de/",r"https://invidious.privacyredirect.com/",r"https://youtube.076.ne.jp/",r"https://vid.puffyan.us/",r"https://inv.riverside.rocks/",r"https://invidio.xamh.de/",r"https://y.com.sb/",r"https://invidious.sethforprivacy.com/",r"https://invidious.tiekoetter.com/",r"https://inv.bp.projectsegfau.lt/",r"https://inv.vern.cc/",r"https://invidious.nerdvpn.de/",r"https://inv.privacy.com.de/",r"https://invidious.rhyshl.live/",r"https://invidious.slipfox.xyz/",r"https://invidious.weblibre.org/",r"https://invidious.namazso.eu/"]
apivideos = {"related":"https://youtube-v31.p.rapidapi.com/search","info":"https://youtube-data-api-v33.p.rapidapi.com"}
rapidapi_apikey = os.getenv("rapidapi_apikey","couldn't find")
"""

from fastapi import FastAPI, Request ,Cookie
from fastapi.responses import HTMLResponse
from fastapi.staticfales import StaticFiles
from fastapi.templating import Jinja2Templates
import json

app = FastAPI()
template = Jinja2Templates(directory="templates").TemplateResponse

version = "3.0.0"

app.mount("/css",StaticFiles(directory="css"),name="css")
app.mount("/blog",StaticFiles(directory="blog"),name="blog")

@app.get("/")
def route(req: req, res: res, yuki: str = "false"):
    if not yuki:
        return template("word.html",{"request": req})
    return template("home.html",{"request":req,"version": version})