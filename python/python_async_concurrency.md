# Python异步编程与并发高级指南

## 1. asyncio事件循环机制深入理解

### 1.1 事件循环的核心工作原理

asyncio的核心是事件循环，它是一个单线程的调度器，负责管理和分发I/O事件和回调函数。

```python
import asyncio
import time
from functools import partial

# 自定义事件循环策略
async def event_loop_basics():
    """演示事件循环的基本机制"""
    
    # 获取当前事件循环
    loop = asyncio.get_running_loop()
    print(f"当前事件循环: {loop}")
    
    # 获取循环的时间
    current_time = loop.time()
    print(f"循环时间: {current_time:.4f}")
    
    # 安排一个回调函数
    def callback(msg, loop_time):
        print(f"回调函数执行: {msg}, 调用时间: {loop.time() - loop_time:.4f}s")
    
    loop.call_soon(callback, "Hello from callback", current_time)
    
    # 延迟调用回调函数
    loop.call_later(0.1, callback, "Delayed callback", current_time)
    
    # 安排一个在特定时间执行的回调
    specific_time = current_time + 0.2
    loop.call_at(specific_time, callback, "Scheduled callback", current_time)
    
    # 让协程等待一段时间，以便回调执行
    await asyncio.sleep(0.3)

async def event_loop_tasks():
    """演示事件循环中的任务管理"""
    
    loop = asyncio.get_running_loop()
    
    # 创建协程函数
    async def worker(name, duration):
        print(f"任务 {name} 开始")
        await asyncio.sleep(duration)
        print(f"任务 {name} 完成")
        return f"{name} 结果"
    
    # 创建任务但不立即运行
    task1 = loop.create_task(worker("Task 1", 0.1))
    task2 = loop.create_task(worker("Task 2", 0.2))
    
    # 获取所有任务
    tasks = asyncio.all_tasks(loop)
    print(f"当前循环中的任务数: {len(tasks)}")
    
    # 等待任务完成
    result1 = await task1
    result2 = await task2
    
    print(f"任务结果: {result1}, {result2}")

async def event_loop_policy():
    """演示事件循环策略"""
    
    # 默认事件循环策略
    policy = asyncio.get_event_loop_policy()
    print(f"默认事件循环策略: {policy}")
    
    # 设置不同的事件循环策略 (在某些平台上可用)
    # policy = asyncio.WindowsProactorEventLoopPolicy()  # Windows
    
    # 自定义事件循环策略可以用来控制循环的创建和生命周期

async def main():
    print("=== 事件循环核心机制演示 ===")
    await event_loop_basics()
    await asyncio.sleep(0.5)
    await event_loop_tasks()

# 运行事件循环示例
asyncio.run(main())
```

### 1.2 事件循环中的信号处理与资源管理

```python
import asyncio
import signal
import sys

class AsyncApplication:
    """使用asyncio构建的应用程序类，展示信号处理和资源管理"""
    
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.running = False
        self.shutdown_event = asyncio.Event()
    
    async def setup(self):
        """设置应用程序"""
        # 设置信号处理
        for sig in (signal.SIGINT, signal.SIGTERM):
            self.loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(self.shutdown(s)))
        
        print("应用程序设置完成，已注册信号处理")
    
    async def shutdown(self, signal):
        """优雅关闭应用程序"""
        print(f"\n接收到信号 {signal.name}，开始关闭程序...")
        self.running = False
        self.shutdown_event.set()
        
        # 执行清理工作
        print("正在清理资源...")
        await asyncio.sleep(0.1)  # 模拟清理工作
        
        # 停止事件循环
        self.loop.stop()
    
    async def worker(self, name, interval):
        """工作协程"""
        while self.running:
            print(f"工作线程 {name} 执行中...")
            await asyncio.sleep(interval)
    
    async def run(self):
        """运行应用程序"""
        await self.setup()
        self.running = True
        
        # 创建工作协程
        tasks = [
            asyncio.create_task(self.worker("Worker 1", 1)),
            asyncio.create_task(self.worker("Worker 2", 2))
        ]
        
        # 等待关闭信号
        try:
            await self.shutdown_event.wait()
        finally:
            # 取消所有任务
            for task in tasks:
                task.cancel()
            
            # 等待任务完成取消
            await asyncio.gather(*tasks, return_exceptions=True)
            print("所有任务已取消")
    
    def start(self):
        """启动应用程序"""
        self.loop.run_until_complete(self.run())
        self.loop.close()

# 运行应用程序 (在实际环境中运行)
# app = AsyncApplication()
# app.start()
```

## 2. async/await高级用法与协程优化

### 2.1 高级协程控制技术

