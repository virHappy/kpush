package cn.kpush_demo;

import android.app.Activity;
import android.os.Bundle;
import cn.kpush.KPush;

public class MainActivity extends Activity {
    /**
     * Called when the activity is first created.
     */
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);

        KPush.init(this);
        KPush.setAliasAndTags("dante", new String[]{"a", "c"});
    }
}
