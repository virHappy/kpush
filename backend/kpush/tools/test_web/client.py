# -*- coding: utf-8 -*-

import requests
from share.utils import pack_data, unpack_data


def test_alloc_server():
    url = 'http://115.28.224.64:7555/server/alloc'

    post_body = pack_data(
        dict(
            appkey='7d357c9b4ce1414fb27f077b54fb5a8f',
            channel='M',
            device_id='234234',
            device_name='fefer',
        )
    )

    rsp = requests.post(url, post_body)

    print rsp.text

if __name__ == '__main__':
    test_alloc_server()
