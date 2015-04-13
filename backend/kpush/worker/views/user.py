# -*- coding: utf-8 -*-

from maple import Blueprint

from worker.worker_share import proto
from worker.worker_share.utils import pack_data
from share.kit import kit


bp = Blueprint()


@bp.route(proto.CMD_REGISTER)
def login(request):
    """
    appinfo_table = kit.mongo_client.get_default_database().appinfo

    appinfo_table.find_one(dict(
    ))

    user_table = kit.mongo_client.get_default_database().user
    """

    rsp = dict(
        uid=request.json_data['device_id'],
        key="mykey",
    )

    request.login_client(rsp['uid'])

    request.write_to_client(dict(
        ret=0,
        body=pack_data(rsp)
    ))
