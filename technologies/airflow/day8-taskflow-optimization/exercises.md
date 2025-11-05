# Day 8: 任务流优化 - 实践练习

## 概述

本练习将帮助你掌握Airflow任务流优化的核心技能，包括性能调优、并发控制、资源管理和监控体系建设。通过实际案例和动手实践，你将学会如何诊断和解决性能问题。

## 练习目标

完成本练习后，你将能够：
- ✅ 识别和诊断Airflow性能瓶颈
- ✅ 实施有效的性能优化策略
- ✅ 配置合理的并发控制机制
- ✅ 建立完善的监控和告警体系
- ✅ 处理生产环境中的性能问题

---

## 练习1：性能瓶颈诊断 🔍

### 目标
学会使用各种工具和技术诊断Airflow性能瓶颈

### 场景
你的团队发现某个关键DAG的执行时间从原来的30分钟增加到了2小时，需要找出性能瓶颈并进行优化。

### 任务

#### 1.1 创建诊断DAG
```python
def create_diagnostic_dag():
    """创建用于性能诊断的DAG"""
    # TODO: 创建一个包含以下功能的诊断DAG：
    # 1. 系统资源监控（CPU、内存、磁盘I/O）
    # 2. 数据库连接状态检查
    # 3. 任务执行时间统计
    # 4. 内存使用监控
    # 5. 网络延迟测试
    pass

# 诊断任务实现
def system_resource_monitor(**context):
    """系统资源监控"""
    # TODO: 实现系统资源监控
    # - 获取CPU使用率
    # - 获取内存使用情况
    # - 获取磁盘I/O统计
    # - 获取网络I/O统计
    pass

def database_performance_check(**context):
    """数据库性能检查"""
    # TODO: 实现数据库性能检查
    # - 测试数据库连接时间
    # - 执行简单的查询性能测试
    # - 检查数据库连接池状态
    # - 监控数据库锁等待情况
    pass

def task_execution_profiler(**context):
    """任务执行分析器"""
    # TODO: 实现任务执行分析
    # - 记录任务开始和结束时间
    # - 监控内存使用变化
    # - 跟踪函数调用耗时
    # - 生成性能报告
    pass
```

#### 1.2 性能数据收集
```python
def collect_performance_metrics():
    """收集性能指标"""
    # TODO: 实现性能指标收集
    # 1. 收集Airflow内部指标
    # 2. 收集系统级指标
    # 3. 收集应用级指标
    # 4. 存储到时间序列数据库
    
    metrics = {
        'timestamp': datetime.now(),
        'cpu_usage': None,  # 需要实现
        'memory_usage': None,  # 需要实现
        'disk_io': None,  # 需要实现
        'network_io': None,  # 需要实现
        'database_connections': None,  # 需要实现
        'airflow_queue_size': None,  # 需要实现
        'task_execution_times': [],  # 需要实现
    }
    
    return metrics

def analyze_performance_trends():
    """分析性能趋势"""
    # TODO: 分析历史性能数据
    # 1. 计算性能指标变化趋势
    # 2. 识别性能退化点
    # 3. 生成性能报告
    # 4. 提供优化建议
    pass
```

#### 1.3 性能诊断报告
```python
def generate_diagnostic_report():
    """生成性能诊断报告"""
    # TODO: 生成综合性能诊断报告
    # 包含以下内容：
    # 1. 系统资源使用情况
    # 2. 数据库性能分析
    # 3. 任务执行时间分析
    # 4. 内存使用模式
    # 5. 网络延迟分析
    # 6. 优化建议
    
    report = {
        'diagnostic_timestamp': datetime.now(),
        'system_status': {},
        'database_status': {},
        'airflow_status': {},
        'performance_bottlenecks': [],
        'optimization_recommendations': [],
        'severity_level': 'low',  # low, medium, high, critical
    }
    
    return report
```

### 验证标准
- ✅ 能够正确收集系统资源指标
- ✅ 能够识别数据库性能问题
- ✅ 能够分析任务执行时间趋势
- ✅ 能够生成详细的诊断报告
- ✅ 能够提供具体的优化建议

---

## 练习2：性能优化实战 ⚡

### 目标
实施具体的性能优化策略，提升DAG执行效率

### 场景
基于练习1的诊断结果，你需要对现有的数据处理DAG进行性能优化

### 任务