```python
import asyncio
import random
import time
from typing import List, Tuple, Any

async def advanced_coroutine_control():
    """演示高级协程控制技术"""
    
    # 可取消的协程
    async def cancellable_task(name, duration):
        try:
            print(f"任务 {name} 开始，将运行 {duration}s")
            await asyncio.sleep(duration)
            print(f"任务 {name} 完成")
            return f"{name} 结果"
        except asyncio.CancelledError:
            print(f"任务 {name} 被取消")
            return f"{name} 已取消"
    
    # 创建一个长期运行的任务
    long_task = asyncio.create_task(cancellable_task("Long Task", 10))
    
    # 让它运行一段时间
    await asyncio.sleep(1)
    
    # 取消任务
    long_task.cancel()
    
    # 等待任务完成取消
    result = await long_task
    print(f"取消后任务结果: {result}")
    
    # 超时控制
    try:
        # 带超时的wait_for
        result = await asyncio.wait_for(cancellable_task("Timeout Task", 5), timeout=2)
        print(f"超时任务结果: {result}")
    except asyncio.TimeoutError:
        print("任务执行超时")
    
    # 任务调度和并发限制
    async def concurrent_limiter():
        """演示并发限制技术"""
        
        async def limited_worker(worker_id):
            print(f"工人 {worker_id} 开始工作")
            await asyncio.sleep(random.uniform(0.5, 1.5))
            print(f"工人 {worker_id} 完成工作")
            return f"工人 {worker_id} 的结果"
        
        # 创建信号量限制并发数
        semaphore = asyncio.Semaphore(3)  # 最多3个并发
        
        async def limited_call(worker_id):
            async with semaphore:
                return await limited_worker(worker_id)
        
        # 创建多个任务
        tasks = [limited_call(i) for i in range(10)]
        results = await asyncio.gather(*tasks)
        return results
    
    concurrent_results = await concurrent_limiter()
    print(f"\n并发限制任务结果数量: {len(concurrent_results)}")

async def advanced_await_patterns():
    """演示高级await模式"""
    
    # 嵌套协程调用
    async def fetch_data(url):
        """模拟数据获取"""
        await asyncio.sleep(random.uniform(0.1, 0.5))
        return f"来自 {url} 的数据"
    
    async def process_data(data):
        """模拟数据处理"""
        await asyncio.sleep(random.uniform(0.1, 0.3))
        return f"处理过的 {data}"
    
    async def nested_calls():
        """嵌套协程调用示例"""
        url = "https://example.com/api"
        raw_data = await fetch_data(url)
        processed_data = await process_data(raw_data)
        return processed_data
    
    result = await nested_calls()
    print(f"嵌套调用结果: {result}")
    
    # 异步上下文管理器
    class AsyncResource:
        """异步资源管理器示例"""
        
        async def __aenter__(self):
            print("资源获取中...")
            await asyncio.sleep(0.1)  # 模拟资源获取
            print("资源已获取")
            return self
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            print("资源释放中...")
            await asyncio.sleep(0.1)  # 模拟资源释放
            print("资源已释放")
            if exc_type:
                print(f"发生异常: {exc_val}")
        
        async def use(self):
            print("使用资源...")
            await asyncio.sleep(0.2)
            return "资源使用结果"
    
    # 使用异步上下文管理器
    async with AsyncResource() as resource:
        result = await resource.use()
        print(f"资源使用结果: {result}")
    
    # 动态创建和调度任务
    async def dynamic_task_creation():
        """动态任务创建"""
        
        async def worker(task_id):
            await asyncio.sleep(random.uniform(0.1, 0.3))
            return f"任务 {task_id} 完成"
        
        # 动态创建任务
        pending_tasks = set()
        results = []
        
        # 添加初始任务
        for i in range(5):
            task = asyncio.create_task(worker(i))
            pending_tasks.add(task)
        
        # 当有任务完成时，添加新任务
        while pending_tasks:
            done, pending_tasks = await asyncio.wait(
                pending_tasks, return_when=asyncio.FIRST_COMPLETED
            )
            
            for task in done:
                results.append(task.result())
                
                # 随机决定是否添加新任务
                if random.random() < 0.6 and len(pending_tasks) < 8:
                    new_id = max(results) if results else 0
                    new_id = int(str(new_id).split()[1]) + 1
                    new_task = asyncio.create_task(worker(new_id))
                    pending_tasks.add(new_task)
                    print(f"添加新任务: {new_id}")
        
        return results
    
    dynamic_results = await dynamic_task_creation()
    print(f"\n动态任务创建结果: {dynamic_results}")

async def advanced_async_generators():
    """演示高级异步生成器用法"""
    
    async def async_range(count):
        """异步范围生成器"""
        for i in range(count):
            await asyncio.sleep(0.1)  # 模拟异步操作
            yield i
    
    async def async_data_processor():
        """异步数据处理流水线"""
        
        # 数据生成
        async def data_source():
            for i in range(10):
                await asyncio.sleep(0.1)  # 模拟数据获取延迟
                yield {"id": i, "value": random.randint(1, 100)}
        
        # 数据过滤
        async def filter_even(data_stream):
            async for item in data_stream:
                await asyncio.sleep(0.05)  # 模拟处理延迟
                if item["value"] % 2 == 0:
                    yield item
        
        # 数据转换
        async def transform(data_stream):
            async for item in data_stream:
                await asyncio.sleep(0.05)  # 模拟处理延迟
                yield {"id": item["id"], "value": item["value"] * 2}
        
        # 组合处理流水线
        source = data_source()
        filtered = filter_even(source)
        transformed = transform(filtered)
        
        results = []
        async for item in transformed:
            results.append(item)
            print(f"处理结果: {item}")
        
        return results
    
    # 使用异步生成器
    print("\n异步生成器示例:")
    async for num in async_range(5):
        print(f"生成数字: {num}")
    
    # 使用异步数据处理流水线
    print("\n异步数据处理流水线:")
    pipeline_results = await async_data_processor()
    print(f"流水线处理结果: {pipeline_results}")

async def main():
    print("=== async/await高级用法 ===")
    await advanced_coroutine_control()
    await asyncio.sleep(0.5)
    await advanced_await_patterns()
    await asyncio.sleep(0.5)
    await advanced_async_generators()

asyncio.run(main())
```

### 2.2 协程池与任务调度策略

