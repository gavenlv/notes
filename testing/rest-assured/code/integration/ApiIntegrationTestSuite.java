package com.example.restassured.integration;

import com.example.restassured.framework.BaseApiTest;
import io.restassured.response.Response;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.OrderAnnotation;

import java.util.HashMap;
import java.util.Map;

import static io.restassured.RestAssured.given;
import static org.hamcrest.CoreMatchers.*;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.collection.IsMapContaining.hasKey;

/**
 * API集成测试套件
 * 模拟真实场景的API测试，包括完整的CRUD操作流程
 */
@TestMethodOrder(OrderAnnotation.class)
public class ApiIntegrationTestSuite extends BaseApiTest {
    
    private static int createdUserId;
    private static int createdPostId;
    private static int createdCommentId;
    private static int createdAlbumId;
    private static int createdPhotoId;
    private static int createdTodoId;
    
    @Test
    @Order(1)
    @DisplayName("步骤1: 创建用户并验证")
    public void createUserAndVerify() {
        Map<String, Object> newUser = new HashMap<>();
        newUser.put("name", "Integration Test User");
        newUser.put("username", "integrationtest_" + System.currentTimeMillis());
        newUser.put("email", "integration.test@example.com");
        newUser.put("phone", "555-123-4567");
        
        Map<String, Object> address = new HashMap<>();
        address.put("street", "123 Test Street");
        address.put("suite", "Apt. 456");
        address.put("city", "Test City");
        address.put("zipcode", "12345");
        
        Map<String, String> geo = new HashMap<>();
        geo.put("lat", "40.7128");
        geo.put("lng", "-74.0060");
        address.put("geo", geo);
        
        newUser.put("address", address);
        
        Map<String, Object> company = new HashMap<>();
        company.put("name", "Test Company Inc.");
        company.put("catchPhrase", "Testing the boundaries of API integration");
        company.put("bs", "synergize seamless partnerships");
        newUser.put("company", company);
        
        // 创建用户
        Response createResponse = given()
            .spec(requestSpec)
            .body(newUser)
        .when()
            .post("/users")
        .then()
            .statusCode(201)
            .contentType("application/json")
            .body("name", equalTo(newUser.get("name")))
            .body("username", equalTo(newUser.get("username")))
            .body("email", equalTo(newUser.get("email")))
            .body("address.street", equalTo(newUser.get("address").toString()))
            .extract()
            .response();
        
        // 获取创建的用户ID
        createdUserId = createResponse.jsonPath().getInt("id");
        
        // 验证用户创建成功
        given()
            .spec(requestSpec)
            .pathParam("id", createdUserId)
        .when()
            .get("/users/{id}")
        .then()
            .statusCode(200)
            .body("id", equalTo(createdUserId))
            .body("name", equalTo(newUser.get("name")))
            .body("username", equalTo(newUser.get("username")))
            .body("email", equalTo(newUser.get("email")));
    }
    
    @Test
    @Order(2)
    @DisplayName("步骤2: 为用户创建文章并验证")
    public void createPostForUserAndVerify() {
        Map<String, Object> newPost = new HashMap<>();
        newPost.put("title", "Integration Test: API Testing Best Practices");
        newPost.put("body", "In this article, we explore the best practices for API testing using REST Assured. We'll cover various aspects including authentication, request building, response validation, and advanced testing techniques.");
        newPost.put("userId", createdUserId);
        
        // 创建文章
        Response createResponse = given()
            .spec(requestSpec)
            .body(newPost)
        .when()
            .post("/posts")
        .then()
            .statusCode(201)
            .contentType("application/json")
            .body("title", equalTo(newPost.get("title")))
            .body("body", equalTo(newPost.get("body")))
            .body("userId", equalTo(newPost.get("userId")))
            .extract()
            .response();
        
        // 获取创建的文章ID
        createdPostId = createResponse.jsonPath().getInt("id");
        
        // 验证文章创建成功
        given()
            .spec(requestSpec)
            .pathParam("id", createdPostId)
        .when()
            .get("/posts/{id}")
        .then()
            .statusCode(200)
            .body("id", equalTo(createdPostId))
            .body("title", equalTo(newPost.get("title")))
            .body("userId", equalTo(createdUserId));
    }
    