#### 2.1 批量处理优化
```python
def optimize_batch_processing():
    """优化批量处理"""
    # TODO: 实现批量处理优化
    # 1. 动态调整批次大小
    # 2. 实现内存感知的批处理
    # 3. 添加进度监控
    # 4. 实现错误恢复机制
    
    batch_config = {
        'initial_batch_size': 1000,
        'max_batch_size': 10000,
        'min_batch_size': 100,
        'memory_threshold': 0.8,  # 80%内存使用率
        'progress_interval': 1000,  # 每1000条记录报告进度
    }
    
    return batch_config

def adaptive_batch_processor(data_source, batch_config):
    """自适应批处理器"""
    # TODO: 实现自适应批处理
    # - 根据系统资源动态调整批次大小
    # - 监控内存使用情况
    # - 实时调整处理策略
    # - 记录性能指标
    
    current_batch_size = batch_config['initial_batch_size']
    processed_count = 0
    
    while True:
        # 获取当前批次数据
        batch = []
        try:
            for _ in range(current_batch_size):
                item = next(data_source)
                batch.append(item)
        except StopIteration:
            break
        
        if not batch:
            break
        
        # 处理批次
        process_batch(batch)
        
        # 更新计数
        processed_count += len(batch)
        
        # 动态调整批次大小
        current_batch_size = adjust_batch_size(
            current_batch_size, 
            batch_config, 
            processed_count
        )
        
        # 报告进度
        if processed_count % batch_config['progress_interval'] == 0:
            report_progress(processed_count)
    
    return processed_count

def adjust_batch_size(current_size, config, processed_count):
    """调整批次大小"""
    # TODO: 根据性能指标调整批次大小
    # - 内存使用率高时减小批次
    # - 处理速度快时增大批次
    # - 错误率高时减小批次
    
    memory_usage = get_memory_usage()
    processing_speed = get_processing_speed()
    error_rate = get_error_rate()
    
    if memory_usage > config['memory_threshold']:
        return max(config['min_batch_size'], current_size // 2)
    elif processing_speed > 1000 and error_rate < 0.01:
        return min(config['max_batch_size'], current_size * 2)
    else:
        return current_size
```

#### 2.2 并发处理优化
```python
def optimize_concurrent_processing():
    """优化并发处理"""
    # TODO: 实现并发处理优化
    # 1. 智能并发度控制
    # 2. 资源池管理
    # 3. 任务优先级调度
    # 4. 并发安全机制
    
    concurrency_config = {
        'max_workers': 8,
        'min_workers': 2,
        'worker_scaling_threshold': 0.8,
        'task_queue_size': 1000,
        'resource_pool_size': 4,
        'priority_levels': 3,
    }
    
    return concurrency_config

class SmartConcurrentProcessor:
    """智能并发处理器"""
    
    def __init__(self, config):
        self.config = config
        self.current_workers = config['min_workers']
        self.task_queue = queue.Queue(maxsize=config['task_queue_size'])
        self.resource_pool = self._create_resource_pool()
        self.executor = None
    
    def process_concurrently(self, tasks):
        """并发处理任务"""
        # TODO: 实现智能并发处理
        # - 根据系统负载调整并发度
        # - 管理资源池
        # - 处理任务优先级
        # - 监控执行状态
        
        # 动态调整并发度
        optimal_workers = self._calculate_optimal_workers(tasks)
        self._adjust_concurrency(optimal_workers)
        
        # 提交任务
        futures = []
        for task in tasks:
            future = self.executor.submit(self._process_task_with_resource, task)
            futures.append(future)
        
        # 收集结果
        results = []
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result(timeout=300)
                results.append(result)
            except Exception as e:
                logging.error(f"任务执行失败: {e}")
                results.append({'error': str(e)})
        
        return results
    
    def _calculate_optimal_workers(self, tasks):
        """计算最优工作线程数"""
        # TODO: 根据任务特性和系统资源计算最优并发度
        # - 考虑任务类型（CPU/IO密集型）
        # - 考虑系统资源可用性
        # - 考虑历史性能数据
        
        task_complexity = self._estimate_task_complexity(tasks)
        system_load = self._get_system_load()
        available_memory = self._get_available_memory()
        
        # 基于可用内存的计算
        memory_based_workers = available_memory // 100  # 假设每个任务需要100MB
        
        # 基于系统负载的计算
        if system_load < 0.3:
            load_based_workers = self.config['max_workers']
        elif system_load < 0.7:
            load_based_workers = self.config['max_workers'] // 2
        else:
            load_based_workers = self.config['min_workers']
        
        # 综合考虑
        optimal_workers = min(memory_based_workers, load_based_workers)
        
        return max(self.config['min_workers'], optimal_workers)
    
    def _process_task_with_resource(self, task):
        """使用资源处理任务"""
        # TODO: 实现资源感知的任务处理
        # - 从资源池获取资源
        # - 执行任务
        # - 释放资源
        # - 记录性能指标
        
        with self.resource_pool.get_resource() as resource:
            start_time = time.time()
            
            try:
                result = self._execute_task(task, resource)
                
                execution_time = time.time() - start_time
                self._record_performance_metrics(task, execution_time, 'success')
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                self._record_performance_metrics(task, execution_time, 'failed')
                raise
```

