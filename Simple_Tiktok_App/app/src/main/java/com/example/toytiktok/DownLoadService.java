package com.example.toytiktok;

import android.app.Service;
import android.content.Intent;
import android.os.Binder;
import android.os.Handler;
import android.os.IBinder;
import android.os.Message;
import android.util.Log;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import com.example.toytiktok.utils.HttpUtil;

public class DownLoadService extends Service {
    public static final int SUCCESS_DOWNLOAD_MSG = 1234;
    public static final int FAILED_DOWNLOAD_MSG = 1235;


    private Handler handler = new Handler() {
        @Override
        public void handleMessage(@NonNull Message msg) {
            switch (msg.what) {
                case SUCCESS_DOWNLOAD_MSG:
                    Toast.makeText(DownLoadService.this, "文件下载至" + msg.obj, Toast.LENGTH_SHORT).show();
                    break;
                case FAILED_DOWNLOAD_MSG:
                    Toast.makeText(DownLoadService.this, "文件下载失败", Toast.LENGTH_SHORT).show();
                    break;
                default:
                    break;
            }
        }
    };

    class MyBinder extends Binder {
        public void download(String path) {
            DownLoadService.this.download(path);
        }
    }

    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return new MyBinder();
    }


    private void download(String path) {
        HttpUtil.downloadVideoByPath(path, handler);
    }

}
