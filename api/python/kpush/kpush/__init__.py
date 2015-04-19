# -*- coding: utf-8 -*-

__version__ = '0.1.0'

import json
import hashlib
import requests


def safe_str(src):
    if isinstance(src, unicode):
        return src.encode('utf8')
    return str(src)


class KPush(object):

    domain = None
    appkey = None
    appsecret = None

    def __init__(self, domain, appkey, appsecret):
        self.domain = domain
        self.appkey = appkey
        self.appsecret = appsecret

    def push(self, title, content, query, silent=False):
        """
        推送
        :param title: 标题
        :param content: 内容
        :param query: 字典格式
            all: True 代表所有人，其他字段即无效
            alias: 为None代表不过滤
            tags_or: [
                ["x", "y", "z"],
                ["a", "b", "c"],
            ]
        :param silent:
        :return:
        """

        url = 'http://%s/api/push' % self.domain
        body = self.pack_data(dict(
            title=safe_str(title),
            content=safe_str(content),
            query=query,
            silent=silent
        ))

        rsp = requests.post(url, body)

        if not rsp.ok:
            return -1, 'status code: %s' % rsp.status_code

        return rsp.json()['ret'], rsp.json().get('error')

    def pack_data(self, json_data):
        """
        :param json_data:
        :return:
        """

        if json_data is None:
            return ""

        data = json.dumps(json_data)
        sign = hashlib.md5('|'.join([self.appsecret, self.appkey, data])).hexdigest()

        return json.dumps(dict(
            appkey=self.appkey,
            data=data,
            sign=sign,
        ))

