# 第6章：Redis性能优化与监控

## 6.1 Redis性能瓶颈分析

### 6.1.1 常见性能瓶颈

Redis性能主要受以下因素影响：

```python
# 性能瓶颈检测脚本
import time
import redis
from threading import Thread

class PerformanceAnalyzer:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def analyze_memory_usage(self):
        """分析内存使用情况"""
        info = self.redis.info('memory')
        
        memory_analysis = {
            'used_memory': int(info.get('used_memory', 0)),
            'used_memory_human': info.get('used_memory_human', '0'),
            'used_memory_peak': int(info.get('used_memory_peak', 0)),
            'used_memory_peak_human': info.get('used_memory_peak_human', '0'),
            'used_memory_rss': int(info.get('used_memory_rss', 0)),
            'used_memory_rss_human': info.get('used_memory_rss_human', '0'),
            'mem_fragmentation_ratio': float(info.get('mem_fragmentation_ratio', 0)),
            'memory_pressure': 'normal'
        }
        
        # 判断内存压力
        if memory_analysis['mem_fragmentation_ratio'] > 1.5:
            memory_analysis['memory_pressure'] = 'high_fragmentation'
        elif memory_analysis['used_memory'] > 0.8 * memory_analysis['used_memory_peak']:
            memory_analysis['memory_pressure'] = 'high_usage'
        
        return memory_analysis
    
    def analyze_cpu_usage(self):
        """分析CPU使用情况"""
        info = self.redis.info('cpu')
        
        cpu_analysis = {
            'used_cpu_sys': float(info.get('used_cpu_sys', 0)),
            'used_cpu_user': float(info.get('used_cpu_user', 0)),
            'used_cpu_sys_children': float(info.get('used_cpu_sys_children', 0)),
            'used_cpu_user_children': float(info.get('used_cpu_user_children', 0)),
            'cpu_pressure': 'normal'
        }
        
        # 简单的CPU压力判断
        total_cpu = cpu_analysis['used_cpu_sys'] + cpu_analysis['used_cpu_user']
        if total_cpu > 80:  # 假设80%为阈值
            cpu_analysis['cpu_pressure'] = 'high_usage'
        
        return cpu_analysis
    
    def analyze_network_io(self):
        """分析网络IO"""
        info = self.redis.info('stats')
        
        io_analysis = {
            'total_connections_received': int(info.get('total_connections_received', 0)),
            'total_commands_processed': int(info.get('total_commands_processed', 0)),
            'instantaneous_ops_per_sec': int(info.get('instantaneous_ops_per_sec', 0)),
            'instantaneous_input_kbps': float(info.get('instantaneous_input_kbps', 0)),
            'instantaneous_output_kbps': float(info.get('instantaneous_output_kbps', 0)),
            'rejected_connections': int(info.get('rejected_connections', 0)),
            'io_pressure': 'normal'
        }
        
        if io_analysis['rejected_connections'] > 0:
            io_analysis['io_pressure'] = 'connection_rejected'
        
        return io_analysis
    
    def run_comprehensive_analysis(self):
        """综合性能分析"""
        analysis = {
            'timestamp': time.time(),
            'memory': self.analyze_memory_usage(),
            'cpu': self.analyze_cpu_usage(),
            'network_io': self.analyze_network_io(),
            'overall_health': 'healthy'
        }
        
        # 综合健康评估
        issues = []
        
        if analysis['memory']['memory_pressure'] != 'normal':
            issues.append(f"内存问题: {analysis['memory']['memory_pressure']}")
        
        if analysis['cpu']['cpu_pressure'] != 'normal':
            issues.append(f"CPU问题: {analysis['cpu']['cpu_pressure']}")
        
        if analysis['network_io']['io_pressure'] != 'normal':
            issues.append(f"IO问题: {analysis['network_io']['io_pressure']}")
        
        if issues:
            analysis['overall_health'] = 'degraded'
            analysis['issues'] = issues
        
        return analysis

# 使用示例
r = redis.Redis(decode_responses=True)
analyzer = PerformanceAnalyzer(r)

analysis = analyzer.run_comprehensive_analysis()
print("性能分析结果:")
import json
print(json.dumps(analysis, indent=2, ensure_ascii=False))
```

