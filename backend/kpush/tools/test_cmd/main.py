# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from flask import current_app, request
from netkit.contrib.tcp_client import TcpClient
from netkit.box import Box
from web.application import create_app
from share import proto


class TestWorker():
    app = None
    app_ctx = None
    worker_client = None

    def __init__(self):
        self.app = create_app()
        self.app_ctx = self.app.test_request_context()
        self.worker_client = TcpClient(Box, '115.28.224.64', 29000)

    def setUp(self):
        self.app_ctx.push()
        self.worker_client.connect()

    def tearDown(self):
        self.app_ctx.pop()

    def test_register(self):
        from share.net_pb2 import ReqUserRegister
        req = ReqUserRegister()
        self.worker_client.write(dict(
            cmd=proto.CMD_REGISTER,
            body=req.SerializeToString()
        ))

        print self.worker_client.read()
