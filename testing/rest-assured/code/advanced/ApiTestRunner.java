package com.example.restassured.advanced;

import com.example.restassured.framework.BaseApiTest;
import io.restassured.response.Response;
import io.restassured.specification.RequestSpecification;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.function.Consumer;

/**
 * API测试运行器
 * 提供高级测试执行和验证功能，支持链式调用和自定义验证
 */
public class ApiTestRunner {
    
    private final RequestSpecification requestSpec;
    private Response response;
    private final List<Executable> beforeActions = new ArrayList<>();
    private final List<Executable> afterActions = new ArrayList<>();
    private final List<Consumer<Response>> responseValidators = new ArrayList<>();
    private final List<Runnable> cleanupActions = new ArrayList<>();
    private ResponseValidator responseValidator;
    
    private ApiTestRunner(RequestSpecification requestSpec) {
        this.requestSpec = requestSpec;
    }
    
    /**
     * 创建新的API测试运行器实例
     */
    public static ApiTestRunner with(RequestSpecification requestSpec) {
        return new ApiTestRunner(requestSpec);
    }
    
    /**
     * 创建使用默认请求规范的API测试运行器实例
     */
    public static ApiTestRunner withDefaults() {
        return new ApiTestRunner(BaseApiTest.requestSpec);
    }
    
    /**
     * 执行GET请求
     */
    public ApiTestRunner get(String path) {
        executeRequest(() -> given().spec(requestSpec).get(path));
        return this;
    }
    
    /**
     * 执行POST请求
     */
    public ApiTestRunner post(String path) {
        executeRequest(() -> given().spec(requestSpec).post(path));
        return this;
    }
    
    /**
     * 执行带请求体的POST请求
     */
    public ApiTestRunner post(String path, Object body) {
        executeRequest(() -> given().spec(requestSpec).body(body).post(path));
        return this;
    }
    
    /**
     * 执行PUT请求
     */
    public ApiTestRunner put(String path) {
        executeRequest(() -> given().spec(requestSpec).put(path));
        return this;
    }
    
    /**
     * 执行带请求体的PUT请求
     */
    public ApiTestRunner put(String path, Object body) {
        executeRequest(() -> given().spec(requestSpec).body(body).put(path));
        return this;
    }
    
    /**
     * 执行PATCH请求
     */
    public ApiTestRunner patch(String path) {
        executeRequest(() -> given().spec(requestSpec).patch(path));
        return this;
    }
    
    /**
     * 执行带请求体的PATCH请求
     */
    public ApiTestRunner patch(String path, Object body) {
        executeRequest(() -> given().spec(requestSpec).body(body).patch(path));
        return this;
    }
    
    /**
     * 执行DELETE请求
     */
    public ApiTestRunner delete(String path) {
        executeRequest(() -> given().spec(requestSpec).delete(path));
        return this;
    }
    
    /**
     * 添加前置操作
     */
    public ApiTestRunner before(Executable action) {
        beforeActions.add(action);
        return this;
    }
    
    /**
     * 添加后置操作
     */
    public ApiTestRunner after(Executable action) {
        afterActions.add(action);
        return this;
    }
    
    /**
     * 添加响应验证器
     */
    public ApiTestRunner validate(Consumer<Response> validator) {
        responseValidators.add(validator);
        return this;
    }
    
    /**
     * 添加清理操作
     */
    public ApiTestRunner cleanup(Runnable action) {
        cleanupActions.add(action);
        return this;
    }
    
    /**
     * 验证状态码
     */
    public ApiTestRunner assertStatus(int expectedStatus) {
        return validate(response -> {
            int actualStatus = response.getStatusCode();
            if (actualStatus != expectedStatus) {
                throw new AssertionError("Expected status code " + expectedStatus + " but got " + actualStatus);
            }
        });
    }
    
