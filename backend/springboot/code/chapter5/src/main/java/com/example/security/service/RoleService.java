package com.example.security.service;

import com.example.security.model.ERole;
import com.example.security.model.Role;
import com.example.security.repository.RoleRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class RoleService {
    
    @Autowired
    private RoleRepository roleRepository;
    
    public Optional<Role> findByName(ERole name) {
        return roleRepository.findByName(name);
    }
    
    public Role save(Role role) {
        return roleRepository.save(role);
    }
}