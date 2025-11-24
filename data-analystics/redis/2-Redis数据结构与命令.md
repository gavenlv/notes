# 第2章：Redis数据结构与命令

## 2.1 Redis数据模型概述

### 2.1.1 键值对基础

Redis是一个键值存储系统，每个键都与一个特定的值相关联。键是二进制安全的字符串，最大长度为512MB。值可以是以下5种基本数据结构之一：

- **String（字符串）**：最基本的数据类型
- **Hash（哈希）**：字段-值对的集合
- **List（列表）**：字符串列表，按插入顺序排序
- **Set（集合）**：无序的字符串集合
- **Sorted Set（有序集合）**：带分数的字符串集合

### 2.1.2 键的命名规范

良好的键命名规范对于维护和性能至关重要：

```python
# 良好的键命名示例
"user:123:profile"          # 用户123的个人资料
"session:abc123:data"        # 会话数据
"product:electronics:list"   # 电子产品列表
"cache:api:v1:users"        # API缓存

# 避免的键命名
"user123profile"             # 难以解析
"data"                       # 过于通用
"temp123"                    # 含义不明确
```

## 2.2 字符串（String）

### 2.2.1 字符串基础操作

字符串是Redis最基本的数据类型，可以存储文本、数字或二进制数据。

```python
import redis

r = redis.Redis(decode_responses=True)

# 基本设置和获取
r.set('username', 'alice')
username = r.get('username')
print(f"用户名: {username}")

# 设置带过期时间的键
r.setex('temp_token', 300, 'abc123')  # 5分钟后过期

# 只有当键不存在时才设置
r.setnx('counter', 0)  # 仅当counter不存在时设置为0

# 批量操作
r.mset({'name': 'Bob', 'age': '30', 'city': 'Beijing'})
values = r.mget(['name', 'age', 'city'])
print(f"批量获取: {values}")
```

### 2.2.2 数字操作

Redis可以将字符串作为数字进行处理，支持原子操作：

```python
# 数字递增递减
r.set('page_views', 0)
r.incr('page_views')        # 增加到1
r.incrby('page_views', 5)  # 增加到6
r.decr('page_views')       # 减少到5
r.decrby('page_views', 3)  # 减少到2

# 浮点数操作
r.set('temperature', 25.5)
r.incrbyfloat('temperature', 1.5)  # 增加到27.0

# 获取并设置（原子操作）
current = r.getset('counter', 100)  # 获取旧值并设置新值
print(f"原值: {current}, 新值: {r.get('counter')}")
```

### 2.2.3 位操作

Redis支持对字符串的位级别操作：

```python
# 设置位图
r.setbit('user_online', 1001, 1)  # 用户1001在线
r.setbit('user_online', 1002, 1)  # 用户1002在线
r.setbit('user_online', 1003, 0)  # 用户1003离线

# 检查位
is_online = r.getbit('user_online', 1001)
print(f"用户1001是否在线: {is_online}")

# 统计设置位的数量
online_count = r.bitcount('user_online')
print(f"在线用户数: {online_count}")

# 位操作示例：用户签到系统
import datetime

def user_sign_in(user_id):
    """用户签到"""
    today = datetime.date.today()
    key = f"sign_in:{user_id}:{today.year}"
    offset = today.timetuple().tm_yday - 1  # 一年中的第几天
    
    r.setbit(key, offset, 1)
    return True

def get_sign_in_stats(user_id, year):
    """获取签到统计"""
    key = f"sign_in:{user_id}:{year}"
    return r.bitcount(key)
```

## 2.3 哈希（Hash）

### 2.3.1 哈希基础操作

哈希适合存储对象，可以高效地操作单个字段：

```python
# 存储用户信息
user_data = {
    'name': '张三',
    'age': '28',
    'email': 'zhangsan@example.com',
    'city': '上海'
}

r.hset('user:1001', mapping=user_data)

# 获取单个字段
name = r.hget('user:1001', 'name')
print(f"用户名: {name}")

# 获取所有字段
user_info = r.hgetall('user:1001')
print(f"用户信息: {user_info}")

# 检查字段是否存在
if r.hexists('user:1001', 'email'):
    print("邮箱字段存在")

# 删除字段
r.hdel('user:1001', 'city')
```

### 2.3.2 哈希数字操作

哈希也支持数字字段的原子操作：