```python
import asyncio
import random
from typing import Callable, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor

class AsyncWorkerPool:
    """异步工作者池，支持协程和函数"""
    
    def __init__(self, max_workers: int = 10, use_threads: bool = False):
        self.max_workers = max_workers
        self.use_threads = use_threads
        self.semaphore = asyncio.Semaphore(max_workers)
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers) if use_threads else None
        self.tasks = set()
        self.results = []
    
    async def submit(self, func: Callable, *args, **kwargs):
        """提交任务到池中"""
        
        async def limited_execution():
            async with self.semaphore:
                if asyncio.iscoroutinefunction(func):
                    # 异步函数
                    return await func(*args, **kwargs)
                elif self.use_threads:
                    # 在线程池中运行同步函数
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(
                        self.thread_pool, 
                        lambda: func(*args, **kwargs)
                    )
                else:
                    # 直接运行同步函数（不推荐，可能阻塞事件循环）
                    return func(*args, **kwargs)
        
        task = asyncio.create_task(limited_execution())
        self.tasks.add(task)
        
        # 添加回调以处理任务完成
        task.add_done_callback(lambda t: self.tasks.discard(t))
        task.add_done_callback(lambda t: self._process_result(t))
        
        return task
    
    def _process_result(self, task):
        """处理完成的任务结果"""
        try:
            result = task.result()
            self.results.append(result)
        except Exception as e:
            self.results.append(e)
    
    async def wait_for_completion(self):
        """等待所有任务完成"""
        if self.tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def close(self):
        """关闭工作池"""
        await self.wait_for_completion()
        if self.thread_pool:
            self.thread_pool.shutdown(wait=True)
        self.tasks.clear()
        self.results = []

# 高级任务调度器
class AsyncTaskScheduler:
    """高级异步任务调度器"""
    
    def __init__(self):
        self.task_queue = asyncio.Queue()
        self.result_queue = asyncio.Queue()
        self.priority_queues = {
            'high': asyncio.PriorityQueue(),
            'normal': asyncio.Queue(),
            'low': asyncio.Queue()
        }
        self.running = False
        self.completed_tasks = 0
        self.failed_tasks = 0
    
    async def add_task(self, func: Callable, *args, priority='normal', **kwargs):
        """添加任务到调度器"""
        task_info = {
            'func': func,
            'args': args,
            'kwargs': kwargs,
            'priority': priority,
            'id': random.randint(1000, 9999)
        }
        
        if priority in self.priority_queues:
            if priority == 'high':
                # 优先级队列使用 (priority_number, task_id, task_info)
                await self.priority_queues['high'].put((1, task_info['id'], task_info))
            else:
                await self.priority_queues[priority].put(task_info)
        else:
            await self.task_queue.put(task_info)
        
        print(f"添加任务 {task_info['id']} (优先级: {priority})")
    
    async def worker(self, worker_id):
        """工作协程"""
        print(f"工作者 {worker_id} 启动")
        
        while self.running:
            # 尝试按优先级获取任务
            task_info = None
            
            # 高优先级任务
            if not self.priority_queues['high'].empty():
                _, _, task_info = await self.priority_queues['high'].get()
            # 普通优先级任务
            elif not self.priority_queues['normal'].empty():
                task_info = await self.priority_queues['normal'].get()
            # 低优先级任务
            elif not self.priority_queues['low'].empty():
                task_info = await self.priority_queues['low'].get()
            # 默认优先级任务
            elif not self.task_queue.empty():
                task_info = await self.task_queue.get()
            else:
                # 没有任务，短暂休眠
                await asyncio.sleep(0.1)
                continue
            
            if task_info and self.running:
                try:
                    task_id = task_info['id']
                    print(f"工作者 {worker_id} 开始处理任务 {task_id}")
                    
                    # 执行任务
                    if asyncio.iscoroutinefunction(task_info['func']):
                        result = await task_info['func'](*task_info['args'], **task_info['kwargs'])
                    else:
                        result = task_info['func'](*task_info['args'], **task_info['kwargs'])
                    
                    # 记录结果
                    await self.result_queue.put({
                        'task_id': task_id,
                        'status': 'completed',
                        'result': result,
                        'worker': worker_id
                    })
                    self.completed_tasks += 1
                    print(f"工作者 {worker_id} 完成任务 {task_id}")
                    
                except Exception as e:
                    # 记录错误
                    await self.result_queue.put({
                        'task_id': task_info['id'],
                        'status': 'failed',
                        'error': str(e),
                        'worker': worker_id
                    })
                    self.failed_tasks += 1
                    print(f"工作者 {worker_id} 任务 {task_info['id']} 失败: {e}")
    
    async def start(self, num_workers=3):
        """启动调度器"""
        self.running = True
        
        # 启动工作协程
        self.workers = [
            asyncio.create_task(self.worker(i)) 
            for i in range(num_workers)
        ]
        
        # 启动结果收集协程
        self.collector = asyncio.create_task(self.result_collector())
        
        print(f"任务调度器已启动，{num_workers} 个工作者")
    
    async def stop(self):
        """停止调度器"""
        print("停止任务调度器...")
        self.running = False
        
        # 等待所有工作协程完成
        await asyncio.gather(*self.workers, return_exceptions=True)
        
        # 停止结果收集器
        self.collector.cancel()
        
        print(f"调度器已停止，完成: {self.completed_tasks}，失败: {self.failed_tasks}")
    
    async def result_collector(self):
        """结果收集协程"""
        while self.running:
            try:
                result = await asyncio.wait_for(
                    self.result_queue.get(), 
                    timeout=0.5
                )
                print(f"收集到结果: {result}")
            except asyncio.TimeoutError:
                pass  # 超时，继续循环

async def demo_pools_and_schedulers():
    """演示协程池和任务调度器"""
    
    print("=== 协程池演示 ===")
    
    # 创建协程池
    pool = AsyncWorkerPool(max_workers=3)
    
    # 添加一些任务
    async def async_task(name, duration):
        await asyncio.sleep(duration)
        return f"异步任务 {name} 完成"
    
    def sync_task(name, duration):
        time.sleep(duration)
        return f"同步任务 {name} 完成"
    
    tasks = [
        pool.submit(async_task, "Task 1", 0.5),
        pool.submit(async_task, "Task 2", 0.3),
        pool.submit(sync_task, "Task 3", 0.4),
        pool.submit(sync_task, "Task 4", 0.2),
    ]
    
    # 等待所有任务完成
    await asyncio.gather(*tasks)
    
    # 关闭池
    await pool.close()
    
    print(f"池中任务结果: {pool.results}")
    
    print("\n=== 任务调度器演示 ===")
    
    # 创建调度器
    scheduler = AsyncTaskScheduler()
    
    # 启动调度器
    await scheduler.start(num_workers=2)
    
    # 添加不同优先级的任务
    await scheduler.add_task(async_task, "高优先级1", 0.2, priority='high')
    await scheduler.add_task(async_task, "高优先级2", 0.3, priority='high')
    await scheduler.add_task(async_task, "普通任务1", 0.4)
    await scheduler.add_task(async_task, "普通任务2", 0.2)
    await scheduler.add_task(async_task, "低优先级1", 0.5, priority='low')
    
    # 等待一段时间让任务执行
    await asyncio.sleep(2)
    
    # 添加更多任务
    await scheduler.add_task(async_task, "额外任务", 0.3)
    
    # 等待所有任务完成
    await asyncio.sleep(2)
    
    # 停止调度器
    await scheduler.stop()

async def main():
    await demo_pools_and_schedulers()

asyncio.run(main())
```

## 3. 异步I/O与网络编程

### 3.1 高性能异步TCP服务器

