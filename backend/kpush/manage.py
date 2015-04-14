#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import random

from flask import current_app
from flask import render_template_string
import flask_script
from flask_script.commands import ShowUrls

from web.application import create_app
from share.extensions import db
from share.models import AdminUser

manager = flask_script.Manager(create_app)
manager.add_option('-c', '--config', dest='config', required=False)
manager.add_option('-n', '--name', dest='name', required=False)


class GServer(flask_script.Command):
    """
    Runs the Flask gevent server

    :param host: server host
    :param port: server port
    """

    help = description = 'Runs the Flask gevent server'

    def __init__(self, host='127.0.0.1', port=5000):
        super(GServer, self).__init__()
        self.host = host
        self.port = port

    def get_options(self):

        options = (
            flask_script.Option('-t', '--host',
                                dest='host',
                                default=self.host),

            flask_script.Option('-p', '--port',
                                dest='port',
                                type=int,
                                default=self.port),
        )

        return options

    def __call__(self, app, host, port):
        # we don't need to run the server in request context
        # so just run it directly

        from gevent import monkey; monkey.patch_all()
        from gevent import wsgi

        print "* Running gserver on http://%s:%s" % (host, port)
        try:
            wsgi.WSGIServer((host, int(port)), app).serve_forever()
        except KeyboardInterrupt:
            sys.exit(0)


manager.add_command('urls', ShowUrls())
manager.add_command('rungserver', GServer())


@manager.command
def syncdb():
    """
    Create tables
    """
    db.create_all()


@manager.command
def addadmin(username, password, roles=None):
    """
    Add admin user
    """
    admin_user = AdminUser(username=username)
    admin_user.set_password(password)
    admin_user.roles = roles

    db.session.add(admin_user)
    db.session.commit()


@manager.command
def dbshell():
    """
    Like Django's dbshell，with flask-sqlalchemy
    """
    SQLALCHEMY_DATABASE_URI = current_app.config['SQLALCHEMY_DATABASE_URI']
    if not SQLALCHEMY_DATABASE_URI:
        print 'no SQLALCHEMY_DATABASE_URI'
        return

    if SQLALCHEMY_DATABASE_URI.startswith('sqlite:'):
        db_path = SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')
        cmd = 'sqlite3 %s' % db_path
    elif SQLALCHEMY_DATABASE_URI.startswith('mysql:'):
        params = SQLALCHEMY_DATABASE_URI.split('/')
        dbname = params[-1]
        user_pass_part, host_port_part = params[-2].split('@')
        if user_pass_part.find(':') >= 0:
            user, password = user_pass_part.split(':')
        else:
            user, password = user_pass_part, ''

        if host_port_part.find(':') >= 0:
            host, port = host_port_part.split(':')
        else:
            host, port = host_port_part, ''

        cmd = render_template_string(
            'mysql -u{{user}} {% if password %}-p{{password}}{% endif %} {% if host %}-h{{host}}{% endif %} {% if port %}-P{{port}}{% endif %} -D{{dbname}}',
            user=user, password=password, host=host, port=port, dbname=dbname
        )

    else:
        print '\033[1;33m%s\033[0m' % 'only support mysql, sqlite'
        return

    print '\033[1;32m%s\033[0m' % cmd
    os.system(cmd)


@manager.option(dest='length', type=int)
def genkey(length):
    """
    generate secret key，参考django
    """
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    print ''.join([random.choice(chars) for i in range(length)])


@manager.option('-w', '--workers', dest='workers', type=int, default=1)
@manager.option('-d', '--debug', dest='debug', action='store_true')
@manager.option('-t', '--host', dest='host', default='127.0.0.1')
@manager.option('-p', '--port', dest='port', type=int, required=True)
def runworker(host, port, debug, workers):
    """
    start worker
    """
    from worker.application import create_app
    app = create_app()
    app.run(host, port, debug, workers)


@manager.option('-k', '--appkey', dest='appkey')
def addapp(appkey):
    import uuid
    from share.kit import kit
    from share.utils import alloc_autoid
    appinfo_table = kit.mongo_client.get_default_database()[current_app.config['MONGO_TB_APPINFO']]

    if appkey:
        if appinfo_table.find_one({
            "appkey": appkey
        }):
            print 'appkey exists'
            return
    else:
        appkey = uuid.uuid4().hex

    appid = alloc_autoid("appinfo")

    appinfo_table.insert({
        "appid": appid,
        "appkey": appkey,
    })

    print "appid: %s, appkey: %s" % (appid, appkey)

if __name__ == '__main__':
    manager.run()
