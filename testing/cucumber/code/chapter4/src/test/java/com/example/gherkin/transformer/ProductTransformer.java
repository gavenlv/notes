package com.example.gherkin.transformer;

import com.example.gherkin.model.Product;
import io.cucumber.java.ParameterType;

import java.math.BigDecimal;
import java.util.Arrays;
import java.util.List;

/**
 * 产品参数转换器
 */
public class ProductTransformer {
    
    /**
     * 将字符串转换为BigDecimal
     */
    @ParameterType(".*")
    public BigDecimal bigDecimal(String value) {
        try {
            return new BigDecimal(value);
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("无法将 '" + value + "' 转换为BigDecimal");
        }
    }
    
    /**
     * 将字符串转换为布尔值
     * 接受的值: true, false, yes, no, 1, 0
     */
    @ParameterType("true|false|yes|no|1|0")
    public boolean booleanValue(String value) {
        return Arrays.asList("true", "yes", "1").contains(value.toLowerCase());
    }
    
    /**
     * 将字符串转换为产品类别
     */
    @ParameterType("手机|笔记本|平板|耳机|其他")
    public String productCategory(String value) {
        return value;
    }
    
    /**
     * 将字符串转换为产品品牌
     */
    @ParameterType("Apple|Samsung|Sony|Huawei|Xiaomi|其他")
    public String productBrand(String value) {
        return value;
    }
    
    /**
     * 将字符串转换为产品对象
     * 格式: "名称:描述:价格:类别:品牌:库存数量:可用:SKU"
     */
    @ParameterType("([^:]+):([^:]*):([^:]+):([^:]+):([^:]*):([^:]+):([^:]+):([^:]*)")
    public Product product(String name, String description, String price, 
                         String category, String brand, String stockQuantity, 
                         String available, String sku) {
        
        try {
            return Product.builder()
                    .name(name.trim())
                    .description(description.trim().isEmpty() ? null : description.trim())
                    .price(new BigDecimal(price.trim()))
                    .category(category.trim())
                    .brand(brand.trim().isEmpty() ? null : brand.trim())
                    .stockQuantity(Integer.parseInt(stockQuantity.trim()))
                    .available(booleanValue(available.trim()))
                    .sku(sku.trim().isEmpty() ? null : sku.trim())
                    .build();
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("无效的产品参数: " + e.getMessage());
        }
    }
    
    /**
     * 将逗号分隔的字符串转换为产品类别列表
     */
    @ParameterType("([^,]+(?:,[^,]+)*)")
    public List<String> categoryList(String categories) {
        return Arrays.asList(categories.split(","))
                .stream()
                .map(String::trim)
                .collect(java.util.stream.Collectors.toList());
    }
    
    /**
     * 将逗号分隔的字符串转换为产品品牌列表
     */
    @ParameterType("([^,]+(?:,[^,]+)*)")
    public List<String> brandList(String brands) {
        return Arrays.asList(brands.split(","))
                .stream()
                .map(String::trim)
                .collect(java.util.stream.Collectors.toList());
    }
    
    /**
     * 将价格范围字符串转换为价格范围数组
     * 格式: "100-500" 或 "100-" 或 "-500"
     */
    @ParameterType("([0-9.]+)?-([0-9.]+)?")
    public BigDecimal[] priceRange(String minPrice, String maxPrice) {
        BigDecimal min = minPrice != null && !minPrice.isEmpty() ? 
                        new BigDecimal(minPrice) : null;
        BigDecimal max = maxPrice != null && !maxPrice.isEmpty() ? 
                        new BigDecimal(maxPrice) : null;
        return new BigDecimal[]{min, max};
    }
    
    /**
     * 将价格比较操作符转换为谓词
     * 格式: ">100", "<500", "=200", ">=100", "<=500"
     */
    @ParameterType("(>=|<=|>|<|=)([0-9.]+)")
    public PricePredicate pricePredicate(String operator, String value) {
        BigDecimal price = new BigDecimal(value);
        return new PricePredicate(operator, price);
    }
    
    /**
     * 价格谓词类，用于封装价格比较操作
     */
    public static class PricePredicate {
        private final String operator;
        private final BigDecimal value;
        
        public PricePredicate(String operator, BigDecimal value) {
            this.operator = operator;
            this.value = value;
        }
        
        public boolean test(BigDecimal price) {
            if (price == null) return false;
            
            switch (operator) {
                case ">":
                    return price.compareTo(value) > 0;
                case "<":
                    return price.compareTo(value) < 0;
                case "=":
                    return price.compareTo(value) == 0;
                case ">=":
                    return price.compareTo(value) >= 0;
                case "<=":
                    return price.compareTo(value) <= 0;
                default:
                    return false;
            }
        }
        
        public String getOperator() {
            return operator;
        }
        
        public BigDecimal getValue() {
            return value;
        }
    }
}