```python
import asyncio
import struct
import json
import time
from typing import Dict, Tuple, Optional, Callable

class AsyncTCPServer:
    """高性能异步TCP服务器"""
    
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.clients = {}  # 客户端连接管理
        self.message_handlers = {}  # 消息处理器
        self.running = False
        self._server = None
    
    async def start(self):
        """启动服务器"""
        self.running = True
        self._server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port
        )
        
        addr = self._server.sockets[0].getsockname()
        print(f"服务器启动，监听 {addr}")
        
        async with self._server:
            await self._server.serve_forever()
    
    async def stop(self):
        """停止服务器"""
        self.running = False
        
        # 关闭所有客户端连接
        for client_info in list(self.clients.values()):
            writer = client_info['writer']
            try:
                writer.close()
                await writer.wait_closed()
            except:
                pass
        
        # 关闭服务器
        if self._server:
            self._server.close()
            await self._server.wait_closed()
        
        print("服务器已停止")
    
    def register_handler(self, message_type: str, handler: Callable):
        """注册消息处理器"""
        self.message_handlers[message_type] = handler
        print(f"注册处理器: {message_type}")
    
    async def handle_client(self, reader, writer):
        """处理客户端连接"""
        addr = writer.get_extra_info('peername')
        client_id = f"{addr[0]}:{addr[1]}"
        
        print(f"新客户端连接: {client_id}")
        
        # 保存客户端信息
        self.clients[client_id] = {
            'reader': reader,
            'writer': writer,
            'addr': addr,
            'connected_at': time.time()
        }
        
        try:
            # 处理客户端消息
            await self.process_client_messages(client_id)
        except (asyncio.CancelledError, ConnectionResetError):
            pass
        finally:
            # 清理客户端连接
            await self.cleanup_client(client_id)
    
    async def process_client_messages(self, client_id: str):
        """处理客户端消息"""
        client_info = self.clients[client_id]
        reader = client_info['reader']
        
        while self.running:
            try:
                # 读取消息长度 (前4字节)
                length_data = await reader.readexactly(4)
                if not length_data:
                    break
                
                # 解析消息长度
                length = struct.unpack('!I', length_data)[0]
                
                # 读取消息内容
                message_data = await reader.readexactly(length)
                
                # 解析消息
                try:
                    message = json.loads(message_data.decode('utf-8'))
                    await self.handle_message(client_id, message)
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    print(f"无效消息格式: {e}")
                
            except asyncio.IncompleteReadError:
                break
            except Exception as e:
                print(f"处理消息时出错: {e}")
                break
    
    async def handle_message(self, client_id: str, message: Dict):
        """处理客户端消息"""
        msg_type = message.get('type')
        handler = self.message_handlers.get(msg_type)
        
        if handler:
            try:
                await handler(client_id, message)
            except Exception as e:
                print(f"处理消息 {msg_type} 时出错: {e}")
                await self.send_error(client_id, f"处理错误: {e}")
        else:
            print(f"未知消息类型: {msg_type}")
            await self.send_error(client_id, f"未知消息类型: {msg_type}")
    
    async def send_message(self, client_id: str, message: Dict):
        """向客户端发送消息"""
        if client_id not in self.clients:
            return False
        
        client_info = self.clients[client_id]
        writer = client_info['writer']
        
        try:
            # 序列化消息
            message_str = json.dumps(message)
            message_bytes = message_str.encode('utf-8')
            
            # 添加长度前缀
            length_data = struct.pack('!I', len(message_bytes))
            
            # 发送消息
            writer.write(length_data + message_bytes)
            await writer.drain()
            return True
        except Exception as e:
            print(f"发送消息失败: {e}")
            return False
    
    async def send_error(self, client_id: str, error_msg: str):
        """发送错误消息"""
        await self.send_message(client_id, {
            'type': 'error',
            'message': error_msg,
            'timestamp': time.time()
        })
    
    async def broadcast(self, message: Dict, exclude: Optional[str] = None):
        """广播消息给所有客户端"""
        for client_id in list(self.clients.keys()):
            if client_id != exclude:
                await self.send_message(client_id, message)
    
    async def cleanup_client(self, client_id: str):
        """清理客户端连接"""
        if client_id in self.clients:
            client_info = self.clients[client_id]
            writer = client_info['writer']
            
            try:
                writer.close()
                await writer.wait_closed()
            except:
                pass
            
            del self.clients[client_id]
            print(f"客户端 {client_id} 已断开连接")

# 演示服务器使用
async def demo_tcp_server():
    """演示TCP服务器"""
    
    # 创建服务器
    server = AsyncTCPServer(host='127.0.0.1', port=8888)
    
    # 注册消息处理器
    async def handle_ping(client_id, message):
        """处理ping消息"""
        await server.send_message(client_id, {
            'type': 'pong',
            'timestamp': time.time()
        })
    
    async def handle_echo(client_id, message):
        """处理echo消息"""
        text = message.get('text', '')
        await server.send_message(client_id, {
            'type': 'echo_response',
            'text': text,
            'timestamp': time.time()
        })
    
    async def handle_broadcast(client_id, message):
        """处理广播消息"""
        text = message.get('text', '')
        await server.broadcast({
            'type': 'broadcast_message',
            'text': text,
            'from': client_id,
            'timestamp': time.time()
        }, exclude=client_id)
    
    async def handle_get_clients(client_id, message):
        """处理获取客户端列表请求"""
        clients = list(server.clients.keys())
        await server.send_message(client_id, {
            'type': 'clients_list',
            'clients': clients,
            'timestamp': time.time()
        })
    
    # 注册处理器
    server.register_handler('ping', handle_ping)
    server.register_handler('echo', handle_echo)
    server.register_handler('broadcast', handle_broadcast)
    server.register_handler('get_clients', handle_get_clients)
    
    # 启动服务器
    server_task = asyncio.create_task(server.start())
    
    # 运行一段时间后停止
    try:
        await asyncio.sleep(30)  # 运行30秒
    except KeyboardInterrupt:
        pass
    finally:
        server.running = False
        server_task.cancel()
        await server.stop()

# 演示客户端
class AsyncTCPClient:
    """异步TCP客户端"""
    
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None
        self.connected = False
        self.response_handlers = {}
        self.message_id = 0
    
    async def connect(self):
        """连接到服务器"""
        try:
            self.reader, self.writer = await asyncio.open_connection(
                self.host, self.port
            )
            self.connected = True
            print(f"连接到服务器 {self.host}:{self.port}")
            
            # 启动消息处理任务
            self.message_task = asyncio.create_task(self.process_messages())
            
            return True
        except Exception as e:
            print(f"连接失败: {e}")
            return False
    
    async def disconnect(self):
        """断开连接"""
        self.connected = False
        
        if self.message_task:
            self.message_task.cancel()
            try:
                await self.message_task
            except asyncio.CancelledError:
                pass
        
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
        
        print("已断开连接")
    
    async def send_message(self, message: Dict, expect_response=True):
        """发送消息到服务器"""
        if not self.connected:
            return None
        
        # 添加消息ID
        if expect_response:
            self.message_id += 1
            message['id'] = self.message_id
            
            # 创建等待响应的Future
            response_future = asyncio.Future()
            self.response_handlers[self.message_id] = response_future
            
            # 序列化消息
            message_str = json.dumps(message)
            message_bytes = message_str.encode('utf-8')
            length_data = struct.pack('!I', len(message_bytes))
            
            # 发送消息
            self.writer.write(length_data + message_bytes)
            await self.writer.drain()
            
            # 等待响应
            try:
                response = await response_future
                return response
            except asyncio.TimeoutError:
                print(f"消息 {message['id']} 超时")
                if message['id'] in self.response_handlers:
                    del self.response_handlers[message['id']]
                return None
        else:
            # 不需要响应的消息
            message_str = json.dumps(message)
            message_bytes = message_str.encode('utf-8')
            length_data = struct.pack('!I', len(message_bytes))
            
            self.writer.write(length_data + message_bytes)
            await self.writer.drain()
            return True
    
    async def process_messages(self):
        """处理来自服务器的消息"""
        while self.connected:
            try:
                # 读取消息长度
                length_data = await self.reader.readexactly(4)
                length = struct.unpack('!I', length_data)[0]
                
                # 读取消息内容
                message_data = await self.reader.readexactly(length)
                message = json.loads(message_data.decode('utf-8'))
                
                # 处理响应
                msg_id = message.get('id')
                if msg_id and msg_id in self.response_handlers:
                    future = self.response_handlers.pop(msg_id)
                    future.set_result(message)
                else:
                    # 处理服务器推送的消息
                    await self.handle_server_message(message)
                
            except asyncio.IncompleteReadError:
                break
            except Exception as e:
                print(f"处理消息时出错: {e}")
                break
    
    async def handle_server_message(self, message: Dict):
        """处理服务器推送的消息"""
        msg_type = message.get('type')
        print(f"收到服务器消息: {message}")
        
        if msg_type == 'broadcast_message':
            from_client = message.get('from', 'unknown')
            text = message.get('text', '')
            print(f"[广播] {from_client}: {text}")
        # 可以根据需要添加更多消息类型处理
    
    async def ping(self):
        """发送ping消息"""
        return await self.send_message({'type': 'ping'})
    
    async def echo(self, text):
        """发送echo消息"""
        return await self.send_message({'type': 'echo', 'text': text})
    
    async def broadcast(self, text):
        """发送广播消息"""
        return await self.send_message({'type': 'broadcast', 'text': text}, expect_response=False)
    
    async def get_clients(self):
        """获取客户端列表"""
        return await self.send_message({'type': 'get_clients'})

async def demo_client_interaction():
    """演示客户端交互"""
    
    client = AsyncTCPClient()
    
    if await client.connect():
        # 发送ping
        response = await client.ping()
        print(f"Ping响应: {response}")
        
        # 发送echo
        response = await client.echo("Hello, Server!")
        print(f"Echo响应: {response}")
        
        # 获取客户端列表
        response = await client.get_clients()
        print(f"客户端列表: {response}")
        
        # 发送广播
        await client.broadcast("Hello, everyone!")
        
        # 保持连接一段时间
        await asyncio.sleep(5)
        
        # 断开连接
        await client.disconnect()

# 运行演示 (实际使用时取消注释)
# async def main():
#     # 启动服务器和客户端
#     server_task = asyncio.create_task(demo_tcp_server())
#     await asyncio.sleep(1)  # 等待服务器启动
#     
#     # 启动多个客户端
#     clients = [asyncio.create_task(demo_client_interaction()) for _ in range(3)]
#     await asyncio.gather(*clients)
#     
#     # 停止服务器
#     server_task.cancel()
# 
# asyncio.run(main())
```

