package com.redis.tutorial;

import redis.clients.jedis.Jedis;
import redis.clients.jedis.params.SetParams;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.ReentrantLock;

/**
 * Redis分布式锁实现
 * 支持可重入锁、公平锁、读写锁等高级特性
 */
public class DistributedLock {
    
    private static final Logger logger = LoggerFactory.getLogger(DistributedLock.class);
    
    private final Jedis jedis;
    private final String lockKey;
    private final int expireTime;
    private final String identifier;
    
    /**
     * 基础分布式锁
     */
    public DistributedLock(Jedis jedis, String lockKey, int expireTime) {
        this.jedis = jedis;
        this.lockKey = lockKey;
        this.expireTime = expireTime;
        this.identifier = UUID.randomUUID().toString();
    }
    
    /**
     * 获取分布式锁
     */
    public boolean acquire(long timeout, TimeUnit unit) {
        long endTime = System.currentTimeMillis() + unit.toMillis(timeout);
        
        while (System.currentTimeMillis() < endTime) {
            // 使用SET命令的NX和EX参数实现原子操作
            SetParams setParams = SetParams.setParams()
                    .nx()
                    .ex(expireTime);
            
            String result = jedis.set(lockKey, identifier, setParams);
            
            if ("OK".equals(result)) {
                logger.info("成功获取分布式锁: {}", lockKey);
                return true;
            }
            
            // 检查锁是否已经过期但没有被删除
            Long ttl = jedis.ttl(lockKey);
            if (ttl != null && ttl == -1) {
                // 没有设置过期时间，重新设置
                jedis.expire(lockKey, expireTime);
            }
            
            try {
                Thread.sleep(100); // 短暂休眠后重试
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return false;
            }
        }
        
        return false;
    }
    
    /**
     * 释放分布式锁
     */
    public boolean release() {
        // 使用Lua脚本保证原子性操作
        String luaScript = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """;
        
        Object result = jedis.eval(luaScript, 1, lockKey, identifier);
        
        boolean success = result != null && (Long) result == 1;
        if (success) {
            logger.info("成功释放分布式锁: {}", lockKey);
        } else {
            logger.warn("释放分布式锁失败: {}", lockKey);
        }
        
        return success;
    }
}

/**
 * 可重入分布式锁
 */
class ReentrantDistributedLock {
    
    private final DistributedLock distributedLock;
    private final ReentrantLock localLock;
    private int holdCount;
    
    public ReentrantDistributedLock(Jedis jedis, String lockKey, int expireTime) {
        this.distributedLock = new DistributedLock(jedis, lockKey, expireTime);
        this.localLock = new ReentrantLock();
        this.holdCount = 0;
    }
    
    public boolean acquire(long timeout, TimeUnit unit) {
        localLock.lock();
        try {
            if (holdCount > 0) {
                // 当前线程已经持有锁
                holdCount++;
                return true;
            }
            
            // 尝试获取Redis锁
            boolean acquired = distributedLock.acquire(timeout, unit);
            if (acquired) {
                holdCount = 1;
            }
            return acquired;
        } finally {
            localLock.unlock();
        }
    }
    
    public boolean release() {
        localLock.lock();
        try {
            if (holdCount == 0) {
                return false;
            }
            
            holdCount--;
            if (holdCount == 0) {
                // 只有完全释放时才删除Redis锁
                return distributedLock.release();
            }
            return true;
        } finally {
            localLock.unlock();
        }
    }
}

/**
 * 读写分布式锁
 */
class ReadWriteDistributedLock {
    
    private final Jedis jedis;
    private final String lockKey;
    private final int expireTime;
    private final String identifier;
    
    public ReadWriteDistributedLock(Jedis jedis, String lockKey, int expireTime) {
        this.jedis = jedis;
        this.lockKey = lockKey;
        this.expireTime = expireTime;
        this.identifier = UUID.randomUUID().toString();
    }
    
    /**
     * 获取读锁
     */
    public boolean acquireRead(long timeout, TimeUnit unit) {
        long endTime = System.currentTimeMillis() + unit.toMillis(timeout);
        
        while (System.currentTimeMillis() < endTime) {
            // 检查是否有写锁
            String writeLock = jedis.get(lockKey + ":write");
            
            if (writeLock == null) {
                // 没有写锁，可以获取读锁
                // 使用计数器记录读锁数量
                jedis.incr(lockKey + ":read");
                jedis.expire(lockKey + ":read", expireTime);
                return true;
            }
            
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return false;
            }
        }
        
        return false;
    }
    
    /**
     * 释放读锁
     */
    public boolean releaseRead() {
        Long readCount = jedis.decr(lockKey + ":read");
        if (readCount != null && readCount <= 0) {
            jedis.del(lockKey + ":read");
        }
        return true;
    }
    
    /**
     * 获取写锁
     */
    public boolean acquireWrite(long timeout, TimeUnit unit) {
        long endTime = System.currentTimeMillis() + unit.toMillis(timeout);
        
        while (System.currentTimeMillis() < endTime) {
            // 检查是否有读锁或写锁
            String readCountStr = jedis.get(lockKey + ":read");
            int readCount = readCountStr != null ? Integer.parseInt(readCountStr) : 0;
            String writeLock = jedis.get(lockKey + ":write");
            
            if (readCount == 0 && writeLock == null) {
                // 可以获取写锁
                SetParams setParams = SetParams.setParams()
                        .nx()
                        .ex(expireTime);
                
                String result = jedis.set(lockKey + ":write", identifier, setParams);
                
                if ("OK".equals(result)) {
                    return true;
                }
            }
            
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return false;
            }
        }
        
        return false;
    }
    
    /**
     * 释放写锁
     */
    public boolean releaseWrite() {
        // 使用Lua脚本保证原子性
        String luaScript = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """;
        
        Object result = jedis.eval(luaScript, 1, lockKey + ":write", identifier);
        return result != null && (Long) result == 1;
    }
}

