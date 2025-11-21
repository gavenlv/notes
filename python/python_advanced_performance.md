# Python高级性能优化指南

## 1. 深入理解Python内存管理

### 1.1 引用计数机制详解

Python使用引用计数作为主要的内存管理机制，每个对象都有一个计数器，记录有多少引用指向该对象。

```python
import sys

def reference_count_demo():
    # 创建对象，初始引用计数为1
    a = []  # a指向列表对象
    print(f"初始引用计数: {sys.getrefcount(a)}")  # 2 (getrefcount也算一个引用)
    
    # 增加引用
    b = a  # b指向同一个列表对象
    print(f"增加引用后计数: {sys.getrefcount(a)}")  # 3
    
    # 函数调用会增加临时引用
    def use_list(lst):
        print(f"函数内引用计数: {sys.getrefcount(lst)}")  # 4
    
    use_list(a)
    
    # 函数返回后临时引用消失
    print(f"函数返回后计数: {sys.getrefcount(a)}")  # 3
    
    # 删除引用
    del b
    print(f"删除b后计数: {sys.getrefcount(a)}")  # 2
    
    # 当引用计数为0时，对象被销毁
    del a
    # 此时对象会被垃圾回收器回收

reference_count_demo()
```

### 1.2 循环引用问题与垃圾回收

循环引用会导致引用计数机制失效，Python使用分代垃圾回收器解决此问题。

```python
import gc
import weakref
import time

class Node:
    def __init__(self, name):
        self.name = name
        self.children = []
    
    def add_child(self, child):
        self.children.append(child)
        child.parent = self  # 创建循环引用
    
    def __del__(self):
        print(f"{self.name} 对象被销毁")
    
    def __repr__(self):
        return f"Node({self.name})"

def demo_cycle_reference():
    # 开启调试模式查看垃圾回收过程
    gc.set_debug(gc.DEBUG_LEAK)
    
    print("创建节点")
    parent = Node("Parent")
    child = Node("Child")
    
    print("建立循环引用")
    parent.add_child(child)
    child.parent = parent  # 显式建立循环引用
    
    print("删除引用")
    del parent, child
    
    # 手动触发垃圾回收
    print("\n手动触发垃圾回收")
    collected = gc.collect()
    print(f"回收了 {collected} 个对象")
    
    # 恢复默认设置
    gc.set_debug(0)

def demo_weak_ref_solution():
    """使用弱引用解决循环引用问题"""
    class WeakNode:
        def __init__(self, name):
            self.name = name
            self.children = []
        
        def add_child(self, child):
            self.children.append(child)
            # 使用弱引用指向父节点，避免循环引用
            child.parent = weakref.ref(self)
        
        def __del__(self):
            print(f"{self.name} 对象被销毁")
        
        @property
        def parent(self):
            # 处理弱引用可能已失效的情况
            ref = getattr(self, '_parent', None)
            return ref() if ref else None
        
        @parent.setter
        def parent(self, value):
            self._parent = value
    
    print("\n使用弱引用解决方案")
    parent = WeakNode("Parent")
    child = WeakNode("Child")
    
    parent.add_child(child)
    
    print("删除引用")
    del parent, child
    # 对象会被自动回收，无需手动垃圾回收

demo_cycle_reference()
demo_weak_ref_solution()
```

### 1.3 内存池与小整数缓存

Python针对小对象和小整数进行了优化，使用内存池和缓存机制提高性能。

```python
def demo_memory_optimization():
    # 小整数缓存 (-5到256)
    a = 100
    b = 100
    print(f"a is b: {a is b}")  # True，使用缓存对象
    
    c = 257
    d = 257
    print(f"c is d: {c is d}")  # False，超出缓存范围
    
    # 字符串驻留机制
    e = "hello"
    f = "hello"
    print(f"e is f: {e is f}")  # True，短字符串会被自动驻留
    
    g = "hello, world!"
    h = "hello, world!"
    print(f"g is h: {g is h}")  # 可能是False，取决于Python实现
    
    # 手动字符串驻留
    import sys
    i = sys.intern("another string")
    j = sys.intern("another string")
    print(f"i is j: {i is j}")  # True，手动驻留后相同

demo_memory_optimization()
```

## 2. 高级性能分析工具

### 2.1 cProfile与性能瓶颈分析

cProfile是Python内置的性能分析工具，可以精确测量代码执行时间。

```python
import cProfile
import pstats
import io
import time
import random

def compute_data(n):
    """计算密集型函数"""
    result = []
    for i in range(n):
        result.append(i * i)
    return result

def process_data(data):
    """数据处理函数"""
    processed = []
    for item in data:
        if item % 2 == 0:
            processed.append(item * 2)
    return processed

def simulate_database_query():
    """模拟数据库查询"""
    time.sleep(0.1)  # 模拟I/O等待
    return [random.randint(1, 100) for _ in range(100)]

def main():
    """主函数 - 我们要分析的代码"""
    # 模拟数据库查询
    data = simulate_database_query()
    
    # 计算密集型处理
    squares = compute_data(len(data))
    
    # 数据处理
    processed = process_data(squares)
    
    return processed

def profile_analysis():
    """使用cProfile分析性能"""
    # 创建Profile对象
    profiler = cProfile.Profile()
    
    # 开始分析
    profiler.enable()
    
    # 运行目标函数
    result = main()
    
    # 停止分析
    profiler.disable()
    
    # 创建统计流
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    
    # 打印分析结果
    ps.print_stats()
    print(s.getvalue())
    
    # 获取函数调用次数
    print("\n按调用次数排序:")
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('calls')
    ps.print_stats(10)  # 只显示前10个函数
    print(s.getvalue())

profile_analysis()
```

### 2.2 line_profiler与逐行性能分析

line_profiler可以分析函数每一行的执行时间，精确定位性能瓶颈。

