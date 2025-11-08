package com.example.restassured.performance;

import io.restassured.RestAssured;
import io.restassured.response.Response;
import org.junit.BeforeClass;
import org.junit.Test;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Random;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

import static io.restassured.RestAssured.*;

/**
 * 负载测试示例
 * 演示如何使用REST Assured进行负载测试和性能分析
 */
public class LoadTestExample {
    
    private static final int THREAD_COUNT = 10;
    private static final int REQUESTS_PER_THREAD = 20;
    private static final int TOTAL_REQUESTS = THREAD_COUNT * REQUESTS_PER_THREAD;
    
    @BeforeClass
    public static void setup() {
        RestAssured.baseURI = "https://jsonplaceholder.typicode.com";
        // 生产环境测试中，可能需要禁用日志以提高性能
        // RestAssured.enableLoggingOfRequestAndResponseIfValidationFails();
    }
    
    @Test
    public void testBasicLoadTest() throws InterruptedException {
        // 用于收集响应时间
        List<Long> responseTimes = Collections.synchronizedList(new ArrayList<>());
        AtomicInteger successCount = new AtomicInteger(0);
        AtomicInteger errorCount = new AtomicInteger(0);
        
        // 创建线程池
        ExecutorService executor = Executors.newFixedThreadPool(THREAD_COUNT);
        CountDownLatch latch = new CountDownLatch(THREAD_COUNT);
        
        // 记录开始时间
        long testStartTime = System.currentTimeMillis();
        
        // 启动多个线程执行请求
        for (int i = 0; i < THREAD_COUNT; i++) {
            final int threadId = i;
            executor.submit(() -> {
                try {
                    for (int j = 0; j < REQUESTS_PER_THREAD; j++) {
                        long requestStartTime = System.currentTimeMillis();
                        
                        try {
                            Response response = given()
                                .when()
                                .get("/posts/1");
                            
                            long requestEndTime = System.currentTimeMillis();
                            responseTimes.add(requestEndTime - requestStartTime);
                            
                            if (response.getStatusCode() == 200) {
                                successCount.incrementAndGet();
                            } else {
                                errorCount.incrementAndGet();
                            }
                        } catch (Exception e) {
                            errorCount.incrementAndGet();
                            System.err.println("Request failed in thread " + threadId + ": " + e.getMessage());
                        }
                    }
                } finally {
                    latch.countDown();
                }
            });
        }
        
        // 等待所有线程完成
        latch.await(60, TimeUnit.SECONDS);
        executor.shutdown();
        
        // 记录结束时间
        long testEndTime = System.currentTimeMillis();
        long totalTestTime = testEndTime - testStartTime;
        
        // 分析结果
        analyzeResults(responseTimes, successCount.get(), errorCount.get(), totalTestTime);
    }
    
    @Test
    public void testVaryingLoadTest() throws InterruptedException {
        System.out.println("=== Varying Load Test ===");
        
        // 测试不同级别的负载
        int[] threadCounts = {1, 5, 10, 20};
        
        for (int threadCount : threadCounts) {
            System.out.println("Testing with " + threadCount + " threads...");
            
            LoadTestResult result = runLoadTestWithThreads(threadCount, 30);
            printLoadTestResult(threadCount, result);
        }
    }
    
    @Test
    public void testBurstLoadTest() throws InterruptedException {
        System.out.println("=== Burst Load Test ===");
        
        // 突发负载测试：在短时间内发送大量请求
        List<Long> responseTimes = Collections.synchronizedList(new ArrayList<>());
        AtomicInteger successCount = new AtomicInteger(0);
        AtomicInteger errorCount = new AtomicInteger(0);
        
        // 创建大量线程同时发送请求
        ExecutorService executor = Executors.newFixedThreadPool(50);
        CountDownLatch latch = new CountDownLatch(50);
        
        long testStartTime = System.currentTimeMillis();
        
        for (int i = 0; i < 50; i++) {
            final int threadId = i;
            executor.submit(() -> {
                try {
                    long requestStartTime = System.currentTimeMillis();
                    
                    try {
                        Response response = given()
                            .when()
                            .get("/users/1");
                        
                        long requestEndTime = System.currentTimeMillis();
                        responseTimes.add(requestEndTime - requestStartTime);
                        
                        if (response.getStatusCode() == 200) {
                            successCount.incrementAndGet();
                        } else {
                            errorCount.incrementAndGet();
                        }
                    } catch (Exception e) {
                        errorCount.incrementAndGet();
                        System.err.println("Request failed in thread " + threadId + ": " + e.getMessage());
                    }
                } finally {
                    latch.countDown();
                }
            });
        }
        
        latch.await(60, TimeUnit.SECONDS);
        executor.shutdown();
        
        long testEndTime = System.currentTimeMillis();
        long totalTestTime = testEndTime - testStartTime;
        
        analyzeResults(responseTimes, successCount.get(), errorCount.get(), totalTestTime);
    }
    
