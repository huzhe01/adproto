package com.example.toytiktok.utils;

import android.util.Log;

import com.example.toytiktok.bean.AdInfo;

import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

/**
 * 广告 API 工具类
 */
public class AdHttpUtil {
    private static final String TAG = "AdHttpUtil";

    // 广告推荐后端地址
    // Android 模拟器使用 10.0.2.2 访问本机
    // 真机调试时需要改为电脑的实际 IP 地址
    private static final String AD_BASE_URL = "http://10.0.2.2:8001/";

    private static Retrofit adRetrofit = new Retrofit.Builder()
            .baseUrl(AD_BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build();

    private static AdService adService = adRetrofit.create(AdService.class);

    // 广告数据回调接口
    public interface AdCallback {
        void onSuccess(List<AdInfo> ads);

        void onFailure(String error);
    }

    /**
     * 获取推荐广告
     * 
     * @param visitorId 访客 ID
     * @param size      返回数量
     * @param callback  回调
     */
    public static void getRecommendedAds(int visitorId, int size, AdCallback callback) {
        adService.getRecommendedAds(visitorId, size, "emb").enqueue(new Callback<List<AdInfo>>() {
            @Override
            public void onResponse(Call<List<AdInfo>> call, Response<List<AdInfo>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    List<AdInfo> ads = response.body();
                    Log.d(TAG, "Got " + ads.size() + " recommended ads");
                    callback.onSuccess(ads);
                } else {
                    callback.onFailure("Response not successful: " + response.code());
                }
            }

            @Override
            public void onFailure(Call<List<AdInfo>> call, Throwable t) {
                Log.e(TAG, "Failed to get recommended ads", t);
                callback.onFailure(t.getMessage());
            }
        });
    }

    /**
     * 获取热门广告
     * 
     * @param size     返回数量
     * @param callback 回调
     */
    public static void getTopAds(int size, AdCallback callback) {
        adService.getTopAds(size, "ctr").enqueue(new Callback<List<AdInfo>>() {
            @Override
            public void onResponse(Call<List<AdInfo>> call, Response<List<AdInfo>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    callback.onSuccess(response.body());
                } else {
                    callback.onFailure("Response not successful: " + response.code());
                }
            }

            @Override
            public void onFailure(Call<List<AdInfo>> call, Throwable t) {
                Log.e(TAG, "Failed to get top ads", t);
                callback.onFailure(t.getMessage());
            }
        });
    }

    /**
     * 记录广告点击
     * 
     * @param visitorId 访客 ID
     * @param adId      广告 ID
     * @param position  展示位置
     */
    public static void recordClick(int visitorId, int adId, int position) {
        AdService.ClickRequest request = new AdService.ClickRequest(visitorId, adId, 1, position);
        adService.recordClick(request).enqueue(new Callback<AdService.ClickResponse>() {
            @Override
            public void onResponse(Call<AdService.ClickResponse> call, Response<AdService.ClickResponse> response) {
                Log.d(TAG, "Click recorded for ad " + adId);
            }

            @Override
            public void onFailure(Call<AdService.ClickResponse> call, Throwable t) {
                Log.e(TAG, "Failed to record click", t);
            }
        });
    }
}