```python
# 安装: pip install line_profiler
# 使用: 在命令行执行 kernprof -l -v script.py

@profile  # line_profiler需要的装饰器
def analyze_performance():
    total = 0
    data = range(10000)
    
    # 计算总和 - 多种方法对比
    for i in data:
        total += i
    
    # 使用sum函数
    total2 = sum(data)
    
    # 使用生成器表达式
    total3 = sum(i for i in data)
    
    # 列表推导式
    squares = [i*i for i in data]
    
    # 使用map
    squares2 = list(map(lambda x: x*x, data))
    
    return total, total2, total3, squares, squares2

if __name__ == "__main__":
    result = analyze_performance()
```

### 2.3 memory_profiler与内存使用分析

memory_profiler可以逐行分析内存使用情况，帮助发现内存泄漏。

```python
# 安装: pip install memory_profiler
# 使用: 在命令行执行 python -m memory_profiler script.py

@profile
def analyze_memory():
    data = []
    
    # 添加数据，观察内存增长
    for i in range(100000):
        data.append(i * 2)
    
    # 创建大列表，观察内存峰值
    big_list = [0] * 1000000
    
    # 删除大列表，观察内存回收
    del big_list
    
    # 使用生成器表达式，减少内存占用
    gen = (i*i for i in range(100000))
    sum_of_squares = sum(gen)
    
    return len(data), sum_of_squares

if __name__ == "__main__":
    result = analyze_memory()
```

## 3. 高级算法优化技术

### 3.1 使用NumPy加速数值计算

NumPy使用C语言实现的底层算法，比纯Python代码快几个数量级。

```python
import numpy as np
import time

def pure_python_sum(n):
    """纯Python计算平方和"""
    total = 0
    for i in range(n):
        total += i * i
    return total

def numpy_sum(n):
    """使用NumPy计算平方和"""
    arr = np.arange(n)
    return np.sum(arr * arr)

def compare_performance():
    """比较纯Python和NumPy性能"""
    sizes = [10**3, 10**4, 10**5, 10**6]
    
    print("大小\t\t纯Python(秒)\tNumPy(秒)\t加速比")
    print("-" * 50)
    
    for size in sizes:
        # 测试纯Python
        start = time.time()
        result1 = pure_python_sum(size)
        python_time = time.time() - start
        
        # 测试NumPy
        start = time.time()
        result2 = numpy_sum(size)
        numpy_time = time.time() - start
        
        # 验证结果一致性
        assert result1 == result2, "结果不一致!"
        
        speedup = python_time / numpy_time
        print(f"{size:,}\t\t{python_time:.4f}\t\t{numpy_time:.4f}\t\t{speedup:.2f}x")

# 演示NumPy向量化操作的优势
def vectorization_benefits():
    """展示向量化的优势"""
    size = 10_000_000
    
    # 生成两个大数组
    a = np.random.rand(size)
    b = np.random.rand(size)
    
    # 向量化操作
    start = time.time()
    c = a + b  # 向量化加法
    vectorized_time = time.time() - start
    
    # 非向量化操作
    start = time.time()
    c_loop = np.empty(size)
    for i in range(size):
        c_loop[i] = a[i] + b[i]
    loop_time = time.time() - start
    
    print(f"向量化操作时间: {vectorized_time:.4f}秒")
    print(f"循环操作时间: {loop_time:.4f}秒")
    print(f"向量化加速比: {loop_time/vectorized_time:.2f}x")

compare_performance()
vectorization_benefits()
```

### 3.2 使用多进程池处理CPU密集型任务

多进程可以绕过GIL限制，充分利用多核CPU。

```python
import multiprocessing as mp
import time
import math
import random

def cpu_intensive_task(n):
    """CPU密集型任务示例"""
    # 模拟复杂计算
    result = 0
    for i in range(n):
        result += math.sqrt(random.random() * i)
    return result

def parallel_vs_sequential():
    """比较并行和顺序执行的性能"""
    num_tasks = 8
    task_size = 1_000_000
    
    # 顺序执行
    start = time.time()
    sequential_results = [cpu_intensive_task(task_size) for _ in range(num_tasks)]
    sequential_time = time.time() - start
    
    # 并行执行
    start = time.time()
    with mp.Pool(processes=mp.cpu_count()) as pool:
        parallel_results = pool.starmap(cpu_intensive_task, [(task_size,) for _ in range(num_tasks)])
    parallel_time = time.time() - start
    
    print(f"CPU核心数: {mp.cpu_count()}")
    print(f"顺序执行时间: {sequential_time:.2f}秒")
    print(f"并行执行时间: {parallel_time:.2f}秒")
    print(f"加速比: {sequential_time/parallel_time:.2f}x")
    
    # 验证结果一致性
    for i, (s, p) in enumerate(zip(sequential_results, parallel_results)):
        if abs(s - p) > 1e-10:
            print(f"结果不一致! 任务{i}: {s} vs {p}")
            return
    
    print("所有任务结果一致")

# 演示任务分块对性能的影响
def chunk_size_optimization():
    """测试不同任务块大小的影响"""
    num_tasks = 100
    task_size = 100_000
    
    def measure_time(chunk_size):
        start = time.time()
        with mp.Pool() as pool:
            results = pool.map(
                lambda x: cpu_intensive_task(task_size),
                range(num_tasks),
                chunksize=chunk_size
            )
        return time.time() - start
    
    chunk_sizes = [1, 5, 10, 20, 50]
    print("块大小\t\t执行时间(秒)")
    print("-" * 30)
    
    for chunk_size in chunk_sizes:
        elapsed = measure_time(chunk_size)
        print(f"{chunk_size}\t\t{elapsed:.2f}")

parallel_vs_sequential()
chunk_size_optimization()
```

### 3.3 使用缓存技术避免重复计算

缓存是避免重复计算的有效方法，特别适合递归和耗时计算。

