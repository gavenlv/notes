# 7. Redis性能优化与监控

## 7.1 Redis性能优化核心原则

### 7.1.1 内存使用优化

**内存使用策略**

```python
# 内存优化示例代码
import redis
import json
from datetime import datetime

class MemoryOptimizedRedis:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def compress_data(self, data):
        """数据压缩优化"""
        if isinstance(data, str) and len(data) > 100:
            # 使用简单的压缩算法
            return f"COMPRESSED:{len(data)}:{data[:50]}..."
        return data
    
    def store_optimized(self, key, data, ttl=3600):
        """优化存储"""
        # 压缩数据
        optimized_data = self.compress_data(data)
        
        # 使用合适的数据结构
        if isinstance(data, dict):
            # 对于小字典，使用Hash
            if len(data) <= 10:
                self.redis.hset(key, mapping=data)
                self.redis.expire(key, ttl)
            else:
                # 对于大字典，使用JSON序列化
                self.redis.setex(key, ttl, json.dumps(data))
        elif isinstance(data, list):
            # 对于列表，使用List
            self.redis.delete(key)  # 先清空
            self.redis.rpush(key, *data)
            self.redis.expire(key, ttl)
        else:
            self.redis.setex(key, ttl, str(data))
    
    def memory_analysis(self):
        """内存使用分析"""
        info = self.redis.info('memory')
        
        print("=== 内存使用分析 ===")
        print(f"已用内存: {info['used_memory_human']}")
        print(f"峰值内存: {info['used_memory_peak_human']}")
        print(f"内存碎片率: {info['mem_fragmentation_ratio']:.2f}")
        print(f"已用内存RSS: {info['used_memory_rss_human']}")
        
        # 分析大Key
        big_keys = self.redis.execute_command('MEMORY USAGE', 'sample_key')
        print(f"示例Key内存使用: {big_keys} bytes")

# 使用示例
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
optimized_redis = MemoryOptimizedRedis(r)

# 测试不同数据类型的存储优化
test_data = {
    'small_dict': {'a': 1, 'b': 2},
    'large_dict': {f'key_{i}': f'value_{i}' for i in range(100)},
    'large_string': 'x' * 1000
}

for key, data in test_data.items():
    optimized_redis.store_optimized(key, data)

optimized_redis.memory_analysis()
```

### 7.1.2 命令执行优化

**批量操作与管道**

```python
import time
import redis

class PerformanceOptimizer:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def batch_operations_comparison(self):
        """批量操作性能对比"""
        
        # 方法1: 逐个设置（低效）
        start_time = time.time()
        for i in range(1000):
            self.redis.set(f'key_{i}', f'value_{i}')
        sequential_time = time.time() - start_time
        
        # 清理
        for i in range(1000):
            self.redis.delete(f'key_{i}')
        
        # 方法2: 使用管道（高效）
        start_time = time.time()
        pipeline = self.redis.pipeline()
        for i in range(1000):
            pipeline.set(f'key_{i}', f'value_{i}')
        pipeline.execute()
        pipeline_time = time.time() - start_time
        
        # 清理
        pipeline = self.redis.pipeline()
        for i in range(1000):
            pipeline.delete(f'key_{i}')
        pipeline.execute()
        
        print("=== 批量操作性能对比 ===")
        print(f"逐个设置耗时: {sequential_time:.3f}秒")
        print(f"管道批量设置耗时: {pipeline_time:.3f}秒")
        print(f"性能提升: {sequential_time/pipeline_time:.1f}倍")
    
    def mset_vs_pipeline(self):
        """MSET与管道性能对比"""
        
        # 准备数据
        data = {f'key_mset_{i}': f'value_{i}' for i in range(100)}
        
        # MSET方法
        start_time = time.time()
        self.redis.mset(data)
        mset_time = time.time() - start_time
        
        # 管道方法
        start_time = time.time()
        pipeline = self.redis.pipeline()
        for key, value in data.items():
            pipeline.set(key, value)
        pipeline.execute()
        pipeline_time = time.time() - start_time
        
        print("=== MSET vs 管道 ===")
        print(f"MSET耗时: {mset_time:.3f}秒")
        print(f"管道耗时: {pipeline_time:.3f}秒")
        print(f"MSET优势: {pipeline_time/mset_time:.1f}倍")

# 使用示例
optimizer = PerformanceOptimizer(r)
optimizer.batch_operations_comparison()
optimizer.mset_vs_pipeline()
```

