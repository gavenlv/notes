#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第6章：性能测试 - 示例代码
本文件包含性能测试的示例代码，涵盖性能测试指标、工具使用、
测试设计和结果分析等内容。
"""

import time
import threading
import random
import statistics
import requests
import json
import sqlite3
import os
import sys
import psutil
import concurrent.futures
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
from urllib.parse import urljoin
import matplotlib.pyplot as plt
import numpy as np

# ============================================================================
# 实验1：性能测试基础 - 响应时间与吞吐量测量
# ============================================================================

@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    response_times: List[float]
    throughput: float  # 每秒请求数
    error_rate: float  # 错误率百分比
    cpu_usage: float   # CPU使用率
    memory_usage: float  # 内存使用率
    timestamp: datetime

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.response_times = []
        self.errors = 0
        self.total_requests = 0
        self.cpu_samples = []
        self.memory_samples = []
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """开始监控"""
        self.start_time = time.time()
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_resources)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        print("性能监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.end_time = time.time()
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("性能监控已停止")
    
    def record_response(self, response_time: float, success: bool = True):
        """记录响应时间"""
        self.response_times.append(response_time)
        self.total_requests += 1
        if not success:
            self.errors += 1
    
    def _monitor_resources(self):
        """监控系统资源"""
        while self.monitoring:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_info = psutil.virtual_memory()
            self.cpu_samples.append(cpu_percent)
            self.memory_samples.append(memory_info.percent)
            time.sleep(0.5)
    
    def get_metrics(self) -> PerformanceMetrics:
        """获取性能指标"""
        if not self.start_time or not self.end_time:
            raise ValueError("监控未完成")
        
        duration = self.end_time - self.start_time
        throughput = self.total_requests / duration if duration > 0 else 0
        error_rate = (self.errors / self.total_requests * 100) if self.total_requests > 0 else 0
        avg_cpu = statistics.mean(self.cpu_samples) if self.cpu_samples else 0
        avg_memory = statistics.mean(self.memory_samples) if self.memory_samples else 0
        
        return PerformanceMetrics(
            response_times=self.response_times,
            throughput=throughput,
            error_rate=error_rate,
            cpu_usage=avg_cpu,
            memory_usage=avg_memory,
            timestamp=datetime.now()
        )
    
    def print_summary(self):
        """打印性能摘要"""
        metrics = self.get_metrics()
        
        print("\n性能测试结果摘要:")
        print(f"测试持续时间: {self.end_time - self.start_time:.2f} 秒")
        print(f"总请求数: {self.total_requests}")
        print(f"成功请求数: {self.total_requests - self.errors}")
        print(f"失败请求数: {self.errors}")
        print(f"错误率: {metrics.error_rate:.2f}%")
        print(f"吞吐量: {metrics.throughput:.2f} 请求/秒")
        
        if metrics.response_times:
            print(f"平均响应时间: {statistics.mean(metrics.response_times):.2f} 毫秒")
            print(f"最小响应时间: {min(metrics.response_times):.2f} 毫秒")
            print(f"最大响应时间: {max(metrics.response_times):.2f} 毫秒")
            print(f"中位数响应时间: {statistics.median(metrics.response_times):.2f} 毫秒")
            print(f"95百分位响应时间: {np.percentile(metrics.response_times, 95):.2f} 毫秒")
            print(f"99百分位响应时间: {np.percentile(metrics.response_times, 99):.2f} 毫秒")
        
        print(f"平均CPU使用率: {metrics.cpu_usage:.2f}%")
        print(f"平均内存使用率: {metrics.memory_usage:.2f}%")
    
    def plot_response_times(self, save_path: str = None):
        """绘制响应时间分布图"""
        if not self.response_times:
            print("没有响应时间数据可绘制")
            return
        
        plt.figure(figsize=(10, 6))
        plt.hist(self.response_times, bins=20, alpha=0.7, color='blue')
        plt.title('响应时间分布')
        plt.xlabel('响应时间 (毫秒)')
        plt.ylabel('频次')
        plt.grid(True)
        
        if save_path:
            plt.savefig(save_path)
            print(f"响应时间分布图已保存到: {save_path}")
        else:
            plt.show()
    
    def plot_timeline(self, save_path: str = None):
        """绘制响应时间时间线图"""
        if not self.response_times:
            print("没有响应时间数据可绘制")
            return
        
        plt.figure(figsize=(12, 6))
        plt.plot(self.response_times, alpha=0.7)
        plt.title('响应时间时间线')
        plt.xlabel('请求序号')
        plt.ylabel('响应时间 (毫秒)')
        plt.grid(True)
        
        if save_path:
            plt.savefig(save_path)
            print(f"响应时间时间线图已保存到: {save_path}")
        else:
            plt.show()

def demo_basic_performance_testing():
    """演示基本性能测试"""
    print("=== 实验1：性能测试基础 - 响应时间与吞吐量测量 ===")
    
    # 创建性能监控器
    monitor = PerformanceMonitor()
    
    # 模拟一个简单的API端点
    def mock_api_endpoint():
        """模拟API端点，随机响应时间"""
        # 模拟处理时间：50ms到500ms之间
        processing_time = random.uniform(50, 500)
        time.sleep(processing_time / 1000)  # 转换为秒
        
        # 模拟5%的失败率
        if random.random() < 0.05:
            return False, processing_time
        return True, processing_time
    
    # 开始监控
    monitor.start_monitoring()
    
    # 模拟100个请求
    print("\n模拟100个API请求...")
    for i in range(100):
        success, response_time = mock_api_endpoint()
        monitor.record_response(response_time, success)
        
        # 模拟用户间隔：10ms到100ms之间
        time.sleep(random.uniform(0.01, 0.1))
    
    # 停止监控
    monitor.stop_monitoring()
    
    # 打印结果
    monitor.print_summary()
    
    # 绘制图表
    try:
        monitor.plot_response_times()
        monitor.plot_timeline()
    except Exception as e:
        print(f"绘图时出错: {e}")
    
    return monitor


# ============================================================================
# 实验2：负载测试 - 并发用户模拟
# ============================================================================

class LoadTester:
    """负载测试器"""
    
    def __init__(self, target_url: str, max_workers: int = 10):
        self.target_url = target_url
        self.max_workers = max_workers
        self.monitor = PerformanceMonitor()
    
    def single_request(self) -> Tuple[bool, float]:
        """发送单个请求"""
        start_time = time.time()
        try:
            response = requests.get(self.target_url, timeout=5)
            response_time = (time.time() - start_time) * 1000  # 转换为毫秒
            return response.status_code == 200, response_time
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            print(f"请求异常: {e}")
            return False, response_time
    
    def run_load_test(self, duration_seconds: int, concurrent_users: int) -> PerformanceMetrics:
        """运行负载测试"""
        print(f"\n开始负载测试: {concurrent_users}个并发用户，持续{duration_seconds}秒")
        
        # 开始监控
        self.monitor.start_monitoring()
        
        # 创建线程池
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            # 提交任务
            futures = []
            end_time = time.time() + duration_seconds
            
            def worker():
                while time.time() < end_time:
                    success, response_time = self.single_request()
                    self.monitor.record_response(response_time, success)
                    time.sleep(random.uniform(0.1, 0.5))  # 随机间隔
            
            # 启动工作线程
            for _ in range(concurrent_users):
                futures.append(executor.submit(worker))
            
            # 等待所有任务完成
            concurrent.futures.wait(futures)
        
        # 停止监控
        self.monitor.stop_monitoring()
        
        # 获取并返回指标
        metrics = self.monitor.get_metrics()
        self.monitor.print_summary()
        
        return metrics
    
    def run_ramp_up_test(self, max_users: int, ramp_up_time: int, test_duration: int):
        """运行渐进式负载测试"""
        print(f"\n开始渐进式负载测试: 从1到{max_users}个用户，{ramp_up_time}秒内线性增加，然后持续{test_duration}秒")
        
        # 开始监控
        self.monitor.start_monitoring()
        
        # 计算用户增加间隔
        user_increment_interval = ramp_up_time / max_users if max_users > 0 else 1
        
        # 创建线程池
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_users) as executor:
            futures = []
            current_users = 0
            start_time = time.time()
            ramp_up_end_time = start_time + ramp_up_time
            test_end_time = ramp_up_end_time + test_duration
            
            def worker():
                while time.time() < test_end_time:
                    success, response_time = self.single_request()
                    self.monitor.record_response(response_time, success)
                    time.sleep(random.uniform(0.1, 0.5))  # 随机间隔
            
            # 渐进式增加用户
            while time.time() < ramp_up_end_time and current_users < max_users:
                futures.append(executor.submit(worker()))
                current_users += 1
                time.sleep(user_increment_interval)
                print(f"当前并发用户数: {current_users}")
            
            # 添加剩余用户
            while current_users < max_users:
                futures.append(executor.submit(worker()))
                current_users += 1
            
            # 等待所有任务完成
            concurrent.futures.wait(futures)
        
        # 停止监控
        self.monitor.stop_monitoring()
        
        # 获取并返回指标
        metrics = self.monitor.get_metrics()
        self.monitor.print_summary()
        
        return metrics

def demo_load_testing():
    """演示负载测试"""
    print("\n=== 实验2：负载测试 - 并发用户模拟 ===")
    
    # 使用公共API进行测试
    target_url = "https://httpbin.org/get"  # 公共测试API
    
    # 创建负载测试器
    load_tester = LoadTester(target_url, max_workers=20)
    
    # 运行不同级别的负载测试
    test_scenarios = [
        {"users": 5, "duration": 10},
        {"users": 10, "duration": 10},
        {"users": 15, "duration": 10}
    ]
    
    results = []
    for scenario in test_scenarios:
        print(f"\n{'='*50}")
        print(f"测试场景: {scenario['users']}个并发用户，持续{scenario['duration']}秒")
        print(f"{'='*50}")
        
        try:
            metrics = load_tester.run_load_test(scenario['duration'], scenario['users'])
            results.append({
                "users": scenario['users'],
                "metrics": metrics
            })
        except Exception as e:
            print(f"测试失败: {e}")
    
    # 运行渐进式负载测试
    print(f"\n{'='*50}")
    print("渐进式负载测试")
    print(f"{'='*50}")
    
    try:
        load_tester.run_ramp_up_test(max_users=20, ramp_up_time=30, test_duration=30)
    except Exception as e:
        print(f"渐进式测试失败: {e}")
    
    # 比较不同场景的结果
    if len(results) > 1:
        print(f"\n{'='*50}")
        print("测试结果比较")
        print(f"{'='*50}")
        print("并发用户数 | 吞吐量(请求/秒) | 平均响应时间(ms) | 错误率(%)")
        print("-" * 60)
        
        for result in results:
            users = result["users"]
            metrics = result["metrics"]
            avg_response_time = statistics.mean(metrics.response_times) if metrics.response_times else 0
            print(f"{users:10} | {metrics.throughput:15.2f} | {avg_response_time:16.2f} | {metrics.error_rate:10.2f}")
    
    return load_tester


# ============================================================================
# 实验3：数据库性能测试
# ============================================================================

class DatabasePerformanceTester:
    """数据库性能测试器"""
    
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.connection = None
        self.monitor = PerformanceMonitor()
        self._setup_database()
    
    def _setup_database(self):
        """设置测试数据库"""
        if self.db_path != ":memory:" and os.path.exists(self.db_path):
            os.remove(self.db_path)
        
        self.connection = sqlite3.connect(self.db_path)
        cursor = self.connection.cursor()
        
        # 创建测试表
        cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            age INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX idx_users_email ON users(email)')
        cursor.execute('CREATE INDEX idx_users_age ON users(age)')
        
        self.connection.commit()
    
    def insert_user(self, name: str, email: str, age: int) -> Tuple[bool, float]:
        """插入用户记录"""
        start_time = time.time()
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                (name, email, age)
            )
            self.connection.commit()
            response_time = (time.time() - start_time) * 1000
            return True, response_time
        except Exception as e:
            self.connection.rollback()
            response_time = (time.time() - start_time) * 1000
            print(f"插入用户失败: {e}")
            return False, response_time
    
    def select_user_by_id(self, user_id: int) -> Tuple[bool, float, Optional[Dict]]:
        """根据ID查询用户"""
        start_time = time.time()
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            response_time = (time.time() - start_time) * 1000
            
            if user:
                user_data = {
                    "id": user[0],
                    "name": user[1],
                    "email": user[2],
                    "age": user[3],
                    "created_at": user[4]
                }
                return True, response_time, user_data
            else:
                return False, response_time, None
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            print(f"查询用户失败: {e}")
            return False, response_time, None
    
    def select_users_by_age_range(self, min_age: int, max_age: int) -> Tuple[bool, float, List[Dict]]:
        """根据年龄范围查询用户"""
        start_time = time.time()
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE age BETWEEN ? AND ?",
                (min_age, max_age)
            )
            users = cursor.fetchall()
            response_time = (time.time() - start_time) * 1000
            
            users_data = []
            for user in users:
                users_data.append({
                    "id": user[0],
                    "name": user[1],
                    "email": user[2],
                    "age": user[3],
                    "created_at": user[4]
                })
            
            return True, response_time, users_data
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            print(f"查询用户失败: {e}")
            return False, response_time, []
    
    def run_insert_test(self, num_records: int) -> PerformanceMetrics:
        """运行插入性能测试"""
        print(f"\n开始插入性能测试: 插入{num_records}条记录")
        
        # 开始监控
        self.monitor.start_monitoring()
        
        # 生成测试数据并插入
        for i in range(num_records):
            name = f"用户{i}"
            email = f"user{i}@example.com"
            age = random.randint(18, 65)
            
            success, response_time = self.insert_user(name, email, age)
            self.monitor.record_response(response_time, success)
        
        # 停止监控
        self.monitor.stop_monitoring()
        
        # 获取并返回指标
        metrics = self.monitor.get_metrics()
        self.monitor.print_summary()
        
        return metrics
    
    def run_select_test(self, num_queries: int) -> PerformanceMetrics:
        """运行查询性能测试"""
        print(f"\n开始查询性能测试: 执行{num_queries}次查询")
        
        # 确保有数据可查询
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("没有数据可查询，先插入一些测试数据")
            self.run_insert_test(100)
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
        
        # 开始监控
        self.monitor.start_monitoring()
        
        # 执行查询
        for i in range(num_queries):
            # 随机选择查询类型
            query_type = random.choice(["by_id", "by_age_range"])
            
            if query_type == "by_id":
                # 根据ID查询
                user_id = random.randint(1, count)
                success, response_time, _ = self.select_user_by_id(user_id)
            else:
                # 根据年龄范围查询
                min_age = random.randint(18, 40)
                max_age = random.randint(41, 65)
                success, response_time, _ = self.select_users_by_age_range(min_age, max_age)
            
            self.monitor.record_response(response_time, success)
        
        # 停止监控
        self.monitor.stop_monitoring()
        
        # 获取并返回指标
        metrics = self.monitor.get_metrics()
        self.monitor.print_summary()
        
        return metrics
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()

def demo_database_performance_testing():
    """演示数据库性能测试"""
    print("\n=== 实验3：数据库性能测试 ===")
    
    # 创建数据库性能测试器
    db_tester = DatabasePerformanceTester("test_performance.db")
    
    try:
        # 运行插入性能测试
        insert_metrics = db_tester.run_insert_test(1000)
        
        # 运行查询性能测试
        select_metrics = db_tester.run_select_test(500)
        
        # 比较插入和查询性能
        print(f"\n{'='*50}")
        print("数据库操作性能比较")
        print(f"{'='*50}")
        print("操作类型 | 吞吐量(操作/秒) | 平均响应时间(ms) | 错误率(%)")
        print("-" * 60)
        
        insert_avg_time = statistics.mean(insert_metrics.response_times) if insert_metrics.response_times else 0
        select_avg_time = statistics.mean(select_metrics.response_times) if select_metrics.response_times else 0
        
        print(f"{'插入':8} | {insert_metrics.throughput:15.2f} | {insert_avg_time:16.2f} | {insert_metrics.error_rate:10.2f}")
        print(f"{'查询':8} | {select_metrics.throughput:15.2f} | {select_avg_time:16.2f} | {select_metrics.error_rate:10.2f}")
        
    finally:
        # 清理资源
        db_tester.close()
        if os.path.exists("test_performance.db"):
            os.remove("test_performance.db")
    
    return db_tester


# ============================================================================
# 实验4：前端性能测试
# ============================================================================

class FrontendPerformanceTester:
    """前端性能测试器"""
    
    def __init__(self, target_url: str):
        self.target_url = target_url
        self.monitor = PerformanceMonitor()
    
    def measure_page_load_time(self) -> Dict[str, Any]:
        """测量页面加载时间"""
        print(f"\n测量页面加载时间: {self.target_url}")
        
        # 开始监控
        self.monitor.start_monitoring()
        
        start_time = time.time()
        try:
            # 发送请求
            response = requests.get(self.target_url)
            load_time = (time.time() - start_time) * 1000  # 转换为毫秒
            
            # 记录响应
            self.monitor.record_response(load_time, response.status_code == 200)
            
            # 获取响应头信息
            headers = dict(response.headers)
            
            # 计算页面大小
            page_size = len(response.content) / 1024  # KB
            
            result = {
                "url": self.target_url,
                "status_code": response.status_code,
                "load_time_ms": load_time,
                "page_size_kb": page_size,
                "headers": headers
            }
            
            print(f"页面加载完成: {load_time:.2f}ms")
            print(f"页面大小: {page_size:.2f}KB")
            
            return result
            
        except Exception as e:
            load_time = (time.time() - start_time) * 1000
            self.monitor.record_response(load_time, False)
            print(f"页面加载失败: {e}")
            return {
                "url": self.target_url,
                "status_code": 0,
                "load_time_ms": load_time,
                "error": str(e)
            }
        finally:
            # 停止监控
            self.monitor.stop_monitoring()
    
    def measure_resource_loading(self) -> Dict[str, Any]:
        """测量资源加载时间"""
        print(f"\n测量资源加载时间: {self.target_url}")
        
        try:
            # 获取页面内容
            response = requests.get(self.target_url)
            if response.status_code != 200:
                print(f"无法获取页面内容: {response.status_code}")
                return {}
            
            # 简单解析HTML，提取资源链接
            html_content = response.text
            import re
            
            # 提取CSS、JS、图片等资源
            css_pattern = r'<link[^>]*href=["\']([^"\']*)["\'][^>]*>'
            js_pattern = r'<script[^>]*src=["\']([^"\']*)["\'][^>]*>'
            img_pattern = r'<img[^>]*src=["\']([^"\']*)["\'][^>]*>'
            
            css_resources = re.findall(css_pattern, html_content)
            js_resources = re.findall(js_pattern, html_content)
            img_resources = re.findall(img_pattern, html_content)
            
            # 转换相对URL为绝对URL
            def to_absolute_url(url):
                if url.startswith('http'):
                    return url
                elif url.startswith('/'):
                    from urllib.parse import urlparse
                    base_url = f"{urlparse(self.target_url).scheme}://{urlparse(self.target_url).netloc}"
                    return urljoin(base_url, url)
                else:
                    return urljoin(self.target_url, url)
            
            css_resources = [to_absolute_url(url) for url in css_resources]
            js_resources = [to_absolute_url(url) for url in js_resources]
            img_resources = [to_absolute_url(url) for url in img_resources]
            
            # 测量资源加载时间
            resources = []
            
            for url in css_resources[:5]:  # 限制数量
                start_time = time.time()
                try:
                    res_response = requests.get(url, timeout=5)
                    load_time = (time.time() - start_time) * 1000
                    size = len(res_response.content) / 1024  # KB
                    
                    resources.append({
                        "type": "css",
                        "url": url,
                        "load_time_ms": load_time,
                        "size_kb": size,
                        "status": res_response.status_code
                    })
                except Exception as e:
                    load_time = (time.time() - start_time) * 1000
                    resources.append({
                        "type": "css",
                        "url": url,
                        "load_time_ms": load_time,
                        "error": str(e)
                    })
            
            for url in js_resources[:5]:  # 限制数量
                start_time = time.time()
                try:
                    res_response = requests.get(url, timeout=5)
                    load_time = (time.time() - start_time) * 1000
                    size = len(res_response.content) / 1024  # KB
                    
                    resources.append({
                        "type": "js",
                        "url": url,
                        "load_time_ms": load_time,
                        "size_kb": size,
                        "status": res_response.status_code
                    })
                except Exception as e:
                    load_time = (time.time() - start_time) * 1000
                    resources.append({
                        "type": "js",
                        "url": url,
                        "load_time_ms": load_time,
                        "error": str(e)
                    })
            
            # 统计结果
            total_resources = len(resources)
            successful_resources = len([r for r in resources if "status" in r and r["status"] == 200])
            total_load_time = sum(r["load_time_ms"] for r in resources)
            total_size = sum(r.get("size_kb", 0) for r in resources)
            
            result = {
                "total_resources": total_resources,
                "successful_resources": successful_resources,
                "total_load_time_ms": total_load_time,
                "total_size_kb": total_size,
                "resources": resources
            }
            
            print(f"资源加载完成: {successful_resources}/{total_resources} 成功")
            print(f"总加载时间: {total_load_time:.2f}ms")
            print(f"总大小: {total_size:.2f}KB")
            
            return result
            
        except Exception as e:
            print(f"资源加载测试失败: {e}")
            return {"error": str(e)}
    
    def run_performance_test(self, num_iterations: int = 3) -> Dict[str, Any]:
        """运行前端性能测试"""
        print(f"\n开始前端性能测试: {num_iterations}次迭代")
        
        page_load_times = []
        resource_load_results = []
        
        for i in range(num_iterations):
            print(f"\n第{i+1}次迭代:")
            
            # 测量页面加载时间
            page_result = self.measure_page_load_time()
            page_load_times.append(page_result["load_time_ms"])
            
            # 测量资源加载时间
            resource_result = self.measure_resource_loading()
            resource_load_results.append(resource_result)
            
            # 等待一段时间再进行下一次测试
            if i < num_iterations - 1:
                time.sleep(2)
        
        # 计算平均值
        avg_page_load_time = statistics.mean(page_load_times)
        min_page_load_time = min(page_load_times)
        max_page_load_time = max(page_load_times)
        
        # 打印结果
        print(f"\n{'='*50}")
        print("前端性能测试结果")
        print(f"{'='*50}")
        print(f"页面加载时间 - 平均: {avg_page_load_time:.2f}ms")
        print(f"页面加载时间 - 最小: {min_page_load_time:.2f}ms")
        print(f"页面加载时间 - 最大: {max_page_load_time:.2f}ms")
        
        if resource_load_results and "total_resources" in resource_load_results[0]:
            avg_total_resources = statistics.mean(r.get("total_resources", 0) for r in resource_load_results)
            avg_successful_resources = statistics.mean(r.get("successful_resources", 0) for r in resource_load_results)
            avg_total_load_time = statistics.mean(r.get("total_load_time_ms", 0) for r in resource_load_results)
            avg_total_size = statistics.mean(r.get("total_size_kb", 0) for r in resource_load_results)
            
            print(f"资源数量 - 平均: {avg_total_resources:.2f}")
            print(f"成功加载资源 - 平均: {avg_successful_resources:.2f}")
            print(f"资源总加载时间 - 平均: {avg_total_load_time:.2f}ms")
            print(f"资源总大小 - 平均: {avg_total_size:.2f}KB")
        
        return {
            "page_load_times": page_load_times,
            "resource_load_results": resource_load_results,
            "avg_page_load_time": avg_page_load_time,
            "min_page_load_time": min_page_load_time,
            "max_page_load_time": max_page_load_time
        }

def demo_frontend_performance_testing():
    """演示前端性能测试"""
    print("\n=== 实验4：前端性能测试 ===")
    
    # 使用公共网站进行测试
    target_url = "https://httpbin.org/html"  # 简单的HTML页面
    
    # 创建前端性能测试器
    frontend_tester = FrontendPerformanceTester(target_url)
    
    # 运行性能测试
    results = frontend_tester.run_performance_test(3)
    
    return frontend_tester


# ============================================================================
# 主函数：运行所有实验
# ============================================================================

def main():
    """运行所有实验"""
    print("性能测试 - 示例代码")
    print("=" * 50)
    
    # 运行所有实验
    demo_basic_performance_testing()
    demo_load_testing()
    demo_database_performance_testing()
    demo_frontend_performance_testing()
    
    print("\n所有实验已完成！")
    print("\n性能测试核心要点:")
    print("1. 定义明确的性能指标和目标")
    print("2. 设计真实的负载模型")
    print("3. 监控系统资源使用情况")
    print("4. 分析性能瓶颈和根本原因")
    print("5. 持续进行性能测试和优化")
    print("6. 将性能测试集成到CI/CD流程中")
    print("7. 建立性能基线和监控告警")


if __name__ == "__main__":
    main()