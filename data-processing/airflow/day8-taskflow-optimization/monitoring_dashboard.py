#!/usr/bin/env python3
"""
Airflow实时监控仪表板

该脚本提供了一个基于终端的实时监控仪表板，用于监控Airflow任务执行状态和系统资源使用情况。
"""

import time
import psutil
import logging
import argparse
import threading
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import json
import sqlite3
from contextlib import contextmanager


@dataclass
class SystemMetrics:
    """系统指标数据类"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_usage_percent: float
    network_sent_kbps: float
    network_recv_kbps: float
    load_average: float


@dataclass
class AirflowMetrics:
    """Airflow指标数据类"""
    timestamp: float
    running_tasks: int
    queued_tasks: int
    scheduler_heartbeat: float
    dag_processing_time: float
    task_success_rate: float
    executor_slots_used: int
    executor_slots_total: int


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, db_path: str = "metrics.db"):
        self.db_path = db_path
        self.last_net_io = psutil.net_io_counters()
        self.last_disk_io = psutil.disk_io_counters()
        self._init_database()
        
    def _init_database(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建系统指标表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    timestamp REAL PRIMARY KEY,
                    cpu_percent REAL,
                    memory_percent REAL,
                    memory_available_mb REAL,
                    disk_usage_percent REAL,
                    network_sent_kbps REAL,
                    network_recv_kbps REAL,
                    load_average REAL
                )
            """)
            
            # 创建Airflow指标表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS airflow_metrics (
                    timestamp REAL PRIMARY KEY,
                    running_tasks INTEGER,
                    queued_tasks INTEGER,
                    scheduler_heartbeat REAL,
                    dag_processing_time REAL,
                    task_success_rate REAL,
                    executor_slots_used INTEGER,
                    executor_slots_total INTEGER
                )
            """)
            
            conn.commit()
    
    def collect_system_metrics(self) -> SystemMetrics:
        """收集系统指标"""
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 内存使用情况
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available_mb = memory.available / 1024 / 1024
        
        # 磁盘使用情况
        disk = psutil.disk_usage("/")
        disk_usage_percent = (disk.used / disk.total) * 100
        
        # 网络IO
        current_net_io = psutil.net_io_counters()
        time_delta = 1.0  # 我们每秒收集一次
        
        network_sent_kbps = (
            (current_net_io.bytes_sent - self.last_net_io.bytes_sent) / 1024 / time_delta
        )
        network_recv_kbps = (
            (current_net_io.bytes_recv - self.last_net_io.bytes_recv) / 1024 / time_delta
        )
        
        self.last_net_io = current_net_io
        
        # 系统负载
        load_avg = psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0.0
        
        return SystemMetrics(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_available_mb=memory_available_mb,
            disk_usage_percent=disk_usage_percent,
            network_sent_kbps=network_sent_kbps,
            network_recv_kbps=network_recv_kbps,
            load_average=load_avg
        )
    
    def collect_airflow_metrics(self) -> AirflowMetrics:
        """收集Airflow指标（模拟数据）"""
        # 在实际应用中，这些数据应该从Airflow的API或数据库中获取
        # 这里使用模拟数据进行演示
        
        import random
        
        return AirflowMetrics(
            timestamp=time.time(),
            running_tasks=random.randint(0, 20),
            queued_tasks=random.randint(0, 50),
            scheduler_heartbeat=random.uniform(0, 5),
            dag_processing_time=random.uniform(0.1, 10.0),
            task_success_rate=random.uniform(0.8, 1.0),
            executor_slots_used=random.randint(0, 8),
            executor_slots_total=8
        )
    
    def save_metrics(self, system_metrics: SystemMetrics, airflow_metrics: AirflowMetrics):
        """保存指标到数据库"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 保存系统指标
            cursor.execute("""
                INSERT OR REPLACE INTO system_metrics 
                (timestamp, cpu_percent, memory_percent, memory_available_mb, 
                 disk_usage_percent, network_sent_kbps, network_recv_kbps, load_average)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                system_metrics.timestamp,
                system_metrics.cpu_percent,
                system_metrics.memory_percent,
                system_metrics.memory_available_mb,
                system_metrics.disk_usage_percent,
                system_metrics.network_sent_kbps,
                system_metrics.network_recv_kbps,
                system_metrics.load_average
            ))
            
            # 保存Airflow指标
            cursor.execute("""
                INSERT OR REPLACE INTO airflow_metrics 
                (timestamp, running_tasks, queued_tasks, scheduler_heartbeat,
                 dag_processing_time, task_success_rate, executor_slots_used, executor_slots_total)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                airflow_metrics.timestamp,
                airflow_metrics.running_tasks,
                airflow_metrics.queued_tasks,
                airflow_metrics.scheduler_heartbeat,
                airflow_metrics.dag_processing_time,
                airflow_metrics.task_success_rate,
                airflow_metrics.executor_slots_used,
                airflow_metrics.executor_slots_total
            ))
            
            conn.commit()


