# -*- coding: utf-8 -*-

from wtforms import StringField, PasswordField, SelectField, BooleanField
from wtforms.validators import DataRequired
from flask_wtf import Form


class LoginForm(Form):
    """后台管理登录框"""

    username = StringField(u'帐号', validators=[DataRequired(u'该项不能为空')])
    password = PasswordField(u'密码', validators=[DataRequired(u'该项不能为空')])


class NotificationCreateForm(Form):
    """
    创建推送
    """

    appid = SelectField(u'应用', validators=[DataRequired(u'该项不能为空')], coerce=int)
    title = StringField(u'标题', validators=[DataRequired(u'该项不能为空')])
    content = StringField(u'内容', validators=[DataRequired(u'该项不能为空')])
    all = BooleanField(u'所有用户', default=False)
    alias = StringField(u'别名')
    tags = StringField(u'标签')
