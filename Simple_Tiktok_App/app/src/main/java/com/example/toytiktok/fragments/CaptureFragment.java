package com.example.toytiktok.fragments;

import android.hardware.Camera;
import android.os.Bundle;
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
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;

public class CaptureFragment extends Fragment {

    private Button preview, capture;
    private SurfaceView surfaceView;
    private SurfaceHolder holder;
    private Camera mCamera;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.activity_cap, container, false);

        preview = view.findViewById(R.id.cap_preview);
        capture = view.findViewById(R.id.cap_capture);
        surfaceView = view.findViewById(R.id.cap_surface);
        holder = surfaceView.getHolder();

        openCamera();

        preview.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                try {
                    mCamera.setPreviewDisplay(holder);
                    mCamera.startPreview();
                } catch (IOException e) {
                    e.printStackTrace();
                }

            }
        });

        capture.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                mCamera.takePicture(null, null, new Camera.PictureCallback() {
                    @Override
                    public void onPictureTaken(byte[] data, Camera camera) {
                        File file = HttpUtil.getOutPutFile(FileType.VIDEO);
                        FileOutputStream fos = null;
                        try {
                            fos = new FileOutputStream(file);
                        } catch (FileNotFoundException e) {
                            e.printStackTrace();
                        }
                        try {
                            fos.write(data);
                            fos.close();
                            Toast.makeText(getActivity(), "图片已保存至" + file.getAbsolutePath(), Toast.LENGTH_SHORT).show();
                        } catch (IOException e) {
                            e.printStackTrace();
                        }
                    }
                });
            }
        });
        return view;
    }

    @Override
    public void onStop() {
        super.onStop();
        mCamera.release();
    }

    private void openCamera() {
        try {
            mCamera = Camera.open(Camera.CameraInfo.CAMERA_FACING_BACK);
        } catch (Exception e) {

        }
    }
}