#### 2.3 内存优化
```python
def optimize_memory_usage():
    """优化内存使用"""
    # TODO: 实现内存优化
    # 1. 内存监控和预警
    # 2. 垃圾回收优化
    # 3. 数据流处理
    # 4. 内存池管理
    
    memory_config = {
        'memory_threshold': 0.8,
        'gc_threshold': (700, 10, 10),  # 垃圾回收阈值
        'max_object_size': 100 * 1024 * 1024,  # 100MB
        'memory_pool_size': 50 * 1024 * 1024,  # 50MB
        'cleanup_interval': 1000,  # 每1000个对象清理一次
    }
    
    return memory_config

class MemoryOptimizer:
    """内存优化器"""
    
    def __init__(self, config):
        self.config = config
        self.memory_monitor = MemoryMonitor()
        self.object_pool = ObjectPool(max_size=config['memory_pool_size'])
        
        # 设置垃圾回收参数
        gc.set_threshold(*config['gc_threshold'])
    
    def process_with_memory_control(self, data_source):
        """在内存控制下处理数据"""
        # TODO: 实现内存控制的数据处理
        # - 监控内存使用
        # - 动态调整处理策略
        # - 及时清理无用对象
        # - 优化数据结构设计
        
        processed_count = 0
        cleanup_counter = 0
        
        for data_chunk in self._chunked_iterator(data_source):
            # 检查内存使用
            memory_usage = self.memory_monitor.get_memory_usage()
            
            if memory_usage > self.config['memory_threshold']:
                # 内存使用过高，进行清理
                self._emergency_cleanup()
                
                if self.memory_monitor.get_memory_usage() > self.config['memory_threshold']:
                    # 仍然过高，暂停处理
                    logging.warning("内存使用过高，暂停处理")
                    time.sleep(10)
                    continue
            
            # 处理数据块
            processed_data = self._process_chunk(data_chunk)
            
            # 及时释放大对象
            del data_chunk
            
            # 定期清理
            cleanup_counter += len(processed_data)
            if cleanup_counter >= self.config['cleanup_interval']:
                self._periodic_cleanup()
                cleanup_counter = 0
            
            processed_count += len(processed_data)
            
            yield processed_data
    
    def _chunked_iterator(self, data_source, chunk_size=1000):
        """分块迭代器"""
        # TODO: 实现内存高效的分块迭代
        chunk = []
        
        for item in data_source:
            chunk.append(item)
            
            if len(chunk) >= chunk_size:
                yield chunk
                chunk = []
        
        if chunk:
            yield chunk
    
    def _emergency_cleanup(self):
        """紧急内存清理"""
        # 强制垃圾回收
        gc.collect()
        
        # 清理对象池
        self.object_pool.clear()
        
        # 清理缓存
        if hasattr(self, 'cache'):
            self.cache.clear()
    
    def _periodic_cleanup(self):
        """定期清理"""
        # 清理循环引用
        gc.collect(0)  # 只清理最年轻的一代
        
        # 清理对象池中的过期对象
        self.object_pool.cleanup()
```

### 验证标准
- ✅ 批量处理性能提升30%以上
- ✅ 内存使用控制在合理范围内
- ✅ 并发处理效率提升显著
- ✅ 错误恢复机制正常工作
- ✅ 性能指标持续监控

---

## 练习3：并发控制和资源管理 🔄

### 目标
实现高效的并发控制和资源管理机制

### 场景
你的Airflow实例需要同时处理多个不同类型的任务，需要合理分配系统资源

### 任务

