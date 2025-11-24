#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据质量监控工具
用于持续监控数据质量变化，及时发现和预警数据质量问题
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import sqlite3
import json
import warnings
warnings.filterwarnings('ignore')

class DataQualityMonitor:
    """数据质量监控器"""
    
    def __init__(self, db_path='quality_monitor.db'):
        """
        初始化监控器
        
        Args:
            db_path (str): 监控数据库路径
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化监控数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建质量指标表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quality_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_name TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                threshold REAL,
                dimension TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                details TEXT
            )
        ''')
        
        # 创建监控配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitor_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_name TEXT NOT NULL,
                dimension TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                threshold REAL,
                check_interval INTEGER,
                alert_enabled BOOLEAN DEFAULT 1,
                alert_recipients TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # 创建告警记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_name TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                alert_level TEXT NOT NULL,
                message TEXT NOT NULL,
                threshold REAL,
                actual_value REAL,
                timestamp TEXT NOT NULL,
                acknowledged BOOLEAN DEFAULT 0,
                acknowledged_by TEXT,
                acknowledged_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_metric(self, dataset_name, dimension, metric_name, threshold=None, 
                        check_interval=3600, alert_enabled=True, alert_recipients=None):
        """
        注册监控指标
        
        Args:
            dataset_name (str): 数据集名称
            dimension (str): 质量维度
            metric_name (str): 指标名称
            threshold (float): 阈值
            check_interval (int): 检查间隔（秒）
            alert_enabled (bool): 是否启用告警
            alert_recipients (list): 告警接收者列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        current_time = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO monitor_configs 
            (dataset_name, dimension, metric_name, threshold, check_interval, 
             alert_enabled, alert_recipients, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            dataset_name, dimension, metric_name, threshold, check_interval,
            alert_enabled, json.dumps(alert_recipients) if alert_recipients else None,
            current_time, current_time
        ))
        
        conn.commit()
        conn.close()
    
    def record_metric(self, dataset_name, dimension, metric_name, metric_value, 
                      threshold=None, details=None):
        """
        记录质量指标
        
        Args:
            dataset_name (str): 数据集名称
            dimension (str): 质量维度
            metric_name (str): 指标名称
            metric_value (float): 指标值
            threshold (float): 阈值
            details (dict): 详细信息
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        current_time = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO quality_metrics 
            (dataset_name, metric_name, metric_value, threshold, dimension, timestamp, details)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            dataset_name, metric_name, metric_value, threshold, dimension, 
            current_time, json.dumps(details) if details else None
        ))
        
        conn.commit()
        conn.close()
        
        # 检查是否需要告警
        if threshold is not None:
            self._check_alert(dataset_name, metric_name, metric_value, threshold, details)
    
    def calculate_completeness(self, df, dataset_name, columns=None):
        """
        计算完整性指标
        
        Args:
            df (pd.DataFrame): 数据集
            dataset_name (str): 数据集名称
            columns (list): 要检查的列，如果为None则检查所有列
            
        Returns:
            dict: 完整性指标
        """
        if columns is None:
            columns = df.columns.tolist()
        
        metrics = {}
        
        # 整体完整性
        total_cells = len(df) * len(columns)
        missing_cells = df[columns].isnull().sum().sum()
        completeness_score = (1 - missing_cells / total_cells) * 100
        
        metrics['overall'] = completeness_score
        
        # 各列完整性
        for col in columns:
            col_missing = df[col].isnull().sum()
            col_completeness = (1 - col_missing / len(df)) * 100
            metrics[col] = col_completeness
        
        # 记录指标
        self.record_metric(
            dataset_name=dataset_name,
            dimension='completeness',
            metric_name='overall_completeness',
            metric_value=completeness_score,
            details={'missing_cells': missing_cells, 'total_cells': total_cells}
        )
        
        for col, score in metrics.items():
            if col != 'overall':
                self.record_metric(
                    dataset_name=dataset_name,
                    dimension='completeness',
                    metric_name=f'completeness_{col}',
                    metric_value=score
                )
        
        return metrics
    
    def calculate_uniqueness(self, df, dataset_name, columns=None):
        """
        计算唯一性指标
        
        Args:
            df (pd.DataFrame): 数据集
            dataset_name (str): 数据集名称
            columns (list): 要检查的列，如果为None则检查所有列
            
        Returns:
            dict: 唯一性指标
        """
        if columns is None:
            columns = df.columns.tolist()
        
        metrics = {}
        
        for col in columns:
            duplicate_count = df[col].duplicated().sum()
            uniqueness_score = (1 - duplicate_count / len(df)) * 100
            metrics[col] = uniqueness_score
            
            self.record_metric(
                dataset_name=dataset_name,
                dimension='uniqueness',
                metric_name=f'uniqueness_{col}',
                metric_value=uniqueness_score,
                details={'duplicate_count': duplicate_count, 'total_count': len(df)}
            )
        
        return metrics
    
    def calculate_validity(self, df, dataset_name, column_rules=None):
        """
        计算有效性指标
        
        Args:
            df (pd.DataFrame): 数据集
            dataset_name (str): 数据集名称
            column_rules (dict): 列验证规则
            
        Returns:
            dict: 有效性指标
        """
        if column_rules is None:
            column_rules = {}
        
        metrics = {}
        
        for col, rule in column_rules.items():
            if col not in df.columns:
                continue
                
            col_data = df[col].dropna()
            total_count = len(col_data)
            valid_count = 0
            
            for _, value in col_data.items():
                if self._validate_value(value, rule):
                    valid_count += 1
            
            validity_score = (valid_count / total_count) * 100 if total_count > 0 else 100
            metrics[col] = validity_score
            
            self.record_metric(
                dataset_name=dataset_name,
                dimension='validity',
                metric_name=f'validity_{col}',
                metric_value=validity_score,
                details={'valid_count': valid_count, 'total_count': total_count}
            )
        
        return metrics
    
    def calculate_timeliness(self, df, dataset_name, date_column, threshold_days=30):
        """
        计算时效性指标
        
        Args:
            df (pd.DataFrame): 数据集
            dataset_name (str): 数据集名称
            date_column (str): 日期列名
            threshold_days (int): 时效性阈值（天数）
            
        Returns:
            dict: 时效性指标
        """
        if date_column not in df.columns:
            return {}
        
        # 转换日期列
        try:
            date_series = pd.to_datetime(df[date_column], errors='coerce')
        except:
            return {}
        
        current_date = datetime.now()
        threshold_date = current_date - timedelta(days=threshold_days)
        
        timely_records = (date_series >= threshold_date).sum()
        total_records = len(date_series.dropna())
        
        timeliness_score = (timely_records / total_records) * 100 if total_records > 0 else 100
        
        # 计算平均延迟天数
        delays = (current_date - date_series).dt.days
        avg_delay = delays.mean()
        
        metrics = {
            'timeliness': timeliness_score,
            'avg_delay_days': avg_delay
        }
        
        self.record_metric(
            dataset_name=dataset_name,
            dimension='timeliness',
            metric_name='timeliness_score',
            metric_value=timeliness_score,
            details={'timely_records': timely_records, 'total_records': total_records}
        )
        
        self.record_metric(
            dataset_name=dataset_name,
            dimension='timeliness',
            metric_name='avg_delay_days',
            metric_value=avg_delay,
            details={'threshold_days': threshold_days}
        )
        
        return metrics
    
    def get_metric_history(self, dataset_name, metric_name, days=30):
        """
        获取指标历史数据
        
        Args:
            dataset_name (str): 数据集名称
            metric_name (str): 指标名称
            days (int): 天数
            
        Returns:
            pd.DataFrame: 历史数据
        """
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT metric_value, timestamp, threshold, details
            FROM quality_metrics
            WHERE dataset_name = ? AND metric_name = ?
            AND timestamp >= datetime('now', '-{} days')
            ORDER BY timestamp
        '''.format(days)
        
        df = pd.read_sql_query(query, conn, params=(dataset_name, metric_name))
        conn.close()
        
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['details'] = df['details'].apply(lambda x: json.loads(x) if x else None)
        
        return df
    
    def get_current_metrics(self, dataset_name, dimension=None):
        """
        获取当前质量指标
        
        Args:
            dataset_name (str): 数据集名称
            dimension (str): 质量维度
            
        Returns:
            pd.DataFrame: 当前指标
        """
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT 
                metric_name, 
                metric_value, 
                threshold, 
                dimension,
                max(timestamp) as latest_timestamp
            FROM quality_metrics
            WHERE dataset_name = ?
        '''
        
        params = [dataset_name]
        
        if dimension:
            query += ' AND dimension = ?'
            params.append(dimension)
        
        query += ' GROUP BY metric_name ORDER BY metric_name'
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return df
    
    def generate_quality_report(self, dataset_name, output_format='html'):
        """
        生成质量报告
        
        Args:
            dataset_name (str): 数据集名称
            output_format (str): 输出格式 ('html', 'json', 'markdown')
            
        Returns:
            str: 报告内容
        """
        # 获取当前指标
        current_metrics = self.get_current_metrics(dataset_name)
        
        # 获取告警记录
        conn = sqlite3.connect(self.db_path)
        alert_query = '''
            SELECT metric_name, alert_level, message, threshold, actual_value, timestamp
            FROM alert_logs
            WHERE dataset_name = ? AND acknowledged = 0
            ORDER BY timestamp DESC
            LIMIT 20
        '''
        alerts_df = pd.read_sql_query(alert_query, conn, params=(dataset_name,))
        conn.close()
        
        if output_format == 'html':
            return self._generate_html_report(dataset_name, current_metrics, alerts_df)
        elif output_format == 'json':
            return self._generate_json_report(dataset_name, current_metrics, alerts_df)
        elif output_format == 'markdown':
            return self._generate_markdown_report(dataset_name, current_metrics, alerts_df)
        else:
            raise ValueError(f"不支持的输出格式: {output_format}")
    
    def visualize_trends(self, dataset_name, metrics=None, days=30, save_path=None):
        """
        可视化质量趋势
        
        Args:
            dataset_name (str): 数据集名称
            metrics (list): 要可视化的指标列表，如果为None则选择所有指标
            days (int): 天数
            save_path (str): 保存路径
        """
        # 获取所有可用指标
        all_metrics = self.get_current_metrics(dataset_name)
        
        if metrics is None:
            metrics = all_metrics['metric_name'].tolist()
        
        # 为每个指标获取历史数据
        fig, axes = plt.subplots(len(metrics), 1, figsize=(12, 5 * len(metrics)))
        if len(metrics) == 1:
            axes = [axes]
        
        for i, metric_name in enumerate(metrics):
            history_data = self.get_metric_history(dataset_name, metric_name, days)
            
            ax = axes[i]
            
            if not history_data.empty:
                # 绘制指标值
                ax.plot(history_data['timestamp'], history_data['metric_value'], 
                        marker='o', label='指标值')
                
                # 绘制阈值线
                if 'threshold' in history_data.columns and history_data['threshold'].notna().any():
                    threshold_value = history_data['threshold'].iloc[0]
                    ax.axhline(y=threshold_value, color='r', linestyle='--', 
                             label=f'阈值: {threshold_value}')
                
                ax.set_title(f'{dataset_name} - {metric_name} 趋势')
                ax.set_xlabel('时间')
                ax.set_ylabel('指标值')
                ax.legend()
                ax.grid(True)
                
                # 格式化x轴日期标签
                ax.tick_params(axis='x', rotation=45)
            else:
                ax.text(0.5, 0.5, '无数据', horizontalalignment='center', 
                        verticalalignment='center')
                ax.set_title(f'{dataset_name} - {metric_name} (无数据)')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def _check_alert(self, dataset_name, metric_name, actual_value, threshold, details=None):
        """
        检查是否需要告警
        
        Args:
            dataset_name (str): 数据集名称
            metric_name (str): 指标名称
            actual_value (float): 实际值
            threshold (float): 阈值
            details (dict): 详细信息
        """
        # 判断告警级别
        alert_level = None
        
        if actual_value < threshold * 0.7:
            alert_level = 'critical'
        elif actual_value < threshold:
            alert_level = 'warning'
        
        if alert_level:
            self._create_alert(dataset_name, metric_name, alert_level, threshold, actual_value, details)
    
    def _create_alert(self, dataset_name, metric_name, alert_level, threshold, actual_value, details=None):
        """
        创建告警记录
        
        Args:
            dataset_name (str): 数据集名称
            metric_name (str): 指标名称
            alert_level (str): 告警级别
            threshold (float): 阈值
            actual_value (float): 实际值
            details (dict): 详细信息
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        current_time = datetime.now().isoformat()
        
        message = f'{dataset_name} 的 {metric_name} 指标值为 {actual_value:.2f}，低于阈值 {threshold}'
        
        cursor.execute('''
            INSERT INTO alert_logs 
            (dataset_name, metric_name, alert_level, message, threshold, actual_value, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            dataset_name, metric_name, alert_level, message, threshold, actual_value, current_time
        ))
        
        conn.commit()
        conn.close()
        
        print(f"[{alert_level.upper()}] {message}")
    
    def _validate_value(self, value, rule):
        """
        验证值是否符合规则
        
        Args:
            value: 要验证的值
            rule (dict): 验证规则
            
        Returns:
            bool: 是否有效
        """
        import re
        
        rule_type = rule.get('type')
        
        if rule_type == 'regex':
            pattern = rule.get('pattern')
            return re.match(pattern, str(value)) is not None
        elif rule_type == 'range':
            min_val = rule.get('min')
            max_val = rule.get('max')
            
            if min_val is not None and value < min_val:
                return False
            if max_val is not None and value > max_val:
                return False
            return True
        elif rule_type == 'enum':
            valid_values = rule.get('values', [])
            return value in valid_values
        
        return True
    
    def _generate_html_report(self, dataset_name, current_metrics, alerts_df):
        """生成HTML格式报告"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>数据质量报告 - {dataset_name}</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f5f5f5; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; min-width: 150px; }}
                .score {{ font-size: 24px; font-weight: bold; }}
                .good {{ color: green; }}
                .warning {{ color: orange; }}
                .bad {{ color: red; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .alert {{ background-color: #ffe6e6; padding: 10px; margin: 10px 0; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>数据质量报告</h1>
                <p>数据集: {dataset_name}</p>
                <p>报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>当前质量指标</h2>
        """
        
        # 添加当前指标
        for _, row in current_metrics.iterrows():
            score = row['metric_value']
            score_class = "good" if score >= 90 else "warning" if score >= 80 else "bad"
            
            html += f"""
                <div class="metric">
                    <div>{row['metric_name']}</div>
                    <div class="score {score_class}">{score:.1f}</div>
                    <div>阈值: {row['threshold']}</div>
                </div>
            """
        
        html += """
            </div>
            
            <div class="section">
                <h2>未处理告警</h2>
        """
        
        # 添加告警信息
        if not alerts_df.empty:
            for _, alert in alerts_df.iterrows():
                alert_class = "alert alert-critical" if alert['alert_level'] == 'critical' else "alert alert-warning"
                html += f"""
                    <div class="{alert_class}">
                        <strong>{alert['alert_level'].upper()}</strong> - {alert['message']} 
                        <small>({alert['timestamp']})</small>
                    </div>
                """
        else:
            html += "<p>当前无未处理告警</p>"
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_json_report(self, dataset_name, current_metrics, alerts_df):
        """生成JSON格式报告"""
        report = {
            'dataset_name': dataset_name,
            'report_time': datetime.now().isoformat(),
            'current_metrics': current_metrics.to_dict(orient='records'),
            'unacknowledged_alerts': alerts_df.to_dict(orient='records')
        }
        
        return json.dumps(report, indent=2, ensure_ascii=False)
    
    def _generate_markdown_report(self, dataset_name, current_metrics, alerts_df):
        """生成Markdown格式报告"""
        md = f"""# 数据质量报告

## 基本信息

- **数据集**: {dataset_name}
- **报告时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 当前质量指标

| 指标名称 | 当前值 | 阈值 | 状态 |
|----------|--------|------|------|
"""
        
        # 添加当前指标
        for _, row in current_metrics.iterrows():
            score = row['metric_value']
            threshold = row['threshold']
            status = "良好" if score >= threshold else "需要关注"
            
            md += f"| {row['metric_name']} | {score:.2f} | {threshold} | {status} |\n"
        
        md += "\n## 未处理告警\n\n"
        
        # 添加告警信息
        if not alerts_df.empty:
            for _, alert in alerts_df.iterrows():
                md += f"### **{alert['alert_level'].upper()}**\n\n"
                md += f"{alert['message']} ({alert['timestamp']})\n\n"
        else:
            md += "当前无未处理告警\n"
        
        return md


# 示例使用
if __name__ == "__main__":
    # 创建示例数据
    data = {
        'customer_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'name': ['张三', '李四', '王五', '赵六', '钱七', None, '孙八', '周九', '吴十', '郑十一'],
        'email': [
            'zhangsan@example.com',
            'LISI@example.com',
            'wangwu@example.com',
            'zhaoliu@example.com',
            'qianqi@example.com',
            'invalid-email',
            'sunba@example.com',
            'zhoujiu@example.com',
            'wushi@example.com',
            'zhengshiyi@example.com'
        ],
        'phone': [
            '13812345678',
            '13912345678',
            '13612345678',
            '13712345678',
            '13512345678',
            'invalid-phone',
            '13312345678',
            '13212345678',
            '13112345678',
            'invalid-phone'
        ],
        'age': [25, 30, 35, 40, 45, 50, 55, 60, 65, 200],
        'registration_date': [
            '2023-01-01',
            '2023-01-15',
            '2023-02-01',
            '2023-02-15',
            '2023-03-01',
            '2023-03-15',
            '2023-04-01',
            '2023-04-15',
            '2023-05-01',
            '2023-05-15'
        ]
    }
    
    df = pd.DataFrame(data)
    dataset_name = 'customer_data'
    
    # 创建监控器
    monitor = DataQualityMonitor()
    
    # 注册监控指标
    monitor.register_metric(
        dataset_name=dataset_name,
        dimension='completeness',
        metric_name='overall_completeness',
        threshold=90
    )
    
    monitor.register_metric(
        dataset_name=dataset_name,
        dimension='validity',
        metric_name='validity_email',
        threshold=95
    )
    
    # 计算并记录质量指标
    print("计算质量指标...")
    completeness = monitor.calculate_completeness(df, dataset_name)
    print(f"完整性指标: {completeness}")
    
    uniqueness = monitor.calculate_uniqueness(df, dataset_name, ['customer_id', 'email'])
    print(f"唯一性指标: {uniqueness}")
    
    validity_rules = {
        'email': {'type': 'regex', 'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'},
        'phone': {'type': 'regex', 'pattern': r'^1[3-9]\d{9}$'},
        'age': {'type': 'range', 'min': 0, 'max': 120}
    }
    
    validity = monitor.calculate_validity(df, dataset_name, validity_rules)
    print(f"有效性指标: {validity}")
    
    timeliness = monitor.calculate_timeliness(df, dataset_name, 'registration_date', threshold_days=365)
    print(f"时效性指标: {timeliness}")
    
    # 生成质量报告
    print("\n生成质量报告...")
    html_report = monitor.generate_quality_report(dataset_name, 'html')
    with open(f'{dataset_name}_quality_report.html', 'w', encoding='utf-8') as f:
        f.write(html_report)
    
    markdown_report = monitor.generate_quality_report(dataset_name, 'markdown')
    with open(f'{dataset_name}_quality_report.md', 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    
    # 模拟多次数据采集，生成趋势数据
    print("\n模拟数据采集，生成趋势数据...")
    for day in range(1, 8):
        # 模拟数据质量变化
        sim_data = df.copy()
        
        # 随机引入一些问题
        if day % 3 == 0:
            idx = np.random.randint(0, len(sim_data) - 1)
            sim_data.loc[idx, 'name'] = None
        
        if day % 4 == 0:
            idx = np.random.randint(0, len(sim_data) - 1)
            sim_data.loc[idx, 'email'] = 'invalid-email-' + str(day)
        
        # 计算指标
        monitor.calculate_completeness(sim_data, dataset_name)
        monitor.calculate_validity(sim_data, dataset_name, validity_rules)
        
        print(f"Day {day}: 记录质量指标")
    
    # 可视化趋势
    print("\n可视化质量趋势...")
    monitor.visualize_trends(
        dataset_name=dataset_name,
        metrics=['overall_completeness', 'validity_email'],
        days=7,
        save_path=f'{dataset_name}_quality_trends.png'
    )
    
    print("\n数据质量监控完成！")
    print(f"HTML报告: {dataset_name}_quality_report.html")
    print(f"Markdown报告: {dataset_name}_quality_report.md")
    print(f"趋势图表: {dataset_name}_quality_trends.png")