package com.example.gherkin.context;

import java.util.HashMap;
import java.util.Map;
import java.util.function.Supplier;

/**
 * 测试上下文，用于在步骤定义之间共享状态
 */
public class TestContext {
    
    private final Map<String, Object> data = new HashMap<>();
    
    /**
     * 存储数据到上下文
     */
    public void set(String key, Object value) {
        data.put(key, value);
    }
    
    /**
     * 从上下文获取数据
     */
    @SuppressWarnings("unchecked")
    public <T> T get(String key, Class<T> type) {
        Object value = data.get(key);
        if (value == null) {
            return null;
        }
        
        if (!type.isInstance(value)) {
            throw new ClassCastException("Value for key '" + key + "' is not of type " + type.getName());
        }
        
        return (T) value;
    }
    
    /**
     * 从上下文获取数据，如果不存在则使用提供的默认值
     */
    @SuppressWarnings("unchecked")
    public <T> T get(String key, Class<T> type, T defaultValue) {
        Object value = data.get(key);
        if (value == null) {
            return defaultValue;
        }
        
        if (!type.isInstance(value)) {
            throw new ClassCastException("Value for key '" + key + "' is not of type " + type.getName());
        }
        
        return (T) value;
    }
    
    /**
     * 从上下文获取数据，如果不存在则使用提供的Supplier创建
     */
    public <T> T getOrCreate(String key, Class<T> type, Supplier<T> supplier) {
        if (!data.containsKey(key)) {
            data.put(key, supplier.get());
        }
        return get(key, type);
    }
    
    /**
     * 检查上下文中是否包含指定键
     */
    public boolean contains(String key) {
        return data.containsKey(key);
    }
    
    /**
     * 从上下文中移除数据
     */
    public void remove(String key) {
        data.remove(key);
    }
    
    /**
     * 清空上下文
     */
    public void clear() {
        data.clear();
    }
    
    /**
     * 获取上下文中所有键
     */
    public java.util.Set<String> getKeys() {
        return data.keySet();
    }
    
    /**
     * 获取上下文中所有数据
     */
    public Map<String, Object> getAll() {
        return new HashMap<>(data);
    }
    
    /**
     * 获取上下文大小
     */
    public int size() {
        return data.size();
    }
    
    /**
     * 检查上下文是否为空
     */
    public boolean isEmpty() {
        return data.isEmpty();
    }
}