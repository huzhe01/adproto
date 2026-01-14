package com.example.toytiktok.adapters;

import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.bumptech.glide.Glide;
import com.example.toytiktok.ItemActivity;
import com.example.toytiktok.R;
import com.example.toytiktok.fakedata.DataCollections;
import com.example.toytiktok.utils.HttpUtil;

public class MeAdapter extends RecyclerView.Adapter<MeAdapter.MeViewHolder> {
    private Context mContext;
    private String userName;

    public MeAdapter(Context context, String name) {
        mContext = context;
        userName = name;
    }

    @NonNull
    @Override
    public MeViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.me_layout, parent, false);


        return new MeViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull MeViewHolder holder, int position) {
        Glide.with(mContext).load(Uri.parse(HttpUtil.userInfos.get(position).getImageUrl())).into(holder.imageView);
        holder.imageUrl = HttpUtil.infos.get(position).getImageUrl();
        holder.videoUrl = HttpUtil.infos.get(position).getVideoUrl();
        final int num = DataCollections.generateNumber(500) + 1;
        String text = num + " " + userName;
        holder.textView.setText(text);

        holder.imageView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(mContext, ItemActivity.class);
                intent.putExtra("position", position);
                intent.putExtra("count", num);
                mContext.startActivity(intent);
            }
        });
    }

    @Override
    public int getItemCount() {
        return HttpUtil.userInfos.size();
    }

    static class MeViewHolder extends RecyclerView.ViewHolder {
        ImageView imageView;
        TextView textView;
        String imageUrl;
        String videoUrl;


        public MeViewHolder(@NonNull View itemView) {
            super(itemView);
            imageView = itemView.findViewById(R.id.me_image);
            textView = itemView.findViewById(R.id.me_text);
        }
    }
}
