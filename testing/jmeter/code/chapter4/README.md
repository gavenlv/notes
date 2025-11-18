# 第4章代码示例 - JMeter高级测试场景设计

## 高级测试场景脚本

### 1. 数据库性能测试脚本

**database_performance_test.jmx** - 包含数据库连接池、SQL查询性能测试的完整场景

```xml
<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.3">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="数据库性能测试" enabled="true">
      <stringProp name="TestPlan.comments">数据库连接池性能测试，包含查询、插入、更新、删除操作</stringProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.tearDown_on_shutdown">true</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
      <elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
        <collectionProp name="Arguments.arguments">
          <elementProp name="DB_URL" elementType="Argument">
            <stringProp name="Argument.name">DB_URL</stringProp>
            <stringProp name="Argument.value">jdbc:mysql://localhost:3306/testdb</stringProp>
            <stringProp name="Argument.metadata">=</stringProp>
          </elementProp>
          <elementProp name="DB_USER" elementType="Argument">
            <stringProp name="Argument.name">DB_USER</stringProp>
            <stringProp name="Argument.value">root</stringProp>
            <stringProp name="Argument.metadata">=</stringProp>
          </elementProp>
          <elementProp name="DB_PASSWORD" elementType="Argument">
            <stringProp name="Argument.name">DB_PASSWORD</stringProp>
            <stringProp name="Argument.value">password</stringProp>
            <stringProp name="Argument.metadata">=</stringProp>
          </elementProp>
        </collectionProp>
      </elementProp>
      <stringProp name="TestPlan.user_define_classpath">lib/mysql-connector-java-8.0.28.jar</stringProp>
    </TestPlan>
    <hashTree>
      
      <!-- JDBC连接配置 -->
      <JDBCDataSource guiclass="TestBeanGUI" testclass="JDBCDataSource" testname="JDBC连接池配置" enabled="true">
        <stringProp name="dataSource">jdbcDataSource</stringProp>
        <stringProp name="dbUrl">${DB_URL}</stringProp>
        <stringProp name="driver">com.mysql.cj.jdbc.Driver</stringProp>
        <stringProp name="password">${DB_PASSWORD}</stringProp>
        <stringProp name="poolMax">10</stringProp>
        <stringProp name="timeout">10000</stringProp>
        <stringProp name="trimInterval">60000</stringProp>
        <stringProp name="username">${DB_USER}</stringProp>
        <stringProp name="connectionAge">5000</stringProp>
        <stringProp name="checkQuery">Select 1</stringProp>
        <stringProp name="autocommit">true</stringProp>
        <stringProp name="keepAlive">true</stringProp>
        <stringProp name="transactionIsolation">DEFAULT</stringProp>
      </JDBCDataSource>
      <hashTree/>
      
      <!-- 主要测试线程组 -->
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="数据库并发测试" enabled="true">
        <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="循环控制器" enabled="true">
          <boolProp name="LoopController.continue_forever">false</boolProp>
          <stringProp name="LoopController.loops">5</stringProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">10</stringProp>
        <stringProp name="ThreadGroup.ramp_time">30</stringProp>
        <boolProp name="ThreadGroup.scheduler">true</boolProp>
        <stringProp name="ThreadGroup.duration">300</stringProp>
        <stringProp name="ThreadGroup.delay"></stringProp>
      </ThreadGroup>
      <hashTree>
        
        <!-- 查询性能测试 -->
        <TransactionController guiclass="TransactionControllerGui" testclass="TransactionController" testname="查询性能测试" enabled="true">
          <boolProp name="TransactionController.includeTimers">true</boolProp>
          <boolProp name="TransactionController.parent">true</boolProp>
        </TransactionController>
        <hashTree>
          
          <!-- 简单查询 -->
          <JDBCSampler guiclass="TestBeanGUI" testclass="JDBCSampler" testname="JDBC查询_简单查询" enabled="true">
            <stringProp name="dataSource">jdbcDataSource</stringProp>
            <stringProp name="query">SELECT * FROM users WHERE id = ?</stringProp>
            <stringProp name="queryArguments">${__Random(1,1000)}</stringProp>
            <stringProp name="queryArgumentsTypes">INTEGER</stringProp>
            <stringProp name="queryType">Prepared Select Statement</stringProp>
            <stringProp name="resultVariable">user_result</stringProp>
            <stringProp name="queryTimeout">30</stringProp>
            <stringProp name="resultSetHandler">Store as String</stringProp>
          </JDBCSampler>
          <hashTree>
            
            <!-- 响应断言 - 验证查询结果 -->
            <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="响应断言_验证查询结果" enabled="true">
              <collectionProp name="Asserion.test_strings">
                <stringProp name="49586">SUCCESS</stringProp>
              </collectionProp>
              <stringProp name="Assertion.custom_message">数据库查询失败</stringProp>
              <stringProp name="Assertion.test_field">Response Message</stringProp>
              <boolProp name="Assertion.assume_success">false</boolProp>
              <intProp name="Assertion.test_type">16</intProp>
            </ResponseAssertion>
            <hashTree/>
            
          </hashTree>
          
          <!-- 复杂查询 -->
          <JDBCSampler guiclass="TestBeanGUI" testclass="JDBCSampler" testname="JDBC查询_复杂查询" enabled="true">
            <stringProp name="dataSource">jdbcDataSource</stringProp>
            <stringProp name="query">SELECT u.name, u.email, p.title, p.content 
FROM users u 
JOIN posts p ON u.id = p.user_id 
WHERE u.status = 'active' 
AND p.created_at > DATE_SUB(NOW(), INTERVAL 7 DAY) 
ORDER BY p.created_at DESC 
LIMIT 10</stringProp>
            <stringProp name="queryArguments"></stringProp>
            <stringProp name="queryArgumentsTypes"></stringProp>
            <stringProp name="queryType">Select Statement</stringProp>
            <stringProp name="resultVariable">complex_result</stringProp>
            <stringProp name="queryTimeout">60</stringProp>
            <stringProp name="resultSetHandler">Store as String</stringProp>
          </JDBCSampler>
          <hashTree/>
          
        </hashTree>
        
        <!-- 插入性能测试 -->
        <TransactionController guiclass="TransactionControllerGui" testclass="TransactionController" testname="插入性能测试" enabled="true">
          <boolProp name="TransactionController.includeTimers">true</boolProp>
          <boolProp name="TransactionController.parent">true</boolProp>
        </TransactionController>
        <hashTree>
          
          <!-- 插入操作 -->
          <JDBCSampler guiclass="TestBeanGUI" testclass="JDBCSampler" testname="JDBC插入_用户数据" enabled="true">
            <stringProp name="dataSource">jdbcDataSource</stringProp>
            <stringProp name="query">INSERT INTO test_users (name, email, created_at) VALUES (?, ?, NOW())</stringProp>
            <stringProp name="queryArguments">test_user_${__threadNum},test${__threadNum}@example.com</stringProp>
            <stringProp name="queryArgumentsTypes">VARCHAR,VARCHAR</stringProp>
            <stringProp name="queryType">Prepared Update Statement</stringProp>
            <stringProp name="resultVariable">insert_result</stringProp>
            <stringProp name="queryTimeout">30</stringProp>
            <stringProp name="resultSetHandler">Store as String</stringProp>
          </JDBCSampler>
          <hashTree>
            
            <!-- 响应断言 - 验证插入结果 -->
            <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="响应断言_验证插入结果" enabled="true">
              <collectionProp name="Asserion.test_strings">
                <stringProp name="49586">1</stringProp>
              </collectionProp>
              <stringProp name="Assertion.custom_message">插入操作失败，影响行数不是1</stringProp>
              <stringProp name="Assertion.test_field">Response Data</stringProp>
              <boolProp name="Assertion.assume_success">false</boolProp>
              <intProp name="Assertion.test_type">16</intProp>
            </ResponseAssertion>
            <hashTree/>
            
          </hashTree>
          
        </hashTree>
        
        <!-- 更新性能测试 -->
        <TransactionController guiclass="TransactionControllerGui" testclass="TransactionController" testname="更新性能测试" enabled="true">
          <boolProp name="TransactionController.includeTimers">true</boolProp>
          <boolProp name="TransactionController.parent">true</boolProp>
        </TransactionController>
        <hashTree>
          
          <!-- 更新操作 -->
          <JDBCSampler guiclass="TestBeanGUI" testclass="JDBCSampler" testname="JDBC更新_用户状态" enabled="true">
            <stringProp name="dataSource">jdbcDataSource</stringProp>
            <stringProp name="query">UPDATE test_users SET status = 'updated', updated_at = NOW() WHERE id = ?</stringProp>
            <stringProp name="queryArguments">${__Random(1,100)}</stringProp>
            <stringProp name="queryArgumentsTypes">INTEGER</stringProp>
            <stringProp name="queryType">Prepared Update Statement</stringProp>
            <stringProp name="resultVariable">update_result</stringProp>
            <stringProp name="queryTimeout">30</stringProp>
            <stringProp name="resultSetHandler">Store as String</stringProp>
          </JDBCSampler>
          <hashTree/>
          
        </hashTree>
        
        <!-- 删除性能测试 -->
        <TransactionController guiclass="TransactionControllerGui" testclass="TransactionController" testname="删除性能测试" enabled="true">
          <boolProp name="TransactionController.includeTimers">true</boolProp>
          <boolProp name="TransactionController.parent">true</boolProp>
        </TransactionController>
        <hashTree>
          
          <!-- 删除操作 -->
          <JDBCSampler guiclass="TestBeanGUI" testclass="JDBCSampler" testname="JDBC删除_测试数据" enabled="true">
            <stringProp name="dataSource">jdbcDataSource</stringProp>
            <stringProp name="query">DELETE FROM test_users WHERE created_at < DATE_SUB(NOW(), INTERVAL 1 HOUR)</stringProp>
            <stringProp name="queryArguments"></stringProp>
            <stringProp name="queryArgumentsTypes"></stringProp>
            <stringProp name="queryType">Update Statement</stringProp>
            <stringProp name="resultVariable">delete_result</stringProp>
            <stringProp name="queryTimeout">30</stringProp>
            <stringProp name="resultSetHandler">Store as String</stringProp>
          </JDBCSampler>
          <hashTree/>
          
        </hashTree>
        
      </hashTree>
      
      <!-- 监听器 -->
      <ResultCollector guiclass="AggregateReport" testclass="ResultCollector" testname="聚合报告" enabled="true">
        <boolProp name="ResultCollector.error_logging">false</boolProp>
        <objProp>
          <name>saveConfig</name>
          <value class="SaveConfig">
            <time>true</time>
            <latency>true</latency>
            <timestamp>true</timestamp>
            <success>true</success>
            <label>true</label>
            <code>true</code>
            <message>true</message>
            <threadName>true</threadName>
            <dataType>true</dataType>
            <encoding>false</encoding>
            <assertions>true</assertions>
            <subresults>true</subresults>
            <responseData>false</responseData>
            <samplerData>false</samplerData>
            <xml>false</xml>
            <fieldNames>true</fieldNames>
            <responseHeaders>false</responseHeaders>
            <requestHeaders>false</requestHeaders>
            <responseDataOnError>false</responseDataOnError>
            <saveAssertionResultsFailureMessage>true</saveAssertionResultsFailureMessage>
            <assertionsResultsToSave>0</assertionsResultsToSave>
            <bytes>true</bytes>
            <sentBytes>true</sentBytes>
            <url>true</url>
            <threadCounts>true</threadCounts>
            <idleTime>true</idleTime>
            <connectTime>true</connectTime>
          </value>
        </objProp>
        <stringProp name="filename"></stringProp>
      </ResultCollector>
      <hashTree/>
      
      <ResultCollector guiclass="ResponseTimeGraph" testclass="ResultCollector" testname="响应时间图" enabled="true">
        <boolProp name="ResultCollector.error_logging">false</boolProp>
        <objProp>
          <name>saveConfig</name>
          <value class="SaveConfig">
            <time>true</time>
            <latency>true</latency>
            <timestamp>true</timestamp>
            <success>true</success>
            <label>true</label>
            <code>true</code>
            <message>true</message>
            <threadName>true</threadName>
            <dataType>true</dataType>
            <encoding>false</encoding>
            <assertions>true</assertions>
            <subresults>true</subresults>
            <responseData>false</responseData>
            <samplerData>false</samplerData>
            <xml>false</xml>
            <fieldNames>true</fieldNames>
            <responseHeaders>false</responseHeaders>
            <requestHeaders>false</requestHeaders>
            <responseDataOnError>false</responseDataOnError>
            <saveAssertionResultsFailureMessage>true</saveAssertionResultsFailureMessage>
            <assertionsResultsToSave>0</assertionsResultsToSave>
            <bytes>true</bytes>
            <sentBytes>true</sentBytes>
            <url>true</url>
            <threadCounts>true</threadCounts>
            <idleTime>true</idleTime>
            <connectTime>true</connectTime>
          </value>
        </objProp>
        <stringProp name="filename"></stringProp>
      </ResultCollector>
      <hashTree/>
      
    </hashTree>
  </hashTree>
</jmeterTestPlan>
```

