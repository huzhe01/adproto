package com.example.toytiktok.fragments;

import android.content.Intent;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import com.example.toytiktok.MultiMediaActivity;
import com.example.toytiktok.R;
import com.example.toytiktok.UploadActivity;

public class MainFragment extends Fragment {

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.activity_util, container, false);

        Button capture = view.findViewById(R.id.util_cap);
        Button record = view.findViewById(R.id.util_record);
        Button upload = view.findViewById(R.id.util_upload);
        capture.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                ((MultiMediaActivity)getActivity()).replaceFragment(new CaptureFragment(), true);
            }
        });
        record.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                ((MultiMediaActivity)getActivity()).replaceFragment(new RecordFragment(), true);
            }
        });
        upload.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startActivity(new Intent(getActivity(), UploadActivity.class));
            }
        });

        return view;
    }
}
