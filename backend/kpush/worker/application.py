# -*- coding: utf-8 -*-

import hashlib
import json
from flask import current_app
from maple import Worker
from netkit.box import Box
from share.log import worker_logger


def configure_views(app):
    from views import user
    app.register_blueprint(user.bp)


def configure_handlers(app):
    """
    回调
    """

    @app.before_request
    def inject_json_content(request):
        """
        内部content json
        """

        # 先赋值None
        request.json_content = None

        json_body = request.box.get_json()
        content = json_body.get('content')
        sign = json_body.get('sign')

        calc_sign = hashlib.md5('|'.join(
            [current_app.config['SECRET_KEY'], content]
        )).hexdigest()

        if calc_sign != sign:
            worker_logger.error('sign not equal. sign: %s, calc_sign: %s', sign, calc_sign)
            return

        request.json_content = json.loads(content)


def create_app():
    app = Worker(Box)
    configure_views(app)
    configure_handlers(app)

    return app
