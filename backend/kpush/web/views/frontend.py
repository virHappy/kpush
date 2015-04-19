#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from flask import Blueprint
from flask import render_template, jsonify
from flask import current_app, request
from share.kit import kit
from share import proto
from share.log import web_logger
from share.utils import get_appinfo_by_appkey, create_or_update_user, pack_data

bp = Blueprint('frontend', __name__)


@bp.route('/server/alloc', methods=['POST'])
def alloc_server():
    """
    # 方便测试
    if not request.json_data:
        return jsonify(
            ret=proto.RET_INVALID_PARAMS
        )
    """

    appinfo = get_appinfo_by_appkey(request.json_data['appkey'])
    web_logger.debug("appinfo: %s", appinfo)

    if appinfo is None:
        # 报错
        jsonify(
            ret=proto.RET_INVALID_PARAMS
        )
        return

    user = create_or_update_user(dict(
        appid=appinfo['appid'],
        channel=request.json_data['channel'],
        device_id=request.json_data['device_id'],
        device_name=request.json_data.get('device_name'),
        os=request.json_data.get('os'),
        os_version=request.json_data.get('os_version'),
        sdk_version=request.json_data.get('sdk_version'),
    ))

    server_list = current_app.config['SERVER_LIST']

    # 取模
    server = server_list[user['uid'] % len(server_list)]

    return current_app.response_class(pack_data(
        dict(
            ret=0,
            user=dict(
                uid=user['uid'],
                key=user['key'],
            ),
            server=dict(
                host=server['outer_host'],
                port=server['outer_port'],
            )
        )
    ), mimetype='application/json')


@bp.route('/api/push', methods=['POST'])
def push_api():
    """
    push的api
    {
        title
        content
        silent
        query
    }
    :return:
    """
    from share.api_utils import unpack_api_data
    from share.push_helper import PushHelper

    appinfo, json_data = unpack_api_data(request.get_data())

    if appinfo is None or json_data is None:
        return jsonify(
            ret=proto.RET_INVALID_PARAMS,
            error=u'签名验证失败',
        )

    query = json_data.get('query')
    if not query:
        return jsonify(
            ret=proto.RET_INVALID_PARAMS,
            error=u'query参数不存在',
        )

    if not (query.get('all') or query.get('alias') or query.get('tags_or')):
        return jsonify(
            ret=proto.RET_INVALID_PARAMS,
            error=u'query参数不合法, 请至少指定all/alias/tags_or其中一个',
        )

    if not json_data.get('title') or not json_data.get('content'):
        return jsonify(
            ret=proto.RET_INVALID_PARAMS,
            error=u'请指定title和content',
        )

    real_query = dict()
    if not query.get('all'):
        if query.get('alias') is not None:
            real_query['alias'] = query.get('alias')

        if query.get('tags_or') is not None:
            real_query['tags_or'] = query.get('tags_or')

    push_helper = PushHelper()
    notification_id, dst_uids = push_helper.push_notification(
        json_data.get('title'),
        json_data.get('content'),
        appinfo['appid'],
        query=real_query,
        silent=json_data.get('silent')
    )

    return jsonify(
        ret=0,
        notification_id=notification_id,
        dst_uids=len(dst_uids),
    )
