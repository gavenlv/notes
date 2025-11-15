#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第8章：数据质量最佳实践与案例研究 - 示例代码
"""

import pandas as pd
import numpy as np
import re
import time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Callable
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class DataQualityCulture:
    """数据质量文化建设工具"""
    
    def __init__(self, organization_name: str):
        self.organization_name = organization_name
        self.initiatives = []
        self.metrics = {}
    
    def add_initiative(self, name: str, description: str, responsible_team: str, timeline: str):
        """添加文化建设举措"""
        initiative = {
            'name': name,
            'description': description,
            'responsible_team': responsible_team,
            'timeline': timeline,
            'status': 'planned'
        }
        self.initiatives.append(initiative)
        print(f"已添加文化建设举措: {name}")
    
    def set_metric(self, metric_name: str, target_value: float, current_value: float = 0):
        """设置数据质量指标"""
        self.metrics[metric_name] = {
            'target': target_value,
            'current': current_value
        }
        print(f"已设置指标 {metric_name}: {current_value}/{target_value}")
    
    def update_initiative_status(self, initiative_name: str, status: str):
        """更新举措状态"""
        for initiative in self.initiatives:
            if initiative['name'] == initiative_name:
                initiative['status'] = status
                print(f"已更新举措 {initiative_name} 状态为: {status}")
                break
    
    def generate_culture_report(self) -> str:
        """生成文化建设报告"""
        report = f"""
{self.organization_name} 数据质量文化建设报告
====================================

