# kpush
开源android push解决方案

### 一. 使用说明

1. gateway服务器部署
    
    1. 下载 [maple](http://github.com/dantezhu/maple) 源码，编译gateway。
    2. gateway的参考配置如下
        
            [outer]
            host=0.0.0.0
            port=29100
            backlog=512

            recv_buf_init_size=1024
            recv_buf_max_size=-1

            conn_timeout_check_interval=10
            conn_timeout=90
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
            
      3. 使用supervisor来启动的话，配置如下:
      
            [program:gateway]
            directory=/data/release/gateway/
            command=/data/release/gateway/bin/gateway -c etc/config.ini
            user=root
            autorestart=true
            redirect_stderr=true
            
      4. 注意
       
         由于是要直接连入公网，请务必不要将tcp_tw_recycle和tcp_timestamps同时开启，会导致connect失败的问题

      
2. kpush服务器部署

      1. 拷贝 kpush/backend/kpush 至目标部署路径
      2. 拷贝 local_config_example.py 为 local_config.py
      3. 修改 local_config.py 中的配置，具体参看注释
      4. 添加后台管理员
      
              python manage.py addadmin $username $password
          
      5. 如果通过supervisor启动，配置如下
                
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

       6. http://domain/admin 即可进入后台，创建应用或者下发通知。
       
3. 客户端接入

    1. 执行 ./pull_modules.sh，将会拉取依赖的项目
    2. 将 kpush/android/kpush/src的所有文件copy到目标工程
    3. 修改src目录下 cn/kpush/PushService.java 中的 DOMAIN 和 SECRET_KEY 配置，修改为自己部署服务器的信息
    4. 修改目标工程的 AndroidManifest.xml，参考 kpush/android/kpush/ 下的 AndroidManifest.xml
    5. 编译运行即可
    
4. 开放api

    目前仅支持python版本
    
    1. pip install kpush 即可
    2. 具体使用参看 examples

### 二. 设计思路

服务器端是用 [maple](http://github.com/dantezhu/maple)，客户端使用 [ferry](http://github.com/dantezhu/ferry)

类似push这种连接多活跃少的模式，用epoll来实现是最合适不过的了。

所以流程如下:

1. 用户登录
    
    先访问http，将device_id等传入，从而申请uid和gateway的ip，gateway的ip按照取模的方式返回。
    用户连接gateway，并发送登录请求，gateway验证通过后，将连接标记为已登陆，并返回登录成功

2. 消息下发

    先到mongodb查找满足条件的用户，之后在通过trigger.write_to_users 向指定用户群发送消息
    目前支持的过滤条件为
    
    * 全员下发
    * 按照别名下发
    * 按照tags下发
        
        tags下发支持两层，如下
            
            tags_or: {
                [1, 2],
                [3, 4]
            }
        
        即 tags=[1,2] 或者 tags=[3,4]
        
3. 离线消息

    不支持
    
### 三. 已知bug

1. 魅族系统下，在应用已经运行在前台的情况下，点击通知有时候会不进入PushActivity，重现路径不明。在小米4上测试正常
