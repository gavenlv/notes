package com.example.gherkin.service;

import com.example.gherkin.model.Product;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Predicate;
import java.util.stream.Collectors;

/**
 * 产品服务类
 */
@Service
public class ProductService {
    private final Map<Long, Product> products = new HashMap<>();
    private long nextId = 1L;
    
    /**
     * 初始化一些示例产品
     */
    public ProductService() {
        initializeSampleProducts();
    }
    
    /**
     * 创建新产品
     * @param product 要创建的产品
     * @return 创建的产品（带有生成的ID）
     */
    public Product createProduct(Product product) {
        Product newProduct = Product.builder()
                .id(nextId++)
                .name(product.getName())
                .description(product.getDescription())
                .price(product.getPrice())
                .category(product.getCategory())
                .brand(product.getBrand())
                .stockQuantity(product.getStockQuantity())
                .available(product.isAvailable())
                .sku(product.getSku())
                .build();
        
        products.put(newProduct.getId(), newProduct);
        return newProduct;
    }
    
    /**
     * 根据ID获取产品
     * @param id 产品ID
     * @return 产品的Optional对象
     */
    public Optional<Product> getProductById(Long id) {
        return Optional.ofNullable(products.get(id));
    }
    
    /**
     * 根据SKU获取产品
     * @param sku 产品SKU
     * @return 产品的Optional对象
     */
    public Optional<Product> getProductBySku(String sku) {
        return products.values().stream()
                .filter(p -> p.getSku().equals(sku))
                .findFirst();
    }
    
    /**
     * 获取所有产品
     * @return 所有产品的列表
     */
    public List<Product> getAllProducts() {
        return new ArrayList<>(products.values());
    }
    
    /**
     * 根据条件搜索产品
     * @param predicate 搜索条件
     * @return 符合条件的产品列表
     */
    public List<Product> searchProducts(Predicate<Product> predicate) {
        return products.values().stream()
                .filter(predicate)
                .collect(Collectors.toList());
    }
    
    /**
     * 根据名称搜索产品（模糊匹配）
     * @param name 产品名称或部分名称
     * @return 匹配的产品列表
     */
    public List<Product> searchProductsByName(String name) {
        return searchProducts(p -> 
            p.getName() != null && p.getName().toLowerCase().contains(name.toLowerCase()));
    }
    
    /**
     * 根据类别搜索产品
     * @param category 产品类别
     * @return 匹配的产品列表
     */
    public List<Product> searchProductsByCategory(String category) {
        return searchProducts(p -> p.isInCategory(category));
    }
    
    /**
     * 根据品牌搜索产品
     * @param brand 产品品牌
     * @return 匹配的产品列表
     */
    public List<Product> searchProductsByBrand(String brand) {
        return searchProducts(p -> 
            p.getBrand() != null && p.getBrand().equalsIgnoreCase(brand));
    }
    
    /**
     * 根据价格范围搜索产品
     * @param minPrice 最低价格（可为null表示无下限）
     * @param maxPrice 最高价格（可为null表示无上限）
     * @return 匹配的产品列表
     */
    public List<Product> searchProductsByPriceRange(BigDecimal minPrice, BigDecimal maxPrice) {
        return searchProducts(p -> p.isPriceInRange(minPrice, maxPrice));
    }
    
    /**
     * 搜索有库存的产品
     * @return 有库存的产品列表
     */
    public List<Product> searchInStockProducts() {
        return searchProducts(Product::isInStock);
    }
    
    /**
     * 复合搜索：根据名称、类别、品牌和价格范围搜索产品
     * @param name 产品名称（可为null）
     * @param category 产品类别（可为null）
     * @param brand 产品品牌（可为null）
     * @param minPrice 最低价格（可为null）
     * @param maxPrice 最高价格（可为null）
     * @return 匹配的产品列表
     */
    public List<Product> searchProducts(String name, String category, String brand, 
                                       BigDecimal minPrice, BigDecimal maxPrice) {
        return searchProducts(p -> {
            boolean matches = true;
            
            if (name != null && !name.isEmpty()) {
                matches = matches && (p.getName() != null && 
                    p.getName().toLowerCase().contains(name.toLowerCase()));
            }
            
            if (category != null && !category.isEmpty()) {
                matches = matches && p.isInCategory(category);
            }
            
            if (brand != null && !brand.isEmpty()) {
                matches = matches && (p.getBrand() != null && 
                    p.getBrand().equalsIgnoreCase(brand));
            }
            
            matches = matches && p.isPriceInRange(minPrice, maxPrice);
            
            return matches;
        });
    }
    
    /**
     * 更新产品信息
     * @param id 产品ID
     * @param product 更新的产品信息
     * @return 更新后的产品的Optional对象
     */
    public Optional<Product> updateProduct(Long id, Product product) {
        if (!products.containsKey(id)) {
            return Optional.empty();
        }
        
        Product existingProduct = products.get(id);
        Product updatedProduct = Product.builder()
                .id(id)
                .name(product.getName() != null ? product.getName() : existingProduct.getName())
                .description(product.getDescription() != null ? product.getDescription() : existingProduct.getDescription())
                .price(product.getPrice() != null ? product.getPrice() : existingProduct.getPrice())
                .category(product.getCategory() != null ? product.getCategory() : existingProduct.getCategory())
                .brand(product.getBrand() != null ? product.getBrand() : existingProduct.getBrand())
                .stockQuantity(product.getStockQuantity() >= 0 ? product.getStockQuantity() : existingProduct.getStockQuantity())
                .available(product.isAvailable())
                .sku(product.getSku() != null ? product.getSku() : existingProduct.getSku())
                .build();
        
        products.put(id, updatedProduct);
        return Optional.of(updatedProduct);
    }
    
    /**
     * 删除产品
     * @param id 产品ID
     * @return 如果删除成功返回true，否则返回false
     */
    public boolean deleteProduct(Long id) {
        return products.remove(id) != null;
    }
    
    /**
     * 初始化一些示例产品
     */
    private void initializeSampleProducts() {
        createProduct(Product.builder()
                .name("iPhone 14 Pro")
                .description("Apple最新旗舰手机")
                .price(new BigDecimal("999.00"))
                .category("手机")
                .brand("Apple")
                .stockQuantity(50)
                .available(true)
                .sku("IP14P-128-BLK")
                .build());
                
        createProduct(Product.builder()
                .name("Samsung Galaxy S23")
                .description("三星旗舰安卓手机")
                .price(new BigDecimal("899.00"))
                .category("手机")
                .brand("Samsung")
                .stockQuantity(30)
                .available(true)
                .sku("SGS23-256-BLU")
                .build());
                
        createProduct(Product.builder()
                .name("MacBook Pro 16")
                .description("Apple高性能笔记本电脑")
                .price(new BigDecimal("2499.00"))
                .category("笔记本")
                .brand("Apple")
                .stockQuantity(15)
                .available(true)
                .sku("MBP16-M2-512")
                .build());
                
        createProduct(Product.builder()
                .name("Sony WH-1000XM5")
                .description("索尼降噪耳机")
                .price(new BigDecimal("399.00"))
                .category("耳机")
                .brand("Sony")
                .stockQuantity(0)
                .available(false)
                .sku("SNY-XM5-BLK")
                .build());
                
        createProduct(Product.builder()
                .name("iPad Air")
                .description("Apple中端平板电脑")
                .price(new BigDecimal("599.00"))
                .category("平板")
                .brand("Apple")
                .stockQuantity(25)
                .available(true)
                .sku("IPAD-AIR-64")
                .build());
    }
}