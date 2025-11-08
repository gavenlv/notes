package com.example.restassured.framework;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.restassured.response.Response;
import org.apache.commons.lang3.RandomStringUtils;
import org.apache.commons.lang3.RandomUtils;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Supplier;

/**
 * 测试数据管理器
 * 提供测试数据的创建、存储、检索和清理功能
 */
public class TestDataManager {
    
    private static final ConcurrentHashMap<String, Object> testDataStore = new ConcurrentHashMap<>();
    private static final ObjectMapper objectMapper = new ObjectMapper();
    
    // 预定义的数据生成器
    private static final Map<String, Supplier<Object>> dataGenerators = new HashMap<>();
    
    static {
        // 初始化数据生成器
        dataGenerators.put("randomString", () -> RandomStringUtils.randomAlphabetic(10));
        dataGenerators.put("randomEmail", () -> 
            RandomStringUtils.randomAlphabetic(8).toLowerCase() + "@example.com");
        dataGenerators.put("randomNumber", () -> RandomUtils.nextInt(1, 1000));
        dataGenerators.put("randomBoolean", () -> RandomUtils.nextBoolean());
        dataGenerators.put("timestamp", () -> System.currentTimeMillis());
    }
    
    /**
     * 存储测试数据
     */
    public static void storeData(String key, Object value) {
        testDataStore.put(key, value);
    }
    
    /**
     * 获取测试数据
     */
    @SuppressWarnings("unchecked")
    public static <T> T getData(String key, Class<T> type) {
        Object value = testDataStore.get(key);
        if (value == null) {
            return null;
        }
        
        // 如果类型匹配，直接返回
        if (type.isInstance(value)) {
            return (T) value;
        }
        
        // 如果是Map且请求的是POJO，尝试转换
        if (value instanceof Map && !type.isAssignableFrom(Map.class)) {
            try {
                return objectMapper.convertValue(value, type);
            } catch (IllegalArgumentException e) {
                throw new RuntimeException("Failed to convert stored data to requested type", e);
            }
        }
        
        // 其他情况抛出异常
        throw new ClassCastException("Cannot cast " + value.getClass() + " to " + type);
    }
    
    /**
     * 获取测试数据（如果不存在则返回null）
     */
    public static Object getData(String key) {
        return testDataStore.get(key);
    }
    
    /**
     * 删除测试数据
     */
    public static void removeData(String key) {
        testDataStore.remove(key);
    }
    
    /**
     * 清除所有测试数据
     */
    public static void clearAllData() {
        testDataStore.clear();
    }
    
    /**
     * 从响应中提取数据并存储
     */
    public static void extractAndStore(String key, Response response, String jsonPath) {
        Object extractedValue = response.jsonPath().get(jsonPath);
        storeData(key, extractedValue);
    }
    
    /**
     * 生成随机数据
     */
    public static Object generateRandomData(String generatorName) {
        Supplier<Object> generator = dataGenerators.get(generatorName);
        if (generator == null) {
            throw new IllegalArgumentException("Unknown data generator: " + generatorName);
        }
        return generator.get();
    }
    
    /**
     * 注册自定义数据生成器
     */
    public static void registerDataGenerator(String name, Supplier<Object> generator) {
        dataGenerators.put(name, generator);
    }
    
    /**
     * 从JSON字符串创建Map并存储
     */
    public static void storeFromJson(String key, String jsonString) {
        try {
            Map<String, Object> data = objectMapper.readValue(jsonString, Map.class);
            storeData(key, data);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Failed to parse JSON string", e);
        }
    }
    
    /**
     * 将存储的数据转换为JSON字符串
     */
    public static String getAsJson(String key) {
        Object data = getData(key);
        try {
            return objectMapper.writeValueAsString(data);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Failed to convert data to JSON", e);
        }
    }
    