```python
import functools
import time

# Python内置的LRU缓存装饰器
@functools.lru_cache(maxsize=128)
def fibonacci_cached(n):
    """带缓存的斐波那契数列计算"""
    if n <= 1:
        return n
    return fibonacci_cached(n-1) + fibonacci_cached(n-2)

def fibonacci_uncached(n):
    """不带缓存的斐波那契数列计算"""
    if n <= 1:
        return n
    return fibonacci_uncached(n-1) + fibonacci_uncached(n-2)

def test_fibonacci_performance():
    """测试斐波那契计算的性能差异"""
    n = 35
    
    # 测试不带缓存的版本
    start = time.time()
    result1 = fibonacci_uncached(n)
    uncached_time = time.time() - start
    
    # 清除缓存
    fibonacci_cached.cache_clear()
    
    # 测试带缓存的版本
    start = time.time()
    result2 = fibonacci_cached(n)
    cached_time = time.time() - start
    
    print(f"计算fibonacci({n})")
    print(f"无缓存时间: {uncached_time:.4f}秒")
    print(f"有缓存时间: {cached_time:.6f}秒")
    print(f"加速比: {uncached_time/cached_time:.2f}x")
    print(f"结果一致: {result1 == result2}")
    print(f"缓存命中信息: {fibonacci_cached.cache_info()}")

# 自定义缓存类
class CustomCache:
    """自定义LRU缓存实现"""
    def __init__(self, maxsize=128):
        self.maxsize = maxsize
        self.cache = {}
        self.order = []
    
    def get(self, key):
        if key in self.cache:
            # 更新使用顺序
            self.order.remove(key)
            self.order.append(key)
            return self.cache[key]
        return None
    
    def put(self, key, value):
        if key in self.cache:
            # 更新现有项
            self.cache[key] = value
            self.order.remove(key)
            self.order.append(key)
        else:
            # 添加新项
            if len(self.cache) >= self.maxsize:
                # 移除最久未使用的项
                oldest = self.order.pop(0)
                del self.cache[oldest]
            
            self.cache[key] = value
            self.order.append(key)
    
    def __call__(self, func):
        """将此类用作装饰器"""
        def wrapper(*args):
            # 使用函数参数作为键
            key = str(args)
            
            # 尝试从缓存获取
            cached_value = self.get(key)
            if cached_value is not None:
                return cached_value
            
            # 计算新值
            result = func(*args)
            
            # 存入缓存
            self.put(key, result)
            return result
        
        return wrapper

@CustomCache(maxsize=64)
def slow_function(x, y):
    """模拟耗时函数"""
    time.sleep(0.1)  # 模拟计算延迟
    return x * y + x + y

def test_custom_cache():
    """测试自定义缓存"""
    print("\n测试自定义缓存")
    
    # 第一次调用 - 需要计算
    start = time.time()
    result1 = slow_function(10, 20)
    first_call_time = time.time() - start
    
    # 第二次调用相同参数 - 使用缓存
    start = time.time()
    result2 = slow_function(10, 20)
    second_call_time = time.time() - start
    
    # 第三次调用不同参数 - 需要计算
    start = time.time()
    result3 = slow_function(15, 25)
    third_call_time = time.time() - start
    
    print(f"第一次调用时间: {first_call_time:.4f}秒")
    print(f"第二次调用时间: {second_call_time:.4f}秒")
    print(f"第三次调用时间: {third_call_time:.4f}秒")
    print(f"缓存命中效果: {first_call_time/second_call_time:.2f}x加速")
    print(f"结果验证: {result1 == result2 and result1 != result3}")

test_fibonacci_performance()
test_custom_cache()
```

## 4. 数据结构优化技巧

### 4.1 选择合适的数据结构

不同数据结构的性能特性差异巨大，选择合适的结构能显著提升性能。

```python
import time
import random
from collections import defaultdict, Counter, deque

def test_container_performance():
    """测试不同容器的性能特点"""
    size = 1_000_000
    
    # 测试数据
    data = [random.randint(0, 9999) for _ in range(size)]
    test_values = [random.randint(0, 9999) for _ in range(1000)]
    
    # 测试列表查找
    start = time.time()
    for val in test_values:
        _ = val in data  # 列表查找O(n)
    list_time = time.time() - start
    
    # 测试集合查找
    data_set = set(data)
    start = time.time()
    for val in test_values:
        _ = val in data_set  # 集合查找O(1)
    set_time = time.time() - start
    
    # 测试字典计数
    start = time.time()
    dict_counts = {}
    for val in data:
        dict_counts[val] = dict_counts.get(val, 0) + 1
    dict_time = time.time() - start
    
    # 测试collections.Counter计数
    start = time.time()
    counter = Counter(data)
    counter_time = time.time() - start
    
    # 测试defaultdict计数
    start = time.time()
    default_counts = defaultdict(int)
    for val in data:
        default_counts[val] += 1
    default_time = time.time() - start
    
    print(f"数据大小: {size:,}, 查询次数: 1,000")
    print(f"列表查找时间: {list_time:.4f}秒")
    print(f"集合查找时间: {set_time:.4f}秒")
    print(f"字典计数时间: {dict_time:.4f}秒")
    print(f"Counter计数时间: {counter_time:.4f}秒")
    print(f"defaultdict计数时间: {default_time:.4f}秒")
    print(f"集合vs列表加速比: {list_time/set_time:.2f}x")

def test_deque_vs_list():
    """测试deque与list在队列操作上的性能差异"""
    size = 1_000_000
    
    # 列表实现队列
    list_queue = list(range(size))
    start = time.time()
    for _ in range(1000):
        # 头部出队和尾部入队
        list_queue.pop(0)
        list_queue.append(999999)
    list_time = time.time() - start
    
    # deque实现队列
    deque_queue = deque(range(size))
    start = time.time()
    for _ in range(1000):
        # 头部出队和尾部入队
        deque_queue.popleft()
        deque_queue.append(999999)
    deque_time = time.time() - start
    
    print(f"队列操作测试 (1,000次)")
    print(f"列表实现时间: {list_time:.4f}秒")
    print(f"deque实现时间: {deque_time:.4f}秒")
    print(f"deque加速比: {list_time/deque_time:.2f}x")

test_container_performance()
test_deque_vs_list()
```

### 4.2 高效的字符串处理技巧

字符串操作在某些场景下可能是性能瓶颈，使用高效的方法可以显著提升性能。

