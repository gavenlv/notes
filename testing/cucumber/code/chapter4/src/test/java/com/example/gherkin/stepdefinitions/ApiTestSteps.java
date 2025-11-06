package com.example.gherkin.stepdefinitions;

import io.cucumber.java.en.And;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import io.restassured.RestAssured;
import io.restassured.response.Response;
import io.restassured.specification.RequestSpecification;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;

import java.util.HashMap;
import java.util.Map;

import static io.restassured.RestAssured.given;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasKey;
import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * API测试步骤定义类
 * 演示如何使用数据驱动测试进行API测试
 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
public class ApiTestSteps {

    @LocalServerPort
    private int port;

    private RequestSpecification request;
    private Response response;
    private Map<String, Object> requestBody = new HashMap<>();

    @Given("API基础URL设置为 {string}")
    public void setApiBaseUrl(String baseUrl) {
        RestAssured.baseURI = baseUrl;
        RestAssured.port = port;
    }

    @Given("请求头包含 {string}: {string}")
    public void setRequestHeader(String headerName, String headerValue) {
        if (request == null) {
            request = given();
        }
        request.header(headerName, headerValue);
    }

    @Given("请求体包含 {string}: {string}")
    public void setRequestBody(String key, String value) {
        requestBody.put(key, value);
    }

    @When("用户发送 {string} 请求到 {string}")
    public void sendRequest(String method, String endpoint) {
        if (request == null) {
            request = given();
        }

        if (!requestBody.isEmpty()) {
            request.body(requestBody);
        }

        switch (method.toUpperCase()) {
            case "GET":
                response = request.get(endpoint);
                break;
            case "POST":
                response = request.post(endpoint);
                break;
            case "PUT":
                response = request.put(endpoint);
                break;
            case "DELETE":
                response = request.delete(endpoint);
                break;
            default:
                throw new IllegalArgumentException("不支持的HTTP方法: " + method);
        }

        // 重置请求体
        requestBody.clear();
    }

    @Then("响应状态码应该是 {int}")
    public void verifyStatusCode(int expectedStatusCode) {
        assertEquals(expectedStatusCode, response.getStatusCode());
    }

    @Then("响应应该包含字段 {string}")
    public void verifyResponseContainsField(String fieldName) {
        response.then().body("$", hasKey(fieldName));
    }

    @Then("响应中字段 {string} 的值应该是 {string}")
    public void verifyFieldValue(String fieldName, String expectedValue) {
        response.then().body(fieldName, equalTo(expectedValue));
    }

    @And("响应时间应该小于 {int} 毫秒")
    public void verifyResponseTime(long maxResponseTime) {
        long responseTime = response.getTime();
        if (responseTime > maxResponseTime) {
            throw new AssertionError("响应时间 " + responseTime + " 毫秒超过了最大允许时间 " + maxResponseTime + " 毫秒");
        }
    }

    @Given("使用以下数据表设置API测试参数")
    public void setApiTestParametersFromDataTable(io.cucumber.datatable.DataTable dataTable) {
        Map<String, String> parameters = dataTable.asMap(String.class, String.class);
        
        for (Map.Entry<String, String> entry : parameters.entrySet()) {
            String key = entry.getKey();
            String value = entry.getValue();
            
            if (key.startsWith("header.")) {
                String headerName = key.substring(7); // 去掉"header."前缀
                setRequestHeader(headerName, value);
            } else if (key.startsWith("body.")) {
                String bodyKey = key.substring(5); // 去掉"body."前缀
                setRequestBody(bodyKey, value);
            }
        }
    }

    @When("使用场景大纲参数发送 {string} 请求到 {string}，参数为 {string}")
    public void sendRequestWithScenarioOutlineParams(String method, String endpoint, String params) {
        // 解析参数字符串，假设格式为 "key1=value1,key2=value2"
        Map<String, String> paramMap = new HashMap<>();
        String[] paramPairs = params.split(",");
        
        for (String pair : paramPairs) {
            String[] keyValue = pair.split("=");
            if (keyValue.length == 2) {
                paramMap.put(keyValue[0].trim(), keyValue[1].trim());
            }
        }
        
        // 设置请求参数
        if (request == null) {
            request = given();
        }
        
        // 根据请求方法设置参数
        if ("GET".equalsIgnoreCase(method)) {
            request.queryParams(paramMap);
        } else {
            request.formParams(paramMap);
        }
        
        // 发送请求
        sendRequest(method, endpoint);
    }

    @Then("响应应该包含以下数据")
    public void verifyResponseContainsData(io.cucumber.datatable.DataTable expectedData) {
        Map<String, String> expectedFields = expectedData.asMap(String.class, String.class);
        
        for (Map.Entry<String, String> entry : expectedFields.entrySet()) {
            String fieldName = entry.getKey();
            String expectedValue = entry.getValue();
            
            verifyFieldValue(fieldName, expectedValue);
        }
    }
}