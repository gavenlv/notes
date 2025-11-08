package com.example.restassured.basic;

import io.restassured.RestAssured;
import io.restassured.http.ContentType;
import org.junit.BeforeClass;
import org.junit.Test;

import static io.restassured.RestAssured.*;
import static io.restassured.matcher.RestAssuredMatchers.*;
import static org.hamcrest.Matchers.*;

/**
 * 简单API测试示例
 * 演示REST Assured的基础用法
 */
public class SimpleApiTest {
    
    @BeforeClass
    public static void setup() {
        // 配置基础URI和端口
        RestAssured.baseURI = "https://jsonplaceholder.typicode.com";
        RestAssured.port = 443;
        
        // 启用请求和响应日志（仅在验证失败时）
        RestAssured.enableLoggingOfRequestAndResponseIfValidationFails();
    }
    
    @Test
    public void testGetSingleUser() {
        given()
            .pathParam("userId", 1)
        .when()
            .get("/users/{userId}")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("id", equalTo(1))
            .body("name", notNullValue())
            .body("email", containsString("@"))
            .body("address.city", notNullValue())
            .body("company.name", notNullValue());
    }
    
    @Test
    public void testGetAllUsers() {
        when()
            .get("/users")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("size()", greaterThan(0))
            .body("[0].id", notNullValue())
            .body("[0].name", notNullValue())
            .body("[0].email", containsString("@"));
    }
    
    @Test
    public void testCreateNewPost() {
        String requestBody = "{\n" +
            "  \"title\": \"REST Assured Test\",\n" +
            "  \"body\": \"This is a test post created with REST Assured\",\n" +
            "  \"userId\": 1\n" +
            "}";
        
        given()
            .contentType(ContentType.JSON)
            .body(requestBody)
        .when()
            .post("/posts")
        .then()
            .statusCode(201)
            .contentType(ContentType.JSON)
            .body("title", equalTo("REST Assured Test"))
            .body("body", containsString("test post"))
            .body("userId", equalTo(1))
            .body("id", notNullValue());
    }
    
    @Test
    public void testUpdatePost() {
        // 首先创建一个帖子
        String createBody = "{\n" +
            "  \"title\": \"Original Title\",\n" +
            "  \"body\": \"Original body content\",\n" +
            "  \"userId\": 1\n" +
            "}";
        
        int postId = given()
            .contentType(ContentType.JSON)
            .body(createBody)
        .when()
            .post("/posts")
        .then()
            .statusCode(201)
            .extract()
            .path("id");
        
        // 更新帖子
        String updateBody = "{\n" +
            "  \"id\": " + postId + ",\n" +
            "  \"title\": \"Updated Title\",\n" +
            "  \"body\": \"Updated body content\",\n" +
            "  \"userId\": 1\n" +
            "}";
        
        given()
            .contentType(ContentType.JSON)
            .body(updateBody)
            .pathParam("postId", postId)
        .when()
            .put("/posts/{postId}")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("id", equalTo(postId))
            .body("title", equalTo("Updated Title"))
            .body("body", containsString("Updated"));
    }
    
    @Test
    public void testDeletePost() {
        // 首先创建一个帖子
        String createBody = "{\n" +
            "  \"title\": \"To Be Deleted\",\n" +
            "  \"body\": \"This post will be deleted\",\n" +
            "  \"userId\": 1\n" +
            "}";
        
        int postId = given()
            .contentType(ContentType.JSON)
            .body(createBody)
        .when()
            .post("/posts")
        .then()
            .statusCode(201)
            .extract()
            .path("id");
        
        // 删除帖子
        given()
            .pathParam("postId", postId)
        .when()
            .delete("/posts/{postId}")
        .then()
            .statusCode(200);
    }
    
    @Test
    public void testGetCommentsForPost() {
        given()
            .pathParam("postId", 1)
        .when()
            .get("/posts/{postId}/comments")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("size()", greaterThan(0))
            .body("[0].postId", equalTo(1))
            .body("[0].email", containsString("@"))
            .body("[0].name", notNullValue())
            .body("[0].body", notNullValue());
    }
    
    @Test
    public void testQueryParameters() {
        given()
            .queryParam("userId", 1)
        .when()
            .get("/posts")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("size()", greaterThan(0))
            .body("[0].userId", equalTo(1));
    }
    
    @Test
    public void testComplexJsonValidation() {
        when()
            .get("/users/1")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("id", equalTo(1))
            .body("name", both(notNullValue()).and(instanceOf(String.class)))
            .body("email", matchesPattern("[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}"))
            .body("address", hasKey("street"))
            .body("address", hasKey("city"))
            .body("address", hasKey("zipcode"))
            .body("company", hasKey("name"))
            .body("company", hasKey("catchPhrase"));
    }
}