    /**
     * 验证响应时间
     */
    public ApiTestRunner assertResponseTimeLessThan(long maxTimeMs) {
        return validate(response -> {
            long actualTime = response.getTime();
            if (actualTime > maxTimeMs) {
                throw new AssertionError("Response time " + actualTime + "ms exceeded maximum " + maxTimeMs + "ms");
            }
        });
    }
    
    /**
     * 验证JSON路径值
     */
    public ApiTestRunner assertJsonPath(String jsonPath, Object expectedValue) {
        return validate(response -> {
            Object actualValue = response.jsonPath().get(jsonPath);
            if (!expectedValue.equals(actualValue)) {
                throw new AssertionError("JSON path '" + jsonPath + "' expected '" + expectedValue + "' but got '" + actualValue + "'");
            }
        });
    }
    
    /**
     * 验证JSON路径值（使用Hamcrest匹配器）
     */
    public ApiTestRunner assertJsonPath(String jsonPath, org.hamcrest.Matcher<?> matcher) {
        return validate(response -> {
            Object actualValue = response.jsonPath().get(jsonPath);
            org.hamcrest.MatcherAssert.assertThat("JSON path: " + jsonPath, actualValue, matcher);
        });
    }
    
    /**
     * 获取响应
     */
    public Response getResponse() {
        if (response == null) {
            throw new IllegalStateException("No request has been executed yet");
        }
        return response;
    }
    
    /**
     * 获取响应验证器
     */
    public ResponseValidator getValidator() {
        if (responseValidator == null) {
            responseValidator = new ResponseValidator(getResponse());
        }
        return responseValidator;
    }
    
    /**
     * 执行请求并运行所有验证
     */
    public void run() {
        if (response == null) {
            throw new IllegalStateException("No request has been executed yet");
        }
        
        try {
            // 执行前置操作
            for (Executable action : beforeActions) {
                action.execute();
            }
            
            // 执行响应验证器
            for (Consumer<Response> validator : responseValidators) {
                validator.accept(response);
            }
            
            // 执行后置操作
            for (Executable action : afterActions) {
                action.execute();
            }
        } catch (Exception e) {
            // 执行清理操作
            runCleanup();
            
            if (e instanceof AssertionError) {
                throw (AssertionError) e;
            } else {
                throw new RuntimeException("Test execution failed", e);
            }
        }
    }
    
    /**
     * 执行清理操作
     */
    public void runCleanup() {
        for (Runnable action : cleanupActions) {
            try {
                action.run();
            } catch (Exception e) {
                // 忽略清理错误，确保所有清理操作都有机会执行
                System.err.println("Cleanup action failed: " + e.getMessage());
            }
        }
    }
    
    /**
     * 重置测试运行器状态
     */
    public ApiTestRunner reset() {
        response = null;
        responseValidator = null;
        return this;
    }
    
    /**
     * 执行请求
     */
    private void executeRequest(Callable<Response> requestCallable) {
        try {
            // 执行前置操作
            for (Executable action : beforeActions) {
                action.execute();
            }
            
            // 执行请求
            response = requestCallable.call();
            
            // 执行后置操作
            for (Executable action : afterActions) {
                action.execute();
            }
        } catch (Exception e) {
            // 执行清理操作
            runCleanup();
            
            if (e instanceof AssertionError) {
                throw (AssertionError) e;
            } else if (e instanceof RuntimeException) {
                throw (RuntimeException) e;
            } else {
                throw new RuntimeException("Failed to execute request", e);
            }
        }
    }
    
    /**
     * 创建API测试构建器
     */
    public static class ApiTestBuilder {
        private final List<ApiTestRunner> testRunners = new ArrayList<>();
        private Runnable finalCleanup = null;
        
        /**
         * 添加测试步骤
         */
        public ApiTestBuilder step(Consumer<ApiTestRunner> stepBuilder) {
            ApiTestRunner runner = ApiTestRunner.withDefaults();
            stepBuilder.accept(runner);
            testRunners.add(runner);
            return this;
        }
        
