package com.redis.tutorial;

import redis.clients.jedis.Jedis;
import redis.clients.jedis.params.SetParams;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

/**
 * Redis缓存模式实现
 * 包含缓存穿透、雪崩、击穿等问题的解决方案
 */
public class CachePatterns {
    
    private static final Logger logger = LoggerFactory.getLogger(CachePatterns.class);
    private static final ObjectMapper objectMapper = new ObjectMapper();
    
    private final Jedis jedis;
    private final String prefix;
    
    public CachePatterns(Jedis jedis, String prefix) {
        this.jedis = jedis;
        this.prefix = prefix;
    }
    
    public CachePatterns(Jedis jedis) {
        this(jedis, "cache:");
    }
    
    /**
     * 获取完整的缓存key
     */
    private String getKey(String key) {
        return prefix + key;
    }
    
    /**
     * 设置缓存
     */
    public boolean set(String key, Object value, int expireSeconds) {
        try {
            String cacheKey = getKey(key);
            String serializedValue = objectMapper.writeValueAsString(value);
            
            SetParams setParams = SetParams.setParams().ex(expireSeconds);
            String result = jedis.set(cacheKey, serializedValue, setParams);
            
            return "OK".equals(result);
        } catch (JsonProcessingException e) {
            logger.error("缓存序列化失败: {}", e.getMessage());
            return false;
        }
    }
    
    /**
     * 获取缓存
     */
    public <T> T get(String key, Class<T> clazz) {
        try {
            String cacheKey = getKey(key);
            String cachedData = jedis.get(cacheKey);
            
            if (cachedData == null) {
                return null;
            }
            
            return objectMapper.readValue(cachedData, clazz);
        } catch (Exception e) {
            logger.error("缓存反序列化失败: {}", e.getMessage());
            return null;
        }
    }
    
    /**
     * 删除缓存
     */
    public boolean delete(String key) {
        String cacheKey = getKey(key);
        Long result = jedis.del(cacheKey);
        return result != null && result > 0;
    }
}

/**
 * 布隆过滤器缓存（解决缓存穿透）
 */
class BloomFilterCache extends CachePatterns {
    
    private final String bloomPrefix;
    private final int bitSize;
    private final int hashCount;
    
    public BloomFilterCache(Jedis jedis, String prefix, String bloomPrefix, int bitSize, int hashCount) {
        super(jedis, prefix);
        this.bloomPrefix = bloomPrefix;
        this.bitSize = bitSize;
        this.hashCount = hashCount;
    }
    
    public BloomFilterCache(Jedis jedis) {
        this(jedis, "cache:", "bloom:", 1 << 20, 5);
    }
    
    /**
     * 计算布隆过滤器的多个hash值
     */
    private List<Integer> getHashValues(String key) {
        List<Integer> hashValues = new ArrayList<>();
        
        for (int i = 0; i < hashCount; i++) {
            // 使用不同的盐值计算hash
            String saltedKey = key + ":" + i;
            int hashVal = Math.abs(saltedKey.hashCode()) % bitSize;
            hashValues.add(hashVal);
        }
        
        return hashValues;
    }
    
    /**
     * 将key添加到布隆过滤器
     */
    public boolean addToBloom(String key) {
        String bloomKey = bloomPrefix + "filter";
        List<Integer> hashValues = getHashValues(key);
        
        // 使用管道批量设置位
        var pipeline = jedis.pipelined();
        for (int hashVal : hashValues) {
            pipeline.setbit(bloomKey, hashVal, true);
        }
        
        pipeline.sync();
        return true;
    }
    
    /**
     * 检查key是否可能在布隆过滤器中
     */
    public boolean existsInBloom(String key) {
        String bloomKey = bloomPrefix + "filter";
        List<Integer> hashValues = getHashValues(key);
        
        // 使用管道批量检查位
        var pipeline = jedis.pipelined();
        for (int hashVal : hashValues) {
            pipeline.getbit(bloomKey, hashVal);
        }
        
        List<Object> results = pipeline.syncAndReturnAll();
        
        // 所有位都为1才认为可能存在
        for (Object result : results) {
            if (!(result instanceof Boolean) || !(Boolean) result) {
                return false;
            }
        }
        
        return true;
    }
    
