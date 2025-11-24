#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis秒杀系统实现
包含库存预减、限流、防超卖等核心功能
"""

import redis
import time
import uuid
import threading
import random
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed


class RedisSeckillSystem:
    """Redis秒杀系统核心实现"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def init_seckill_product(self, product_id: str, stock: int, seckill_price: float) -> bool:
        """
        初始化秒杀商品
        
        Args:
            product_id: 商品ID
            stock: 库存数量
            seckill_price: 秒杀价格
            
        Returns:
            bool: 初始化是否成功
        """
        try:
            # 使用管道保证原子性
            pipeline = self.redis.pipeline()
            
            # 设置商品库存
            pipeline.hset(f"seckill:product:{product_id}", "stock", stock)
            pipeline.hset(f"seckill:product:{product_id}", "price", seckill_price)
            pipeline.hset(f"seckill:product:{product_id}", "sold", 0)
            
            # 设置库存计数器
            pipeline.set(f"seckill:stock:{product_id}", stock)
            
            # 执行管道
            pipeline.execute()
            return True
        except Exception as e:
            print(f"初始化商品失败: {e}")
            return False
    
    def seckill_v1_basic(self, product_id: str, user_id: str) -> Dict:
        """
        基础版秒杀（存在超卖问题）
        
        Returns:
            Dict: 秒杀结果
        """
        # 检查库存
        stock_key = f"seckill:stock:{product_id}"
        current_stock = int(self.redis.get(stock_key) or 0)
        
        if current_stock <= 0:
            return {
                "success": False,
                "message": "商品已售完",
                "product_id": product_id,
                "user_id": user_id
            }
        
        # 减少库存
        self.redis.decr(stock_key)
        
        # 记录订单
        order_id = str(uuid.uuid4())
        order_key = f"seckill:order:{order_id}"
        
        self.redis.hset(order_key, "product_id", product_id)
        self.redis.hset(order_key, "user_id", user_id)
        self.redis.hset(order_key, "create_time", int(time.time()))
        
        return {
            "success": True,
            "message": "秒杀成功",
            "product_id": product_id,
            "user_id": user_id,
            "order_id": order_id
        }
    
    def seckill_v2_atomic(self, product_id: str, user_id: str) -> Dict:
        """
        原子操作版秒杀（解决超卖问题）
        
        Returns:
            Dict: 秒杀结果
        """
        stock_key = f"seckill:stock:{product_id}"
        
        # 使用Lua脚本保证原子性
        lua_script = """
        local stock_key = KEYS[1]
        local product_key = KEYS[2]
        local user_id = ARGV[1]
        local current_time = ARGV[2]
        
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
        redis.call('hset', order_key, 'product_id', ARGV[3])
        redis.call('hset', order_key, 'user_id', user_id)
        redis.call('hset', order_key, 'create_time', current_time)
        
        return {1, order_id}
        """
        
        try:
            result = self.redis.eval(
                lua_script, 
                2, 
                stock_key, 
                f"seckill:product:{product_id}", 
                user_id, 
                str(int(time.time())), 
                product_id
            )
            
            if result[0] == 1:
                return {
                    "success": True,
                    "message": "秒杀成功",
                    "product_id": product_id,
                    "user_id": user_id,
                    "order_id": result[1]
                }
            else:
                return {
                    "success": False,
                    "message": result[1],
                    "product_id": product_id,
                    "user_id": user_id
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"系统错误: {e}",
                "product_id": product_id,
                "user_id": user_id
            }
    
    def seckill_v3_limit(self, product_id: str, user_id: str) -> Dict:
        """
        限流版秒杀（防止单个用户重复购买）
        
        Returns:
            Dict: 秒杀结果
        """
        # 检查用户是否已经购买过
        user_bought_key = f"seckill:user:{user_id}:{product_id}"
        if self.redis.exists(user_bought_key):
            return {
                "success": False,
                "message": "每个用户只能购买一次",
                "product_id": product_id,
                "user_id": user_id
            }
        
        # 使用Lua脚本实现原子操作
        lua_script = """
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
        redis.call('setex', user_bought_key, 3600, '1')  -- 1小时过期
        
        -- 更新商品已售数量
        redis.call('hincrby', product_key, 'sold', 1)
        
        -- 生成订单
        local order_id = redis.call('incr', 'seckill:order:id')
        local order_key = 'seckill:order:' .. order_id
        
        redis.call('hset', order_key, 'product_id', product_id)
        redis.call('hset', order_key, 'user_id', user_id)
        redis.call('hset', order_key, 'create_time', current_time)
        
        return {1, order_id}
        """
        
        try:
            result = self.redis.eval(
                lua_script,
                3,
                f"seckill:stock:{product_id}",
                f"seckill:product:{product_id}",
                user_bought_key,
                user_id,
                str(int(time.time())),
                product_id
            )
            
            if result[0] == 1:
                return {
                    "success": True,
                    "message": "秒杀成功",
                    "product_id": product_id,
                    "user_id": user_id,
                    "order_id": result[1]
                }
            else:
                return {
                    "success": False,
                    "message": result[1],
                    "product_id": product_id,
                    "user_id": user_id
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"系统错误: {e}",
                "product_id": product_id,
                "user_id": user_id
            }