### 2. 负载测试场景脚本

**load_test_scenario.jmx** - 模拟真实用户行为的负载测试场景

```xml
<!-- 模拟用户登录浏览场景 -->
<ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="模拟用户场景" enabled="true">
  <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
  <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="循环控制器" enabled="true">
    <boolProp name="LoopController.continue_forever">false</boolProp>
    <stringProp name="LoopController.loops">-1</stringProp>
  </elementProp>
  <stringProp name="ThreadGroup.num_threads">50</stringProp>
  <stringProp name="ThreadGroup.ramp_time">60</stringProp>
  <boolProp name="ThreadGroup.scheduler">true</boolProp>
  <stringProp name="ThreadGroup.duration">600</stringProp>
  <stringProp name="ThreadGroup.delay"></stringProp>
</ThreadGroup>

<!-- 随机定时器 -->
<GaussianRandomTimer guiclass="GaussianRandomTimerGui" testclass="GaussianRandomTimer" testname="高斯随机定时器" enabled="true">
  <stringProp name="RandomTimer.delay">3000</stringProp>
  <stringProp name="RandomTimer.range">1000</stringProp>
</GaussianRandomTimer>

<!-- 同步定时器 -->
<SynchronizingTimer guiclass="TestBeanGUI" testclass="SynchronizingTimer" testname="同步定时器" enabled="true">
  <stringProp name="groupSize">10</stringProp>
  <stringProp name="timeoutInMs">30000</stringProp>
</SynchronizingTimer>
```

