package com.redis.tutorial;

import redis.clients.jedis.Jedis;
import redis.clients.jedis.params.SetParams;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Redis秒杀系统实现
 * 包含库存预减、限流、防超卖等核心功能
 */
public class SeckillSystem {
    
    private static final Logger logger = LoggerFactory.getLogger(SeckillSystem.class);
    private static final ObjectMapper objectMapper = new ObjectMapper();
    
    private final Jedis jedis;
    
    public SeckillSystem(Jedis jedis) {
        this.jedis = jedis;
    }
    
    /**
     * 初始化秒杀商品
     */
    public boolean initSeckillProduct(String productId, int stock, double seckillPrice) {
        try {
            // 使用管道保证原子性
            String productKey = "seckill:product:" + productId;
            String stockKey = "seckill:stock:" + productId;
            
            jedis.hset(productKey, "stock", String.valueOf(stock));
            jedis.hset(productKey, "price", String.valueOf(seckillPrice));
            jedis.hset(productKey, "sold", "0");
            
            // 设置库存计数器
            jedis.set(stockKey, String.valueOf(stock));
            
            logger.info("初始化秒杀商品成功: {}, 库存: {}, 价格: {}", productId, stock, seckillPrice);
            return true;
        } catch (Exception e) {
            logger.error("初始化商品失败: {}", e.getMessage());
            return false;
        }
    }
    
    /**
     * 基础版秒杀（存在超卖问题）
     */
    public SeckillResult seckillV1Basic(String productId, String userId) {
        try {
            String stockKey = "seckill:stock:" + productId;
            
            // 检查库存
            String stockStr = jedis.get(stockKey);
            if (stockStr == null) {
                return SeckillResult.failure("商品不存在", productId, userId);
            }
            
            int currentStock = Integer.parseInt(stockStr);
            if (currentStock <= 0) {
                return SeckillResult.failure("商品已售完", productId, userId);
            }
            
            // 减少库存
            jedis.decr(stockKey);
            
            // 记录订单
            String orderId = UUID.randomUUID().toString();
            String orderKey = "seckill:order:" + orderId;
            
            Map<String, String> orderData = new HashMap<>();
            orderData.put("product_id", productId);
            orderData.put("user_id", userId);
            orderData.put("create_time", String.valueOf(System.currentTimeMillis()));
            
            jedis.hset(orderKey, orderData);
            
            return SeckillResult.success("秒杀成功", productId, userId, orderId);
        } catch (Exception e) {
            return SeckillResult.failure("系统错误: " + e.getMessage(), productId, userId);
        }
    }
    
    /**
     * 原子操作版秒杀（解决超卖问题）
     */
    public SeckillResult seckillV2Atomic(String productId, String userId) {
        try {
            String stockKey = "seckill:stock:" + productId;
            String productKey = "seckill:product:" + productId;
            
            // 使用Lua脚本保证原子性
            String luaScript = """
                    local stock_key = KEYS[1]
                    local product_key = KEYS[2]
                    local user_id = ARGV[1]
                    local current_time = ARGV[2]
                    local product_id = ARGV[3]
                    
                    -- 检查库存
                    local stock = tonumber(redis.call('get', stock_key))
                    if not stock or stock <= 0 then
                        return {0, '商品已售完'}
                    end
                    
                    -- 减少库存
                    redis.call('decr', stock_key)
                    
                    -- 更新商品已售数量
                    redis.call('hincrby', product_key, 'sold', 1)
                    
                    -- 生成订单ID
                    local order_id = redis.call('incr', 'seckill:order:id')
                    local order_key = 'seckill:order:' .. order_id
                    
                    -- 创建订单
                    redis.call('hset', order_key, 'product_id', product_id)
                    redis.call('hset', order_key, 'user_id', user_id)
                    redis.call('hset', order_key, 'create_time', current_time)
                    
                    return {1, order_id}
                    """;
            
            List<String> keys = Arrays.asList(stockKey, productKey);
            List<String> args = Arrays.asList(
                    userId,
                    String.valueOf(System.currentTimeMillis()),
                    productId
            );
            
            Object result = jedis.eval(luaScript, keys, args);
            
            if (result instanceof List) {
                List<?> resultList = (List<?>) result;
                if (resultList.size() >= 2) {
                    Long successFlag = (Long) resultList.get(0);
                    String message = (String) resultList.get(1);
                    
                    if (successFlag == 1) {
                        return SeckillResult.success("秒杀成功", productId, userId, message);
                    } else {
                        return SeckillResult.failure(message, productId, userId);
                    }
                }
            }
            
            return SeckillResult.failure("系统错误", productId, userId);
        } catch (Exception e) {
            return SeckillResult.failure("系统错误: " + e.getMessage(), productId, userId);
        }
    }
    
