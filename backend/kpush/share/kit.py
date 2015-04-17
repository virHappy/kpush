# -*- coding: utf-8 -*-

from flask import current_app
from maple import Trigger
from netkit.box import Box
import pymongo


class Kit(object):

    _mongo_client = None
    _triggers = None

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


kit = Kit()