### 6.1.2 性能基准测试

```python
# Redis性能基准测试
import time
import statistics

class RedisBenchmark:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def benchmark_set_operations(self, key_count=10000, value_size=100):
        """测试SET操作性能"""
        # 准备测试数据
        value = 'x' * value_size
        
        # 预热
        self.redis.flushdb()
        
        # 测试SET操作
        start_time = time.time()
        
        for i in range(key_count):
            self.redis.set(f'key_{i}', value)
        
        set_time = time.time() - start_time
        
        # 计算性能指标
        set_ops_per_sec = key_count / set_time
        
        return {
            'operation': 'SET',
            'key_count': key_count,
            'value_size': value_size,
            'total_time': round(set_time, 3),
            'ops_per_sec': round(set_ops_per_sec, 2),
            'throughput_mb_per_sec': round((key_count * value_size) / set_time / 1024 / 1024, 2)
        }
    
    def benchmark_get_operations(self, key_count=10000):
        """测试GET操作性能"""
        # 确保有数据
        if self.redis.dbsize() == 0:
            self.benchmark_set_operations(key_count, 100)
        
        # 测试GET操作
        start_time = time.time()
        
        for i in range(key_count):
            self.redis.get(f'key_{i}')
        
        get_time = time.time() - start_time
        
        # 计算性能指标
        get_ops_per_sec = key_count / get_time
        
        return {
            'operation': 'GET',
            'key_count': key_count,
            'total_time': round(get_time, 3),
            'ops_per_sec': round(get_ops_per_sec, 2)
        }
    
    def benchmark_pipeline(self, batch_size=100, total_operations=10000):
        """测试管道性能"""
        value = 'x' * 100
        
        # 普通操作
        self.redis.flushdb()
        start_time = time.time()
        
        for i in range(total_operations):
            self.redis.set(f'key_{i}', value)
        
        normal_time = time.time() - start_time
        
        # 管道操作
        self.redis.flushdb()
        start_time = time.time()
        
        pipeline = self.redis.pipeline()
        for i in range(total_operations):
            pipeline.set(f'key_{i}', value)
            
            if (i + 1) % batch_size == 0:
                pipeline.execute()
        
        # 执行剩余命令
        if total_operations % batch_size != 0:
            pipeline.execute()
        
        pipeline_time = time.time() - start_time
        
        return {
            'operation': 'PIPELINE',
            'batch_size': batch_size,
            'total_operations': total_operations,
            'normal_time': round(normal_time, 3),
            'pipeline_time': round(pipeline_time, 3),
            'speedup_ratio': round(normal_time / pipeline_time, 2)
        }
    
    def run_comprehensive_benchmark(self):
        """运行综合基准测试"""
        benchmarks = []
        
        # 测试不同操作类型
        benchmarks.append(self.benchmark_set_operations(10000, 100))
        benchmarks.append(self.benchmark_get_operations(10000))
        benchmarks.append(self.benchmark_pipeline(100, 10000))
        
        # 汇总结果
        summary = {
            'timestamp': time.time(),
            'benchmarks': benchmarks,
            'average_ops_per_sec': statistics.mean([b['ops_per_sec'] for b in benchmarks if 'ops_per_sec' in b])
        }
        
        return summary

# 使用示例
benchmark = RedisBenchmark(r)
results = benchmark.run_comprehensive_benchmark()
print("基准测试结果:")
print(json.dumps(results, indent=2, ensure_ascii=False))
```

## 6.2 内存优化策略

### 6.2.1 内存使用分析