class SeckillRateLimiter:
    """秒杀限流器"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def token_bucket_limit(self, key: str, capacity: int, refill_rate: float) -> bool:
        """
        令牌桶限流算法
        
        Args:
            key: 限流key
            capacity: 桶容量
            refill_rate: 令牌补充速率（每秒）
            
        Returns:
            bool: 是否允许通过
        """
        current_time = time.time()
        
        lua_script = """
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
            redis.call('expire', key, 3600)  -- 设置过期时间
            return 1
        else
            redis.call('hset', key, 'tokens', tokens)
            redis.call('hset', key, 'last_refill', current_time)
            redis.call('expire', key, 3600)
            return 0
        end
        """
        
        result = self.redis.eval(lua_script, 1, key, capacity, refill_rate, current_time)
        return result == 1
    
    def sliding_window_limit(self, key: str, window_size: int, max_requests: int) -> bool:
        """
        滑动窗口限流算法
        
        Args:
            key: 限流key
            window_size: 窗口大小（秒）
            max_requests: 最大请求数
            
        Returns:
            bool: 是否允许通过
        """
        current_time = int(time.time())
        window_start = current_time - window_size + 1
        
        lua_script = """
        local key = KEYS[1]
        local window_start = tonumber(ARGV[1])
        local current_time = tonumber(ARGV[2])
        local max_requests = tonumber(ARGV[3])
        local window_size = tonumber(ARGV[4])
        
        -- 移除过期时间戳
        redis.call('zremrangebyscore', key, 0, window_start - 1)
        
        -- 获取当前窗口内的请求数量
        local request_count = redis.call('zcard', key)
        
        if request_count < max_requests then
            -- 添加当前请求时间戳
            redis.call('zadd', key, current_time, current_time .. ':' .. math.random())
            redis.call('expire', key, window_size * 2)  -- 设置过期时间
            return 1
        else
            return 0
        end
        """
        
        result = self.redis.eval(
            lua_script, 
            1, 
            key, 
            window_start, 
            current_time, 
            max_requests, 
            window_size
        )
        return result == 1


def simulate_seckill(seckill_system: RedisSeckillSystem, product_id: str, user_id: str):
    """模拟单个用户秒杀"""
    try:
        # 添加随机延迟模拟网络延迟
        time.sleep(random.uniform(0.01, 0.1))
        
        # 执行秒杀
        result = seckill_system.seckill_v3_limit(product_id, user_id)
        return result
    except Exception as e:
        return {
            "success": False,
            "message": f"异常: {e}",
            "product_id": product_id,
            "user_id": user_id
        }


def test_seckill_system():
    """测试秒杀系统"""
    # 创建Redis连接
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    
    # 清空测试数据
    r.delete("seckill:product:test001", "seckill:stock:test001", "seckill:order:id")
    
    seckill_system = RedisSeckillSystem(r)
    
    print("=== 初始化秒杀商品 ===")
    if seckill_system.init_seckill_product("test001", 100, 99.9):
        print("✓ 商品初始化成功")
    
    print("\n=== 测试基础版秒杀（存在超卖问题） ===")
    
    # 模拟并发请求
    user_ids = [f"user_{i:03d}" for i in range(1, 151)]  # 150个用户
    
    print("模拟150个用户并发秒杀100件商品...")
    
    success_count = 0
    fail_count = 0
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [
            executor.submit(simulate_seckill, seckill_system, "test001", user_id)
            for user_id in user_ids
        ]
        
        for future in as_completed(futures):
            result = future.result()
            if result["success"]:
                success_count += 1
            else:
                fail_count += 1
    
    print(f"秒杀成功: {success_count} 次")
    print(f"秒杀失败: {fail_count} 次")
    
    # 检查实际库存
    final_stock = int(r.get("seckill:stock:test001") or 0)
    sold_count = int(r.hget("seckill:product:test001", "sold") or 0)
    
    print(f"最终库存: {final_stock}")
    print(f"实际售出: {sold_count}")
    
    # 测试限流器
    print("\n=== 测试限流器 ===")
    rate_limiter = SeckillRateLimiter(r)
    
    # 令牌桶限流测试
    print("令牌桶限流测试:")
    for i in range(15):
        allowed = rate_limiter.token_bucket_limit("rate:limit:test", 10, 2)
        print(f"请求 {i+1}: {'允许' if allowed else '拒绝'}")
        time.sleep(0.1)
    
    print("\n秒杀系统测试完成!")


if __name__ == "__main__":
    test_seckill_system()