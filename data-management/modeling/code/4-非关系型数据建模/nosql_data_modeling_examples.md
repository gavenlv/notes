# 非关系型数据建模示例代码

本文件包含不同类型非关系型数据库的数据建模实例代码，涵盖文档型、键值型、列族型、图形型和时间序列数据库。

## 1. MongoDB（文档型数据库）

### 1.1 数据库连接与基本操作

```javascript
// 使用Node.js和MongoDB驱动
const { MongoClient } = require('mongodb');

// 连接字符串
const uri = 'mongodb://localhost:27017';
const client = new MongoClient(uri);

async function main() {
  try {
    // 连接数据库
    await client.connect();
    console.log('Connected to MongoDB');

    // 获取数据库和集合
    const db = client.db('ecommerce');
    const usersCollection = db.collection('users');
    const productsCollection = db.collection('products');
    const ordersCollection = db.collection('orders');

    // 1. 创建用户
    const user = {
      username: 'john_doe',
      email: 'john.doe@example.com',
      password: 'hashed_password',
      profile: {
        firstName: 'John',
        lastName: 'Doe',
        address: {
          street: '123 Main St',
          city: 'New York',
          state: 'NY',
          zip: '10001',
          country: 'USA'
        },
        phone: '123-456-7890'
      },
      createdAt: new Date(),
      updatedAt: new Date()
    };
    const result = await usersCollection.insertOne(user);
    console.log(`User created with ID: ${result.insertedId}`);

    // 2. 创建产品
    const product = {
      name: 'Dell XPS 13',
      description: '13-inch laptop with 11th Gen Intel Core processor',
      price: 999.99,
      category: 'Electronics',
      subcategory: 'Laptops',
      brand: 'Dell',
      specs: {
        processor: 'Intel Core i7-1165G7',
        ram: '16GB',
        storage: '512GB SSD',
        display: '13.4-inch FHD+'
      },
      stock: 50,
      images: [
        'https://example.com/images/xps13-1.jpg',
        'https://example.com/images/xps13-2.jpg'
      ],
      tags: ['laptop', 'dell', 'ultrabook'],
      createdAt: new Date(),
      updatedAt: new Date()
    };
    const productResult = await productsCollection.insertOne(product);
    console.log(`Product created with ID: ${productResult.insertedId}`);

    // 3. 创建订单
    const order = {
      userId: result.insertedId,
      orderDate: new Date(),
      status: 'shipped',
      shippingAddress: {
        street: '123 Main St',
        city: 'New York',
        state: 'NY',
        zip: '10001',
        country: 'USA'
      },
      items: [
        {
          productId: productResult.insertedId,
          name: 'Dell XPS 13',
          price: 999.99,
          quantity: 1
        },
        {
          productId: '609c8e6b6b7d4f0017a1b2c6', // 假设的产品ID
          name: 'Wireless Mouse',
          price: 29.99,
          quantity: 2
        }
      ],
      totalAmount: 1059.97,
      paymentMethod: 'credit_card',
      paymentStatus: 'completed',
      trackingNumber: '1Z999AA10123456784',
      createdAt: new Date(),
      updatedAt: new Date()
    };
    const orderResult = await ordersCollection.insertOne(order);
    console.log(`Order created with ID: ${orderResult.insertedId}`);

    // 4. 查询示例
    // 查询用户的所有订单
    const userOrders = await ordersCollection.find({ userId: result.insertedId }).toArray();
    console.log('User orders:', userOrders);

    // 查询特定产品的所有订单
    const productOrders = await ordersCollection.find({
      'items.productId': productResult.insertedId
    }).toArray();
    console.log('Product orders:', productOrders);

    // 5. 更新示例
    await productsCollection.updateOne(
      { _id: productResult.insertedId },
      { $inc: { stock: -1 } }
    );
    console.log('Product stock updated');

  } catch (error) {
    console.error('Error:', error);
  } finally {
    // 关闭连接
    await client.close();
    console.log('Disconnected from MongoDB');
  }
}

main();
```

### 1.2 索引创建

```javascript
// 创建索引
async function createIndexes() {
  try {
    await client.connect();
    const db = client.db('ecommerce');
    const usersCollection = db.collection('users');
    const productsCollection = db.collection('products');
    const ordersCollection = db.collection('orders');

    // 创建用户邮箱索引
    await usersCollection.createIndex({ email: 1 }, { unique: true });
    
    // 创建产品名称和分类索引
    await productsCollection.createIndex({ name: 1 });
    await productsCollection.createIndex({ category: 1, subcategory: 1 });
    
    // 创建订单用户ID和日期索引
    await ordersCollection.createIndex({ userId: 1, orderDate: -1 });
    
    console.log('Indexes created successfully');
  } catch (error) {
    console.error('Error creating indexes:', error);
  } finally {
    await client.close();
  }
}
```

