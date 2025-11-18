# 第4章：JMeter高级测试场景设计

## 4.1 复杂业务逻辑测试

### 4.1.1 业务流程建模

在实际应用中，用户操作往往不是孤立的请求，而是包含多个步骤的业务流程。JMeter可以通过逻辑控制器模拟复杂的用户行为。

**典型电商业务流程：**
```
用户登录 → 浏览商品 → 搜索商品 → 查看详情 → 添加购物车 → 结算下单 → 支付 → 订单查询
```

**JMeter实现方案：**
```
线程组：电商用户流程
├── 事务控制器：用户登录流程
├── 随机控制器：浏览行为（随机选择操作）
├── 如果控制器：根据库存状态决定是否购买
├── 循环控制器：重复浏览行为
└── 事务控制器：购买流程
```

### 4.1.2 条件逻辑测试

使用If控制器实现条件分支，模拟真实用户决策过程。

**If控制器配置示例：**
```properties
名称：库存充足时购买
条件：${__jexl3("${STOCK_STATUS}" == "available")}
表达式必须为：是
```

**完整条件逻辑示例：**
```
┌─────────────────┐
│   查看商品详情   │
└─────────┬───────┘
          │
┌─────────▼───────┐
│  If控制器：库存检查 │
└─────────┬───────┘
    ┌─────┴─────┐
    │           │
┌───▼───┐   ┌───▼───┐
│ 购买流程 │   │继续浏览│
└───────┘   └───────┘
```

### 4.1.3 数据依赖测试

处理请求之间的数据依赖关系，如登录后获取token用于后续请求。

**数据依赖处理流程：**
```
登录请求 → JSON提取器（提取token） → 后续请求使用${AUTH_TOKEN}
```

**JSON提取器配置：**
```properties
名称：提取用户Token
变量名称：AUTH_TOKEN
JSON路径表达式：$.data.access_token
匹配编号：0
缺省值：NOT_FOUND
```

## 4.2 数据库性能测试

### 4.2.1 JDBC连接配置

JMeter支持直接测试数据库性能，通过JDBC连接执行SQL查询。

**JDBC连接配置步骤：**
1. 添加JDBC连接配置
2. 配置数据库连接参数
3. 添加JDBC请求采样器
4. 配置SQL查询

**JDBC连接配置示例：**
```properties
名称：MySQL数据库连接
数据库URL：jdbc:mysql://localhost:3306/testdb
JDBC驱动类：com.mysql.cj.jdbc.Driver
用户名：testuser
密码：testpass
连接池配置：
├── 最大连接数：10
├── 超时时间：10000
└── 事务隔离级别：READ_COMMITTED
```

### 4.2.2 SQL查询测试

**简单查询示例：**
```properties
名称：查询用户信息
SQL查询：SELECT * FROM users WHERE username = ?
参数值：${USERNAME}
参数类型：VARCHAR
变量名称：user_count
```

**复杂查询示例：**
```properties
名称：统计订单数据
SQL查询：
SELECT 
    COUNT(*) as total_orders,
    SUM(amount) as total_amount,
    AVG(amount) as avg_amount
FROM orders 
WHERE create_time > ? AND status = ?

参数值：
├── ${START_TIME}
├── 'completed'
参数类型：
├── TIMESTAMP
├── VARCHAR
```

### 4.2.3 数据库压力测试场景

**典型数据库测试场景：**

1. **查询性能测试**：
   - 简单主键查询
   - 复杂联合查询
   - 大数据量分页查询

2. **写入性能测试**：
   - 单条记录插入
   - 批量数据插入
   - 更新操作测试

3. **事务性能测试**：
   - 简单事务
   - 复杂业务事务
   - 死锁检测

## 4.3 FTP文件传输测试

### 4.3.1 FTP请求配置

JMeter可以测试FTP服务器的性能，模拟文件上传下载操作。

**FTP请求基本配置：**
```properties
名称：FTP文件下载测试
服务器名称：ftp.example.com
端口：21
远程文件：/downloads/testfile.zip
本地文件：./downloads/testfile.zip
获取文件模式：ASCII或BINARY
用户名：ftpuser
密码：ftppass
```

### 4.3.2 FTP测试场景设计

**文件上传测试：**
```properties
名称：FTP文件上传
操作：STOR（上传文件）
本地文件：./uploads/sample.txt
远程文件：/uploads/sample_${__threadNum}.txt
```

**文件下载测试：**
```properties
名称：FTP文件下载
操作：RETR（下载文件）
远程文件：/downloads/largefile.iso
本地文件：./downloads/largefile_${__threadNum}.iso
```

**目录列表测试：**
```properties
名称：FTP目录列表
操作：LIST（列出目录）
远程目录：/uploads/
```

### 4.3.3 FTP性能指标

**关键性能指标：**
- **传输速率**：MB/s
- **连接时间**：建立FTP连接的时间
- **传输时间**：文件传输完成的时间
- **并发连接数**：同时处理的FTP连接数

## 4.4 Web服务测试

### 4.4.1 SOAP Web服务测试

JMeter支持测试基于SOAP协议的Web服务。

**SOAP请求配置：**
```properties
名称：SOAP用户查询服务
SOAP/XML-RPC数据：
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <getUser xmlns="http://example.com/webservice">
            <userId>${USER_ID}</userId>
        </getUser>
    </soap:Body>
</soap:Envelope>

URL：http://webservice.example.com/UserService
SOAPAction：getUser
```

### 4.4.2 REST API测试

**REST API请求示例：**

**GET请求：**
```properties
名称：GET用户信息
方法：GET
路径：/api/v1/users/${USER_ID}
```

