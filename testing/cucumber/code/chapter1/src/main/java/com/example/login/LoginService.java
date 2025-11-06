package com.example.login;

public class LoginService {
    private AuthenticationService authService;
    
    public LoginService(AuthenticationService authService) {
        this.authService = authService;
    }
    
    public AuthenticationService.LoginResult authenticate(String username, String password) {
        return authService.login(username, password);
    }
}