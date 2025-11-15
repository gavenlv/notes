#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据质量评估指标计算示例
本脚本演示了如何计算各种数据质量指标，包括准确性、完整性、一致性等
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re


class DataQualityMetrics:
    """数据质量指标计算器"""
    
    def __init__(self, df):
        """
        初始化数据质量指标计算器
        
        Args:
            df (pandas.DataFrame): 待评估的数据框
        """
        self.df = df
        self.total_records = len(df)
        
    def accuracy_metrics(self, column, expected_values=None):
        """
        计算准确性指标
        
        Args:
            column (str): 要评估的列名
            expected_values (set, optional): 期望的值集合
            
        Returns:
            dict: 包含准确性指标的字典
        """
        if expected_values is None:
            # 如果没有提供期望值，这里只是一个示例
            # 实际应用中应根据业务规则定义期望值
            return {
                'accuracy_rate': 100.0,
                'error_rate': 0.0,
                'accurate_count': self.total_records,
                'error_count': 0
            }
            
        # 计算准确记录数
        accurate_mask = self.df[column].isin(expected_values)
        accurate_count = accurate_mask.sum()
        error_count = self.total_records - accurate_count
        
        accuracy_rate = (accurate_count / self.total_records) * 100
        error_rate = (error_count / self.total_records) * 100
        
        return {
            'accuracy_rate': round(accuracy_rate, 2),
            'error_rate': round(error_rate, 2),
            'accurate_count': accurate_count,
            'error_count': error_count
        }
    
    def completeness_metrics(self, columns=None):
        """
        计算完整性指标
        
        Args:
            columns (list, optional): 要评估的列名列表，如果为None则评估所有列
            
        Returns:
            dict: 包含完整性指标的字典
        """
        if columns is None:
            columns = self.df.columns.tolist()
            
        results = {}
        
        for col in columns:
            # 计算非空值数量
            non_null_count = self.df[col].notna().sum()
            null_count = self.total_records - non_null_count
            
            completeness_rate = (non_null_count / self.total_records) * 100
            missing_rate = (null_count / self.total_records) * 100
            
            results[col] = {
                'completeness_rate': round(completeness_rate, 2),
                'missing_rate': round(missing_rate, 2),
                'non_null_count': non_null_count,
                'null_count': null_count
            }
            
        # 计算整体完整性
        total_cells = self.total_records * len(columns)
        total_non_null = sum([results[col]['non_null_count'] for col in columns])
        total_null = total_cells - total_non_null
        
        overall_completeness = (total_non_null / total_cells) * 100
        overall_missing = (total_null / total_cells) * 100
        
        results['overall'] = {
            'completeness_rate': round(overall_completeness, 2),
            'missing_rate': round(overall_missing, 2),
            'total_cells': total_cells,
            'filled_cells': total_non_null,
            'empty_cells': total_null
        }
        
        return results
    
    def consistency_metrics(self, column_pairs):
        """
        计算一致性指标
        
        Args:
            column_pairs (list): 列对列表，例如 [('col1', 'col2'), ('col3', 'col4')]
            
        Returns:
            dict: 包含一致性指标的字典
        """
        results = {}
        
        for col1, col2 in column_pairs:
            # 比较两列的一致性
            consistent_mask = self.df[col1] == self.df[col2]
            consistent_count = consistent_mask.sum()
            conflict_count = self.total_records - consistent_count
            
            consistency_rate = (consistent_count / self.total_records) * 100
            conflict_rate = (conflict_count / self.total_records) * 100
            
            results[f"{col1}_vs_{col2}"] = {
                'consistency_rate': round(consistency_rate, 2),
                'conflict_rate': round(conflict_rate, 2),
                'consistent_count': consistent_count,
                'conflict_count': conflict_count
            }
            
        return results
    
    def timeliness_metrics(self, date_column, expected_update_frequency='daily'):
        """
        计算及时性指标
        
        Args:
            date_column (str): 时间戳列名
            expected_update_frequency (str): 期望更新频率 ('daily', 'weekly', 'monthly')
            
        Returns:
            dict: 包含及时性指标的字典
        """
        # 确保日期列是datetime类型
        if not pd.api.types.is_datetime64_any_dtype(self.df[date_column]):
            self.df[date_column] = pd.to_datetime(self.df[date_column])
            
        # 获取当前时间
        now = datetime.now()
        
        # 根据更新频率计算期望的最新更新时间
        if expected_update_frequency == 'daily':
            expected_latest = now - timedelta(days=1)
        elif expected_update_frequency == 'weekly':
            expected_latest = now - timedelta(weeks=1)
        elif expected_update_frequency == 'monthly':
            expected_latest = now - timedelta(days=30)
        else:
            expected_latest = now - timedelta(days=1)  # 默认每日
            
        # 计算及时更新的记录数
        timely_mask = self.df[date_column] >= expected_latest
        timely_count = timely_mask.sum()
        delayed_count = self.total_records - timely_count
        
        timeliness_rate = (timely_count / self.total_records) * 100
        delay_rate = (delayed_count / self.total_records) * 100
        
        # 计算平均延迟时间
        delays = now - self.df[date_column]
        avg_delay_days = delays.dt.days.mean()
        
        return {
            'timeliness_rate': round(timeliness_rate, 2),
            'delay_rate': round(delay_rate, 2),
            'timely_count': timely_count,
            'delayed_count': delayed_count,
            'average_delay_days': round(avg_delay_days, 2)
        }
    
    def uniqueness_metrics(self, columns):
        """
        计算唯一性指标
        
        Args:
            columns (list): 要检查唯一性的列名列表
            
        Returns:
            dict: 包含唯一性指标的字典
        """
        results = {}
        
        for col in columns:
            # 计算唯一值数量
            unique_count = self.df[col].nunique()
            duplicate_count = self.total_records - unique_count
            
            uniqueness_rate = (unique_count / self.total_records) * 100
            duplication_rate = (duplicate_count / self.total_records) * 100
            
            results[col] = {
                'uniqueness_rate': round(uniqueness_rate, 2),
                'duplication_rate': round(duplication_rate, 2),
                'unique_count': unique_count,
                'duplicate_count': duplicate_count
            }
            
        return results
    
    def validity_metrics(self, column, validation_func):
        """
        计算有效性指标
        
        Args:
            column (str): 要验证的列名
            validation_func (function): 验证函数，返回布尔值
            
        Returns:
            dict: 包含有效性指标的字典
        """
        # 应用验证函数
        valid_mask = self.df[column].apply(validation_func)
        valid_count = valid_mask.sum()
        invalid_count = self.total_records - valid_count
        
        validity_rate = (valid_count / self.total_records) * 100
        invalidity_rate = (invalid_count / self.total_records) * 100
        
        return {
            'validity_rate': round(validity_rate, 2),
            'invalidity_rate': round(invalidity_rate, 2),
            'valid_count': valid_count,
            'invalid_count': invalid_count
        }
    
    def composite_dq_index(self, weights=None):
        """
        计算综合数据质量指数 (Composite Data Quality Index)
        
        Args:
            weights (dict, optional): 各维度权重，默认相等
            
        Returns:
            float: 综合数据质量指数
        """
        if weights is None:
            # 默认各维度权重相等
            weights = {
                'accuracy': 0.167,
                'completeness': 0.167,
                'consistency': 0.167,
                'timeliness': 0.167,
                'uniqueness': 0.167,
                'validity': 0.165
            }
        
        # 这里简化计算，实际应用中应基于具体指标计算
        # 假设各维度得分都是85分
        dimension_scores = {
            'accuracy': 85.0,
            'completeness': 85.0,
            'consistency': 85.0,
            'timeliness': 85.0,
            'uniqueness': 85.0,
            'validity': 85.0
        }
        
        # 计算加权平均
        cdqi = sum(weights[dim] * score for dim, score in dimension_scores.items())
        
        return round(cdqi, 2)


