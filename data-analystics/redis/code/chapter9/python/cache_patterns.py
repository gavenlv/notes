#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis缓存模式实现
包含缓存穿透、雪崩、击穿等问题的解决方案
"""

import redis
import time
import json
import hashlib
from typing import Any, Optional, Callable
from threading import Lock


class RedisCache:
    """Redis缓存基础类"""
    
    def __init__(self, redis_client: redis.Redis, prefix: str = "cache:"):
        self.redis = redis_client
        self.prefix = prefix
    
    def get_key(self, key: str) -> str:
        """生成完整的缓存key"""
        return f"{self.prefix}{key}"
    
    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """设置缓存"""
        try:
            cache_key = self.get_key(key)
            serialized_value = json.dumps(value)
            return self.redis.setex(cache_key, expire, serialized_value)
        except Exception as e:
            print(f"缓存设置失败: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            cache_key = self.get_key(key)
            cached_data = self.redis.get(cache_key)
            
            if cached_data is None:
                return None
            
            return json.loads(cached_data)
        except Exception as e:
            print(f"缓存获取失败: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            cache_key = self.get_key(key)
            return self.redis.delete(cache_key) > 0
        except Exception as e:
            print(f"缓存删除失败: {e}")
            return False


class BloomFilterCache(RedisCache):
    """布隆过滤器缓存（解决缓存穿透）"""
    
    def __init__(self, redis_client: redis.Redis, prefix: str = "cache:", 
                 bloom_prefix: str = "bloom:", bit_size: int = 2**20, hash_count: int = 5):
        super().__init__(redis_client, prefix)
        self.bloom_prefix = bloom_prefix
        self.bit_size = bit_size
        self.hash_count = hash_count
    
    def _get_hash_values(self, key: str) -> list:
        """计算布隆过滤器的多个hash值"""
        hash_values = []
        
        for i in range(self.hash_count):
            # 使用不同的盐值计算hash
            salted_key = f"{key}:{i}"
            hash_val = int(hashlib.md5(salted_key.encode()).hexdigest(), 16) % self.bit_size
            hash_values.append(hash_val)
        
        return hash_values
    
    def add_to_bloom(self, key: str) -> bool:
        """将key添加到布隆过滤器"""
        bloom_key = f"{self.bloom_prefix}filter"
        hash_values = self._get_hash_values(key)
        
        # 使用管道批量设置位
        pipeline = self.redis.pipeline()
        for hash_val in hash_values:
            pipeline.setbit(bloom_key, hash_val, 1)
        
        pipeline.execute()
        return True
    
    def exists_in_bloom(self, key: str) -> bool:
        """检查key是否可能在布隆过滤器中"""
        bloom_key = f"{self.bloom_prefix}filter"
        hash_values = self._get_hash_values(key)
        
        # 使用管道批量检查位
        pipeline = self.redis.pipeline()
        for hash_val in hash_values:
            pipeline.getbit(bloom_key, hash_val)
        
        results = pipeline.execute()
        
        # 所有位都为1才认为可能存在
        return all(results)
    
    def get_with_penetration_protection(self, key: str, data_fetcher: Callable) -> Optional[Any]:
        """带缓存穿透保护的获取方法"""
        # 先检查布隆过滤器
        if not self.exists_in_bloom(key):
            print(f"Key {key} 不在布隆过滤器中，直接返回空")
            return None
        
        # 检查缓存
        cached_data = self.get(key)
        if cached_data is not None:
            return cached_data
        
        # 从数据源获取数据
        data = data_fetcher(key)
        
        if data is not None:
            # 数据存在，设置缓存
            self.set(key, data)
            # 添加到布隆过滤器
            self.add_to_bloom(key)
        else:
            # 数据不存在，设置空值缓存（短时间）
            self.set(key, "__NULL__", expire=300)  # 5分钟
        
        return data


class CacheBreakdownProtection(RedisCache):
    """缓存击穿保护（热点key失效保护）"""
    
    def __init__(self, redis_client: redis.Redis, prefix: str = "cache:"):
        super().__init__(redis_client, prefix)
        self.local_locks = {}  # 本地锁字典
        self.lock_lock = Lock()  # 保护本地锁字典的锁
    
    def get_local_lock(self, key: str) -> Lock:
        """获取或创建本地锁"""
        with self.lock_lock:
            if key not in self.local_locks:
                self.local_locks[key] = Lock()
            return self.local_locks[key]
    
    def get_with_breakdown_protection(self, key: str, data_fetcher: Callable, 
                                    expire: int = 3600) -> Optional[Any]:
        """带缓存击穿保护的获取方法"""
        # 第一次尝试获取缓存
        cached_data = self.get(key)
        if cached_data is not None:
            return cached_data
        
        # 获取本地锁
        local_lock = self.get_local_lock(key)
        
        # 尝试获取分布式锁
        lock_key = f"lock:{key}"
        lock_acquired = False
        
        try:
            # 先尝试获取本地锁（避免不必要的分布式锁竞争）
            if local_lock.acquire(blocking=False):
                # 再次检查缓存（双重检查锁定）
                cached_data = self.get(key)
                if cached_data is not None:
                    return cached_data
                
                # 获取分布式锁
                lock_acquired = self._acquire_distributed_lock(lock_key)
                
                if lock_acquired:
                    # 第三次检查缓存
                    cached_data = self.get(key)
                    if cached_data is not None:
                        return cached_data
                    
                    # 从数据源获取数据
                    data = data_fetcher(key)
                    
                    if data is not None:
                        # 设置缓存
                        self.set(key, data, expire)
                    
                    return data
                else:
                    # 等待其他线程加载数据
                    for i in range(50):  # 最多等待5秒
                        time.sleep(0.1)
                        cached_data = self.get(key)
                        if cached_data is not None:
                            return cached_data
                    
                    # 超时后直接查询数据源
                    return data_fetcher(key)
            else:
                # 等待本地锁
                local_lock.acquire()
                try:
                    # 再次检查缓存
                    cached_data = self.get(key)
                    return cached_data if cached_data is not None else data_fetcher(key)
                finally:
                    local_lock.release()
        
        finally:
            if lock_acquired:
                self._release_distributed_lock(lock_key)
            
            # 清理本地锁（可选）
            with self.lock_lock:
                if key in self.local_locks:
                    try:
                        local_lock.release()
                        del self.local_locks[key]
                    except:
                        pass
    
    def _acquire_distributed_lock(self, lock_key: str, timeout: int = 10) -> bool:
        """获取分布式锁"""
        end_time = time.time() + timeout
        identifier = str(time.time())
        
        while time.time() < end_time:
            if self.redis.set(lock_key, identifier, ex=30, nx=True):
                return True
            time.sleep(0.1)
        
        return False
    
    def _release_distributed_lock(self, lock_key: str) -> bool:
        """释放分布式锁"""
        try:
            self.redis.delete(lock_key)
            return True
        except:
            return False


class CacheAvalancheProtection(RedisCache):
    """缓存雪崩保护（大量缓存同时失效保护）"""
    
    def __init__(self, redis_client: redis.Redis, prefix: str = "cache:"):
        super().__init__(redis_client, prefix)
    
    def set_with_avalanche_protection(self, key: str, value: Any, 
                                     base_expire: int = 3600, 
                                     random_range: int = 600) -> bool:
        """
        设置带雪崩保护的缓存
        
        Args:
            base_expire: 基础过期时间
            random_range: 随机范围（秒）
        """
        # 添加随机偏移，避免同时失效
        random_offset = hash(key) % random_range  # 使用key的hash确保一致性
        actual_expire = base_expire + random_offset
        
        return self.set(key, value, actual_expire)
    
    def batch_set_with_avalanche_protection(self, data_dict: dict, 
                                           base_expire: int = 3600, 
                                           random_range: int = 600) -> bool:
        """批量设置带雪崩保护的缓存"""
        try:
            pipeline = self.redis.pipeline()
            
            for key, value in data_dict.items():
                cache_key = self.get_key(key)
                random_offset = hash(key) % random_range
                actual_expire = base_expire + random_offset
                serialized_value = json.dumps(value)
                
                pipeline.setex(cache_key, actual_expire, serialized_value)
            
            pipeline.execute()
            return True
        except Exception as e:
            print(f"批量设置缓存失败: {e}")
            return False


class MultiLevelCache:
    """多级缓存（本地缓存 + Redis缓存）"""
    
    def __init__(self, redis_client: redis.Redis, local_cache_size: int = 1000):
        self.redis_cache = RedisCache(redis_client)
        self.local_cache = {}
        self.local_cache_size = local_cache_size
        self.local_cache_ttl = 300  # 本地缓存5分钟
        self.access_times = {}
    
    def get(self, key: str, data_fetcher: Callable) -> Optional[Any]:
        """从多级缓存中获取数据"""
        current_time = time.time()
        
        # 第一级：本地缓存
        if key in self.local_cache:
            timestamp, data = self.local_cache[key]
            if current_time - timestamp < self.local_cache_ttl:
                print(f"从本地缓存获取: {key}")
                return data
            else:
                # 本地缓存过期
                del self.local_cache[key]
                if key in self.access_times:
                    del self.access_times[key]
        
        # 第二级：Redis缓存
        cached_data = self.redis_cache.get(key)
        if cached_data is not None:
            print(f"从Redis缓存获取: {key}")
            # 更新本地缓存
            self._update_local_cache(key, cached_data, current_time)
            return cached_data
        
        # 第三级：数据库查询
        print(f"缓存未命中，查询数据库: {key}")
        data = data_fetcher(key)
        
        if data is not None:
            # 更新Redis缓存
            self.redis_cache.set(key, data)
            # 更新本地缓存
            self._update_local_cache(key, data, current_time)
        
        return data
    
    def _update_local_cache(self, key: str, data: Any, timestamp: float):
        """更新本地缓存"""
        # 检查缓存大小，如果超过限制则清理最久未使用的
        if len(self.local_cache) >= self.local_cache_size:
            # 找到最久未使用的key
            oldest_key = min(self.access_times.items(), key=lambda x: x[1])[0]
            del self.local_cache[oldest_key]
            del self.access_times[oldest_key]
        
        self.local_cache[key] = (timestamp, data)
        self.access_times[key] = timestamp
    
    def invalidate(self, key: str):
        """失效缓存"""
        if key in self.local_cache:
            del self.local_cache[key]
        if key in self.access_times:
            del self.access_times[key]
        
        self.redis_cache.delete(key)


def test_cache_patterns():
    """测试缓存模式"""
    # 创建Redis连接
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    
    print("=== 测试基础缓存 ===")
    basic_cache = RedisCache(r)
    
    # 测试基础缓存操作
    basic_cache.set("test_key", {"name": "test", "value": 123})
    result = basic_cache.get("test_key")
    print(f"基础缓存获取结果: {result}")
    
    print("\n=== 测试布隆过滤器缓存 ===")
    bloom_cache = BloomFilterCache(r)
    
    # 模拟数据源
    def mock_db_fetcher(key):
        if key.startswith("exist_"):
            return f"data_for_{key}"
        return None
    
    # 测试存在的数据
    result1 = bloom_cache.get_with_penetration_protection("exist_001", mock_db_fetcher)
    print(f"存在数据查询结果: {result1}")
    
    # 测试不存在的数据
    result2 = bloom_cache.get_with_penetration_protection("not_exist_001", mock_db_fetcher)
    print(f"不存在数据查询结果: {result2}")
    
    print("\n=== 测试缓存击穿保护 ===")
    breakdown_cache = CacheBreakdownProtection(r)
    
    call_count = 0
    def expensive_fetcher(key):
        nonlocal call_count
        call_count += 1
        print(f"数据源被调用第 {call_count} 次")
        time.sleep(0.5)  # 模拟耗时操作
        return f"expensive_data_for_{key}"
    
    # 模拟并发访问
    import threading
    
    results = []
    
    def concurrent_get():
        result = breakdown_cache.get_with_breakdown_protection("hot_key", expensive_fetcher)
        results.append(result)
    
    threads = []
    for i in range(10):
        t = threading.Thread(target=concurrent_get)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print(f"并发访问结果数量: {len(results)}")
    print(f"数据源实际调用次数: {call_count}")
    
    print("\n=== 测试缓存雪崩保护 ===")
    avalanche_cache = CacheAvalancheProtection(r)
    
    # 批量设置缓存
    test_data = {f"key_{i}": f"value_{i}" for i in range(10)}
    avalanche_cache.batch_set_with_avalanche_protection(test_data)
    
    print("批量缓存设置完成")
    
    print("\n=== 测试多级缓存 ===")
    multi_cache = MultiLevelCache(r, local_cache_size=5)
    
    def simple_fetcher(key):
        return f"fetched_{key}"
    
    # 第一次访问
    result1 = multi_cache.get("test_key", simple_fetcher)
    print(f"第一次访问结果: {result1}")
    
    # 第二次访问（应该从本地缓存获取）
    result2 = multi_cache.get("test_key", simple_fetcher)
    print(f"第二次访问结果: {result2}")
    
    print("\n缓存模式测试完成!")


if __name__ == "__main__":
    test_cache_patterns()