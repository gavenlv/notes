package com.example.login;

public class User {
    private String username;
    private String password;
    private boolean active;
    
    public User(String username, String password) {
        this.username = username;
        this.password = password;
        this.active = true;
    }
    
    public String getUsername() {
        return username;
    }
    
    public String getPassword() {
        return password;
    }
    
    public boolean isActive() {
        return active;
    }
    
    public void setActive(boolean active) {
        this.active = active;
    }
}