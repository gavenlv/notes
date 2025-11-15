#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据质量监控与告警机制示例代码

本模块展示了如何构建一个完整的数据质量监控系统，包括：
1. 数据采集层
2. 指标计算层
3. 异常检测层
4. 告警通知层
5. 监控流程编排
"""

import pandas as pd
import numpy as np
import sqlite3
import json
import smtplib
import requests
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# ================================
# 1. 数据采集层
# ================================

class DataCollector:
    """数据采集器"""
    
    def __init__(self):
        self.collectors = {}
    
    def register_collector(self, source_type, collector_func):
        """注册数据采集器"""
        self.collectors[source_type] = collector_func
    
    def collect_data(self, source_config):
        """采集数据"""
        source_type = source_config['type']
        if source_type in self.collectors:
            return self.collectors[source_type](source_config)
        else:
            raise ValueError(f"不支持的数据源类型: {source_type}")

def collect_database_metrics(config):
    """数据库指标采集"""
    try:
        # 连接数据库并执行查询
        connection_string = config['connection_string']
        query = config['query']
        
        # 示例：使用pandas读取数据库
        df = pd.read_sql(query, connection_string)
        return df
    except Exception as e:
        print(f"数据库采集失败: {e}")
        return pd.DataFrame()

def collect_api_metrics(config):
    """API接口指标采集"""
    try:
        url = config['url']
        headers = config.get('headers', {})
        params = config.get('params', {})
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # 转换为DataFrame
            if isinstance(data, list):
                return pd.DataFrame(data)
            elif isinstance(data, dict):
                return pd.DataFrame([data])
            else:
                return pd.DataFrame()
        else:
            raise Exception(f"API调用失败: {response.status_code}")
    except Exception as e:
        print(f"API采集失败: {e}")
        return pd.DataFrame()

# ================================
# 2. 指标计算层
# ================================

class MetricsCalculator:
    """指标计算器"""
    
    def __init__(self):
        self.calculators = {}
    
    def register_calculator(self, metric_type, calculator_func):
        """注册指标计算器"""
        self.calculators[metric_type] = calculator_func
    
    def calculate_metrics(self, data, metric_configs):
        """计算指标"""
        results = {}
        for config in metric_configs:
            metric_type = config['type']
            metric_name = config['name']
            
            if metric_type in self.calculators:
                try:
                    result = self.calculators[metric_type](data, config)
                    results[metric_name] = result
                except Exception as e:
                    print(f"计算指标 {metric_name} 时出错: {e}")
                    results[metric_name] = None
            else:
                raise ValueError(f"不支持的指标类型: {metric_type}")
        
        return results

# 基础指标计算函数
def calculate_completeness(df, config):
    """计算完整性指标"""
    columns = config.get('columns', df.columns.tolist())
    total_records = len(df)
    
    if total_records == 0:
        return 0.0
    
    completeness_scores = {}
    for column in columns:
        if column in df.columns:
            non_null_records = df[column].count()
            completeness_scores[column] = non_null_records / total_records
        else:
            completeness_scores[column] = 0.0
    
    # 计算平均完整性
    avg_completeness = sum(completeness_scores.values()) / len(completeness_scores)
    return avg_completeness

def calculate_volume_metric(data, config):
    """计算数据量指标"""
    return len(data)

def calculate_distribution_metric(data, config):
    """计算数据分布指标"""
    column = config['column']
    if column in data.columns:
        return data[column].value_counts().to_dict()
    else:
        return {}

def calculate_accuracy_metric(data, config):
    """计算准确性指标（示例：数值范围检查）"""
    column = config['column']
    min_val = config.get('min_value', None)
    max_val = config.get('max_value', None)
    
    if column not in data.columns:
        return 0.0
    
    total_records = len(data)
    if total_records == 0:
        return 0.0
    
    valid_records = data[column]
    if min_val is not None:
        valid_records = valid_records[valid_records >= min_val]
    if max_val is not None:
        valid_records = valid_records[valid_records <= max_val]
    
    accuracy = len(valid_records) / total_records
    return accuracy

def calculate_timeliness_metric(data, config):
    """计算及时性指标"""
    timestamp_column = config['timestamp_column']
    expected_frequency_hours = config.get('expected_frequency_hours', 24)
    
    if timestamp_column not in data.columns:
        return 0.0
    
    # 确保时间列是datetime类型
    data[timestamp_column] = pd.to_datetime(data[timestamp_column])
    data_sorted = data.sort_values(timestamp_column)
    
    if len(data_sorted) < 2:
        return 1.0  # 只有一条记录时认为是及时的
    
    # 计算相邻记录的时间差
    data_sorted['time_diff'] = data_sorted[timestamp_column].diff()
    data_sorted['time_diff_hours'] = data_sorted['time_diff'].dt.total_seconds() / 3600
    
    # 计算及时更新的比例
    timely_updates = (data_sorted['time_diff_hours'] <= expected_frequency_hours).sum()
    total_updates = len(data_sorted) - 1  # 减去第一个NaN值
    
    timeliness = timely_updates / total_updates if total_updates > 0 else 0.0
    return timeliness

# ================================
# 3. 异常检测层
# ================================

class AnomalyDetector:
    """异常检测器"""
    
    def __init__(self):
        self.detectors = {}
    
    def register_detector(self, detector_type, detector_func):
        """注册异常检测器"""
        self.detectors[detector_type] = detector_func
    
    def detect_anomalies(self, metrics, detection_configs):
        """检测异常"""
        anomalies = []
        for config in detection_configs:
            detector_type = config['type']
            metric_name = config['metric']
            threshold = config['threshold']
            
            if detector_type in self.detectors:
                if metric_name in metrics and metrics[metric_name] is not None:
                    try:
                        is_anomaly, details = self.detectors[detector_type](
                            metrics[metric_name], threshold, config
                        )
                        if is_anomaly:
                            anomalies.append({
                                'metric': metric_name,
                                'value': metrics[metric_name],
                                'threshold': threshold,
                                'details': details
                            })
                    except Exception as e:
                        print(f"检测异常 {metric_name} 时出错: {e}")
            else:
                raise ValueError(f"不支持的检测器类型: {detector_type}")
        
        return anomalies

# 异常检测函数
def threshold_detector(value, threshold, config):
    """阈值检测器"""
    operator = config.get('operator', 'lt')  # lt: less than, gt: greater than
    
    if operator == 'lt':
        is_anomaly = value < threshold
    elif operator == 'gt':
        is_anomaly = value > threshold
    elif operator == 'eq':
        is_anomaly = value == threshold
    else:
        raise ValueError(f"不支持的操作符: {operator}")
    
    details = f"值 {value} {'小于' if operator == 'lt' else '大于' if operator == 'gt' else '等于'} 阈值 {threshold}"
    return is_anomaly, details

def trend_detector(value, threshold, config):
    """趋势检测器"""
    historical_values = config.get('historical_values', [])
    window_size = config.get('window_size', 5)
    
    if len(historical_values) < window_size:
        return False, "历史数据不足"
    
    # 计算移动平均
    moving_avg = sum(historical_values[-window_size:]) / window_size
    
    # 检查是否偏离趋势
    if moving_avg != 0:
        deviation = abs(value - moving_avg) / moving_avg
    else:
        deviation = 0 if value == 0 else float('inf')
    
    is_anomaly = deviation > threshold
    
    details = f"当前值 {value}, 移动平均 {moving_avg:.2f}, 偏离度 {deviation:.2%}"
    return is_anomaly, details

# ================================
# 4. 告警通知层
# ================================

class AlertNotifier:
    """告警通知器"""
    
    def __init__(self):
        self.notifiers = {}
    
    def register_notifier(self, channel_type, notifier_func):
        """注册通知器"""
        self.notifiers[channel_type] = notifier_func
    
    def send_alert(self, alert_info, notification_configs):
        """发送告警"""
        for config in notification_configs:
            channel_type = config['type']
            recipients = config['recipients']
            
            if channel_type in self.notifiers:
                try:
                    self.notifiers[channel_type](alert_info, recipients, config)
                except Exception as e:
                    print(f"发送告警到 {channel_type} 时出错: {e}")
            else:
                raise ValueError(f"不支持的通知渠道: {channel_type}")

# 通知函数
def email_notifier(alert_info, recipients, config):
    """邮件通知"""
    try:
        # 构造邮件内容
        msg = MIMEMultipart()
        msg['From'] = config.get('sender', 'dq-monitor@example.com')
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = f"[数据质量告警] {alert_info['metric']}"
        
        body = f"""
