# -*- coding: utf-8 -*-

from maple import Blueprint
from share import proto
from share.net_pb2 import ReqUserRegister, RspUserRegister

bp = Blueprint()


@bp.route(proto.CMD_REGISTER)
def login(request):
    rsp = RspUserRegister()
    rsp.uid = 1
    rsp.key = "mykey"

    request.login_client(rsp.uid)

    request.write_to_client(dict(
        ret=0,
        body=rsp.SerializeToString(),
    ))
