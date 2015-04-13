# -*- coding: utf-8 -*-
"""
仅存放如下类型配置: flask自身配置，flask.ext配置，blueprint之间共享的配置
至于仅在单独模块下使用的，放到各自模块下即可
"""

import os
import logging

BASE_DIR = os.path.dirname(__file__)

DEV_MODE = 'DEV'
MODE = os.environ.get('MODE')

DEBUG = MODE == DEV_MODE

# 不能随便修改。用作 session、user.password 的密钥
SECRET_KEY = "4y%zgs*074ibnacl31w2d!l-o$3qaa+lu)w25g*0#e6i_qt1*#305^gij7a+js$i"

BLUEPRINTS = (
    ('web.views.frontend', ''),
)


class RequireDebugOrNot(logging.Filter):
    _need_debug = False

    def __init__(self, need_debug, *args, **kwargs):
        super(RequireDebugOrNot, self).__init__(*args, **kwargs)
        self._need_debug = need_debug
        
    def filter(self, record):
        from flask import current_app
        return current_app.debug if self._need_debug else not current_app.debug

WEB_LOG_FILE_PATH = os.path.join(BASE_DIR, "logs/web.log")
WORKER_LOG_FILE_PATH = os.path.join(BASE_DIR, "logs/worker.log")
NETKIT_LOG_FILE_PATH = os.path.join(BASE_DIR, "logs/netkit.log")
MAPLE_LOG_FILE_PATH = os.path.join(BASE_DIR, "logs/maple.log")

LOG_FORMAT = '\n'.join((
    '/' + '-' * 80,
    '[%(levelname)s][%(asctime)s][%(process)d:%(thread)d][%(filename)s:%(lineno)d %(funcName)s]:',
    '%(message)s',
    '-' * 80 + '/',
))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,

    'formatters': {
        'standard': {
            'format': LOG_FORMAT,
        },
    },

    'filters': {
        'require_debug_false': {
            '()': RequireDebugOrNot,
            'need_debug': False,
        },
        'require_debug_true': {
            '()': RequireDebugOrNot,
            'need_debug': True,
        },
    },

    'handlers': {
        'flylog': {
            'level': 'CRITICAL',
            'class': 'flylog.FlyLogHandler',
            'formatter': 'standard',
            'source': os.path.basename(BASE_DIR),
        },
        'maple_flylog': {
            'level': 'ERROR',
            'class': 'flylog.FlyLogHandler',
            'formatter': 'standard',
            'source': os.path.basename(BASE_DIR),
        },
        'web_rfile': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': WEB_LOG_FILE_PATH,
            'maxBytes': 1024 * 1024 * 500,  # 500 MB
            'backupCount': 5,
        },
        'worker_rfile': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': WORKER_LOG_FILE_PATH,
            'maxBytes': 1024 * 1024 * 500,  # 500 MB
            'backupCount': 5,
        },
        'netkit_rfile': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': NETKIT_LOG_FILE_PATH,
            'maxBytes': 1024 * 1024 * 500,  # 500 MB
            'backupCount': 5,
        },
        'maple_rfile': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': MAPLE_LOG_FILE_PATH,
            'maxBytes': 1024 * 1024 * 500,  # 500 MB
            'backupCount': 5,
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'filters': ['require_debug_true'],
        },
    },

    'loggers': {
        'web': {
            'handlers': ['console', 'web_rfile', 'flylog'],
            'level': 'DEBUG',
            'propagate': False
        },
        'worker': {
            'handlers': ['console', 'worker_rfile', 'flylog'],
            'level': 'DEBUG',
            'propagate': False
        },
        'netkit': {
            'handlers': ['console', 'netkit_rfile', 'flylog'],
            'level': 'DEBUG',
            'propagate': False
        },
        'maple': {
            'handlers': ['console', 'maple_rfile', 'maple_flylog'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}

LOGGER_NAME = 'web'

# flask-sqlalchemy
SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % os.path.join(BASE_DIR, 'db.sqlite')
#SQLALCHEMY_DATABASE_URI = 'mysql://root:@localhost/flask_dpl'
SQLALCHEMY_ECHO = False

# admin_user
SESSION_KEY_ADMIN_USERNAME = 'admin_username'

# mongodb
MONGO_URL = 'mongodb://admin:admin@127.0.0.1:27017/kpush'