## 2. Redis（键值型数据库）

### 2.1 基本操作

```javascript
// 使用Node.js和Redis驱动
const redis = require('redis');

// 创建客户端
const client = redis.createClient({
  url: 'redis://localhost:6379'
});

async function main() {
  try {
    // 连接数据库
    await client.connect();
    console.log('Connected to Redis');

    // 1. 字符串操作
    // 用户信息
    await client.hSet('user:1001', {
      name: 'John Doe',
      email: 'john.doe@example.com',
      age: 30
    });
    
    // 获取用户信息
    const user = await client.hGetAll('user:1001');
    console.log('User:', user);

    // 2. 集合操作
    // 用户关注关系
    await client.sAdd('following:1001', '1002', '1003', '1004');
    await client.sAdd('followers:1002', '1001', '1005');
    
    // 获取用户1001的关注列表
    const following = await client.sMembers('following:1001');
    console.log('User 1001 follows:', following);

    // 3. 列表操作
    // 用户帖子
    await client.lPush('posts:1001', 'Post content 1', 'Post content 2');
    
    // 获取用户1001的最新帖子
    const posts = await client.lRange('posts:1001', 0, -1);
    console.log('User 1001 posts:', posts);

    // 4. 有序集合操作
    // 帖子点赞
    await client.zAdd('post:likes:2001', {
      score: 1621000000, // 时间戳
      value: '1001'
    });
    await client.zAdd('post:likes:2001', {
      score: 1621000100, // 时间戳
      value: '1002'
    });
    
    // 实时排行榜
    await client.zAdd('leaderboard:weekly', {
      score: 1500,
      value: '1001'
    });
    await client.zAdd('leaderboard:weekly', {
      score: 1200,
      value: '1002'
    });
    await client.zAdd('leaderboard:weekly', {
      score: 900,
      value: '1003'
    });
    
    // 获取排行榜前三名
    const leaderboard = await client.zRange('leaderboard:weekly', 0, 2, { REV: true, WITHSCORES: true });
    console.log('Leaderboard:', leaderboard);

    // 5. 计数器操作
    // 页面访问量
    await client.incr('page:views:home');
    await client.incr('page:views:profile');
    
    // 获取页面访问量
    const homeViews = await client.get('page:views:home');
    const profileViews = await client.get('page:views:profile');
    console.log('Home views:', homeViews, 'Profile views:', profileViews);

    // 6. 设置过期时间
    // 用户在线状态
    await client.set('user:online:1001', 'true', { EX: 3600 });
    await client.set('user:online:1002', 'true', { EX: 3600 });
    
    // 检查用户在线状态
    const isUser1001Online = await client.get('user:online:1001');
    console.log('User 1001 is online:', isUser1001Online);

  } catch (error) {
    console.error('Error:', error);
  } finally {
    // 关闭连接
    await client.quit();
    console.log('Disconnected from Redis');
  }
}

main();
```

## 3. Cassandra（列族型数据库）

### 3.1 基本操作

```cql
-- 创建键空间
CREATE KEYSPACE iot WITH replication = {
  'class': 'SimpleStrategy',
  'replication_factor': 3
};

-- 使用键空间
USE iot;

-- 创建传感器数据表
CREATE TABLE sensor_data (
  device_id UUID,
  sensor_type TEXT,
  timestamp TIMESTAMP,
  value DOUBLE,
  PRIMARY KEY ((device_id, sensor_type), timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

-- 创建设备信息表
CREATE TABLE device_info (
  device_id UUID PRIMARY KEY,
  device_name TEXT,
  location TEXT,
  status TEXT,
  last_seen TIMESTAMP
);

-- 插入设备信息
INSERT INTO device_info (device_id, device_name, location, status, last_seen)
VALUES (uuid(), 'Temperature Sensor 1', 'Building A, Floor 1', 'active', toTimestamp(now()));

-- 插入多个传感器数据点
INSERT INTO sensor_data (device_id, sensor_type, timestamp, value)
VALUES (uuid(), 'temperature', toTimestamp(now()), 22.5);

INSERT INTO sensor_data (device_id, sensor_type, timestamp, value)
VALUES (uuid(), 'temperature', toTimestamp(now()), 22.7);

INSERT INTO sensor_data (device_id, sensor_type, timestamp, value)
VALUES (uuid(), 'humidity', toTimestamp(now()), 45.2);

INSERT INTO sensor_data (device_id, sensor_type, timestamp, value)
VALUES (uuid(), 'humidity', toTimestamp(now()), 45.5);

-- 查询特定设备的温度数据（最近10条）
SELECT * FROM sensor_data 
WHERE device_id = ? AND sensor_type = 'temperature'
ORDER BY timestamp DESC LIMIT 10;

-- 查询特定设备和时间范围的所有传感器数据
SELECT * FROM sensor_data 
WHERE device_id = ? AND sensor_type IN ('temperature', 'humidity')
AND timestamp >= '2023-05-01T00:00:00Z' AND timestamp <= '2023-05-31T23:59:59Z'
ORDER BY timestamp DESC;

-- 更新设备状态
UPDATE device_info 
SET status = 'inactive', last_seen = toTimestamp(now())
WHERE device_id = ?;

-- 删除旧数据（超过30天）
DELETE FROM sensor_data 
WHERE device_id = ? AND sensor_type = 'temperature'
AND timestamp < toTimestamp(now() - 30d);
```

