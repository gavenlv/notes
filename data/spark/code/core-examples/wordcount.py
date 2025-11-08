#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Spark WordCount 示例
这是Spark的经典入门示例，用于统计文本中单词的出现频率。

运行方式:
spark-submit wordcount.py
"""

from pyspark import SparkContext
import sys
import os

def word_count():
    """WordCount主函数"""
    # 创建SparkContext
    sc = SparkContext(appName="PythonWordCount")
    
    try:
        # 输入文件路径，可以是本地文件、HDFS路径或任何支持的文件系统
        if len(sys.argv) > 1:
            input_path = sys.argv[1]
        else:
            # 默认创建一个临时文件作为输入
            input_path = "temp_input.txt"
            with open(input_path, "w") as f:
                f.write("Hello world\n")
                f.write("Hello Spark\n")
                f.write("Spark is great\n")
                f.write("Hello big data\n")
                f.write("Spark is fast\n")
                f.write("Hello Python\n")
                f.write("Spark is powerful\n")
                f.write("Hello PySpark\n")
        
        # 读取文本文件
        text_rdd = sc.textFile(input_path)
        
        # 执行WordCount转换
        # 1. 将每行文本分割为单词
        words = text_rdd.flatMap(lambda line: line.split(" "))
        
        # 2. 将每个单词转换为键值对 (word, 1)
        word_pairs = words.map(lambda word: (word, 1))
        
        # 3. 按单词分组并计算每个单词的总数
        word_counts = word_pairs.reduceByKey(lambda a, b: a + b)
        
        # 4. 按单词出现次数降序排序
        sorted_word_counts = word_counts.sortBy(lambda x: x[1], ascending=False)
        
        # 收集结果
        results = sorted_word_counts.collect()
        
        # 打印结果
        print("WordCount结果:")
        for word, count in results:
            print(f"{word}: {count}")
        
        # 保存结果到文件
        output_path = "wordcount_output"
        word_counts.saveAsTextFile(output_path)
        print(f"结果已保存到: {output_path}")
        
    except Exception as e:
        print(f"WordCount执行失败: {str(e)}")
    finally:
        # 清理临时文件
        if len(sys.argv) <= 1 and os.path.exists(input_path):
            os.remove(input_path)
        
        # 停止SparkContext
        sc.stop()

if __name__ == "__main__":
    word_count()