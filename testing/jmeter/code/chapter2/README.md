# 第2章代码示例

## 核心组件实战脚本

### 1. 完整的API测试脚本

**api_test_complete.jmx** - 完整的用户管理系统API测试

```xml
<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.3">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="用户管理系统API测试" enabled="true">
      <stringProp name="TestPlan.comments">完整的用户登录、查询、更新、登出流程测试</stringProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.tearDown_on_shutdown">true</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
      <elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
        <collectionProp name="Arguments.arguments">
          <elementProp name="BASE_URL" elementType="Argument">
            <stringProp name="Argument.name">BASE_URL</stringProp>
            <stringProp name="Argument.value">http://api.example.com</stringProp>
            <stringProp name="Argument.metadata">=</stringProp>
          </elementProp>
          <elementProp name="API_VERSION" elementType="Argument">
            <stringProp name="Argument.name">API_VERSION</stringProp>
            <stringProp name="Argument.value">v1</stringProp>
            <stringProp name="Argument.metadata">=</stringProp>
          </elementProp>
        </collectionProp>
      </elementProp>
      <stringProp name="TestPlan.user_define_classpath"></stringProp>
    </TestPlan>
    <hashTree>
      <!-- HTTP请求默认值 -->
      <ConfigTestElement guiclass="HttpDefaultsGui" testclass="ConfigTestElement" testname="HTTP请求默认值" enabled="true">
        <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
          <collectionProp name="Arguments.arguments"/>
        </elementProp>
        <stringProp name="HTTPSampler.domain">api.example.com</stringProp>
        <stringProp name="HTTPSampler.port">8080</stringProp>
        <stringProp name="HTTPSampler.protocol">http</stringProp>
        <stringProp name="HTTPSampler.contentEncoding">UTF-8</stringProp>
        <stringProp name="HTTPSampler.path">/api/${API_VERSION}</stringProp>
        <stringProp name="HTTPSampler.concurrentPool">6</stringProp>
        <stringProp name="HTTPSampler.connect_timeout"></stringProp>
        <stringProp name="HTTPSampler.response_timeout"></stringProp>
      </ConfigTestElement>
      <hashTree/>
      
      <!-- HTTP信息头管理器 -->
      <HeaderManager guiclass="HeaderPanel" testclass="HeaderManager" testname="HTTP信息头管理器" enabled="true">
        <collectionProp name="HeaderManager.headers">
          <elementProp name="" elementType="Header">
            <stringProp name="Header.name">Content-Type</stringProp>
            <stringProp name="Header.value">application/json</stringProp>
          </elementProp>
          <elementProp name="" elementType="Header">
            <stringProp name="Header.name">Accept</stringProp>
            <stringProp name="Header.value">application/json</stringProp>
          </elementProp>
          <elementProp name="" elementType="Header">
            <stringProp name="Header.name">User-Agent</stringProp>
            <stringProp name="Header.value">JMeter-Performance-Test/1.0</stringProp>
          </elementProp>
        </collectionProp>
      </HeaderManager>
      <hashTree/>
      
      <!-- CSV数据文件设置 -->
      <CSVDataSet guiclass="TestBeanGUI" testclass="CSVDataSet" testname="CSV数据文件设置" enabled="true">
        <stringProp name="delimiter">,</stringProp>
        <stringProp name="fileEncoding">UTF-8</stringProp>
        <stringProp name="filename">./data/users.csv</stringProp>
        <boolProp name="ignoreFirstLine">true</boolProp>
        <boolProp name="quotedData">false</boolProp>
        <boolProp name="recycle">true</boolProp>
        <stringProp name="shareMode">shareMode.all</stringProp>
        <boolProp name="stopThread">false</boolProp>
        <stringProp name="variableNames">username,password,email</stringProp>
      </CSVDataSet>
      <hashTree/>
      
      <!-- 主要测试线程组 -->
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="并发用户测试" enabled="true">
        <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="循环控制器" enabled="true">
          <boolProp name="LoopController.continue_forever">false</boolProp>
          <stringProp name="LoopController.loops">3</stringProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">5</stringProp>
        <stringProp name="ThreadGroup.ramp_time">10</stringProp>
        <boolProp name="ThreadGroup.scheduler">false</boolProp>
        <stringProp name="ThreadGroup.duration"></stringProp>
        <stringProp name="ThreadGroup.delay"></stringProp>
      </ThreadGroup>
      <hashTree>
        
        <!-- 用户登录流程 -->
        <TransactionController guiclass="TransactionControllerGui" testclass="TransactionController" testname="用户登录流程" enabled="true">
          <boolProp name="TransactionController.includeTimers">false</boolProp>
          <boolProp name="TransactionController.parent">true</boolProp>
        </TransactionController>
        <hashTree>
          
          <!-- 登录请求 -->
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="POST_用户登录" enabled="true">
            <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
              <collectionProp name="Arguments.arguments">
                <elementProp name="" elementType="HTTPArgument">
                  <boolProp name="HTTPArgument.always_encode">false</boolProp>
                  <stringProp name="Argument.value">{"username": "${username}", "password": "${password}"}</stringProp>
                  <stringProp name="Argument.metadata">=</stringProp>
                  <boolProp name="HTTPArgument.use_equals">true</boolProp>
                  <stringProp name="Argument.name"></stringProp>
                </elementProp>
              </collectionProp>
            </elementProp>
            <stringProp name="HTTPSampler.domain"></stringProp>
            <stringProp name="HTTPSampler.port"></stringProp>
            <stringProp name="HTTPSampler.protocol"></stringProp>
            <stringProp name="HTTPSampler.contentEncoding"></stringProp>
            <stringProp name="HTTPSampler.path">/auth/login</stringProp>
            <stringProp name="HTTPSampler.method">POST</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
            <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
            <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
            <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
            <stringProp name="HTTPSampler.embedded_url_re"></stringProp>
            <stringProp name="HTTPSampler.connect_timeout"></stringProp>
            <stringProp name="HTTPSampler.response_timeout"></stringProp>
          </HTTPSamplerProxy>
          <hashTree>
            
            <!-- JSON提取器 - 提取token -->
            <JSONPostProcessor guiclass="JSONPostProcessorGui" testclass="JSONPostProcessor" testname="JSON提取器_提取Token" enabled="true">
              <stringProp name="JSONPostProcessor.referenceNames">AUTH_TOKEN</stringProp>
              <stringProp name="JSONPostProcessor.jsonPathExprs">$.data.access_token</stringProp>
              <stringProp name="JSONPostProcessor.match_numbers">0</stringProp>
              <stringProp name="JSONPostProcessor.defaultValues">NOT_FOUND</stringProp>
              <stringProp name="JSONPostProcessor.compute_concat">false</stringProp>
            </JSONPostProcessor>
            <hashTree/>
            
            <!-- 响应断言 - 验证登录成功 -->
            <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="响应断言_验证登录成功" enabled="true">
              <collectionProp name="Asserion.test_strings">
                <stringProp name="49586">"success":true</stringProp>
              </collectionProp>
              <stringProp name="Assertion.custom_message"></stringProp>
              <stringProp name="Assertion.test_field">Response Data</stringProp>
              <boolProp name="Assertion.assume_success">false</boolProp>
              <intProp name="Assertion.test_type">16</intProp>
            </ResponseAssertion>
            <hashTree/>
          </hashTree>
          
          <!-- 添加认证头部 -->
          <HeaderManager guiclass="HeaderPanel" testclass="HeaderManager" testname="认证头部管理器" enabled="true">
            <collectionProp name="HeaderManager.headers">
              <elementProp name="" elementType="Header">
                <stringProp name="Header.name">Authorization</stringProp>
                <stringProp name="Header.value">Bearer ${AUTH_TOKEN}</stringProp>
              </elementProp>
            </collectionProp>
          </HeaderManager>
          <hashTree/>
        </hashTree>
        
        <!-- 查询用户信息 -->
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="GET_查询用户信息" enabled="true">
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
            <collectionProp name="Arguments.arguments"/>
          </elementProp>
          <stringProp name="HTTPSampler.domain"></stringProp>
          <stringProp name="HTTPSampler.port"></stringProp>
          <stringProp name="HTTPSampler.protocol"></stringProp>
          <stringProp name="HTTPSampler.contentEncoding"></stringProp>
          <stringProp name="HTTPSampler.path">/users/profile</stringProp>
          <stringProp name="HTTPSampler.method">GET</stringProp>
          <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
          <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
          <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
          <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          <stringProp name="HTTPSampler.embedded_url_re"></stringProp>
          <stringProp name="HTTPSampler.connect_timeout"></stringProp>
          <stringProp name="HTTPSampler.response_timeout"></stringProp>
        </HTTPSamplerProxy>
        <hashTree>
          
          <!-- 响应断言 - 验证用户信息 -->
          <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="响应断言_验证用户信息" enabled="true">
            <collectionProp name="Asserion.test_strings">
              <stringProp name="49586">"email":"${email}"</stringProp>
            </collectionProp>
            <stringProp name="Assertion.custom_message"></stringProp>
            <stringProp name="Assertion.test_field">Response Data</stringProp>
            <boolProp name="Assertion.assume_success">false</boolProp>
            <intProp name="Assertion.test_type">16</intProp>
          </ResponseAssertion>
          <hashTree/>
        </hashTree>
        
        <!-- 用户登出 -->
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="POST_用户登出" enabled="true">
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
            <collectionProp name="Arguments.arguments"/>
          </elementProp>
          <stringProp name="HTTPSampler.domain"></stringProp>
          <stringProp name="HTTPSampler.port"></stringProp>
          <stringProp name="HTTPSampler.protocol"></stringProp>
          <stringProp name="HTTPSampler.contentEncoding"></stringProp>
          <stringProp name="HTTPSampler.path">/auth/logout</stringProp>
          <stringProp name="HTTPSampler.method">POST</stringProp>
          <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
          <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
          <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
          <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          <stringProp name="HTTPSampler.embedded_url_re"></stringProp>
          <stringProp name="HTTPSampler.connect_timeout"></stringProp>
          <stringProp name="HTTPSampler.response_timeout"></stringProp>
        </HTTPSamplerProxy>
        <hashTree/>
        
      </hashTree>
      
      <!-- 监听器 -->
      <ResultCollector guiclass="ViewResultsFullVisualizer" testclass="ResultCollector" testname="查看结果树" enabled="true">
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
      
      <ResultCollector guiclass="SummaryReport" testclass="ResultCollector" testname="汇总报告" enabled="true">
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

### 2. 测试数据文件

**data/users.csv**
```csv
username,password,email
user1,password123,user1@example.com
user2,password456,user2@example.com
user3,password789,user3@example.com
user4,password012,user4@example.com
user5,password345,user5@example.com
```

### 3. 逻辑控制器示例

**logic_controllers.jmx** - 各种逻辑控制器的使用示例

```xml
<!-- 循环控制器示例 -->
<LoopController guiclass="LoopControlPanel" testclass="LoopController" testname="循环控制器" enabled="true">
  <boolProp name="LoopController.continue_forever">false</boolProp>
  <stringProp name="LoopController.loops">5</stringProp>
