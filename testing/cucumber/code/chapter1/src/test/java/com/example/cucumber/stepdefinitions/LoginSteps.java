package com.example.cucumber.stepdefinitions;

import com.example.login.AuthenticationService;
import com.example.login.LoginService;
import com.example.login.User;
import io.cucumber.java.en.And;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import static org.junit.Assert.*;

public class LoginSteps {
    private LoginService loginService;
    private AuthenticationService authService;
    private AuthenticationService.LoginResult loginResult;
    
    @Given("我有一个登录服务")
    public void 我有一个登录服务() {
        authService = new AuthenticationService();
        loginService = new LoginService(authService);
    }
    
    @And("用户 {string} 存在且密码为 {string}")
    public void 用户存在且密码为(String username, String password) {
        authService.addUser(username, password);
    }
    
    @When("我使用用户名 {string} 和密码 {string} 登录")
    public void 我使用用户名和密码登录(String username, String password) {
        loginResult = loginService.authenticate(username, password);
    }
    
    @Then("我应该能够成功登录")
    public void 我应该能够成功登录() {
        assertTrue("登录应该成功", loginResult.isSuccess());
    }
    
    @And("我应该看到 {string} 的消息")
    public void 我应该看到的消息(String expectedMessage) {
        assertEquals("消息不匹配", expectedMessage, loginResult.getMessage());
    }
    
    @Then("我应该无法登录")
    public void 我应该无法登录() {
        assertFalse("登录应该失败", loginResult.isSuccess());
    }
    
    @And("用户 {string} 已被禁用")
    public void 用户已被禁用(String username) {
        authService.deactivateUser(username);
    }
    
    @Then("我应该{string}登录")
    public void 我应该登录(String success) {
        if ("能够".equals(success)) {
            assertTrue("登录应该成功", loginResult.isSuccess());
        } else {
            assertFalse("登录应该失败", loginResult.isSuccess());
        }
    }
}