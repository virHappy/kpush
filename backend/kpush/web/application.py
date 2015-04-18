# -*- coding: utf-8 -*-

# need python >= 2.7
from importlib import import_module
from flask import Flask, request

from share.extensions import admin
import views.admin


def create_app(config=None, name=None):
    if config is None:
        config = 'config'

    if not name:
        name = __name__

    app = Flask(name)

    app.config.from_object(config)

    configure_logging(app)
    configure_extensions(app)
    configure_views(app)
    configure_context_processors(app)
    configure_handlers(app)

    return app


def configure_logging(app):
    import logging.config

    app.logger and logging.config.dictConfig(app.config['LOGGING'])


def configure_extensions(app):
    """
    初始化插件
    """
    admin.init_app(app)


def configure_context_processors(app):
    """
    模板变量
    """
    pass


def configure_handlers(app):
    @app.before_request
    def inject_json_data():
        from share.utils import unpack_data
        request.json_data = None
        if request.method == 'POST' and request.get_data():
            try:
                request.json_data = unpack_data(request.get_data())
            except:
                pass


def configure_views(app):
    """
    注册views
    """
    # 注册 admin views
    views.admin.register_views(app)

    for it in app.config['BLUEPRINTS']:
        app.register_blueprint(import_module(it[0]).bp, url_prefix=it[1])
