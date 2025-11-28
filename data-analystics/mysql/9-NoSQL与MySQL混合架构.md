# 9-NoSQL与MySQL混合架构

## 1. 混合数据架构概述

### 1.1 为什么需要混合架构

在现代应用系统中，单一类型的数据库往往无法满足所有业务需求。不同的数据模型和访问模式需要不同的存储解决方案，这导致了混合数据架构的兴起。

混合数据架构的主要驱动因素包括：

1. **多样化数据需求**：
   - 结构化数据（关系型）：用户信息、订单、财务记录等
   - 半结构化数据（文档型）：用户配置、JSON文档、日志数据等
   - 非结构化数据（键值、图）：缓存、社交网络、推荐数据等

2. **不同的访问模式**：
   - 高并发读写：需要快速响应的实时操作
   - 复杂查询：需要多表关联的分析查询
   - 大规模数据：需要水平扩展的海量数据存储

3. **性能要求**：
   - 低延迟：关键业务操作需要毫秒级响应
   - 高吞吐：需要处理大量并发请求
   - 可扩展性：随业务增长平滑扩展

4. **一致性需求**：
   - 强一致性：财务交易等需要严格ACID保证
   - 最终一致性：社交更新等可以接受短暂不一致

### 1.2 混合架构的优势

1. **扬长避短**：结合不同数据库的优势，发挥各自长处
2. **性能优化**：针对不同访问模式选择最适合的存储引擎
3. **成本效益**：根据数据价值和使用频率选择合适的存储方案
4. **技术灵活性**：利用新技术解决特定问题，避免全面重构
5. **渐进式演进**：逐步引入新技术，降低迁移风险

### 1.3 混合架构挑战

1. **数据一致性**：跨不同数据库系统维护数据一致性
2. **事务管理**：分布式事务处理和补偿机制
3. **操作复杂性**：多系统部署、监控和维护
4. **技能要求**：需要团队掌握多种数据库技术
5. **数据集成**：不同系统间的数据同步和转换

## 2. MySQL与NoSQL数据模型对比

### 2.1 关系模型 vs 文档模型

| 特性 | MySQL (关系模型) | MongoDB (文档模型) |
|------|-----------------|-------------------|
| 数据结构 | 表格行和列，预定义schema | JSON/BSON文档，灵活schema |
| 关系表示 | 外键和JOIN | 嵌入文档和引用 |
| 查询语言 | SQL | MongoDB查询语言 |
| 事务支持 | 完整ACID事务 | 文档级原子操作 |
| 扩展方式 | 垂直扩展为主，水平分片 | 水平扩展为主 |
| 适用场景 | 强一致性、复杂查询 | 灵活schema、快速迭代 |

### 2.2 关系模型 vs 键值模型

| 特性 | MySQL (关系模型) | Redis (键值模型) |
|------|-----------------|------------------|
| 数据结构 | 表格行和列 | 简单键值对 |
| 访问模式 | 复杂查询和关联 | 简单键值访问 |
| 性能特点 | 查询复杂但功能强大 | 访问速度极快 |
| 数据持久性 | 持久化存储 | 内存为主，可选持久化 |
| 适用场景 | 业务数据存储 | 缓存、会话、计数器 |

### 2.3 关系模型 vs 列族模型

| 特性 | MySQL (关系模型) | Cassandra (列族模型) |
|------|-----------------|---------------------|
| 数据结构 | 行列固定的表 | 动态列族 |
| 分区方式 | 分片和分区 | 分布式哈希 |
| 写性能 | 中等 | 极高 |
| 一致性模型 | 强一致性 | 可调一致性 |
| 适用场景 | 交易型应用 | 时间序列、日志 |

### 2.4 关系模型 vs 图模型

| 特性 | MySQL (关系模型) | Neo4j (图模型) |
|------|-----------------|----------------|
| 数据结构 | 表格和关系 | 节点和边 |
| 关系查询 | JOIN遍历 | 图遍历算法 |
| 复杂关系 | 多表JOIN性能下降 | 天然支持复杂关系 |
| 适用场景 | 结构化数据 | 社交网络、推荐 |

## 3. 常见混合架构模式

### 3.1 MySQL + MongoDB 模式

这种模式将MySQL作为主要的事务性数据存储，MongoDB用于存储半结构化数据和文档内容。

#### 3.1.1 适用场景
- 电商平台：产品信息、订单存储在MySQL，产品评论、用户画像存储在MongoDB
- 内容管理系统：结构化内容在MySQL，灵活内容块和元数据在MongoDB
- 日志分析：业务数据在MySQL，日志和事件数据在MongoDB

#### 3.1.2 架构设计

```plaintext
                     ┌─────────────┐
                     │   应用服务   │
                     └──────┬──────┘
                            │
                    ┌───────┴───────┐
                    │               │
          ┌─────────┴─────────┐   ┌─┴────────┐
          │    MySQL集群      │   │MongoDB集群 │
          │(事务性数据)       │   │(文档数据)  │
          └───────────────────┘   └───────────┘
```

#### 3.1.3 实现方式

**1. 数据分离策略**
```sql
-- MySQL中的用户核心信息
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- MySQL中的订单核心信息
CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status ENUM('pending', 'paid', 'shipped', 'delivered', 'cancelled') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

```javascript
// MongoDB中的用户扩展信息
{
  "_id": ObjectId("60a5e3b3f3a6e4a5f8e7a1b2"),
  "user_id": 12345,
  "profile": {
    "first_name": "张",
    "last_name": "三",
    "avatar": "https://example.com/avatars/user12345.jpg",
    "bio": "软件工程师，热爱开源技术",
    "interests": ["编程", "开源", "人工智能", "大数据"],
    "social_links": {
      "github": "https://github.com/zhangsan",
      "linkedin": "https://linkedin.com/in/zhangsan",
      "twitter": "@zhangsan"
    }
  },
  "preferences": {
    "theme": "dark",
    "language": "zh-CN",
    "notifications": {
      "email": true,
      "sms": false,
      "push": true
    }
  },
  "activity_history": [
    {
      "action": "login",
      "timestamp": ISODate("2023-05-15T08:30:00Z"),
      "ip_address": "192.168.1.100"
    },
    {
      "action": "purchase",
      "timestamp": ISODate("2023-05-14T14:22:15Z"),
      "product_id": 67890,
      "amount": 199.99
    }
  ],
  "created_at": ISODate("2023-01-10T10:15:30Z"),
  "updated_at": ISODate("2023-05-15T08:30:00Z")
}
```

```javascript
// MongoDB中的产品评论
{
  "_id": ObjectId("60a5e3b3f3a6e4a5f8e7a1c3"),
  "product_id": 67890,
  "user_id": 12345,
  "rating": 5,
  "title": "非常满意的产品",
  "content": "这个产品超出了我的预期，质量很好，物流也很快。",
  "images": [
    "https://example.com/reviews/img1.jpg",
    "https://example.com/reviews/img2.jpg"
  ],
  "helpful_votes": 15,
  "verified_purchase": true,
  "response_from_seller": {
    "timestamp": ISODate("2023-05-16T09:15:00Z"),
    "content": "感谢您的反馈，很高兴您对我们的产品满意！"
  },
  "created_at": ISODate("2023-05-14T16:45:20Z")
}
```

**2. 数据同步机制**

```python
# Python示例：MySQL与MongoDB数据同步
import pymysql
from pymongo import MongoClient
import json
from datetime import datetime

