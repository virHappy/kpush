package cn.kpush;

/**
 * Created by dantezhu on 15-4-13.
 */
public class Constants {
    public static final String DOMAIN = "192.168.0.108:5000";
    public static final String ALLOC_SERVER_URL = "http://" + DOMAIN + "/server/alloc";

    public static final String SECRET = "4y%zgs*074ibnacl31w2d!l-o$3qaa+lu)w25g*0#e6i_qt1*#305^gij7a+js$i";

    public static final int SDK_VERSION = 1;
    public static final String OS = "android";

    public static final String PREFS_NAME = "data";

    // 最多缓存的msg
    public static final int MAX_PENDING_MSG = 500;

    // 出错重试的时间（秒）
    public static final int ERROR_RETRY_INTERVAL = 1;

    // 心跳间隔（秒）
    public static final int HEARTBEAT_INTERVAL = 300;

    // 自定义action
    public static final String INTENT_ACTION_SERVICE_START = "cn.kpush.intent.SERVICE_START";
    public static final String INTENT_ACTION_SEND_MSG = "cn.kpush.intent.SEND_MSG";
}
