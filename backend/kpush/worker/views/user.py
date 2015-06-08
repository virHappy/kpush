# -*- coding: utf-8 -*-

import time
from maple import Blueprint
from flask import current_app

from share import proto
from share.utils import pack_data, create_or_update_user, get_appinfo_by_appkey, save_redis_online, remove_redis_online
from share.kit import kit
from share.log import logger
from worker.worker_share.utils import login_required


bp = Blueprint('user')


@bp.close_app_client
def client_conn_closed(request):
    """
    当客户端链接断掉的时候
    :param request:
    :return:
    """
    if current_app.config['REDIS_ONLINE_SAVE'] and request.gw_box.uid > 0:
        # 有效
        try:
            remove_redis_online(request.gw_box.uid, request.gw_box.userdata)
        except:
            logger.error('exc occur. request: %s', request, exc_info=True)


# @bp.route(proto.CMD_REGISTER)
def register(request):
    """
    (未使用)注册
    :param request:
    :return:
    """
    appinfo = get_appinfo_by_appkey(request.json_data['appkey'])

    if appinfo is None:
        # 报错
        request.write_to_client(
            dict(
                ret=proto.RET_INVALID_PARAMS
            )
        )
        return

    user = create_or_update_user(dict(
        appid=appinfo['appid'],
        channel=request.json_data['channel'],
        device_id=request.json_data['device_id'],
        device_name=request.json_data.get('device_name'),
        os=request.json_data.get('os'),
        os_version=request.json_data.get('os_version'),
        sdk_version=request.json_data.get('sdk_version'),
    ))

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

    # 因为现在注册永远是第一步，所以不需要再在login的时候做更新了
    # 只有部分数据要更新，其他的就按照注册的时候来
    # user_table.update({
    #     '_id': user['_id'],
    # }, {
    #     '$set': dict(
    #         os=request.json_data.get('os'),
    #         os_version=request.json_data.get('os_version'),
    #         sdk_version=request.json_data.get('sdk_version'),
    #     )
    # })

    # 放appid的原因是，心跳的时候可以直接取到appid，这样写入redis的时候就方便多了
    request.login_client(user['uid'], user['appid'])

    if current_app.config['REDIS_ONLINE_SAVE']:
        # 有效
        try:
            save_redis_online(user['uid'], user['appid'])
        except:
            logger.error('exc occur. request: %s', request, exc_info=True)

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
    logger.debug('uid: %s, userdata: %s', request.gw_box.uid, request.gw_box.userdata)

    if current_app.config['REDIS_ONLINE_SAVE']:
        # 有效
        try:
            save_redis_online(request.gw_box.uid, request.gw_box.userdata)
        except:
            logger.error('exc occur. request: %s', request, exc_info=True)

    request.write_to_client(dict(
        ret=0
    ))


@bp.route(proto.CMD_REMOVE_USER)
@login_required
def remove_user(request):
    """
    (未使用)删除自己
    :param request:
    :return:
    """

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
    user = kit.mongo_client.get_default_database()['user'].find_one(dict(
        uid=request.gw_box.uid
    ))
    if not user:
        request.write_to_client(dict(
            ret=proto.RET_NO_DATA,
        ))
        return

    notification_id = request.json_data['notification_id']

    notification_table = kit.mongo_client.get_default_database()[current_app.config['MONGO_TB_NOTIFICATION']]

    user_recv_notifications = user.get('recv_notifications') or []

    if notification_id in user_recv_notifications:
        request.write_to_client(dict(
            ret=proto.RET_REPEAT_ACTION
        ))
        return

    # 加入到用户存储中，并修改stat
    user_table = kit.mongo_client.get_default_database()[current_app.config['MONGO_TB_USER']]
    user_table.update(dict(
        uid=request.gw_box.uid,
    ), {
        '$push': {
            'recv_notifications': notification_id
        }
    })

    notification_table.update(dict(
        id=notification_id
    ), {
        '$inc': {
            'stat.recv': 1,
        }
    })

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

    user = kit.mongo_client.get_default_database()['user'].find_one(dict(
        uid=request.gw_box.uid
    ))
    if not user:
        request.write_to_client(dict(
            ret=proto.RET_NO_DATA,
        ))
        return

    notification_id = request.json_data['notification_id']

    notification_table = kit.mongo_client.get_default_database()[current_app.config['MONGO_TB_NOTIFICATION']]

    user_click_notifications = user.get('click_notifications') or []

    if notification_id in user_click_notifications:
        request.write_to_client(dict(
            ret=proto.RET_REPEAT_ACTION
        ))
        return

    # 加入到用户存储中，并修改stat
    user_table = kit.mongo_client.get_default_database()[current_app.config['MONGO_TB_USER']]
    user_table.update(dict(
        uid=request.gw_box.uid,
    ), {
        '$push': {
            'click_notifications': notification_id
        }
    })

    notification_table.update(dict(
        id=notification_id
    ), {
        '$inc': {
            'stat.click': 1,
            }
    })

    request.write_to_client(dict(
        ret=0
    ))