    @Test
    public void testSustainedLoadTest() throws InterruptedException {
        System.out.println("=== Sustained Load Test ===");
        
        // 持续负载测试：在较长时间内保持稳定负载
        ExecutorService executor = Executors.newFixedThreadPool(THREAD_COUNT);
        List<Future<?>> futures = new ArrayList<>();
        
        // 持续运行2分钟的负载测试
        long testDuration = 2 * 60 * 1000; // 2分钟
        long testStartTime = System.currentTimeMillis();
        
        List<Long> responseTimes = Collections.synchronizedList(new ArrayList<>());
        AtomicInteger successCount = new AtomicInteger(0);
        AtomicInteger errorCount = new AtomicInteger(0);
        
        // 持续启动线程
        while (System.currentTimeMillis() - testStartTime < testDuration) {
            Future<?> future = executor.submit(() -> {
                try {
                    long requestStartTime = System.currentTimeMillis();
                    
                    try {
                        Response response = given()
                            .when()
                            .get("/posts/1");
                        
                        long requestEndTime = System.currentTimeMillis();
                        responseTimes.add(requestEndTime - requestStartTime);
                        
                        if (response.getStatusCode() == 200) {
                            successCount.incrementAndGet();
                        } else {
                            errorCount.incrementAndGet();
                        }
                    } catch (Exception e) {
                        errorCount.incrementAndGet();
                    }
                } catch (Exception e) {
                    // 忽略
                }
            });
            
            futures.add(future);
            
            // 每200ms启动一个新线程
            Thread.sleep(200);
        }
        
        // 等待所有线程完成
        for (Future<?> future : futures) {
            try {
                future.get(10, TimeUnit.SECONDS);
            } catch (Exception e) {
                // 忽略
            }
        }
        
        executor.shutdown();
        
        long testEndTime = System.currentTimeMillis();
        long totalTestTime = testEndTime - testStartTime;
        
        analyzeResults(responseTimes, successCount.get(), errorCount.get(), totalTestTime);
    }
    
    @Test
    public void testMixedLoadTest() throws InterruptedException {
        System.out.println("=== Mixed Load Test ===");
        
        // 混合负载测试：混合不同类型的请求
        
        ExecutorService executor = Executors.newFixedThreadPool(THREAD_COUNT);
        CountDownLatch latch = new CountDownLatch(THREAD_COUNT);
        
        List<Long> responseTimes = Collections.synchronizedList(new ArrayList<>());
        AtomicInteger successCount = new AtomicInteger(0);
        AtomicInteger errorCount = new AtomicInteger(0);
        
        // 随机选择不同端点进行测试
        String[] endpoints = {
            "/posts",
            "/users",
            "/comments",
            "/albums",
            "/photos"
        };
        
        Random random = new Random();
        
        long testStartTime = System.currentTimeMillis();
        
        for (int i = 0; i < THREAD_COUNT; i++) {
            final int threadId = i;
            executor.submit(() -> {
                try {
                    for (int j = 0; j < REQUESTS_PER_THREAD; j++) {
                        String endpoint = endpoints[random.nextInt(endpoints.length)];
                        
                        long requestStartTime = System.currentTimeMillis();
                        
                        try {
                            Response response = given()
                                .when()
                                .get(endpoint);
                            
                            long requestEndTime = System.currentTimeMillis();
                            responseTimes.add(requestEndTime - requestStartTime);
                            
                            if (response.getStatusCode() == 200) {
                                successCount.incrementAndGet();
                            } else {
                                errorCount.incrementAndGet();
                            }
                        } catch (Exception e) {
                            errorCount.incrementAndGet();
                            System.err.println("Request failed in thread " + threadId + ": " + e.getMessage());
                        }
                    }
                } finally {
                    latch.countDown();
                }
            });
        }
        
        latch.await(60, TimeUnit.SECONDS);
        executor.shutdown();
        
        long testEndTime = System.currentTimeMillis();
        long totalTestTime = testEndTime - testStartTime;
        
        analyzeResults(responseTimes, successCount.get(), errorCount.get(), totalTestTime);
    }
    
    private LoadTestResult runLoadTestWithThreads(int threadCount, int requestsPerThread) 
            throws InterruptedException {
        
        List<Long> responseTimes = Collections.synchronizedList(new ArrayList<>());
        AtomicInteger successCount = new AtomicInteger(0);
        AtomicInteger errorCount = new AtomicInteger(0);
        
        ExecutorService executor = Executors.newFixedThreadPool(threadCount);
        CountDownLatch latch = new CountDownLatch(threadCount);
        
        long testStartTime = System.currentTimeMillis();
        
        for (int i = 0; i < threadCount; i++) {
            executor.submit(() -> {
                try {
                    for (int j = 0; j < requestsPerThread; j++) {
                        long requestStartTime = System.currentTimeMillis();
                        
                        try {
                            Response response = given()
                                .when()
                                .get("/users/1");
                            
                            long requestEndTime = System.currentTimeMillis();
                            responseTimes.add(requestEndTime - requestStartTime);
                            
                            if (response.getStatusCode() == 200) {
                                successCount.incrementAndGet();
                            } else {
                                errorCount.incrementAndGet();
                            }
                        } catch (Exception e) {
                            errorCount.incrementAndGet();
                        }
                    }
                } finally {
                    latch.countDown();
                }
            });
        }
        
        latch.await(60, TimeUnit.SECONDS);
        executor.shutdown();
        
        long testEndTime = System.currentTimeMillis();
        long totalTestTime = testEndTime - testStartTime;
        
        return new LoadTestResult(
            threadCount * requestsPerThread,
            successCount.get(),
            errorCount.get(),
            responseTimes,
            totalTestTime
        );
    }
    
