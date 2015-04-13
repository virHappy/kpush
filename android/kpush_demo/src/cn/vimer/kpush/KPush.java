package cn.vimer.kpush;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.os.Build;
import android.telephony.TelephonyManager;
import android.util.Log;

import java.util.UUID;

/**
 * Created by dantezhu on 15-4-13.
 */
public class KPush {

    private static Context context = null;
    // 默认从清单文件里获取
    private static String appkey = null;
    private static String channel = null;

    public static void init(Context context) {
        KPush.context = context;

        DeviceUtil.init(context);

        appkey = Utils.getMetaValue(context, "KPUSH_APPKEY");
        channel = Utils.getMetaValue(context, "KPUSH_CHANNEL");

        Log.v(Constants.LOG_TAG, String.format("channel:%s, appkey: %s", channel, appkey));

        startService();
    }

    private static void startService() {
        // 启动service
        Intent intent = new Intent(context, PushService.class);
        context.startService(intent);
    }

    public static String getAppkey() {
        return appkey;
    }

    public static String getChannel() {
        return channel;
    }
}
