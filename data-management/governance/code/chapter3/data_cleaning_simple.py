#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据清洗工具（简化版）
用于处理数据质量问题，包括缺失值处理、重复数据删除、异常值检测与处理
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

class DataCleaner:
    """数据清洗器"""
    
    def __init__(self, df: pd.DataFrame):
        """
        初始化清洗器
        
        Args:
            df (pd.DataFrame): 待清洗的数据集
        """
        self.original_df = df.copy()
        self.df = df.copy()
        self.cleaning_log = []
    
    def handle_missing_values(self, strategy: str = 'mean', columns: list = None, fill_value=None):
        """
        处理缺失值
        
        Args:
            strategy (str): 处理策略 ('mean', 'median', 'mode', 'drop', 'fill', 'forward_fill', 'backward_fill')
            columns (list): 要处理的列，如果为None则处理所有列
            fill_value: 当strategy='fill'时使用的填充值
        """
        if columns is None:
            columns = self.df.columns.tolist()
        
        original_missing = self.df[columns].isnull().sum().to_dict()
        
        if strategy == 'drop':
            self.df.dropna(subset=columns, inplace=True)
        
        elif strategy == 'fill':
            if fill_value is None:
                raise ValueError("使用'fill'策略时必须提供fill_value参数")
            self.df[columns] = self.df[columns].fillna(fill_value)
        
        elif strategy == 'mean':
            for col in columns:
                if self.df[col].dtype in ['int64', 'float64']:
                    self.df[col].fillna(self.df[col].mean(), inplace=True)
        
        elif strategy == 'median':
            for col in columns:
                if self.df[col].dtype in ['int64', 'float64']:
                    self.df[col].fillna(self.df[col].median(), inplace=True)
        
        elif strategy == 'mode':
            for col in columns:
                mode_value = self.df[col].mode()
                if len(mode_value) > 0:
                    self.df[col].fillna(mode_value[0], inplace=True)
        
        elif strategy == 'forward_fill':
            self.df[columns] = self.df[columns].fillna(method='ffill')
        
        elif strategy == 'backward_fill':
            self.df[columns] = self.df[columns].fillna(method='bfill')
        
        # 记录清洗操作
        after_missing = self.df[columns].isnull().sum().to_dict()
        
        self.cleaning_log.append({
            'operation': 'handle_missing_values',
            'strategy': strategy,
            'columns': columns,
            'before': original_missing,
            'after': after_missing,
            'timestamp': datetime.now().isoformat()
        })
        
        return self.df
    
    def remove_duplicates(self, columns=None, keep='first'):
        """
        删除重复数据
        
        Args:
            columns: 要检查重复的列，如果为None则检查所有列
            keep: 保留策略 ('first', 'last', False)
        """
        original_shape = self.df.shape[0]
        self.df.drop_duplicates(subset=columns, keep=keep, inplace=True)
        duplicates_removed = original_shape - self.df.shape[0]
        
        self.cleaning_log.append({
            'operation': 'remove_duplicates',
            'columns': columns,
            'keep': keep,
            'duplicates_removed': duplicates_removed,
            'timestamp': datetime.now().isoformat()
        })
        
        return self.df
    
    def detect_outliers_iqr(self, column, threshold=1.5):
        """
        使用IQR方法检测异常值
        
        Args:
            column: 要检测的列名
            threshold: IQR阈值倍数
        """
        q1 = self.df[column].quantile(0.25)
        q3 = self.df[column].quantile(0.75)
        iqr = q3 - q1
        
        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr
        
        outliers_mask = (self.df[column] < lower_bound) | (self.df[column] > upper_bound)
        return outliers_mask
    
    def detect_outliers_zscore(self, column, threshold=3.0):
        """
        使用Z-score方法检测异常值
        
        Args:
            column: 要检测的列名
            threshold: Z-score阈值
        """
        z_scores = np.abs((self.df[column] - self.df[column].mean()) / self.df[column].std())
        return z_scores > threshold
    
    def handle_outliers(self, column, method='iqr', strategy='cap', threshold=None):
        """
        处理异常值
        
        Args:
            column: 要处理的列名
            method: 检测方法 ('iqr', 'zscore')
            strategy: 处理策略 ('remove', 'cap')
            threshold: 检测阈值
        """
        if method == 'iqr':
            outlier_mask = self.detect_outliers_iqr(column, threshold or 1.5)
        elif method == 'zscore':
            outlier_mask = self.detect_outliers_zscore(column, threshold or 3.0)
        else:
            raise ValueError(f"不支持的异常值检测方法: {method}")
        
        outliers_count = outlier_mask.sum()
        
        if strategy == 'remove':
            self.df = self.df[~outlier_mask].copy()
        
        elif strategy == 'cap':
            if method == 'iqr':
                q1 = self.df[column].quantile(0.25)
                q3 = self.df[column].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - (threshold or 1.5) * iqr
                upper_bound = q3 + (threshold or 1.5) * iqr
                
                # 替换超出边界的值
                self.df.loc[self.df[column] < lower_bound, column] = lower_bound
                self.df.loc[self.df[column] > upper_bound, column] = upper_bound
            
            elif method == 'zscore':
                mean_val = self.df[column].mean()
                std_val = self.df[column].std()
                lower_bound = mean_val - (threshold or 3.0) * std_val
                upper_bound = mean_val + (threshold or 3.0) * std_val
                
                # 替换超出边界的值
                self.df.loc[self.df[column] < lower_bound, column] = lower_bound
                self.df.loc[self.df[column] > upper_bound, column] = upper_bound
        
        # 记录清洗操作
        self.cleaning_log.append({
            'operation': 'handle_outliers',
            'column': column,
            'method': method,
            'strategy': strategy,
            'outliers_detected': outliers_count,
            'timestamp': datetime.now().isoformat()
        })
        
        return self.df
    
    def standardize_text(self, column, operations):
        """
        标准化文本数据
        
        Args:
            column: 要处理的列名
            operations: 要执行的操作列表
                       ('lower', 'upper', 'strip', 'remove_punct', 'remove_numbers', 'remove_extra_spaces')
        """
        original_data = self.df[column].copy()
        
        for operation in operations:
            if operation == 'lower':
                self.df[column] = self.df[column].astype(str).str.lower()
            elif operation == 'upper':
                self.df[column] = self.df[column].astype(str).str.upper()
            elif operation == 'strip':
                self.df[column] = self.df[column].astype(str).str.strip()
            elif operation == 'remove_punct':
                self.df[column] = self.df[column].astype(str).str.replace(r'[^\w\s]', '', regex=True)
            elif operation == 'remove_numbers':
                self.df[column] = self.df[column].astype(str).str.replace(r'\d+', '', regex=True)
            elif operation == 'remove_extra_spaces':
                self.df[column] = self.df[column].astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()
        
        # 记录清洗操作
        self.cleaning_log.append({
            'operation': 'standardize_text',
            'column': column,
            'operations': operations,
            'timestamp': datetime.now().isoformat()
        })
        
        return self.df
    
    def standardize_data_format(self, column, target_format):
        """
        标准化数据格式
        
        Args:
            column: 要处理的列名
            target_format: 目标格式 ('email', 'phone', 'date', 'number')
        """
        conversion_count = 0
        error_count = 0
        
        if target_format == 'email':
            # 标准化邮箱格式
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            valid_emails = self.df[column].astype(str).str.match(email_pattern)
            conversion_count = valid_emails.sum()
            error_count = len(self.df) - conversion_count
        
        elif target_format == 'phone':
            # 标准化手机号格式（中国大陆）
            self.df[column] = self.df[column].astype(str).str.replace(r'\D', '', regex=True)
            self.df[column] = self.df[column].str.slice(-11)
            
            phone_pattern = r'^1[3-9]\d{9}$'
            valid_phones = self.df[column].str.match(phone_pattern)
            conversion_count = valid_phones.sum()
            error_count = len(self.df) - conversion_count
        
        elif target_format == 'date':
            try:
                self.df[column] = pd.to_datetime(self.df[column], errors='coerce')
                self.df[column] = self.df[column].dt.strftime('%Y-%m-%d')
                conversion_count = self.df[column].notna().sum()
                error_count = len(self.df) - conversion_count
            except Exception as e:
                print(f"日期标准化错误: {str(e)}")
        
        elif target_format == 'number':
            try:
                self.df[column] = pd.to_numeric(self.df[column], errors='coerce')
                conversion_count = self.df[column].notna().sum()
                error_count = len(self.df) - conversion_count
            except Exception as e:
                print(f"数字标准化错误: {str(e)}")
        
        # 记录清洗操作
        self.cleaning_log.append({
            'operation': 'standardize_data_format',
            'column': column,
            'target_format': target_format,
            'conversions': conversion_count,
            'errors': error_count,
            'timestamp': datetime.now().isoformat()
        })
        
        return self.df
    
    def get_cleaning_summary(self):
        """获取清洗摘要"""
        return {
            'original_shape': self.original_df.shape,
            'current_shape': self.df.shape,
            'cleaning_operations': len(self.cleaning_log),
            'operations_log': self.cleaning_log
        }
    
    def visualize_changes(self, figsize=(15, 10), save_path=None):
        """可视化清洗前后的变化"""
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        fig.suptitle('数据清洗前后对比', fontsize=16)
        
        # 缺失值对比
        ax = axes[0, 0]
        original_missing = self.original_df.isnull().sum()
        current_missing = self.df.isnull().sum()
        
        df_missing = pd.DataFrame({
            '原始数据': original_missing,
            '清洗后': current_missing
        })
        
        df_missing.plot(kind='bar', ax=ax)
        ax.set_title('缺失值对比')
        ax.set_ylabel('缺失值数量')
        
        # 数据分布对比（选择第一个数值型列）
        ax = axes[0, 1]
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            col = numeric_cols[0]
            self.original_df[col].hist(ax=ax, alpha=0.7, label='原始数据', bins=20)
            self.df[col].hist(ax=ax, alpha=0.7, label='清洗后', bins=20)
            ax.set_title(f'{col} 分布对比')
            ax.legend()
        else:
            ax.text(0.5, 0.5, '无数值型数据', horizontalalignment='center', verticalalignment='center')
            ax.set_title('数据分布对比')
        
        # 数据类型变化
        ax = axes[1, 0]
        original_dtypes = self.original_df.dtypes.value_counts()
        current_dtypes = self.df.dtypes.value_counts()
        
        dtype_df = pd.DataFrame({
            '原始数据': original_dtypes,
            '清洗后': current_dtypes
        })
        
        dtype_df.plot(kind='bar', ax=ax)
        ax.set_title('数据类型变化')
        ax.set_ylabel('列数')
        
        # 数据行数变化
        ax = axes[1, 1]
        rows_before = self.original_df.shape[0]
        rows_after = self.df.shape[0]
        
        ax.bar(['清洗前', '清洗后'], [rows_before, rows_after], color=['blue', 'green'])
        ax.set_title(f'数据行数变化: {rows_before} → {rows_after}')
        ax.set_ylabel('行数')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()


