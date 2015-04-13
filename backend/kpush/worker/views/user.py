# -*- coding: utf-8 -*-

from maple import Blueprint

from worker.worker_share import proto
from worker.worker_share.utils import pack_content
from share.kit import kit


bp = Blueprint()


@bp.route(proto.CMD_REGISTER)
def login(request):
    rsp = dict(
        uid=request.json_content['device_id'],
        key="mykey",
    )

    request.login_client(rsp['uid'])

    request.write_to_client(dict(
        ret=0,
        body=pack_content(rsp)
    ))
