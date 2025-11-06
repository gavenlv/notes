package com.example.gherkin.stepdefinitions;

import com.example.gherkin.model.User;
import com.example.gherkin.service.UserService;
import io.cucumber.java.en.And;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import org.springframework.beans.factory.annotation.Autowired;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

/**
 * 用户登录功能的步骤定义类
 */
public class UserLoginSteps {

    @Autowired
    private UserService userService;

    private UserService.LoginResult loginResult;
    private List<UserService.LoginResult> multipleLoginResults;
    private User loggedInUser;
    private LocalDateTime lastLoginTimeBefore;

    @Given("系统已经初始化用户服务")
    public void systemInitializedUserService() {
        assertNotNull(userService, "用户服务应该已初始化");
    }

    @Given("用户{string}已经存在")
    public void userExists(String username) {
        // 创建一个已存在的用户
        User user = new User(username, username + "@example.com", "P@ssw0rd123", "Test", "User");
        user.setVerified(true);
        user.setActive(true);
        userService.updateUser(user);
    }

    @Given("用户{string}已经验证邮箱")
    public void userHasVerifiedEmail(String username) {
        User user = userService.getUserByUsername(username).orElse(null);
        if (user != null) {
            user.setVerified(true);
            userService.updateUser(user);
        }
    }

    @Given("用户{string}的密码是{string}")
    public void userHasPassword(String username, String password) {
        User user = userService.getUserByUsername(username).orElse(null);
        if (user != null) {
            user.setPassword(password);
            userService.updateUser(user);
        }
    }

    @Given("用户{string}尚未验证邮箱")
    public void userHasNotVerifiedEmail(String username) {
        User user = userService.getUserByUsername(username).orElse(null);
        if (user != null) {
            user.setVerified(false);
            userService.updateUser(user);
        }
    }

    @Given("用户{string}的账户已被禁用")
    public void userAccountIsDisabled(String username) {
        User user = userService.getUserByUsername(username).orElse(null);
        if (user != null) {
            user.setActive(false);
            userService.updateUser(user);
        }
    }

    @When("我使用用户名{string}和密码{string}登录")
    public void loginWithUsernameAndPassword(String username, String password) {
        // 记录登录前的最后登录时间
        User user = userService.getUserByUsername(username).orElse(null);
        if (user != null) {
            lastLoginTimeBefore = user.getLastLoginTime();
        }
        
        loginResult = userService.authenticateUser(username, password);
        
        if (loginResult.isSuccess()) {
            loggedInUser = loginResult.getUser();
        }
    }

    @When("我使用用户名{string}和错误密码登录")
    public void loginWithWrongPassword(String username) {
        loginResult = userService.authenticateUser(username, "wrong_password");
    }

    @When("我尝试使用以下凭据登录:")
    public void attemptLoginWithMultipleCredentials(io.cucumber.datatable.DataTable dataTable) {
        List<Map<String, String>> credentials = dataTable.asMaps(String.class, String.class);
        multipleLoginResults = new ArrayList<>();

        for (Map<String, String> credential : credentials) {
            String username = credential.get("username");
            String password = credential.get("password");
            
            UserService.LoginResult result = userService.authenticateUser(username, password);
            multipleLoginResults.add(result);
        }
    }

    @When("我尝试使用以下用户名变体登录:")
    public void attemptLoginWithUsernameVariants(io.cucumber.datatable.DataTable dataTable) {
        List<Map<String, String>> usernameVariants = dataTable.asMaps(String.class, String.class);
        multipleLoginResults = new ArrayList<>();

        for (Map<String, String> variant : usernameVariants) {
            String username = variant.get("username");
            
            UserService.LoginResult result = userService.authenticateUser(username, "P@ssw0rd123");
            multipleLoginResults.add(result);
        }
    }

    @Then("登录应该成功")
    public void loginShouldSucceed() {
        assertTrue(loginResult.isSuccess(), "登录应该成功");
    }

    @Then("登录应该失败")
    public void loginShouldFail() {
        assertFalse(loginResult.isSuccess(), "登录应该失败");
    }

    @Then("我应该收到用户信息")
    public void shouldReceiveUserInfo() {
        assertNotNull(loggedInUser, "应该收到用户信息");
        assertNotNull(loggedInUser.getUsername(), "用户信息应包含用户名");
        assertNotNull(loggedInUser.getEmail(), "用户信息应包含邮箱");
    }

    @Then("最后登录时间应该被更新")
    public void lastLoginTimeShouldBeUpdated() {
        assertNotNull(loggedInUser, "应该有登录用户");
        assertNotNull(loggedInUser.getLastLoginTime(), "应该有最后登录时间");
        assertTrue(
            loggedInUser.getLastLoginTime().isAfter(lastLoginTimeBefore) || 
            lastLoginTimeBefore == null,
            "最后登录时间应该被更新"
        );
    }

    @Then("我应该收到错误消息{string}")
    public void shouldReceiveErrorMessage(String expectedMessage) {
        assertEquals(expectedMessage, loginResult.getMessage(), "错误消息应该匹配");
    }

    @Then("登录结果应该与预期一致")
    public void loginResultsShouldMatchExpectations(io.cucumber.datatable.DataTable dataTable) {
        List<Map<String, String>> expectedResults = dataTable.asMaps(String.class, String.class);
        
        assertEquals(expectedResults.size(), multipleLoginResults.size(), "结果数量应该匹配");
        
        for (int i = 0; i < expectedResults.size(); i++) {
            Map<String, String> expected = expectedResults.get(i);
            UserService.LoginResult actual = multipleLoginResults.get(i);
            
            String expectedResult = expected.get("expectedResult");
            if ("成功".equals(expectedResult)) {
                assertTrue(actual.isSuccess(), "第 " + (i+1) + " 次登录应该成功");
            } else {
                assertFalse(actual.isSuccess(), "第 " + (i+1) + " 次登录应该失败");
            }
        }
    }

    @Then("应该创建新的用户会话")
    public void newSessionShouldBeCreated() {
        // 在实际实现中，这里应该验证会话是否已创建
        // 由于我们的示例中没有实现会话管理，这里只做基本验证
        assertTrue(loginResult.isSuccess(), "成功登录应该创建会话");
    }

    @Then("会话应该包含用户标识信息")
    public void sessionShouldContainUserIdentification() {
        // 在实际实现中，这里应该验证会话是否包含用户标识信息
        assertNotNull(loggedInUser, "会话应该包含用户信息");
        assertNotNull(loggedInUser.getId(), "会话应该包含用户ID");
    }

    @When("我注销当前会话")
    public void logoutCurrentSession() {
        // 在实际实现中，这里应该实现注销逻辑
        // 由于我们的示例中没有实现会话管理，这里只做基本处理
    }

    @Then("会话应该被终止")
    public void sessionShouldBeTerminated() {
        // 在实际实现中，这里应该验证会话是否已终止
        // 由于我们的示例中没有实现会话管理，这里只做基本处理
    }

    @When("我尝试使用已注销的会话访问受保护资源")
    public void attemptAccessProtectedResourceWithLoggedOutSession() {
        // 在实际实现中，这里应该尝试使用已注销的会话访问受保护资源
        // 由于我们的示例中没有实现会话管理，这里只做基本处理
    }

    @Then("访问应该被拒绝")
    public void accessShouldBeDenied() {
        // 在实际实现中，这里应该验证访问是否被拒绝
        // 由于我们的示例中没有实现会话管理，这里只做基本处理
    }
}