        /**
         * 添加GET请求步骤
         */
        public ApiTestBuilder get(String path, Consumer<ApiTestRunner> validators) {
            return step(runner -> {
                runner.get(path);
                validators.accept(runner);
            });
        }
        
        /**
         * 添加POST请求步骤
         */
        public ApiTestBuilder post(String path, Object body, Consumer<ApiTestRunner> validators) {
            return step(runner -> {
                runner.post(path, body);
                validators.accept(runner);
            });
        }
        
        /**
         * 添加PUT请求步骤
         */
        public ApiTestBuilder put(String path, Object body, Consumer<ApiTestRunner> validators) {
            return step(runner -> {
                runner.put(path, body);
                validators.accept(runner);
            });
        }
        
        /**
         * 添加DELETE请求步骤
         */
        public ApiTestBuilder delete(String path, Consumer<ApiTestRunner> validators) {
            return step(runner -> {
                runner.delete(path);
                validators.accept(runner);
            });
        }
        
        /**
         * 设置最终清理操作
         */
        public ApiTestBuilder finallyCleanup(Runnable cleanup) {
            this.finalCleanup = cleanup;
            return this;
        }
        
        /**
         * 执行所有测试步骤
         */
        public void execute() {
            try {
                for (ApiTestRunner runner : testRunners) {
                    runner.run();
                }
            } finally {
                if (finalCleanup != null) {
                    finalCleanup.run();
                }
            }
        }
        
        /**
         * 创建并执行单个API测试
         */
        public static void runTest(Consumer<ApiTestRunner> testBuilder) {
            ApiTestRunner runner = ApiTestRunner.withDefaults();
            testBuilder.accept(runner);
            runner.run();
            runner.runCleanup();
        }
    }
    
    // 为了方便使用，添加一个静态方法来创建基本的given()请求
    private static RequestSpecification given() {
        return io.restassured.RestAssured.given();
    }
    
    /**
     * 示例测试方法，展示如何使用ApiTestRunner
     */
    public static class ExampleUsage {
        @Test
        public void testSimpleGetRequest() {
            ApiTestRunner.withDefaults()
                .get("/users/1")
                .assertStatus(200)
                .assertJsonPath("id", 1)
                .assertJsonPath("username", notNullValue())
                .run();
        }
        
        @Test
        public void testComplexWorkflow() {
            // 创建API测试构建器
            new ApiTestBuilder.ApiTestBuilder()
                .get("/users", runner -> {
                    runner.assertStatus(200)
                           .assertJsonPath("$", not(empty()))
                           .validate(response -> {
                               int userId = response.jsonPath().getInt("[0].id");
                               // 将用户ID存储到测试数据管理器中，供后续使用
                           });
                })
                .post("/posts", Map.of("title", "Test Post", "body", "Test Body", "userId", 1), runner -> {
                    runner.assertStatus(201)
                           .validate(response -> {
                               int postId = response.jsonPath().getInt("id");
                               // 将文章ID存储到测试数据管理器中，供后续使用
                           });
                })
                .finallyCleanup(() -> {
                    // 清理测试数据
                })
                .execute();
        }
        
        @Test
        public void testWithCustomValidation() {
            ApiTestRunner.withDefaults()
                .get("/users")
                .validate(response -> {
                    // 自定义验证逻辑
                    List<Map<String, Object>> users = response.jsonPath().getList("$");
                    for (Map<String, Object> user : users) {
                        if (!user.containsKey("id") || !user.containsKey("username")) {
                            throw new AssertionError("User missing required fields");
                        }
                    }
                })
                .run();
        }
        
        @Test
        public void testWithBeforeAndAfterActions() {
            ApiTestRunner.withDefaults()
                .before(() -> {
                    // 设置测试前置条件
                })
                .post("/users", Map.of("name", "Test User"))
                .after(() -> {
                    // 测试后置操作
                })
                .cleanup(() -> {
                    // 清理操作
                })
                .run();
        }
    }
}