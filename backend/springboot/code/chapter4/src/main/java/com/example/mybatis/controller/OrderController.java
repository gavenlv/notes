package com.example.mybatis.controller;

import com.example.mybatis.entity.Order;
import com.example.mybatis.service.OrderService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/orders")
public class OrderController {
    
    @Autowired
    private OrderService orderService;
    
    /**
     * 根据ID查询订单
     */
    @GetMapping("/{id}")
    public ResponseEntity<Order> getOrderById(@PathVariable Long id) {
        Order order = orderService.getOrderById(id);
        if (order != null) {
            return ResponseEntity.ok(order);
        } else {
            return ResponseEntity.notFound().build();
        }
    }
    
    /**
     * 根据用户ID查询订单
     */
    @GetMapping("/user/{userId}")
    public ResponseEntity<List<Order>> getOrdersByUserId(@PathVariable Long userId) {
        List<Order> orders = orderService.getOrdersByUserId(userId);
        return ResponseEntity.ok(orders);
    }
    
    /**
     * 查询所有订单
     */
    @GetMapping
    public ResponseEntity<List<Order>> getAllOrders() {
        List<Order> orders = orderService.getAllOrders();
        return ResponseEntity.ok(orders);
    }
    
    /**
     * 创建订单
     */
    @PostMapping
    public ResponseEntity<Integer> createOrder(@RequestBody Order order) {
        int result = orderService.createOrder(order);
        return ResponseEntity.ok(result);
    }
    
    /**
     * 更新订单
     */
    @PutMapping("/{id}")
    public ResponseEntity<Integer> updateOrder(@PathVariable Long id, @RequestBody Order order) {
        order.setId(id);
        int result = orderService.updateOrder(order);
        return ResponseEntity.ok(result);
    }
    
    /**
     * 删除订单
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Integer> deleteOrder(@PathVariable Long id) {
        int result = orderService.deleteOrder(id);
        return ResponseEntity.ok(result);
    }
}