# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

import time
from netkit.contrib.tcp_client import TcpClient
from netkit.box import Box
from web.application import create_app
from share import proto
from share.utils import pack_data


worker_client = TcpClient(Box, '115.28.224.64', 29100)


def login():
    req = dict(
        uid=199,
        key='4b91e0cd5d534a8c9cb41d2517415260',
        os='android',
        os_version=33,
        sdk_version=22,
    )
    worker_client.write(dict(
        cmd=proto.CMD_LOGIN,
        body=pack_data(req)
    ))

    box = worker_client.read()
    print 'box:', box
    if not box:
        return False

    # worker_client.write(dict(
    #     cmd=proto.CMD_SET_ALIAS_AND_TAGS,
    #     body=pack_data(dict(
    #         alias='dante',
    #     ))
    # ))
    #
    # box = worker_client.read()
    # print 'box:', box
    # if not box:
    #     return False

    return True


def wait_notifications():
    while True:
        box = worker_client.read()
        print 'box:', type(box), repr(box)
        if not box:
            return


def main():
    while True:
        try:
            worker_client.connect()
            if not login():
                raise ValueError('connection closed')
            wait_notifications()
            print 'connection closed'
        except Exception, e:
            print 'exc occur. e: %s' % e

        time.sleep(1)

if __name__ == '__main__':
    app = create_app()
    with app.test_request_context():
        main()
