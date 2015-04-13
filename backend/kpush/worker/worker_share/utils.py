# -*- coding: utf-8 -*-

import json
import hashlib
from flask import current_app


def pack_data(json_data):
    """
    :param json_data:
    :return:
    """

    data = json.dumps(json_data)
    sign = hashlib.md5('|'.join([current_app.config['SECRET_KEY'], data])).hexdigest()

    return json.dumps(dict(
        data=data,
        sign=sign,
    ))


def unpack_data(body):
    json_body = json.loads(body)

    data = json_body.get("data")
    sign = json_body.get("sign")

    calc_sign = hashlib.md5('|'.join([current_app.config['SECRET_KEY'], data])).hexdigest()

    if sign != calc_sign:
        return None

    return json.loads(data)
