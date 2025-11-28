"""
第7章：安全与认证 - 安全监控与审计系统
演示安全事件监控、审计日志、实时安全检查和自动响应机制
"""

import logging
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import re


class SecurityEventType(Enum):
    """安全事件类型"""
    AUTHENTICATION_SUCCESS = "authentication_success"
    AUTHENTICATION_FAILURE = "authentication_failure"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    PERMISSION_DENIED = "permission_denied"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_BREACH_ATTEMPT = "data_breach_attempt"
    SYSTEM_COMPROMISE = "system_compromise"


class SecuritySeverity(Enum):
    """安全事件严重级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityEvent:
    """安全事件数据类"""
    event_id: str
    event_type: SecurityEventType
    severity: SecuritySeverity
    timestamp: datetime
    source_ip: str
    user_id: str
    resource: str
    description: str
    details: Dict
    resolved: bool = False
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'severity': self.severity.value,
            'timestamp': self.timestamp.isoformat(),
            'source_ip': self.source_ip,
            'user_id': self.user_id,
            'resource': self.resource,
            'description': self.description,
            'details': self.details,
            'resolved': self.resolved
        }


class SecurityAuditor:
    """安全审计器"""
    
    def __init__(self, log_file='security_audit.log'):
        self.logger = logging.getLogger('SecurityAuditor')
        self.logger.setLevel(logging.INFO)
        
        # 文件处理器
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # 审计事件存储
        self.audit_events: List[SecurityEvent] = []
        self.event_counter = 0
        
        # 统计数据
        self.stats = {
            'total_events': 0,
            'events_by_type': {},
            'events_by_severity': {},
            'events_by_user': {},
            'events_by_ip': {}
        }
    
    def generate_event_id(self) -> str:
        """生成事件ID"""
        self.event_counter += 1
        return f"SEC-{datetime.now().strftime('%Y%m%d')}-{self.event_counter:06d}"
    
    def log_security_event(self, event: SecurityEvent) -> str:
        """记录安全事件"""
        # 生成事件ID
        event.event_id = self.generate_event_id()
        
        # 添加到审计列表
        self.audit_events.append(event)
        
        # 记录到日志
        log_message = f"SECURITY_EVENT - {event.severity.value.upper()}: {event.description}"
        if event.severity == SecuritySeverity.CRITICAL:
            self.logger.critical(log_message)
        elif event.severity == SecuritySeverity.HIGH:
            self.logger.error(log_message)
        elif event.severity == SecuritySeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
        
        # 更新统计数据
        self._update_stats(event)
        
        # 触发安全响应
        self._trigger_security_response(event)
        
        return event.event_id
    
    def _update_stats(self, event: SecurityEvent):
        """更新统计数据"""
        self.stats['total_events'] += 1
        
        # 按类型统计
        event_type = event.event_type.value
        self.stats['events_by_type'][event_type] = self.stats['events_by_type'].get(event_type, 0) + 1
        
        # 按严重级别统计
        severity = event.severity.value
        self.stats['events_by_severity'][severity] = self.stats['events_by_severity'].get(severity, 0) + 1
        
        # 按用户统计
        self.stats['events_by_user'][event.user_id] = self.stats['events_by_user'].get(event.user_id, 0) + 1
        
        # 按IP统计
        self.stats['events_by_ip'][event.source_ip] = self.stats['events_by_ip'].get(event.source_ip, 0) + 1
    
    def _trigger_security_response(self, event: SecurityEvent):
        """触发安全响应"""
        # 根据事件类型和严重级别执行响应动作
        if event.severity == SecuritySeverity.CRITICAL:
            self._handle_critical_event(event)
        elif event.severity == SecuritySeverity.HIGH:
            self._handle_high_severity_event(event)
        elif event.event_type == SecurityEventType.AUTHENTICATION_FAILURE:
            self._handle_authentication_failure(event)
    
    def _handle_critical_event(self, event: SecurityEvent):
        """处理严重事件"""
        print(f"🚨 严重安全事件: {event.description}")
        print(f"   事件ID: {event.event_id}")
        print(f"   用户: {event.user_id}")
        print(f"   IP: {event.source_ip}")
        print(f"   资源: {event.resource}")
        
        # 这里可以集成紧急通知系统
        # 比如发送邮件、短信、Slack消息等
        self._send_emergency_notification(event)
    
    def _handle_high_severity_event(self, event: SecurityEvent):
        """处理高严重性事件"""
        print(f"⚠️ 高风险安全事件: {event.description}")
        
        # 可以记录到专用的高风险事件日志
        self.logger.error(f"HIGH_RISK_EVENT: {event.to_dict()}")
    
    def _handle_authentication_failure(self, event: SecurityEvent):
        """处理认证失败事件"""
        # 这里可以检查失败次数，如果超过阈值则触发更严格的措施
        print(f"🔐 认证失败: {event.user_id} 来自 {event.source_ip}")
    
    def _send_emergency_notification(self, event: SecurityEvent):
        """发送紧急通知"""
        # 模拟紧急通知发送
        notification = {
            'title': '紧急安全事件',
            'severity': event.severity.value,
            'message': event.description,
            'timestamp': event.timestamp.isoformat(),
            'event_id': event.event_id,
            'source_ip': event.source_ip,
            'user_id': event.user_id,
            'resource': event.resource
        }
        
        print(f"📧 紧急通知已发送: {notification}")
        
        # 实际实现中可以集成:
        # - 邮件通知
        # - 短信通知
        # - Slack/Teams通知
        # - 钉钉/企业微信通知
        # - 安全运营中心(SOC)系统
    
    def get_audit_summary(self, hours: int = 24) -> Dict:
        """获取审计摘要"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_events = [
            event for event in self.audit_events 
            if event.timestamp > cutoff_time
        ]
        
        summary = {
            'period_hours': hours,
            'total_events': len(recent_events),
            'unresolved_events': len([e for e in recent_events if not e.resolved]),
            'events_by_type': {},
            'events_by_severity': {},
            'top_users': {},
            'top_source_ips': {},
            'recent_critical_events': []
        }
        
        # 统计最近事件
        for event in recent_events:
            # 按类型统计
            event_type = event.event_type.value
            summary['events_by_type'][event_type] = summary['events_by_type'].get(event_type, 0) + 1
            
            # 按严重级别统计
            severity = event.severity.value
            summary['events_by_severity'][severity] = summary['events_by_severity'].get(severity, 0) + 1
            
            # 按用户统计
            summary['top_users'][event.user_id] = summary['top_users'].get(event.user_id, 0) + 1
            
            # 按IP统计
            summary['top_source_ips'][event.source_ip] = summary['top_source_ips'].get(event.source_ip, 0) + 1
            
            # 最近严重事件
            if event.severity in [SecuritySeverity.HIGH, SecuritySeverity.CRITICAL]:
                summary['recent_critical_events'].append(event.to_dict())
        
        # 排序top用户和IP
        summary['top_users'] = dict(sorted(summary['top_users'].items(), key=lambda x: x[1], reverse=True)[:10])
        summary['top_source_ips'] = dict(sorted(summary['top_source_ips'].items(), key=lambda x: x[1], reverse=True)[:10])
        
        return summary
    
    def export_audit_log(self, filename: str, start_time: datetime = None, end_time: datetime = None):
        """导出审计日志"""
        filtered_events = self.audit_events
        
        if start_time:
            filtered_events = [e for e in filtered_events if e.timestamp >= start_time]
        
        if end_time:
            filtered_events = [e for e in filtered_events if e.timestamp <= end_time]
        
        export_data = {
            'export_time': datetime.now().isoformat(),
            'total_events': len(filtered_events),
            'events': [event.to_dict() for event in filtered_events]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"📁 审计日志已导出到: {filename}")


