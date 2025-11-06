#!/usr/bin/env python3
"""
Python数据科学环境示例
演示如何使用DevContainer进行数据科学开发
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

def generate_sample_data():
    """生成示例数据"""
    X, y = make_classification(
        n_samples=1000, 
        n_features=20, 
        n_informative=15, 
        n_redundant=5,
        random_state=42
    )
    
    # 转换为DataFrame
    feature_names = [f'feature_{i}' for i in range(X.shape[1])]
    df = pd.DataFrame(X, columns=feature_names)
    df['target'] = y
    
    return df, X, y

def perform_eda(df):
    """执行探索性数据分析"""
    print("=== 数据基本信息 ===")
    print(f"数据形状: {df.shape}")
    print("\n前5行数据:")
    print(df.head())
    
    print("\n=== 数据统计信息 ===")
    print(df.describe())
    
    print("\n=== 缺失值检查 ===")
    print(df.isnull().sum())

def create_visualizations(df):
    """创建可视化图表"""
    # 设置样式
    plt.style.use('seaborn-v0_8')
    
    # 创建子图
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # 1. 目标变量分布
    df['target'].value_counts().plot(kind='bar', ax=axes[0, 0])
    axes[0, 0].set_title('目标变量分布')
    axes[0, 0].set_xlabel('类别')
    axes[0, 0].set_ylabel('数量')
    
    # 2. 特征相关性热力图
    corr_matrix = df.corr()
    sns.heatmap(corr_matrix, ax=axes[0, 1], cmap='coolwarm', center=0)
    axes[0, 1].set_title('特征相关性热力图')
    
    # 3. 两个特征的关系图
    axes[1, 0].scatter(df['feature_0'], df['feature_1'], c=df['target'], alpha=0.6)
    axes[1, 0].set_title('特征0 vs 特征1')
    axes[1, 0].set_xlabel('特征0')
    axes[1, 0].set_ylabel('特征1')
    
    # 4. 箱线图
    df[['feature_0', 'feature_1', 'feature_2']].boxplot(ax=axes[1, 1])
    axes[1, 1].set_title('特征分布箱线图')
    
    plt.tight_layout()
    plt.savefig('data_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def train_model(X, y):
    """训练机器学习模型"""
    # 分割数据
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # 训练模型
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # 预测
    y_pred = model.predict(X_test)
    
    # 评估
    print("=== 模型评估结果 ===")
    print(classification_report(y_test, y_pred))
    
    # 特征重要性
    feature_importance = pd.DataFrame({
        'feature': [f'feature_{i}' for i in range(X.shape[1])],
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n=== 特征重要性排名 ===")
    print(feature_importance.head(10))
    
    return model, feature_importance

if __name__ == "__main__":
    print("🚀 Python数据科学环境演示")
    print("=" * 50)
    
    # 生成数据
    df, X, y = generate_sample_data()
    
    # 探索性数据分析
    perform_eda(df)
    
    # 可视化
    print("\n📊 正在生成可视化图表...")
    create_visualizations(df)
    
    # 模型训练
    print("\n🤖 正在训练机器学习模型...")
    model, feature_importance = train_model(X, y)
    
    print("\n✅ 数据科学分析完成！")
    print("生成的文件: data_analysis.png")