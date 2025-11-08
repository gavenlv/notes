package com.example.restassured.integration;

import com.example.restassured.framework.BaseApiTest;
import io.restassured.http.ContentType;
import io.restassured.response.Response;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static io.restassured.RestAssured.given;
import static org.hamcrest.CoreMatchers.*;
import static org.hamcrest.Matchers.hasKey;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.collection.IsMapContaining.hasEntry;

/**
 * GitHub API集成测试
 * 使用真实的GitHub API端点进行测试
 * 注意：实际运行时请确保GitHub API访问限制
 */
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
public class GitHubApiTest extends BaseApiTest {
    
    private static final String GITHUB_API_BASE = "https://api.github.com";
    private static String accessToken;
    
    @BeforeAll
    public static void setUpGitHubApi() {
        // 设置GitHub API基础URI
        RestAssured.baseURI = GITHUB_API_BASE;
        
        // 从系统属性或环境变量获取访问令牌（可选）
        accessToken = System.getProperty("github.token", System.getenv().getOrDefault("GITHUB_TOKEN", ""));
        
        // 如果有访问令牌，使用OAuth2认证
        if (!accessToken.isEmpty()) {
            RestAssured.authentication = RestAssured.oauth2(accessToken);
        }
    }
    
    @Test
    @DisplayName("获取公共仓库信息")
    public void testGetPublicRepository() {
        given()
            .spec(requestSpec)
            .pathParam("owner", "octocat")
            .pathParam("repo", "Hello-World")
        .when()
            .get("/repos/{owner}/{repo}")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("name", equalTo("Hello-World"))
            .body("owner.login", equalTo("octocat"))
            .body("full_name", equalTo("octocat/Hello-World"))
            .body("private", is(false))
            .body("fork", is(false))
            .body("$", hasKey("id"))
            .body("$", hasKey("description"));
    }
    
    @Test
    @DisplayName("获取用户信息")
    public void testGetUserInformation() {
        given()
            .spec(requestSpec)
            .pathParam("username", "octocat")
        .when()
            .get("/users/{username}")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("login", equalTo("octocat"))
            .body("id", notNullValue())
            .body("type", equalTo("User"))
            .body("site_admin", is(false))
            .body("$", hasKey("name"))
            .body("$", hasKey("company"))
            .body("$", hasKey("blog"))
            .body("$", hasKey("location"))
            .body("$", hasKey("email"))
            .body("$", hasKey("public_repos"))
            .body("$", hasKey("followers"))
            .body("$", hasKey("following"));
    }
    
    @Test
    @DisplayName("获取用户仓库列表")
    public void testGetUserRepositories() {
        Response response = given()
            .spec(requestSpec)
            .pathParam("username", "octocat")
            .queryParam("type", "owner")
            .queryParam("sort", "updated")
            .queryParam("per_page", 10)
        .when()
            .get("/users/{username}/repos")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .extract()
            .response();
        
        // 验证响应是数组
        List<Map<String, Object>> repos = response.jsonPath().getList("$");
        
        // 验证每个仓库都包含必要字段
        for (Map<String, Object> repo : repos) {
            org.hamcrest.MatcherAssert.assertThat(repo, hasKey("id"));
            org.hamcrest.MatcherAssert.assertThat(repo, hasKey("name"));
            org.hamcrest.MatcherAssert.assertThat(repo, hasKey("full_name"));
            org.hamcrest.MatcherAssert.assertThat(repo, hasKey("owner"));
            org.hamcrest.MatcherAssert.assertThat(repo, hasKey("private"));
            org.hamcrest.MatcherAssert.assertThat(repo, hasKey("html_url"));
            org.hamcrest.MatcherAssert.assertThat(repo, hasKey("description"));
            org.hamcrest.MatcherAssert.assertThat(repo, hasKey("fork"));
            org.hamcrest.MatcherAssert.assertThat(repo, hasKey("url"));
        }
    }
    
    @Test
    @DisplayName("搜索仓库")
    public void testSearchRepositories() {
        given()
            .spec(requestSpec)
            .queryParam("q", "language:java stars:>1000")
            .queryParam("sort", "stars")
            .queryParam("order", "desc")
        .when()
            .get("/search/repositories")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("total_count", greaterThan(0))
            .body("items", notNullValue())
            .body("items[0].id", notNullValue())
            .body("items[0].name", notNullValue())
            .body("items[0].full_name", notNullValue())
            .body("items[0].owner", notNullValue())
            .body("items[0].owner.login", notNullValue())
            .body("items[0].stargazers_count", greaterThan(1000));
    }
    
    @Test
    @DisplayName("获取仓库提交历史")
    public void testGetRepositoryCommits() {
        given()
            .spec(requestSpec)
            .pathParam("owner", "octocat")
            .pathParam("repo", "Hello-World")
        .when()
            .get("/repos/{owner}/{repo}/commits")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("$", notNullValue())
            .body("[0].sha", notNullValue())
            .body("[0].commit", notNullValue())
            .body("[0].commit.author", notNullValue())
            .body("[0].commit.message", notNullValue())
            .body("[0].html_url", notNullValue());
    }
    
    @Test
    @DisplayName("获取仓库分支信息")
    public void testGetRepositoryBranches() {
        given()
            .spec(requestSpec)
            .pathParam("owner", "octocat")
            .pathParam("repo", "Hello-World")
        .when()
            .get("/repos/{owner}/{repo}/branches")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("$", notNullValue())
            .body("[0].name", notNullValue())
            .body("[0].commit", notNullValue())
            .body("[0].commit.sha", notNullValue())
            .body("[0].commit.url", notNullValue())
            .body("[0].protected", notNullValue());
    }
    
