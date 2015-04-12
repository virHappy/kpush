# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

import json
from flask import current_app, request
from netkit.contrib.tcp_client import TcpClient
from netkit.box import Box
from web.application import create_app
from share import proto


app = create_app()
app_ctx = app.test_request_context()
worker_client = TcpClient(Box, '115.28.224.64', 29000)


def setup():
    """
    小写更喜欢
    :return:
    """
    app_ctx.push()
    worker_client.connect()


def teardown():
    app_ctx.pop()


def test_register():
    req = dict()
    worker_client.write(dict(
        cmd=proto.CMD_REGISTER,
        body=json.dumps(req)
    ))

    print worker_client.read()
