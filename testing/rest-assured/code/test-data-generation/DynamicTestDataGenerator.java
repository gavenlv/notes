package com.example.restassured.testdata.generation;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.commons.lang3.RandomStringUtils;
import org.apache.commons.lang3.RandomUtils;

import java.util.*;
import java.util.function.Supplier;

/**
 * 动态测试数据生成器
 * 提供各种类型的数据生成功能，用于API测试
 */
public class DynamicTestDataGenerator {
    
    private static final ObjectMapper objectMapper = new ObjectMapper();
    private static final Random random = new Random();
    
    // 常用数据模板
    private static final String[] FIRST_NAMES = {
        "John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Lisa", 
        "James", "Jennifer", "William", "Mary", "Richard", "Patricia", "Joseph", "Linda"
    };
    
    private static final String[] LAST_NAMES = {
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas"
    };
    
    private static final String[] CITIES = {
        "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
        "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville",
        "Fort Worth", "Columbus", "Charlotte", "San Francisco"
    };
    
    private static final String[] COMPANIES = {
        "Tech Solutions", "Digital Innovations", "Data Systems", "Cloud Services", 
        "Software Masters", "Web Developers", "Mobile Apps", "AI Technologies",
        "Security Experts", "Database Pros", "Network Solutions", "IT Consulting"
    };
    
    private static final String[] PRODUCT_CATEGORIES = {
        "Electronics", "Clothing", "Home & Garden", "Sports & Outdoors", 
        "Books & Media", "Toys & Games", "Health & Beauty", "Automotive"
    };
    
    /**
     * 生成随机用户数据
     */
    public static Map<String, Object> generateUser() {
        String firstName = FIRST_NAMES[random.nextInt(FIRST_NAMES.length)];
        String lastName = LAST_NAMES[random.nextInt(LAST_NAMES.length)];
        String username = firstName.toLowerCase() + "." + lastName.toLowerCase() + random.nextInt(1000);
        String email = username + "@example.com";
        String phone = String.format("555-%03d-%04d", 
                                   RandomUtils.nextInt(100, 999), 
                                   RandomUtils.nextInt(1000, 9999));
        
        Map<String, Object> user = new HashMap<>();
        user.put("name", firstName + " " + lastName);
        user.put("username", username);
        user.put("email", email);
        user.put("phone", phone);
        user.put("website", "https://" + username + ".example.com");
        
        // 地址信息
        Map<String, Object> address = generateAddress();
        user.put("address", address);
        
        // 公司信息
        Map<String, Object> company = generateCompany();
        user.put("company", company);
        
        return user;
    }
    
    /**
     * 生成随机地址数据
     */
    public static Map<String, Object> generateAddress() {
        String streetNumber = String.valueOf(RandomUtils.nextInt(100, 9999));
        String[] streetTypes = {"St", "Ave", "Blvd", "Dr", "Ln", "Rd"};
        String streetName = RandomStringUtils.randomAlphabetic(8);
        String streetType = streetTypes[random.nextInt(streetTypes.length)];
        String street = streetNumber + " " + streetName + " " + streetType;
        
        String city = CITIES[random.nextInt(CITIES.length)];
        String zipcode = String.format("%05d", RandomUtils.nextInt(10000, 99999));
        
        Map<String, Object> address = new HashMap<>();
        address.put("street", street);
        address.put("suite", "Apt. " + RandomUtils.nextInt(100, 999));
        address.put("city", city);
        address.put("zipcode", zipcode);
        
        // 地理坐标
        Map<String, String> geo = new HashMap<>();
        geo.put("lat", String.format("%.6f", -90 + 180 * random.nextDouble()));
        geo.put("lng", String.format("%.6f", -180 + 360 * random.nextDouble()));
        address.put("geo", geo);
        
        return address;
    }
    
    /**
     * 生成随机公司数据
     */
    public static Map<String, Object> generateCompany() {
        String companyName = COMPANIES[random.nextInt(COMPANIES.length)] + " " + RandomStringUtils.randomAlphabetic(5);
        
        Map<String, Object> company = new HashMap<>();
        company.put("name", companyName);
        company.put("catchPhrase", "Multi-layered client-server neural-net");
        company.put("bs", "harness real-time e-markets");
        
        return company;
    }
    
