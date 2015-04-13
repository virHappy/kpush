package cn.kpush;

import android.content.Context;
import android.content.Intent;


/**
 * Created by dantezhu on 15-4-13.
 */
public class KPush {

    private static Context context = null;

    public static void init(Context context) {
        KPush.context = context;

        startService();
    }

    private static void startService() {
        // 启动service
        Intent intent = new Intent(context, PushService.class);
        context.startService(intent);
    }

    public static Context getContext() {
        return context;
    }
}
