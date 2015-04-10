#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import render_template

bp = Blueprint('frontend', __name__)


@bp.route('/')
def index():
    return render_template('index.html')
