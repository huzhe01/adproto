package com.example.toytiktok.view;

import android.content.Context;
import android.content.res.TypedArray;
import android.util.AttributeSet;
import android.util.Log;
import android.widget.LinearLayout;

import androidx.annotation.Nullable;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.example.toytiktok.R;
import com.example.toytiktok.VideoDownLoadCallback;
import com.example.toytiktok.adapters.IconAdapter;

public class IconSetView extends LinearLayout {

    private Context mContext;
    private int num;

    public IconSetView(Context context) {
        super(context);
        mContext = context;
    }

    public IconSetView(Context context, @Nullable AttributeSet attrs) {
        super(context, attrs);
        mContext = context;

        TypedArray a = mContext.obtainStyledAttributes(attrs, R.styleable.CustomAttrTest);
        num = a.getInteger(R.styleable.CustomAttrTest_dataSet, 0);
        a.recycle();
    }

    public IconSetView(Context context, @Nullable AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);

        TypedArray a = mContext.obtainStyledAttributes(attrs, R.styleable.CustomAttrTest);
        num = a.getInteger(R.styleable.CustomAttrTest_dataSet, 0);
        a.recycle();

        mContext = context;
    }


    public void initView(IconAdapter.IconViewHolder.JumpCallBack callBack, VideoDownLoadCallback downLoadCallback, String videoUrl) {
        inflate(mContext, R.layout.icon_set_layout, this);
        RecyclerView recyclerView = findViewById(R.id.icon_set_recycle);
        LinearLayoutManager manager = new LinearLayoutManager(mContext);
        manager.setOrientation(LinearLayoutManager.HORIZONTAL);
        recyclerView.setLayoutManager(manager);
        recyclerView.setAdapter(new IconAdapter(num, callBack, downLoadCallback, videoUrl));
    }
}
