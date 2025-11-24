# 7. Spark MLlib机器学习库

## 7.1 MLlib概述

MLlib是Apache Spark的机器学习库，提供了丰富的机器学习算法和实用工具。它支持分类、回归、聚类、协同过滤、降维等常见的机器学习任务，并且与Spark生态系统无缝集成，能够在大规模数据上高效运行。

### 7.1.1 MLlib架构与特点

MLlib具有以下主要特点：

1. **分布式计算**：基于Spark的分布式计算能力，可处理大规模数据
2. **高性能**：利用内存计算和迭代优化的优势，提供高效的算法实现
3. **易用性**：提供高级API，支持Python、Java、Scala和R语言
4. **Pipeline支持**：支持构建、评估和调优机器学习Pipeline
5. **模型持久化**：支持模型的保存和加载，便于生产环境部署

**代码示例：查看MLlib基本信息**

```python
# code/mlib-examples/mllib_info.py
from pyspark import SparkContext
from pyspark.sql import SparkSession
import inspect

def mllib_info():
    # 创建SparkSession
    spark = SparkSession.builder.appName("MLlibInfo").getOrCreate()
    
    # 查看MLlib版本
    print(f"Spark版本: {spark.version}")
    
    # 导入主要的MLlib模块
    from pyspark.ml import Pipeline, PipelineModel
    from pyspark.ml.feature import VectorAssembler, StandardScaler
    from pyspark.ml.classification import LogisticRegression, RandomForestClassifier
    from pyspark.ml.regression import LinearRegression, RandomForestRegressor
    from pyspark.ml.clustering import KMeans
    from pyspark.ml.evaluation import BinaryClassificationEvaluator, RegressionEvaluator
    from pyspark.ml.tuning import ParamGridBuilder, CrossValidator
    
    # 列出可用的算法
    algorithms = [
        "分类算法:",
        "- LogisticRegression",
        "- RandomForestClassifier",
        "- DecisionTreeClassifier",
        "- NaiveBayes",
        "- SVM",
        "\n回归算法:",
        "- LinearRegression",
        "- RandomForestRegressor",
        "- DecisionTreeRegressor",
        "- GBTRegressor",
        "\n聚类算法:",
        "- KMeans",
        "- GaussianMixture",
        "- BisectingKMeans",
        "- LDA",
        "\n特征工程:",
        "- VectorAssembler",
        "- StandardScaler",
        "- MinMaxScaler",
        "- PCA",
        "- Word2Vec",
        "- Tokenizer",
        "\n模型评估:",
        "- BinaryClassificationEvaluator",
        "- MulticlassClassificationEvaluator",
        "- RegressionEvaluator",
        "- ClusteringEvaluator"
    ]
    
    print("\nMLlib主要算法:")
    for algo in algorithms:
        print(algo)
    
    spark.stop()

if __name__ == "__main__":
    mllib_info()
```

## 7.2 MLlib数据类型

MLlib使用特定的数据类型表示机器学习所需的数据结构和模型。

### 7.2.1 向量类型

MLlib支持两种主要的向量类型：密集向量和稀疏向量。

```python
# code/mlib-examples/vector_types.py
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.ml.linalg import Vectors

def vector_types():
    # 创建SparkSession
    spark = SparkSession.builder.appName("VectorTypes").getOrCreate()
    
    # 密集向量
    dense_vector = Vectors.dense([1.0, 2.0, 3.0, 4.0])
    print(f"密集向量: {dense_vector}")
    print(f"向量大小: {dense_vector.size}")
    print(f"向量类型: {type(dense_vector)}")
    
    # 稀疏向量
    # 参数: 向量大小, 非零元素索引, 非零元素值
    sparse_vector = Vectors.sparse(5, [0, 2, 4], [1.0, 3.0, 5.0])
    print(f"\n稀疏向量: {sparse_vector}")
    print(f"向量大小: {sparse_vector.size}")
    print(f"非零元素数量: {sparse_vector.numNonzeros}")
    
    # 访问向量元素
    print(f"\n访问密集向量元素:")
    print(f"第一个元素: {dense_vector[0]}")
    print(f"最后一个元素: {dense_vector[3]}")
    
    print(f"\n访问稀疏向量元素:")
    print(f"第一个元素: {sparse_vector[0]}")
    print(f"第三个元素: {sparse_vector[2]}")
    print(f"第四个元素(0): {sparse_vector[3]}")  # 应该是0，因为我们没有设置这个值
    
    # 向量运算
    dot_product = dense_vector.dot(Vectors.dense([1.0, 1.0, 1.0, 1.0]))
    print(f"\n密集向量点积(1,1,1,1): {dot_product}")
    
    # 创建DataFrame并应用向量
    data = [
        (1, Vectors.dense([2.0, 3.0])),
        (2, Vectors.sparse(2, [0, 1], [4.0, 5.0])),
        (3, Vectors.dense([6.0, 7.0]))
    ]
    
    df = spark.createDataFrame(data, ["id", "features"])
    print(f"\n包含向量的DataFrame:")
    df.show(truncate=False)
    df.printSchema()
    
    spark.stop()

if __name__ == "__main__":
    vector_types()
```

### 7.2.2 标签点类型

标签点是用于监督学习的基本数据结构，包含特征向量和对应的标签。

```python
# code/mlib-examples/labeled_point.py
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.ml.linalg import Vectors

def labeled_point():
    # 创建SparkSession
    spark = SparkSession.builder.appName("LabeledPoint").getOrCreate()
    
    # 创建监督学习数据
    # 格式: (标签, 特征向量)
    classification_data = [
        (0.0, Vectors.dense([2.0, 3.0, 1.0])),
        (1.0, Vectors.dense([5.0, 6.0, 2.0])),
        (0.0, Vectors.dense([1.0, 2.0, 1.0])),
        (1.0, Vectors.dense([8.0, 9.0, 3.0])),
        (0.0, Vectors.dense([3.0, 3.0, 1.5])),
        (1.0, Vectors.dense([7.0, 8.0, 2.5]))
    ]
    
    regression_data = [
        (25.5, Vectors.dense([1.0, 2.0])),
        (42.3, Vectors.dense([2.0, 3.0])),
        (38.7, Vectors.dense([1.5, 2.8])),
        (55.2, Vectors.dense([3.0, 4.5])),
        (30.1, Vectors.dense([1.2, 2.5]))
    ]
    
    # 创建DataFrame
    classification_df = spark.createDataFrame(classification_data, ["label", "features"])
    regression_df = spark.createDataFrame(regression_data, ["label", "features"])
    
    print("分类数据:")
    classification_df.show(truncate=False)
    classification_df.printSchema()
    
    print("\n回归数据:")
    regression_df.show(truncate=False)
    regression_df.printSchema()
    
    # 数据统计
    print("\n分类数据统计:")
    classification_df.describe().show()
    
    print("\n回归数据统计:")
    regression_df.describe().show()
    
    spark.stop()

if __name__ == "__main__":
    labeled_point()
```

## 7.3 特征工程