class HybridDataManager:
    def __init__(self, mysql_config, mongodb_config):
        # 连接MySQL
        self.mysql_conn = pymysql.Connect(**mysql_config)
        
        # 连接MongoDB
        self.mongo_client = MongoClient(mongodb_config['uri'])
        self.mongo_db = self.mongo_client[mongodb_config['database']]
    
    def create_user_with_profile(self, user_data, profile_data):
        """创建用户及扩展资料"""
        try:
            # 开启MySQL事务
            with self.mysql_conn.cursor() as cursor:
                # 插入MySQL用户核心信息
                cursor.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                    (user_data['username'], user_data['email'], user_data['password_hash'])
                )
                user_id = cursor.lastrowid
                
                # 提交MySQL事务
                self.mysql_conn.commit()
                
                # 插入MongoDB用户扩展信息
                profile_data['user_id'] = user_id
                profile_data['created_at'] = datetime.utcnow()
                
                self.mongo_db.user_profiles.insert_one(profile_data)
                
                return user_id
                
        except Exception as e:
            # 回滚MySQL事务
            self.mysql_conn.rollback()
            raise e
    
    def get_user_with_profile(self, user_id):
        """获取用户及扩展资料"""
        # 从MySQL获取核心信息
        with self.mysql_conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
        
        if not user:
            return None
        
        # 从MongoDB获取扩展信息
        profile = self.mongo_db.user_profiles.find_one({"user_id": user_id})
        
        # 合并数据
        result = user
        if profile:
            # 移除MongoDB内部字段
            del profile['_id']
            result['profile'] = profile
        
        return result
```

### 3.2 MySQL + Redis 模式

这种模式使用Redis作为缓存层，提高MySQL的读取性能，同时利用Redis的高性能特性处理特定场景。

#### 3.2.1 适用场景
- 高频读取：用户会话、产品目录、配置信息
- 实时计数：点赞数、浏览量、库存数量
- 分布式锁：防止并发操作冲突
- 排行榜：实时排名、热门内容

#### 3.2.2 架构设计

```plaintext
                     ┌─────────────┐
                     │   应用服务   │
                     └──────┬──────┘
                            │
                ┌───────────┴───────────┐
                │                       │
          ┌─────┴─────┐         ┌───────┴───────┐
          │  Redis    │         │    MySQL     │
          │  缓存层   │◄────────►│   主存储    │
          └───────────┘         └──────────────┘
```

#### 3.2.3 实现方式

**1. 缓存策略**

```python
# Python示例：MySQL与Redis缓存策略
import redis
import pymysql
import json
from functools import wraps