**POST请求：**
```properties
名称：POST创建用户
方法：POST
路径：/api/v1/users
主体数据：
{
    "username": "${USERNAME}",
    "email": "${EMAIL}",
    "role": "${ROLE}"
}
```

**PUT请求：**
```properties
名称：PUT更新用户
方法：PUT
路径：/api/v1/users/${USER_ID}
主体数据：
{
    "email": "newemail@example.com",
    "status": "active"
}
```

**DELETE请求：**
```properties
名称：DELETE删除用户
方法：DELETE
路径：/api/v1/users/${USER_ID}
```

### 4.4.3 API身份验证测试

**基本认证：**
```properties
名称：Basic认证API
用户名：api_user
密码：api_pass
```

**Bearer Token认证：**
```properties
名称：JWT Token认证
在HTTP信息头管理器中添加：
Authorization: Bearer ${ACCESS_TOKEN}
```

**API Key认证：**
```properties
名称：API Key认证
在参数中添加：
api_key：${API_KEY}
```

## 4.5 自定义协议测试

### 4.5.1 TCP采样器测试

JMeter支持测试自定义TCP协议，适用于非HTTP协议的应用测试。

**TCP采样器配置：**
```properties
名称：TCP自定义协议测试
TCPClient类名：org.apache.jmeter.protocol.tcp.sampler.TCPClient
服务器名称：tcp.example.com
端口：9000
请求数据：${REQUEST_DATA}
重用连接：是
关闭连接：否
```

### 4.5.2 自定义协议实现

**实现自定义协议处理：**

1. **创建自定义TCPClient类：**
```java
public class CustomTCPClient extends TCPClient {
    @Override
    public void write(OutputStream os, String s) throws IOException {
        // 自定义协议编码
        byte[] data = encodeProtocol(s);
        os.write(data);
        os.flush();
    }
    
    @Override
    public String read(InputStream is) throws IOException {
        // 自定义协议解码
        return decodeProtocol(is);
    }
}
```

2. **在JMeter中配置：**
```properties
TCPClient类名：com.example.CustomTCPClient
```

### 4.5.3 Java请求采样器

对于更复杂的协议，可以使用Java请求采样器调用自定义Java代码。

**Java请求配置：**
```properties
名称：Java自定义协议测试
类名：com.example.CustomProtocolTest
```

## 4.6 实战示例：电商系统全链路测试

### 4.6.1 测试场景设计

**完整的电商用户旅程：**
```
用户注册 → 邮箱验证 → 用户登录 → 商品浏览 → 搜索商品 → 
加入购物车 → 结算订单 → 选择支付方式 → 支付流程 → 订单确认 → 订单查询
```

### 4.6.2 脚本架构

```
测试计划：电商全链路性能测试
├── 配置元素
│   ├── HTTP请求默认值
│   ├── HTTP信息头管理器
│   ├── CSV数据文件设置
│   └── JDBC连接配置
├── setUp线程组：测试数据准备
├── 线程组：主要测试流程
│   ├── 事务控制器：用户注册流程
│   ├── 事务控制器：登录验证流程
│   ├── 随机控制器：浏览行为
│   ├── 如果控制器：购买决策
│   ├── 事务控制器：购物流程
│   └── 事务控制器：支付流程
├── tearDown线程组：测试数据清理
└── 监听器组
```

### 4.6.3 关键技术实现

**数据准备（setUp线程组）：**
```properties
名称：准备测试数据
JDBC请求：清理测试数据
JDBC请求：插入基础数据
```

**用户注册流程：**
```properties
HTTP请求：用户注册
JSON提取器：提取用户ID
HTTP请求：发送验证邮件
定时器：等待邮件验证
HTTP请求：验证邮箱
```

**支付流程事务：**
```properties
事务控制器：支付流程
├── HTTP请求：生成支付订单
├── HTTP请求：调用支付网关
├── 如果控制器：支付成功
│   └── HTTP请求：确认订单
└── 如果控制器：支付失败
    └── HTTP请求：取消订单
```

## 4.7 本章小结

### 学习要点回顾
- ✅ 掌握了复杂业务逻辑测试的设计方法
- ✅ 学会了数据库性能测试的实施技巧
- ✅ 了解了FTP文件传输测试的配置
- ✅ 掌握了Web服务测试的多种协议支持
- ✅ 学习了自定义协议测试的实现方式
- ✅ 通过电商全链路测试示例巩固了综合应用能力

### 高级场景关键技能

**业务逻辑建模：**
- 使用逻辑控制器模拟真实用户行为
- 实现条件分支和循环逻辑
- 处理请求间的数据依赖关系

**多协议测试：**
- 数据库JDBC测试
- FTP文件传输测试
- SOAP/REST Web服务测试
- 自定义TCP协议测试

**全链路测试：**
- 设计完整的用户旅程
- 实现测试数据准备和清理
- 监控端到端性能指标

### 实践练习

**练习1：数据库性能测试**
1. 配置JDBC连接测试数据库
2. 设计查询和写入性能测试场景
3. 分析数据库性能瓶颈

**练习2：Web服务综合测试**
1. 实现REST API的完整CRUD操作测试
2. 测试不同认证方式的API
3. 设计API链式调用测试

**练习3：自定义协议测试**
1. 使用TCP采样器测试自定义协议
2. 实现简单的协议编码解码
3. 测试协议处理性能

### 下一章预告

在下一章中，我们将深入学习JMeter性能测试与监控，包括：
- 性能测试指标与分析方法
- 实时监控与结果分析
- 性能瓶颈定位技巧
- 性能测试报告生成

---

**继续学习：** [第5章 - JMeter性能测试与监控](./5-JMeter性能测试与监控.md)