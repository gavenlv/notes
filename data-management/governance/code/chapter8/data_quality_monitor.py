#!/usr/bin/env python3
"""
数据质量监控工具
持续监控数据质量并生成报告和告警
"""

import os
import json
import sqlite3
import pandas as pd
import numpy as np
import datetime
import re
import hashlib
import logging
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Any, Optional, Tuple, Union, Set, Callable
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from enum import Enum
import uuid

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    """告警级别枚举"""
    INFO = "info"                        # 信息
    WARNING = "warning"                  # 警告
    ERROR = "error"                      # 错误
    CRITICAL = "critical"                # 严重

class MonitorStatus(Enum):
    """监控状态枚举"""
    ACTIVE = "active"                    # 激活
    PAUSED = "paused"                    # 暂停
    DISABLED = "disabled"                # 禁用
    ERROR = "error"                      # 错误

class AlertChannel(Enum):
    """告警渠道枚举"""
    EMAIL = "email"                      # 邮件
    WEBHOOK = "webhook"                  # Webhook
    LOG = "log"                          # 日志
    DATABASE = "database"                # 数据库

@dataclass
class QualityMonitor:
    """质量监控配置数据类"""
    id: str
    name: str
    description: str
    table_name: str
    schedule: str  # Cron表达式
    status: MonitorStatus
    rules: List[str]  # 规则ID列表
    thresholds: Dict[str, Any]  # 阈值配置
    alert_channels: List[AlertChannel]
    created_by: str
    created_at: datetime.datetime
    updated_by: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None
    last_run: Optional[datetime.datetime] = None
    next_run: Optional[datetime.datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['status'] = self.status.value
        data['alert_channels'] = [channel.value for channel in self.alert_channels]
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat() if self.updated_at else None
        data['last_run'] = self.last_run.isoformat() if self.last_run else None
        data['next_run'] = self.next_run.isoformat() if self.next_run else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QualityMonitor':
        """从字典创建实例"""
        data['status'] = MonitorStatus(data['status'])
        data['alert_channels'] = [AlertChannel(channel) for channel in data['alert_channels']]
        data['created_at'] = datetime.datetime.fromisoformat(data['created_at'])
        if data['updated_at']:
            data['updated_at'] = datetime.datetime.fromisoformat(data['updated_at'])
        if data['last_run']:
            data['last_run'] = datetime.datetime.fromisoformat(data['last_run'])
        if data['next_run']:
            data['next_run'] = datetime.datetime.fromisoformat(data['next_run'])
        return cls(**data)

@dataclass
class QualityAlert:
    """质量告警数据类"""
    id: str
    monitor_id: str
    table_name: str
    rule_id: str
    rule_name: str
    alert_level: AlertLevel
    message: str
    metrics: Dict[str, Any]
    triggered_at: datetime.datetime
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime.datetime] = None
    resolved: bool = False
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime.datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'monitor_id': self.monitor_id,
            'table_name': self.table_name,
            'rule_id': self.rule_id,
            'rule_name': self.rule_name,
            'alert_level': self.alert_level.value,
            'message': self.message,
            'metrics': self.metrics,
            'triggered_at': self.triggered_at.isoformat(),
            'acknowledged': self.acknowledged,
            'acknowledged_by': self.acknowledged_by,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved': self.resolved,
            'resolved_by': self.resolved_by,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }

@dataclass
class QualityReport:
    """质量报告数据类"""
    id: str
    monitor_id: str
    table_name: str
    report_date: datetime.datetime
    overall_score: float
    total_rules: int
    passed_rules: int
    failed_rules: int
    total_issues: int
    new_issues: int
    resolved_issues: int
    summary: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'monitor_id': self.monitor_id,
            'table_name': self.table_name,
            'report_date': self.report_date.isoformat(),
            'overall_score': self.overall_score,
            'total_rules': self.total_rules,
            'passed_rules': self.passed_rules,
            'failed_rules': self.failed_rules,
            'total_issues': self.total_issues,
            'new_issues': self.new_issues,
            'resolved_issues': self.resolved_issues,
            'summary': self.summary
        }

class AlertNotifier(ABC):
    """告警通知器抽象基类"""
    
    @abstractmethod
    def send_alert(self, alert: QualityAlert) -> bool:
        """发送告警"""
        pass