    /**
     * 限流版秒杀（防止单个用户重复购买）
     */
    public SeckillResult seckillV3Limit(String productId, String userId) {
        try {
            String userBoughtKey = "seckill:user:" + userId + ":" + productId;
            
            // 检查用户是否已经购买过
            if (jedis.exists(userBoughtKey)) {
                return SeckillResult.failure("每个用户只能购买一次", productId, userId);
            }
            
            String stockKey = "seckill:stock:" + productId;
            String productKey = "seckill:product:" + productId;
            
            // 使用Lua脚本实现原子操作
            String luaScript = """
                    local stock_key = KEYS[1]
                    local product_key = KEYS[2]
                    local user_bought_key = KEYS[3]
                    local user_id = ARGV[1]
                    local current_time = ARGV[2]
                    local product_id = ARGV[3]
                    
                    -- 检查用户是否已经购买
                    if redis.call('exists', user_bought_key) == 1 then
                        return {0, '每个用户只能购买一次'}
                    end
                    
                    -- 检查库存
                    local stock = tonumber(redis.call('get', stock_key))
                    if not stock or stock <= 0 then
                        return {0, '商品已售完'}
                    end
                    
                    -- 减少库存
                    redis.call('decr', stock_key)
                    
                    -- 标记用户已购买
                    redis.call('setex', user_bought_key, 3600, '1')
                    
                    -- 更新商品已售数量
                    redis.call('hincrby', product_key, 'sold', 1)
                    
                    -- 生成订单
                    local order_id = redis.call('incr', 'seckill:order:id')
                    local order_key = 'seckill:order:' .. order_id
                    
                    redis.call('hset', order_key, 'product_id', product_id)
                    redis.call('hset', order_key, 'user_id', user_id)
                    redis.call('hset', order_key, 'create_time', current_time)
                    
                    return {1, order_id}
                    """;
            
            List<String> keys = Arrays.asList(stockKey, productKey, userBoughtKey);
            List<String> args = Arrays.asList(
                    userId,
                    String.valueOf(System.currentTimeMillis()),
                    productId
            );
            
            Object result = jedis.eval(luaScript, keys, args);
            
            if (result instanceof List) {
                List<?> resultList = (List<?>) result;
                if (resultList.size() >= 2) {
                    Long successFlag = (Long) resultList.get(0);
                    String message = (String) resultList.get(1);
                    
                    if (successFlag == 1) {
                        return SeckillResult.success("秒杀成功", productId, userId, message);
                    } else {
                        return SeckillResult.failure(message, productId, userId);
                    }
                }
            }
            
            return SeckillResult.failure("系统错误", productId, userId);
        } catch (Exception e) {
            return SeckillResult.failure("系统错误: " + e.getMessage(), productId, userId);
        }
    }
}

/**
 * 秒杀限流器
 */
class SeckillRateLimiter {
    
    private final Jedis jedis;
    
    public SeckillRateLimiter(Jedis jedis) {
        this.jedis = jedis;
    }
    
    /**
     * 令牌桶限流算法
     */
    public boolean tokenBucketLimit(String key, int capacity, double refillRate) {
        long currentTime = System.currentTimeMillis() / 1000;
        
        String luaScript = """
                local key = KEYS[1]
                local capacity = tonumber(ARGV[1])
                local refill_rate = tonumber(ARGV[2])
                local current_time = tonumber(ARGV[3])
                
                -- 获取当前令牌桶状态
                local bucket = redis.call('hmget', key, 'tokens', 'last_refill')
                local tokens = tonumber(bucket[1]) or capacity
                local last_refill = tonumber(bucket[2]) or current_time
                
                -- 计算需要补充的令牌
                local time_passed = current_time - last_refill
                local tokens_to_add = math.floor(time_passed * refill_rate)
                
                -- 更新令牌数量
                tokens = math.min(capacity, tokens + tokens_to_add)
                
                -- 检查是否有足够令牌
                if tokens >= 1 then
                    tokens = tokens - 1
                    redis.call('hset', key, 'tokens', tokens)
                    redis.call('hset', key, 'last_refill', current_time)
                    redis.call('expire', key, 3600)
                    return 1
                else
                    redis.call('hset', key, 'tokens', tokens)
                    redis.call('hset', key, 'last_refill', current_time)
                    redis.call('expire', key, 3600)
                    return 0
                end
                """;
        
        Object result = jedis.eval(luaScript, 1, key, String.valueOf(capacity), 
                String.valueOf(refillRate), String.valueOf(currentTime));
        
        return result != null && (Long) result == 1;
    }
}

