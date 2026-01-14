package com.example.toytiktok;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import com.example.toytiktok.utils.HttpUtil;

public class UploadActivity extends AppCompatActivity {

    private static final int IMAGE_REQUEST_CODE = 9023;
    private static final int VIDEO_REQUEST_CODE = 9024;

    Button image, video, upload;
    TextView imagePath, videoPath;

    private Handler handler = new Handler() {
        @Override
        public void handleMessage(@NonNull Message msg) {
            switch (msg.what) {
                case DownLoadService.SUCCESS_DOWNLOAD_MSG:
                    Toast.makeText(UploadActivity.this, "成功上传", Toast.LENGTH_SHORT).show();
                    break;
                case DownLoadService.FAILED_DOWNLOAD_MSG:
                    Toast.makeText(UploadActivity.this, "上传失败", Toast.LENGTH_SHORT).show();
                    break;
                default:
                    break;
            }
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_upload);


        image = findViewById(R.id.upload_image_btn);
        video = findViewById(R.id.upload_video_btn);
        upload = findViewById(R.id.upload_btn);

        imagePath = findViewById(R.id.upload_image_path);
        videoPath = findViewById(R.id.upload_video_path);

        image.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                pickFile(IMAGE_REQUEST_CODE);
            }
        });

        video.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                pickFile(VIDEO_REQUEST_CODE);
            }
        });

        upload.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (HttpUtil.userName == null) {
                    Toast.makeText(UploadActivity.this, "上传之前请登录", Toast.LENGTH_SHORT).show();
                    return;
                }

                String imPath = imagePath.getText().toString();
                String viPath = videoPath.getText().toString();
                if (imPath.length() == 0 || viPath.length() == 0) {
                    if (imPath.length() == 0) {
                        Toast.makeText(UploadActivity.this, "请选择图片", Toast.LENGTH_SHORT).show();
                    }
                    if (viPath.length() == 0) {
                        Toast.makeText(UploadActivity.this, "请选择视频", Toast.LENGTH_SHORT).show();
                    }
                    return;
                }

                HttpUtil.upload(HttpUtil.userName, imPath, viPath, "extra_info", handler);

            }
        });

    }


    @Override
    protected void onActivityResult(final int requestCode, final int resultCode, @Nullable final Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if (data == null || resultCode != RESULT_OK) {
            return;
        }

        Uri uri = data.getData();
        String path = uri.getPath();
        int idx = path.indexOf(":");
        String filename = path.substring(idx+1);

        switch (requestCode) {
            case IMAGE_REQUEST_CODE:
                imagePath.setText(filename);
                break;
            case VIDEO_REQUEST_CODE:
                videoPath.setText(filename);
                break;
            default:
                break;
        }
    }

    public void pickFile(int code) {
        Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("*/*");
        this.startActivityForResult(intent, code);
    }
}