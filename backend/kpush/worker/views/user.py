# -*- coding: utf-8 -*-

import json
from maple import Blueprint
from share import proto

bp = Blueprint()


@bp.route(proto.CMD_REGISTER)
def login(request):
    req = json.loads(request.box.body)
    rsp = dict(
        uid=req['device_id'],
        key="mykey",
    )

    request.login_client(rsp['uid'])

    request.write_to_client(dict(
        ret=0,
        body=json.dumps(rsp)
    ))