def validate_email(email):
    """验证邮箱格式"""
    if pd.isna(email):
        return False
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    return bool(re.match(pattern, str(email)))


def validate_phone(phone):
    """验证电话号码格式"""
    if pd.isna(phone):
        return False
    # 简单的电话号码验证（11位数字）
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, str(phone)))


def create_sample_data():
    """创建示例数据"""
    data = {
        'customer_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                       11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
        'name': ['张三', '李四', '王五', '赵六', '钱七',
                '孙八', '周九', '吴十', '郑一', '王二',
                '张三', '李四', None, '赵六', '钱七',
                '孙八', '周九', '吴十', '郑一', '王二'],
        'email': ['zhangsan@example.com', 'lisi@example.com', 'wangwu@example.com',
                 'zhaoliu@example.com', 'qianqi@example.com',
                 'sunba@example.com', 'zhoujiu@example.com', 'wushi@example.com',
                 'zhengyi@example.com', 'wanger@example.com',
                 'zhangsan@example.com', 'lisi@example.com', 'invalid-email',
                 'zhaoliu@example.com', 'qianqi@example.com',
                 'sunba@example.com', 'zhoujiu@example.com', 'wushi@example.com',
                 'zhengyi@example.com', 'wanger@example.com'],
        'phone': ['13812345678', '13987654321', '13711223344',
                 '13655667788', '13599887766',
                 '13411223344', '13355667788', '13299887766',
                 '13111223344', '13055667788',
                 '13812345678', '13987654321', '13711223344',
                 '13655667788', '13599887766',
                 '13411223344', '13355667788', '13299887766',
                 '13111223344', '13055667788'],
        'address': ['北京市朝阳区', '上海市浦东新区', '广州市天河区',
                   '深圳市南山区', '杭州市西湖区',
                   '南京市鼓楼区', '成都市锦江区', '武汉市江汉区',
                   '西安市雁塔区', '重庆市渝中区',
                   '北京市朝阳区', '上海市浦东新区', '广州市天河区',
                   '深圳市南山区', '杭州市西湖区',
                   '南京市鼓楼区', '成都市锦江区', '武汉市江汉区',
                   '西安市雁塔区', None],
        'registration_date': [
            datetime.now() - timedelta(days=5),
            datetime.now() - timedelta(days=10),
            datetime.now() - timedelta(days=15),
            datetime.now() - timedelta(days=20),
            datetime.now() - timedelta(days=25),
            datetime.now() - timedelta(days=30),
            datetime.now() - timedelta(days=35),
            datetime.now() - timedelta(days=40),
            datetime.now() - timedelta(days=45),
            datetime.now() - timedelta(days=50),
            datetime.now() - timedelta(days=55),
            datetime.now() - timedelta(days=60),
            datetime.now() - timedelta(days=65),
            datetime.now() - timedelta(days=70),
            datetime.now() - timedelta(days=75),
            datetime.now() - timedelta(days=80),
            datetime.now() - timedelta(days=85),
            datetime.now() - timedelta(days=90),
            datetime.now() - timedelta(days=95),
            datetime.now() - timedelta(days=100)
        ]
    }
    
    # 创建DataFrame
    df = pd.DataFrame(data)
    return df