class CacheManager:
    def __init__(self, mysql_config, redis_config):
        # 连接MySQL
        self.mysql_conn = pymysql.Connect(**mysql_config)
        
        # 连接Redis
        self.redis_client = redis.Redis(**redis_config)
        
        # 缓存过期时间（秒）
        self.default_ttl = 3600  # 1小时
    
    def cache_result(self, key_prefix, ttl=None):
        """装饰器：缓存查询结果"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 生成缓存键
                cache_key = f"{key_prefix}:{hash(str(args) + str(kwargs))}"
                
                # 尝试从缓存获取
                cached_result = self.redis_client.get(cache_key)
                if cached_result:
                    return json.loads(cached_result)
                
                # 缓存未命中，执行原函数
                result = func(*args, **kwargs)
                
                # 将结果存入缓存
                expire_time = ttl if ttl is not None else self.default_ttl
                self.redis_client.setex(
                    cache_key, 
                    expire_time, 
                    json.dumps(result, default=str)
                )
                
                return result
            return wrapper
        return decorator
    
    @cache_result("user", 1800)  # 30分钟
    def get_user(self, user_id):
        """获取用户信息（带缓存）"""
        with self.mysql_conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            return cursor.fetchone()
    
    @cache_result("product", 3600)  # 1小时
    def get_product(self, product_id):
        """获取产品信息（带缓存）"""
        with self.mysql_conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
            return cursor.fetchone()
    
    def invalidate_cache(self, pattern):
        """清除匹配模式的所有缓存"""
        for key in self.redis_client.scan_iter(match=pattern):
            self.redis_client.delete(key)
    
    def update_user(self, user_id, user_data):
        """更新用户信息并清除相关缓存"""
        with self.mysql_conn.cursor() as cursor:
            # 构建UPDATE语句
            set_clause = ", ".join([f"{k} = %s" for k in user_data.keys()])
            values = list(user_data.values()) + [user_id]
            
            cursor.execute(f"UPDATE users SET {set_clause} WHERE id = %s", values)
            self.mysql_conn.commit()
        
        # 清除用户相关缓存
        self.invalidate_cache(f"user:{user_id}*")
```

**2. 实时计数器**

```python
class CounterManager:
    def __init__(self, mysql_config, redis_config):
        # 连接MySQL
        self.mysql_conn = pymysql.Connect(**mysql_config)
        
        # 连接Redis
        self.redis_client = redis.Redis(**redis_config)
    
    def increment_view(self, item_type, item_id):
        """增加浏览量"""
        # Redis中的键名
        key = f"{item_type}:{item_id}:views"
        
        # 增加Redis计数器
        count = self.redis_client.incr(key)
        
        # 设置过期时间（24小时）
        self.redis_client.expire(key, 86400)
        
        # 定期同步到MySQL（每100次浏览量同步一次）
        if count % 100 == 0:
            self._sync_counter_to_mysql(item_type, item_id, 'views', count)
        
        return count
    
    def get_view_count(self, item_type, item_id):
        """获取浏览量"""
        # 先从Redis获取
        key = f"{item_type}:{item_id}:views"
        redis_count = self.redis_client.get(key)
        
        if redis_count:
            return int(redis_count)
        
        # Redis中没有，从MySQL获取
        with self.mysql_conn.cursor() as cursor:
            cursor.execute(
                f"SELECT view_count FROM {item_type}s WHERE id = %s",
                (item_id,)
            )
            result = cursor.fetchone()
            
            if result:
                count = result[0]
                # 同步到Redis
                self.redis_client.setex(key, 86400, count)
                return count
            
            return 0
    
    def _sync_counter_to_mysql(self, item_type, item_id, counter_field, value):
        """同步计数器到MySQL"""
        with self.mysql_conn.cursor() as cursor:
            cursor.execute(
                f"UPDATE {item_type}s SET {counter_field} = %s WHERE id = %s",
                (value, item_id)
            )
            self.mysql_conn.commit()
```

**3. 分布式锁**

```python
class DistributedLock:
    def __init__(self, redis_client):
        self.redis_client = redis_client
        # 获取锁的重试间隔（毫秒）
        self.retry_delay = 100
        # 获取锁的超时时间（毫秒）
        self.acquire_timeout = 10000
    
    def acquire(self, lock_key, lock_value, expire_time=30000):
        """获取分布式锁"""
        # 使用SET命令的NX和PX选项实现原子性锁获取
        end_time = time.time() + self.acquire_timeout / 1000
        
        while time.time() < end_time:
            # 尝试获取锁
            if self.redis_client.set(
                lock_key, lock_value, nx=True, px=expire_time
            ):
                return True
            
            # 等待后重试
            time.sleep(self.retry_delay / 1000)
        
        return False
    
    def release(self, lock_key, lock_value):
        """释放分布式锁"""
        # 使用Lua脚本确保只有锁的持有者才能释放锁
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        result = self.redis_client.eval(
            lua_script, 1, lock_key, lock_value
        )
        
        return result == 1

# 使用示例
def process_order(order_id):
    """处理订单（使用分布式锁防止并发处理）"""
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    lock = DistributedLock(redis_client)
    
    lock_key = f"order_lock:{order_id}"
    lock_value = str(uuid.uuid4())
    
    # 尝试获取锁
    if lock.acquire(lock_key, lock_value):
        try:
            # 获取锁成功，处理订单
            print(f"Processing order {order_id}")
            # 业务逻辑...
            
            return True
        finally:
            # 释放锁
            lock.release(lock_key, lock_value)
    else:
        # 获取锁失败
        print(f"Could not acquire lock for order {order_id}")
        return False
```

### 3.3 MySQL + Elasticsearch 模式

这种模式使用Elasticsearch作为全文搜索引擎，弥补MySQL在复杂搜索场景下的性能不足。

#### 3.3.1 适用场景
- 全文搜索：商品搜索、内容检索
- 复杂过滤：多维度、多条件筛选
- 聚合分析：数据统计、趋势分析
- 地理空间搜索：位置相关查询

#### 3.3.2 架构设计

```plaintext
                     ┌─────────────┐
                     │   应用服务   │
                     └──────┬──────┘
                            │
                ┌───────────┴───────────┐
                │                       │
          ┌─────┴─────┐         ┌───────┴───────┐
          │Elasticsearch│         │    MySQL     │
          │  搜索引擎  │◄────────►│   主存储    │
          └───────────┘         └──────────────┘
```

#### 3.3.3 实现方式

**1. 数据同步机制**

```python
# Python示例：MySQL与Elasticsearch数据同步
from elasticsearch import Elasticsearch
import pymysql
import json
from datetime import datetime

class SearchManager:
    def __init__(self, mysql_config, es_config):
        # 连接MySQL
        self.mysql_conn = pymysql.Connect(**mysql_config)
        
        # 连接Elasticsearch
        self.es_client = Elasticsearch(**es_config)
        
        # 索引名称
        self.product_index = "products"
        self.article_index = "articles"
    
    def index_product(self, product_id):
        """将产品数据索引到Elasticsearch"""
        # 从MySQL获取产品数据
        with self.mysql_conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                """
                SELECT p.*, c.name AS category_name, b.name AS brand_name
                FROM products p
                JOIN categories c ON p.category_id = c.id
                JOIN brands b ON p.brand_id = b.id
                WHERE p.id = %s
                """,
                (product_id,)
            )
            product = cursor.fetchone()
        
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
            "updated_at": product["updated_at"]
        }
        
        # 索引到Elasticsearch
        try:
            self.es_client.index(
                index=self.product_index,
                id=product_id,
                body=es_doc
            )
            return True
        except Exception as e:
            print(f"Failed to index product {product_id}: {e}")
            return False
    
    def search_products(self, query_text, filters=None, sort=None, page=1, size=10):
        """搜索产品"""
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
        try:
            response = self.es_client.search(
                index=self.product_index,
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
            
            # 获取产品详情（从MySQL）
            for product in results:
                product_id = product["id"]
                with self.mysql_conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
                    db_product = cursor.fetchone()
                    
                    if db_product:
                        # 合并Elasticsearch和MySQL数据
                        product.update(db_product)
            
            return {
                "products": results,
                "total": response["hits"]["total"]["value"],
                "page": page,
                "size": size,
                "pages": (response["hits"]["total"]["value"] + size - 1) // size
            }
            
        except Exception as e:
            print(f"Search failed: {e}")
            return {
                "products": [],
                "total": 0,
                "page": page,
                "size": size,
                "pages": 0
            }
```

### 3.4 MySQL + Cassandra 模式

这种模式使用Cassandra处理大规模写入和时间序列数据，MySQL处理核心业务数据。

#### 3.4.1 适用场景
- 时间序列数据：IoT传感器数据、应用监控指标
- 高写入负载：日志收集、事件流处理
- 大规模数据：用户行为跟踪、分析数据
- 地理分布：全球部署的多数据中心架构

#### 3.4.2 架构设计

```plaintext
                     ┌─────────────┐
                     │   应用服务   │
                     └──────┬──────┘
                            │
                ┌───────────┴───────────┐
                │                       │
          ┌─────┴─────┐         ┌───────┴───────┐
          │ Cassandra │         │    MySQL     │
          │时序数据存储│◄────────►│   主存储    │
          └───────────┘         └──────────────┘
```

#### 3.4.3 实现方式

**1. 数据模型设计**

```sql
-- MySQL中的用户和设备信息
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE devices (
    id VARCHAR(36) PRIMARY KEY,  -- UUID
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

```cql
-- Cassandra中的时间序列数据表
CREATE TABLE user_events (
    user_id INT,
    device_id UUID,
    event_id TIMEUUID,
    event_type VARCHAR(50),
    event_data MAP<TEXT, TEXT>,
    timestamp TIMESTAMP,
    PRIMARY KEY ((user_id, device_id), timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

-- 用于聚合查询的物化视图
CREATE MATERIALIZED VIEW user_events_by_type AS
    SELECT *
    FROM user_events
    WHERE user_id IS NOT NULL AND device_id IS NOT NULL AND event_type IS NOT NULL AND timestamp IS NOT NULL
    PRIMARY KEY ((user_id, event_type), timestamp);
```

**2. 数据写入机制**

```python
# Python示例：MySQL与Cassandra数据写入
import pymysql
from cassandra.cluster import Cluster
from cassandra.util import uuid_from_time
import uuid
from datetime import datetime

class TimeSeriesDataManager:
    def __init__(self, mysql_config, cassandra_config):
        # 连接MySQL
        self.mysql_conn = pymysql.Connect(**mysql_config)
        
        # 连接Cassandra
        cluster = Cluster([cassandra_config['host']])
        self.cassandra_session = cluster.connect(cassandra_config['keyspace'])
        
        # 准备语句（提高性能）
        self.insert_event_prepared = self.cassandra_session.prepare(
            """
            INSERT INTO user_events (user_id, device_id, event_id, event_type, event_data, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            """
        )
    
    def register_device(self, user_id, device_name, device_type):
        """注册新设备"""
        device_id = str(uuid.uuid4())
        
        with self.mysql_conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO devices (id, user_id, name, type) VALUES (%s, %s, %s, %s)",
                (device_id, user_id, device_name, device_type)
            )
            self.mysql_conn.commit()
        
        return device_id
    
    def log_event(self, user_id, device_id, event_type, event_data):
        """记录事件到Cassandra"""
        # 生成时间UUID
        event_id = uuid_from_time(datetime.now())
        
        # 执行插入
        self.cassandra_session.execute(
            self.insert_event_prepared,
            (user_id, device_id, event_id, event_type, event_data, datetime.now())
        )
    
    def get_user_events(self, user_id, device_id=None, event_type=None, limit=100):
        """获取用户事件"""
        if device_id and event_type:
            query = "SELECT * FROM user_events WHERE user_id = %s AND device_id = %s AND event_type = %s LIMIT %s"
            params = (user_id, device_id, event_type, limit)
        elif device_id:
            query = "SELECT * FROM user_events WHERE user_id = %s AND device_id = %s LIMIT %s"
            params = (user_id, device_id, limit)
        elif event_type:
            query = "SELECT * FROM user_events_by_type WHERE user_id = %s AND event_type = %s LIMIT %s"
            params = (user_id, event_type, limit)
        else:
            query = "SELECT * FROM user_events WHERE user_id = %s LIMIT %s"
            params = (user_id, limit)
        
        rows = self.cassandra_session.execute(query, params)
        return list(rows)
    
    def get_aggregated_events(self, user_id, time_window_hours=24):
        """获取聚合事件数据"""
        from datetime import datetime, timedelta
        
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=time_window_hours)
        
        query = """
        SELECT event_type, count(*) as event_count
        FROM user_events
        WHERE user_id = %s AND timestamp >= %s AND timestamp <= %s
        GROUP BY event_type
        """
        
        rows = self.cassandra_session.execute(query, (user_id, start_time, end_time))
        return {row.event_type: row.event_count for row in rows}
```

## 4. 数据一致性与同步策略

### 4.1 数据一致性级别

#### 4.1.1 强一致性
**特点**：所有副本在任意时刻都有相同的数据
**适用场景**：金融交易、库存管理、用户认证
**实现方式**：两阶段提交、Paxos/Raft协议

```python
# Python示例：两阶段提交
import pymysql
from pymongo import MongoClient

class TwoPhaseCommit:
    def __init__(self, mysql_config, mongodb_config):
        self.mysql_conn = pymysql.Connect(**mysql_config)
        self.mongo_client = MongoClient(mongodb_config['uri'])
        self.mongo_db = self.mongo_client[mongodb_config['database']]
    
    def transfer_data(self, source_table, target_collection, data_id):
        """两阶段提交数据迁移"""
        mysql_cursor = self.mysql_conn.cursor()
        
        try:
            # 阶段1：准备阶段
            # 1.1 MySQL准备
            mysql_cursor.execute(f"SELECT * FROM {source_table} WHERE id = %s FOR UPDATE", (data_id,))
            mysql_data = mysql_cursor.fetchone()
            
            if not mysql_data:
                raise Exception("Data not found in MySQL")
            
            # 1.2 MongoDB准备（插入临时文档）
            temp_doc = dict(mysql_data)
            temp_doc['_temp'] = True
            temp_doc['_status'] = 'preparing'
            
            self.mongo_db[target_collection].insert_one(temp_doc)
            
            # 阶段2：提交阶段
            # 2.1 MySQL提交
            mysql_cursor.execute(f"DELETE FROM {source_table} WHERE id = %s", (data_id,))
            self.mysql_conn.commit()
            
            # 2.2 MongoDB提交（移除临时标记）
            self.mongo_db[target_collection].update_one(
                {'_id': temp_doc['_id']},
                {'$unset': {'_temp': True, '_status': True}}
            )
            
            return True
            
        except Exception as e:
            # 回滚操作
            try:
                # MySQL回滚
                self.mysql_conn.rollback()
                
                # MongoDB回滚（删除临时文档）
                self.mongo_db[target_collection].delete_many(
                    {'_status': 'preparing'}
                )
            except:
                pass
            
            raise e
        finally:
            mysql_cursor.close()
```

#### 4.1.2 最终一致性
**特点**：系统经过一段时间后所有副本会达到一致状态
**适用场景**：社交网络、内容分发、分析数据
**实现方式**：异步复制、事件溯源、CQRS模式

```python
# Python示例：基于事件溯源的最终一致性
import json
import uuid
from datetime import datetime
import threading
import time
import queue

class EventSourcingManager:
    def __init__(self, mysql_config, mongodb_config):
        # 连接MySQL
        self.mysql_conn = pymysql.Connect(**mysql_config)
        
        # 连接MongoDB
        self.mongo_client = MongoClient(mongodb_config['uri'])
        self.mongo_db = self.mongo_client[mongodb_config['database']]
        
        # 事件队列
        self.event_queue = queue.Queue()
        
        # 启动事件处理器线程
        self.event_processor_thread = threading.Thread(target=self._process_events)
        self.event_processor_thread.daemon = True
        self.event_processor_thread.start()
        
        # 确保事件表存在
        self._ensure_event_table_exists()
    
    def _ensure_event_table_exists(self):
        """确保事件表存在"""
        with self.mysql_conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id VARCHAR(36) PRIMARY KEY,
                    aggregate_type VARCHAR(50) NOT NULL,
                    aggregate_id VARCHAR(36) NOT NULL,
                    event_type VARCHAR(50) NOT NULL,
                    event_data JSON NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed BOOLEAN DEFAULT FALSE,
                    processed_at TIMESTAMP NULL
                )
            """)
            self.mysql_conn.commit()
    
    def save_event(self, aggregate_type, aggregate_id, event_type, event_data):
        """保存事件"""
        event_id = str(uuid.uuid4())
        
        with self.mysql_conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO events (id, aggregate_type, aggregate_id, event_type, event_data)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (event_id, aggregate_type, aggregate_id, event_type, json.dumps(event_data))
            )
            self.mysql_conn.commit()
        
        # 将事件加入处理队列
        self.event_queue.put({
            'id': event_id,
            'aggregate_type': aggregate_type,
            'aggregate_id': aggregate_id,
            'event_type': event_type,
            'event_data': event_data
        })
        
        return event_id
    
    def _process_events(self):
        """事件处理器线程"""
        while True:
            try:
                # 从队列获取事件
                event = self.event_queue.get(timeout=1)
                
                # 处理事件
                self._handle_event(event)
                
                # 标记事件为已处理
                self._mark_event_processed(event['id'])
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing event: {e}")
    
    def _handle_event(self, event):
        """处理单个事件"""
        aggregate_type = event['aggregate_type']
        event_type = event['event_type']
        event_data = event['event_data']
        
        # 根据事件类型处理
        if aggregate_type == 'user':
            self._handle_user_event(event_type, event_data)
        elif aggregate_type == 'order':
            self._handle_order_event(event_type, event_data)
    
    def _handle_user_event(self, event_type, event_data):
        """处理用户事件"""
        if event_type == 'UserCreated':
            # 在MongoDB创建用户文档
            user_doc = {
                'id': event_data['id'],
                'username': event_data['username'],
                'email': event_data['email'],
                'created_at': event_data['created_at'],
                'profile': {}
            }
            self.mongo_db.users.insert_one(user_doc)
            
        elif event_type == 'UserProfileUpdated':
            # 更新MongoDB中的用户档案
            self.mongo_db.users.update_one(
                {'id': event_data['user_id']},
                {'$set': {'profile': event_data['profile']}}
            )
    
    def _handle_order_event(self, event_type, event_data):
        """处理订单事件"""
        if event_type == 'OrderPlaced':
            # 在MongoDB创建订单文档
            order_doc = {
                'id': event_data['id'],
                'user_id': event_data['user_id'],
                'items': event_data['items'],
                'total_amount': event_data['total_amount'],
                'status': event_data['status'],
                'created_at': event_data['created_at']
            }
            self.mongo_db.orders.insert_one(order_doc)
            
        elif event_type == 'OrderStatusChanged':
            # 更新MongoDB中的订单状态
            self.mongo_db.orders.update_one(
                {'id': event_data['order_id']},
                {'$set': {'status': event_data['new_status'], 'updated_at': datetime.now()}}
            )
    
    def _mark_event_processed(self, event_id):
        """标记事件为已处理"""
        with self.mysql_conn.cursor() as cursor:
            cursor.execute(
                "UPDATE events SET processed = TRUE, processed_at = NOW() WHERE id = %s",
                (event_id,)
            )
            self.mysql_conn.commit()