```python
import time
import random

def test_string_concatenation():
    """测试不同字符串连接方法的性能"""
    size = 100_000
    strings = [f"item_{i}" for i in range(size)]
    
    # 方法1: 使用+连接
    start = time.time()
    result1 = ""
    for s in strings:
        result1 += s
    plus_time = time.time() - start
    
    # 方法2: 使用join
    start = time.time()
    result2 = "".join(strings)
    join_time = time.time() - start
    
    # 方法3: 使用StringIO
    from io import StringIO
    start = time.time()
    buffer = StringIO()
    for s in strings:
        buffer.write(s)
    result3 = buffer.getvalue()
    sio_time = time.time() - start
    
    # 方法4: 使用列表推导+join
    start = time.time()
    result4 = "".join([s for s in strings])
    list_join_time = time.time() - start
    
    print(f"字符串连接测试 ({size:,}个字符串)")
    print(f"+操作时间: {plus_time:.4f}秒")
    print(f"join时间: {join_time:.4f}秒")
    print(f"StringIO时间: {sio_time:.4f}秒")
    print(f"列表推导+join时间: {list_join_time:.4f}秒")
    print(f"join相对于+的加速比: {plus_time/join_time:.2f}x")
    
    # 验证结果一致性
    assert result1 == result2 == result3 == result4, "结果不一致!"

def test_string_search():
    """测试不同字符串搜索方法的性能"""
    text = " ".join([f"word_{i}" for i in range(100_000)])
    search_terms = ["word_1", "word_50000", "word_99999", "nonexistent"]
    
    # 方法1: 使用in操作符
    start = time.time()
    for term in search_terms:
        _ = term in text
    in_time = time.time() - start
    
    # 方法2: 使用find方法
    start = time.time()
    for term in search_terms:
        _ = text.find(term) >= 0
    find_time = time.time() - start
    
    # 方法3: 使用正则表达式
    import re
    pattern = re.compile("|".join(search_terms))
    start = time.time()
    _ = pattern.search(text)
    regex_time = time.time() - start
    
    # 方法4: 使用正则表达式预编译
    start = time.time()
    compiled_patterns = [re.compile(term) for term in search_terms]
    for pattern in compiled_patterns:
        _ = pattern.search(text)
    regex_compiled_time = time.time() - start
    
    print(f"\n字符串搜索测试 (搜索4个词)")
    print(f"in操作时间: {in_time:.6f}秒")
    print(f"find方法时间: {find_time:.6f}秒")
    print(f"正则表达式时间: {regex_time:.6f}秒")
    print(f"预编译正则时间: {regex_compiled_time:.6f}秒")

def test_string_formatting():
    """测试不同字符串格式化方法的性能"""
    name = "Alice"
    age = 30
    score = 95.5
    
    iterations = 100_000
    
    # 方法1: %格式化
    start = time.time()
    for _ in range(iterations):
        _ = "%s is %d years old, score: %.1f" % (name, age, score)
    percent_time = time.time() - start
    
    # 方法2: str.format
    start = time.time()
    for _ in range(iterations):
        _ = "{} is {} years old, score: {}".format(name, age, score)
    format_time = time.time() - start
    
    # 方法3: f-string (Python 3.6+)
    start = time.time()
    for _ in range(iterations):
        _ = f"{name} is {age} years old, score: {score}"
    fstring_time = time.time() - start
    
    print(f"\n字符串格式化测试 ({iterations:,}次迭代)")
    print(f"%格式化时间: {percent_time:.4f}秒")
    print(f"str.format时间: {format_time:.4f}秒")
    print(f"f-string时间: {fstring_time:.4f}秒")
    print(f"f-string相对于%的加速比: {percent_time/fstring_time:.2f}x")

test_string_concatenation()
test_string_search()
test_string_formatting()
```

## 5. 高级内存优化技术

### 5.1 使用生成器和迭代器减少内存占用

生成器和迭代器可以极大地减少处理大数据时的内存占用。

```python
import time
import sys
import random

def memory_vs_generator():
    """比较列表和生成器的内存占用"""
    size = 10_000_000
    
    # 列表方法
    print("创建列表...")
    start = time.time()
    number_list = [i * 2 for i in range(size)]
    list_time = time.time() - start
    list_memory = sys.getsizeof(number_list) + sum(sys.getsizeof(x) for x in number_list[:1000]) * (size/1000)  # 估算
    
    # 生成器方法
    print("创建生成器...")
    start = time.time()
    number_generator = (i * 2 for i in range(size))
    gen_time = time.time() - start
    gen_memory = sys.getsizeof(number_generator)
    
    print(f"数据大小: {size:,}")
    print(f"列表创建时间: {list_time:.4f}秒")
    print(f"生成器创建时间: {gen_time:.4f}秒")
    print(f"列表内存占用(估算): ~{list_memory/(1024*1024):.2f} MB")
    print(f"生成器内存占用: ~{gen_memory/(1024):.2f} KB")
    
    # 计算总和
    print("\n计算总和...")
    
    # 列表求和
    start = time.time()
    list_sum = sum(number_list)
    list_sum_time = time.time() - start
    
    # 生成器求和
    start = time.time()
    gen_sum = sum(number_generator)
    gen_sum_time = time.time() - start
    
    print(f"列表求和时间: {list_sum_time:.4f}秒")
    print(f"生成器求和时间: {gen_sum_time:.4f}秒")
    print(f"结果一致: {list_sum == gen_sum}")

def custom_generator_example():
    """自定义生成器的实际应用"""
    import os
    
    def find_files(directory, pattern):
        """递归查找匹配模式的文件生成器"""
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(pattern):
                    yield os.path.join(root, file)
    
    def process_large_file(file_path, chunk_size=1024):
        """大文件分块处理生成器"""
        with open(file_path, 'r', encoding='utf-8') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk
    
    def fibonacci_generator(n):
        """斐波那契数列生成器"""
        a, b = 0, 1
        for _ in range(n):
            yield a
            a, b = b, a + b
    
    # 使用示例
    print("\n自定义生成器示例:")
    
    # 斐波那契数列
    print("前10个斐波那契数:", list(fibonacci_generator(10)))
    
    # 注意: 文件操作需要实际文件，这里只展示方法
    # 使用示例:
    # for file_path in find_files('.', '.py'):
    #     print(f"找到Python文件: {file_path}")
    # 
    # for chunk in process_large_file('large_file.txt'):
    #     # 处理文件块
    #     pass

memory_vs_generator()
custom_generator_example()
```