### 3.2 复合查询和聚合

```cql
-- 创建用于聚合查询的表
CREATE TABLE daily_averages (
  device_id UUID,
  sensor_type TEXT,
  date DATE,
  avg_value DOUBLE,
  min_value DOUBLE,
  max_value DOUBLE,
  PRIMARY KEY ((device_id, sensor_type), date)
) WITH CLUSTERING ORDER BY (date DESC);

-- 插入每日平均值（通常通过ETL或批处理作业完成）
INSERT INTO daily_averages (device_id, sensor_type, date, avg_value, min_value, max_value)
VALUES (uuid(), 'temperature', '2023-05-15', 22.5, 20.1, 25.3);

-- 查询月度平均值
SELECT sensor_type, avg(avg_value) AS monthly_avg
FROM daily_averages
WHERE device_id = ? AND date >= '2023-05-01' AND date <= '2023-05-31'
GROUP BY sensor_type;
```

## 4. Neo4j（图形型数据库）

### 4.1 基本操作

```cypher
-- 创建节点
CREATE (john:Person {name: 'John Doe', age: 30, city: 'New York'})
CREATE (jane:Person {name: 'Jane Smith', age: 28, city: 'London'})
CREATE (bob:Person {name: 'Bob Johnson', age: 35, city: 'Paris'})
CREATE (alice:Person {name: 'Alice Williams', age: 25, city: 'New York'})

CREATE (neo4j:Company {name: 'Neo4j', industry: 'Software'})
CREATE (oracle:Company {name: 'Oracle', industry: 'Software'})

CREATE (graphdb:Technology {name: 'Graph Database', category: 'Database'})
CREATE (sql:Technology {name: 'SQL', category: 'Database'})

-- 创建关系
CREATE (john)-[:FRIENDS_WITH]->(jane)
CREATE (john)-[:FRIENDS_WITH]->(bob)
CREATE (jane)-[:FRIENDS_WITH]->(alice)
CREATE (bob)-[:FRIENDS_WITH]->(alice)

CREATE (john)-[:WORKS_AT {position: 'Developer', since: 2020}]->(neo4j)
CREATE (jane)-[:WORKS_AT {position: 'Manager', since: 2019}]->(oracle)
CREATE (bob)-[:WORKS_AT {position: 'Architect', since: 2018}]->(neo4j)

CREATE (john)-[:INTERESTED_IN]->(graphdb)
CREATE (jane)-[:INTERESTED_IN]->(sql)
CREATE (bob)-[:INTERESTED_IN]->(graphdb)
CREATE (alice)-[:INTERESTED_IN]->(graphdb)
CREATE (alice)-[:INTERESTED_IN]->(sql)

-- 查询示例
-- 1. 查找John的所有朋友
MATCH (john:Person {name: 'John Doe'})-[:FRIENDS_WITH]->(friend)
RETURN friend.name, friend.city

-- 2. 查找John的朋友的朋友
MATCH (john:Person {name: 'John Doe'})-[:FRIENDS_WITH]->()-[:FRIENDS_WITH]->(friend_of_friend)
RETURN DISTINCT friend_of_friend.name

-- 3. 查找在Neo4j工作的人及其感兴趣的技术
MATCH (person:Person)-[:WORKS_AT]->(company:Company {name: 'Neo4j'})-[:INTERESTED_IN]->(tech)
RETURN person.name, tech.name, tech.category

-- 4. 查找对图形数据库感兴趣的人所在的城市
MATCH (person:Person)-[:INTERESTED_IN]->(:Technology {name: 'Graph Database'})
RETURN person.city, count(person) AS person_count
ORDER BY person_count DESC

-- 5. 查找共同朋友
MATCH (a:Person {name: 'John Doe'})-[:FRIENDS_WITH]->(common)-[:FRIENDS_WITH]->(b:Person {name: 'Alice Williams'})
RETURN common.name

-- 6. 查找最短路径
MATCH p=shortestPath((john:Person {name: 'John Doe'})-[*]-(jane:Person {name: 'Jane Smith'}))
RETURN p

-- 7. 更新节点属性
MATCH (person:Person {name: 'John Doe'})
SET person.age = 31, person.updatedAt = datetime()
RETURN person

-- 8. 删除关系
MATCH (john:Person {name: 'John Doe'})-[r:FRIENDS_WITH]->(bob:Person {name: 'Bob Johnson'})
DELETE r

-- 9. 删除节点（需要先删除所有关系）
MATCH (person:Person {name: 'Bob Johnson'})
DETACH DELETE person
```

