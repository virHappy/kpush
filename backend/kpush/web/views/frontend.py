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


@bp.route('/server/alloc', methods=['GET', 'POST'])
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
