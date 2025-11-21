# Python数据处理与分析高级指南

## 1. Pandas高级应用与性能优化

### 1.1 高效数据处理与内存优化

Pandas是Python数据分析的核心库，但处理大数据时需要特别关注性能和内存使用。以下是Pandas高级应用技巧：

```python
import pandas as pd
import numpy as np
import time
import gc
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 内存优化示例
def optimize_memory_usage(df: pd.DataFrame) -> pd.DataFrame:
    """优化DataFrame的内存使用"""
    start_mem = df.memory_usage().sum() / 1024 ** 2
    print(f"初始内存使用: {start_mem:.2f} MB")
    
    # 遍历所有列
    for col in df.columns:
        col_type = df[col].dtype
        
        if col_type != object:
            c_min = df[col].min()
            c_max = df[col].max()
            
            if str(col_type)[:3] == 'int':
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
                elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                    df[col] = df[col].astype(np.int64)
            
            else:
                if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                    df[col] = df[col].astype(np.float32)
                elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                    df[col] = df[col].astype(np.float32)
                else:
                    df[col] = df[col].astype(np.float64)
        
        else:
            # 转换为category类型以节省内存
            if df[col].nunique() / len(df[col]) < 0.5:  # 如果唯一值比例小于50%
                df[col] = df[col].astype('category')
    
    end_mem = df.memory_usage().sum() / 1024 ** 2
    print(f"优化后内存使用: {end_mem:.2f} MB")
    print(f"内存减少了: {100 * (start_mem - end_mem) / start_mem:.1f}%")
    
    return df

# 分块处理大数据
def process_large_data_in_chunks(filepath: str, chunksize: int = 10000):
    """分块处理大型数据集"""
    reader = pd.read_csv(filepath, chunksize=chunksize)
    chunks = []
    
    for i, chunk in enumerate(reader):
        # 处理每个数据块
        chunk = optimize_memory_usage(chunk)
        
        # 示例处理：过滤、转换等
        processed_chunk = chunk[chunk['value'] > 0]  # 示例过滤
        
        # 可以在这里执行聚合等操作
        chunks.append(processed_chunk)
        
        print(f"处理块 {i+1}, 形状: {processed_chunk.shape}")
    
    # 合并所有处理过的块
    result = pd.concat(chunks, ignore_index=True)
    return result

# 高效数据聚合
def efficient_aggregation(df: pd.DataFrame):
    """高效的聚合操作"""
    # 使用groupby + agg进行多列聚合
    result = df.groupby('category').agg({
        'value': ['mean', 'std', 'count'],
        'price': ['min', 'max', 'sum']
    })
    
    # 展平多级列索引
    result.columns = ['_'.join(col).strip() for col in result.columns.values]
    result.reset_index(inplace=True)
    
    return result

# 高效数据合并
def efficient_merging():
    """高效的数据合并技术"""
    # 创建示例数据
    df1 = pd.DataFrame({
        'key': np.random.choice(['A', 'B', 'C', 'D'], 1000000),
        'value1': np.random.rand(1000000)
    })
    
    df2 = pd.DataFrame({
        'key': ['A', 'B', 'C', 'D'],
        'value2': [10, 20, 30, 40]
    })
    
    # 方法1: 使用merge（标准方法）
    start = time.time()
    result1 = pd.merge(df1, df2, on='key', how='left')
    time1 = time.time() - start
    print(f"标准merge耗时: {time1:.4f}秒")
    
    # 方法2: 使用set_index + join（通常更快）
    start = time.time()
    df1_indexed = df1.set_index('key')
    df2_indexed = df2.set_index('key')
    result2 = df1_indexed.join(df2_indexed, how='left').reset_index()
    time2 = time.time() - start
    print(f"索引join耗时: {time2:.4f}秒")
    
    print(f"性能提升: {time1/time2:.2f}倍")
    
    return result1, result2

# 高效数据过滤
def efficient_filtering():
    """高效的数据过滤技术"""
    # 创建示例数据
    n = 1000000
    df = pd.DataFrame({
        'id': range(n),
        'category': np.random.choice(['A', 'B', 'C', 'D'], n),
        'value': np.random.randn(n),
        'date': pd.date_range('2020-01-01', periods=n, freq='H')
    })
    
    # 方法1: 布尔索引
    start = time.time()
    mask = (df['category'] == 'A') & (df['value'] > 0)
    result1 = df[mask]
    time1 = time.time() - start
    print(f"布尔索引耗时: {time1:.4f}秒")
    
    # 方法2: query方法（更简洁且通常更快）
    start = time.time()
    result2 = df.query("category == 'A' and value > 0")
    time2 = time.time() - start
    print(f"query方法耗时: {time2:.4f}秒")
    
    print(f"性能提升: {time1/time2:.2f}倍")
    
    # 方法3: 使用eval（对于复杂表达式）
    start = time.time()
    result3 = df.eval("category == 'A' and value > 0")
    df_filtered = df[result3]
    time3 = time.time() - start
    print(f"eval方法耗时: {time3:.4f}秒")
    
    return result1, result2, df_filtered

# 高效时间序列处理
def efficient_time_series():
    """高效的时间序列处理"""
    # 创建时间序列数据
    n = 1000000
    dates = pd.date_range('2020-01-01', periods=n, freq='H')
    df = pd.DataFrame({
        'datetime': dates,
        'value': np.random.randn(n),
        'category': np.random.choice(['A', 'B', 'C'], n)
    })
    
    # 设置为索引
    df.set_index('datetime', inplace=True)
    
    # 方法1: 标准重采样
    start = time.time()
    daily1 = df.resample('D').agg({
        'value': ['mean', 'std'],
        'category': 'count'
    })
    time1 = time.time() - start
    print(f"标准重采样耗时: {time1:.4f}秒")
    
    # 方法2: 使用groupby + Grouper（更灵活）
    start = time.time()
    from pandas.core.groupby.grouper import Grouper
    daily2 = df.groupby([Grouper(freq='D'), 'category']).agg({
        'value': ['mean', 'std']
    })
    time2 = time.time() - start
    print(f"groupby+Grouper耗时: {time2:.4f}秒")
    
    # 方法3: 滚动窗口计算
    start = time.time()
    rolling_mean = df['value'].rolling(window=24).mean()  # 24小时滚动平均
    time3 = time.time() - start
    print(f"滚动计算耗时: {time3:.4f}秒")
    
    return daily1, daily2, rolling_mean

# 高效字符串操作
def efficient_string_operations():
    """高效的字符串操作"""
    # 创建示例数据
    n = 1000000
    df = pd.DataFrame({
        'text': ['Lorem ipsum dolor sit amet'] * n,
        'email': [f'user{i}@example.com' for i in range(n)],
        'phone': [f'123-456-{i:04d}' for i in range(n)]
    })
    
    # 方法1: 标准字符串方法
    start = time.time()
    df['text_upper'] = df['text'].str.upper()
    df['domain'] = df['email'].str.split('@').str[1]
    df['area_code'] = df['phone'].str[:3]
    time1 = time.time() - start
    print(f"标准字符串方法耗时: {time1:.4f}秒")
    
    # 方法2: 向量化操作（更高效）
    start = time.time()
    df['text_upper2'] = np.vectorize(str.upper)(df['text'])
    df['domain2'] = np.vectorize(lambda x: x.split('@')[1])(df['email'])
    df['area_code2'] = np.vectorize(lambda x: x[:3])(df['phone'])
    time2 = time.time() - start
    print(f"向量化操作耗时: {time2:.4f}秒")
    
    print(f"性能提升: {time1/time2:.2f}倍")
    
    return df

# 高效缺失值处理
def efficient_missing_values():
    """高效的缺失值处理"""
    # 创建含缺失值的示例数据
    n = 1000000
    df = pd.DataFrame({
        'A': np.random.rand(n),
        'B': np.random.rand(n),
        'C': np.random.choice([1, 2, 3, np.nan], n),
        'D': np.random.choice(['X', 'Y', 'Z', np.nan], n)
    })
    
    # 随机插入一些NaN
    mask = np.random.random(df.shape) < 0.05  # 5%的值设为NaN
    df[mask] = np.nan
    
    # 统计缺失值
    missing_count = df.isnull().sum()
    missing_pct = 100 * df.isnull().sum() / len(df)
    missing_df = pd.DataFrame({
        'count': missing_count,
        'percentage': missing_pct
    })
    print("缺失值统计:")
    print(missing_df)
    
    # 高效填充策略
    start = time.time()
    
    # 数值列：用中位数填充
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
    
    # 分类列：用众数填充
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    for col in categorical_cols:
        mode_value = df[col].mode()
        if len(mode_value) > 0:
            df[col] = df[col].fillna(mode_value[0])
    
    time1 = time.time() - start
    print(f"填充缺失值耗时: {time1:.4f}秒")
    
    return df

# 运行示例
def demo_pandas_optimization():
    """演示Pandas优化技术"""
    print("=== Pandas高级应用与性能优化 ===")
    
    # 1. 内存优化
    print("\n1. 内存优化")
    sample_data = {
        'id': range(10000),
        'value': np.random.rand(10000),
        'category': np.random.choice(['A', 'B', 'C'], 10000),
        'price': np.random.uniform(1, 100, 10000)
    }
    df = pd.DataFrame(sample_data)
    df = optimize_memory_usage(df)
    
    # 2. 高效合并
    print("\n2. 高效数据合并")
    result1, result2 = efficient_merging()
    
    # 3. 高效过滤
    print("\n3. 高效数据过滤")
    r1, r2, r3 = efficient_filtering()
    
    # 4. 时间序列处理
    print("\n4. 高效时间序列处理")
    daily1, daily2, rolling_mean = efficient_time_series()
    
    # 5. 字符串操作
    print("\n5. 高效字符串操作")
    text_df = efficient_string_operations()
    
    # 6. 缺失值处理
    print("\n6. 高效缺失值处理")
    clean_df = efficient_missing_values()
    
    print("\n所有优化技术演示完成!")

# 运行演示
if __name__ == "__main__":
    demo_pandas_optimization()
```

