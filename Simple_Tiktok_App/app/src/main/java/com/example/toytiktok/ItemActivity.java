package com.example.toytiktok;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;

import com.example.toytiktok.adapters.MyAdapter;
import com.example.toytiktok.utils.HttpUtil;

public class ItemActivity extends AppCompatActivity {
    private int position;
    private int count;
    private MyAdapter.MyViewHolder holder;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.item);

        holder = new MyAdapter.MyViewHolder(findViewById(R.id.item_parent));

        Intent intent = getIntent();
        position = intent.getIntExtra("position", 0);
        count = intent.getIntExtra("count", 0);
        holder.functions(holder, position, HttpUtil.ResType.PART);

    }

}