class SecurityRuleEngine:
    """安全规则引擎"""
    
    def __init__(self, auditor: SecurityAuditor):
        self.auditor = auditor
        self.rules = []
        self.failed_logins: Dict[str, List[datetime]] = {}  # {user: [timestamps]}
        self.suspicious_ips: Dict[str, int] = {}  # {ip: count}
        self.user_activities: Dict[str, List[Dict]] = {}  # {user: [{timestamp, action, resource}]}
    
    def add_rule(self, rule_func):
        """添加安全规则"""
        self.rules.append(rule_func)
    
    def check_authentication_event(self, user_id: str, source_ip: str, success: bool):
        """检查认证事件"""
        current_time = datetime.now()
        
        if not success:
            # 记录失败登录
            if user_id not in self.failed_logins:
                self.failed_logins[user_id] = []
            
            self.failed_logins[user_id].append(current_time)
            
            # 检查是否超过失败阈值
            window_start = current_time - timedelta(minutes=15)
            recent_failures = [ts for ts in self.failed_logins[user_id] if ts > window_start]
            
            if len(recent_failures) >= 5:
                # 触发多次登录失败事件
                event = SecurityEvent(
                    event_id="",
                    event_type=SecurityEventType.AUTHENTICATION_FAILURE,
                    severity=SecuritySeverity.HIGH,
                    timestamp=current_time,
                    source_ip=source_ip,
                    user_id=user_id,
                    resource="authentication",
                    description=f"用户 {user_id} 在15分钟内失败登录 {len(recent_failures)} 次",
                    details={'failure_count': len(recent_failures), 'window_minutes': 15}
                )
                self.auditor.log_security_event(event)
            
            # 更新可疑IP计数
            self.suspicious_ips[source_ip] = self.suspicious_ips.get(source_ip, 0) + 1
            
            if self.suspicious_ips[source_ip] >= 10:
                # 触发可疑IP活动事件
                event = SecurityEvent(
                    event_id="",
                    event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
                    severity=SecuritySeverity.MEDIUM,
                    timestamp=current_time,
                    source_ip=source_ip,
                    user_id=user_id,
                    resource="authentication",
                    description=f"IP {source_ip} 显示可疑登录活动 ({self.suspicious_ips[source_ip]} 次失败)",
                    details={'failure_count': self.suspicious_ips[source_ip]}
                )
                self.auditor.log_security_event(event)
        
        else:
            # 成功登录，清理失败记录
            self.failed_logins[user_id] = []
            self.suspicious_ips[source_ip] = 0
    
    def check_user_activity(self, user_id: str, action: str, resource: str):
        """检查用户活动"""
        current_time = datetime.now()
        
        # 记录用户活动
        if user_id not in self.user_activities:
            self.user_activities[user_id] = []
        
        activity = {
            'timestamp': current_time,
            'action': action,
            'resource': resource
        }
        self.user_activities[user_id].append(activity)
        
        # 检查异常活动模式
        self._check_unusual_activity_pattern(user_id, current_time)
        
        # 检查权限提升尝试
        self._check_privilege_escalation(user_id, action, resource)
        
        # 检查数据访问异常
        self._check_data_access_pattern(user_id, resource, current_time)
    
    def _check_unusual_activity_pattern(self, user_id: str, current_time: datetime):
        """检查异常活动模式"""
        window_start = current_time - timedelta(hours=1)
        recent_activities = [
            activity for activity in self.user_activities.get(user_id, [])
            if activity['timestamp'] > window_start
        ]
        
        # 如果用户在1小时内有超过100次活动，认为是异常行为
        if len(recent_activities) > 100:
            event = SecurityEvent(
                event_id="",
                event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
                severity=SecuritySeverity.MEDIUM,
                timestamp=current_time,
                source_ip="unknown",  # 实际实现中需要获取真实IP
                user_id=user_id,
                resource="system",
                description=f"用户 {user_id} 在1小时内执行了 {len(recent_activities)} 次操作，可能存在异常行为",
                details={'activity_count': len(recent_activities), 'window_hours': 1}
            )
            self.auditor.log_security_event(event)
    
    def _check_privilege_escalation(self, user_id: str, action: str, resource: str):
        """检查权限提升尝试"""
        # 权限提升关键词
        escalation_keywords = ['admin', 'root', 'superuser', 'sudo', 'configure', 'management']
        
        if any(keyword in resource.lower() or keyword in action.lower() for keyword in escalation_keywords):
            event = SecurityEvent(
                event_id="",
                event_type=SecurityEventType.PRIVILEGE_ESCALATION,
                severity=SecuritySeverity.HIGH,
                timestamp=datetime.now(),
                source_ip="unknown",
                user_id=user_id,
                resource=resource,
                description=f"用户 {user_id} 可能尝试权限提升: {action} on {resource}",
                details={'action': action, 'resource': resource}
            )
            self.auditor.log_security_event(event)
    
    def _check_data_access_pattern(self, user_id: str, resource: str, current_time: datetime):
        """检查数据访问模式"""
        # 敏感资源关键词
        sensitive_resources = ['user_data', 'financial', 'customer_info', 'employee_data', 'salary']
        
        if any(keyword in resource.lower() for keyword in sensitive_resources):
            event = SecurityEvent(
                event_id="",
                event_type=SecurityEventType.DATA_BREACH_ATTEMPT,
                severity=SecuritySeverity.HIGH,
                timestamp=current_time,
                source_ip="unknown",
                user_id=user_id,
                resource=resource,
                description=f"用户 {user_id} 访问敏感资源: {resource}",
                details={'resource_type': 'sensitive_data'}
            )
            self.auditor.log_security_event(event)


