package com.example.security.controller;

import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

@CrossOrigin(origins = "*", maxAge = 3600)
@RestController
@RequestMapping("/api/test")
public class TestController {

    @GetMapping("/all")
    public Map<String, Object> allAccess() {
        Map<String, Object> response = new HashMap<>();
        response.put("message", "Public Content.");
        
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication != null && authentication.isAuthenticated() && 
            !"anonymousUser".equals(authentication.getPrincipal())) {
            response.put("currentUser", authentication.getName());
        }
        
        return response;
    }

    @GetMapping("/user")
    @PreAuthorize("hasRole('USER') or hasRole('MODERATOR') or hasRole('ADMIN')")
    public Map<String, Object> userAccess() {
        Map<String, Object> response = new HashMap<>();
        response.put("message", "User Content.");
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        response.put("currentUser", authentication.getName());
        response.put("authorities", authentication.getAuthorities());
        return response;
    }

    @GetMapping("/mod")
    @PreAuthorize("hasRole('MODERATOR')")
    public Map<String, Object> moderatorAccess() {
        Map<String, Object> response = new HashMap<>();
        response.put("message", "Moderator Board.");
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        response.put("currentUser", authentication.getName());
        return response;
    }

    @GetMapping("/admin")
    @PreAuthorize("hasRole('ADMIN')")
    public Map<String, Object> adminAccess() {
        Map<String, Object> response = new HashMap<>();
        response.put("message", "Admin Board.");
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        response.put("currentUser", authentication.getName());
        return response;
    }
}