数据质量异常告警

指标名称: {alert_info['metric']}
当前值: {alert_info['value']}
阈值: {alert_info['threshold']}
详细信息: {alert_info['details']}
发生时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # 注意：在生产环境中需要配置真实的SMTP服务器
        print(f"模拟发送邮件告警给: {recipients}")
        print(f"主题: {msg['Subject']}")
        print(f"内容: {body}")
        
    except Exception as e:
        print(f"邮件通知失败: {e}")

def webhook_notifier(alert_info, recipients, config):
    """Webhook通知"""
    webhook_url = config.get('webhook_url')
    if not webhook_url:
        raise ValueError("Webhook URL未配置")
    
    payload = {
        'alert': alert_info,
        'timestamp': datetime.now().isoformat(),
        'recipients': recipients
    }
    
    try:
        # 注意：在生产环境中取消注释下面的代码
        # response = requests.post(webhook_url, json=payload, timeout=10)
        # if response.status_code != 200:
        #     print(f"Webhook调用失败: {response.status_code}")
        print(f"模拟发送Webhook告警到: {webhook_url}")
        print(f"载荷: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
    except Exception as e:
        print(f"Webhook调用异常: {e}")

def console_notifier(alert_info, recipients, config):
    """控制台通知（用于演示）"""
    print("=" * 50)
    print("【数据质量告警】")
    print(f"指标: {alert_info['metric']}")
    print(f"当前值: {alert_info['value']}")
    print(f"阈值: {alert_info['threshold']}")
    print(f"详情: {alert_info['details']}")
    print(f"接收人: {', '.join(recipients)}")
    print("=" * 50)

# ================================
# 5. 监控流程编排
# ================================

class DataQualityMonitor:
    """数据质量监控器"""
    
    def __init__(self):
        self.collector = DataCollector()
        self.calculator = MetricsCalculator()
        self.detector = AnomalyDetector()
        self.notifier = AlertNotifier()
        self.history = []
        self.configure_components()
    
    def configure_components(self):
        """配置各组件"""
        # 注册数据采集器
        self.collector.register_collector('database', collect_database_metrics)
        self.collector.register_collector('api', collect_api_metrics)
        
        # 注册指标计算器
        self.calculator.register_calculator('completeness', calculate_completeness)
        self.calculator.register_calculator('volume', calculate_volume_metric)
        self.calculator.register_calculator('distribution', calculate_distribution_metric)
        self.calculator.register_calculator('accuracy', calculate_accuracy_metric)
        self.calculator.register_calculator('timeliness', calculate_timeliness_metric)
        
        # 注册异常检测器
        self.detector.register_detector('threshold', threshold_detector)
        self.detector.register_detector('trend', trend_detector)
        
        # 注册通知器
        self.notifier.register_notifier('email', email_notifier)
        self.notifier.register_notifier('webhook', webhook_notifier)
        self.notifier.register_notifier('console', console_notifier)
    
    def run_monitoring_cycle(self, source_configs, metric_configs, detection_configs, notification_configs):
        """执行一次监控周期"""
        print("开始执行数据质量监控周期...")
        
        all_anomalies = []
        
        # 遍历所有数据源
        for source_config in source_configs:
            try:
                print(f"\n--- 处理数据源: {source_config['name']} ---")
                
                # 1. 采集数据
                print(f"采集数据...")
                data = self.collector.collect_data(source_config)
                print(f"采集到 {len(data)} 条记录")
                
                if len(data) == 0:
                    print("警告: 未采集到数据")
                    continue
                
                # 2. 计算指标
                print(f"计算指标...")
                metrics = self.calculator.calculate_metrics(data, metric_configs)
                print(f"计算完成，共 {len([m for m in metrics.values() if m is not None])} 个有效指标")
                
                # 3. 检测异常
                print(f"检测异常...")
                anomalies = self.detector.detect_anomalies(metrics, detection_configs)
                print(f"检测完成，发现 {len(anomalies)} 个异常")
                
                # 4. 记录历史
                cycle_result = {
                    'source': source_config['name'],
                    'timestamp': datetime.now(),
                    'metrics': metrics,
                    'anomalies': anomalies,
                    'record_count': len(data)
                }
                self.history.append(cycle_result)
                
                # 5. 收集所有异常
                for anomaly in anomalies:
                    anomaly_with_source = {
                        'source': source_config['name'],
                        **anomaly
                    }
                    all_anomalies.append(anomaly_with_source)
                    
            except Exception as e:
                print(f"处理数据源 {source_config['name']} 时发生错误: {e}")
        
        # 6. 发送告警
        if all_anomalies:
            print(f"\n发现 {len(all_anomalies)} 个异常，发送告警...")
            for anomaly in all_anomalies:
                self.notifier.send_alert(anomaly, notification_configs)
        else:
            print("\n本次监控周期未发现异常")
        
        print("\n数据质量监控周期执行完成")
        return all_anomalies
    
    def get_monitoring_history(self, hours=24):
        """获取监控历史"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_history = [
            record for record in self.history
            if record['timestamp'] > cutoff_time
        ]
        return recent_history

# ================================
# 6. 监控仪表板
# ================================

def create_monitoring_dashboard(monitor):
    """创建监控仪表板"""
    # 获取最近的监控历史
    history = monitor.get_monitoring_history(hours=24)
    
    if not history:
        print("没有监控历史数据")
        return
    
    # 准备数据
    timestamps = [record['timestamp'] for record in history]
    record_counts = [record['record_count'] for record in history]
    
    # 提取指标数据
    completeness_values = []
    volume_values = []
    
    for record in history:
        completeness = record['metrics'].get('order_completeness', 0)
        volume = record['metrics'].get('order_volume', 0)
        completeness_values.append(completeness if completeness is not None else 0)
        volume_values.append(volume if volume is not None else 0)
    
    # 创建图表
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('数据质量监控仪表板', fontsize=16)
    
    # 1. 完整性趋势图
    axes[0, 0].plot(timestamps, completeness_values, marker='o', linewidth=2, markersize=6)
    axes[0, 0].set_title('数据完整性趋势')
    axes[0, 0].set_ylabel('完整性比例')
    axes[0, 0].set_ylim(0, 1)
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # 2. 数据量趋势图
    axes[0, 1].plot(timestamps, volume_values, marker='s', color='orange', linewidth=2, markersize=6)
    axes[0, 1].set_title('数据量趋势')
    axes[0, 1].set_ylabel('记录数量')
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # 3. 异常统计
    anomaly_counts = {}
    for record in history:
        source = record['source']
        anomaly_count = len(record['anomalies'])
        if source not in anomaly_counts:
            anomaly_counts[source] = 0
        anomaly_counts[source] += anomaly_count
    
    sources = list(anomaly_counts.keys())
    counts = list(anomaly_counts.values())
    
    bars = axes[1, 0].bar(sources, counts, color='red', alpha=0.7)
    axes[1, 0].set_title('各数据源异常统计')
    axes[1, 0].set_ylabel('异常数量')
    axes[1, 0].grid(True, alpha=0.3)
    
    # 在柱状图上添加数值标签
    for bar, count in zip(bars, counts):
        axes[1, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                       str(count), ha='center', va='bottom')
    
    # 4. 综合质量评分
    quality_scores = []
    for record in history:
        metrics = record['metrics']
        # 简单的综合评分计算（排除None值）
        valid_metrics = [v for v in metrics.values() if v is not None]
        score = sum(valid_metrics) / len(valid_metrics) if valid_metrics else 0
        quality_scores.append(score)
    
    axes[1, 1].plot(timestamps, quality_scores, marker='^', color='green', linewidth=2, markersize=6)
    axes[1, 1].set_title('数据质量综合评分趋势')
    axes[1, 1].set_ylabel('质量评分')
    axes[1, 1].set_ylim(0, 1)
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    dashboard_file = 'data_quality_dashboard.png'
    plt.savefig(dashboard_file, dpi=300, bbox_inches='tight')
    print(f"监控仪表板已保存为: {dashboard_file}")
    plt.show()

# ================================
# 7. 智能告警管理
# ================================

class SmartAlertManager:
    """智能告警管理器"""
    
    def __init__(self):
        self.alert_history = {}
        self.suppression_window = 3600  # 1小时内的重复告警将被抑制
    
    def should_suppress_alert(self, alert_key, timestamp):
        """判断是否应该抑制告警"""
        if alert_key not in self.alert_history:
            return False
        
        last_alert_time = self.alert_history[alert_key]
        time_diff = (timestamp - last_alert_time).total_seconds()
        
        # 如果距离上次告警不到抑制窗口时间，则抑制
        if time_diff < self.suppression_window:
            return True
        
        return False
    
    def process_alert(self, alert_info, notifier, notification_configs):
        """处理告警"""
        alert_key = f"{alert_info['source']}_{alert_info['metric']}"
        timestamp = datetime.now()
        
        # 检查是否应该抑制告警
        if self.should_suppress_alert(alert_key, timestamp):
            print(f"抑制重复告警: {alert_key}")
            return False
        
        # 记录告警时间
        self.alert_history[alert_key] = timestamp
        
        # 发送告警
        notifier.send_alert(alert_info, notification_configs)
        return True

# ================================
# 8. 示例数据生成
# ================================

def create_sample_database():
    """创建示例数据库和数据"""
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    
    # 创建订单表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        amount REAL,
        status TEXT,
        created_at TIMESTAMP
    )
    ''')
    
    # 插入示例数据（包含一些质量问题）
    sample_orders = [
        (1001, 101, 299.99, 'completed', datetime.now() - timedelta(hours=2)),
        (1002, 102, 149.50, 'completed', datetime.now() - timedelta(hours=1)),
        (1003, None, 89.99, 'pending', datetime.now() - timedelta(minutes=45)),  # 缺少customer_id
        (1004, 104, None, 'completed', datetime.now() - timedelta(minutes=30)),   # 缺少amount
        (1005, 105, -50.00, 'completed', datetime.now() - timedelta(minutes=15)), # 负金额
    ]
    
    cursor.executemany('INSERT OR REPLACE INTO orders VALUES (?, ?, ?, ?, ?)', sample_orders)
    conn.commit()
    conn.close()
    print("示例数据库创建完成")

def create_sample_api_data():
    """创建示例API数据文件"""
    sample_data = [
        {"product_id": 1, "name": "商品A", "price": 99.99, "stock": 100},
        {"product_id": 2, "name": "商品B", "price": 149.99, "stock": 50},
        {"product_id": 3, "name": "商品C", "price": 0, "stock": 200},  # 价格为0可能有问题
    ]
    
    with open('sample_api_data.json', 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    print("示例API数据文件创建完成")

# ================================
# 9. 主程序入口
# ================================

def main():
    """主程序入口"""
    print("=== 数据质量监控系统演示 ===\n")
    
    # 创建示例数据
    print("1. 创建示例数据...")
    create_sample_database()
    create_sample_api_data()
    
    # 配置数据源
    SOURCE_CONFIGS = [
        {
            'name': 'orders_database',
            'type': 'database',
            'connection_string': 'sqlite:///ecommerce.db',
            'query': 'SELECT * FROM orders WHERE created_at >= datetime("now", "-1 day")'
        },
        {
            'name': 'products_api',
            'type': 'api',
            'url': 'http://localhost/sample_api_data.json'  # 实际使用时替换为真实API地址
        }
    ]
    
    # 配置指标
    METRIC_CONFIGS = [
        {
            'name': 'order_completeness',
            'type': 'completeness',
            'columns': ['order_id', 'customer_id', 'amount', 'status']
        },
        {
            'name': 'order_volume',
            'type': 'volume'
        },
        {
            'name': 'order_amount_accuracy',
            'type': 'accuracy',
            'column': 'amount',
            'min_value': 0  # 订单金额不能为负数
        },
        {
            'name': 'order_timeliness',
            'type': 'timeliness',
            'timestamp_column': 'created_at',
            'expected_frequency_hours': 1  # 期望每小时有新订单
        }
    ]
    
    # 配置异常检测
    DETECTION_CONFIGS = [
        {
            'metric': 'order_completeness',
            'type': 'threshold',
            'threshold': 0.95,
            'operator': 'lt'
        },
        {
            'metric': 'order_amount_accuracy',
            'type': 'threshold',
            'threshold': 0.98,
            'operator': 'lt'
        },
        {
            'metric': 'order_volume',
            'type': 'trend',
            'threshold': 0.5,  # 50%的偏差
            'window_size': 3,
            'historical_values': [100, 120, 110, 95, 105]  # 示例历史数据
        }
    ]
    
    # 配置通知
    NOTIFICATION_CONFIGS = [
        {
            'type': 'console',  # 使用控制台通知以便演示
            'recipients': ['admin@example.com', 'data-team@example.com']
        }
    ]
    
    # 初始化监控器
    print("\n2. 初始化监控器...")
    monitor = DataQualityMonitor()
    
    # 执行监控周期
    print("\n3. 执行监控周期...")
    anomalies = monitor.run_monitoring_cycle(
        SOURCE_CONFIGS,
        METRIC_CONFIGS,
        DETECTION_CONFIGS,
        NOTIFICATION_CONFIGS
    )
    
    # 显示结果
    print("\n4. 监控结果汇总:")
    if anomalies:
        print(f"   发现 {len(anomalies)} 个异常:")
        for i, anomaly in enumerate(anomalies, 1):
            print(f"   {i}. 数据源: {anomaly['source']}")
            print(f"      指标: {anomaly['metric']}")
            print(f"      当前值: {anomaly['value']}")
            print(f"      阈值: {anomaly['threshold']}")
            print(f"      详情: {anomaly['details']}")
            print()
    else:
        print("   未发现异常")
    
    # 创建监控仪表板
    print("\n5. 生成监控仪表板...")
    try:
        create_monitoring_dashboard(monitor)
    except Exception as e:
        print(f"生成监控仪表板时出错: {e}")
    
    # 智能告警演示
    print("\n6. 智能告警管理演示...")
    smart_alert_manager = SmartAlertManager()
    
    # 模拟重复告警
    sample_alert = {
        'source': 'orders_database',
        'metric': 'order_completeness',
        'value': 0.85,
        'threshold': 0.95,
        'details': '完整性低于阈值'
    }
    
    # 第一次告警
    print("第一次告警:")
    smart_alert_manager.process_alert(sample_alert, monitor.notifier, NOTIFICATION_CONFIGS)
    
    # 立即再次告警（应该被抑制）
    print("\n立即再次告警（应该被抑制）:")
    smart_alert_manager.process_alert(sample_alert, monitor.notifier, NOTIFICATION_CONFIGS)
    
    print("\n=== 演示完成 ===")

if __name__ == "__main__":
    main()