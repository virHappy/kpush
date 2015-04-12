package cn.vimer.kpush;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;
import android.util.Log;
import cn.vimer.ferry.Ferry;
import cn.vimer.kpush_demo.Constants;
import cn.vimer.netkit.Box;
import cn.vimer.netkit.IBox;

/**
 * Created by dantezhu on 15-4-13.
 */
public class PushService extends Service {
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    public void onCreate() {
        super.onCreate();
        Log.d(Constants.LOG_TAG, "onCreate");

        regEventCallback();

        Ferry.getInstance().init("192.168.1.77", 29000);
        Ferry.getInstance().start();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        // 每次发intent都会进来，可以重复进入
        Log.d(Constants.LOG_TAG, "onStartCommand");
        return super.onStartCommand(intent, flags, startId);
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        Log.d(Constants.LOG_TAG, "onDestory");
    }

    private void regEventCallback() {
        Ferry.getInstance().addEventCallback(new Ferry.CallbackListener() {
            @Override
            public void onOpen() {
                Log.d(Constants.LOG_TAG, "onOpen");

                Box box = new Box();
                box.version = 100;
                box.flag = 99;
                box.cmd = 1;
                box.body = new String("I love you").getBytes();

                Ferry.getInstance().send(box, new Ferry.CallbackListener() {
                    @Override
                    public void onSend(IBox ibox) {
                        Log.d(Constants.LOG_TAG, String.format("onSend, box: %s", ibox));
                    }

                    @Override
                    public void onRecv(IBox ibox) {
                        Log.d(Constants.LOG_TAG, String.format("onRecv, box: %s", ibox));
                    }

                    @Override
                    public void onError(int code, IBox ibox) {
                        Log.d(Constants.LOG_TAG, String.format("onError, code: %s, box: %s", code, ibox));
                    }

                    @Override
                    public void onTimeout() {
                        Log.d(Constants.LOG_TAG, "onTimeout");
                    }
                }, 5, this);
            }

            @Override
            public void onRecv(IBox ibox) {
                Log.d(Constants.LOG_TAG, String.format("onRecv, box: %s", ibox));
            }

            @Override
            public void onClose() {
                Log.d(Constants.LOG_TAG, "onClose");
                Ferry.getInstance().connect();
            }

            @Override
            public void onError(int code, IBox ibox) {
                Log.d(Constants.LOG_TAG, String.format("onError, code: %s, box: %s", code, ibox));
            }

        }, this, "ok");
    }

}
