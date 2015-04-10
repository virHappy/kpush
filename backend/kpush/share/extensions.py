# -*- coding: utf-8 -*-

"""
所有的插件，只是生成，初始化统一放到application里
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_util_js import FlaskUtilJs
from flask_babel import Babel

db = SQLAlchemy()
login_manager = LoginManager()
fujs = FlaskUtilJs()
babel = Babel()