    private void analyzeResults(List<Long> responseTimes, int successCount, int errorCount, long totalTestTime) {
        // 计算响应时间统计
        Collections.sort(responseTimes);
        
        double averageResponseTime = responseTimes.stream().mapToLong(Long::longValue).average().orElse(0);
        long minResponseTime = responseTimes.isEmpty() ? 0 : responseTimes.get(0);
        long maxResponseTime = responseTimes.isEmpty() ? 0 : responseTimes.get(responseTimes.size() - 1);
        
        long p50 = getPercentile(responseTimes, 50);
        long p90 = getPercentile(responseTimes, 90);
        long p95 = getPercentile(responseTimes, 95);
        long p99 = getPercentile(responseTimes, 99);
        
        // 计算吞吐量
        double throughput = (successCount + errorCount) * 1000.0 / totalTestTime; // 请求/秒
        
        // 打印结果
        System.out.println("Load Test Results:");
        System.out.println("Total Requests: " + TOTAL_REQUESTS);
        System.out.println("Successful Requests: " + successCount);
        System.out.println("Failed Requests: " + errorCount);
        System.out.println("Success Rate: " + String.format("%.2f%%", (double) successCount / TOTAL_REQUESTS * 100));
        System.out.println("Total Test Time: " + totalTestTime + " ms");
        System.out.println("Throughput: " + String.format("%.2f", throughput) + " requests/sec");
        System.out.println();
        System.out.println("Response Time Statistics:");
        System.out.println("Average: " + String.format("%.2f", averageResponseTime) + " ms");
        System.out.println("Min: " + minResponseTime + " ms");
        System.out.println("Max: " + maxResponseTime + " ms");
        System.out.println("50th Percentile: " + p50 + " ms");
        System.out.println("90th Percentile: " + p90 + " ms");
        System.out.println("95th Percentile: " + p95 + " ms");
        System.out.println("99th Percentile: " + p99 + " ms");
        System.out.println("----------------------------------------");
    }
    
    private long getPercentile(List<Long> sortedList, int percentile) {
        if (sortedList.isEmpty()) {
            return 0;
        }
        
        int index = (int) Math.ceil(percentile / 100.0 * sortedList.size()) - 1;
        index = Math.max(0, Math.min(index, sortedList.size() - 1));
        
        return sortedList.get(index);
    }
    
    private void printLoadTestResult(int threadCount, LoadTestResult result) {
        double successRate = (double) result.getSuccessCount() / result.getTotalRequests() * 100;
        double throughput = result.getTotalRequests() * 1000.0 / result.getTotalTestTime();
        
        System.out.println("  Threads: " + threadCount);
        System.out.println("  Total Requests: " + result.getTotalRequests());
        System.out.println("  Success Rate: " + String.format("%.2f%%", successRate));
        System.out.println("  Throughput: " + String.format("%.2f", throughput) + " req/sec");
        System.out.println("  Avg Response Time: " + String.format("%.2f", result.getAverageResponseTime()) + " ms");
        System.out.println("  95th Percentile: " + result.getP95ResponseTime() + " ms");
        System.out.println();
    }
    
    /**
     * 负载测试结果数据类
     */
    private static class LoadTestResult {
        private final int totalRequests;
        private final int successCount;
        private final int errorCount;
        private final List<Long> responseTimes;
        private final long totalTestTime;
        
        public LoadTestResult(int totalRequests, int successCount, int errorCount, 
                              List<Long> responseTimes, long totalTestTime) {
            this.totalRequests = totalRequests;
            this.successCount = successCount;
            this.errorCount = errorCount;
            this.responseTimes = responseTimes;
            this.totalTestTime = totalTestTime;
        }
        
        public double getAverageResponseTime() {
            return responseTimes.stream().mapToLong(Long::longValue).average().orElse(0);
        }
        
        public long getP95ResponseTime() {
            if (responseTimes.isEmpty()) {
                return 0;
            }
            
            List<Long> sortedTimes = new ArrayList<>(responseTimes);
            Collections.sort(sortedTimes);
            
            int index = (int) Math.ceil(95.0 / 100.0 * sortedTimes.size()) - 1;
            index = Math.max(0, Math.min(index, sortedTimes.size() - 1));
            
            return sortedTimes.get(index);
        }
        
        public int getTotalRequests() { return totalRequests; }
        public int getSuccessCount() { return successCount; }
        public int getErrorCount() { return errorCount; }
        public List<Long> getResponseTimes() { return responseTimes; }
        public long getTotalTestTime() { return totalTestTime; }
    }
}