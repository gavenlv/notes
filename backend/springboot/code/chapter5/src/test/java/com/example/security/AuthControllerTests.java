package com.example.security;

import com.example.security.model.ERole;
import com.example.security.model.Role;
import com.example.security.model.User;
import com.example.security.repository.RoleRepository;
import com.example.security.repository.UserRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashSet;
import java.util.Set;

import static org.hamcrest.Matchers.containsString;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@Transactional
public class AuthControllerTests {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    UserRepository userRepository;

    @Autowired
    RoleRepository roleRepository;

    @Autowired
    PasswordEncoder passwordEncoder;

    @Test
    public void testRegisterUser() throws Exception {
        mockMvc.perform(post("/api/auth/signup")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"username\":\"testuser\",\"email\":\"test@example.com\",\"password\":\"password\"}"))
                .andExpect(status().isOk())
                .andExpect(content().string(containsString("User registered successfully")));
    }

    @Test
    public void testRegisterUserWithExistingUsername() throws Exception {
        // 先创建一个用户
        User user = new User("existinguser", "existing@example.com", passwordEncoder.encode("password"));
        Set<Role> roles = new HashSet<>();
        Role userRole = roleRepository.findByName(ERole.ROLE_USER)
            .orElseGet(() -> {
                Role newRole = new Role(ERole.ROLE_USER);
                return roleRepository.save(newRole);
            });
        roles.add(userRole);
        user.setRoles(roles);
        userRepository.save(user);

        mockMvc.perform(post("/api/auth/signup")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"username\":\"existinguser\",\"email\":\"new@example.com\",\"password\":\"password\"}"))
                .andExpect(status().isBadRequest())
                .andExpect(content().string(containsString("Error: Username is already taken")));
    }

    @Test
    public void testAuthenticateUser() throws Exception {
        // 先注册一个用户
        mockMvc.perform(post("/api/auth/signup")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"username\":\"authuser\",\"email\":\"auth@example.com\",\"password\":\"password\"}"))
                .andExpect(status().isOk());

        mockMvc.perform(post("/api/auth/signin")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"username\":\"authuser\",\"password\":\"password\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.token").exists())
                .andExpect(jsonPath("$.username").value("authuser"));
    }
}