特征工程是机器学习中的重要环节，MLlib提供了丰富的特征处理和转换工具。

### 7.3.1 特征提取与转换

```python
# code/mlib-examples/feature_extraction.py
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.ml.linalg import Vectors
from pyspark.ml.feature import (
    Tokenizer, HashingTF, IDF, Word2Vec,
    VectorAssembler, StandardScaler, MinMaxScaler,
    PCA, PolynomialExpansion, OneHotEncoder, 
    StringIndexer
)

def feature_extraction():
    # 创建SparkSession
    spark = SparkSession.builder.appName("FeatureExtraction").getOrCreate()
    
    # 文本特征提取
    print("=== 文本特征提取 ===")
    
    # 创建文本数据
    text_data = [
        (1, "Apache Spark is a fast cluster computing system"),
        (2, "Machine learning with Spark MLlib"),
        (3, "Spark SQL and DataFrames"),
        (4, "Spark Streaming for real-time data processing"),
        (5, "GraphX for graph processing with Spark")
    ]
    
    text_df = spark.createDataFrame(text_data, ["id", "text"])
    print("原始文本数据:")
    text_df.show(truncate=False)
    
    # 分词
    tokenizer = Tokenizer(inputCol="text", outputCol="words")
    words_df = tokenizer.transform(text_df)
    print("分词结果:")
    words_df.select("id", "words").show(truncate=False)
    
    # 词频统计 (TF)
    hashingTF = HashingTF(inputCol="words", outputCol="rawFeatures", numFeatures=100)
    tf_df = hashingTF.transform(words_df)
    print("TF特征:")
    tf_df.select("id", "rawFeatures").show(truncate=False)
    
    # TF-IDF
    idf = IDF(inputCol="rawFeatures", outputCol="features")
    idf_model = idf.fit(tf_df)
    tfidf_df = idf_model.transform(tf_df)
    print("TF-IDF特征:")
    tfidf_df.select("id", "features").show(truncate=False)
    
    # Word2Vec
    word2vec = Word2Vec(vectorSize=3, minCount=0, inputCol="words", outputCol="word2vec")
    model = word2vec.fit(words_df)
    w2v_df = model.transform(words_df)
    print("Word2Vec特征:")
    w2v_df.select("id", "word2vec").show(truncate=False)
    
    # 数值特征处理
    print("\n=== 数值特征处理 ===")
    
    # 创建数值数据
    numeric_data = [
        (1, 18.0, 1.68, 55.0, "A"),
        (2, 25.0, 1.75, 70.0, "B"),
        (3, 32.0, 1.62, 48.0, "A"),
        (4, 41.0, 1.80, 85.0, "C"),
        (5, 28.0, 1.70, 62.0, "B")
    ]
    
    numeric_df = spark.createDataFrame(numeric_data, ["id", "age", "height", "weight", "category"])
    print("原始数值数据:")
    numeric_df.show()
    
    # 类别特征转换
    string_indexer = StringIndexer(inputCol="category", outputCol="category_index")
    si_model = string_indexer.fit(numeric_df)
    indexed_df = si_model.transform(numeric_df)
    print("类别特征索引化:")
    indexed_df.select("id", "category", "category_index").show()
    
    # One-Hot编码
    encoder = OneHotEncoder(inputCol="category_index", outputCol="category_vec")
    encoded_df = encoder.fit(indexed_df).transform(indexed_df)
    print("One-Hot编码:")
    encoded_df.select("id", "category_index", "category_vec").show()
    
    # 向量化多个数值特征
    assembler = VectorAssembler(
        inputCols=["age", "height", "weight"],
        outputCol="features"
    )
    assembled_df = assembler.transform(numeric_df)
    print("向量化特征:")
    assembled_df.select("id", "features").show(truncate=False)
    
    # 标准化
    scaler = StandardScaler(inputCol="features", outputCol="scaled_features")
    scaler_model = scaler.fit(assembled_df)
    scaled_df = scaler_model.transform(assembled_df)
    print("标准化特征:")
    scaled_df.select("id", "features", "scaled_features").show(truncate=False)
    
    # 归一化
    minmax_scaler = MinMaxScaler(inputCol="features", outputCol="normalized_features")
    minmax_model = minmax_scaler.fit(assembled_df)
    normalized_df = minmax_model.transform(assembled_df)
    print("归一化特征:")
    normalized_df.select("id", "features", "normalized_features").show(truncate=False)
    
    # 降维 (PCA)
    pca = PCA(k=2, inputCol="scaled_features", outputCol="pca_features")
    pca_model = pca.fit(scaled_df)
    pca_df = pca_model.transform(scaled_df)
    print("PCA降维特征:")
    pca_df.select("id", "pca_features").show(truncate=False)
    
    # 多项式扩展
    poly = PolynomialExpansion(degree=2, inputCol="features", outputCol="poly_features")
    poly_df = poly.transform(assembled_df)
    print("多项式扩展特征:")
    poly_df.select("id", "features", "poly_features").show(truncate=False)
    
    spark.stop()

if __name__ == "__main__":
    feature_extraction()
```

### 7.3.2 特征选择

