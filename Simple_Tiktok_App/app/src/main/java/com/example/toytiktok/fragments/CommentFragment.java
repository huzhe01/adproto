package com.example.toytiktok.fragments;

import android.app.Dialog;
import android.graphics.Color;
import android.os.Bundle;
import android.view.Display;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.view.ViewTreeObserver;
import android.widget.ArrayAdapter;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.ListView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.coordinatorlayout.widget.CoordinatorLayout;

import com.example.toytiktok.R;
import com.google.android.material.bottomsheet.BottomSheetBehavior;
import com.google.android.material.bottomsheet.BottomSheetDialog;
import com.google.android.material.bottomsheet.BottomSheetDialogFragment;

public class CommentFragment extends BottomSheetDialogFragment {
    private static String[] comments = new String[] {
            "这家技术太高，我们换一家喷.",
            "你的笔很听话，我的笔有自己的想法。",
            "欢迎收看一看就会，一做就废系列。",
            "明人不说暗话，我喜欢那个小姐姐。",
            "本以为是青铜，没想到是王者",
            "你弄这么快，是怕我学会么?",
            "这是我在抖音想买的第多少件东西",
            "听最嗨的歌，喝最烈的酒，打最好的石膏。",
            "把酸奶瓶掏空给儿子喝，装的药，喝了一口往后退了。",
            "超快速的四驱车，开动后都看不清身影",
            "你长得真好看要交税吗?",
            "我涨粉五个，我骄傲了吗?",
            "我承认你长得比我美，但我还是最爱我自己",
            "以前忙着可爱忙着长大，长大后，忙着相亲，忙着护发",
            "你永远不知道那些看起来穷的人有多有钱但我不一样我是表里如一的.",
            "你老是这么抠门，门都被你抠坏了好几扇。",
            "朕的江山养你一个祸水够不够。",
            "那天我把乞丐装满钱的碗拿走后，竟然治好了他多年以来的残疾",
            "看到了有人摔倒了我毫不犹豫的点赞了!",
            "这么好看的牙齿不卡两片韭菜叶可惜了!",
            "初听不知曲中意,再听已是曲中人。初看不知剧中意,再看已是剧中人"
    };

    private BottomSheetBehavior<View> mBottomSheetBehavior;
    private BottomSheetBehavior.BottomSheetCallback mBottomSheetBehaviorCallback
            = new BottomSheetBehavior.BottomSheetCallback() {

        @Override
        public void onStateChanged(@NonNull View bottomSheet, int newState) {
            if (newState == BottomSheetBehavior.STATE_DRAGGING) {
                mBottomSheetBehavior.setState(BottomSheetBehavior.STATE_COLLAPSED);
            }
        }
        @Override
        public void onSlide(@NonNull View bottomSheet, float slideOffset) {
        }
    };

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.comment_frag, container, false);
        ListView lv = view.findViewById(R.id.list_view_common);
        ArrayAdapter<String> adapter = new ArrayAdapter<>(getContext(), android.R.layout.simple_list_item_1, comments);
        lv.setAdapter(adapter);

        TextView textView = view.findViewById(R.id.comment_text);
        String text = comments.length + "条评论";
        textView.setText(text);

        ImageView imageView = view.findViewById(R.id.comment_cancel);
        imageView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                CommentFragment.this.dismiss();
            }
        });

        return view;
    }


    @Override
    public void onStart() {
        super.onStart();
        Dialog dialog = getDialog();

        if (dialog != null) {
            View bottomSheet = dialog.findViewById(R.id.design_bottom_sheet);
            bottomSheet.getLayoutParams().height = ViewGroup.LayoutParams.MATCH_PARENT;
        }
        final View view = getView();
        view.post(new Runnable() {
            @Override
            public void run() {
                View parent = (View) view.getParent();
                CoordinatorLayout.LayoutParams params = (CoordinatorLayout.LayoutParams) (parent).getLayoutParams();
                CoordinatorLayout.Behavior behavior = params.getBehavior();
                mBottomSheetBehavior = (BottomSheetBehavior) behavior;
                mBottomSheetBehavior.setBottomSheetCallback(mBottomSheetBehaviorCallback);
                Display display = getActivity().getWindowManager().getDefaultDisplay();

                int height = display.getHeight() * 2 / 3;
                mBottomSheetBehavior.setPeekHeight(height);
            }
        });
    }
}
