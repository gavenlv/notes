package com.example.gherkin.stepdefinitions;

import com.example.gherkin.context.TestContext;
import com.example.gherkin.model.User;
import com.example.gherkin.service.UserService;
import io.cucumber.java.en.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.util.Assert;

import java.util.List;
import java.util.Map;
import java.util.Optional;

import static org.junit.Assert.*;

/**
 * 用户相关功能的步骤定义
 */
public class UserSteps {
    
    @Autowired
    private UserService userService;
    
    @Autowired
    private TestContext testContext;
    
    private User currentUser;
    private Exception lastException;
    
    @Given("用户 {string} 不存在")
    public void userDoesNotExist(String username) {
        Optional<User> user = userService.getUserByUsername(username);
        if (user.isPresent()) {
            userService.deleteUser(user.get().getId());
        }
    }
    
    @Given("用户 {string} 存在，密码为 {string}")
    public void userExistsWithPassword(String username, String password) {
        if (!userService.existsByUsername(username)) {
            String email = username + "@example.com";
            userService.createUser(username, email, password);
        }
    }
    
    @Given("用户 {string} 存在，邮箱为 {string}，密码为 {string}")
    public void userExistsWithEmailAndPassword(String username, String email, String password) {
        if (!userService.existsByUsername(username)) {
            userService.createUser(username, email, password);
        }
    }
    
    @Given("已创建以下用户:")
    public void createUsersFromDataTable(io.cucumber.datatable.DataTable dataTable) {
        List<Map<String, String>> userDataList = dataTable.asMaps(String.class, String.class);
        List<User> createdUsers = userService.createUsers(userDataList);
        testContext.set("createdUsers", createdUsers);
    }
    
    @When("用户使用用户名 {string} 和密码 {string} 注册")
    public void userRegistersWithCredentials(String username, String password) {
        try {
            String email = username + "@example.com";
            currentUser = userService.createUser(username, email, password);
            testContext.set("currentUser", currentUser);
            lastException = null;
        } catch (Exception e) {
            lastException = e;
            testContext.set("lastException", e);
        }
    }
    
    @When("用户使用用户名 {string}，邮箱 {string} 和密码 {string} 注册")
    public void userRegistersWithUsernameEmailAndPassword(String username, String email, String password) {
        try {
            currentUser = userService.createUser(username, email, password);
            testContext.set("currentUser", currentUser);
            lastException = null;
        } catch (Exception e) {
            lastException = e;
            testContext.set("lastException", e);
        }
    }
    
    @When("用户使用用户名 {string} 和密码 {string} 登录")
    public void userLogsInWithCredentials(String username, String password) {
        try {
            currentUser = userService.authenticate(username, password);
            testContext.set("currentUser", currentUser);
            lastException = null;
        } catch (Exception e) {
            lastException = e;
            testContext.set("lastException", e);
        }
    }
    
    @When("用户更新个人信息为名字 {string}，姓氏 {string}，电话 {string}")
    public void userUpdatesPersonalInfo(String firstName, String lastName, String phone) {
        try {
            if (currentUser == null) {
                currentUser = testContext.get("currentUser", User.class);
            }
            
            Assert.notNull(currentUser, "当前用户不能为空");
            currentUser = userService.updateUser(currentUser.getId(), firstName, lastName, phone);
            testContext.set("currentUser", currentUser);
            lastException = null;
        } catch (Exception e) {
            lastException = e;
            testContext.set("lastException", e);
        }
    }
    
    @When("用户将密码从 {string} 更新为 {string}")
    public void userUpdatesPassword(String oldPassword, String newPassword) {
        try {
            if (currentUser == null) {
                currentUser = testContext.get("currentUser", User.class);
            }
            
            Assert.notNull(currentUser, "当前用户不能为空");
            userService.updatePassword(currentUser.getId(), oldPassword, newPassword);
            lastException = null;
        } catch (Exception e) {
            lastException = e;
            testContext.set("lastException", e);
        }
    }
    
    @When("管理员验证用户 {string} 的邮箱")
    public void adminVerifiesUserEmail(String username) {
        try {
            Optional<User> user = userService.getUserByUsername(username);
            Assert.isTrue(user.isPresent(), "用户不存在: " + username);
            
            userService.verifyEmail(user.get().getId());
            lastException = null;
        } catch (Exception e) {
            lastException = e;
            testContext.set("lastException", e);
        }
    }
    
