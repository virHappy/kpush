# kpush
开源android push解决方案

### 设计思路

服务器端是用 [maple](http://github.com/dantezhu/maple)，客户端使用 [ferry](http://github.com/dantezhu/ferry)

类似push这种连接多活跃少的模式，用epoll来实现是最合适不过的了。

所以流程如下:

1. 用户登录
    用户将请求发送给gateway，具体参数如uuid等暂且不表，worker收到请求后，分配给客户端一个唯一long long的uid，并将连接标记为已登陆

2. 消息下发
    trigger可以直接调用write_to_users也可以调用write_to_worker

    全员下发消息是比较简单的，因为write_to_users 时指定-1就可以全员下发了
    而指定uid列表也是可以的，gateway那边就要判断一下而已

3. 离线消息
    这个要用到数据存储了