```python
# code/mlib-examples/feature_selection.py
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, ChiSqSelector, UnivariateFeatureSelector
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.linalg import Vectors

def feature_selection():
    # 创建SparkSession
    spark = SparkSession.builder.appName("FeatureSelection").getOrCreate()
    
    # 创建示例数据 - 特征和标签
    data = [
        (1.0, Vectors.dense([2.0, 3.0, 4.0, 5.0, 1.0])),
        (0.0, Vectors.dense([1.0, 1.0, 2.0, 1.0, 1.0])),
        (1.0, Vectors.dense([5.0, 4.0, 3.0, 2.0, 1.0])),
        (0.0, Vectors.dense([2.0, 1.0, 1.0, 1.0, 2.0])),
        (1.0, Vectors.dense([3.0, 4.0, 4.0, 3.0, 1.0])),
        (0.0, Vectors.dense([1.0, 2.0, 1.0, 1.0, 3.0])),
        (1.0, Vectors.dense([4.0, 5.0, 5.0, 4.0, 1.0])),
        (0.0, Vectors.dense([1.0, 1.0, 2.0, 1.0, 2.0])),
        (1.0, Vectors.dense([5.0, 4.0, 4.0, 5.0, 1.0])),
        (0.0, Vectors.dense([2.0, 2.0, 1.0, 1.0, 3.0]))
    ]
    
    df = spark.createDataFrame(data, ["label", "features"])
    print("原始数据:")
    df.show(truncate=False)
    
    # 方法1: ChiSqSelector - 基于卡方检验的特征选择
    print("\n=== 卡方检验特征选择 ===")
    
    chi_selector = ChiSqSelector(numTopFeatures=3, featuresCol="features", 
                               outputCol="selected_features", labelCol="label")
    chi_model = chi_selector.fit(df)
    chi_result = chi_model.transform(df)
    
    print("选择后的特征:")
    chi_result.select("label", "features", "selected_features").show(truncate=False)
    
    # 获取选择的特征索引
    selected_indices = chi_model.selectedFeatures
    print(f"选择的特征索引: {selected_indices}")
    
    # 方法2: UnivariateFeatureSelector - 基于统计检验的特征选择
    print("\n=== 单变量统计特征选择 ===")
    
    univariate_selector = UnivariateFeatureSelector(
        featuresCol="features", 
        outputCol="selected_features",
        labelCol="label",
        selectionMode="numTopFeatures"
    ).setFeatureType("continuous").setLabelType("categorical").setSelectionThreshold(3)
    
    univariate_model = univariate_selector.fit(df)
    univariate_result = univariate_model.transform(df)
    
    print("选择后的特征:")
    univariate_result.select("label", "features", "selected_features").show(truncate=False)
    
    # 方法3: 基于模型权重的特征选择
    print("\n=== 基于模型权重的特征选择 ===")
    
    # 训练逻辑回归模型
    lr = LogisticRegression(featuresCol="features", labelCol="label")
    lr_model = lr.fit(df)
    
    # 获取模型权重
    coefficients = lr_model.coefficients.toArray()
    print(f"模型权重: {coefficients}")
    
    # 选择权重绝对值较大的特征
    threshold = 0.1
    important_features = [i for i, coef in enumerate(coefficients) if abs(coef) > threshold]
    print(f"重要特征索引 (阈值={threshold}): {important_features}")
    
    # 方法4: 相关性特征选择
    print("\n=== 相关性特征选择 ===")
    
    # 将向量分解为单独的特征列
    feature_cols = ["f1", "f2", "f3", "f4", "f5"]
    
    # 将向量转换为多个单独的列
    from pyspark.sql.functions import udf
    from pyspark.sql.types import ArrayType, DoubleType
    
    extract_vector = udf(lambda vector: vector.toArray().tolist(), ArrayType(DoubleType()))
    expanded_df = df.withColumn("feature_array", extract_vector("features"))
    
    for i, col_name in enumerate(feature_cols):
        expanded_df = expanded_df.withColumn(col_name, expanded_df["feature_array"].getItem(i))
    
    print("扩展后的特征:")
    expanded_df.select("label", *feature_cols).show()
    
    # 计算特征与标签的相关性
    from pyspark.ml.stat import Correlation
    
    # 创建包含所有特征和标签的DataFrame
    assembler = VectorAssembler(inputCols=["label"] + feature_cols, outputCol="all_features")
    all_features_df = assembler.transform(expanded_df)
    
    # 计算相关矩阵
    corr_matrix = Correlation.corr(all_features_df, "all_features").head()[0].toArray()
    
    print("相关矩阵:")
    for row in corr_matrix:
        print([round(val, 3) for val in row])
    
    # 选择与标签相关性高的特征
    label_corr = [abs(corr_matrix[0, i]) for i in range(1, corr_matrix.shape[0])]
    top_features = sorted([(feature_cols[i], label_corr[i]) for i in range(len(label_corr))], 
                         key=lambda x: x[1], reverse=True)
    
    print("特征与标签的相关性:")
    for feature, corr in top_features:
        print(f"{feature}: {corr:.4f}")
    
    spark.stop()

if __name__ == "__main__":
    feature_selection()
```

## 7.4 分类算法

分类是监督学习的一种，目标是预测离散的类别标签。MLlib提供了多种分类算法。

### 7.4.1 逻辑回归

```python
# code/mlib-examples/logistic_regression.py
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml import Pipeline

def logistic_regression_example():
    # 创建SparkSession
    spark = SparkSession.builder.appName("LogisticRegression").getOrCreate()
    
    # 创建示例数据
    data = [
        # 特征: [年龄, 收入, 教育年数], 标签: 是否购买 (1=是, 0=否)
        (23, 30000, 12, 0),
        (45, 80000, 16, 1),
        (31, 50000, 14, 1),
        (25, 35000, 12, 0),
        (38, 75000, 16, 1),
        (28, 40000, 14, 0),
        (52, 95000, 18, 1),
        (33, 55000, 14, 1),
        (26, 38000, 12, 0),
        (41, 70000, 16, 1),
        (30, 45000, 14, 0),
        (35, 60000, 15, 1),
        (27, 36000, 12, 0),
        (48, 85000, 17, 1),
        (29, 42000, 14, 0)
    ]
    
    columns = ["age", "income", "education", "label"]
    df = spark.createDataFrame(data, columns)
    
    print("原始数据:")
    df.show()
    
    # 特征工程
    # 将特征列合并为单个特征向量
    assembler = VectorAssembler(
        inputCols=["age", "income", "education"],
        outputCol="features"
    )
    
    # 标准化特征
    scaler = StandardScaler(
        inputCol="features",
        outputCol="scaled_features"
    )
    
    # 逻辑回归模型
    lr = LogisticRegression(
        featuresCol="scaled_features",
        labelCol="label",
        maxIter=10,
        regParam=0.01,
        elasticNetParam=0.8
    )
    
    # 构建Pipeline
    pipeline = Pipeline(stages=[assembler, scaler, lr])
    
    # 划分训练集和测试集
    train_data, test_data = df.randomSplit([0.8, 0.2], seed=42)
    
    # 训练模型
    print("\n训练模型...")
    model = pipeline.fit(train_data)
    
    # 在测试集上进行预测
    print("\n在测试集上进行预测...")
    predictions = model.transform(test_data)
    
    # 查看预测结果
    print("预测结果:")
    predictions.select("age", "income", "education", "label", "probability", "prediction").show()
    
    # 评估模型性能
    evaluator = BinaryClassificationEvaluator(rawPredictionCol="rawPrediction", labelCol="label")
    auc = evaluator.evaluate(predictions)
    print(f"\n模型AUC: {auc:.4f}")
    
    # 查看模型参数
    lr_model = model.stages[-1]
    print(f"\n模型系数: {lr_model.coefficients}")
    print(f"模型截距: {lr_model.intercept}")
    
    # 模型总结
    print("\n模型总结:")
    summary = lr_model.summary
    print(f"准确率: {summary.accuracy:.4f}")
    print(f"精确率(Positive): {summary.precisionByLabel[1]:.4f}")
    print(f"召回率(Positive): {summary.recallByLabel[1]:.4f}")
    print(f"F1分数(Positive): {summary.fMeasureByLabel()[1]:.4f}")
    
    spark.stop()

if __name__ == "__main__":
    logistic_regression_example()
```

### 7.4.2 随机森林