class SecurityMonitor:
    """安全监控器"""
    
    def __init__(self, auditor: SecurityAuditor, rule_engine: SecurityRuleEngine):
        self.auditor = auditor
        self.rule_engine = rule_engine
        self.is_monitoring = False
        self.monitoring_thread = None
        self.stop_event = threading.Event()
        
        # 监控配置
        self.config = {
            'check_interval_seconds': 30,
            'cleanup_old_events_hours': 24,
            'max_events_in_memory': 10000
        }
    
    def start_monitoring(self):
        """开始安全监控"""
        if self.is_monitoring:
            print("⚠️ 安全监控已经在运行中")
            return
        
        self.is_monitoring = True
        self.stop_event.clear()
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        print("🔍 安全监控已启动")
        self.auditor.log_security_event(SecurityEvent(
            event_id="",
            event_type=SecurityEventType.AUTHENTICATION_SUCCESS,
            severity=SecuritySeverity.LOW,
            timestamp=datetime.now(),
            source_ip="localhost",
            user_id="system",
            resource="security_monitor",
            description="安全监控系统启动",
            details={'monitoring_pid': threading.get_ident()}
        ))
    
    def stop_monitoring(self):
        """停止安全监控"""
        if not self.is_monitoring:
            print("⚠️ 安全监控未在运行")
            return
        
        self.is_monitoring = False
        self.stop_event.set()
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        print("⏹️ 安全监控已停止")
        self.auditor.log_security_event(SecurityEvent(
            event_id="",
            event_type=SecurityEventType.AUTHENTICATION_SUCCESS,
            severity=SecuritySeverity.LOW,
            timestamp=datetime.now(),
            source_ip="localhost",
            user_id="system",
            resource="security_monitor",
            description="安全监控系统停止",
            details={}
        ))
    
    def _monitoring_loop(self):
        """监控循环"""
        while not self.stop_event.is_set():
            try:
                # 执行定期检查
                self._perform_periodic_checks()
                
                # 清理旧事件
                self._cleanup_old_events()
                
                # 检查内存使用
                self._check_memory_usage()
                
                # 等待下一次检查
                self.stop_event.wait(self.config['check_interval_seconds'])
                
            except Exception as e:
                print(f"❌ 安全监控循环异常: {e}")
                # 记录监控异常事件
                self.auditor.log_security_event(SecurityEvent(
                    event_id="",
                    event_type=SecurityEventType.SYSTEM_COMPROMISE,
                    severity=SecuritySeverity.HIGH,
                    timestamp=datetime.now(),
                    source_ip="localhost",
                    user_id="system",
                    resource="security_monitor",
                    description=f"安全监控系统异常: {str(e)}",
                    details={'error': str(e)}
                ))
                
                # 发生异常后等待较短时间再继续
                self.stop_event.wait(5)
    
    def _perform_periodic_checks(self):
        """执行定期检查"""
        # 这里可以添加更多定期检查逻辑
        current_time = datetime.now()
        
        # 检查长时间未活跃的用户
        for user_id, activities in self.rule_engine.user_activities.items():
            if activities:
                last_activity = max(activity['timestamp'] for activity in activities)
                if current_time - last_activity > timedelta(hours=24):
                    print(f"👤 用户 {user_id} 超过24小时未活动")
    
    def _cleanup_old_events(self):
        """清理旧事件"""
        cutoff_time = datetime.now() - timedelta(hours=self.config['cleanup_old_events_hours'])
        
        # 清理审计事件
        original_count = len(self.auditor.audit_events)
        self.auditor.audit_events = [
            event for event in self.auditor.audit_events 
            if event.timestamp > cutoff_time
        ]
        
        cleaned_count = original_count - len(self.auditor.audit_events)
        if cleaned_count > 0:
            print(f"🧹 清理了 {cleaned_count} 个超过 {self.config['cleanup_old_events_hours']} 小时的安全事件")
    
    def _check_memory_usage(self):
        """检查内存使用"""
        if len(self.auditor.audit_events) > self.config['max_events_in_memory']:
            print(f"⚠️ 安全事件数量 ({len(self.auditor.audit_events)}) 超过内存限制")
            
            # 触发高优先级事件
            event = SecurityEvent(
                event_id="",
                event_type=SecurityEventType.SYSTEM_COMPROMISE,
                severity=SecuritySeverity.MEDIUM,
                timestamp=datetime.now(),
                source_ip="localhost",
                user_id="system",
                resource="security_monitor",
                description=f"安全监控系统内存使用过高，事件数量: {len(self.auditor.audit_events)}",
                details={'event_count': len(self.auditor.audit_events), 'max_allowed': self.config['max_events_in_memory']}
            )
            self.auditor.log_security_event(event)
    
    def get_monitoring_status(self) -> Dict:
        """获取监控状态"""
        return {
            'is_monitoring': self.is_monitoring,
            'monitoring_thread_alive': self.monitoring_thread.is_alive() if self.monitoring_thread else False,
            'total_events': len(self.auditor.audit_events),
            'monitoring_config': self.config.copy(),
            'system_stats': {
                'failed_logins_tracked': len(self.rule_engine.failed_logins),
                'suspicious_ips_tracked': len(self.rule_engine.suspicious_ips),
                'active_users_tracked': len(self.rule_engine.user_activities)
            }
        }


