"""
RabbitMQ日志分析模块
提供日志解析、分析、监控和告警功能
"""

import re
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Pattern, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import logging
import os
from pathlib import Path


class LogLevel(Enum):
    """日志级别"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogEventType(Enum):
    """日志事件类型"""
    CONNECTION = "connection"
    CHANNEL = "channel"
    QUEUE = "queue"
    MESSAGE = "message"
    AUTHENTICATION = "authentication"
    CLUSTER = "cluster"
    GARBAGE_COLLECTION = "gc"
    DISK = "disk"
    MEMORY = "memory"
    UNKNOWN = "unknown"


@dataclass
class LogEntry:
    """日志条目"""
    timestamp: datetime
    level: LogLevel
    source: str
    message: str
    event_type: LogEventType
    details: Dict[str, Any]
    raw_line: str


@dataclass
class LogStats:
    """日志统计"""
    total_entries: int
    entries_by_level: Dict[str, int]
    entries_by_type: Dict[str, int]
    entries_by_source: Dict[str, int]
    error_rate: float
    time_range: tuple


@dataclass
class LogPattern:
    """日志模式"""
    name: str
    pattern: str
    event_type: LogEventType
    extract_fields: List[str]
    description: str


class LogParser:
    """日志解析器"""
    
    def __init__(self):
        self.patterns = []
        self._setup_default_patterns()
    
    def _setup_default_patterns(self):
        """设置默认模式"""
        # 连接日志模式
        connection_pattern = LogPattern(
            name="connection_pattern",
            pattern=r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}) \[(info|warning|error)\] <\d+> (rabbit_\d+) started\. TCP connection from (\d+\.\d+\.\d+\.\d+:\d+)',
            event_type=LogEventType.CONNECTION,
            extract_fields=['timestamp', 'level', 'pid', 'source'],
            description="连接启动日志"
        )
        
        # 错误日志模式
        error_pattern = LogPattern(
            name="error_pattern",
            pattern=r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}) \[(error|critical)\] <\d+> (rabbit_\d+) (.*?)(?: \{(\{.*?\})\})?',
            event_type=LogEventType.UNKNOWN,
            extract_fields=['timestamp', 'level', 'pid', 'message', 'context'],
            description="错误日志模式"
        )
        
        # 队列日志模式
        queue_pattern = LogPattern(
            name="queue_pattern",
            pattern=r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}) \[(info|warning)\] <\d+> rabbit_queue (created|deleted|declaring|deleting)\s+(.*?)(?: \(.*? (\d+)\))?',
            event_type=LogEventType.QUEUE,
            extract_fields=['timestamp', 'level', 'action', 'queue_name'],
            description="队列操作日志"
        )
        
        # 认证日志模式
        auth_pattern = LogPattern(
            name="auth_pattern",
            pattern=r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}) \[(info|warning)\] <\d+> rabbit_access_control (.*?)(?: denied for user (\'.*?\'))?(?: in vhost (\'.*?\'))?',
            event_type=LogEventType.AUTHENTICATION,
            extract_fields=['timestamp', 'level', 'action', 'user', 'vhost'],
            description="认证日志模式"
        )
        
        # GC日志模式
        gc_pattern = LogPattern(
            name="gc_pattern",
            pattern=r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}) \[info\] <\d+> (\w+): GC started',
            event_type=LogEventType.GARBAGE_COLLECTION,
            extract_fields=['timestamp', 'type'],
            description="垃圾回收日志"
        )
        
        # 磁盘日志模式
        disk_pattern = LogPattern(
            name="disk_pattern",
            pattern=r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}) \[(info|warning)\] <\d+> Disk free: (\d+)\. Space available: (\d+)',
            event_type=LogEventType.DISK,
            extract_fields=['timestamp', 'level', 'free_bytes', 'available_bytes'],
            description="磁盘空间日志"
        )
        
        self.patterns = [
            connection_pattern,
            error_pattern,
            queue_pattern,
            auth_pattern,
            gc_pattern,
            disk_pattern
        ]
    
    def add_pattern(self, pattern: LogPattern):
        """添加自定义模式"""
        self.patterns.append(pattern)
    
    def parse_log_line(self, line: str) -> Optional[LogEntry]:
        """解析单行日志"""
        line = line.strip()
        if not line:
            return None
        
        for pattern in self.patterns:
            match = re.match(pattern.pattern, line)
            if match:
                try:
                    groups = match.groups()
                    details = {}
                    
                    # 提取详细字段
                    for i, field in enumerate(pattern.extract_fields):
                        if i < len(groups):
                            details[field] = groups[i]
                    
                    # 解析时间戳
                    timestamp_str = details.get('timestamp', '')
                    if timestamp_str:
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
                    else:
                        timestamp = datetime.now()
                    
                    # 解析日志级别
                    level_str = details.get('level', 'info')
                    level = self._parse_log_level(level_str)
                    
                    # 确定事件类型
                    event_type = self._determine_event_type(line, pattern.event_type)
                    
                    return LogEntry(
                        timestamp=timestamp,
                        level=level,
                        source=details.get('pid', 'unknown'),
                        message=details.get('message', line),
                        event_type=event_type,
                        details=details,
                        raw_line=line
                    )
                except Exception as e:
                    logging.warning(f"解析日志行失败: {e}, 行: {line}")
                    continue
        
        # 如果没有匹配的模式，创建通用条目
        return self._create_generic_entry(line)
    
    def _parse_log_level(self, level_str: str) -> LogLevel:
        """解析日志级别"""
        level_str = level_str.lower()
        level_mapping = {
            'debug': LogLevel.DEBUG,
            'info': LogLevel.INFO,
            'warning': LogLevel.WARNING,
            'error': LogLevel.ERROR,
            'critical': LogLevel.CRITICAL
        }
        return level_mapping.get(level_str, LogLevel.INFO)
    
    def _determine_event_type(self, line: str, pattern_type: LogEventType) -> LogEventType:
        """确定事件类型"""
        line_lower = line.lower()
        
        # 基于关键词进一步分类
        if 'connection' in line_lower:
            return LogEventType.CONNECTION
        elif 'channel' in line_lower:
            return LogEventType.CHANNEL
        elif 'queue' in line_lower:
            return LogEventType.QUEUE
        elif 'message' in line_lower:
            return LogEventType.MESSAGE
        elif 'auth' in line_lower or 'login' in line_lower:
            return LogEventType.AUTHENTICATION
        elif 'cluster' in line_lower:
            return LogEventType.CLUSTER
        elif 'gc' in line_lower or 'garbage' in line_lower:
            return LogEventType.GARBAGE_COLLECTION
        elif 'disk' in line_lower:
            return LogEventType.DISK
        elif 'memory' in line_lower:
            return LogEventType.MEMORY
        else:
            return pattern_type
    
    def _create_generic_entry(self, line: str) -> LogEntry:
        """创建通用日志条目"""
        return LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.INFO,
            source='unknown',
            message=line,
            event_type=LogEventType.UNKNOWN,
            details={},
            raw_line=line
        )


class LogFileReader:
    """日志文件阅读器"""
    
    def __init__(self, log_file: str):
        self.log_file = Path(log_file)
        self.parser = LogParser()
        self.following = False
        self.reader_thread = None
        self.callbacks = []
        self.logger = logging.getLogger(__name__)
        
        # 跟踪文件位置
        self.last_position = 0
    
    def add_log_callback(self, callback: Callable[[LogEntry], None]):
        """添加日志回调"""
        self.callbacks.append(callback)
    
    def start_following(self, seek_to_end: bool = True):
        """开始跟踪日志文件"""
        if self.following:
            return
        
        self.following = True
        
        # 如果从文件末尾开始
        if seek_to_end and self.log_file.exists():
            self.last_position = self.log_file.stat().st_size
        
        self.reader_thread = threading.Thread(target=self._follow_loop, daemon=True)
        self.reader_thread.start()
        self.logger.info(f"开始跟踪日志文件: {self.log_file}")
    
    def stop_following(self):
        """停止跟踪日志文件"""
        self.following = False
        if self.reader_thread:
            self.reader_thread.join(timeout=5)
        self.logger.info("停止跟踪日志文件")
    
    def _follow_loop(self):
        """跟踪循环"""
        while self.following:
            try:
                if not self.log_file.exists():
                    time.sleep(1)
                    continue
                
                # 检查文件是否被轮换
                current_size = self.log_file.stat().st_size
                if current_size < self.last_position:
                    # 文件被轮换，重置位置
                    self.last_position = 0
                
                with open(self.log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(self.last_position)
                    
                    for line in f:
                        entry = self.parser.parse_log_line(line)
                        if entry:
                            self._notify_callbacks(entry)
                    
                    self.last_position = f.tell()
                
                time.sleep(0.1)  # 100ms间隔
            except Exception as e:
                self.logger.error(f"跟踪日志文件时发生错误: {e}")
                time.sleep(1)
    
    def _notify_callbacks(self, entry: LogEntry):
        """通知回调函数"""
        for callback in self.callbacks:
            try:
                callback(entry)
            except Exception as e:
                self.logger.error(f"回调函数执行失败: {e}")
    
    def read_historical_logs(self, start_time: Optional[datetime] = None, 
                           end_time: Optional[datetime] = None,
                           max_entries: int = 10000) -> List[LogEntry]:
        """读取历史日志"""
        entries = []
        
        if not self.log_file.exists():
            return entries
        
        try:
            with open(self.log_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    entry = self.parser.parse_log_line(line)
                    if entry:
                        # 时间范围过滤
                        if start_time and entry.timestamp < start_time:
                            continue
                        if end_time and entry.timestamp > end_time:
                            break
                        
                        entries.append(entry)
                        
                        if len(entries) >= max_entries:
                            break
            
            self.logger.info(f"读取历史日志: {len(entries)} 条记录")
            return entries
        
        except Exception as e:
            self.logger.error(f"读取历史日志失败: {e}")
            return entries


class LogAnalyzer:
    """日志分析器"""
    
    def __init__(self, max_entries: int = 100000):
        self.max_entries = max_entries
        self.entries = deque(maxlen=max_entries)
        self.analysis_callbacks = []
        self.logger = logging.getLogger(__name__)
    
    def add_analysis_callback(self, callback: Callable[[LogEntry], None]):
        """添加分析回调"""
        self.analysis_callbacks.append(callback)
    
    def add_entry(self, entry: LogEntry):
        """添加日志条目"""
        self.entries.append(entry)
        
        # 通知分析回调
        for callback in self.analysis_callbacks:
            try:
                callback(entry)
            except Exception as e:
                self.logger.error(f"分析回调执行失败: {e}")
    
    def analyze_errors(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """分析错误"""
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=time_window_minutes)
        
        # 过滤时间范围内的错误
        recent_errors = [
            entry for entry in self.entries
            if entry.level in [LogLevel.ERROR, LogLevel.CRITICAL] and
            start_time <= entry.timestamp <= end_time
        ]
        
        if not recent_errors:
            return {
                'error_count': 0,
                'error_rate': 0.0,
                'error_types': {},
                'error_sources': {},
                'time_range_minutes': time_window_minutes
            }
        
        # 错误分类
        error_types = defaultdict(int)
        error_sources = defaultdict(int)
        error_messages = defaultdict(int)
        
        for error in recent_errors:
            error_types[error.event_type.value] += 1
            error_sources[error.source] += 1
            error_messages[error.message] += 1
        
        # 计算错误率
        total_entries = len([
            entry for entry in self.entries
            if start_time <= entry.timestamp <= end_time
        ])
        
        error_rate = len(recent_errors) / max(total_entries, 1) * 100
        
        return {
            'error_count': len(recent_errors),
            'error_rate': round(error_rate, 2),
            'error_types': dict(error_types),
            'error_sources': dict(error_sources),
            'common_messages': dict(sorted(error_messages.items(), key=lambda x: x[1], reverse=True)[:10]),
            'time_range_minutes': time_window_minutes
        }
    
    def analyze_performance(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """分析性能"""
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=time_window_minutes)
        
        # 过滤时间范围内的日志
        recent_entries = [
            entry for entry in self.entries
            if start_time <= entry.timestamp <= end_time
        ]
        
        if not recent_entries:
            return {
                'total_entries': 0,
                'entries_per_minute': 0.0,
                'level_distribution': {},
                'event_type_distribution': {},
                'time_range_minutes': time_window_minutes
            }
        
        # 按级别统计
        level_dist = defaultdict(int)
        type_dist = defaultdict(int)
        
        for entry in recent_entries:
            level_dist[entry.level.value] += 1
            type_dist[entry.event_type.value] += 1
        
        return {
            'total_entries': len(recent_entries),
            'entries_per_minute': len(recent_entries) / time_window_minutes,
            'level_distribution': dict(level_dist),
            'event_type_distribution': dict(type_dist),
            'time_range_minutes': time_window_minutes
        }
    
    def detect_anomalies(self, time_window_minutes: int = 60) -> List[Dict[str, Any]]:
        """检测异常"""
        anomalies = []
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=time_window_minutes)
        
        recent_entries = [
            entry for entry in self.entries
            if start_time <= entry.timestamp <= end_time
        ]
        
        if len(recent_entries) < 10:
            return anomalies
        
        # 检测错误率异常
        error_count = len([e for e in recent_entries if e.level in [LogLevel.ERROR, LogLevel.CRITICAL]])
        error_rate = error_count / len(recent_entries)
        
        if error_rate > 0.1:  # 超过10%错误率
            anomalies.append({
                'type': 'high_error_rate',
                'severity': 'high' if error_rate > 0.2 else 'medium',
                'description': f'错误率异常: {error_rate:.2%}',
                'error_rate': error_rate,
                'timestamp': end_time
            })
        
        # 检测消息量异常
        entries_per_minute = len(recent_entries) / time_window_minutes
        
        # 与历史平均比较
        historical_minute_counts = []
        for i in range(6):  # 过去6个时间段
            hist_start = start_time - timedelta(minutes=(i+1) * time_window_minutes)
            hist_end = hist_start + timedelta(minutes=time_window_minutes)
            
            hist_count = len([
                e for e in self.entries
                if hist_start <= e.timestamp <= hist_end
            ])
            historical_minute_counts.append(hist_count)
        
        if historical_minute_counts:
            avg_historical = sum(historical_minute_counts) / len(historical_minute_counts)
            
            if entries_per_minute > avg_historical * 3:  # 超过平均值3倍
                anomalies.append({
                    'type': 'high_log_volume',
                    'severity': 'high',
                    'description': f'日志量异常高: {entries_per_minute:.1f}/分钟 (平均: {avg_historical:.1f}/分钟)',
                    'current_rate': entries_per_minute,
                    'historical_average': avg_historical,
                    'timestamp': end_time
                })
        
        return anomalies
    
    def get_statistics(self, time_window_minutes: int = 60) -> LogStats:
        """获取统计信息"""
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=time_window_minutes)
        
        recent_entries = [
            entry for entry in self.entries
            if start_time <= entry.timestamp <= end_time
        ]
        
        # 统计
        level_dist = defaultdict(int)
        type_dist = defaultdict(int)
        source_dist = defaultdict(int)
        
        for entry in recent_entries:
            level_dist[entry.level.value] += 1
            type_dist[entry.event_type.value] += 1
            source_dist[entry.source] += 1
        
        # 计算错误率
        error_count = level_dist.get('error', 0) + level_dist.get('critical', 0)
        error_rate = error_count / max(len(recent_entries), 1) * 100
        
        return LogStats(
            total_entries=len(recent_entries),
            entries_by_level=dict(level_dist),
            entries_by_type=dict(type_dist),
            entries_by_source=dict(source_dist),
            error_rate=round(error_rate, 2),
            time_range=(start_time, end_time)
        )


class LogAlertManager:
    """日志告警管理器"""
    
    def __init__(self):
        self.alert_rules = []
        self.active_alerts = {}
        self.alert_callbacks = []
        self.logger = logging.getLogger(__name__)
    
    def add_alert_rule(self, name: str, condition: str, threshold: float, 
                      time_window_minutes: int, level: LogLevel = LogLevel.ERROR,
                      description: str = ""):
        """添加告警规则"""
        self.alert_rules.append({
            'name': name,
            'condition': condition,
            'threshold': threshold,
            'time_window_minutes': time_window_minutes,
            'level': level,
            'description': description
        })
    
    def add_alert_callback(self, callback: Callable[[Dict], None]):
        """添加告警回调"""
        self.alert_callbacks.append(callback)
    
    def check_alerts(self, analyzer: LogAnalyzer) -> List[Dict]:
        """检查告警"""
        alerts = []
        
        # 获取错误分析
        error_analysis = analyzer.analyze_errors()
        
        for rule in self.alert_rules:
            alert_triggered = False
            alert_message = ""
            
            if rule['condition'] == 'error_rate_high':
                if error_analysis['error_rate'] > rule['threshold']:
                    alert_triggered = True
                    alert_message = f"错误率过高: {error_analysis['error_rate']:.2f}% (阈值: {rule['threshold']}%)"
            
            elif rule['condition'] == 'error_count_high':
                if error_analysis['error_count'] > rule['threshold']:
                    alert_triggered = True
                    alert_message = f"错误数量过多: {error_analysis['error_count']} (阈值: {rule['threshold']})"
            
            elif rule['condition'] == 'critical_error':
                # 检查是否有Critical级别的错误
                critical_entries = [
                    entry for entry in analyzer.entries
                    if entry.level == LogLevel.CRITICAL and
                    entry.timestamp >= datetime.now() - timedelta(minutes=rule['time_window_minutes'])
                ]
                if critical_entries:
                    alert_triggered = True
                    alert_message = f"检测到 {len(critical_entries)} 个严重错误"
            
            alert_key = rule['name']
            
            if alert_triggered:
                if alert_key not in self.active_alerts:
                    alert = {
                        'id': alert_key,
                        'name': rule['name'],
                        'level': rule['level'],
                        'condition': rule['condition'],
                        'message': alert_message,
                        'triggered_at': datetime.now(),
                        'rule': rule
                    }
                    
                    self.active_alerts[alert_key] = alert
                    alerts.append(alert)
                    
                    # 通知回调
                    for callback in self.alert_callbacks:
                        try:
                            callback(alert)
                        except Exception as e:
                            self.logger.error(f"告警回调失败: {e}")
            
            else:
                # 告警恢复
                if alert_key in self.active_alerts:
                    del self.active_alerts[alert_key]
                    self.logger.info(f"告警恢复: {rule['name']}")
        
        return alerts
    
    def get_active_alerts(self) -> List[Dict]:
        """获取活跃告警"""
        return list(self.active_alerts.values())


class LogAnalysisDemo:
    """日志分析演示"""
    
    def __init__(self, log_file: str = None):
        self.log_file = log_file
        self.reader = None
        self.analyzer = LogAnalyzer()
        self.alert_manager = LogAlertManager()
        
        # 设置默认告警规则
        self._setup_default_alerts()
        
        # 添加分析回调
        self.analyzer.add_analysis_callback(self._analyze_entry)
        
        # 添加告警回调
        self.alert_manager.add_alert_callback(self._alert_callback)
        
        self.logger = logging.getLogger(__name__)
    
    def _setup_default_alerts(self):
        """设置默认告警规则"""
        self.alert_manager.add_alert_rule(
            name='high_error_rate',
            condition='error_rate_high',
            threshold=5.0,
            time_window_minutes=10,
            level=LogLevel.WARNING,
            description='错误率超过5%时触发告警'
        )
        
        self.alert_manager.add_alert_rule(
            name='critical_errors',
            condition='critical_error',
            threshold=1.0,
            time_window_minutes=5,
            level=LogLevel.CRITICAL,
            description='检测到Critical级别错误时立即告警'
        )
    
    def _analyze_entry(self, entry: LogEntry):
        """分析日志条目"""
        # 这里可以实现实时分析逻辑
        pass
    
    def _alert_callback(self, alert: Dict):
        """告警回调"""
        level_icons = {
            LogLevel.DEBUG: '🐛',
            LogLevel.INFO: 'ℹ️',
            LogLevel.WARNING: '⚠️',
            LogLevel.ERROR: '❌',
            LogLevel.CRITICAL: '🚨'
        }
        
        icon = level_icons.get(alert['level'], '❓')
        print(f"{icon} 日志告警: {alert['name']} - {alert['message']}")
    
    def demo_log_file_parsing(self):
        """演示日志文件解析"""
        print("=== 日志文件解析演示 ===")
        
        # 创建测试日志文件
        test_log_file = "test_rabbitmq.log"
        self._create_test_log_file(test_log_file)
        
        try:
            reader = LogFileReader(test_log_file)
            
            # 读取历史日志
            print(f"解析日志文件: {test_log_file}")
            entries = reader.read_historical_logs(max_entries=50)
            
            print(f"解析到 {len(entries)} 条日志记录")
            
            # 显示前几条记录
            for i, entry in enumerate(entries[:5]):
                print(f"\n日志条目 {i+1}:")
                print(f"  时间: {entry.timestamp}")
                print(f"  级别: {entry.level.value}")
                print(f"  源: {entry.source}")
                print(f"  类型: {entry.event_type.value}")
                print(f"  消息: {entry.message}")
            
            # 分析统计
            for entry in entries:
                self.analyzer.add_entry(entry)
            
            stats = self.analyzer.get_statistics()
            print(f"\n日志统计:")
            print(f"  总记录数: {stats.total_entries}")
            print(f"  错误率: {stats.error_rate}%")
            print(f"  级别分布: {stats.entries_by_level}")
            print(f"  类型分布: {stats.entries_by_type}")
            
        finally:
            # 清理测试文件
            if os.path.exists(test_log_file):
                os.remove(test_log_file)
    
    def _create_test_log_file(self, filename: str):
        """创建测试日志文件"""
        test_logs = [
            "2024-01-15 10:00:00.123 [info] <1234> rabbit_123 started. TCP connection from 192.168.1.100:12345",
            "2024-01-15 10:01:30.456 [warning] <1234> rabbit_queue declaring queue: test_queue",
            "2024-01-15 10:02:15.789 [error] <1234> Connection closed by client",
            "2024-01-15 10:03:00.012 [info] <1234> Disk free: 1000000000. Space available: 800000000",
            "2024-01-15 10:04:45.345 [warning] <1235> rabbit_access_control denied for user 'test_user' in vhost '/test'",
            "2024-01-15 10:05:30.678 [critical] <1234> Memory allocation failed",
            "2024-01-15 10:06:00.901 [info] <1234> Garbage collection started",
            "2024-01-15 10:07:15.234 [error] <1234> Channel closed: channel error",
            "2024-01-15 10:08:00.567 [info] <1234> Queue created: test_queue",
            "2024-01-15 10:09:30.890 [error] <1236> Authentication failed for user 'admin'"
        ]
        
        with open(filename, 'w') as f:
            for log in test_logs:
                f.write(log + '\n')
    
    def demo_real_time_monitoring(self):
        """演示实时监控"""
        print("\n=== 实时日志监控演示 ===")
        
        # 创建实时日志文件
        real_time_log = "realtime_rabbitmq.log"
        self._create_real_time_log_stream(real_time_log)
        
        try:
            reader = LogFileReader(real_time_log)
            self.reader = reader
            
            # 添加日志回调
            reader.add_log_callback(self._log_entry_callback)
            
            # 开始跟踪
            print("开始实时跟踪日志...")
            reader.start_following()
            
            # 运行30秒
            time.sleep(30)
            
            # 停止跟踪
            reader.stop_following()
            
        except KeyboardInterrupt:
            print("\n监控被用户中断")
            if self.reader:
                self.reader.stop_following()
        finally:
            # 清理测试文件
            if os.path.exists(real_time_log):
                os.remove(real_time_log)
    
    def _log_entry_callback(self, entry: LogEntry):
        """日志条目回调"""
        self.analyzer.add_entry(entry)
        
        # 显示关键日志
        if entry.level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            icon = "❌" if entry.level == LogLevel.ERROR else "🚨"
            print(f"{icon} {entry.timestamp.strftime('%H:%M:%S')} - {entry.event_type.value}: {entry.message}")
        
        # 每10条记录显示一次统计
        if len(self.analyzer.entries) % 10 == 0:
            stats = self.analyzer.get_statistics(time_window_minutes=60)
            print(f"\n📊 统计更新 - 总记录: {stats.total_entries}, 错误率: {stats.error_rate}%")
    
    def _create_real_time_log_stream(self, filename: str):
        """创建实时日志流"""
        import threading
        
        # 清空文件
        with open(filename, 'w') as f:
            f.write("")
        
        def log_writer():
            log_messages = [
                "2024-01-15 15:00:00.000 [info] <1001> rabbit_1001 started. TCP connection from 10.0.0.1:54321",
                "2024-01-15 15:00:05.000 [info] <1001> Queue operation: test_queue",
                "2024-01-15 15:00:10.000 [warning] <1002> Disk space running low",
                "2024-01-15 15:00:15.000 [error] <1001> Message processing failed",
                "2024-01-15 15:00:20.000 [info] <1003> Connection established",
                "2024-01-15 15:00:25.000 [critical] <1004> System overload detected",
                "2024-01-15 15:00:30.000 [info] <1002> GC started",
                "2024-01-15 15:00:35.000 [warning] <1003> High memory usage",
                "2024-01-15 15:00:40.000 [error] <1001> Connection lost",
                "2024-01-15 15:00:45.000 [info] <1002> System recovered"
            ]
            
            for i, message in enumerate(log_messages * 10):  # 重复10次
                with open(filename, 'a') as f:
                    f.write(message + '\n')
                time.sleep(3)
        
        # 在后台线程中写入日志
        writer_thread = threading.Thread(target=log_writer, daemon=True)
        writer_thread.start()
    
    def demo_error_analysis(self):
        """演示错误分析"""
        print("\n=== 错误分析演示 ===")
        
        # 添加一些测试日志条目
        test_entries = self._generate_test_entries()
        
        for entry in test_entries:
            self.analyzer.add_entry(entry)
        
        # 分析错误
        error_analysis = self.analyzer.analyze_errors(time_window_minutes=60)
        
        print(f"错误分析结果:")
        print(f"  错误总数: {error_analysis['error_count']}")
        print(f"  错误率: {error_analysis['error_rate']}%")
        print(f"  错误类型分布: {error_analysis['error_types']}")
        print(f"  错误源分布: {error_analysis['error_sources']}")
        
        if error_analysis['common_messages']:
            print(f"  常见错误信息:")
            for message, count in list(error_analysis['common_messages'].items())[:5]:
                print(f"    - {message} ({count}次)")
        
        # 检测异常
        anomalies = self.analyzer.detect_anomalies(time_window_minutes=60)
        if anomalies:
            print(f"\n检测到 {len(anomalies)} 个异常:")
            for anomaly in anomalies:
                print(f"  - {anomaly['type']}: {anomaly['description']} (严重程度: {anomaly['severity']})")
        else:
            print("\n未检测到异常")
    
    def _generate_test_entries(self) -> List[LogEntry]:
        """生成测试日志条目"""
        entries = []
        base_time = datetime.now() - timedelta(hours=1)
        
        # 正常日志
        for i in range(100):
            entries.append(LogEntry(
                timestamp=base_time + timedelta(minutes=i),
                level=LogLevel.INFO,
                source=f"rabbit_{1000 + i % 10}",
                message="Normal operation",
                event_type=LogEventType.CONNECTION,
                details={},
                raw_line=""
            ))
        
        # 错误日志
        error_sources = ["rabbit_1001", "rabbit_1002", "rabbit_1003"]
        error_messages = ["Connection timeout", "Memory error", "Disk full", "Network error"]
        
        for i in range(15):  # 15%错误率
            entries.append(LogEntry(
                timestamp=base_time + timedelta(minutes=i * 4),
                level=LogLevel.ERROR,
                source=error_sources[i % len(error_sources)],
                message=error_messages[i % len(error_messages)],
                event_type=LogEventType.CONNECTION if i % 3 == 0 else LogEventType.QUEUE,
                details={},
                raw_line=""
            ))
        
        # 严重错误
        for i in range(3):
            entries.append(LogEntry(
                timestamp=base_time + timedelta(minutes=i * 20),
                level=LogLevel.CRITICAL,
                source="rabbit_system",
                message="System failure",
                event_type=LogEventType.CLUSTER,
                details={},
                raw_line=""
            ))
        
        return entries
    
    def demo_alert_system(self):
        """演示告警系统"""
        print("\n=== 告警系统演示 ===")
        
        # 添加测试日志
        test_entries = self._generate_test_entries()
        
        for entry in test_entries:
            self.analyzer.add_entry(entry)
        
        # 检查告警
        print("检查告警...")
        alerts = self.alert_manager.check_alerts(self.analyzer)
        
        if alerts:
            print(f"触发 {len(alerts)} 个告警:")
            for alert in alerts:
                level_icon = {
                    LogLevel.DEBUG: '🐛',
                    LogLevel.INFO: 'ℹ️',
                    LogLevel.WARNING: '⚠️',
                    LogLevel.ERROR: '❌',
                    LogLevel.CRITICAL: '🚨'
                }
                icon = level_icon.get(alert['level'], '❓')
                print(f"  {icon} {alert['name']}: {alert['message']}")
        else:
            print("未触发告警")
        
        # 显示活跃告警
        active_alerts = self.alert_manager.get_active_alerts()
        print(f"\n当前活跃告警: {len(active_alerts)} 个")
        
        for alert in active_alerts:
            print(f"  - {alert['name']}: {alert['message']}")
    
    def run_complete_demo(self):
        """运行完整演示"""
        print("RabbitMQ日志分析演示开始")
        print("=" * 50)
        
        try:
            # 1. 日志文件解析
            self.demo_log_file_parsing()
            
            # 2. 错误分析
            self.demo_error_analysis()
            
            # 3. 告警系统
            self.demo_alert_system()
            
            # 4. 实时监控
            self.demo_real_time_monitoring()
            
            print("\n演示完成!")
            
        except KeyboardInterrupt:
            print("\n演示被用户中断")
            if self.reader:
                self.reader.stop_following()
        except Exception as e:
            print(f"\n演示过程中发生错误: {e}")


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    demo = LogAnalysisDemo()
    demo.run_complete_demo()