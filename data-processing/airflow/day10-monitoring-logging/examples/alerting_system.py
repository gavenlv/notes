#!/usr/bin/env python3
"""
Airflow告警系统示例

这个脚本演示了如何实现一个自定义的Airflow告警系统，
包括基于指标的告警、基于日志的告警和通知机制。
"""

import smtplib
import json
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from dataclasses import dataclass, asdict
from enum import Enum

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """告警严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(Enum):
    """告警状态"""
    TRIGGERED = "triggered"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"

@dataclass
class Alert:
    """告警数据类"""
    id: str
    title: str
    description: str
    severity: AlertSeverity
    source: str
    timestamp: datetime
    status: AlertStatus = AlertStatus.TRIGGERED
    metadata: Dict[str, Any] = None

class NotificationChannel:
    """通知渠道基类"""
    
    def send(self, alert: Alert) -> bool:
        """
        发送告警通知
        
        Args:
            alert: 告警对象
            
        Returns:
            发送是否成功
        """
        raise NotImplementedError

class EmailNotificationChannel(NotificationChannel):
    """邮件通知渠道"""
    
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, 
                 from_addr: str, to_addrs: List[str]):
        """
        初始化邮件通知渠道
        
        Args:
            smtp_server: SMTP服务器地址
            smtp_port: SMTP端口
            username: SMTP用户名
            password: SMTP密码
            from_addr: 发件人地址
            to_addrs: 收件人地址列表
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_addr = from_addr
        self.to_addrs = to_addrs
        
    def send(self, alert: Alert) -> bool:
        """发送邮件告警"""
        try:
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = self.from_addr
            msg['To'] = ', '.join(self.to_addrs)
            msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.title}"
            
            # 邮件正文
            body = f"""
告警详情:
标题: {alert.title}
描述: {alert.description}
来源: {alert.source}
时间: {alert.timestamp.isoformat()}
严重程度: {alert.severity.value}
状态: {alert.status.value}

元数据:
{json.dumps(alert.metadata or {}, indent=2, ensure_ascii=False)}
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 发送邮件
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
                
            logger.info(f"Email alert sent successfully: {alert.title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False

class SlackNotificationChannel(NotificationChannel):
    """Slack通知渠道"""
    
    def __init__(self, webhook_url: str):
        """
        初始化Slack通知渠道
        
        Args:
            webhook_url: Slack webhook URL
        """
        self.webhook_url = webhook_url
        
    def send(self, alert: Alert) -> bool:
        """发送Slack告警"""
        try:
            # 构造Slack消息
            severity_colors = {
                AlertSeverity.LOW: "#36a64f",      # 绿色
                AlertSeverity.MEDIUM: "#ffff00",   # 黄色
                AlertSeverity.HIGH: "#ff9900",     # 橙色
                AlertSeverity.CRITICAL: "#ff0000"  # 红色
            }
            
            payload = {
                "attachments": [
                    {
                        "color": severity_colors.get(alert.severity, "#36a64f"),
                        "title": alert.title,
                        "text": alert.description,
                        "fields": [
                            {
                                "title": "来源",
                                "value": alert.source,
                                "short": True
                            },
                            {
                                "title": "严重程度",
                                "value": alert.severity.value,
                                "short": True
                            },
                            {
                                "title": "时间",
                                "value": alert.timestamp.isoformat(),
                                "short": True
                            }
                        ],
                        "footer": "Airflow告警系统",
                        "ts": int(alert.timestamp.timestamp())
                    }
                ]
            }
            
            # 发送请求
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            
            logger.info(f"Slack alert sent successfully: {alert.title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            return False

class AlertRule:
    """告警规则"""
    
    def __init__(self, name: str, condition: str, severity: AlertSeverity, 
                 description: str = ""):
        """
        初始化告警规则
        
        Args:
            name: 规则名称
            condition: 告警条件（表达式）
            severity: 告警严重程度
            description: 规则描述
        """
        self.name = name
        self.condition = condition
        self.severity = severity
        self.description = description
        self.enabled = True
        self.last_triggered = None
        
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        评估告警条件
        
        Args:
            context: 评估上下文（变量）
            
        Returns:
            是否满足告警条件
        """
        try:
            # 简单的条件评估（实际应用中可能需要更复杂的表达式解析）
            # 这里仅支持简单的比较操作
            if '>=' in self.condition:
                left, right = self.condition.split('>=')
                left_val = self._get_value(left.strip(), context)
                right_val = self._get_value(right.strip(), context)
                return left_val >= right_val
            elif '>' in self.condition:
                left, right = self.condition.split('>')
                left_val = self._get_value(left.strip(), context)
                right_val = self._get_value(right.strip(), context)
                return left_val > right_val
            elif '<=' in self.condition:
                left, right = self.condition.split('<=')
                left_val = self._get_value(left.strip(), context)
                right_val = self._get_value(right.strip(), context)
                return left_val <= right_val
            elif '<' in self.condition:
                left, right = self.condition.split('<')
                left_val = self._get_value(left.strip(), context)
                right_val = self._get_value(right.strip(), context)
                return left_val < right_val
            elif '==' in self.condition:
                left, right = self.condition.split('==')
                left_val = self._get_value(left.strip(), context)
                right_val = self._get_value(right.strip(), context)
                return left_val == right_val
            else:
                logger.warning(f"Unsupported condition format: {self.condition}")
                return False
                
        except Exception as e:
            logger.error(f"Error evaluating condition '{self.condition}': {e}")
            return False
    
    def _get_value(self, key: str, context: Dict[str, Any]) -> Any:
        """从上下文中获取值"""
        # 支持嵌套键访问，如 "metrics.dag_failure_rate"
        keys = key.split('.')
        value = context
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                # 如果键不存在，尝试转换为数字
                try:
                    return float(key)
                except ValueError:
                    return key
        return value

