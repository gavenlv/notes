"""
第2章：单例模式 - 示例代码

本文件包含了第2章中提到的所有示例代码，用于演示单例模式的各种实现方式和应用场景。
"""

print("=== 单例模式示例 ===\n")

# 1. 使用__new__方法实现单例
print("1. 使用__new__方法实现单例:")

class Singleton:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.value = 0
            self.initialized = True
    
    def increase(self):
        self.value += 1

# 测试
s1 = Singleton()
s2 = Singleton()

print(f"s1和s2是同一个实例: {id(s1) == id(s2)}")  # 输出: True
print(f"s1的初始值: {s1.value}")  # 输出: 0
s1.increase()
print(f"s2的值: {s2.value}")  # 输出: 1

# 2. 使用装饰器实现单例
print("\n2. 使用装饰器实现单例:")

def singleton(cls):
    instances = {}
    
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance

@singleton
class SingletonClass:
    def __init__(self):
        self.value = 0
    
    def increase(self):
        self.value += 1

# 测试
s3 = SingletonClass()
s4 = SingletonClass()

print(f"s3和s4是同一个实例: {id(s3) == id(s4)}")  # 输出: True
print(f"s3的初始值: {s3.value}")  # 输出: 0
s3.increase()
print(f"s4的值: {s4.value}")  # 输出: 1

# 3. 使用元类实现单例
print("\n3. 使用元类实现单例:")

class SingletonMeta(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class MetaSingleton(metaclass=SingletonMeta):
    def __init__(self):
        self.value = 0
    
    def increase(self):
        self.value += 1

# 测试
s5 = MetaSingleton()
s6 = MetaSingleton()

print(f"s5和s6是同一个实例: {id(s5) == id(s6)}")  # 输出: True
print(f"s5的初始值: {s5.value}")  # 输出: 0
s5.increase()
print(f"s6的值: {s6.value}")  # 输出: 1

# 4. 数据库连接池示例
print("\n4. 数据库连接池示例:")

import threading

class DatabaseConnectionPool:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # 双重检查锁定
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.connections = []
            self.max_connections = 10
            self.initialized = True
    
    def get_connection(self):
        if not self.connections:
            return self._create_connection()
        return self.connections.pop()
    
    def release_connection(self, connection):
        if len(self.connections) < self.max_connections:
            self.connections.append(connection)
    
    def _create_connection(self):
        # 实际应用中会创建真实的数据库连接
        return f"数据库连接{len(self.connections) + 1}"

# 使用示例
pool1 = DatabaseConnectionPool()
pool2 = DatabaseConnectionPool()

conn1 = pool1.get_connection()
conn2 = pool2.get_connection()

print(f"pool1和pool2是同一个实例: {id(pool1) == id(pool2)}")  # 输出: True
print(f"从池1获取连接: {conn1}")
print(f"从池2获取连接: {conn2}")

pool1.release_connection(conn1)
pool2.release_connection(conn2)

# 5. 日志记录器示例
print("\n5. 日志记录器示例:")

import datetime

class Logger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.logs = []
            self.initialized = True
    
    def log(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        print(log_entry)
    
    def get_logs(self):
        return self.logs

# 使用示例
logger1 = Logger()
logger2 = Logger()

print(f"logger1和logger2是同一个实例: {id(logger1) == id(logger2)}")  # 输出: True
logger1.log("系统启动")
logger2.log("用户登录")
logger1.log("系统关闭")

print("\n所有日志:")
for log in logger1.get_logs():
    print(log)

# 6. 配置管理器示例
print("\n6. 配置管理器示例:")

import json
import os

class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.config = {}
            self.config_file = "config.json"
            self.load_config()
            self.initialized = True
    
    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "database": {
                    "host": "localhost",
                    "port": 3306,
                    "user": "root",
                    "password": "123456"
                },
                "server": {
                    "host": "localhost",
                    "port": 8080
                }
            }
            self.save_config()
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value
        self.save_config()

# 使用示例
config1 = ConfigManager()
config2 = ConfigManager()

print(f"config1和config2是同一个实例: {id(config1) == id(config2)}")  # 输出: True
print(f"数据库主机: {config1.get('database')['host']}")
config2.set('database', 'host', '192.168.1.100')
print(f"更新后的数据库主机: {config1.get('database')['host']}")

# 清理配置文件
if os.path.exists("config.json"):
    os.remove("config.json")

# 7. 线程安全的单例模式示例
print("\n7. 线程安全的单例模式示例:")

class ThreadSafeSingleton:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # 双重检查锁定
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.value = 0
            self.initialized = True
    
    def increase(self):
        self.value += 1

# 测试线程安全性
import time
import random

def worker(singleton_instance, worker_id):
    for _ in range(100):
        with singleton_instance._lock:
            current_value = singleton_instance.value
            time.sleep(0.001)  # 模拟一些处理时间
            singleton_instance.value = current_value + 1

if __name__ == "__main__":
    singleton = ThreadSafeSingleton()
    
    threads = []
    for i in range(10):
        t = threading.Thread(target=worker, args=(singleton, i))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print(f"最终值应该是1000，实际是: {singleton.value}")

# 8. 使用装饰器实现线程安全
print("\n8. 使用装饰器实现线程安全:")

def thread_safe_singleton(cls):
    instances = {}
    lock = threading.Lock()
    
    def get_instance(*args, **kwargs):
        if cls not in instances:
            with lock:
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance

@thread_safe_singleton
class ThreadSafeSingletonClass:
    def __init__(self):
        self.value = 0
    
    def increase(self):
        self.value += 1

# 测试
s7 = ThreadSafeSingletonClass()
s8 = ThreadSafeSingletonClass()

print(f"s7和s8是同一个实例: {id(s7) == id(s8)}")  # 输出: True

# 总结
print("\n=== 总结 ===")
print("单例模式确保一个类只有一个实例，并提供全局访问点。")
print("在Python中，可以使用多种方式实现单例模式:")
print("1. 使用__new__方法")
print("2. 使用装饰器")
print("3. 使用元类")
print("4. 使用模块")
print("5. 使用类方法")
print("\n在多线程环境下，需要考虑线程安全问题，可以使用锁机制。")
print("单例模式适用于需要频繁创建和销毁的对象，或者需要共享状态的场景。")