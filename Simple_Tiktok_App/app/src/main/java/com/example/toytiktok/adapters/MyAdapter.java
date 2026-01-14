package com.example.toytiktok.adapters;

import android.animation.ObjectAnimator;
import android.animation.ValueAnimator;
import android.media.MediaPlayer;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.view.animation.LinearInterpolator;
import android.widget.ImageView;
import android.widget.SeekBar;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.VideoView;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.RecyclerView;

import com.airbnb.lottie.LottieAnimationView;
import com.example.toytiktok.R;
import com.example.toytiktok.bean.Info;
import com.example.toytiktok.bean.Music;
import com.example.toytiktok.constant.ButtonType;
import com.example.toytiktok.fakedata.DataCollections;
import com.example.toytiktok.utils.HttpUtil;
import com.example.toytiktok.view.IconWithContentView;
import com.example.toytiktok.view.MarqueeView;

import java.util.List;

public class MyAdapter extends RecyclerView.Adapter<MyAdapter.MyViewHolder> {
    private static final int CACHESIZE = 6;
    private static final int SEEKBAR_MSG = 1001;
    private static final int SINGLE_CLICK_MSG = 1002;
    private static final int DOUBLE_CLICK_MSG = 1003;

    @NonNull
    @Override
    public MyViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.item, parent, false);
        return new MyViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull MyViewHolder holder, int position) {
        holder.functions(holder, position, HttpUtil.ResType.ALL);
    }

    @Override
    public int getItemCount() {
        return HttpUtil.infos == null ? 0 : HttpUtil.infos.size();
    }

    public static class MyViewHolder extends RecyclerView.ViewHolder {
        VideoView videoView;
        SeekBar seekBar;
        LottieAnimationView animeView;

        MarqueeView marqueeView;
        TextView textContent;
        TextView textAuthor;

        IconWithContentView heart, message, share;

        ImageView coverImage;
        LottieAnimationView loadingAnime;

        ImageView mPlayer;

        Handler handler = new Handler() {
            @Override
            public void handleMessage(@NonNull Message msg) {
                switch (msg.what) {
                    case SEEKBAR_MSG:
                        updateSeekBar();
                        break;
                    case SINGLE_CLICK_MSG:
                        handleSingleClickEvent(MyViewHolder.this);
                        break;
                    case DOUBLE_CLICK_MSG:
                        handleDoubleClickEvent(MyViewHolder.this);
                        break;
                    default:
                        break;
                }
            }
        };

        boolean isPlaying;

        private long mLastTime;
        private long mCurTime;

        private LottieAnimationView popView;

        public MyViewHolder(@NonNull View itemView) {
            super(itemView);
            videoView = itemView.findViewById(R.id.item_video);
            seekBar = itemView.findViewById(R.id.item_seekbar);
            animeView = itemView.findViewById(R.id.item_animation);

            marqueeView = itemView.findViewById(R.id.item_marquee);
            textContent = itemView.findViewById(R.id.item_content);
            textAuthor = itemView.findViewById(R.id.item_author);

            heart = itemView.findViewById(R.id.btn_heart);
            message = itemView.findViewById(R.id.btn_message);
            share = itemView.findViewById(R.id.btn_share);
            heart.addImageId(R.drawable.heart_white);
            heart.addImageId(R.drawable.heart_red);
            heart.setType(ButtonType.HEART);
            message.addImageId(R.drawable.message);
            message.setType(ButtonType.COMMENT);
            share.addImageId(R.drawable.share);
            share.setType(ButtonType.SHARE);

            coverImage = itemView.findViewById(R.id.item_cover);
            loadingAnime = itemView.findViewById(R.id.load_effect);

            mPlayer = itemView.findViewById(R.id.item_player);

            popView = itemView.findViewById(R.id.pop_heart);
        }

        public void msgCancel() {
            handler.removeMessages(SEEKBAR_MSG);
        }

        public void updateSeekBar() {
            seekBar.setProgress(videoView.getCurrentPosition());
            handler.sendEmptyMessageDelayed(SEEKBAR_MSG, 50);
        }

        public void functions(MyViewHolder holder, int position, HttpUtil.ResType type) {
            List<Info> infos;
            if (type == HttpUtil.ResType.ALL) {
                infos = HttpUtil.infos;
            } else {
                infos = HttpUtil.userInfos;
            }
            holder.heart.setVideoUrl(infos.get(position).getVideoUrl());
            holder.message.setVideoUrl(infos.get(position).getVideoUrl());
            holder.share.setVideoUrl(infos.get(position).getVideoUrl());

            holder.videoView.setOnClickListener(null);
            holder.msgCancel();
            holder.seekBar.setProgress(0);
            holder.seekBar.setEnabled(false);
            holder.isPlaying = false;
            holder.animeView.setVisibility(View.INVISIBLE);

            holder.popView.setVisibility(View.GONE);

            holder.heart.resetComponents();
            holder.message.resetComponents();
            holder.share.resetComponents();

            holder.videoView.setVideoURI(Uri.parse(infos.get(position).getVideoUrl()));
            holder.videoView.setOnPreparedListener(new MediaPlayer.OnPreparedListener() {
                @Override
                public void onPrepared(MediaPlayer mp) {
                    holder.coverImage.setVisibility(View.GONE);
                    holder.loadingAnime.setVisibility(View.GONE);

                    ObjectAnimator animator = ObjectAnimator.ofFloat(mPlayer,
                            "rotation", 0, -360);
                    animator.setRepeatCount(ValueAnimator.INFINITE);
                    animator.setInterpolator(new LinearInterpolator());
                    animator.setDuration(8000);
                    animator.setRepeatMode(ValueAnimator.RESTART);
                    animator.start();

                    mp.start();
                    mp.setLooping(true);

                    holder.heart.bindEventListener();
                    holder.message.bindEventListener();
                    holder.share.bindEventListener();

                    holder.textAuthor.setText("@" + infos.get(position).getUserName());
                    holder.textContent.setText(DataCollections.generateComments());
                    Music music = DataCollections.generateMusic();
                    holder.marqueeView.setText(music.getName());

                    holder.seekBar.setMax(holder.videoView.getDuration());
                    holder.seekBar.setEnabled(true);
                    holder.seekBar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
                        @Override
                        public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                            if (fromUser) {
                                mp.seekTo(progress);
                            }
                        }

                        @Override
                        public void onStartTrackingTouch(SeekBar seekBar) {

                        }

                        @Override
                        public void onStopTrackingTouch(SeekBar seekBar) {

                        }
                    });

                    holder.updateSeekBar();
                }
            });

            holder.videoView.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {

                    mLastTime = mCurTime;
                    mCurTime = System.currentTimeMillis();
                    if (mCurTime - mLastTime < 300) {
                        mCurTime = 0;
                        mLastTime = 0;
                        handler.removeMessages(SINGLE_CLICK_MSG);
                        handler.sendEmptyMessage(DOUBLE_CLICK_MSG);
                    } else {
                        handler.sendEmptyMessageDelayed(SINGLE_CLICK_MSG, 310);
                    }
                }
            });

        }

        private void handleSingleClickEvent(MyViewHolder holder) {
            if (holder.isPlaying) {
                holder.videoView.pause();
                holder.isPlaying = false;
                holder.msgCancel();
                holder.animeView.setVisibility(View.VISIBLE);
                holder.animeView.playAnimation();
            } else {
                holder.videoView.start();
                holder.isPlaying = true;
                holder.updateSeekBar();
                holder.animeView.pauseAnimation();
                holder.animeView.setVisibility(View.INVISIBLE);
            }
        }

        private void handleDoubleClickEvent(MyViewHolder holder) {
            holder.popView.setVisibility(View.VISIBLE);
            holder.popView.playAnimation();
        }
    }

}
