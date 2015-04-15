package cn.kpush;

import android.app.Notification;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.os.AsyncTask;
import android.os.Handler;
import android.os.IBinder;
import android.util.Log;
import cn.vimer.ferry.Ferry;
import cn.vimer.netkit.Box;
import cn.vimer.netkit.IBox;
import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.util.EntityUtils;
import org.json.JSONObject;

/**
 * Created by dantezhu on 15-4-13.
 */
public class PushService extends Service {

    private Handler handler;
    private String serverHost;
    private Integer serverPort;
    private long userId;
    private String userKey;

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    public void onCreate() {
        super.onCreate();

        // 因为service可能重新进来
        DeviceInfo.init(this);

        Log.d(Constants.LOG_TAG, "onCreate");

        handler = new Handler();

        regEventCallback();

    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        // 每次发intent都会进来，可以重复进入
        Log.d(Constants.LOG_TAG, "onStartCommand. action: " + (intent == null ? null : intent.getAction()));
        return super.onStartCommand(intent, flags, startId);
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        Ferry.getInstance().stop();
        Log.d(Constants.LOG_TAG, "onDestory");
    }

    private void connectToServer() {
        Ferry.getInstance().init(serverHost, serverPort);
        if (Ferry.getInstance().isRunning()) {
            Ferry.getInstance().connect();
        }
        else {
            Ferry.getInstance().start();
        }
    }

    private void regEventCallback() {
        Ferry.getInstance().addEventCallback(new Ferry.CallbackListener() {
            @Override
            public void onOpen() {
                Log.d(Constants.LOG_TAG, "onOpen");

                userLogin();
            }

            @Override
            public void onRecv(IBox ibox) {
                Log.d(Constants.LOG_TAG, String.format("onRecv, box: %s", ibox));
                Box box = (Box) ibox;

                JSONObject jsonData = Utils.unpackData(box.body);

                if (box.cmd == Proto.EVT_NOTIFICATION) {
                    if (jsonData != null) {
                        try {
                            showNotification(jsonData.getString("title"), jsonData.getString("content"));
                        } catch (Exception e) {
                            Log.e(Constants.LOG_TAG, String.format("exc occur. e: %s, box: %s", e, box));
                        }
                    }
                }
            }

            @Override
            public void onClose() {
                Log.d(Constants.LOG_TAG, "onClose");
                // Ferry.getInstance().connect();
                // 从获取IP开始
                allocServer();
            }

            @Override
            public void onError(int code, IBox ibox) {
                Log.d(Constants.LOG_TAG, String.format("onError, code: %s, box: %s", code, ibox));
            }

        }, this, "main");
    }

    private void userLogin() {

        Log.d(Constants.LOG_TAG, "userLogin");

        Box box = new Box();
        box.cmd = Proto.CMD_LOGIN;
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put("uid", userId);
            jsonObject.put("key", userKey);
            jsonObject.put("os", Constants.OS);
            jsonObject.put("sdk_version", Constants.SDK_VERSION);
            jsonObject.put("os_version", DeviceInfo.getOsVersion());
        } catch (Exception e) {
        }

        Log.d(Constants.LOG_TAG, jsonObject.toString());

        String body = Utils.packData(jsonObject);

        box.body = body == null ? null:body.getBytes();

