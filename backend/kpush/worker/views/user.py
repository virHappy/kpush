# -*- coding: utf-8 -*-

from maple import Blueprint
from flask import current_app

from worker.worker_share import proto
from worker.worker_share.utils import pack_data, get_or_create_user, get_appinfo_by_appkey
from share.kit import kit
from share.log import worker_logger
from worker.worker_share.utils import login_required


bp = Blueprint()


@bp.route(proto.CMD_REGISTER)
def register(request):
    appinfo = get_appinfo_by_appkey(request.json_data['appkey'])
    worker_logger.debug("appinfo: %s", appinfo)

    if appinfo is None:
        # 报错
        request.write_to_client(
            dict(
                ret=proto.RET_INVALID_PARAMS
            )
        )
        return

    user = get_or_create_user(dict(
        appid=appinfo['appid'],
        channel=request.json_data['channel'],
        device_id=request.json_data['device_id'],
        os=request.json_data.get('os'),
        os_version=request.json_data.get('os_version'),
        sdk_version=request.json_data.get('sdk_version'),
        device_name=request.json_data.get('device_name'),
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


@bp.route(proto.CMD_SET_ALIAS_AND_TAGS)
@login_required
def set_alias_and_tags(request):
    user_table = kit.mongo_client.get_default_database()[current_app.config['MONGO_TB_USER']]

    update_values = dict()
    if request.json_data.get('alias') is not None:
        update_values['alias'] = request.json_data.get('alias')

    if request.json_data.get('tags') is not None:
        update_values['tags'] = list(set(request.json_data.get('tags')))

    user_table.update({
        'uid': request.gw_box.uid,
    }, {
        '$set': update_values
    })

    request.write_to_client(dict(
        ret=0
    ))
