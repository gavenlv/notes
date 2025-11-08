# 第4章：Redis高级特性与事务

## 4.1 Redis事务机制

### 4.1.1 事务基础概念

Redis事务提供了一种将多个命令打包执行的方式，保证这些命令要么全部执行，要么全部不执行。Redis事务不同于传统数据库事务，它不支持回滚操作。

```python
import redis

r = redis.Redis(decode_responses=True)

# 基本事务操作
pipe = r.pipeline(transaction=True)

# 开始事务（MULTI命令）
pipe.multi()

# 添加命令到事务
pipe.set('user:1001:name', 'Alice')
pipe.set('user:1001:age', '25')
pipe.incr('user:1001:visits')

# 执行事务（EXEC命令）
result = pipe.execute()
print(f"事务执行结果: {result}")
```

### 4.1.2 事务执行流程

Redis事务的执行分为三个阶段：

1. **开始事务**：`MULTI`命令标记事务开始
2. **命令入队**：后续命令被放入队列，不立即执行
3. **执行事务**：`EXEC`命令执行队列中的所有命令

```python
# 事务执行流程示例

def transactional_operation():
    """演示事务执行流程"""
    pipe = r.pipeline(transaction=True)
    
    # 阶段1: 开始事务
    pipe.multi()
    
    # 阶段2: 命令入队
    pipe.set('counter', 0)
    pipe.incr('counter')
    pipe.incr('counter')
    pipe.get('counter')
    
    # 阶段3: 执行事务
    results = pipe.execute()
    
    print(f"事务执行结果: {results}")
    print(f"最终counter值: {results[-1]}")
    
    return results

transactional_operation()
```

### 4.1.3 事务的原子性

Redis事务保证原子性，但在执行期间如果某个命令失败，不会影响其他命令的执行：

```python
# 事务原子性演示

def atomic_transaction():
    """演示事务的原子性"""
    pipe = r.pipeline(transaction=True)
    
    pipe.multi()
    
    # 有效的命令
    pipe.set('key1', 'value1')
    pipe.set('key2', 'value2')
    
    # 语法错误的命令（会在执行时失败）
    # 但不会影响其他命令的执行
    pipe.execute_command('INVALIDCOMMAND')
    
    pipe.set('key3', 'value3')
    
    try:
        results = pipe.execute()
        print(f"事务执行成功: {results}")
    except redis.exceptions.ResponseError as e:
        print(f"事务执行失败: {e}")
        # 注意：即使有命令失败，其他命令仍然会执行

atomic_transaction()
```

## 4.2 事务监控（WATCH）

### 4.2.1 WATCH机制原理

WATCH命令用于监控一个或多个键，如果在事务执行前这些键被其他客户端修改，则事务不会执行：

```python
# WATCH机制示例

def watch_transaction():
    """使用WATCH实现乐观锁"""
    
    # 监控键
    key = 'account:1001:balance'
    
    while True:
        try:
            # 开始监控
            r.watch(key)
            
            # 获取当前值
            current_balance = int(r.get(key) or 0)
            
            # 检查业务条件
            if current_balance < 100:
                r.unwatch()  # 取消监控
                return False, "余额不足"
            
            # 开始事务
            pipe = r.pipeline(transaction=True)
            pipe.multi()
            
            # 业务操作：扣除100
            pipe.set(key, current_balance - 100)
            
            # 执行事务（如果key被修改，会抛出WatchError）
            pipe.execute()
            
            return True, "扣款成功"
            
        except redis.WatchError:
            # 键被修改，重试
            print("数据被修改，重试事务...")
            continue
        except Exception as e:
            r.unwatch()  # 确保取消监控
            return False, f"操作失败: {str(e)}"

# 使用示例
success, message = watch_transaction()
print(f"操作结果: {success}, 消息: {message}")
```

### 4.2.2 多键监控

WATCH可以同时监控多个键：