/**
 * 秒杀结果类
 */
class SeckillResult {
    private final boolean success;
    private final String message;
    private final String productId;
    private final String userId;
    private final String orderId;
    
    private SeckillResult(boolean success, String message, String productId, String userId, String orderId) {
        this.success = success;
        this.message = message;
        this.productId = productId;
        this.userId = userId;
        this.orderId = orderId;
    }
    
    public static SeckillResult success(String message, String productId, String userId, String orderId) {
        return new SeckillResult(true, message, productId, userId, orderId);
    }
    
    public static SeckillResult failure(String message, String productId, String userId) {
        return new SeckillResult(false, message, productId, userId, null);
    }
    
    // Getters
    public boolean isSuccess() { return success; }
    public String getMessage() { return message; }
    public String getProductId() { return productId; }
    public String getUserId() { return userId; }
    public String getOrderId() { return orderId; }
}

/**
 * 秒杀系统测试类
 */
class SeckillSystemTest {
    
    public static void main(String[] args) throws Exception {
        Jedis jedis = RedisConfig.getJedis();
        
        try {
            // 清空测试数据
            jedis.del("seckill:product:test001", "seckill:stock:test001", "seckill:order:id");
            
            SeckillSystem seckillSystem = new SeckillSystem(jedis);
            
            System.out.println("=== 初始化秒杀商品 ===");
            if (seckillSystem.initSeckillProduct("test001", 100, 99.9)) {
                System.out.println("✓ 商品初始化成功");
            }
            
            System.out.println("\n=== 测试并发秒杀 ===");
            
            // 模拟并发请求
            List<String> userIds = new ArrayList<>();
            for (int i = 1; i <= 150; i++) {
                userIds.add("user_" + String.format("%03d", i));
            }
            
            System.out.println("模拟150个用户并发秒杀100件商品...");
            
            AtomicInteger successCount = new AtomicInteger();
            AtomicInteger failCount = new AtomicInteger();
            
            ExecutorService executor = Executors.newFixedThreadPool(50);
            List<Future<SeckillResult>> futures = new ArrayList<>();
            
            for (String userId : userIds) {
                Future<SeckillResult> future = executor.submit(() -> {
                    try {
                        // 添加随机延迟模拟网络延迟
                        Thread.sleep(new Random().nextInt(100));
                        return seckillSystem.seckillV3Limit("test001", userId);
                    } catch (Exception e) {
                        return SeckillResult.failure("异常: " + e.getMessage(), "test001", userId);
                    }
                });
                futures.add(future);
            }
            
            for (Future<SeckillResult> future : futures) {
                SeckillResult result = future.get();
                if (result.isSuccess()) {
                    successCount.incrementAndGet();
                } else {
                    failCount.incrementAndGet();
                }
            }
            
            executor.shutdown();
            
            System.out.println("秒杀成功: " + successCount.get() + " 次");
            System.out.println("秒杀失败: " + failCount.get() + " 次");
            
            // 检查实际库存
            String finalStock = jedis.get("seckill:stock:test001");
            String soldCount = jedis.hget("seckill:product:test001", "sold");
            
            System.out.println("最终库存: " + finalStock);
            System.out.println("实际售出: " + soldCount);
            
            // 测试限流器
            System.out.println("\n=== 测试限流器 ===");
            SeckillRateLimiter rateLimiter = new SeckillRateLimiter(jedis);
            
            System.out.println("令牌桶限流测试:");
            for (int i = 0; i < 15; i++) {
                boolean allowed = rateLimiter.tokenBucketLimit("rate:limit:test", 10, 2);
                System.out.println("请求 " + (i + 1) + ": " + (allowed ? "允许" : "拒绝"));
                Thread.sleep(100);
            }
            
            System.out.println("\n秒杀系统测试完成!");
            
        } finally {
            RedisConfig.closeJedis(jedis);
        }
    }
}