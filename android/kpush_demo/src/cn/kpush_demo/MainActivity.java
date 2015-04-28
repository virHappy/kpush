package cn.kpush_demo;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import cn.kpush.KPush;

public class MainActivity extends Activity {

    Handler handler = new Handler();

    /**
     * Called when the activity is first created.
     */
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);

        KPush.init(this);
        KPush.setDebug(true);
        // KPush.setAliasAndTags("dante", new String[]{"a", "c"});

        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                startActivity(new Intent(MainActivity.this, NextActivity.class));
            }
        }, 5 * 1000);
    }
}
