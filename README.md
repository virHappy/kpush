# kpush
开源android push解决方案

### 设计思路

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


### 部署配置

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
    command=/usr/local/bin/python manage.py runworker -p 28000
    user=user_00
    autorestart=true
    redirect_stderr=true
    stopsignal=USR1
    stopwaitsecs=10

