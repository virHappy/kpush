package cn.kpush;

import android.content.Context;
import android.content.SharedPreferences;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.graphics.drawable.Drawable;
import android.os.Build;
import android.provider.Settings;
import android.telephony.TelephonyManager;

import java.util.UUID;

/**
 * Created by dantezhu on 15-4-13.
 */
public class DeviceInfo {
    // 默认从清单文件里获取
    private static String appkey = null;
    private static String channel = null;

    private static String packageName = null;
    private static int appVersion = 0;
    private static String deviceId = null;
    private static int osVersion = 0;
    private static String deviceName = null;
    private static Drawable appIcon = null;
    private static int appIconId = 0;

    private static Context context = null;

    public static void init(Context context) {
        DeviceInfo.context = context;

        initVals();

        KLog.v(String.format(
                        "packageName: %s, appVersion: %s, deviceId: %s, osVersion: %s, deviceName: %s",
                        packageName, appVersion, deviceId, osVersion, deviceName
                )
        );

    }

    private static void initVals() {
        appkey = Utils.getMetaValue(context, "KPUSH_APPKEY");
        channel = Utils.getMetaValue(context, "KPUSH_CHANNEL");

        packageName = context.getPackageName();

        try
        {
            PackageInfo packageInfo = context.getPackageManager().getPackageInfo(packageName, PackageManager.GET_CONFIGURATIONS);
            appVersion = packageInfo.versionCode;
            appIcon = packageInfo.applicationInfo.loadIcon(context.getPackageManager());
            appIconId = packageInfo.applicationInfo.icon;
        }
        catch (Exception e) {
            KLog.e("get versionCode fail");
        }

        initDeviceId();

        deviceName = Build.MODEL;
        osVersion = Build.VERSION.SDK_INT;
    }


    public static Context getContext() {
        return context;
    }

    public static String getPackageName() {
        return packageName;
    }

    public static int getAppVersion() {
        return appVersion;
    }

    public static String getDeviceId() {
        return deviceId;
    }

    public static int getOsVersion() {
        return osVersion;
    }

    public static String getDeviceName() {
        return deviceName;
    }

    public static Drawable getAppIcon() {
        return appIcon;
    }

    public static int getAppIconId() {
        return appIconId;
    }

    public static String getAppkey() {
        return appkey;
    }

    public static String getChannel() {
        return channel;
    }

    private static void initDeviceId() {
        SharedPreferences sharedPreferences = context.getSharedPreferences(Constants.PREFS_NAME, 0);

        String tmpDeviceId = sharedPreferences.getString("device_id", null);

        if (tmpDeviceId != null && !tmpDeviceId.isEmpty()) {
            deviceId = tmpDeviceId;
            return;
        }

        tmpDeviceId = Settings.Secure.getString(context.getContentResolver(), Settings.Secure.ANDROID_ID);
        if (tmpDeviceId == null || tmpDeviceId.isEmpty() || "9774d56d682e549c".equals(tmpDeviceId)) {
            tmpDeviceId = ((TelephonyManager)context.getSystemService(Context.TELEPHONY_SERVICE)).getDeviceId();
        }

        if (tmpDeviceId != null && !tmpDeviceId.isEmpty()) {
            deviceId = UUID.nameUUIDFromBytes(tmpDeviceId.getBytes()).toString();
        }
        else {
            deviceId = UUID.randomUUID().toString();
        }

        // apply
        sharedPreferences.edit().putString("device_id", deviceId).apply();
    }
}
