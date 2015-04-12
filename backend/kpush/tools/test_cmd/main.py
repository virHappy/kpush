# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from web.application import create_app


def setup():
    print 'setup'


def teardown():
    print 'teardown'


def app_request_ctx(func):
    import functools
    @functools.wraps(func)
    def func_wrapper(*args, **kwargs):

        return func(*args, **kwargs)
    return func_wrapper


def test_register():
    pass
