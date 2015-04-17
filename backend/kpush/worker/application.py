# -*- coding: utf-8 -*-

import hashlib
import json
from flask import current_app
from maple import Worker
from netkit.box import Box
from share.log import worker_logger
from share.kit import kit


def configure_views(app):
    from views import user
    app.register_blueprint(user.bp)


def configure_handlers(app):
    """
    回调
    """

    @app.before_request
    def inject_json_data(request):
        """
        内部content json
        """

        worker_logger.debug(request.box)

        # 先赋值None
        request.json_data = None

        json_body = request.box.get_json()
        if not json_body:
            return

        data = json_body.get('data')
        sign = json_body.get('sign')

        calc_sign = hashlib.md5('|'.join(
            [current_app.config['SECRET_KEY'], data]
        )).hexdigest()

        if calc_sign != sign:
            worker_logger.error('sign not equal. sign: %s, calc_sign: %s', sign, calc_sign)
            return

        request.json_data = json.loads(data)

    @app.before_request
    def inject_user(request):
        if request.gw_box.uid > 0:
            request.user = kit.mongo_client.get_default_database()['user'].find_one(dict(
                uid=request.gw_box.uid
            ))
        else:
            request.user = None


def create_app():
    app = Worker(Box)
    configure_views(app)
    configure_handlers(app)

    return app