    @Test
    @Order(3)
    @DisplayName("步骤3: 为文章添加评论并验证")
    public void addCommentToPostAndVerify() {
        Map<String, Object> newComment = new HashMap<>();
        newComment.put("name", "API Tester");
        newComment.put("email", "tester@example.com");
        newComment.put("body", "Great article on API testing! The examples provided are very helpful and the explanations are clear. Looking forward to more content on advanced testing techniques.");
        newComment.put("postId", createdPostId);
        
        // 创建评论
        Response createResponse = given()
            .spec(requestSpec)
            .body(newComment)
        .when()
            .post("/comments")
        .then()
            .statusCode(201)
            .contentType("application/json")
            .body("name", equalTo(newComment.get("name")))
            .body("email", equalTo(newComment.get("email")))
            .body("body", equalTo(newComment.get("body")))
            .body("postId", equalTo(newComment.get("postId")))
            .extract()
            .response();
        
        // 获取创建的评论ID
        createdCommentId = createResponse.jsonPath().getInt("id");
        
        // 验证评论创建成功
        given()
            .spec(requestSpec)
            .pathParam("id", createdCommentId)
        .when()
            .get("/comments/{id}")
        .then()
            .statusCode(200)
            .body("id", equalTo(createdCommentId))
            .body("postId", equalTo(createdPostId));
    }
    
    @Test
    @Order(4)
    @DisplayName("步骤4: 为用户创建相册并验证")
    public void createAlbumForUserAndVerify() {
        Map<String, Object> newAlbum = new HashMap<>();
        newAlbum.put("title", "API Testing Screenshots");
        newAlbum.put("userId", createdUserId);
        
        // 创建相册
        Response createResponse = given()
            .spec(requestSpec)
            .body(newAlbum)
        .when()
            .post("/albums")
        .then()
            .statusCode(201)
            .contentType("application/json")
            .body("title", equalTo(newAlbum.get("title")))
            .body("userId", equalTo(newAlbum.get("userId")))
            .extract()
            .response();
        
        // 获取创建的相册ID
        createdAlbumId = createResponse.jsonPath().getInt("id");
        
        // 验证相册创建成功
        given()
            .spec(requestSpec)
            .pathParam("id", createdAlbumId)
        .when()
            .get("/albums/{id}")
        .then()
            .statusCode(200)
            .body("id", equalTo(createdAlbumId))
            .body("title", equalTo(newAlbum.get("title")))
            .body("userId", equalTo(createdUserId));
    }
    
    @Test
    @Order(5)
    @DisplayName("步骤5: 为相册添加照片并验证")
    public void addPhotoToAlbumAndVerify() {
        Map<String, Object> newPhoto = new HashMap<>();
        newPhoto.put("title", "API Test Execution Screenshot");
        newPhoto.put("url", "https://picsum.photos/id/1/600/400");
        newPhoto.put("thumbnailUrl", "https://picsum.photos/id/1/150/150");
        newPhoto.put("albumId", createdAlbumId);
        
        // 创建照片
        Response createResponse = given()
            .spec(requestSpec)
            .body(newPhoto)
        .when()
            .post("/photos")
        .then()
            .statusCode(201)
            .contentType("application/json")
            .body("title", equalTo(newPhoto.get("title")))
            .body("url", equalTo(newPhoto.get("url")))
            .body("albumId", equalTo(newPhoto.get("albumId")))
            .extract()
            .response();
        
        // 获取创建的照片ID
        createdPhotoId = createResponse.jsonPath().getInt("id");
        
        // 验证照片创建成功
        given()
            .spec(requestSpec)
            .pathParam("id", createdPhotoId)
        .when()
            .get("/photos/{id}")
        .then()
            .statusCode(200)
            .body("id", equalTo(createdPhotoId))
            .body("albumId", equalTo(createdAlbumId));
    }
    
