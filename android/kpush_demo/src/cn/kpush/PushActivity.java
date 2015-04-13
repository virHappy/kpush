package cn.kpush;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;

/**
 * Created by dantezhu on 15-4-14.
 */
public class PushActivity extends Activity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        Intent intent = new Intent();
        intent.setAction(Intent.ACTION_MAIN);
        intent.addCategory(Intent.CATEGORY_LAUNCHER);

        //startActivity(intent);
    }
}