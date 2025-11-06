package com.example.gherkin.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.Objects;

/**
 * 产品模型类
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Product {
    private Long id;
    private String name;
    private String description;
    private BigDecimal price;
    private String category;
    private String brand;
    private int stockQuantity;
    private boolean available;
    private String sku;
    
    /**
     * 检查产品是否可用（有库存且标记为可用）
     * @return 如果产品可用返回true，否则返回false
     */
    public boolean isInStock() {
        return available && stockQuantity > 0;
    }
    
    /**
     * 检查产品是否属于指定类别
     * @param category 要检查的类别
     * @return 如果产品属于该类别返回true，否则返回false
     */
    public boolean isInCategory(String category) {
        return Objects.equals(this.category, category);
    }
    
    /**
     * 检查产品价格是否在指定范围内
     * @param minPrice 最低价格
     * @param maxPrice 最高价格
     * @return 如果价格在范围内返回true，否则返回false
     */
    public boolean isPriceInRange(BigDecimal minPrice, BigDecimal maxPrice) {
        if (price == null) return false;
        if (minPrice != null && price.compareTo(minPrice) < 0) return false;
        if (maxPrice != null && price.compareTo(maxPrice) > 0) return false;
        return true;
    }
    
    /**
     * 减少库存数量
     * @param quantity 要减少的数量
     * @return 如果成功减少返回true，否则返回false
     */
    public boolean reduceStock(int quantity) {
        if (quantity <= 0 || stockQuantity < quantity) {
            return false;
        }
        stockQuantity -= quantity;
        if (stockQuantity == 0) {
            available = false;
        }
        return true;
    }
    
    /**
     * 增加库存数量
     * @param quantity 要增加的数量
     */
    public void increaseStock(int quantity) {
        if (quantity > 0) {
            stockQuantity += quantity;
            if (!available && stockQuantity > 0) {
                available = true;
            }
        }
    }
}