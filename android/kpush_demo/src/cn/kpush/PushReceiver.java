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
        Intent serviceIntent = new Intent();

        // Intent.ACTION_USER_PRESENT 是在锁屏操作触发的，并不实时
        serviceIntent.setAction(Config.INTENT_ACTION_SERVICE_START);

        context.startService(serviceIntent);
    }
}