    /**
     * 生成随机文章数据
     */
    public static Map<String, Object> generatePost() {
        return generatePost(null);
    }
    
    /**
     * 生成带有指定用户ID的文章数据
     */
    public static Map<String, Object> generatePost(Integer userId) {
        String[] titleWords = {"Introduction", "Overview", "Analysis", "Implementation", "Best Practices", 
                              "Tutorial", "Guide", "Tips", "Strategies", "Solutions"};
        String[] topicWords = {"API Testing", "Automation", "REST", "Assured", "Testing", "Development", 
                              "Quality", "Performance", "Security", "Integration"};
        
        String title = titleWords[random.nextInt(titleWords.length)] + " to " + 
                       topicWords[random.nextInt(topicWords.length)];
        
        String[] bodyStarts = {"This article explores", "In this post, we discuss", "Let's dive into", 
                              "This tutorial covers", "Today we're looking at"};
        String[] bodyMiddles = {"the fundamental concepts of", "advanced techniques for", "best practices in", 
                               "practical applications of", "the latest trends in"};
        String[] bodyEnds = {"testing frameworks", "API automation", "REST services", "quality assurance", 
                           "performance optimization"};
        
        String body = bodyStarts[random.nextInt(bodyStarts.length)] + " " + 
                      bodyMiddles[random.nextInt(bodyMiddles.length)] + " " + 
                      bodyEnds[random.nextInt(bodyEnds.length)] + ". " +
                      "We'll examine various approaches and provide practical examples that can be " +
                      "implemented in real-world scenarios. The goal is to help developers understand " +
                      "the importance of robust testing strategies and how to apply them effectively.";
        
        Map<String, Object> post = new HashMap<>();
        post.put("title", title);
        post.put("body", body);
        post.put("userId", userId != null ? userId : RandomUtils.nextInt(1, 11));
        
        return post;
    }
    
    /**
     * 生成随机评论数据
     */
    public static Map<String, Object> generateComment() {
        return generateComment(null);
    }
    