#### 3.1 资源池管理
```python
def create_resource_management_system():
    """创建资源管理系统"""
    # TODO: 实现资源管理系统
    # 1. 多层级资源池
    # 2. 动态资源分配
    # 3. 资源使用监控
    # 4. 资源回收机制
    
    resource_pools = {
        'cpu_intensive': {
            'max_slots': 2,
            'priority': 'high',
            'timeout': 3600,
            'description': 'CPU密集型任务池'
        },
        'io_intensive': {
            'max_slots': 4,
            'priority': 'medium',
            'timeout': 1800,
            'description': 'IO密集型任务池'
        },
        'memory_intensive': {
            'max_slots': 1,
            'priority': 'high',
            'timeout': 7200,
            'description': '内存密集型任务池'
        },
        'database': {
            'max_slots': 3,
            'priority': 'high',
            'timeout': 900,
            'description': '数据库连接池'
        },
        'api_calls': {
            'max_slots': 5,
            'priority': 'low',
            'timeout': 300,
            'description': 'API调用池'
        }
    }
    
    return resource_pools

class AdvancedResourcePool:
    """高级资源池"""
    
    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.available_slots = config['max_slots']
        self.waiting_queue = queue.PriorityQueue()
        self.active_tasks = {}
        self.resource_usage_history = []
        
        # 监控指标
        self.metrics = {
            'total_requests': 0,
            'successful_allocations': 0,
            'failed_allocations': 0,
            'average_wait_time': 0,
            'peak_usage': 0
        }
    
    def acquire_resource(self, task_id, priority=5, timeout=300):
        """获取资源"""
        # TODO: 实现资源获取逻辑
        # - 优先级管理
        # - 超时控制
        # - 等待队列管理
        # - 使用统计
        
        self.metrics['total_requests'] += 1
        
        # 检查是否有可用资源
        if self.available_slots > 0:
            return self._allocate_resource(task_id)
        
        # 没有可用资源，加入等待队列
        wait_start = time.time()
        wait_item = {
            'task_id': task_id,
            'priority': priority,
            'timeout': timeout,
            'wait_start': wait_start,
            'event': threading.Event()
        }
        
        self.waiting_queue.put((priority, wait_item))
        
        # 等待资源释放或超时
        if wait_item['event'].wait(timeout):
            # 成功获取资源
            self.metrics['successful_allocations'] += 1
            wait_time = time.time() - wait_start
            self._update_wait_time_metrics(wait_time)
            return True
        else:
            # 超时
            self.metrics['failed_allocations'] += 1
            return False
    
    def release_resource(self, task_id):
        """释放资源"""
        # TODO: 实现资源释放逻辑
        # - 释放资源槽位
        # - 通知等待队列
        # - 更新使用统计
        # - 记录使用历史
        
        if task_id in self.active_tasks:
            del self.active_tasks[task_id]
            self.available_slots += 1
            
            # 记录释放时间
            self._record_resource_usage(task_id, 'released')
            
            # 通知等待队列中的下一个任务
            self._notify_next_waiting_task()
            
            return True
        
        return False
    
    def get_resource_statistics(self):
        """获取资源使用统计"""
        # TODO: 生成资源使用统计报告
        stats = {
            'pool_name': self.name,
            'available_slots': self.available_slots,
            'max_slots': self.config['max_slots'],
            'waiting_tasks': self.waiting_queue.qsize(),
            'active_tasks': len(self.active_tasks),
            'metrics': self.metrics.copy(),
            'usage_efficiency': self._calculate_usage_efficiency(),
            'recommendations': self._generate_recommendations()
        }
        
        return stats
```

#### 3.2 并发安全机制
```python
def implement_concurrent_safety():
    """实现并发安全机制"""
    # TODO: 实现并发安全机制
    # 1. 线程安全的数据结构
    # 2. 分布式锁机制
    # 3. 事务性操作
    # 4. 冲突检测和解决
    
    safety_mechanisms = {
        'thread_safety': {
            'locks': {},
            'atomic_operations': {},
            'thread_local_storage': {}
        },
        'distributed_locking': {
            'redis_locks': {},
            'zookeeper_locks': {},
            'database_locks': {}
        },
        'transaction_support': {
            'database_transactions': {},
            'saga_pattern': {},
            'compensation_mechanisms': {}
        }
    }
    
    return safety_mechanisms

class DistributedLockManager:
    """分布式锁管理器"""
    
    def __init__(self, redis_client, default_timeout=30):
        self.redis = redis_client
        self.default_timeout = default_timeout
        self.active_locks = {}
        
        # 锁配置
        self.lock_config = {
            'retry_count': 3,
            'retry_delay': 0.1,
            'lock_timeout': default_timeout
        }
    
    def acquire_lock(self, lock_name, task_id, timeout=None):
        """获取分布式锁"""
        # TODO: 实现分布式锁获取
        # - 使用Redis SET NX EX命令
        # - 实现锁续期机制
        # - 处理锁竞争
        # - 防止死锁
        
        timeout = timeout or self.default_timeout
        lock_key = f"distributed_lock:{lock_name}"
        lock_value = f"{task_id}:{time.time()}"
        
        # 尝试获取锁
        for attempt in range(self.lock_config['retry_count']):
            try:
                # 使用SET NX EX原子操作
                result = self.redis.set(
                    lock_key, 
                    lock_value, 
                    nx=True, 
                    ex=timeout
                )
                
                if result:
                    # 成功获取锁
                    self.active_locks[lock_name] = {
                        'task_id': task_id,
                        'acquired_at': time.time(),
                        'timeout': timeout,
                        'lock_value': lock_value
                    }
                    
                    # 启动锁续期线程
                    self._start_lock_renewal(lock_name, lock_key, lock_value, timeout)
                    
                    return True
                
                else:
                    # 锁被占用，检查持有者
                    current_lock_value = self.redis.get(lock_key)
                    if current_lock_value:
                        current_task_id = current_lock_value.decode().split(':')[0]
                        logging.info(f"锁 {lock_name} 被任务 {current_task_id} 占用")
                    
            except Exception as e:
                logging.error(f"获取锁失败 (尝试 {attempt + 1}): {e}")
            
            # 等待后重试
            time.sleep(self.lock_config['retry_delay'] * (2 ** attempt))
        
        return False
    
    def release_lock(self, lock_name, task_id):
        """释放分布式锁"""
        # TODO: 实现分布式锁释放
        # - 验证锁持有者
        # - 安全释放锁
        # - 清理续期线程
        # - 记录释放日志
        
        lock_key = f"distributed_lock:{lock_name}"
        
        # 使用Lua脚本确保原子性
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        try:
            # 获取当前锁值
            current_lock_value = self.redis.get(lock_key)
            if not current_lock_value:
                logging.warning(f"锁 {lock_name} 不存在")
                return False
            
            current_task_id = current_lock_value.decode().split(':')[0]
            
            # 验证任务ID
            if current_task_id != task_id:
                logging.warning(f"任务 {task_id} 尝试释放不属于自己的锁 {lock_name}")
                return False
            
            # 执行Lua脚本释放锁
            result = self.redis.eval(lua_script, 1, lock_key, current_lock_value.decode())
            
            if result == 1:
                # 成功释放锁
                if lock_name in self.active_locks:
                    del self.active_locks[lock_name]
                
                logging.info(f"任务 {task_id} 成功释放锁 {lock_name}")
                return True
            else:
                logging.warning(f"释放锁 {lock_name} 失败")
                return False
                
        except Exception as e:
            logging.error(f"释放锁失败: {e}")
            return False
```

