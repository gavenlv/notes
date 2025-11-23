package com.example.security;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@Transactional
public class SecurityIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    public void testPublicAccess() throws Exception {
        mockMvc.perform(get("/api/test/all"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.message").value("Public Content."));
    }

    @Test
    public void testUnauthorizedAccessToProtectedEndpoint() throws Exception {
        mockMvc.perform(get("/api/test/user"))
                .andExpect(status().isForbidden()); // Should be forbidden instead of unauthorized
    }

    @Test
    public void testUserRegistrationAndAuthentication() throws Exception {
        // Register a new user
        String signupRequest = "{ \"username\": \"testuser\", \"email\": \"test@example.com\", \"password\": \"password123\" }";
        
        mockMvc.perform(post("/api/auth/signup")
                .contentType(MediaType.APPLICATION_JSON)
                .content(signupRequest))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.message").value("User registered successfully!"));

        // Authenticate the user
        String signinRequest = "{ \"username\": \"testuser\", \"password\": \"password123\" }";
        
        mockMvc.perform(post("/api/auth/signin")
                .contentType(MediaType.APPLICATION_JSON)
                .content(signinRequest))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.token").exists())
                .andExpect(jsonPath("$.username").value("testuser"));
    }
}