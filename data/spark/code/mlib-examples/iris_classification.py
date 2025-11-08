#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Spark MLlib鸢尾花分类示例
使用鸢尾花数据集演示机器学习分类任务，包括特征工程、模型训练、评估和预测。

运行方式:
spark-submit iris_classification.py
"""

from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, StringIndexer, StandardScaler
from pyspark.ml.classification import LogisticRegression, DecisionTreeClassifier, RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml import Pipeline
import numpy as np

def load_iris_data(spark):
    """加载鸢尾花数据"""
    
    # 鸢尾花数据集
    iris_data = [
        # Setosa类
        (5.1, 3.5, 1.4, 0.2, "setosa"),
        (4.9, 3.0, 1.4, 0.2, "setosa"),
        (4.7, 3.2, 1.3, 0.2, "setosa"),
        (4.6, 3.1, 1.5, 0.2, "setosa"),
        (5.0, 3.6, 1.4, 0.2, "setosa"),
        (5.4, 3.9, 1.7, 0.4, "setosa"),
        (4.6, 3.4, 1.4, 0.3, "setosa"),
        (5.0, 3.4, 1.5, 0.2, "setosa"),
        (4.4, 2.9, 1.4, 0.2, "setosa"),
        (4.9, 3.1, 1.5, 0.1, "setosa"),
        (5.4, 3.7, 1.5, 0.2, "setosa"),
        (4.8, 3.4, 1.6, 0.2, "setosa"),
        (4.8, 3.0, 1.4, 0.1, "setosa"),
        (4.3, 3.0, 1.1, 0.1, "setosa"),
        (5.8, 4.0, 1.2, 0.2, "setosa"),
        # Versicolor类
        (7.0, 3.2, 4.7, 1.4, "versicolor"),
        (6.4, 3.2, 4.5, 1.5, "versicolor"),
        (6.9, 3.1, 4.9, 1.5, "versicolor"),
        (5.5, 2.3, 4.0, 1.3, "versicolor"),
        (6.5, 2.8, 4.6, 1.5, "versicolor"),
        (5.7, 2.8, 4.5, 1.3, "versicolor"),
        (6.3, 3.3, 4.7, 1.6, "versicolor"),
        (4.9, 2.4, 3.3, 1.0, "versicolor"),
        (6.6, 2.9, 4.6, 1.3, "versicolor"),
        (5.2, 2.7, 3.9, 1.4, "versicolor"),
        (5.0, 2.0, 3.5, 1.0, "versicolor"),
        (5.9, 3.0, 4.2, 1.5, "versicolor"),
        (6.0, 2.2, 4.0, 1.0, "versicolor"),
        (6.1, 2.9, 4.7, 1.4, "versicolor"),
        (5.6, 2.9, 3.6, 1.3, "versicolor"),
        # Virginica类
        (6.3, 3.3, 6.0, 2.5, "virginica"),
        (5.8, 2.7, 5.1, 1.9, "virginica"),
        (7.1, 3.0, 5.9, 2.1, "virginica"),
        (6.3, 2.9, 5.6, 1.8, "virginica"),
        (6.5, 3.0, 5.8, 2.2, "virginica"),
        (7.6, 3.0, 6.6, 2.1, "virginica"),
        (4.9, 2.5, 4.5, 1.7, "virginica"),
        (7.3, 2.9, 6.3, 1.8, "virginica"),
        (6.7, 2.5, 5.8, 1.8, "virginica"),
        (7.2, 3.6, 6.1, 2.5, "virginica"),
        (6.5, 3.2, 5.1, 2.0, "virginica"),
        (6.4, 2.7, 5.3, 1.9, "virginica"),
        (6.8, 3.0, 5.5, 2.1, "virginica"),
        (5.7, 2.5, 5.0, 2.0, "virginica"),
        (5.8, 2.8, 5.1, 2.4, "virginica")
    ]
    
    # 增加一些随机生成的数据点
    np.random.seed(42)
    for i in range(100):
        species = np.random.choice(["setosa", "versicolor", "virginica"])
        if species == "setosa":
            sepal_length = np.random.normal(5.0, 0.3)
            sepal_width = np.random.normal(3.4, 0.3)
            petal_length = np.random.normal(1.5, 0.2)
            petal_width = np.random.normal(0.2, 0.1)
        elif species == "versicolor":
            sepal_length = np.random.normal(5.9, 0.5)
            sepal_width = np.random.normal(2.8, 0.3)
            petal_length = np.random.normal(4.3, 0.4)
            petal_width = np.random.normal(1.3, 0.2)
        else:  # virginica
            sepal_length = np.random.normal(6.6, 0.6)
            sepal_width = np.random.normal(3.0, 0.3)
            petal_length = np.random.normal(5.6, 0.5)
            petal_width = np.random.normal(2.0, 0.3)
            
        iris_data.append((sepal_length, sepal_width, petal_length, petal_width, species))
    
    # 创建DataFrame
    columns = ["sepal_length", "sepal_width", "petal_length", "petal_width", "species"]
    df = spark.createDataFrame(iris_data, columns)
    
    return df

def build_pipeline(classifier, classifier_name):
    """构建机器学习Pipeline"""
    
    # 特征列
    feature_cols = ["sepal_length", "sepal_width", "petal_length", "petal_width"]
    
    # 特征工程步骤
    # 1. 合并特征为向量
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
    
    # 2. 标准化特征
    scaler = StandardScaler(inputCol="features", outputCol="scaled_features")
    
    # 3. 将标签转换为数值索引
    label_indexer = StringIndexer(inputCol="species", outputCol="label")
    
    # 4. 分类器
    model = classifier
    
    # 构建Pipeline
    pipeline = Pipeline(stages=[assembler, scaler, label_indexer, model])
    
    return pipeline, classifier_name

def evaluate_model(predictions, model_name):
    """评估模型性能"""
    
    # 创建评估器
    evaluator = MulticlassClassificationEvaluator(
        predictionCol="prediction", 
        labelCol="label"
    )
    
    # 计算评估指标
    accuracy = evaluator.evaluate(predictions, {evaluator.metricName: "accuracy"})
    precision = evaluator.evaluate(predictions, {evaluator.metricName: "weightedPrecision"})
    recall = evaluator.evaluate(predictions, {evaluator.metricName: "weightedRecall"})
    f1 = evaluator.evaluate(predictions, {evaluator.metricName: "f1"})
    
    print(f"{model_name} 评估结果:")
    print(f"  准确率: {accuracy:.4f}")
    print(f"  精确率: {precision:.4f}")
    print(f"  召回率: {recall:.4f}")
    print(f"  F1分数: {f1:.4f}")
    
    return {
        "model": model_name,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }

def main():
    """主函数"""
    
    # 创建SparkSession
    spark = SparkSession.builder.appName("IrisClassification").getOrCreate()
    
    try:
        # 加载鸢尾花数据
        iris_df = load_iris_data(spark)
        print("鸢尾花数据集样本:")
        iris_df.show(5)
        
        # 数据统计
        print("\n数据集统计:")
        iris_df.describe().show()
        
        # 类别分布
        print("\n类别分布:")
        iris_df.groupBy("species").count().show()
        
        # 划分训练集和测试集
        train_data, test_data = iris_df.randomSplit([0.7, 0.3], seed=42)
        print(f"\n训练集大小: {train_data.count()}")
        print(f"测试集大小: {test_data.count()}")
        
        # 定义不同的分类器
        classifiers = [
            (LogisticRegression(featuresCol="scaled_features", labelCol="label", maxIter=10), "逻辑回归"),
            (DecisionTreeClassifier(featuresCol="scaled_features", labelCol="label"), "决策树"),
            (RandomForestClassifier(featuresCol="scaled_features", labelCol="label", numTrees=10, seed=42), "随机森林")
        ]
        
        # 训练和评估多个模型
        models = []
        evaluation_results = []
        
        for classifier, name in classifiers:
            print(f"\n=== 训练 {name} 模型 ===")
            
            # 构建Pipeline
            pipeline, _ = build_pipeline(classifier, name)
            
            # 训练模型
            model = pipeline.fit(train_data)
            models.append((model, name))
            
            # 在测试集上进行预测
            predictions = model.transform(test_data)
            
            # 评估模型
            result = evaluate_model(predictions, name)
            evaluation_results.append(result)
        
        # 比较模型性能
        print("\n=== 模型性能比较 ===")
        print("{:<15} {:<10} {:<10} {:<10} {:<10}".format(
            "模型", "准确率", "精确率", "召回率", "F1分数"
        ))
        print("-" * 60)
        
        for result in evaluation_results:
            print("{:<15} {:<10.4f} {:<10.4f} {:<10.4f} {:<10.4f}".format(
                result["model"],
                result["accuracy"],
                result["precision"],
                result["recall"],
                result["f1"]
            ))
        
        # 选择最佳模型
        best_model_result = max(evaluation_results, key=lambda x: x["accuracy"])
        best_model = [model for model, name in models if name == best_model_result["model"]][0]
        
        print(f"\n最佳模型: {best_model_result['model']}")
        print(f"最佳准确率: {best_model_result['accuracy']:.4f}")
        
        # 使用最佳模型进行预测
        print("\n=== 使用最佳模型进行预测 ===")
        
        # 创建一些新样本
        new_samples = [
            (5.1, 3.5, 1.4, 0.2),  # 应该是setosa
            (6.0, 2.7, 4.0, 1.3),  # 应该是versicolor
            (6.3, 3.3, 6.0, 2.5)   # 应该是virginica
        ]
        
        new_samples_df = spark.createDataFrame(new_samples, ["sepal_length", "sepal_width", "petal_length", "petal_width"])
        
        # 进行预测
        predictions = best_model.transform(new_samples_df)
        
        # 显示预测结果
        predictions.select("sepal_length", "sepal_width", "petal_length", "petal_width", "probability", "prediction").show()
        
        # 保存最佳模型
        model_path = f"best_iris_model_{best_model_result['model'].replace(' ', '_')}"
        best_model.write().overwrite().save(model_path)
        print(f"\n最佳模型已保存到: {model_path}")
        
    except Exception as e:
        print(f"执行失败: {str(e)}")
    finally:
        # 停止SparkSession
        spark.stop()

if __name__ == "__main__":
    main()