package cn.kpush;

import android.content.Context;
import android.content.Intent;
import android.util.Log;
import cn.vimer.ferry.Ferry;


/**
 * Created by dantezhu on 15-4-13.
 */
public class KPush {

    private static Context context = null;
    private static boolean debug = false;

    public static void init(Context context_) {
        context = context_;

        setDebug(false);

        Intent intent = new Intent(context, PushService.class);
        intent.setAction(Config.INTENT_ACTION_SERVICE_START);
        context_.startService(intent);
    }

    public static void setDebug(boolean debug_) {
        debug = debug_;

        Ferry.setDebug(debug);

        if (debug) {
            KLog.setLevel(Log.DEBUG);
        }
        else {
            KLog.setLevel(Log.ERROR);
        }
    }

    public static boolean getDebug() {
        return debug;
    }

    public static void setAliasAndTags(String alias, String[] tags) {
        Intent intent = new Intent();
        intent.setAction(Config.INTENT_ACTION_SEND_MSG);
        intent.putExtra("cmd", Proto.CMD_SET_ALIAS_AND_TAGS);
        intent.putExtra("alias", alias);
        intent.putExtra("tags", tags);

        context.startService(intent);
    }

    public static Context getContext() {
        return context;
    }
}
