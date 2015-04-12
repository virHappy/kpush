# -*- coding: utf-8 -*-

import json
from maple import Blueprint
from share import proto

bp = Blueprint()


@bp.route(proto.CMD_REGISTER)
def login(request):
    rsp = dict(
        uid=1,
        key="mykey",
    )

    request.login_client(rsp['uid'])

    request.write_to_client(dict(
        ret=0,
        body=json.dumps(rsp)
    ))
