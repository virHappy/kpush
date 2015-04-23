package cn.kpush;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/**
 * Created by dantezhu on 15-4-14.
 */
public class PushReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {

        KLog.d(String.format("action: %s, data: %s", intent.getAction(), intent.getData()));
        // 一定要指定context和类，否则会报如下错误
        // java.lang.RuntimeException: Unable to start receiver cn.kpush.PushReceiver: java.lang.SecurityException: Not allowed to start service Intent { act=cn.kpush.intent.SERVICE_START } without permission not exported from uid 10571
        Intent serviceIntent = new Intent(context, PushService.class);

        // Intent.ACTION_USER_PRESENT 是在锁屏操作触发的，并不实时
        serviceIntent.setAction(Config.INTENT_ACTION_SERVICE_START);

        context.startService(serviceIntent);
    }
}
