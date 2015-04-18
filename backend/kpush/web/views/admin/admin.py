# -*- coding: utf-8 -*-

import functools
import datetime

from flask import redirect, url_for, flash
from flask import session, request, g, current_app
from flask import Markup
from flask_admin import AdminIndexView, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from passlib.hash import sha256_crypt

from share.extensions import admin
from share.kit import kit
from forms import LoginForm


def register_views(app):
    """注册 admin views"""
    @app.before_request
    def inject_admin_user():
        # 注入admin_user
        admin_user_table = kit.mongo_client.get_default_database()[current_app.config['MONGO_TB_ADMIN_USER']]
        g.admin_user = admin_user_table.find_one(dict(
            username=session.get(current_app.config['SESSION_KEY_ADMIN_USERNAME'])
        ))

    admin.add_view(AdminAuthView())


class AdminAuthView(BaseView):

    def is_visible(self):
        return False

    @expose('/')
    def index(self):
        return redirect(url_for('admin.index'))

    @expose('/login', methods=['GET', 'POST'])
    def login(self):
        form = LoginForm()
        if form.validate_on_submit():
            admin_user_table = kit.mongo_client.get_default_database()[current_app.config['MONGO_TB_ADMIN_USER']]
            admin_user = admin_user_table.find_one(dict(
                username=form.username.data
            ))

            if not admin_user or not sha256_crypt.verify(form.password.data, admin_user['password']):
                # flash('invalid username or password')
                form.username.errors.append(u'错误的用户名或密码')
                form.password.errors.append(u'错误的用户名或密码')
                return self.render("admin/login.html", form=form)

            session.permanent = True
            session[current_app.config['SESSION_KEY_ADMIN_USERNAME']] = admin_user['username']

            if request.args.get('next', None):
                return redirect(request.args['next'])
            else:
                return redirect(url_for('admin.index'))

        return self.render("admin/login.html", form=form)

    @expose('/logout', methods=['POST'])
    def logout(self):
        session.pop(current_app.config['SESSION_KEY_ADMIN_USERNAME'], None)
        return redirect(url_for('admin.index'))

