package com.example.toytiktok.utils;

import android.content.res.AssetManager;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Message;
import android.util.Log;
import android.view.View;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.example.toytiktok.DownLoadService;
import com.example.toytiktok.DownloadCallBack;
import com.example.toytiktok.bean.Info;
import com.example.toytiktok.bean.VideoInfo;
import com.example.toytiktok.constant.FileType;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.RequestBody;
import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

public class HttpUtil {
    private static final String TAG = "httputil";
    private static final String baseUrl = "https://api-sjtu-camp.bytedance.com/invoke/";
    private static Retrofit retrofit = new Retrofit.Builder().baseUrl(baseUrl)
            .addConverterFactory(GsonConverterFactory.create()).build();

    public static List<Info> infos;
    public static List<Info> userInfos;
    public static String userName;

    public static enum ResType {
        ALL, PART;
    }

    public static void download(DownloadCallBack callBack) {
        DownloadService downloadService = retrofit.create(DownloadService.class);
        downloadService.download().enqueue(new Callback<VideoInfo>() {
            @Override
            public void onResponse(Call<VideoInfo> call, Response<VideoInfo> response) {
                if (response.isSuccessful()) {
                    VideoInfo vis = response.body();
                    infos = vis.getFeeds();
                }
                // 无论是否成功都继续初始化，避免卡死
                callBack.callback();
            }

            @Override
            public void onFailure(Call<VideoInfo> call, Throwable t) {
                Log.d(TAG, "operation failed: ", t);
                // 失败也继续初始化
                callBack.callback();
            }
        });
    }

    public static void downloadById(DownloadCallBack callBack, String id) {
        FilteredDownloadService service = retrofit.create(FilteredDownloadService.class);
        service.download(id).enqueue(new Callback<VideoInfo>() {
            @Override
            public void onResponse(Call<VideoInfo> call, Response<VideoInfo> response) {
                VideoInfo vis = response.body();
                userInfos = vis.getFeeds();
                callBack.callback();
            }

            @Override
            public void onFailure(Call<VideoInfo> call, Throwable t) {
                Log.d(TAG, "operation failed: ", t);
                callBack.callback();
            }
        });
    }

    public static File getOutPutFile(FileType type) {
        File dir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS);
        if (!dir.exists()) {
            dir.mkdirs();
        }
        String ts = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
        File file;
        if (type == FileType.PICTURE) {
            file = new File(dir.getAbsolutePath() + File.separator + "IMG_" + ts + ".jpg");
        } else {
            file = new File(dir.getAbsolutePath() + File.separator + "VID_" + ts + ".mp4");
        }

        return file;
    }

    public static String loginRequest(String name) {
        return "20200300";
    }

    public static void downloadVideoByPath(String path, Handler handler) {
        String[] pieces = path.split("/");
        String filename = pieces[pieces.length - 1];
        int idx = path.indexOf(filename);
        String baseUrl = path.substring(0, idx);

        Retrofit videoDownloadRetrofit = new Retrofit.Builder().baseUrl(baseUrl)
                .addConverterFactory(GsonConverterFactory.create()).build();
        VideoDoadLoadService service = videoDownloadRetrofit.create(VideoDoadLoadService.class);
        service.download(filename).enqueue(new Callback<ResponseBody>() {
            @Override
            public void onResponse(Call<ResponseBody> call, Response<ResponseBody> response) {
                if (!response.isSuccessful()) {
                    handler.sendEmptyMessage(DownLoadService.FAILED_DOWNLOAD_MSG);
                    return;
                }

                Log.d("tag", "got here");
                ResponseBody body = response.body();
                InputStream is = body.byteStream();
                Message message = null;
                File file = getOutPutFile(FileType.VIDEO);
                FileOutputStream fos = null;
                try {
                    fos = new FileOutputStream(file);
                } catch (FileNotFoundException e) {
                    e.printStackTrace();
                }
                byte[] buffer = new byte[1024];
                int len;
                try {
                    while ((len = is.read(buffer)) != -1) {
                        fos.write(buffer, 0, len);
                    }
                    fos.flush();
                    message = new Message();
                    message.what = DownLoadService.SUCCESS_DOWNLOAD_MSG;
                    message.obj = file.getAbsolutePath();
                    handler.sendMessage(message);
                } catch (Exception e) {
                    e.printStackTrace();
                    message = new Message();
                    message.what = DownLoadService.FAILED_DOWNLOAD_MSG;
                    handler.sendMessage(message);
                } finally {
                    if (is != null) {
                        try {
                            is.close();
                        } catch (IOException e) {
                            e.printStackTrace();
                        }
                    }
                    if (fos != null) {
                        try {
                            fos.close();
                        } catch (IOException e) {
                            e.printStackTrace();
                        }
                    }
                }

            }

            @Override
            public void onFailure(Call<ResponseBody> call, Throwable t) {

            }
        });
    }

    public static void upload(String name, String imagePath, String videoPath, String extra, Handler handler) {
        UploadService uploadService = retrofit.create(UploadService.class);
        List<MultipartBody.Part> parts = new ArrayList<>();
        parts.add(getMultiPartFromAsset("cover_image", imagePath));
        parts.add(getMultiPartFromAsset("video", videoPath));
        uploadService.upload(loginRequest(name), name, extra, parts).enqueue(new Callback<ResponseBody>() {
            @Override
            public void onResponse(Call<ResponseBody> call, Response<ResponseBody> response) {
                if (!response.isSuccessful()) {
                    handler.sendEmptyMessage(DownLoadService.FAILED_DOWNLOAD_MSG);
                    return;
                }
                handler.sendEmptyMessage(DownLoadService.SUCCESS_DOWNLOAD_MSG);
            }

            @Override
            public void onFailure(Call<ResponseBody> call, Throwable t) {
                Log.d(TAG, "operation failed: ", t);
            }
        });
    }

    private static MultipartBody.Part getMultiPartFromAsset(String key, String path) {
        RequestBody body = RequestBody.create(MediaType.parse("multipart/form-data"), fileNameToByte(path));
        return MultipartBody.Part.createFormData(key, path, body);
    }

    private static byte[] fileNameToByte(String path) {
        FileInputStream is = null;
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        byte[] buffer = new byte[1024];
        int n;
        byte[] ret = null;
        try {
            is = new FileInputStream(path);
            while (-1 != (n = is.read(buffer))) {
                bos.write(buffer, 0, n);
            }
            ret = bos.toByteArray();
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            try {
                bos.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
            if (is != null) {
                try {
                    is.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
        return ret;
    }
}