## 7.2 Redis监控与诊断

### 7.2.1 实时监控指标

```python
import time
import redis
from collections import defaultdict

class RedisMonitor:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.metrics_history = defaultdict(list)
    
    def collect_metrics(self):
        """收集Redis监控指标"""
        
        # 基础信息
        info = self.redis.info()
        
        metrics = {
            'timestamp': time.time(),
            'connected_clients': info['connected_clients'],
            'used_memory': info['used_memory'],
            'used_memory_rss': info['used_memory_rss'],
            'mem_fragmentation_ratio': info['mem_fragmentation_ratio'],
            'total_commands_processed': info['total_commands_processed'],
            'instantaneous_ops_per_sec': info['instantaneous_ops_per_sec'],
            'keyspace_hits': info['keyspace_hits'],
            'keyspace_misses': info['keyspace_misses'],
            'evicted_keys': info['evicted_keys'],
            'expired_keys': info['expired_keys'],
            'connected_slaves': info.get('connected_slaves', 0),
            'rejected_connections': info['rejected_connections']
        }
        
        # 计算命中率
        total_commands = metrics['keyspace_hits'] + metrics['keyspace_misses']
        if total_commands > 0:
            metrics['hit_ratio'] = metrics['keyspace_hits'] / total_commands
        else:
            metrics['hit_ratio'] = 0
        
        return metrics
    
    def print_metrics(self, metrics):
        """打印监控指标"""
        print("=== Redis实时监控 ===")
        print(f"连接客户端数: {metrics['connected_clients']}")
        print(f"内存使用: {metrics['used_memory'] / 1024 / 1024:.1f} MB")
        print(f"内存碎片率: {metrics['mem_fragmentation_ratio']:.2f}")
        print(f"QPS: {metrics['instantaneous_ops_per_sec']}")
        print(f"缓存命中率: {metrics['hit_ratio']:.2%}")
        print(f"已驱逐Key数: {metrics['evicted_keys']}")
        print(f"已过期Key数: {metrics['expired_keys']}")
        print(f"拒绝连接数: {metrics['rejected_connections']}")
    
    def continuous_monitoring(self, duration=60, interval=5):
        """持续监控"""
        print(f"开始持续监控，持续时间: {duration}秒，间隔: {interval}秒")
        
        start_time = time.time()
        while time.time() - start_time < duration:
            metrics = self.collect_metrics()
            self.print_metrics(metrics)
            
            # 存储历史数据
            for key, value in metrics.items():
                if key != 'timestamp':
                    self.metrics_history[key].append(value)
            
            time.sleep(interval)
    
    def analyze_trends(self):
        """分析趋势"""
        print("=== 趋势分析 ===")
        
        for metric_name, values in self.metrics_history.items():
            if values:
                avg = sum(values) / len(values)
                max_val = max(values)
                min_val = min(values)
                print(f"{metric_name}: 平均={avg:.2f}, 最大={max_val}, 最小={min_val}")

# 使用示例
monitor = RedisMonitor(r)

# 单次监控
metrics = monitor.collect_metrics()
monitor.print_metrics(metrics)

# 持续监控（短时间演示）
monitor.continuous_monitoring(duration=15, interval=3)
monitor.analyze_trends()
```

### 7.2.2 慢查询分析