# 示例使用
if __name__ == "__main__":
    # 创建示例数据
    data = {
        'name': ['张三', '李四', '王五', '赵六', '钱七', None, '孙八', '周九', '吴十', '郑十一'],
        'email': [
            'zhangsan@example.com',
            'LISI@example.com',  # 大小写不一致
            'wangwu@example.com',
            'zhaoliu@example.com',
            'qianqi@example.com',
            'invalid-email',  # 无效邮箱
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
            'invalid-phone',  # 无效手机号
            '13312345678',
            '13212345678',
            '13112345678',
            'invalid-phone'  # 重复的无效手机号
        ],
        'age': [25, 30, 35, 40, 45, 50, 55, 60, 65, 200],  # 200是异常值
        'salary': [5000, 6000, None, 8000, 9000, 10000, 11000, 12000, None, 15000]
    }
    
    df = pd.DataFrame(data)
    
    print("原始数据:")
    print(df)
    print("\n原始数据信息:")
    print(df.info())
    
    # 创建清洗器
    cleaner = DataCleaner(df)
    
    # 1. 处理缺失值
    print("\n1. 处理缺失值...")
    cleaner.handle_missing_values(strategy='mode', columns=['name'])
    cleaner.handle_missing_values(strategy='mean', columns=['salary'])
    
    # 2. 处理重复数据
    print("\n2. 删除重复数据...")
    cleaner.remove_duplicates()
    
    # 3. 处理异常值
    print("\n3. 处理异常值...")
    cleaner.handle_outliers('age', method='iqr', strategy='cap', threshold=1.5)
    
    # 4. 标准化文本数据
    print("\n4. 标准化邮箱格式...")
    cleaner.standardize_text('email', ['lower', 'strip'])
    
    # 5. 标准化数据格式
    print("\n5. 标准化手机号格式...")
    cleaner.standardize_data_format('phone', 'phone')
    
    # 获取清洗后的数据
    cleaned_df = cleaner.df
    
    print("\n清洗后的数据:")
    print(cleaned_df)
    print("\n清洗后数据信息:")
    print(cleaned_df.info())
    
    # 显示清洗摘要
    summary = cleaner.get_cleaning_summary()
    print("\n清洗摘要:")
    print(f"原始数据形状: {summary['original_shape']}")
    print(f"清洗后数据形状: {summary['current_shape']}")
    print(f"执行的清洗操作数: {summary['cleaning_operations']}")
    
    # 可视化清洗效果
    cleaner.visualize_changes(save_path='data_cleaning_comparison.png')
    
    print("\n数据清洗完成！")
    print("可视化图表已保存到: data_cleaning_comparison.png")