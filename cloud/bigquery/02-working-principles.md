# BigQuery 工作原理 / BigQuery Working Principles

## 中文版

### BigQuery 架构概述

BigQuery 采用了分离计算与存储的架构设计，这是现代云数据仓库的关键特性。这种架构允许计算资源和存储资源独立扩展，从而提供更高的灵活性和成本效益。

### 核心组件

#### 1. 存储系统 (Colossus)

- **分布式文件系统**：BigQuery 使用 Google 的 Colossus 分布式文件系统存储数据
- **列式存储格式**：数据以列式格式存储，而不是传统的行式格式
- **压缩**：自动应用高效的压缩算法
- **数据加密**：静态数据和传输中的数据都进行加密
- **自动复制**：数据自动跨多个区域复制以确保高可用性

#### 2. 查询执行引擎 (Dremel)

- **分布式查询处理**：使用 Google 的 Dremel 技术进行大规模并行处理
- **树形架构**：查询被分解为树形结构，由根服务器、中间服务器和叶子服务器组成
- **动态资源分配**：根据查询复杂性自动分配计算资源
- **查询优化器**：自动优化查询执行计划

#### 3. 元数据服务 (Capacitor)

- **管理表结构和统计信息**：跟踪表的模式、分区信息和统计数据
- **缓存查询结果**：缓存频繁执行的查询结果以提高性能
- **权限管理**：控制对数据集和表的访问权限

### 数据处理流程

1. **查询提交**：用户通过 SQL 接口提交查询
2. **查询解析与验证**：系统解析 SQL 并验证语法和权限
3. **查询规划**：优化器生成执行计划
4. **资源分配**：系统分配必要的计算资源
5. **分布式执行**：查询被分解并在多个节点上并行执行
6. **数据读取**：从 Colossus 读取必要的列数据
7. **数据处理**：执行过滤、聚合、连接等操作
8. **结果返回**：将处理后的结果返回给用户

### 关键技术特性

#### 列式存储的优势

- **I/O 效率**：只读取查询所需的列，减少数据传输
- **压缩效率**：同类型数据存储在一起，提高压缩率
- **向量化处理**：支持 CPU 的 SIMD 指令集，提高处理速度

#### 查询执行优化

- **分区修剪**：自动跳过不相关的分区
- **谓词下推**：尽早应用过滤条件
- **查询重写**：自动重写查询以提高效率
- **智能缓存**：缓存中间结果和频繁查询

#### 并发和扩展性

- **无限扩展**：理论上可以处理任意大小的数据集
- **自动扩展**：根据工作负载自动调整资源
- **高并发**：支持多用户同时查询
- **资源隔离**：不同查询之间的资源隔离

### 存储格式和数据类型

- **内部存储格式**：使用优化的 Capacitor 列式格式
- **支持的数据类型**：包括基本类型（整数、浮点数、字符串等）和复杂类型（ARRAY、STRUCT、GEOGRAPHY 等）
- **嵌套和重复字段**：支持复杂的数据结构

### 数据一致性模型

- **强一致性**：读操作始终返回最新写入的数据
- **原子性操作**：表级别的原子性操作
- **事务支持**：有限的事务支持，主要用于加载操作

---

## English Version

### BigQuery Architecture Overview

BigQuery employs an architecture that separates computation from storage, a key feature of modern cloud data warehouses. This architecture allows compute and storage resources to scale independently, providing greater flexibility and cost-effectiveness.

### Core Components

#### 1. Storage System (Colossus)

- **Distributed File System**: BigQuery uses Google's Colossus distributed file system for data storage
- **Columnar Storage Format**: Data is stored in columnar format rather than traditional row-based format
- **Compression**: Efficient compression algorithms are automatically applied
- **Data Encryption**: Data is encrypted both at rest and in transit
- **Automatic Replication**: Data is automatically replicated across multiple zones for high availability

#### 2. Query Execution Engine (Dremel)

- **Distributed Query Processing**: Uses Google's Dremel technology for massively parallel processing
- **Tree Architecture**: Queries are broken down into a tree structure with root, intermediate, and leaf servers
- **Dynamic Resource Allocation**: Compute resources are automatically allocated based on query complexity
- **Query Optimizer**: Automatically optimizes query execution plans

#### 3. Metadata Service (Capacitor)

- **Manages Table Structures and Statistics**: Tracks table schemas, partition information, and statistics
- **Caches Query Results**: Caches results of frequently executed queries to improve performance
- **Permission Management**: Controls access to datasets and tables

### Data Processing Flow

1. **Query Submission**: User submits a query through SQL interface
2. **Query Parsing and Validation**: System parses SQL and validates syntax and permissions
3. **Query Planning**: Optimizer generates an execution plan
4. **Resource Allocation**: System allocates necessary compute resources
5. **Distributed Execution**: Query is broken down and executed in parallel across multiple nodes
6. **Data Reading**: Necessary column data is read from Colossus
7. **Data Processing**: Filtering, aggregation, joining, and other operations are performed
8. **Result Return**: Processed results are returned to the user

### Key Technical Features

#### Advantages of Columnar Storage

- **I/O Efficiency**: Only reads columns needed for the query, reducing data transfer
- **Compression Efficiency**: Similar data types stored together, improving compression ratios
- **Vectorized Processing**: Supports CPU's SIMD instruction sets for faster processing

#### Query Execution Optimization

- **Partition Pruning**: Automatically skips irrelevant partitions
- **Predicate Pushdown**: Applies filter conditions as early as possible
- **Query Rewriting**: Automatically rewrites queries for efficiency
- **Intelligent Caching**: Caches intermediate results and frequent queries

#### Concurrency and Scalability

- **Unlimited Scaling**: Theoretically can handle datasets of any size
- **Automatic Scaling**: Adjusts resources automatically based on workload
- **High Concurrency**: Supports multiple users querying simultaneously
- **Resource Isolation**: Resources are isolated between different queries

### Storage Formats and Data Types

- **Internal Storage Format**: Uses optimized Capacitor columnar format
- **Supported Data Types**: Includes basic types (integers, floats, strings, etc.) and complex types (ARRAY, STRUCT, GEOGRAPHY, etc.)
- **Nested and Repeated Fields**: Supports complex data structures

### Data Consistency Model

- **Strong Consistency**: Read operations always return the most recently written data
- **Atomic Operations**: Table-level atomic operations
- **Transaction Support**: Limited transaction support, primarily for loading operations