### 5.2 使用slots减少对象内存占用

对于需要创建大量小对象的场景，使用__slots__可以显著减少内存占用。

```python
import time
import sys

class RegularPoint:
    """常规类定义"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def distance(self, other):
        return ((self.x - other.x)**2 + (self.y - other.y)**2)**0.5

class SlottedPoint:
    """使用slots的类定义"""
    __slots__ = ('x', 'y')  # 限制实例属性
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def distance(self, other):
        return ((self.x - other.x)**2 + (self.y - other.y)**2)**0.5

def compare_slots_performance():
    """比较使用slots前后的性能和内存占用"""
    size = 1_000_000
    
    # 创建常规点
    start = time.time()
    regular_points = [RegularPoint(i, i*2) for i in range(size)]
    regular_creation_time = time.time() - start
    
    # 创建使用slots的点
    start = time.time()
    slotted_points = [SlottedPoint(i, i*2) for i in range(size)]
    slotted_creation_time = time.time() - start
    
    # 内存比较
    regular_memory = sys.getsizeof(regular_points) + sum(sys.getsizeof(p) for p in regular_points[:100]) * (size/100)
    slotted_memory = sys.getsizeof(slotted_points) + sum(sys.getsizeof(p) for p in slotted_points[:100]) * (size/100)
    
    # 计算距离
    start = time.time()
    for i in range(1000):
        _ = regular_points[i].distance(regular_points[i+1])
    regular_access_time = time.time() - start
    
    start = time.time()
    for i in range(1000):
        _ = slotted_points[i].distance(slotted_points[i+1])
    slotted_access_time = time.time() - start
    
    print(f"创建 {size:,} 个对象比较:")
    print(f"常规类创建时间: {regular_creation_time:.4f}秒")
    print(f"slots类创建时间: {slotted_creation_time:.4f}秒")
    print(f"创建时间比率: {regular_creation_time/slotted_creation_time:.2f}x")
    print(f"\n内存占用比较(估算):")
    print(f"常规类内存: ~{regular_memory/(1024*1024):.2f} MB")
    print(f"slots类内存: ~{slotted_memory/(1024*1024):.2f} MB")
    print(f"内存节省: {(regular_memory-slotted_memory)/regular_memory*100:.1f}%")
    print(f"\n访问速度比较(1,000次操作):")
    print(f"常规类访问时间: {regular_access_time:.6f}秒")
    print(f"slots类访问时间: {slotted_access_time:.6f}秒")

def slots_with_inheritance():
    """展示slots与继承的注意事项"""
    
    class Base:
        __slots__ = ('x',)
        def __init__(self, x):
            self.x = x
    
    # 错误示例 - 子类需要重新声明slots
    class ChildError(Base):
        def __init__(self, x, y):
            super().__init__(x)
            self.y = y  # 会报错，因为ChildError没有定义y在slots中
    
    # 正确示例 - 子类重新声明slots
    class Child(Base):
        __slots__ = ('x', 'y')  # 重新声明父类的x和新的y
        
        def __init__(self, x, y):
            super().__init__(x)
            self.y = y
    
    # 多重继承中的slots
    class Mixin:
        __slots__ = ('z',)
    
    class Multiple(Child, Mixin):
        __slots__ = ('x', 'y', 'z')  # 必须声明所有slots
        
        def __init__(self, x, y, z):
            Child.__init__(self, x, y)
            self.z = z
    
    print("\nslots与继承示例:")
    point = Child(10, 20)
    print(f"Child对象: x={point.x}, y={point.y}")
    
    multi = Multiple(5, 10, 15)
    print(f"Multiple对象: x={multi.x}, y={multi.y}, z={multi.z}")

compare_slots_performance()
slots_with_inheritance()
```

## 6. 高性能第三方库集成

### 6.1 使用Cython加速Python代码

Cython可以将Python代码编译成C扩展，大幅提升性能。

```python
# 注意: 这是一个示例，实际Cython代码需要写在.pyx文件中
# 示例: 在cython_example.pyx中:

"""
# cython: language_level=3

def cython_fibonacci(int n):
    cdef int i, a, b, temp
    a, b = 0, 1
    for i in range(n):
        temp = a
        a = b
        b = temp + b
    return a

def cython_sum_squares(int n):
    cdef int i
    cdef long long total = 0
    for i in range(n):
        total += i * i
    return total
"""

# 使用方法:
# 1. 将上述代码保存为cython_example.pyx
# 2. 创建setup.py文件
# 3. 运行python setup.py build_ext --inplace
# 4. 在Python中导入并使用

import time

def python_fibonacci(n):
    """纯Python实现的斐波那契数"""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def python_sum_squares(n):
    """纯Python实现的平方和"""
    total = 0
    for i in range(n):
        total += i * i
    return total

def simulate_cython_performance():
    """模拟Cython的性能提升"""
    # 这些函数模拟Cython可能带来的性能提升
    # 实际性能提升取决于具体代码和Cython编译
    
    n = 10_000_000
    
    # 测试Python版本
    start = time.time()
    fib_result = python_fibonacci(n)
    python_fib_time = time.time() - start
    
    start = time.time()
    sum_result = python_sum_squares(n)
    python_sum_time = time.time() - start
    
    # 模拟Cython版本(通常快2-10倍)
    cython_speedup_factor = 5.0
    cython_fib_time = python_fib_time / cython_speedup_factor
    cython_sum_time = python_sum_time / cython_speedup_factor
    
    print(f"斐波那契数列计算(n={n:,}):")
    print(f"Python时间: {python_fib_time:.4f}秒")
    print(f"Cython时间(估计): {cython_fib_time:.4f}秒")
    print(f"性能提升: {cython_speedup_factor:.1f}x")
    
    print(f"\n平方和计算(n={n:,}):")
    print(f"Python时间: {python_sum_time:.4f}秒")
    print(f"Cython时间(估计): {cython_sum_time:.4f}秒")
    print(f"性能提升: {cython_speedup_factor:.1f}x")
    
    print("\n注意: 实际Cython性能提升取决于代码特性和优化程度")

# 展示Cython的关键特性
def explain_cython_features():
    """解释Cython的关键特性和优化方法"""
    
    features = """
    Cython关键特性:
    
    1. 静态类型声明:
       - 使用cdef声明C变量
       - 显著减少Python对象开销
       - 示例: cdef int i, total = 0
    
    2. 函数优化:
       - 使用cdef或cpdef定义函数
       - 减少函数调用开销
       - 示例: cpdef int fast_function(int n)
    
    3. 内存视图:
       - 高效处理NumPy数组
       - 无Python API调用
       - 示例: cdef double[:, :] mv = array
    
    4. 编译指令:
       - 禁用边界检查
       - 禁用负索引检查
       - 示例: # cython: boundscheck=False
    """
    
    print(features)
    
    # 展示实际应用场景
    scenarios = """
    最适合Cython优化的场景:
    
    1. 计算密集型循环
    2. 数值计算
    3. 字符串处理
    4. 算法实现
    
    不适合Cython优化的场景:
    
    1. I/O密集型操作
    2. 已经使用NumPy的数值计算
    3. 简单的Web应用逻辑
    """
    
    print(scenarios)

simulate_cython_performance()
explain_cython_features()
```