    @Test
    @DisplayName("获取仓库贡献者")
    public void testGetRepositoryContributors() {
        given()
            .spec(requestSpec)
            .pathParam("owner", "octocat")
            .pathParam("repo", "Hello-World")
        .when()
            .get("/repos/{owner}/{repo}/contributors")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("$", notNullValue())
            .body("[0].login", notNullValue())
            .body("[0].id", notNullValue())
            .body("[0].avatar_url", notNullValue())
            .body("[0].gravatar_id", notNullValue())
            .body("[0].url", notNullValue())
            .body("[0].html_url", notNullValue())
            .body("[0].contributions", greaterThan(0));
    }
    
    @ParameterizedTest
    @ValueSource(strings = {"octocat", "torvalds", "gaearon"})
    @DisplayName("参数化测试：获取不同用户信息")
    public void testGetDifferentUserInformation(String username) {
        given()
            .spec(requestSpec)
            .pathParam("username", username)
        .when()
            .get("/users/{username}")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("login", equalTo(username))
            .body("id", notNullValue())
            .body("type", equalTo("User"))
            .body("site_admin", notNullValue())
            .body("$", hasKey("public_repos"));
    }
    
    @Test
    @DisplayName("获取API速率限制信息")
    public void testGetRateLimit() {
        given()
            .spec(requestSpec)
        .when()
            .get("/rate_limit")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("$", hasKey("resources"))
            .body("resources", hasKey("core"))
            .body("resources", hasKey("search"))
            .body("resources", hasKey("graphql"))
            .body("resources.core", hasKey("limit"))
            .body("resources.core", hasKey("remaining"))
            .body("resources.core", hasKey("reset"));
    }
    
    @Test
    @DisplayName("获取仓库问题列表")
    public void testGetRepositoryIssues() {
        given()
            .spec(requestSpec)
            .pathParam("owner", "octocat")
            .pathParam("repo", "Hello-World")
            .queryParam("state", "open")
            .queryParam("sort", "created")
            .queryParam("direction", "desc")
        .when()
            .get("/repos/{owner}/{repo}/issues")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("$", notNullValue());
        
        // 如果仓库有开放问题，验证问题结构
        List<Map<String, Object>> issues = given()
            .spec(requestSpec)
            .pathParam("owner", "octocat")
            .pathParam("repo", "Hello-World")
            .queryParam("state", "open")
        .when()
            .get("/repos/{owner}/{repo}/issues")
        .then()
            .extract()
            .response()
            .jsonPath()
            .getList("$");
        
        if (!issues.isEmpty()) {
            Map<String, Object> firstIssue = issues.get(0);
            org.hamcrest.MatcherAssert.assertThat(firstIssue, hasKey("id"));
            org.hamcrest.MatcherAssert.assertThat(firstIssue, hasKey("number"));
            org.hamcrest.MatcherAssert.assertThat(firstIssue, hasKey("title"));
            org.hamcrest.MatcherAssert.assertThat(firstIssue, hasKey("user"));
            org.hamcrest.MatcherAssert.assertThat(firstIssue, hasKey("labels"));
            org.hamcrest.MatcherAssert.assertThat(firstIssue, hasKey("state"));
            org.hamcrest.MatcherAssert.assertThat(firstIssue, hasKey("created_at"));
            org.hamcrest.MatcherAssert.assertThat(firstIssue, hasKey("updated_at"));
        }
    }
    
    @Test
    @DisplayName("创建和删除仓库标记 - 需要认证")
    public void testCreateAndDeleteLabel() {
        // 如果没有访问令牌，跳过此测试
        if (accessToken.isEmpty()) {
            return;
        }
        
        // 创建一个测试标记
        Map<String, Object> label = new HashMap<>();
        label.put("name", "test-label-" + System.currentTimeMillis());
        label.put("color", "f29513");
        label.put("description", "A test label for API testing");
        
        // 创建标记
        Response createResponse = given()
            .spec(requestSpec)
            .pathParam("owner", "octocat")  // 注意：实际使用时需要替换为有权限的仓库
            .pathParam("repo", "Hello-World")
            .body(label)
        .when()
            .post("/repos/{owner}/{repo}/labels")
        .then()
            .extract()
            .response();
        
        // 如果创建成功，验证并删除
        if (createResponse.statusCode() == 201) {
            createResponse.then()
                .statusCode(201)
                .contentType(ContentType.JSON)
                .body("name", equalTo(label.get("name")))
                .body("color", equalTo(label.get("color")))
                .body("description", equalTo(label.get("description")));
            
            // 获取创建的标记名称
            String createdLabelName = createResponse.jsonPath().getString("name");
            
            // 删除标记
            given()
                .spec(requestSpec)
                .pathParam("owner", "octocat")  // 注意：实际使用时需要替换为有权限的仓库
                .pathParam("repo", "Hello-World")
                .pathParam("name", createdLabelName)
            .when()
                .delete("/repos/{owner}/{repo}/labels/{name}")
            .then()
                .statusCode(204);
        } else {
            // 如果创建失败（没有权限），跳过删除
            System.out.println("Skipping label deletion test due to lack of permissions");
        }
    }
}