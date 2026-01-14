package com.example.toytiktok.utils;

import com.example.toytiktok.bean.VideoInfo;

import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.http.GET;
import retrofit2.http.Path;

public interface VideoDoadLoadService {

    @GET("{filename}")
    Call<ResponseBody> download(@Path("filename") String filename);
}
