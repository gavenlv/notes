package com.example.mybatis.service;

import com.example.mybatis.entity.Order;
import com.example.mybatis.mapper.OrderMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class OrderService {
    
    @Autowired
    private OrderMapper orderMapper;
    
    /**
     * 根据ID查询订单
     */
    public Order getOrderById(Long id) {
        return orderMapper.selectOrderById(id);
    }
    
    /**
     * 根据用户ID查询订单
     */
    public List<Order> getOrdersByUserId(Long userId) {
        return orderMapper.selectOrdersByUserId(userId);
    }
    
    /**
     * 查询所有订单
     */
    public List<Order> getAllOrders() {
        return orderMapper.selectAllOrders();
    }
    
    /**
     * 创建订单
     */
    @Transactional
    public int createOrder(Order order) {
        return orderMapper.insertOrder(order);
    }
    
    /**
     * 更新订单
     */
    @Transactional
    public int updateOrder(Order order) {
        return orderMapper.updateOrder(order);
    }
    
    /**
     * 删除订单
     */
    @Transactional
    public int deleteOrder(Long id) {
        return orderMapper.deleteOrder(id);
    }
    
    /**
     * 根据用户ID删除订单
     */
    @Transactional
    public int deleteOrdersByUserId(Long userId) {
        return orderMapper.deleteOrdersByUserId(userId);
    }
}