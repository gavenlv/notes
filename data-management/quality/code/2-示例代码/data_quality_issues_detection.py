#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据质量问题识别与分类演示代码
本代码用于演示如何识别和分类不同类型的数据质量问题

作者: Assistant
日期: 2025-11-15
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re

def create_sample_order_data():
    """
    创建包含各种数据质量问题的电商订单示例数据
    """
    data = {
        'order_id': ['ORD001', 'ORD002', 'ORD003', 'ORD004', 'ORD005', 
                     'ORD006', 'ORD007', 'ORD008', 'ORD009', 'ORD010'],
        'customer_id': ['C001', 'C002', 'C003', 'C004', 'C005', 
                        'C001', 'C006', 'C007', 'C008', 'C009'],
        'product_name': ['iPhone 14', 'Samsung Galaxy S23', 'iPad Pro', 
                         'MacBook Air', '', 'iPhone 14 Pro', 'AirPods Pro', 
                         'Apple Watch', 'iPhone 14', 'Surface Pro'],
        'quantity': [1, 2, -1, 1, 3, 1, 2, 1, 1, 1],  # 注意：有一个负数
        'unit_price': [6999.00, 5699.00, 8999.00, 9999.00, 7999.00, 
                       8999.00, 1899.00, 2999.00, 6999.00, 8888.00],
        'total_price': [6999.00, 11398.00, -8999.00, 10000.00, 23997.00, 
                        8999.00, 3798.00, 2999.00, 6999.00, 8888.00],  # 注意：计算错误和负数
        'order_date': [
            '2023-01-15', '2023-02-20', '2023-03-10', '2024-12-31',  # 未来日期
            '2023-04-05', '2023-01-15', '2023-05-12', '2023-06-18',
            '2022-01-01', '2023-07-22'  # 过期日期
        ],
        'customer_address': [
            '北京市朝阳区xxx街道', '上海市浦东新区yyy路', '',  # 缺失地址
            '广州市天河区zzz大道', '深圳市南山区aaa路', '北京市朝阳区xxx街道',  # 重复地址
            '杭州市西湖区bbb街', '南京市鼓楼区ccc巷', '成都市锦江区ddd路',
            '武汉市江汉区eee街'
        ]
    }
    
    df = pd.DataFrame(data)
    return df

def detect_missing_values(df):
    """
    识别缺失值问题
    """
    print("=== 缺失值问题识别 ===")
    missing_data = df.isnull().sum()
    missing_data_percent = 100 * df.isnull().sum() / len(df)
    
    missing_summary = pd.DataFrame({
        'Missing Count': missing_data,
        'Percentage': missing_data_percent
    })
    
    print(missing_summary[missing_summary['Missing Count'] > 0])
    
    # 检查空字符串
    empty_string_cols = []
    for col in df.columns:
        empty_count = (df[col] == '').sum()
        if empty_count > 0:
            empty_string_cols.append((col, empty_count))
    
    if empty_string_cols:
        print("\n空字符串问题:")
        for col, count in empty_string_cols:
            print(f"  {col}: {count} 个空字符串")
    
    print()

def detect_format_inconsistencies(df):
    """
    识别格式不一致问题
    """
    print("=== 格式不一致问题识别 ===")
    
    # 检查日期格式一致性
    date_patterns = {}
    for date_str in df['order_date']:
        pattern = re.sub(r'\d', 'D', date_str)
        date_patterns[pattern] = date_patterns.get(pattern, 0) + 1
    
    if len(date_patterns) > 1:
        print("发现多种日期格式:")
        for pattern, count in date_patterns.items():
            print(f"  {pattern}: {count} 条记录")
    
    # 检查产品名称大小写一致性
    product_names = df['product_name'].dropna()
    uppercase_count = sum(1 for name in product_names if name.isupper())
    lowercase_count = sum(1 for name in product_names if name.islower())
    mixed_case_count = len(product_names) - uppercase_count - lowercase_count
    
    print(f"\n产品名称大小写情况:")
    print(f"  全大写: {uppercase_count}")
    print(f"  全小写: {lowercase_count}")
    print(f"  混合大小写: {mixed_case_count}")
    
    print()

def detect_duplicate_data(df):
    """
    识别重复数据问题
    """
    print("=== 重复数据问题识别 ===")
    
    # 完全重复的行
    duplicates = df[df.duplicated(keep=False)]
    if not duplicates.empty:
        print("完全重复的记录:")
        print(duplicates)
    else:
        print("未发现完全重复的记录")
    
    # 基于特定列的重复（如订单ID应该唯一）
    order_id_duplicates = df[df.duplicated('order_id', keep=False)]
    if not order_id_duplicates.empty:
        print("\n重复的订单ID:")
        print(order_id_duplicates[['order_id']])
    
    # 基于业务逻辑的重复（如相同客户在同一时间购买相同商品）
    business_duplicates = df[df.duplicated(['customer_id', 'product_name', 'order_date'], keep=False)]
    if not business_duplicates.empty:
        print("\n业务逻辑重复（相同客户同一天购买相同商品）:")
        print(business_duplicates[['customer_id', 'product_name', 'order_date']])
    
    print()

