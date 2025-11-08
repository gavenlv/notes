package com.example.restassured.performance;

import com.example.restassured.framework.BaseApiTest;
import io.restassured.response.Response;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;
import java.util.stream.Collectors;

import static io.restassured.RestAssured.given;

/**
 * 并发API测试
 * 测试API在并发请求下的性能表现和稳定性
 */
public class ConcurrentApiTest extends BaseApiTest {
    
    private static final int THREAD_COUNT = 10;
    private static final int REQUESTS_PER_THREAD = 5;
    private static final int TOTAL_TIMEOUT_SECONDS = 30;
    
    @Test
    @DisplayName("并发获取所有用户")
    public void testConcurrentGetAllUsers() throws InterruptedException, ExecutionException {
        ExecutorService executorService = Executors.newFixedThreadPool(THREAD_COUNT);
        List<Future<Response>> futures = new ArrayList<>();
        
        // 提交任务
        for (int i = 0; i < THREAD_COUNT; i++) {
            Future<Response> future = executorService.submit(() -> {
                return given()
                    .spec(requestSpec)
                .when()
                    .get("/users")
                .then()
                    .extract()
                    .response();
            });
            futures.add(future);
        }
        
        // 等待所有任务完成
        List<Response> responses = new ArrayList<>();
        for (Future<Response> future : futures) {
            responses.add(future.get());
        }
        
        // 验证所有响应
        for (Response response : responses) {
            response.then()
                .statusCode(200);
        }
        
        executorService.shutdown();
    }
    
    @Test
    @DisplayName("并发创建和删除资源")
    public void testConcurrentCreateAndDeleteResources() throws InterruptedException, ExecutionException {
        ExecutorService executorService = Executors.newFixedThreadPool(THREAD_COUNT);
        List<Future<Integer>> futures = new ArrayList<>();
        
        // 提交创建任务
        for (int i = 0; i < THREAD_COUNT; i++) {
            final int threadId = i;
            Future<Integer> future = executorService.submit(() -> {
                // 创建文章
                Response createResponse = given()
                    .spec(requestSpec)
                    .body("{\"title\": \"Concurrent Test Post " + threadId + "\", \"body\": \"Test body for concurrent test " + threadId + "\", \"userId\": 1}")
                .when()
                    .post("/posts")
                .then()
                    .statusCode(201)
                    .extract()
                    .response();
                
                int postId = createResponse.jsonPath().getInt("id");
                
                // 获取创建的文章以验证
                given()
                    .spec(requestSpec)
                    .pathParam("id", postId)
                .when()
                    .get("/posts/{id}")
                .then()
                    .statusCode(200)
                    .body("id", equalTo(postId));
                
                // 删除创建的文章
                given()
                    .spec(requestSpec)
                    .pathParam("id", postId)
                .when()
                    .delete("/posts/{id}")
                .then()
                    .statusCode(200);
                
                return postId;
            });
            futures.add(future);
        }
        
        // 等待所有任务完成
        List<Integer> createdPostIds = new ArrayList<>();
        for (Future<Integer> future : futures) {
            createdPostIds.add(future.get());
        }
        
        executorService.shutdown();
    }
    
    @Test
    @DisplayName("负载测试 - 固定数量的并发请求")
    public void testLoadFixedConcurrentRequests() throws InterruptedException, ExecutionException {
        ExecutorService executorService = Executors.newFixedThreadPool(THREAD_COUNT);
        List<Future<RequestMetrics>> futures = new ArrayList<>();
        
        // 提交请求任务
        for (int i = 0; i < THREAD_COUNT * REQUESTS_PER_THREAD; i++) {
            final int requestId = i;
            Future<RequestMetrics> future = executorService.submit(() -> {
                long startTime = System.currentTimeMillis();
                
                Response response = given()
                    .spec(requestSpec)
                .when()
                    .get("/users")
                .then()
                    .extract()
                    .response();
                
                long endTime = System.currentTimeMillis();
                int statusCode = response.getStatusCode();
                long responseTime = endTime - startTime;
                
                return new RequestMetrics(requestId, statusCode, responseTime);
            });
            futures.add(future);
        }
        
        // 等待所有任务完成并收集指标
        List<RequestMetrics> metricsList = new ArrayList<>();
        for (Future<RequestMetrics> future : futures) {
            metricsList.add(future.get());
        }
        
        // 计算统计信息
        long totalTime = metricsList.stream().mapToLong(m -> m.responseTime).sum();
        long averageTime = totalTime / metricsList.size();
        long minTime = metricsList.stream().mapToLong(m -> m.responseTime).min().orElse(0);
        long maxTime = metricsList.stream().mapToLong(m -> m.responseTime).max().orElse(0);
        long successCount = metricsList.stream().mapToLong(m -> m.statusCode == 200 ? 1 : 0).sum();
        
        System.out.println("Load Test Results:");
        System.out.println("Total Requests: " + metricsList.size());
        System.out.println("Successful Requests: " + successCount);
        System.out.println("Success Rate: " + (100.0 * successCount / metricsList.size()) + "%");
        System.out.println("Average Response Time: " + averageTime + "ms");
        System.out.println("Min Response Time: " + minTime + "ms");
        System.out.println("Max Response Time: " + maxTime + "ms");
        
        executorService.shutdown();
    }
    