文化建设举措:
"""
        for initiative in self.initiatives:
            report += f"- {initiative['name']} ({initiative['status']}): {initiative['description']}\n"
        
        report += "\n关键指标进展:\n"
        for metric_name, values in self.metrics.items():
            progress = (values['current'] / values['target']) * 100 if values['target'] > 0 else 0
            report += f"- {metric_name}: {values['current']}/{values['target']} ({progress:.1f}%)\n"
        
        return report


class DataQualityMetrics:
    """数据质量指标体系"""
    
    def __init__(self):
        self.metrics = {}
        self.thresholds = {}
    
    def register_metric(self, name: str, description: str, threshold: float, 
                       calculation_function: Callable):
        """注册监控指标"""
        self.metrics[name] = {
            'description': description,
            'calculation_function': calculation_function
        }
        self.thresholds[name] = threshold
        print(f"已注册指标: {name}")
    
    def calculate_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """计算所有指标"""
        results = {}
        for name, config in self.metrics.items():
            try:
                value = config['calculation_function'](df)
                threshold = self.thresholds.get(name, 0)
                status = 'pass' if value >= threshold else 'fail'
                
                results[name] = {
                    'value': value,
                    'threshold': threshold,
                    'status': status,
                    'description': config['description']
                }
            except Exception as e:
                results[name] = {
                    'value': None,
                    'threshold': threshold,
                    'status': 'error',
                    'description': config['description'],
                    'error': str(e)
                }
        return results
    
    def generate_dashboard_data(self, metrics_results: Dict[str, Any]) -> Dict[str, Any]:
        """生成仪表板数据"""
        dashboard = {
            'timestamp': datetime.now().isoformat(),
            'overall_score': self._calculate_overall_score(metrics_results),
            'metrics': metrics_results
        }
        return dashboard
    
    def _calculate_overall_score(self, metrics_results: Dict[str, Any]) -> float:
        """计算总体质量分数"""
        passed_metrics = sum(1 for result in metrics_results.values() 
                           if result.get('status') == 'pass')
        total_metrics = len([m for m in metrics_results.values() 
                           if m.get('status') in ['pass', 'fail']])
        return round(passed_metrics / total_metrics * 100, 2) if total_metrics > 0 else 0


class MonitoringFrequencyManager:
    """监控频率管理器"""
    
    def __init__(self):
        self.frequencies = {}
    
    def set_frequency(self, table_name: str, frequency: str, priority: str = 'medium'):
        """
        设置监控频率
        
        Args:
            table_name: 表名
            frequency: 监控频率 ('realtime', 'hourly', 'daily', 'weekly')
            priority: 优先级 ('high', 'medium', 'low')
        """
        self.frequencies[table_name] = {
            'frequency': frequency,
            'priority': priority,
            'last_check': None
        }
        print(f"已设置 {table_name} 的监控频率为 {frequency}")
    
    def get_scheduling_plan(self) -> Dict[str, List[Dict]]:
        """获取调度计划"""
        plan = {
            'realtime': [],
            'hourly': [],
            'daily': [],
            'weekly': []
        }
        
        for table_name, config in self.frequencies.items():
            plan[config['frequency']].append({
                'table': table_name,
                'priority': config['priority']
            })
        
        return plan
    
    def should_check(self, table_name: str, current_time: datetime) -> bool:
        """判断是否应该检查"""
        if table_name not in self.frequencies:
            return False
        
        config = self.frequencies[table_name]
        last_check = config['last_check']
        
        if config['frequency'] == 'realtime':
            return True
        elif config['frequency'] == 'hourly':
            if not last_check or (current_time - last_check).seconds >= 3600:
                config['last_check'] = current_time
                return True
        elif config['frequency'] == 'daily':
            if not last_check or (current_time - last_check).days >= 1:
                config['last_check'] = current_time
                return True
        elif config['frequency'] == 'weekly':
            if not last_check or (current_time - last_check).days >= 7:
                config['last_check'] = current_time
                return True
        
        return False


class AlertManager:
    """告警管理器"""
    
    def __init__(self):
        self.alert_rules = []
        self.alert_history = []
    
    def add_alert_rule(self, metric_name: str, threshold: float, severity: str, 
                      notification_channels: List[str]):
        """添加告警规则"""
        rule = {
            'metric_name': metric_name,
            'threshold': threshold,
            'severity': severity,  # 'critical', 'high', 'medium', 'low'
            'channels': notification_channels,  # ['email', 'sms', 'slack']
            'enabled': True
        }
        self.alert_rules.append(rule)
        print(f"已添加告警规则: {metric_name} < {threshold} ({severity})")
    
    def check_and_alert(self, metrics_results: Dict[str, Any]) -> List[Dict]:
        """检查指标并触发告警"""
        alerts = []
        
        for rule in self.alert_rules:
            if not rule['enabled']:
                continue
                
            metric_name = rule['metric_name']
            if metric_name in metrics_results:
                result = metrics_results[metric_name]
                current_value = result.get('value', 0)
                
                if current_value < rule['threshold']:
                    alert = {
                        'timestamp': datetime.now().isoformat(),
                        'metric_name': metric_name,
                        'current_value': current_value,
                        'threshold': rule['threshold'],
                        'severity': rule['severity'],
                        'channels': rule['channels'],
                        'message': f"{metric_name} 指标值 {current_value:.4f} 低于阈值 {rule['threshold']}"
                    }
                    alerts.append(alert)
                    self.alert_history.append(alert)
                    self._send_alert(alert)
        
        return alerts
    
    def _send_alert(self, alert: Dict[str, Any]):
        """发送告警"""
        print(f"[{alert['severity'].upper()}] {alert['message']}")
        print(f"  通知渠道: {', '.join(alert['channels'])}")
    
    def get_alert_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """获取告警统计"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_alerts = [
            alert for alert in self.alert_history
            if datetime.fromisoformat(alert['timestamp']) > cutoff_time
        ]
        
        severity_counts = {}
        for alert in recent_alerts:
            severity = alert['severity']
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            'total_alerts': len(recent_alerts),
            'severity_distribution': severity_counts,
            'most_common_metrics': self._get_most_common_metrics(recent_alerts)
        }
    
    def _get_most_common_metrics(self, alerts: List[Dict]) -> List[tuple]:
        """获取最常见的告警指标"""
        metric_counts = {}
        for alert in alerts:
            metric = alert['metric_name']
            metric_counts[metric] = metric_counts.get(metric, 0) + 1
        
        return sorted(metric_counts.items(), key=lambda x: x[1], reverse=True)[:5]