### 3.2 异步HTTP客户端与服务器

```python
import asyncio
import json
import time
from typing import Dict, List, Optional, Union, Callable
from urllib.parse import urlparse, parse_qs
import mimetypes

# 简单的异步HTTP服务器实现
class AsyncHTTPServer:
    """简单的异步HTTP服务器"""
    
    def __init__(self, host='127.0.0.1', port=8000):
        self.host = host
        self.port = port
        self.routes = {}  # 路由表
        self.middleware = []  # 中间件
        self.static_files = {}  # 静态文件
    
    def route(self, path, method='GET'):
        """装饰器：注册路由"""
        def decorator(handler):
            self.routes[(path, method)] = handler
            return handler
        return decorator
    
    def add_middleware(self, middleware_func):
        """添加中间件"""
        self.middleware.append(middleware_func)
    
    def add_static_file(self, path, file_path, content_type=None):
        """添加静态文件路由"""
        if content_type is None:
            content_type, _ = mimetypes.guess_type(file_path)
            if content_type is None:
                content_type = 'application/octet-stream'
        
        async def static_handler(request):
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                return {
                    'status': 200,
                    'headers': {
                        'Content-Type': content_type,
                        'Content-Length': str(len(content))
                    },
                    'body': content
                }
            except FileNotFoundError:
                return {
                    'status': 404,
                    'headers': {'Content-Type': 'text/html'},
                    'body': b'<h1>File Not Found</h1>'
                }
        
        self.routes[(path, 'GET')] = static_handler
    
    async def start(self):
        """启动服务器"""
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        print(f"HTTP服务器启动: http://{self.host}:{self.port}")
        
        async with server:
            await server.serve_forever()
    
    async def handle_client(self, reader, writer):
        """处理客户端请求"""
        try:
            # 读取请求行
            request_line = await reader.readline()
            if not request_line:
                return
            
            # 解析请求行
            request_line = request_line.decode('utf-8').strip()
            parts = request_line.split(' ')
            if len(parts) != 3:
                return
            
            method, path, version = parts
            
            # 读取请求头
            headers = {}
            while True:
                header_line = await reader.readline()
                if not header_line or header_line == b'\r\n':
                    break
                
                header_line = header_line.decode('utf-8').strip()
                if ':' in header_line:
                    name, value = header_line.split(':', 1)
                    headers[name.strip().lower()] = value.strip()
            
            # 读取请求体
            content_length = int(headers.get('content-length', 0))
            body = b''
            if content_length > 0:
                body = await reader.readexactly(content_length)
            
            # 构建请求对象
            request = {
                'method': method,
                'path': path,
                'query': parse_qs(urlparse(path).query),
                'headers': headers,
                'body': body
            }
            
            # 应用中间件
            for middleware in self.middleware:
                request = await middleware(request)
                if request is None:  # 中间件可能中断请求处理
                    writer.close()
                    await writer.wait_closed()
                    return
            
            # 处理请求
            response = await self.handle_request(request)
            
            # 发送响应
            await self.send_response(writer, response)
            
        except Exception as e:
            print(f"处理请求时出错: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
    
    async def handle_request(self, request):
        """处理HTTP请求"""
        method = request['method']
        path = request['path']
        
        # 查找路由
        handler = self.routes.get((path, method))
        if handler:
            return await handler(request)
        
        # 尝试动态路由 (简化实现)
        for (route_path, route_method), route_handler in self.routes.items():
            if route_method == method and self.path_matches(route_path, path):
                # 提取路径参数
                params = self.extract_path_params(route_path, path)
                request['path_params'] = params
                return await route_handler(request)
        
        # 404响应
        return {
            'status': 404,
            'headers': {'Content-Type': 'text/html'},
            'body': b'<h1>404 Not Found</h1>'
        }
    
    def path_matches(self, pattern, path):
        """检查路径是否匹配模式"""
        # 简化实现，只支持简单的参数替换
        pattern_parts = pattern.split('/')
        path_parts = path.split('/')
        
        if len(pattern_parts) != len(path_parts):
            return False
        
        for pattern_part, path_part in zip(pattern_parts, path_parts):
            if not pattern_part.startswith('{') and pattern_part != path_part:
                return False
        
        return True
    
    def extract_path_params(self, pattern, path):
        """从路径中提取参数"""
        pattern_parts = pattern.split('/')
        path_parts = path.split('/')
        
        params = {}
        for pattern_part, path_part in zip(pattern_parts, path_parts):
            if pattern_part.startswith('{') and pattern_part.endswith('}'):
                param_name = pattern_part[1:-1]
                params[param_name] = path_part
        
        return params
    
    async def send_response(self, writer, response):
        """发送HTTP响应"""
        status = response.get('status', 200)
        headers = response.get('headers', {})
        body = response.get('body', b'')
        
        # 状态行
        status_text = {
            200: 'OK',
            404: 'Not Found',
            500: 'Internal Server Error'
        }.get(status, 'Unknown')
        
        writer.write(f"HTTP/1.1 {status} {status_text}\r\n".encode('utf-8'))
        
        # 头部
        for name, value in headers.items():
            writer.write(f"{name}: {value}\r\n".encode('utf-8'))
        
        # 空行
        writer.write(b"\r\n")
        
        # 正文
        if isinstance(body, str):
            body = body.encode('utf-8')
        writer.write(body)
        
        await writer.drain()

# 演示HTTP服务器
async def demo_http_server():
    """演示HTTP服务器"""
    
    # 创建服务器
    server = AsyncHTTPServer(host='127.0.0.1', port=8000)
    
    # 添加日志中间件
    async def logging_middleware(request):
        start_time = time.time()
        # 存储开始时间
        request['_start_time'] = start_time
        return request
    
    # 添加请求ID中间件
    async def request_id_middleware(request):
        import uuid
        request['request_id'] = str(uuid.uuid4())
        print(f"[{request['request_id']}] {request['method']} {request['path']}")
        return request
    
    server.add_middleware(logging_middleware)
    server.add_middleware(request_id_middleware)
    
    # 注册路由
    @server.route('/')
    async def home(request):
        """首页"""
        html = """
        <html>
        <head><title>异步HTTP服务器</title></head>
        <body>
            <h1>欢迎访问异步HTTP服务器</h1>
            <p>这是一个使用asyncio实现的简单HTTP服务器</p>
            <ul>
                <li><a href="/hello">GET /hello</a></li>
                <li><a href="/users/123">GET /users/:id</a></li>
                <li><a href="/api/data">GET /api/data</a></li>
            </ul>
        </body>
        </html>
        """
        return {
            'status': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': html
        }
    
    @server.route('/hello')
    async def hello(request):
        """简单问候"""
        name = request['query'].get('name', ['World'])[0]
        html = f"<h1>Hello, {name}!</h1>"
        return {
            'status': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': html
        }
    
    @server.route('/users/{id}')
    async def get_user(request):
        """获取用户信息"""
        user_id = request['path_params'].get('id', '0')
        
        # 模拟数据库查询延迟
        await asyncio.sleep(0.1)
        
        user_data = {
            'id': user_id,
            'name': f"User {user_id}",
            'email': f"user{user_id}@example.com"
        }
        
        return {
            'status': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(user_data)
        }
    
    @server.route('/api/data', 'GET')
    async def get_data(request):
        """获取数据API"""
        # 模拟数据库查询
        await asyncio.sleep(0.2)
        
        data = {
            'items': [
                {'id': 1, 'name': 'Item 1'},
                {'id': 2, 'name': 'Item 2'},
                {'id': 3, 'name': 'Item 3'}
            ],
            'total': 3
        }
        
        return {
            'status': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(data)
        }
    
    @server.route('/api/data', 'POST')
    async def create_data(request):
        """创建数据API"""
        try:
            body = json.loads(request['body'].decode('utf-8'))
            name = body.get('name', '')
            
            # 模拟数据库插入
            await asyncio.sleep(0.1)
            
            new_item = {
                'id': 4,  # 模拟自增ID
                'name': name
            }
            
            return {
                'status': 201,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(new_item)
            }
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {
                'status': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Invalid JSON'})
            }
    
    # 启动服务器
    await server.start()

# 异步HTTP客户端实现
class AsyncHTTPClient:
    """简单的异步HTTP客户端"""
    
    def __init__(self):
        self.timeout = 10
    
    async def request(self, method, url, headers=None, body=None):
        """发送HTTP请求"""
        # 解析URL
        parsed = urlparse(url)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        path = parsed.path or '/'
        query = parsed.query
        
        if query:
            path += '?' + query
        
        # 连接服务器
        reader, writer = await asyncio.open_connection(host, port)
        
        try:
            # 构建请求行
            request_line = f"{method} {path} HTTP/1.1\r\n"
            
            # 默认头部
            request_headers = {
                'Host': f"{host}:{port}",
                'User-Agent': 'AsyncHTTPClient/1.0',
                'Connection': 'close'
            }
            
            # 添加自定义头部
            if headers:
                request_headers.update(headers)
            
            # 添加Content-Length（如果有body）
            if body:
                if isinstance(body, str):
                    body = body.encode('utf-8')
                request_headers['Content-Length'] = str(len(body))
            
            # 发送请求
            writer.write(request_line.encode('utf-8'))
            
            for name, value in request_headers.items():
                writer.write(f"{name}: {value}\r\n".encode('utf-8'))
            
            writer.write(b"\r\n")
            
            if body:
                writer.write(body)
            
            await writer.drain()
            
            # 读取响应
            status_line = await reader.readline()
            status_line = status_line.decode('utf-8').strip()
            parts = status_line.split(' ', 2)
            if len(parts) >= 2:
                status_code = int(parts[1])
            
            # 读取响应头
            response_headers = {}
            while True:
                header_line = await reader.readline()
                if not header_line or header_line == b'\r\n':
                    break
                
                header_line = header_line.decode('utf-8').strip()
                if ':' in header_line:
                    name, value = header_line.split(':', 1)
                    response_headers[name.strip().lower()] = value.strip()
            
            # 读取响应体
            content_length = int(response_headers.get('content-length', 0))
            response_body = b''
            
            if content_length > 0:
                response_body = await reader.readexactly(content_length)
            else:
                # 如果没有Content-Length，读取直到连接关闭
                chunk = await reader.read(4096)
                while chunk:
                    response_body += chunk
                    chunk = await reader.read(4096)
            
            # 返回响应
            return {
                'status_code': status_code,
                'headers': response_headers,
                'body': response_body
            }
            
        finally:
            writer.close()
            await writer.wait_closed()
    
    async def get(self, url, headers=None):
        """发送GET请求"""
        return await self.request('GET', url, headers)
    
    async def post(self, url, data=None, headers=None):
        """发送POST请求"""
        body = None
        if data:
            if isinstance(data, dict):
                body = json.dumps(data)
                if not headers:
                    headers = {}
                headers['Content-Type'] = 'application/json'
            else:
                body = data
        
        return await self.request('POST', url, headers, body)

# 演示HTTP客户端
async def demo_http_client():
    """演示HTTP客户端"""
    client = AsyncHTTPClient()
    
    try:
        # GET请求
        print("发送GET请求...")
        response = await client.get('http://127.0.0.1:8000/hello?name=Async')
        print(f"状态码: {response['status_code']}")
        print(f"响应体: {response['body'].decode('utf-8')}")
        
        # GET API请求
        print("\n发送API GET请求...")
        response = await client.get('http://127.0.0.1:8000/api/data')
        print(f"状态码: {response['status_code']}")
        print(f"响应体: {response['body'].decode('utf-8')}")
        
        # POST请求
        print("\n发送POST请求...")
        post_data = {'name': 'New Item'}
        response = await client.post('http://127.0.0.1:8000/api/data', post_data)
        print(f"状态码: {response['status_code']}")
        print(f"响应体: {response['body'].decode('utf-8')}")
        
    except Exception as e:
        print(f"请求失败: {e}")

# 并发HTTP请求示例
async def fetch_multiple_urls():
    """并发获取多个URL"""
    client = AsyncHTTPClient()
    urls = [
        'http://127.0.0.1:8000/',
        'http://127.0.0.1:8000/hello',
        'http://127.0.0.1:8000/api/data'
    ]
    
    # 并发请求
    tasks = [client.get(url) for url in urls]
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 处理响应
    for i, response in enumerate(responses):
        url = urls[i]
        if isinstance(response, Exception):
            print(f"请求 {url} 失败: {response}")
        else:
            print(f"请求 {url} 成功，状态码: {response['status_code']}")

# 运行演示 (实际使用时取消注释)
# async def main():
#     # 启动HTTP服务器
#     server_task = asyncio.create_task(demo_http_server())
#     await asyncio.sleep(1)  # 等待服务器启动
#     
#     # 演示客户端请求
#     await demo_http_client()
#     
#     # 演示并发请求
#     await fetch_multiple_urls()
#     
#     # 停止服务器
#     server_task.cancel()
# 
# asyncio.run(main())
```

