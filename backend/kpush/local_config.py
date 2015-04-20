# -*- coding: utf-8 -*-

# 不能随便修改。用作 session、push 的密钥
SECRET_KEY = "tmp_secret"

# mongodb
MONGO_URL = 'mongodb://admin:admin@127.0.0.1:27017/kpush'

# 服务器列表
SERVER_LIST = [
    dict(
        outer_host='115.28.224.64',
        outer_port=29100,
        inner_host='115.28.224.64',
        inner_port=28100,
    )
]

# (可选) redis配置，用来存储在线用户状态
REDIS_ONLINE_SAVE = False