class EmailAlertNotifier(AlertNotifier):
    """邮件告警通知器"""
    
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, from_address: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_address = from_address
    
    def send_alert(self, alert: QualityAlert) -> bool:
        """发送邮件告警"""
        try:
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = self.from_address
            msg['To'] = "data-quality-team@example.com"  # 这里应该是配置的收件人列表
            msg['Subject'] = f"[{alert.alert_level.value.upper()}] 数据质量告警: {alert.table_name}"
            
            # 邮件正文
            body = f"""
            数据质量告警通知
            
            表名: {alert.table_name}
            规则: {alert.rule_name}
            级别: {alert.alert_level.value}
            时间: {alert.triggered_at}
            
            消息: {alert.message}
            
            详细指标:
            {json.dumps(alert.metrics, indent=2)}
            
            请及时处理此告警。
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # 发送邮件
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"邮件告警发送成功: {alert.id}")
            return True
        
        except Exception as e:
            logger.error(f"邮件告警发送失败: {str(e)}")
            return False

class WebhookAlertNotifier(AlertNotifier):
    """Webhook告警通知器"""
    
    def __init__(self, webhook_url: str, headers: Dict[str, str] = None):
        self.webhook_url = webhook_url
        self.headers = headers or {"Content-Type": "application/json"}
    
    def send_alert(self, alert: QualityAlert) -> bool:
        """发送Webhook告警"""
        try:
            import requests
            
            payload = {
                "alert_id": alert.id,
                "monitor_id": alert.monitor_id,
                "table_name": alert.table_name,
                "rule_id": alert.rule_id,
                "rule_name": alert.rule_name,
                "alert_level": alert.alert_level.value,
                "message": alert.message,
                "metrics": alert.metrics,
                "triggered_at": alert.triggered_at.isoformat()
            }
            
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Webhook告警发送成功: {alert.id}")
                return True
            else:
                logger.error(f"Webhook告警发送失败，状态码: {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"Webhook告警发送失败: {str(e)}")
            return False

class LogAlertNotifier(AlertNotifier):
    """日志告警通知器"""
    
    def send_alert(self, alert: QualityAlert) -> bool:
        """发送日志告警"""
        try:
            log_message = f"数据质量告警 [级别:{alert.alert_level.value}] [表:{alert.table_name}] [规则:{alert.rule_name}] {alert.message}"
            
            if alert.alert_level == AlertLevel.CRITICAL:
                logger.critical(log_message)
            elif alert.alert_level == AlertLevel.ERROR:
                logger.error(log_message)
            elif alert.alert_level == AlertLevel.WARNING:
                logger.warning(log_message)
            else:
                logger.info(log_message)
            
            return True
        
        except Exception as e:
            logger.error(f"日志告警发送失败: {str(e)}")
            return False

class DataQualityMonitor:
    """数据质量监控器"""
    
    def __init__(self, rule_manager=None):
        self.rule_manager = rule_manager
        self.notifiers = {
            AlertChannel.EMAIL: None,  # 需要配置
            AlertChannel.WEBHOOK: None,  # 需要配置
            AlertChannel.LOG: LogAlertNotifier(),
            AlertChannel.DATABASE: None  # 直接保存到数据库
        }
    
    def configure_email_notifier(self, smtp_server: str, smtp_port: int, 
                               username: str, password: str, from_address: str):
        """配置邮件通知器"""
        self.notifiers[AlertChannel.EMAIL] = EmailAlertNotifier(
            smtp_server, smtp_port, username, password, from_address
        )
    
    def configure_webhook_notifier(self, webhook_url: str, headers: Dict[str, str] = None):
        """配置Webhook通知器"""
        self.notifiers[AlertChannel.WEBHOOK] = WebhookAlertNotifier(webhook_url, headers)
    
    def send_alert(self, alert: QualityAlert) -> Dict[str, bool]:
        """发送告警到所有配置的渠道"""
        results = {}
        
        for channel, notifier in self.notifiers.items():
            if notifier:
                success = notifier.send_alert(alert)
                results[channel.value] = success
            else:
                results[channel.value] = False
        
        return results
    
    def check_thresholds(self, monitor: QualityMonitor, results: List[Dict[str, Any]]) -> List[QualityAlert]:
        """检查阈值并生成告警"""
        alerts = []
        
        # 解析阈值配置
        thresholds = monitor.thresholds
        failed_threshold = thresholds.get('failed_rules_percentage', 10)  # 失败规则百分比阈值
        issues_threshold = thresholds.get('new_issues_count', 5)  # 新问题数量阈值
        score_threshold = thresholds.get('overall_score', 0.9)  # 总体质量分数阈值
        
        # 计算指标
        total_rules = len(results)
        failed_rules = sum(1 for result in results if result['failed_rows'] > 0)
        failed_percentage = (failed_rules / total_rules) * 100 if total_rules > 0 else 0
        total_issues = sum(result['failed_rows'] for result in results)
        overall_score = sum(result['pass_rate'] for result in results) / total_rules if total_rules > 0 else 0
        
        # 检查失败规则百分比
        if failed_percentage > failed_threshold:
            alert_level = AlertLevel.CRITICAL if failed_percentage > (failed_threshold * 2) else AlertLevel.ERROR
            alert = QualityAlert(
                id=str(uuid.uuid4()),
                monitor_id=monitor.id,
                table_name=monitor.table_name,
                rule_id="threshold_check",
                rule_name="失败规则百分比阈值检查",
                alert_level=alert_level,
                message=f"失败规则百分比 {failed_percentage:.1f}% 超过阈值 {failed_threshold}%",
                metrics={
                    'failed_rules_percentage': failed_percentage,
                    'threshold': failed_threshold,
                    'total_rules': total_rules,
                    'failed_rules': failed_rules
                },
                triggered_at=datetime.datetime.now()
            )
            alerts.append(alert)
        
        # 检查新问题数量
        if total_issues > issues_threshold:
            alert_level = AlertLevel.CRITICAL if total_issues > (issues_threshold * 2) else AlertLevel.ERROR
            alert = QualityAlert(
                id=str(uuid.uuid4()),
                monitor_id=monitor.id,
                table_name=monitor.table_name,
                rule_id="threshold_check",
                rule_name="新问题数量阈值检查",
                alert_level=alert_level,
                message=f"新问题数量 {total_issues} 超过阈值 {issues_threshold}",
                metrics={
                    'new_issues_count': total_issues,
                    'threshold': issues_threshold
                },
                triggered_at=datetime.datetime.now()
            )
            alerts.append(alert)
        
        # 检查总体质量分数
        if overall_score < score_threshold:
            alert_level = AlertLevel.ERROR if overall_score < (score_threshold * 0.8) else AlertLevel.WARNING
            alert = QualityAlert(
                id=str(uuid.uuid4()),
                monitor_id=monitor.id,
                table_name=monitor.table_name,
                rule_id="threshold_check",
                rule_name="总体质量分数阈值检查",
                alert_level=alert_level,
                message=f"总体质量分数 {overall_score:.2f} 低于阈值 {score_threshold}",
                metrics={
                    'overall_score': overall_score,
                    'threshold': score_threshold
                },
                triggered_at=datetime.datetime.now()
            )
            alerts.append(alert)
        
        # 检查单个规则结果
        for result in results:
            failed_rows = result['failed_rows']
            if failed_rows > 0:
                rule_id = result['rule_id']
                if self.rule_manager:
                    rule = self.rule_manager.get_rule(rule_id)
                    rule_name = rule['name'] if rule else "未知规则"
                    
                    # 根据失败行数确定告警级别
                    if failed_rows > 10:
                        alert_level = AlertLevel.CRITICAL
                    elif failed_rows > 5:
                        alert_level = AlertLevel.ERROR
                    else:
                        alert_level = AlertLevel.WARNING
                    
                    alert = QualityAlert(
                        id=str(uuid.uuid4()),
                        monitor_id=monitor.id,
                        table_name=monitor.table_name,
                        rule_id=rule_id,
                        rule_name=rule_name,
                        alert_level=alert_level,
                        message=f"规则 '{rule_name}' 检查失败，发现 {failed_rows} 个问题",
                        metrics={
                            'failed_rows': failed_rows,
                            'total_rows': result['total_rows'],
                            'pass_rate': result['pass_rate']
                        },
                        triggered_at=datetime.datetime.now()
                    )
                    alerts.append(alert)
        
        return alerts

class QualityMonitorRepository:
    """质量监控存储库"""
    
    def __init__(self, db_path: str = "quality_monitor.db"):
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quality_monitors (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    schedule TEXT NOT NULL,
                    status TEXT NOT NULL,
                    rules TEXT NOT NULL,
                    thresholds TEXT NOT NULL,
                    alert_channels TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_by TEXT,
                    updated_at TEXT,
                    last_run TEXT,
                    next_run TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quality_alerts (
                    id TEXT PRIMARY KEY,
                    monitor_id TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    rule_id TEXT NOT NULL,
                    rule_name TEXT NOT NULL,
                    alert_level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    metrics TEXT NOT NULL,
                    triggered_at TEXT NOT NULL,
                    acknowledged BOOLEAN NOT NULL DEFAULT 0,
                    acknowledged_by TEXT,
                    acknowledged_at TEXT,
                    resolved BOOLEAN NOT NULL DEFAULT 0,
                    resolved_by TEXT,
                    resolved_at TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quality_reports (
                    id TEXT PRIMARY KEY,
                    monitor_id TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    report_date TEXT NOT NULL,
                    overall_score REAL NOT NULL,
                    total_rules INTEGER NOT NULL,
                    passed_rules INTEGER NOT NULL,
                    failed_rules INTEGER NOT NULL,
                    total_issues INTEGER NOT NULL,
                    new_issues INTEGER NOT NULL,
                    resolved_issues INTEGER NOT NULL,
                    summary TEXT NOT NULL
                )
            """)
            
            # 创建索引
            conn.execute("CREATE INDEX IF NOT EXISTS idx_quality_monitors_table_name ON quality_monitors (table_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_quality_monitors_status ON quality_monitors (status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_quality_alerts_monitor_id ON quality_alerts (monitor_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_quality_alerts_table_name ON quality_alerts (table_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_quality_alerts_triggered_at ON quality_alerts (triggered_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_quality_reports_monitor_id ON quality_reports (monitor_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_quality_reports_table_name ON quality_reports (table_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_quality_reports_report_date ON quality_reports (report_date)")
            
            conn.commit()
    
    def save_monitor(self, monitor: QualityMonitor) -> str:
        """保存质量监控"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO quality_monitors
                (id, name, description, table_name, schedule, status, rules, thresholds,
                 alert_channels, created_by, created_at, updated_by, updated_at, last_run, next_run)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                monitor.id, monitor.name, monitor.description, monitor.table_name, monitor.schedule,
                monitor.status.value, json.dumps(monitor.rules), json.dumps(monitor.thresholds),
                json.dumps([channel.value for channel in monitor.alert_channels]),
                monitor.created_by, monitor.created_at.isoformat(),
                monitor.updated_by, monitor.updated_at.isoformat() if monitor.updated_at else None,
                monitor.last_run.isoformat() if monitor.last_run else None,
                monitor.next_run.isoformat() if monitor.next_run else None
            ))
            conn.commit()
        
        return monitor.id
    
    def get_monitor_by_id(self, monitor_id: str) -> Optional[QualityMonitor]:
        """根据ID获取监控"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM quality_monitors WHERE id = ?", (monitor_id,))
            row = cursor.fetchone()
            
            if row:
                return QualityMonitor.from_dict(dict(row))
            return None
    
    def get_monitors_by_table(self, table_name: str) -> List[QualityMonitor]:
        """根据表名获取监控"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM quality_monitors 
                WHERE table_name = ?
                ORDER BY created_at DESC
            """, (table_name,))
            
            rows = cursor.fetchall()
            return [QualityMonitor.from_dict(dict(row)) for row in rows]
    
    def get_active_monitors(self) -> List[QualityMonitor]:
        """获取所有激活的监控"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM quality_monitors 
                WHERE status = ?
                ORDER BY next_run ASC
            """, (MonitorStatus.ACTIVE.value,))
            
            rows = cursor.fetchall()
            return [QualityMonitor.from_dict(dict(row)) for row in rows]
    
    def update_monitor_run_time(self, monitor_id: str, last_run: datetime.datetime, next_run: datetime.datetime):
        """更新监控运行时间"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE quality_monitors
                SET last_run = ?, next_run = ?
                WHERE id = ?
            """, (last_run.isoformat(), next_run.isoformat(), monitor_id))
            conn.commit()
    
    def save_alert(self, alert: QualityAlert) -> str:
        """保存告警"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO quality_alerts
                (id, monitor_id, table_name, rule_id, rule_name, alert_level,
                 message, metrics, triggered_at, acknowledged, acknowledged_by,
                 acknowledged_at, resolved, resolved_by, resolved_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                alert.id, alert.monitor_id, alert.table_name, alert.rule_id, alert.rule_name,
                alert.alert_level.value, alert.message, json.dumps(alert.metrics),
                alert.triggered_at.isoformat(), alert.acknowledged, alert.acknowledged_by,
                alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                alert.resolved, alert.resolved_by,
                alert.resolved_at.isoformat() if alert.resolved_at else None
            ))
            conn.commit()
        
        return alert.id
    
    def get_alerts_by_monitor(self, monitor_id: str, limit: int = 100) -> List[QualityAlert]:
        """获取监控的告警"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM quality_alerts
                WHERE monitor_id = ?
                ORDER BY triggered_at DESC
                LIMIT ?
            """, (monitor_id, limit))
            
            rows = cursor.fetchall()
            alerts = []
            for row in rows:
                data = dict(row)
                data['alert_level'] = AlertLevel(data['alert_level'])
                data['triggered_at'] = datetime.datetime.fromisoformat(data['triggered_at'])
                if data['acknowledged_at']:
                    data['acknowledged_at'] = datetime.datetime.fromisoformat(data['acknowledged_at'])
                if data['resolved_at']:
                    data['resolved_at'] = datetime.datetime.fromisoformat(data['resolved_at'])
                alerts.append(QualityAlert(**data))
            
            return alerts
    
    def get_unresolved_alerts(self, table_name: str = None) -> List[QualityAlert]:
        """获取未解决的告警"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if table_name:
                cursor = conn.execute("""
                    SELECT * FROM quality_alerts
                    WHERE resolved = 0 AND table_name = ?
                    ORDER BY triggered_at DESC
                """, (table_name,))
            else:
                cursor = conn.execute("""
                    SELECT * FROM quality_alerts
                    WHERE resolved = 0
                    ORDER BY triggered_at DESC
                """)
            
            rows = cursor.fetchall()
            alerts = []
            for row in rows:
                data = dict(row)
                data['alert_level'] = AlertLevel(data['alert_level'])
                data['triggered_at'] = datetime.datetime.fromisoformat(data['triggered_at'])
                if data['acknowledged_at']:
                    data['acknowledged_at'] = datetime.datetime.fromisoformat(data['acknowledged_at'])
                if data['resolved_at']:
                    data['resolved_at'] = datetime.datetime.fromisoformat(data['resolved_at'])
                alerts.append(QualityAlert(**data))
            
            return alerts
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """确认告警"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                UPDATE quality_alerts
                SET acknowledged = 1, acknowledged_by = ?, acknowledged_at = ?
                WHERE id = ? AND resolved = 0
            """, (acknowledged_by, datetime.datetime.now().isoformat(), alert_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def resolve_alert(self, alert_id: str, resolved_by: str) -> bool:
        """解决告警"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                UPDATE quality_alerts
                SET resolved = 1, resolved_by = ?, resolved_at = ?
                WHERE id = ?
            """, (resolved_by, datetime.datetime.now().isoformat(), alert_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def save_report(self, report: QualityReport) -> str:
        """保存报告"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO quality_reports
                (id, monitor_id, table_name, report_date, overall_score,
                 total_rules, passed_rules, failed_rules, total_issues,
                 new_issues, resolved_issues, summary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                report.id, report.monitor_id, report.table_name, report.report_date.isoformat(),
                report.overall_score, report.total_rules, report.passed_rules, report.failed_rules,
                report.total_issues, report.new_issues, report.resolved_issues, json.dumps(report.summary)
            ))
            conn.commit()
        
        return report.id
    
    def get_reports_by_monitor(self, monitor_id: str, limit: int = 30) -> List[QualityReport]:
        """获取监控的报告"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM quality_reports
                WHERE monitor_id = ?
                ORDER BY report_date DESC
                LIMIT ?
            """, (monitor_id, limit))
            
            rows = cursor.fetchall()
            reports = []
            for row in rows:
                data = dict(row)
                data['report_date'] = datetime.datetime.fromisoformat(data['report_date'])
                data['summary'] = json.loads(data['summary'])
                reports.append(QualityReport(**data))
            
            return reports
    
    def get_monitor_statistics(self) -> Dict[str, Any]:
        """获取监控统计信息"""
        with sqlite3.connect(self.db_path) as conn:
            # 总监控数
            cursor = conn.execute("SELECT COUNT(*) FROM quality_monitors")
            total_monitors = cursor.fetchone()[0]
            
            # 按状态统计
            cursor = conn.execute("""
                SELECT status, COUNT(*) FROM quality_monitors 
                GROUP BY status
            """)
            status_distribution = dict(cursor.fetchall())
            
            # 总告警数
            cursor = conn.execute("SELECT COUNT(*) FROM quality_alerts")
            total_alerts = cursor.fetchone()[0]
            
            # 未解决告警数
            cursor = conn.execute("SELECT COUNT(*) FROM quality_alerts WHERE resolved = 0")
            unresolved_alerts = cursor.fetchone()[0]
            
            # 最近7天的告警数
            seven_days_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()
            cursor = conn.execute("""
                SELECT COUNT(*) FROM quality_alerts 
                WHERE triggered_at >= ?
            """, (seven_days_ago,))
            recent_alerts = cursor.fetchone()[0]
            
            # 按级别统计告警
            cursor = conn.execute("""
                SELECT alert_level, COUNT(*) FROM quality_alerts 
                GROUP BY alert_level
            """)
            alert_level_distribution = dict(cursor.fetchall())
            
            return {
                'total_monitors': total_monitors,
                'status_distribution': status_distribution,
                'total_alerts': total_alerts,
                'unresolved_alerts': unresolved_alerts,
                'recent_alerts': recent_alerts,
                'alert_level_distribution': alert_level_distribution,
                'last_updated': datetime.datetime.now().isoformat()
            }

class QualityMonitorManager:
    """质量监控管理器"""
    
    def __init__(self, rule_manager=None, monitor: DataQualityMonitor = None, repository: QualityMonitorRepository = None):
        self.rule_manager = rule_manager
        self.monitor = monitor or DataQualityMonitor(rule_manager)
        self.repository = repository or QualityMonitorRepository()
    
    def create_monitor(self, name: str, description: str, table_name: str, 
                      schedule: str, rules: List[str], thresholds: Dict[str, Any] = None,
                      alert_channels: List[str] = None, created_by: str = "system") -> str:
        """创建质量监控"""
        
        # 设置默认阈值
        if not thresholds:
            thresholds = {
                'failed_rules_percentage': 10,  # 失败规则百分比阈值
                'new_issues_count': 5,  # 新问题数量阈值
                'overall_score': 0.9  # 总体质量分数阈值
            }
        
        # 设置默认告警渠道
        if not alert_channels:
            alert_channels = ['log']
        
        # 创建监控对象
        monitor = QualityMonitor(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            table_name=table_name,
            schedule=schedule,
            status=MonitorStatus.ACTIVE,
            rules=rules,
            thresholds=thresholds,
            alert_channels=[AlertChannel(channel) for channel in alert_channels],
            created_by=created_by,
            created_at=datetime.datetime.now()
        )
        
        # 保存监控
        self.repository.save_monitor(monitor)
        logger.info(f"创建了质量监控: {name} (ID: {monitor.id})")
        
        return monitor.id
    
    def update_monitor(self, monitor_id: str, updates: Dict[str, Any], updated_by: str = "system") -> bool:
        """更新质量监控"""
        monitor = self.repository.get_monitor_by_id(monitor_id)
        if not monitor:
            return False
        
        # 应用更新
        if 'name' in updates:
            monitor.name = updates['name']
        
        if 'description' in updates:
            monitor.description = updates['description']
        
        if 'schedule' in updates:
            monitor.schedule = updates['schedule']
        
        if 'status' in updates:
            monitor.status = MonitorStatus(updates['status'])
        
        if 'rules' in updates:
            monitor.rules = updates['rules']
        
        if 'thresholds' in updates:
            monitor.thresholds = updates['thresholds']
        
        if 'alert_channels' in updates:
            monitor.alert_channels = [AlertChannel(channel) for channel in updates['alert_channels']]
        
        monitor.updated_by = updated_by
        monitor.updated_at = datetime.datetime.now()
        
        # 保存更新
        self.repository.save_monitor(monitor)
        return True
    
    def get_monitor(self, monitor_id: str) -> Optional[Dict[str, Any]]:
        """获取监控详情"""
        monitor = self.repository.get_monitor_by_id(monitor_id)
        return monitor.to_dict() if monitor else None
    
    def get_monitors_by_table(self, table_name: str) -> List[Dict[str, Any]]:
        """根据表名获取监控"""
        monitors = self.repository.get_monitors_by_table(table_name)
        return [monitor.to_dict() for monitor in monitors]
    
    def get_active_monitors(self) -> List[Dict[str, Any]]:
        """获取所有激活的监控"""
        monitors = self.repository.get_active_monitors()
        return [monitor.to_dict() for monitor in monitors]
    
    def run_monitor(self, monitor_id: str, data_source_func: Callable) -> Dict[str, Any]:
        """运行监控检查"""
        # 获取监控配置
        monitor = self.repository.get_monitor_by_id(monitor_id)
        if not monitor:
            return {"error": f"未找到监控: {monitor_id}"}
        
        if monitor.status != MonitorStatus.ACTIVE:
            return {"error": f"监控 {monitor_id} 未激活"}
        
        try:
            # 获取数据
            table_name = monitor.table_name
            df = data_source_func(table_name)
            
            if df is None or df.empty:
                return {"error": f"无法获取表 {table_name} 的数据"}
            
            # 运行质量规则检查
            if self.rule_manager:
                rule_results = self.rule_manager.run_rules_on_table(df, table_name)
            else:
                return {"error": "规则管理器未配置"}
            
            # 检查阈值并生成告警
            alerts = self.monitor.check_thresholds(monitor, rule_results)
            
            # 发送告警
            notification_results = {}
            for alert in alerts:
                # 保存告警
                self.repository.save_alert(alert)
                
                # 发送通知
                results = self.monitor.send_alert(alert)
                notification_results[alert.id] = results
            
            # 生成报告
            total_rules = len(rule_results)
            failed_rules = sum(1 for result in rule_results if result['failed_rows'] > 0)
            total_issues = sum(result['failed_rows'] for result in rule_results)
            overall_score = sum(result['pass_rate'] for result in rule_results) / total_rules if total_rules > 0 else 0
            
            report = QualityReport(
                id=str(uuid.uuid4()),
                monitor_id=monitor.id,
                table_name=table_name,
                report_date=datetime.datetime.now(),
                overall_score=overall_score,
                total_rules=total_rules,
                passed_rules=total_rules - failed_rules,
                failed_rules=failed_rules,
                total_issues=total_issues,
                new_issues=total_issues,
                resolved_issues=0,  # 这里需要逻辑来计算解决的问题
                summary={
                    'rule_results': rule_results,
                    'alerts': [alert.to_dict() for alert in alerts],
                    'notification_results': notification_results
                }
            )
            
            self.repository.save_report(report)
            
            # 更新监控运行时间
            next_run = datetime.datetime.now() + datetime.timedelta(hours=1)  # 简化，实际应根据schedule计算
            self.repository.update_monitor_run_time(monitor_id, datetime.datetime.now(), next_run)
            
            return {
                "monitor_id": monitor_id,
                "table_name": table_name,
                "total_rows": len(df),
                "total_rules": total_rules,
                "failed_rules": failed_rules,
                "total_issues": total_issues,
                "overall_score": overall_score,
                "alerts_generated": len(alerts),
                "report_id": report.id
            }
        
        except Exception as e:
            logger.error(f"运行监控失败: {monitor_id}, 错误: {str(e)}")
            return {"error": str(e)}
    
    def get_alerts(self, monitor_id: str = None, table_name: str = None, unresolved_only: bool = False, limit: int = 100) -> List[Dict[str, Any]]:
        """获取告警"""
        if monitor_id:
            alerts = self.repository.get_alerts_by_monitor(monitor_id, limit)
        elif unresolved_only:
            alerts = self.repository.get_unresolved_alerts(table_name)
        else:
            # 这里需要实现更复杂的查询逻辑
            if table_name:
                alerts = self.repository.get_unresolved_alerts(table_name)
            else:
                alerts = self.repository.get_unresolved_alerts()
        
        return [alert.to_dict() for alert in alerts]
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """确认告警"""
        return self.repository.acknowledge_alert(alert_id, acknowledged_by)
    
    def resolve_alert(self, alert_id: str, resolved_by: str) -> bool:
        """解决告警"""
        return self.repository.resolve_alert(alert_id, resolved_by)
    
    def get_reports(self, monitor_id: str, limit: int = 30) -> List[Dict[str, Any]]:
        """获取报告"""
        reports = self.repository.get_reports_by_monitor(monitor_id, limit)
        return [report.to_dict() for report in reports]
    
    def get_monitor_statistics(self) -> Dict[str, Any]:
        """获取监控统计信息"""
        return self.repository.get_monitor_statistics()
    
    def configure_email_alerts(self, smtp_server: str, smtp_port: int, username: str, password: str, from_address: str):
        """配置邮件告警"""
        self.monitor.configure_email_notifier(smtp_server, smtp_port, username, password, from_address)
        logger.info("配置了邮件告警通知器")
    
    def configure_webhook_alerts(self, webhook_url: str, headers: Dict[str, str] = None):
        """配置Webhook告警"""
        self.monitor.configure_webhook_notifier(webhook_url, headers)
        logger.info("配置了Webhook告警通知器")

def main():
    """主函数，演示数据质量监控使用"""
    print("=" * 50)
    print("数据质量监控工具演示")
    print("=" * 50)
    
    # 这里需要导入规则管理器，但为了避免循环导入，我们简化处理
    # from data_quality_rules_engine import QualityRuleManager
    # rule_manager = QualityRuleManager()
    
    # 创建质量监控管理器（不使用规则管理器）
    manager = QualityMonitorManager()
    
    # 1. 创建质量监控
    print("\n1. 创建质量监控...")
    
    # 创建一个示例监控
    monitor_id = manager.create_monitor(
        name="员工表质量监控",
        description="监控员工表的数据质量",
        table_name="employees",
        schedule="0 0 * * *",  # 每天午夜执行
        rules=["rule1", "rule2", "rule3"],  # 假设的规则ID
        thresholds={
            'failed_rules_percentage': 10,
            'new_issues_count': 5,
            'overall_score': 0.9
        },
        alert_channels=['log'],  # 只使用日志告警
        created_by="演示用户"
    )
    
    print(f"创建了质量监控，ID: {monitor_id}")
    
    # 2. 获取监控详情
    print("\n2. 获取监控详情...")
    monitor = manager.get_monitor(monitor_id)
    if monitor:
        print(f"监控名称: {monitor['name']}")
        print(f"表名: {monitor['table_name']}")
        print(f"状态: {monitor['status']}")
        print(f"调度: {monitor['schedule']}")
        print(f"规则数量: {len(monitor['rules'])}")
        print(f"告警渠道: {', '.join(monitor['alert_channels'])}")
    
    # 3. 配置告警渠道
    print("\n3. 配置告警渠道...")
    
    # 配置Webhook告警（使用模拟URL）
    manager.configure_webhook_alerts("https://example.com/webhook/data-quality-alerts")
    
    # 更新监控以使用Webhook告警
    manager.update_monitor(monitor_id, {
        'alert_channels': ['log', 'webhook']
    }, "演示用户")
    
    # 获取更新后的监控
    updated_monitor = manager.get_monitor(monitor_id)
    if updated_monitor:
        print(f"更新后的告警渠道: {', '.join(updated_monitor['alert_channels'])}")
    
    # 4. 模拟运行监控（使用模拟数据）
    print("\n4. 模拟运行监控...")
    
    def mock_data_source(table_name):
        """模拟数据源"""
        if table_name == "employees":
            # 创建一个包含质量问题的模拟DataFrame
            data = {
                'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace', 'Henry', 'Ivy', 'Jack'],
                'email': ['alice@example.com', 'bob@example.com', 'charlie@example.com', 'david@example.com', 
                          'eve@example.com', 'frank@example.com', 'grace@example.com', 'henry@example.com',
                          'ivy@example.com', 'invalid-email'],  # 包含一个无效邮箱
                'age': [25, 30, 35, 40, 45, 50, 55, 60, 65, 200],  # 包含一个异常年龄
                'department': ['IT', 'HR', 'Finance', 'IT', 'Marketing', 'HR', 'IT', 'Finance', 'Marketing', None],  # 包含一个空值
                'join_date': ['2020-01-15', '2019-05-20', '2018-11-10', '2021-02-28', 
                              '2017-07-05', '2022-03-12', '2016-09-18', '2023-01-25', 
                              '2015-04-30', 'invalid-date']  # 包含一个无效日期
            }
            return pd.DataFrame(data)
        return pd.DataFrame()
    
    # 由于没有规则管理器，我们直接模拟运行结果
    # 在实际使用中，这将是 rule_manager.run_rules_on_table(df, table_name) 的结果
    mock_rule_results = [
        {
            'rule_id': 'rule1',
            'table_name': 'employees',
            'column_name': 'email',
            'total_rows': 10,
            'passed_rows': 9,
            'failed_rows': 1,
            'pass_rate': 0.9,
            'issues': [
                {
                    'id': 'issue1',
                    'row_identifier': 9,
                    'issue_message': '邮箱格式不正确',
                    'issue_value': 'invalid-email'
                }
            ]
        },
        {
            'rule_id': 'rule2',
            'table_name': 'employees',
            'column_name': 'age',
            'total_rows': 10,
            'passed_rows': 9,
            'failed_rows': 1,
            'pass_rate': 0.9,
            'issues': [
                {
                    'id': 'issue2',
                    'row_identifier': 9,
                    'issue_message': '年龄超出范围',
                    'issue_value': 200
                }
            ]
        },
        {
            'rule_id': 'rule3',
            'table_name': 'employees',
            'column_name': 'department',
            'total_rows': 10,
            'passed_rows': 9,
            'failed_rows': 1,
            'pass_rate': 0.9,
            'issues': [
                {
                    'id': 'issue3',
                    'row_identifier': 9,
                    'issue_message': '部门值为空',
                    'issue_value': None
                }
            ]
        }
    ]
    
    # 手动创建告警（因为没有规则管理器）
    monitor = manager.repository.get_monitor_by_id(monitor_id)
    alerts = []
    
    # 检查阈值并生成告警
    total_rules = len(mock_rule_results)
    failed_rules = sum(1 for result in mock_rule_results if result['failed_rows'] > 0)
    failed_percentage = (failed_rules / total_rules) * 100 if total_rules > 0 else 0
    total_issues = sum(result['failed_rows'] for result in mock_rule_results)
    overall_score = sum(result['pass_rate'] for result in mock_rule_results) / total_rules if total_rules > 0 else 0
    
    # 检查失败规则百分比
    if failed_percentage > monitor.thresholds.get('failed_rules_percentage', 10):
        alert_level = AlertLevel.CRITICAL if failed_percentage > (monitor.thresholds.get('failed_rules_percentage', 10) * 2) else AlertLevel.ERROR
        alert = QualityAlert(
            id=str(uuid.uuid4()),
            monitor_id=monitor.id,
            table_name=monitor.table_name,
            rule_id="threshold_check",
            rule_name="失败规则百分比阈值检查",
            alert_level=alert_level,
            message=f"失败规则百分比 {failed_percentage:.1f}% 超过阈值 {monitor.thresholds.get('failed_rules_percentage', 10)}%",
            metrics={
                'failed_rules_percentage': failed_percentage,
                'threshold': monitor.thresholds.get('failed_rules_percentage', 10),
                'total_rules': total_rules,
                'failed_rules': failed_rules
            },
            triggered_at=datetime.datetime.now()
        )
        alerts.append(alert)
    
    # 发送告警
    for alert in alerts:
        manager.repository.save_alert(alert)
        results = manager.monitor.send_alert(alert)
        print(f"发送告警 {alert.id} 到各渠道的结果: {results}")
    
    # 5. 获取告警
    print("\n5. 获取告警...")
    all_alerts = manager.get_alerts(unresolved_only=True)
    print(f"未解决的告警数量: {len(all_alerts)}")
    for alert in all_alerts:
        print(f"- {alert['rule_name']}: {alert['message']} (级别: {alert['alert_level']})")
    
    # 6. 确认告警
    if all_alerts:
        print("\n6. 确认告警...")
        alert_id = all_alerts[0]['id']
        success = manager.acknowledge_alert(alert_id, "演示用户")
        print(f"确认告警 {alert_id}: {'成功' if success else '失败'}")
        
        # 获取更新后的告警
        updated_alert = manager.repository.get_alerts_by_monitor(monitor_id, limit=1)[0]
        print(f"确认状态: {updated_alert.acknowledged}, 确认人: {updated_alert.acknowledged_by}")
    
    # 7. 解决告警
    if all_alerts:
        print("\n7. 解决告警...")
        alert_id = all_alerts[0]['id']
        success = manager.resolve_alert(alert_id, "演示用户")
        print(f"解决告警 {alert_id}: {'成功' if success else '失败'}")
    
    # 8. 获取监控统计信息
    print("\n8. 获取监控统计信息...")
    stats = manager.get_monitor_statistics()
    print(f"总监控数: {stats['total_monitors']}")
    print(f"状态分布: {stats['status_distribution']}")
    print(f"总告警数: {stats['total_alerts']}")
    print(f"未解决告警数: {stats['unresolved_alerts']}")
    print(f"最近7天告警数: {stats['recent_alerts']}")
    print(f"告警级别分布: {stats['alert_level_distribution']}")
    
    # 9. 创建第二个监控
    print("\n9. 创建第二个监控...")
    product_monitor_id = manager.create_monitor(
        name="产品表质量监控",
        description="监控产品表的数据质量",
        table_name="products",
        schedule="0 6 * * *",  # 每天早上6点执行
        rules=["rule4", "rule5"],  # 假设的规则ID
        thresholds={
            'failed_rules_percentage': 5,
            'new_issues_count': 3,
            'overall_score': 0.95
        },
        alert_channels=['log', 'webhook'],
        created_by="演示用户"
    )
    
    print(f"创建了产品表监控，ID: {product_monitor_id}")
    
    # 10. 获取所有监控
    print("\n10. 获取所有监控...")
    all_monitors = manager.get_active_monitors()
    print(f"激活的监控数量: {len(all_monitors)}")
    for monitor in all_monitors:
        print(f"- {monitor['name']} ({monitor['table_name']}) - 状态: {monitor['status']}")

if __name__ == "__main__":
    main()