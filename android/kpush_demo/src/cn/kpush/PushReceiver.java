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

        Log.d(Constants.LOG_TAG, "action: " + intent.getAction());
        Intent serviceIntent = new Intent();

        if (intent.getAction().equals("android.intent.action.PACKAGE_ADDED")) {
            serviceIntent.setAction("cn.kpush.intent.PACKAGE_ADDED");
        }
        else if (intent.getAction().equals("android.intent.action.PACKAGE_REMOVED")) {
            serviceIntent.setAction("cn.kpush.intent.PACKAGE_REMOVED");
        }
        else {
            serviceIntent.setAction("cn.kpush.intent.SERVICE_START");
        }

        context.startService(serviceIntent);
    }
}
