package com.example.toytiktok.bean;

import com.google.gson.annotations.SerializedName;

public class Info {
    @SerializedName("_id")
    private String id;

    @SerializedName("student_id")
    private String studentId;

    @SerializedName("user_name")
    private String userName;

    @SerializedName("video_url")
    private String videoUrl;

    @SerializedName("image_url")
    private String imageUrl;

    @SerializedName("image_w")
    private int width;

    @SerializedName("image_h")
    private int height;

    private String createdAt;
    private String updatedAt;

    @Override
    public String toString() {
        return "Info:\n" +
                "id = " + id + "\n" +
                "studentId = " + studentId + "\n" +
                "userName = " + userName + "\n" +
                "videoUrl = " + videoUrl + "\n" +
                "imageUrl = " + imageUrl + "\n" +
                "width = " + width + "\n" +
                "height = " + height + "\n" +
                "createdAt = " + createdAt + "\n" +
                "updatedAt = " + updatedAt + "\n";
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getStudentId() {
        return studentId;
    }

    public void setStudentId(String studentId) {
        this.studentId = studentId;
    }

    public String getUserName() {
        return userName;
    }

    public void setUserName(String userName) {
        this.userName = userName;
    }

    public String getVideoUrl() {
        return videoUrl;
    }

    public void setVideoUrl(String videoUrl) {
        this.videoUrl = videoUrl;
    }

    public String getImageUrl() {
        return imageUrl;
    }

    public void setImageUrl(String imageUrl) {
        this.imageUrl = imageUrl;
    }

    public int getWidth() {
        return width;
    }

    public void setWidth(int width) {
        this.width = width;
    }

    public int getHeight() {
        return height;
    }

    public void setHeight(int height) {
        this.height = height;
    }

    public String getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(String createdAt) {
        this.createdAt = createdAt;
    }

    public String getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(String updatedAt) {
        this.updatedAt = updatedAt;
    }
}
