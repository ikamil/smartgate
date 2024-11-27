import requests
from aiohttp import payload

from .creds import *
import base64, hmac, json, hashlib
import logging
from .models import *
import time
URL = "https://eu-apia.coolkit.cc/v2/"


def ewelink_auth() -> str:
    creds = dict(email=APP_EMAIL, password=APP_PASSWORD, countryCode="+7")
    sign = base64.b64encode(hmac.new(APP_SECRET, msg=json.dumps(creds).encode(), digestmod=hashlib.sha256).digest()).decode()
    session = requests.post(f"{URL}user/login", headers={"Authorization": f"Sign {sign}", "x-ck-appid": APP_ID}, json=creds).json()
    logging.warning(session)
    return session.get("data", {}).get("at")


def post(token, json):
    return requests.post(f"{URL}device/thing/status", headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, json=json).json()


def ewelink_on(token: str, dev: str):
    switch = {"type": 1, "id": dev, "params": {"switches": [{"switch": "on", "outlet": 0}]}}
    if not token:
        token = ewelink_auth()
    res = post(token, switch)
    if "token" in res["msg"] or res["error"] != 0:
        token = ewelink_auth()
        res = post(token, switch)
    logging.warning(res)
    return res


def open_close(loc: Location, do_open: bool = True):
    def set_status(status, token, payload):
        loc.status = status
        if token:
            loc.token = token
        loc.changed = now()
        loc.save()
        event = Event(location=loc, status=status, owner=loc.owner, payload=payload)
        event.save()

    STATUS = "OPEN" if do_open else "CLOSED"
    ACTION = "OPENING" if do_open else "CLOSING"
    WAIT = "CLOSING" if do_open else "OPENING"

    if loc.status not in (STATUS, ACTION):
        if loc.status == WAIT:
            time.sleep(1)
        set_status(ACTION, None, dict(device=loc.device))
        res = ewelink_on(loc.token, loc.device)
        if res["error"]:
            set_status("ERROR", loc.token, res)
        else:
            set_status(STATUS, loc.token, res)