</LoopController>

<!-- If控制器示例 -->
<IfController guiclass="IfControllerPanel" testclass="IfController" testname="If控制器" enabled="true">
  <stringProp name="IfController.condition">${__jexl3("${AUTH_TOKEN}" != "NOT_FOUND")}</stringProp>
  <boolProp name="IfController.evaluateAll">false</boolProp>
  <boolProp name="IfController.useExpression">true</boolProp>
</IfController>

<!-- 事务控制器示例 -->
<TransactionController guiclass="TransactionControllerGui" testclass="TransactionController" testname="用户登录事务" enabled="true">
  <boolProp name="TransactionController.includeTimers">true</boolProp>
  <boolProp name="TransactionController.parent">true</boolProp>
</TransactionController>
```

### 4. 断言和后置处理器示例

**assertions_processors.jmx** - 断言和后置处理器的使用示例

```xml
<!-- 响应断言示例 -->
<ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="响应代码断言" enabled="true">
  <collectionProp name="Asserion.test_strings">
    <stringProp name="49586">200</stringProp>
  </collectionProp>
  <stringProp name="Assertion.custom_message">响应代码应该是200</stringProp>
  <stringProp name="Assertion.test_field">Response Code</stringProp>
  <boolProp name="Assertion.assume_success">false</boolProp>
  <intProp name="Assertion.test_type">8</intProp>
