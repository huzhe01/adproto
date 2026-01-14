package com.example.toytiktok.fragments;

import android.app.Dialog;
import android.content.Context;
import android.graphics.Color;
import android.os.Bundle;
import android.util.Log;
import android.view.Display;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ListView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.coordinatorlayout.widget.CoordinatorLayout;

import com.example.toytiktok.R;
import com.example.toytiktok.VideoDownLoadCallback;
import com.example.toytiktok.adapters.IconAdapter;
import com.example.toytiktok.view.IconSetView;
import com.google.android.material.bottomsheet.BottomSheetBehavior;
import com.google.android.material.bottomsheet.BottomSheetDialogFragment;

public class ShareFragment extends BottomSheetDialogFragment implements IconAdapter.IconViewHolder.JumpCallBack {
    private Context mContext;

    public static ShareFragment getInstance(String videoUrl) {
        ShareFragment fragment = new ShareFragment();
        Bundle bundle = new Bundle();
        bundle.putString("videoUrl", videoUrl);
        fragment.setArguments(bundle);
        return fragment;
    }

    private BottomSheetBehavior<View> mBottomSheetBehavior;
    private BottomSheetBehavior.BottomSheetCallback mBottomSheetBehaviorCallback
            = new BottomSheetBehavior.BottomSheetCallback() {

        @Override
        public void onStateChanged(@NonNull View bottomSheet, int newState) {
            if (newState == BottomSheetBehavior.STATE_DRAGGING) {
                mBottomSheetBehavior.setState(BottomSheetBehavior.STATE_COLLAPSED);
            }
        }
        @Override
        public void onSlide(@NonNull View bottomSheet, float slideOffset) {
        }
    };


    @Override
    public void onAttach(@NonNull Context context) {
        super.onAttach(context);
        mContext = context;
    }

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.share_frag, container, false);
        Button button = view.findViewById(R.id.share_btn);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                ShareFragment.this.dismiss();
            }
        });
        Bundle bundle = getArguments();
        String videoUrl = null;
        if (bundle != null) {
            videoUrl = bundle.getString("videoUrl");
        }

        IconSetView view1 = view.findViewById(R.id.icon_set_one);
        IconSetView view2 = view.findViewById(R.id.icon_set_two);
        view1.initView(ShareFragment.this, (VideoDownLoadCallback) mContext, videoUrl);
        view2.initView(ShareFragment.this, (VideoDownLoadCallback) mContext, videoUrl);

        return view;
    }

    @Override
    public void onStart() {
        super.onStart();
        Dialog dialog = getDialog();

        if (dialog != null) {
            View bottomSheet = dialog.findViewById(R.id.design_bottom_sheet);
            bottomSheet.getLayoutParams().height = ViewGroup.LayoutParams.MATCH_PARENT;
        }
        final View view = getView();
        view.post(new Runnable() {
            @Override
            public void run() {
                View parent = (View) view.getParent();
                CoordinatorLayout.LayoutParams params = (CoordinatorLayout.LayoutParams) (parent).getLayoutParams();
                CoordinatorLayout.Behavior behavior = params.getBehavior();
                mBottomSheetBehavior = (BottomSheetBehavior) behavior;
                mBottomSheetBehavior.setBottomSheetCallback(mBottomSheetBehaviorCallback);
                Display display = getActivity().getWindowManager().getDefaultDisplay();

                int height = display.getHeight() / 2;
                mBottomSheetBehavior.setPeekHeight(height);

                parent.setBackgroundColor(Color.GRAY);
            }
        });
    }

    @Override
    public void callback() {
        PyqFragment fragment = new PyqFragment();
        fragment.show(getActivity().getSupportFragmentManager(), "pyq");
        ShareFragment.this.dismiss();
    }
}