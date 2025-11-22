package com.example.mybatis.mapper;

import com.example.mybatis.entity.User;
import org.apache.ibatis.annotations.*;

import java.util.List;

@Mapper
public interface UserMapper {
    
    @Select("SELECT id, username, email, created_at FROM users WHERE id = #{id}")
    User selectUserById(Long id);
    
    @Select("SELECT id, username, email, created_at FROM users")
    List<User> selectAllUsers();
    
    @Select("SELECT id, username, email, created_at FROM users WHERE username LIKE CONCAT('%', #{username}, '%')")
    List<User> selectUsersByUsername(String username);
    
    @Insert("INSERT INTO users(username, email, created_at) VALUES(#{username}, #{email}, #{createdAt})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insertUser(User user);
    
    @Update("UPDATE users SET username = #{username}, email = #{email} WHERE id = #{id}")
    int updateUser(User user);
    
    @Delete("DELETE FROM users WHERE id = #{id}")
    int deleteUser(Long id);
    
    // 使用XML映射的示例方法
    List<User> selectUsers(User user);
    
    int batchInsertUsers(List<User> users);
    
    int batchDeleteUsers(List<Long> ids);
}