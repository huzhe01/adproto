package com.example.toytiktok;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.util.Log;
import android.widget.Toast;

public class NetReceiver extends BroadcastReceiver {

    @Override
    public void onReceive(Context context, Intent intent) {
        Log.d("tag", "net");
        ConnectivityManager manager = (ConnectivityManager) context.getSystemService(Context.CONNECTIVITY_SERVICE);
        NetworkInfo info = manager.getActiveNetworkInfo();
        if (info != null && info.isAvailable()) {
            Toast.makeText(context, "网络恢复", Toast.LENGTH_SHORT).show();
        } else {
            Toast.makeText(context, "当前无网络, 请检查后重试", Toast.LENGTH_SHORT).show();
        }
    }
}