# -*- coding: utf-8 -*-

from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
from flask_wtf import Form


class LoginForm(Form):
    """后台管理登录框"""

    username = StringField(u'帐号', validators=[DataRequired(u'该项不能为空')])
    password = PasswordField(u'密码', validators=[DataRequired(u'该项不能为空')])
