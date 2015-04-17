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

        if (intent.getAction().equals(Intent.ACTION_PACKAGE_REMOVED)) {
            serviceIntent.setAction(Constants.INTENT_ACTION_SEND_MSG);
            serviceIntent.putExtra("cmd", Proto.CMD_REMOVE_USER);
        }
        else {
            // Intent.ACTION_USER_PRESENT 是在锁屏操作触发的，并不实时
            serviceIntent.setAction(Constants.INTENT_ACTION_SERVICE_START);
        }

        context.startService(serviceIntent);
    }
}
