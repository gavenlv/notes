package com.example.login;

public class LoginResult {
    private boolean success;
    private String message;
    
    public LoginResult(boolean success, String message) {
        this.success = success;
        this.message = message;
    }
    
    public boolean isSuccess() {
        return success;
    }
    
    public String getMessage() {
        return message;
    }
    
    public static LoginResult success(String message) {
        return new LoginResult(true, message);
    }
    
    public static LoginResult failure(String message) {
        return new LoginResult(false, message);
    }
}