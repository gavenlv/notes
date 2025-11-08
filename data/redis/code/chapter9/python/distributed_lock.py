#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis分布式锁实现
支持可重入锁、公平锁、读写锁等高级特性
"""

import redis
import time
import uuid
import threading
from typing import Optional


class RedisDistributedLock:
    """Redis分布式锁基础实现"""
    
    def __init__(self, redis_client: redis.Redis, lock_key: str, expire_time: int = 30):
        """
        初始化分布式锁
        
        Args:
            redis_client: Redis客户端实例
            lock_key: 锁的key
            expire_time: 锁的过期时间（秒）
        """
        self.redis = redis_client
        self.lock_key = lock_key
        self.expire_time = expire_time
        self.identifier = str(uuid.uuid4())  # 锁的唯一标识
        
    def acquire(self, timeout: int = 10) -> bool:
        """
        获取分布式锁
        
        Args:
            timeout: 获取锁的超时时间（秒）
            
        Returns:
            bool: 是否成功获取锁
        """
        end_time = time.time() + timeout
        
        while time.time() < end_time:
            # 使用SET命令的NX和EX参数实现原子操作
            result = self.redis.set(
                self.lock_key, 
                self.identifier, 
                ex=self.expire_time, 
                nx=True
            )
            
            if result:
                return True
            
            # 检查锁是否已经过期但没有被删除
            ttl = self.redis.ttl(self.lock_key)
            if ttl == -1:  # 没有设置过期时间
                self.redis.expire(self.lock_key, self.expire_time)
            
            time.sleep(0.1)  # 短暂休眠后重试
        
        return False
    
    def release(self) -> bool:
        """
        释放分布式锁
        
        Returns:
            bool: 是否成功释放锁
        """
        # 使用Lua脚本保证原子性操作
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        result = self.redis.eval(lua_script, 1, self.lock_key, self.identifier)
        return result == 1


class ReentrantDistributedLock(RedisDistributedLock):
    """可重入分布式锁"""
    
    def __init__(self, redis_client: redis.Redis, lock_key: str, expire_time: int = 30):
        super().__init__(redis_client, lock_key, expire_time)
        self.local_lock = threading.RLock()
        self.hold_count = 0
    
    def acquire(self, timeout: int = 10) -> bool:
        """获取可重入锁"""
        with self.local_lock:
            if self.hold_count > 0:
                # 当前线程已经持有锁
                self.hold_count += 1
                return True
            
            # 尝试获取Redis锁
            acquired = super().acquire(timeout)
            if acquired:
                self.hold_count = 1
            return acquired
    
    def release(self) -> bool:
        """释放可重入锁"""
        with self.local_lock:
            if self.hold_count == 0:
                return False
            
            self.hold_count -= 1
            if self.hold_count == 0:
                # 只有完全释放时才删除Redis锁
                return super().release()
            return True


class FairDistributedLock:
    """公平分布式锁（基于Redis List实现）"""
    
    def __init__(self, redis_client: redis.Redis, lock_key: str, expire_time: int = 30):
        self.redis = redis_client
        self.lock_key = lock_key
        self.queue_key = f"{lock_key}:queue"
        self.expire_time = expire_time
        self.identifier = str(uuid.uuid4())
    
    def acquire(self, timeout: int = 10) -> bool:
        """获取公平锁"""
        # 加入等待队列
        self.redis.rpush(self.queue_key, self.identifier)
        
        end_time = time.time() + timeout
        
        try:
            while time.time() < end_time:
                # 检查是否轮到当前请求
                queue_head = self.redis.lindex(self.queue_key, 0)
                
                if queue_head and queue_head.decode('utf-8') == self.identifier:
                    # 轮到当前请求，尝试获取锁
                    result = self.redis.set(
                        self.lock_key, 
                        self.identifier, 
                        ex=self.expire_time, 
                        nx=True
                    )
                    
                    if result:
                        return True
                
                time.sleep(0.1)
            
            return False
        finally:
            # 超时或异常时从队列中移除
            self.redis.lrem(self.queue_key, 0, self.identifier)
    
    def release(self) -> bool:
        """释放公平锁"""
        # 删除锁
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            redis.call("del", KEYS[1])
            redis.call("lpop", KEYS[2])  # 从队列头部移除
            return 1
        else
            return 0
        end
        """
        
        result = self.redis.eval(lua_script, 2, self.lock_key, self.queue_key, self.identifier)
        return result == 1


