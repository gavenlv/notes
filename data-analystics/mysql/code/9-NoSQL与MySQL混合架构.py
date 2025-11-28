#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MySQL与NoSQL混合架构代码示例
包含MySQL与MongoDB、Redis、Elasticsearch、Cassandra等NoSQL数据库的混合架构演示

使用方法:
    python 9-NoSQL与MySQL混合架构.py [选项]

示例:
    python 9-NoSQL与MySQL混合架构.py --demo mysql_mongodb
    python 9-NoSQL与MySQL混合架构.py --demo mysql_redis
    python 9-NoSQL与MySQL混合架构.py --demo mysql_elasticsearch
    python 9-NoSQL与MySQL混合架构.py --demo mysql_cassandra
    python 9-NoSQL与MySQL混合架构.py --demo all
"""

import sys
import os
import json
import uuid
import time
import threading
import queue
import hashlib
import logging
import argparse
import random
from datetime import datetime, timedelta
from functools import wraps
from collections import defaultdict

# 数据库连接库
import pymysql
try:
    import redis
except ImportError:
    print("警告: Redis库未安装，Redis相关功能将不可用")
    redis = None

try:
    from pymongo import MongoClient
except ImportError:
    print("警告: PyMongo库未安装，MongoDB相关功能将不可用")
    MongoClient = None

try:
    from elasticsearch import Elasticsearch
except ImportError:
    print("警告: Elasticsearch库未安装，Elasticsearch相关功能将不可用")
    Elasticsearch = None

try:
    from cassandra.cluster import Cluster
    from cassandra.util import uuid_from_time
except ImportError:
    print("警告: Cassandra库未安装，Cassandra相关功能将不可用")
    Cluster = None

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('hybrid_architecture.log')
    ]
)
logger = logging.getLogger(__name__)

class HybridArchitectureBase:
    """混合架构基础类"""
    
    def __init__(self, config):
        """
        初始化混合架构基础类
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.connections = {}
        
        # 初始化数据库连接
        self._init_connections()
    
    def _init_connections(self):
        """初始化数据库连接"""
        # 初始化MySQL连接
        if 'mysql' in self.config:
            try:
                self.connections['mysql'] = pymysql.Connect(**self.config['mysql'])
                logger.info("MySQL连接已建立")
            except Exception as e:
                logger.error(f"MySQL连接失败: {e}")
        
        # 初始化Redis连接
        if 'redis' in self.config and redis:
            try:
                self.connections['redis'] = redis.Redis(**self.config['redis'])
                # 测试连接
                self.connections['redis'].ping()
                logger.info("Redis连接已建立")
            except Exception as e:
                logger.error(f"Redis连接失败: {e}")
        
        # 初始化MongoDB连接
        if 'mongodb' in self.config and MongoClient:
            try:
                self.connections['mongodb'] = MongoClient(self.config['mongodb']['uri'])
                # 测试连接
                self.connections['mongodb'].server_info()
                logger.info("MongoDB连接已建立")
            except Exception as e:
                logger.error(f"MongoDB连接失败: {e}")
        
        # 初始化Elasticsearch连接
        if 'elasticsearch' in self.config and Elasticsearch:
            try:
                self.connections['elasticsearch'] = Elasticsearch(**self.config['elasticsearch'])
                # 测试连接
                self.connections['elasticsearch'].ping()
                logger.info("Elasticsearch连接已建立")
            except Exception as e:
                logger.error(f"Elasticsearch连接失败: {e}")
        
        # 初始化Cassandra连接
        if 'cassandra' in self.config and Cluster:
            try:
                cluster = Cluster([self.config['cassandra']['host']])
                self.connections['cassandra'] = cluster.connect(self.config['cassandra']['keyspace'])
                logger.info("Cassandra连接已建立")
            except Exception as e:
                logger.error(f"Cassandra连接失败: {e}")
    
    def close(self):
        """关闭所有连接"""
        for name, conn in self.connections.items():
            try:
                if name == 'mysql':
                    conn.close()
                elif name == 'redis':
                    conn.close()
                elif name == 'mongodb':
                    conn.close()
                elif name == 'elasticsearch':
                    # Elasticsearch连接不需要显式关闭
                    pass
                elif name == 'cassandra':
                    conn.shutdown()
                
                logger.info(f"{name}连接已关闭")
            except Exception as e:
                logger.error(f"关闭{name}连接失败: {e}")
        
        self.connections.clear()
    
    def mysql_execute(self, query, params=None, fetch_one=False):
        """
        执行MySQL查询
        
        Args:
            query: SQL查询
            params: 查询参数
            fetch_one: 是否只获取一条记录
            
        Returns:
            查询结果
        """
        if 'mysql' not in self.connections:
            raise Exception("MySQL连接未建立")
        
        try:
            with self.connections['mysql'].cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(query, params)
                
                if query.strip().upper().startswith(('SELECT', 'SHOW', 'DESCRIBE')):
                    if fetch_one:
                        return cursor.fetchone()
                    else:
                        return cursor.fetchall()
                else:
                    self.connections['mysql'].commit()
                    return cursor.rowcount
        except Exception as e:
            logger.error(f"MySQL查询失败: {e}")
            raise