    /**
     * 生成带有指定文章ID的评论数据
     */
    public static Map<String, Object> generateComment(Integer postId) {
        String[] firstNames = {"Alex", "Sam", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Jamie"};
        String[] subjects = {"Great article", "Thanks for sharing", "Very helpful", "Good explanation", 
                            "Nice post", "Excellent content", "Well written", "Clear and concise"};
        
        String name = firstNames[random.nextInt(firstNames.length)] + " " + RandomStringUtils.randomAlphabetic(6);
        String email = name.toLowerCase().replace(" ", ".") + "@example.com";
        
        String[] bodyPhrases = {
            "This was exactly what I was looking for. The examples are clear and easy to follow.",
            "I appreciate the depth of explanation. It really helped me understand the concept better.",
            "Would you be able to elaborate more on the security aspects? That would be very helpful.",
            "I've implemented something similar and found that adding caching significantly improves performance.",
            "What tools do you recommend for monitoring API performance in production environments?"
        };
        
        String body = bodyPhrases[random.nextInt(bodyPhrases.length)];
        
        Map<String, Object> comment = new HashMap<>();
        comment.put("name", name);
        comment.put("email", email);
        comment.put("body", body);
        comment.put("postId", postId != null ? postId : RandomUtils.nextInt(1, 101));
        
        return comment;
    }
    
    /**
     * 生成随机待办事项数据
     */
    public static Map<String, Object> generateTodo() {
        return generateTodo(null);
    }
    
    /**
     * 生成带有指定用户ID的待办事项数据
     */
    public static Map<String, Object> generateTodo(Integer userId) {
        String[] taskStarts = {"Complete", "Review", "Update", "Implement", "Test", "Fix", "Design", "Document"};
        String[] taskMiddles = {"the API", "user interface", "test cases", "documentation", 
                               "security measures", "performance metrics", "data model", "error handling"};
        String[] taskEnds = {"for release", "before deadline", "according to requirements", 
                            "for client feedback", "before next sprint", "as planned", "following best practices"};
        
        String title = taskStarts[random.nextInt(taskStarts.length)] + " " + 
                      taskMiddles[random.nextInt(taskMiddles.length)] + " " + 
                      taskEnds[random.nextInt(taskEnds.length)];
        
        Map<String, Object> todo = new HashMap<>();
        todo.put("title", title);
        todo.put("completed", random.nextBoolean());
        todo.put("userId", userId != null ? userId : RandomUtils.nextInt(1, 11));
        
        return todo;
    }
    
    /**
     * 生成随机相册数据
     */
    public static Map<String, Object> generateAlbum() {
        return generateAlbum(null);
    }
    
    /**
     * 生成带有指定用户ID的相册数据
     */
    public static Map<String, Object> generateAlbum(Integer userId) {
        String[] albumTypes = {"Vacation", "Family", "Work", "Hobby", "Travel", "Events", "Projects", "Personal"};
        String[] albumDescriptors = {"Summer", "Winter", "Spring", "Fall", "Amazing", "Wonderful", "Beautiful", "Unforgettable"};
        
        String title = albumDescriptors[random.nextInt(albumDescriptors.length)] + " " + 
                      albumTypes[random.nextInt(albumTypes.length)] + " Photos";
        
        Map<String, Object> album = new HashMap<>();
        album.put("title", title);
        album.put("userId", userId != null ? userId : RandomUtils.nextInt(1, 11));
        
        return album;
    }
    
    /**
     * 生成随机照片数据
     */
    public static Map<String, Object> generatePhoto() {
        return generatePhoto(null);
    }
    
    /**
     * 生成带有指定相册ID的照片数据
     */
    public static Map<String, Object> generatePhoto(Integer albumId) {
        String[] photoSubjects = {"Sunset", "Mountain", "Ocean", "City", "Forest", "Beach", "Desert", "Lake"};
        String[] photoQualities = {"Amazing", "Breathtaking", "Stunning", "Beautiful", "Spectacular", "Impressive"};
        
        String title = photoQualities[random.nextInt(photoQualities.length)] + " " + 
                       photoSubjects[random.nextInt(photoSubjects.length)];
        
        String photoId = RandomStringUtils.randomNumeric(6);
        String thumbnailId = RandomStringUtils.randomNumeric(6);
        
        Map<String, Object> photo = new HashMap<>();
        photo.put("title", title);
        photo.put("url", "https://picsum.photos/id/" + photoId + "/600/400");
        photo.put("thumbnailUrl", "https://picsum.photos/id/" + thumbnailId + "/150/150");
        photo.put("albumId", albumId != null ? albumId : RandomUtils.nextInt(1, 51));
        
        return photo;
    }
    
    /**
     * 生成随机产品数据
     */
    public static Map<String, Object> generateProduct() {
        String[] adjectives = {"Premium", "Professional", "Advanced", "Basic", "Deluxe", "Standard", 
                              "Essential", "Ultimate", "Eco-friendly", "Smart"};
        String[] products = {"Laptop", "Phone", "Headphones", "Camera", "Watch", "Speaker", 
                           "Tablet", "Monitor", "Keyboard", "Mouse"};
        String[] editions = {"Pro", "Plus", "Max", "Lite", "X", "S", "SE", "Mini"};
        
        String category = PRODUCT_CATEGORIES[random.nextInt(PRODUCT_CATEGORIES.length)];
        String adjective = adjectives[random.nextInt(adjectives.length)];
        String product = products[random.nextInt(products.length)];
        String edition = editions[random.nextInt(editions.length)];
        
        String name = adjective + " " + product + " " + edition;
        String description = "High-quality " + product.toLowerCase() + " with advanced features and " +
                             "superior performance. Perfect for professionals and enthusiasts alike.";
        
        Map<String, Object> productMap = new HashMap<>();
        productMap.put("name", name);
        productMap.put("description", description);
        productMap.put("price", 9.99 + random.nextInt(9900) / 100.0);
        productMap.put("category", category);
        productMap.put("inStock", random.nextBoolean());
        productMap.put("rating", 1 + random.nextFloat() * 4);
        productMap.put("reviews", random.nextInt(500));
        
        return productMap;
    }
    
    /**
     * 生成随机订单数据
     */
    public static Map<String, Object> generateOrder() {
        int userId = RandomUtils.nextInt(1, 11);
        String orderDate = String.format("%04d-%02d-%02d", 
                                        2020 + random.nextInt(3), 
                                        1 + random.nextInt(12), 
                                        1 + random.nextInt(28));
        
        String[] statuses = {"pending", "processing", "shipped", "delivered", "cancelled"};
        String status = statuses[random.nextInt(statuses.length)];
        
        // 生成1-5个订单项
        List<Map<String, Object>> items = new ArrayList<>();
        int itemCount = 1 + random.nextInt(5);
        for (int i = 0; i < itemCount; i++) {
            Map<String, Object> item = new HashMap<>();
            item.put("productId", 1 + random.nextInt(100));
            item.put("productName", generateProduct().get("name"));
            item.put("quantity", 1 + random.nextInt(5));
            item.put("price", 9.99 + random.nextInt(9900) / 100.0);
            items.add(item);
        }
        
        // 计算订单总额
        double total = items.stream()
            .mapToDouble(item -> ((Double) item.get("price")) * ((Integer) item.get("quantity")))
            .sum();
        
        Map<String, Object> order = new HashMap<>();
        order.put("userId", userId);
        order.put("orderDate", orderDate);
        order.put("status", status);
        order.put("items", items);
        order.put("total", Math.round(total * 100.0) / 100.0);
        
        return order;
    }
    
    /**
     * 生成随机字符串
     */
    public static String randomString(int length) {
        return RandomStringUtils.randomAlphabetic(length);
    }
    
    /**
     * 生成随机数字字符串
     */
    public static String randomNumeric(int length) {
        return RandomStringUtils.randomNumeric(length);
    }
    
    /**
     * 生成随机字母数字字符串
     */
    public static String randomAlphanumeric(int length) {
        return RandomStringUtils.randomAlphanumeric(length);
    }
    
    /**
     * 生成随机UUID
     */
    public static String randomUUID() {
        return UUID.randomUUID().toString();
    }
    
    /**
     * 生成随机日期
     */
    public static String randomDate() {
        int year = 2020 + random.nextInt(3);
        int month = 1 + random.nextInt(12);
        int day = 1 + random.nextInt(28);
        return String.format("%04d-%02d-%02d", year, month, day);
    }
    
    /**
     * 生成随机时间戳
     */
    public static long randomTimestamp() {
        long currentTime = System.currentTimeMillis();
        long oneYearInMillis = 365L * 24 * 60 * 60 * 1000;
        return currentTime - random.nextInt((int) oneYearInMillis);
    }
    
    /**
     * 生成指定范围的随机整数
     */
    public static int randomInt(int min, int max) {
        return RandomUtils.nextInt(min, max + 1);
    }
    
    /**
     * 生成指定范围的随机浮点数
     */
    public static double randomDouble(double min, double max) {
        return min + random.nextDouble() * (max - min);
    }
    
    /**
     * 从给定数组中随机选择一个元素
     */
    public static <T> T randomChoice(T[] array) {
        return array[random.nextInt(array.length)];
    }
    
    /**
     * 从给定列表中随机选择一个元素
     */
    public static <T> T randomChoice(List<T> list) {
        return list.get(random.nextInt(list.size()));
    }
    
    /**
     * 将对象转换为JSON字符串
     */
    public static String toJson(Object obj) {
        try {
            return objectMapper.writeValueAsString(obj);
        } catch (Exception e) {
            throw new RuntimeException("Failed to convert object to JSON", e);
        }
    }
    
    /**
     * 注册自定义数据生成器
     */
    public static <T> void registerCustomGenerator(String name, Supplier<T> generator) {
        CustomGenerators.registerGenerator(name, generator);
    }
    
    /**
     * 使用自定义生成器生成数据
     */
    public static Object generateCustom(String name) {
        return CustomGenerators.generate(name);
    }
    
    /**
     * 自定义生成器注册表
     */
    private static class CustomGenerators {
        private static final Map<String, Supplier<?>> generators = new HashMap<>();
        
        static <T> void registerGenerator(String name, Supplier<T> generator) {
            generators.put(name, generator);
        }
        
        static Object generate(String name) {
            Supplier<?> generator = generators.get(name);
            if (generator == null) {
                throw new IllegalArgumentException("No custom generator registered for: " + name);
            }
            return generator.get();
        }
    }
}