    @Test
    @DisplayName("压力测试 - 逐步增加并发数")
    public void testStressWithIncreasingConcurrency() throws InterruptedException, ExecutionException {
        int[] concurrencyLevels = {1, 5, 10, 20, 50};
        
        for (int level : concurrencyLevels) {
            System.out.println("Testing with concurrency level: " + level);
            
            ExecutorService executorService = Executors.newFixedThreadPool(level);
            CountDownLatch latch = new CountDownLatch(level);
            List<RequestMetrics> metricsList = new CopyOnWriteArrayList<>();
            
            long testStartTime = System.currentTimeMillis();
            
            // 提交任务
            for (int i = 0; i < level; i++) {
                final int requestId = i;
                executorService.submit(() -> {
                    try {
                        long startTime = System.currentTimeMillis();
                        
                        Response response = given()
                            .spec(requestSpec)
                        .when()
                            .get("/users")
                        .then()
                            .extract()
                            .response();
                        
                        long endTime = System.currentTimeMillis();
                        int statusCode = response.getStatusCode();
                        long responseTime = endTime - startTime;
                        
                        metricsList.add(new RequestMetrics(requestId, statusCode, responseTime));
                    } finally {
                        latch.countDown();
                    }
                });
            }
            
            // 等待所有任务完成
            latch.await(TOTAL_TIMEOUT_SECONDS, TimeUnit.SECONDS);
            
            long testEndTime = System.currentTimeMillis();
            long totalTestTime = testEndTime - testStartTime;
            
            // 计算统计信息
            long totalTime = metricsList.stream().mapToLong(m -> m.responseTime).sum();
            long averageTime = metricsList.isEmpty() ? 0 : totalTime / metricsList.size();
            long minTime = metricsList.stream().mapToLong(m -> m.responseTime).min().orElse(0);
            long maxTime = metricsList.stream().mapToLong(m -> m.responseTime).max().orElse(0);
            long successCount = metricsList.stream().mapToLong(m -> m.statusCode == 200 ? 1 : 0).sum();
            
            System.out.println("Concurrency Level " + level + " Results:");
            System.out.println("Total Requests: " + metricsList.size());
            System.out.println("Successful Requests: " + successCount);
            System.out.println("Success Rate: " + (metricsList.isEmpty() ? 0 : (100.0 * successCount / metricsList.size())) + "%");
            System.out.println("Average Response Time: " + averageTime + "ms");
            System.out.println("Min Response Time: " + minTime + "ms");
            System.out.println("Max Response Time: " + maxTime + "ms");
            System.out.println("Total Test Time: " + totalTestTime + "ms");
            System.out.println("Requests Per Second: " + (metricsList.size() * 1000.0 / totalTestTime));
            System.out.println("------------------------");
            
            executorService.shutdown();
        }
    }
    
    @Test
    @DisplayName("批量请求测试 - 使用CompletableFuture")
    public void testBatchRequestsUsingCompletableFuture() {
        List<CompletableFuture<Response>> futures = new ArrayList<>();
        
        // 创建异步请求
        for (int i = 0; i < THREAD_COUNT; i++) {
            CompletableFuture<Response> future = CompletableFuture.supplyAsync(() -> 
                given()
                    .spec(requestSpec)
                .when()
                    .get("/users")
                .then()
                    .extract()
                    .response()
            );
            futures.add(future);
        }
        
        // 等待所有请求完成
        CompletableFuture<Void> allFutures = CompletableFuture.allOf(
            futures.toArray(new CompletableFuture[0])
        );
        
        // 获取所有响应
        List<Response> responses = futures.stream()
            .map(CompletableFuture::join)
            .collect(Collectors.toList());
        
        // 验证所有响应
        for (Response response : responses) {
            response.then()
                .statusCode(200);
        }
        
        System.out.println("Batch requests completed successfully with " + responses.size() + " responses");
    }
    