class SecurityResponseSystem:
    """安全响应系统"""
    
    def __init__(self, auditor: SecurityAuditor):
        self.auditor = auditor
        self.response_actions = {
            SecurityEventType.AUTHENTICATION_FAILURE: self._handle_auth_failure,
            SecurityEventType.PRIVILEGE_ESCALATION: self._handle_privilege_escalation,
            SecurityEventType.DATA_BREACH_ATTEMPT: self._handle_data_breach,
            SecurityEventType.SUSPICIOUS_ACTIVITY: self._handle_suspicious_activity
        }
    
    def handle_security_event(self, event: SecurityEvent):
        """处理安全事件"""
        if event.event_type in self.response_actions:
            try:
                self.response_actions[event.event_type](event)
            except Exception as e:
                print(f"❌ 安全事件处理失败: {e}")
                self.auditor.log_security_event(SecurityEvent(
                    event_id="",
                    event_type=SecurityEventType.SYSTEM_COMPROMISE,
                    severity=SecuritySeverity.HIGH,
                    timestamp=datetime.now(),
                    source_ip="localhost",
                    user_id="system",
                    resource="security_response",
                    description=f"安全响应系统处理事件失败: {event.event_id}",
                    details={'original_event': event.to_dict(), 'error': str(e)}
                ))
    
    def _handle_auth_failure(self, event: SecurityEvent):
        """处理认证失败"""
        print(f"🔐 处理认证失败事件: {event.description}")
        
        # 增加IP黑名单检查逻辑
        # 这里可以调用IP黑名单服务
        print(f"   检查IP黑名单: {event.source_ip}")
        
        # 可以考虑临时禁用该IP的访问
        # self._temporary_block_ip(event.source_ip, minutes=30)
    
    def _handle_privilege_escalation(self, event: SecurityEvent):
        """处理权限提升"""
        print(f"⚠️ 处理权限提升事件: {event.description}")
        
        # 立即记录到高风险日志
        self.auditor.logger.error(f"PRIVILEGE_ESCALATION_DETECTED: {event.to_dict()}")
        
        # 触发紧急通知
        self._send_critical_alert(event)
        
        # 可以考虑临时撤销用户权限
        # self._revoke_user_permissions(event.user_id)
    
    def _handle_data_breach(self, event: SecurityEvent):
        """处理数据泄露尝试"""
        print(f"🚨 处理数据泄露事件: {event.description}")
        
        # 记录到数据泄露日志
        self.auditor.logger.critical(f"DATA_BREACH_ATTEMPT: {event.to_dict()}")
        
        # 立即通知安全团队
        self._send_critical_alert(event)
        
        # 可以考虑暂停用户账户
        # self._suspend_user_account(event.user_id)
    
    def _handle_suspicious_activity(self, event: SecurityEvent):
        """处理可疑活动"""
        print(f"🔍 处理可疑活动事件: {event.description}")
        
        # 增强监控该用户
        print(f"   为用户 {event.user_id} 启用增强监控")
        
        # 可以增加监控频率
        # self._increase_user_monitoring(event.user_id)
    
    def _send_critical_alert(self, event: SecurityEvent):
        """发送严重警报"""
        alert = {
            'level': 'CRITICAL',
            'title': '严重安全事件',
            'message': event.description,
            'event_id': event.event_id,
            'timestamp': event.timestamp.isoformat(),
            'user_id': event.user_id,
            'source_ip': event.source_ip,
            'resource': event.resource,
            'details': event.details,
            'action_required': True
        }
        
        print(f"🚨 严重警报: {alert}")
        
        # 实际实现中发送通知到:
        # - 安全运营中心(SOC)
        # - 安全团队邮件列表
        # - 短信通知
        # - Slack/Teams频道
        # -PagerDuty/AlertManager等告警系统


