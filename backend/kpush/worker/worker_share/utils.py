# -*- coding: utf-8 -*-

import json
import hashlib
from flask import current_app
import uuid
from share.kit import kit
from worker.worker_share import proto


def pack_data(json_data):
    """
    :param json_data:
    :return:
    """

    if json_data is None:
        return ""

    data = json.dumps(json_data)
    sign = hashlib.md5('|'.join([current_app.config['SECRET_KEY'], data])).hexdigest()

    return json.dumps(dict(
        data=data,
        sign=sign,
    ))


def unpack_data(body):
    if not body:
        return None

    json_body = json.loads(body)

    data = json_body.get("data")
    sign = json_body.get("sign")

    calc_sign = hashlib.md5('|'.join([current_app.config['SECRET_KEY'], data])).hexdigest()

    if sign != calc_sign:
        return None

    return json.loads(data)


def alloc_autoid(name):
    """
    获取一个自增的id
    :return:
    """

    autoid_table = kit.mongo_client.get_default_database().autoid

    autoid_info = autoid_table.find_and_modify(
        query=dict(
            name=name,
        ),
        update={
            "$inc": {
                "value": 1,
            }
        },
        upsert=True,
        new=True,  # 返回修改过的
    )

    # print autoid_info
    return autoid_info["value"]


def get_appinfo_by_appkey(appkey):
    """
    获取appinfo
    """

    appinfo_table = kit.mongo_client.get_default_database().appinfo

    return appinfo_table.find_one(dict(
        appkey=appkey
    ))


def get_or_create_user(user_info):
    """
    返回或者创建user
    """

    user_table = kit.mongo_client.get_default_database().user

    user = user_table.find_one(dict(
        appid=user_info['appid'],
        device_id=user_info['device_id'],
    ))

    if user is None:
        new_user_info = dict(
            uid=alloc_autoid("user"),
            key=uuid.uuid4().hex,
        )
        new_user_info.update(user_info)

        # 没有这个用户
        user_table.insert(new_user_info)
    else:
        # 更新字段, 要用 $set 才会只更新指定的字段
        user_table.update({
            '_id': user['_id'],
        }, {
            "$set": user_info,
        })

    return user_table.find_one(dict(
        appid=user_info['appid'],
        device_id=user_info['device_id'],
    ))


def login_required(func):
    import functools
    @functools.wraps(func)
    def func_wrapper(request, *args, **kwargs):
        if request.gw_box.uid <= 0:
            request.write_to_client(dict(
                ret=proto.RET_NOT_LOGIN,
            ))
            return

        return func(request, *args, **kwargs)
    return func_wrapper