#### 3.3 任务调度优化
```python
def optimize_task_scheduling():
    """优化任务调度"""
    # TODO: 实现任务调度优化
    # 1. 智能任务分组
    # 2. 依赖关系优化
    # 3. 执行时间预测
    # 4. 资源冲突避免
    
    scheduling_strategies = {
        'priority_based': {
            'high_priority_weight': 10,
            'medium_priority_weight': 5,
            'low_priority_weight': 1,
            'starvation_prevention': True
        },
        'resource_based': {
            'cpu_aware_scheduling': True,
            'memory_aware_scheduling': True,
            'io_aware_scheduling': True,
            'network_aware_scheduling': True
        },
        'time_based': {
            'execution_time_prediction': True,
            'deadline_aware_scheduling': True,
            'historical_data_analysis': True
        }
    }
    
    return scheduling_strategies

class IntelligentTaskScheduler:
    """智能任务调度器"""
    
    def __init__(self, resource_manager, historical_data=None):
        self.resource_manager = resource_manager
        self.historical_data = historical_data or {}
        self.scheduling_queue = queue.PriorityQueue()
        self.execution_history = []
        
        # 调度配置
        self.config = {
            'max_concurrent_tasks': 10,
            'priority_weights': {'high': 10, 'medium': 5, 'low': 1},
            'resource_thresholds': {'cpu': 0.8, 'memory': 0.8, 'io': 0.7},
            'starvation_timeout': 3600  # 1小时
        }
    
    def schedule_tasks(self, tasks):
        """调度任务"""
        # TODO: 实现智能任务调度
        # - 分析任务特性
        # - 预测执行时间
        # - 评估资源需求
        # - 优化执行顺序
        
        # 分析任务
        task_analysis = self._analyze_tasks(tasks)
        
        # 生成调度计划
        schedule_plan = self._generate_schedule_plan(task_analysis)
        
        # 执行调度
        execution_results = self._execute_schedule(schedule_plan)
        
        # 更新历史数据
        self._update_historical_data(execution_results)
        
        return execution_results
    
    def _analyze_tasks(self, tasks):
        """分析任务特性"""
        # TODO: 实现任务分析
        # - 识别任务类型
        # - 评估资源需求
        # - 预测执行时间
        # - 确定优先级
        
        analyzed_tasks = []
        
        for task in tasks:
            analysis = {
                'task_id': task['id'],
                'task_type': self._identify_task_type(task),
                'estimated_duration': self._estimate_execution_time(task),
                'resource_requirements': self._assess_resource_needs(task),
                'priority': self._determine_priority(task),
                'dependencies': task.get('dependencies', []),
                'deadline': task.get('deadline')
            }
            
            analyzed_tasks.append(analysis)
        
        return analyzed_tasks
    
    def _estimate_execution_time(self, task):
        """预测执行时间"""
        # TODO: 基于历史数据预测执行时间
        # - 查找相似任务的历史数据
        # - 考虑当前系统负载
        # - 应用机器学习模型
        # - 提供置信区间
        
        task_type = task.get('type', 'unknown')
        task_params = task.get('parameters', {})
        
        # 查找历史数据
        historical_tasks = self.historical_data.get(task_type, [])
        
        if historical_tasks:
            # 基于历史数据预测
            similar_tasks = self._find_similar_tasks(task, historical_tasks)
            
            if similar_tasks:
                execution_times = [t['execution_time'] for t in similar_tasks]
                
                # 计算预测值
                predicted_time = statistics.mean(execution_times)
                confidence_interval = self._calculate_confidence_interval(execution_times)
                
                return {
                    'predicted_time': predicted_time,
                    'confidence_interval': confidence_interval,
                    'confidence_level': 0.95,
                    'method': 'historical_similarity'
                }
        
        # 没有历史数据，使用默认预测
        return {
            'predicted_time': 300,  # 默认5分钟
            'confidence_interval': (60, 900),  # 1分钟到15分钟
            'confidence_level': 0.5,
            'method': 'default_estimate'
        }
```