```python
# 存储商品库存
r.hset('product:2001', 'stock', 50)
r.hset('product:2001', 'price', 299.99)

# 增减库存
r.hincrby('product:2001', 'stock', -5)  # 减少5个库存
r.hincrbyfloat('product:2001', 'price', 10.50)  # 涨价10.5

# 获取多个字段
fields = r.hmget('product:2001', ['stock', 'price'])
print(f"库存: {fields[0]}, 价格: {fields[1]}")

# 获取所有字段名
field_names = r.hkeys('user:1001')
print(f"字段名: {field_names}")

# 获取所有字段值
field_values = r.hvals('user:1001')
print(f"字段值: {field_values}")
```

### 2.3.3 哈希应用场景

**购物车实现**：

```python
class ShoppingCart:
    def __init__(self, user_id):
        self.user_id = user_id
        self.cart_key = f"cart:{user_id}"
    
    def add_item(self, product_id, quantity=1):
        """添加商品到购物车"""
        r.hincrby(self.cart_key, product_id, quantity)
    
    def remove_item(self, product_id):
        """从购物车移除商品"""
        r.hdel(self.cart_key, product_id)
    
    def get_cart(self):
        """获取购物车内容"""
        return r.hgetall(self.cart_key)
    
    def update_quantity(self, product_id, quantity):
        """更新商品数量"""
        if quantity <= 0:
            self.remove_item(product_id)
        else:
            r.hset(self.cart_key, product_id, quantity)
    
    def clear_cart(self):
        """清空购物车"""
        r.delete(self.cart_key)

# 使用示例
cart = ShoppingCart('user123')
cart.add_item('product001', 2)
cart.add_item('product002', 1)
print(f"购物车内容: {cart.get_cart()}")
```

## 2.4 列表（List）

### 2.4.1 列表基础操作

列表按插入顺序存储字符串，支持从两端操作：

```python
# 从左侧添加元素
r.lpush('tasks', 'task1', 'task2', 'task3')

# 从右侧添加元素
r.rpush('tasks', 'task4', 'task5')

# 获取列表长度
length = r.llen('tasks')
print(f"任务数量: {length}")

# 获取范围元素
tasks = r.lrange('tasks', 0, -1)  # 获取所有元素
print(f"所有任务: {tasks}")

# 从左侧弹出元素
first_task = r.lpop('tasks')
print(f"第一个任务: {first_task}")

# 从右侧弹出元素
last_task = r.rpop('tasks')
print(f"最后一个任务: {last_task}")
```

### 2.4.2 列表高级操作

```python
# 按索引获取和设置元素
second_task = r.lindex('tasks', 1)  # 获取索引1的元素
r.lset('tasks', 0, 'urgent_task')  # 设置索引0的元素

# 修剪列表，只保留指定范围
r.ltrim('tasks', 0, 9)  # 只保留前10个元素

# 阻塞操作（消息队列场景）
# 从列表左侧阻塞弹出，超时时间5秒
task = r.blpop('task_queue', timeout=5)
if task:
    print(f"收到任务: {task[1]}")

# 在指定元素前后插入
r.linsert('tasks', 'BEFORE', 'task2', 'new_task')  # 在task2前插入
r.linsert('tasks', 'AFTER', 'task2', 'another_task')  # 在task2后插入

# 移除指定数量的元素
r.lrem('tasks', 2, 'task1')  # 从左侧开始移除2个'task1'
```

### 2.4.3 列表应用场景

**消息队列实现**：

```python
class MessageQueue:
    def __init__(self, queue_name):
        self.queue_name = queue_name
    
    def send_message(self, message):
        """发送消息"""
        r.lpush(self.queue_name, message)
    
    def receive_message(self, timeout=0):
        """接收消息（阻塞）"""
        if timeout > 0:
            result = r.brpop(self.queue_name, timeout=timeout)
            return result[1] if result else None
        else:
            return r.rpop(self.queue_name)
    
    def get_queue_length(self):
        """获取队列长度"""
        return r.llen(self.queue_name)
    
    def peek_messages(self, count=10):
        """查看消息（不移除）"""
        return r.lrange(self.queue_name, 0, count-1)

# 使用示例
mq = MessageQueue('email_queue')
mq.send_message('欢迎邮件')
mq.send_message('订单确认')
print(f"队列长度: {mq.get_queue_length()}")
message = mq.receive_message(timeout=5)
print(f"收到消息: {message}")
```

**最新消息列表**：

