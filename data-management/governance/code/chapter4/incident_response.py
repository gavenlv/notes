#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据安全事件响应系统
实现完整的安全事件管理流程，包括事件创建、分类、响应计划生成和报告
"""

import json
import hashlib
import random
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

class IncidentSeverity(Enum):
    """事件严重性"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class IncidentStatus(Enum):
    """事件状态"""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class IncidentType(Enum):
    """事件类型"""
    DATA_BREACH = "data_breach"
    DATA_TAMPERING = "data_tampering"
    RANSOMWARE = "ransomware"
    SYSTEM_COMPROMISE = "system_compromise"
    MALWARE = "malware"
    ACCESS_ANOMALY = "access_anomaly"
    MISCONFIGURATION = "misconfiguration"

class DataSecurityIncident:
    """数据安全事件"""
    
    def __init__(self, incident_id: str, title: str):
        self.incident_id = incident_id
        self.title = title
        self.description = ""
        self.incident_type: Optional[IncidentType] = None
        self.severity: Optional[IncidentSeverity] = None
        self.status = IncidentStatus.NEW
        self.detected_at = datetime.now()
        self.affected_assets: List[str] = []
        self.data_categories: List[str] = []
        self.affected_records_count = 0
        self.root_cause = ""
        self.containment_actions: List[str] = []
        self.eradication_actions: List[str] = []
        self.recovery_actions: List[str] = []
        self.reported_to_authorities = False
        self.reported_to_individuals = False
        self.resolution_time = None
        self.assigned_to = ""
        self.timeline: List[Dict] = []
        
        # 记录初始状态
        self.add_timeline_entry("事件创建", "事件被创建和记录")
    
    def add_timeline_entry(self, action: str, description: str, actor: str = "系统"):
        """添加时间线条目"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "description": description,
            "actor": actor
        }
        self.timeline.append(entry)
    
    def update_status(self, status: IncidentStatus, actor: str = "系统"):
        """更新事件状态"""
        old_status = self.status.value
        self.status = status
        self.add_timeline_entry("状态更新", f"状态从 {old_status} 更新为 {status.value}", actor)
        
        if status == IncidentStatus.RESOLVED:
            self.resolution_time = datetime.now()
    
    def assign_to(self, assignee: str):
        """分配事件给处理人员"""
        self.assigned_to = assignee
        self.add_timeline_entry("分配处理", f"事件分配给 {assignee}", "系统")
    
    def calculate_severity(self, data_sensitivity: List[str], affected_users: int, business_impact: str):
        """计算事件严重性"""
        # 数据敏感性评分
        sensitivity_score = 0
        if "highly_sensitive" in data_sensitivity:
            sensitivity_score = 3
        elif "sensitive" in data_sensitivity:
            sensitivity_score = 2
        elif "internal" in data_sensitivity:
            sensitivity_score = 1
        
        # 影响用户数评分
        impact_score = 0
        if affected_users > 10000:
            impact_score = 3
        elif affected_users > 1000:
            impact_score = 2
        elif affected_users > 100:
            impact_score = 1
        
        # 业务影响评分
        business_score = 0
        if business_impact == "critical":
            business_score = 3
        elif business_impact == "high":
            business_score = 2
        elif business_impact == "medium":
            business_score = 1
        
        # 计算总体严重性
        total_score = sensitivity_score + impact_score + business_score
        
        if total_score >= 7:
            self.severity = IncidentSeverity.CRITICAL
        elif total_score >= 5:
            self.severity = IncidentSeverity.HIGH
        elif total_score >= 3:
            self.severity = IncidentSeverity.MEDIUM
        else:
            self.severity = IncidentSeverity.LOW
        
        self.add_timeline_entry(
            "严重性评估", 
            f"事件严重性评估为 {self.severity.value} (评分: {total_score})"
        )
    
    def check_notification_requirements(self):
        """检查通知要求"""
        requirements = {
            "notify_management": False,
            "notify_authorities": False,
            "notify_individuals": False,
            "notify_time_limit": None
        }
        
        # GDPR和其他法规要求的时间限制
        if self.incident_type == IncidentType.DATA_BREACH:
            if self.severity in [IncidentSeverity.CRITICAL, IncidentSeverity.HIGH]:
                requirements["notify_management"] = True
                requirements["notify_authorities"] = True
                requirements["notify_individuals"] = True
                requirements["notify_time_limit"] = 72  # 72小时内
            
            elif self.severity == IncidentSeverity.MEDIUM:
                requirements["notify_management"] = True
                requirements["notify_authorities"] = True
                requirements["notify_time_limit"] = 72
        
        return requirements
    
    def get_duration_hours(self):
        """获取事件持续时间（小时）"""
        end_time = self.resolution_time if self.resolution_time else datetime.now()
        duration = end_time - self.detected_at
        return duration.total_seconds() / 3600
    
    def to_dict(self):
        """转换为字典"""
        return {
            "incident_id": self.incident_id,
            "title": self.title,
            "description": self.description,
            "incident_type": self.incident_type.value if self.incident_type else None,
            "severity": self.severity.value if self.severity else None,
            "status": self.status.value,
            "detected_at": self.detected_at.isoformat(),
            "affected_assets": self.affected_assets,
            "data_categories": self.data_categories,
            "affected_records_count": self.affected_records_count,
            "root_cause": self.root_cause,
            "assigned_to": self.assigned_to,
            "duration_hours": self.get_duration_hours(),
            "resolution_time": self.resolution_time.isoformat() if self.resolution_time else None,
            "timeline": self.timeline
        }

class IncidentResponseSystem:
    """事件响应系统"""
    
    def __init__(self):
        self.incidents: Dict[str, DataSecurityIncident] = {}
        self.templates: Dict[str, Dict] = self._load_response_templates()
        self.notification_channels = []
        self.response_team: Dict[str, Dict] = {}
        self.audit_log: List[Dict] = []
        
        # 生成事件ID计数器
        self.incident_counter = 1000
    
    def _load_response_templates(self):
        """加载响应模板"""
        return {
            IncidentType.DATA_BREACH.value: {
                "containment": [
                    "隔离受影响的系统",
                    "重置所有相关账户密码",
                    "阻止受攻击的IP地址"
                ],
                "eradication": [
                    "识别并修复漏洞",
                    "清除恶意软件",
                    "加强访问控制"
                ],
                "recovery": [
                    "从备份恢复系统",
                    "验证数据完整性",
                    "监控系统异常活动"
                ]
            },
            IncidentType.RANSOMWARE.value: {
                "containment": [
                    "隔离受感染系统",
                    "断开网络连接",
                    "保存内存镜像"
                ],
                "eradication": [
                    "分析勒索软件变种",
                    "寻找解密工具",
                    "清除恶意软件"
                ],
                "recovery": [
                    "从干净备份恢复",
                    "重建系统",
                    "加强安全防护"
                ]
            },
            IncidentType.SYSTEM_COMPROMISE.value: {
                "containment": [
                    "隔离受入侵系统",
                    "更改所有管理员凭证",
                    "限制横向移动"
                ],
                "eradication": [
                    "识别攻击入口点",
                    "清除攻击工具",
                    "修复安全漏洞"
                ],
                "recovery": [
                    "系统安全加固",
                    "部署入侵检测系统",
                    "加强监控"
                ]
            }
        }
    
    def create_incident(self, title: str, description: str = "") -> DataSecurityIncident:
        """创建新事件"""
        incident_id = f"INC-{self.incident_counter}"
        self.incident_counter += 1
        
        incident = DataSecurityIncident(incident_id, title)
        incident.description = description
        
        self.incidents[incident_id] = incident
        
        self._log_action("create_incident", {
            "incident_id": incident_id,
            "title": title
        })
        
        return incident
    
    def update_incident(self, incident_id: str, update_data: Dict):
        """更新事件信息"""
        if incident_id not in self.incidents:
            raise ValueError(f"事件ID {incident_id} 不存在")
        
        incident = self.incidents[incident_id]
        
        for key, value in update_data.items():
            if hasattr(incident, key):
                setattr(incident, key, value)
        
        self._log_action("update_incident", {
            "incident_id": incident_id,
            "update_fields": list(update_data.keys())
        })
    
    def assign_incident(self, incident_id: str, assignee: str):
        """分配事件"""
        if incident_id not in self.incidents:
            raise ValueError(f"事件ID {incident_id} 不存在")
        
        incident = self.incidents[incident_id]
        incident.assign_to(assignee)
        
        self._log_action("assign_incident", {
            "incident_id": incident_id,
            "assignee": assignee
        })
    
    def generate_response_plan(self, incident_id: str) -> Dict:
        """生成响应计划"""
        if incident_id not in self.incidents:
            raise ValueError(f"事件ID {incident_id} 不存在")
        
        incident = self.incidents[incident_id]
        
        # 获取模板
        template = self.templates.get(
            incident.incident_type.value, 
            {
                "containment": ["分析事件范围", "限制进一步损害"],
                "eradication": ["识别根本原因", "消除威胁"],
                "recovery": ["恢复系统", "验证功能"]
            }
        )
        
        # 根据严重性调整响应计划
        if incident.severity == IncidentSeverity.CRITICAL:
            # 关键事件需要额外措施
            template["containment"].insert(0, "立即通知管理层")
            template["containment"].insert(1, "激活应急响应团队")
            template["eradication"].append("联系外部安全专家")
            template["recovery"].append("实施额外监控")
        
        response_plan = {
            "incident_id": incident_id,
            "severity": incident.severity.value if incident.severity else "unknown",
            "incident_type": incident.incident_type.value if incident.incident_type else "unknown",
            "containment_actions": template["containment"],
            "eradication_actions": template["eradication"],
            "recovery_actions": template["recovery"],
            "created_at": datetime.now().isoformat()
        }
        
        # 更新事件
        incident.containment_actions = response_plan["containment_actions"]
        incident.eradication_actions = response_plan["eradication_actions"]
        incident.recovery_actions = response_plan["recovery_actions"]
        
        incident.add_timeline_entry("生成响应计划", f"为事件生成了响应计划")
        
        return response_plan
    
    def assess_notification_requirements(self, incident_id: str) -> Dict:
        """评估通知要求"""
        if incident_id not in self.incidents:
            raise ValueError(f"事件ID {incident_id} 不存在")
        
        incident = self.incidents[incident_id]
        requirements = incident.check_notification_requirements()
        
        # 计算通知截止时间
        if requirements["notify_time_limit"]:
            detected_at = incident.detected_at
            notification_deadline = detected_at + timedelta(hours=requirements["notify_time_limit"])
            requirements["notification_deadline"] = notification_deadline.isoformat()
            
            # 检查是否已超过期限
            now = datetime.now()
            if now > notification_deadline:
                requirements["deadline_exceeded"] = True
            else:
                time_remaining = notification_deadline - now
                requirements["time_remaining"] = str(time_remaining)
                requirements["deadline_exceeded"] = False
        
        return requirements
    
    def resolve_incident(self, incident_id: str, root_cause: str, resolution_summary: str):
        """解决事件"""
        if incident_id not in self.incidents:
            raise ValueError(f"事件ID {incident_id} 不存在")
        
        incident = self.incidents[incident_id]
        
        incident.root_cause = root_cause
        incident.update_status(IncidentStatus.RESOLVED)
        
        incident.add_timeline_entry("事件解决", f"事件已解决，原因: {root_cause}，摘要: {resolution_summary}")
        
        self._log_action("resolve_incident", {
            "incident_id": incident_id,
            "root_cause": root_cause,
            "duration_hours": incident.get_duration_hours()
        })
    
    def close_incident(self, incident_id: str, lessons_learned: str):
        """关闭事件"""
        if incident_id not in self.incidents:
            raise ValueError(f"事件ID {incident_id} 不存在")
        
        incident = self.incidents[incident_id]
        
        incident.update_status(IncidentStatus.CLOSED)
        
        incident.add_timeline_entry("事件关闭", f"事件已关闭，经验教训: {lessons_learned}")
        
        self._log_action("close_incident", {
            "incident_id": incident_id,
            "lessons_learned": lessons_learned
        })
    
    def generate_incident_report(self, incident_id: str) -> Dict:
        """生成事件报告"""
        if incident_id not in self.incidents:
            raise ValueError(f"事件ID {incident_id} 不存在")
        
        incident = self.incidents[incident_id]
        
        # 计算持续时间
        duration_hours = incident.get_duration_hours()
        
        # 获取通知要求
        notification_requirements = self.assess_notification_requirements(incident_id)
        
        report = {
            "incident_id": incident.incident_id,
            "title": incident.title,
            "description": incident.description,
            "incident_type": incident.incident_type.value if incident.incident_type else "unknown",
            "severity": incident.severity.value if incident.severity else "unknown",
            "status": incident.status.value,
            "detected_at": incident.detected_at.isoformat(),
            "resolution_time": incident.resolution_time.isoformat() if incident.resolution_time else None,
            "duration_hours": round(duration_hours, 2),
            "affected_assets": incident.affected_assets,
            "data_categories": incident.data_categories,
            "affected_records_count": incident.affected_records_count,
            "root_cause": incident.root_cause,
            "assigned_to": incident.assigned_to,
            "timeline": incident.timeline,
            "notification_requirements": notification_requirements,
            "response_plan": {
                "containment": incident.containment_actions,
                "eradication": incident.eradication_actions,
                "recovery": incident.recovery_actions
            },
            "generated_at": datetime.now().isoformat()
        }
        
        return report
    
    def get_incident_metrics(self) -> Dict:
        """获取事件指标"""
        if not self.incidents:
            return {
                "total_incidents": 0,
                "resolved_incidents": 0,
                "open_incidents": 0,
                "severity_distribution": {},
                "type_distribution": {},
                "average_resolution_time": 0,
                "mttr": 0  # 平均解决时间（仅计已解决事件）
            }
        
        total_incidents = len(self.incidents)
        resolved_incidents = len([
            inc for inc in self.incidents.values() 
            if inc.status in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]
        ])
        
        open_incidents = total_incidents - resolved_incidents
        
        # 严重性分布
        severity_counts = {}
        for incident in self.incidents.values():
            if incident.severity:
                severity = incident.severity.value
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # 事件类型分布
        type_counts = {}
        for incident in self.incidents.values():
            if incident.incident_type:
                inc_type = incident.incident_type.value
                type_counts[inc_type] = type_counts.get(inc_type, 0) + 1
        
        # 平均解决时间和平均修复时间（MTTR）
        resolved_incident_list = [
            inc for inc in self.incidents.values() 
            if inc.status in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED] and inc.resolution_time
        ]
        
        average_resolution_time = 0
        mttr = 0
        
        if resolved_incident_list:
            total_resolution_time = sum([
                inc.get_duration_hours()
                for inc in resolved_incident_list
            ])
            
            average_resolution_time = total_resolution_time / len(resolved_incident_list)
            mttr = average_resolution_time  # 在此简化中，两者相同
        
        return {
            "total_incidents": total_incidents,
            "resolved_incidents": resolved_incidents,
            "open_incidents": open_incidents,
            "severity_distribution": severity_counts,
            "type_distribution": type_counts,
            "average_resolution_time": round(average_resolution_time, 2),
            "mttr": round(mttr, 2)
        }
    
    def visualize_incident_metrics(self, save_path: str = None):
        """可视化事件指标"""
        metrics = self.get_incident_metrics()
        
        if metrics["total_incidents"] == 0:
            print("无事件数据可视化")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('数据安全事件指标分析', fontsize=16)
        
        # 严重性分布饼图
        ax1 = axes[0, 0]
        if metrics["severity_distribution"]:
            severity_labels = list(metrics["severity_distribution"].keys())
            severity_values = list(metrics["severity_distribution"].values())
            
            # 设置颜色
            colors = {
                'critical': 'red',
                'high': 'orange',
                'medium': 'yellow',
                'low': 'green'
            }
            pie_colors = [colors.get(label, 'blue') for label in severity_labels]
            
            ax1.pie(severity_values, labels=severity_labels, colors=pie_colors, autopct='%1.1f%%')
            ax1.set_title('事件严重性分布')
        else:
            ax1.text(0.5, 0.5, '无严重性数据', horizontalalignment='center', verticalalignment='center')
            ax1.set_title('事件严重性分布')
        
        # 事件类型分布柱状图
        ax2 = axes[0, 1]
        if metrics["type_distribution"]:
            type_labels = list(metrics["type_distribution"].keys())
            type_values = list(metrics["type_distribution"].values())
            
            # 转换类型名为更友好的显示名称
            display_names = {
                'data_breach': '数据泄露',
                'data_tampering': '数据篡改',
                'ransomware': '勒索软件',
                'system_compromise': '系统入侵',
                'malware': '恶意软件',
                'access_anomaly': '访问异常',
                'misconfiguration': '配置错误'
            }
            
            display_labels = [display_names.get(label, label) for label in type_labels]
            
            ax2.bar(display_labels, type_values)
            ax2.set_title('事件类型分布')
            ax2.set_ylabel('事件数量')
            ax2.tick_params(axis='x', rotation=45)
        else:
            ax2.text(0.5, 0.5, '无类型数据', horizontalalignment='center', verticalalignment='center')
            ax2.set_title('事件类型分布')
        
        # 事件状态饼图
        ax3 = axes[1, 0]
        status_labels = ['已解决', '未解决']
        status_values = [metrics["resolved_incidents"], metrics["open_incidents"]]
        
        ax3.pie(status_values, labels=status_labels, colors=['green', 'red'], autopct='%1.1f%%')
        ax3.set_title('事件状态分布')
        
        # 解决时间指标
        ax4 = axes[1, 1]
        metrics_data = ['平均解决时间', 'MTTR']
        metrics_values = [metrics["average_resolution_time"], metrics["mttr"]]
        
        ax4.bar(metrics_data, metrics_values, color=['blue', 'purple'])
        ax4.set_title('解决时间指标')
        ax4.set_ylabel('时间（小时）')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def export_incidents_to_csv(self, file_path: str):
        """导出事件数据到CSV"""
        if not self.incidents:
            print("无事件数据可导出")
            return
        
        incidents_data = []
        
        for incident in self.incidents.values():
            incidents_data.append({
                "事件ID": incident.incident_id,
                "标题": incident.title,
                "类型": incident.incident_type.value if incident.incident_type else "",
                "严重性": incident.severity.value if incident.severity else "",
                "状态": incident.status.value,
                "检测时间": incident.detected_at.isoformat(),
                "解决时间": incident.resolution_time.isoformat() if incident.resolution_time else "",
                "持续时间(小时)": incident.get_duration_hours(),
                "受影响资产": ",".join(incident.affected_assets),
                "受影响记录数": incident.affected_records_count,
                "处理人员": incident.assigned_to
            })
        
        df = pd.DataFrame(incidents_data)
        df.to_csv(file_path, index=False, encoding='utf-8')
        print(f"事件数据已导出到: {file_path}")
    
    def _log_action(self, action: str, details: Dict):
        """记录审计日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details
        }
        
        self.audit_log.append(log_entry)