### 验证标准
- ✅ 资源池管理功能正常
- ✅ 并发安全机制有效
- ✅ 任务调度优化显著
- ✅ 系统资源利用率提升
- ✅ 任务执行效率改善

---

## 练习4：监控和告警系统 📊

### 目标
建立完善的监控和告警体系

### 场景
你需要为生产环境的Airflow建立全面的监控和告警系统

### 任务

#### 4.1 性能监控指标
```python
def define_performance_metrics():
    """定义性能监控指标"""
    # TODO: 定义全面的性能监控指标
    # 1. 系统级指标
    # 2. 应用级指标
    # 3. 业务级指标
    # 4. 自定义指标
    
    metrics = {
        'system_metrics': {
            'cpu_usage': {
                'type': 'gauge',
                'unit': 'percent',
                'thresholds': {'warning': 70, 'critical': 85},
                'description': 'CPU使用率'
            },
            'memory_usage': {
                'type': 'gauge',
                'unit': 'percent',
                'thresholds': {'warning': 80, 'critical': 95},
                'description': '内存使用率'
            },
            'disk_io': {
                'type': 'counter',
                'unit': 'bytes/second',
                'thresholds': {'warning': 100000000, 'critical': 200000000},
                'description': '磁盘I/O速率'
            }
        },
        'airflow_metrics': {
            'dag_execution_time': {
                'type': 'histogram',
                'unit': 'seconds',
                'buckets': [30, 60, 120, 300, 600, 1800, 3600],
                'description': 'DAG执行时间'
            },
            'task_queue_size': {
                'type': 'gauge',
                'unit': 'count',
                'thresholds': {'warning': 100, 'critical': 500},
                'description': '任务队列大小'
            },
            'scheduler_delay': {
                'type': 'gauge',
                'unit': 'seconds',
                'thresholds': {'warning': 10, 'critical': 60},
                'description': '调度延迟'
            }
        },
        'business_metrics': {
            'data_processing_throughput': {
                'type': 'counter',
                'unit': 'records/second',
                'description': '数据处理吞吐量'
            },
            'error_rate': {
                'type': 'gauge',
                'unit': 'percent',
                'thresholds': {'warning': 5, 'critical': 10},
                'description': '错误率'
            }
        }
    }
    
    return metrics

def create_metrics_collector():
    """创建指标收集器"""
    # TODO: 实现指标收集器
    # - 多源数据收集
    # - 实时数据处理
    # - 指标聚合计算
    # - 数据质量保证
    
    collector = MetricsCollector()
    
    # 系统指标收集器
    system_collector = SystemMetricsCollector()
    collector.register_collector('system', system_collector)
    
    # Airflow指标收集器
    airflow_collector = AirflowMetricsCollector()
    collector.register_collector('airflow', airflow_collector)
    
    # 业务指标收集器
    business_collector = BusinessMetricsCollector()
    collector.register_collector('business', business_collector)
    
    return collector

class RealTimeMetricsMonitor:
    """实时指标监控器"""
    
    def __init__(self, metrics_config):
        self.metrics_config = metrics_config
        self.metric_collectors = {}
        self.alert_rules = {}
        self.metrics_history = {}
        
        # 启动监控循环
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def _monitoring_loop(self):
        """监控循环"""
        while self.monitoring_active:
            try:
                # 收集所有指标
                current_metrics = self._collect_all_metrics()
                
                # 存储历史数据
                self._store_metrics_history(current_metrics)
                
                # 检查告警规则
                self._check_alert_rules(current_metrics)
                
                # 等待下一个周期
                time.sleep(30)  # 30秒监控周期
                
            except Exception as e:
                logging.error(f"监控循环错误: {e}")
                time.sleep(60)  # 错误时等待更长时间
    
    def _collect_all_metrics(self):
        """收集所有指标"""
        all_metrics = {}
        
        for collector_name, collector in self.metric_collectors.items():
            try:
                metrics = collector.collect_metrics()
                all_metrics[collector_name] = metrics
            except Exception as e:
                logging.error(f"收集指标失败 [{collector_name}]: {e}")
                all_metrics[collector_name] = {'error': str(e)}
        
        return all_metrics
    
    def register_collector(self, name, collector):
        """注册指标收集器"""
        self.metric_collectors[name] = collector
        logging.info(f"注册指标收集器: {name}")
```