```python
# code/mlib-examples/random_forest.py
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, StringIndexer, OneHotEncoder
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml import Pipeline

def random_forest_example():
    # 创建SparkSession
    spark = SparkSession.builder.appName("RandomForest").getOrCreate()
    
    # 创建示例数据
    data = [
        # 特征: [年龄, 收入, 教育年数, 性别], 标签: 产品类别
        (23, 30000, 12, "M", "A"),
        (45, 80000, 16, "F", "B"),
        (31, 50000, 14, "M", "B"),
        (25, 35000, 12, "F", "A"),
        (38, 75000, 16, "M", "B"),
        (28, 40000, 14, "F", "A"),
        (52, 95000, 18, "M", "C"),
        (33, 55000, 14, "M", "B"),
        (26, 38000, 12, "F", "A"),
        (41, 70000, 16, "F", "B"),
        (30, 45000, 14, "M", "A"),
        (35, 60000, 15, "F", "B"),
        (27, 36000, 12, "M", "A"),
        (48, 85000, 17, "F", "C"),
        (29, 42000, 14, "M", "A"),
        (36, 65000, 16, "F", "B"),
        (32, 58000, 15, "M", "B"),
        (24, 32000, 12, "F", "A"),
        (46, 88000, 17, "M", "C"),
        (39, 72000, 16, "F", "B")
    ]
    
    columns = ["age", "income", "education", "gender", "category"]
    df = spark.createDataFrame(data, columns)
    
    print("原始数据:")
    df.show()
    
    # 特征工程
    # 将类别特征转换为数值
    gender_indexer = StringIndexer(inputCol="gender", outputCol="gender_index")
    gender_encoder = OneHotEncoder(inputCol="gender_index", outputCol="gender_vec")
    
    # 将标签转换为数值
    label_indexer = StringIndexer(inputCol="category", outputCol="label")
    
    # 将特征合并为向量
    assembler = VectorAssembler(
        inputCols=["age", "income", "education", "gender_vec"],
        outputCol="features"
    )
    
    # 随机森林分类器
    rf = RandomForestClassifier(
        featuresCol="features",
        labelCol="label",
        numTrees=10,
        maxDepth=5,
        seed=42
    )
    
    # 构建Pipeline
    pipeline = Pipeline(stages=[
        gender_indexer, gender_encoder, label_indexer, assembler, rf
    ])
    
    # 划分训练集和测试集
    train_data, test_data = df.randomSplit([0.7, 0.3], seed=42)
    
    # 训练模型
    print("\n训练模型...")
    model = pipeline.fit(train_data)
    
    # 在测试集上进行预测
    print("\n在测试集上进行预测...")
    predictions = model.transform(test_data)
    
    # 查看预测结果
    print("预测结果:")
    predictions.select("age", "income", "education", "gender", "category", 
                      "probability", "prediction").show()
    
    # 评估模型性能
    evaluator = MulticlassClassificationEvaluator(
        predictionCol="prediction", 
        labelCol="label"
    )
    
    accuracy = evaluator.evaluate(predictions, {evaluator.metricName: "accuracy"})
    precision = evaluator.evaluate(predictions, {evaluator.metricName: "weightedPrecision"})
    recall = evaluator.evaluate(predictions, {evaluator.metricName: "weightedRecall"})
    f1 = evaluator.evaluate(predictions, {evaluator.metricName: "f1"})
    
    print(f"\n准确率: {accuracy:.4f}")
    print(f"精确率: {precision:.4f}")
    print(f"召回率: {recall:.4f}")
    print(f"F1分数: {f1:.4f}")
    
    # 查看特征重要性
    rf_model = model.stages[-1]
    feature_importances = rf_model.featureImportances
    
    print("\n特征重要性:")
    feature_names = ["age", "income", "education", "gender_vec"]
    for name, importance in zip(feature_names, feature_importances):
        print(f"{name}: {importance:.4f}")
    
    spark.stop()

if __name__ == "__main__":
    random_forest_example()
```

## 7.5 回归算法

回归是监督学习的另一种形式，目标是预测连续的数值。

### 7.5.1 线性回归

```python
# code/mlib-examples/linear_regression.py
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml import Pipeline

def linear_regression_example():
    # 创建SparkSession
    spark = SparkSession.builder.appName("LinearRegression").getOrCreate()
    
    # 创建示例数据
    data = [
        # 特征: [年龄, 教育年数, 工作经验], 标签: 年薪(万元)
        (23, 12, 1, 8.5),
        (25, 14, 2, 10.2),
        (28, 16, 4, 13.5),
        (31, 16, 6, 15.8),
        (35, 18, 8, 18.5),
        (38, 16, 10, 20.3),
        (42, 18, 12, 22.8),
        (45, 20, 15, 26.7),
        (48, 18, 18, 28.5),
        (51, 22, 20, 32.3),
        (26, 14, 3, 11.2),
        (29, 16, 5, 14.7),
        (33, 18, 7, 17.5),
        (36, 18, 9, 19.8),
        (40, 20, 11, 23.5),
        (43, 22, 13, 25.2),
        (46, 20, 16, 27.8),
        (49, 22, 19, 30.5),
        (52, 24, 22, 34.8),
        (27, 15, 3, 12.5),
        (30, 16, 4, 15.0),
        (34, 18, 6, 18.0),
        (37, 19, 8, 20.5),
        (41, 20, 10, 23.0),
        (44, 22, 12, 26.0)
    ]
    
    columns = ["age", "education", "experience", "salary"]
    df = spark.createDataFrame(data, columns)
    
    print("原始数据:")
    df.show()
    
    # 数据统计
    print("\n数据统计:")
    df.describe().show()
    
    # 特征工程
    # 将特征列合并为单个特征向量
    assembler = VectorAssembler(
        inputCols=["age", "education", "experience"],
        outputCol="features"
    )
    
    # 标准化特征
    scaler = StandardScaler(
        inputCol="features",
        outputCol="scaled_features"
    )
    
    # 线性回归模型
    lr = LinearRegression(
        featuresCol="scaled_features",
        labelCol="salary",
        maxIter=100,
        regParam=0.1,
        elasticNetParam=0.8
    )
    
    # 构建Pipeline
    pipeline = Pipeline(stages=[assembler, scaler, lr])
    
    # 划分训练集和测试集
    train_data, test_data = df.randomSplit([0.8, 0.2], seed=42)
    
    # 训练模型
    print("\n训练模型...")
    model = pipeline.fit(train_data)
    
    # 在测试集上进行预测
    print("\n在测试集上进行预测...")
    predictions = model.transform(test_data)
    
    # 查看预测结果
    print("预测结果:")
    predictions.select("age", "education", "experience", "salary", "prediction").show()
    
    # 计算残差
    predictions = predictions.withColumn("residual", 
                                       predictions["salary"] - predictions["prediction"])
    print("残差:")
    predictions.select("salary", "prediction", "residual").show()
    
    # 评估模型性能
    evaluator = RegressionEvaluator(
        predictionCol="prediction", 
        labelCol="salary"
    )
    
    rmse = evaluator.setMetricName("rmse").evaluate(predictions)
    mse = evaluator.setMetricName("mse").evaluate(predictions)
    r2 = evaluator.setMetricName("r2").evaluate(predictions)
    mae = evaluator.setMetricName("mae").evaluate(predictions)
    
    print(f"\n评估指标:")
    print(f"RMSE: {rmse:.4f}")
    print(f"MSE: {mse:.4f}")
    print(f"R²: {r2:.4f}")
    print(f"MAE: {mae:.4f}")
    
    # 查看模型参数
    lr_model = model.stages[-1]
    print(f"\n模型系数: {lr_model.coefficients}")
    print(f"模型截距: {lr_model.intercept}")
    
    # 模型总结
    print("\n模型总结:")
    summary = lr_model.summary
    print(f"训练数据中的样本数: {summary.totalObservations}")
    print(f"模型中的特征数: {summary.degreesOfFreedom}")
    
    print("\n系数标准误差:")
    for name, std_err in zip(["age", "education", "experience"], summary.coefficientStandardErrors):
        print(f"{name}: {std_err:.4f}")
    
    print("\n系数t值:")
    for name, t_val in zip(["age", "education", "experience"], summary.tValues):
        print(f"{name}: {t_val:.4f}")
    
    print("\n系数p值:")
    for name, p_val in zip(["age", "education", "experience"], summary.pValues):
        print(f"{name}: {p_val:.4f}")
    
    spark.stop()

if __name__ == "__main__":
    linear_regression_example()
```

