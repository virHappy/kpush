package cn.kpush;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

/**
 * Created by dantezhu on 15-4-14.
 */
public class PushReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {

        Log.d(Constants.LOG_TAG, String.format("action: %s, data: %s", intent.getAction(), intent.getData()));
        Intent serviceIntent = new Intent();

        if (intent.getAction().equals(Intent.ACTION_PACKAGE_ADDED)) {
            serviceIntent.setAction(Constants.INTENT_ACTION_PACKAGE_ADDED);
        }
        else if (intent.getAction().equals(Intent.ACTION_PACKAGE_REMOVED)) {
            serviceIntent.setAction(Constants.INTENT_ACTION_PACKAGE_REMOVED);
        }
        else {
            // Intent.ACTION_USER_PRESENT 是在锁屏操作触发的，并不实时
            serviceIntent.setAction(Constants.INTENT_ACTION_SERVICE_START);
        }

        context.startService(serviceIntent);
    }
}