class TerminalDashboard:
    """终端仪表板"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self.is_running = False
        self.refresh_interval = 1.0  # 秒
        
    def clear_screen(self):
        """清屏"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def format_value(self, value: float, precision: int = 2) -> str:
        """格式化数值显示"""
        if value >= 1000000:
            return f"{value/1000000:.{precision}f}M"
        elif value >= 1000:
            return f"{value/1000:.{precision}f}K"
        else:
            return f"{value:.{precision}f}"
    
    def display_system_metrics(self, metrics: SystemMetrics):
        """显示系统指标"""
        print("=" * 80)
        print(f"系统监控仪表板 - 更新时间: {datetime.fromtimestamp(metrics.timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # CPU使用率
        cpu_bar = "█" * int(metrics.cpu_percent / 2)
        cpu_color = "\033[91m" if metrics.cpu_percent > 80 else "\033[93m" if metrics.cpu_percent > 60 else "\033[92m"
        print(f"CPU使用率: {cpu_color}{metrics.cpu_percent:6.2f}%\033[0m [{cpu_bar:<50}]")
        
        # 内存使用率
        mem_bar = "█" * int(metrics.memory_percent / 2)
        mem_color = "\033[91m" if metrics.memory_percent > 85 else "\033[93m" if metrics.memory_percent > 70 else "\033[92m"
        print(f"内存使用:  {mem_color}{metrics.memory_percent:6.2f}%\033[0m [{mem_bar:<50}] ({self.format_value(metrics.memory_available_mb)} MB 可用)")
        
        # 磁盘使用率
        disk_bar = "█" * int(metrics.disk_usage_percent / 2)
        disk_color = "\033[91m" if metrics.disk_usage_percent > 90 else "\033[93m" if metrics.disk_usage_percent > 80 else "\033[92m"
        print(f"磁盘使用:  {disk_color}{metrics.disk_usage_percent:6.2f}%\033[0m [{disk_bar:<50}]")
        
        # 网络IO
        print(f"网络IO:    ↑ {self.format_value(metrics.network_sent_kbps)} KB/s  ↓ {self.format_value(metrics.network_recv_kbps)} KB/s")
        
        # 系统负载
        load_color = "\033[91m" if metrics.load_average > 2.0 else "\033[93m" if metrics.load_average > 1.0 else "\033[92m"
        print(f"系统负载:  {load_color}{metrics.load_average:6.2f}\033[0m")
        
        print()
    
    def display_airflow_metrics(self, metrics: AirflowMetrics):
        """显示Airflow指标"""
        print("Airflow任务状态:")
        print("-" * 40)
        
        # 任务状态
        print(f"运行中任务: {metrics.running_tasks:3d}")
        print(f"队列中任务: {metrics.queued_tasks:3d}")
        
        # 调度器状态
        scheduler_color = "\033[91m" if metrics.scheduler_heartbeat > 30 else "\033[93m" if metrics.scheduler_heartbeat > 10 else "\033[92m"
        print(f"调度器心跳: {scheduler_color}{metrics.scheduler_heartbeat:6.2f}s\033[0m")
        
        # DAG处理时间
        dag_color = "\033[91m" if metrics.dag_processing_time > 5.0 else "\033[93m" if metrics.dag_processing_time > 2.0 else "\033[92m"
        print(f"DAG处理时间: {dag_color}{metrics.dag_processing_time:6.2f}s\033[0m")
        
        # 任务成功率
        success_color = "\033[91m" if metrics.task_success_rate < 0.9 else "\033[93m" if metrics.task_success_rate < 0.95 else "\033[92m"
        print(f"任务成功率: {success_color}{metrics.task_success_rate*100:6.2f}%\033[0m")
        
        # 执行器槽位
        slots_used_percent = (metrics.executor_slots_used / metrics.executor_slots_total) * 100 if metrics.executor_slots_total > 0 else 0
        slots_bar = "█" * int(slots_used_percent / 5)
        slots_color = "\033[91m" if slots_used_percent > 80 else "\033[93m" if slots_used_percent > 60 else "\033[92m"
        print(f"执行器槽位: {slots_color}{slots_used_percent:6.2f}%\033[0m [{slots_bar:<20}] ({metrics.executor_slots_used}/{metrics.executor_slots_total})")
        
        print()
    
    def display_help(self):
        """显示帮助信息"""
        print("控制命令:")
        print("  q - 退出监控")
        print("  + - 增加刷新间隔")
        print("  - - 减少刷新间隔")
        print()
    
    def run(self):
        """运行仪表板"""
        self.is_running = True
        print("启动Airflow监控仪表板...")
        print("按 'q' 退出, '+' 增加刷新间隔, '-' 减少刷新间隔")
        time.sleep(2)
        
        try:
            while self.is_running:
                # 收集指标
                system_metrics = self.collector.collect_system_metrics()
                airflow_metrics = self.collector.collect_airflow_metrics()
                
                # 保存指标
                self.collector.save_metrics(system_metrics, airflow_metrics)
                
                # 清屏并显示指标
                self.clear_screen()
                self.display_system_metrics(system_metrics)
                self.display_airflow_metrics(airflow_metrics)
                self.display_help()
                
                # 检查用户输入
                import sys, select
                if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    char = sys.stdin.read(1)
                    if char == 'q':
                        self.is_running = False
                    elif char == '+':
                        self.refresh_interval = min(10.0, self.refresh_interval + 0.5)
                    elif char == '-':
                        self.refresh_interval = max(0.5, self.refresh_interval - 0.5)
                
                # 等待下次更新
                time.sleep(self.refresh_interval)
                
        except KeyboardInterrupt:
            self.is_running = False
        except Exception as e:
            print(f"监控过程中发生错误: {e}")
        finally:
            print("\n监控已停止")


def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Airflow实时监控仪表板")
    parser.add_argument(
        "--db-path",
        default="metrics.db",
        help="指标数据库路径"
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="刷新间隔（秒）"
    )
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging()
    
    # 创建指标收集器
    collector = MetricsCollector(db_path=args.db_path)
    
    # 创建并运行仪表板
    dashboard = TerminalDashboard(collector)
    dashboard.refresh_interval = args.interval
    
    # 启用非阻塞输入
    import sys, tty, termios
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        dashboard.run()
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


if __name__ == "__main__":
    main()