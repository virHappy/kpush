# -*- coding: utf-8 -*-

from share.kit import kit
from flask import current_app
from share.log import web_logger
from share import proto
from share.utils import pack_data


class PushHelper(object):
    """
    发送消息的helper
    """

    def push_notification(self, notification, appid=None, appkey=None, alias=None, tags_or=None):
        """
        发送通知
        :param notification: 发送内容 {
            title: 标题
            content: 内容
        }
        :param appid: 如果有appid就直接用
        :param appkey: 需要先把appkey换成appid
        :param alias: 为None代表不过滤
        :param tags_or: [
            ["x", "y", "z"],
            ["a", "b", "c"],
        ]
        即顶上一层使用 or，底下那层是and
        :return:
        """

        if appid is None:
            assert appkey is not None, "if appid is None, appkey should not be None"

            appinfo_table = kit.mongo_client.get_default_database()[current_app.config['MONGO_TB_APPINFO']]
            appinfo = appinfo_table.find_one(dict(
                appkey=appkey
            ))

            if not appinfo:
                web_logger.error('appinfo not found: %s', appkey)
                return False

            appid = appinfo['appid']

        match_uids = self.find_match_uids(appid, alias, tags_or)
        if not match_uids:
            return match_uids

        # 要对uids分组
        uids_list = [[] for it in range(0, len(kit.triggers))]

        for uid in match_uids:
            i = uid % len(uids_list)
            uids_list[i].append(uid)

        for i, uids in enumerate(uids_list):
            if not uids:
                continue
            kit.triggers[i].write_to_users([
                [uids, dict(
                    cmd=proto.EVT_NOTIFICATION,
                    body=pack_data(notification)
                )],
            ])

        return match_uids

    def find_match_uids(self, appid, alias=None, tags_or=None):
        """
        获取匹配的uid列表
        :param appid: appid
        :param alias: 为None代表不过滤
        :param tags_or: [
            ["x", "y", "z"],
            ["a", "b", "c"],
        ]
        即顶上一层使用 or，底下那层是and
        :return:
        """

        query_params = dict(
            appid=appid
        )
        if alias is not None:
            query_params['alias'] = alias

        if tags_or:
            # 有内容
            query_params['$or'] = []
            for tags in tags_or:
                query_params['$or'].append({
                    "tags": {
                        "$all": tags
                    }
                })

        user_table = kit.mongo_client.get_default_database()[current_app.config['MONGO_TB_USER']]

        users = user_table.find(query_params, {
            "uid": 1
        })

        return [user['uid'] for user in users]
