package com.example.toytiktok.view;

import android.content.Context;
import android.util.AttributeSet;
import android.util.Log;
import android.view.View;
import android.widget.ImageButton;
import android.widget.LinearLayout;
import android.widget.TextView;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;

import com.example.toytiktok.R;
import com.example.toytiktok.constant.ButtonType;
import com.example.toytiktok.fakedata.DataCollections;
import com.example.toytiktok.fragments.CommentFragment;
import com.example.toytiktok.fragments.ShareFragment;

import java.util.*;

public class IconWithContentView extends LinearLayout {
    private ImageButton imageButton;
    private TextView textView;
    private boolean isHeartClick;
    private int initNum;
    private List<Integer> imageIds = new ArrayList<>();
    private ButtonType type;
    private Context mContext;

    private String videoUrl;

    public IconWithContentView(Context context) {
        super(context);
        mContext = context;
        initView();
    }

    public IconWithContentView(Context context, @Nullable AttributeSet attrs) {
        super(context, attrs);
        mContext = context;
        initView();
    }

    public IconWithContentView(Context context, @Nullable AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        mContext = context;
        initView();
    }

    private void initView() {
        inflate(getContext(), R.layout.icon_with_content, this);

        imageButton = findViewById(R.id.layout_btn);
        textView = findViewById(R.id.layout_text);
    }

    public void setVideoUrl(String videoUrl) {
        this.videoUrl = videoUrl;
    }

    public void addImageId(int id) {
        imageIds.add(id);
    }

    public void resetComponents() {
        imageButton.setImageResource(imageIds.get(0));
        isHeartClick = false;
        initNum = DataCollections.generateNumber(500) + 1;
        textView.setText(String.valueOf(initNum));
        imageButton.setOnClickListener(null);
    }

    public void bindEventListener() {
        imageButton.setOnClickListener(new OnClickListener() {
            @Override
            public void onClick(View v) {
                switch (type) {
                    case HEART:
                        heartButtonFunctions();
                        break;
                    case COMMENT:
                        commonButtonFunctions();
                        break;
                    case SHARE:
                        shareButtonFunctions();
                        break;
                    default:
                        break;
                }

            }
        });
    }

    private void commonButtonFunctions() {
        CommentFragment fragment = new CommentFragment();
        fragment.show(((AppCompatActivity)mContext).getSupportFragmentManager(), "comment");
    }

    private void shareButtonFunctions() {
        ShareFragment fragment = ShareFragment.getInstance(videoUrl);
        fragment.show(((AppCompatActivity)mContext).getSupportFragmentManager(), "share");
    }

    private void heartButtonFunctions() {
        isHeartClick = !isHeartClick;
        if (isHeartClick) {
            imageButton.setImageResource(imageIds.get(1));
            textView.setText(String.valueOf(initNum+1));
        } else {
            imageButton.setImageResource(imageIds.get(0));
            textView.setText(String.valueOf(initNum));
        }
    }

    public void setType(ButtonType type) {
        this.type = type;
    }

}