class ReadWriteDistributedLock:
    """读写分布式锁"""
    
    def __init__(self, redis_client: redis.Redis, lock_key: str, expire_time: int = 30):
        self.redis = redis_client
        self.lock_key = lock_key
        self.read_lock_key = f"{lock_key}:read"
        self.write_lock_key = f"{lock_key}:write"
        self.expire_time = expire_time
        self.identifier = str(uuid.uuid4())
    
    def acquire_read(self, timeout: int = 10) -> bool:
        """获取读锁"""
        end_time = time.time() + timeout
        
        while time.time() < end_time:
            # 检查是否有写锁
            write_lock = self.redis.get(self.write_lock_key)
            
            if not write_lock:
                # 没有写锁，可以获取读锁
                # 使用计数器记录读锁数量
                self.redis.incr(self.read_lock_key)
                self.redis.expire(self.read_lock_key, self.expire_time)
                return True
            
            time.sleep(0.1)
        
        return False
    
    def release_read(self) -> bool:
        """释放读锁"""
        read_count = self.redis.decr(self.read_lock_key)
        if read_count <= 0:
            self.redis.delete(self.read_lock_key)
        return True
    
    def acquire_write(self, timeout: int = 10) -> bool:
        """获取写锁"""
        end_time = time.time() + timeout
        
        while time.time() < end_time:
            # 检查是否有读锁或写锁
            read_count = int(self.redis.get(self.read_lock_key) or 0)
            write_lock = self.redis.get(self.write_lock_key)
            
            if read_count == 0 and not write_lock:
                # 可以获取写锁
                result = self.redis.set(
                    self.write_lock_key, 
                    self.identifier, 
                    ex=self.expire_time, 
                    nx=True
                )
                
                if result:
                    return True
            
            time.sleep(0.1)
        
        return False
    
    def release_write(self) -> bool:
        """释放写锁"""
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        result = self.redis.eval(lua_script, 1, self.write_lock_key, self.identifier)
        return result == 1


def test_distributed_lock():
    """测试分布式锁功能"""
    # 创建Redis连接
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    
    print("=== 基础分布式锁测试 ===")
    lock = RedisDistributedLock(r, "test:basic:lock", expire_time=10)
    
    # 测试获取和释放锁
    if lock.acquire():
        print("✓ 成功获取基础锁")
        
        # 测试锁的重入保护
        if not lock.acquire(timeout=1):
            print("✓ 锁的重入保护正常")
        
        if lock.release():
            print("✓ 成功释放基础锁")
    
    print("\n=== 可重入锁测试 ===")
    reentrant_lock = ReentrantDistributedLock(r, "test:reentrant:lock")
    
    # 测试可重入性
    if reentrant_lock.acquire():
        print("✓ 第一次获取可重入锁")
        
        if reentrant_lock.acquire():
            print("✓ 第二次获取可重入锁（重入成功）")
            
            reentrant_lock.release()
            print("✓ 第一次释放可重入锁")
            
            if reentrant_lock.release():
                print("✓ 第二次释放可重入锁（完全释放）")
    
    print("\n=== 公平锁测试 ===")
    fair_lock1 = FairDistributedLock(r, "test:fair:lock")
    fair_lock2 = FairDistributedLock(r, "test:fair:lock")
    
    # 简单测试公平锁
    if fair_lock1.acquire(timeout=2):
        print("✓ 第一个请求获取公平锁成功")
        fair_lock1.release()
    
    print("\n=== 读写锁测试 ===")
    rw_lock = ReadWriteDistributedLock(r, "test:rw:lock")
    
    # 测试读锁
    if rw_lock.acquire_read():
        print("✓ 获取读锁成功")
        
        # 测试写锁获取失败（因为有读锁）
        if not rw_lock.acquire_write(timeout=1):
            print("✓ 写锁获取被正确阻止（因为有读锁）")
        
        rw_lock.release_read()
        print("✓ 释放读锁成功")
    
    # 测试写锁
    if rw_lock.acquire_write():
        print("✓ 获取写锁成功")
        
        # 测试读锁获取失败（因为有写锁）
        if not rw_lock.acquire_read(timeout=1):
            print("✓ 读锁获取被正确阻止（因为有写锁）")
        
        rw_lock.release_write()
        print("✓ 释放写锁成功")
    
    print("\n=== 所有测试完成 ===")


if __name__ == "__main__":
    test_distributed_lock()