```python
# 多键监控示例

def multi_key_watch():
    """监控多个键的事务"""
    keys = ['account:1001:balance', 'account:1002:balance']
    
    while True:
        try:
            # 监控多个键
            r.watch(*keys)
            
            # 获取当前值
            balances = r.mget(keys)
            balance1 = int(balances[0] or 0)
            balance2 = int(balances[1] or 0)
            
            # 业务逻辑：转账操作
            if balance1 < 50:
                r.unwatch()
                return False, "账户1余额不足"
            
            pipe = r.pipeline(transaction=True)
            pipe.multi()
            
            # 转账操作
            pipe.set(keys[0], balance1 - 50)  # 账户1扣款
            pipe.set(keys[1], balance2 + 50)  # 账户2收款
            
            pipe.execute()
            return True, "转账成功"
            
        except redis.WatchError:
            print("数据被修改，重试转账...")
            continue
        except Exception as e:
            r.unwatch()
            return False, f"转账失败: {str(e)}"

# 使用示例
success, message = multi_key_watch()
print(f"转账结果: {success}, 消息: {message}")
```

### 4.2.3 UNWATCH命令

UNWATCH用于取消对所有键的监控：

```python
# UNWATCH使用示例

def conditional_watch():
    """条件性监控示例"""
    key = 'resource:lock'
    
    try:
        r.watch(key)
        
        # 检查条件
        if r.get(key) == 'locked':
            print("资源已被锁定，取消监控")
            r.unwatch()  # 取消监控
            return False, "资源不可用"
        
        # 条件满足，继续执行事务
        pipe = r.pipeline(transaction=True)
        pipe.multi()
        pipe.set(key, 'locked')
        pipe.execute()
        
        return True, "资源锁定成功"
        
    except redis.WatchError:
        return False, "资源状态发生变化"
    except Exception as e:
        r.unwatch()
        return False, f"操作失败: {str(e)}"
```

## 4.3 Lua脚本

### 4.3.1 Lua脚本基础

Redis支持执行Lua脚本，保证原子性，适合实现复杂逻辑：

```python
# 基本Lua脚本示例

# 简单的计数器脚本
counter_script = """
local key = KEYS[1]
local increment = tonumber(ARGV[1])

local current = redis.call('GET', key)
if current then
    current = tonumber(current)
else
    current = 0
end

local new_value = current + increment
redis.call('SET', key, new_value)

return new_value
"""

# 注册并执行脚本
counter_script_sha = r.register_script(counter_script)

result = counter_script_sha(keys=['my_counter'], args=[5])
print(f"计数器结果: {result}")

# 直接执行脚本
result = r.eval(counter_script, 1, 'my_counter', 3)
print(f"直接执行结果: {result}")
```

### 4.3.2 复杂业务逻辑

使用Lua脚本实现复杂业务逻辑：

```python
# 库存扣减Lua脚本
inventory_script = """
local product_key = KEYS[1]
local quantity = tonumber(ARGV[1])

-- 获取当前库存
local current_stock = redis.call('GET', product_key)
if not current_stock then
    return {err = '商品不存在'}
end

current_stock = tonumber(current_stock)

-- 检查库存是否充足
if current_stock < quantity then
    return {err = '库存不足', current = current_stock, required = quantity}
end

-- 扣减库存
local new_stock = current_stock - quantity
redis.call('SET', product_key, new_stock)

-- 记录操作日志
local log_key = 'inventory_log:' .. product_key
redis.call('LPUSH', log_key, 
    '扣减库存: ' .. tostring(quantity) .. 
    ', 剩余: ' .. tostring(new_stock) .. 
    ', 时间: ' .. tostring(redis.call('TIME')[1])
)

-- 限制日志数量
redis.call('LTRIM', log_key, 0, 99)

return {ok = true, previous = current_stock, current = new_stock}
"""

# 执行库存扣减
inventory_script_sha = r.register_script(inventory_script)

def deduct_inventory(product_id, quantity):
    """扣减库存"""
    product_key = f"inventory:{product_id}"
    
    result = inventory_script_sha(keys=[product_key], args=[quantity])
    
    if result.get('err'):
        print(f"库存扣减失败: {result['err']}")
        return False
    else:
        print(f"库存扣减成功: 原库存{result['previous']}, 现库存{result['current']}")
        return True

# 初始化库存
r.set('inventory:1001', 50)

# 测试扣减
deduct_inventory('1001', 10)
deduct_inventory('1001', 45)  # 这会失败
```

