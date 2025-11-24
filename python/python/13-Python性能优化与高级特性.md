# 第13章 Python性能优化与高级特性

## 目录
- [Python性能分析工具](#python性能分析工具)
- [算法优化](#算法优化)
- [数据结构优化](#数据结构优化)
- [内存管理优化](#内存管理优化)
- [并发与并行处理](#并发与并行处理)
- [Cython加速Python](#cython加速python)
- [NumPy向量化操作](#numpy向量化操作)
- [装饰器高级用法](#装饰器高级用法)
- [上下文管理器](#上下文管理器)
- [元类编程](#元类编程)
- [描述符](#描述符)
- [生成器与协程](#生成器与协程)
- [异步编程](#异步编程)
- [性能测试与基准测试](#性能测试与基准测试)

## Python性能分析工具

### timeit模块
```python
import timeit

# 测试代码执行时间
def test_list_comprehension():
    return [i**2 for i in range(1000)]

def test_loop():
    result = []
    for i in range(1000):
        result.append(i**2)
    return result

# 比较两种方法的性能
time1 = timeit.timeit(test_list_comprehension, number=10000)
time2 = timeit.timeit(test_loop, number=10000)

print(f"列表推导式耗时: {time1:.6f}秒")
print(f"循环耗时: {time2:.6f}秒")
```

### cProfile性能分析
```python
import cProfile
import pstats

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def main():
    result = [fibonacci(i) for i in range(30)]
    return sum(result)

# 性能分析
if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    
    main()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # 显示前10个最耗时的函数
```

### line_profiler行级分析
```python
# 安装: pip install line_profiler
# 使用: kernprof -l -v script.py

@profile
def process_data(data):
    result = []
    for item in data:
        # 分析每一行的执行时间
        processed = item * 2
        if processed > 100:
            result.append(processed)
    return result

if __name__ == "__main__":
    data = list(range(10000))
    result = process_data(data)
```

### memory_profiler内存分析
```python
# 安装: pip install memory_profiler
# 使用: python -m memory_profiler script.py

from memory_profiler import profile

@profile
def memory_intensive_function():
    # 创建大列表
    big_list = [i for i in range(1000000)]
    
    # 创建字典
    big_dict = {i: i**2 for i in range(100000)}
    
    # 删除变量释放内存
    del big_list
    del big_dict
    
    return "处理完成"

if __name__ == "__main__":
    result = memory_intensive_function()
    print(result)
```

## 算法优化

### 时间复杂度优化
```python
# 低效的查找算法 O(n^2)
def find_duplicates_slow(arr):
    duplicates = []
    for i in range(len(arr)):
        for j in range(i+1, len(arr)):
            if arr[i] == arr[j] and arr[i] not in duplicates:
                duplicates.append(arr[i])
    return duplicates

# 高效的查找算法 O(n)
def find_duplicates_fast(arr):
    seen = set()
    duplicates = set()
    for item in arr:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    return list(duplicates)

# 测试性能差异
import random
test_data = [random.randint(1, 1000) for _ in range(10000)]

# 比较两种方法的性能
import timeit
time_slow = timeit.timeit(lambda: find_duplicates_slow(test_data[:1000]), number=10)
time_fast = timeit.timeit(lambda: find_duplicates_fast(test_data[:1000]), number=10)

print(f"慢速算法耗时: {time_slow:.6f}秒")
print(f"快速算法耗时: {time_fast:.6f}秒")
```

### 缓存优化
```python
from functools import lru_cache
import time

# 使用LRU缓存优化递归函数
@lru_cache(maxsize=128)
def fibonacci_cached(n):
    if n <= 1:
        return n
    return fibonacci_cached(n-1) + fibonacci_cached(n-2)

# 无缓存版本
def fibonacci_uncached(n):
    if n <= 1:
        return n
    return fibonacci_uncached(n-1) + fibonacci_uncached(n-2)

# 性能对比
start_time = time.time()
result1 = fibonacci_cached(35)
cached_time = time.time() - start_time

start_time = time.time()
result2 = fibonacci_uncached(35)
uncached_time = time.time() - start_time

print(f"缓存版本耗时: {cached_time:.6f}秒")
print(f"无缓存版本耗时: {uncached_time:.6f}秒")
```

## 数据结构优化

### 使用适当的数据结构
```python
# 列表 vs 集合 vs 字典的查找性能
import timeit

# 创建测试数据
data_list = list(range(10000))
data_set = set(range(10000))
data_dict = {i: i for i in range(10000)}

# 查找元素
def lookup_list():
    return 9999 in data_list

def lookup_set():
    return 9999 in data_set

def lookup_dict():
    return 9999 in data_dict

# 性能测试
time_list = timeit.timeit(lookup_list, number=1000)
time_set = timeit.timeit(lookup_set, number=1000)
time_dict = timeit.timeit(lookup_dict, number=1000)

print(f"列表查找耗时: {time_list:.6f}秒")
print(f"集合查找耗时: {time_set:.6f}秒")
print(f"字典查找耗时: {time_dict:.6f}秒")
```

### collections模块优化
```python
from collections import deque, defaultdict, Counter, namedtuple
import timeit

# 使用deque优化队列操作
def test_deque():
    dq = deque()
    for i in range(10000):
        dq.appendleft(i)
    while dq:
        dq.pop()

def test_list():
    lst = []
    for i in range(10000):
        lst.insert(0, i)
    while lst:
        lst.pop()

# 性能对比
time_deque = timeit.timeit(test_deque, number=100)
time_list = timeit.timeit(test_list, number=100)

print(f"deque操作耗时: {time_deque:.6f}秒")
print(f"list操作耗时: {time_list:.6f}秒")

# 使用defaultdict避免键检查
def count_words_defaultdict(text):
    word_count = defaultdict(int)
    for word in text.split():
        word_count[word] += 1
    return dict(word_count)

def count_words_regular(text):
    word_count = {}
    for word in text.split():
        if word in word_count:
            word_count[word] += 1
        else:
            word_count[word] = 1
    return word_count

# 使用namedtuple替代普通类
Point = namedtuple('Point', ['x', 'y'])

# 普通类
class RegularPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# 性能测试
point1 = Point(1, 2)
point2 = RegularPoint(1, 2)

print(f"namedtuple内存占用: {point1.__sizeof__()}")
print(f"普通类内存占用: {point2.__sizeof__()}")
```

## 内存管理优化

### 对象复用
```python
import sys

# 字符串驻留
a = "hello"
b = "hello"
print(f"字符串驻留: {a is b}")  # True

# 小整数缓存 (-5到256)
x = 100
y = 100
print(f"小整数缓存: {x is y}")  # True

z = 1000
w = 1000
print(f"大整数不缓存: {z is w}")  # False
```

### 弱引用避免循环引用
```python
import weakref
import gc

class Parent:
    def __init__(self, name):
        self.name = name
        self.children = []
    
    def add_child(self, child):
        self.children.append(child)
        # 使用弱引用避免循环引用
        child.parent = weakref.ref(self)

class Child:
    def __init__(self, name):
        self.name = name
        self.parent = None
    
    def get_parent(self):
        if self.parent is not None:
            return self.parent()  # 调用弱引用
        return None

# 测试循环引用
parent = Parent("父节点")
child = Child("子节点")
parent.add_child(child)

print(f"子节点的父节点: {child.get_parent().name}")

# 删除强引用
del parent
gc.collect()  # 强制垃圾回收

print(f"父节点被回收后: {child.get_parent()}")  # None
```

### 内存映射文件
```python
import mmap
import os

# 创建大文件并使用内存映射
def create_large_file(filename, size):
    with open(filename, 'wb') as f:
        f.write(b'0' * size)

def read_with_mmap(filename):
    with open(filename, 'r+b') as f:
        with mmap.mmap(f.fileno(), 0) as mm:
            # 可以像操作bytes一样操作文件
            return mm[:10]  # 读取前10个字节

# 创建1MB的文件
filename = 'large_file.txt'
create_large_file(filename, 1024*1024)

# 使用内存映射读取
data = read_with_mmap(filename)
print(f"读取的数据: {data}")

# 清理
os.remove(filename)
```

## 并发与并行处理

### 多线程处理I/O密集型任务
```python
import threading
import time
import requests

# I/O密集型任务示例
def fetch_url(url):
    try:
        response = requests.get(url, timeout=5)
        return f"{url}: {response.status_code}"
    except Exception as e:
        return f"{url}: 错误 - {str(e)}"

# 单线程处理
def sequential_fetch(urls):
    results = []
    for url in urls:
        result = fetch_url(url)
        results.append(result)
    return results

# 多线程处理
def concurrent_fetch(urls):
    threads = []
    results = []
    
    def worker(url, results, index):
        result = fetch_url(url)
        results.append((index, result))
    
    # 创建线程
    for i, url in enumerate(urls):
        thread = threading.Thread(target=worker, args=(url, results, i))
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    # 按顺序排列结果
    results.sort(key=lambda x: x[0])
    return [result[1] for result in results]

# 测试
urls = [
    'https://httpbin.org/delay/1',
    'https://httpbin.org/delay/2',
    'https://httpbin.org/status/200',
    'https://httpbin.org/status/404'
]

start_time = time.time()
sequential_results = sequential_fetch(urls)
sequential_time = time.time() - start_time

start_time = time.time()
concurrent_results = concurrent_fetch(urls)
concurrent_time = time.time() - start_time

print(f"单线程耗时: {sequential_time:.2f}秒")
print(f"多线程耗时: {concurrent_time:.2f}秒")
```

### 多进程处理CPU密集型任务
```python
import multiprocessing
import time

# CPU密集型任务
def cpu_bound_task(n):
    """计算斐波那契数列"""
    def fib(x):
        if x <= 1:
            return x
        return fib(x-1) + fib(x-2)
    return fib(n)

# 单进程处理
def sequential_processing(numbers):
    results = []
    for num in numbers:
        result = cpu_bound_task(num)
        results.append(result)
    return results

# 多进程处理
def parallel_processing(numbers):
    with multiprocessing.Pool() as pool:
        results = pool.map(cpu_bound_task, numbers)
    return results

# 测试
numbers = [30, 31, 32, 33, 34]

start_time = time.time()
sequential_results = sequential_processing(numbers)
sequential_time = time.time() - start_time

start_time = time.time()
parallel_results = parallel_processing(numbers)
parallel_time = time.time() - start_time

print(f"单进程耗时: {sequential_time:.2f}秒")
print(f"多进程耗时: {parallel_time:.2f}秒")
print(f"加速比: {sequential_time/parallel_time:.2f}x")
```

### asyncio异步处理
```python
import asyncio
import aiohttp
import time

# 异步HTTP请求
async def fetch_async(session, url):
    try:
        async with session.get(url, timeout=5) as response:
            return f"{url}: {response.status}"
    except Exception as e:
        return f"{url}: 错误 - {str(e)}"

async def fetch_all_async(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_async(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
    return results

# 同步版本对比
def fetch_sync(url):
    try:
        response = requests.get(url, timeout=5)
        return f"{url}: {response.status_code}"
    except Exception as e:
        return f"{url}: 错误 - {str(e)}"

def fetch_all_sync(urls):
    return [fetch_sync(url) for url in urls]

# 测试
urls = [
    'https://httpbin.org/delay/1',
    'https://httpbin.org/delay/1',
    'https://httpbin.org/status/200',
    'https://httpbin.org/status/404'
]

# 同步执行
start_time = time.time()
sync_results = fetch_all_sync(urls)
sync_time = time.time() - start_time

# 异步执行
start_time = time.time()
async_results = asyncio.run(fetch_all_async(urls))
async_time = time.time() - start_time

print(f"同步执行耗时: {sync_time:.2f}秒")
print(f"异步执行耗时: {async_time:.2f}秒")
```

## Cython加速Python

### 安装和基本使用
```bash
# 安装Cython
pip install cython

# 创建setup.py文件
```

```python
# setup.py
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize("fibonacci.pyx")
)
```

```cython
# fibonacci.pyx - Cython版本的斐波那契数列
def fibonacci_cython(int n):
    cdef int a = 0
    cdef int b = 1
    cdef int i
    
    if n <= 1:
        return n
    
    for i in range(2, n+1):
        a, b = b, a + b
    
    return b

# Python版本用于对比
def fibonacci_python(n):
    if n <= 1:
        return n
    return fibonacci_python(n-1) + fibonacci_python(n-2)
```

```python
# 编译和使用
# python setup.py build_ext --inplace

import time
from fibonacci import fibonacci_cython, fibonacci_python

# 性能对比
n = 35

start_time = time.time()
result_py = fibonacci_python(n)
time_py = time.time() - start_time

start_time = time.time()
result_cy = fibonacci_cython(n)
time_cy = time.time() - start_time

print(f"Python版本耗时: {time_py:.6f}秒")
print(f"Cython版本耗时: {time_cy:.6f}秒")
print(f"加速比: {time_py/time_cy:.2f}x")
```

## NumPy向量化操作

### 数组操作优化
```python
import numpy as np
import timeit

# 创建大型数组
size = 1000000
arr1 = np.random.rand(size)
arr2 = np.random.rand(size)

# 向量化操作 vs 循环
def vectorized_operation():
    return arr1 * arr2 + np.sin(arr1)

def loop_operation():
    result = np.zeros(size)
    for i in range(size):
        result[i] = arr1[i] * arr2[i] + np.sin(arr1[i])
    return result

# 性能对比
time_vectorized = timeit.timeit(vectorized_operation, number=10)
time_loop = timeit.timeit(loop_operation, number=10)

print(f"向量化操作耗时: {time_vectorized:.6f}秒")
print(f"循环操作耗时: {time_loop:.6f}秒")
print(f"加速比: {time_loop/time_vectorized:.2f}x")
```

### 广播机制
```python
import numpy as np

# 广播机制示例
matrix = np.random.rand(1000, 1000)
vector = np.random.rand(1000)

# 使用广播进行矩阵运算
result = matrix + vector  # vector会自动扩展到矩阵的每一行

# 传统方法需要显式复制
vector_expanded = np.tile(vector, (1000, 1))
result_traditional = matrix + vector_expanded

# 验证结果相同
print(f"结果相同: {np.allclose(result, result_traditional)}")

# 性能对比
import timeit

def broadcast_method():
    return matrix + vector

def traditional_method():
    return matrix + np.tile(vector, (1000, 1))

time_broadcast = timeit.timeit(broadcast_method, number=100)
time_traditional = timeit.timeit(traditional_method, number=100)

print(f"广播方法耗时: {time_broadcast:.6f}秒")
print(f"传统方法耗时: {time_traditional:.6f}秒")
```

## 装饰器高级用法

### 类装饰器
```python
class CountCalls:
    def __init__(self, func):
        self.func = func
        self.count = 0
    
    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"{self.func.__name__} 被调用了 {self.count} 次")
        return self.func(*args, **kwargs)

@CountCalls
def say_hello(name):
    return f"Hello, {name}!"

# 测试
print(say_hello("Alice"))
print(say_hello("Bob"))
print(say_hello("Charlie"))
```

### 带参数的装饰器
```python
import functools
import time

def retry(max_attempts=3, delay=1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise e
                    print(f"第{attempt+1}次尝试失败: {e}")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

@retry(max_attempts=3, delay=0.5)
def unreliable_function():
    import random
    if random.random() < 0.7:  # 70%概率失败
        raise Exception("随机错误")
    return "成功!"

# 测试
try:
    result = unreliable_function()
    print(result)
except Exception as e:
    print(f"最终失败: {e}")
```

### 属性装饰器
```python
class Circle:
    def __init__(self, radius):
        self._radius = radius
    
    @property
    def radius(self):
        """获取半径"""
        return self._radius
    
    @radius.setter
    def radius(self, value):
        """设置半径"""
        if value < 0:
            raise ValueError("半径不能为负数")
        self._radius = value
    
    @property
    def area(self):
        """计算面积（只读属性）"""
        return 3.14159 * self._radius ** 2
    
    @property
    def diameter(self):
        """计算直径（只读属性）"""
        return 2 * self._radius

# 使用示例
circle = Circle(5)
print(f"半径: {circle.radius}")
print(f"直径: {circle.diameter}")
print(f"面积: {circle.area}")

# 修改半径
circle.radius = 10
print(f"新半径: {circle.radius}")
print(f"新面积: {circle.area}")
```

## 上下文管理器

### 自定义上下文管理器
```python
import time

class Timer:
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.elapsed_time = self.end_time - self.start_time
        print(f"执行时间: {self.elapsed_time:.6f}秒")
        return False  # 不抑制异常

# 使用自定义上下文管理器
with Timer() as timer:
    # 模拟一些耗时操作
    time.sleep(1)
    result = sum(range(1000000))
    print(f"计算结果: {result}")
```

### contextlib模块
```python
from contextlib import contextmanager, suppress
import os

@contextmanager
def change_directory(path):
    """临时切换目录的上下文管理器"""
    old_path = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(old_path)

# 使用示例
print(f"当前目录: {os.getcwd()}")
with change_directory("../"):
    print(f"切换后目录: {os.getcwd()}")
print(f"恢复后目录: {os.getcwd()}")

# 使用suppress忽略特定异常
with suppress(FileNotFoundError):
    with open("不存在的文件.txt", "r") as f:
        content = f.read()
    print(content)  # 这行不会执行
print("程序继续执行...")
```

## 元类编程

### 基本元类
```python
class SingletonMeta(type):
    """单例模式元类"""
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Database(metaclass=SingletonMeta):
    def __init__(self):
        self.connection = "数据库连接"
    
    def query(self, sql):
        return f"执行查询: {sql}"

# 测试单例模式
db1 = Database()
db2 = Database()
print(f"db1 is db2: {db1 is db2}")  # True
print(db1.query("SELECT * FROM users"))
```

### 属性验证元类
```python
class ValidatedMeta(type):
    """属性验证元类"""
    def __new__(cls, name, bases, attrs):
        # 为所有带验证注解的属性添加验证逻辑
        for key, value in attrs.items():
            if hasattr(value, '_validator'):
                attrs[key] = ValidatedProperty(value, value._validator)
        return super().__new__(cls, name, bases, attrs)

def validator(func):
    """验证器装饰器"""
    func._validator = func
    return func

class ValidatedProperty:
    def __init__(self, default_value, validator):
        self.value = default_value
        self.validator = validator
        self.name = None
    
    def __set_name__(self, owner, name):
        self.name = name
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return self.value
    
    def __set__(self, obj, value):
        if not self.validator(value):
            raise ValueError(f"Invalid value for {self.name}: {value}")
        self.value = value

class Person(metaclass=ValidatedMeta):
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    @validator
    def name_validator(value):
        return isinstance(value, str) and len(value) > 0
    
    @validator
    def age_validator(value):
        return isinstance(value, int) and 0 <= value <= 150

# 使用示例
person = Person("Alice", 25)
print(f"姓名: {person.name}, 年龄: {person.age}")

# 尝试设置无效值
try:
    person.age = -5
except ValueError as e:
    print(f"验证错误: {e}")
```

## 描述符

### 数据描述符
```python
class PositiveInteger:
    def __init__(self, name):
        self.name = name
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.name, 0)
    
    def __set__(self, obj, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f"{self.name} 必须是正整数")
        obj.__dict__[self.name] = value
    
    def __delete__(self, obj):
        del obj.__dict__[self.name]

class Product:
    price = PositiveInteger('price')
    quantity = PositiveInteger('quantity')
    
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity
    
    @property
    def total_value(self):
        return self.price * self.quantity

# 使用示例
product = Product("笔记本电脑", 5000, 10)
print(f"产品: {product.name}")
print(f"单价: {product.price}")
print(f"数量: {product.quantity}")
print(f"总价值: {product.total_value}")

# 尝试设置无效值
try:
    product.price = -100
except ValueError as e:
    print(f"错误: {e}")
```

## 生成器与协程

### 生成器优化内存使用
```python
def fibonacci_generator(n):
    """斐波那契数列生成器"""
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

def fibonacci_list(n):
    """返回斐波那契数列列表"""
    result = []
    a, b = 0, 1
    for _ in range(n):
        result.append(a)
        a, b = b, a + b
    return result

# 内存使用对比
import sys

# 生成器对象
gen = fibonacci_generator(1000000)
print(f"生成器大小: {sys.getsizeof(gen)} bytes")

# 列表对象
lst = fibonacci_list(1000)
print(f"列表大小: {sys.getsizeof(lst)} bytes")

# 使用生成器处理大数据
def process_large_data():
    total = 0
    for num in fibonacci_generator(1000000):
        if num > 1000:
            break
        total += num
    return total

result = process_large_data()
print(f"处理结果: {result}")
```

### 协程通信
```python
def accumulator():
    """累加器协程"""
    total = 0
    try:
        while True:
            value = yield total
            if value is not None:
                total += value
    except GeneratorExit:
        print(f"最终总计: {total}")
        return total

# 使用协程
acc = accumulator()
next(acc)  # 启动协程

print(f"当前总计: {acc.send(10)}")
print(f"当前总计: {acc.send(20)}")
print(f"当前总计: {acc.send(30)}")

acc.close()  # 关闭协程
```

## 异步编程

### async/await语法
```python
import asyncio
import aiohttp
import time

class AsyncDataManager:
    def __init__(self):
        self.data = {}
        self.lock = asyncio.Lock()
    
    async def fetch_and_store(self, session, url, key):
        """异步获取数据并存储"""
        try:
            async with session.get(url) as response:
                data = await response.text()
                # 使用锁确保线程安全
                async with self.lock:
                    self.data[key] = data
                return f"{key}: 成功获取 {len(data)} 字符"
        except Exception as e:
            return f"{key}: 错误 - {str(e)}"
    
    async def process_multiple_urls(self, urls):
        """并发处理多个URL"""
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.fetch_and_store(session, url, key) 
                for key, url in urls.items()
            ]
            results = await asyncio.gather(*tasks)
            return results
    
    def get_data(self, key):
        """获取存储的数据"""
        return self.data.get(key, "未找到数据")

# 使用示例
async def main():
    manager = AsyncDataManager()
    
    urls = {
        'google': 'https://httpbin.org/get',
        'httpbin': 'https://httpbin.org/json',
        'uuid': 'https://httpbin.org/uuid'
    }
    
    start_time = time.time()
    results = await manager.process_multiple_urls(urls)
    elapsed_time = time.time() - start_time
    
    for result in results:
        print(result)
    
    print(f"总耗时: {elapsed_time:.2f}秒")
    
    # 查看存储的数据
    print(f"Google数据长度: {len(manager.get_data('google') or '')}")

# 运行异步主函数
# asyncio.run(main())
```

### 异步迭代器
```python
import asyncio

class AsyncRange:
    def __init__(self, start, stop, step=1):
        self.start = start
        self.stop = stop
        self.step = step
    
    def __aiter__(self):
        return AsyncRangeIterator(self.start, self.stop, self.step)

class AsyncRangeIterator:
    def __init__(self, start, stop, step):
        self.current = start
        self.stop = stop
        self.step = step
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self.current >= self.stop:
            raise StopAsyncIteration
        
        # 模拟异步操作
        await asyncio.sleep(0.01)
        value = self.current
        self.current += self.step
        return value

# 使用异步迭代器
async def process_async_range():
    async for i in AsyncRange(0, 10, 2):
        print(f"处理值: {i}")
        # 模拟处理时间
        await asyncio.sleep(0.1)

# asyncio.run(process_async_range())
```

## 性能测试与基准测试

### pytest-benchmark
```python
# 安装: pip install pytest-benchmark

def bubble_sort(arr):
    """冒泡排序"""
    arr = arr.copy()
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def quick_sort(arr):
    """快速排序"""
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

def test_bubble_sort(benchmark):
    """基准测试冒泡排序"""
    data = list(range(1000, 0, -1))
    result = benchmark(bubble_sort, data)
    assert result == sorted(data)

def test_quick_sort(benchmark):
    """基准测试快速排序"""
    data = list(range(1000, 0, -1))
    result = benchmark(quick_sort, data)
    assert result == sorted(data)
```

### 内存使用测试
```python
import tracemalloc
import gc

def memory_test_function():
    """测试函数的内存使用"""
    # 开始跟踪内存分配
    tracemalloc.start()
    
    # 执行可能消耗内存的操作
    big_list = [i**2 for i in range(100000)]
    big_dict = {i: str(i) for i in range(50000)}
    
    # 获取当前内存使用情况
    current, peak = tracemalloc.get_traced_memory()
    print(f"当前内存使用: {current / 1024 / 1024:.2f} MB")
    print(f"峰值内存使用: {peak / 1024 / 1024:.2f} MB")
    
    # 获取内存使用最多的前10个位置
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    
    print("\n内存使用最多的前5个位置:")
    for stat in top_stats[:5]:
        print(stat)
    
    # 停止跟踪
    tracemalloc.stop()
    
    # 清理
    del big_list, big_dict
    gc.collect()

# 运行内存测试
memory_test_function()
```

## 总结

Python性能优化和高级特性是一个广泛的领域，主要包括以下几个方面：

1. **性能分析**：使用适当的工具识别性能瓶颈
2. **算法优化**：选择合适的数据结构和算法
3. **内存管理**：理解Python的内存模型和垃圾回收机制
4. **并发编程**：根据任务类型选择合适的并发模型
5. **编译优化**：使用Cython等工具加速关键代码
6. **科学计算**：利用NumPy等库进行向量化操作
7. **高级语法**：掌握装饰器、上下文管理器、元类等高级特性
8. **异步编程**：使用async/await提高I/O密集型任务的效率

通过合理运用这些技术和工具，可以显著提升Python应用程序的性能和可维护性。在实际开发中，应该根据具体需求选择合适的优化策略，并始终以性能分析数据为依据进行优化。