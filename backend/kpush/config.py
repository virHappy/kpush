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

SECRET_KEY = "tmp_secret"

BLUEPRINTS = (
    ('web.views.frontend', ''),
)

LOGGER_NAME = 'web'


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

# admin_user
SESSION_KEY_ADMIN_USERNAME = 'admin_username'

# admin里每页数量
ADMIN_PAGE_PER_SIZE = 50

# mongodb
MONGO_URL = 'mongodb://127.0.0.1:27017/kpush'

# 表
MONGO_TB_AUTOID = 'autoid'
MONGO_TB_APPINFO = 'appinfo'
MONGO_TB_USER = 'user'
MONGO_TB_NOTIFICATION = 'notification'

MONGO_TB_ADMIN_USER = 'admin_user'

# 服务器列表
SERVER_LIST = [
    dict(
        outer_host='127.0.0.1',
        outer_port=29100,
        inner_host='127.0.0.1',
        inner_port=28100,
    )
]

# (可选) redis配置，用来存储在线用户状态
# 默认关闭，即不保存
REDIS_ONLINE_SAVE = False
# 在线超时(秒)
REDIS_ONLINE_TIMEOUT = 180
# key模板
REDIS_ONLINE_KEY_TPL = 'kpush:uid:{uid}:appid:{appid}:'
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0

# 导入自定义配置
try:
    from local_config import *
except:
    pass