```python
def add_latest_news(news_id, content, max_items=100):
    """添加最新新闻"""
    news_key = 'latest_news'
    
    # 使用管道保证原子性
    pipe = r.pipeline()
    pipe.lpush(news_key, f"{news_id}:{content}")
    pipe.ltrim(news_key, 0, max_items-1)  # 保持最多100条
    pipe.execute()

def get_latest_news(count=10):
    """获取最新新闻"""
    return r.lrange('latest_news', 0, count-1)
```

## 2.5 集合（Set）

### 2.5.1 集合基础操作

集合存储无序的唯一字符串：

```python
# 添加元素
r.sadd('tags', 'python', 'redis', 'database', 'cache')

# 获取所有元素
all_tags = r.smembers('tags')
print(f"所有标签: {all_tags}")

# 检查元素是否存在
if r.sismember('tags', 'python'):
    print("python标签存在")

# 移除元素
r.srem('tags', 'cache')

# 随机获取元素
random_tag = r.srandmember('tags')
print(f"随机标签: {random_tag}")

# 弹出随机元素
popped_tag = r.spop('tags')
print(f"弹出的标签: {popped_tag}")

# 获取集合大小
size = r.scard('tags')
print(f"标签数量: {size}")
```

### 2.5.2 集合运算

集合支持丰富的数学运算：

```python
# 创建多个集合
r.sadd('group1', 'user1', 'user2', 'user3', 'user4')
r.sadd('group2', 'user3', 'user4', 'user5', 'user6')

# 并集
union = r.sunion('group1', 'group2')
print(f"并集: {union}")

# 交集
intersection = r.sinter('group1', 'group2')
print(f"交集: {intersection}")

# 差集（在group1中但不在group2中）
difference = r.sdiff('group1', 'group2')
print(f"差集: {difference}")

# 将结果存储到新集合
r.sunionstore('all_users', 'group1', 'group2')
r.sinterstore('common_users', 'group1', 'group2')

# 判断集合关系
if r.sismember('group1', 'user1'):
    print("user1在group1中")
```

### 2.5.3 集合应用场景

**标签系统**：

```python
class TagSystem:
    def add_tags_to_item(self, item_id, *tags):
        """为物品添加标签"""
        item_key = f"item:{item_id}:tags"
        r.sadd(item_key, *tags)
        
        # 同时维护标签到物品的映射
        for tag in tags:
            r.sadd(f"tag:{tag}:items", item_id)
    
    def get_item_tags(self, item_id):
        """获取物品的标签"""
        return r.smembers(f"item:{item_id}:tags")
    
    def get_items_by_tag(self, tag):
        """通过标签获取物品"""
        return r.smembers(f"tag:{tag}:items")
    
    def get_common_tags(self, item1_id, item2_id):
        """获取两个物品的共同标签"""
        return r.sinter(
            f"item:{item1_id}:tags",
            f"item:{item2_id}:tags"
        )
    
    def remove_tag_from_item(self, item_id, tag):
        """从物品移除标签"""
        r.srem(f"item:{item_id}:tags", tag)
        r.srem(f"tag:{tag}:items", item_id)

# 使用示例
tag_system = TagSystem()
tag_system.add_tags_to_item('book001', 'python', 'programming', 'database')
tag_system.add_tags_to_item('book002', 'python', 'web', 'framework')

common_tags = tag_system.get_common_tags('book001', 'book002')
print(f"共同标签: {common_tags}")
```

**唯一值统计**：

```python
def track_unique_visitors(page_id, visitor_id):
    """跟踪唯一访客"""
    key = f"page:{page_id}:unique_visitors"
    return r.sadd(key, visitor_id)  # 返回1表示新访客，0表示重复

def get_unique_visitor_count(page_id):
    """获取唯一访客数量"""
    return r.scard(f"page:{page_id}:unique_visitors")

def get_common_visitors(page1_id, page2_id):
    """获取两个页面的共同访客"""
    return r.sinter(
        f"page:{page1_id}:unique_visitors",
        f"page:{page2_id}:unique_visitors"
    )
```

## 2.6 有序集合（Sorted Set）

### 2.6.1 有序集合基础操作

有序集合为每个元素关联一个分数，用于排序：

```python
# 添加元素（带分数）
r.zadd('leaderboard', {'alice': 1000, 'bob': 800, 'charlie': 1200})

# 获取元素分数
score = r.zscore('leaderboard', 'alice')
print(f"Alice的分数: {score}")

# 按分数范围获取元素（升序）
players = r.zrange('leaderboard', 0, -1, withscores=True)
print(f"所有玩家（升序）: {players}")

# 按分数范围获取元素（降序）
players_desc = r.zrevrange('leaderboard', 0, -1, withscores=True)
print(f"所有玩家（降序）: {players_desc}")

# 获取排名
rank = r.zrank('leaderboard', 'bob')  # 升序排名（从0开始）
rev_rank = r.zrevrank('leaderboard', 'bob')  # 降序排名
print(f"Bob的排名: 升序{rank}, 降序{rev_rank}")

# 按分数范围计数
count = r.zcount('leaderboard', 800, 1100)
print(f"分数在800-1100之间的玩家数: {count}")
```

