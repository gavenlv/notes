# Apache Spark 从入门到专家

本教程是Apache Spark的完整学习指南，从基础概念到高级应用，帮助您从零开始逐步成为Spark专家。

## 教程结构

### 文档部分

1. [Spark简介与生态系统](1-Spark简介与生态系统.md)
   - Spark是什么
   - Spark与其他大数据框架的对比
   - Spark生态系统组件
   - Spark应用场景

2. [Spark核心概念与架构](2-Spark核心概念与架构.md)
   - Spark运行架构
   - RDD、DataFrame与Dataset
   - Spark执行流程
   - 内存管理机制

3. [Spark安装与环境配置](3-Spark安装与环境配置.md)
   - 本地模式安装
   - 集群模式安装
   - 开发环境配置
   - IDE集成设置

4. [Spark Core编程基础](4-Spark Core编程基础.md)
   - RDD操作基础
   - 转换操作与行动操作
   - 键值对操作
   - 数据分区与缓存

5. [Spark SQL与结构化数据处理](5-Spark SQL与结构化数据处理.md)
   - DataFrame与Dataset API
   - SQL查询与函数
   - 数据源连接
   - 性能优化

6. [Spark Streaming实时数据处理](6-Spark Streaming实时数据处理.md)
   - DStream编程模型
   - 有状态与无状态计算
   - 窗口操作
   - 容错机制

7. [Spark MLlib机器学习库](7-Spark MLlib机器学习库.md)
   - MLlib架构与数据类型
   - 特征工程
   - 分类与回归算法
   - 聚类与推荐系统

8. [Spark性能调优与生产实践](8-Spark性能调优与生产实践.md)
   - 性能调优策略
   - 资源管理与配置
   - 作业监控与故障排查
   - 生产环境最佳实践

### 代码示例

[code](code/) 目录包含各章节的完整代码示例：

- **installation/**: 安装配置脚本
- **core-examples/**: Spark Core基础示例
- **sql-examples/**: Spark SQL示例
- **streaming-examples/**: Spark Streaming示例
- **mlib-examples/**: MLlib机器学习示例
- **performance-tuning/**: 性能调优示例
- **production-templates/**: 生产环境模板

## 学习路径

1. **入门阶段**: 章节1-3，了解Spark基础概念，搭建开发环境
2. **进阶阶段**: 章节4-5，掌握Spark核心编程和SQL处理
3. **高级阶段**: 章节6-8，学习流处理、机器学习和性能优化

## 代码运行要求

- Java 8+
- Python 3.6+ (如使用PySpark)
- Scala 2.11+ (如使用Scala API)
- Hadoop 2.7+ (可选，用于HDFS集成)

## 快速开始

1. 阅读[Spark简介与生态系统](1-Spark简介与生态系统.md)
2. 按照[Spark安装与环境配置](3-Spark安装与环境配置.md)搭建环境
3. 运行[code/core-examples](code/core-examples/)中的基础示例

## 学习建议

- 每个章节理论结合实践，运行相应代码示例
- 理解Spark的核心设计思想，尤其是内存计算和惰性求值
- 关注性能优化，理解Spark内部执行机制
- 尝试修改示例代码，解决实际业务问题

## 参考资源

- [Apache Spark官方文档](https://spark.apache.org/docs/latest/)
- [Spark GitHub仓库](https://github.com/apache/spark)
- [Spark权威指南](https://www.oreilly.com/library/view/learning-spark-2nd/9781492050049/)