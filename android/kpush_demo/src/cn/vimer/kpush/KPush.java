package cn.vimer.kpush;

import android.content.Context;
import android.content.Intent;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import android.util.Log;

/**
 * Created by dantezhu on 15-4-13.
 */
public class KPush {

    private static Context context = null;
    // 默认从清单文件里获取
    private static String channel = null;
    private static String appkey = null;

    public static void init(Context context) {
        KPush.context = context;
        channel = Utils.getMetaValue(context, "KPUSH_CHANNEL");
        appkey = Utils.getMetaValue(context, "KPUSH_APPKEY");

        Log.v(Constants.LOG_TAG, String.format("channel:%s, appkey: %s", channel, appkey));

        startService();
    }

    public static Context getContext() {
        return context;
    }

    public static String getChannel() {
        return channel;
    }

    public static String getAppkey() {
        return appkey;
    }

    private static void startService() {
        // 启动service
        Intent intent = new Intent(context, PushService.class);
        context.startService(intent);
    }
}