```python
class SlowQueryAnalyzer:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def configure_slow_log(self, slowlog_max_len=128, slowlog_log_slower_than=10000):
        """配置慢查询日志"""
        # 设置慢查询阈值（微秒）
        self.redis.config_set('slowlog-log-slower-than', slowlog_log_slower_than)
        # 设置慢查询日志最大长度
        self.redis.config_set('slowlog-max-len', slowlog_max_len)
        
        print(f"慢查询配置完成: 阈值={slowlog_log_slower_than}微秒, 最大长度={slowlog_max_len}")
    
    def get_slow_queries(self):
        """获取慢查询"""
        slow_queries = self.redis.slowlog_get()
        
        print("=== 慢查询分析 ===")
        print(f"慢查询数量: {len(slow_queries)}")
        
        for i, query in enumerate(slow_queries):
            print(f"\n慢查询 #{i+1}:")
            print(f"  执行时间: {query['duration']} 微秒")
            print(f"  命令: {' '.join(query['command'])}")
            print(f"  时间戳: {query['start_time']}")
            print(f"  客户端: {query['client_address']}:{query['client_port']}")
            print(f"  客户端名称: {query.get('client_name', 'N/A')}")
        
        return slow_queries
    
    def generate_slow_query_report(self):
        """生成慢查询报告"""
        slow_queries = self.get_slow_queries()
        
        if not slow_queries:
            print("未发现慢查询")
            return
        
        # 分析最慢的命令
        slowest_query = max(slow_queries, key=lambda x: x['duration'])
        
        print("\n=== 慢查询报告 ===")
        print(f"最慢查询耗时: {slowest_query['duration']} 微秒")
        print(f"最慢查询命令: {' '.join(slowest_query['command'])}")
        
        # 按命令类型分组
        command_groups = {}
        for query in slow_queries:
            command = query['command'][0] if query['command'] else 'unknown'
            if command not in command_groups:
                command_groups[command] = []
            command_groups[command].append(query)
        
        print("\n按命令类型分组:")
        for command, queries in command_groups.items():
            avg_duration = sum(q['duration'] for q in queries) / len(queries)
            print(f"  {command}: {len(queries)}次, 平均耗时: {avg_duration:.0f}微秒")

# 使用示例
slow_analyzer = SlowQueryAnalyzer(r)

# 配置慢查询（阈值设为10毫秒）
slow_analyzer.configure_slow_log(slowlog_log_slower_than=10000)

# 生成一些操作来测试慢查询
for i in range(100):
    r.set(f'test_key_{i}', 'x' * 1000)

# 获取慢查询报告
slow_analyzer.generate_slow_query_report()
```

## 7.3 高级优化技巧

### 7.3.1 连接池优化

```python
import redis
from redis.connection import ConnectionPool

class ConnectionPoolOptimizer:
    def __init__(self, host='localhost', port=6379):
        self.host = host
        self.port = port
    
    def create_optimized_pool(self, max_connections=20, timeout=5, retry_on_timeout=True):
        """创建优化的连接池"""
        
        pool = ConnectionPool(
            host=self.host,
            port=self.port,
            max_connections=max_connections,
            socket_connect_timeout=timeout,
            socket_timeout=timeout,
            retry_on_timeout=retry_on_timeout,
            health_check_interval=30,  # 健康检查间隔
            decode_responses=True
        )
        
        redis_client = redis.Redis(connection_pool=pool)
        
        print(f"连接池配置: 最大连接数={max_connections}, 超时={timeout}秒")
        return redis_client
    
    def test_connection_pool(self, client, concurrent_requests=50):
        """测试连接池性能"""
        import threading
        import time
        
        results = []
        lock = threading.Lock()
        
        def worker(worker_id):
            start_time = time.time()
            
            try:
                # 执行一些操作
                for i in range(10):
                    client.set(f'pool_test_{worker_id}_{i}', f'value_{i}')
                    client.get(f'pool_test_{worker_id}_{i}')
                
                end_time = time.time()
                duration = end_time - start_time
                
                with lock:
                    results.append((worker_id, duration, True))
            except Exception as e:
                with lock:
                    results.append((worker_id, 0, False, str(e)))
        
        # 创建并发线程
        threads = []
        for i in range(concurrent_requests):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 分析结果
        successful = [r for r in results if r[2]]
        failed = [r for r in results if not r[2]]
        
        print(f"\n=== 连接池测试结果 ===")
        print(f"并发请求数: {concurrent_requests}")
        print(f"成功: {len(successful)}")
        print(f"失败: {len(failed)}")
        
        if successful:
            avg_duration = sum(r[1] for r in successful) / len(successful)
            print(f"平均耗时: {avg_duration:.3f}秒")
        
        if failed:
            print("失败原因:")
            for failure in failed:
                print(f"  线程 {failure[0]}: {failure[3]}")

# 使用示例
optimizer = ConnectionPoolOptimizer()

# 创建优化连接池
client = optimizer.create_optimized_pool(max_connections=10, timeout=3)

# 测试连接池
optimizer.test_connection_pool(client, concurrent_requests=15)
```

