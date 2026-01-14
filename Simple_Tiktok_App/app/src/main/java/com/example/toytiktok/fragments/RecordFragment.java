package com.example.toytiktok.fragments;

import android.hardware.Camera;
import android.media.CamcorderProfile;
import android.media.MediaRecorder;
import android.os.Bundle;
import android.os.Environment;
import android.view.LayoutInflater;
import android.view.SurfaceHolder;
import android.view.SurfaceView;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import com.example.toytiktok.R;
import com.example.toytiktok.constant.FileType;
import com.example.toytiktok.utils.HttpUtil;

import java.io.File;
import java.io.IOException;

public class RecordFragment extends Fragment {

    private Button record, stop;
    private SurfaceView surfaceView;
    private SurfaceHolder holder;
    private Camera mCamera;
    private MediaRecorder recorder;
    private boolean isRecord;
    private File file;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.activity_rec, container, false);

        record = view.findViewById(R.id.rec_video);
        stop = view.findViewById(R.id.rec_stop);
        surfaceView = view.findViewById(R.id.rec_surface);
        holder = surfaceView.getHolder();

        mCamera = Camera.open(Camera.CameraInfo.CAMERA_FACING_BACK);


        record.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (isRecord) return;
                recorder = new MediaRecorder();
                mCamera.unlock();
                recorder.setCamera(mCamera);
                recorder.setAudioSource(MediaRecorder.AudioSource.CAMCORDER);
                recorder.setVideoSource(MediaRecorder.VideoSource.CAMERA);
                recorder.setProfile(CamcorderProfile.get(CamcorderProfile.QUALITY_HIGH));
                file = HttpUtil.getOutPutFile(FileType.VIDEO);
                recorder.setOutputFile(file.toString());
                recorder.setPreviewDisplay(holder.getSurface());

                try {
                    recorder.prepare();
                    recorder.start();
                    isRecord = true;
                } catch (IOException e) {
                    e.printStackTrace();
                    releaseRecorder();
                }
            }
        });

        stop.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (!isRecord) return;
                recorder.stop();
                recorder.release();
                isRecord = false;
                Toast.makeText(getActivity(), "视频已保存至" + file.getAbsolutePath(), Toast.LENGTH_SHORT).show();
            }
        });

        return view;
    }

    private void releaseRecorder() {
        recorder.stop();
        recorder.reset();
        recorder.release();
        mCamera.lock();
    }

    @Override
    public void onStop() {
        super.onStop();
        releaseRecorder();
    }

}


