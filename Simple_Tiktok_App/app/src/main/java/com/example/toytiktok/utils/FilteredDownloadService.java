package com.example.toytiktok.utils;

import com.example.toytiktok.bean.VideoInfo;

import java.util.List;

import retrofit2.Call;
import retrofit2.http.GET;
import retrofit2.http.Query;

public interface FilteredDownloadService {

    @GET("video/")
    Call<VideoInfo> download(@Query("student_id") String id);
}
