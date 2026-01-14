package com.example.toytiktok.bean;

import com.google.gson.annotations.SerializedName;
import java.util.List;

/**
 * 广告信息 Bean - 对应后端 AdResponse
 */
public class AdInfo {
    @SerializedName("ad_id")
    private int adId;

    private String title;

    @SerializedName("release_year")
    private int releaseYear;

    private List<String> categories;

    @SerializedName("click_count")
    private int clickCount;

    @SerializedName("impression_count")
    private int impressionCount;

    private float ctr;

    // Getters and Setters
    public int getAdId() {
        return adId;
    }

    public void setAdId(int adId) {
        this.adId = adId;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public int getReleaseYear() {
        return releaseYear;
    }

    public void setReleaseYear(int releaseYear) {
        this.releaseYear = releaseYear;
    }

    public List<String> getCategories() {
        return categories;
    }

    public void setCategories(List<String> categories) {
        this.categories = categories;
    }

    public int getClickCount() {
        return clickCount;
    }

    public void setClickCount(int clickCount) {
        this.clickCount = clickCount;
    }

    public int getImpressionCount() {
        return impressionCount;
    }

    public void setImpressionCount(int impressionCount) {
        this.impressionCount = impressionCount;
    }

    public float getCtr() {
        return ctr;
    }

    public void setCtr(float ctr) {
        this.ctr = ctr;
    }

    /**
     * 生成占位图 URL (基于 ad_id)
     */
    public String getPlaceholderImageUrl() {
        // 使用 picsum.photos 生成占位图
        return "https://picsum.photos/seed/" + adId + "/400/300";
    }

    /**
     * 获取分类字符串
     */
    public String getCategoriesString() {
        if (categories == null || categories.isEmpty()) {
            return "";
        }
        return String.join(" | ", categories);
    }

    @Override
    public String toString() {
        return "AdInfo{" +
                "adId=" + adId +
                ", title='" + title + '\'' +
                ", ctr=" + ctr +
                '}';
    }
}
