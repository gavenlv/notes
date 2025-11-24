#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据匿名化工具
实现多种数据匿名化技术，包括哈希匿名化、令牌化、数据屏蔽、K-匿名化等
"""

import hashlib
import random
import pandas as pd
from faker import Faker
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import pairwise_distances
import warnings
warnings.filterwarnings('ignore')

class DataAnonymizer:
    """数据匿名化工具"""
    
    def __init__(self, locale='zh_CN'):
        """
        初始化匿名化工具
        
        Args:
            locale (str): 本地化设置
        """
        self.fake = Faker(locale)
        self.token_mapping = {}  # 令牌映射表
        self.hash_salts = {}      # 哈希盐值
    
    def hash_anonymization(self, data: Any, salt: str = None) -> str:
        """
        哈希匿名化
        
        Args:
            data: 要匿名化的数据
            salt: 盐值，增强安全性
            
        Returns:
            str: 哈希值
        """
        if pd.isna(data):
            return data
        
        data_str = str(data)
        
        # 如果没有提供盐值，生成一个随机盐值
        if salt is None:
            # 对于相同的数据，使用相同的盐值
            if data_str not in self.hash_salts:
                self.hash_salts[data_str] = str(random.randint(10000, 99999))
            salt = self.hash_salts[data_str]
        
        # 计算哈希值
        hash_value = hashlib.sha256(f"{data_str}{salt}".encode()).hexdigest()
        return hash_value
    
    def tokenization(self, data: Any, token_length: int = 12) -> str:
        """
        令牌化
        
        Args:
            data: 要令牌化的数据
            token_length: 令牌长度
            
        Returns:
            str: 令牌
        """
        if pd.isna(data):
            return data
        
        data_str = str(data)
        
        # 检查是否已存在映射
        if data_str in self.token_mapping:
            return self.token_mapping[data_str]
        
        # 生成新令牌
        token = f"TOKEN_{''.join([str(random.randint(0, 9)) for _ in range(token_length)])}"
        
        # 存储映射关系
        self.token_mapping[data_str] = token
        
        return token
    
    def masking(self, data: Any, mask_type: str = "partial", custom_params: Dict = None) -> str:
        """
        数据屏蔽
        
        Args:
            data: 要屏蔽的数据
            mask_type: 屏蔽类型 ('partial', 'full', 'email', 'phone', 'id_card')
            custom_params: 自定义参数
            
        Returns:
            str: 屏蔽后的数据
        """
        if pd.isna(data):
            return data
        
        data_str = str(data)
        
        if mask_type == "partial":
            # 部分屏蔽，保留前后几位
            params = custom_params or {'preserve_start': 2, 'preserve_end': 2}
            start = params.get('preserve_start', 2)
            end = params.get('preserve_end', 2)
            
            if len(data_str) <= start + end:
                return "*" * len(data_str)
            
            return data_str[:start] + "*" * (len(data_str) - start - end) + data_str[-end:]
        
        elif mask_type == "full":
            # 完全屏蔽
            return "*" * len(data_str)
        
        elif mask_type == "email":
            # 邮箱屏蔽
            if "@" not in data_str:
                return data_str
            
            username, domain = data_str.split("@", 1)
            
            # 保留用户名的首尾字符
            if len(username) <= 2:
                username_mask = "*" * len(username)
            else:
                username_mask = username[0] + "*" * (len(username) - 2) + username[-1]
            
            return f"{username_mask}@{domain}"
        
        elif mask_type == "phone":
            # 手机号屏蔽（中国大陆）
            digits = ''.join(filter(str.isdigit, data_str))
            
            if len(digits) < 7:
                return "*" * len(data_str)
            
            # 保留前3位和后4位
            masked_digits = digits[:3] + "*" * (len(digits) - 7) + digits[-4:]
            
            # 保持原始格式中的非数字字符
            result = ""
            digit_idx = 0
            for char in data_str:
                if char.isdigit():
                    if digit_idx < len(masked_digits):
                        result += masked_digits[digit_idx]
                        digit_idx += 1
                    else:
                        result += "*"
                else:
                    result += char
            
            return result
        
        elif mask_type == "id_card":
            # 身份证号屏蔽
            if len(data_str) < 8:
                return "*" * len(data_str)
            
            # 保留前6位和后4位
            return data_str[:6] + "*" * (len(data_str) - 10) + data_str[-4:]
        
        else:
            raise ValueError(f"不支持的屏蔽类型: {mask_type}")
    
    def fake_data_generation(self, data_type: str, original_data: Any = None) -> str:
        """
        生成虚假数据
        
        Args:
            data_type: 数据类型
            original_data: 原始数据（用于保持类型一致性）
            
        Returns:
            str: 虚假数据
        """
        if data_type == "name":
            return self.fake.name()
        elif data_type == "email":
            return self.fake.email()
        elif data_type == "phone":
            return self.fake.phone_number()
        elif data_type == "address":
            return self.fake.address()
        elif data_type == "company":
            return self.fake.company()
        elif data_type == "id_card":
            return self.fake.ssn()  # 简化处理
        elif data_type == "job":
            return self.fake.job()
        elif data_type == "date":
            return self.fake.date()
        elif data_type == "number" and original_data is not None:
            # 保持原始数字的类型和范围
            try:
                original_val = float(original_data)
                if original_val == int(original_val):
                    # 整数
                    return str(random.randint(int(original_val * 0.8), int(original_val * 1.2)))
                else:
                    # 浮点数
                    return str(round(original_val * random.uniform(0.8, 1.2), 2))
            except:
                return str(random.randint(1, 100))
        else:
            return self.fake.text(max_nb_chars=20)
    
    def k_anonymity(self, df: pd.DataFrame, quasi_identifiers: List[str], 
                    k: int = 3, generalization_method: str = "simple") -> pd.DataFrame:
        """
        K-匿名化
        
        Args:
            df: 原始数据框
            quasi_identifiers: 准标识符列表
            k: K值
            generalization_method: 泛化方法 ('simple', 'hierarchical')
            
        Returns:
            pd.DataFrame: K-匿名化后的数据框
        """
        anonymized_df = df.copy()
        
        if generalization_method == "simple":
            # 简单泛化方法
            for column in quasi_identifiers:
                if column not in anonymized_df.columns:
                    continue
                
                # 数值型数据：按区间分组
                if anonymized_df[column].dtype in ['int64', 'float64']:
                    min_val = anonymized_df[column].min()
                    max_val = anonymized_df[column].max()
                    
                    # 计算合适的分组数量
                    num_bins = max(5, len(anonymized_df) // k)
                    
                    # 创建分组标签
                    anonymized_df[column] = pd.cut(
                        anonymized_df[column],
                        bins=num_bins,
                        labels=[f"{column}_Bin_{i}" for i in range(num_bins)]
                    )
                
                # 文本型数据：保留前N个字符或转换为类别
                else:
                    # 计算每个唯一值的频次
                    value_counts = anonymized_df[column].value_counts()
                    
                    # 对于出现次数少的值进行泛化
                    rare_values = value_counts[value_counts < k].index.tolist()
                    
                    # 泛化稀疏值
                    for value in rare_values:
                        # 保留前N个字符并添加*
                        if len(str(value)) > 2:
                            anonymized_df.loc[anonymized_df[column] == value, column] = str(value)[:2] + "*"
                        else:
                            anonymized_df.loc[anonymized_df[column] == value, column] = "OTHER"
        
        elif generalization_method == "hierarchical":
            # 层次化泛化方法（简化实现）
            for column in quasi_identifiers:
                if column not in anonymized_df.columns:
                    continue
                
                # 基于列名的简单层次化规则
                if "age" in column.lower():
                    # 年龄：按年龄段分组
                    bins = [0, 18, 30, 45, 60, 100]
                    labels = ["0-18", "19-30", "31-45", "46-60", "60+"]
                    anonymized_df[column] = pd.cut(
                        anonymized_df[column],
                        bins=bins,
                        labels=labels,
                        right=False
                    )
                
                elif "zip" in column.lower() or "postcode" in column.lower():
                    # 邮编：只保留前几位
                    anonymized_df[column] = anonymized_df[column].astype(str).str[:3] + "***"
                
                elif "income" in column.lower() or "salary" in column.lower():
                    # 收入：按范围分组
                    anonymized_df[column] = pd.qcut(
                        anonymized_df[column],
                        q=5,
                        labels=["很低", "低", "中", "高", "很高"]
                    )
        
        # 检查K-匿名化是否满足
        value_counts = anonymized_df[quasi_identifiers].value_counts()
        violating_records = value_counts[value_counts < k].sum()
        
        print(f"K-匿名化结果：{len(anonymized_df)} 条记录中，{violating_records} 条违反 {k}-匿名性")
        
        return anonymized_df
    
    def l_diversity(self, df: pd.DataFrame, quasi_identifiers: List[str], 
                    sensitive_column: str, l: int = 3) -> pd.DataFrame:
        """
        L-多样性
        
        Args:
            df: 原始数据框
            quasi_identifiers: 准标识符列表
            sensitive_column: 敏感属性列
            l: L值
            
        Returns:
            pd.DataFrame: L-多样性处理后的数据框
        """
        # 首先进行K-匿名化
        k_anonymized_df = self.k_anonymity(df, quasi_identifiers, k=l)
        
        # 检查每个等价类的敏感属性多样性
        group_counts = k_anonymized_df.groupby(quasi_identifiers)[sensitive_column].nunique()
        
        # 找出不满足L-多样性的组
        violating_groups = group_counts[group_counts < l]
        
        if not violating_groups.empty:
            print(f"发现 {len(violating_groups)} 个组不满足 {l}-多样性")
            
            # 对不满足多样性的组进行泛化
            for group_values in violating_groups.index:
                if len(quasi_identifiers) == 1:
                    mask = k_anonymized_df[quasi_identifiers[0]] == group_values[0]
                else:
                    # 多维条件
                    mask = True
                    for i, qi in enumerate(quasi_identifiers):
                        mask = mask & (k_anonymized_df[qi] == group_values[i])
                
                # 进一步泛化准标识符
                for qi in quasi_identifiers:
                    if k_anonymized_df[qi].dtype == 'object':
                        # 对文本型准标识符进行更泛化处理
                        k_anonymized_df.loc[mask, qi] = "GENERALIZED"
        
        return k_anonymized_df
    
    def t_closeness(self, df: pd.DataFrame, quasi_identifiers: List[str], 
                   sensitive_column: str, t: float = 0.2) -> pd.DataFrame:
        """
        T-相近性
        
        Args:
            df: 原始数据框
            quasi_identifiers: 准标识符列表
            sensitive_column: 敏感属性列
            t: T值
            
        Returns:
            pd.DataFrame: T-相近性处理后的数据框
        """
        # 计算整体敏感属性的分布
        overall_distribution = df[sensitive_column].value_counts(normalize=True)
        
        # 首先进行K-匿名化
        k_anonymized_df = self.k_anonymity(df, quasi_identifiers, k=2)
        
        # 检查每个等价类的敏感属性分布
        groups = k_anonymized_df.groupby(quasi_identifiers)
        
        violating_groups = []
        
        for name, group in groups:
            # 计算组内敏感属性分布
            group_distribution = group[sensitive_column].value_counts(normalize=True)
            
            # 计算与整体分布的距离（使用总变差距离）
            distance = 0
            for value in overall_distribution.index:
                overall_prob = overall_distribution[value]
                group_prob = group_distribution.get(value, 0)
                distance += abs(overall_prob - group_prob)
            
            distance = distance / 2  # 总变差距离
            
            # 检查是否满足T-相近性
            if distance > t:
                violating_groups.append((name, distance))
        
        if violating_groups:
            print(f"发现 {len(violating_groups)} 个组不满足 {t}-相近性")
            
            # 对不满足的组进行进一步泛化
            for group_values, distance in violating_groups:
                if len(quasi_identifiers) == 1:
                    mask = k_anonymized_df[quasi_identifiers[0]] == group_values[0]
                else:
                    # 多维条件
                    mask = True
                    for i, qi in enumerate(quasi_identifiers):
                        mask = mask & (k_anonymized_df[qi] == group_values[i])
                
                # 进一步泛化准标识符
                for qi in quasi_identifiers:
                    if k_anonymized_df[qi].dtype == 'object':
                        # 对文本型准标识符进行更泛化处理
                        k_anonymized_df.loc[mask, qi] = "GENERALIZED_T"
        
        return k_anonymized_df
    
    def evaluate_anonymization_quality(self, original_df: pd.DataFrame, 
                                    anonymized_df: pd.DataFrame, 
                                    quasi_identifiers: List[str],
                                    sensitive_column: str = None) -> Dict:
        """
        评估匿名化质量
        
        Args:
            original_df: 原始数据框
            anonymized_df: 匿名化后的数据框
            quasi_identifiers: 准标识符列表
            sensitive_column: 敏感属性列
            
        Returns:
            Dict: 评估结果
        """
        evaluation_results = {
            'records_count': {
                'original': len(original_df),
                'anonymized': len(anonymized_df)
            },
            'k_anonymity': {},
            'l_diversity': {},
            'data_utility': {},
            'reidentification_risk': {}
        }
        
        # 评估K-匿名性
        if quasi_identifiers:
            value_counts = anonymized_df[quasi_identifiers].value_counts()
            evaluation_results['k_anonymity'] = {
                'min_group_size': value_counts.min(),
                'max_group_size': value_counts.max(),
                'mean_group_size': value_counts.mean(),
                'groups_below_3': (value_counts < 3).sum(),
                'groups_below_5': (value_counts < 5).sum()
            }
        
        # 评估L-多样性
        if sensitive_column and quasi_identifiers:
            diversity_counts = anonymized_df.groupby(quasi_identifiers)[sensitive_column].nunique()
            evaluation_results['l_diversity'] = {
                'min_diversity': diversity_counts.min(),
                'max_diversity': diversity_counts.max(),
                'mean_diversity': diversity_counts.mean(),
                'groups_below_2': (diversity_counts < 2).sum(),
                'groups_below_3': (diversity_counts < 3).sum()
            }
        
        # 评估数据实用性
        if quasi_identifiers:
            # 计算准标识符的信息损失
            total_loss = 0
            total_values = 0
            
            for qi in quasi_identifiers:
                if original_df[qi].dtype == 'object':
                    # 分类属性：计算唯一值数量的变化
                    original_unique = original_df[qi].nunique()
                    anonymized_unique = anonymized_df[qi].nunique()
                    
                    loss = (original_unique - anonymized_unique) / original_unique
                    total_loss += loss
                    total_values += 1
                
                elif original_df[qi].dtype in ['int64', 'float64']:
                    # 数值属性：计算标准差的变化
                    original_std = original_df[qi].std()
                    
                    # 尝试从分组数据中估算标准差
                    if anonymized_df[qi].dtype == 'category':
                        # 如果是分类数据，无法直接计算标准差
                        loss = 0.5  # 假定中等损失
                    else:
                        # 如果仍为数值
                        try:
                            anonymized_std = anonymized_df[qi].std()
                            loss = abs(original_std - anonymized_std) / original_std
                        except:
                            loss = 0.5  # 假定中等损失
                    
                    total_loss += loss
                    total_values += 1
            
            evaluation_results['data_utility'] = {
                'information_loss_ratio': total_loss / total_values if total_values > 0 else 0,
                'utility_score': 1 - (total_loss / total_values if total_values > 0 else 0)
            }
        
        # 评估重识别风险
        if quasi_identifiers:
            # 计算唯一记录的比例
            value_counts = anonymized_df[quasi_identifiers].value_counts()
            unique_records = (value_counts == 1).sum()
            total_records = len(anonymized_df)
            
            evaluation_results['reidentification_risk'] = {
                'unique_records_ratio': unique_records / total_records,
                'max_group_risk': 1 / value_counts.max(),
                'average_risk': (1 / value_counts).mean()
            }
        
        return evaluation_results
    
    def visualize_anonymization_comparison(self, original_df: pd.DataFrame, 
                                         anonymized_df: pd.DataFrame,
                                         column: str,
                                         save_path: str = None):
        """
        可视化匿名化前后对比
        
        Args:
            original_df: 原始数据框
            anonymized_df: 匿名化后的数据框
            column: 要可视化的列
            save_path: 保存路径
        """
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        # 原始数据分布
        if original_df[column].dtype in ['int64', 'float64']:
            # 数值型数据：直方图
            original_df[column].hist(ax=axes[0], bins=20, alpha=0.7)
            axes[0].set_title(f'原始数据: {column}')
            axes[0].set_xlabel(column)
            axes[0].set_ylabel('频次')
            
            # 匿名化数据分布
            if anonymized_df[column].dtype in ['int64', 'float64']:
                anonymized_df[column].hist(ax=axes[1], bins=20, alpha=0.7)
            else:
                # 如果是分类数据，使用条形图
                value_counts = anonymized_df[column].value_counts()
                value_counts.plot(kind='bar', ax=axes[1])
            
            axes[1].set_title(f'匿名化数据: {column}')
            axes[1].set_xlabel(column)
            axes[1].set_ylabel('频次')
        else:
            # 分类数据：条形图
            original_counts = original_df[column].value_counts()
            original_counts.plot(kind='bar', ax=axes[0])
            axes[0].set_title(f'原始数据: {column}')
            axes[0].set_xlabel(column)
            axes[0].set_ylabel('频次')
            axes[0].tick_params(axis='x', rotation=45)
            
            # 匿名化数据分布
            anonymized_counts = anonymized_df[column].value_counts()
            anonymized_counts.plot(kind='bar', ax=axes[1])
            axes[1].set_title(f'匿名化数据: {column}')
            axes[1].set_xlabel(column)
            axes[1].set_ylabel('频次')
            axes[1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()

# 使用示例
if __name__ == "__main__":
    # 创建示例数据
    np.random.seed(42)
    
    data = {
        'name': ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十', '郑十一', '冯十二'],
        'id_card': ['110101199001011234', '110101199002022345', '110101199003033456', 
                    '110101199004044567', '110101199005055678', '110101199006066789',
                    '110101199007077890', '110101199008088901', '110101199009099012', 
                    '110101199010010123'],
        'phone': ['13812345678', '13912345678', '13612345678', '13712345678', '13512345678',
                  '13412345678', '13312345678', '13212345678', '13112345678', '13012345678'],
        'email': ['zhangsan@example.com', 'lisi@example.com', 'wangwu@example.com', 
                  'zhaoliu@example.com', 'qianqi@example.com', 'sunba@example.com',
                  'zhoujiu@example.com', 'wushi@example.com', 'zhengshiyi@example.com', 
                  'fengshier@example.com'],
        'age': [25, 30, 35, 40, 45, 50, 55, 60, 65, 28],
        'income': [5000, 7000, 9000, 12000, 15000, 18000, 22000, 25000, 30000, 6000],
        'address': ['北京市朝阳区建国路1号', '北京市海淀区中关村大街2号', '上海市浦东新区陆家嘴环路3号', 
                    '广州市天河区珠江新城4号', '深圳市南山区科技园5号', '成都市高新区天府大道6号',
                    '杭州市西湖区文三路7号', '南京市鼓楼区中山路8号', '武汉市洪山区珞瑜路9号', 
                    '西安市雁塔区高新路10号'],
        'job': ['软件工程师', '产品经理', '数据分析师', '市场总监', '财务经理',
                '人力资源主管', '销售经理', '运营总监', '技术总监', '测试工程师']
    }
    
    df = pd.DataFrame(data)
    
    print("原始数据:")
    print(df.head())
    
    # 创建匿名化器
    anonymizer = DataAnonymizer()
    
    # 1. 哈希匿名化示例
    print("\n1. 哈希匿名化示例:")
    df_hashed = df.copy()
    df_hashed['id_card_hashed'] = df['id_card'].apply(anonymizer.hash_anonymization)
    print(df_hashed[['id_card', 'id_card_hashed']].head())
    
    # 2. 令牌化示例
    print("\n2. 令牌化示例:")
    df_tokenized = df.copy()
    df_tokenized['name_tokenized'] = df['name'].apply(anonymizer.tokenization)
    print(df_tokenized[['name', 'name_tokenized']].head())
    
    # 3. 数据屏蔽示例
    print("\n3. 数据屏蔽示例:")
    df_masked = df.copy()
    df_masked['id_card_masked'] = df['id_card'].apply(lambda x: anonymizer.masking(x, 'id_card'))
    df_masked['phone_masked'] = df['phone'].apply(lambda x: anonymizer.masking(x, 'phone'))
    df_masked['email_masked'] = df['email'].apply(lambda x: anonymizer.masking(x, 'email'))
    print(df_masked[['id_card', 'id_card_masked', 'phone', 'phone_masked', 'email', 'email_masked']].head())
    
    # 4. 虚假数据生成示例
    print("\n4. 虚假数据生成示例:")
    df_fake = df.copy()
    df_fake['name_fake'] = df['name'].apply(lambda x: anonymizer.fake_data_generation('name'))
    df_fake['email_fake'] = df['email'].apply(lambda x: anonymizer.fake_data_generation('email'))
    df_fake['address_fake'] = df['address'].apply(lambda x: anonymizer.fake_data_generation('address'))
    print(df_fake[['name', 'name_fake', 'email', 'email_fake', 'address', 'address_fake']].head())
    
    # 5. K-匿名化示例
    print("\n5. K-匿名化示例:")
    quasi_identifiers = ['age', 'income']
    k_anonymized_df = anonymizer.k_anonymity(df, quasi_identifiers, k=3)
    print(k_anonymized_df[['name', 'age', 'income']].head())
    
    # 6. L-多样性示例
    print("\n6. L-多样性示例:")
    l_diversified_df = anonymizer.l_diversity(df, quasi_identifiers, 'job', l=2)
    print(l_diversified_df[['name', 'age', 'income', 'job']].head())
    
    # 7. T-相近性示例
    print("\n7. T-相近性示例:")
    t_close_df = anonymizer.t_closeness(df, quasi_identifiers, 'job', t=0.3)
    print(t_close_df[['name', 'age', 'income', 'job']].head())
    
    # 8. 评估匿名化质量
    print("\n8. 评估匿名化质量:")
    evaluation = anonymizer.evaluate_anonymization_quality(
        df, k_anonymized_df, quasi_identifiers, 'job'
    )
    
    print(f"K-匿名性评估:")
    for metric, value in evaluation['k_anonymity'].items():
        print(f"  {metric}: {value}")
    
    print(f"L-多样性评估:")
    for metric, value in evaluation['l_diversity'].items():
        print(f"  {metric}: {value}")
    
    print(f"数据实用性评估:")
    for metric, value in evaluation['data_utility'].items():
        print(f"  {metric}: {value}")
    
    print(f"重识别风险评估:")
    for metric, value in evaluation['reidentification_risk'].items():
        print(f"  {metric}: {value:.4f}")
    
    # 9. 可视化匿名化前后对比
    print("\n9. 可视化匿名化前后对比:")
    anonymizer.visualize_anonymization_comparison(
        df, k_anonymized_df, 'age', 'age_anonymization_comparison.png'
    )
    
    # 10. 保存匿名化后的数据
    print("\n10. 保存匿名化后的数据:")
    k_anonymized_df.to_csv('k_anonymized_data.csv', index=False, encoding='utf-8')
    print("K-匿名化数据已保存到: k_anonymized_data.csv")
    
    # 综合匿名化示例
    print("\n11. 综合匿名化示例:")
    comprehensive_anonymized = df.copy()
    
    # 对敏感字段应用不同匿名化技术
    comprehensive_anonymized['id_card'] = df['id_card'].apply(lambda x: anonymizer.masking(x, 'id_card'))
    comprehensive_anonymized['phone'] = df['phone'].apply(lambda x: anonymizer.masking(x, 'phone'))
    comprehensive_anonymized['email'] = df['email'].apply(lambda x: anonymizer.masking(x, 'email'))
    comprehensive_anonymized['name'] = df['name'].apply(anonymizer.tokenization)
    
    # 对准标识符进行K-匿名化
    comprehensive_anonymized = anonymizer.k_anonymity(
        comprehensive_anonymized, ['age', 'income'], k=3
    )
    
    print(comprehensive_anonymized.head())
    
    # 评估综合匿名化质量
    comprehensive_evaluation = anonymizer.evaluate_anonymization_quality(
        df, comprehensive_anonymized, ['age', 'income'], 'job'
    )
    
    print("\n综合匿名化质量评估:")
    print(f"K-匿名性最小组大小: {comprehensive_evaluation['k_anonymity']['min_group_size']}")
    print(f"平均重识别风险: {comprehensive_evaluation['reidentification_risk']['average_risk']:.4f}")
    print(f"数据实用性得分: {comprehensive_evaluation['data_utility']['utility_score']:.4f}")
    
    # 保存综合匿名化数据
    comprehensive_anonymized.to_csv('comprehensive_anonymized_data.csv', index=False, encoding='utf-8')
    print("综合匿名化数据已保存到: comprehensive_anonymized_data.csv")
    
    print("\n数据匿名化演示完成!")