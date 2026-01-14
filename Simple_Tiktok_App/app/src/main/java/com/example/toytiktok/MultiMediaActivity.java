package com.example.toytiktok;

import androidx.appcompat.app.AppCompatActivity;
import androidx.fragment.app.Fragment;

import android.os.Bundle;
import android.widget.FrameLayout;

import com.example.toytiktok.fragments.MainFragment;

public class MultiMediaActivity extends AppCompatActivity {

    private FrameLayout container;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_multi_media);

        container = findViewById(R.id.multi_container);
        replaceFragment(new MainFragment(), false);
    }


    public void replaceFragment(Fragment fragment, boolean isSave) {
        if (!isSave) {
            getSupportFragmentManager().beginTransaction().replace(R.id.multi_container, fragment).commit();
        } else {
            getSupportFragmentManager().beginTransaction().replace(R.id.multi_container, fragment).addToBackStack(null).commit();
        }
    }
}