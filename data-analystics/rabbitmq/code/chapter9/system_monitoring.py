"""
系统监控模块
提供系统资源的实时监控、告警和报告功能
"""

import psutil
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging
from collections import defaultdict, deque
import json


class AlertLevel(Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class SystemMetric:
    """系统指标"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, int]
    process_count: int
    load_average: float
    health_score: float


@dataclass
class Alert:
    """告警信息"""
    level: AlertLevel
    title: str
    message: str
    metric_name: str
    current_value: float
    threshold: float
    timestamp: datetime


class SystemMonitor:
    """系统资源监控器"""
    
    def __init__(self, collection_interval: int = 30):
        self.collection_interval = collection_interval
        self.metrics_history = deque(maxlen=1000)
        self.alert_rules = []
        self.alert_callbacks = []
        self.active_alerts = {}
        self.monitoring = False
        self.monitor_thread = None
        
        # 配置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def add_alert_rule(self, metric_name: str, condition: str, threshold: float, 
                      level: AlertLevel, message: str):
        """添加告警规则"""
        self.alert_rules.append({
            'metric': metric_name,
            'condition': condition,  # '>', '<', '>=', '<='
            'threshold': threshold,
            'level': level,
            'message': message
        })
    
    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """添加告警回调函数"""
        self.alert_callbacks.append(callback)
    
    def start_monitoring(self):
        """开始监控"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitor_thread.start()
            self.logger.info("系统监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("系统监控已停止")
    
    def _monitoring_loop(self):
        """监控循环"""
        while self.monitoring:
            try:
                metric = self._collect_system_metric()
                self.metrics_history.append(metric)
                
                # 检查告警
                self._check_alerts(metric)
                
                time.sleep(self.collection_interval)
            except Exception as e:
                self.logger.error(f"监控循环错误: {e}")
                time.sleep(5)
    
    def _collect_system_metric(self) -> SystemMetric:
        """收集系统指标"""
        # CPU信息
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 内存信息
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # 磁盘信息
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        
        # 网络IO
        network_io = psutil.net_io_counters()._asdict()
        
        # 进程数
        process_count = len(psutil.pids())
        
        # 负载平均值
        try:
            load_avg = psutil.getloadavg()[0]
        except AttributeError:
            load_avg = 0.0
        
        # 计算健康度分数
        health_score = self._calculate_health_score(cpu_percent, memory_percent, disk_percent, load_avg)
        
        return SystemMetric(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_percent=disk_percent,
            network_io=network_io,
            process_count=process_count,
            load_average=load_avg,
            health_score=health_score
        )
    
    def _calculate_health_score(self, cpu: float, memory: float, disk: float, load: float) -> float:
        """计算系统健康度分数 (0-100)"""
        scores = []
        
        # CPU分数 (40%权重)
        cpu_score = max(0, 100 - cpu)
        scores.append(cpu_score * 0.4)
        
        # 内存分数 (30%权重)
        memory_score = max(0, 100 - memory)
        scores.append(memory_score * 0.3)
        
        # 磁盘分数 (20%权重)
        disk_score = max(0, 100 - disk)
        scores.append(disk_score * 0.2)
        
        # 负载分数 (10%权重)
        load_score = max(0, 100 - min(load * 20, 100))
        scores.append(load_score * 0.1)
        
        return round(sum(scores), 2)
    
    def _check_alerts(self, metric: SystemMetric):
        """检查告警"""
        metrics = {
            'cpu_percent': metric.cpu_percent,
            'memory_percent': metric.memory_percent,
            'disk_percent': metric.disk_percent,
            'load_average': metric.load_average,
            'process_count': metric.process_count
        }
        
        for rule in self.alert_rules:
            metric_value = metrics.get(rule['metric'])
            if metric_value is None:
                continue
            
            # 检查告警条件
            triggered = False
            if rule['condition'] == '>' and metric_value > rule['threshold']:
                triggered = True
            elif rule['condition'] == '<' and metric_value < rule['threshold']:
                triggered = True
            elif rule['condition'] == '>=' and metric_value >= rule['threshold']:
                triggered = True
            elif rule['condition'] == '<=' and metric_value <= rule['threshold']:
                triggered = True
            
            alert_key = f"{rule['metric']}:{rule['threshold']}"
            
            if triggered:
                if alert_key not in self.active_alerts:
                    # 创建新告警
                    alert = Alert(
                        level=rule['level'],
                        title=f"{rule['metric']} 告警",
                        message=rule['message'].format(value=metric_value, threshold=rule['threshold']),
                        metric_name=rule['metric'],
                        current_value=metric_value,
                        threshold=rule['threshold'],
                        timestamp=datetime.now()
                    )
                    
                    self.active_alerts[alert_key] = alert
                    
                    # 调用告警回调
                    for callback in self.alert_callbacks:
                        try:
                            callback(alert)
                        except Exception as e:
                            self.logger.error(f"告警回调执行失败: {e}")
            
            else:
                # 告警恢复
                if alert_key in self.active_alerts:
                    del self.active_alerts[alert_key]
                    self.logger.info(f"告警恢复: {rule['metric']}")
    
    def get_current_metrics(self) -> Optional[SystemMetric]:
        """获取当前指标"""
        return self.metrics_history[-1] if self.metrics_history else None
    
    def get_metrics_in_time_range(self, start_time: datetime, end_time: datetime) -> List[SystemMetric]:
        """获取时间范围内的指标"""
        return [
            metric for metric in self.metrics_history
            if start_time <= metric.timestamp <= end_time
        ]
    
    def get_performance_summary(self, hours: int = 1) -> Dict[str, any]:
        """获取性能摘要"""
        if not self.metrics_history:
            return {}
        
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        recent_metrics = self.get_metrics_in_time_range(start_time, end_time)
        
        if not recent_metrics:
            return {}
        
        # 计算统计信息
        cpu_values = [m.cpu_percent for m in recent_metrics]
        memory_values = [m.memory_percent for m in recent_metrics]
        disk_values = [m.disk_percent for m in recent_metrics]
        
        return {
            'time_range': f"{hours}小时",
            'sample_count': len(recent_metrics),
            'cpu': {
                'current': cpu_values[-1],
                'avg': sum(cpu_values) / len(cpu_values),
                'max': max(cpu_values),
                'min': min(cpu_values)
            },
            'memory': {
                'current': memory_values[-1],
                'avg': sum(memory_values) / len(memory_values),
                'max': max(memory_values),
                'min': min(memory_values)
            },
            'disk': {
                'current': disk_values[-1],
                'avg': sum(disk_values) / len(disk_values),
                'max': max(disk_values),
                'min': min(disk_values)
            },
            'current_health_score': recent_metrics[-1].health_score,
            'average_health_score': sum(m.health_score for m in recent_metrics) / len(recent_metrics)
        }
    
    def get_alert_statistics(self) -> Dict[str, any]:
        """获取告警统计"""
        return {
            'active_alerts': len(self.active_alerts),
            'total_alert_rules': len(self.alert_rules),
            'active_alert_details': [
                {
                    'metric': alert.metric_name,
                    'level': alert.level.value,
                    'message': alert.message
                }
                for alert in self.active_alerts.values()
            ]
        }


class SystemAlertHandler:
    """系统告警处理器"""
    
    def __init__(self, log_file: str = "system_alerts.log"):
        self.log_file = log_file
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """设置日志记录器"""
        logger = logging.getLogger('system_alerts')
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler(self.log_file, encoding='utf-8')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def handle_alert(self, alert: Alert):
        """处理告警"""
        message = f"[{alert.level.value.upper()}] {alert.title}: {alert.message}"
        
        if alert.level == AlertLevel.CRITICAL:
            self.logger.critical(message)
        elif alert.level == AlertLevel.WARNING:
            self.logger.warning(message)
        else:
            self.logger.info(message)
        
        # 这里可以添加其他告警处理逻辑，如发送邮件、短信等


class SystemMonitoringDemo:
    """系统监控演示"""
    
    def __init__(self):
        self.monitor = SystemMonitor(collection_interval=5)  # 5秒间隔
        self.alert_handler = SystemAlertHandler()
        
        # 添加告警规则
        self._setup_alert_rules()
        
        # 添加告警回调
        self.monitor.add_alert_callback(self.alert_handler.handle_alert)
    
    def _setup_alert_rules(self):
        """设置告警规则"""
        self.monitor.add_alert_rule(
            metric_name='cpu_percent',
            condition='>',
            threshold=80.0,
            level=AlertLevel.WARNING,
            message='CPU使用率过高: {value:.1f}% (阈值: {threshold}%)'
        )
        
        self.monitor.add_alert_rule(
            metric_name='cpu_percent',
            condition='>',
            threshold=90.0,
            level=AlertLevel.CRITICAL,
            message='CPU使用率严重过高: {value:.1f}% (阈值: {threshold}%)'
        )
        
        self.monitor.add_alert_rule(
            metric_name='memory_percent',
            condition='>',
            threshold=85.0,
            level=AlertLevel.WARNING,
            message='内存使用率过高: {value:.1f}% (阈值: {threshold}%)'
        )
        
        self.monitor.add_alert_rule(
            metric_name='memory_percent',
            condition='>',
            threshold=95.0,
            level=AlertLevel.CRITICAL,
            message='内存使用率严重过高: {value:.1f}% (阈值: {threshold}%)'
        )
        
        self.monitor.add_alert_rule(
            metric_name='disk_percent',
            condition='>',
            threshold=90.0,
            level=AlertLevel.WARNING,
            message='磁盘使用率过高: {value:.1f}% (阈值: {threshold}%)'
        )
        
        self.monitor.add_alert_rule(
            metric_name='disk_percent',
            condition='>',
            threshold=95.0,
            level=AlertLevel.CRITICAL,
            message='磁盘使用率严重过高: {value:.1f}% (阈值: {threshold}%)'
        )
    
    def demonstrate_basic_monitoring(self):
        """演示基础监控功能"""
        print("=== 基础系统监控演示 ===")
        
        # 收集当前系统指标
        current_metric = self.monitor._collect_system_metric()
        
        print(f"时间: {current_metric.timestamp}")
        print(f"CPU使用率: {current_metric.cpu_percent:.1f}%")
        print(f"内存使用率: {current_metric.memory_percent:.1f}%")
        print(f"磁盘使用率: {current_metric.disk_percent:.1f}%")
        print(f"进程数量: {current_metric.process_count}")
        print(f"负载平均值: {current_metric.load_average:.2f}")
        print(f"系统健康度: {current_metric.health_score}/100")
        
        # 获取网络IO信息
        print("\n网络IO统计:")
        for interface, stats in current_metric.network_io.items():
            print(f"  {interface}: {stats}")
        
        return current_metric
    
    def demonstrate_alert_monitoring(self):
        """演示告警监控功能"""
        print("\n=== 告警监控演示 ===")
        print("启动监控（运行60秒）...")
        
        # 启动监控
        self.monitor.start_monitoring()
        
        # 运行监控一段时间
        time.sleep(60)
        
        # 停止监控
        self.monitor.stop_monitoring()
        
        # 显示告警统计
        alert_stats = self.monitor.get_alert_statistics()
        print(f"\n告警统计:")
        print(f"  活跃告警数: {alert_stats['active_alerts']}")
        print(f"  告警规则数: {alert_stats['total_alert_rules']}")
        
        if alert_stats['active_alerts']:
            print("  活跃告警详情:")
            for alert_detail in alert_stats['active_alert_details']:
                print(f"    - {alert_detail['metric']} [{alert_detail['level']}]: {alert_detail['message']}")
    
    def demonstrate_performance_analysis(self):
        """演示性能分析功能"""
        print("\n=== 性能分析演示 ===")
        
        # 收集一些历史数据
        print("收集性能数据...")
        for i in range(12):  # 收集1分钟数据
            self.monitor._collect_system_metric()
            time.sleep(5)
        
        # 获取性能摘要
        summary = self.monitor.get_performance_summary(hours=1)
        
        if summary:
            print(f"时间范围: {summary['time_range']}")
            print(f"采样次数: {summary['sample_count']}")
            
            print("\nCPU统计:")
            cpu = summary['cpu']
            print(f"  当前: {cpu['current']:.1f}%")
            print(f"  平均: {cpu['avg']:.1f}%")
            print(f"  最大: {cpu['max']:.1f}%")
            print(f"  最小: {cpu['min']:.1f}%")
            
            print("\n内存统计:")
            memory = summary['memory']
            print(f"  当前: {memory['current']:.1f}%")
            print(f"  平均: {memory['avg']:.1f}%")
            print(f"  最大: {memory['max']:.1f}%")
            print(f"  最小: {memory['min']:.1f}%")
            
            print("\n磁盘统计:")
            disk = summary['disk']
            print(f"  当前: {disk['current']:.1f}%")
            print(f"  平均: {disk['avg']:.1f}%")
            print(f"  最大: {disk['max']:.1f}%")
            print(f"  最小: {disk['min']:.1f}%")
            
            print(f"\n健康度:")
            print(f"  当前: {summary['current_health_score']}/100")
            print(f"  平均: {summary['average_health_score']:.1f}/100")
    
    def demonstrate_stress_scenario(self):
        """演示压力场景"""
        print("\n=== 压力场景演示 ===")
        print("模拟系统负载...")
        
        # 启动监控
        self.monitor.start_monitoring()
        
        # 模拟CPU负载
        import multiprocessing
        import os
        
        def cpu_stress():
            """CPU压力函数"""
            end_time = time.time() + 30  # 运行30秒
            while time.time() < end_time:
                # 执行一些计算密集型操作
                for i in range(100000):
                    sqrt(i)
        
        # 启动多个CPU压力进程
        processes = []
        cpu_count = multiprocessing.cpu_count()
        
        print(f"启动 {cpu_count} 个CPU压力进程...")
        for i in range(cpu_count):
            p = multiprocessing.Process(target=cpu_stress)
            p.start()
            processes.append(p)
        
        # 监控30秒
        print("监控CPU负载提升...")
        time.sleep(30)
        
        # 停止进程
        for p in processes:
            p.terminate()
            p.join()
        
        # 停止监控
        self.monitor.stop_monitoring()
        
        # 显示结果
        current_metric = self.monitor.get_current_metrics()
        if current_metric:
            print(f"压力测试后CPU使用率: {current_metric.cpu_percent:.1f}%")
            print(f"系统健康度: {current_metric.health_score}/100")
        
        # 显示告警情况
        alert_stats = self.monitor.get_alert_statistics()
        print(f"压力测试期间告警数: {alert_stats['active_alerts']}")
    
    def run_complete_demo(self):
        """运行完整演示"""
        print("系统监控演示开始...")
        print("=" * 50)
        
        try:
            # 1. 基础监控演示
            self.demonstrate_basic_monitoring()
            
            # 2. 性能分析演示
            self.demonstrate_performance_analysis()
            
            # 3. 告警监控演示（较短时间）
            print("\n=== 短时间告警演示 ===")
            print("启动监控（运行30秒）...")
            self.monitor.start_monitoring()
            time.sleep(30)
            self.monitor.stop_monitoring()
            
            alert_stats = self.monitor.get_alert_statistics()
            print(f"告警监控完成，活跃告警: {alert_stats['active_alerts']}")
            
            # 4. 压力场景演示
            self.demonstrate_stress_scenario()
            
            print("\n演示完成!")
            
        except KeyboardInterrupt:
            print("\n演示被用户中断")
            self.monitor.stop_monitoring()
        except Exception as e:
            print(f"\n演示过程中发生错误: {e}")
            self.monitor.stop_monitoring()


if __name__ == "__main__":
    demo = SystemMonitoringDemo()
    demo.run_complete_demo()