### 6.2 使用Numba进行即时编译优化

Numba可以将Python和NumPy代码转换为高效的机器码。

```python
# 安装: pip install numba

import time
import math
import random

# 模拟Numba功能的示例(实际代码需要Numba库)
# 以下代码展示如何使用Numba装饰器:

"""
from numba import jit, njit, prange
import numpy as np

# 使用jit装饰器
@jit(nopython=True)  # nopython模式获得最佳性能
def numba_monte_carlo_pi(num_samples):
    acc = 0
    for i in range(num_samples):
        x = random.random()
        y = random.random()
        if (x**2 + y**2) < 1.0:
            acc += 1
    return 4.0 * acc / num_samples

# 使用并行化
@njit(parallel=True)
def numba_parallel_sum(arr):
    total = 0.0
    for i in prange(len(arr)):  # 并行循环
        total += math.sin(arr[i])
    return total
"""

def python_monte_carlo_pi(num_samples):
    """纯Python实现的蒙特卡洛PI计算"""
    acc = 0
    for i in range(num_samples):
        x = random.random()
        y = random.random()
        if (x**2 + y**2) < 1.0:
            acc += 1
    return 4.0 * acc / num_samples

def python_parallel_sum(arr):
    """纯Python实现的并行求和模拟"""
    total = 0.0
    for i in range(len(arr)):
        total += math.sin(arr[i])
    return total

def simulate_numba_performance():
    """模拟Numba的性能提升"""
    num_samples = 10_000_000
    arr = [random.random() for _ in range(1_000_000)]
    
    # 蒙特卡洛PI计算
    print("蒙特卡洛PI计算:")
    start = time.time()
    pi_estimate = python_monte_carlo_pi(num_samples)
    python_pi_time = time.time() - start
    print(f"Python时间: {python_pi_time:.4f}秒, 估计值: {pi_estimate:.6f}")
    
    # 模拟Numba性能(通常快10-100倍)
    numba_pi_speedup = 30.0
    numba_pi_time = python_pi_time / numba_pi_speedup
    print(f"Numba时间(估计): {numba_pi_time:.4f}秒")
    print(f"性能提升: {numba_pi_speedup:.1f}x")
    
    # 数组求和
    print("\n数组sin求和:")
    start = time.time()
    sum_result = python_parallel_sum(arr)
    python_sum_time = time.time() - start
    print(f"Python时间: {python_sum_time:.4f}秒")
    
    # 模拟Numba性能
    numba_sum_speedup = 15.0
    numba_sum_time = python_sum_time / numba_sum_speedup
    print(f"Numba时间(估计): {numba_sum_time:.4f}秒")
    print(f"性能提升: {numba_sum_speedup:.1f}x")

def explain_numba_features():
    """解释Numba的关键特性和使用场景"""
    
    features = """
    Numba关键特性:
    
    1. 即时编译(JIT):
       - 将Python代码编译为机器码
       - 无需单独编译步骤
       - 首次运行有编译开销，后续执行快
    
    2. 支持的数据类型:
       - 基本数值类型(int, float, complex)
       - NumPy数组
       - 部分Python数据结构
    
    3. 并行化支持:
       - 自动并行化循环
       - 使用prange替代range
       - 支持多核CPU
    
    4. GPU支持:
       - CUDA后端支持
       - 适合大规模并行计算
       - 需要NVIDIA GPU
    """
    
    print(features)
    
    scenarios = """
    Numba最适合的场景:
    
    1. 数值计算和科学计算
    2. 仿真和模拟
    3. 图像和信号处理
    4. 统计计算
    
    Numba的限制:
    
    1. 不支持所有Python特性
    2. 首次运行有编译延迟
    3. 对某些复杂算法可能不如手动优化
    4. 需要特定的代码模式才能获得最佳性能
    """
    
    print(scenarios)

# 使用Numba的最佳实践
def numba_best_practices():
    """展示Numba的最佳实践"""
    
    practices = """
    Numba最佳实践:
    
    1. 使用nopython模式:
       @jit(nopython=True)  # 获得最佳性能
    
    2. 避免在循环中分配内存:
       # 不好的做法
       for i in range(n):
           new_array = np.zeros(10)  # 每次循环都分配
       
       # 好的做法
       new_array = np.zeros(10)  # 循环外分配
       for i in range(n):
           # 使用数组
    
    3. 使用NumPy数组而非Python列表:
       @jit(nopython=True)
       def process_data(data):
           # 使用NumPy数组
           arr = np.array(data)
           return arr * 2
    
    4. 合理使用并行化:
       @njit(parallel=True)
       def parallel_process(arr):
           for i in prange(len(arr)):  # 使用prange
               arr[i] = some_calculation(i)
    """
    
    print(practices)

simulate_numba_performance()
explain_numba_features()
numba_best_practices()
```