### 2.6.2 有序集合高级操作

```python
# 增减分数
r.zincrby('leaderboard', 50, 'alice')  # Alice分数增加50

# 按字典序范围获取
r.zadd('autocomplete', {
    'apple': 0, 'application': 0, 'app': 0,
    'banana': 0, 'band': 0, 'bank': 0
})

# 获取以'app'开头的元素
words = r.zrangebylex('autocomplete', '[app', '[app\xff')
print(f"以'app'开头的单词: {words}")

# 移除元素
r.zrem('leaderboard', 'charlie')

# 按排名范围移除
r.zremrangebyrank('leaderboard', 0, 2)  # 移除前3名

# 按分数范围移除
r.zremrangebyscore('leaderboard', 0, 500)  # 移除分数0-500的元素

# 获取集合大小
size = r.zcard('leaderboard')
print(f"排行榜大小: {size}")
```

### 2.6.3 有序集合应用场景

**排行榜系统**：

```python
class Leaderboard:
    def __init__(self, name):
        self.name = name
    
    def add_player(self, player_id, score):
        """添加玩家分数"""
        r.zadd(self.name, {player_id: score})
    
    def increment_score(self, player_id, increment):
        """增加玩家分数"""
        r.zincrby(self.name, increment, player_id)
    
    def get_player_rank(self, player_id):
        """获取玩家排名（从1开始）"""
        rank = r.zrevrank(self.name, player_id)
        return rank + 1 if rank is not None else None
    
    def get_top_players(self, limit=10):
        """获取前N名玩家"""
        return r.zrevrange(self.name, 0, limit-1, withscores=True)
    
    def get_players_in_range(self, start_rank, end_rank):
        """获取排名范围内的玩家"""
        return r.zrevrange(self.name, start_rank-1, end_rank-1, withscores=True)
    
    def get_player_score(self, player_id):
        """获取玩家分数"""
        return r.zscore(self.name, player_id)
    
    def remove_player(self, player_id):
        """移除玩家"""
        r.zrem(self.name, player_id)

# 使用示例
lb = Leaderboard('game_leaderboard')
lb.add_player('player1', 1500)
lb.add_player('player2', 2000)
lb.add_player('player3', 1800)

lb.increment_score('player1', 100)
print(f"玩家1的排名: {lb.get_player_rank('player1')}")
print(f"前三名: {lb.get_top_players(3)}")
```

**延迟队列**：

```python
import time

class DelayedQueue:
    def __init__(self, name):
        self.name = name
    
    def add_task(self, task_id, delay_seconds):
        """添加延迟任务"""
        execute_time = time.time() + delay_seconds
        r.zadd(self.name, {task_id: execute_time})
    
    def get_ready_tasks(self):
        """获取已到期的任务"""
        current_time = time.time()
        
        # 获取所有已到期的任务
        tasks = r.zrangebyscore(self.name, 0, current_time)
        
        if tasks:
            # 原子性地移除已获取的任务
            pipe = r.pipeline()
            pipe.zremrangebyscore(self.name, 0, current_time)
            pipe.execute()
        
        return tasks
    
    def peek_next_task_time(self):
        """查看下一个任务的执行时间"""
        next_task = r.zrange(self.name, 0, 0, withscores=True)
        return next_task[0][1] if next_task else None

# 使用示例
dq = DelayedQueue('email_delivery_queue')
dq.add_task('welcome_email_123', 300)  # 5分钟后发送

time.sleep(1)
ready_tasks = dq.get_ready_tasks()
print(f"待处理任务: {ready_tasks}")
```

## 2.7 高级数据操作技巧

### 2.7.1 管道（Pipeline）操作

管道可以批量执行命令，减少网络往返：

```python
# 不使用管道（效率低）
for i in range(100):
    r.set(f'key{i}', f'value{i}')

# 使用管道（高效）
pipe = r.pipeline()
for i in range(100):
    pipe.set(f'key{i}', f'value{i}')
pipe.execute()  # 一次性发送所有命令

# 管道事务
pipe = r.pipeline(transaction=True)
pipe.multi()
pipe.set('counter', 0)
pipe.incr('counter')
pipe.incr('counter')
result = pipe.execute()
print(f"管道执行结果: {result}")
```