```python
# 内存使用分析工具
class MemoryOptimizer:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def analyze_memory_usage_by_key_pattern(self, pattern='*', sample_size=1000):
        """按key模式分析内存使用"""
        # 获取匹配的key
        keys = self.redis.keys(pattern)
        
        if not keys:
            return {'error': 'No keys found matching pattern'}
        
        # 采样分析
        sample_keys = keys[:sample_size] if len(keys) > sample_size else keys
        
        memory_usage = []
        
        for key in sample_keys:
            try:
                # 使用debug object命令获取内存使用（需要Redis 4.0+）
                memory_info = self.redis.memory_usage(key)
                
                if memory_info:
                    key_type = self.redis.type(key)
                    
                    memory_usage.append({
                        'key': key,
                        'type': key_type,
                        'memory_bytes': memory_info,
                        'memory_kb': round(memory_info / 1024, 2)
                    })
            except Exception as e:
                # 某些Redis版本可能不支持memory usage命令
                pass
        
        # 按内存使用排序
        memory_usage.sort(key=lambda x: x['memory_bytes'], reverse=True)
        
        # 统计信息
        total_memory = sum(item['memory_bytes'] for item in memory_usage)
        
        return {
            'pattern': pattern,
            'total_keys': len(keys),
            'sampled_keys': len(sample_keys),
            'total_memory_bytes': total_memory,
            'total_memory_mb': round(total_memory / 1024 / 1024, 2),
            'top_memory_users': memory_usage[:10],  # 前10个内存使用最多的key
            'memory_by_type': self._group_by_type(memory_usage)
        }
    
    def _group_by_type(self, memory_usage):
        """按数据类型分组统计"""
        type_groups = {}
        
        for item in memory_usage:
            key_type = item['type']
            if key_type not in type_groups:
                type_groups[key_type] = {
                    'count': 0,
                    'total_memory': 0,
                    'avg_memory': 0
                }
            
            type_groups[key_type]['count'] += 1
            type_groups[key_type]['total_memory'] += item['memory_bytes']
        
        # 计算平均值
        for key_type in type_groups:
            if type_groups[key_type]['count'] > 0:
                type_groups[key_type]['avg_memory'] = \
                    type_groups[key_type]['total_memory'] / type_groups[key_type]['count']
        
        return type_groups
    
    def find_memory_hogs(self, threshold_mb=10):
        """查找内存占用过大的key"""
        threshold_bytes = threshold_mb * 1024 * 1024
        
        memory_hogs = []
        
        # 扫描所有key（生产环境慎用）
        cursor = 0
        while True:
            cursor, keys = self.redis.scan(cursor, count=100)
            
            for key in keys:
                try:
                    memory_usage = self.redis.memory_usage(key)
                    
                    if memory_usage and memory_usage > threshold_bytes:
                        key_type = self.redis.type(key)
                        ttl = self.redis.ttl(key)
                        
                        memory_hogs.append({
                            'key': key,
                            'type': key_type,
                            'memory_mb': round(memory_usage / 1024 / 1024, 2),
                            'ttl': ttl
                        })
                except:
                    pass
            
            if cursor == 0:
                break
        
        # 按内存使用排序
        memory_hogs.sort(key=lambda x: x['memory_mb'], reverse=True)
        
        return memory_hogs
    
    def optimize_memory_usage(self):
        """内存优化建议"""
        suggestions = []
        
        # 获取内存信息
        memory_info = self.redis.info('memory')
        
        # 检查内存碎片率
        frag_ratio = float(memory_info.get('mem_fragmentation_ratio', 1))
        if frag_ratio > 1.5:
            suggestions.append({
                'type': 'fragmentation',
                'severity': 'high',
                'message': f'内存碎片率较高: {frag_ratio:.2f}',
                'suggestion': '考虑重启Redis实例或使用memory purge命令'
            })
        
        # 检查是否接近内存限制
        used_memory = int(memory_info.get('used_memory', 0))
        max_memory = int(memory_info.get('maxmemory', 0))
        
        if max_memory > 0 and used_memory > 0.8 * max_memory:
            suggestions.append({
                'type': 'memory_limit',
                'severity': 'high',
                'message': f'内存使用接近限制: {used_memory}/{max_memory}',
                'suggestion': '考虑增加maxmemory配置或优化数据存储'
            })
        
        # 检查大key
        big_keys = self.find_memory_hogs(1)  # 查找大于1MB的key
        if big_keys:
            suggestions.append({
                'type': 'big_keys',
                'severity': 'medium',
                'message': f'发现 {len(big_keys)} 个大key（>1MB）',
                'suggestion': '考虑拆分大key或使用更合适的数据结构'
            })
        
        return suggestions

# 使用示例
optimizer = MemoryOptimizer(r)

# 分析内存使用
memory_analysis = optimizer.analyze_memory_usage_by_key_pattern('user:*')
print("内存使用分析:")
print(json.dumps(memory_analysis, indent=2, ensure_ascii=False))

# 查找内存占用大的key
big_keys = optimizer.find_memory_hogs(1)
print(f"发现 {len(big_keys)} 个大key")

# 获取优化建议
suggestions = optimizer.optimize_memory_usage()
print("优化建议:")
for suggestion in suggestions:
    print(f"- [{suggestion['severity'].upper()}] {suggestion['message']}")
    print(f"  建议: {suggestion['suggestion']}")
```

