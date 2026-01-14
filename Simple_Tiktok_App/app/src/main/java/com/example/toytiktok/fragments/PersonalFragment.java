package com.example.toytiktok.fragments;

import android.content.Context;
import android.content.res.Resources;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Rect;
import android.graphics.drawable.ColorDrawable;
import android.graphics.drawable.Drawable;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.util.TypedValue;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.ColorInt;
import androidx.annotation.ColorRes;
import androidx.annotation.DimenRes;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.core.content.ContextCompat;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.GridLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import androidx.recyclerview.widget.StaggeredGridLayoutManager;

import com.airbnb.lottie.LottieAnimationView;
import com.bumptech.glide.Glide;
import com.bumptech.glide.request.RequestOptions;
import com.example.toytiktok.DownloadCallBack;
import com.example.toytiktok.R;
import com.example.toytiktok.adapters.MeAdapter;
import com.example.toytiktok.bean.Info;
import com.example.toytiktok.utils.HttpUtil;

import retrofit2.http.Url;

public class PersonalFragment extends Fragment implements DownloadCallBack {
    private static final int PARTIAL_SUCCECSS_FETCH_MSG = 3379;

    private LottieAnimationView lottieAnimationView;
    private ImageView imageView, avatarImageView;
    private RecyclerView recyclerView;
    private TextView userTextView;
    private String userName, id;

    private Handler handler = new Handler() {
        @Override
        public void handleMessage(@NonNull Message msg) {
            switch (msg.what) {
                case PARTIAL_SUCCECSS_FETCH_MSG:
                    init();
                    break;
                default:
                    break;
            }
        }
    };

    public static PersonalFragment getFragment(String userName, String id) {
        PersonalFragment fragment = new PersonalFragment();
        Bundle bundle = new Bundle();
        bundle.putString("userName", userName);
        bundle.putString("id", id);
        fragment.setArguments(bundle);
        return fragment;
    }

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.me_frag, container, false);

        lottieAnimationView = view.findViewById(R.id.personal_loading);
        imageView = view.findViewById(R.id.personal_cover);
        avatarImageView = view.findViewById(R.id.me_image);
        recyclerView = view.findViewById(R.id.me_recycle);
        userTextView = view.findViewById(R.id.me_name);

        Bundle args = getArguments();
        if (args != null) {
            userName = args.getString("userName", null);
            id = args.getString("id", null);
        }

        if (HttpUtil.userInfos == null) {
            HttpUtil.downloadById(PersonalFragment.this, id);

        } else {
            init();
        }

        return view;
    }

    private void init() {
        lottieAnimationView.setVisibility(View.GONE);
        imageView.setVisibility(View.GONE);

        userTextView.setText(userName);
        Glide.with(getContext()).load(getUrl(R.drawable.avatar)).apply(RequestOptions.circleCropTransform()).into(avatarImageView);
        recyclerView.setLayoutManager(new GridLayoutManager(getContext(), 3));
        GridItemDecoration divider = new GridItemDecoration.Builder(getContext())
                .setHorizontalSpan(R.dimen.common_vew_column_padding)
                .setVerticalSpan(R.dimen.common_vew_raw_padding)
                .setColorResource(R.color.unchosen)
                .setShowLastLine(true)
                .build();
        recyclerView.addItemDecoration(divider);
        recyclerView.setAdapter(new MeAdapter(getContext(), userName));
    }

    private Uri getUrl(int resId) {
        return Uri.parse("android.resource://" + getContext().getPackageName() + "/" + resId);
    }

    @Override
    public void onActivityCreated(@Nullable Bundle savedInstanceState) {
        super.onActivityCreated(savedInstanceState);
    }

    @Override
    public void callback() {
        // fake operation
        for (Info info : HttpUtil.userInfos) {
            info.setUserName(userName);
        }
        handler.sendEmptyMessage(PARTIAL_SUCCECSS_FETCH_MSG);
    }
}

class GridItemDecoration extends RecyclerView.ItemDecoration {

    private Drawable mDivider;
    private boolean mShowLastLine;
    private int mHorizonSpan;
    private int mVerticalSpan;

    private GridItemDecoration(int horizonSpan,int verticalSpan,int color,boolean showLastLine) {
        this.mHorizonSpan = horizonSpan;
        this.mShowLastLine = showLastLine;
        this.mVerticalSpan = verticalSpan;
        mDivider = new ColorDrawable(color);
    }

    @Override
    public void onDrawOver(Canvas c, RecyclerView parent, RecyclerView.State state) {
        drawHorizontal(c, parent);
        drawVertical(c, parent);
    }

    private void drawHorizontal(Canvas c, RecyclerView parent) {
        int childCount = parent.getChildCount();

        for (int i = 0; i < childCount; i++) {
            View child = parent.getChildAt(i);

            if (isLastRaw(parent,i,getSpanCount(parent),childCount) && !mShowLastLine){
                continue;
            }
            RecyclerView.LayoutParams params = (RecyclerView.LayoutParams) child.getLayoutParams();
            final int left = child.getLeft() - params.leftMargin;
            final int right = child.getRight() + params.rightMargin;
            final int top = child.getBottom() + params.bottomMargin;
            final int bottom = top + mHorizonSpan;

            mDivider.setBounds(left, top, right, bottom);
            mDivider.draw(c);
        }
    }