</ResponseAssertion>

<!-- JSON提取器示例 -->
<JSONPostProcessor guiclass="JSONPostProcessorGui" testclass="JSONPostProcessor" testname="JSON提取器" enabled="true">
  <stringProp name="JSONPostProcessor.referenceNames">user_id</stringProp>
  <stringProp name="JSONPostProcessor.jsonPathExprs">$.data.user.id</stringProp>
  <stringProp name="JSONPostProcessor.match_numbers">0</stringProp>
  <stringProp name="JSONPostProcessor.defaultValues">0</stringProp>
</JSONPostProcessor>

<!-- 正则表达式提取器示例 -->
<RegexExtractor guiclass="RegexExtractorGui" testclass="RegexExtractor" testname="正则表达式提取器" enabled="true">
  <stringProp name="RegexExtractor.useHeaders">false</stringProp>
  <stringProp name="RegexExtractor.refname">session_id</stringProp>
  <stringProp name="RegexExtractor.regex">sessionId=([a-zA-Z0-9]+)</stringProp>
  <stringProp name="RegexExtractor.template">$1$</stringProp>
  <stringProp name="RegexExtractor.default">NO_SESSION</stringProp>
  <stringProp name="RegexExtractor.match_number">1</stringProp>
</RegexExtractor>
```

## 运行说明

### 1. 准备测试数据
```bash
# 创建数据目录
mkdir -p data