## 7.6 聚类算法

聚类是无监督学习的一种，目标是将相似的数据点分组。

### 7.6.1 K-Means聚类

```python
# code/mlib-examples/kmeans_clustering.py
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator
from pyspark.ml import Pipeline
import numpy as np

def kmeans_clustering_example():
    # 创建SparkSession
    spark = SparkSession.builder.appName("KMeansClustering").getOrCreate()
    
    # 创建示例数据
    # 生成3个聚类中心，每个聚类中心周围有一些数据点
    np.random.seed(42)
    
    # 聚类中心1: (5, 5)
    cluster1 = [(5 + np.random.normal(0, 1), 5 + np.random.normal(0, 1)) for _ in range(20)]
    
    # 聚类中心2: (10, 10)
    cluster2 = [(10 + np.random.normal(0, 1), 10 + np.random.normal(0, 1)) for _ in range(20)]
    
    # 聚类中心3: (15, 5)
    cluster3 = [(15 + np.random.normal(0, 1), 5 + np.random.normal(0, 1)) for _ in range(20)]
    
    # 合并所有数据点
    data = cluster1 + cluster2 + cluster3
    
    # 创建DataFrame
    df = spark.createDataFrame([(x, y) for x, y in data], ["x", "y"])
    
    print("原始数据(前10行):")
    df.show(10)
    
    # 特征工程
    # 将特征合并为向量
    assembler = VectorAssembler(
        inputCols=["x", "y"],
        outputCol="features"
    )
    
    # K-Means聚类
    kmeans = KMeans(featuresCol="features", predictionCol="cluster", k=3, seed=42)
    
    # 构建Pipeline
    pipeline = Pipeline(stages=[assembler, kmeans])
    
    # 训练模型
    print("\n训练K-Means模型...")
    model = pipeline.fit(df)
    
    # 进行预测
    predictions = model.transform(df)
    
    # 查看聚类结果
    print("\n聚类结果:")
    predictions.select("x", "y", "cluster").show(10)
    
    # 聚类中心
    kmeans_model = model.stages[-1]
    centers = kmeans_model.clusterCenters()
    print("\n聚类中心:")
    for i, center in enumerate(centers):
        print(f"聚类 {i}: ({center[0]:.4f}, {center[1]:.4f})")
    
    # 聚类统计
    cluster_counts = predictions.groupBy("cluster").count().orderBy("cluster")
    print("\n每个聚类的样本数:")
    cluster_counts.show()
    
    # 评估聚类质量
    evaluator = ClusteringEvaluator(featuresCol="features", predictionCol="cluster")
    silhouette = evaluator.evaluate(predictions)
    print(f"\n轮廓系数: {silhouette:.4f}")
    
    # 尝试不同的k值，找出最佳的聚类数
    print("\n尝试不同的k值:")
    for k in range(2, 6):
        kmeans_k = KMeans(featuresCol="features", predictionCol="cluster", k=k, seed=42)
        pipeline_k = Pipeline(stages=[assembler, kmeans_k])
        model_k = pipeline_k.fit(df)
        predictions_k = model_k.transform(df)
        silhouette_k = evaluator.evaluate(predictions_k)
        print(f"k={k}: 轮廓系数={silhouette_k:.4f}")
    
    spark.stop()

if __name__ == "__main__":
    kmeans_clustering_example()
```

## 7.7 降维算法

降维用于减少数据的特征数量，同时保留大部分信息。

### 7.7.1 主成分分析(PCA)

```python
# code/mlib-examples/pca.py
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, StandardScaler, PCA
from pyspark.ml import Pipeline
import numpy as np

def pca_example():
    # 创建SparkSession
    spark = SparkSession.builder.appName("PCA").getOrCreate()
    
    # 创建示例数据
    # 生成具有相关性的特征
    np.random.seed(42)
    
    # 创建3个基本特征
    feature1 = np.random.normal(0, 1, 100)
    feature2 = 2 * feature1 + np.random.normal(0, 0.5, 100)  # 与feature1相关
    feature3 = np.random.normal(0, 1, 100)  # 独立特征
    feature4 = 3 * feature3 + np.random.normal(0, 0.3, 100)  # 与feature3相关
    feature5 = -1 * feature1 + np.random.normal(0, 0.4, 100)  # 与feature1负相关
    
    # 创建DataFrame
    data = list(zip(feature1, feature2, feature3, feature4, feature5))
    df = spark.createDataFrame(data, ["f1", "f2", "f3", "f4", "f5"])
    
    print("原始数据(前10行):")
    df.show(10)
    
    # 数据统计
    print("\n原始特征统计:")
    df.describe().show()
    
    # 特征工程
    # 将特征合并为向量
    assembler = VectorAssembler(
        inputCols=["f1", "f2", "f3", "f4", "f5"],
        outputCol="features"
    )
    
    # 标准化特征
    scaler = StandardScaler(
        inputCol="features",
        outputCol="scaled_features"
    )
    
    # PCA降维到2维
    pca = PCA(k=2, inputCol="scaled_features", outputCol="pca_features")
    
    # 构建Pipeline
    pipeline = Pipeline(stages=[assembler, scaler, pca])
    
    # 训练模型
    print("\n应用PCA降维...")
    model = pipeline.fit(df)
    
    # 转换数据
    result = model.transform(df)
    
    # 查看降维结果
    print("\n降维后的数据(前10行):")
    result.select("f1", "f2", "f3", "f4", "f5", "pca_features").show(10)
    
    # PCA模型信息
    pca_model = model.stages[-1]
    
    # 解释方差比例
    explained_variance = pca_model.explainedVariance
    print(f"\n各主成分解释的方差比例:")
    for i, variance in enumerate(explained_variance):
        print(f"主成分 {i+1}: {variance:.4f}")
    
    # 主成分
    components = pca_model.pc.toArray()
    print("\n主成分矩阵:")
    for i in range(components.shape[0]):
        print(f"主成分 {i+1}: ", end="")
        for j in range(components.shape[1]):
            print(f"{components[i,j]:.4f} ", end="")
        print()
    
    # 尝试不同的维度
    print("\n尝试不同维度的PCA:")
    for k in range(1, 6):
        pca_k = PCA(k=k, inputCol="scaled_features", outputCol=f"pca_features_{k}")
        pipeline_k = Pipeline(stages=[assembler, scaler, pca_k])
        model_k = pipeline_k.fit(df)
        result_k = model_k.transform(df)
        
        total_variance = sum(model_k.stages[-1].explainedVariance)
        print(f"k={k}: 累计解释方差比例={total_variance:.4f}")
    
    # 可视化(伪代码，实际需要导入可视化库)
    print("\n降维结果:")
    result.select("pca_features").show(5, truncate=False)
    
    spark.stop()

if __name__ == "__main__":
    pca_example()
```

