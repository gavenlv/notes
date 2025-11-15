#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第8章：数据质量最佳实践与案例研究 - 简化版示例代码
（去除了matplotlib等图形依赖库）
"""

import pandas as pd
import numpy as np
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Callable
import warnings
warnings.filterwarnings('ignore')


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


def main():
    """主函数 - 演示数据质量最佳实践代码示例"""
    print("=== 第8章：数据质量最佳实践与案例研究 代码示例 ===\n")
    
    # 1. 数据质量文化建设示例
    print("1. 数据质量文化建设示例")
    print("-" * 40)
    
    culture_builder = DataQualityCulture("华泰科技有限公司")
    
    # 添加文化建设举措
    culture_builder.add_initiative(
        "数据质量月活动",
        "每年举办数据质量主题活动，提高全员数据质量意识",
        "数据治理委员会",
        "2024年Q2"
    )
    
    culture_builder.add_initiative(
        "数据质量培训计划",
        "为不同岗位提供定制化的数据质量培训课程",
        "人力资源部",
        "2024年全年"
    )
    
    culture_builder.add_initiative(
        "数据质量激励机制",
        "建立数据质量贡献奖励制度，鼓励员工参与数据治理",
        "数据治理委员会",
        "2024年Q3"
    )
    
    # 设置关键指标
    culture_builder.set_metric("员工数据质量意识测评平均分", 4.5, 3.2)
    culture_builder.set_metric("数据质量问题主动上报数量", 100, 65)
    culture_builder.set_metric("数据质量改进建议采纳率", 0.8, 0.65)
    
    # 更新举措状态
    culture_builder.update_initiative_status("数据质量月活动", "进行中")
    
    # 生成文化建设报告
    culture_report = culture_builder.generate_culture_report()
    print(culture_report)
    
    print("\n" + "="*60 + "\n")
    
    # 2. 数据质量指标体系示例
    print("2. 数据质量指标体系示例")
    print("-" * 40)
    
    # 创建示例数据
    np.random.seed(42)
    sample_data = pd.DataFrame({
        'id': range(1, 1001),
        'name': [f'User_{i}' for i in range(1, 1001)],
        'email': [f'user{i}@example.com' for i in range(1, 1001)],
        'age': np.random.randint(18, 80, 1000),
        'salary': np.random.normal(50000, 15000, 1000),
        'department': np.random.choice(['IT', 'HR', 'Finance', 'Marketing'], 1000),
        'join_date': pd.date_range('2020-01-01', periods=1000, freq='D')
    })
    
    # 添加一些数据质量问题
    # 添加缺失值
    sample_data.loc[np.random.choice(sample_data.index, 50, replace=False), 'age'] = np.nan
    sample_data.loc[np.random.choice(sample_data.index, 30, replace=False), 'salary'] = np.nan
    
    # 添加重复记录
    duplicate_rows = sample_data.sample(20)
    sample_data = pd.concat([sample_data, duplicate_rows], ignore_index=True)
    
    # 定义指标计算函数
    def completeness_check(df):
        """完整性检查"""
        total_cells = df.size
        missing_cells = df.isnull().sum().sum()
        return (total_cells - missing_cells) / total_cells
    
    def uniqueness_check(df):
        """唯一性检查"""
        total_rows = len(df)
        unique_rows = len(df.drop_duplicates())
        return unique_rows / total_rows
    
    def timeliness_check(df, date_column='join_date'):
        """及时性检查"""
        if date_column in df.columns:
            latest_date = df[date_column].max()
            current_date = datetime.now()
            days_diff = (current_date - latest_date).days
            # 假设7天内为及时
            return 1.0 if days_diff <= 7 else 0.0
        return 0.5
    
    # 初始化指标体系
    dq_metrics = DataQualityMetrics()
    
    # 注册指标
    dq_metrics.register_metric(
        "completeness_rate",
        "数据完整性比率",
        0.95,  # 阈值95%
        completeness_check
    )
    
    dq_metrics.register_metric(
        "uniqueness_rate",
        "数据唯一性比率",
        0.98,  # 阈值98%
        uniqueness_check
    )
    
    dq_metrics.register_metric(
        "timeliness_rate",
        "数据及时性比率",
        0.90,  # 阈值90%
        lambda df: timeliness_check(df)
    )
    
    # 计算指标
    metrics_results = dq_metrics.calculate_metrics(sample_data)
    
    # 生成仪表板数据
    dashboard_data = dq_metrics.generate_dashboard_data(metrics_results)
    
    print(f"数据质量仪表板 - 生成时间: {dashboard_data['timestamp']}")
    print(f"总体质量分数: {dashboard_data['overall_score']}%")
    print("\n各项指标详情:")
    for metric_name, result in dashboard_data['metrics'].items():
        status_icon = "✓" if result['status'] == 'pass' else "✗"
        print(f"  {status_icon} {metric_name}: {result['value']:.4f} "
              f"(阈值: {result['threshold']}) - {result['description']}")
    
    print("\n" + "="*60 + "\n")
    
    # 3. 监控频率管理示例
    print("3. 监控频率管理示例")
    print("-" * 40)
    
    frequency_manager = MonitoringFrequencyManager()
    
    # 设置不同表的监控频率
    frequency_manager.set_frequency("user_profiles", "realtime", "high")
    frequency_manager.set_frequency("transaction_records", "hourly", "high")
    frequency_manager.set_frequency("product_catalog", "daily", "medium")
    frequency_manager.set_frequency("audit_logs", "weekly", "low")
    
    # 获取调度计划
    scheduling_plan = frequency_manager.get_scheduling_plan()
    
    print("监控调度计划:")
    for frequency, tables in scheduling_plan.items():
        if tables:  # 只显示有表的频率类别
            print(f"  {frequency.capitalize()} 监控:")
            for table_info in tables:
                print(f"    - {table_info['table']} (优先级: {table_info['priority']})")
    
    # 检查是否应该执行监控
    current_time = datetime.now()
    should_check_user = frequency_manager.should_check("user_profiles", current_time)
    should_check_product = frequency_manager.should_check("product_catalog", current_time)
    
    print(f"\n监控检查结果:")
    print(f"  用户资料表是否应检查: {should_check_user}")
    print(f"  商品目录表是否应检查: {should_check_product}")

    print("\n" + "="*60)
    print("数据质量最佳实践演示完成!")


if __name__ == "__main__":
    main()