    /**
     * 带缓存穿透保护的获取方法
     */
    public <T> T getWithPenetrationProtection(String key, Class<T> clazz, DataFetcher<T> dataFetcher) {
        // 先检查布隆过滤器
        if (!existsInBloom(key)) {
            logger.info("Key {} 不在布隆过滤器中，直接返回空", key);
            return null;
        }
        
        // 检查缓存
        T cachedData = get(key, clazz);
        if (cachedData != null) {
            return cachedData;
        }
        
        // 从数据源获取数据
        T data = dataFetcher.fetch(key);
        
        if (data != null) {
            // 数据存在，设置缓存
            set(key, data, 3600);
            // 添加到布隆过滤器
            addToBloom(key);
        } else {
            // 数据不存在，设置空值缓存（短时间）
            set(key, "__NULL__", 300); // 5分钟
        }
        
        return data;
    }
}

/**
 * 缓存击穿保护（热点key失效保护）
 */
class CacheBreakdownProtection extends CachePatterns {
    
    private final Map<String, Lock> localLocks = new ConcurrentHashMap<>();
    private final Lock lockLock = new ReentrantLock();
    
    public CacheBreakdownProtection(Jedis jedis, String prefix) {
        super(jedis, prefix);
    }
    
    public CacheBreakdownProtection(Jedis jedis) {
        super(jedis);
    }
    
    /**
     * 获取或创建本地锁
     */
    private Lock getLocalLock(String key) {
        lockLock.lock();
        try {
            return localLocks.computeIfAbsent(key, k -> new ReentrantLock());
        } finally {
            lockLock.unlock();
        }
    }
    
    /**
     * 带缓存击穿保护的获取方法
     */
    public <T> T getWithBreakdownProtection(String key, Class<T> clazz, 
                                           DataFetcher<T> dataFetcher, int expireSeconds) {
        // 第一次尝试获取缓存
        T cachedData = get(key, clazz);
        if (cachedData != null) {
            return cachedData;
        }
        
        // 获取本地锁
        Lock localLock = getLocalLock(key);
        
        // 尝试获取分布式锁
        String lockKey = "lock:" + key;
        boolean lockAcquired = false;
        
        try {
            // 先尝试获取本地锁（避免不必要的分布式锁竞争）
            if (localLock.tryLock()) {
                try {
                    // 再次检查缓存（双重检查锁定）
                    cachedData = get(key, clazz);
                    if (cachedData != null) {
                        return cachedData;
                    }
                    
                    // 获取分布式锁
                    lockAcquired = acquireDistributedLock(lockKey, 10);
                    
                    if (lockAcquired) {
                        // 第三次检查缓存
                        cachedData = get(key, clazz);
                        if (cachedData != null) {
                            return cachedData;
                        }
                        
                        // 从数据源获取数据
                        T data = dataFetcher.fetch(key);
                        
                        if (data != null) {
                            // 设置缓存
                            set(key, data, expireSeconds);
                        }
                        
                        return data;
                    } else {
                        // 等待其他线程加载数据
                        for (int i = 0; i < 50; i++) { // 最多等待5秒
                            try {
                                TimeUnit.MILLISECONDS.sleep(100);
                            } catch (InterruptedException e) {
                                Thread.currentThread().interrupt();
                                break;
                            }
                            
                            cachedData = get(key, clazz);
                            if (cachedData != null) {
                                return cachedData;
                            }
                        }
                        
                        // 超时后直接查询数据源
                        return dataFetcher.fetch(key);
                    }
                } finally {
                    localLock.unlock();
                }
            } else {
                // 等待本地锁
                localLock.lock();
                try {
                    // 再次检查缓存
                    cachedData = get(key, clazz);
                    return cachedData != null ? cachedData : dataFetcher.fetch(key);
                } finally {
                    localLock.unlock();
                }
            }
        } finally {
            if (lockAcquired) {
                releaseDistributedLock(lockKey);
            }
            
            // 清理本地锁（可选）
            lockLock.lock();
            try {
                localLocks.remove(key);
            } finally {
                lockLock.unlock();
            }
        }
    }
    
