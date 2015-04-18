# -*- coding: utf-8 -*-
import json
import hashlib
from utils import get_appinfo_by_appkey


def unpack_api_data(body):
    if not body:
        return None, None

    json_body = json.loads(body)

    appkey = json_body.get("appkey")
    data = json_body.get("data")
    sign = json_body.get("sign")

    appinfo = get_appinfo_by_appkey(appkey)
    if not appinfo:
        return None, None

    appsecret = appinfo['appsecret']

    calc_sign = hashlib.md5('|'.join([appsecret, appkey, data])).hexdigest()

    if sign != calc_sign:
        return appinfo, None

    return appinfo, json.loads(data)