```

### 4.2 同步策略模式

#### 4.2.1 双写模式
**描述**：应用层同时写入MySQL和NoSQL数据库
**优点**：实现简单，实时性好
**缺点**：数据不一致风险高，系统复杂度增加

```python
# Python示例：双写模式
import pymysql
from pymongo import MongoClient

class DualWriteManager:
    def __init__(self, mysql_config, mongodb_config):
        self.mysql_conn = pymysql.Connect(**mysql_config)
        self.mongo_client = MongoClient(mongodb_config['uri'])
        self.mongo_db = self.mongo_client[mongodb_config['database']]
    
    def create_user(self, user_data):
        """创建用户（双写）"""
        user_id = None
        
        try:
            # 写入MySQL
            with self.mysql_conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                    (user_data['username'], user_data['email'], user_data['password_hash'])
                )
                user_id = cursor.lastrowid
                self.mysql_conn.commit()
            
            # 写入MongoDB
            mongo_doc = {
                'user_id': user_id,
                'profile': user_data.get('profile', {}),
                'preferences': user_data.get('preferences', {}),
                'created_at': datetime.utcnow()
            }
            self.mongo_db.user_profiles.insert_one(mongo_doc)
            
            return user_id
            
        except Exception as e:
            # 回滚MySQL
            if user_id:
                with self.mysql_conn.cursor() as cursor:
                    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                    self.mysql_conn.commit()
            
            raise e
