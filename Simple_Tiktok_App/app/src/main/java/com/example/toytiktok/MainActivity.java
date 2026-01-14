package com.example.toytiktok;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.PagerSnapHelper;
import androidx.recyclerview.widget.RecyclerView;

import android.Manifest;
import android.content.ComponentName;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.ServiceConnection;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.IBinder;
import android.os.Message;
import android.util.Log;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.Toast;

import com.airbnb.lottie.LottieAnimationView;
import com.example.toytiktok.fragments.AdFragment;
import com.example.toytiktok.fragments.HomePageFragment;
import com.example.toytiktok.fragments.LoginFragment;
import com.example.toytiktok.fragments.MessageFragment;
import com.example.toytiktok.fragments.PersonalFragment;
import com.example.toytiktok.utils.HttpUtil;

import java.util.ArrayList;
import java.util.List;

public class MainActivity extends AppCompatActivity
        implements View.OnClickListener, DownloadCallBack, LoginFragment.LoginCallback, VideoDownLoadCallback {
    private static final int SUCCESS_FETCH_MSG = 10003;

    private FrameLayout container;
    private Button preComponent;
    private int preId;
    private Button homepage, friend, message, me;
    private ImageButton record;

    private boolean isLogin;
    private String userName;
    private String id;

    private LottieAnimationView loadView;
    private ImageView coverImage;

    private NetReceiver receiver;

    private ServiceConnection conn;
    private DownLoadService.MyBinder binder;

    private Handler handler = new Handler() {
        @Override
        public void handleMessage(@NonNull Message msg) {
            switch (msg.what) {
                case SUCCESS_FETCH_MSG:
                    init();
                    break;
                default:
                    break;
            }
        }
    };

    public boolean isLogin() {
        return isLogin;
    }

    public void setLogin(boolean login) {
        isLogin = login;
    }

    public String getUserName() {
        return userName;
    }

    public void setUserName(String userName) {
        this.userName = userName;
    }

    String[] permissionList = new String[] { Manifest.permission.WRITE_EXTERNAL_STORAGE, Manifest.permission.CAMERA,
            Manifest.permission.RECORD_AUDIO };

    private final static int REQUEST_PERMISSION = 123;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        container = findViewById(R.id.container);
        homepage = findViewById(R.id.homepage);
        friend = findViewById(R.id.friend);
        message = findViewById(R.id.message);
        me = findViewById(R.id.me);
        record = findViewById(R.id.record);
        loadView = findViewById(R.id.main_loading);
        coverImage = findViewById(R.id.main_cover);

        Intent intent = new Intent(MainActivity.this, DownLoadService.class);
        startService(intent);
        conn = new DownloadServiceConn();
        bindService(intent, conn, BIND_AUTO_CREATE);

        if (savedInstanceState != null) {
            isLogin = savedInstanceState.getBoolean("loginStatus", false);
            userName = savedInstanceState.getString("userName", null);
            id = savedInstanceState.getString("id", null);
        }

        if (HttpUtil.infos == null) {
            HttpUtil.download(MainActivity.this);
        } else {
            init();
        }

    }

    private void init() {
        loadView.setVisibility(View.GONE);
        coverImage.setVisibility(View.GONE);

        replaceFragment(new HomePageFragment());
        preComponent = homepage;
        preId = R.id.homepage;

        homepage.setOnClickListener(this);
        friend.setOnClickListener(this);
        message.setOnClickListener(this);
        me.setOnClickListener(this);
        record.setOnClickListener(this);

        receiver = new NetReceiver();
        IntentFilter filter = new IntentFilter();
        filter.addAction("android.net.conn.CONNECTIVITY_CHANGE");
        registerReceiver(receiver, filter);

    }

    @Override
    public void downloadVideoCallback(String path) {
        binder.download(path);
    }

    class DownloadServiceConn implements ServiceConnection {

        @Override
        public void onServiceConnected(ComponentName name, IBinder service) {
            binder = (DownLoadService.MyBinder) service;
        }

        @Override
        public void onServiceDisconnected(ComponentName name) {

        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        unregisterReceiver(receiver);
        unbindService(conn);
    }

    @Override
    public void onClick(View v) {
        int id = v.getId();
        if (id == R.id.homepage || id == R.id.friend || id == R.id.message || id == R.id.me) {
            if (id == preId)
                return;
            preComponent.setTextColor(getResources().getColor(R.color.unchosen));
            preId = id;
        }
        switch (v.getId()) {
            case R.id.homepage:
                homepage.setTextColor(getResources().getColor(R.color.chosen));
                preComponent = homepage;
                replaceFragment(new HomePageFragment());
                break;
            case R.id.friend:
                friend.setTextColor(getResources().getColor(R.color.chosen));
                preComponent = friend;
                replaceFragment(new AdFragment()); // 替换为广告推荐页面
                break;
            case R.id.message:
                message.setTextColor(getResources().getColor(R.color.chosen));
                preComponent = message;
                replaceFragment(new MessageFragment());
                break;
            case R.id.me:
                me.setTextColor(getResources().getColor(R.color.chosen));
                preComponent = me;
                if (isLogin) {
                    replaceFragment(PersonalFragment.getFragment(userName, this.id));
                } else {
                    replaceFragment(new LoginFragment());
                }
                break;
            case R.id.record:
                List<String> todo = new ArrayList<>();
                for (String permission : permissionList) {
                    if (ContextCompat.checkSelfPermission(MainActivity.this,
                            permission) != PackageManager.PERMISSION_GRANTED) {
                        todo.add(permission);
                    }
                    Log.d("res", "num : " + todo.toString());
                }
                if (todo.size() != 0) {
                    ActivityCompat.requestPermissions(MainActivity.this, todo.toArray(new String[0]), 1);
                    Log.d("res", "request");
                } else {
                    jump();
                }

                break;
            default:
                break;
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions,
            @NonNull int[] grantResults) {
        if (grantResults.length > 0) {

            // Log.d("res", "len : " + grantResults.length);
            // for (int res : grantResults) {
            // Log.d("res", res+"");
            // }
            for (int res : grantResults) {
                if (res != PackageManager.PERMISSION_GRANTED) {
                    Toast.makeText(MainActivity.this, "refuse", Toast.LENGTH_SHORT).show();
                    return;
                }
            }
            jump();
        }
    }

    private void jump() {
        Intent intent = new Intent(MainActivity.this, MultiMediaActivity.class);
        startActivity(intent);
    }

    @Override
    protected void onSaveInstanceState(@NonNull Bundle outState) {
        super.onSaveInstanceState(outState);
        outState.putString("userName", userName);
        outState.putBoolean("loginStatus", isLogin);
        outState.putString("id", id);
    }

    private void open(int buttonId, final Class<?> clz) {
        findViewById(buttonId).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startActivity(new Intent(MainActivity.this, clz));
            }
        });
    }

    public void replaceFragment(Fragment fragment) {
        // friend / message fragment will not be implemented at present
        if (fragment == null)
            return;

        getSupportFragmentManager().beginTransaction().replace(R.id.container, fragment).commit();
    }

    @Override
    public void callback() {
        handler.sendEmptyMessage(SUCCESS_FETCH_MSG);
    }

    @Override
    public void loginCallBack(String userName, String id) {
        isLogin = true;
        this.userName = userName;
        this.id = id;
        replaceFragment(PersonalFragment.getFragment(userName, id));
    }
}