package com.example.toytiktok.bean;

public class Music {
    private String name;

    public Music(String name, int id) {
        this.name = name;
        this.id = id;
    }

    private int id;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }
}