## 7.8 Pipeline和模型评估

Pipeline和模型评估是机器学习工作流中的重要环节。

### 7.8.1 构建机器学习Pipeline

```python
# code/mlib-examples/ml_pipeline.py
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.ml.feature import VectorAssembler, StringIndexer, OneHotEncoder, StandardScaler
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml import Pipeline

def ml_pipeline_example():
    # 创建SparkSession
    spark = SparkSession.builder.appName("MLPipeline").getOrCreate()
    
    # 创建示例数据
    data = [
        (35, "M", "Graduate", "IT", "High", 1),
        (25, "F", "Undergraduate", "Finance", "Low", 0),
        (45, "M", "Graduate", "IT", "High", 1),
        (30, "F", "Graduate", "HR", "Medium", 1),
        (28, "M", "Undergraduate", "Sales", "Low", 0),
        (38, "F", "Postgraduate", "IT", "High", 1),
        (42, "M", "Graduate", "Finance", "Medium", 0),
        (32, "F", "Graduate", "HR", "Medium", 1),
        (26, "M", "Undergraduate", "Sales", "Low", 0),
        (40, "F", "Postgraduate", "IT", "High", 1),
        (33, "M", "Graduate", "Finance", "Medium", 0),
        (29, "F", "Undergraduate", "HR", "Medium", 1),
        (36, "M", "Graduate", "Sales", "High", 1),
        (31, "F", "Postgraduate", "IT", "High", 1),
        (27, "M", "Undergraduate", "Finance", "Low", 0)
    ]
    
    columns = ["age", "gender", "education", "department", "income_level", "approved"]
    df = spark.createDataFrame(data, columns)
    
    print("原始数据:")
    df.show()
    
    # 特征工程步骤
    # 1. 类别特征转换为数值索引
    gender_indexer = StringIndexer(inputCol="gender", outputCol="gender_index")
    education_indexer = StringIndexer(inputCol="education", outputCol="education_index")
    department_indexer = StringIndexer(inputCol="department", outputCol="department_index")
    income_level_indexer = StringIndexer(inputCol="income_level", outputCol="income_level_index")
    
    # 2. One-Hot编码
    gender_encoder = OneHotEncoder(inputCol="gender_index", outputCol="gender_vec")
    education_encoder = OneHotEncoder(inputCol="education_index", outputCol="education_vec")
    department_encoder = OneHotEncoder(inputCol="department_index", outputCol="department_vec")
    income_level_encoder = OneHotEncoder(inputCol="income_level_index", outputCol="income_level_vec")
    
    # 3. 合并特征向量
    assembler = VectorAssembler(
        inputCols=[
            "age", 
            "gender_vec", 
            "education_vec", 
            "department_vec", 
            "income_level_vec"
        ],
        outputCol="features"
    )
    
    # 4. 特征标准化
    scaler = StandardScaler(inputCol="features", outputCol="scaled_features")
    
    # 5. 随机森林分类器
    classifier = RandomForestClassifier(
        featuresCol="scaled_features",
        labelCol="approved",
        numTrees=20,
        maxDepth=5,
        seed=42
    )
    
    # 构建Pipeline
    pipeline = Pipeline(stages=[
        gender_indexer, education_indexer, department_indexer, income_level_indexer,
        gender_encoder, education_encoder, department_encoder, income_level_encoder,
        assembler, scaler, classifier
    ])
    
    # 划分训练集和测试集
    train_data, test_data = df.randomSplit([0.7, 0.3], seed=42)
    
    # 训Pipeline
    print("\n训练Pipeline...")
    model = pipeline.fit(train_data)
    
    # 在测试集上进行预测
    print("\n在测试集上进行预测...")
    predictions = model.transform(test_data)
    
    # 查看预测结果
    print("预测结果:")
    predictions.select("age", "gender", "education", "department", "income_level", 
                      "approved", "probability", "prediction").show()
    
    # 评估模型性能
    evaluator = BinaryClassificationEvaluator(rawPredictionCol="rawPrediction", labelCol="approved")
    auc = evaluator.evaluate(predictions)
    print(f"\n模型AUC: {auc:.4f}")
    
    # 查看Pipeline中每个阶段的信息
    print("\nPipeline各阶段:")
    for i, stage in enumerate(model.stages):
        print(f"阶段 {i+1}: {type(stage).__name__}")
        if hasattr(stage, 'coefficients'):
            print(f"  系数: {stage.coefficients}")
        if hasattr(stage, 'featureImportances'):
            print(f"  特征重要性: {stage.featureImportances}")
    
    # 保存Pipeline模型
    model_path = "pipeline_model"
    model.write().overwrite().save(model_path)
    print(f"\nPipeline模型已保存到: {model_path}")
    
    # 加载Pipeline模型
    from pyspark.ml import PipelineModel
    loaded_model = PipelineModel.load(model_path)
    
    # 使用加载的模型进行预测
    new_data = spark.createDataFrame([
        (30, "M", "Graduate", "IT", "Medium")
    ], ["age", "gender", "education", "department", "income_level"])
    
    new_predictions = loaded_model.transform(new_data)
    print("\n使用加载的模型进行预测:")
    new_predictions.select("age", "gender", "education", "department", "income_level", 
                          "probability", "prediction").show()
    
    spark.stop()

if __name__ == "__main__":
    ml_pipeline_example()
```

### 7.8.2 模型调优与交叉验证

