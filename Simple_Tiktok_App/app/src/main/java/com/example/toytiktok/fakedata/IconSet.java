package com.example.toytiktok.fakedata;

import com.example.toytiktok.R;

public class IconSet {
    private static int[] set_one_ids = new int[] {R.drawable.sixin, R.drawable.zhuanfa, R.drawable.pyq, R.drawable.weixin, R.drawable.qq, R.drawable.weibo};
    private static String[] set_one_names = new String[] {"私信", "转发", "朋友圈", "微信", "QQ", "微博"};

    private static int[] set_two_ids = new int[] {R.drawable.xiazai, R.drawable.jubao, R.drawable.shoucang, R.drawable.hepai, R.drawable.qiangjing};
    private static String[] set_two_names = new String[] {"下载", "举报", "收藏", "合拍", "抢镜"};

    public static int getImageId(int num, int pos) {
        return num == 0 ? set_one_ids[pos] : set_two_ids[pos];
    }

    public static String getName(int num, int pos) {
        return num == 0 ? set_one_names[pos] : set_two_names[pos];
    }

    public static int getSize(int num) {
        return num == 0 ? set_one_ids.length : set_two_ids.length;
    }
}