### 6.2.2 数据结构优化

```python
# 数据结构优化示例
class DataStructureOptimizer:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def optimize_user_session_storage(self, user_id):
        """优化用户会话存储"""
        # 原始方案：使用字符串存储JSON
        session_key = f"session:{user_id}"
        
        session_data = {
            'user_id': user_id,
            'username': 'testuser',
            'last_login': '2024-01-01 10:00:00',
            'preferences': {'theme': 'dark', 'language': 'zh'},
            'cart_items': 5
        }
        
        # 方案1：JSON字符串（不推荐）
        self.redis.set(session_key, json.dumps(session_data))
        memory_json = self.redis.memory_usage(session_key) or 0
        
        # 方案2：Hash结构（推荐）
        hash_key = f"session:hash:{user_id}"
        
        # 存储基本字段
        self.redis.hset(hash_key, mapping={
            'user_id': session_data['user_id'],
            'username': session_data['username'],
            'last_login': session_data['last_login'],
            'cart_items': str(session_data['cart_items'])
        })
        
        # 复杂字段单独存储
        self.redis.hset(f"{hash_key}:preferences", mapping=session_data['preferences'])
        
        memory_hash = self.redis.memory_usage(hash_key) or 0
        memory_hash_prefs = self.redis.memory_usage(f"{hash_key}:preferences") or 0
        total_memory_hash = memory_hash + memory_hash_prefs
        
        return {
            'user_id': user_id,
            'json_approach': {
                'memory_bytes': memory_json,
                'memory_kb': round(memory_json / 1024, 2)
            },
            'hash_approach': {
                'memory_bytes': total_memory_hash,
                'memory_kb': round(total_memory_hash / 1024, 2),
                'components': {
                    'main_hash': memory_hash,
                    'preferences_hash': memory_hash_prefs
                }
            },
            'savings_percentage': round((memory_json - total_memory_hash) / memory_json * 100, 2)
        }
    
    def optimize_counter_storage(self):
        """优化计数器存储"""
        # 方案1：字符串存储（不推荐用于频繁更新的计数器）
        str_counter_key = "counter:string"
        
        # 方案2：使用INCR命令（推荐）
        incr_counter_key = "counter:incr"
        
        # 测试内存使用
        self.redis.set(str_counter_key, "0")
        self.redis.set(incr_counter_key, "0")
        
        # 执行多次递增
        for i in range(1000):
            self.redis.incr(incr_counter_key)
            self.redis.set(str_counter_key, str(int(self.redis.get(str_counter_key)) + 1))
        
        memory_str = self.redis.memory_usage(str_counter_key) or 0
        memory_incr = self.redis.memory_usage(incr_counter_key) or 0
        
        return {
            'string_approach': {
                'memory_bytes': memory_str,
                'operations': 'SET命令'
            },
            'incr_approach': {
                'memory_bytes': memory_incr,
                'operations': 'INCR命令'
            },
            'efficiency_gain': round(memory_str / memory_incr, 2) if memory_incr > 0 else 0
        }

# 使用示例
ds_optimizer = DataStructureOptimizer(r)

# 优化用户会话存储
session_optimization = ds_optimizer.optimize_user_session_storage('user123')
print("会话存储优化对比:")
print(json.dumps(session_optimization, indent=2, ensure_ascii=False))

# 优化计数器存储
counter_optimization = ds_optimizer.optimize_counter_storage()
print("计数器存储优化对比:")
print(json.dumps(counter_optimization, indent=2, ensure_ascii=False))
```