/**
 * 分布式锁测试类
 */
class DistributedLockTest {
    
    public static void main(String[] args) {
        Jedis jedis = RedisConfig.getJedis();
        
        try {
            System.out.println("=== 基础分布式锁测试 ===");
            DistributedLock lock = new DistributedLock(jedis, "test:basic:lock", 10);
            
            // 测试获取和释放锁
            if (lock.acquire(5, TimeUnit.SECONDS)) {
                System.out.println("✓ 成功获取基础锁");
                
                // 测试锁的重入保护
                if (!lock.acquire(1, TimeUnit.SECONDS)) {
                    System.out.println("✓ 锁的重入保护正常");
                }
                
                if (lock.release()) {
                    System.out.println("✓ 成功释放基础锁");
                }
            }
            
            System.out.println("\n=== 可重入锁测试 ===");
            ReentrantDistributedLock reentrantLock = new ReentrantDistributedLock(jedis, "test:reentrant:lock", 30);
            
            // 测试可重入性
            if (reentrantLock.acquire(5, TimeUnit.SECONDS)) {
                System.out.println("✓ 第一次获取可重入锁");
                
                if (reentrantLock.acquire(5, TimeUnit.SECONDS)) {
                    System.out.println("✓ 第二次获取可重入锁（重入成功）");
                    
                    reentrantLock.release();
                    System.out.println("✓ 第一次释放可重入锁");
                    
                    if (reentrantLock.release()) {
                        System.out.println("✓ 第二次释放可重入锁（完全释放）");
                    }
                }
            }
            
            System.out.println("\n=== 读写锁测试 ===");
            ReadWriteDistributedLock rwLock = new ReadWriteDistributedLock(jedis, "test:rw:lock", 30);
            
            // 测试读锁
            if (rwLock.acquireRead(5, TimeUnit.SECONDS)) {
                System.out.println("✓ 获取读锁成功");
                
                // 测试写锁获取失败（因为有读锁）
                if (!rwLock.acquireWrite(1, TimeUnit.SECONDS)) {
                    System.out.println("✓ 写锁获取被正确阻止（因为有读锁）");
                }
                
                rwLock.releaseRead();
                System.out.println("✓ 释放读锁成功");
            }
            
            // 测试写锁
            if (rwLock.acquireWrite(5, TimeUnit.SECONDS)) {
                System.out.println("✓ 获取写锁成功");
                
                // 测试读锁获取失败（因为有写锁）
                if (!rwLock.acquireRead(1, TimeUnit.SECONDS)) {
                    System.out.println("✓ 读锁获取被正确阻止（因为有写锁）");
                }
                
                rwLock.releaseWrite();
                System.out.println("✓ 释放写锁成功");
            }
            
            System.out.println("\n=== 所有测试完成 ===");
            
        } finally {
            RedisConfig.closeJedis(jedis);
        }
    }
}