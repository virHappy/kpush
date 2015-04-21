package cn.kpush;

/**
 * Created by dantezhu on 15-4-13.
 */
public class Config {
    public static final String ALLOC_SERVER_URL = "http://%s/server/alloc";

    public static final int SDK_VERSION = 5;
    public static final String OS = "android";

    public static final String PREFS_NAME = "data";

    // 最多缓存的msgs
    public static final int MAX_PENDING_MSGS = 500;

    // http请求端口超时设置(秒)
    public static final int HTTP_CONNECT_TIMEOUT = 10;
    public static final int HTTP_READ_TIMEOUT = 10;

    // 出错重试的时间（秒）
    public static final int ERROR_RETRY_INTERVAL = 10;

    // 心跳间隔（秒）
    public static final int HEARTBEAT_INTERVAL = 30;

    // 多长时间内没有收到任何消息，与服务器配置一样。<= 0 为永不超时
    public static final int CONN_ALIVE_TIMEOUT = HEARTBEAT_INTERVAL * 3;

    // 自定义action
    public static final String INTENT_ACTION_SERVICE_START = "cn.kpush.intent.SERVICE_START";
    public static final String INTENT_ACTION_SEND_MSG = "cn.kpush.intent.SEND_MSG";
}
