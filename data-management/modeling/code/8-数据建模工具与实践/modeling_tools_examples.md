# 第8章：数据建模工具与实践 - 代码示例

## 8.1 MySQL Workbench 使用示例

### 8.1.1 创建新模型

1. 打开MySQL Workbench
2. 点击"File" -> "New Model"
3. 在"Model Overview"中选择"Add Diagram"

### 8.1.2 添加表

在ER图编辑器中，点击工具栏中的"Add Table"按钮，然后在画布上点击添加表。

### 8.1.3 编辑表结构

```sql
-- 用户表
CREATE TABLE `user` (
  `user_id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `email` VARCHAR(100) NOT NULL,
  `phone` VARCHAR(20) NOT NULL,
  `registration_time` DATETIME NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC) VISIBLE,
  UNIQUE INDEX `email_UNIQUE` (`email` ASC) VISIBLE)
ENGINE = InnoDB;

-- 地址表
CREATE TABLE `address` (
  `address_id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `recipient` VARCHAR(50) NOT NULL,
  `phone` VARCHAR(20) NOT NULL,
  `province` VARCHAR(50) NOT NULL,
  `city` VARCHAR(50) NOT NULL,
  `district` VARCHAR(50) NOT NULL,
  `detail_address` VARCHAR(200) NOT NULL,
  `is_default` TINYINT NOT NULL DEFAULT 0,
  PRIMARY KEY (`address_id`),
  INDEX `fk_address_user_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_address_user`
    FOREIGN KEY (`user_id`)
    REFERENCES `user` (`user_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

-- 分类表
CREATE TABLE `category` (
  `category_id` INT NOT NULL AUTO_INCREMENT,
  `category_name` VARCHAR(50) NOT NULL,
  `parent_category_id` INT NULL,
  PRIMARY KEY (`category_id`),
  INDEX `fk_category_category_idx` (`parent_category_id` ASC) VISIBLE,
  CONSTRAINT `fk_category_category`
    FOREIGN KEY (`parent_category_id`)
    REFERENCES `category` (`category_id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE)
ENGINE = InnoDB;

-- 产品表
CREATE TABLE `product` (
  `product_id` INT NOT NULL AUTO_INCREMENT,
  `category_id` INT NOT NULL,
  `product_name` VARCHAR(100) NOT NULL,
  `description` TEXT NULL,
  `price` DECIMAL(10,2) NOT NULL,
  `stock` INT NOT NULL DEFAULT 0,
  `image` VARCHAR(255) NULL,
  `creation_time` DATETIME NOT NULL,
  PRIMARY KEY (`product_id`),
  INDEX `fk_product_category_idx` (`category_id` ASC) VISIBLE,
  CONSTRAINT `fk_product_category`
    FOREIGN KEY (`category_id`)
    REFERENCES `category` (`category_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

-- 订单表
CREATE TABLE `order` (
  `order_id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `address_id` INT NOT NULL,
  `order_time` DATETIME NOT NULL,
  `total_amount` DECIMAL(10,2) NOT NULL,
  `order_status` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`order_id`),
  INDEX `fk_order_user_idx` (`user_id` ASC) VISIBLE,
  INDEX `fk_order_address_idx` (`address_id` ASC) VISIBLE,
  CONSTRAINT `fk_order_user`
    FOREIGN KEY (`user_id`)
    REFERENCES `user` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_order_address`
    FOREIGN KEY (`address_id`)
    REFERENCES `address` (`address_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

-- 订单明细表
CREATE TABLE `order_item` (
  `order_item_id` INT NOT NULL AUTO_INCREMENT,
  `order_id` INT NOT NULL,
  `product_id` INT NOT NULL,
  `quantity` INT NOT NULL,
  `unit_price` DECIMAL(10,2) NOT NULL,
  PRIMARY KEY (`order_item_id`),
  INDEX `fk_order_item_order_idx` (`order_id` ASC) VISIBLE,
  INDEX `fk_order_item_product_idx` (`product_id` ASC) VISIBLE,
  CONSTRAINT `fk_order_item_order`
    FOREIGN KEY (`order_id`)
    REFERENCES `order` (`order_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_order_item_product`
    FOREIGN KEY (`product_id`)
    REFERENCES `product` (`product_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

-- 支付表
CREATE TABLE `payment` (
  `payment_id` INT NOT NULL AUTO_INCREMENT,
  `order_id` INT NOT NULL,
  `payment_method` VARCHAR(20) NOT NULL,
  `payment_amount` DECIMAL(10,2) NOT NULL,
  `payment_time` DATETIME NOT NULL,
  `payment_status` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`payment_id`),
  UNIQUE INDEX `order_id_UNIQUE` (`order_id` ASC) VISIBLE,
  CONSTRAINT `fk_payment_order`
    FOREIGN KEY (`order_id`)
    REFERENCES `order` (`order_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

-- 物流表
CREATE TABLE `shipping` (
  `shipping_id` INT NOT NULL AUTO_INCREMENT,
  `order_id` INT NOT NULL,
  `shipping_company` VARCHAR(50) NOT NULL,
  `shipping_number` VARCHAR(50) NOT NULL,
  `shipping_status` VARCHAR(20) NOT NULL,
  `ship_time` DATETIME NULL,
  `sign_time` DATETIME NULL,
  PRIMARY KEY (`shipping_id`),
  UNIQUE INDEX `order_id_UNIQUE` (`order_id` ASC) VISIBLE,
  CONSTRAINT `fk_shipping_order`
    FOREIGN KEY (`order_id`)
    REFERENCES `order` (`order_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;
```

### 8.1.4 生成SQL脚本

1. 在MySQL Workbench中，点击"Database" -> "Forward Engineer"
2. 连接到MySQL服务器
3. 选择要生成的对象（表、索引、外键等）
4. 点击"Next" -> "Execute"生成数据库

## 8.2 MongoDB Compass 使用示例

### 8.2.1 连接到MongoDB

1. 打开MongoDB Compass
2. 输入连接字符串（例如：`mongodb://localhost:27017`）
3. 点击"Connect"连接到MongoDB服务器

### 8.2.2 创建数据库和集合

1. 点击"Create Database"
2. 输入数据库名称（例如：`ecommerce`）
3. 输入集合名称（例如：`users`）
4. 点击"Create Database"

### 8.2.3 插入文档

```javascript
// 插入用户文档
{
  "username": "john_doe",
  "password": "hashed_password",
  "email": "john@example.com",
  "phone": "13800138000",
  "registration_time": ISODate("2023-01-01T00:00:00Z"),
  "addresses": [
    {
      "recipient": "John Doe",
      "phone": "13800138000",
      "province": "California",
      "city": "Los Angeles",
      "district": "LA County",
      "detail_address": "123 Main St",
      "is_default": true
    }
  ]
}

// 插入产品文档
{
  "category_id": ObjectId("636b9c9a8f8e8a0011e7a0b1"),
  "product_name": "iPhone 14 Pro",
  "description": "Latest iPhone model",
  "price": 999.99,
  "stock": 100,
  "image": "iphone14pro.jpg",
  "creation_time": ISODate("2023-01-01T00:00:00Z")
}

// 插入订单文档
{
  "user_id": ObjectId("636b9c9a8f8e8a0011e7a0b0"),
  "address": {
    "recipient": "John Doe",
    "phone": "13800138000",
    "province": "California",
    "city": "Los Angeles",
    "district": "LA County",
    "detail_address": "123 Main St"
  },
  "order_time": ISODate("2023-01-02T10:00:00Z"),
  "total_amount": 999.99,
  "order_status": "pending",
  "items": [
    {
      "product_id": ObjectId("636b9c9a8f8e8a0011e7a0b1"),
      "quantity": 1,
      "unit_price": 999.99
    }
  ],
  "payment": {
    "payment_method": "credit_card",
    "payment_amount": 999.99,
    "payment_time": ISODate("2023-01-02T10:05:00Z"),
    "payment_status": "completed"
  },
  "shipping": {
    "shipping_company": "UPS",
    "shipping_number": "1Z999AA10123456784",
    "shipping_status": "shipped",
    "ship_time": ISODate("2023-01-03T08:00:00Z")
  }
}
```

### 8.2.4 查询文档

```javascript
// 查询所有用户
db.users.find()

// 查询特定用户
db.users.find({ "username": "john_doe" })

// 查询订单总额大于500的订单
db.orders.find({ "total_amount": { $gt: 500 } })

// 查询包含特定产品的订单
db.orders.find({ "items.product_id": ObjectId("636b9c9a8f8e8a0011e7a0b1") })
```

## 8.3 Apache Hive 数据仓库建模示例

### 8.3.1 启动Hive CLI

```bash
hive
```

### 8.3.2 创建数据库和表

```sql
-- 创建数据库
CREATE DATABASE IF NOT EXISTS ecommerce;

-- 使用数据库
USE ecommerce;

-- 创建日期维度表
CREATE TABLE IF NOT EXISTS dim_date (
  date_id STRING,
  date DATE,
  year INT,
  quarter INT,
  month INT,
  day INT,
  weekday INT,
  is_weekend BOOLEAN
) ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t' STORED AS TEXTFILE;

-- 创建产品维度表
CREATE TABLE IF NOT EXISTS dim_product (
  product_id INT,
  product_name STRING,
  category_id INT,
  category_name STRING,
  brand STRING,
  price DECIMAL(10,2)
) ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t' STORED AS TEXTFILE;

-- 创建客户维度表
CREATE TABLE IF NOT EXISTS dim_customer (
  customer_id INT,
  customer_name STRING,
  email STRING,
  phone STRING,
  country STRING,
  city STRING
) ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t' STORED AS TEXTFILE;

-- 创建商店维度表
CREATE TABLE IF NOT EXISTS dim_store (
  store_id INT,
  store_name STRING,
  country STRING,
  city STRING
) ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t' STORED AS TEXTFILE;

-- 创建销售事实表
CREATE TABLE IF NOT EXISTS fact_sales (
  sale_id INT,
  date_id STRING,
  product_id INT,
  customer_id INT,
  store_id INT,
  quantity INT,
  unit_price DECIMAL(10,2),
  total_amount DECIMAL(10,2)
) ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t' STORED AS TEXTFILE;
```

### 8.3.3 加载数据

```sql
-- 加载日期维度数据
LOAD DATA LOCAL INPATH '/path/to/dim_date.txt' INTO TABLE dim_date;

-- 加载产品维度数据
LOAD DATA LOCAL INPATH '/path/to/dim_product.txt' INTO TABLE dim_product;

-- 加载客户维度数据
LOAD DATA LOCAL INPATH '/path/to/dim_customer.txt' INTO TABLE dim_customer;

-- 加载商店维度数据
LOAD DATA LOCAL INPATH '/path/to/dim_store.txt' INTO TABLE dim_store;

-- 加载销售事实数据
LOAD DATA LOCAL INPATH '/path/to/fact_sales.txt' INTO TABLE fact_sales;
```

### 8.3.4 查询数据

```sql
-- 查询每日销售额
SELECT d.date, SUM(f.total_amount) AS daily_sales
FROM fact_sales f
JOIN dim_date d ON f.date_id = d.date_id
GROUP BY d.date
ORDER BY d.date;

-- 查询产品类别销售统计
SELECT p.category_name, SUM(f.quantity) AS total_quantity, SUM(f.total_amount) AS total_sales
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.category_name
ORDER BY total_sales DESC;

-- 查询客户国家分布
SELECT c.country, COUNT(DISTINCT f.customer_id) AS customer_count, SUM(f.total_amount) AS total_sales
FROM fact_sales f
JOIN dim_customer c ON f.customer_id = c.customer_id
GROUP BY c.country
ORDER BY customer_count DESC;
```

## 8.4 Apache Flink 实时数据建模示例

### 8.4.1 环境准备

```xml
<!-- pom.xml -->
<dependencies>
    <dependency>
        <groupId>org.apache.flink</groupId>
        <artifactId>flink-java</artifactId>
        <version>1.16.0</version>
    </dependency>
    <dependency>
        <groupId>org.apache.flink</groupId>
        <artifactId>flink-streaming-java</artifactId>
        <version>1.16.0</version>
    </dependency>
    <dependency>
        <groupId>org.apache.flink</groupId>
        <artifactId>flink-connector-kafka</artifactId>
        <version>1.16.0</version>
    </dependency>
    <dependency>
        <groupId>org.apache.flink</groupId>
        <artifactId>flink-connector-jdbc</artifactId>
        <version>1.16.0</version>
    </dependency>
    <dependency>
        <groupId>org.apache.flink</groupId>
        <artifactId>flink-table-api-java-bridge</artifactId>
        <version>1.16.0</version>
    </dependency>
</dependencies>
```

### 8.4.2 数据流处理应用

```java
import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.windowing.assigners.TumblingProcessingTimeWindows;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaProducer;

import java.util.Properties;

public class RealTimeSalesAnalysis {
    public static void main(String[] args) throws Exception {
        // 设置执行环境
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        // 配置Kafka消费者
        Properties consumerProps = new Properties();
        consumerProps.setProperty("bootstrap.servers", "localhost:9092");
        consumerProps.setProperty("group.id", "sales-group");
        consumerProps.setProperty("auto.offset.reset", "latest");

        // 从Kafka读取销售数据
        DataStream<String> salesStream = env.addSource(
                new FlinkKafkaConsumer<>("sales-topic", new SimpleStringSchema(), consumerProps)
        );

        // 解析销售数据并转换为Tuple2<productId, amount>
        DataStream<Tuple2<Integer, Double>> productSalesStream = salesStream.map(new MapFunction<String, Tuple2<Integer, Double>>() {
            @Override
            public Tuple2<Integer, Double> map(String value) throws Exception {
                // 假设数据格式为: productId,quantity,unitPrice
                String[] fields = value.split(",");
                int productId = Integer.parseInt(fields[0]);
                int quantity = Integer.parseInt(fields[1]);
                double unitPrice = Double.parseDouble(fields[2]);
                double amount = quantity * unitPrice;
                return new Tuple2<>(productId, amount);
            }
        });

        // 按产品ID分组，计算每5分钟的销售额
        DataStream<Tuple2<Integer, Double>> windowedSalesStream = productSalesStream
                .keyBy(0)
                .window(TumblingProcessingTimeWindows.of(Time.minutes(5)))
                .sum(1);

        // 配置Kafka生产者
        Properties producerProps = new Properties();
        producerProps.setProperty("bootstrap.servers", "localhost:9092");

        // 将结果写入Kafka
        windowedSalesStream.map(new MapFunction<Tuple2<Integer, Double>, String>() {
            @Override
            public String map(Tuple2<Integer, Double> value) throws Exception {
                return value.f0 + "," + value.f1;
            }
        }).addSink(new FlinkKafkaProducer<>("sales-result-topic", new SimpleStringSchema(), producerProps));

        // 执行作业
        env.execute("Real Time Sales Analysis");
    }
}
```

### 8.4.3 Flink SQL 示例

```sql
-- 创建Kafka源表
CREATE TABLE sales_source (
    product_id INT,
    quantity INT,
    unit_price DOUBLE,
    event_time TIMESTAMP(3) METADATA FROM 'timestamp'
) WITH (
    'connector' = 'kafka',
    'topic' = 'sales-topic',
    'properties.bootstrap.servers' = 'localhost:9092',
    'properties.group.id' = 'sales-sql-group',
    'scan.startup.mode' = 'latest-offset',
    'format' = 'csv'
);

-- 创建Kafka结果表
CREATE TABLE sales_result (
    product_id INT,
    window_start TIMESTAMP(3),
    window_end TIMESTAMP(3),
    total_amount DOUBLE
) WITH (
    'connector' = 'kafka',
    'topic' = 'sales-sql-result',
    'properties.bootstrap.servers' = 'localhost:9092',
    'format' = 'csv'
);

-- 执行实时销售分析
INSERT INTO sales_result
SELECT 
    product_id,
    TUMBLE_START(event_time, INTERVAL '5' MINUTE) AS window_start,
    TUMBLE_END(event_time, INTERVAL '5' MINUTE) AS window_end,
    SUM(quantity * unit_price) AS total_amount
FROM sales_source
GROUP BY 
    product_id,
    TUMBLE(event_time, INTERVAL '5' MINUTE);
```

## 8.5 PowerDesigner 使用示例

### 8.5.1 创建概念数据模型(CDM)

1. 打开PowerDesigner
2. 点击"File" -> "New Model"
3. 选择"Conceptual Data Model"并点击"OK"
4. 在工具箱中选择"Entity"工具，在画布上点击创建实体
5. 双击实体，编辑实体属性
6. 使用"Relationship"工具创建实体之间的关系

### 8.5.2 转换为物理数据模型(PDM)

1. 在CDM中，点击"Tools" -> "Generate Physical Data Model"
2. 选择目标数据库（例如：MySQL 8.0）
3. 点击"OK"生成PDM

### 8.5.3 生成SQL脚本

1. 在PDM中，点击"Database" -> "Generate Database"
2. 选择输出目录和文件名
3. 点击"Generate"生成SQL脚本

## 8.6 数据建模工具比较

| 工具名称 | 类型 | 主要功能 | 适用场景 | 价格 |
|---------|------|---------|---------|------|
| MySQL Workbench | 关系型 | ER图设计、SQL开发、数据库管理 | 小型项目、MySQL数据库 | 免费 |
| PowerDesigner | 综合型 | CDM、PDM、OOM建模、正向/逆向工程 | 企业级项目、多种数据库 | 商业软件 |
| ER/Studio | 企业级 | 数据建模、元数据管理、数据 lineage | 大型企业、数据治理 | 商业软件 |
| MongoDB Compass | 文档型 | 可视化集合、查询构建、索引管理 | MongoDB数据库 | 免费 |
| Redis Insight | 键值型 | 可视化键空间、数据编辑、性能监控 | Redis数据库 | 免费 |
| Neo4j Browser | 图形型 | Cypher查询、数据可视化、导入导出 | Neo4j数据库 | 免费 |
| Apache Hive | 数据仓库 | 类SQL查询、数据仓库建模 | 大数据平台、数据仓库 | 开源免费 |
| Apache Flink | 实时处理 | 流处理、批处理、状态管理 | 实时数据处理、流分析 | 开源免费 |

## 8.7 最佳实践

### 8.7.1 工具选择

1. **根据项目规模选择**：小型项目可以选择免费工具（如MySQL Workbench、MongoDB Compass），大型项目可以选择企业级工具（如PowerDesigner、ER/Studio）

2. **根据数据库类型选择**：关系型数据库选择ER/Studio、PowerDesigner等，NoSQL数据库选择对应的官方工具

3. **考虑团队技能**：选择团队成员熟悉的工具，减少学习成本

### 8.7.2 建模流程

1. **遵循标准流程**：需求分析 -> 概念建模 -> 逻辑建模 -> 物理建模 -> 实现

2. **保持文档更新**：及时更新数据模型文档，确保文档与实际模型一致

3. **版本控制**：使用版本控制工具管理数据模型的变更

### 8.7.3 性能优化

1. **索引设计**：根据查询需求设计合适的索引

2. **分区表**：对大数据量的表进行分区，提高查询性能

3. **物化视图**：创建物化视图，加速复杂查询

### 8.7.4 团队协作

1. **建立命名规范**：统一命名规范，提高模型的可读性

2. **定期评审**：定期评审数据模型，确保其符合业务需求

3. **知识共享**：促进团队成员之间的知识共享，提高整体技能水平

## 8.8 部署与运行

### 8.8.1 MySQL Workbench

1. 下载地址：https://dev.mysql.com/downloads/workbench/
2. 安装步骤：
   - 运行安装程序
   - 按照向导完成安装
   - 启动MySQL Workbench

### 8.8.2 MongoDB Compass

1. 下载地址：https://www.mongodb.com/try/download/compass
2. 安装步骤：
   - 运行安装程序
   - 按照向导完成安装
   - 启动MongoDB Compass

### 8.8.3 Apache Hive

1. 安装Hadoop
2. 下载Hive：https://hive.apache.org/downloads.html
3. 解压并配置环境变量
4. 启动Hive服务：`hive --service metastore &` 和 `hive --service hiveserver2 &`
5. 连接Hive：`beeline -u jdbc:hive2://localhost:10000`

### 8.8.4 Apache Flink

1. 下载Flink：https://flink.apache.org/downloads.html
2. 解压并配置环境变量
3. 启动Flink集群：`./bin/start-cluster.sh`
4. 提交作业：`./bin/flink run -c com.example.RealTimeSalesAnalysis /path/to/real-time-sales-analysis.jar`

## 8.9 总结

本章介绍了几种常用的数据建模工具的使用方法和代码示例，包括关系型数据库建模工具（MySQL Workbench、PowerDesigner）、非关系型数据库建模工具（MongoDB Compass、Redis Insight、Neo4j Browser）、数据仓库建模工具（Apache Hive）和实时数据建模工具（Apache Flink）。

选择合适的数据建模工具对于提高数据建模效率和质量非常重要。需要根据项目规模、数据库类型、团队技能和预算等因素进行综合考虑。

通过遵循数据建模的最佳实践，可以创建高质量的数据模型，为业务提供有效的数据支持。同时，定期评审和优化数据模型，可以确保其始终符合业务需求和性能要求。