package com.example.mybatis.mapper;

import com.example.mybatis.entity.Order;
import org.apache.ibatis.annotations.*;

import java.util.List;

@Mapper
public interface OrderMapper {
    
    @Select("SELECT id, user_id, product_name, price, quantity, total_amount, created_at FROM orders WHERE id = #{id}")
    Order selectOrderById(Long id);
    
    @Select("SELECT id, user_id, product_name, price, quantity, total_amount, created_at FROM orders WHERE user_id = #{userId}")
    List<Order> selectOrdersByUserId(Long userId);
    
    @Select("SELECT id, user_id, product_name, price, quantity, total_amount, created_at FROM orders")
    List<Order> selectAllOrders();
    
    @Insert("INSERT INTO orders(user_id, product_name, price, quantity, total_amount, created_at) " +
            "VALUES(#{userId}, #{productName}, #{price}, #{quantity}, #{totalAmount}, #{createdAt})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insertOrder(Order order);
    
    @Update("UPDATE orders SET product_name = #{productName}, price = #{price}, quantity = #{quantity}, " +
            "total_amount = #{totalAmount} WHERE id = #{id}")
    int updateOrder(Order order);
    
    @Delete("DELETE FROM orders WHERE id = #{id}")
    int deleteOrder(Long id);
    
    @Delete("DELETE FROM orders WHERE user_id = #{userId}")
    int deleteOrdersByUserId(Long userId);
}