def detect_data_conflicts(df):
    """
    识别数据冲突问题
    """
    print("=== 数据冲突问题识别 ===")
    
    # 检查总价计算是否正确
    df['calculated_total'] = df['quantity'] * df['unit_price']
    df['price_difference'] = abs(df['total_price'] - df['calculated_total'])
    
    incorrect_pricing = df[df['price_difference'] > 0.01]  # 允许微小的浮点数误差
    if not incorrect_pricing.empty:
        print("总价计算错误的记录:")
        print(incorrect_pricing[['order_id', 'quantity', 'unit_price', 'total_price', 'calculated_total']])
    
    # 检查负数问题
    negative_quantity = df[df['quantity'] < 0]
    if not negative_quantity.empty:
        print("\n数量为负数的记录（可能是退货但未正确标识）:")
        print(negative_quantity[['order_id', 'product_name', 'quantity']])
    
    negative_price = df[df['total_price'] < 0]
    if not negative_price.empty:
        print("\n总价为负数的记录:")
        print(negative_price[['order_id', 'product_name', 'total_price']])
    
    print()

def detect_outliers(df):
    """
    识别离群值问题
    """
    print("=== 离群值问题识别 ===")
    
    # 使用IQR方法检测数量的离群值
    Q1 = df['quantity'].quantile(0.25)
    Q3 = df['quantity'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = df[(df['quantity'] < lower_bound) | (df['quantity'] > upper_bound)]
    if not outliers.empty:
        print(f"数量离群值（正常范围: {lower_bound:.2f} - {upper_bound:.2f}）:")
        print(outliers[['order_id', 'product_name', 'quantity']])
    
    # 检查异常日期
    df['order_date_parsed'] = pd.to_datetime(df['order_date'], errors='coerce')
    today = datetime.today()
    future_dates = df[df['order_date_parsed'] > today]
    if not future_dates.empty:
        print("\n未来日期的订单:")
        print(future_dates[['order_id', 'order_date']])
    
    old_dates = df[df['order_date_parsed'] < (today - timedelta(days=365*2))]
    if not old_dates.empty:
        print("\n两年前的旧订单:")
        print(old_dates[['order_id', 'order_date']])
    
    print()

def classify_issues(df):
    """
    对识别出的问题进行分类
    """
    print("=== 数据质量问题分类 ===")
    
    # 创建问题分类统计
    issue_categories = {
        '准确性问题': 0,
        '完整性问题': 0,
        '一致性问题': 0,
        '及时性问题': 0,
        '唯一性问题': 0,
        '有效性问题': 0
    }
    
    # 统计各类问题
    # 准确性问题：总价计算错误、负数价格
    df['calculated_total'] = df['quantity'] * df['unit_price']
    df['price_difference'] = abs(df['total_price'] - df['calculated_total'])
    accuracy_issues = len(df[df['price_difference'] > 0.01]) + len(df[df['total_price'] < 0])
    issue_categories['准确性问题'] = accuracy_issues
    
    # 完整性问题：缺失值
    completeness_issues = df.isnull().sum().sum() + sum((df[col] == '').sum() for col in df.columns)
    issue_categories['完整性问题'] = completeness_issues
    
    # 一致性问题：格式不一致
    date_patterns = {}
    for date_str in df['order_date']:
        pattern = re.sub(r'\d', 'D', date_str)
        date_patterns[pattern] = date_patterns.get(pattern, 0) + 1
    consistency_issues = len(date_patterns) - 1 if len(date_patterns) > 1 else 0
    issue_categories['一致性问题'] = consistency_issues
    
    # 及时性问题：未来日期、过期日期
    df['order_date_parsed'] = pd.to_datetime(df['order_date'], errors='coerce')
    today = datetime.today()
    timeliness_issues = len(df[df['order_date_parsed'] > today]) + len(df[df['order_date_parsed'] < (today - timedelta(days=365*2))])
    issue_categories['及时性问题'] = timeliness_issues
    
    # 唯一性问题：重复数据
    uniqueness_issues = len(df[df.duplicated(keep=False)])
    issue_categories['唯一性问题'] = uniqueness_issues
    
    # 有效性问题：负数数量
    validity_issues = len(df[df['quantity'] < 0])
    issue_categories['有效性问题'] = validity_issues
    
    # 输出分类统计
    print("数据质量问题分类统计:")
    for category, count in issue_categories.items():
        print(f"  {category}: {count} 个问题")
    
    print()

def main():
    """
    主函数：演示数据质量问题识别与分类过程
    """
    print("数据质量问题识别与分类演示")
    print("=" * 50)
    
    # 创建示例数据
    df = create_sample_order_data()
    print("原始订单数据:")
    print(df)
    print("\n" + "=" * 50)
    
    # 执行各项数据质量问题识别
    detect_missing_values(df)
    detect_format_inconsistencies(df)
    detect_duplicate_data(df)
    detect_data_conflicts(df)
    detect_outliers(df)
    classify_issues(df)
    
    print("数据质量问题识别与分类完成！")
    print("\n总结:")
    print("通过以上分析，我们识别出了以下几类数据质量问题:")
    print("1. 缺失值问题：部分订单缺少产品名称或客户地址")
    print("2. 格式不一致问题：日期格式虽然看起来一致，但我们演示了如何检查")
    print("3. 重复数据问题：完全重复的记录和业务逻辑重复")
    print("4. 数据冲突问题：总价计算错误、负数数量和价格")
    print("5. 离群值问题：未来日期订单和过期订单")
    print("\n这些识别方法可以应用于实际的数据质量管理工作中。")

if __name__ == "__main__":
    main()