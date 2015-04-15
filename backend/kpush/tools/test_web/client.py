# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

import requests
from web.application import create_app
from share.utils import pack_data, unpack_data


def test_alloc_server():
    # url = 'http://115.28.224.64:7555/server/alloc'
    url = 'http://127.0.0.1:5000/server/alloc'

    post_body = pack_data(
        dict(
            appkey='7d357c9b4ce1414fb27f077b54fb5a8f',
            channel='M',
            device_id='23423',
            device_name='fefer',
        )
    )

    rsp = requests.post(url, post_body)

    print rsp.text

if __name__ == '__main__':
    app = create_app()
    with app.test_request_context():
        test_alloc_server()
