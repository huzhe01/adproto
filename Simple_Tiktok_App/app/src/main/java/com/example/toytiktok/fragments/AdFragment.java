package com.example.toytiktok.fragments;

import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.example.toytiktok.R;
import com.example.toytiktok.adapters.AdAdapter;
import com.example.toytiktok.bean.AdInfo;
import com.example.toytiktok.utils.AdHttpUtil;

import java.util.List;

/**
 * 广告推荐 Fragment
 * 展示从后端获取的推荐广告列表
 */
public class AdFragment extends Fragment implements AdAdapter.OnAdClickListener {
    private static final String TAG = "AdFragment";
    private static final int DEFAULT_VISITOR_ID = 1;
    private static final int DEFAULT_AD_SIZE = 10;

    private RecyclerView recyclerView;
    private ProgressBar loadingView;
    private TextView errorView;
    private TextView refreshBtn;

    private AdAdapter adapter;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container,
            @Nullable Bundle savedInstanceState) {
        return inflater.inflate(R.layout.ad_frag, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        // 初始化视图
        recyclerView = view.findViewById(R.id.ad_recycler);
        loadingView = view.findViewById(R.id.ad_loading);
        errorView = view.findViewById(R.id.ad_error);
        refreshBtn = view.findViewById(R.id.ad_refresh);

        // 设置 RecyclerView
        adapter = new AdAdapter();
        adapter.setOnAdClickListener(this);
        recyclerView.setLayoutManager(new LinearLayoutManager(getContext()));
        recyclerView.setAdapter(adapter);

        // 刷新按钮
        refreshBtn.setOnClickListener(v -> loadAds());

        // 加载广告
        loadAds();
    }

    /**
     * 加载广告数据
     */
    private void loadAds() {
        showLoading();

        AdHttpUtil.getRecommendedAds(DEFAULT_VISITOR_ID, DEFAULT_AD_SIZE, new AdHttpUtil.AdCallback() {
            @Override
            public void onSuccess(List<AdInfo> ads) {
                if (getActivity() == null)
                    return;

                getActivity().runOnUiThread(() -> {
                    hideLoading();
                    if (ads.isEmpty()) {
                        showError("暂无推荐广告");
                    } else {
                        adapter.setAdList(ads);
                        Log.d(TAG, "Loaded " + ads.size() + " ads");
                    }
                });
            }

            @Override
            public void onFailure(String error) {
                if (getActivity() == null)
                    return;

                getActivity().runOnUiThread(() -> {
                    hideLoading();
                    showError("加载失败: " + error + "\n\n请确保后端服务已启动\nhttp://localhost:8001");
                    Log.e(TAG, "Failed to load ads: " + error);
                });
            }
        });
    }

    private void showLoading() {
        loadingView.setVisibility(View.VISIBLE);
        errorView.setVisibility(View.GONE);
        recyclerView.setVisibility(View.GONE);
    }

    private void hideLoading() {
        loadingView.setVisibility(View.GONE);
        recyclerView.setVisibility(View.VISIBLE);
    }

    private void showError(String message) {
        errorView.setText(message);
        errorView.setVisibility(View.VISIBLE);
        recyclerView.setVisibility(View.GONE);
    }

    @Override
    public void onAdClick(AdInfo ad, int position) {
        // 记录点击事件
        AdHttpUtil.recordClick(DEFAULT_VISITOR_ID, ad.getAdId(), position);

        // 显示 Toast
        Toast.makeText(getContext(),
                "点击广告: " + ad.getTitle() + "\nCTR: " + String.format("%.1f%%", ad.getCtr() * 100),
                Toast.LENGTH_SHORT).show();
    }
}
