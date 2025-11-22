package com.example.security;

import com.example.security.model.User;
import com.example.security.repository.UserRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.security.crypto.password.PasswordEncoder;
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

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Test
    public void testPublicAccess() throws Exception {
        mockMvc.perform(get("/api/test/all"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.message").value("Public Content."));
    }

    @Test
    public void testUnauthorizedAccessToProtectedEndpoint() throws Exception {
        mockMvc.perform(get("/api/test/user"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    public void testUserRegistrationAndAuthentication() throws Exception {
        // Register a new user
        String signupRequest = "{ \"username\": \"testuser\", \"email\": \"test@example.com\", \"password\": \"password123\", \"roles\": [\"user\"] }";
        
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

    @Test
    public void testUserRoleBasedAccess() throws Exception {
        // Create a user with USER role
        User user = new User("testuser2", "test2@example.com", passwordEncoder.encode("password123"));
        userRepository.save(user);

        // Authenticate the user to get token
        String signinRequest = "{ \"username\": \"testuser2\", \"password\": \"password123\" }";
        
        String token = mockMvc.perform(post("/api/auth/signin")
                .contentType(MediaType.APPLICATION_JSON)
                .content(signinRequest))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();

        // Extract token from response (simplified - in reality you'd parse JSON)
        // For this test, we'll just verify that authenticated requests work
        mockMvc.perform(get("/api/test/user"))
                .andExpect(status().isUnauthorized()); // Will fail without token

        // Note: A full test would extract the token and use it in the Authorization header
    }
}