    @When("管理员禁用用户 {string}")
    public void adminDisablesUser(String username) {
        try {
            Optional<User> user = userService.getUserByUsername(username);
            Assert.isTrue(user.isPresent(), "用户不存在: " + username);
            
            userService.enableUser(user.get().getId(), false);
            lastException = null;
        } catch (Exception e) {
            lastException = e;
            testContext.set("lastException", e);
        }
    }
    
    @Then("用户应该成功注册")
    public void userShouldBeSuccessfullyRegistered() {
        assertNull("注册不应该抛出异常", lastException);
        assertNotNull("当前用户不应该为空", currentUser);
        assertNotNull("用户ID不应该为空", currentUser.getId());
        assertEquals("用户名应该匹配", testContext.get("username", String.class), currentUser.getUsername());
    }
    
    @Then("用户应该成功登录")
    public void userShouldBeSuccessfullyLoggedIn() {
        assertNull("登录不应该抛出异常", lastException);
        assertNotNull("当前用户不应该为空", currentUser);
        assertNotNull("用户ID不应该为空", currentUser.getId());
    }
    
    @Then("用户登录应该失败")
    public void userLoginShouldFail() {
        assertNotNull("登录应该抛出异常", lastException);
        assertNull("当前用户应该为空", currentUser);
    }
    
    @Then("用户注册应该失败")
    public void userRegistrationShouldFail() {
        assertNotNull("注册应该抛出异常", lastException);
        assertNull("当前用户应该为空", currentUser);
    }
    
    @Then("用户应该看到错误消息 {string}")
    public void userShouldSeeErrorMessage(String expectedMessage) {
        assertNotNull("应该有异常", lastException);
        assertTrue("错误消息应该包含预期文本", 
            lastException.getMessage().contains(expectedMessage));
    }
    
    @Then("用户个人信息应该更新为名字 {string}，姓氏 {string}，电话 {string}")
    public void userInfoShouldBeUpdated(String firstName, String lastName, String phone) {
        assertNotNull("当前用户不应该为空", currentUser);
        assertEquals("名字应该匹配", firstName, currentUser.getFirstName());
        assertEquals("姓氏应该匹配", lastName, currentUser.getLastName());
        assertEquals("电话应该匹配", phone, currentUser.getPhone());
    }
    
    @Then("用户密码应该更新成功")
    public void userPasswordShouldBeUpdated() {
        assertNull("密码更新不应该抛出异常", lastException);
    }
    
    @Then("用户 {string} 的邮箱应该已验证")
    public void userEmailShouldBeVerified(String username) {
        Optional<User> user = userService.getUserByUsername(username);
        Assert.isTrue(user.isPresent(), "用户不存在: " + username);
        assertTrue("邮箱应该已验证", user.get().isEmailVerified());
    }
    
    @Then("用户 {string} 应该被禁用")
    public void userShouldBeDisabled(String username) {
        Optional<User> user = userService.getUserByUsername(username);
        Assert.isTrue(user.isPresent(), "用户不存在: " + username);
        assertFalse("用户应该被禁用", user.get().isEnabled());
    }
    
    @Then("系统应该有 {int} 个用户")
    public void systemShouldHaveNumberOfUsers(int expectedCount) {
        int actualCount = userService.getAllUsers().size();
        assertEquals("用户数量应该匹配", expectedCount, actualCount);
    }
    
    @Then("用户 {string} 应该存在")
    public void userShouldExist(String username) {
        assertTrue("用户应该存在", userService.existsByUsername(username));
    }
    
    @Then("用户 {string} 不应该存在")
    public void userShouldNotExist(String username) {
        assertFalse("用户不应该存在", userService.existsByUsername(username));
    }
    
    @Then("搜索关键词 {string} 应该返回 {int} 个用户")
    public void searchKeywordShouldReturnNumberOfUsers(String keyword, int expectedCount) {
        List<User> searchResults = userService.searchUsers(keyword);
        assertEquals("搜索结果数量应该匹配", expectedCount, searchResults.size());
    }
}