package com.example.toytiktok.utils;


import com.example.toytiktok.bean.VideoInfo;

import retrofit2.Call;
import retrofit2.http.GET;

public interface DownloadService {

    @GET("video/")
    Call<VideoInfo> download();
}