### 4.3.3 脚本缓存与性能

Redis会对Lua脚本进行缓存，使用SHA1校验和来标识脚本：

```python
# 脚本缓存管理

def manage_scripts():
    """脚本缓存管理示例"""
    
    # 定义脚本
    script_content = "return 'Hello, ' .. ARGV[1]"
    
    # 计算SHA1（与Redis内部使用的一致）
    import hashlib
    script_sha = hashlib.sha1(script_content.encode()).hexdigest()
    
    print(f"脚本SHA1: {script_sha}")
    
    # 检查脚本是否存在
    try:
        result = r.evalsha(script_sha, 0, 'World')
        print(f"脚本已缓存: {result}")
    except redis.exceptions.NoScriptError:
        print("脚本未缓存，重新加载")
        # 加载脚本
        result = r.eval(script_content, 0, 'World')
        print(f"脚本执行结果: {result}")
    
    # 查看脚本缓存
    script_cache = r.script_exists(script_sha)
    print(f"脚本是否存在缓存中: {script_cache[0]}")
    
    # 清空脚本缓存
    r.script_flush()
    print("脚本缓存已清空")

manage_scripts()
```

## 4.4 发布订阅（Pub/Sub）

### 4.4.1 发布订阅基础

Redis发布订阅模式允许消息的发布者和订阅者解耦：

```python
# 发布订阅基础示例
import threading
import time

def publisher():
    """发布者"""
    time.sleep(1)  # 等待订阅者准备
    
    # 发布消息到频道
    r.publish('news', '今日头条：Redis发布订阅')
    r.publish('sports', '体育新闻：篮球比赛结果')
    r.publish('news', '最新消息：技术更新')
    
    print("发布者：消息发布完成")

def subscriber(channel_name):
    """订阅者"""
    pubsub = r.pubsub()
    pubsub.subscribe(channel_name)
    
    print(f"订阅者：开始监听频道 {channel_name}")
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            print(f"订阅者收到消息: {message['data']} (来自频道: {message['channel']})")
        elif message['type'] == 'subscribe':
            print(f"成功订阅频道: {message['channel']}")

# 启动订阅者线程
news_thread = threading.Thread(target=subscriber, args=('news',))
sports_thread = threading.Thread(target=subscriber, args=('sports',))

news_thread.start()
sports_thread.start()

# 启动发布者线程
pub_thread = threading.Thread(target=publisher)
pub_thread.start()

# 等待线程完成
pub_thread.join()
news_thread.join(timeout=5)
sports_thread.join(timeout=5)
```

### 4.4.2 模式订阅

Redis支持使用通配符进行模式订阅：

```python
# 模式订阅示例

def pattern_subscriber():
    """模式订阅者"""
    pubsub = r.pubsub()
    
    # 订阅所有以'user:'开头的频道
    pubsub.psubscribe('user:*')
    
    print("模式订阅者：开始监听 user:* 频道")
    
    for message in pubsub.listen():
        if message['type'] == 'pmessage':
            print(f"模式订阅收到消息: {message['data']} "
                  f"(频道: {message['channel']}, 模式: {message['pattern']})")
        elif message['type'] == 'psubscribe':
            print(f"成功模式订阅: {message['pattern']}")

# 测试模式订阅
def test_pattern_pubsub():
    """测试模式发布订阅"""
    import threading
    
    # 启动模式订阅者
    pattern_thread = threading.Thread(target=pattern_subscriber)
    pattern_thread.start()
    
    time.sleep(1)
    
    # 发布消息到不同频道
    r.publish('user:login', '用户123登录')
    r.publish('user:logout', '用户456登出')
    r.publish('system:alert', '系统警告')  # 这个不会被模式订阅者收到
    
    time.sleep(1)
    pattern_thread.join(timeout=5)

test_pattern_pubsub()
```

