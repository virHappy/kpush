# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from flask import current_app, request
from web.application import create_app


class TestWorker():
    app = None
    app_ctx = None

    def __init__(self):
        self.app = create_app()
        self.app_ctx = self.app.test_request_context()

    def setUp(self):
        self.app_ctx.push()

    def tearDown(self):
        self.app_ctx.pop()

    def test_register(self):
        pass
