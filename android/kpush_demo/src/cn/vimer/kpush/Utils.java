package cn.vimer.kpush;

import android.content.Context;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import android.util.Log;
import org.json.JSONObject;

import java.security.MessageDigest;

/**
 * Created by dantezhu on 15-4-13.
 */
public class Utils {
    public static String genMD5(String val) {
        try{
            MessageDigest md5 = MessageDigest.getInstance("MD5");
            md5.update(val.getBytes());
            byte[] m = md5.digest();//加密
            return hexToString(m);
        }
        catch (Exception e) {
            return null;
        }
    }

    public static String hexToString(byte[] b){
        StringBuffer sb = new StringBuffer();
        for(int i = 0; i < b.length; i ++){
            //sb.append(b[i]);
            sb.append(String.format("%02x", b[i]));
        }
        return sb.toString();
    }

    public static String getMetaValue(Context context, String key) {
        try {
            ApplicationInfo appInfo = context.getPackageManager()
                    .getApplicationInfo(context.getPackageName(),
                            PackageManager.GET_META_DATA);
            return appInfo.metaData.getString(key);
        } catch (Exception e) {
            e.printStackTrace();
        }

        return null;
    }

    public static JSONObject unpackData(byte[] bytesBody) {
        try{
            if (bytesBody == null) {
                return null;
            }

            String body = new String(bytesBody, "UTF-8");

            JSONObject jsonBody = new JSONObject(body);

            String data = jsonBody.getString("data");
            String sign = jsonBody.getString("sign");

            String source = Constants.SECRET + "|" + data;

            String calcSign = genMD5(source);

            if (!sign.equals(calcSign)) {
                Log.e(Constants.LOG_TAG, String.format("sign not equal. sign: %s, calcSign: %s", sign, calcSign));
                return null;
            }

            return new JSONObject(data);
        }
        catch (Exception e) {
            Log.e(Constants.LOG_TAG, "unpackData fail: " + bytesBody);
        }

        return null;
    }

    public static byte[] packData(JSONObject jsonData) {
        try{
            if (jsonData == null) {
                return null;
            }

            JSONObject jsonBody = new JSONObject();

            String data = jsonData.toString();
            String source = Constants.SECRET + "|" + data;
            String sign = genMD5(source);

            jsonBody.put("data", data);
            jsonBody.put("sign", sign);

            return jsonBody.toString().getBytes();
        }
        catch (Exception e) {
            Log.e(Constants.LOG_TAG, "packData fail: " + jsonData.toString());
        }

        return null;
    }

}
