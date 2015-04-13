# -*- coding: utf-8 -*-

from flask import current_app
import pymongo


class Kit(object):

    _mongo_client = None

    @property
    def mongo_client(self):
        if self._mongo_client is None:
            self._mongo_client =  pymongo.MongoClient(current_app.config['MONGO_URL'])
        return self._mongo_client


kit = Kit()