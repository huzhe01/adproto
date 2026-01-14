package com.example.toytiktok.fakedata;

import com.example.toytiktok.R;
import com.example.toytiktok.bean.Music;

import java.util.Random;

public class DataCollections {
    private static String[] comments = new String[] {
            "当你没有借口的那一刻，就是你成功的开始。",
            "成功者学习别人的经验，一般人学习自己的经验。",
            "如果你想得到，你就会得到，你所需要付出的只是行动。",
            "别人的话只能作为一种参考，是不能左右自己的。",
            "别把生活当作游戏，谁游戏人生，生活就惩罚谁，这不是劝诫，而是--规则！",
            "把气愤的心境转化为柔和，把柔和的心境转化为爱，如此，这个世间将更加完美。",
            "活在忙与闲的两种境界里，才能俯仰自得，享受生活的乐趣，成就人生的意义。",
            "只要能执着远大的理想，且有不达目的绝不终止的意愿，便能产生惊人的力量。"
    };

    private static String[] musics = new String[] {
            "Cymophane-Tassel.mp3",
            "赵海洋-秋的思念.mp3",
            "Richard Clayderman-罗密欧与朱丽叶.mp3",
            "昼夜-雨的印记.mp3",
            "Richard Clayderman-秋日私语.mp3",
            "July-My Soul.mp3",
            "纯音乐-遇见.mp3",
            "文武贝-夜的钢琴曲5.mp3"
    };

    private static int[] musicPaths = new int[] {
            R.raw.music_one,
            R.raw.music_two,
            R.raw.music_three,
            R.raw.music_four,
            R.raw.music_five,
            R.raw.music_six,
            R.raw.music_seven,
            R.raw.music_eight
    };

    private static Random random = new Random();

    public static String generateComments() {
        int idx = random.nextInt(comments.length);
        return comments[idx];
    }

    public static Music generateMusic() {
        int idx = random.nextInt(musics.length);
        return new Music(musics[idx], musicPaths[idx]);
    }

    public static int generateNumber(int bound) {
        return random.nextInt(bound);
    }
}