### 1.2 高级数据分析技巧

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')

# 高级数据探索
def advanced_data_exploration(df: pd.DataFrame):
    """高级数据探索技巧"""
    print("=== 数据基本形状 ===")
    print(f"数据集形状: {df.shape}")
    
    print("\n=== 数据类型 ===")
    print(df.dtypes)
    
    print("\n=== 缺失值情况 ===")
    missing_data = pd.DataFrame({
        'count': df.isnull().sum(),
        'percentage': 100 * df.isnull().sum() / len(df)
    })
    print(missing_data)
    
    print("\n=== 数值列描述统计 ===")
    print(df.describe().T)
    
    print("\n=== 分类列描述统计 ===")
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    for col in categorical_cols:
        print(f"\n{col} 的唯一值数量: {df[col].nunique()}")
        print(f"{col} 的值分布:")
        print(df[col].value_counts(normalize=True).head(10))
    
    # 生成可视化图表
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # 数值列分布
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        df[numeric_cols].hist(ax=axes[0, 0], bins=20, alpha=0.7)
        axes[0, 0].set_title('数值列分布')
    
    # 相关性热图
    if len(numeric_cols) > 1:
        corr = df[numeric_cols].corr()
        sns.heatmap(corr, annot=True, cmap='coolwarm', ax=axes[0, 1])
        axes[0, 1].set_title('特征相关性')
    
    # 缺失值模式
    missing_data['count'].plot(kind='bar', ax=axes[1, 0])
    axes[1, 0].set_title('缺失值数量')
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # 数据类型分布
    dtype_counts = df.dtypes.value_counts()
    dtype_counts.plot(kind='pie', autopct='%1.1f%%', ax=axes[1, 1])
    axes[1, 1].set_title('数据类型分布')
    
    plt.tight_layout()
    plt.show()
    
    return missing_data

# 高级特征工程
def advanced_feature_engineering(df: pd.DataFrame):
    """高级特征工程技术"""
    print("=== 高级特征工程 ===")
    
    # 复制原始数据
    df_feat = df.copy()
    
    # 1. 数值特征转换
    numeric_cols = df_feat.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        # 对数变换（处理偏态分布）
        skewed_cols = []
        for col in numeric_cols:
            skewness = df_feat[col].skew()
            if abs(skewness) > 1:  # 偏态绝对值大于1认为偏态
                skewed_cols.append(col)
                df_feat[f'{col}_log'] = np.log1p(df_feat[col])
        
        print(f"对数变换的列: {skewed_cols}")
        
        # 标准化
        scaler = StandardScaler()
        df_feat[[f'{col}_scaled' for col in numeric_cols]] = scaler.fit_transform(df_feat[numeric_cols])
        
        # 归一化
        minmax_scaler = MinMaxScaler()
        df_feat[[f'{col}_norm' for col in numeric_cols]] = minmax_scaler.fit_transform(df_feat[numeric_cols])
    
    # 2. 分类特征编码
    categorical_cols = df_feat.select_dtypes(include=['object', 'category']).columns
    for col in categorical_cols:
        if df_feat[col].nunique() <= 10:  # 低基数分类变量
            # 独热编码
            dummies = pd.get_dummies(df_feat[col], prefix=col)
            df_feat = pd.concat([df_feat, dummies], axis=1)
        else:  # 高基数分类变量
            # 目标编码（示例，实际需要目标变量）
            if df_feat[col].nunique() > len(df_feat) * 0.5:  # 唯一值超过50%
                # 频次编码
                freq_map = df_feat[col].value_counts().to_dict()
                df_feat[f'{col}_freq'] = df_feat[col].map(freq_map)
            else:
                # 标签编码
                df_feat[f'{col}_encoded'] = df_feat[col].astype('category').cat.codes
    
    # 3. 交互特征
    if len(numeric_cols) >= 2:
        # 数值特征之间的交互
        for i, col1 in enumerate(numeric_cols[:3]):  # 限制为前3列以避免过多特征
            for col2 in numeric_cols[i+1:4]:  # 限制交互特征数量
                df_feat[f'{col1}_x_{col2}'] = df_feat[col1] * df_feat[col2]
    
    # 4. 多项式特征
    if len(numeric_cols) > 0:
        from sklearn.preprocessing import PolynomialFeatures
        poly = PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)
        poly_features = poly.fit_transform(df_feat[numeric_cols[:2]])  # 限制为前2列
        
        poly_feature_names = [f'poly_{i}' for i in range(poly_features.shape[1])]
        df_feat[poly_feature_names] = poly_features
    
    # 5. 时间特征（如果有时间列）
    date_cols = df_feat.select_dtypes(include=['datetime64']).columns
    for col in date_cols:
        df_feat[f'{col}_year'] = df_feat[col].dt.year
        df_feat[f'{col}_month'] = df_feat[col].dt.month
        df_feat[f'{col}_day'] = df_feat[col].dt.day
        df_feat[f'{col}_weekday'] = df_feat[col].dt.weekday
        df_feat[f'{col}_quarter'] = df_feat[col].dt.quarter
    
    print(f"原始特征数量: {df.shape[1]}")
    print(f"新特征数量: {df_feat.shape[1]}")
    print(f"特征增加: {df_feat.shape[1] - df.shape[1]}")
    
    return df_feat

