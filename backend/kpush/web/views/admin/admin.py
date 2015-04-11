# -*- coding: utf-8 -*-

import functools
import datetime

from flask import redirect, url_for, flash
from flask import session, request, g, current_app
from flask import Markup
from flask_admin import AdminIndexView, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin

from share.extensions import db
from share.models import AdminUser
from forms import LoginForm


def register_views(app):
    """注册 admin views"""
    @app.before_request
    def inject_admin_user():
        # 注入admin_user
        g.admin_user = AdminUser.query.filter(
            AdminUser.username == session.get(current_app.config['SESSION_KEY_ADMIN_USERNAME'])).first()

    admin = Admin(app)

    admin.add_view(AdminAuthView())

    # model
    admin.add_view(AdminUserView())

    return admin


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
            admin_user = AdminUser.auth(form.username.data, form.password.data)
            if not admin_user:
                flash(u'用户名或密码错误')
                return self.render("admin/login.html", form=form)

            session.permanent = True
            session[current_app.config['SESSION_KEY_ADMIN_USERNAME']] = admin_user.username

            admin_user.login_time = datetime.datetime.utcnow()
            db.session.commit()

            if request.args.get('next', None):
                return redirect(request.args['next'])
            else:
                return redirect(url_for('admin.index'))

        return self.render("admin/login.html", form=form)

    @expose('/logout', methods=['POST'])
    def logout(self):
        session.pop(current_app.config['SESSION_KEY_ADMIN_USERNAME'], None)
        return redirect(url_for('admin.index'))


class AdminUserView(ModelView):
    column_exclude_list = ('password',)

    def __init__(self, *args, **kwargs):
        super(AdminUserView, self).__init__(AdminUser, db.session, *args, **kwargs)

    def is_accessible(self):
        return g.admin_user
