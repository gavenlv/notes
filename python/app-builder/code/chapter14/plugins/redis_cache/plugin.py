from flask_appbuilder import BasePlugin
from flask import current_app
import redis
import json
import pickle
import logging
from functools import wraps
from typing import Any, Optional, Callable

class RedisCachePlugin(BasePlugin):
    name = "Redis Cache"
    category = "Performance"
    version = "1.0.0"
    
    def __init__(self, appbuilder):
        super().__init__(appbuilder)
        self.redis_client = None
        self.logger = logging.getLogger('redis_cache')
        self.connect()
    
    def connect(self):
        """连接到Redis服务器"""
        try:
            redis_url = current_app.config.get('REDIS_URL', 'redis://localhost:6379/0')
            self.redis_client = redis.from_url(redis_url)
            # 测试连接
            self.redis_client.ping()
            self.logger.info("Redis cache connected successfully")
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {str(e)}")
            self.redis_client = None
    
    def get(self, key: str) -> Any:
        """从缓存获取数据"""
        if not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                # 尝试JSON反序列化，如果失败则使用pickle
                try:
                    return json.loads(value.decode('utf-8'))
                except:
                    return pickle.loads(value)
            return None
        except Exception as e:
            self.logger.error(f"Failed to get cache key {key}: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, timeout: int = 300) -> bool:
        """设置缓存数据"""
        if not self.redis_client:
            return False
        
        try:
            # 尝试JSON序列化，如果失败则使用pickle
            try:
                serialized_value = json.dumps(value)
            except:
                serialized_value = pickle.dumps(value)
            
            result = self.redis_client.setex(key, timeout, serialized_value)
            return result
        except Exception as e:
            self.logger.error(f"Failed to set cache key {key}: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存数据"""
        if not self.redis_client:
            return False
        
        try:
            result = self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            self.logger.error(f"Failed to delete cache key {key}: {str(e)}")
            return False
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self.redis_client:
            return False
        
        try:
            return self.redis_client.exists(key) > 0
        except Exception as e:
            self.logger.error(f"Failed to check cache key {key}: {str(e)}")
            return False
    
    def expire(self, key: str, timeout: int) -> bool:
        """设置键的过期时间"""
        if not self.redis_client:
            return False
        
        try:
            return self.redis_client.expire(key, timeout)
        except Exception as e:
            self.logger.error(f"Failed to set expire for cache key {key}: {str(e)}")
            return False
    
    def flush(self) -> bool:
        """清空所有缓存"""
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.flushdb()
            self.logger.info("Redis cache flushed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to flush cache: {str(e)}")
            return False
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """递增键值"""
        if not self.redis_client:
            return None
        
        try:
            return self.redis_client.incrby(key, amount)
        except Exception as e:
            self.logger.error(f"Failed to increment cache key {key}: {str(e)}")
            return None
    
    def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """递减键值"""
        if not self.redis_client:
            return None
        
        try:
            return self.redis_client.decrby(key, amount)
        except Exception as e:
            self.logger.error(f"Failed to decrement cache key {key}: {str(e)}")
            return None
    
    def cache(self, timeout: int = 300, key_prefix: str = "cache_"):
        """缓存装饰器"""
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def wrapper(*args, **kwargs):
                # 生成缓存键
                cache_key = f"{key_prefix}{f.__name__}_{hash(str(args) + str(kwargs))}"
                
                # 尝试从缓存获取
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    self.logger.debug(f"Cache hit for key: {cache_key}")
                    return cached_result
                
                # 执行函数并缓存结果
                result = f(*args, **kwargs)
                self.set(cache_key, result, timeout)
                self.logger.debug(f"Cache set for key: {cache_key}")
                
                return result
            return wrapper
        return decorator
    
    def get_stats(self) -> dict:
        """获取缓存统计信息"""
        if not self.redis_client:
            return {}
        
        try:
            info = self.redis_client.info()
            return {
                'connected_clients': info.get('connected_clients', 0),
                'used_memory': info.get('used_memory_human', '0B'),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'uptime_in_seconds': info.get('uptime_in_seconds', 0)
            }
        except Exception as e:
            self.logger.error(f"Failed to get cache stats: {str(e)}")
            return {}

# 全局缓存装饰器
def cached(timeout: int = 300, key_prefix: str = "global_cache_"):
    """全局缓存装饰器"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # 获取缓存插件实例
            appbuilder = current_app.extensions['appbuilder']
            cache_plugin = None
            for plugin in appbuilder.plugins:
                if isinstance(plugin, RedisCachePlugin):
                    cache_plugin = plugin
                    break
            
            if cache_plugin:
                # 生成缓存键
                cache_key = f"{key_prefix}{f.__name__}_{hash(str(args) + str(kwargs))}"
                
                # 尝试从缓存获取
                cached_result = cache_plugin.get(cache_key)
                if cached_result is not None:
                    cache_plugin.logger.debug(f"Global cache hit for key: {cache_key}")
                    return cached_result
                
                # 执行函数并缓存结果
                result = f(*args, **kwargs)
                cache_plugin.set(cache_key, result, timeout)
                cache_plugin.logger.debug(f"Global cache set for key: {cache_key}")
                
                return result
            else:
                # 如果没有找到缓存插件，则正常执行函数
                return f(*args, **kwargs)
        return wrapper
    return decorator