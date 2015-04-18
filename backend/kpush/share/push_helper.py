# -*- coding: utf-8 -*-

import datetime

from share.kit import kit
from flask import current_app
from share.log import web_logger
from share import proto
from share.utils import pack_data, alloc_autoid


class PushHelper(object):
    """
    发送消息的helper
    """

    def push_notification(self, title, content, appid, query, silent=None):
        """
        发送通知
        :param title: 标题
        :param content: 内容
        :param appid: 如果有appid就直接用
        :param silent: 不弹出
        :param query 为{}代表不过滤
            alias: 为None代表不过滤
            tags_or: [
                ["x", "y", "z"],
                ["a", "b", "c"],
            ]
        即顶上一层使用 or，底下那层是and
        :return:
        """

        silent = silent or False

        match_uids = self.find_match_uids(appid, query)

        # 保存消息
        notification_id = self.saveNotification(dict(
            title=title,
            content=content,
            appid=appid,
            silent=silent,
            query=query,
        ),
            dst_users_count=len(match_uids),
        )

        if not match_uids:
            return notification_id, match_uids

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
                    body=pack_data(dict(
                        id=notification_id,
                        title=title,
                        content=content,
                        silent=silent,
                    ))
                )],
            ])

        return notification_id, match_uids

    def find_match_uids(self, appid, query):
        """
        获取匹配的uid列表
        :param appid: appid
        :param query
            all: True，代表全部发送，其他字段就无效了
            alias: 为None代表不过滤
            tags_or: [
                ["x", "y", "z"],
                ["a", "b", "c"],
            ]
        即顶上一层使用 or，底下那层是and
        :return:
        """

        query_params = dict(
            appid=appid
        )

        alias = query.get('alias')
        tags_or = query.get('tags_or')

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

    def saveNotification(self, src_notification, dst_users_count):
        """
        保存起来
        dst_users: 目标用户数
        :return:
        """

        notification_table = kit.mongo_client.get_default_database()[current_app.config['MONGO_TB_NOTIFICATION']]

        notification_id = alloc_autoid('notification')

        notification = dict(
            id=notification_id,
            create_time=datetime.datetime.now(),
            stat=dict(
                dst=dst_users_count,
                recv=0,  # 收到通知的用户数
                click=0,  # 点击通知的用户数
            )
        )

        notification.update(src_notification)

        notification_table.save(notification)

        return notification_id
