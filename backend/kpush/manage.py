#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import random
import uuid
import re
import json
import pprint
import time
import datetime

from flask import current_app
from flask import render_template_string
import flask_script
from flask_script.commands import ShowUrls

from web.application import create_app
from share.kit import kit
from share.utils import alloc_autoid, get_appinfo_by_appkey, create_appinfo

manager = flask_script.Manager(create_app)
manager.add_option('-c', '--config', dest='config', required=False)


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
def addadmin(username, password, roles=None):
    """
    Add admin user
    """
    from passlib.hash import sha256_crypt

    admin_user_table = kit.mongo_client.get_default_database()[current_app.config['MONGO_TB_ADMIN_USER']]

    roles = re.split(r'\s*,\s*', roles) if roles else []

    if admin_user_table.find_one(dict(
        username=username
    )):
        print 'username exists'
        return

    admin_user_table.insert(dict(
        username=username,
        password=sha256_crypt.encrypt(password),
        roles=roles,
    ))

    print 'succ'


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
@manager.option(dest='package')
def addapp(package, appkey):

    appinfo, error = create_appinfo(package, appkey)
    if not appinfo:
        print error
        return

    print 'package: %s' % appinfo['package']
    print 'appid: %s' % appinfo['appid']
    print 'appkey: %s' % appinfo['appkey']
    print 'appsecret: %s' % appinfo['appsecret']


@manager.option('--tags', dest='str_tags_or', action='append')
@manager.option('--alias', dest='alias')
@manager.option('--all', dest='all', action='store_true')
@manager.option('-k', '--appkey', dest='appkey')
@manager.option('-d', '--appid', dest='appid', type=int)
@manager.option('-s', '--silent', dest='silent', action='store_true')
@manager.option(dest='content')
@manager.option(dest='title')
def pushntf(title, content, silent, appid, appkey, all, alias, str_tags_or):
    """
    python manage.py pushntf "t" "c" -k 7d357c9b4ce1414fb27f077b54fb5a8f -g "a, b" -g c
    :param title:
    :param content:
    :param appid:
    :param appkey:
    :param alias:
    :param str_tags_or:
    :return:
    """
    from share.push_helper import PushHelper

    if not (all or alias or str_tags_or):
        # 起码要指定一个
        print 'please special one at least: --all, --alias, --tags'
        return

    if not appid:
        if not appkey:
            print 'if appid is None, appkey should not be None'
            return
        else:
            appinfo = get_appinfo_by_appkey(appkey)
            if not appinfo:
                print 'appkey is invalid'
                return
            else:
                appid = appinfo['appid']

    push_helper = PushHelper()

    # 这样获取到的tags是个string
    if str_tags_or:
        tags_or = []
        for str_tags in str_tags_or:
            tags_or.append(re.split(r'\s*,\s*', str_tags))
    else:
        tags_or = None

    query = {}

    if not all:
        if alias is not None:
            query['alias'] = alias

        if tags_or is not None:
            query['tags_or'] = tags_or
            
    notification_id, users = push_helper.push_notification(
        title, content, appid, query=query, silent=silent
    )

    print 'notification_id: %s\nusers: %s' % (notification_id, users)
    statntf(notification_id, True)


@manager.option('-l', '--loop', dest='loop', action='store_true')
@manager.option(dest='notification_id', type=int)
def statntf(notification_id, loop):

    notification_table = kit.mongo_client.get_default_database()[current_app.config['MONGO_TB_NOTIFICATION']]

    while True:
        notification = notification_table.find_one(dict(
            id=notification_id
        ))

        if not notification:
            print 'notification not exists: %s' % notification_id
            return

        stat_info = dict(
            dst=0,
            recv=0,
            click=0,
        )
        if notification.get('stat'):
            stat_info.update(
                notification.get('stat')
            )

        stat_info['recv_rate'] = 0 if stat_info['dst'] == 0 else 1.0 * stat_info['recv'] / stat_info['dst']
        stat_info['click_rate'] = 0 if stat_info['recv'] == 0 else 1.0 * stat_info['click'] / stat_info['recv']

        print '-' * 80
        print '时间: ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print u'目标数: %s' % stat_info['dst']
        print u'到达数: %s' % stat_info['recv']
        print u'点击数: %s' % stat_info['click']
        print u'到达率: %.02f%%' % (stat_info['recv_rate'] * 100)
        print u'点击率: %.02f%%' % (stat_info['click_rate'] * 100)

        if not loop:
            break
        else:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break

if __name__ == '__main__':
    manager.run()