    @Test
    @Order(6)
    @DisplayName("步骤6: 为用户创建待办事项并验证")
    public void createTodoForUserAndVerify() {
        Map<String, Object> newTodo = new HashMap<>();
        newTodo.put("title", "Complete API integration testing");
        newTodo.put("completed", false);
        newTodo.put("userId", createdUserId);
        
        // 创建待办事项
        Response createResponse = given()
            .spec(requestSpec)
            .body(newTodo)
        .when()
            .post("/todos")
        .then()
            .statusCode(201)
            .contentType("application/json")
            .body("title", equalTo(newTodo.get("title")))
            .body("completed", equalTo(newTodo.get("completed")))
            .body("userId", equalTo(newTodo.get("userId")))
            .extract()
            .response();
        
        // 获取创建的待办事项ID
        createdTodoId = createResponse.jsonPath().getInt("id");
        
        // 验证待办事项创建成功
        given()
            .spec(requestSpec)
            .pathParam("id", createdTodoId)
        .when()
            .get("/todos/{id}")
        .then()
            .statusCode(200)
            .body("id", equalTo(createdTodoId))
            .body("title", equalTo(newTodo.get("title")))
            .body("userId", equalTo(createdUserId));
    }
    
    @Test
    @Order(7)
    @DisplayName("步骤7: 验证用户的所有资源")
    public void verifyAllUserResources() {
        // 验证用户信息
        given()
            .spec(requestSpec)
            .pathParam("id", createdUserId)
        .when()
            .get("/users/{id}")
        .then()
            .statusCode(200)
            .body("id", equalTo(createdUserId))
            .body("$", hasKey("name"))
            .body("$", hasKey("username"))
            .body("$", hasKey("email"))
            .body("$", hasKey("address"));
        
        // 验证用户的文章
        given()
            .spec(requestSpec)
            .queryParam("userId", createdUserId)
        .when()
            .get("/posts")
        .then()
            .statusCode(200)
            .body("userId", everyItem(equalTo(createdUserId)))
            .body("find { it.id == " + createdPostId + " }", notNullValue());
        
        // 验证用户的待办事项
        given()
            .spec(requestSpec)
            .queryParam("userId", createdUserId)
        .when()
            .get("/todos")
        .then()
            .statusCode(200)
            .body("userId", everyItem(equalTo(createdUserId)))
            .body("find { it.id == " + createdTodoId + " }", notNullValue());
        
        // 验证用户的相册
        given()
            .spec(requestSpec)
            .queryParam("userId", createdUserId)
        .when()
            .get("/albums")
        .then()
            .statusCode(200)
            .body("userId", everyItem(equalTo(createdUserId)))
            .body("find { it.id == " + createdAlbumId + " }", notNullValue());
        
        // 验证相册中的照片
        given()
            .spec(requestSpec)
            .pathParam("albumId", createdAlbumId)
        .when()
            .get("/albums/{albumId}/photos")
        .then()
            .statusCode(200)
            .body("albumId", everyItem(equalTo(createdAlbumId)))
            .body("find { it.id == " + createdPhotoId + " }", notNullValue());
        
        // 验证文章下的评论
        given()
            .spec(requestSpec)
            .pathParam("postId", createdPostId)
        .when()
            .get("/posts/{postId}/comments")
        .then()
            .statusCode(200)
            .body("postId", everyItem(equalTo(createdPostId)))
            .body("find { it.id == " + createdCommentId + " }", notNullValue());
    }
    
    @Test
    @Order(8)
    @DisplayName("步骤8: 更新待办事项状态并验证")
    public void updateTodoStatusAndVerify() {
        // 更新待办事项状态为已完成
        Map<String, Object> updateData = new HashMap<>();
        updateData.put("completed", true);
        updateData.put("title", "Completed API integration testing");
        
        given()
            .spec(requestSpec)
            .pathParam("id", createdTodoId)
            .body(updateData)
        .when()
            .put("/todos/{id}")
        .then()
            .statusCode(200)
            .contentType("application/json")
            .body("id", equalTo(createdTodoId))
            .body("completed", equalTo(true))
            .body("title", equalTo(updateData.get("title")))
            .body("userId", equalTo(createdUserId));
        
        // 验证更新成功
        given()
            .spec(requestSpec)
            .pathParam("id", createdTodoId)
        .when()
            .get("/todos/{id}")
        .then()
            .statusCode(200)
            .body("id", equalTo(createdTodoId))
            .body("completed", equalTo(true));
    }
    
