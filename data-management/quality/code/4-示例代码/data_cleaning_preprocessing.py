#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据清洗与预处理技术示例代码
本脚本演示了各种数据清洗和预处理技术的实现方法
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
import matplotlib.pyplot as plt
import seaborn as sns


class DataCleaner:
    """通用数据清洗器"""
    
    def __init__(self, df):
        """
        初始化数据清洗器
        
        Args:
            df (pandas.DataFrame): 待清洗的数据框
        """
        self.df = df.copy()
        self.original_shape = df.shape
        self.cleaning_log = []
    
    def remove_duplicates(self, subset=None, keep='first'):
        """
        删除重复数据
        
        Args:
            subset (list, optional): 用于判断重复的列名列表
            keep (str): 保留策略 ('first', 'last', False)
            
        Returns:
            DataCleaner: 返回自身以支持链式调用
        """
        before_count = len(self.df)
        self.df = self.df.drop_duplicates(subset=subset, keep=keep)
        after_count = len(self.df)
        removed_count = before_count - after_count
        
        log_msg = f"删除重复数据: {removed_count} 条"
        if subset:
            log_msg += f" (基于列: {subset})"
        self.cleaning_log.append(log_msg)
        print(log_msg)
        
        return self
    
    def handle_missing_values(self, strategy='auto', columns=None):
        """
        处理缺失值
        
        Args:
            strategy (str): 处理策略 ('mean', 'median', 'mode', 'drop', 'forward', 'backward', 'auto')
            columns (list, optional): 要处理的列名列表
            
        Returns:
            DataCleaner: 返回自身以支持链式调用
        """
        if columns is None:
            columns = self.df.columns.tolist()
        
        for col in columns:
            missing_count = self.df[col].isnull().sum()
            if missing_count == 0:
                continue
                
            if strategy == 'auto':
                # 根据数据类型自动选择策略
                if self.df[col].dtype in ['int64', 'float64']:
                    strategy_use = 'mean'
                else:
                    strategy_use = 'mode'
            else:
                strategy_use = strategy
            
            if strategy_use == 'mean':
                fill_value = self.df[col].mean()
                self.df[col].fillna(fill_value, inplace=True)
                self.cleaning_log.append(f"用均值填充 {col} 的缺失值: {missing_count} 条")
                
            elif strategy_use == 'median':
                fill_value = self.df[col].median()
                self.df[col].fillna(fill_value, inplace=True)
                self.cleaning_log.append(f"用中位数填充 {col} 的缺失值: {missing_count} 条")
                
            elif strategy_use == 'mode':
                fill_value = self.df[col].mode()
                if len(fill_value) > 0:
                    self.df[col].fillna(fill_value[0], inplace=True)
                    self.cleaning_log.append(f"用众数填充 {col} 的缺失值: {missing_count} 条")
                    
            elif strategy_use == 'drop':
                self.df = self.df.dropna(subset=[col])
                self.cleaning_log.append(f"删除 {col} 的缺失值记录: {missing_count} 条")
                
            elif strategy_use == 'forward':
                self.df[col].fillna(method='ffill', inplace=True)
                self.cleaning_log.append(f"用前向填充处理 {col} 的缺失值: {missing_count} 条")
                
            elif strategy_use == 'backward':
                self.df[col].fillna(method='bfill', inplace=True)
                self.cleaning_log.append(f"用后向填充处理 {col} 的缺失值: {missing_count} 条")
            
            print(f"处理 {col} 的缺失值: {missing_count} 条 ({strategy_use})")
        
        return self
    
    def handle_outliers(self, columns=None, method='iqr', factor=1.5):
        """
        处理异常值
        
        Args:
            columns (list, optional): 要处理的列名列表
            method (str): 处理方法 ('iqr', 'zscore')
            factor (float): 异常值判定因子
            
        Returns:
            DataCleaner: 返回自身以支持链式调用
        """
        if columns is None:
            # 自动选择数值型列
            columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        for col in columns:
            if self.df[col].dtype not in ['int64', 'float64']:
                continue
                
            outliers_count = 0
            
            if method == 'iqr':
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - factor * IQR
                upper_bound = Q3 + factor * IQR
                
                # 识别异常值
                outlier_mask = (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
                outliers_count = outlier_mask.sum()
                
                # 用边界值替换异常值
                self.df.loc[self.df[col] < lower_bound, col] = lower_bound
                self.df.loc[self.df[col] > upper_bound, col] = upper_bound
                
            elif method == 'zscore':
                z_scores = np.abs((self.df[col] - self.df[col].mean()) / self.df[col].std())
                outlier_mask = z_scores > factor
                outliers_count = outlier_mask.sum()
                
                # 用均值替换异常值
                mean_value = self.df[col].mean()
                self.df.loc[outlier_mask, col] = mean_value
            
            if outliers_count > 0:
                self.cleaning_log.append(f"处理 {col} 的异常值: {outliers_count} 条 ({method}方法)")
                print(f"处理 {col} 的异常值: {outliers_count} 条 ({method}方法)")
        
        return self
    
    def standardize_text_format(self, columns=None, operations=None):
        """
        标准化文本格式
        
        Args:
            columns (list, optional): 要处理的列名列表
            operations (list): 要执行的操作列表 ('lower', 'strip', 'remove_spaces')
            
        Returns:
            DataCleaner: 返回自身以支持链式调用
        """
        if columns is None:
            # 自动选择字符串型列
            columns = self.df.select_dtypes(include=['object']).columns.tolist()
        
        if operations is None:
            operations = ['strip', 'lower']
        
        for col in columns:
            if self.df[col].dtype != 'object':
                continue
                
            original_series = self.df[col].copy()
            
            for op in operations:
                if op == 'lower':
                    self.df[col] = self.df[col].astype(str).str.lower()
                elif op == 'strip':
                    self.df[col] = self.df[col].astype(str).str.strip()
                elif op == 'remove_spaces':
                    self.df[col] = self.df[col].astype(str).str.replace(r'\s+', ' ', regex=True)
            
            # 计算发生变化的记录数
            changed_count = (original_series.astype(str) != self.df[col].astype(str)).sum()
            if changed_count > 0:
                self.cleaning_log.append(f"标准化 {col} 格式: {changed_count} 条记录发生变化")
                print(f"标准化 {col} 格式: {changed_count} 条记录发生变化")
        
        return self
    
    def validate_email_format(self, email_column):
        """
        验证并清理邮箱格式
        
        Args:
            email_column (str): 邮箱列名
            
        Returns:
            DataCleaner: 返回自身以支持链式调用
        """
        if email_column not in self.df.columns:
            print(f"警告: 列 {email_column} 不存在")
            return self
        
        # 定义邮箱正则表达式
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        # 标记有效的邮箱
        valid_emails = self.df[email_column].astype(str).str.match(email_pattern, na=False)
        invalid_count = (~valid_emails).sum()
        
        if invalid_count > 0:
            # 将无效邮箱替换为NaN
            self.df.loc[~valid_emails, email_column] = np.nan
            self.cleaning_log.append(f"清理无效邮箱: {invalid_count} 条")
            print(f"清理无效邮箱: {invalid_count} 条")
        
        return self
    
    def get_cleaned_data(self):
        """
        获取清洗后的数据
        
        Returns:
            pandas.DataFrame: 清洗后的数据框
        """
        return self.df
    
    def get_cleaning_log(self):
        """
        获取清洗日志
        
        Returns:
            list: 清洗操作日志列表
        """
        return self.cleaning_log
    
    def print_summary(self):
        """打印清洗摘要"""
        print("\n=== 数据清洗摘要 ===")
        print(f"原始数据形状: {self.original_shape}")
        print(f"清洗后数据形状: {self.df.shape}")
        print(f"删除记录数: {self.original_shape[0] - self.df.shape[0]}")
        print(f"清洗操作日志:")
        for i, log in enumerate(self.cleaning_log, 1):
            print(f"  {i}. {log}")


class DataPreprocessor:
    """数据预处理器"""
    
    def __init__(self, df):
        """
        初始化数据预处理器
        
        Args:
            df (pandas.DataFrame): 待预处理的数据框
        """
        self.df = df.copy()
        self.preprocess_log = []
    
    def normalize_data(self, columns=None, method='minmax'):
        """
        数据标准化
        
        Args:
            columns (list, optional): 要标准化的列名列表
            method (str): 标准化方法 ('minmax', 'zscore')
            
        Returns:
            DataPreprocessor: 返回自身以支持链式调用
        """
        if columns is None:
            # 自动选择数值型列
            columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        if method == 'minmax':
            scaler = MinMaxScaler()
            self.df[columns] = scaler.fit_transform(self.df[columns])
            self.preprocess_log.append(f"Min-Max标准化: {len(columns)} 列")
            
        elif method == 'zscore':
            scaler = StandardScaler()
            self.df[columns] = scaler.fit_transform(self.df[columns])
            self.preprocess_log.append(f"Z-Score标准化: {len(columns)} 列")
        
        print(f"完成 {method} 标准化: {len(columns)} 列")
        return self
    
    def encode_categorical(self, columns=None, method='onehot'):
        """
        分类变量编码
        
        Args:
            columns (list, optional): 要编码的列名列表
            method (str): 编码方法 ('label', 'onehot')
            
        Returns:
            DataPreprocessor: 返回自身以支持链式调用
        """
        if columns is None:
            # 自动选择分类列
            columns = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if method == 'label':
            for col in columns:
                le = LabelEncoder()
                self.df[col] = le.fit_transform(self.df[col].astype(str))
                self.preprocess_log.append(f"标签编码: {col}")
                print(f"标签编码: {col}")
                
        elif method == 'onehot':
            # 使用pandas进行独热编码
            dummies = pd.get_dummies(self.df[columns], prefix=columns)
            # 删除原始列并添加编码后的列
            self.df = self.df.drop(columns=columns)
            self.df = pd.concat([self.df, dummies], axis=1)
            self.preprocess_log.append(f"独热编码: {len(columns)} 列 -> {len(dummies.columns)} 列")
            print(f"独热编码: {len(columns)} 列 -> {len(dummies.columns)} 列")
        
        return self
    
    def create_features(self, date_column, feature_names=None):
        """
        从日期列创建特征
        
        Args:
            date_column (str): 日期列名
            feature_names (dict, optional): 新特征名称映射
            
        Returns:
            DataPreprocessor: 返回自身以支持链式调用
        """
        if date_column not in self.df.columns:
            print(f"警告: 列 {date_column} 不存在")
            return self
        
        # 确保日期列是datetime类型
        if not pd.api.types.is_datetime64_any_dtype(self.df[date_column]):
            self.df[date_column] = pd.to_datetime(self.df[date_column])
        
        # 创建默认特征名称映射
        if feature_names is None:
            feature_names = {
                'year': f'{date_column}_year',
                'month': f'{date_column}_month',
                'day': f'{date_column}_day',
                'weekday': f'{date_column}_weekday',
                'quarter': f'{date_column}_quarter'
            }
        
        # 提取特征
        self.df[feature_names['year']] = self.df[date_column].dt.year
        self.df[feature_names['month']] = self.df[date_column].dt.month
        self.df[feature_names['day']] = self.df[date_column].dt.day
        self.df[feature_names['weekday']] = self.df[date_column].dt.weekday
        self.df[feature_names['quarter']] = self.df[date_column].dt.quarter
        
        self.preprocess_log.append(f"从 {date_column} 创建5个时间特征")
        print(f"从 {date_column} 创建5个时间特征")
        
        return self
    
    def get_processed_data(self):
        """
        获取预处理后的数据
        
        Returns:
            pandas.DataFrame: 预处理后的数据框
        """
        return self.df
    
    def get_preprocess_log(self):
        """
        获取预处理日志
        
        Returns:
            list: 预处理操作日志列表
        """
        return self.preprocess_log


def create_sample_data():
    """创建示例数据"""
    np.random.seed(42)
    
    # 创建基础数据
    n_records = 1000
    data = {
        'customer_id': np.random.randint(1000, 9999, n_records),
        'age': np.random.randint(18, 80, n_records),
        'income': np.random.normal(50000, 15000, n_records),
        'purchase_amount': np.random.exponential(100, n_records),
        'product_category': np.random.choice(['Electronics', 'Clothing', 'Books', 'Home'], n_records),
        'signup_date': pd.date_range('2020-01-01', periods=n_records, freq='D'),
        'email': [f'user{i}@example.com' for i in range(n_records)],
        'city': np.random.choice(['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen', 'Hangzhou'], n_records)
    }
    
    # 添加一些数据质量问题
    df = pd.DataFrame(data)
    
    # 1. 添加缺失值
    missing_indices = np.random.choice(n_records, 50, replace=False)
    df.loc[missing_indices[:25], 'age'] = np.nan
    df.loc[missing_indices[25:], 'income'] = np.nan
    
    # 2. 添加重复数据
    duplicate_indices = np.random.choice(n_records, 20, replace=False)
    for idx in duplicate_indices:
        if idx > 0:
            df.iloc[idx] = df.iloc[idx-1]
    
    # 3. 添加异常值
    outlier_indices = np.random.choice(n_records, 15, replace=False)
    df.loc[outlier_indices[:5], 'age'] = np.random.randint(100, 150, 5)  # 年龄异常
    df.loc[outlier_indices[5:10], 'income'] = np.random.uniform(200000, 500000, 5)  # 收入异常
    df.loc[outlier_indices[10:], 'purchase_amount'] = np.random.uniform(10000, 50000, 5)  # 购买金额异常
    
    # 4. 添加格式不一致的数据
    format_indices = np.random.choice(n_records, 30, replace=False)
    df.loc[format_indices[:10], 'email'] = df.loc[format_indices[:10], 'email'].str.upper()  # 大写邮箱
    df.loc[format_indices[10:20], 'email'] = df.loc[format_indices[10:20], 'email'].str.strip() + ' '  # 带空格的邮箱
    df.loc[format_indices[20:], 'city'] = df.loc[format_indices[20:], 'city'].str.upper()  # 大写城市
    
    # 5. 添加一些无效邮箱
    invalid_email_indices = np.random.choice(n_records, 10, replace=False)
    df.loc[invalid_email_indices, 'email'] = ['invalid.email', 'not-an-email', '@invalid.com', 'test@', 'user@@domain.com'] * 2
    
    return df


def visualize_data_quality(df, title="数据质量可视化"):
    """可视化数据质量"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(title, fontsize=16)
    
    # 1. 缺失值热力图
    sns.heatmap(df.isnull(), cbar=True, ax=axes[0,0])
    axes[0,0].set_title('缺失值分布')
    
    # 2. 数值列分布
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        df[numeric_cols].hist(bins=30, ax=axes[0,1])
        axes[0,1].set_title('数值列分布')
    
    # 3. 分类列分布
    categorical_cols = df.select_dtypes(include=['object']).columns
    if len(categorical_cols) > 0:
        col_to_plot = categorical_cols[0] if len(categorical_cols) > 0 else None
        if col_to_plot:
            df[col_to_plot].value_counts().plot(kind='bar', ax=axes[1,0])
            axes[1,0].set_title(f'{col_to_plot} 分布')
            axes[1,0].tick_params(axis='x', rotation=45)
    
    # 4. 数据类型统计
    dtypes_count = df.dtypes.value_counts()
    axes[1,1].pie(dtypes_count.values, labels=dtypes_count.index, autopct='%1.1f%%')
    axes[1,1].set_title('数据类型分布')
    
    plt.tight_layout()
    plt.show()


def main():
    """主函数"""
    print("=== 数据清洗与预处理技术示例 ===\n")
    
    # 1. 创建示例数据
    print("1. 创建示例数据...")
    df_raw = create_sample_data()
    print(f"原始数据形状: {df_raw.shape}")
    print("\n原始数据前5行:")
    print(df_raw.head())
    
    # 2. 数据质量可视化
    print("\n2. 原始数据质量可视化...")
    visualize_data_quality(df_raw, "原始数据质量")
    
    # 3. 数据清洗
    print("\n3. 开始数据清洗...")
    cleaner = DataCleaner(df_raw)
    
    # 执行清洗操作
    df_cleaned = (cleaner
                  .remove_duplicates()
                  .handle_missing_values(strategy='auto')
                  .handle_outliers(method='iqr')
                  .standardize_text_format(operations=['lower', 'strip'])
                  .validate_email_format('email')
                  .get_cleaned_data())
    
    # 打印清洗摘要
    cleaner.print_summary()
    
    # 4. 清洗后数据质量可视化
    print("\n4. 清洗后数据质量可视化...")
    visualize_data_quality(df_cleaned, "清洗后数据质量")
    
    # 5. 数据预处理
    print("\n5. 开始数据预处理...")
    preprocessor = DataPreprocessor(df_cleaned)
    
    # 执行预处理操作
    df_processed = (preprocessor
                    .normalize_data(method='minmax')
                    .encode_categorical(method='onehot')
                    .create_features('signup_date')
                    .get_processed_data())
    
    print(f"\n预处理后数据形状: {df_processed.shape}")
    print("\n预处理后数据前5行:")
    print(df_processed.head())
    
    print("\n预处理日志:")
    for i, log in enumerate(preprocessor.get_preprocess_log(), 1):
        print(f"  {i}. {log}")
    
    # 6. 构建自动化清洗管道
    print("\n6. 构建自动化清洗管道...")
    
    # 定义数值特征和分类特征
    numeric_features = ['age', 'income', 'purchase_amount']
    categorical_features = ['product_category', 'city']
    
    # 创建预处理管道
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', MinMaxScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse=False))
    ])
    
    # 组合预处理管道
    preprocessor_pipeline = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ]
    )
    
    # 应用管道（注意：这里我们使用原始数据作为示例）
    print("应用预处理管道到原始数据...")
    processed_array = preprocessor_pipeline.fit_transform(df_raw)
    print(f"管道处理后数组形状: {processed_array.shape}")
    
    print("\n=== 示例完成 ===")


if __name__ == "__main__":
    main()