```

#### 4.2.2 事件驱动模式
**描述**：通过事件系统协调不同数据库间的数据同步
**优点**：解耦系统，扩展性好，可追踪变更
**缺点**：延迟较高，系统复杂

```python
# Python示例：事件驱动模式
import json
import threading
import queue
import time

class EventBus:
    def __init__(self):
        self.subscribers = {}
        self.event_queue = queue.Queue()
        
        # 启动事件处理线程
        self.processor_thread = threading.Thread(target=self._process_events)
        self.processor_thread.daemon = True
        self.processor_thread.start()
    
    def publish(self, event_type, data):
        """发布事件"""
        event = {
            'id': str(uuid.uuid4()),
            'type': event_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        self.event_queue.put(event)
        return event['id']
    
    def subscribe(self, event_type, handler):
        """订阅事件"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        self.subscribers[event_type].append(handler)
    
    def _process_events(self):
        """处理事件队列"""
        while True:
            try:
                event = self.event_queue.get(timeout=1)
                
                # 分发给订阅者
                if event['type'] in self.subscribers:
                    for handler in self.subscribers[event['type']]:
                        handler(event)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing event: {e}")

# 使用示例
event_bus = EventBus()

# MySQL处理器
def mysql_handler(event):
    if event['type'] == 'UserCreated':
        with mysql_conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (event['data']['username'], event['data']['email'], event['data']['password_hash'])
            )
            mysql_conn.commit()

# MongoDB处理器
def mongodb_handler(event):
    if event['type'] == 'UserCreated':
        user_doc = {
            'user_id': event['data']['id'],
            'profile': event['data'].get('profile', {}),
            'created_at': event['timestamp']
        }
        mongo_db.user_profiles.insert_one(user_doc)

# 订阅事件
event_bus.subscribe('UserCreated', mysql_handler)
event_bus.subscribe('UserCreated', mongodb_handler)

# 发布事件（创建用户）
event_bus.publish('UserCreated', {
    'id': 123,
    'username': 'newuser',
    'email': 'newuser@example.com',
    'password_hash': 'hashed_password',
    'profile': {'first_name': 'New', 'last_name': 'User'}
})
```

#### 4.2.3 CDC (Change Data Capture) 模式
**描述**：通过捕获数据库变更日志实现数据同步
**优点**：对应用透明，可靠性高
**缺点**：实现复杂，可能有延迟

```python
# Python示例：基于MySQL Binlog的CDC同步
from pymysqlreplication import BinLogStreamReader
from pymongo import MongoClient
import json

class CDCManager:
    def __init__(self, mysql_config, mongodb_config):
        self.mysql_settings = {
            'host': mysql_config['host'],
            'port': mysql_config.get('port', 3306),
            'user': mysql_config['user'],
            'passwd': mysql_config['password']
        }
        
        self.mongo_client = MongoClient(mongodb_config['uri'])
        self.mongo_db = self.mongo_client[mongodb_config['database']]
    
    def start_replication(self, server_id=100):
        """启动CDC复制"""
        # 流式读取binlog
        stream = BinLogStreamReader(
            connection_settings=self.mysql_settings,
            server_id=server_id,
            blocking=True,
            only_events=['DeleteRowsEvent', 'WriteRowsEvent', 'UpdateRowsEvent']
        )
        
        for binlogevent in stream:
            self._process_binlog_event(binlogevent)
        
        stream.close()
    
    def _process_binlog_event(self, binlogevent):
        """处理binlog事件"""
        table = binlogevent.table
        schema = binlogevent.schema
        
        # 只处理特定表的变更
        if schema == 'app_db' and table == 'users':
            for row in binlogevent.rows:
                self._sync_user_to_mongo(binlogevent.event_type, row)
    
    def _sync_user_to_mongo(self, event_type, row):
        """同步用户数据到MongoDB"""
        if event_type == 'WriteRowsEvent':
            # 插入事件
            user_data = row['values']
            mongo_doc = {
                'user_id': user_data['id'],
                'username': user_data['username'],
                'email': user_data['email'],
                'created_at': user_data['created_at'],
                'updated_at': user_data.get('updated_at')
            }
            self.mongo_db.users.insert_one(mongo_doc)
            
        elif event_type == 'UpdateRowsEvent':
            # 更新事件
            user_data = row['after_values']
            self.mongo_db.users.update_one(
                {'user_id': user_data['id']},
                {'$set': {
                    'username': user_data['username'],
                    'email': user_data['email'],
                    'updated_at': user_data.get('updated_at')
                }}
            )
            
        elif event_type == 'DeleteRowsEvent':
            # 删除事件
            user_data = row['values']
            self.mongo_db.users.delete_one({'user_id': user_data['id']})

# 启动CDC
cdc_manager = CDCManager(mysql_config, mongodb_config)
# 在单独线程中运行，避免阻塞主线程
import threading
cdc_thread = threading.Thread(target=cdc_manager.start_replication)
cdc_thread.daemon = True
cdc_thread.start()
```

## 5. 架构设计最佳实践

### 5.1 数据分布策略

#### 5.1.1 按功能分离
**原则**：根据数据特性和访问模式选择合适的存储
**示例**：
- 用户账户、订单：MySQL（事务性、强一致性）
- 产品目录、搜索：Elasticsearch（全文搜索）
- 用户画像、推荐：MongoDB（灵活schema）
- 会话、缓存：Redis（高速访问）

#### 5.1.2 按访问模式分离
**原则**：根据读写频率和数据大小选择存储
**示例**：
- 热数据：Redis + MySQL（高频读写）
- 温数据：MongoDB（中等频率）
- 冷数据：对象存储 + 大数据平台（归档分析）

#### 5.1.3 按数据生命周期分离
**原则**：根据数据活跃度进行分层存储
**示例**：
- 实时层：Redis（秒级）
- 近期层：MySQL（分钟到小时）
- 历史层：数据仓库 + 大数据平台（天级）

### 5.2 一致性保障策略

#### 5.2.1 Saga模式
**描述**：将长事务分解为一系列本地事务，通过补偿操作确保一致性
**适用场景**：跨服务的业务流程

```python
# Python示例：Saga模式实现
class SagaManager:
    def __init__(self):
        self.steps = []
        self.compensations = []
    
    def add_step(self, action, compensation):
        """添加步骤和补偿操作"""
        self.steps.append(action)
        self.compensations.append(compensation)
    
    def execute(self):
        """执行Saga事务"""
        executed_steps = []
        
        try:
            # 执行所有步骤
            for i, step in enumerate(self.steps):
                result = step()
                executed_steps.append(i)
            
            return True
        except Exception as e:
            # 执行补偿操作
            for step_index in reversed(executed_steps):
                try:
                    self.compensations[step_index]()
                except Exception as comp_e:
                    print(f"Compensation failed: {comp_e}")
            
            raise e

# 使用示例：订单处理Saga
def create_order():
    print("创建订单")
    # 实际业务逻辑
    return {"order_id": 123}

def reserve_inventory():
    print("预留库存")
    # 实际业务逻辑
    return True

def process_payment():
    print("处理支付")
    # 实际业务逻辑
    return True

# 补偿操作
def cancel_order():
    print("取消订单")
    # 实际业务逻辑

def release_inventory():
    print("释放库存")
    # 实际业务逻辑

def refund_payment():
    print("退款")
    # 实际业务逻辑

# 创建Saga
saga = SagaManager()
saga.add_step(create_order, cancel_order)
saga.add_step(reserve_inventory, release_inventory)
saga.add_step(process_payment, refund_payment)

# 执行Saga
try:
    saga.execute()
    print("订单处理成功")
except Exception as e:
    print(f"订单处理失败: {e}")
```

#### 5.2.2 幂等性设计
**原则**：确保同一操作多次执行结果相同
**实现方式**：唯一ID、版本号、状态检查

```python
# Python示例：幂等性设计
import uuid

class IdempotentService:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def process_with_idempotency(self, operation_id, operation_func, ttl=3600):
        """幂等操作执行"""
        # 检查操作是否已执行
        result_key = f"op_result:{operation_id}"
        existing_result = self.redis.get(result_key)
        
        if existing_result:
            # 操作已执行，返回原结果
            return json.loads(existing_result)
        
        # 检查是否正在执行
        processing_key = f"op_processing:{operation_id}"
        is_processing = self.redis.exists(processing_key)
        
        if is_processing:
            # 等待处理完成
            while self.redis.exists(processing_key):
                time.sleep(0.1)
            
            # 再次检查结果
            existing_result = self.redis.get(result_key)
            if existing_result:
                return json.loads(existing_result)
            
            # 如果没有结果，说明处理失败
            raise Exception("Operation failed previously")
        
        # 标记开始处理
        self.redis.setex(processing_key, ttl, "processing")
        
        try:
            # 执行操作
            result = operation_func()
            
            # 存储结果
            self.redis.setex(result_key, ttl, json.dumps(result, default=str))
            
            # 清除处理标记
            self.redis.delete(processing_key)
            
            return result
            
        except Exception as e:
            # 清除处理标记，允许重试
            self.redis.delete(processing_key)
            raise e

# 使用示例
def place_order(order_data):
    """下订单操作（幂等）"""
    # 生成操作ID
    operation_id = order_data.get('operation_id', str(uuid.uuid4()))
    
    # 幂等处理
    idempotent_service = IdempotentService(redis_client)
    
    def _place_order():
        # 实际下订单逻辑
        print(f"Creating order for user {order_data['user_id']}")
        
        with mysql_conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO orders (user_id, total_amount) VALUES (%s, %s)",
                (order_data['user_id'], order_data['total_amount'])
            )
            order_id = cursor.lastrowid
            mysql_conn.commit()
        
        return {"order_id": order_id, "status": "created"}
    
    return idempotent_service.process_with_idempotency(operation_id, _place_order)
```

### 5.3 监控与运维

#### 5.3.1 数据一致性检查
**目标**：定期验证不同系统间的数据一致性
**实现方式**：定时任务、校验算法、修复机制

```python
# Python示例：数据一致性检查
import pymysql
from pymongo import MongoClient
from datetime import datetime, timedelta

class ConsistencyChecker:
    def __init__(self, mysql_config, mongodb_config):
        self.mysql_conn = pymysql.Connect(**mysql_config)
        self.mongo_client = MongoClient(mongodb_config['uri'])
        self.mongo_db = self.mongo_client[mongodb_config['database']]
        
        # 记录不一致情况
        self.inconsistencies = []
    
    def check_user_data_consistency(self, limit=100):
        """检查用户数据一致性"""
        # 获取MySQL中的用户
        with self.mysql_conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(f"SELECT * FROM users LIMIT {limit}")
            mysql_users = cursor.fetchall()
        
        # 获取MongoDB中的用户
        mongo_users = list(self.mongo_db.user_profiles.find())
        
        # 转换为字典以便比较
        mongo_user_map = {u['user_id']: u for u in mongo_users}
        
        # 检查一致性
        for mysql_user in mysql_users:
            user_id = mysql_user['id']
            mongo_user = mongo_user_map.get(user_id)
            
            if not mongo_user:
                self.inconsistencies.append({
                    'type': 'missing_in_mongo',
                    'user_id': user_id,
                    'timestamp': datetime.now()
                })
                continue
            
            # 检查字段一致性
            if mysql_user['username'] != mongo_user.get('username'):
                self.inconsistencies.append({
                    'type': 'username_mismatch',
                    'user_id': user_id,
                    'mysql_value': mysql_user['username'],
                    'mongo_value': mongo_user.get('username'),
                    'timestamp': datetime.now()
                })
            
            if mysql_user['email'] != mongo_user.get('email'):
                self.inconsistencies.append({
                    'type': 'email_mismatch',
                    'user_id': user_id,
                    'mysql_value': mysql_user['email'],
                    'mongo_value': mongo_user.get('email'),
                    'timestamp': datetime.now()
                })
        
        # 检查MongoDB中多余的数据
        mysql_user_ids = {u['id'] for u in mysql_users}
        for mongo_user in mongo_users:
            if mongo_user['user_id'] not in mysql_user_ids:
                self.inconsistencies.append({
                    'type': 'missing_in_mysql',
                    'user_id': mongo_user['user_id'],
                    'timestamp': datetime.now()
                })
        
        return self.inconsistencies
    
    def fix_inconsistencies(self, dry_run=True):
        """修复不一致数据"""
        fixed_count = 0
        
        for inconsistency in self.inconsistencies:
            if inconsistency['type'] == 'missing_in_mongo':
                # MongoDB中缺失，从MySQL同步
                user_id = inconsistency['user_id']
                
                if not dry_run:
                    # 从MySQL获取用户数据
                    with self.mysql_conn.cursor(pymysql.cursors.DictCursor) as cursor:
                        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                        mysql_user = cursor.fetchone()
                    
                    if mysql_user:
                        # 插入到MongoDB
                        mongo_doc = {
                            'user_id': user_id,
                            'username': mysql_user['username'],
                            'email': mysql_user['email'],
                            'created_at': mysql_user['created_at'],
                            'updated_at': mysql_user.get('updated_at')
                        }
                        self.mongo_db.user_profiles.insert_one(mongo_doc)
                
                fixed_count += 1
                
            elif inconsistency['type'] == 'username_mismatch':
                # 用户名不一致，以MySQL为准
                user_id = inconsistency['user_id']
                correct_username = inconsistency['mysql_value']
                
                if not dry_run:
                    self.mongo_db.user_profiles.update_one(
                        {'user_id': user_id},
                        {'$set': {'username': correct_username}}
                    )
                
                fixed_count += 1
                
            elif inconsistency['type'] == 'email_mismatch':
                # 邮箱不一致，以MySQL为准
                user_id = inconsistency['user_id']
                correct_email = inconsistency['mysql_value']
                
                if not dry_run:
                    self.mongo_db.user_profiles.update_one(
                        {'user_id': user_id},
                        {'$set': {'email': correct_email}}
                    )
                
                fixed_count += 1
                
            elif inconsistency['type'] == 'missing_in_mysql':
                # MySQL中缺失，从MongoDB同步（或删除MongoDB中的数据）
                # 这里选择删除MongoDB中的多余数据
                user_id = inconsistency['user_id']
                
                if not dry_run:
                    self.mongo_db.user_profiles.delete_one({'user_id': user_id})
                
                fixed_count += 1
        
        return fixed_count
    
    def generate_report(self):
        """生成一致性报告"""
        if not self.inconsistencies:
            return "数据一致性检查通过，未发现不一致。"
        
        # 按类型统计
        type_counts = {}
        for inconsistency in self.inconsistencies:
            inc_type = inconsistency['type']
            type_counts[inc_type] = type_counts.get(inc_type, 0) + 1
        
        report = f"数据一致性检查发现 {len(self.inconsistencies)} 处不一致：\n"
        for inc_type, count in type_counts.items():
            report += f"- {inc_type}: {count} 处\n"
        
        return report

# 使用示例
checker = ConsistencyChecker(mysql_config, mongodb_config)

# 执行一致性检查
inconsistencies = checker.check_user_data_consistency()

# 生成报告
report = checker.generate_report()
print(report)

# 修复不一致（先试运行）
fixed_count = checker.fix_inconsistencies(dry_run=True)
print(f"试运行将修复 {fixed_count} 处不一致")

# 实际修复
# fixed_count = checker.fix_inconsistencies(dry_run=False)
# print(f"已修复 {fixed_count} 处不一致")
```

#### 5.3.2 性能监控
**目标**：监控各系统性能，发现瓶颈和问题
**指标**：延迟、吞吐量、错误率、资源使用率

```python
# Python示例：混合架构性能监控
import time
import threading
import psutil
from collections import defaultdict
import json

class HybridArchitectureMonitor:
    def __init__(self, mysql_conn, redis_client, mongo_client, es_client):
        self.mysql_conn = mysql_conn
        self.redis_client = redis_client
        self.mongo_client = mongo_client
        self.es_client = es_client
        
        # 性能数据
        self.metrics = defaultdict(list)
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def _monitor_loop(self):
        """监控循环"""
        while True:
            try:
                # 收集各项指标
                self._collect_mysql_metrics()
                self._collect_redis_metrics()
                self._collect_mongodb_metrics()
                self._collect_elasticsearch_metrics()
                self._collect_system_metrics()
                
                # 等待下次收集
                time.sleep(60)  # 每分钟收集一次
                
            except Exception as e:
                print(f"Monitor error: {e}")
    
    def _collect_mysql_metrics(self):
        """收集MySQL指标"""
        start_time = time.time()
        
        try:
            with self.mysql_conn.cursor() as cursor:
                # 获取连接数
                cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
                result = cursor.fetchone()
                connections = result[1] if result else 0
                
                # 获取查询数
                cursor.execute("SHOW STATUS LIKE 'Queries'")
                result = cursor.fetchone()
                queries = result[1] if result else 0
                
                # 获取慢查询数
                cursor.execute("SHOW STATUS LIKE 'Slow_queries'")
                result = cursor.fetchone()
                slow_queries = result[1] if result else 0
            
            # 测试查询延迟
            query_start = time.time()
            cursor.execute("SELECT 1")
            query_latency = time.time() - query_start
            
            # 存储指标
            self.metrics['mysql_connections'].append({
                'value': int(connections),
                'timestamp': time.time()
            })
            
            self.metrics['mysql_queries'].append({
                'value': int(queries),
                'timestamp': time.time()
            })
            
            self.metrics['mysql_slow_queries'].append({
                'value': int(slow_queries),
                'timestamp': time.time()
            })
            
            self.metrics['mysql_query_latency'].append({
                'value': query_latency * 1000,  # 毫秒
                'timestamp': time.time()
            })
            
        except Exception as e:
            print(f"Error collecting MySQL metrics: {e}")
            self.metrics['mysql_error'].append({
                'value': 1,
                'timestamp': time.time()
            })
    
    def _collect_redis_metrics(self):
        """收集Redis指标"""
        try:
            # 测试Redis延迟
            start_time = time.time()
            self.redis_client.ping()
            latency = time.time() - start_time
            
            # 获取Redis信息
            info = self.redis_client.info()
            
            self.metrics['redis_latency'].append({
                'value': latency * 1000,  # 毫秒
                'timestamp': time.time()
            })
            
            self.metrics['redis_memory'].append({
                'value': info.get('used_memory', 0),
                'timestamp': time.time()
            })
            
            self.metrics['redis_clients'].append({
                'value': info.get('connected_clients', 0),
                'timestamp': time.time()
            })
            
            self.metrics['redis_hits'].append({
                'value': info.get('keyspace_hits', 0),
                'timestamp': time.time()
            })
            
            self.metrics['redis_misses'].append({
                'value': info.get('keyspace_misses', 0),
                'timestamp': time.time()
            })
            
        except Exception as e:
            print(f"Error collecting Redis metrics: {e}")
            self.metrics['redis_error'].append({
                'value': 1,
                'timestamp': time.time()
            })
    
    def _collect_mongodb_metrics(self):
        """收集MongoDB指标"""
        try:
            # 获取服务器状态
            admin_db = self.mongo_client.admin
            server_status = admin_db.command("serverStatus")
            
            # 测试查询延迟
            start_time = time.time()
            self.mongo_client.list_database_names()
            latency = time.time() - start_time
            
            self.metrics['mongodb_latency'].append({
                'value': latency * 1000,  # 毫秒
                'timestamp': time.time()
            })
            
            self.metrics['mongodb_connections'].append({
                'value': server_status.get('connections', {}).get('current', 0),
                'timestamp': time.time()
            })
            
            self.metrics['mongodb_operations'].append({
                'value': server_status.get('opcounters', {}).get('query', 0),
                'timestamp': time.time()
            })
            
            self.metrics['mongodb_memory'].append({
                'value': server_status.get('mem', {}).get('resident', 0),
                'timestamp': time.time()
            })
            
        except Exception as e:
            print(f"Error collecting MongoDB metrics: {e}")
            self.metrics['mongodb_error'].append({
                'value': 1,
                'timestamp': time.time()
            })
    
    def _collect_elasticsearch_metrics(self):
        """收集Elasticsearch指标"""
        try:
            # 测试查询延迟
            start_time = time.time()
            self.es_client.cluster.health()
            latency = time.time() - start_time
            
            # 获取集群统计
            stats = self.es_client.cluster.stats()
            
            self.metrics['elasticsearch_latency'].append({
                'value': latency * 1000,  # 毫秒
                'timestamp': time.time()
            })
            
            self.metrics['elasticsearch_nodes'].append({
                'value': stats.get('nodes', {}).get('count', {}).get('total', 0),
                'timestamp': time.time()
            })
            
            self.metrics['elasticsearch_docs'].append({
                'value': stats.get('indices', {}).get('docs', {}).get('count', 0),
                'timestamp': time.time()
            })
            
            self.metrics['elasticsearch_store_size'].append({
                'value': stats.get('indices', {}).get('store', {}).get('size_in_bytes', 0),
                'timestamp': time.time()
            })
            
        except Exception as e:
            print(f"Error collecting Elasticsearch metrics: {e}")
            self.metrics['elasticsearch_error'].append({
                'value': 1,
                'timestamp': time.time()
            })
    
    def _collect_system_metrics(self):
        """收集系统指标"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            self.metrics['system_cpu'].append({
                'value': cpu_percent,
                'timestamp': time.time()
            })
            
            self.metrics['system_memory'].append({
                'value': memory.percent,
                'timestamp': time.time()
            })
            
            self.metrics['system_disk'].append({
                'value': disk.percent,
                'timestamp': time.time()
            })
            
        except Exception as e:
            print(f"Error collecting system metrics: {e}")
    
    def get_latest_metrics(self, metric_name, count=10):
        """获取最新的指标数据"""
        if metric_name not in self.metrics:
            return []
        
        return self.metrics[metric_name][-count:]
    
    def get_dashboard_data(self):
        """获取仪表板数据"""
        dashboard = {}
        
        # 计算平均值
        for metric_name, values in self.metrics.items():
            if not values:
                dashboard[metric_name] = {'avg': 0, 'current': 0, 'count': 0}
                continue
            
            # 最新值
            current = values[-1]['value']
            
            # 平均值（取最近10个）
            recent_values = values[-10:]
            avg = sum(v['value'] for v in recent_values) / len(recent_values)
            
            dashboard[metric_name] = {
                'avg': avg,
                'current': current,
                'count': len(values)
            }
        
        return dashboard
    
    def generate_alerts(self):
        """生成告警"""
        alerts = []
        
        # 检查延迟告警
        mysql_latency = self.get_latest_metrics('mysql_query_latency', 1)
        if mysql_latency and mysql_latency[0]['value'] > 100:  # 100ms
            alerts.append({
                'level': 'warning',
                'component': 'MySQL',
                'metric': 'query_latency',
                'value': mysql_latency[0]['value'],
                'threshold': 100,
                'message': f"MySQL查询延迟过高: {mysql_latency[0]['value']:.2f}ms"
            })
        
        redis_latency = self.get_latest_metrics('redis_latency', 1)
        if redis_latency and redis_latency[0]['value'] > 10:  # 10ms
            alerts.append({
                'level': 'warning',
                'component': 'Redis',
                'metric': 'latency',
                'value': redis_latency[0]['value'],
                'threshold': 10,
                'message': f"Redis延迟过高: {redis_latency[0]['value']:.2f}ms"
            })
        
        # 检查资源使用告警
        system_memory = self.get_latest_metrics('system_memory', 1)
        if system_memory and system_memory[0]['value'] > 90:  # 90%
            alerts.append({
                'level': 'critical',
                'component': 'System',
                'metric': 'memory_usage',
                'value': system_memory[0]['value'],
                'threshold': 90,
                'message': f"系统内存使用率过高: {system_memory[0]['value']:.2f}%"
            })
        
        return alerts

