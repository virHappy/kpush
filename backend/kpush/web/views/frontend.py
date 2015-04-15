#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from flask import Blueprint
from flask import render_template, jsonify
from flask import current_app, request
from share.kit import kit
from share import proto

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

    server = random.choice(current_app.config['SERVER_LIST'])

    return jsonify(
        ret=0,
        server=dict(
            host=server[0],
            port=server[1],
        )
    )