class SecurityMonitoringDemo:
    """安全监控演示"""
    
    def __init__(self):
        self.auditor = SecurityAuditor()
        self.rule_engine = SecurityRuleEngine(self.auditor)
        self.monitor = SecurityMonitor(self.auditor, self.rule_engine)
        self.response_system = SecurityResponseSystem(self.auditor)
    
    def simulate_security_events(self):
        """模拟安全事件"""
        print("🎭 模拟安全事件")
        print("-" * 40)
        
        # 模拟成功认证
        event = SecurityEvent(
            event_id="",
            event_type=SecurityEventType.AUTHENTICATION_SUCCESS,
            severity=SecuritySeverity.LOW,
            timestamp=datetime.now(),
            source_ip="192.168.1.100",
            user_id="admin",
            resource="login",
            description="用户admin成功登录",
            details={'login_method': 'password'}
        )
        self.auditor.log_security_event(event)
        
        # 模拟认证失败
        for i in range(3):
            event = SecurityEvent(
                event_id="",
                event_type=SecurityEventType.AUTHENTICATION_FAILURE,
                severity=SecuritySeverity.MEDIUM,
                timestamp=datetime.now(),
                source_ip="10.0.0.50",
                user_id="hack_attempt",
                resource="login",
                description=f"认证失败尝试 #{i+1}",
                details={'attempt_number': i+1}
            )
            self.auditor.log_security_event(event)
            self.rule_engine.check_authentication_event("hack_attempt", "10.0.0.50", False)
        
        # 模拟权限提升尝试
        event = SecurityEvent(
            event_id="",
            event_type=SecurityEventType.PRIVILEGE_ESCALATION,
            severity=SecuritySeverity.HIGH,
            timestamp=datetime.now(),
            source_ip="192.168.1.101",
            user_id="normal_user",
            resource="admin_dashboard",
            description="用户尝试访问管理员面板",
            details={'attempted_action': 'access_admin_panel'}
        )
        self.auditor.log_security_event(event)
        
        # 模拟数据访问尝试
        event = SecurityEvent(
            event_id="",
            event_type=SecurityEventType.DATA_BREACH_ATTEMPT,
            severity=SecuritySeverity.HIGH,
            timestamp=datetime.now(),
            source_ip="192.168.1.102",
            user_id="curious_user",
            resource="customer_data",
            description="用户尝试访问客户数据",
            details={'data_type': 'customer_information'}
        )
        self.auditor.log_security_event(event)
    
    def demonstrate_monitoring_workflow(self):
        """演示监控工作流"""
        print("\n🔍 监控工作流演示")
        print("-" * 40)
        
        # 启动监控
        self.monitor.start_monitoring()
        
        # 模拟用户活动
        users = ['user1', 'user2', 'user3']
        actions = ['read', 'write', 'delete', 'configure']
        resources = ['queue1', 'user_data', 'admin_panel', 'customer_info']
        
        print("🔄 模拟用户活动...")
        for i in range(50):
            user = users[i % len(users)]
            action = actions[i % len(actions)]
            resource = resources[i % len(resources)]
            
            self.rule_engine.check_user_activity(user, action, resource)
            time.sleep(0.1)  # 模拟实时活动
        
        # 等待监控检查
        print("⏳ 等待监控检查...")
        time.sleep(35)  # 等待超过检查间隔
        
        # 停止监控
        self.monitor.stop_monitoring()
    
    def demonstrate_audit_reporting(self):
        """演示审计报告"""
        print("\n📊 审计报告演示")
        print("-" * 40)
        
        # 生成24小时摘要
        summary = self.auditor.get_audit_summary(hours=24)
        print("📈 24小时安全事件摘要:")
        print(f"   总事件数: {summary['total_events']}")
        print(f"   未解决事件: {summary['unresolved_events']}")
        print(f"   按类型统计: {summary['events_by_type']}")
        print(f"   按严重级别统计: {summary['events_by_severity']}")
        print(f"   活跃用户Top5: {list(summary['top_users'].keys())[:5]}")
        print(f"   可疑IP Top5: {list(summary['top_source_ips'].keys())[:5]}")
        
        # 导出审计日志
        self.auditor.export_audit_log('security_audit_export.json')
        
        # 获取监控状态
        status = self.monitor.get_monitoring_status()
        print(f"\n🔍 监控状态:")
        print(f"   正在监控: {status['is_monitoring']}")
        print(f"   总事件数: {status['total_events']}")
        print(f"   跟踪失败登录: {status['system_stats']['failed_logins_tracked']}")
        print(f"   跟踪可疑IP: {status['system_stats']['suspicious_ips_tracked']}")
        print(f"   跟踪活跃用户: {status['system_stats']['active_users_tracked']}")
    
    def run_security_monitoring_demo(self):
        """运行安全监控演示"""
        print("🔐 RabbitMQ 安全监控与审计系统演示")
        print("=" * 60)
        
        try:
            # 模拟安全事件
            self.simulate_security_events()
            
            # 演示监控工作流
            self.demonstrate_monitoring_workflow()
            
            # 演示审计报告
            self.demonstrate_audit_reporting()
            
        except KeyboardInterrupt:
            print("\n⏹️ 演示被用户中断")
            if self.monitor.is_monitoring:
                self.monitor.stop_monitoring()
        except Exception as e:
            print(f"❌ 演示运行失败: {e}")
        
        print(f"\n🏁 安全监控与审计演示完成")


if __name__ == "__main__":
    # 运行安全监控演示
    demo = SecurityMonitoringDemo()
    demo.run_security_monitoring_demo()