## 6.3 网络与连接优化

### 6.3.1 连接池优化

```python
# 连接池优化配置
class ConnectionPoolOptimizer:
    def __init__(self, host='localhost', port=6379):
        self.host = host
        self.port = port
    
    def test_connection_pool_performance(self, pool_sizes=[5, 10, 20, 50]):
        """测试不同连接池大小的性能"""
        results = []
        
        for pool_size in pool_sizes:
            # 创建连接池
            pool = redis.ConnectionPool(
                host=self.host,
                port=self.port,
                max_connections=pool_size,
                decode_responses=True
            )
            
            # 创建客户端
            client = redis.Redis(connection_pool=pool)
            
            # 性能测试
            start_time = time.time()
            
            # 模拟并发操作
            import threading
            
            def worker(thread_id):
                for i in range(100):
                    client.set(f'test_{thread_id}_{i}', f'value_{thread_id}_{i}')
                    client.get(f'test_{thread_id}_{i}')
            
            threads = []
            for i in range(min(pool_size, 20)):  # 最多20个线程
                thread = threading.Thread(target=worker, args=(i,))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            total_time = time.time() - start_time
            
            # 清理测试数据
            client.flushdb()
            
            results.append({
                'pool_size': pool_size,
                'threads': len(threads),
                'total_time': round(total_time, 3),
                'operations_per_second': round((len(threads) * 200) / total_time, 2)
            })
            
            # 关闭连接池
            pool.disconnect()
        
        return results
    
    def optimize_pool_configuration(self):
        """优化连接池配置"""
        # 获取系统信息
        import multiprocessing
        cpu_count = multiprocessing.cpu_count()
        
        # 推荐配置
        recommendations = {
            'max_connections': min(100, cpu_count * 10),
            'idle_time_seconds': 300,
            'retry_on_timeout': True,
            'socket_keepalive': True,
            'socket_keepalive_options': {
                'TCP_KEEPIDLE': 60,
                'TCP_KEEPINTVL': 30,
                'TCP_KEEPCNT': 3
            }
        }
        
        # 性能测试结果
        performance_results = self.test_connection_pool_performance([5, 10, 20])
        
        # 基于测试结果调整推荐
        best_pool_size = max(performance_results, key=lambda x: x['operations_per_second'])
        recommendations['recommended_pool_size'] = best_pool_size['pool_size']
        
        return {
            'system_info': {
                'cpu_count': cpu_count,
                'recommendations': recommendations
            },
            'performance_test': performance_results
        }

# 使用示例
pool_optimizer = ConnectionPoolOptimizer()

# 测试连接池性能
pool_results = pool_optimizer.test_connection_pool_performance()
print("连接池性能测试:")
for result in pool_results:
    print(f"池大小 {result['pool_size']}: {result['operations_per_second']} ops/sec")

# 获取优化建议
optimization_advice = pool_optimizer.optimize_pool_configuration()
print("连接池优化建议:")
print(json.dumps(optimization_advice, indent=2, ensure_ascii=False))
```

