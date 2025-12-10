# 1. Technology Stack Overview & Architecture Design

## 1.1 Overall Architecture Overview

Modern data architecture typically adopts a layered design, distributing data processing responsibilities appropriately across different technical components. This topic focuses on the following technology stack:

```
Data Sources Layer
    ↓
ETL Layer (Flink / BigQuery)
    ↓
Analytical Database Layer (ClickHouse)
    ↓
Application Layer (BI tools, reporting systems, etc.)
```

## 1.2 Technical Components Introduction

### 1.2.1 Data Sources Layer
- **API Data Sources**: RESTful API, GraphQL, etc.
- **Message Queues**: Kafka, RabbitMQ, Pulsar, etc.
- **Direct Connections**: Database direct connections, file systems, etc.

### 1.2.2 ETL Layer
- **Apache Flink**: Stream data processing, suitable for real-time ETL
- **Google BigQuery**: Batch processing ETL, suitable for large-scale data analysis

### 1.2.3 Analytical Database Layer
- **ClickHouse**: Columnar storage, suitable for OLAP scenarios

## 1.3 Scan Logic Division Principles

### 1.3.1 Core Principles
1. **Data preprocessing should be completed primarily in the ETL layer**
2. **Complex calculations and aggregations should be performed in the analytical database layer**
3. **Real-time requirements determine processing location**
4. **Data volume size influences technology selection**

### 1.3.2 Specific Division Criteria

| Scan Logic Type | ETL Layer Processing | ClickHouse Layer Processing |
|-----------------|---------------------|----------------------------|
| Data Cleaning | ✅ Primary processing | ❌ Minimal processing |
| Data Transformation | ✅ Format conversion | ❌ Mostly avoided |
| Data Aggregation | ⚠️ Pre-aggregation | ✅ Primary aggregation |
| Complex Calculations | ❌ Avoid | ✅ Primary processing |
| Real-time Queries | ⚠️ Stream processing | ✅ Analytical queries |

## 1.4 Architecture Advantages

### 1.4.1 Performance Advantages
- **ETL Layer**: Parallel processing, data preprocessing optimization
- **ClickHouse Layer**: Columnar storage, fast analytical queries

### 1.4.2 Scalability
- Independent scaling of each layer
- Flexible technology stack selection

### 1.4.3 Maintainability
- Clear separation of responsibilities
- Fault isolation

## 1.5 Typical Application Scenarios

### 1.5.1 Real-time Data Analysis
- Use Flink for real-time ETL
- ClickHouse provides real-time query capabilities

### 1.5.2 Batch Processing Analysis
- BigQuery handles large-scale batch processing
- ClickHouse provides interactive query capabilities

### 1.5.3 Hybrid Scenarios
- Flink processes real-time data streams
- BigQuery processes historical data
- ClickHouse provides unified query interface

## 1.6 Summary

Proper division of scan logic is key to building an efficient data architecture. The ETL layer is primarily responsible for data preprocessing and initial transformation, while the ClickHouse layer focuses on analytical calculations and fast queries. The next chapter will discuss data source integration strategies in detail.