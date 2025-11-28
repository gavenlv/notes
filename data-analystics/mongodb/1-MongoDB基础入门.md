# 第1章：MongoDB基础入门

## 目录
1. [MongoDB简介](#1-mongodb简介)
2. [NoSQL基础概念](#2-nosql基础概念)
3. [MongoDB安装与配置](#3-mongodb安装与配置)
4. [MongoDB基本操作](#4-mongodb基本操作)
5. [文档结构与数据类型](#5-文档结构与数据类型)
6. [集合操作](#6-集合操作)
7. [CRUD操作基础](#7-crud操作基础)
8. [最佳实践](#8-最佳实践)

## 1. MongoDB简介

### 1.1 MongoDB概述

MongoDB是一个开源的文档数据库，属于NoSQL数据库的一种。它以高性能、高可用性和易扩展性为设计目标，使用JSON-like的文档格式存储数据。MongoDB是当前最流行的NoSQL数据库之一，广泛应用于Web应用、大数据分析、实时分析等场景。

### 1.2 MongoDB特点

- **文档存储**：以BSON格式存储类似JSON的文档
- **模式灵活**：同一集合中的文档可以有不同结构
- **高性能**：支持索引、聚合、查询优化
- **高可用性**：内置复制集、自动故障转移
- **水平扩展**：支持分片、数据自动分片
- **丰富查询**：支持复杂查询、聚合框架
- **强大的索引**：支持多种索引类型

### 1.3 MongoDB vs 关系型数据库

| 特性 | MongoDB | MySQL | PostgreSQL |
|------|---------|-------|------------|
| 数据模型 | 文档 | 表 | 表 |
| 存储格式 | BSON/JSON | 行/列 | 行/列 |
| 模式 | 灵活 | 固定 | 固定 |
| 事务 | 支持多文档事务 | ACID事务 | ACID事务 |
| 查询语言 | Mongo Query | SQL | SQL |
| 扩展性 | 水平/垂直 | 主要垂直 | 垂直 |
| 索引 | 多种类型 | B-Tree | B-Tree |

### 1.4 应用场景

- **内容管理系统**：灵活的文档结构适合存储各种类型的内容
- **实时分析**：快速的读写操作适合实时数据处理
- **移动应用**：支持地理位置查询和离线同步
- **物联网**：支持大量传感器数据的存储和查询
- **单页应用**：JavaScript友好，适合现代Web开发
- **大数据**：支持大数据量的存储和分析

## 2. NoSQL基础概念

### 2.1 NoSQL定义

NoSQL（Not Only SQL）是一类非关系型数据库的总称，它们不使用传统的关系型数据库的表格模型，而是使用其他数据模型，如键值对、文档、列族或图结构。

### 2.2 NoSQL数据库类型

#### 2.2.1 文档数据库
- **代表产品**：MongoDB、CouchDB、RavenDB
- **特点**：存储结构化的文档数据
- **适用场景**：内容管理、配置文件、事件日志

#### 2.2.2 键值数据库
- **代表产品**：Redis、DynamoDB、Cassandra
- **特点**：简单的键值对存储
- **适用场景**：缓存、会话存储、快速查找

#### 2.2.3 列族数据库
- **代表产品**：Cassandra、HBase、Google Bigtable
- **特点**：按列而非按行存储数据
- **适用场景**：大数据分析、时间序列数据

#### 2.2.4 图数据库
- **代表产品**：Neo4j、ArangoDB、OrientDB
- **特点**：专门处理关系数据
- **适用场景**：社交网络、推荐系统、知识图谱

### 2.3 CAP定理

CAP定理指出，在分布式系统中，不可能同时满足一致性（Consistency）、可用性（Availability）和分区容错性（Partition tolerance）三个特性。

- **一致性（Consistency）**：所有节点在同一时间看到相同的数据
- **可用性（Availability）**：每个请求都能收到响应
- **分区容错性（Partition tolerance）**：系统继续运行，即使网络分区发生

MongoDB在CAP定理中偏向于可用性和分区容错性，最终一致性。

## 3. MongoDB安装与配置

### 3.1 Windows安装

#### 3.1.1 下载安装包
1. 访问 [MongoDB官网](https://www.mongodb.com/try/download/community)
2. 选择合适的版本：
   - Version: 7.0.x (最新稳定版)
   - Platform: Windows 64 (8.1+)
   - Package: .msi

#### 3.1.2 安装过程
1. 运行下载的 .msi 安装文件
2. 选择 "Complete" 安装类型
3. 配置服务设置：
   - Run service as Network Service user
   - Data Directory: C:\Program Files\MongoDB\Server\7.0\data
   - Log Directory: C:\Program Files\MongoDB\Server\7.0\log
4. 安装MongoDB Compass（GUI工具）

#### 3.1.3 验证安装
```powershell
# 检查MongoDB服务状态
net start MongoDB

# 连接MongoDB
mongosh
```

### 3.2 Linux安装 (Ubuntu/Debian)

#### 3.2.1 导入GPG密钥
```bash
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
```

#### 3.2.2 添加软件仓库
```bash
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
```

#### 3.2.3 安装MongoDB
```bash
sudo apt update
sudo apt install -y mongodb-org

# 启动MongoDB服务
sudo systemctl start mongod
sudo systemctl enable mongod
```

### 3.3 Docker安装

#### 3.3.1 单实例MongoDB
```bash
# 拉取MongoDB镜像
docker pull mongo:7.0

# 运行MongoDB容器
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -v mongodb_data:/data/db \
  mongo:7.0
```

#### 3.3.2 MongoDB复制集
```bash
# 创建自定义网络
docker network create mongodb

# 运行三个MongoDB实例
for i in 1 2 3; do
  docker run -d \
    --name mongodb$i \
    --network mongodb \
    -p 2701$i:27017 \
    -v mongodb_data$i:/data/db \
    mongo:7.0 --replSet rs0 --bind_ip_all
done
```

### 3.4 基本配置

#### 3.4.1 配置文件
```yaml
# /etc/mongod.conf
storage:
  dbPath: /var/lib/mongodb
  journal:
    enabled: true

systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log

net:
  port: 27017
  bindIp: 127.0.0.1

processManagement:
  fork: true
  timeZoneInfo: /usr/share/zoneinfo

replication:
  replSetName: rs0
```

#### 3.4.2 启动参数
```bash
# 启动MongoDB
mongod --config /etc/mongod.conf

# 带参数启动
mongod --dbpath /data/db --logpath /var/log/mongodb/mongod.log --fork
```

## 4. MongoDB基本操作

### 4.1 连接MongoDB

#### 4.1.1 使用mongosh连接
```bash
# 连接本地MongoDB
mongosh

# 连接远程MongoDB
mongosh --host <hostname> --port <port>

# 连接带认证的MongoDB
mongosh --username <username> --password <password> --authenticationDatabase <db>

# 连接副本集
mongosh --host rs0/<primary_host> --username <username> --password <password>
```

#### 4.1.2 MongoDB Compass连接
1. 打开MongoDB Compass
2. 连接字符串：`mongodb://localhost:27017`
3. 点击连接

### 4.2 基本命令

#### 4.2.1 数据库操作
```javascript
// 显示所有数据库
show dbs

// 切换数据库
use mydatabase

// 显示当前数据库
db

// 创建数据库
use newdatabase
db.users.insertOne({name: "test"})

// 删除数据库
db.dropDatabase()
```

#### 4.2.2 集合操作
```javascript
// 显示当前数据库的所有集合
show collections

// 显示集合统计信息
db.users.stats()

// 获取集合详细信息
db.users.getIndexes()

// 创建集合（可选）
db.createCollection("mycollection", {capped: false, size: 1000000})
```

### 4.3 帮助命令

```javascript
// 查看帮助
help

// 查看数据库帮助
db.help()

// 查看集合帮助
db.users.help()

// 查看命令详细信息
db.users.find().help()
```

## 5. 文档结构与数据类型

### 5.1 BSON数据类型

MongoDB使用BSON（Binary JSON）格式存储数据，支持以下数据类型：

#### 5.1.1 基本数据类型
```javascript
// 字符串
{ name: "John Doe" }

// 整数
{ age: 30, count: 123456789 }

// 浮点数
{ price: 29.99, rating: 4.5 }

// 布尔值
{ active: true, verified: false }

// 空值
{ middle_name: null }
```

#### 5.1.2 日期和时间
```javascript
// 日期（UTC时间）
{ 
  created_at: new Date(),
  updated_at: ISODate("2024-01-01T00:00:00Z")
}

// 时间戳
{ timestamp: Timestamp(1704067200, 1) }
```

#### 5.1.3 数组
```javascript
// 字符串数组
{ tags: ["mongodb", "nosql", "database"] }

// 混合类型数组
{ mixed: [1, "string", true, {nested: "object"}, [1, 2, 3]] }

// 嵌套文档数组
{ 
  comments: [
    { author: "user1", text: "Great post!", timestamp: new Date() },
    { author: "user2", text: "Very helpful", timestamp: new Date() }
  ]
}
```

#### 5.1.4 嵌套文档
```javascript
// 简单嵌套文档
{
  address: {
    street: "123 Main St",
    city: "New York",
    zipCode: "10001"
  }
}

// 复杂嵌套文档
{
  profile: {
    personal: {
      name: "John",
      age: 30,
      gender: "male"
    },
    contact: {
      email: "john@example.com",
      phone: "+1-555-0123"
    }
  }
}
```

### 5.2 ObjectId

每个MongoDB文档都有一个唯一的_id字段：

```javascript
// 自动生成的ObjectId
{
  _id: ObjectId("64a7b1234567890abcdef1234"),
  name: "John Doe"
}

// 手动创建ObjectId
{
  _id: ObjectId(),
  custom_id: "user_123",
  name: "John Doe"
}
```

### 5.3 数据类型转换

```javascript
// 字符串转日期
db.users.findOne({created_at: { $gte: new Date("2024-01-01") }})

// 数值转换
db.users.aggregate([
  {
    $project: {
      age: { $toInt: "$age_string" },
      price: { $toDouble: "$price" }
    }
  }
])
```

## 6. 集合操作

### 6.1 创建集合

#### 6.1.1 基本创建
```javascript
// 简单集合
db.createCollection("users")

// 带选项的集合
db.createCollection("products", {
  capped: true,           // 固定集合
  size: 1000000,          // 最大大小（字节）
  max: 10000,             // 最大文档数
  autoIndexId: true       // 自动创建_id索引
})
```

#### 6.1.2 固定集合（Capped Collection）
```javascript
// 创建日志集合
db.createCollection("logs", {
  capped: true,
  size: 1000000,
  max: 1000
})

// 插入数据到固定集合
for (let i = 0; i < 100; i++) {
  db.logs.insertOne({
    timestamp: new Date(),
    level: "info",
    message: `Log entry ${i}`
  })
}
```

### 6.2 删除集合

```javascript
// 删除集合
db.mycollection.drop()

// 检查集合是否存在
db.getCollectionNames().includes("mycollection")
```

### 6.3 集合重命名

```javascript
// 重命名集合
db.mycollection.renameCollection("newcollection", true)  // dropTarget: true
```

## 7. CRUD操作基础

### 7.1 插入操作

#### 7.1.1 insertOne() - 插入单个文档
```javascript
// 插入单个文档
db.users.insertOne({
  name: "John Doe",
  age: 30,
  email: "john@example.com",
  address: {
    street: "123 Main St",
    city: "New York",
    zipCode: "10001"
  },
  tags: ["developer", "mongodb"],
  created_at: new Date()
})

// 返回结果
{
  acknowledged: true,
  insertedId: ObjectId("64a7b1234567890abcdef1234")
}
```

#### 7.1.2 insertMany() - 插入多个文档
```javascript
// 插入多个文档
db.users.insertMany([
  {
    name: "Jane Smith",
    age: 25,
    email: "jane@example.com",
    tags: ["designer"]
  },
  {
    name: "Bob Johnson",
    age: 35,
    email: "bob@example.com",
    tags: ["manager", "mongodb"]
  },
  {
    name: "Alice Brown",
    age: 28,
    email: "alice@example.com",
    tags: ["developer", "python"]
  }
])

// 返回结果
{
  acknowledged: true,
  insertedIds: [
    ObjectId("64a7b1234567890abcdef1235"),
    ObjectId("64a7b1234567890abcdef1236"),
    ObjectId("64a7b1234567890abcdef1237")
  ]
}
```

#### 7.1.3 insert() - 通用插入方法（已弃用）
```javascript
// 插入单个文档
db.users.insert({
  name: "Test User",
  age: 25
})

// 插入多个文档
db.users.insert([
  {name: "User 1", age: 20},
  {name: "User 2", age: 22}
])
```

### 7.2 查询操作

#### 7.2.1 find() - 基本查询
```javascript
// 查询所有文档
db.users.find()

// 查询特定条件的文档
db.users.find({age: 30})

// 查询嵌套字段
db.users.find({"address.city": "New York"})

// 查询数组字段
db.users.find({tags: "developer"})
```

#### 7.2.2 pretty() - 格式化输出
```javascript
// 普通格式
db.users.find()

// 格式化输出
db.users.find().pretty()

// 限定结果数量
db.users.find().limit(5)

// 跳过前几个结果
db.users.find().skip(2)

// 排序结果
db.users.find().sort({name: 1})     // 按name升序
db.users.find().sort({age: -1})     // 按age降序
```

#### 7.2.3 findOne() - 查询单个文档
```javascript
// 返回第一个匹配的文档
db.users.findOne({name: "John Doe"})

// 如果没有找到，返回null
db.users.findOne({name: "Nonexistent"})
```

### 7.3 更新操作

#### 7.3.1 updateOne() - 更新单个文档
```javascript
// 更新单个文档
db.users.updateOne(
  {name: "John Doe"},           // 查询条件
  {
    $set: {                      // 更新操作符
      age: 31,
      "address.city": "San Francisco"
    }
  }
)

// 返回结果
{
  acknowledged: true,
  matchedCount: 1,
  modifiedCount: 1
}
```

#### 7.3.2 updateMany() - 更新多个文档
```javascript
// 更新多个文档
db.users.updateMany(
  {tags: "developer"},           // 查询条件
  {
    $set: {
      role: "developer",
      updated_at: new Date()
    }
  }
)
```

#### 7.3.3 replaceOne() - 替换文档
```javascript
// 完全替换文档（保留_id）
db.users.replaceOne(
  {name: "John Doe"},
  {
    name: "John Doe",
    age: 32,
    email: "john.doe@example.com",
    role: "senior developer"
  }
)
```

### 7.4 删除操作

#### 7.4.1 deleteOne() - 删除单个文档
```javascript
// 删除单个文档
db.users.deleteOne({name: "John Doe"})

// 返回结果
{
  acknowledged: true,
  deletedCount: 1
}
```

#### 7.4.2 deleteMany() - 删除多个文档
```javascript
// 删除多个文档
db.users.deleteMany({
  age: {$lt: 25}    // 删除所有年龄小于25的用户
})
```

### 7.5 批量写入

```javascript
// 批量插入和更新
db.users.bulkWrite([
  {
    insertOne: {
      document: {name: "User 1", age: 25}
    }
  },
  {
    updateOne: {
      filter: {name: "User 2"},
      update: {$set: {age: 30}}
    }
  },
  {
    deleteOne: {
      filter: {name: "Old User"}
    }
  }
])
```

## 8. 最佳实践

### 8.1 设计原则

#### 8.1.1 文档设计
```javascript
// ✅ 好的设计 - 嵌入相关数据
{
  _id: ObjectId("..."),
  name: "John Doe",
  email: "john@example.com",
  address: {                    // 嵌入地址信息
    street: "123 Main St",
    city: "New York",
    zipCode: "10001"
  },
  contact: {                    // 嵌入联系信息
    phone: "+1-555-0123",
    emergency_contact: "Jane Doe"
  }
}

// ❌ 避免 - 过度规范化
{
  _id: ObjectId("..."),
  name: "John Doe",
  address_id: ObjectId("..."),    // 引用其他集合
  contact_id: ObjectId("...")
}
```

#### 8.1.2 数组使用
```javascript
// ✅ 适中的数组大小
{
  name: "User",
  skills: ["JavaScript", "MongoDB", "Node.js"],    // 小数组
  recent_logins: [                                 // 时间序列
    new Date("2024-01-01"),
    new Date("2024-01-02"),
    new Date("2024-01-03")
  ]
}

// ❌ 避免 - 数组过大
{
  name: "User",
  logs: [/* 10000+ log entries */]    // 大数组影响性能
}
```

### 8.2 性能优化

#### 8.2.1 索引使用
```javascript
// 创建索引
db.users.createIndex({name: 1})
db.users.createIndex({email: 1}, {unique: true})
db.users.createIndex({tags: 1, age: 1})

// 复合索引
db.products.createIndex({
  category: 1,
  brand: 1,
  price: -1
})

// 数组索引
db.users.createIndex({tags: 1})
db.users.createIndex({"address.city": 1})
```

#### 8.2.2 查询优化
```javascript
// 使用投影减少数据传输
db.users.find({}, {name: 1, email: 1, _id: 0})

// 使用limit限制结果数量
db.users.find().limit(10)

// 使用hint强制使用特定索引
db.users.find({tags: "mongodb"}).hint({tags: 1})

// 避免返回大文档
db.users.find({}, {name: 1, tags: 1}).limit(100)
```

### 8.3 数据一致性

#### 8.3.1 引用vs嵌入
```javascript
// 嵌入适合 - 强一致性需求
{
  user_id: ObjectId("..."),
  order_date: new Date(),
  total_amount: 150.00,
  items: [                    // 嵌入订单项
    {product_id: "prod1", quantity: 2, price: 25.00},
    {product_id: "prod2", quantity: 1, price: 100.00}
  ]
}

// 引用适合 - 分离数据，分级数据
{
  _id: ObjectId("..."),
  user_id: ObjectId("..."),
  order_date: new Date(),
  total_amount: 150.00,
  item_ids: [ObjectId("item1"), ObjectId("item2")]  // 引用订单项
}
```

### 8.4 迁移策略

```javascript
// 版本化文档结构
{
  _id: ObjectId("..."),
  version: 2,                    // 文档版本
  name: "John Doe",
  email: "john@example.com",
  // v1字段
  // v2新增字段
}

// 使用聚合管道进行迁移
db.users.aggregate([
  {
    $addFields: {
      version: 2,
      updated_at: new Date()
    }
  },
  {
    $merge: {
      into: "users_v2",
      whenMatched: "replace"
    }
  }
])
```

---

*第1章涵盖了MongoDB的基础概念、安装配置和基本操作。通过本章的学习，您将掌握MongoDB的基本使用方法，为后续的深入学习打下坚实基础。*