# 使用示例
monitor = HybridArchitectureMonitor(
    mysql_conn=mysql_conn,
    redis_client=redis_client,
    mongo_client=mongo_client,
    es_client=es_client
)

# 等待收集一些数据
time.sleep(120)

# 获取仪表板数据
dashboard = monitor.get_dashboard_data()

# 生成告警
alerts = monitor.generate_alerts()
for alert in alerts:
    print(f"[{alert['level'].upper()}] {alert['message']}")
```

## 总结

混合数据架构是现代复杂应用系统的必然选择，它允许我们根据不同的业务需求选择最合适的数据存储解决方案。本章详细介绍了MySQL与各种NoSQL数据库的混合架构模式，包括：

1. **MySQL + MongoDB**：适合需要灵活schema和文档存储的场景
2. **MySQL + Redis**：适合需要高性能缓存和实时处理的场景
3. **MySQL + Elasticsearch**：适合需要全文搜索和复杂分析的场景
4. **MySQL + Cassandra**：适合需要处理大规模时间序列数据的场景

我们还探讨了数据一致性的不同级别和实现策略，以及如何通过事件驱动、CDC等模式实现可靠的数据同步。最后，我们介绍了架构设计的最佳实践和运维监控方法。

混合架构虽然带来了更高的复杂性，但也提供了更强大的能力和更好的性能。通过合理的设计和实施，混合架构可以充分发挥各种数据库的优势，为应用系统提供最优的解决方案。

在实际应用中，选择合适的混合架构模式需要综合考虑业务需求、数据特性、访问模式、团队技能和运维能力等多个因素。随着技术的发展，混合架构模式也在不断演进，我们需要持续关注新技术和新模式，不断优化我们的架构设计。