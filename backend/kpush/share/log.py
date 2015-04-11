# -*- coding: utf-8 -*-

import os
import logging


class RequireDebugOrNot(logging.Filter):
    _need_debug = False

    def __init__(self, need_debug, *args, **kwargs):
        super(RequireDebugOrNot, self).__init__(*args, **kwargs)
        self._need_debug = need_debug
        
    def filter(self, record):
        from flask import current_app
        return current_app.debug if self._need_debug else not current_app.debug

LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), "../logs/site.log")

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
            'source': os.path.basename(os.path.dirname(os.path.abspath(__file__))),
        },
        'rfile': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': LOG_FILE_PATH,
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
        'default': {
            'handlers': ['console', 'rfile', 'flylog'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}

logger = logging.getLogger('default')
