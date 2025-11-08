package com.example.restassured.basic;

import io.restassured.RestAssured;
import io.restassured.http.ContentType;
import io.restassured.response.Response;
import org.junit.BeforeClass;
import org.junit.Test;

import java.util.HashMap;
import java.util.Map;

import static io.restassured.RestAssured.*;
import static io.restassured.matcher.RestAssuredMatchers.*;
import static org.hamcrest.Matchers.*;

/**
 * 认证测试示例
 * 演示REST Assured中的各种认证方式
 */
public class AuthenticationTest {
    
    @BeforeClass
    public static void setup() {
        // 配置基础URI
        RestAssured.baseURI = "https://httpbin.org";
        
        // 启用请求和响应日志（仅在验证失败时）
        RestAssured.enableLoggingOfRequestAndResponseIfValidationFails();
    }
    
    @Test
    public void testBasicAuthentication() {
        given()
            .auth().basic("user", "passwd")
        .when()
            .get("/basic-auth/user/passwd")
        .then()
            .statusCode(200)
            .body("authenticated", equalTo(true))
            .body("user", equalTo("user"));
    }
    
    @Test
    public void testBasicAuthenticationFailure() {
        given()
            .auth().basic("user", "wrongpass")
        .when()
            .get("/basic-auth/user/passwd")
        .then()
            .statusCode(401);
    }
    
    @Test
    public void testPreemptiveBasicAuthentication() {
        given()
            .auth().preemptive().basic("user", "passwd")
        .when()
            .get("/basic-auth/user/passwd")
        .then()
            .statusCode(200)
            .body("authenticated", equalTo(true))
            .body("user", equalTo("user"));
    }
    
    @Test
    public void testDigestAuthentication() {
        given()
            .auth().digest("user", "passwd")
        .when()
            .get("/digest-auth/auth/user/passwd")
        .then()
            .statusCode(200)
            .body("authenticated", equalTo(true))
            .body("user", equalTo("user"));
    }
    
    @Test
    public void testOAuth2BearerToken() {
        given()
            .auth().oauth2("fake-token")
        .when()
            .get("/bearer")
        .then()
            .statusCode(200)
            .body("authenticated", equalTo(true))
            .body("token", equalTo("fake-token"));
    }
    
    @Test
    public void testOAuth2BearerTokenFailure() {
        given()
            .auth().oauth2("invalid-token")
        .when()
            .get("/bearer")
        .then()
            .statusCode(401);
    }
    
    @Test
    public void testApiKeyAsHeader() {
        given()
            .header("X-API-Key", "secret-key")
        .when()
            .get("/headers")
        .then()
            .statusCode(200)
            .body("headers.X-Api-Key", equalTo("secret-key"));
    }
    
    @Test
    public void testApiKeyAsQueryParam() {
        given()
            .queryParam("api_key", "secret-key")
        .when()
            .get("/get")
        .then()
            .statusCode(200)
            .body("args.api_key", equalTo("secret-key"));
    }
    
    @Test
    public void testCustomAuthenticationHeader() {
        given()
            .header("Authorization", "CustomAuth token123")
        .when()
            .get("/headers")
        .then()
            .statusCode(200)
            .body("headers.Authorization", equalTo("CustomAuth token123"));
    }
    
    @Test
    public void testFormAuthentication() {
        given()
            .auth().form("user", "passwd")
        .when()
            .get("/basic-auth/user/passwd")
        .then()
            .statusCode(200);
    }
    
    @Test
    public void testMultiStepAuthentication() {
        // 1. 首先登录获取令牌
        Response loginResponse = given()
            .contentType(ContentType.JSON)
            .body("{\"username\":\"user\",\"password\":\"passwd\"}")
        .when()
            .post("/post")  // 使用post端点模拟登录
        .then()
            .statusCode(200)
            .extract()
            .response();
        
        // 提取响应中的数据（这里模拟令牌提取）
        String token = loginResponse.jsonPath().getString("data");
        
        // 2. 使用令牌访问受保护资源
        given()
            .header("Authorization", "Bearer " + (token != null ? token : "fake-token"))
        .when()
            .get("/bearer")
        .then()
            .statusCode(200)
            .body("authenticated", equalTo(true));
    }
    