```python
# code/mlib-examples/model_tuning.py
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.regression import RandomForestRegressor
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator
from pyspark.ml import Pipeline
import numpy as np

def model_tuning_example():
    # 创建SparkSession
    spark = SparkSession.builder.appName("ModelTuning").getOrCreate()
    
    # 创建示例数据
    np.random.seed(42)
    
    # 创建一些带有噪声的非线性关系数据
    x1 = np.random.uniform(0, 10, 100)
    x2 = np.random.uniform(0, 5, 100)
    x3 = np.random.uniform(0, 8, 100)
    
    # 目标变量与特征的非线性关系，加上一些噪声
    y = 2.5 * x1 + 1.8 * x2 - 0.5 * x3 + 0.3 * x1 * x2 + np.random.normal(0, 2, 100)
    
    # 创建DataFrame
    data = list(zip(x1, x2, x3, y))
    df = spark.createDataFrame(data, ["x1", "x2", "x3", "y"])
    
    print("原始数据(前10行):")
    df.show(10)
    
    # 特征工程
    # 将特征合并为向量
    assembler = VectorAssembler(
        inputCols=["x1", "x2", "x3"],
        outputCol="features"
    )
    
    # 标准化特征
    scaler = StandardScaler(
        inputCol="features",
        outputCol="scaled_features"
    )
    
    # 随机森林回归器
    rf = RandomForestRegressor(
        featuresCol="scaled_features",
        labelCol="y",
        seed=42
    )
    
    # 构建Pipeline
    pipeline = Pipeline(stages=[assembler, scaler, rf])
    
    # 划分训练集和测试集
    train_data, test_data = df.randomSplit([0.7, 0.3], seed=42)
    
    # 基准模型（使用默认参数）
    print("\n训练基准模型...")
    baseline_model = pipeline.fit(train_data)
    baseline_predictions = baseline_model.transform(test_data)
    
    # 评估基准模型
    evaluator = RegressionEvaluator(labelCol="y", predictionCol="prediction")
    baseline_rmse = evaluator.evaluate(baseline_predictions, {evaluator.metricName: "rmse"})
    baseline_r2 = evaluator.evaluate(baseline_predictions, {evaluator.metricName: "r2"})
    
    print(f"基准模型 - RMSE: {baseline_rmse:.4f}, R²: {baseline_r2:.4f}")
    
    # 创建参数网格
    print("\n设置参数网格...")
    param_grid = ParamGridBuilder() \
        .addGrid(rf.numTrees, [10, 20, 50]) \
        .addGrid(rf.maxDepth, [5, 10, 15]) \
        .addGrid(rf.minInstancesPerNode, [1, 2, 4]) \
        .build()
    
    print(f"参数组合数量: {len(param_grid)}")
    
    # 创建交叉验证
    print("\n设置交叉验证...")
    cross_val = CrossValidator(
        estimator=pipeline,
        estimatorParamMaps=param_grid,
        evaluator=evaluator,
        numFolds=5,  # 5折交叉验证
        parallelism=2,  # 并行度
        seed=42
    )
    
    # 运行交叉验证
    print("\n运行交叉验证...")
    cv_model = cross_val.fit(train_data)
    
    # 获取最佳模型
    best_model = cv_model.bestModel
    
    # 获取最佳参数
    best_rf = best_model.stages[-1]
    print(f"\n最佳参数:")
    print(f"numTrees: {best_rf.getNumTrees}")
    print(f"maxDepth: {best_rf.getMaxDepth()}")
    print(f"minInstancesPerNode: {best_rf.getMinInstancesPerNode}")
    
    # 使用最佳模型进行预测
    best_predictions = best_model.transform(test_data)
    
    # 评估最佳模型
    best_rmse = evaluator.evaluate(best_predictions, {evaluator.metricName: "rmse"})
    best_r2 = evaluator.evaluate(best_predictions, {evaluator.metricName: "r2"})
    
    print(f"\n最佳模型 - RMSE: {best_rmse:.4f}, R²: {best_r2:.4f}")
    print(f"改进 - RMSE: {baseline_rmse - best_rmse:.4f}, R²: {best_r2 - baseline_r2:.4f}")
    
    # 查看所有参数组合的性能
    print("\n所有参数组合的性能:")
    params = cv_model.getEstimatorParamMaps()
    metrics = cv_model.avgMetrics
    
    for i, (param, metric) in enumerate(zip(params, metrics)):
        num_trees = param[rf.numTrees]
        max_depth = param[rf.maxDepth]
        min_instances = param[rf.minInstancesPerNode]
        print(f"组合 {i+1}: numTrees={num_trees}, maxDepth={max_depth}, minInstancesPerNode={min_instances}, RMSE={metric:.4f}")
    
    # 特征重要性
    feature_importances = best_rf.featureImportances
    print(f"\n特征重要性: {feature_importances}")
    
    spark.stop()

if __name__ == "__main__":
    model_tuning_example()
```

## 7.9 实战案例：电商用户购买预测