    private void drawVertical(Canvas c, RecyclerView parent) {
        int childCount = parent.getChildCount();
        for (int i = 0; i < childCount; i++) {
            final View child = parent.getChildAt(i);
            if((parent.getChildViewHolder(child).getAdapterPosition() + 1) % getSpanCount(parent) == 0){
                continue;
            }
            final RecyclerView.LayoutParams params = (RecyclerView.LayoutParams) child.getLayoutParams();
            final int top = child.getTop() - params.topMargin;
            final int bottom = child.getBottom() + params.bottomMargin + mHorizonSpan;
            final int left = child.getRight() + params.rightMargin;
            int right = left + mVerticalSpan;
            if (i==childCount-1) {
                right -= mVerticalSpan;
            }
            mDivider.setBounds(left, top, right, bottom);
            mDivider.draw(c);
        }
    }


    @Override
    public void getItemOffsets(Rect outRect, View view, RecyclerView parent, RecyclerView.State state) {
        int spanCount = getSpanCount(parent);
        int childCount = parent.getAdapter().getItemCount();
        int itemPosition = ((RecyclerView.LayoutParams) view.getLayoutParams()).getViewLayoutPosition();

        if (itemPosition < 0){
            return;
        }

        int column = itemPosition % spanCount;
        int bottom;

        int left = column * mVerticalSpan / spanCount;
        int right = mVerticalSpan - (column + 1) * mVerticalSpan / spanCount;

        if (isLastRaw(parent, itemPosition, spanCount, childCount)){
            if (mShowLastLine){
                bottom = mHorizonSpan;
            }else{
                bottom = 0;
            }
        }else{
            bottom = mHorizonSpan;
        }
        outRect.set(left, 0, right, bottom);
    }


    private int getSpanCount(RecyclerView parent) {
        int mSpanCount = -1;
        RecyclerView.LayoutManager layoutManager = parent.getLayoutManager();
        if (layoutManager instanceof GridLayoutManager) {
            mSpanCount = ((GridLayoutManager) layoutManager).getSpanCount();
        } else if (layoutManager instanceof StaggeredGridLayoutManager) {
            mSpanCount = ((StaggeredGridLayoutManager) layoutManager).getSpanCount();
        }
        return mSpanCount;
    }


    private boolean isLastRaw(RecyclerView parent, int pos, int spanCount, int childCount) {
        RecyclerView.LayoutManager layoutManager = parent.getLayoutManager();

        if (layoutManager instanceof GridLayoutManager) {
            return getResult(pos,spanCount,childCount);
        } else if (layoutManager instanceof StaggeredGridLayoutManager) {
            int orientation = ((StaggeredGridLayoutManager) layoutManager).getOrientation();
            if (orientation == StaggeredGridLayoutManager.VERTICAL) {
                return getResult(pos,spanCount,childCount);
            } else {
                if ((pos + 1) % spanCount == 0) {
                    return true;
                }
            }
        }
        return false;
    }

    private boolean getResult(int pos,int spanCount,int childCount){
        int remainCount = childCount % spanCount;
        if (remainCount == 0){
            if(pos >= childCount - spanCount){
                return true;
            }
        }else{
            if (pos >= childCount - childCount % spanCount){
                return true;
            }
        }
        return false;
    }


    public static class Builder {
        private Context mContext;
        private Resources mResources;
        private boolean mShowLastLine;
        private int mHorizonSpan;
        private int mVerticalSpan;
        private int mColor;

        public Builder(Context context) {
            mContext = context;
            mResources = context.getResources();
            mShowLastLine = true;
            mHorizonSpan = 0;
            mVerticalSpan = 0;
            mColor = Color.WHITE;
        }

        public Builder setColorResource(@ColorRes int resource) {
            setColor(ContextCompat.getColor(mContext, resource));
            return this;
        }


        public Builder setColor(@ColorInt int color) {
            mColor = color;
            return this;
        }


        public Builder setVerticalSpan(@DimenRes int vertical) {
            this.mVerticalSpan = mResources.getDimensionPixelSize(vertical);
            return this;
        }


        public Builder setVerticalSpan(float mVertical) {
            this.mVerticalSpan = (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_PX, mVertical, mResources.getDisplayMetrics());
            return this;
        }


        public Builder setHorizontalSpan(@DimenRes int horizontal) {
            this.mHorizonSpan = mResources.getDimensionPixelSize(horizontal);
            return this;
        }


        public Builder setHorizontalSpan(float horizontal) {
            this.mHorizonSpan = (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_PX, horizontal, mResources.getDisplayMetrics());
            return this;
        }

        public GridItemDecoration.Builder setShowLastLine(boolean show){
            mShowLastLine = show;
            return this;
        }

        public GridItemDecoration build() {
            return new GridItemDecoration(mHorizonSpan, mVerticalSpan, mColor,mShowLastLine);
        }
    }
}
