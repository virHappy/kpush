package cn.kpush;

import android.app.Activity;
import android.content.ComponentName;
import android.content.Intent;
import android.content.pm.ResolveInfo;
import android.os.Bundle;
import android.os.Handler;

import java.util.List;

/**
 * Created by dantezhu on 15-4-14.
 */
public class PushActivity extends Activity {
    private Handler handler = new Handler();

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    protected void onResume() {
        super.onResume();

        // 移到onResume里，finish可能不会立即让activity析构？
        // 但是移到onResume还是有时候调用不到这个activity
        Intent comingIntent = getIntent();
        int notificationID = comingIntent.getIntExtra("notification_id", 0);

        KLog.d("notification_id: " + notificationID);

        sendClickNotificationMsg(notificationID);

        openAppMainActivity();

        handler.post(new Runnable() {
            @Override
            public void run() {
                // 关闭自己
                PushActivity.this.finish();
            }
        });
    }

    private void openAppMainActivity() {
        Intent resolveIntent = new Intent(Intent.ACTION_MAIN, null);
        resolveIntent.addCategory(Intent.CATEGORY_LAUNCHER);
        resolveIntent.setPackage(DeviceInfo.getPackageName());

        List<ResolveInfo> apps = getPackageManager().queryIntentActivities(resolveIntent, 0);

        ResolveInfo ri = apps.iterator().next();
        if (ri != null ) {
            String packageName = ri.activityInfo.packageName;
            String className = ri.activityInfo.name;

            Intent intent = new Intent(Intent.ACTION_MAIN);
            intent.addCategory(Intent.CATEGORY_LAUNCHER);

            // 如果已经存在，就用现有的，并放到ui栈顶
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);

            ComponentName cn = new ComponentName(packageName, className);

            intent.setComponent(cn);
            startActivity(intent);
        }
    }

    private void sendClickNotificationMsg(int notificationID) {
        Intent serviceIntent = new Intent();

        serviceIntent.setAction(Config.INTENT_ACTION_SEND_MSG);
        serviceIntent.putExtra("cmd", Proto.CMD_NOTIFICATION_CLICK);
        serviceIntent.putExtra("notification_id", notificationID);

        startService(serviceIntent);
    }
}