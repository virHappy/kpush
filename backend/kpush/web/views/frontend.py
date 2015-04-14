#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from flask import Blueprint
from flask import render_template, jsonify
from flask import current_app, request
from share.kit import kit
from share import proto

bp = Blueprint('frontend', __name__)


@bp.route('/server/alloc', methods=['POST'])
def alloc_server():
    if not request.json_data:
        return jsonify(
            ret=proto.RET_INVALID_PARAMS
        )

    server_table = kit.mongo_client.get_default_database()[current_app.config['MONGO_TB_SERVER']]

    server_list = list(server_table.find())

    if not server_list:
        return jsonify(
            ret=proto.RET_INTERNAL_ERROR,
        )

    server = random.choice(server_list)

    return jsonify(
        ret=0,
        server=dict(
            host=server['host'],
            port=server['port'],
        )
    )

