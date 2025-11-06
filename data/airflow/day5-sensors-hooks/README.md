# Day 5: 传感器与钩子

## 概述

本日学习将深入探讨Airflow中的传感器(Sensors)和钩子(Hooks)，这两个组件是Airflow与外部系统交互的核心。传感器允许DAG等待特定条件满足后再继续执行，而钩子提供了与各种外部服务和API交互的接口。

## 学习目标

- 理解传感器的工作原理和不同类型
- 掌握常用传感器的使用方法
- 学习钩子的概念和常用钩子的使用
- 实现传感器驱动的DAG设计
- 了解传感器和钩子的最佳实践

## 课程内容

### 1. 传感器(Sensors)基础

- 传感器的概念和作用
- 传感器的工作模式：轮询(poke)模式与响应(resume)模式
- 传感器的超时和重试机制
- 传感器的参数配置

### 2. 常用传感器类型

- `FileSensor`: 等待文件出现
- `SqlSensor`: 等待SQL查询结果满足条件
- `HttpSensor`: 等待HTTP端点返回特定响应
- `TimeDeltaSensor`: 等待指定时间间隔
- `ExternalTaskSensor`: 等待其他DAG或任务完成

### 3. 钩子(Hooks)基础

- 钩子的概念和作用
- 钩子的连接(Connections)管理
- 钩子的生命周期和最佳实践
- 自定义钩子的开发

### 4. 常用钩子类型

- 数据库钩子：`PostgresHook`, `MySqlHook`, `SqliteHook`等
- 云服务钩子：`S3Hook`, `GCSHook`, `AzureBlobStorageHook`等
- API钩子：`HttpHook`, `SlackHook`等
- 其他钩子：`SSHHook`, `EmailHook`等

### 5. 传感器与钩子的结合应用

- 使用钩子在传感器中检查外部系统状态
- 在传感器中实现复杂条件判断
- 传感器和钩子的错误处理和重试策略

## 实践练习

- 创建使用文件传感器的DAG
- 实现使用SQL传感器的数据管道
- 构建使用HTTP传感器的API集成
- 开发使用多种钩子的数据处理流程

## 示例代码

本日学习包含以下示例：

1. `file_sensor_example.py`: 文件传感器示例
2. `sql_sensor_example.py`: SQL传感器示例
3. `http_sensor_example.py`: HTTP传感器示例
4. `hooks_integration_example.py`: 钩子集成示例
5. `sensor_hook_workflow.py`: 传感器与钩子结合的完整工作流

## 参考资源

- [Airflow传感器文档](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/sensors.html)
- [Airflow钩子文档](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/hooks/index.html)
- [Airflow连接管理](https://airflow.apache.org/docs/apache-airflow/stable/howto/connection.html)

## 评估标准

完成本日学习后，您应该能够：

- 解释传感器的工作原理和不同模式
- 根据需求选择合适的传感器类型
- 配置传感器的超时和重试参数
- 使用常用钩子与外部系统交互
- 设计传感器驱动的DAG工作流
- 实现传感器和钩子的错误处理

---

**注意**: 在开始本日学习之前，请确保已完成Day 4: XComs与任务间通信的学习，因为传感器和钩子经常与XComs结合使用。