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
import cn.vimer.ferry.Ferry;
import cn.vimer.netkit.Box;
import cn.vimer.netkit.IBox;
import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.util.EntityUtils;
import org.json.JSONArray;
import org.json.JSONObject;

import java.util.concurrent.ArrayBlockingQueue;


/**
 * Created by dantezhu on 15-4-13.
 */
public class PushService extends Service {

    private Handler handler;
    private String serverHost;
    private Integer serverPort;
    private long userId;
    private String userKey;

    // 一开始就是未验证通过的
    private boolean userAuthed;

    private ArrayBlockingQueue<Box> pendingMsgs = new ArrayBlockingQueue<Box>(Config.MAX_PENDING_MSGS);

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    public void onCreate() {
        super.onCreate();
        KLog.d("");

        // 初始化的时候
        userAuthed = false;

        // 因为service可能重新进来
        DeviceInfo.init(this);
        handler = new Handler();

        regEventCallback();
        allocServer();
        // 启动心跳
        heartbeat();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        // 每次发intent都会进来，可以重复进入
        KLog.d("action: " + (intent == null ? null : intent.getAction()));
        int result = super.onStartCommand(intent, flags, startId);

        if (intent != null) {
            if (intent.getAction().equals(Config.INTENT_ACTION_SEND_MSG)) {
                switch (intent.getIntExtra("cmd", 0)) {
                    case Proto.CMD_SET_ALIAS_AND_TAGS:
                        // 设置
                        setAliasAndTags(
                                intent.getStringExtra("alias"),
                                intent.getStringArrayExtra("tags")
                        );
                        break;
                    case Proto.CMD_NOTIFICATION_CLICK:
                        clickNotification(intent.getIntExtra("notification_id", 0));
                        break;
                }
            }
        }

        return result;
    }

    @Override
    public void onDestroy() {
        KLog.d("");
        super.onDestroy();
        Ferry.getInstance().stop();
    }

    private void connectToServer() {
        Ferry.getInstance().init(serverHost, serverPort);
        if (Ferry.getInstance().isRunning()) {
            if (!Ferry.getInstance().isConnected()) {
                Ferry.getInstance().connect();
            }
        }
        else {
            Ferry.getInstance().start();
        }
    }

    private void regEventCallback() {
        Ferry.getInstance().addEventCallback(new Ferry.CallbackListener() {
            @Override
            public void onOpen() {

                userLogin();
            }

            @Override
            public void onRecv(IBox ibox) {
                Box box = (Box) ibox;

                JSONObject jsonData = Utils.unpackData(box.body);

                if (box.cmd == Proto.EVT_NOTIFICATION) {
                    if (jsonData != null) {
                        try {
                            int notificationID = jsonData.getInt("id");

                            recvNotification(notificationID);

                            boolean silent = false;
                            if (jsonData.has("silent")) {
                                silent = jsonData.getBoolean("silent");
                            }

                            if (!silent) {
                                showNotification(notificationID, jsonData.getString("title"), jsonData.getString("content"));
                            }
                        } catch (Exception e) {
                            KLog.e(String.format("exc occur. e: %s, box: %s", e, box));
                        }
                    }
                }
            }

            @Override
            public void onClose() {
                userAuthed = false;
                KLog.d("");
                // Ferry.getInstance().connect();
                // 从获取IP开始
                allocServer();
            }

            @Override
            public void onError(int code, IBox ibox) {
            }

        }, this, "main");
    }

    private void userLogin() {

        Box box = new Box();
        box.cmd = Proto.CMD_LOGIN;
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put("uid", userId);
            jsonObject.put("key", userKey);
        } catch (Exception e) {
            KLog.e("exc occur. e: " + e);
        }

        String body = Utils.packData(jsonObject);

        box.body = body == null ? null:body.getBytes();