### 7.3.2 Lua脚本优化

```python
class LuaScriptOptimizer:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def register_optimized_scripts(self):
        """注册优化的Lua脚本"""
        
        # 脚本1: 原子性计数器
        counter_script = """
        local key = KEYS[1]
        local increment = tonumber(ARGV[1])
        local ttl = tonumber(ARGV[2])
        
        local current = redis.call('GET', key)
        if current == false then
            current = 0
        else
            current = tonumber(current)
        end
        
        local new_value = current + increment
        redis.call('SET', key, new_value)
        
        if ttl > 0 then
            redis.call('EXPIRE', key, ttl)
        end
        
        return new_value
        """
        
        # 脚本2: 条件性设置
        conditional_set_script = """
        local key = KEYS[1]
        local value = ARGV[1]
        local condition = ARGV[2]
        
        local current = redis.call('GET', key)
        
        if condition == 'exists' and current == false then
            return {err = 'Key does not exist'}
        elseif condition == 'not_exists' and current ~= false then
            return {err = 'Key already exists'}
        elseif condition == 'greater' and tonumber(current) <= tonumber(value) then
            return {err = 'Current value is not greater'}
        end
        
        redis.call('SET', key, value)
        return {ok = 'Success'}
        """
        
        # 注册脚本
        self.counter_script_sha = self.redis.script_load(counter_script)
        self.conditional_set_script_sha = self.redis.script_load(conditional_set_script)
        
        print("Lua脚本注册完成")
        return {
            'counter_script': self.counter_script_sha,
            'conditional_set_script': self.conditional_set_script_sha
        }
    
    def test_optimized_scripts(self):
        """测试优化脚本性能"""
        import time
        
        # 测试原子计数器
        print("=== 原子计数器测试 ===")
        
        start_time = time.time()
        
        # 使用脚本执行
        for i in range(100):
            result = self.redis.evalsha(
                self.counter_script_sha, 
                1, 'test_counter', 1, 60
            )
        
        script_time = time.time() - start_time
        
        # 传统方法（作为对比）
        start_time = time.time()
        
        for i in range(100):
            with self.redis.pipeline() as pipe:
                pipe.get('test_counter_2')
                pipe.incr('test_counter_2')
                pipe.execute()
        
        traditional_time = time.time() - start_time
        
        print(f"脚本方法耗时: {script_time:.3f}秒")
        print(f"传统方法耗时: {traditional_time:.3f}秒")
        print(f"性能提升: {traditional_time/script_time:.1f}倍")
        
        # 测试条件设置
        print("\n=== 条件设置测试 ===")
        
        # 设置初始值
        self.redis.set('conditional_key', '10')
        
        # 使用脚本进行条件设置
        result = self.redis.evalsha(
            self.conditional_set_script_sha,
            1, 'conditional_key', '20', 'greater'
        )
        
        print(f"条件设置结果: {result}")

# 使用示例
lua_optimizer = LuaScriptOptimizer(r)
scripts = lua_optimizer.register_optimized_scripts()
lua_optimizer.test_optimized_scripts()
```