    @Test
    public void testSessionBasedAuthentication() {
        // 1. 登录并获取会话Cookie
        Response loginResponse = given()
            .contentType(ContentType.URLENC)
            .formParam("username", "user")
            .formParam("password", "passwd")
        .when()
            .post("/post")  // 使用post端点模拟登录
        .then()
            .statusCode(200)
            .extract()
            .response();
        
        // 2. 使用会话Cookie访问受保护资源
        String sessionCookie = loginResponse.getCookie("JSESSIONID");
        
        given()
            .cookie("JSESSIONID", sessionCookie != null ? sessionCookie : "fake-session")
        .when()
            .get("/cookies")
        .then()
            .statusCode(200)
            .body("cookies.JSESSIONID", notNullValue());
    }
    
    @Test
    public void testComplexAuthenticationFlow() {
        // 模拟多因素认证流程
        
        // 1. 第一步认证：用户名/密码
        String tempToken = given()
            .contentType(ContentType.JSON)
            .body("{\"username\":\"user\",\"password\":\"passwd\"}")
        .when()
            .post("/post")  // 模拟API端点
        .then()
            .statusCode(200)
            .extract()
            .path("tempToken");  // 模拟临时令牌
        
        // 2. 第二步认证：验证码（假设获取了验证码）
        String otpCode = "123456";
        
        String authToken = given()
            .contentType(ContentType.JSON)
            .body("{\"tempToken\":\"" + tempToken + "\",\"otp\":\"" + otpCode + "\"}")
        .when()
            .post("/post")  // 模拟API端点
        .then()
            .statusCode(200)
            .extract()
            .path("authToken");  // 模拟最终认证令牌
        
        // 3. 使用最终令牌访问受保护资源
        given()
            .header("Authorization", "Bearer " + authToken)
        .when()
            .get("/bearer")
        .then()
            .statusCode(200)
            .body("authenticated", equalTo(true));
    }
    
    @Test
    public void testTokenRefreshFlow() {
        // 1. 使用刷新令牌获取新的访问令牌
        String refreshToken = "fake-refresh-token";
        
        String newAccessToken = given()
            .contentType(ContentType.JSON)
            .body("{\"refreshToken\":\"" + refreshToken + "\"}")
        .when()
            .post("/post")  // 模拟API端点
        .then()
            .statusCode(200)
            .extract()
            .path("accessToken");  // 模拟新的访问令牌
        
        // 2. 使用新令牌访问受保护资源
        given()
            .header("Authorization", "Bearer " + newAccessToken)
        .when()
            .get("/bearer")
        .then()
            .statusCode(200)
            .body("authenticated", equalTo(true));
    }
    
    @Test
    public void testApiKeySignature() {
        // 模拟基于签名的API密钥认证
        
        String apiKey = "my-api-key";
        String apiSecret = "my-api-secret";
        String timestamp = String.valueOf(System.currentTimeMillis());
        String nonce = "random-nonce-string";
        
        // 生成签名（简化版）
        String message = apiKey + timestamp + nonce;
        String signature = calculateHmacSha256(message, apiSecret);
        
        given()
            .header("X-API-Key", apiKey)
            .header("X-Timestamp", timestamp)
            .header("X-Nonce", nonce)
            .header("X-Signature", signature)
        .when()
            .get("/headers")
        .then()
            .statusCode(200)
            .body("headers.X-Api-Key", equalTo(apiKey))
            .body("headers.X-Timestamp", equalTo(timestamp))
            .body("headers.X-Nonce", equalTo(nonce))
            .body("headers.X-Signature", equalTo(signature));
    }
    
    /**
     * 简化的HMAC-SHA256签名生成方法
     */
    private String calculateHmacSha256(String data, String secret) {
        // 在实际应用中，应使用标准加密库
        // 这里仅返回模拟值
        return "simulated-signature-for-" + data.length();
    }
}