## 4. 高级异步模式与设计

### 4.1 异步上下文管理器与资源管理

```python
import asyncio
import aiofiles
import time
from contextlib import asynccontextmanager

class AsyncDatabaseConnection:
    """异步数据库连接池示例"""
    
    def __init__(self, host, port, max_connections=10):
        self.host = host
        self.port = port
        self.max_connections = max_connections
        self.pool = asyncio.Queue(maxsize=max_connections)
        self.semaphore = asyncio.Semaphore(max_connections)
        self.active_connections = 0
    
    async def initialize(self):
        """初始化连接池"""
        print(f"初始化数据库连接池 {self.host}:{self.port}")
        for i in range(self.max_connections):
            connection = f"connection_{i}"
            await self.pool.put(connection)
        print(f"创建了 {self.max_connections} 个连接")
    
    async def get_connection(self):
        """获取连接"""
        await self.semaphore.acquire()
        connection = await self.pool.get()
        self.active_connections += 1
        print(f"获取连接: {connection}, 当前活跃: {self.active_connections}")
        return connection
    
    async def release_connection(self, connection):
        """释放连接"""
        await self.pool.put(connection)
        self.semaphore.release()
        self.active_connections -= 1
        print(f"释放连接: {connection}, 当前活跃: {self.active_connections}")
    
    async def execute_query(self, query):
        """执行查询"""
        async with self.connection() as connection:
            print(f"执行查询: {query}")
            await asyncio.sleep(0.2)  # 模拟查询延迟
            return f"{connection} 查询结果: {query}"
    
    @asynccontextmanager
    async def connection(self):
        """异步上下文管理器获取连接"""
        connection = await self.get_connection()
        try:
            yield connection
        finally:
            await self.release_connection(connection)

# 异步文件处理器
class AsyncFileProcessor:
    """异步文件处理器"""
    
    def __init__(self):
        self.processed_files = 0
    
    @asynccontextmanager
    async def open_file(self, filename, mode='r'):
        """异步文件打开上下文管理器"""
        print(f"打开文件: {filename}")
        async with aiofiles.open(filename, mode) as file:
            try:
                yield file
            finally:
                print(f"文件关闭: {filename}")
    
    async def process_file(self, input_file, output_file):
        """处理文件"""
        async with self.open_file(input_file) as infile, self.open_file(output_file, 'w') as outfile:
            print(f"处理文件: {input_file} -> {output_file}")
            
            # 逐行处理
            async for line in infile:
                # 模拟处理逻辑
                processed_line = line.upper().strip() + '\n'
                await outfile.write(processed_line)
                await asyncio.sleep(0.01)  # 模拟处理延迟
            
            self.processed_files += 1
            print(f"文件处理完成: {output_file}")
    
    async def process_files_batch(self, file_pairs):
        """批量处理文件"""
        tasks = [self.process_file(input_file, output_file) 
                for input_file, output_file in file_pairs]
        
        await asyncio.gather(*tasks)
        print(f"批量处理完成，共处理 {self.processed_files} 个文件")

# 异步缓存管理器
class AsyncCache:
    """异步缓存实现"""
    
    def __init__(self, max_size=100, ttl=60):
        self.max_size = max_size
        self.ttl = ttl  # 生存时间(秒)
        self.cache = {}
        self.access_times = {}
        self.lock = asyncio.Lock()
    
    async def get(self, key):
        """获取缓存值"""
        async with self.lock:
            if key in self.cache:
                # 检查是否过期
                if time.time() - self.access_times[key] < self.ttl:
                    self.access_times[key] = time.time()
                    print(f"缓存命中: {key}")
                    return self.cache[key]
                else:
                    # 过期，删除
                    del self.cache[key]
                    del self.access_times[key]
                    print(f"缓存过期: {key}")
            
            print(f"缓存未命中: {key}")
            return None
    
    async def set(self, key, value):
        """设置缓存值"""
        async with self.lock:
            # 如果缓存已满，删除最久未访问的项
            if len(self.cache) >= self.max_size and key not in self.cache:
                oldest_key = min(self.access_times, key=self.access_times.get)
                del self.cache[oldest_key]
                del self.access_times[oldest_key]
                print(f"缓存已满，删除最久未访问项: {oldest_key}")
            
            self.cache[key] = value
            self.access_times[key] = time.time()
            print(f"缓存设置: {key}")
    
    async def delete(self, key):
        """删除缓存项"""
        async with self.lock:
            if key in self.cache:
                del self.cache[key]
                del self.access_times[key]
                print(f"缓存删除: {key}")
                return True
            return False
    
    @asynccontextmanager
    async def get_or_compute(self, key, compute_func):
        """获取缓存或计算值"""
        value = await self.get(key)
        if value is None:
            print(f"计算新值: {key}")
            value = await compute_func()
            await self.set(key, value)
        else:
            print(f"使用缓存值: {key}")
        
        yield value

# 异步资源池管理器
class AsyncResourcePool:
    """通用异步资源池"""
    
    def __init__(self, factory, max_size=10, validator=None):
        self.factory = factory  # 资源创建函数
        self.max_size = max_size
        self.validator = validator  # 资源验证函数
        self.pool = asyncio.Queue(maxsize=max_size)
        self.semaphore = asyncio.Semaphore(max_size)
        self.created = 0
    
    async def get(self):
        """获取资源"""
        await self.semaphore.acquire()
        
        try:
            # 尝试从池中获取资源
            resource = self.pool.get_nowait()
            
            # 验证资源是否有效
            if self.validator and not await self.validator(resource):
                print("资源无效，创建新资源")
                resource = await self.factory()
            else:
                print("从池中获取资源")
        except asyncio.QueueEmpty:
            # 池为空，创建新资源
            resource = await self.factory()
            self.created += 1
            print(f"创建新资源 (总创建数: {self.created})")
        
        return resource
    
    async def release(self, resource):
        """释放资源"""
        try:
            # 尝试将资源放回池中
            self.pool.put_nowait(resource)
            print("资源放回池中")
        except asyncio.QueueFull:
            # 池已满，丢弃资源
            print("池已满，丢弃资源")
        
        self.semaphore.release()
    
    @asynccontextmanager
    async def acquire(self):
        """异步上下文管理器获取资源"""
        resource = await self.get()
        try:
            yield resource
        finally:
            await self.release(resource)

# 演示异步资源管理
async def demo_async_resource_management():
    """演示异步资源管理"""
    
    print("=== 异步数据库连接池演示 ===")
    db_pool = AsyncDatabaseConnection("localhost", 5432, max_connections=3)
    await db_pool.initialize()
    
    # 使用连接池执行查询
    queries = [
        "SELECT * FROM users",
        "SELECT * FROM products",
        "SELECT * FROM orders",
        "SELECT * FROM inventory"
    ]
    
    # 并发执行查询
    tasks = [db_pool.execute_query(query) for query in queries]
    results = await asyncio.gather(*tasks)
    
    for result in results:
        print(result)
    
    print("\n=== 异步文件处理演示 ===")
    
    # 准备测试文件
    test_files = []
    for i in range(3):
        input_file = f"test_input_{i}.txt"
        output_file = f"test_output_{i}.txt"
        
        # 创建测试输入文件
        async with aiofiles.open(input_file, 'w') as f:
            await f.write(f"This is test file {i}\n")
            await f.write(f"Line 2 of file {i}\n")
            await f.write(f"Line 3 of file {i}\n")
        
        test_files.append((input_file, output_file))
    
    # 处理文件
    processor = AsyncFileProcessor()
    await processor.process_files_batch(test_files)
    
    print("\n=== 异步缓存演示 ===")
    cache = AsyncCache(max_size=3, ttl=5)
    
    # 模拟耗时计算
    async def expensive_compute(x):
        await asyncio.sleep(0.5)
        return x * 2
    
    # 使用缓存
    async with cache.get_or_compute("key1", lambda: expensive_compute(10)) as value:
        print(f"计算结果: {value}")
    
    async with cache.get_or_compute("key1", lambda: expensive_compute(10)) as value:
        print(f"计算结果: {value}")  # 应该使用缓存
    
    # 测试缓存过期
    await asyncio.sleep(6)
    
    async with cache.get_or_compute("key1", lambda: expensive_compute(10)) as value:
        print(f"计算结果: {value}")  # 缓存已过期
    
    print("\n=== 通用资源池演示 ===")
    
    # 创建模拟连接资源
    async def create_connection():
        await asyncio.sleep(0.1)
        conn_id = random.randint(1000, 9999)
        print(f"创建连接 {conn_id}")
        return f"connection_{conn_id}"
    
    # 验证连接
    async def validate_connection(conn):
        # 模拟连接验证
        return random.random() > 0.1  # 90%的连接有效
    
    # 创建资源池
    pool = AsyncResourcePool(create_connection, max_size=3, validator=validate_connection)
    
    # 并发使用资源
    async def use_resource(resource_name):
        async with pool.acquire() as resource:
            print(f"{resource_name} 正在使用 {resource}")
            await asyncio.sleep(0.5)
            print(f"{resource_name} 使用完毕")
    
    # 启动多个任务
    tasks = [use_resource(f"Worker_{i}") for i in range(5)]
    await asyncio.gather(*tasks)
    
    # 清理测试文件
    for input_file, output_file in test_files:
        try:
            os.remove(input_file)
            os.remove(output_file)
        except:
            pass

import os
import random

async def main():
    await demo_async_resource_management()

asyncio.run(main())
```

这份Python异步编程与并发高级指南涵盖了事件循环机制深入理解、async/await高级用法、协程池与任务调度、异步I/O与网络编程，以及异步资源管理等高级主题。通过这份指南，您可以掌握构建高性能、高并发Python应用程序的核心技能，在实际项目中有效利用异步编程模式提高系统吞吐量和响应速度。