# kpush
开源android push解决方案

### 一. 设计思路

服务器端是用 [maple](http://github.com/dantezhu/maple)，客户端使用 [ferry](http://github.com/dantezhu/ferry)

类似push这种连接多活跃少的模式，用epoll来实现是最合适不过的了。

所以流程如下:

1. 用户登录
    
    先访问http，将device_id等传入，从而申请uid和gateway的ip，gateway的ip按照取模的方式返回。
    用户连接gateway，并发送登录请求，gateway验证通过后，将连接标记为已登陆，并返回登录成功

2. 消息下发

    trigger可以直接调用write_to_users也可以调用write_to_worker

    全员下发消息是比较简单的，因为write_to_users 时指定-1就可以全员下发了

    而指定uid列表也是可以的，gateway那边就要判断一下而已

3. 离线消息

    这个要用到数据存储了


### 二. 部署配置

supervisor配置:

    [program:kpush_web]
    environment=PYTHON_EGG_CACHE=/tmp/.python-eggs/
    directory=/kpush/backend/kpush
    command=/usr/local/bin/gunicorn -c gun_config.py web.wsgi:app
    user=user_00
    autorestart=true
    redirect_stderr=true

    [program:kpush_worker]
    environment=PYTHON_EGG_CACHE=/tmp/.python-eggs/
    directory=/kpush/backend/kpush
    command=/usr/local/bin/python manage.py runworker -p 28100
    user=user_00
    autorestart=true
    redirect_stderr=true
    stopsignal=USR1
    stopwaitsecs=20

gateway配置:

    [outer]
    host=0.0.0.0
    port=29100
    backlog=512

    recv_buf_init_size=1024
    recv_buf_max_size=-1

    conn_timeout_check_interval=10
    conn_timeout=180
    conns_maxsize=500000

    [inner]
    host=0.0.0.0
    port=28100
    backlog=512

    recv_buf_init_size=1024
    recv_buf_max_size=-1

    conns_maxsize=-1

    [log]
    log_level=error
    log_dir=logs
    file_prefix=gw
    file_max_size=1024
    file_max_num=20

    [stat]
    file_name=stat_file

系统配置:

由于是要直接连入公网，请务必不要将tcp_tw_recycle和tcp_timestamps同时开启，会导致connect失败的问题

### 三. 已知bug

1. 魅族系统下，在应用已经运行在前台的情况下，点击通知有时候会不进入PushActivity，重现路径不明。在小米4上测试正常
