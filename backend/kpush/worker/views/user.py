# -*- coding: utf-8 -*-

from maple import Blueprint

bp = Blueprint()

@bp.route(1)
def login(request):
    request.write(dict(
        ret=0
    ))