#### 4.2 告警系统设计
```python
def design_alert_system():
    """设计告警系统"""
    # TODO: 设计完整的告警系统
    # 1. 告警规则引擎
    # 2. 多渠道通知
    # 3. 告警抑制和聚合
    # 4. 告警升级机制
    
    alert_system = {
        'rule_engine': {
            'threshold_alerts': {},
            'anomaly_detection': {},
            'trend_analysis': {},
            'composite_rules': {}
        },
        'notification_channels': {
            'email': {
                'enabled': True,
                'recipients': [],
                'severity_filter': ['warning', 'critical']
            },
            'slack': {
                'enabled': True,
                'webhooks': [],
                'severity_filter': ['critical']
            },
            'pagerduty': {
                'enabled': True,
                'service_key': '',
                'severity_filter': ['critical']
            }
        },
        'alert_management': {
            'deduplication': True,
            'aggregation': True,
            'escalation': True,
            'silencing': True
        }
    }
    
    return alert_system

class IntelligentAlertEngine:
    """智能告警引擎"""
    
    def __init__(self, config):
        self.config = config
        self.alert_rules = {}
        self.alert_history = []
        self.notification_manager = NotificationManager(config['notification_channels'])
        
        # 告警管理
        self.alert_deduplicator = AlertDeduplicator()
        self.alert_aggregator = AlertAggregator()
        self.alert_escalator = AlertEscalator()
    
    def evaluate_metrics(self, metrics):
        """评估指标并生成告警"""
        # TODO: 实现智能告警评估
        # - 阈值检查
        # - 异常检测
        # - 趋势分析
        # - 复合规则评估
        
        alerts_generated = []
        
        # 阈值告警
        threshold_alerts = self._evaluate_threshold_rules(metrics)
        alerts_generated.extend(threshold_alerts)
        
        # 异常检测告警
        anomaly_alerts = self._detect_anomalies(metrics)
        alerts_generated.extend(anomaly_alerts)
        
        # 趋势分析告警
        trend_alerts = self._analyze_trends(metrics)
        alerts_generated.extend(trend_alerts)
        
        # 处理生成的告警
        processed_alerts = self._process_alerts(alerts_generated)
        
        # 发送通知
        self._send_notifications(processed_alerts)
        
        return processed_alerts
    
    def _detect_anomalies(self, metrics):
        """检测异常"""
        # TODO: 实现异常检测算法
        # - 统计异常检测
        # - 机器学习异常检测
        # - 时间序列异常检测
        # - 多维度异常检测
        
        anomaly_alerts = []
        
        for metric_name, metric_value in self._flatten_metrics(metrics):
            # 简单统计异常检测
            if self._is_statistical_anomaly(metric_name, metric_value):
                alert = self._create_anomaly_alert(metric_name, metric_value, 'statistical')
                anomaly_alerts.append(alert)
            
            # 趋势异常检测
            if self._is_trend_anomaly(metric_name, metric_value):
                alert = self._create_anomaly_alert(metric_name, metric_value, 'trend')
                anomaly_alerts.append(alert)
        
        return anomaly_alerts
    
    def _is_statistical_anomaly(self, metric_name, current_value):
        """统计异常检测"""
        # 获取历史数据
        historical_data = self._get_historical_data(metric_name, hours=24)
        
        if len(historical_data) < 10:
            return False  # 数据不足
        
        # 计算统计参数
        mean = statistics.mean(historical_data)
        stdev = statistics.stdev(historical_data)
        
        # 3-sigma规则
        if stdev == 0:
            return False
        
        z_score = abs(current_value - mean) / stdev
        
        return z_score > 3  # 超过3个标准差
```

#### 4.3 监控仪表板
```python
def create_monitoring_dashboard():
    """创建监控仪表板"""
    # TODO: 创建监控仪表板
    # 1. 实时指标展示
    # 2. 历史趋势图表
    # 3. 告警状态显示
    # 4. 交互式数据探索
    
    dashboard = MonitoringDashboard()
    
    # 添加仪表板组件
    dashboard.add_widget('system_overview', SystemOverviewWidget())
    dashboard.add_widget('performance_trends', PerformanceTrendsWidget())
    dashboard.add_widget('alert_summary', AlertSummaryWidget())
    dashboard.add_widget('resource_usage', ResourceUsageWidget())
    dashboard.add_widget('task_execution', TaskExecutionWidget())
    
    return dashboard

class MonitoringDashboard:
    """监控仪表板"""
    
    def __init__(self):
        self.widgets = {}
        self.data_sources = {}
        self.refresh_interval = 30  # 30秒刷新间隔
        
        # 启动数据更新循环
        self.update_active = True
        self.update_thread = threading.Thread(target=self._update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()
    
    def add_widget(self, widget_id, widget):
        """添加仪表板组件"""
        self.widgets[widget_id] = widget
        logging.info(f"添加仪表板组件: {widget_id}")
    
    def register_data_source(self, source_id, data_source):
        """注册数据源"""
        self.data_sources[source_id] = data_source
        logging.info(f"注册数据源: {source_id}")
    
    def _update_loop(self):
        """数据更新循环"""
        while self.update_active:
            try:
                # 更新所有组件
                for widget_id, widget in self.widgets.items():
                    try:
                        # 获取最新数据
                        widget_data = self._get_widget_data(widget)
                        
                        # 更新组件
                        widget.update(widget_data)
                        
                    except Exception as e:
                        logging.error(f"更新组件失败 [{widget_id}]: {e}")
                
                # 等待下一次更新
                time.sleep(self.refresh_interval)
                
            except Exception as e:
                logging.error(f"仪表板更新循环错误: {e}")
                time.sleep(60)
```