def main():
    """主函数"""
    print("=== 数据质量评估指标计算示例 ===\n")
    
    # 创建示例数据
    df = create_sample_data()
    print(f"示例数据形状: {df.shape}")
    print("\n前5行数据:")
    print(df.head())
    
    # 初始化数据质量指标计算器
    dq_metrics = DataQualityMetrics(df)
    
    print("\n=== 1. 完整性指标 ===")
    completeness_results = dq_metrics.completeness_metrics()
    for col, metrics in completeness_results.items():
        if col != 'overall':
            print(f"{col}: 完整性率={metrics['completeness_rate']}%, "
                  f"缺失率={metrics['missing_rate']}%")
    
    print(f"\n整体完整性: 完整性率={completeness_results['overall']['completeness_rate']}%, "
          f"缺失率={completeness_results['overall']['missing_rate']}%")
    
    print("\n=== 2. 唯一性指标 ===")
    uniqueness_results = dq_metrics.uniqueness_metrics(['customer_id'])
    for col, metrics in uniqueness_results.items():
        print(f"{col}: 唯一性率={metrics['uniqueness_rate']}%, "
              f"重复率={metrics['duplication_rate']}%")
    
    print("\n=== 3. 有效性指标 ===")
    # 邮箱有效性
    email_validity = dq_metrics.validity_metrics('email', validate_email)
    print(f"邮箱有效性: 有效率={email_validity['validity_rate']}%, "
          f"无效率={email_validity['invalidity_rate']}%")
    
    # 电话号码有效性
    phone_validity = dq_metrics.validity_metrics('phone', validate_phone)
    print(f"电话有效性: 有效率={phone_validity['validity_rate']}%, "
          f"无效率={phone_validity['invalidity_rate']}%")
    
    print("\n=== 4. 及时性指标 ===")
    timeliness_results = dq_metrics.timeliness_metrics('registration_date', 'daily')
    print(f"注册时间及时性: 及时率={timeliness_results['timeliness_rate']}%, "
          f"延迟率={timeliness_results['delay_rate']}%")
    print(f"平均延迟天数: {timeliness_results['average_delay_days']}天")
    
    print("\n=== 5. 一致性指标 ===")
    # 创建一些用于一致性检查的示例数据
    df_copy = df.copy()
    df_copy['email_copy'] = df_copy['email']
    # 人为制造一些不一致
    df_copy.loc[0, 'email_copy'] = 'different@example.com'
    df_copy.loc[5, 'email_copy'] = 'another@example.com'
    
    dq_metrics_copy = DataQualityMetrics(df_copy)
    consistency_results = dq_metrics_copy.consistency_metrics([('email', 'email_copy')])
    for comparison, metrics in consistency_results.items():
        print(f"{comparison}: 一致性率={metrics['consistency_rate']}%, "
              f"冲突率={metrics['conflict_rate']}%")
    
    print("\n=== 6. 综合数据质量指数 ===")
    cdqi = dq_metrics.composite_dq_index()
    print(f"综合数据质量指数 (CDQI): {cdqi}")


if __name__ == "__main__":
    main()