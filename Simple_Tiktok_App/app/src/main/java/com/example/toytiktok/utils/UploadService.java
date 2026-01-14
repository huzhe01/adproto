package com.example.toytiktok.utils;

import java.util.List;

import okhttp3.MultipartBody;
import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.http.Multipart;
import retrofit2.http.POST;
import retrofit2.http.Part;
import retrofit2.http.Query;

public interface UploadService {

    @Multipart
    @POST("video/")
    Call<ResponseBody> upload(
            @Query("student_id") String id,
            @Query("user_name") String name,
            @Query("extra_value") String extra,
            @Part List<MultipartBody.Part> parts);
}