### 4.2 使用Python进行Neo4j操作

```python
from neo4j import GraphDatabase

# 连接信息
uri = "bolt://localhost:7687"
username = "neo4j"
password = "password"

# 创建驱动和会话
driver = GraphDatabase.driver(uri, auth=(username, password))

def create_social_graph():
    with driver.session() as session:
        # 创建节点
        session.run("""
        CREATE (john:Person {name: 'John Doe', age: 30, city: 'New York'})
        CREATE (jane:Person {name: 'Jane Smith', age: 28, city: 'London'})
        CREATE (bob:Person {name: 'Bob Johnson', age: 35, city: 'Paris'})
        """)
        
        # 创建关系
        session.run("""
        MATCH (john:Person {name: 'John Doe'})
        MATCH (jane:Person {name: 'Jane Smith'})
        CREATE (john)-[:FRIENDS_WITH]->(jane)
        """)

def find_friends(name):
    with driver.session() as session:
        result = session.run("""
        MATCH (person:Person {name: $name})-[:FRIENDS_WITH]->(friend)
        RETURN friend.name, friend.city
        """, name=name)
        
        return [(record["friend.name"], record["friend.city"]) for record in result]

# 示例使用
if __name__ == "__main__":
    create_social_graph()
    johns_friends = find_friends("John Doe")
    print("John's friends:", johns_friends)
    
    # 关闭驱动
    driver.close()
```

## 5. InfluxDB（时间序列数据库）

### 5.1 基本操作

```influxql
-- 创建数据库
CREATE DATABASE monitoring;

-- 使用数据库
USE monitoring;

-- 创建数据保留策略
CREATE RETENTION POLICY "30d" ON "monitoring" DURATION 30d REPLICATION 1 DEFAULT;
CREATE RETENTION POLICY "1y" ON "monitoring" DURATION 365d REPLICATION 1;

-- 创建连续查询（降采样）
CREATE CONTINUOUS QUERY "cpu_hourly" ON "monitoring"
BEGIN
  SELECT mean(usage_user) AS usage_user, mean(usage_system) AS usage_system
  INTO "30d".:MEASUREMENT
  FROM cpu
  GROUP BY time(1h), *
END;

-- 插入数据点
INSERT INTO monitoring
measurement cpu,
host=server01,region=us-east,
usage_user=90.5,usage_system=5.7,usage_idle=3.8

INSERT INTO monitoring
measurement memory,
host=server01,region=us-east,
used=8500,free=1500,total=10000

INSERT INTO monitoring
measurement disk,
host=server01,region=us-east,device=/dev/sda1,
used=4000,free=1000,total=5000

-- 查询示例
-- 1. 查询过去24小时内server01的CPU使用率
SELECT usage_user, usage_system FROM cpu WHERE host = 'server01' AND time > now() - 24h;

-- 2. 查询所有服务器的平均内存使用情况
SELECT mean(used) FROM memory GROUP BY host;

-- 3. 查询特定时间范围的磁盘使用情况
SELECT used, free FROM disk WHERE host = 'server01' AND device = '/dev/sda1' 
AND time >= '2023-05-01T00:00:00Z' AND time <= '2023-05-31T23:59:59Z';

-- 4. 使用降采样数据
SELECT usage_user, usage_system FROM "30d".cpu WHERE host = 'server01' AND time > now() - 7d;

-- 5. 聚合查询
SELECT mean(usage_user) AS avg_cpu, max(usage_user) AS max_cpu
FROM cpu WHERE host = 'server01' AND time > now() - 1d
GROUP BY time(1h);
```

### 5.2 使用Python进行InfluxDB操作