```python
# code/mlib-examples/ecommerce_purchase_prediction.py
from pyspark import SparkContext
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import col, when, countDistinct, avg, sum as _sum
from pyspark.ml.feature import VectorAssembler, StandardScaler, StringIndexer, OneHotEncoder
from pyspark.ml.classification import LogisticRegression, RandomForestClassifier, GBTClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator
from pyspark.ml import Pipeline
import random

def ecommerce_purchase_prediction():
    # 创建SparkSession
    spark = SparkSession.builder.appName("EcommercePurchasePrediction").getOrCreate()
    
    # 模拟电商用户数据
    print("=== 生成电商用户数据 ===")
    
    # 用户特征数据
    users_data = []
    for user_id in range(1, 1001):
        age = random.randint(18, 65)
        gender = random.choice(["M", "F"])
        income_level = random.choice(["Low", "Medium", "High"])
        registration_months = random.randint(1, 36)
        
        # 基于用户特征和历史行为，生成购买概率
        purchase_prob = 0.1 + (income_level == "High") * 0.3 + (registration_months > 12) * 0.2 + (age > 30) * 0.1
        has_purchased = 1 if random.random() < purchase_prob else 0
        
        users_data.append((user_id, age, gender, income_level, registration_months, has_purchased))
    
    # 创建用户DataFrame
    users_df = spark.createDataFrame(
        users_data, 
        ["user_id", "age", "gender", "income_level", "registration_months", "has_purchased"]
    )
    
    print("用户数据样本:")
    users_df.show(10)
    
    # 用户行为数据
    behaviors_data = []
    for user_id in range(1, 1001):
        # 每个用户的行为数据
        sessions_count = random.randint(1, 50)
        avg_session_duration = random.randint(30, 1800)  # 秒
        pages_viewed = random.randint(1, 100)
        items_added_to_cart = random.randint(0, 20)
        items_removed_from_cart = random.randint(0, min(items_added_to_cart, 10))
        
        behaviors_data.append((
            user_id, 
            sessions_count, 
            avg_session_duration, 
            pages_viewed, 
            items_added_to_cart, 
            items_removed_from_cart
        ))
    
    # 创建行为DataFrame
    behaviors_df = spark.createDataFrame(
        behaviors_data, 
        ["user_id", "sessions_count", "avg_session_duration", "pages_viewed", 
         "items_added_to_cart", "items_removed_from_cart"]
    )
    
    print("\n用户行为数据样本:")
    behaviors_df.show(10)
    
    # 合并用户特征和行为数据
    full_data = users_df.join(behaviors_df, on="user_id")
    
    # 数据探索
    print("\n=== 数据探索 ===")
    print("用户总数:", full_data.count())
    
    # 购买用户与未购买用户的比例
    purchase_stats = full_data.groupBy("has_purchased").count().orderBy("has_purchased")
    print("购买与未购买用户分布:")
    purchase_stats.show()
    
    # 按性别和收入水平的购买情况
    gender_purchase = full_data.groupBy("gender", "has_purchased").count().orderBy("gender", "has_purchased")
    print("按性别和购买情况分布:")
    gender_purchase.show()
    
    income_purchase = full_data.groupBy("income_level", "has_purchased").count().orderBy("income_level", "has_purchased")
    print("按收入水平和购买情况分布:")
    income_purchase.show()
    
    # 特征工程
    print("\n=== 特征工程 ===")
    
    # 类别特征转换
    gender_indexer = StringIndexer(inputCol="gender", outputCol="gender_index")
    income_indexer = StringIndexer(inputCol="income_level", outputCol="income_level_index")
    
    # One-Hot编码
    gender_encoder = OneHotEncoder(inputCol="gender_index", outputCol="gender_vec")
    income_encoder = OneHotEncoder(inputCol="income_level_index", outputCol="income_level_vec")
    
    # 创建购物车转化率等衍生特征
    full_data = full_data.withColumn(
        "cart_conversion_rate", 
        when(col("items_added_to_cart") > 0, 
             (col("items_added_to_cart") - col("items_removed_from_cart")) / col("items_added_to_cart")
        ).otherwise(0)
    )
    
    full_data = full_data.withColumn("items_in_cart", 
                                    col("items_added_to_cart") - col("items_removed_from_cart"))
    
    # 合并特征
    feature_cols = [
        "age", 
        "registration_months",
        "sessions_count", 
        "avg_session_duration", 
        "pages_viewed", 
        "items_added_to_cart", 
        "items_removed_from_cart",
        "cart_conversion_rate",
        "items_in_cart",
        "gender_vec",
        "income_level_vec"
    ]
    
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
    
    # 标准化特征
    scaler = StandardScaler(inputCol="features", outputCol="scaled_features")
    
    # 模型训练
    print("\n=== 模型训练 ===")
    
    # 划分训练集和测试集
    train_data, test_data = full_data.randomSplit([0.8, 0.2], seed=42)
    
    # 逻辑回归
    lr = LogisticRegression(featuresCol="scaled_features", labelCol="has_purchased")
    lr_pipeline = Pipeline(stages=[
        gender_indexer, income_indexer, gender_encoder, income_encoder, 
        assembler, scaler, lr
    ])
    
    print("\n训练逻辑回归模型...")
    lr_model = lr_pipeline.fit(train_data)
    lr_predictions = lr_model.transform(test_data)
    
    # 随机森林
    rf = RandomForestClassifier(featuresCol="scaled_features", labelCol="has_purchased", seed=42)
    rf_pipeline = Pipeline(stages=[
        gender_indexer, income_indexer, gender_encoder, income_encoder, 
        assembler, scaler, rf
    ])
    
    print("\n训练随机森林模型...")
    rf_model = rf_pipeline.fit(train_data)
    rf_predictions = rf_model.transform(test_data)
    
    # 梯度提升树
    gbt = GBTClassifier(featuresCol="scaled_features", labelCol="has_purchased", seed=42)
    gbt_pipeline = Pipeline(stages=[
        gender_indexer, income_indexer, gender_encoder, income_encoder, 
        assembler, scaler, gbt
    ])
    
    print("\n训练梯度提升树模型...")
    gbt_model = gbt_pipeline.fit(train_data)
    gbt_predictions = gbt_model.transform(test_data)
    
    # 模型评估
    print("\n=== 模型评估 ===")
    
    evaluator = BinaryClassificationEvaluator(labelCol="has_purchased")
    
    # 逻辑回归评估
    lr_auc = evaluator.evaluate(lr_predictions)
    print(f"逻辑回归 AUC: {lr_auc:.4f}")
    
    # 随机森林评估
    rf_auc = evaluator.evaluate(rf_predictions)
    print(f"随机森林 AUC: {rf_auc:.4f}")
    
    # 梯度提升树评估
    gbt_auc = evaluator.evaluate(gbt_predictions)
    print(f"梯度提升树 AUC: {gbt_auc:.4f}")
    
    # 多分类评估
    multi_evaluator = MulticlassClassificationEvaluator(labelCol="has_purchased")
    
    # 比较各模型的准确率
    lr_accuracy = multi_evaluator.evaluate(lr_predictions, {multi_evaluator.metricName: "accuracy"})
    rf_accuracy = multi_evaluator.evaluate(rf_predictions, {multi_evaluator.metricName: "accuracy"})
    gbt_accuracy = multi_evaluator.evaluate(gbt_predictions, {multi_evaluator.metricName: "accuracy"})
    
    print(f"\n逻辑回归准确率: {lr_accuracy:.4f}")
    print(f"随机森林准确率: {rf_accuracy:.4f}")
    print(f"梯度提升树准确率: {gbt_accuracy:.4f}")
    
    # 选择最佳模型
    if rf_auc > lr_auc and rf_auc > gbt_auc:
        best_model = rf_model
        best_predictions = rf_predictions
        best_name = "随机森林"
    elif gbt_auc > lr_auc:
        best_model = gbt_model
        best_predictions = gbt_predictions
        best_name = "梯度提升树"
    else:
        best_model = lr_model
        best_predictions = lr_predictions
        best_name = "逻辑回归"
    
    print(f"\n最佳模型是: {best_name}")
    
    # 最佳模型的特征重要性（如果可用）
    if best_name == "随机森林" or best_name == "梯度提升树":
        feature_importances = best_model.stages[-1].featureImportances
        print("\n特征重要性:")
        for i, (col_name, importance) in enumerate(zip(feature_cols, feature_importances)):
            print(f"{col_name}: {importance:.4f}")
    
    # 查看预测结果示例
    print("\n最佳模型的预测结果示例:")
    best_predictions.select("user_id", "age", "gender", "income_level", "has_purchased", 
                           "probability", "prediction").show(10)
    
    # 保存最佳模型
    model_path = f"best_ecommerce_model_{best_name.replace(' ', '_')}"
    best_model.write().overwrite().save(model_path)
    print(f"\n最佳模型已保存到: {model_path}")
    
    spark.stop()
    print("电商用户购买预测分析完成")

if __name__ == "__main__":
    ecommerce_purchase_prediction()
```

## 7.10 小结

本章详细介绍了Spark MLlib机器学习库，包括数据类型、特征工程、分类、回归、聚类、降维算法，以及Pipeline和模型评估。MLlib提供了一个强大的机器学习工具集，能够在大规模数据上高效运行。通过Pipeline API，可以构建完整的机器学习工作流，从数据预处理到模型训练和评估。在下一章中，我们将学习Spark性能调优和生产环境实践。

## 实验与练习

1. 使用MLlib实现一个简单的文本分类系统
2. 构建一个完整的Pipeline，包括特征工程、模型训练和评估
3. 使用不同的分类算法比较同一数据集上的性能
4. 实现一个回归模型预测房价或销售量
5. 使用聚类算法对客户进行分群

## 参考资源

- [MLlib编程指南](https://spark.apache.org/docs/latest/ml-guide.html)
- [MLlib API文档](https://spark.apache.org/docs/latest/api/python/reference/pyspark.ml.html)