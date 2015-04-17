# -*- coding: utf-8 -*-

from maple import Blueprint
from flask import current_app

from share import proto
from share.utils import pack_data, get_or_create_user, get_appinfo_by_appkey
from share.kit import kit
from share.log import worker_logger
from worker.worker_share.utils import login_required


bp = Blueprint('user')


# @bp.route(proto.CMD_REGISTER)
def register(request):
    """
    注册，废弃
    :param request:
    :return:
    """
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
        device_name=request.json_data.get('device_name'),
        os=request.json_data.get('os'),
        os_version=request.json_data.get('os_version'),
        sdk_version=request.json_data.get('sdk_version'),
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


@bp.route(proto.CMD_LOGIN)
def login(request):
    """
    登录
    :param request:
    :return:
    """
    worker_logger.debug(request.json_data)
    user_table = kit.mongo_client.get_default_database()[current_app.config['MONGO_TB_USER']]

    user = user_table.find_one({
        'uid': request.json_data['uid'],
        'key': request.json_data['key'],
    })

    if not user:
        request.write_to_client(dict(
            ret=proto.RET_NO_DATA
        ))
        return

    worker_logger.debug("user: %s", user)

    # 只有部分数据要更新，其他的就按照注册的时候来
    user_table.update({
        '_id': user['_id'],
    }, {
        '$set': dict(
            os=request.json_data.get('os'),
            os_version=request.json_data.get('os_version'),
            sdk_version=request.json_data.get('sdk_version'),
        )
    })

    request.login_client(user['uid'])

    request.write_to_client(dict(
        ret=0
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

    worker_logger.debug('update_values: %s', update_values)

    if not update_values:
        request.write_to_client(dict(
            ret=0
        ))
        return

    user_table.update({
        'uid': request.gw_box.uid,
    }, {
        '$set': update_values
    })

    request.write_to_client(dict(
        ret=0
    ))


@bp.route(proto.CMD_HEARTBEAT)
@login_required
def heartbeat(request):
    """
    心跳
    :param request:
    :return:
    """
    request.write_to_client(dict(
        ret=0
    ))


@bp.route(proto.CMD_REMOVE_USER)
@login_required
def remove_user(request):
    """
    删除自己
    :param request:
    :return:
    """

    worker_logger.debug("remove_user: %s", request.gw_box.uid)

    user_table = kit.mongo_client.get_default_database()[current_app.config['MONGO_TB_USER']]

    user_table.remove(dict(
        uid=request.gw_box.uid
    ))

    request.write_to_client(
        dict(
            ret=0
        )
    )


@bp.route(proto.CMD_NOTIFICATION_RECV)
@login_required
def recv_notification(request):
    """
    收到通知
    :param request:
    :return:
    """
    notification_id = request.json_data['notification_id']

    notification_table = kit.mongo_client.get_default_database()[current_app.config['MONGO_TB_NOTIFICATION']]

    user_recv_notifications = request.user.get('recv_notifications', [])

    if notification_id in user_recv_notifications:
        request.write_to_client(dict(
            ret=proto.RET_REPEAT_ACTION
        ))
        return

    # TODO 加入到用户存储中，并修改stat

    request.write_to_client(dict(
        ret=0
    ))


@bp.route(proto.CMD_NOTIFICATION_CLICK)
@login_required
def click_notification(request):
    """
    点击通知
    :param request:
    :return:
    """

    notification_id = request.json_data['notification_id']

    notification_table = kit.mongo_client.get_default_database()[current_app.config['MONGO_TB_NOTIFICATION']]

    user_click_notifications = request.user.get('click_notifications', [])

    if notification_id in user_click_notifications:
        request.write_to_client(dict(
            ret=proto.RET_REPEAT_ACTION
        ))
        return

    request.write_to_client(dict(
        ret=0
    ))