class BankCustomerDataQualityStandards:
    """银行客户数据质量标准"""
    
    def __init__(self):
        self.standards = {
            'completeness': {
                'customer_name': 0.99,
                'id_number': 0.99,
                'phone': 0.95,
                'address': 0.90
            },
            'accuracy': {
                'phone_format': 0.99,
                'id_number_format': 1.0,
                'email_format': 0.95
            },
            'consistency': {
                'cross_system_consistency': 0.99
            },
            'timeliness': {
                'update_sync_time': 24  # 小时
            }
        }
    
    def validate_customer_data(self, customer_data: pd.DataFrame) -> Dict[str, Any]:
        """验证客户数据质量"""
        validation_results = {}
        
        # 完整性检查
        completeness_results = self._check_completeness(customer_data)
        validation_results['completeness'] = completeness_results
        
        # 准确性检查
        accuracy_results = self._check_accuracy(customer_data)
        validation_results['accuracy'] = accuracy_results
        
        # 一致性检查
        consistency_results = self._check_consistency(customer_data)
        validation_results['consistency'] = consistency_results
        
        # 及时性检查
        timeliness_results = self._check_timeliness(customer_data)
        validation_results['timeliness'] = timeliness_results
        
        return validation_results
    
    def _check_completeness(self, data: pd.DataFrame) -> Dict[str, Any]:
        """检查完整性"""
        results = {}
        total_records = len(data)
        
        for field, threshold in self.standards['completeness'].items():
            if field in data.columns:
                missing_count = data[field].isnull().sum()
                completeness_rate = (total_records - missing_count) / total_records
                results[field] = {
                    'rate': completeness_rate,
                    'threshold': threshold,
                    'status': 'pass' if completeness_rate >= threshold else 'fail'
                }
        
        return results
    
    def _check_accuracy(self, data: pd.DataFrame) -> Dict[str, Any]:
        """检查准确性"""
        results = {}
        
        # 检查身份证号码格式
        if 'id_number' in data.columns:
            id_pattern = re.compile(r'^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$')
            valid_format = data['id_number'].astype(str).apply(lambda x: bool(id_pattern.match(x)))
            accuracy_rate = valid_format.sum() / len(data)
            threshold = self.standards['accuracy']['id_number_format']
            results['id_number_format'] = {
                'rate': accuracy_rate,
                'threshold': threshold,
                'status': 'pass' if accuracy_rate >= threshold else 'fail'
            }
        
        # 检查手机号码格式
        if 'phone' in data.columns:
            phone_pattern = re.compile(r'^1[3-9]\d{9}$')
            valid_format = data['phone'].astype(str).apply(lambda x: bool(phone_pattern.match(x)))
            accuracy_rate = valid_format.sum() / len(data)
            threshold = self.standards['accuracy']['phone_format']
            results['phone_format'] = {
                'rate': accuracy_rate,
                'threshold': threshold,
                'status': 'pass' if accuracy_rate >= threshold else 'fail'
            }
        
        return results
    
    def _check_consistency(self, data: pd.DataFrame) -> Dict[str, Any]:
        """检查一致性"""
        # 简化实现，实际应用中需要跨系统比较
        return {'cross_system_consistency': {'rate': 0.95, 'threshold': 0.99, 'status': 'fail'}}
    
    def _check_timeliness(self, data: pd.DataFrame) -> Dict[str, Any]:
        """检查及时性"""
        # 简化实现，实际应用中需要检查数据更新时间
        return {'update_sync_time': {'hours': 12, 'threshold': 24, 'status': 'pass'}}


class BankDataQualityDashboard:
    """银行数据质量监控仪表板"""
    
    def __init__(self):
        self.metrics_history = []
        self.alerts = []
    
    def update_metrics(self, metrics_data: Dict[str, Any]):
        """更新指标数据"""
        timestamp = datetime.now()
        metrics_data['timestamp'] = timestamp
        self.metrics_history.append(metrics_data)
        print(f"已更新指标数据: {timestamp}")
    
    def check_thresholds_and_alert(self, current_metrics: Dict[str, float], 
                                  thresholds: Dict[str, float]):
        """检查阈值并告警"""
        for metric_name, current_value in current_metrics.items():
            if metric_name in thresholds:
                threshold = thresholds[metric_name]
                if current_value < threshold:
                    alert = {
                        'timestamp': datetime.now(),
                        'metric': metric_name,
                        'current_value': current_value,
                        'threshold': threshold,
                        'severity': self._determine_severity(metric_name),
                        'message': f'{metric_name} 指标 {current_value:.2%} 低于阈值 {threshold:.2%}'
                    }
                    self.alerts.append(alert)
                    self._send_alert(alert)
    
    def _determine_severity(self, metric_name: str) -> str:
        """确定告警严重程度"""
        critical_metrics = ['id_number_format', 'customer_name_completeness']
        high_metrics = ['phone_format', 'phone_completeness']
        
        if metric_name in critical_metrics:
            return 'critical'
        elif metric_name in high_metrics:
            return 'high'
        else:
            return 'medium'
    
    def _send_alert(self, alert: Dict[str, Any]):
        """发送告警"""
        severity_colors = {'critical': '🔴', 'high': '🟠', 'medium': '🟡'}
        color = severity_colors.get(alert['severity'], '⚪')
        print(f"{color} [{alert['severity'].upper()}] {alert['message']}")
    
    def generate_report(self, hours: int = 24) -> str:
        """生成监控报告"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [
            metric for metric in self.metrics_history
            if metric['timestamp'] > cutoff_time
        ]
        
        recent_alerts = [
            alert for alert in self.alerts
            if alert['timestamp'] > cutoff_time
        ]
        
        report = f"""