# 创建测试数据文件
echo 'username,password,email
user1,password123,user1@example.com
user2,password456,user2@example.com
user3,password789,user3@example.com
user4,password012,user4@example.com
user5,password345,user5@example.com' > data/users.csv
```

### 2. 执行测试
```bash
# 使用GUI模式打开测试脚本
jmeter -t api_test_complete.jmx

# 使用非GUI模式执行测试
jmeter -n -t api_test_complete.jmx -l results.jtl -e -o reports/
```

### 3. 查看结果分析
- 在JMeter GUI中查看各个监听器的结果
- 分析事务控制器的性能数据
- 验证断言和后置处理器的效果

## 核心概念验证

### 1. 组件执行顺序验证
通过查看"查看结果树"，观察组件的执行顺序：
1. 配置元素（HTTP请求默认值、信息头管理器）
2. 前置处理器
3. 定时器
4. 采样器
5. 后置处理器
6. 断言
7. 监听器

### 2. 数据流验证
验证数据在不同组件间的传递：
- CSV数据 → 登录请求
- 登录响应 → JSON提取器 → AUTH_TOKEN
- AUTH_TOKEN → 认证头部管理器 → 后续请求

### 3. 逻辑控制验证
验证逻辑控制器的效果：
- 循环控制器的重复执行
- If控制器的条件分支
- 事务控制器的整体性能测量

## 练习建议

### 练习1：组件配置
1. 修改HTTP请求默认值的配置参数
2. 添加新的HTTP信息头
3. 修改CSV数据文件设置

### 练习2：逻辑控制
1. 修改循环控制器的循环次数
2. 添加新的If控制器条件
3. 创建嵌套的逻辑控制器

### 练习3：结果验证
1. 添加更多的响应断言
2. 使用不同的JSON路径表达式
3. 配置正则表达式提取器

## 下一步

完成本章练习后，可以继续学习第3章：JMeter脚本编写与HTTP测试，学习更高级的脚本编写技巧和HTTP测试配置。