# 高级分组分析
def advanced_groupby_analysis(df: pd.DataFrame):
    """高级分组分析技术"""
    print("=== 高级分组分析 ===")
    
    # 示例数据
    if 'category' not in df.columns or 'value' not in df.columns:
        # 如果没有这些列，创建示例数据
        df = pd.DataFrame({
            'category': np.random.choice(['A', 'B', 'C', 'D'], 10000),
            'value': np.random.randn(10000),
            'group': np.random.choice(['X', 'Y', 'Z'], 10000),
            'price': np.random.uniform(10, 100, 10000)
        })
    
    # 1. 多级分组聚合
    multi_level = df.groupby(['category', 'group']).agg({
        'value': ['mean', 'std', 'count', 'min', 'max'],
        'price': ['sum', 'mean']
    })
    
    # 展平多级索引
    multi_level.columns = ['_'.join(col).strip() for col in multi_level.columns.values]
    multi_level.reset_index(inplace=True)
    
    print("多级分组聚合:")
    print(multi_level.head())
    
    # 2. 自定义聚合函数
    def range_calc(x):
        return x.max() - x.min()
    
    def cv_calc(x):  # 变异系数
        return x.std() / x.mean() if x.mean() != 0 else 0
    
    custom_agg = df.groupby('category').agg({
        'value': ['mean', range_calc, cv_calc],
        'price': lambda x: x.quantile(0.75) - x.quantile(0.25)  # IQR
    })
    
    # 展平列名
    custom_agg.columns = ['_'.join(col).strip() for col in custom_agg.columns.values]
    custom_agg.reset_index(inplace=True)
    
    print("\n自定义聚合函数:")
    print(custom_agg)
    
    # 3. 分组转换（窗口函数）
    df['value_rank'] = df.groupby('category')['value'].rank(method='dense')
    df['value_pct'] = df.groupby('category')['value'].transform(lambda x: x.rank(pct=True))
    df['value_zscore'] = df.groupby('category')['value'].transform(lambda x: (x - x.mean()) / x.std())
    
    print("\n分组转换示例:")
    print(df[['category', 'value', 'value_rank', 'value_pct', 'value_zscore']].head(10))
    
    # 4. 分组过滤
    # 过滤出值数量大于1000的类别
    filtered = df.groupby('category').filter(lambda x: len(x) > 2500)
    print(f"\n过滤后数据量: {len(filtered)} / {len(df)}")
    
    # 5. 分组应用复杂函数
    def complex_calc(group):
        # 对每个分组执行复杂计算
        result = pd.DataFrame()
        result['mean'] = [group['value'].mean()]
        result['median'] = [group['value'].median()]
        result['outliers'] = [((group['value'] < group['value'].quantile(0.25) - 1.5 * (group['value'].quantile(0.75) - group['value'].quantile(0.25))) |
                                  (group['value'] > group['value'].quantile(0.75) + 1.5 * (group['value'].quantile(0.75) - group['value'].quantile(0.25)))).sum()]
        return result
    
    complex_result = df.groupby('category').apply(complex_calc)
    print("\n复杂分组计算:")
    print(complex_result)
    
    return multi_level, custom_agg, filtered, complex_result

# 高级数据透视分析
def advanced_pivot_analysis(df: pd.DataFrame):
    """高级数据透视分析"""
    print("=== 高级数据透视分析 ===")
    
    # 示例数据
    if all(col not in df.columns for col in ['category', 'group', 'value', 'price']):
        df = pd.DataFrame({
            'category': np.random.choice(['A', 'B', 'C', 'D'], 10000),
            'group': np.random.choice(['X', 'Y', 'Z'], 10000),
            'value': np.random.randn(10000),
            'price': np.random.uniform(10, 100, 10000),
            'quantity': np.random.randint(1, 10, 10000),
            'date': pd.date_range('2022-01-01', periods=10000, freq='D')
        })
    
    # 1. 基本透视表
    pivot1 = pd.pivot_table(df, 
                          values='value', 
                          index='category', 
                          columns='group', 
                          aggfunc='mean')
    
    print("基本透视表:")
    print(pivot1)
    
    # 2. 多值透视表
    pivot2 = pd.pivot_table(df, 
                          values=['value', 'price'], 
                          index='category', 
                          columns='group', 
                          aggfunc={'value': 'mean', 'price': 'sum'})
    
    print("\n多值透视表:")
    print(pivot2)
    
    # 3. 多级索引透视表
    pivot3 = pd.pivot_table(df, 
                          values='value', 
                          index=['category', 'group'], 
                          columns='date', 
                          aggfunc='mean')
    
    # 4. 添加总计和边缘总计
    pivot4 = pd.pivot_table(df, 
                          values='value', 
                          index='category', 
                          columns='group', 
                          aggfunc='mean', 
                          margins=True, 
                          margins_name='Total')
    
    print("\n带总计的透视表:")
    print(pivot4)
    
    # 5. 自定义聚合函数
    pivot5 = pd.pivot_table(df, 
                          values='value', 
                          index='category', 
                          columns='group', 
                          aggfunc=[np.mean, np.std, lambda x: x.max() - x.min()])
    
    print("\n自定义聚合透视表:")
    print(pivot5)
    
    # 6. crosstab（交叉表）
    crosstab1 = pd.crosstab(df['category'], df['group'])
    print("\n交叉表:")
    print(crosstab1)
    
    # 7. 带归一化的交叉表
    crosstab2 = pd.crosstab(df['category'], df['group'], normalize='index')
    print("\n归一化交叉表:")
    print(crosstab2)
    
    return pivot1, pivot2, pivot4, crosstab1, crosstab2

# 高级时间序列分析
def advanced_time_series_analysis():
    """高级时间序列分析"""
    print("=== 高级时间序列分析 ===")
    
    # 创建示例时间序列数据
    dates = pd.date_range('2020-01-01', periods=1000, freq='D')
    trend = np.linspace(100, 200, 1000)
    seasonal = 10 * np.sin(np.linspace(0, 20 * np.pi, 1000))
    noise = np.random.normal(0, 5, 1000)
    values = trend + seasonal + noise
    
    df = pd.DataFrame({
        'date': dates,
        'value': values,
        'category': np.random.choice(['A', 'B', 'C'], 1000)
    })
    
    df.set_index('date', inplace=True)
    
    # 1. 时间序列分解
    from statsmodels.tsa.seasonal import seasonal_decompose
    
    # 周期性分解（假设有周度季节性）
    decomposition = seasonal_decompose(df['value'], model='additive', period=7)
    
    # 绘制分解图
    fig, axes = plt.subplots(4, 1, figsize=(12, 10))
    decomposition.observed.plot(ax=axes[0], title='原始值')
    decomposition.trend.plot(ax=axes[1], title='趋势')
    decomposition.seasonal.plot(ax=axes[2], title='季节性')
    decomposition.resid.plot(ax=axes[3], title='残差')
    plt.tight_layout()
    plt.show()
    
    # 2. 滚动窗口统计
    windows = [7, 30, 90]
    for window in windows:
        df[f'rolling_mean_{window}'] = df['value'].rolling(window=window).mean()
        df[f'rolling_std_{window}'] = df['value'].rolling(window=window).std()
    
    # 3. 滚动相关系数
    df['rolling_corr'] = df['value'].rolling(window=30).corr(df['rolling_mean_7'])
    
    # 4. 差分（用于时间序列平稳化）
    df['diff_1'] = df['value'].diff(1)
    df['diff_30'] = df['value'].diff(30)
    
    # 5. 滞后特征
    for lag in [1, 7, 30]:
        df[f'lag_{lag}'] = df['value'].shift(lag)
    
    # 6. 日期特征
    df['day_of_week'] = df.index.dayofweek
    df['month'] = df.index.month
    df['quarter'] = df.index.quarter
    df['year'] = df.index.year
    
    # 7. 按时间分组聚合
    daily = df.resample('D').agg({
        'value': ['mean', 'std', 'min', 'max'],
        'rolling_mean_7': 'last'
    })
    
    weekly = df.resample('W').agg({
        'value': ['mean', 'std'],
        'lag_7': 'first'
    })
    
    monthly = df.resample('M').agg({
        'value': ['mean', 'std', 'min', 'max'],
        'rolling_mean_30': 'last'
    })
    
    print("日级别聚合:")
    print(daily.head())
    
    print("\n周级别聚合:")
    print(weekly.head())
    
    print("\n月级别聚合:")
    print(monthly.head())
    
    # 8. 时间序列可视化
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # 原始值与移动平均
    df[['value', 'rolling_mean_7', 'rolling_mean_30']].plot(ax=axes[0, 0])
    axes[0, 0].set_title('原始值与移动平均')
    axes[0, 0].legend(['原始值', '7日均线', '30日均线'])
    
    # 滚动标准差
    df[['rolling_std_7', 'rolling_std_30']].plot(ax=axes[0, 1])
    axes[0, 1].set_title('滚动标准差')
    
    # 按月分组
    monthly['value']['mean'].plot(kind='bar', ax=axes[1, 0])
    axes[1, 0].set_title('月平均')
    
    # 按星期分组
    weekly['value']['mean'].plot(kind='bar', ax=axes[1, 1])
    axes[1, 1].set_title('周平均')
    
    plt.tight_layout()
    plt.show()
    
    return df, daily, weekly, monthly

