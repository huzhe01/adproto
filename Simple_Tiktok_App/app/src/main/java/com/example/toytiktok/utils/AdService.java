package com.example.toytiktok.utils;

import com.example.toytiktok.bean.AdInfo;

import java.util.List;

import retrofit2.Call;
import retrofit2.http.GET;
import retrofit2.http.POST;
import retrofit2.http.Path;
import retrofit2.http.Query;
import retrofit2.http.Body;

/**
 * 广告推荐 API 服务接口
 */
public interface AdService {

    /**
     * 获取个性化推荐广告
     * @param visitorId 访客 ID
     * @param size 返回数量
     * @param model 排序模型 (emb, neuralcf, default)
     */
    @GET("api/rec/ads")
    Call<List<AdInfo>> getRecommendedAds(
            @Query("visitor_id") int visitorId,
            @Query("size") int size,
            @Query("model") String model
    );

    /**
     * 获取热门广告
     * @param size 返回数量
     * @param sortBy 排序方式 (ctr, clicks, year)
     */
    @GET("api/rec/top")
    Call<List<AdInfo>> getTopAds(
            @Query("size") int size,
            @Query("sort_by") String sortBy
    );

    /**
     * 获取相似广告
     * @param adId 广告 ID
     * @param size 返回数量
     */
    @GET("api/rec/similar")
    Call<List<AdInfo>> getSimilarAds(
            @Query("ad_id") int adId,
            @Query("size") int size
    );

    /**
     * 获取广告详情
     * @param adId 广告 ID
     */
    @GET("api/rec/ad/{ad_id}")
    Call<AdInfo> getAdDetail(@Path("ad_id") int adId);

    /**
     * 记录点击事件
     */
    @POST("api/rec/click")
    Call<ClickResponse> recordClick(@Body ClickRequest request);

    /**
     * 点击请求
     */
    class ClickRequest {
        int visitor_id;
        int ad_id;
        int clicked;
        int position;

        public ClickRequest(int visitorId, int adId, int clicked, int position) {
            this.visitor_id = visitorId;
            this.ad_id = adId;
            this.clicked = clicked;
            this.position = position;
        }
    }

    /**
     * 点击响应
     */
    class ClickResponse {
        boolean success;
        String message;
    }
}