    /**
     * 获取分布式锁
     */
    private boolean acquireDistributedLock(String lockKey, int timeoutSeconds) {
        long endTime = System.currentTimeMillis() + TimeUnit.SECONDS.toMillis(timeoutSeconds);
        String identifier = String.valueOf(System.currentTimeMillis());
        
        while (System.currentTimeMillis() < endTime) {
            SetParams setParams = SetParams.setParams().nx().ex(30);
            String result = jedis.set(lockKey, identifier, setParams);
            
            if ("OK".equals(result)) {
                return true;
            }
            
            try {
                TimeUnit.MILLISECONDS.sleep(100);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
        
        return false;
    }
    
    /**
     * 释放分布式锁
     */
    private boolean releaseDistributedLock(String lockKey) {
        try {
            jedis.del(lockKey);
            return true;
        } catch (Exception e) {
            return false;
        }
    }
}

/**
 * 缓存雪崩保护（大量缓存同时失效保护）
 */
class CacheAvalancheProtection extends CachePatterns {
    
    public CacheAvalancheProtection(Jedis jedis, String prefix) {
        super(jedis, prefix);
    }
    
    public CacheAvalancheProtection(Jedis jedis) {
        super(jedis);
    }
    
    /**
     * 设置带雪崩保护的缓存
     */
    public boolean setWithAvalancheProtection(String key, Object value, 
                                             int baseExpireSeconds, int randomRangeSeconds) {
        // 添加随机偏移，避免同时失效
        int randomOffset = Math.abs(key.hashCode()) % randomRangeSeconds;
        int actualExpireSeconds = baseExpireSeconds + randomOffset;
        
        return set(key, value, actualExpireSeconds);
    }
    
    /**
     * 批量设置带雪崩保护的缓存
     */
    public boolean batchSetWithAvalancheProtection(Map<String, Object> dataMap, 
                                                  int baseExpireSeconds, int randomRangeSeconds) {
        try {
            var pipeline = jedis.pipelined();
            
            for (Map.Entry<String, Object> entry : dataMap.entrySet()) {
                String cacheKey = getKey(entry.getKey());
                int randomOffset = Math.abs(entry.getKey().hashCode()) % randomRangeSeconds;
                int actualExpireSeconds = baseExpireSeconds + randomOffset;
                
                try {
                    String serializedValue = objectMapper.writeValueAsString(entry.getValue());
                    pipeline.setex(cacheKey, actualExpireSeconds, serializedValue);
                } catch (JsonProcessingException e) {
                    logger.error("缓存序列化失败: {}", e.getMessage());
                }
            }
            
            pipeline.sync();
            return true;
        } catch (Exception e) {
            logger.error("批量设置缓存失败: {}", e.getMessage());
            return false;
        }
    }
}

/**
 * 多级缓存（本地缓存 + Redis缓存）
 */
class MultiLevelCache<T> {
    
    private final CachePatterns redisCache;
    private final Map<String, CacheEntry<T>> localCache = new ConcurrentHashMap<>();
    private final int localCacheSize;
    private final long localCacheTtl;
    private final Map<String, Long> accessTimes = new ConcurrentHashMap<>();
    
    public MultiLevelCache(Jedis jedis, int localCacheSize, long localCacheTtl) {
        this.redisCache = new CachePatterns(jedis);
        this.localCacheSize = localCacheSize;
        this.localCacheTtl = localCacheTtl;
    }
    
    /**
     * 从多级缓存中获取数据
     */
    public T get(String key, DataFetcher<T> dataFetcher) {
        long currentTime = System.currentTimeMillis();
        
        // 第一级：本地缓存
        CacheEntry<T> cacheEntry = localCache.get(key);
        if (cacheEntry != null) {
            if (currentTime - cacheEntry.timestamp < localCacheTtl) {
                logger.info("从本地缓存获取: {}", key);
                accessTimes.put(key, currentTime);
                return cacheEntry.data;
            } else {
                // 本地缓存过期
                localCache.remove(key);
                accessTimes.remove(key);
            }
        }
        
        // 第二级：Redis缓存
        @SuppressWarnings("unchecked")
        T cachedData = (T) redisCache.get(key, Object.class);
        if (cachedData != null) {
            logger.info("从Redis缓存获取: {}", key);
            // 更新本地缓存
            updateLocalCache(key, cachedData, currentTime);
            return cachedData;
        }
        
        // 第三级：数据库查询
        logger.info("缓存未命中，查询数据库: {}", key);
        T data = dataFetcher.fetch(key);
        
        if (data != null) {
            // 更新Redis缓存
            redisCache.set(key, data, 3600);
            // 更新本地缓存
            updateLocalCache(key, data, currentTime);
        }
        
        return data;
    }
    
    /**
     * 更新本地缓存
     */
    private void updateLocalCache(String key, T data, long timestamp) {
        // 检查缓存大小，如果超过限制则清理最久未使用的
        if (localCache.size() >= localCacheSize) {
            // 找到最久未使用的key
            String oldestKey = accessTimes.entrySet().stream()
                    .min(Map.Entry.comparingByValue())
                    .map(Map.Entry::getKey)
                    .orElse(null);
                    
            if (oldestKey != null) {
                localCache.remove(oldestKey);
                accessTimes.remove(oldestKey);
            }
        }
        
        localCache.put(key, new CacheEntry<>(data, timestamp));
        accessTimes.put(key, timestamp);
    }
    
    /**
     * 失效缓存
     */
    public void invalidate(String key) {
        localCache.remove(key);
        accessTimes.remove(key);
        redisCache.delete(key);
    }
    
    /**
     * 缓存条目
     */
    private static class CacheEntry<T> {
        final T data;
        final long timestamp;
        
        CacheEntry(T data, long timestamp) {
            this.data = data;
            this.timestamp = timestamp;
        }
    }
}

/**
 * 数据获取器接口
 */
@FunctionalInterface
interface DataFetcher<T> {
    T fetch(String key);
}

/**
 * 缓存模式测试类
 */
class CachePatternsTest {
    
    public static void main(String[] args) {
        Jedis jedis = RedisConfig.getJedis();
        
        try {
            System.out.println("=== 测试基础缓存 ===");
            CachePatterns basicCache = new CachePatterns(jedis);
            
            // 测试基础缓存操作
            Map<String, Object> testData = Map.of("name", "test", "value", 123);
            basicCache.set("test_key", testData, 3600);
            
            @SuppressWarnings("unchecked")
            Map<String, Object> result = (Map<String, Object>) basicCache.get("test_key", Object.class);
            System.out.println("基础缓存获取结果: " + result);
            
            System.out.println("\n=== 测试布隆过滤器缓存 ===");
            BloomFilterCache bloomCache = new BloomFilterCache(jedis);
            
            // 模拟数据源
            DataFetcher<String> mockDbFetcher = key -> {
                if (key.startsWith("exist_")) {
                    return "data_for_" + key;
                }
                return null;
            };
            
            // 测试存在的数据
            String result1 = bloomCache.getWithPenetrationProtection("exist_001", String.class, mockDbFetcher);
            System.out.println("存在数据查询结果: " + result1);
            
            // 测试不存在的数据
            String result2 = bloomCache.getWithPenetrationProtection("not_exist_001", String.class, mockDbFetcher);
            System.out.println("不存在数据查询结果: " + result2);
            
            System.out.println("\n=== 测试缓存雪崩保护 ===");
            CacheAvalancheProtection avalancheCache = new CacheAvalancheProtection(jedis);
            
            // 批量设置缓存
            Map<String, Object> testData2 = new HashMap<>();
            for (int i = 0; i < 10; i++) {
                testData2.put("key_" + i, "value_" + i);
            }
            avalancheCache.batchSetWithAvalancheProtection(testData2, 3600, 600);
            
            System.out.println("批量缓存设置完成");
            
            System.out.println("\n=== 测试多级缓存 ===");
            MultiLevelCache<String> multiCache = new MultiLevelCache<>(jedis, 5, TimeUnit.MINUTES.toMillis(5));
            
            DataFetcher<String> simpleFetcher = key -> "fetched_" + key;
            
            // 第一次访问
            String result3 = multiCache.get("test_key", simpleFetcher);
            System.out.println("第一次访问结果: " + result3);
            
            // 第二次访问（应该从本地缓存获取）
            String result4 = multiCache.get("test_key", simpleFetcher);
            System.out.println("第二次访问结果: " + result4);
            
            System.out.println("\n缓存模式测试完成!");
            
        } finally {
            RedisConfig.closeJedis(jedis);
        }
    }
}