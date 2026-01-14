package com.example.toytiktok.adapters;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.bumptech.glide.Glide;
import com.bumptech.glide.load.resource.bitmap.RoundedCorners;
import com.bumptech.glide.request.RequestOptions;
import com.example.toytiktok.R;
import com.example.toytiktok.bean.AdInfo;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * 广告列表适配器
 */
public class AdAdapter extends RecyclerView.Adapter<AdAdapter.AdViewHolder> {

    private List<AdInfo> adList = new ArrayList<>();
    private OnAdClickListener clickListener;

    public interface OnAdClickListener {
        void onAdClick(AdInfo ad, int position);
    }

    public void setOnAdClickListener(OnAdClickListener listener) {
        this.clickListener = listener;
    }

    public void setAdList(List<AdInfo> ads) {
        this.adList = ads;
        notifyDataSetChanged();
    }

    @NonNull
    @Override
    public AdViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.ad_item, parent, false);
        return new AdViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull AdViewHolder holder, int position) {
        AdInfo ad = adList.get(position);
        holder.bind(ad, position);
    }

    @Override
    public int getItemCount() {
        return adList.size();
    }

    class AdViewHolder extends RecyclerView.ViewHolder {
        ImageView adImage;
        TextView adTitle;
        TextView adCategories;
        TextView adCtr;
        TextView adClicks;
        TextView adYear;

        AdViewHolder(@NonNull View itemView) {
            super(itemView);
            adImage = itemView.findViewById(R.id.ad_image);
            adTitle = itemView.findViewById(R.id.ad_title);
            adCategories = itemView.findViewById(R.id.ad_categories);
            adCtr = itemView.findViewById(R.id.ad_ctr);
            adClicks = itemView.findViewById(R.id.ad_clicks);
            adYear = itemView.findViewById(R.id.ad_year);
        }

        void bind(AdInfo ad, int position) {
            // 标题
            adTitle.setText(ad.getTitle());

            // 分类
            adCategories.setText(ad.getCategoriesString());

            // CTR (转换为百分比)
            adCtr.setText(String.format(Locale.US, "CTR: %.1f%%", ad.getCtr() * 100));

            // 点击数
            adClicks.setText(String.format(Locale.US, "%d 点击", ad.getClickCount()));

            // 年份
            adYear.setText(String.valueOf(ad.getReleaseYear()));

            // 加载占位图
            Glide.with(itemView.getContext())
                    .load(ad.getPlaceholderImageUrl())
                    .apply(new RequestOptions()
                            .placeholder(R.color.grey)
                            .error(R.color.grey)
                            .transform(new RoundedCorners(24)))
                    .into(adImage);

            // 点击事件
            itemView.setOnClickListener(v -> {
                if (clickListener != null) {
                    clickListener.onAdClick(ad, position);
                }
            });
        }
    }
}
