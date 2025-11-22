package com.example.mybatis.service;

import com.example.mybatis.entity.User;
import com.example.mybatis.mapper.UserMapper;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class UserService {
    
    @Autowired
    private UserMapper userMapper;
    
    /**
     * 根据ID查询用户
     */
    public User getUserById(Long id) {
        return userMapper.selectUserById(id);
    }
    
    /**
     * 查询所有用户
     */
    public List<User> getAllUsers() {
        return userMapper.selectAllUsers();
    }
    
    /**
     * 分页查询用户
     */
    public PageInfo<User> getUsersByPage(int pageNum, int pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<User> users = userMapper.selectAllUsers();
        return new PageInfo<>(users);
    }
    
    /**
     * 根据用户名模糊查询
     */
    public List<User> getUsersByUsername(String username) {
        return userMapper.selectUsersByUsername(username);
    }
    
    /**
     * 创建用户
     */
    @Transactional
    public int createUser(User user) {
        return userMapper.insertUser(user);
    }
    
    /**
     * 更新用户
     */
    @Transactional
    public int updateUser(User user) {
        return userMapper.updateUser(user);
    }
    
    /**
     * 删除用户
     */
    @Transactional
    public int deleteUser(Long id) {
        return userMapper.deleteUser(id);
    }
    
    /**
     * 批量创建用户
     */
    @Transactional
    public int batchCreateUsers(List<User> users) {
        return userMapper.batchInsertUsers(users);
    }
    
    /**
     * 批量删除用户
     */
    @Transactional
    public int batchDeleteUsers(List<Long> ids) {
        return userMapper.batchDeleteUsers(ids);
    }
}