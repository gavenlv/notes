package com.example.security;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
public class TestControllerTests {

    @Autowired
    private MockMvc mockMvc;

    @Test
    public void testPublicContent() throws Exception {
        mockMvc.perform(get("/api/test/all"))
                .andExpect(status().isOk())
                .andExpect(content().string("Public Content."));
    }

    @Test
    @WithMockUser(roles = "USER")
    public void testUserContentWithUserRole() throws Exception {
        mockMvc.perform(get("/api/test/user"))
                .andExpect(status().isOk())
                .andExpect(content().string("User Content."));
    }

    @Test
    @WithMockUser(roles = "ADMIN")
    public void testUserContentWithAdminRole() throws Exception {
        mockMvc.perform(get("/api/test/user"))
                .andExpect(status().isOk())
                .andExpect(content().string("User Content."));
    }

    @Test
    @WithMockUser(roles = "MODERATOR")
    public void testModeratorContent() throws Exception {
        mockMvc.perform(get("/api/test/mod"))
                .andExpect(status().isOk())
                .andExpect(content().string("Moderator Board."));
    }

    @Test
    @WithMockUser(roles = "ADMIN")
    public void testAdminContent() throws Exception {
        mockMvc.perform(get("/api/test/admin"))
                .andExpect(status().isOk())
                .andExpect(content().string("Admin Board."));
    }

    @Test
    @WithMockUser(roles = "USER")
    public void testModeratorContentWithUserRole() throws Exception {
        mockMvc.perform(get("/api/test/mod"))
                .andExpect(status().isForbidden());
    }
}