### 6.3.2 管道与批量操作

```python
# 管道与批量操作优化
class PipelineOptimizer:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def benchmark_batch_operations(self, batch_sizes=[10, 50, 100, 500]):
        """测试不同批量大小的性能"""
        results = []
        total_operations = 10000
        
        for batch_size in batch_sizes:
            self.redis.flushdb()
            
            start_time = time.time()
            
            # 使用管道进行批量操作
            pipeline = self.redis.pipeline()
            
            for i in range(total_operations):
                pipeline.set(f'key_{i}', f'value_{i}')
                
                if (i + 1) % batch_size == 0:
                    pipeline.execute()
            
            # 执行剩余操作
            if total_operations % batch_size != 0:
                pipeline.execute()
            
            total_time = time.time() - start_time
            
            results.append({
                'batch_size': batch_size,
                'total_operations': total_operations,
                'total_time': round(total_time, 3),
                'throughput_ops_per_sec': round(total_operations / total_time, 2)
            })
        
        return results
    
    def optimize_batch_size(self):
        """优化批量操作大小"""
        # 测试不同批量大小
        batch_results = self.benchmark_batch_operations()
        
        # 找到最佳批量大小
        best_batch = max(batch_results, key=lambda x: x['throughput_ops_per_sec'])
        
        # 推荐配置
        recommendations = {
            'optimal_batch_size': best_batch['batch_size'],
            'expected_throughput': best_batch['throughput_ops_per_sec'],
            'considerations': [
                '批量大小应避免过大，以免阻塞Redis过久',
                '对于网络延迟较高的环境，可以适当增大批量大小',
                '监控Redis内存使用，避免大批量操作导致内存压力'
            ]
        }
        
        return {
            'batch_test_results': batch_results,
            'recommendations': recommendations
        }

# 使用示例
pipeline_optimizer = PipelineOptimizer(r)

# 测试批量操作性能
batch_results = pipeline_optimizer.benchmark_batch_operations()
print("批量操作性能测试:")
for result in batch_results:
    print(f"批量大小 {result['batch_size']}: {result['throughput_ops_per_sec']} ops/sec")

# 获取优化建议
batch_advice = pipeline_optimizer.optimize_batch_size()
print("批量操作优化建议:")
print(json.dumps(batch_advice, indent=2, ensure_ascii=False))
```

## 6.4 监控与告警

### 6.4.1 实时监控系统