### 4.4.3 发布订阅应用场景

**实时消息系统**：

```python
class RealTimeMessaging:
    def __init__(self):
        self.pubsub = r.pubsub()
    
    def send_message(self, room_id, user_id, message):
        """发送消息到聊天室"""
        channel = f"chat:room:{room_id}"
        message_data = {
            'user_id': user_id,
            'message': message,
            'timestamp': time.time()
        }
        
        r.publish(channel, json.dumps(message_data))
        return True
    
    def join_room(self, room_id, callback):
        """加入聊天室"""
        channel = f"chat:room:{room_id}"
        
        def message_handler():
            self.pubsub.subscribe(channel)
            
            for message in self.pubsub.listen():
                if message['type'] == 'message':
                    message_data = json.loads(message['data'])
                    callback(message_data)
        
        # 在单独线程中处理消息
        thread = threading.Thread(target=message_handler)
        thread.daemon = True
        thread.start()
        
        return thread
    
    def leave_room(self, room_id):
        """离开聊天室"""
        channel = f"chat:room:{room_id}"
        self.pubsub.unsubscribe(channel)

# 使用示例
messaging = RealTimeMessaging()

def handle_chat_message(message):
    """处理聊天消息"""
    print(f"收到消息 - 用户: {message['user_id']}, 内容: {message['message']}")

# 用户加入聊天室
messaging.join_room('general', handle_chat_message)

# 发送消息
time.sleep(1)
messaging.send_message('general', 'user123', '大家好！')
messaging.send_message('general', 'user456', '欢迎新人！')

time.sleep(2)
```

## 4.5 管道（Pipeline）高级用法

### 4.5.1 管道性能优化

管道可以显著减少网络往返时间，提高性能：

```python
# 管道性能优化示例
import time

def benchmark_pipeline():
    """管道性能对比"""
    
    # 普通操作（每次往返）
    start_time = time.time()
    
    for i in range(1000):
        r.set(f'key_{i}', f'value_{i}')
    
    normal_time = time.time() - start_time
    
    # 清空数据
    r.flushdb()
    
    # 管道操作（批量往返）
    start_time = time.time()
    
    pipe = r.pipeline()
    for i in range(1000):
        pipe.set(f'key_{i}', f'value_{i}')
    pipe.execute()
    
    pipeline_time = time.time() - start_time
    
    print(f"普通操作时间: {normal_time:.3f}秒")
    print(f"管道操作时间: {pipeline_time:.3f}秒")
    print(f"性能提升: {normal_time/pipeline_time:.1f}倍")

benchmark_pipeline()
```

### 4.5.2 管道与事务结合

管道可以与事务结合使用，实现批量原子操作：

```python
# 管道事务示例

def pipeline_transaction():
    """管道事务操作"""
    
    # 创建事务管道
    pipe = r.pipeline(transaction=True)
    
    # 开始事务
    pipe.multi()
    
    # 批量操作
    users = [
        ('user:1001', 'Alice', 25),
        ('user:1002', 'Bob', 30),
        ('user:1003', 'Charlie', 28)
    ]
    
    for user_id, name, age in users:
        pipe.hset(f'{user_id}:profile', mapping={
            'name': name,
            'age': age,
            'created_at': time.time()
        })
        pipe.sadd('users:active', user_id)
    
    # 执行事务
    results = pipe.execute()
    
    print(f"事务执行结果数量: {len(results)}")
    
    # 验证结果
    active_users = r.smembers('users:active')
    print(f"活跃用户: {active_users}")
    
    return results

pipeline_transaction()
```

## 4.6 高级特性综合应用

### 4.6.1 分布式锁实现

结合事务和Lua脚本实现分布式锁：