        Ferry.getInstance().send(box, new Ferry.CallbackListener() {
            @Override
            public void onSend(IBox ibox) {
            }

            @Override
            public void onRecv(IBox ibox) {
                Box box = (Box) ibox;

                if (box.ret != 0) {
                    // 几秒后再重试
                    userLoginLater();
                } else {
                    // 登录成功
                    userAuthed = true;

                    sendPendingMsgs();
                }
            }

            @Override
            public void onError(int code, IBox ibox) {
                userLoginLater();
            }

            @Override
            public void onTimeout() {
                KLog.d("");

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
        }, Config.ERROR_RETRY_INTERVAL * 1000);
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
        }, Config.ERROR_RETRY_INTERVAL * 1000);
    }

    private boolean setAliasAndTags(String alias, String[] tags) {
        Box box = new Box();
        box.cmd = Proto.CMD_SET_ALIAS_AND_TAGS;

        JSONObject jsonObject = new JSONObject();
        try{
            if (alias != null) {
                jsonObject.put("alias", alias);
            }
            if (tags != null) {
                JSONArray jsonArray = new JSONArray();
                for(int i=0; i<tags.length; i++) {
                    jsonArray.put(tags[i]);
                }
                jsonObject.put("tags", jsonArray);
            }

            String body = Utils.packData(jsonObject);
            box.body = body == null ? null:body.getBytes();
        }
        catch (Exception e) {
            KLog.e("exc occur. e: " + e);
            return false;
        }


        // 因为一定是在主线程里操作
        if (userAuthed) {
            // 其实是可以支持回调的
            Ferry.getInstance().send(box);
            return true;
        }
        else {
            // 不要阻塞
            return pendingMsgs.offer(box);
        }
    }

    private boolean recvNotification(int notificationID) {
        Box box = new Box();
        box.cmd = Proto.CMD_NOTIFICATION_RECV;

        JSONObject jsonObject = new JSONObject();
        try{
            jsonObject.put("notification_id", notificationID);

            String body = Utils.packData(jsonObject);
            box.body = body == null ? null:body.getBytes();
        }
        catch (Exception e) {
            KLog.e("exc occur. e: " + e);
            return false;
        }

        // 因为一定是在主线程里操作
        if (userAuthed) {
            // 其实是可以支持回调的
            Ferry.getInstance().send(box);
            return true;
        }
        else {
            // 不要阻塞
            return pendingMsgs.offer(box);
        }
    }

    private boolean clickNotification(int notificationID) {
        Box box = new Box();
        box.cmd = Proto.CMD_NOTIFICATION_CLICK;

        JSONObject jsonObject = new JSONObject();
        try{
            jsonObject.put("notification_id", notificationID);

            String body = Utils.packData(jsonObject);
            box.body = body == null ? null:body.getBytes();
        }
        catch (Exception e) {
            KLog.e("exc occur. e: " + e);
            return false;
        }

        // 因为一定是在主线程里操作
        if (userAuthed) {
            // 其实是可以支持回调的
            Ferry.getInstance().send(box);
            return true;
        }
        else {
            // 不要阻塞
            return pendingMsgs.offer(box);
        }
    }

    private void heartbeat() {
        Box box = new Box();
        box.cmd = Proto.CMD_HEARTBEAT;

        // TODO 检测服务器超时
        if (Ferry.getInstance().isConnected()) {
            // 心跳
            Ferry.getInstance().send(box);
        }

        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                heartbeat();
            }
        }, Config.HEARTBEAT_INTERVAL * 1000);

        // 该发送的还是发送
        if (System.currentTimeMillis() - Ferry.getInstance().getLastRecvTimeMills() > Config.CONN_ALIVE_TIMEOUT * 1000) {
            // 说明链接已经断开
            Ferry.getInstance().disconnect();
        }
    }

    private void sendPendingMsgs() {
        while (true) {
            // 不阻塞
            Box box = pendingMsgs.poll();
            if (box == null) {
                break;
            }

            // 其实还是可以有回调的
            Ferry.getInstance().send(box);
        }
    }

    private void showNotification(int ID, String title, String content) {
        //消息通知栏
        //定义NotificationManager
        String ns = Context.NOTIFICATION_SERVICE;
        NotificationManager notificationManager = (NotificationManager) getSystemService(ns);
        //定义通知栏展现的内容信息
        CharSequence tickerText = title;
        long when = System.currentTimeMillis();

        //定义下拉通知栏时要展现的内容信息
        Intent notificationIntent = new Intent(this, PushActivity.class);
        // 让activiy可以取到
        notificationIntent.putExtra("notification_id", ID);

        // 对于FLAG_UPDATE_CURRENT,如果上面的num为常量， 则所有对应的Intent里面的extra被更新为最新的， 就是全部为最后一次的。
        // 相反，如果num每次不一样，则里面的Intent的数据没被更新。
        // 所以要通过extra数据来区分intent，应采用PendingIntent.FLAG_UPDATE_CURRENT)，且每次num不一样
        PendingIntent contentIntent = PendingIntent.getActivity(this, ID,
                notificationIntent, PendingIntent.FLAG_UPDATE_CURRENT);

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
        // 固定用0，这样就不会显示很多通知了
        notificationManager.notify(0, notification);
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

                HttpPost httpPost = new HttpPost(Config.ALLOC_SERVER_URL);

                JSONObject jsonObject = new JSONObject();
                jsonObject.put("appkey", DeviceInfo.getAppkey());
                jsonObject.put("channel", DeviceInfo.getChannel());
                jsonObject.put("device_id", DeviceInfo.getDeviceId());
                jsonObject.put("device_name", DeviceInfo.getDeviceName());
                jsonObject.put("os_version", DeviceInfo.getOsVersion());
                jsonObject.put("os", Config.OS);
                jsonObject.put("sdk_version", Config.SDK_VERSION);

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
                KLog.e("fail: " + e.toString());

                return -2;
            }
        }

        @Override
        protected void onProgressUpdate(Integer... progresses) {
        }

        @Override
        protected void onPostExecute(Integer result) {
            KLog.d("result: " + result);
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
                KLog.e("fail: " + e.toString());

                allocServerLater();
                return;
            }

            connectToServer();
        }

        @Override
        protected void onCancelled() {
            KLog.d("");
            allocServerLater();
        }
    }

}