### 3. 压力测试场景脚本

**stress_test_scenario.jmx** - 系统极限压力测试场景

```xml
<!-- 压力测试线程组 -->
<ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="压力测试" enabled="true">
  <stringProp name="ThreadGroup.on_sample_error">stopthread</stringProp>
  <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="循环控制器" enabled="true">
    <boolProp name="LoopController.continue_forever">true</boolProp>
    <stringProp name="LoopController.loops">-1</stringProp>
  </elementProp>
  <stringProp name="ThreadGroup.num_threads">100</stringProp>
  <stringProp name="ThreadGroup.ramp_time">10</stringProp>
  <boolProp name="ThreadGroup.scheduler">true</boolProp>
  <stringProp name="ThreadGroup.duration">900</stringProp>
  <stringProp name="ThreadGroup.delay"></stringProp>
</ThreadGroup>

<!-- 常数吞吐量定时器 -->
<ConstantThroughputTimer guiclass="TestBeanGUI" testclass="ConstantThroughputTimer" testname="常数吞吐量定时器" enabled="true">
  <stringProp name="calcMode">all active threads in current thread group</stringProp>
  <stringProp name="throughput">60</stringProp>
</ConstantThroughputTimer>
```

## 运行说明

### 1. 准备数据库环境
```bash
# 创建测试数据库和表
mysql -u root -p -e "
CREATE DATABASE IF NOT EXISTS testdb;
USE testdb;

CREATE TABLE IF NOT EXISTS users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100),
  email VARCHAR(100),
  status VARCHAR(20) DEFAULT 'active',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS posts (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  title VARCHAR(200),
  content TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS test_users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100),
  email VARCHAR(100),
  status VARCHAR(20) DEFAULT 'active',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NULL
);

-- 插入测试数据
INSERT INTO users (name, email) VALUES 
('张三', 'zhangsan@example.com'),
('李四', 'lisi@example.com'),
('王五', 'wangwu@example.com');

INSERT INTO posts (user_id, title, content) VALUES 
(1, '第一篇帖子', '这是张三的第一篇帖子'),
(2, '李四的分享', '这是李四的分享内容'),
(3, '王五的博客', '这是王五的博客文章');
"
```

