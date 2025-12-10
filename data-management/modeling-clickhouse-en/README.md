# 数据建模高级专题 - Advanced Data Modeling Topics

## 概述 / Overview

本专题深入探讨现代数据架构中的数据建模策略，重点关注ETL层（Flink/BigQuery）与分析数据库（ClickHouse）之间的职责划分和扫描逻辑设计。

This topic provides an in-depth exploration of data modeling strategies in modern data architecture, focusing on the division of responsibilities and scan logic design between the ETL layer (Flink/BigQuery) and the analytical database (ClickHouse).

## 目录结构 / Table of Contents

### 中文文档
- [1. 技术栈概述与架构设计](01-architecture-zh.md)
- [2. 数据源接入策略](02-data-sources-zh.md)
- [3. ETL层职责与扫描逻辑](03-etl-layer-zh.md)
- [4. ClickHouse层职责与扫描逻辑](04-clickhouse-layer-zh.md)
- [5. 职责划分最佳实践](05-best-practices-zh.md)
- [6. 实际案例与代码示例](06-case-studies-zh.md)
- [7. 总结与性能优化](07-summary-zh.md)

### English Documents
- [1. Technology Stack Overview & Architecture Design](01-architecture-en.md)
- [2. Data Source Integration Strategies](02-data-sources-en.md)
- [3. ETL Layer Responsibilities & Scan Logic](03-etl-layer-en.md)
- [4. ClickHouse Layer Responsibilities & Scan Logic](04-clickhouse-layer-en.md)
- [5. Best Practices for Responsibility Division](05-best-practices-en.md)
- [6. Case Studies & Code Examples](06-case-studies-en.md)
- [7. Summary & Performance Optimization](07-summary-en.md)

## 快速开始 / Quick Start

### 核心问题 / Core Questions
- **ETL层应该处理哪些扫描逻辑？**
- **ClickHouse层应该处理哪些扫描逻辑？**
- **如何优化整体数据流水线的性能？**

### What scan logic should be handled by ETL layer?
### What scan logic should be handled by ClickHouse layer?
### How to optimize the performance of the entire data pipeline?

## 技术栈 / Technology Stack

- **数据源 / Data Sources**: API, Message Queue, Direct Connection
- **ETL工具 / ETL Tools**: Apache Flink, Google BigQuery
- **分析数据库 / Analytical Database**: ClickHouse
- **数据建模 / Data Modeling**: Dimensional Modeling, Data Vault, Star Schema

## 贡献指南 / Contribution Guidelines

欢迎提交问题和改进建议。

Issues and improvement suggestions are welcome.