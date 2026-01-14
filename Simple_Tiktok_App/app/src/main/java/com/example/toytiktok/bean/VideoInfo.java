package com.example.toytiktok.bean;

import java.util.List;

public class VideoInfo {
    private List<Info> feeds;
    private boolean success;

    public List<Info> getFeeds() {
        return feeds;
    }

    public void setFeeds(List<Info> feeds) {
        this.feeds = feeds;
    }

    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }

    @Override
    public String toString() {
        return success ? "VideoInfo[details]:\n" + feeds.toString() : "request failed";
    }
}
