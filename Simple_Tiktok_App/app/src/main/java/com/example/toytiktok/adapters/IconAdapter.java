package com.example.toytiktok.adapters;

import android.Manifest;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.recyclerview.widget.RecyclerView;

import com.example.toytiktok.DownloadCallBack;
import com.example.toytiktok.MainActivity;
import com.example.toytiktok.R;
import com.example.toytiktok.VideoDownLoadCallback;
import com.example.toytiktok.fakedata.IconSet;
import com.example.toytiktok.fragments.PyqFragment;

public class IconAdapter extends RecyclerView.Adapter<IconAdapter.IconViewHolder> {
    private static final int STORAGE_PERMISSION_REQUEST_CODE = 3380;
    private int num;
    private IconViewHolder.JumpCallBack callBack;
    private VideoDownLoadCallback downLoadCallback;
    private String videoUrl;

    public IconAdapter(int num, IconViewHolder.JumpCallBack callBack, VideoDownLoadCallback downLoadCallback, String videoUrl) {
        this.num = num;
        this.callBack = callBack;
        this.downLoadCallback = downLoadCallback;
        this.videoUrl = videoUrl;
    }


    @NonNull
    @Override
    public IconViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.icon_name_layout, parent, false);
        return new IconViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull IconViewHolder holder, int position) {
        int imageId = IconSet.getImageId(num, position);
        String imageName = IconSet.getName(num, position);

        cancelListener(holder);
        holder.imageView.setImageResource(imageId);
        holder.textView.setText(imageName);

        if (imageName.equals("朋友圈")) {
            holder.imageView.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    callBack.callback();
                }
            });
        }
        if (imageName.equals("下载")) {
            holder.imageView.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    // permission check
                    Log.d("here", "xx");
//                    if (ContextCompat.checkSelfPermission((AppCompatActivity)downLoadCallback, Manifest.permission_group.STORAGE) != PackageManager.PERMISSION_GRANTED) {
//                        ActivityCompat.requestPermissions((AppCompatActivity)downLoadCallback, new String[] {Manifest.permission_group.STORAGE}, STORAGE_PERMISSION_REQUEST_CODE);
//                    } else {
                        downLoadCallback.downloadVideoCallback(videoUrl);
//                    }
                }
            });
        }
    }

    private void cancelListener(IconViewHolder holder) {
        holder.imageView.setOnClickListener(null);
    }


    @Override
    public int getItemCount() {
        return IconSet.getSize(num);
    }

    public static class IconViewHolder extends RecyclerView.ViewHolder {
        ImageView imageView;
        TextView textView;

        public IconViewHolder(@NonNull View itemView) {
            super(itemView);
            imageView = itemView.findViewById(R.id.icon_name_image);
            textView = itemView.findViewById(R.id.icon_name_text);
        }

        public interface JumpCallBack {
            public void callback();
        }
    }
}