### 2.7.2 Lua脚本

Redis支持执行Lua脚本，保证原子性：

```python
# 简单的Lua脚本示例
script = """
local current = redis.call('GET', KEYS[1])
if current then
    redis.call('SET', KEYS[1], current + ARGV[1])
else
    redis.call('SET', KEYS[1], ARGV[1])
end
return redis.call('GET', KEYS[1])
"""

# 执行Lua脚本
increment_script = r.register_script(script)
result = increment_script(keys=['my_counter'], args=[5])
print(f"Lua脚本执行结果: {result}")

# 复杂的Lua脚本：限流器
rate_limit_script = """
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local current = redis.call('GET', key)

if current and tonumber(current) >= limit then
    return 0
else
    redis.call('INCR', key)
    redis.call('EXPIRE', key, window)
    return 1
end
"""

rate_limiter = r.register_script(rate_limit_script)
allowed = rate_limiter(keys=['api:user123'], args=[10, 60])  # 每分钟最多10次
print(f"是否允许访问: {allowed}")
```

### 2.7.3 键空间通知

监听键的变化事件：

```python
# 配置Redis启用键空间通知
# 在redis.conf中添加: notify-keyspace-events "Kgx"

import redis
from redis import Redis

class KeySpaceMonitor:
    def __init__(self):
        self.pubsub = r.pubsub()
    
    def monitor_expired_keys(self):
        """监控键过期事件"""
        self.pubsub.psubscribe('__keyevent@0__:expired')
        
        for message in self.pubsub.listen():
            if message['type'] == 'pmessage':
                expired_key = message['data']
                print(f"键过期: {expired_key}")
                # 处理过期逻辑
    
    def monitor_set_operations(self):
        """监控set操作"""
        self.pubsub.psubscribe('__keyevent@0__:set')
        
        for message in self.pubsub.listen():
            if message['type'] == 'pmessage':
                key = message['data']
                print(f"键被设置: {key}")

# 注意：需要在单独的线程中运行监控
```

## 2.8 性能优化技巧

### 2.8.1 内存优化

```python
# 使用适当的数据结构
# 错误：使用字符串存储对象
r.set('user:1001', '{"name":"Alice","age":25}')

# 正确：使用哈希存储对象
r.hset('user:1001', mapping={'name': 'Alice', 'age': '25'})

# 使用压缩列表优化小哈希和小列表
# 在redis.conf中配置:
# hash-max-ziplist-entries 512
# hash-max-ziplist-value 64
# list-max-ziplist-size -2

# 使用整数编码
r.set('counter', 100)  # Redis会自动使用整数编码
```

### 2.8.2 批量操作优化

```python
# 避免N+1查询问题
# 错误：循环查询
user_ids = ['1001', '1002', '1003']
user_names = []
for user_id in user_ids:
    name = r.get(f'user:{user_id}:name')
    user_names.append(name)

# 正确：批量查询
pipe = r.pipeline()
for user_id in user_ids:
    pipe.get(f'user:{user_id}:name')
user_names = pipe.execute()

# 使用MSET/MGET进行批量操作
r.mset({
    'user:1001:name': 'Alice',
    'user:1002:name': 'Bob',
    'user:1003:name': 'Charlie'
})

names = r.mget(['user:1001:name', 'user:1002:name', 'user:1003:name'])
```

### 2.8.3 连接池优化

```python
import redis
from redis.connection import ConnectionPool

# 创建连接池
pool = ConnectionPool(
    host='localhost',
    port=6379,
    db=0,
    max_connections=20,
    decode_responses=True
)

# 使用连接池
r = redis.Redis(connection_pool=pool)

# 连接池统计
print(f"活跃连接数: {pool._created_connections}")
print(f"空闲连接数: {len(pool._available_connections)}")
```

## 总结

本章深入探讨了Redis的5种核心数据结构及其丰富的命令集。通过学习本章，您应该能够：

1. 理解每种数据结构的特性和适用场景
2. 熟练使用各种数据操作命令
3. 掌握高级特性如管道、Lua脚本和键空间通知
4. 了解性能优化技巧和最佳实践
5. 能够设计和实现基于Redis的复杂应用

在下一章中，我们将学习Redis的持久化机制和复制功能，这是保证数据可靠性和高可用的重要基础。