        Ferry.getInstance().send(box, new Ferry.CallbackListener() {
            @Override
            public void onSend(IBox ibox) {
                Log.d(Constants.LOG_TAG, String.format("onSend, box: %s", ibox));
            }

            @Override
            public void onRecv(IBox ibox) {
                Log.d(Constants.LOG_TAG, String.format("onRecv, box: %s", ibox));
                Box box = (Box) ibox;
                // Log.d(Constants.LOG_TAG, "data: " + Utils.unpackData(box.body));

                if (box.ret != 0) {
                    // 几秒后再重试
                    userLoginLater();
                }
            }

            @Override
            public void onError(int code, IBox ibox) {
                Log.d(Constants.LOG_TAG, String.format("onError, code: %s, box: %s", code, ibox));
                userLoginLater();
            }

            @Override
            public void onTimeout() {
                Log.d(Constants.LOG_TAG, "onTimeout");

                userLoginLater();
            }
        }, 5, this);
    }

    private void userLoginLater() {
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                userLogin();
            }
        }, Constants.ERROR_RETRY_INTERVAL * 1000);
    }


    private void allocServer() {
        // 申请 server
        new AllocServerTask().execute();
    }

    private void allocServerLater() {
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                // 重新申请
                allocServer();
            }
        }, Constants.ERROR_RETRY_INTERVAL * 1000);
    }

    private void showNotification(String title, String content) {
        //消息通知栏
        //定义NotificationManager
        String ns = Context.NOTIFICATION_SERVICE;
        NotificationManager mNotificationManager = (NotificationManager) getSystemService(ns);
        //定义通知栏展现的内容信息
        CharSequence tickerText = title;
        long when = System.currentTimeMillis();

        //定义下拉通知栏时要展现的内容信息
        Intent notificationIntent = new Intent(this, PushActivity.class);
        PendingIntent contentIntent = PendingIntent.getActivity(this, 0,
                notificationIntent, 0);
        Notification notification = new Notification(DeviceInfo.getAppIconId(), tickerText, when);
        notification.setLatestEventInfo(this, title, content,
                contentIntent);
        //在通知栏上点击此通知后自动清除此通知
        notification.flags |= Notification.FLAG_AUTO_CANCEL;
        /*
        //添加声音
        notification.defaults |=Notification.DEFAULT_SOUND;
        // 添加振动
        notification.defaults |= Notification.DEFAULT_VIBRATE;
        */

        //用mNotificationManager的notify方法通知用户生成标题栏消息通知
        int nfyid = 0;
        mNotificationManager.notify(nfyid, notification);
    }

    private class AllocServerTask extends AsyncTask<String, Integer, Integer> {
        JSONObject jsonData;

        @Override
        protected void onPreExecute() {
        }

        @Override
        protected Integer doInBackground(String... params) {
            try{
                HttpClient httpClient = new DefaultHttpClient();

                HttpPost httpPost = new HttpPost(Constants.ALLOC_SERVER_URL);

                JSONObject jsonObject = new JSONObject();
                jsonObject.put("appkey", DeviceInfo.getAppkey());
                jsonObject.put("channel", DeviceInfo.getChannel());
                jsonObject.put("device_id", DeviceInfo.getDeviceId());
                jsonObject.put("device_name", DeviceInfo.getDeviceName());
                jsonObject.put("os_version", DeviceInfo.getOsVersion());
                jsonObject.put("os", Constants.OS);
                jsonObject.put("sdk_version", Constants.SDK_VERSION);

                Log.d(Constants.LOG_TAG, jsonObject.toString());

                String postBody = Utils.packData(jsonObject);
                if (postBody == null) {
                    return -1;
                }

                httpPost.setEntity(new StringEntity(postBody));

                HttpResponse httpResponse = httpClient.execute(httpPost);
                int code = httpResponse.getStatusLine().getStatusCode();
                if (code == 200) {
                    String recvBody = EntityUtils.toString(httpResponse.getEntity());

                    jsonData = Utils.unpackData(recvBody);

                    if (jsonData == null) {
                        return -3;
                    }

                    // 解析成功
                    return 0;
                }
                else {
                    return -4;
                }
            }
            catch (Exception e) {
                Log.e(Constants.LOG_TAG, "fail: " + e.toString());

                return -2;
            }
        }

        @Override
        protected void onProgressUpdate(Integer... progresses) {
        }

        @Override
        protected void onPostExecute(Integer result) {
            if (result != 0) {
                // 说明失败
                allocServerLater();

                return;
            }

            try{
                serverHost = jsonData.getJSONObject("server").getString("host");
                serverPort = jsonData.getJSONObject("server").getInt("port");
                userId = jsonData.getJSONObject("user").getLong("uid");
                userKey = jsonData.getJSONObject("user").getString("key");
            }
            catch (Exception e) {
                Log.e(Constants.LOG_TAG, "fail: " + e.toString());

                allocServerLater();
                return;
            }

            connectToServer();
        }

        @Override
        protected void onCancelled() {
        }
    }

}