class AlertManager:
    """告警管理器"""
    
    def __init__(self):
        """初始化告警管理器"""
        self.rules: List[AlertRule] = []
        self.channels: List[NotificationChannel] = []
        self.alert_history: List[Alert] = []
        self.alert_cooldown: Dict[str, datetime] = {}  # 告警冷却时间
        self.cooldown_period = timedelta(minutes=5)  # 默认5分钟冷却时间
        
    def add_rule(self, rule: AlertRule):
        """添加告警规则"""
        self.rules.append(rule)
        logger.info(f"Added alert rule: {rule.name}")
        
    def add_channel(self, channel: NotificationChannel):
        """添加通知渠道"""
        self.channels.append(channel)
        logger.info(f"Added notification channel")
        
    def add_channels_from_config(self, config: Dict[str, Any]):
        """从配置添加通知渠道"""
        channels_config = config.get('channels', [])
        for channel_config in channels_config:
            channel_type = channel_config.get('type')
            if channel_type == 'email':
                channel = EmailNotificationChannel(
                    smtp_server=channel_config['smtp_server'],
                    smtp_port=channel_config['smtp_port'],
                    username=channel_config['username'],
                    password=channel_config['password'],
                    from_addr=channel_config['from_addr'],
                    to_addrs=channel_config['to_addrs']
                )
                self.add_channel(channel)
            elif channel_type == 'slack':
                channel = SlackNotificationChannel(
                    webhook_url=channel_config['webhook_url']
                )
                self.add_channel(channel)
                
    def evaluate_rules(self, context: Dict[str, Any]):
        """评估所有告警规则"""
        logger.debug("Evaluating alert rules")
        
        for rule in self.rules:
            if not rule.enabled:
                continue
                
            # 检查冷却时间
            if rule.name in self.alert_cooldown:
                if datetime.now() - self.alert_cooldown[rule.name] < self.cooldown_period:
                    continue
            
            # 评估规则
            if rule.evaluate(context):
                logger.info(f"Alert rule triggered: {rule.name}")
                self.trigger_alert(rule, context)
                # 设置冷却时间
                self.alert_cooldown[rule.name] = datetime.now()
                
    def trigger_alert(self, rule: AlertRule, context: Dict[str, Any]):
        """触发告警"""
        alert = Alert(
            id=f"{rule.name}_{int(datetime.now().timestamp())}",
            title=f"告警: {rule.name}",
            description=rule.description or f"告警规则 '{rule.name}' 被触发",
            severity=rule.severity,
            source="AirflowAlertSystem",
            timestamp=datetime.now(),
            metadata=context
        )
        
        self.alert_history.append(alert)
        logger.info(f"Alert triggered: {alert.title}")
        
        # 通过所有渠道发送告警
        for channel in self.channels:
            try:
                channel.send(alert)
            except Exception as e:
                logger.error(f"Failed to send alert through channel: {e}")
                
    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """获取告警历史"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.alert_history if alert.timestamp >= cutoff_time]

# 示例配置
ALERT_CONFIG = {
    "channels": [
        {
            "type": "email",
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "username": "alert@example.com",
            "password": "password",
            "from_addr": "alert@example.com",
            "to_addrs": ["admin@example.com", "ops@example.com"]
        },
        {
            "type": "slack",
            "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
        }
    ]
}

# 示例告警规则
EXAMPLE_RULES = [
    AlertRule(
        name="high_dag_failure_rate",
        condition="metrics.dag_failure_rate >= 0.1",
        severity=AlertSeverity.HIGH,
        description="DAG失败率超过10%"
    ),
    AlertRule(
        name="scheduler_down",
        condition="scheduler.heartbeat_age > 120",
        severity=AlertSeverity.CRITICAL,
        description="调度器心跳超时（超过2分钟）"
    ),
    AlertRule(
        name="task_queue_backlog",
        condition="queue.pending_tasks >= 50",
        severity=AlertSeverity.MEDIUM,
        description="任务队列积压超过50个任务"
    )
]

def main():
    """主函数"""
    # 创建告警管理器
    alert_manager = AlertManager()
    
    # 添加通知渠道
    alert_manager.add_channels_from_config(ALERT_CONFIG)
    
    # 添加告警规则
    for rule in EXAMPLE_RULES:
        alert_manager.add_rule(rule)
    
    # 模拟监控数据
    mock_context = {
        "metrics": {
            "dag_failure_rate": 0.15,  # 15%失败率
            "task_success_rate": 0.85,
            "average_task_duration": 120.5
        },
        "scheduler": {
            "heartbeat_age": 60,  # 1分钟前的心跳
            "status": "healthy"
        },
        "queue": {
            "pending_tasks": 30,
            "running_tasks": 15
        }
    }
    
    # 评估告警规则
    logger.info("Starting alert evaluation loop")
    try:
        while True:
            alert_manager.evaluate_rules(mock_context)
            
            # 更新模拟数据（随机变化）
            import random
            mock_context["metrics"]["dag_failure_rate"] = random.uniform(0.05, 0.2)
            mock_context["scheduler"]["heartbeat_age"] = random.randint(30, 180)
            mock_context["queue"]["pending_tasks"] = random.randint(10, 100)
            
            time.sleep(10)  # 每10秒检查一次
            
    except KeyboardInterrupt:
        logger.info("Alert system stopped")

if __name__ == '__main__':
    main()