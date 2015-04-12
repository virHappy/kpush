# -*- coding: utf-8 -*-

from maple import Worker
from netkit.box import Box


def configure_views(app):
    from views import user
    app.register_blueprint(user.bp)


def create_app():
    app = Worker(Box)
    configure_views(app)

    return app