### 验证标准
- ✅ 监控指标全面覆盖
- ✅ 告警规则准确有效
- ✅ 通知渠道正常工作
- ✅ 仪表板展示清晰
- ✅ 异常检测算法有效

---

## 综合练习：性能优化项目 🚀

### 目标
综合运用所学知识，完成一个完整的性能优化项目

### 项目描述
你负责优化一个大型电商数据处理平台的Airflow任务流，该平台每天处理数百万订单数据，当前存在以下问题：

1. **性能问题**：核心DAG执行时间超过4小时，影响数据时效性
2. **资源瓶颈**：内存使用经常超过90%，导致任务失败
3. **并发冲突**：多个DAG同时运行时出现资源竞争
4. **监控缺失**：缺乏有效的监控和告警机制

### 项目要求

#### 阶段1：现状分析和诊断
```python
def analyze_current_situation():
    """分析当前状况"""
    # TODO: 完成现状分析
    # 1. 收集性能基准数据
    # 2. 识别主要性能瓶颈
    # 3. 分析资源使用模式
    # 4. 评估当前架构问题
    
    analysis_result = {
        'performance_baseline': {},
        'bottleneck_analysis': {},
        'resource_usage_patterns': {},
        'architecture_issues': {},
        'optimization_opportunities': {}
    }
    
    return analysis_result
```

#### 阶段2：优化方案设计
```python
def design_optimization_solution(analysis_result):
    """设计优化方案"""
    # TODO: 设计综合优化方案
    # 1. 性能优化策略
    # 2. 资源管理方案
    # 3. 并发控制机制
    # 4. 监控告警体系
    
    optimization_plan = {
        'performance_optimization': {},
        'resource_management': {},
        'concurrency_control': {},
        'monitoring_system': {},
        'implementation_roadmap': {},
        'success_metrics': {}
    }
    
    return optimization_plan
```

#### 阶段3：实施和验证
```python
def implement_optimization(optimization_plan):
    """实施优化方案"""
    # TODO: 实施优化方案
    # 1. 代码重构和优化
    # 2. 资源配置调整
    # 3. 监控部署
    # 4. 性能测试
    
    implementation_result = {
        'code_optimizations': {},
        'resource_configurations': {},
        'monitoring_deployment': {},
        'performance_tests': {},
        'validation_results': {}
    }
    
    return implementation_result
```

#### 阶段4：效果评估和持续优化
```python
def evaluate_optimization_results(before_metrics, after_metrics):
    """评估优化效果"""
    # TODO: 评估优化效果
    # 1. 性能指标对比
    # 2. 资源效率分析
    # 3. 稳定性评估
    # 4. ROI计算
    
    evaluation_report = {
        'performance_improvement': {},
        'resource_efficiency': {},
        'stability_assessment': {},
        'roi_analysis': {},
        'lessons_learned': {},
        'future_improvements': {}
    }
    
    return evaluation_report
```

### 项目交付物

1. **性能诊断报告**：详细分析当前性能问题和根因
2. **优化方案文档**：包含具体的优化策略和实施计划
3. **优化代码实现**：重构后的高性能代码
4. **监控系统**：完整的监控和告警系统
5. **效果评估报告**：量化优化效果和ROI

### 成功标准

- ✅ 核心DAG执行时间从4小时缩短到1小时以内
- ✅ 内存使用率降低到70%以下
- ✅ 任务成功率提升到99.5%以上
- ✅ 建立完善的监控和告警体系
- ✅ 提供可量化的性能提升报告

### 项目时间线

- **第1周**：现状分析和诊断
- **第2周**：优化方案设计
- **第3-4周**：实施和验证
- **第5周**：效果评估和文档整理

---

## 总结

通过本日的实践练习，你将掌握：

1. **性能诊断技能**：能够使用各种工具诊断性能问题
2. **优化实施能力**：能够实施有效的性能优化策略
3. **并发控制技术**：掌握资源管理和并发控制机制
4. **监控体系建设**：建立完善的监控和告警系统
5. **项目管理能力**：能够规划和执行性能优化项目

这些技能将帮助你在生产环境中构建高性能、高可用的数据处理平台。