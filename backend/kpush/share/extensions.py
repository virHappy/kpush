# -*- coding: utf-8 -*-

"""
所有的插件，只是生成，初始化统一放到application里
"""

from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin

db = SQLAlchemy()
admin = Admin()