```python
# Redis实时监控系统
import time
import logging
from datetime import datetime

class RedisMonitor:
    def __init__(self, redis_client, check_interval=60):
        self.redis = redis_client
        self.check_interval = check_interval
        self.metrics_history = []
        self.max_history_size = 1000
    
    def collect_metrics(self):
        """收集Redis指标"""
        timestamp = datetime.now()
        
        try:
            # 基础指标
            info = self.redis.info()
            
            metrics = {
                'timestamp': timestamp.isoformat(),
                'memory': {
                    'used_memory': int(info.get('used_memory', 0)),
                    'used_memory_rss': int(info.get('used_memory_rss', 0)),
                    'mem_fragmentation_ratio': float(info.get('mem_fragmentation_ratio', 0))
                },
                'cpu': {
                    'used_cpu_sys': float(info.get('used_cpu_sys', 0)),
                    'used_cpu_user': float(info.get('used_cpu_user', 0))
                },
                'stats': {
                    'connected_clients': int(info.get('connected_clients', 0)),
                    'blocked_clients': int(info.get('blocked_clients', 0)),
                    'instantaneous_ops_per_sec': int(info.get('instantaneous_ops_per_sec', 0)),
                    'keyspace_hits': int(info.get('keyspace_hits', 0)),
                    'keyspace_misses': int(info.get('keyspace_misses', 0))
                },
                'persistence': {
                    'rdb_last_save_time': int(info.get('rdb_last_save_time', 0)),
                    'aof_enabled': int(info.get('aof_enabled', 0))
                }
            }
            
            # 计算命中率
            hits = metrics['stats']['keyspace_hits']
            misses = metrics['stats']['keyspace_misses']
            total = hits + misses
            
            metrics['stats']['hit_rate'] = round(hits / total * 100, 2) if total > 0 else 0
            
            # 保存到历史记录
            self.metrics_history.append(metrics)
            
            # 限制历史记录大小
            if len(self.metrics_history) > self.max_history_size:
                self.metrics_history.pop(0)
            
            return metrics
            
        except Exception as e:
            logging.error(f"收集指标失败: {e}")
            return None
    
    def check_alerts(self, metrics):
        """检查告警条件"""
        alerts = []
        
        if not metrics:
            return [{'level': 'ERROR', 'message': '无法获取监控指标'}]
        
        # 内存告警
        if metrics['memory']['mem_fragmentation_ratio'] > 1.5:
            alerts.append({
                'level': 'WARNING',
                'metric': 'memory_fragmentation',
                'message': f'内存碎片率过高: {metrics["memory"]["mem_fragmentation_ratio"]:.2f}',
                'value': metrics['memory']['mem_fragmentation_ratio']
            })
        
        # 客户端连接告警
        if metrics['stats']['connected_clients'] > 1000:
            alerts.append({
                'level': 'WARNING',
                'metric': 'connected_clients',
                'message': f'客户端连接数过多: {metrics["stats"]["connected_clients"]}',
                'value': metrics['stats']['connected_clients']
            })
        
        # 命中率告警
        if metrics['stats']['hit_rate'] < 80:
            alerts.append({
                'level': 'WARNING',
                'metric': 'hit_rate',
                'message': f'缓存命中率过低: {metrics["stats"]["hit_rate"]}%',
                'value': metrics['stats']['hit_rate']
            })
        
        return alerts
    
    def generate_report(self, hours=24):
        """生成监控报告"""
        if not self.metrics_history:
            return {'error': '没有可用的监控数据'}
        
        # 过滤指定时间范围内的数据
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        recent_metrics = [
            m for m in self.metrics_history 
            if datetime.fromisoformat(m['timestamp']).timestamp() > cutoff_time
        ]
        
        if not recent_metrics:
            return {'error': '指定时间内没有数据'}
        
        # 计算统计信息
        memory_usage = [m['memory']['used_memory'] for m in recent_metrics]
        hit_rates = [m['stats']['hit_rate'] for m in recent_metrics]
        ops_per_sec = [m['stats']['instantaneous_ops_per_sec'] for m in recent_metrics]
        
        report = {
            'report_period_hours': hours,
            'data_points': len(recent_metrics),
            'memory': {
                'avg_usage_mb': round(statistics.mean(memory_usage) / 1024 / 1024, 2),
                'max_usage_mb': round(max(memory_usage) / 1024 / 1024, 2),
                'min_usage_mb': round(min(memory_usage) / 1024 / 1024, 2)
            },
            'performance': {
                'avg_hit_rate': round(statistics.mean(hit_rates), 2),
                'avg_ops_per_sec': round(statistics.mean(ops_per_sec), 2),
                'max_ops_per_sec': max(ops_per_sec)
            },
            'trends': self._analyze_trends(recent_metrics)
        }
        
        return report
    
    def _analyze_trends(self, metrics):
        """分析趋势"""
        if len(metrics) < 2:
            return {'insufficient_data': True}
        
        # 简单的趋势分析
        first = metrics[0]
        last = metrics[-1]
        
        memory_change = last['memory']['used_memory'] - first['memory']['used_memory']
        hit_rate_change = last['stats']['hit_rate'] - first['stats']['hit_rate']
        
        return {
            'memory_trend': 'increasing' if memory_change > 0 else 'decreasing',
            'memory_change_mb': round(abs(memory_change) / 1024 / 1024, 2),
            'hit_rate_trend': 'improving' if hit_rate_change > 0 else 'declining',
            'hit_rate_change': round(abs(hit_rate_change), 2)
        }
    
    def start_monitoring(self):
        """开始监控"""
        import threading
        
        def monitor_loop():
            while True:
                try:
                    metrics = self.collect_metrics()
                    alerts = self.check_alerts(metrics)
                    
                    # 处理告警
                    for alert in alerts:
                        if alert['level'] == 'ERROR':
                            logging.error(f"ALERT: {alert['message']}")
                        elif alert['level'] == 'WARNING':
                            logging.warning(f"ALERT: {alert['message']}")
                    
                    time.sleep(self.check_interval)
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logging.error(f"监控循环错误: {e}")
                    time.sleep(self.check_interval)
        
        # 在后台线程中运行监控
        monitor_thread = threading.Thread(target=monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        return monitor_thread

# 使用示例
monitor = RedisMonitor(r, check_interval=30)

# 开始监控
# monitor_thread = monitor.start_monitoring()

# 生成报告
report = monitor.generate_report(1)  # 最近1小时的报告
print("监控报告:")
print(json.dumps(report, indent=2, ensure_ascii=False))
```