    @Test
    @DisplayName("并发限流测试")
    public void testConcurrentRateLimiting() throws InterruptedException {
        // 每秒5个请求的速率限制
        int requestsPerSecond = 5;
        int totalRequests = 20;
        
        ExecutorService executorService = Executors.newFixedThreadPool(totalRequests);
        List<Future<Response>> futures = new ArrayList<>();
        
        long startTime = System.currentTimeMillis();
        
        // 提交任务
        for (int i = 0; i < totalRequests; i++) {
            final int requestId = i;
            
            // 计算延迟以实现速率限制
            long delayMillis = (i / requestsPerSecond) * 1000L;
            
            Future<Response> future = executorService.submit(() -> {
                try {
                    Thread.sleep(delayMillis);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                
                return given()
                    .spec(requestSpec)
                .when()
                    .get("/users")
                .then()
                    .extract()
                    .response();
            });
            
            futures.add(future);
        }
        
        // 等待所有请求完成
        List<Response> responses = new ArrayList<>();
        int successCount = 0;
        
        for (Future<Response> future : futures) {
            try {
                Response response = future.get();
                responses.add(response);
                
                if (response.getStatusCode() == 200) {
                    successCount++;
                }
            } catch (Exception e) {
                System.out.println("Request failed: " + e.getMessage());
            }
        }
        
        long endTime = System.currentTimeMillis();
        long totalTime = endTime - startTime;
        
        System.out.println("Rate Limiting Test Results:");
        System.out.println("Total Requests: " + totalRequests);
        System.out.println("Successful Requests: " + successCount);
        System.out.println("Success Rate: " + (100.0 * successCount / totalRequests) + "%");
        System.out.println("Total Execution Time: " + totalTime + "ms");
        System.out.println("Actual Requests Per Second: " + (totalRequests * 1000.0 / totalTime));
        
        executorService.shutdown();
    }
    
    @Test
    @DisplayName("长时间运行的并发测试")
    public void testLongRunningConcurrentRequests() throws InterruptedException {
        int testDurationSeconds = 10;
        int maxConcurrency = 5;
        
        ExecutorService executorService = Executors.newFixedThreadPool(maxConcurrency);
        List<Future<Void>> futures = new ArrayList<>();
        List<Long> responseTimes = new CopyOnWriteArrayList<>();
        AtomicInteger requestCount = new AtomicInteger(0);
        AtomicInteger successCount = new AtomicInteger(0);
        
        long testStartTime = System.currentTimeMillis();
        
        // 启动持续请求任务
        for (int i = 0; i < maxConcurrency; i++) {
            Future<Void> future = executorService.submit(() -> {
                long endTime = testStartTime + testDurationSeconds * 1000L;
                
                while (System.currentTimeMillis() < endTime) {
                    long requestStartTime = System.currentTimeMillis();
                    
                    try {
                        Response response = given()
                            .spec(requestSpec)
                        .when()
                            .get("/users")
                        .then()
                            .extract()
                            .response();
                        
                        long requestEndTime = System.currentTimeMillis();
                        responseTimes.add(requestEndTime - requestStartTime);
                        
                        requestCount.incrementAndGet();
                        
                        if (response.getStatusCode() == 200) {
                            successCount.incrementAndGet();
                        }
                    } catch (Exception e) {
                        // 忽略异常，继续执行
                        System.out.println("Request failed: " + e.getMessage());
                    }
                    
                    // 小延迟以避免过于频繁的请求
                    try {
                        Thread.sleep(100);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                        break;
                    }
                }
                
                return null;
            });
            
            futures.add(future);
        }
        
        // 等待所有任务完成
        for (Future<Void> future : futures) {
            future.get();
        }
        
        long testEndTime = System.currentTimeMillis();
        long actualTestDuration = testEndTime - testStartTime;
        
        // 计算统计信息
        long totalTime = responseTimes.stream().mapToLong(Long::longValue).sum();
        long averageTime = responseTimes.isEmpty() ? 0 : totalTime / responseTimes.size();
        long minTime = responseTimes.stream().mapToLong(Long::longValue).min().orElse(0);
        long maxTime = responseTimes.stream().mapToLong(Long::longValue).max().orElse(0);
        
        System.out.println("Long Running Test Results:");
        System.out.println("Test Duration: " + actualTestDuration + "ms");
        System.out.println("Total Requests: " + requestCount.get());
        System.out.println("Successful Requests: " + successCount.get());
        System.out.println("Success Rate: " + (100.0 * successCount.get() / requestCount.get()) + "%");
        System.out.println("Requests Per Second: " + (requestCount.get() * 1000.0 / actualTestDuration));
        System.out.println("Average Response Time: " + averageTime + "ms");
        System.out.println("Min Response Time: " + minTime + "ms");
        System.out.println("Max Response Time: " + maxTime + "ms");
        
        executorService.shutdown();
    }
    
    /**
     * 用于收集请求指标的内部类
     */
    private static class RequestMetrics {
        final int requestId;
        final int statusCode;
        final long responseTime;
        
        RequestMetrics(int requestId, int statusCode, long responseTime) {
            this.requestId = requestId;
            this.statusCode = statusCode;
            this.responseTime = responseTime;
        }
    }
}