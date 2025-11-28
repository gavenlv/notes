# Spark性能优化示例

本目录包含了在Spark环境下对Apache Iceberg表进行性能优化的示例代码。

## 内容概览

1. **文件合并与压缩优化**
   - 数据文件合并示例
   - 元数据文件优化示例
   - 压缩格式配置示例

2. **分区策略优化**
   - 不同分区类型的应用示例
   - 分区演化操作示例
   - 分区裁剪效果演示

3. **查询优化技术**
   - 布隆过滤器配置与使用
   - 数据裁剪优化示例
   - 元数据缓存配置

4. **写入性能优化**
   - 批处理大小调优
   - 并行度设置优化
   - 写入模式选择示例

5. **资源配置优化**
   - Spark配置优化示例
   - 缓存策略配置示例

## 环境要求

- Apache Spark 3.0+
- Iceberg Spark运行时
- Scala 2.12+

## 运行说明

每个示例都是独立的Scala脚本，可以直接在Spark Shell或作为独立应用程序运行。

## 示例文件

- `file-compaction.scala`: 演示如何合并小文件以优化性能
- `partition-strategies.scala`: 展示不同分区策略的使用方法
- `query-optimization.scala`: 演示查询优化技术
- `write-optimization.scala`: 展示写入性能优化技巧
- `caching-config.scala`: 演示缓存配置优化