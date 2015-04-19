# -*- coding: utf-8 -*-

import json
import hashlib
from flask import current_app
import uuid
import datetime
from share.kit import kit


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

    autoid_table = kit.mongo_client.get_default_database()[current_app.config['MONGO_TB_AUTOID']]

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

    appinfo_table = kit.mongo_client.get_default_database()[current_app.config['MONGO_TB_APPINFO']]

    return appinfo_table.find_one(dict(
        appkey=appkey
    ))


def get_appinfo_list(query=None, sort=None):
    """
    获取appinfo列表
    """
    query = query or dict()
    appinfo_table = kit.mongo_client.get_default_database()[current_app.config['MONGO_TB_APPINFO']]

    result = appinfo_table.find(query)
    if sort:
        result.sort(sort)

    return result


def create_appinfo(package, appkey=None):
    """
    创建appinfo
    """

    appinfo_table = kit.mongo_client.get_default_database()[current_app.config['MONGO_TB_APPINFO']]

    if appkey:
        if appinfo_table.find_one({
            "appkey": appkey
        }):
            print 'appkey exists'
            return
    else:
        appkey = uuid.uuid4().hex

    appid = alloc_autoid("appinfo")
    appsecret = uuid.uuid4().hex

    appinfo = {
        "appid": appid,
        "appkey": appkey,
        "package": package,
        "appsecret": appsecret,
        "create_time": datetime.datetime.now()
        }

    appinfo_table.insert(appinfo)

    return appinfo


def create_or_update_user(user_info):
    """
    返回或者创建user
    """

    user_table = kit.mongo_client.get_default_database()[current_app.config['MONGO_TB_USER']]

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