## 7. 性能优化的高级策略

### 7.1 延迟加载与按需计算

延迟加载可以减少启动时间和内存占用，按需计算可以避免不必要的计算。

```python
import time
import random

# 延迟加载示例
class LazyDataLoader:
    """延迟加载数据的类"""
    
    def __init__(self, data_source):
        self.data_source = data_source
        self._data = None  # 延迟加载的数据
    
    @property
    def data(self):
        """属性访问时才加载数据"""
        if self._data is None:
            print(f"正在从{self.data_source}加载数据...")
            time.sleep(1)  # 模拟加载时间
            self._data = [random.randint(0, 1000) for _ in range(10000)]
            print("数据加载完成")
        return self._data
    
    def process_data(self):
        """处理数据的方法"""
        return sum(self.data)  # 访问数据时触发加载

def demo_lazy_loading():
    """演示延迟加载的效果"""
    print("创建数据加载器...")
    loader = LazyDataLoader("大数据集.csv")
    
    print("对象创建完成，但数据尚未加载")
    
    print("首次访问数据...")
    start = time.time()
    total = loader.process_data()
    first_access_time = time.time() - start
    print(f"首次访问完成，耗时: {first_access_time:.2f}秒，总和: {total}")
    
    print("第二次访问数据...")
    start = time.time()
    total = loader.process_data()
    second_access_time = time.time() - start
    print(f"第二次访问完成，耗时: {second_access_time:.2f}秒，总和: {total}")

# 按需计算示例
class LazyCalculator:
    """按需计算的类"""
    
    def __init__(self, data):
        self.data = data
        self._mean = None
        self._median = None
        self._std_dev = None
    
    @property
    def mean(self):
        """按需计算平均值"""
        if self._mean is None:
            print("计算平均值...")
            self._mean = sum(self.data) / len(self.data)
            print(f"平均值计算完成: {self._mean}")
        return self._mean
    
    @property
    def median(self):
        """按需计算中位数"""
        if self._median is None:
            print("计算中位数...")
            sorted_data = sorted(self.data)
            n = len(sorted_data)
            if n % 2 == 1:
                self._median = sorted_data[n//2]
            else:
                self._median = (sorted_data[n//2-1] + sorted_data[n//2]) / 2
            print(f"中位数计算完成: {self._median}")
        return self._median
    
    @property
    def std_dev(self):
        """按需计算标准差"""
        if self._std_dev is None:
            print("计算标准差...")
            mean_val = self.mean  # 可能会触发mean的计算
            variance = sum((x - mean_val)**2 for x in self.data) / len(self.data)
            self._std_dev = variance ** 0.5
            print(f"标准差计算完成: {self._std_dev}")
        return self._std_dev
    
    def invalidate_cache(self):
        """使缓存失效"""
        self._mean = None
        self._median = None
        self._std_dev = None
        print("缓存已清除")

def demo_lazy_calculation():
    """演示按需计算的效果"""
    data = [random.randint(0, 100) for _ in range(10000)]
    calculator = LazyCalculator(data)
    
    print("计算器已创建，但尚未进行任何计算")
    
    print("\n只请求平均值...")
    mean_val = calculator.mean
    
    print("\n只请求中位数...")
    median_val = calculator.median
    
    print("\n请求标准差(会复用已计算的平均值)...")
    std_dev = calculator.std_dev
    
    print("\n再次请求平均值(使用缓存)...")
    mean_val2 = calculator.mean
    
    print("\n清除缓存后再次请求平均值...")
    calculator.invalidate_cache()
    mean_val3 = calculator.mean

demo_lazy_loading()
demo_lazy_calculation()
```

### 7.2 使用多级缓存系统

多级缓存可以提供分层性能优化，减少重复计算和I/O操作。

