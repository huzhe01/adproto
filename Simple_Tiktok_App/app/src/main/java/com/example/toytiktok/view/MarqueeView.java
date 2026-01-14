package com.example.toytiktok.view;

import android.content.Context;
import android.util.AttributeSet;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.widget.AppCompatTextView;

public class MarqueeView extends AppCompatTextView {
    public MarqueeView(@NonNull Context context) {
        super(context);
    }

    public MarqueeView(@NonNull Context context, @Nullable AttributeSet attrs) {
        super(context, attrs);
    }

    public MarqueeView(@NonNull Context context, @Nullable AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
    }

    @Override
    public boolean isFocused() {
        return true;
    }
}
