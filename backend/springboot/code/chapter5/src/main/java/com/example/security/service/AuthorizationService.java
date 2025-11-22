package com.example.security.service;

import com.example.security.model.User;
import com.example.security.model.Role;
import com.example.security.model.ERole;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Set;
import java.util.HashSet;

@Service
public class AuthorizationService {
    
    @Autowired
    private UserService userService;
    
    @Autowired
    private RoleService roleService;
    
    /**
     * 为用户分配角色
     */
    public User assignRolesToUser(User user, Set<String> strRoles) {
        Set<Role> roles = new HashSet<>();
        
        if (strRoles == null || strRoles.isEmpty()) {
            // 默认分配USER角色
            Role userRole = roleService.findByName(ERole.ROLE_USER)
                    .orElseThrow(() -> new RuntimeException("Error: Role is not found."));
            roles.add(userRole);
        } else {
            strRoles.forEach(role -> {
                switch (role.toLowerCase()) {
                    case "admin":
                        Role adminRole = roleService.findByName(ERole.ROLE_ADMIN)
                                .orElseThrow(() -> new RuntimeException("Error: Role is not found."));
                        roles.add(adminRole);
                        break;
                    case "mod":
                        Role modRole = roleService.findByName(ERole.ROLE_MODERATOR)
                                .orElseThrow(() -> new RuntimeException("Error: Role is not found."));
                        roles.add(modRole);
                        break;
                    default:
                        Role userRole = roleService.findByName(ERole.ROLE_USER)
                                .orElseThrow(() -> new RuntimeException("Error: Role is not found."));
                        roles.add(userRole);
                }
            });
        }
        
        user.setRoles(roles);
        return userService.save(user);
    }
    
    /**
     * 检查用户是否具有特定角色
     */
    public boolean hasRole(User user, ERole role) {
        return user.getRoles().stream()
                .anyMatch(r -> r.getName().equals(role));
    }
    
    /**
     * 检查用户是否具有管理员角色
     */
    public boolean isAdmin(User user) {
        return hasRole(user, ERole.ROLE_ADMIN);
    }
    
    /**
     * 检查用户是否具有版主角色
     */
    public boolean isModerator(User user) {
        return hasRole(user, ERole.ROLE_MODERATOR);
    }
    
    /**
     * 检查用户是否具有普通用户角色
     */
    public boolean isUser(User user) {
        return hasRole(user, ERole.ROLE_USER);
    }
}