## 7.4 性能基准测试

```python
import time
import redis
import statistics

class RedisBenchmark:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def benchmark_operations(self, operation_count=1000):
        """基准测试各种操作"""
        
        benchmarks = {}
        
        # SET操作基准
        start_time = time.time()
        for i in range(operation_count):
            self.redis.set(f'benchmark_set_{i}', f'value_{i}')
        benchmarks['SET'] = time.time() - start_time
        
        # GET操作基准
        start_time = time.time()
        for i in range(operation_count):
            self.redis.get(f'benchmark_set_{i}')
        benchmarks['GET'] = time.time() - start_time
        
        # HSET操作基准
        start_time = time.time()
        for i in range(operation_count):
            self.redis.hset('benchmark_hash', f'field_{i}', f'value_{i}')
        benchmarks['HSET'] = time.time() - start_time
        
        # HGET操作基准
        start_time = time.time()
        for i in range(operation_count):
            self.redis.hget('benchmark_hash', f'field_{i}')
        benchmarks['HGET'] = time.time() - start_time
        
        # 管道操作基准
        start_time = time.time()
        pipeline = self.redis.pipeline()
        for i in range(operation_count):
            pipeline.set(f'benchmark_pipeline_{i}', f'value_{i}')
        pipeline.execute()
        benchmarks['PIPELINE_SET'] = time.time() - start_time
        
        # 清理测试数据
        self.redis.delete('benchmark_hash')
        for i in range(operation_count):
            self.redis.delete(f'benchmark_set_{i}')
            self.redis.delete(f'benchmark_pipeline_{i}')
        
        return benchmarks
    
    def run_comprehensive_benchmark(self, iterations=5):
        """运行综合基准测试"""
        
        all_results = []
        
        for i in range(iterations):
            print(f"运行基准测试迭代 {i+1}/{iterations}")
            results = self.benchmark_operations(1000)
            all_results.append(results)
        
        # 计算平均性能
        avg_results = {}
        for operation in all_results[0].keys():
            values = [r[operation] for r in all_results]
            avg_results[operation] = statistics.mean(values)
        
        # 计算QPS
        operation_count = 1000
        qps_results = {}
        for operation, duration in avg_results.items():
            qps_results[operation] = operation_count / duration
        
        print("\n=== Redis性能基准测试结果 ===")
        print("\n操作耗时 (秒):")
        for operation, duration in avg_results.items():
            print(f"  {operation}: {duration:.3f}秒")
        
        print("\nQPS (每秒操作数):")
        for operation, qps in qps_results.items():
            print(f"  {operation}: {qps:.0f} ops/sec")
        
        return avg_results, qps_results

# 使用示例
benchmark = RedisBenchmark(r)

# 运行基准测试
avg_results, qps_results = benchmark.run_comprehensive_benchmark(iterations=3)

print("\n=== 性能优化建议 ===")
print("1. 对于批量操作，优先使用管道(PIPELINE)")
print("2. 对于频繁读取的小数据，使用Hash结构")
print("3. 根据QPS需求调整连接池大小")
print("4. 定期监控内存使用和碎片率")
print("5. 设置合理的Key过期时间避免内存泄漏")
```

## 7.5 本章总结

本章深入探讨了Redis性能优化与监控的各个方面：

1. **性能优化核心原则**：内存使用优化、命令执行优化
2. **实时监控与诊断**：指标收集、慢查询分析、趋势分析
3. **高级优化技巧**：连接池优化、Lua脚本优化
4. **性能基准测试**：综合性能评估与优化建议

通过这些技术，您可以构建高性能、高可用的Redis应用，确保系统在各种负载下都能稳定运行。