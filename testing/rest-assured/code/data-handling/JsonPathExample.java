package com.example.restassured.datahandling;

import io.restassured.RestAssured;
import io.restassured.path.json.JsonPath;
import io.restassured.response.Response;
import org.junit.BeforeClass;
import org.junit.Test;

import java.util.List;
import java.util.Map;

import static io.restassured.RestAssured.*;
import static io.restassured.matcher.RestAssuredMatchers.*;
import static org.hamcrest.Matchers.*;

/**
 * JSONPath示例
 * 演示如何使用JSONPath解析和验证JSON响应
 */
public class JsonPathExample {
    
    @BeforeClass
    public static void setup() {
        RestAssured.baseURI = "https://jsonplaceholder.typicode.com";
        RestAssured.enableLoggingOfRequestAndResponseIfValidationFails();
    }
    
    @Test
    public void testBasicJsonPathExpressions() {
        Response response = get("/users");
        
        // 基本JSONPath表达式
        JsonPath jsonPath = response.jsonPath();
        
        // 获取整个数组
        List<Map<String, Object>> users = jsonPath.getList("$");
        System.out.println("Total users: " + users.size());
        
        // 获取所有用户的名称
        List<String> userNames = jsonPath.getList("name");
        System.out.println("User names: " + userNames);
        
        // 获取所有用户的邮箱
        List<String> userEmails = jsonPath.getList("email");
        System.out.println("User emails: " + userEmails);
        
        // 获取第一个用户
        Map<String, Object> firstUser = jsonPath.getMap("[0]");
        System.out.println("First user: " + firstUser);
        
        // 获取第一个用户的名称
        String firstName = jsonPath.getString("[0].name");
        System.out.println("First user name: " + firstName);
    }
    
    @Test
    public void testNestedJsonPathExpressions() {
        Response response = get("/users/1");
        JsonPath jsonPath = response.jsonPath();
        
        // 获取嵌套对象属性
        String street = jsonPath.getString("address.street");
        String city = jsonPath.getString("address.city");
        String zipcode = jsonPath.getString("address.zipcode");
        String companyName = jsonPath.getString("company.name");
        
        System.out.println("Address: " + street + ", " + city + ", " + zipcode);
        System.out.println("Company: " + companyName);
    }
    
    @Test
    public void testJsonPathWithValidation() {
        when()
            .get("/users")
        .then()
            .statusCode(200)
            // 使用JSONPath进行响应验证
            .body("$", hasSize(greaterThan(0)))
            .body("[0].id", notNullValue())
            .body("[0].name", notNullValue())
            .body("[0].email", containsString("@"))
            .body("[0].address.city", notNullValue())
            .body("[0].company.name", notNullValue());
    }
    
    @Test
    public void testJsonPathFiltering() {
        when()
            .get("/users")
        .then()
            .statusCode(200)
            // 使用Groovy GPath语法进行过滤
            .body("findAll { it.name.startsWith('C') }.size()", greaterThanOrEqualTo(0))
            .body("findAll { it.name.contains('e') }.size()", greaterThan(0))
            .body("findAll { it.email.contains('.biz') }.size()", greaterThanOrEqualTo(0));
    }
    
    @Test
    public void testJsonPathWithCalculations() {
        Response response = get("/posts");
        JsonPath jsonPath = response.jsonPath();
        
        // 计算文章总数
        int totalPosts = jsonPath.getInt("size()");
        System.out.println("Total posts: " + totalPosts);
        
        // 获取用户1的所有文章
        List<Map<String, Object>> user1Posts = jsonPath.getList("findAll { it.userId == 1 }");
        System.out.println("User 1 posts: " + user1Posts.size());
        
        // 获取所有用户的ID列表
        List<Integer> userIds = jsonPath.getList("userId");
        System.out.println("User IDs in posts: " + userIds);
        
        // 按用户ID分组
        Map<Integer, Integer> postsByUser = new java.util.HashMap<>();
        for (Integer userId : userIds) {
            postsByUser.put(userId, postsByUser.getOrDefault(userId, 0) + 1);
        }
        
        System.out.println("Posts by user: " + postsByUser);
    }
    
    @Test
    public void testComplexJsonPathQueries() {
        when()
            .get("/users")
        .then()
            .statusCode(200)
            // 复杂查询
            .body("collect { [name: it.name, domain: it.email.split('@')[1]] }", 
                everyItem(hasKey("name")))
            .body("collect { [name: it.name, domain: it.email.split('@')[1]] }", 
                everyItem(hasKey("domain")))
            .body("groupby { it.address.city }.collectEntries { k, v -> [k, v.size()] }", 
                notNullValue())
            .body("max { it.name.length() }.name", instanceOf(String.class));
    }
    
