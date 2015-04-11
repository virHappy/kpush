# -*- coding: utf-8 -*-
"""
仅存放如下类型配置: flask自身配置，flask.ext配置，blueprint之间共享的配置
至于仅在单独模块下使用的，放到各自模块下即可
"""

import os

BASE_DIR = os.path.dirname(__file__)

DEV_MODE = 'DEV'
MODE = os.environ.get('MODE')

DEBUG = MODE == DEV_MODE

# 不能随便修改。用作 session、user.password 的密钥
SECRET_KEY = 'tmp_secret_key'

BLUEPRINTS = (
    ('web.views.frontend', ''),
)

# flask-sqlalchemy
SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % os.path.join(BASE_DIR, 'db.sqlite')
#SQLALCHEMY_DATABASE_URI = 'mysql://root:@localhost/flask_dpl'
SQLALCHEMY_ECHO = False

# admin_user
SESSION_KEY_ADMIN_USERNAME = 'admin_username'
