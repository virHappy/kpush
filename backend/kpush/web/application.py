# -*- coding: utf-8 -*-

# need python >= 2.7
from importlib import import_module
from flask import Flask

from share.extensions import db, login_manager, fujs, babel
from share import models
import views.admin


def create_app(config=None, app_name=None):
    if config is None:
        import config

    if not app_name:
        app_name = __name__

    app = Flask(app_name)

    app.config.from_object(config)

    configure_logging(app)
    configure_extensions(app)
    configure_views(app)
    configure_context_processors(app)

    return app


def configure_logging(app):
    import copy
    import logging.config

    LOGGING = copy.deepcopy(app.config['LOGGING'])
    LOGGING['loggers'][app.logger.name] = LOGGING['loggers']['default']
    logging.config.dictConfig(LOGGING)


def configure_extensions(app):
    """
    初始化插件
    """
    db.init_app(app)

    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(userid):
        return models.User.query.get(userid)

    fujs.init_app(app)
    babel.init_app(app)


def configure_context_processors(app):
    """
    模板变量
    """
    pass


def configure_views(app):
    """
    注册views
    """
    # 注册 admin views
    views.admin.register_views(app)

    for it in app.config['BLUEPRINTS']:
        app.register_blueprint(import_module(it[0]).bp, url_prefix=it[1])