```python
# 分布式锁实现

class DistributedLock:
    def __init__(self, redis_client, lock_name, timeout=30):
        self.redis = redis_client
        self.lock_name = f"lock:{lock_name}"
        self.timeout = timeout
        self.identifier = str(uuid.uuid4())  # 唯一标识
    
    def acquire(self, block=True, timeout=None):
        """获取锁"""
        
        if block:
            # 阻塞方式获取锁
            end_time = time.time() + (timeout or self.timeout)
            
            while time.time() < end_time:
                if self._try_acquire():
                    return True
                time.sleep(0.1)
            
            return False
        else:
            # 非阻塞方式
            return self._try_acquire()
    
    def _try_acquire(self):
        """尝试获取锁"""
        # 使用SET NX EX命令原子性获取锁
        result = self.redis.set(
            self.lock_name, 
            self.identifier, 
            nx=True, 
            ex=self.timeout
        )
        return result is True
    
    def release(self):
        """释放锁"""
        # 使用Lua脚本保证原子性
        release_script = """
        if redis.call("GET", KEYS[1]) == ARGV[1] then
            return redis.call("DEL", KEYS[1])
        else
            return 0
        end
        """
        
        script = self.redis.register_script(release_script)
        result = script(keys=[self.lock_name], args=[self.identifier])
        
        return result == 1
    
    def __enter__(self):
        """上下文管理器支持"""
        if not self.acquire():
            raise Exception("获取锁失败")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.release()

# 使用示例
lock = DistributedLock(r, 'resource_1', timeout=10)

# 方式1: 使用上下文管理器
with lock:
    print("获取到锁，执行关键操作")
    time.sleep(2)
    print("操作完成，自动释放锁")

# 方式2: 手动管理
if lock.acquire():
    try:
        print("获取到锁，执行关键操作")
        time.sleep(2)
    finally:
        lock.release()
        print("锁已释放")
```

### 4.6.2 限流器实现

使用Lua脚本实现高性能限流器：

```python
# 限流器实现

class RateLimiter:
    def __init__(self, redis_client, key_prefix='rate_limit'):
        self.redis = redis_client
        self.key_prefix = key_prefix
    
    def is_allowed(self, identifier, max_requests, window_seconds):
        """检查是否允许请求"""
        
        limit_script = """
        local key = KEYS[1]
        local max_requests = tonumber(ARGV[1])
        local window_seconds = tonumber(ARGV[2])
        local current_time = tonumber(ARGV[3])
        
        -- 移除过期的时间戳
        redis.call('ZREMRANGEBYSCORE', key, 0, current_time - window_seconds)
        
        -- 获取当前请求数
        local current_requests = redis.call('ZCARD', key)
        
        if current_requests < max_requests then
            -- 允许请求，记录时间戳
            redis.call('ZADD', key, current_time, current_time)
            redis.call('EXPIRE', key, window_seconds)
            return {1, max_requests - current_requests - 1}
        else
            -- 拒绝请求
            return {0, 0}
        end
        """
        
        key = f"{self.key_prefix}:{identifier}"
        current_time = int(time.time())
        
        script = self.redis.register_script(limit_script)
        result = script(
            keys=[key], 
            args=[max_requests, window_seconds, current_time]
        )
        
        allowed = result[0] == 1
        remaining = result[1]
        
        return allowed, remaining

# 使用示例
limiter = RateLimiter(r)

# 测试限流
for i in range(15):
    allowed, remaining = limiter.is_allowed('user123', 10, 60)  # 每分钟10次
    
    if allowed:
        print(f"请求 {i+1}: 允许，剩余 {remaining} 次")
    else:
        print(f"请求 {i+1}: 拒绝，已超过限制")
    
    time.sleep(0.1)
```

## 总结

本章深入探讨了Redis的高级特性和事务机制。通过学习本章，您应该能够：

1. 理解Redis事务的工作原理和局限性
2. 掌握WATCH机制实现乐观锁
3. 熟练使用Lua脚本实现复杂业务逻辑
4. 应用发布订阅模式构建实时系统
5. 使用管道优化性能
6. 实现分布式锁和限流器等高级功能

这些高级特性让Redis不仅仅是一个简单的键值存储，而是能够支持复杂业务场景的强大工具。在下一章中，我们将学习Redis集群和高可用方案，这是构建大规模Redis应用的关键。