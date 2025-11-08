package com.example.restassured.integration;

import com.example.restassured.framework.BaseApiTest;
import com.example.restassured.framework.TestDataManager;
import io.restassured.http.ContentType;
import io.restassured.response.Response;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.TestMethodOrder;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static io.restassured.RestAssured.given;
import static org.hamcrest.CoreMatchers.*;
import static org.hamcrest.Matchers.emptyOrNullString;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.collection.IsMapContaining.hasKey;
import static org.hamcrest.Matchers.greaterThan;

/**
 * JSONPlaceholder API集成测试
 * 使用完整的CRUD操作测试JSONPlaceholder API
 */
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class JsonPlaceholderApiTest extends BaseApiTest {
    
    private Integer createdPostId;
    private Integer createdCommentId;
    private Integer createdTodoId;
    private Integer createdUserId;
    
    @Test
    @Order(1)
    @DisplayName("获取所有用户")
    public void testGetAllUsers() {
        Response response = given()
            .spec(requestSpec)
        .when()
            .get("/users")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .extract()
            .response();
        
        // 验证用户数组不为空
        List<Map<String, Object>> users = response.jsonPath().getList("$");
        org.hamcrest.MatcherAssert.assertThat("Users list should not be empty", users.size(), greaterThan(0));
        
        // 验证第一个用户包含必要字段
        Map<String, Object> firstUser = users.get(0);
        org.hamcrest.MatcherAssert.assertThat(firstUser, hasKey("id"));
        org.hamcrest.MatcherAssert.assertThat(firstUser, hasKey("name"));
        org.hamcrest.MatcherAssert.assertThat(firstUser, hasKey("username"));
        org.hamcrest.MatcherAssert.assertThat(firstUser, hasKey("email"));
        org.hamcrest.MatcherAssert.assertThat(firstUser, hasKey("address"));
        org.hamcrest.MatcherAssert.assertThat(firstUser, hasKey("phone"));
        org.hamcrest.MatcherAssert.assertThat(firstUser, hasKey("website"));
        org.hamcrest.MatcherAssert.assertThat(firstUser, hasKey("company"));
        
        // 存储用户ID供后续测试使用
        Integer firstUserId = response.jsonPath().getInt("[0].id");
        TestDataManager.storeData("testUserId", firstUserId);
    }
    
    @Test
    @Order(2)
    @DisplayName("获取特定用户")
    public void testGetSpecificUser() {
        Integer userId = TestDataManager.getData("testUserId", Integer.class);
        
        given()
            .spec(requestSpec)
            .pathParam("id", userId)
        .when()
            .get("/users/{id}")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("id", equalTo(userId))
            .body("name", not(emptyOrNullString()))
            .body("username", not(emptyOrNullString()))
            .body("email", not(emptyOrNullString()))
            .body("address", notNullValue())
            .body("address.street", not(emptyOrNullString()))
            .body("address.city", not(emptyOrNullString()))
            .body("address.zipcode", not(emptyOrNullString()))
            .body("address.geo", notNullValue())
            .body("address.geo.lat", not(emptyOrNullString()))
            .body("address.geo.lng", not(emptyOrNullString()))
            .body("phone", not(emptyOrNullString()))
            .body("website", not(emptyOrNullString()))
            .body("company", notNullValue())
            .body("company.name", not(emptyOrNullString()));
    }
    
    @Test
    @Order(3)
    @DisplayName("创建新用户")
    public void testCreateUser() {
        Map<String, Object> newUser = TestDataManager.createTestUser();
        
        Response response = given()
            .spec(requestSpec)
            .body(newUser)
        .when()
            .post("/users")
        .then()
            .statusCode(201)
            .contentType(ContentType.JSON)
            .body("name", equalTo(newUser.get("name")))
            .body("username", equalTo(newUser.get("username")))
            .body("email", equalTo(newUser.get("email")))
            .body("phone", equalTo(newUser.get("phone")))
            .body("website", equalTo(newUser.get("website")))
            .body("$", hasKey("id"))
            .extract()
            .response();
        
        // 存储创建的用户ID
        createdUserId = response.jsonPath().getInt("id");
        TestDataManager.storeData("createdUserId", createdUserId);
    }
    
    @Test
    @Order(4)
    @DisplayName("更新用户信息")
    public void testUpdateUser() {
        Integer userId = TestDataManager.getData("testUserId", Integer.class);
        
        // 准备更新数据
        Map<String, Object> updateData = new HashMap<>();
        updateData.put("name", "Updated User Name");
        updateData.put("email", "updated.email@example.com");
        updateData.put("phone", "555-UPDATED");
        
        given()
            .spec(requestSpec)
            .pathParam("id", userId)
            .body(updateData)
        .when()
            .put("/users/{id}")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("id", equalTo(userId))
            .body("name", equalTo(updateData.get("name")))
            .body("email", equalTo(updateData.get("email")))
            .body("phone", equalTo(updateData.get("phone")));
    }
    
    @Test
    @Order(5)
    @DisplayName("部分更新用户信息")
    public void testPatchUser() {
        Integer userId = TestDataManager.getData("testUserId", Integer.class);
        
        // 准备部分更新数据
        Map<String, Object> patchData = new HashMap<>();
        patchData.put("name", "Partially Updated User");
        
        given()
            .spec(requestSpec)
            .pathParam("id", userId)
            .body(patchData)
        .when()
            .patch("/users/{id}")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("id", equalTo(userId))
            .body("name", equalTo(patchData.get("name")));
    }
    
    @Test
    @Order(6)
    @DisplayName("获取所有文章")
    public void testGetAllPosts() {
        Response response = given()
            .spec(requestSpec)
        .when()
            .get("/posts")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .extract()
            .response();
        
        // 验证文章数组不为空
        List<Map<String, Object>> posts = response.jsonPath().getList("$");
        org.hamcrest.MatcherAssert.assertThat("Posts list should not be empty", posts.size(), greaterThan(0));
        
        // 验证第一篇文章包含必要字段
        Map<String, Object> firstPost = posts.get(0);
        org.hamcrest.MatcherAssert.assertThat(firstPost, hasKey("id"));
        org.hamcrest.MatcherAssert.assertThat(firstPost, hasKey("userId"));
        org.hamcrest.MatcherAssert.assertThat(firstPost, hasKey("title"));
        org.hamcrest.MatcherAssert.assertThat(firstPost, hasKey("body"));
    }
    
    @Test
    @Order(7)
    @DisplayName("获取特定用户的文章")
    public void testGetPostsByUser() {
        Integer userId = TestDataManager.getData("testUserId", Integer.class);
        
        given()
            .spec(requestSpec)
            .queryParam("userId", userId)
        .when()
            .get("/posts")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("userId", everyItem(equalTo(userId)));
    }
    
    @Test
    @Order(8)
    @DisplayName("创建新文章")
    public void testCreatePost() {
        Integer userId = TestDataManager.getData("testUserId", Integer.class);
        Map<String, Object> newPost = TestDataManager.createTestPost(userId);
        
        Response response = given()
            .spec(requestSpec)
            .body(newPost)
        .when()
            .post("/posts")
        .then()
            .statusCode(201)
            .contentType(ContentType.JSON)
            .body("title", equalTo(newPost.get("title")))
            .body("body", equalTo(newPost.get("body")))
            .body("userId", equalTo(newPost.get("userId")))
            .body("$", hasKey("id"))
            .extract()
            .response();
        
        // 存储创建的文章ID
        createdPostId = response.jsonPath().getInt("id");
        TestDataManager.storeData("createdPostId", createdPostId);
    }
    
    @Test
    @Order(9)
    @DisplayName("获取特定文章")
    public void testGetSpecificPost() {
        Integer postId = TestDataManager.getData("createdPostId", Integer.class);
        
        given()
            .spec(requestSpec)
            .pathParam("id", postId)
        .when()
            .get("/posts/{id}")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("id", equalTo(postId))
            .body("title", not(emptyOrNullString()))
            .body("body", not(emptyOrNullString()))
            .body("$", hasKey("userId"));
    }
    
    @Test
    @Order(10)
    @DisplayName("获取文章评论")
    public void testGetPostComments() {
        Integer postId = TestDataManager.getData("createdPostId", Integer.class);
        
        given()
            .spec(requestSpec)
            .pathParam("postId", postId)
        .when()
            .get("/posts/{postId}/comments")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("postId", everyItem(equalTo(postId)));
    }
    
    @Test
    @Order(11)
    @DisplayName("创建新评论")
    public void testCreateComment() {
        Integer postId = TestDataManager.getData("createdPostId", Integer.class);
        Map<String, Object> newComment = TestDataManager.createTestComment(postId);
        
        Response response = given()
            .spec(requestSpec)
            .body(newComment)
        .when()
            .post("/comments")
        .then()
            .statusCode(201)
            .contentType(ContentType.JSON)
            .body("name", equalTo(newComment.get("name")))
            .body("email", equalTo(newComment.get("email")))
            .body("body", equalTo(newComment.get("body")))
            .body("postId", equalTo(newComment.get("postId")))
            .body("$", hasKey("id"))
            .extract()
            .response();
        
        // 存储创建的评论ID
        createdCommentId = response.jsonPath().getInt("id");
        TestDataManager.storeData("createdCommentId", createdCommentId);
    }
    
    @Test
    @Order(12)
    @DisplayName("获取所有待办事项")
    public void testGetAllTodos() {
        Response response = given()
            .spec(requestSpec)
        .when()
            .get("/todos")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .extract()
            .response();
        
        // 验证待办事项数组不为空
        List<Map<String, Object>> todos = response.jsonPath().getList("$");
        org.hamcrest.MatcherAssert.assertThat("Todos list should not be empty", todos.size(), greaterThan(0));
        
        // 验证第一个待办事项包含必要字段
        Map<String, Object> firstTodo = todos.get(0);
        org.hamcrest.MatcherAssert.assertThat(firstTodo, hasKey("id"));
        org.hamcrest.MatcherAssert.assertThat(firstTodo, hasKey("userId"));
        org.hamcrest.MatcherAssert.assertThat(firstTodo, hasKey("title"));
        org.hamcrest.MatcherAssert.assertThat(firstTodo, hasKey("completed"));
    }
    
    @Test
    @Order(13)
    @DisplayName("获取特定用户的待办事项")
    public void testGetTodosByUser() {
        Integer userId = TestDataManager.getData("testUserId", Integer.class);
        
        given()
            .spec(requestSpec)
            .queryParam("userId", userId)
        .when()
            .get("/todos")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("userId", everyItem(equalTo(userId)));
    }
    
    @Test
    @Order(14)
    @DisplayName("创建新待办事项")
    public void testCreateTodo() {
        Integer userId = TestDataManager.getData("testUserId", Integer.class);
        Map<String, Object> newTodo = TestDataManager.createTestTodo(userId);
        
        Response response = given()
            .spec(requestSpec)
            .body(newTodo)
        .when()
            .post("/todos")
        .then()
            .statusCode(201)
            .contentType(ContentType.JSON)
            .body("title", equalTo(newTodo.get("title")))
            .body("completed", equalTo(newTodo.get("completed")))
            .body("userId", equalTo(newTodo.get("userId")))
            .body("$", hasKey("id"))
            .extract()
            .response();
        
        // 存储创建的待办事项ID
        createdTodoId = response.jsonPath().getInt("id");
        TestDataManager.storeData("createdTodoId", createdTodoId);
    }
    
    @Test
    @Order(15)
    @DisplayName("更新待办事项状态")
    public void testUpdateTodoStatus() {
        Integer todoId = TestDataManager.getData("createdTodoId", Integer.class);
        
        // 准备更新数据
        Map<String, Object> updateData = new HashMap<>();
        updateData.put("completed", true);
        updateData.put("title", "Updated Todo Title");
        
        given()
            .spec(requestSpec)
            .pathParam("id", todoId)
            .body(updateData)
        .when()
            .put("/todos/{id}")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("id", equalTo(todoId))
            .body("completed", equalTo(updateData.get("completed")))
            .body("title", equalTo(updateData.get("title")));
    }
    
    @Test
    @Order(16)
    @DisplayName("删除创建的文章")
    public void testDeletePost() {
        Integer postId = TestDataManager.getData("createdPostId", Integer.class);
        
        given()
            .spec(requestSpec)
            .pathParam("id", postId)
        .when()
            .delete("/posts/{id}")
        .then()
            .statusCode(200)
            .body(isEmptyOrNullString());
    }
    
    @Test
    @Order(17)
    @DisplayName("删除创建的评论")
    public void testDeleteComment() {
        Integer commentId = TestDataManager.getData("createdCommentId", Integer.class);
        
        given()
            .spec(requestSpec)
            .pathParam("id", commentId)
        .when()
            .delete("/comments/{id}")
        .then()
            .statusCode(200)
            .body(isEmptyOrNullString());
    }
    
    @Test
    @Order(18)
    @DisplayName("删除创建的待办事项")
    public void testDeleteTodo() {
        Integer todoId = TestDataManager.getData("createdTodoId", Integer.class);
        
        given()
            .spec(requestSpec)
            .pathParam("id", todoId)
        .when()
            .delete("/todos/{id}")
        .then()
            .statusCode(200)
            .body(isEmptyOrNullString());
    }
    
    @Test
    @Order(19)
    @DisplayName("删除创建的用户")
    public void testDeleteUser() {
        Integer userId = TestDataManager.getData("createdUserId", Integer.class);
        
        if (userId != null) {
            given()
                .spec(requestSpec)
                .pathParam("id", userId)
            .when()
                .delete("/users/{id}")
            .then()
                .statusCode(200)
                .body(isEmptyOrNullString());
        }
    }
    
    @Test
    @Order(20)
    @DisplayName("验证不存在的资源")
    public void testNonExistentResource() {
        // 测试获取不存在的用户
        given()
            .spec(requestSpec)
            .pathParam("id", 99999)
        .when()
            .get("/users/{id}")
        .then()
            .statusCode(404)
            .body(isEmptyOrNullString());
        
        // 测试获取不存在的文章
        given()
            .spec(requestSpec)
            .pathParam("id", 99999)
        .when()
            .get("/posts/{id}")
        .then()
            .statusCode(404)
            .body(isEmptyOrNullString());
    }
}