```python
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import time

# 连接信息
url = "http://localhost:8086"
token = "your-token"
org = "your-org"
bucket = "monitoring"

# 创建客户端
client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()

def write_server_metrics():
    # 写入CPU数据
    cpu_point = Point("cpu")
    .tag("host", "server01")
    .tag("region", "us-east")
    .field("usage_user", 90.5)
    .field("usage_system", 5.7)
    .field("usage_idle", 3.8)
    .time(time.time_ns())
    
    # 写入内存数据
    memory_point = Point("memory")
    .tag("host", "server01")
    .tag("region", "us-east")
    .field("used", 8500)
    .field("free", 1500)
    .field("total", 10000)
    .time(time.time_ns())
    
    # 写入磁盘数据
    disk_point = Point("disk")
    .tag("host", "server01")
    .tag("region", "us-east")
    .tag("device", "/dev/sda1")
    .field("used", 4000)
    .field("free", 1000)
    .field("total", 5000)
    .time(time.time_ns())
    
    # 写入所有数据点
    write_api.write(bucket=bucket, org=org, record=[cpu_point, memory_point, disk_point])
    print("Metrics written successfully")

def query_cpu_metrics():
    # 查询过去24小时的CPU数据
    query = f"""
    from(bucket: "{bucket}")
      |> range(start: -24h)
      |> filter(fn: (r) => r["_measurement"] == "cpu")
      |> filter(fn: (r) => r["host"] == "server01")
      |> filter(fn: (r) => r["_field"] == "usage_user" or r["_field"] == "usage_system")
    """
    
    result = query_api.query(org=org, query=query)
    
    # 处理查询结果
    for table in result:
        for record in table.records:
            print(f"Time: {record.get_time()}, Field: {record.get_field()}, Value: {record.get_value()}")

# 示例使用
if __name__ == "__main__":
    write_server_metrics()
    query_cpu_metrics()
    
    # 关闭客户端
    client.close()
```

## 6. 最佳实践总结

### 6.1 文档型数据库（MongoDB）
- 使用有意义的集合名称
- 合理嵌入数据以减少查询次数
- 为常用查询字段创建索引
- 避免文档过大（MongoDB限制16MB）
- 使用分片处理大规模数据集

### 6.2 键值型数据库（Redis）
- 使用统一的键命名规范（如`object:id:property`）
- 根据数据类型选择合适的数据结构
- 合理设置键的过期时间
- 使用管道（Pipeline）减少网络往返
- 考虑数据持久化策略

### 6.3 列族型数据库（Cassandra）
- 行键设计应均匀分布，避免热点
- 将经常一起访问的列放在同一列族
- 使用复合主键优化查询
- 避免宽行设计
- 使用批量操作提高性能

### 6.4 图形型数据库（Neo4j）
- 为节点和关系使用有意义的标签和类型
- 为常用查询属性创建索引
- 限制图遍历的深度
- 使用参数化查询提高性能和安全性
- 考虑使用批量导入工具处理大量数据

### 6.5 时间序列数据库（InfluxDB）
- 将常用过滤条件设为标签
- 将实际测量值设为字段
- 设置合理的数据保留策略
- 使用连续查询进行数据降采样
- 使用批量写入提高性能

## 7. 运行说明

### 7.1 MongoDB
1. 安装MongoDB并启动服务
2. 安装Node.js和MongoDB驱动：`npm install mongodb`
3. 运行代码：`node mongodb_example.js`

### 7.2 Redis
1. 安装Redis并启动服务
2. 安装Node.js和Redis驱动：`npm install redis`
3. 运行代码：`node redis_example.js`

### 7.3 Cassandra
1. 安装Cassandra并启动服务
2. 使用cqlsh或其他客户端执行CQL语句

### 7.4 Neo4j
1. 安装Neo4j并启动服务
2. 使用Neo4j Browser或cypher-shell执行Cypher语句
3. 对于Python示例，安装Neo4j驱动：`pip install neo4j`

### 7.5 InfluxDB
1. 安装InfluxDB并启动服务
2. 使用influx CLI或其他客户端执行InfluxQL语句
3. 对于Python示例，安装InfluxDB客户端：`pip install influxdb-client`

## 8. 注意事项

1. 示例代码中的连接字符串、用户名、密码等需要根据实际环境修改
2. 生产环境中应使用安全的认证和授权机制
3. 大规模部署时应考虑数据分片、复制和备份策略
4. 根据实际业务需求选择合适的数据库类型和数据模型
5. 定期监控数据库性能并进行优化

通过这些示例代码，您可以了解不同类型非关系型数据库的数据建模方法和最佳实践。在实际应用中，需要根据具体业务需求和数据特点选择合适的数据库类型和数据模型设计方案。