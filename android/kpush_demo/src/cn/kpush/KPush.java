package cn.kpush;

import android.content.Context;
import android.content.Intent;


/**
 * Created by dantezhu on 15-4-13.
 */
public class KPush {

    private static Context context = null;

    public static void init(Context context) {
        KPush.context = context;

        Intent intent = new Intent();
        intent.setAction(Config.INTENT_ACTION_SERVICE_START);
        context.startService(intent);
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
