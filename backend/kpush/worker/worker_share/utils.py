# -*- coding: utf-8 -*-

import json
import hashlib
from flask import current_app


def pack_content(json_content):
    """
    :param json_content:
    :return:
    """

    content = json.dumps(json_content)
    sign = hashlib.md5('|'.join([current_app.config['SECRET_KEY'], content])).hexdigest()

    return json.dumps(dict(
        content=content,
        sign=sign,
    ))


def unpack_content(body):
    json_body = json.loads(body)

    content = json_body.get("content")
    sign = json_body.get("sign")

    calc_sign = hashlib.md5('|'.join([current_app.config['SECRET_KEY'], content])).hexdigest()

    if sign != calc_sign:
        return None

    return json.loads(content)