    /**
     * 创建测试用户数据
     */
    public static Map<String, Object> createTestUser() {
        Map<String, Object> user = new HashMap<>();
        user.put("name", "Test User " + RandomStringUtils.randomAlphabetic(5));
        user.put("username", "testuser_" + RandomStringUtils.randomAlphabetic(6).toLowerCase());
        user.put("email", RandomStringUtils.randomAlphabetic(8).toLowerCase() + "@example.com");
        user.put("phone", "555-" + RandomStringUtils.randomNumeric(7));
        user.put("website", "https://example.com/" + RandomStringUtils.randomAlphabetic(6).toLowerCase());
        
        Map<String, Object> address = new HashMap<>();
        address.put("street", RandomStringUtils.randomAlphabetic(10) + " St");
        address.put("suite", "Apt. " + RandomUtils.nextInt(100, 999));
        address.put("city", "Test City");
        address.put("zipcode", RandomStringUtils.randomNumeric(5));
        
        Map<String, String> geo = new HashMap<>();
        geo.put("lat", String.format("%.6f", -90 + Math.random() * 180));
        geo.put("lng", String.format("%.6f", -180 + Math.random() * 360));
        address.put("geo", geo);
        
        user.put("address", address);
        
        Map<String, Object> company = new HashMap<>();
        company.put("name", "Test Company " + RandomStringUtils.randomAlphabetic(5));
        company.put("catchPhrase", "Multi-layered client-server neural-net");
        company.put("bs", "harness real-time e-markets");
        
        user.put("company", company);
        
        return user;
    }
    
    /**
     * 创建测试文章数据
     */
    public static Map<String, Object> createTestPost(Integer userId) {
        Map<String, Object> post = new HashMap<>();
        post.put("title", "Test Post " + RandomStringUtils.randomAlphabetic(5));
        post.put("body", "This is a test post body with random content: " + 
                  RandomStringUtils.randomAlphabetic(20) + ".");
        post.put("userId", userId != null ? userId : generateRandomData("randomNumber"));
        return post;
    }
    
    /**
     * 创建测试评论数据
     */
    public static Map<String, Object> createTestComment(Integer postId) {
        Map<String, Object> comment = new HashMap<>();
        comment.put("name", "Test Commenter " + RandomStringUtils.randomAlphabetic(5));
        comment.put("email", RandomStringUtils.randomAlphabetic(8).toLowerCase() + "@example.com");
        comment.put("body", "This is a test comment with random content: " + 
                    RandomStringUtils.randomAlphabetic(15) + ".");
        comment.put("postId", postId != null ? postId : generateRandomData("randomNumber"));
        return comment;
    }
    
    /**
     * 创建测试任务数据
     */
    public static Map<String, Object> createTestTodo(Integer userId) {
        Map<String, Object> todo = new HashMap<>();
        todo.put("title", "Test Todo " + RandomStringUtils.randomAlphabetic(5));
        todo.put("completed", generateRandomData("randomBoolean"));
        todo.put("userId", userId != null ? userId : generateRandomData("randomNumber"));
        return todo;
    }
    
    /**
     * 创建测试相册数据
     */
    public static Map<String, Object> createTestAlbum(Integer userId) {
        Map<String, Object> album = new HashMap<>();
        album.put("title", "Test Album " + RandomStringUtils.randomAlphabetic(5));
        album.put("userId", userId != null ? userId : generateRandomData("randomNumber"));
        return album;
    }
    
    /**
     * 创建测试照片数据
     */
    public static Map<String, Object> createTestPhoto(Integer albumId) {
        Map<String, Object> photo = new HashMap<>();
        photo.put("title", "Test Photo " + RandomStringUtils.randomAlphabetic(5));
        photo.put("url", "https://via.placeholder.com/600/" + RandomStringUtils.randomNumeric(6));
        photo.put("thumbnailUrl", "https://via.placeholder.com/150/" + RandomStringUtils.randomNumeric(6));
        photo.put("albumId", albumId != null ? albumId : generateRandomData("randomNumber"));
        return photo;
    }
    
    /**
     * 存储响应中所有的资源ID
     * 用于后续清理或测试使用
     */
    public static void storeResourceIds(Response response, String idPath, String storageKey) {
        List<Integer> ids = response.jsonPath().getList(idPath);
        storeData(storageKey, ids);
    }
    
    /**
     * 从存储中获取资源ID
     */
    @SuppressWarnings("unchecked")
    public static List<Integer> getResourceIds(String storageKey) {
        return getData(storageKey, List.class);
    }
    
    /**
     * 创建多个测试数据
     */
    public static <T> void createMultipleTestData(String baseKey, int count, Supplier<T> dataSupplier) {
        for (int i = 0; i < count; i++) {
            T data = dataSupplier.get();
            storeData(baseKey + i, data);
        }
    }
    
    /**
     * 获取存储的所有键
     */
    public static String[] getAllStoredKeys() {
        return testDataStore.keySet().toArray(new String[0]);
    }
    
    /**
     * 检查数据是否存在
     */
    public static boolean containsData(String key) {
        return testDataStore.containsKey(key);
    }
}