```python
import time
import random
import functools
import os
import pickle
import hashlib

# 内存缓存
class MemoryCache:
    """内存缓存实现"""
    
    def __init__(self, max_size=1000):
        self.max_size = max_size
        self.cache = {}
        self.access_order = []  # 记录访问顺序，用于LRU
    
    def get(self, key):
        if key in self.cache:
            # 更新访问顺序
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def put(self, key, value):
        if key in self.cache:
            # 更新现有项
            self.cache[key] = value
            self.access_order.remove(key)
            self.access_order.append(key)
        else:
            # 添加新项
            if len(self.cache) >= self.max_size:
                # 移除最少使用的项
                oldest = self.access_order.pop(0)
                del self.cache[oldest]
            
            self.cache[key] = value
            self.access_order.append(key)
    
    def clear(self):
        self.cache.clear()
        self.access_order.clear()

# 磁盘缓存
class DiskCache:
    """磁盘缓存实现"""
    
    def __init__(self, cache_dir="cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _key_to_path(self, key):
        """将键转换为文件路径"""
        # 使用哈希确保文件名有效且均匀分布
        key_hash = hashlib.md5(str(key).encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{key_hash}.cache")
    
    def get(self, key):
        path = self._key_to_path(key)
        if os.path.exists(path):
            try:
                with open(path, 'rb') as f:
                    data = pickle.load(f)
                    # 检查是否过期（示例：1小时后过期）
                    if time.time() - data['timestamp'] < 3600:
                        return data['value']
                    else:
                        # 过期则删除
                        os.remove(path)
            except (pickle.PickleError, EOFError):
                # 损坏的缓存文件，删除
                try:
                    os.remove(path)
                except:
                    pass
        return None
    
    def put(self, key, value):
        path = self._key_to_path(key)
        try:
            with open(path, 'wb') as f:
                pickle.dump({
                    'value': value,
                    'timestamp': time.time()
                }, f)
        except (pickle.PickleError, IOError):
            # 缓存写入失败，忽略
            pass
    
    def clear(self):
        """清除所有缓存文件"""
        for filename in os.listdir(self.cache_dir):
            os.remove(os.path.join(self.cache_dir, filename))

# 多级缓存
class MultiLevelCache:
    """多级缓存系统"""
    
    def __init__(self, memory_size=1000, disk_dir="cache"):
        self.memory_cache = MemoryCache(memory_size)
        self.disk_cache = DiskCache(disk_dir)
        self.stats = {
            'memory_hits': 0,
            'disk_hits': 0,
            'misses': 0
        }
    
    def get(self, key):
        # 先检查内存缓存
        value = self.memory_cache.get(key)
        if value is not None:
            self.stats['memory_hits'] += 1
            return value
        
        # 再检查磁盘缓存
        value = self.disk_cache.get(key)
        if value is not None:
            self.stats['disk_hits'] += 1
            # 将磁盘缓存的数据加载到内存缓存
            self.memory_cache.put(key, value)
            return value
        
        # 都没找到
        self.stats['misses'] += 1
        return None
    
    def put(self, key, value):
        # 同时存入两级缓存
        self.memory_cache.put(key, value)
        self.disk_cache.put(key, value)
    
    def get_stats(self):
        total = sum(self.stats.values())
        if total == 0:
            return self.stats
        
        stats = self.stats.copy()
        stats['memory_hit_rate'] = stats['memory_hits'] / total
        stats['disk_hit_rate'] = stats['disk_hits'] / total
        stats['total_hit_rate'] = (stats['memory_hits'] + stats['disk_hits']) / total
        return stats

# 缓存装饰器
def multi_level_cached(memory_size=1000, disk_dir="cache"):
    """多级缓存装饰器"""
    cache = MultiLevelCache(memory_size, disk_dir)
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 生成键
            key = str(args) + str(sorted(kwargs.items()))
            
            # 尝试从缓存获取
            result = cache.get(key)
            if result is not None:
                return result
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 存入缓存
            cache.put(key, result)
            
            return result
        
        # 添加获取统计的方法
        wrapper.cache_stats = lambda: cache.get_stats()
        wrapper.cache_clear = lambda: cache.memory_cache.clear() or cache.disk_cache.clear()
        
        return wrapper
    return decorator

# 测试多级缓存系统
def test_multi_level_cache():
    """测试多级缓存系统"""
    
    # 定义一个计算密集型函数
    @multi_level_cached(memory_size=100, disk_dir="test_cache")
    def expensive_computation(n, operation="square"):
        """模拟耗时计算"""
        time.sleep(0.1)  # 模拟计算时间
        
        if operation == "square":
            return [i * i for i in range(n)]
        elif operation == "cube":
            return [i * i * i for i in range(n)]
        else:
            return [i for i in range(n)]
    
    print("测试多级缓存系统")
    
    # 第一次调用 - 无缓存
    start = time.time()
    result1 = expensive_computation(1000, "square")
    first_call_time = time.time() - start
    print(f"第一次调用时间: {first_call_time:.4f}秒")
    
    # 第二次调用相同参数 - 内存缓存
    start = time.time()
    result2 = expensive_computation(1000, "square")
    second_call_time = time.time() - start
    print(f"第二次调用时间: {second_call_time:.6f}秒")
    
    # 第三次调用不同参数 - 无缓存
    start = time.time()
    result3 = expensive_computation(1000, "cube")
    third_call_time = time.time() - start
    print(f"第三次调用时间: {third_call_time:.4f}秒")
    
    # 再次调用第一次的参数 - 可能从磁盘缓存恢复
    start = time.time()
    result4 = expensive_computation(1000, "square")
    fourth_call_time = time.time() - start
    print(f"第四次调用时间: {fourth_call_time:.6f}秒")
    
    # 打印缓存统计
    stats = expensive_computation.cache_stats()
    print("\n缓存统计:")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"{key}: {value:.4f}")
        else:
            print(f"{key}: {value}")

# 实际应用示例
class DatabaseQuerySimulator:
    """模拟数据库查询和缓存"""
    
    def __init__(self):
        self.cache = MultiLevelCache()
    
    def query_database(self, table, conditions):
        """模拟数据库查询"""
        # 检查缓存
        cache_key = f"{table}:{str(sorted(conditions.items()))}"
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            print(f"从缓存获取 {table} 数据")
            return cached_result
        
        # 模拟数据库查询
        print(f"查询数据库 {table} 表...")
        time.sleep(0.2)  # 模拟查询延迟
        
        # 生成模拟数据
        result = [f"row_{i}_{random.randint(1000, 9999)}" for i in range(100)]
        
        # 存入缓存
        self.cache.put(cache_key, result)
        return result
    
    def get_cache_stats(self):
        """获取缓存统计"""
        return self.cache.get_stats()

def test_database_caching():
    """测试数据库查询缓存"""
    print("\n测试数据库查询缓存")
    
    db = DatabaseQuerySimulator()
    
    # 第一次查询
    start = time.time()
    data1 = db.query_database("users", {"age_gt": 18, "status": "active"})
    first_query_time = time.time() - start
    print(f"第一次查询时间: {first_query_time:.4f}秒")
    
    # 第二次相同查询
    start = time.time()
    data2 = db.query_database("users", {"age_gt": 18, "status": "active"})
    second_query_time = time.time() - start
    print(f"第二次查询时间: {second_query_time:.6f}秒")
    
    # 不同查询
    start = time.time()
    data3 = db.query_database("products", {"price_lt": 100})
    third_query_time = time.time() - start
    print(f"第三次查询时间: {third_query_time:.4f}秒")
    
    # 打印统计
    stats = db.get_cache_stats()
    print("\n缓存统计:")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"{key}: {value:.4f}")
        else:
            print(f"{key}: {value}")

test_multi_level_cache()
test_database_caching()
```

通过这份Python高级性能优化指南，您可以掌握Python内存管理的深层机制、使用专业工具进行性能分析、选择合适的数据结构和算法优化技巧、利用缓存和延迟加载减少计算开销，以及集成高性能第三方库。这些技能将使您能够编写出高效、可扩展的Python应用程序，在面试和实际工作中都能展现出专业水准的Python性能优化能力。