银行数据质量监控报告 ({hours}小时)
================================

数据质量指标趋势:
"""
        if recent_metrics:
            latest_metrics = recent_metrics[-1]
            for key, value in latest_metrics.items():
                if key != 'timestamp':
                    report += f"- {key}: {value:.2%}\n"
        
        report += f"\n告警统计:\n"
        report += f"- 总告警数: {len(recent_alerts)}\n"
        
        severity_counts = {}
        for alert in recent_alerts:
            severity = alert['severity']
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        for severity, count in severity_counts.items():
            report += f"- {severity}: {count}\n"
        
        return report


class OrderDataQualityRuleEngine:
    """订单数据质量规则引擎"""
    
    def __init__(self):
        self.rules = []
        self.rule_results = []
    
    def add_rule(self, name: str, description: str, condition_function: Callable, 
                action_function: Callable = None):
        """添加规则"""
        rule = {
            'name': name,
            'description': description,
            'condition': condition_function,
            'action': action_function or self._default_action,
            'enabled': True,
            'created_at': datetime.now()
        }
        self.rules.append(rule)
        print(f"已添加规则: {name}")
    
    def validate_order(self, order_data: Dict[str, Any]) -> List[Dict]:
        """验证订单数据"""
        violations = []
        
        for rule in self.rules:
            if not rule['enabled']:
                continue
            
            try:
                if rule['condition'](order_data):
                    violation = {
                        'rule_name': rule['name'],
                        'description': rule['description'],
                        'order_id': order_data.get('order_id'),
                        'timestamp': datetime.now(),
                        'status': 'violation'
                    }
                    violations.append(violation)
                    
                    # 执行处理动作
                    rule['action'](order_data, violation)
                    
            except Exception as e:
                print(f"规则 {rule['name']} 执行出错: {str(e)}")
        
        self.rule_results.extend(violations)
        return violations
    
    def _default_action(self, order_data: Dict[str, Any], violation: Dict[str, Any]):
        """默认处理动作"""
        print(f"订单 {order_data.get('order_id')} 违反规则: {violation['rule_name']}")
    
    def get_violation_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """获取违规统计"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_violations = [
            v for v in self.rule_results
            if v['timestamp'] > cutoff_time
        ]
        
        rule_counts = {}
        for violation in recent_violations:
            rule_name = violation['rule_name']
            rule_counts[rule_name] = rule_counts.get(rule_name, 0) + 1
        
        return {
            'total_violations': len(recent_violations),
            'rule_distribution': rule_counts,
            'top_violations': sorted(rule_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        }


class RealTimeOrderQualityMonitor:
    """实时订单数据质量监控器"""
    
    def __init__(self, rule_engine: OrderDataQualityRuleEngine):
        self.rule_engine = rule_engine
        self.processed_orders = 0
        self.violation_count = 0
        self.performance_metrics = []
    
    def process_order_stream(self, order_stream: List[Dict], batch_size: int = 100):
        """处理订单流数据"""
        batch = []
        start_time = time.time()
        
        for order in order_stream:
            batch.append(order)
            
            # 批量处理以提高性能
            if len(batch) >= batch_size:
                self._process_batch(batch)
                batch = []
                
                # 记录性能指标
                batch_time = time.time() - start_time
                self.performance_metrics.append({
                    'timestamp': datetime.now(),
                    'batch_size': batch_size,
                    'processing_time': batch_time,
                    'throughput': batch_size / batch_time if batch_time > 0 else 0
                })
                
                start_time = time.time()
        
        # 处理剩余的订单
        if batch:
            self._process_batch(batch)
    
    def _process_batch(self, batch: List[Dict]):
        """处理订单批次"""
        for order in batch:
            self.processed_orders += 1
            violations = self.rule_engine.validate_order(order)
            if violations:
                self.violation_count += len(violations)
    
    def get_monitoring_report(self) -> str:
        """获取监控报告"""
        if not self.performance_metrics:
            return "暂无监控数据"
        
        avg_throughput = sum(m['throughput'] for m in self.performance_metrics) / len(self.performance_metrics)
        latest_metrics = self.performance_metrics[-1]
        
        report = f"""
实时订单数据质量监控报告
========================

处理统计:
- 已处理订单数: {self.processed_orders:,}
- 发现违规数: {self.violation_count:,}
- 违规率: {self.violation_count/self.processed_orders:.2%} (如果已处理订单>0)

性能指标:
- 平均吞吐量: {avg_throughput:.2f} 订单/秒
- 最新批次处理时间: {latest_metrics['processing_time']:.3f} 秒
- 最新批次吞吐量: {latest_metrics['throughput']:.2f} 订单/秒
        """
        
        return report
    
    def get_top_violations(self, top_n: int = 10) -> List[tuple]:
        """获取最常见的违规类型"""
        stats = self.rule_engine.get_violation_statistics()
        return stats.get('top_violations', [])[:top_n]


class DataQualityMaturityAssessment:
    """数据质量管理成熟度评估"""
    
    def __init__(self):
        self.dimensions = {
            'strategy_and_governance': {
                'name': '战略与治理',
                'levels': {
                    1: '无明确的数据质量管理策略和治理机制',
                    2: '有初步的数据质量管理意识，但缺乏系统性',
                    3: '建立了基本的数据质量管理策略和治理框架',
                    4: '有完善的数据质量管理策略和治理机制',
                    5: '数据质量管理成为组织核心竞争力，持续优化'
                },
                'indicators': [
                    '是否有明确的数据质量管理策略',
                    '是否建立了数据治理组织',
                    '是否有数据质量管理相关的政策和标准',
                    '数据质量管理是否纳入绩效考核'
                ]
            },
            'process_and_methodology': {
                'name': '流程与方法',
                'levels': {
                    1: '数据质量管理流程缺失或不规范',
                    2: '有零散的数据质量管理活动',
                    3: '建立了基本的数据质量管理流程',
                    4: '有标准化的数据质量管理流程和方法',
                    5: '流程持续优化，方法不断创新'
                },
                'indicators': [
                    '是否有标准化的数据质量检查流程',
                    '是否使用系统化的方法进行数据质量评估',
                    '是否有数据质量问题的处理流程',
                    '是否定期进行数据质量改进'
                ]
            },
            'technology_and_tools': {
                'name': '技术与工具',
                'levels': {
                    1: '缺乏专门的数据质量管理工具',
                    2: '使用简单的工具进行数据质量检查',
                    3: '配备了基本的数据质量管理工具',
                    4: '有集成化的数据质量管理平台',
                    5: '使用先进的技术和工具，支持智能化管理'
                },
                'indicators': [
                    '是否使用专门的数据质量管理工具',
                    '是否有自动化的数据质量监控',
                    '是否支持实时数据质量检查',
                    '是否具备预测性数据质量管理能力'
                ]
            },
            'organization_and_people': {
                'name': '组织与人员',
                'levels': {
                    1: '无专门的数据质量管理团队',
                    2: '有兼职人员负责数据质量管理',
                    3: '建立了专门的数据质量管理团队',
                    4: '团队具备专业的数据质量管理能力',
                    5: '团队持续学习，引领行业发展'
                },
                'indicators': [
                    '是否有专门的数据质量管理团队',
                    '团队成员是否具备专业技能',
                    '是否有定期的培训和能力提升',
                    '是否建立了知识管理体系'
                ]
            },
            'data_quality_outcomes': {
                'name': '质量成果',
                'levels': {
                    1: '数据质量问题频发，严重影响业务',
                    2: '数据质量问题较多，对业务有一定影响',
                    3: '数据质量基本满足业务需求',
                    4: '数据质量良好，支撑业务发展',
                    5: '数据质量成为业务竞争优势'
                },
                'indicators': [
                    '数据质量问题发生频率',
                    '数据质量对业务的影响程度',
                    '数据质量改进的效果',
                    '数据质量带来的业务价值'
                ]
            }
        }
    
    def assess_dimension(self, dimension_name: str, scores: List[float]) -> Dict[str, Any]:
        """评估单个维度的成熟度"""
        if dimension_name not in self.dimensions:
            raise ValueError(f"未知的维度: {dimension_name}")
        
        # 计算平均分并确定成熟度等级
        avg_score = sum(scores) / len(scores) if scores else 0
        level = min(5, max(1, round(avg_score)))
        
        return {
            'dimension': dimension_name,
            'dimension_name': self.dimensions[dimension_name]['name'],
            'average_score': round(avg_score, 2),
            'maturity_level': level,
            'level_description': self.dimensions[dimension_name]['levels'][level]
        }
    
    def assess_overall_maturity(self, dimension_assessments: List[Dict]) -> Dict[str, Any]:
        """评估整体成熟度"""
        total_score = sum(assess['average_score'] for assess in dimension_assessments)
        avg_score = total_score / len(dimension_assessments)
        overall_level = min(5, max(1, round(avg_score)))
        
        return {
            'overall_score': round(avg_score, 2),
            'overall_level': overall_level,
            'level_description': self._get_overall_level_description(overall_level),
            'dimension_details': dimension_assessments
        }
    
    def _get_overall_level_description(self, level: int) -> str:
        """获取整体等级描述"""
        descriptions = {
            1: '初始级：数据质量管理处于起步阶段，缺乏系统性',
            2: '管理级：开始重视数据质量管理，但还不够成熟',
            3: '定义级：建立了基本的数据质量管理体系',
            4: '量化管理级：数据质量管理达到较高水平',
            5: '优化级：数据质量管理成为组织核心竞争力'
        }
        return descriptions.get(level, '未知等级')
    
    def generate_assessment_report(self, overall_assessment: Dict[str, Any]) -> str:
        """生成评估报告"""
        report = f"""
数据质量管理成熟度评估报告
========================

整体评估结果:
- 成熟度等级: {overall_assessment['overall_level']} 级
- 综合得分: {overall_assessment['overall_score']}/5.0
- 等级描述: {overall_assessment['level_description']}

各维度评估详情:
"""
        
        for assess in overall_assessment['dimension_details']:
            report += f"\n{assess['dimension_name']}:\n"
            report += f"  - 等级: {assess['maturity_level']} 级\n"
            report += f"  - 得分: {assess['average_score']}/5.0\n"
            report += f"  - 描述: {assess['level_description']}\n"
        
        report += "\n改进建议:\n"
        report += self._generate_improvement_recommendations(overall_assessment)
        
        return report
    
    def _generate_improvement_recommendations(self, overall_assessment: Dict[str, Any]) -> str:
        """生成改进建议"""
        recommendations = []
        overall_level = overall_assessment['overall_level']
        
        if overall_level < 3:
            recommendations.append("1. 建立完善的数据质量管理体系和治理机制")
            recommendations.append("2. 组建专业的数据质量管理团队")
            recommendations.append("3. 引入合适的数据质量管理工具")
        
        if overall_level < 4:
            recommendations.append("4. 建立标准化的数据质量管理流程")
            recommendations.append("5. 加强团队培训和能力建设")
            recommendations.append("6. 实施持续的数据质量监控和改进")
        
        if overall_level < 5:
            recommendations.append("7. 推进数据质量管理的智能化和自动化")
            recommendations.append("8. 建立数据质量价值评估体系")
            recommendations.append("9. 持续优化和创新数据管理方法")
        
        if not recommendations:
            recommendations.append("继续保持并引领行业发展")
        
        return "\n".join(recommendations)


# 辅助函数定义
def calculate_completeness_rate(df: pd.DataFrame) -> float:
    """计算完整性率"""
    if df.empty:
        return 0.0
    total_cells = df.size
    null_cells = df.isnull().sum().sum()
    return (total_cells - null_cells) / total_cells

def calculate_uniqueness_rate(df: pd.DataFrame) -> float:
    """计算唯一性率"""
    if df.empty:
        return 0.0
    total_rows = len(df)
    duplicate_rows = df.duplicated().sum()
    return (total_rows - duplicate_rows) / total_rows

def calculate_timeliness_score(df: pd.DataFrame) -> float:
    """计算及时性分数"""
    # 简化实现，实际应用中需要根据具体业务逻辑计算
    return 0.95

def amount_anomaly_condition(order: Dict[str, Any]) -> bool:
    """金额异常检测条件"""
    amount = order.get('amount', 0)
    return amount > 100000 or amount < 0

def invalid_sku_condition(order: Dict[str, Any]) -> bool:
    """无效SKU检测条件"""
    sku = order.get('sku', '')
    return not sku or len(sku) < 3

def address_incomplete_condition(order: Dict[str, Any]) -> bool:
    """地址不完整检测条件"""
    address = order.get('shipping_address', '')
    return not address or len(address.strip()) < 10

def email_format_condition(order: Dict[str, Any]) -> bool:
    """邮箱格式检测条件"""
    email = order.get('customer_email', '')
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return email and not re.match(pattern, email)

def flag_suspicious_order(order: Dict[str, Any], violation: Dict[str, Any]):
    """标记可疑订单"""
    order['status'] = 'suspicious'
    order['suspicious_reason'] = violation['rule_name']
    print(f"标记订单 {order['order_id']} 为可疑: {violation['rule_name']}")

def notify_finance_team(order: Dict[str, Any], violation: Dict[str, Any]):
    """通知财务团队"""
    print(f"通知财务团队: 订单 {order['order_id']} 金额异常 ({order.get('amount', 0)})")

def generate_sample_customer_data(size: int = 1000) -> pd.DataFrame:
    """生成示例客户数据"""
    return pd.DataFrame({
        'customer_id': range(1, size + 1),
        'customer_name': ['Customer_' + str(i) for i in range(1, size + 1)],
        'id_number': ['11010119900101' + str(i).zfill(4) + ('0' if i % 2 == 0 else 'X') for i in range(1, size + 1)],
        'phone': ['138' + str(i).zfill(8) for i in range(1, size - 50)] + [None] * 50,  # 50个缺失电话
        'address': ['Address_' + str(i) for i in range(1, size - 100)] + [None] * 100,  # 100个缺失地址
        'created_at': pd.date_range('2024-01-01', periods=size, freq='1H')
    })

def generate_order_stream(count: int = 1000) -> List[Dict]:
    """生成模拟订单流"""
    orders = []
    for i in range(count):
        # 大部分订单是正常的，少部分有质量问题
        is_anomaly = np.random.random() < 0.1  # 10%的概率有质量问题
        
        order = {
            'order_id': f'ORD{i:06d}',
            'amount': np.random.normal(300, 100) if not is_anomaly else np.random.normal(300, 5000),
            'sku': f'SKU{np.random.randint(1000, 9999)}' if not is_anomaly or np.random.random() < 0.8 else '',
            'shipping_address': '北京市朝阳区xxx街道xxx号' if not is_anomaly or np.random.random() < 0.8 else '北京',
            'customer_email': f'customer{i}@example.com' if not is_anomaly or np.random.random() < 0.8 else 'invalid-email'
        }
        orders.append(order)
    return orders


def main():
    """主函数 - 演示所有功能"""
    print("=" * 60)
    print("第8章：数据质量最佳实践与案例研究 - 示例代码演示")
    print("=" * 60)
    
    # 1. 数据质量文化建设演示
    print("\n1. 数据质量文化建设演示")
    print("-" * 30)
    culture = DataQualityCulture("电商平台公司")
    culture.add_initiative(
        "数据质量意识培训",
        "为全体员工提供数据质量基础知识培训",
        "人力资源部",
        "2024年Q1-Q2"
    )
    culture.add_initiative(
        "数据质量奖惩机制",
        "建立数据质量相关的奖励和惩罚机制",
        "质量管理部门",
        "2024年Q2"
    )
    culture.set_metric("员工数据质量知识测试通过率", 95, 75)
    culture.set_metric("数据质量问题报告数量", 50, 30)
    culture.update_initiative_status("数据质量意识培训", "进行中")
    print(culture.generate_culture_report())
    
    # 2. 数据质量指标体系演示
    print("\n2. 数据质量指标体系演示")
    print("-" * 30)
    dq_metrics = DataQualityMetrics()
    dq_metrics.register_metric(
        'completeness_rate',
        '数据完整性率',
        0.95,
        calculate_completeness_rate
    )
    dq_metrics.register_metric(
        'uniqueness_rate',
        '数据唯一性率',
        0.99,
        calculate_uniqueness_rate
    )
    dq_metrics.register_metric(
        'timeliness_score',
        '数据及时性分数',
        0.90,
        calculate_timeliness_score
    )
    
    sample_data = pd.DataFrame({
        'id': range(1, 1001),
        'name': ['User_' + str(i) for i in range(1, 1001)],
        'email': ['user' + str(i) + '@example.com' for i in range(1, 951)] + [np.nan] * 50
    })
    
    metrics_results = dq_metrics.calculate_metrics(sample_data)
    dashboard_data = dq_metrics.generate_dashboard_data(metrics_results)
    print(f"总体数据质量分数: {dashboard_data['overall_score']}")
    for metric_name, result in metrics_results.items():
        print(f"  {metric_name}: {result['value']:.4f} ({result['status']})")
    
    # 3. 银行客户数据质量标准演示
    print("\n3. 银行客户数据质量标准演示")
    print("-" * 30)
    bank_standards = BankCustomerDataQualityStandards()
    customer_data = generate_sample_customer_data(1000)
    validation_results = bank_standards.validate_customer_data(customer_data)
    
    print("银行客户数据质量验证结果:")
    for category, results in validation_results.items():
        print(f"\n{category.upper()} 检查:")
        for field, result in results.items():
            status_icon = "✓" if result['status'] == 'pass' else "✗"
            print(f"  {status_icon} {field}: {result['rate']:.2%} (阈值: {result['threshold']})")
    
    # 4. 银行数据质量监控仪表板演示
    print("\n4. 银行数据质量监控仪表板演示")
    print("-" * 30)
    dashboard = BankDataQualityDashboard()
    sample_metrics = {
        'customer_name_completeness': 0.995,
        'id_number_completeness': 0.992,
        'phone_completeness': 0.945,  # 低于阈值
        'id_number_format_accuracy': 0.998,
        'phone_format_accuracy': 0.92  # 低于阈值
    }
    
    thresholds = {
        'customer_name_completeness': 0.99,
        'id_number_completeness': 0.99,
        'phone_completeness': 0.95,
        'id_number_format_accuracy': 0.99,
        'phone_format_accuracy': 0.95
    }
    
    dashboard.update_metrics(sample_metrics)
    dashboard.check_thresholds_and_alert(sample_metrics, thresholds)
    report = dashboard.generate_report()
    print(report)
    
    # 5. 电商订单数据质量规则引擎演示
    print("\n5. 电商订单数据质量规则引擎演示")
    print("-" * 30)
    rule_engine = OrderDataQualityRuleEngine()
    rule_engine.add_rule(
        'amount_anomaly',
        '订单金额异常检测',
        amount_anomaly_condition,
        notify_finance_team
    )
    rule_engine.add_rule(
        'invalid_sku',
        '无效SKU检测',
        invalid_sku_condition,
        flag_suspicious_order
    )
    rule_engine.add_rule(
        'address_incomplete',
        '地址不完整检测',
        address_incomplete_condition,
        flag_suspicious_order
    )
    rule_engine.add_rule(
        'email_format',
        '邮箱格式检测',
        email_format_condition,
        flag_suspicious_order
    )
    
    test_orders = [
        {
            'order_id': 'ORD001',
            'amount': 150000,  # 金额异常
            'sku': 'ABC123',
            'shipping_address': '北京市朝阳区xxx街道',
            'customer_email': 'customer@example.com'
        },
        {
            'order_id': 'ORD002',
            'amount': 299.99,
            'sku': '',  # 无效SKU
            'shipping_address': '上海市浦东新区xxx路',
            'customer_email': 'customer@example.com'
        },
        {
            'order_id': 'ORD003',
            'amount': 199.99,
            'sku': 'XYZ789',
            'shipping_address': '广州',  # 地址不完整
            'customer_email': 'invalid-email'  # 邮箱格式错误
        }
    ]
    
    for order in test_orders:
        violations = rule_engine.validate_order(order)
        if violations:
            print(f"订单 {order['order_id']} 发现 {len(violations)} 个违规")
    
    stats = rule_engine.get_violation_statistics()
    print(f"\n违规统计: {stats}")
    
    # 6. 实时订单数据质量监控演示
    print("\n6. 实时订单数据质量监控演示")
    print("-" * 30)
    monitor = RealTimeOrderQualityMonitor(rule_engine)
    order_stream = generate_order_stream(500)
    monitor.process_order_stream(order_stream, batch_size=50)
    report = monitor.get_monitoring_report()
    print(report)
    
    top_violations = monitor.get_top_violations()
    print("\n最常见的违规类型:")
    for rule_name, count in top_violations:
        print(f"- {rule_name}: {count} 次")
    
    # 7. 数据质量管理成熟度评估演示
    print("\n7. 数据质量管理成熟度评估演示")
    print("-" * 30)
    assessment = DataQualityMaturityAssessment()
    dimension_scores = {
        'strategy_and_governance': [2, 3, 2, 3],  # 各项指标得分
        'process_and_methodology': [3, 3, 4, 3],
        'technology_and_tools': [2, 2, 3, 3],
        'organization_and_people': [2, 3, 2, 3],
        'data_quality_outcomes': [3, 3, 3, 4]
    }
    
    dimension_assessments = []
    for dimension, scores in dimension_scores.items():
        assess = assessment.assess_dimension(dimension, scores)
        dimension_assessments.append(assess)
    
    overall_assessment = assessment.assess_overall_maturity(dimension_assessments)
    report = assessment.generate_assessment_report(overall_assessment)
    print(report)
    
    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()