### 6.4.2 集成外部监控系统

```python
# 集成Prometheus监控
from prometheus_client import start_http_server, Gauge, Counter

class PrometheusRedisExporter:
    def __init__(self, redis_client, port=8000):
        self.redis = redis_client
        self.port = port
        
        # 定义指标
        self.memory_usage = Gauge('redis_memory_usage_bytes', 'Redis内存使用量')
        self.connected_clients = Gauge('redis_connected_clients', '连接的客户端数量')
        self.ops_per_sec = Gauge('redis_operations_per_second', '每秒操作数')
        self.hit_rate = Gauge('redis_cache_hit_rate', '缓存命中率')
        self.command_errors = Counter('redis_command_errors_total', '命令错误总数')
    
    def update_metrics(self):
        """更新指标"""
        try:
            info = self.redis.info()
            
            # 更新指标
            self.memory_usage.set(info.get('used_memory', 0))
            self.connected_clients.set(info.get('connected_clients', 0))
            self.ops_per_sec.set(info.get('instantaneous_ops_per_sec', 0))
            
            # 计算命中率
            hits = info.get('keyspace_hits', 0)
            misses = info.get('keyspace_misses', 0)
            total = hits + misses
            
            hit_rate = (hits / total * 100) if total > 0 else 0
            self.hit_rate.set(hit_rate)
            
        except Exception as e:
            self.command_errors.inc()
            logging.error(f"更新指标失败: {e}")
    
    def start_exporter(self):
        """启动exporter"""
        # 启动HTTP服务器
        start_http_server(self.port)
        logging.info(f"Prometheus exporter started on port {self.port}")
        
        # 定期更新指标
        import threading
        
        def update_loop():
            while True:
                self.update_metrics()
                time.sleep(15)  # 每15秒更新一次
        
        update_thread = threading.Thread(target=update_loop)
        update_thread.daemon = True
        update_thread.start()
        
        return update_thread

# 使用示例（需要安装prometheus_client）
# exporter = PrometheusRedisExporter(r)
# exporter.start_exporter()
```

## 总结

本章深入探讨了Redis性能优化和监控的各个方面。通过学习本章，您应该能够：

1. 识别和分析Redis性能瓶颈
2. 实施内存优化策略
3. 优化数据结构和存储方式
4. 配置高效的连接池和网络参数
5. 建立全面的监控和告警系统
6. 集成外部监控工具

性能优化和监控是确保Redis在生产环境中稳定高效运行的关键。在下一章中，我们将学习Redis的实际应用场景和最佳实践，帮助您将所学知识应用到真实项目中。