    @Test
    public void testJsonPathExtractAndReuse() {
        // 1. 获取所有用户
        Response usersResponse = get("/users");
        JsonPath usersJsonPath = usersResponse.jsonPath();
        
        // 2. 提取第一个用户的ID
        int firstUserId = usersJsonPath.getInt("[0].id");
        System.out.println("First user ID: " + firstUserId);
        
        // 3. 使用提取的ID获取用户详细信息
        Response userResponse = given()
            .pathParam("userId", firstUserId)
        .when()
            .get("/users/{userId}");
        
        // 4. 验证详细信息
        userResponse.then()
            .statusCode(200)
            .body("id", equalTo(firstUserId))
            .body("name", equalTo(usersJsonPath.getString("[0].name")))
            .body("email", equalTo(usersJsonPath.getString("[0].email")));
    }
    
    @Test
    public void testJsonPathValidationInSteps() {
        Response response = get("/users");
        JsonPath jsonPath = response.jsonPath();
        
        // 步骤1：验证响应不为空
        List<Map<String, Object>> users = jsonPath.getList("$");
        assertNotNull(users, "Users list should not be null");
        assertTrue(users.size() > 0, "Users list should not be empty");
        
        // 步骤2：验证每个用户都有必需字段
        for (int i = 0; i < users.size(); i++) {
            String name = jsonPath.getString("[" + i + "].name");
            String email = jsonPath.getString("[" + i + "].email");
            String street = jsonPath.getString("[" + i + "].address.street");
            String city = jsonPath.getString("[" + i + "].address.city");
            String companyName = jsonPath.getString("[" + i + "].company.name");
            
            assertNotNull(name, "User name should not be null for user at index " + i);
            assertNotNull(email, "User email should not be null for user at index " + i);
            assertTrue(email.contains("@"), "User email should be valid for user at index " + i);
            assertNotNull(street, "User street should not be null for user at index " + i);
            assertNotNull(city, "User city should not be null for user at index " + i);
            assertNotNull(companyName, "User company name should not be null for user at index " + i);
        }
    }
    
    @Test
    public void testJsonPathWithCustomValidation() {
        Response response = get("/users");
        JsonPath jsonPath = response.jsonPath();
        
        // 自定义验证：检查邮箱域名的分布
        List<String> emailDomains = jsonPath.getList("collect { it.email.split('@')[1] }");
        
        System.out.println("Email domains: " + emailDomains);
        
        // 统计每个域名的用户数量
        Map<String, Integer> domainCounts = new java.util.HashMap<>();
        for (String domain : emailDomains) {
            domainCounts.put(domain, domainCounts.getOrDefault(domain, 0) + 1);
        }
        
        System.out.println("Domain counts: " + domainCounts);
        
        // 验证至少有两个不同的域名
        assertTrue(domainCounts.size() >= 2, "Should have at least 2 different email domains");
        
        // 验证没有域名使用超过50%的用户
        int totalUsers = emailDomains.size();
        for (Map.Entry<String, Integer> entry : domainCounts.entrySet()) {
            float percentage = (float) entry.getValue() / totalUsers * 100;
            assertTrue(percentage <= 50, 
                "Domain " + entry.getKey() + " should not be used by more than 50% of users");
        }
    }
    
    @Test
    public void testJsonPathWithArraysAndMaps() {
        // 创建自定义JSON响应（用于演示）
        String customJson = "{\n" +
            "  \"products\": [\n" +
            "    {\"id\": 1, \"name\": \"Laptop\", \"price\": 999.99, \"tags\": [\"electronics\", \"computer\"]},\n" +
            "    {\"id\": 2, \"name\": \"Phone\", \"price\": 699.99, \"tags\": [\"electronics\", \"mobile\"]},\n" +
            "    {\"id\": 3, \"name\": \"Book\", \"price\": 19.99, \"tags\": [\"education\", \"paperback\"]}\n" +
            "  ],\n" +
            "  \"metadata\": {\n" +
            "    \"totalCount\": 3,\n" +
            "    \"categories\": [\"electronics\", \"education\"]\n" +
            "  }\n" +
            "}";
        
        JsonPath jsonPath = new JsonPath(customJson);
        
        // 获取所有产品
        List<Map<String, Object>> products = jsonPath.getList("products");
        assertEquals(3, products.size());
        
        // 获取电子产品
        List<Map<String, Object>> electronics = jsonPath.getList("products.findAll { it.tags.contains('electronics') }");
        assertEquals(2, electronics.size());
        
        // 获取元数据
        Map<String, Object> metadata = jsonPath.getMap("metadata");
        assertEquals(3, metadata.get("totalCount"));
        
        // 验证价格范围
        List<Double> prices = jsonPath.getList("products.collect { it.price }");
        assertTrue(prices.stream().anyMatch(p -> p > 500), "Should have at least one product over $500");
    }
}