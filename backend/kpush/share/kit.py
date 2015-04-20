# -*- coding: utf-8 -*-

from flask import current_app
from maple import Trigger
from netkit.box import Box
import pymongo


class Kit(object):

    _mongo_client = None
    _triggers = None
    _redis_client = None

    @property
    def mongo_client(self):
        if self._mongo_client is None:
            self._mongo_client = pymongo.MongoClient(current_app.config['MONGO_URL'])
        return self._mongo_client

    @property
    def triggers(self):
        if self._triggers is None:
            self._triggers = []
            for server in current_app.config['SERVER_LIST']:
                self._triggers.append(Trigger(Box, server['inner_host'], server['inner_port']))

        return self._triggers

    @property
    def redis_client(self):
        from redis import StrictRedis
        if not current_app.config['REDIS_ONLINE_SAVE']:
            return None

        if self._redis_client is None:
            self._redis_client = StrictRedis(current_app.config['REDIS_HOST'],
                                             current_app.config['REDIS_PORT'],
                                             current_app.config['REDIS_DB'])

        return self._redis_client


kit = Kit()