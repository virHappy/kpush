# -*- coding: utf-8 -*-

import datetime
import re

from passlib.hash import sha256_crypt

from share.extensions import db


class AbstractBaseUser(db.Model):
    """
    user基类
    """

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    login_time = db.Column(db.DateTime)

    def __unicode__(self):
        return u'%s' % self.username

    def set_password(self, raw_password):
        """设置密码，要加密"""
        self.password = sha256_crypt.encrypt(raw_password)

    def check_password(self, raw_password):
        """检查密码是否合法"""
        return sha256_crypt.verify(raw_password, self.password)

    @classmethod
    def auth(cls, username, raw_password):
        """验证用户登录。如果登录成功，返回用户"""
        obj = cls.query.filter_by(username=username).first()

        if obj and obj.check_password(raw_password):
            return obj
        else:
            return None


class AdminUser(AbstractBaseUser):
    __tablename__ = 'admin_user'

    roles = db.Column(db.Text)

    @property
    def parsed_roles(self):
        return re.split(r'\s*,\s*', self.roles) if self.roles else []

    @parsed_roles.setter
    def parsed_roles(self, value):
        self.roles = ','.join(value)
