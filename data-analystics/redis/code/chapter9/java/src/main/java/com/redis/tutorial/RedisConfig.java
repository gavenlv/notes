package com.redis.tutorial;

import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.JedisPoolConfig;

/**
 * Redis配置和连接管理
 */
public class RedisConfig {
    
    private static final String REDIS_HOST = "localhost";
    private static final int REDIS_PORT = 6379;
    private static final int REDIS_DATABASE = 0;
    private static final int MAX_TOTAL = 100;
    private static final int MAX_IDLE = 20;
    private static final int MIN_IDLE = 5;
    
    private static JedisPool jedisPool;
    
    static {
        initJedisPool();
    }
    
    /**
     * 初始化Jedis连接池
     */
    private static void initJedisPool() {
        JedisPoolConfig poolConfig = new JedisPoolConfig();
        poolConfig.setMaxTotal(MAX_TOTAL);
        poolConfig.setMaxIdle(MAX_IDLE);
        poolConfig.setMinIdle(MIN_IDLE);
        poolConfig.setTestOnBorrow(true);
        poolConfig.setTestOnReturn(true);
        poolConfig.setTestWhileIdle(true);
        
        jedisPool = new JedisPool(poolConfig, REDIS_HOST, REDIS_PORT, 2000, null, REDIS_DATABASE);
    }
    
    /**
     * 获取Jedis实例
     */
    public static Jedis getJedis() {
        return jedisPool.getResource();
    }
    
    /**
     * 关闭Jedis连接
     */
    public static void closeJedis(Jedis jedis) {
        if (jedis != null) {
            jedis.close();
        }
    }
    
    /**
     * 关闭连接池
     */
    public static void closePool() {
        if (jedisPool != null && !jedisPool.isClosed()) {
            jedisPool.close();
        }
    }
}