# 运行示例
def demo_advanced_data_analysis():
    """演示高级数据分析技巧"""
    print("=== Pandas高级数据分析技巧 ===")
    
    # 1. 创建示例数据
    np.random.seed(42)
    n = 10000
    df = pd.DataFrame({
        'id': range(n),
        'category': np.random.choice(['A', 'B', 'C', 'D'], n),
        'group': np.random.choice(['X', 'Y', 'Z'], n),
        'value': np.random.randn(n),
        'price': np.random.uniform(10, 100, n),
        'quantity': np.random.randint(1, 10, n),
        'date': pd.date_range('2020-01-01', periods=n, freq='H')
    })
    
    # 添加一些缺失值
    mask = np.random.random(df.shape) < 0.05
    df[mask] = np.nan
    
    # 2. 高级数据探索
    print("\n1. 高级数据探索")
    missing_data = advanced_data_exploration(df)
    
    # 3. 高级特征工程
    print("\n2. 高级特征工程")
    df_features = advanced_feature_engineering(df)
    
    # 4. 高级分组分析
    print("\n3. 高级分组分析")
    multi_level, custom_agg, filtered, complex_result = advanced_groupby_analysis(df)
    
    # 5. 高级数据透视分析
    print("\n4. 高级数据透视分析")
    pivot1, pivot2, pivot4, crosstab1, crosstab2 = advanced_pivot_analysis(df)
    
    # 6. 高级时间序列分析
    print("\n5. 高级时间序列分析")
    ts_df, daily, weekly, monthly = advanced_time_series_analysis()
    
    print("\n所有高级数据分析技巧演示完成!")

# 运行演示
if __name__ == "__main__":
    demo_advanced_data_analysis()
```

## 2. 大数据处理框架

### 2.1 Dask分布式数据处理

```python
import pandas as pd
import numpy as np
import dask
import dask.dataframe as dd
from dask.distributed import Client
import time
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# Dask基础概念与配置
def dask_basics():
    """Dask基础概念与配置"""
    print("=== Dask基础概念与配置 ===")
    
    # 1. 本地Dask客户端
    client = Client(processes=False, threads_per_worker=4, memory_limit='2GB')
    print(f"Dask客户端: {client}")
    print(f"仪表板地址: {client.dashboard_link}")
    
    # 2. 创建Dask DataFrame
    # 方法1: 从Pandas DataFrame创建
    pdf = pd.DataFrame({
        'x': np.random.randint(0, 100, size=100000),
        'y': np.random.randn(100000),
        'z': np.random.choice(['A', 'B', 'C'], 100000)
    })
    
    ddf = dd.from_pandas(pdf, npartitions=10)
    print(f"Dask DataFrame分区数: {ddf.npartitions}")
    
    # 方法2: 直接创建
    ddf2 = dd.DataFrame({
        'x': da.random.randint(0, 100, size=100000, chunks=10000),
        'y': da.random.randn(100000, chunks=10000),
        'z': da.from_array(np.random.choice(['A', 'B', 'C'], 100000), chunks=10000)
    })
    
    # 3. Dask延迟计算
    # 创建一个需要计算的任务
    @dask.delayed
    def inc(x):
        return x + 1
    
    @dask.delayed
    def add(a, b):
        return a + b
    
    # 构建计算图
    a = inc(1)
    b = inc(2)
    c = add(a, b)
    
    print(f"计算结果: {c.compute()}")
    print(f"计算图: {c.dask}")
    c.visualize(filename='dask_graph')  # 需要安装graphviz
    
    return client, ddf, ddf2