    @Test
    @Order(9)
    @DisplayName("步骤9: 部分更新用户信息并验证")
    public void partiallyUpdateUserAndVerify() {
        // 部分更新用户信息
        Map<String, Object> patchData = new HashMap<>();
        patchData.put("name", "Updated Integration Test User");
        patchData.put("email", "updated.integration@example.com");
        
        given()
            .spec(requestSpec)
            .pathParam("id", createdUserId)
            .body(patchData)
        .when()
            .patch("/users/{id}")
        .then()
            .statusCode(200)
            .contentType("application/json")
            .body("id", equalTo(createdUserId))
            .body("name", equalTo(patchData.get("name")))
            .body("email", equalTo(patchData.get("email")));
        
        // 验证更新成功
        given()
            .spec(requestSpec)
            .pathParam("id", createdUserId)
        .when()
            .get("/users/{id}")
        .then()
            .statusCode(200)
            .body("id", equalTo(createdUserId))
            .body("name", equalTo(patchData.get("name")))
            .body("email", equalTo(patchData.get("email")));
    }
    
    @Test
    @Order(10)
    @DisplayName("步骤10: 清理所有创建的资源")
    public void cleanupAllCreatedResources() {
        // 删除创建的照片
        given()
            .spec(requestSpec)
            .pathParam("id", createdPhotoId)
        .when()
            .delete("/photos/{id}")
        .then()
            .statusCode(200);
        
        // 删除创建的相册
        given()
            .spec(requestSpec)
            .pathParam("id", createdAlbumId)
        .when()
            .delete("/albums/{id}")
        .then()
            .statusCode(200);
        
        // 删除创建的评论
        given()
            .spec(requestSpec)
            .pathParam("id", createdCommentId)
        .when()
            .delete("/comments/{id}")
        .then()
            .statusCode(200);
        
        // 删除创建的文章
        given()
            .spec(requestSpec)
            .pathParam("id", createdPostId)
        .when()
            .delete("/posts/{id}")
        .then()
            .statusCode(200);
        
        // 删除创建的待办事项
        given()
            .spec(requestSpec)
            .pathParam("id", createdTodoId)
        .when()
            .delete("/todos/{id}")
        .then()
            .statusCode(200);
        
        // 删除创建的用户
        given()
            .spec(requestSpec)
            .pathParam("id", createdUserId)
        .when()
            .delete("/users/{id}")
        .then()
            .statusCode(200);
    }
    
    @Test
    @Order(11)
    @DisplayName("步骤11: 验证资源清理成功")
    public void verifyResourceCleanup() {
        // 验证用户已删除
        given()
            .spec(requestSpec)
            .pathParam("id", createdUserId)
        .when()
            .get("/users/{id}")
        .then()
            .statusCode(404);
        
        // 验证文章已删除
        given()
            .spec(requestSpec)
            .pathParam("id", createdPostId)
        .when()
            .get("/posts/{id}")
        .then()
            .statusCode(404);
        
        // 验证评论已删除
        given()
            .spec(requestSpec)
            .pathParam("id", createdCommentId)
        .when()
            .get("/comments/{id}")
        .then()
            .statusCode(404);
        
        // 验证相册已删除
        given()
            .spec(requestSpec)
            .pathParam("id", createdAlbumId)
        .when()
            .get("/albums/{id}")
        .then()
            .statusCode(404);
        
        // 验证照片已删除
        given()
            .spec(requestSpec)
            .pathParam("id", createdPhotoId)
        .when()
            .get("/photos/{id}")
        .then()
            .statusCode(404);
        
        // 验证待办事项已删除
        given()
            .spec(requestSpec)
            .pathParam("id", createdTodoId)
        .when()
            .get("/todos/{id}")
        .then()
            .statusCode(404);
    }
}