# 演示系统使用
def demo_incident_response():
    """演示事件响应系统"""
    print("数据安全事件响应系统演示")
    print("=" * 50)
    
    # 创建事件响应系统
    irs = IncidentResponseSystem()
    
    # 1. 创建数据泄露事件
    print("\n1. 创建数据泄露事件:")
    data_breach_incident = irs.create_incident(
        "客户数据泄露",
        "检测到客户数据库未经授权访问，可能涉及个人身份信息泄露"
    )
    
    # 更新事件详情
    irs.update_incident(data_breach_incident.incident_id, {
        "incident_type": IncidentType.DATA_BREACH,
        "affected_assets": ["customer_database", "web_server"],
        "data_categories": ["personal_identifiable", "financial"],
        "affected_records_count": 15000
    })
    
    print(f"  事件ID: {data_breach_incident.incident_id}")
    print(f"  标题: {data_breach_incident.title}")
    print(f"  类型: {data_breach_incident.incident_type.value if data_breach_incident.incident_type else '未设置'}")
    
    # 2. 计算严重性
    print("\n2. 计算事件严重性:")
    irs.update_incident(data_breach_incident.incident_id, {
        "data_categories": ["sensitive", "financial"],
        "affected_records_count": 15000
    })
    
    # 重新获取事件并计算严重性
    incident = irs.incidents[data_breach_incident.incident_id]
    incident.calculate_severity(
        data_categories=incident.data_categories,
        affected_users=incident.affected_records_count,
        business_impact="high"
    )
    
    print(f"  严重性: {incident.severity.value if incident.severity else '未评估'}")
    
    # 3. 分配事件
    print("\n3. 分派事件:")
    irs.assign_incident(data_breach_incident.incident_id, "安全响应团队")
    print(f"  事件分配给: {incident.assigned_to}")
    
    # 4. 生成响应计划
    print("\n4. 生成响应计划:")
    response_plan = irs.generate_response_plan(data_breach_incident.incident_id)
    
    print("  遏制措施:")
    for action in response_plan["containment_actions"]:
        print(f"    - {action}")
    
    print("  根除措施:")
    for action in response_plan["eradication_actions"]:
        print(f"    - {action}")
    
    print("  恢复措施:")
    for action in response_plan["recovery_actions"]:
        print(f"    - {action}")
    
    # 5. 评估通知要求
    print("\n5. 评估通知要求:")
    notification_requirements = irs.assess_notification_requirements(data_breach_incident.incident_id)
    
    print(f"  需要通知管理层: {'是' if notification_requirements['notify_management'] else '否'}")
    print(f"  需要通知监管机构: {'是' if notification_requirements['notify_authorities'] else '否'}")
    print(f"  需要通知个人: {'是' if notification_requirements['notify_individuals'] else '否'}")
    
    if 'notification_deadline' in notification_requirements:
        print(f"  通知截止时间: {notification_requirements['notification_deadline']}")
        
        if notification_requirements.get("deadline_exceeded"):
            print("  ⚠️ 已超过通知截止时间!")
        else:
            print(f"  剩余时间: {notification_requirements.get('time_remaining', '未知')}")
    
    # 6. 更新事件状态并解决
    print("\n6. 解决事件:")
    irs.update_incident(data_breach_incident.incident_id, {
        "status": IncidentStatus.IN_PROGRESS
    })
    
    # 模拟一些时间后解决事件
    irs.resolve_incident(
        data_breach_incident.incident_id,
        "Web应用SQL注入漏洞",
        "修复了漏洞，重置了所有受影响账户密码，并加强了输入验证"
    )
    
    print(f"  事件已解决，持续时间为: {incident.get_duration_hours():.2f} 小时")
    
    # 7. 关闭事件
    print("\n7. 关闭事件:")
    irs.close_incident(
        data_breach_incident.incident_id,
        "需要加强输入验证，定期进行安全测试，并建立更好的监控机制"
    )
    
    # 8. 生成事件报告
    print("\n8. 生成事件报告:")
    incident_report = irs.generate_incident_report(data_breach_incident.incident_id)
    
    print(f"  事件ID: {incident_report['incident_id']}")
    print(f"  标题: {incident_report['title']}")
    print(f"  类型: {incident_report['incident_type']}")
    print(f"  严重性: {incident_report['severity']}")
    print(f"  状态: {incident_report['status']}")
    print(f"  受影响记录数: {incident_report['affected_records_count']:,}")
    print(f"  持续时间: {incident_report['duration_hours']} 小时")
    
    # 创建第二个事件以演示指标
    print("\n9. 创建第二个事件以演示指标:")
    ransomware_incident = irs.create_incident(
        "勒索软件攻击",
        "检测到勒索软件感染，文件被加密"
    )
    
    irs.update_incident(ransomware_incident.incident_id, {
        "incident_type": IncidentType.RANSOMWARE,
        "severity": IncidentSeverity.CRITICAL,
        "affected_assets": ["file_server", "database_server"],
        "affected_records_count": 25000
    })
    
    irs.assign_incident(ransomware_incident.incident_id, "安全响应团队")
    
    # 10. 获取事件指标
    print("\n10. 事件指标:")
    metrics = irs.get_incident_metrics()
    
    print(f"  总事件数: {metrics['total_incidents']}")
    print(f"  已解决事件: {metrics['resolved_incidents']}")
    print(f"  未解决事件: {metrics['open_incidents']}")
    print(f"  平均解决时间: {metrics['average_resolution_time']} 小时")
    print(f"  MTTR: {metrics['mttr']} 小时")
    
    print("\n  严重性分布:")
    for severity, count in metrics['severity_distribution'].items():
        print(f"    {severity}: {count}")
    
    print("\n  事件类型分布:")
    for inc_type, count in metrics['type_distribution'].items():
        print(f"    {inc_type}: {count}")
    
    # 11. 可视化事件指标
    print("\n11. 可视化事件指标:")
    irs.visualize_incident_metrics(save_path="incident_metrics.png")
    
    # 12. 导出事件数据
    print("\n12. 导出事件数据:")
    irs.export_incidents_to_csv("incidents_export.csv")
    
    return irs

# 运行演示
if __name__ == "__main__":
    irs_system = demo_incident_response()
    print("\n事件响应系统演示完成！")