# Dask DataFrame操作
def dask_dataframe_operations():
    """Dask DataFrame操作示例"""
    print("\n=== Dask DataFrame操作 ===")
    
    # 1. 创建大型数据集
    size = 10_000_000  # 1000万行数据
    
    ddf = dd.DataFrame({
        'id': da.arange(size, chunks=1_000_000),
        'value': da.random.randn(size, chunks=1_000_000),
        'category': da.random.choice(['A', 'B', 'C', 'D'], size, chunks=1_000_000),
        'timestamp': da.random.randint(0, 1000000000, size, chunks=1_000_000)
    })
    
    # 2. 基本操作
    print("前5行:")
    print(ddf.head())
    
    print("\n列信息:")
    print(ddf.dtypes)
    
    # 3. 聚合操作
    print("\n聚合操作:")
    mean_val = ddf['value'].mean().compute()
    print(f"value列平均值: {mean_val}")
    
    cat_counts = ddf['category'].value_counts().compute()
    print(f"\ncategory列计数:\n{cat_counts}")
    
    # 4. 分组聚合
    print("\n分组聚合:")
    grouped = ddf.groupby('category').agg({
        'value': ['mean', 'std', 'count']
    })
    
    # 展平多级列名
    grouped.columns = ['_'.join(col).strip() for col in grouped.columns.values]
    result = grouped.compute()
    print(result)
    
    # 5. 过滤和查询
    print("\n过滤和查询:")
    filtered = ddf[(ddf['value'] > 0) & (ddf['category'] == 'A')]
    filtered_count = len(filtered)
    print(f"过滤后行数: {filtered_count}")
    
    # 6. 添加新列
    print("\n添加新列:")
    ddf['value_abs'] = ddf['value'].abs()
    ddf['value_squared'] = ddf['value'] ** 2
    
    print("新列统计:")
    print(ddf[['value_abs', 'value_squared']].describe().compute())
    
    # 7. 连接操作
    print("\n连接操作:")
    ddf2 = dd.DataFrame({
        'id': da.arange(size//2, chunks=500_000),
        'extra_value': da.random.randn(size//2, chunks=500_000)
    })
    
    joined = dd.merge(ddf, ddf2, on='id', how='left')
    print(f"连接后形状: {joined.shape[0].compute()} 行")
    
    return ddf

# Dask性能比较
def dask_vs_pandas_performance():
    """Dask与Pandas性能比较"""
    print("\n=== Dask与Pandas性能比较 ===")
    
    sizes = [100_000, 1_000_000, 5_000_000, 10_000_000]
    pandas_times = []
    dask_times = []
    
    for size in sizes:
        print(f"\n数据大小: {size:,}")
        
        # 1. Pandas处理
        pdf = pd.DataFrame({
            'x': np.random.randn(size),
            'y': np.random.randint(0, 100, size),
            'z': np.random.choice(['A', 'B', 'C'], size)
        })
        
        start_time = time.time()
        result_pandas = pdf.groupby('z').agg({'x': 'mean', 'y': 'sum'})
        pandas_time = time.time() - start_time
        pandas_times.append(pandas_time)
        print(f"Pandas处理时间: {pandas_time:.4f}秒")
        
        # 2. Dask处理
        ddf = dd.from_pandas(pdf, npartitions=max(1, size // 100_000))
        
        start_time = time.time()
        result_dask = ddf.groupby('z').agg({'x': 'mean', 'y': 'sum'}).compute()
        dask_time = time.time() - start_time
        dask_times.append(dask_time)
        print(f"Dask处理时间: {dask_time:.4f}秒")
        
        # 验证结果一致性
        assert np.allclose(result_pandas['x'], result_dask['x'])
        assert np.allclose(result_pandas['y'], result_dask['y'])
        
        speedup = pandas_time / dask_time if dask_time > 0 else float('inf')
        print(f"加速比: {speedup:.2f}x")
    
    # 绘制性能对比图
    plt.figure(figsize=(10, 6))
    plt.plot(sizes, pandas_times, 'o-', label='Pandas')
    plt.plot(sizes, dask_times, 'o-', label='Dask')
    plt.xlabel('数据大小（行数）')
    plt.ylabel('处理时间（秒）')
    plt.title('Pandas vs Dask 性能对比')
    plt.legend()
    plt.grid(True)
    plt.xscale('log')
    plt.yscale('log')
    plt.show()
    
    return pandas_times, dask_times

# Dask分布式计算
def dask_distributed_computing():
    """Dask分布式计算示例"""
    print("\n=== Dask分布式计算 ===")
    
    # 创建本地集群
    client = Client(n_workers=2, threads_per_worker=2, memory_limit='2GB')
    print(f"集群信息: {client}")
    
    # 1. 大型数据集处理
    print("\n大型数据集处理:")
    
    # 创建大型数据集（模拟）
    num_files = 10
    file_pattern = 'temp_data_*.csv'
    
    # 创建临时CSV文件
    for i in range(num_files):
        df = pd.DataFrame({
            'id': range(i*100_000, (i+1)*100_000),
            'value': np.random.randn(100_000),
            'category': np.random.choice(['A', 'B', 'C'], 100_000)
        })
        df.to_csv(f'temp_data_{i}.csv', index=False)
    
    # 使用Dask读取所有CSV文件
    ddf = dd.read_csv(file_pattern)
    print(f"总行数: {len(ddf)}")
    print(f"分区数: {ddf.npartitions}")
    
    # 2. 并行处理
    print("\n并行处理:")
    
    @dask.delayed
    def process_partition(partition):
        """处理单个分区的函数"""
        # 这里可以进行复杂处理
        return partition.groupby('category').agg({
            'value': ['mean', 'std', 'count']
        })
    
    # 创建处理任务
    results = []
    for partition in ddf.to_delayed():
        result = process_partition(partition)
        results.append(result)
    
    # 执行计算
    start_time = time.time()
    computed_results = dask.compute(*results)
    processing_time = time.time() - start_time
    
    print(f"并行处理时间: {processing_time:.4f}秒")
    
    # 3. 自定义聚合
    print("\n自定义聚合:")
    
    # Dask的聚合比Pandas的groupby更高效
    start_time = time.time()
    agg_result = ddf.groupby('category').agg({
        'value': ['mean', 'std', 'min', 'max', 'count']
    }).compute()
    dask_agg_time = time.time() - start_time
    
    print(f"Dask聚合时间: {dask_agg_time:.4f}秒")
    print(agg_result)
    
    # 4. 复杂操作
    print("\n复杂操作:")
    
    # 先计算每个类别的统计量，再计算全局统计
    start_time = time.time()
    
    # 步骤1：按类别分组计算
    category_stats = ddf.groupby('category')['value'].agg(['mean', 'std']).compute()
    
    # 步骤2：使用这些统计量进行进一步处理
    def normalize_by_category(row, stats):
        cat = row['category']
        mean = stats.loc[cat, 'mean']
        std = stats.loc[cat, 'std']
        return (row['value'] - mean) / std if std != 0 else 0
    
    # 应用标准化
    meta = ('value_norm', 'float64')  # 指定输出列的类型
    ddf['value_norm'] = ddf.apply(
        normalize_by_category, 
        args=(category_stats,), 
        axis=1, 
        meta=meta
    )
    
    # 检查标准化后的分布
    norm_result = ddf.groupby('category')['value_norm'].describe().compute()
    complex_time = time.time() - start_time
    
    print(f"复杂操作时间: {complex_time:.4f}秒")
    print(norm_result)
    
    # 清理临时文件
    import glob
    for file in glob.glob('temp_data_*.csv'):
        import os
        os.remove(file)
    
    return client, agg_result, norm_result

# 运行示例
def demo_dask_processing():
    """演示Dask大数据处理"""
    print("=== Dask分布式数据处理演示 ===")
    
    # 1. Dask基础
    client, ddf, ddf2 = dask_basics()
    
    # 2. Dask DataFrame操作
    ddf = dask_dataframe_operations()
    
    # 3. 性能比较
    pandas_times, dask_times = dask_vs_pandas_performance()
    
    # 4. 分布式计算
    client, agg_result, norm_result = dask_distributed_computing()
    
    # 关闭客户端
    client.close()
    
    print("\nDask大数据处理演示完成!")

# 运行演示
if __name__ == "__main__":
    demo_dask_processing()
```

### 2.2 其他大数据处理框架比较

```python
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
from typing import Dict, List, Any
import warnings
warnings.filterwarnings('ignore')

# 大数据处理框架比较
def compare_big_data_frameworks():
    """比较不同的大数据处理框架"""
    print("=== 大数据处理框架比较 ===")
    
    # 数据大小范围
    sizes = [100_000, 500_000, 1_000_000, 5_000_000]
    
    # 存储结果
    results = {
        'Pandas': {'time': [], 'memory': []},
        'Dask': {'time': [], 'memory': []},
        'Polars': {'time': [], 'memory': []},
        'Vaex': {'time': [], 'memory': []}  # 如果安装了
    }
    
    for size in sizes:
        print(f"\n处理 {size:,} 行数据:")
        
        # 1. Pandas
        print("\n--- Pandas ---")
        start = time.time()
        
        # 创建DataFrame
        pdf = pd.DataFrame({
            'id': range(size),
            'value': np.random.randn(size),
            'category': np.random.choice(['A', 'B', 'C', 'D', 'E'], size),
            'timestamp': pd.date_range('2020-01-01', periods=size, freq='s')
        })
        
        # 执行操作
        result = pdf.groupby('category').agg({
            'value': ['mean', 'std', 'min', 'max', 'count']
        })
        
        pandas_time = time.time() - start
        pandas_memory = pdf.memory_usage(deep=True).sum() / (1024 * 1024)  # MB
        
        results['Pandas']['time'].append(pandas_time)
        results['Pandas']['memory'].append(pandas_memory)
        
        print(f"时间: {pandas_time:.4f}秒, 内存: {pandas_memory:.2f}MB")
        
        # 2. Dask
        print("\n--- Dask ---")
        start = time.time()
        
        import dask.dataframe as dd
        ddf = dd.from_pandas(pdf, npartitions=max(1, size // 100_000))
        
        # 执行相同操作
        result = ddf.groupby('category').agg({
            'value': ['mean', 'std', 'min', 'max', 'count']
        }).compute()
        
        dask_time = time.time() - start
        dask_memory = pdf.memory_usage(deep=True).sum() / (1024 * 1024)  # 估算
        
        results['Dask']['time'].append(dask_time)
        results['Dask']['memory'].append(dask_memory)
        
        print(f"时间: {dask_time:.4f}秒, 内存: {dask_memory:.2f}MB")
        
        # 3. Polars (如果安装)
        try:
            print("\n--- Polars ---")
            start = time.time()
            
            import polars as pl
            
            # 创建Polars DataFrame
            pldf = pl.DataFrame({
                'id': range(size),
                'value': np.random.randn(size),
                'category': np.random.choice(['A', 'B', 'C', 'D', 'E'], size),
                'timestamp': pd.date_range('2020-01-01', periods=size, freq='s')
            })
            
            # 执行相同操作
            result = pldf.groupby('category').agg([
                pl.col('value').mean().alias('mean'),
                pl.col('value').std().alias('std'),
                pl.col('value').min().alias('min'),
                pl.col('value').max().alias('max'),
                pl.col('value').count().alias('count')
            ])
            
            polars_time = time.time() - start
            polars_memory = pldf.estimated_size('mb')
            
            results['Polars']['time'].append(polars_time)
            results['Polars']['memory'].append(polars_memory)
            
            print(f"时间: {polars_time:.4f}秒, 内存: {polars_memory:.2f}MB")
            
        except ImportError:
            print("Polars未安装，跳过测试")
            results['Polars']['time'].append(None)
            results['Polars']['memory'].append(None)
        
        # 4. Vaex (如果安装)
        try:
            print("\n--- Vaex ---")
            start = time.time()
            
            import vaex
            
            # 创建Vaex DataFrame
            df = vaex.from_arrays(
                id=np.arange(size),
                value=np.random.randn(size),
                category=np.random.choice(['A', 'B', 'C', 'D', 'E'], size),
                timestamp=pd.date_range('2020-01-01', periods=size, freq='s')
            )
            
            # 执行相同操作
            result = df.groupby('category', 
                               agg={'value': ['mean', 'std', 'min', 'max', 'count']})
            
            vaex_time = time.time() - start
            vaex_memory = df.memory_usage().sum() / (1024 * 1024)
            
            results['Vaex']['time'].append(vaex_time)
            results['Vaex']['memory'].append(vaex_memory)
            
            print(f"时间: {vaex_time:.4f}秒, 内存: {vaex_memory:.2f}MB")
            
        except ImportError:
            print("Vaex未安装，跳过测试")
            results['Vaex']['time'].append(None)
            results['Vaex']['memory'].append(None)
    
    # 绘制比较结果
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 处理时间比较
    for framework, data in results.items():
        if any(time_val is not None for time_val in data['time']):
            ax1.plot(sizes, data['time'], 'o-', label=framework)
    
    ax1.set_xlabel('数据大小（行数）')
    ax1.set_ylabel('处理时间（秒）')
    ax1.set_title('处理时间比较')
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.legend()
    ax1.grid(True)
    
    # 内存使用比较
    for framework, data in results.items():
        if any(mem_val is not None for mem_val in data['memory']):
            ax2.plot(sizes, data['memory'], 'o-', label=framework)
    
    ax2.set_xlabel('数据大小（行数）')
    ax2.set_ylabel('内存使用（MB）')
    ax2.set_title('内存使用比较')
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.show()
    
    # 框架选择建议
    print("\n=== 框架选择建议 ===")
    print("Pandas: 适合中小型数据集（<1GB），功能全面，社区庞大")
    print("Dask: 适合大于内存的数据集，可扩展性好，与Pandas API兼容")
    print("Polars: 适合大数据集，速度快，内存效率高，使用Apache Arrow")
    print("Vaex: 适合超大数据集，支持流式处理，延迟计算")
    
    return results

# 数据库连接与查询
def database_integration():
    """数据库连接与查询"""
    print("\n=== 数据库集成示例 ===")
    
    # 1. SQLite集成
    print("\n--- SQLite集成 ---")
    
    import sqlite3
    from sqlalchemy import create_engine
    
    # 创建SQLite数据库
    engine = create_engine('sqlite:///sample.db')
    
    # 创建示例数据
    df = pd.DataFrame({
        'id': range(10000),
        'name': [f'Item_{i}' for i in range(10000)],
        'value': np.random.randn(10000),
        'category': np.random.choice(['A', 'B', 'C'], 10000)
    })
    
    # 写入数据库
    df.to_sql('items', engine, index=False, if_exists='replace')
    print(f"已写入 {len(df)} 行数据到SQLite数据库")
    
    # 从数据库读取
    start = time.time()
    df_from_db = pd.read_sql('SELECT * FROM items WHERE value > 0', engine)
    db_time = time.time() - start
    
    print(f"从数据库查询 {len(df_from_db)} 行数据，耗时: {db_time:.4f}秒")
    print(df_from_db.head())
    
    # 2. 使用Dask与SQL数据库
    print("\n--- Dask与SQL数据库集成 ---")
    
    try:
        import dask.dataframe as dd
        from dask_sql import Context
        
        # 创建Dask SQL上下文
        c = Context()
        
        # 从SQLite创建表
        c.create_table('items', df)
        
        # 使用SQL查询
        result = c.sql("""
            SELECT category, 
                   AVG(value) as avg_value, 
                   COUNT(*) as count
            FROM items
            GROUP BY category
        """)
        
        # 获取结果
        sql_result = result.compute()
        print("SQL查询结果:")
        print(sql_result)
        
    except ImportError:
        print("dask_sql未安装，跳过Dask SQL演示")
    
    # 3. 大数据处理最佳实践
    print("\n--- 大数据处理最佳实践 ---")
    
    # 最佳实践1: 分块读取
    print("最佳实践1: 分块读取")
    chunk_size = 2000
    chunks = []
    
    start = time.time()
    for chunk in pd.read_sql('SELECT * FROM items', engine, chunksize=chunk_size):
        # 处理每个块
        processed = chunk[chunk['value'] > 0]
        chunks.append(processed)
    
    # 合并结果
    result = pd.concat(chunks, ignore_index=True)
    chunk_time = time.time() - start
    
    print(f"分块处理耗时: {chunk_time:.4f}秒")
    print(f"处理结果: {len(result)} 行")
    
    # 最佳实践2: 使用数据库进行聚合
    print("\n最佳实践2: 使用数据库进行聚合")
    
    start = time.time()
    agg_result = pd.read_sql("""
        SELECT category, 
               AVG(value) as avg_value, 
               STD(value) as std_value,
               COUNT(*) as count
        FROM items
        GROUP BY category
    """, engine)
    agg_time = time.time() - start
    
    print(f"数据库聚合耗时: {agg_time:.4f}秒")
    print(agg_result)
    
    # 最佳实践3: 索引优化
    print("\n最佳实践3: 索引优化")
    
    # 创建索引
    with sqlite3.connect('sample.db') as conn:
        conn.execute("CREATE INDEX IF NOT EXISTS idx_items_category ON items(category)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_items_value ON items(value)")
    
    # 使用索引优化查询
    start = time.time()
    indexed_result = pd.read_sql("""
        SELECT * FROM items
        WHERE category = 'A' AND value > 0.5
    """, engine)
    indexed_time = time.time() - start
    
    print(f"索引查询耗时: {indexed_time:.4f}秒")
    print(f"查询结果: {len(indexed_result)} 行")
    
    return df, agg_result

# 数据可视化优化
def optimized_visualization():
    """大数据可视化优化技术"""
    print("\n=== 大数据可视化优化 ===")
    
    # 1. 创建大数据集
    n = 1_000_000
    df = pd.DataFrame({
        'x': np.random.randn(n),
        'y': np.random.randn(n),
        'category': np.random.choice(['A', 'B', 'C', 'D', 'E'], n),
        'value': np.random.uniform(0, 100, n)
    })
    
    # 2. 采样技术
    print("--- 数据采样技术 ---")
    
    # 随机采样
    sample_size = min(10000, len(df))  # 最多10000个点
    random_sample = df.sample(n=sample_size)
    
    # 分层采样（确保每个类别都有代表性）
    stratified_sample = df.groupby('category').apply(
        lambda x: x.sample(min(2000, len(x)))
    ).reset_index(drop=True)
    
    print(f"原始数据: {len(df)} 行")
    print(f"随机采样: {len(random_sample)} 行")
    print(f"分层采样: {len(stratified_sample)} 行")
    print(f"分层采样类别分布:\n{stratified_sample['category'].value_counts()}")
    
    # 3. 绘制采样数据
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # 散点图（原始数据可能太慢）
    if len(df) <= 10000:  # 只有在数据量不大时才绘制原始数据
        df.plot.scatter('x', 'y', c='value', colormap='viridis', s=5, alpha=0.5, ax=axes[0, 0])
        axes[0, 0].set_title('原始数据散点图')
    else:
        axes[0, 0].text(0.5, 0.5, f'数据太大 ({len(df)} 点)\n跳过散点图', 
                       ha='center', va='center', transform=axes[0, 0].transAxes)
        axes[0, 0].set_title('原始数据散点图（跳过）')
    
    # 随机采样散点图
    random_sample.plot.scatter('x', 'y', c='value', colormap='viridis', s=10, alpha=0.7, ax=axes[0, 1])
    axes[0, 1].set_title(f'随机采样散点图 ({sample_size} 点)')
    
    # 分层采样散点图
    stratified_sample.plot.scatter('x', 'y', c='category', colormap='viridis', s=10, alpha=0.7, ax=axes[1, 0])
    axes[1, 0].set_title(f'分层采样散点图 ({len(stratified_sample)} 点)')
    
    # 六边形图（适合大数据集）
    df.plot.hexbin('x', 'y', C='value', gridsize=20, cmap='viridis', ax=axes[1, 1])
    axes[1, 1].set_title('六边形图')
    
    plt.tight_layout()
    plt.show()
    
    # 4. 聚合可视化
    print("\n--- 聚合可视化 ---")
    
    # 2D直方图
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # 标准直方图
    axes[0].hist2d(df['x'], df['y'], bins=50, cmap='viridis')
    axes[0].set_title('2D直方图')
    axes[0].set_xlabel('x')
    axes[0].set_ylabel('y')
    
    # 密度图
    axes[1].hexbin(df['x'], df['y'], gridsize=30, cmap='viridis')
    axes[1].set_title('六边形密度图')
    axes[1].set_xlabel('x')
    axes[1].set_ylabel('y')
    
    plt.tight_layout()
    plt.show()
    
    # 5. 使用Dask进行可视化
    print("\n--- 使用Dask进行可视化 ---")
    
    try:
        import dask.dataframe as dd
        from dask.distributed import Client
        
        # 创建Dask DataFrame
        ddf = dd.from_pandas(df, npartitions=10)
        
        # 分布式计算聚合
        agg = ddf.groupby('category').agg({
            'x': ['mean', 'std'],
            'y': ['mean', 'std'],
            'value': ['mean', 'count']
        }).compute()
        
        # 展平列名
        agg.columns = ['_'.join(col).strip() for col in agg.columns.values]
        
        print("Dask聚合结果:")
        print(agg)
        
        # 可视化聚合结果
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        # 均值散点图
        axes[0].scatter(agg['x_mean'], agg['y_mean'], s=agg['value_count'], alpha=0.7)
        axes[0].set_title('类别均值散点图')
        axes[0].set_xlabel('x_mean')
        axes[0].set_ylabel('y_mean')
        
        # 条形图
        agg.plot.bar(y='value_count', ax=axes[1])
        axes[1].set_title('类别计数')
        axes[1].set_ylabel('计数')
        
        plt.tight_layout()
        plt.show()
        
    except ImportError:
        print("Dask未安装，跳过Dask可视化演示")
    
    return df, random_sample, stratified_sample

# 运行示例
def demo_big_data_processing():
    """演示大数据处理框架"""
    print("=== Python大数据处理框架演示 ===")
    
    # 1. 大数据处理框架比较
    results = compare_big_data_frameworks()
    
    # 2. 数据库集成
    df, agg_result = database_integration()
    
    # 3. 可视化优化
    df, random_sample, stratified_sample = optimized_visualization()
    
    print("\n所有大数据处理框架演示完成!")

# 运行演示
if __name__ == "__main__":
    demo_big_data_processing()
```

## 3. 高级数据可视化

### 3.1 交互式数据可视化

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
import warnings
warnings.filterwarnings('ignore')

# 交互式图表基础
def interactive_visualization_basics():
    """交互式图表基础"""
    print("=== 交互式图表基础 ===")
    
    # 创建示例数据
    np.random.seed(42)
    n = 500
    df = pd.DataFrame({
        'x': np.random.randn(n),
        'y': np.random.randn(n),
        'color': np.random.choice(['A', 'B', 'C', 'D'], n),
        'size': np.random.randint(10, 100, n)
    })
    
    # 1. 使用Plotly Express创建交互式散点图
    fig = px.scatter(
        df, 
        x='x', 
        y='y', 
        color='color',
        size='size',
        hover_data=['x', 'y', 'color', 'size'],
        title='交互式散点图',
        labels={'x': 'X轴', 'y': 'Y轴', 'color': '类别', 'size': '大小'}
    )
    
    fig.update_layout(
        hovermode='closest',
        width=800,
        height=600
    )
    
    # 在Jupyter环境中显示
    # fig.show()
    
    # 保存为HTML文件
    fig.write_html("interactive_scatter.html")
    print("交互式散点图已保存为 interactive_scatter.html")
    
    # 2. 创建交互式线图
    times = pd.date_range('2020-01-01', periods=100, freq='D')
    values = np.cumsum(np.random.randn(100))
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=times,
        y=values,
        mode='lines+markers',
        name='时间序列',
        line=dict(color='blue', width=2),
        marker=dict(size=5)
    ))
    
    fig.update_layout(
        title='交互式时间序列',
        xaxis_title='日期',
        yaxis_title='值',
        hovermode='x unified'
    )
    
    fig.write_html("interactive_timeseries.html")
    print("交互式时间序列图已保存为 interactive_timeseries.html")
    
    # 3. 创建交互式条形图
    categories = ['A', 'B', 'C', 'D', 'E']
    values = np.random.randint(10, 100, len(categories))
    
    fig = px.bar(
        x=categories,
        y=values,
        labels={'x': '类别', 'y': '值'},
        title='交互式条形图',
        color=values,
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(
        coloraxis_showscale=False,
        xaxis_title='类别',
        yaxis_title='值'
    )
    
    fig.write_html("interactive_bar.html")
    print("交互式条形图已保存为 interactive_bar.html")
    
    return df

# 高级交互式图表
def advanced_interactive_charts():
    """高级交互式图表"""
    print("\n=== 高级交互式图表 ===")
    
    # 创建复杂数据集
    np.random.seed(42)
    n = 1000
    
    # 时间序列数据
    dates = pd.date_range('2020-01-01', periods=n, freq='D')
    trend = np.linspace(100, 200, n)
    seasonal = 10 * np.sin(np.linspace(0, 20 * np.pi, n))
    noise = np.random.normal(0, 5, n)
    values = trend + seasonal + noise
    
    ts_df = pd.DataFrame({
        'date': dates,
        'value': values,
        'category': np.random.choice(['A', 'B', 'C'], n)
    })
    
    # 1. 多条时间序列
    fig = go.Figure()
    
    for category in ts_df['category'].unique():
        cat_data = ts_df[ts_df['category'] == category]
        fig.add_trace(go.Scatter(
            x=cat_data['date'],
            y=cat_data['value'],
            mode='lines',
            name=f'类别 {category}',
            line=dict(width=1.5)
        ))
    
    fig.update_layout(
        title='多条时间序列',
        xaxis_title='日期',
        yaxis_title='值',
        hovermode='x unified'
    )
    
    fig.write_html("multi_timeseries.html")
    print("多条时间序列图已保存为 multi_timeseries.html")
    
    # 2. 3D散点图
    np.random.seed(42)
    df_3d = pd.DataFrame({
        'x': np.random.randn(500),
        'y': np.random.randn(500),
        'z': np.random.randn(500),
        'category': np.random.choice(['A', 'B', 'C', 'D'], 500),
        'size': np.random.randint(5, 20, 500)
    })
    
    fig = px.scatter_3d(
        df_3d,
        x='x',
        y='y',
        z='z',
        color='category',
        size='size',
        title='3D散点图',
        labels={'x': 'X轴', 'y': 'Y轴', 'z': 'Z轴'}
    )
    
    fig.write_html("3d_scatter.html")
    print("3D散点图已保存为 3d_scatter.html")
    
    # 3. 热力图
    corr_data = np.random.randn(10, 10)
    categories = [f'Cat_{i}' for i in range(10)]
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_data,
        x=categories,
        y=categories,
        colorscale='viridis',
        showscale=True
    ))
    
    fig.update_layout(
        title='相关系数热力图',
        xaxis_title='变量',
        yaxis_title='变量'
    )
    
    fig.write_html("heatmap.html")
    print("热力图已保存为 heatmap.html")
    
    # 4. 子图组合
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('散点图', '直方图', '箱线图', '小提琴图'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # 散点图
    fig.add_trace(
        go.Scatter(x=df_3d['x'], y=df_3d['y'], mode='markers'),
        row=1, col=1
    )
    
    # 直方图
    fig.add_trace(
        go.Histogram(x=df_3d['x']),
        row=1, col=2
    )
    
    # 箱线图
    fig.add_trace(
        go.Box(y=df_3d['y']),
        row=2, col=1
    )
    
    # 小提琴图
    fig.add_trace(
        go.Violin(y=df_3d['z']),
        row=2, col=2
    )
    
    fig.update_layout(
        title_text="多种图表类型组合",
        showlegend=False,
        height=700
    )
    
    fig.write_html("subplots.html")
    print("子图组合已保存为 subplots.html")
    
    return ts_df, df_3d

# 交互式仪表板
def interactive_dashboard():
    """创建交互式仪表板"""
    print("\n=== 创建交互式仪表板 ===")
    
    # 生成示例数据
    np.random.seed(42)
    n = 1000
    
    # 销售数据
    dates = pd.date_range('2020-01-01', periods=n, freq='D')
    products = ['产品A', '产品B', '产品C', '产品D']
    regions = ['华东', '华北', '华南', '西部']
    
    sales_df = pd.DataFrame({
        'date': dates,
        'product': np.random.choice(products, n),
        'region': np.random.choice(regions, n),
        'sales': np.random.randint(100, 1000, n),
        'profit': np.random.randint(10, 100, n),
        'customers': np.random.randint(10, 100, n)
    })
    
    # 创建仪表板
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=('销售趋势', '产品销售分布', '区域销售对比', '利润率趋势', '客户数量', '产品利润率'),
        specs=[[{"secondary_y": False}, {"type": "pie"}],
               [{"type": "bar"}, {"secondary_y": True}],
               [{"type": "bar"}, {"type": "box"}]]
    )
    
    # 1. 销售趋势
    daily_sales = sales_df.groupby('date')['sales'].sum().reset_index()
    fig.add_trace(
        go.Scatter(
            x=daily_sales['date'],
            y=daily_sales['sales'],
            mode='lines',
            name='每日销售额',
            line=dict(color='blue')
        ),
        row=1, col=1
    )
    
    # 2. 产品销售分布（饼图）
    product_sales = sales_df.groupby('product')['sales'].sum().reset_index()
    fig.add_trace(
        go.Pie(
            labels=product_sales['product'],
            values=product_sales['sales'],
            name="产品销售分布"
        ),
        row=1, col=2
    )
    
    # 3. 区域销售对比（条形图）
    region_sales = sales_df.groupby('region')['sales'].sum().reset_index()
    fig.add_trace(
        go.Bar(
            x=region_sales['region'],
            y=region_sales['sales'],
            name='区域销售额',
            marker_color='green'
        ),
        row=2, col=1
    )
    
    # 4. 利润率趋势
    daily_profit = sales_df.groupby('date')['profit'].sum().reset_index()
    fig.add_trace(
        go.Scatter(
            x=daily_profit['date'],
            y=daily_profit['profit'],
            mode='lines',
            name='每日利润',
            line=dict(color='red')
        ),
        row=2, col=2
    )
    
    # 5. 客户数量
    daily_customers = sales_df.groupby('date')['customers'].sum().reset_index()
    fig.add_trace(
        go.Bar(
            x=daily_customers['date'],
            y=daily_customers['customers'],
            name='每日客户数',
            marker_color='purple'
        ),
        row=3, col=1
    )
    
    # 6. 产品利润率（箱线图）
    for i, product in enumerate(products):
        product_data = sales_df[sales_df['product'] == product]
        profit_rate = product_data['profit'] / product_data['sales'] * 100
        
        fig.add_trace(
            go.Box(
                y=profit_rate,
                name=product
            ),
            row=3, col=2
        )
    
    # 更新布局
    fig.update_layout(
        title_text="销售数据交互式仪表板",
        height=1200,
        showlegend=False
    )
    
    fig.write_html("dashboard.html")
    print("交互式仪表板已保存为 dashboard.html")
    
    return sales_df

# 动态可视化
def dynamic_visualizations():
    """动态可视化"""
    print("\n=== 动态可视化 ===")
    
    # 创建动画数据
    np.random.seed(42)
    n = 100
    frames = 50
    
    # 生成随时间变化的数据
    data = []
    for frame in range(frames):
        # 随机游走
        if frame == 0:
            x, y = 0, 0
        else:
            x, y = data[-1]['x'], data[-1]['y']
            x += np.random.randn() * 0.5
            y += np.random.randn() * 0.5
        
        data.append({
            'frame': frame,
            'x': x,
            'y': y,
            'category': np.random.choice(['A', 'B', 'C']),
            'size': 10 + frame * 2
        })
    
    df_anim = pd.DataFrame(data)
    
    # 创建动画散点图
    fig = px.scatter(
        df_anim,
        x='x',
        y='y',
        animation_frame='frame',
        color='category',
        size='size',
        range_x=[-10, 10],
        range_y=[-10, 10],
        title='动态散点图'
    )
    
    fig.write_html("animation_scatter.html")
    print("动态散点图已保存为 animation_scatter.html")
    
    # 创建随时间变化的条形图
    categories = ['A', 'B', 'C', 'D', 'E']
    bar_data = []
    
    for frame in range(frames):
        for category in categories:
            bar_data.append({
                'frame': frame,
                'category': category,
                'value': np.random.randint(10, 100)
            })
    
    df_bar = pd.DataFrame(bar_data)
    
    fig = px.bar(
        df_bar,
        x='category',
        y='value',
        animation_frame='frame',
        color='category',
        range_y=[0, 120],
        title='动态条形图'
    )
    
    fig.write_html("animation_bar.html")
    print("动态条形图已保存为 animation_bar.html")
    
    # 创建随时间变化的热力图
    matrix_data = []
    
    for frame in range(frames):
        for i in range(10):
            for j in range(10):
                matrix_data.append({
                    'frame': frame,
                    'x': i,
                    'y': j,
                    'value': np.random.rand()
                })
    
    df_matrix = pd.DataFrame(matrix_data)
    
    fig = px.imshow(
        df_matrix.pivot_table(index='y', columns='x', values='value', aggfunc='mean'),
        animation_frame=df_matrix['frame'].unique(),
        color_continuous_scale='viridis',
        title='动态热力图'
    )
    
    fig.write_html("animation_heatmap.html")
    print("动态热力图已保存为 animation_heatmap.html")
    
    return df_anim, df_bar, df_matrix

# 运行示例
def demo_interactive_visualization():
    """演示交互式数据可视化"""
    print("=== 交互式数据可视化演示 ===")
    
    # 1. 交互式图表基础
    df = interactive_visualization_basics()
    
    # 2. 高级交互式图表
    ts_df, df_3d = advanced_interactive_charts()
    
    # 3. 交互式仪表板
    sales_df = interactive_dashboard()
    
    # 4. 动态可视化
    df_anim, df_bar, df_matrix = dynamic_visualizations()
    
    print("\n所有交互式可视化演示完成!")
    print("生成的HTML文件:")
    print("- interactive_scatter.html")
    print("- interactive_timeseries.html")
    print("- interactive_bar.html")
    print("- multi_timeseries.html")
    print("- 3d_scatter.html")
    print("- heatmap.html")
    print("- subplots.html")
    print("- dashboard.html")
    print("- animation_scatter.html")
    print("- animation_bar.html")
    print("- animation_heatmap.html")

# 运行演示
if __name__ == "__main__":
    demo_interactive_visualization()
```

这份Python数据处理与分析高级指南涵盖了Pandas高级应用与性能优化、大数据处理框架（如Dask）以及高级数据可视化技术。通过这份指南，您可以掌握处理大型数据集的技能，使用高效的数据处理技术，并创建交互式、动态的数据可视化图表，使数据分析更加深入和直观。