class MySQLMongoDBDemo(HybridArchitectureBase):
    """MySQL与MongoDB混合架构演示"""
    
    def __init__(self, config):
        super().__init__(config)
        self.mongodb_db = None
        if 'mongodb' in self.connections:
            self.mongodb_db = self.connections['mongodb'][self.config['mongodb'].get('database', 'hybrid_demo')]
        
        # 初始化数据结构
        self._setup_data_structures()
    
    def _setup_data_structures(self):
        """初始化数据结构"""
        # 创建MySQL表
        if 'mysql' in self.connections:
            try:
                # 创建用户表
                self.mysql_execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        email VARCHAR(100) NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    )
                """)
                
                # 创建订单表
                self.mysql_execute("""
                    CREATE TABLE IF NOT EXISTS orders (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        user_id INT NOT NULL,
                        order_number VARCHAR(50) UNIQUE NOT NULL,
                        total_amount DECIMAL(10,2) NOT NULL,
                        status ENUM('pending', 'paid', 'shipped', 'delivered', 'cancelled') NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                """)
                
                logger.info("MySQL表已创建")
            except Exception as e:
                logger.error(f"创建MySQL表失败: {e}")
        
        # 创建MongoDB集合
        if self.mongodb_db:
            try:
                # 创建索引
                self.mongodb_db.user_profiles.create_index("user_id", unique=True)
                self.mongodb_db.product_reviews.create_index("product_id")
                self.mongodb_db.product_reviews.create_index("user_id")
                
                logger.info("MongoDB集合索引已创建")
            except Exception as e:
                logger.error(f"创建MongoDB索引失败: {e}")
    
    def create_user_with_profile(self, user_data, profile_data):
        """
        创建用户及扩展资料
        
        Args:
            user_data: 用户核心数据
            profile_data: 用户扩展数据
            
        Returns:
            用户ID
        """
        try:
            # 开始MySQL事务
            with self.connections['mysql'].cursor() as cursor:
                # 插入MySQL用户核心信息
                cursor.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                    (user_data['username'], user_data['email'], user_data['password_hash'])
                )
                user_id = cursor.lastrowid
                
                # 提交MySQL事务
                self.connections['mysql'].commit()
                
                # 插入MongoDB用户扩展信息
                profile_data['user_id'] = user_id
                profile_data['created_at'] = datetime.utcnow()
                profile_data['updated_at'] = datetime.utcnow()
                
                self.mongodb_db.user_profiles.insert_one(profile_data)
                
                logger.info(f"创建用户成功: {user_id}")
                return user_id
                
        except Exception as e:
            # 回滚MySQL事务
            if 'mysql' in self.connections:
                self.connections['mysql'].rollback()
            logger.error(f"创建用户失败: {e}")
            raise
    
    def get_user_with_profile(self, user_id):
        """
        获取用户及扩展资料
        
        Args:
            user_id: 用户ID
            
        Returns:
            合并后的用户信息
        """
        try:
            # 从MySQL获取核心信息
            user = self.mysql_execute(
                "SELECT * FROM users WHERE id = %s", 
                (user_id,), 
                fetch_one=True
            )
            
            if not user:
                return None
            
            # 从MongoDB获取扩展信息
            if self.mongodb_db:
                profile = self.mongodb_db.user_profiles.find_one({"user_id": user_id})
                
                # 合并数据
                result = user
                if profile:
                    # 移除MongoDB内部字段
                    del profile['_id']
                    result['profile'] = profile
            else:
                result = user
            
            return result
        except Exception as e:
            logger.error(f"获取用户失败: {e}")
            raise
    
    def add_product_review(self, product_id, user_id, review_data):
        """
        添加产品评论
        
        Args:
            product_id: 产品ID
            user_id: 用户ID
            review_data: 评论数据
            
        Returns:
            评论ID
        """
        try:
            # 添加评论到MongoDB
            review = {
                "product_id": product_id,
                "user_id": user_id,
                "rating": review_data['rating'],
                "title": review_data['title'],
                "content": review_data['content'],
                "created_at": datetime.utcnow()
            }
            
            # 添加可选字段
            if 'images' in review_data:
                review['images'] = review_data['images']
            
            if 'verified_purchase' in review_data:
                review['verified_purchase'] = review_data['verified_purchase']
            
            result = self.mongodb_db.product_reviews.insert_one(review)
            
            logger.info(f"添加评论成功: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            logger.error(f"添加评论失败: {e}")
            raise
    
    def get_product_reviews(self, product_id, limit=10):
        """
        获取产品评论
        
        Args:
            product_id: 产品ID
            limit: 返回数量限制
            
        Returns:
            评论列表
        """
        try:
            if not self.mongodb_db:
                return []
            
            # 从MongoDB获取评论
            reviews = list(
                self.mongodb_db.product_reviews.find(
                    {"product_id": product_id}
                )
                .sort("created_at", -1)
                .limit(limit)
            )
            
            # 移除MongoDB内部字段并转换时间
            for review in reviews:
                del review['_id']
                review['created_at'] = review['created_at'].isoformat()
            
            return reviews
        except Exception as e:
            logger.error(f"获取评论失败: {e}")
            raise
    
    def demo_mysql_mongodb(self):
        """演示MySQL与MongoDB混合架构"""
        print("\n===== MySQL与MongoDB混合架构演示 =====")
        
        try:
            # 1. 创建用户
            print("\n1. 创建用户:")
            user_data = {
                'username': f'user_{int(time.time())}',
                'email': f'user_{int(time.time())}@example.com',
                'password_hash': hashlib.sha256('password123'.encode()).hexdigest()
            }
            
            profile_data = {
                'first_name': '张',
                'last_name': '三',
                'avatar': 'https://example.com/avatars/user12345.jpg',
                'bio': '软件工程师，热爱开源技术',
                'interests': ['编程', '开源', '人工智能', '大数据'],
                'preferences': {
                    'theme': 'dark',
                    'language': 'zh-CN',
                    'notifications': {
                        'email': True,
                        'sms': False,
                        'push': True
                    }
                }
            }
            
            user_id = self.create_user_with_profile(user_data, profile_data)
            print(f"  创建用户成功: {user_id}")
            
            # 2. 获取用户信息
            print("\n2. 获取用户信息:")
            user_info = self.get_user_with_profile(user_id)
            if user_info:
                print(f"  用户名: {user_info['username']}")
                print(f"  邮箱: {user_info['email']}")
                if 'profile' in user_info:
                    profile = user_info['profile']
                    print(f"  姓名: {profile['first_name']}{profile['last_name']}")
                    print(f"  兴趣: {', '.join(profile['interests'])}")
            
            # 3. 创建订单（MySQL）
            print("\n3. 创建订单:")
            order_data = {
                'user_id': user_id,
                'order_number': f'ORDER_{int(time.time())}',
                'total_amount': 199.99,
                'status': 'pending'
            }
            
            self.mysql_execute("""
                INSERT INTO orders (user_id, order_number, total_amount, status)
                VALUES (%s, %s, %s, %s)
            """, (
                order_data['user_id'],
                order_data['order_number'],
                order_data['total_amount'],
                order_data['status']
            ))
            
            orders = self.mysql_execute("SELECT * FROM orders WHERE user_id = %s", (user_id,))
            print(f"  订单数量: {len(orders)}")
            for order in orders:
                print(f"    订单号: {order['order_number']}, 金额: {order['total_amount']}, 状态: {order['status']}")
            
            # 4. 添加产品评论（MongoDB）
            print("\n4. 添加产品评论:")
            review_data = {
                'rating': 5,
                'title': '非常满意的产品',
                'content': '这个产品超出了我的预期，质量很好，物流也很快。',
                'images': ['https://example.com/reviews/img1.jpg', 'https://example.com/reviews/img2.jpg'],
                'verified_purchase': True
            }
            
            product_id = random.randint(1, 1000)
            review_id = self.add_product_review(product_id, user_id, review_data)
            print(f"  添加评论成功: {review_id}")
            
            # 5. 获取产品评论
            print("\n5. 获取产品评论:")
            reviews = self.get_product_reviews(product_id)
            print(f"  产品ID {product_id} 的评论数量: {len(reviews)}")
            for review in reviews:
                print(f"    评分: {review['rating']}/5, 标题: {review['title']}")
                print(f"    内容: {review['content'][:50]}...")
            
            # 6. 数据同步演示
            print("\n6. 数据同步演示:")
            print("  模拟用户信息更新...")
            
            # 更新MySQL中的用户信息
            self.mysql_execute("UPDATE users SET email = %s WHERE id = %s", (
                f'updated_{int(time.time())}@example.com', user_id
            ))
            
            # 更新MongoDB中的用户档案
            if self.mongodb_db:
                self.mongodb_db.user_profiles.update_one(
                    {"user_id": user_id},
                    {"$set": {
                        "bio": "更新后的个人简介",
                        "updated_at": datetime.utcnow()
                    }}
                )
            
            # 再次获取用户信息
            updated_user = self.get_user_with_profile(user_id)
            print(f"  更新后邮箱: {updated_user['email']}")
            if 'profile' in updated_user:
                print(f"  更新后简介: {updated_user['profile']['bio']}")
            
            print("\n✅ MySQL与MongoDB混合架构演示完成")
            
        except Exception as e:
            logger.error(f"MySQL与MongoDB混合架构演示失败: {e}")

class MySQLRedisDemo(HybridArchitectureBase):
    """MySQL与Redis混合架构演示"""
    
    def __init__(self, config):
        super().__init__(config)
        self.redis_client = self.connections.get('redis')
    
    def cache_result(self, key_prefix, ttl=3600):
        """
        装饰器：缓存查询结果
        
        Args:
            key_prefix: 缓存键前缀
            ttl: 缓存过期时间（秒）
            
        Returns:
            装饰器函数
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.redis_client:
                    # 如果没有Redis，直接执行函数
                    return func(*args, **kwargs)
                
                # 生成缓存键
                key_data = f"{key_prefix}:{str(args)}:{str(kwargs)}"
                cache_key = f"cache:{hashlib.md5(key_data.encode()).hexdigest()}"
                
                # 尝试从缓存获取
                cached_result = self.redis_client.get(cache_key)
                if cached_result:
                    return json.loads(cached_result)
                
                # 缓存未命中，执行原函数
                result = func(*args, **kwargs)
                
                # 将结果存入缓存
                self.redis_client.setex(
                    cache_key,
                    ttl,
                    json.dumps(result, default=str)
                )
                
                return result
            return wrapper
        return decorator
    
    def invalidate_cache(self, pattern):
        """
        清除匹配模式的所有缓存
        
        Args:
            pattern: 缓存键模式
        """
        if not self.redis_client:
            return
        
        try:
            for key in self.redis_client.scan_iter(match=pattern):
                self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"清除缓存失败: {e}")
    
    @cache_result("user", 1800)  # 30分钟
    def get_user(self, user_id):
        """
        获取用户信息（带缓存）
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户信息
        """
        try:
            return self.mysql_execute(
                "SELECT * FROM users WHERE id = %s",
                (user_id,),
                fetch_one=True
            )
        except Exception as e:
            logger.error(f"获取用户失败: {e}")
            return None
    
    def increment_view_count(self, item_type, item_id):
        """
        增加浏览量
        
        Args:
            item_type: 项目类型
            item_id: 项目ID
            
        Returns:
            新的浏览量
        """
        if not self.redis_client:
            return 0
        
        try:
            # Redis中的键名
            key = f"{item_type}:{item_id}:views"
            
            # 增加Redis计数器
            count = self.redis_client.incr(key)
            
            # 设置过期时间（24小时）
            self.redis_client.expire(key, 86400)
            
            # 定期同步到MySQL（每100次浏览量同步一次）
            if count % 100 == 0:
                self._sync_counter_to_mysql(item_type, item_id, count)
            
            return count
        except Exception as e:
            logger.error(f"增加浏览量失败: {e}")
            return 0
    
    def get_view_count(self, item_type, item_id):
        """
        获取浏览量
        
        Args:
            item_type: 项目类型
            item_id: 项目ID
            
        Returns:
            浏览量
        """
        if not self.redis_client:
            return 0
        
        try:
            # 先从Redis获取
            key = f"{item_type}:{item_id}:views"
            redis_count = self.redis_client.get(key)
            
            if redis_count:
                return int(redis_count)
            
            # Redis中没有，从MySQL获取
            result = self.mysql_execute(
                f"SELECT view_count FROM {item_type}s WHERE id = %s",
                (item_id,),
                fetch_one=True
            )
            
            if result:
                count = result.get('view_count', 0)
                # 同步到Redis
                self.redis_client.setex(key, 86400, count)
                return count
            
            return 0
        except Exception as e:
            logger.error(f"获取浏览量失败: {e}")
            return 0
    
    def _sync_counter_to_mysql(self, item_type, item_id, value):
        """
        同步计数器到MySQL
        
        Args:
            item_type: 项目类型
            item_id: 项目ID
            value: 计数值
        """
        try:
            self.mysql_execute(
                f"UPDATE {item_type}s SET view_count = %s WHERE id = %s",
                (value, item_id)
            )
            logger.info(f"同步计数器到MySQL: {item_type}:{item_id} = {value}")
        except Exception as e:
            logger.error(f"同步计数器到MySQL失败: {e}")
    
    def acquire_lock(self, lock_key, lock_value, expire_time=30):
        """
        获取分布式锁
        
        Args:
            lock_key: 锁键
            lock_value: 锁值
            expire_time: 过期时间（秒）
            
        Returns:
            是否获取成功
        """
        if not self.redis_client:
            return False
        
        try:
            # 使用SET命令的NX和PX选项实现原子性锁获取
            return self.redis_client.set(
                lock_key, lock_value, nx=True, ex=expire_time
            )
        except Exception as e:
            logger.error(f"获取分布式锁失败: {e}")
            return False
    
    def release_lock(self, lock_key, lock_value):
        """
        释放分布式锁
        
        Args:
            lock_key: 锁键
            lock_value: 锁值
            
        Returns:
            是否释放成功
        """
        if not self.redis_client:
            return False
        
        try:
            # 使用Lua脚本确保只有锁的持有者才能释放锁
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            
            result = self.redis_client.eval(lua_script, 1, lock_key, lock_value)
            return result == 1
        except Exception as e:
            logger.error(f"释放分布式锁失败: {e}")
            return False
    
    def demo_mysql_redis(self):
        """演示MySQL与Redis混合架构"""
        print("\n===== MySQL与Redis混合架构演示 =====")
        
        try:
            # 1. 创建测试数据
            print("\n1. 创建测试数据:")
            
            # 创建用户表（如果没有）
            self.mysql_execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    view_count INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 插入测试用户
            username = f'user_{int(time.time())}'
            self.mysql_execute(
                "INSERT INTO users (username, email) VALUES (%s, %s)",
                (username, f'{username}@example.com')
            )
            
            user = self.mysql_execute(
                "SELECT * FROM users WHERE username = %s",
                (username,),
                fetch_one=True
            )
            
            print(f"  创建测试用户: {user['id']} - {user['username']}")
            
            # 2. 测试缓存功能
            print("\n2. 测试缓存功能:")
            
            # 第一次获取用户（会缓存）
            start_time = time.time()
            user1 = self.get_user(user['id'])
            first_duration = time.time() - start_time
            print(f"  第一次获取用户耗时: {first_duration:.4f}秒")
            
            # 第二次获取用户（从缓存）
            start_time = time.time()
            user2 = self.get_user(user['id'])
            second_duration = time.time() - start_time
            print(f"  第二次获取用户耗时: {second_duration:.4f}秒")
            
            if second_duration < first_duration:
                print(f"  缓存加速: {first_duration/second_duration:.2f}倍")
            
            # 3. 测试计数器功能
            print("\n3. 测试计数器功能:")
            
            # 初始浏览量
            initial_views = self.get_view_count('user', user['id'])
            print(f"  初始浏览量: {initial_views}")
            
            # 增加浏览量
            for i in range(5):
                views = self.increment_view_count('user', user['id'])
                print(f"  第{i+1}次增加后浏览量: {views}")
                time.sleep(0.1)  # 短暂延时
            
            # 4. 测试分布式锁
            print("\n4. 测试分布式锁:")
            
            lock_key = f"lock:user:{user['id']}"
            lock_value = str(uuid.uuid4())
            
            # 获取锁
            acquired = self.acquire_lock(lock_key, lock_value, expire_time=5)
            print(f"  获取锁: {'成功' if acquired else '失败'}")
            
            if acquired:
                # 尝试获取同一个锁（应该失败）
                lock_value2 = str(uuid.uuid4())
                acquired2 = self.acquire_lock(lock_key, lock_value2, expire_time=5)
                print(f"  再次获取锁: {'成功' if acquired2 else '失败（预期）'}")
                
                # 释放锁
                released = self.release_lock(lock_key, lock_value)
                print(f"  释放锁: {'成功' if released else '失败'}")
                
                # 释放后再次获取锁
                acquired3 = self.acquire_lock(lock_key, lock_value2, expire_time=5)
                print(f"  释放后获取锁: {'成功' if acquired3 else '失败'}")
            
            # 5. 测试缓存失效
            print("\n5. 测试缓存失效:")
            
            # 清除用户相关缓存
            self.invalidate_cache("cache:user*")
            print("  已清除用户相关缓存")
            
            # 再次获取用户（应该从数据库重新加载）
            start_time = time.time()
            user3 = self.get_user(user['id'])
            third_duration = time.time() - start_time
            print(f"  清除缓存后获取用户耗时: {third_duration:.4f}秒")
            
            print("\n✅ MySQL与Redis混合架构演示完成")
            
        except Exception as e:
            logger.error(f"MySQL与Redis混合架构演示失败: {e}")

