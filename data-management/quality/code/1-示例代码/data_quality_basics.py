#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据质量基础概念演示代码
本代码用于演示数据质量的几个核心维度：
1. 准确性 (Accuracy)
2. 完整性 (Completeness)
3. 一致性 (Consistency)
4. 唯一性 (Uniqueness)
5. 有效性 (Validity)
6. 及时性 (Timeliness)

作者: Assistant
日期: 2025-11-15
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_sample_data():
    """
    创建示例数据集，包含各种数据质量问题
    """
    # 创建一个包含数据质量问题的客户数据集
    data = {
        'customer_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'name': ['张三', '李四', '王五', '赵六', '', '钱七', '孙八', '周九', '吴十', '郑十一'],
        'email': ['zhangsan@email.com', 'lisi.email.com', 'wangwu@email.com', 
                  'zhaoliu@email.com', 'wu@email.com', 'qianqi@email.com',
                  'suna@email.com', 'zhoujiu@email.com', 'wushi@email.com',
                  'zhengshiyi@email.com'],
        'age': [25, -5, 30, 150, 28, 35, 42, 29, 33, 27],
        'phone': ['13800138000', '13900139000', '13700137000', '13600136000',
                  '13500135000', '13400134000', '13300133000', '13200132000',
                  '13100131000', '13800138000'],  # 注意：这里有重复电话号码
        'city': ['北京', '上海', '广州', '深圳', '杭州', '南京', '成都', '武汉', '西安', '重庆'],
        'registration_date': [
            datetime.now() - timedelta(days=30),
            datetime.now() - timedelta(days=25),
            datetime.now() - timedelta(days=20),
            datetime.now() - timedelta(days=15),
            datetime.now() - timedelta(days=10),
            datetime.now() - timedelta(days=5),
            datetime.now() - timedelta(days=100),  # 较旧的数据
            datetime.now() - timedelta(days=8),
            datetime.now() - timedelta(days=7),
            datetime.now() - timedelta(days=30)   # 与第一个客户重复日期
        ]
    }
    
    df = pd.DataFrame(data)
    return df

def check_accuracy(df):
    """
    检查数据准确性
    示例：年龄应该在合理范围内（0-120岁）
    """
    print("=== 数据准确性检查 ===")
    invalid_age = df[(df['age'] < 0) | (df['age'] > 120)]
    if not invalid_age.empty:
        print("发现年龄异常的记录:")
        print(invalid_age[['customer_id', 'name', 'age']])
    else:
        print("所有年龄数据都在合理范围内")
    print()

def check_completeness(df):
    """
    检查数据完整性
    示例：检查必填字段是否为空
    """
    print("=== 数据完整性检查 ===")
    # 检查姓名字段是否为空
    missing_names = df[df['name'].isnull() | (df['name'] == '')]
    if not missing_names.empty:
        print("发现姓名缺失的记录:")
        print(missing_names[['customer_id', 'name']])
    else:
        print("所有姓名数据完整")
    print()

def check_consistency(df):
    """
    检查数据一致性
    示例：检查邮箱格式是否一致
    """
    print("=== 数据一致性检查 ===")
    # 检查邮箱格式
    invalid_emails = df[~df['email'].str.contains('@', na=False)]
    if not invalid_emails.empty:
        print("发现邮箱格式不正确的记录:")
        print(invalid_emails[['customer_id', 'name', 'email']])
    else:
        print("所有邮箱格式正确")
    print()

def check_uniqueness(df):
    """
    检查数据唯一性
    示例：检查是否有重复的电话号码
    """
    print("=== 数据唯一性检查 ===")
    # 检查重复的电话号码
    duplicate_phones = df[df.duplicated('phone', keep=False)]
    if not duplicate_phones.empty:
        print("发现重复的电话号码:")
        print(duplicate_phones[['customer_id', 'name', 'phone']])
    else:
        print("所有电话号码都是唯一的")
    print()

def check_validity(df):
    """
    检查数据有效性
    示例：检查年龄是否为有效数值
    """
    print("=== 数据有效性检查 ===")
    # 检查年龄是否为负数
    negative_ages = df[df['age'] < 0]
    if not negative_ages.empty:
        print("发现年龄为负数的记录:")
        print(negative_ages[['customer_id', 'name', 'age']])
    else:
        print("所有年龄数据有效")
    print()

def check_timeliness(df):
    """
    检查数据及时性
    示例：检查是否有超过90天未更新的记录
    """
    print("=== 数据及时性检查 ===")
    # 假设超过90天未更新的数据为过时数据
    ninety_days_ago = datetime.now() - timedelta(days=90)
    outdated_records = df[df['registration_date'] < ninety_days_ago]
    if not outdated_records.empty:
        print("发现可能过时的记录:")
        print(outdated_records[['customer_id', 'name', 'registration_date']])
    else:
        print("所有记录都是近期的")
    print()

def main():
    """
    主函数：演示数据质量检查过程
    """
    print("数据质量管理基础概念演示")
    print("=" * 50)
    
    # 创建示例数据
    df = create_sample_data()
    print("原始数据:")
    print(df)
    print("\n" + "=" * 50)
    
    # 执行各项数据质量检查
    check_accuracy(df)
    check_completeness(df)
    check_consistency(df)
    check_uniqueness(df)
    check_validity(df)
    check_timeliness(df)
    
    print("数据质量检查完成！")
    print("\n总结:")
    print("通过以上检查，我们可以发现数据中存在的各种质量问题:")
    print("1. 准确性问题：年龄为-5岁和150岁的不合理值")
    print("2. 完整性问题：客户姓名为空")
    print("3. 一致性问题：邮箱格式不正确")
    print("4. 唯一性问题：重复的电话号码")
    print("5. 有效性问题：负数年龄")
    print("6. 及时性问题：超过90天未更新的记录")

if __name__ == "__main__":
    main()