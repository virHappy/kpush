# -*- coding: utf-8 -*-

from maple import Blueprint

from worker.worker_share import proto
from worker.worker_share.utils import pack_data, get_or_create_user, get_appinfo_by_appkey
from share.kit import kit
from share.log import worker_logger


bp = Blueprint()


@bp.route(proto.CMD_REGISTER)
def register(request):
    appinfo = get_appinfo_by_appkey(request.json_data['appkey'])
    worker_logger.debug("appinfo: %s", appinfo)

    if appinfo is None:
        # 报错
        request.write_to_client(
            dict(
                ret=-1
            )
        )
        return

    user = get_or_create_user(dict(
        appid=appinfo['appid'],
        channel=request.json_data['channel'],
        device_id=request.json_data['device_id'],
    ))

    worker_logger.debug("user: %s", user)

    rsp = dict(
        uid=user['uid'],
    )

    request.login_client(rsp['uid'])

    request.write_to_client(dict(
        ret=0,
        body=pack_data(rsp)
    ))