class MySQLElasticsearchDemo(HybridArchitectureBase):
    """MySQL与Elasticsearch混合架构演示"""
    
    def __init__(self, config):
        super().__init__(config)
        self.es_client = self.connections.get('elasticsearch')
        
        # 初始化Elasticsearch索引
        self._setup_elasticsearch_index()
    
    def _setup_elasticsearch_index(self):
        """初始化Elasticsearch索引"""
        if not self.es_client:
            return
        
        try:
            # 创建产品索引映射
            if self.es_client.indices.exists(index="products"):
                return
            
            mapping = {
                "mappings": {
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword"}
                            },
                            "analyzer": "ik_max_word",
                            "search_analyzer": "ik_smart"
                        },
                        "description": {
                            "type": "text",
                            "analyzer": "ik_max_word",
                            "search_analyzer": "ik_smart"
                        },
                        "price": {"type": "float"},
                        "category": {
                            "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "keyword"}
                            }
                        },
                        "brand": {
                            "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "keyword"}
                            }
                        },
                        "tags": {"type": "keyword"},
                        "in_stock": {"type": "boolean"},
                        "created_at": {"type": "date"},
                        "updated_at": {"type": "date"}
                    }
                }
            }
            
            self.es_client.indices.create(index="products", body=mapping)
            logger.info("Elasticsearch产品索引已创建")
        except Exception as e:
            logger.error(f"创建Elasticsearch索引失败: {e}")
    
    def index_product(self, product_id):
        """
        将产品数据索引到Elasticsearch
        
        Args:
            product_id: 产品ID
            
        Returns:
            是否成功
        """
        if not self.es_client:
            return False
        
        try:
            # 从MySQL获取产品数据
            product = self.mysql_execute(
                """
                SELECT p.*, c.name AS category_name, b.name AS brand_name
                FROM products p
                JOIN categories c ON p.category_id = c.id
                JOIN brands b ON p.brand_id = b.id
                WHERE p.id = %s
                """,
                (product_id,),
                fetch_one=True
            )
            
            if not product:
                return False
            
            # 转换为Elasticsearch文档
            es_doc = {
                "id": product["id"],
                "name": product["name"],
                "description": product["description"],
                "price": float(product["price"]),
                "category": {
                    "id": product["category_id"],
                    "name": product["category_name"]
                },
                "brand": {
                    "id": product["brand_id"],
                    "name": product["brand_name"]
                },
                "tags": product.get("tags", "").split(",") if product.get("tags") else [],
                "in_stock": bool(product["in_stock"]),
                "created_at": product["created_at"],
                "updated_at": product.get("updated_at")
            }
            
            # 索引到Elasticsearch
            self.es_client.index(
                index="products",
                id=product_id,
                body=es_doc
            )
            
            logger.info(f"产品已索引到Elasticsearch: {product_id}")
            return True
        except Exception as e:
            logger.error(f"索引产品失败: {e}")
            return False
    
    def search_products(self, query_text, filters=None, sort=None, page=1, size=10):
        """
        搜索产品
        
        Args:
            query_text: 查询文本
            filters: 过滤条件
            sort: 排序方式
            page: 页码
            size: 每页大小
            
        Returns:
            搜索结果
        """
        if not self.es_client:
            return {
                "products": [],
                "total": 0,
                "page": page,
                "size": size,
                "pages": 0
            }
        
        try:
            # 构建Elasticsearch查询
            es_query = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": query_text,
                                    "fields": ["name^3", "description^2", "tags"],
                                    "type": "best_fields",
                                    "fuzziness": "AUTO"
                                }
                            }
                        ],
                        "filter": []
                    }
                },
                "from": (page - 1) * size,
                "size": size,
                "highlight": {
                    "fields": {
                        "name": {},
                        "description": {}
                    }
                }
            }
            
            # 添加过滤条件
            if filters:
                if "category_id" in filters:
                    es_query["query"]["bool"]["filter"].append(
                        {"term": {"category.id": filters["category_id"]}}
                    )
                
                if "brand_id" in filters:
                    es_query["query"]["bool"]["filter"].append(
                        {"term": {"brand.id": filters["brand_id"]}}
                    )
                
                if "min_price" in filters and "max_price" in filters:
                    es_query["query"]["bool"]["filter"].append(
                        {
                            "range": {
                                "price": {
                                    "gte": filters["min_price"],
                                    "lte": filters["max_price"]
                                }
                            }
                        }
                    )
                
                if "in_stock" in filters:
                    es_query["query"]["bool"]["filter"].append(
                        {"term": {"in_stock": filters["in_stock"]}}
                    )
            
            # 添加排序
            if sort:
                if sort == "price_asc":
                    es_query["sort"] = [{"price": {"order": "asc"}}]
                elif sort == "price_desc":
                    es_query["sort"] = [{"price": {"order": "desc"}}]
                elif sort == "created_desc":
                    es_query["sort"] = [{"created_at": {"order": "desc"}}]
                elif sort == "relevance":
                    es_query["sort"] = ["_score"]
            
            # 执行搜索
            response = self.es_client.search(
                index="products",
                body=es_query
            )
            
            # 处理搜索结果
            results = []
            for hit in response["hits"]["hits"]:
                product = hit["_source"]
                product["score"] = hit["_score"]
                
                # 添加高亮信息
                if "highlight" in hit:
                    product["highlight"] = hit["highlight"]
                
                results.append(product)
            
            return {
                "products": results,
                "total": response["hits"]["total"]["value"],
                "page": page,
                "size": size,
                "pages": (response["hits"]["total"]["value"] + size - 1) // size
            }
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return {
                "products": [],
                "total": 0,
                "page": page,
                "size": size,
                "pages": 0
            }
    
    def demo_mysql_elasticsearch(self):
        """演示MySQL与Elasticsearch混合架构"""
        print("\n===== MySQL与Elasticsearch混合架构演示 =====")
        
        try:
            # 1. 创建测试数据
            print("\n1. 创建测试数据:")
            
            # 创建必要的表
            self.mysql_execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(50) NOT NULL
                )
            """)
            
            self.mysql_execute("""
                CREATE TABLE IF NOT EXISTS brands (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(50) NOT NULL
                )
            """)
            
            self.mysql_execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    price DECIMAL(10,2) NOT NULL,
                    category_id INT,
                    brand_id INT,
                    tags VARCHAR(255),
                    in_stock BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories(id),
                    FOREIGN KEY (brand_id) REFERENCES brands(id)
                )
            """)
            
            # 插入测试分类
            self.mysql_execute("INSERT IGNORE INTO categories (id, name) VALUES (1, '电子产品'), (2, '服装')")
            
            # 插入测试品牌
            self.mysql_execute("INSERT IGNORE INTO brands (id, name) VALUES (1, '品牌A'), (2, '品牌B')")
            
            # 插入测试产品
            test_products = [
                {
                    'name': '智能手机',
                    'description': '高性能智能手机，配备大屏幕和强大的处理器',
                    'price': 2999.99,
                    'category_id': 1,
                    'brand_id': 1,
                    'tags': '智能手机,5G,拍照',
                    'in_stock': True
                },
                {
                    'name': '无线耳机',
                    'description': '降噪无线耳机，提供高品质音频体验',
                    'price': 599.99,
                    'category_id': 1,
                    'brand_id': 2,
                    'tags': '耳机,降噪,蓝牙',
                    'in_stock': True
                },
                {
                    'name': '运动T恤',
                    'description': '透气速干运动T恤，适合各种运动场景',
                    'price': 99.99,
                    'category_id': 2,
                    'brand_id': 1,
                    'tags': 'T恤,运动,速干',
                    'in_stock': True
                }
            ]
            
            product_ids = []
            for product_data in test_products:
                self.mysql_execute("""
                    INSERT INTO products (name, description, price, category_id, brand_id, tags, in_stock)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    product_data['name'],
                    product_data['description'],
                    product_data['price'],
                    product_data['category_id'],
                    product_data['brand_id'],
                    product_data['tags'],
                    product_data['in_stock']
                ))
                
                # 获取插入的产品ID
                product = self.mysql_execute(
                    "SELECT id FROM products WHERE name = %s ORDER BY id DESC LIMIT 1",
                    (product_data['name'],),
                    fetch_one=True
                )
                product_ids.append(product['id'])
                print(f"  创建产品: {product_data['name']} (ID: {product['id']})")
            
            # 2. 索引产品到Elasticsearch
            print("\n2. 索引产品到Elasticsearch:")
            for product_id in product_ids:
                success = self.index_product(product_id)
                print(f"  索引产品 {product_id}: {'成功' if success else '失败'}")
            
            # 3. 测试搜索功能
            print("\n3. 测试搜索功能:")
            
            # 基本搜索
            search_result = self.search_products("智能手机")
            print(f"  搜索'智能手机'，找到 {search_result['total']} 个结果")
            for product in search_result['products']:
                print(f"    - {product['name']}: {product['price']} 元")
            
            # 模糊搜索
            search_result = self.search_products("手机")
            print(f"\n  搜索'手机'，找到 {search_result['total']} 个结果")
            for product in search_result['products']:
                print(f"    - {product['name']}: {product['price']} 元 (评分: {product['score']:.2f})")
            
            # 带过滤条件的搜索
            search_result = self.search_products(
                "",
                filters={"category_id": 1, "min_price": 500, "max_price": 2000},
                sort="price_desc"
            )
            print(f"\n  搜索电子产品(500-2000元)，按价格降序，找到 {search_result['total']} 个结果")
            for product in search_result['products']:
                print(f"    - {product['name']}: {product['price']} 元")
            
            # 4. 测试高亮
            print("\n4. 测试搜索高亮:")
            search_result = self.search_products("运动")
            print(f"  搜索'运动'，找到 {search_result['total']} 个结果")
            for product in search_result['products']:
                print(f"    - {product['name']}")
                if 'highlight' in product:
                    if 'name' in product['highlight']:
                        print(f"      名称高亮: {product['highlight']['name'][0]}")
                    if 'description' in product['highlight']:
                        print(f"      描述高亮: {product['highlight']['description'][0]}")
            
            # 5. 测试性能对比
            print("\n5. 测试性能对比:")
            
            # MySQL搜索
            start_time = time.time()
            mysql_results = self.mysql_execute(
                "SELECT * FROM products WHERE name LIKE '%手机%' OR description LIKE '%手机%'"
            )
            mysql_duration = time.time() - start_time
            print(f"  MySQL搜索耗时: {mysql_duration:.4f}秒，结果数: {len(mysql_results)}")
            
            # Elasticsearch搜索
            start_time = time.time()
            es_result = self.search_products("手机")
            es_duration = time.time() - start_time
            print(f"  Elasticsearch搜索耗时: {es_duration:.4f}秒，结果数: {es_result['total']}")
            
            if es_duration < mysql_duration:
                print(f"  Elasticsearch比MySQL快 {mysql_duration/es_duration:.2f} 倍")
            else:
                print(f"  MySQL比Elasticsearch快 {es_duration/mysql_duration:.2f} 倍")
            
            print("\n✅ MySQL与Elasticsearch混合架构演示完成")
            
        except Exception as e:
            logger.error(f"MySQL与Elasticsearch混合架构演示失败: {e}")

def get_default_config():
    """获取默认配置"""
    return {
        'mysql': {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '',
            'database': 'hybrid_demo',
            'charset': 'utf8mb4',
            'autocommit': True
        },
        'redis': {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'decode_responses': True
        },
        'mongodb': {
            'uri': 'mongodb://localhost:27017/',
            'database': 'hybrid_demo'
        },
        'elasticsearch': {
            'hosts': ['localhost:9200'],
            'timeout': 30
        },
        'cassandra': {
            'host': 'localhost',
            'port': 9042,
            'keyspace': 'hybrid_demo'
        }
    }

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='MySQL与NoSQL混合架构演示')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--demo', 
                        choices=['mysql_mongodb', 'mysql_redis', 'mysql_elasticsearch', 'all'], 
                        default='all', 
                        help='选择要运行的演示')
    
    args = parser.parse_args()
    
    # 加载配置
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f)
    else:
        config = get_default_config()
    
    try:
        # 创建MySQL数据库（如果不存在）
        temp_conn = pymysql.Connect(
            host=config['mysql']['host'],
            port=config['mysql']['port'],
            user=config['mysql']['user'],
            password=config['mysql']['password']
        )
        with temp_conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config['mysql']['database']}")
            temp_conn.commit()
        temp_conn.close()
        
        # 运行演示
        if args.demo == 'mysql_mongodb' or args.demo == 'all':
            print("\n" + "=" * 50)
            print("MySQL与MongoDB混合架构演示")
            print("=" * 50)
            demo = MySQLMongoDBDemo(config)
            demo.demo_mysql_mongodb()
            demo.close()
            
            if args.demo != 'all':
                return
        
        if args.demo == 'mysql_redis' or args.demo == 'all':
            print("\n" + "=" * 50)
            print("MySQL与Redis混合架构演示")
            print("=" * 50)
            demo = MySQLRedisDemo(config)
            demo.demo_mysql_redis()
            demo.close()
            
            if args.demo != 'all':
                return
        
        if args.demo == 'mysql_elasticsearch' or args.demo == 'all':
            print("\n" + "=" * 50)
            print("MySQL与Elasticsearch混合架构演示")
            print("=" * 50)
            demo = MySQLElasticsearchDemo(config)
            demo.demo_mysql_elasticsearch()
            demo.close()
            
            if args.demo != 'all':
                return
        
        print("\n" + "=" * 50)
        print("所有演示完成")
        print("=" * 50)
        
    except Exception as e:
        logger.error(f"运行演示失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()