### 2. 下载数据库驱动
```bash
# 下载MySQL JDBC驱动
wget https://repo1.maven.org/maven2/mysql/mysql-connector-java/8.0.28/mysql-connector-java-8.0.28.jar

# 将驱动放入JMeter的lib目录
cp mysql-connector-java-8.0.28.jar $JMETER_HOME/lib/
```

### 3. 执行测试
```bash
# 使用GUI模式打开测试脚本
jmeter -t database_performance_test.jmx

# 使用非GUI模式执行测试
jmeter -n -t database_performance_test.jmx -l results.jtl -e -o reports/
```

## 高级场景验证

### 1. 数据库连接池性能验证
- 验证连接池配置是否正确
- 监控连接池使用情况
- 分析连接池性能瓶颈

### 2. 负载测试场景验证
- 验证用户行为模拟的真实性
- 分析系统在不同负载下的表现
- 识别性能瓶颈和优化点

### 3. 压力测试场景验证
- 验证系统极限处理能力
- 分析系统崩溃点
- 识别系统容错能力

## 练习建议

### 练习1：数据库性能优化
1. 调整连接池参数，观察性能变化
2. 优化SQL查询语句
3. 测试不同数据库配置的性能差异

### 练习2：负载测试设计
1. 设计更复杂的用户行为场景
2. 调整负载分布和持续时间
3. 分析系统在不同负载模式下的表现

### 练习3：压力测试分析
1. 识别系统性能瓶颈
2. 分析系统崩溃的原因
3. 制定性能优化策略

## 下一步

完成本章练习后，可以继续学习第5章：JMeter性能测试与监控，学习性能监控和结果分析技巧。