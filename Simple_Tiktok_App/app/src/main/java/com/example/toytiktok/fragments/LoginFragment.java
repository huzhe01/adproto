package com.example.toytiktok.fragments;

import android.content.Context;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import com.example.toytiktok.MainActivity;
import com.example.toytiktok.R;
import com.example.toytiktok.utils.HttpUtil;

public class LoginFragment extends Fragment {
    private LoginCallback callback;


    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.login_frag, container, false);

        EditText nameEt = view.findViewById(R.id.login_name);
        EditText pwdEt = view.findViewById(R.id.login_pwd);
        Button btn = view.findViewById(R.id.login_btn);

        btn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String name = nameEt.getText().toString();
                String pwd = pwdEt.getText().toString();
                if (name != null && name.length() != 0) {
                    callback.loginCallBack(name, HttpUtil.loginRequest(name));
                    Toast.makeText(getContext(), "登陆成功", Toast.LENGTH_SHORT).show();
                    HttpUtil.userName = name;
                } else {
                    Toast.makeText(getContext(), "登陆失败", Toast.LENGTH_SHORT).show();
                }
            }
        });

        return view;
    }

    public static interface LoginCallback {
        public void loginCallBack(String userName, String id);
    }


    @Override
    public void onAttach(@NonNull Context context) {
        super.onAttach(context);
        this.callback = (LoginCallback) context;
    }
}
