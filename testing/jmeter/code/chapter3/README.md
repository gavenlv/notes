# 第3章代码示例 - JMeter脚本编写与HTTP测试

## 高级HTTP测试脚本

### 1. 复杂API测试脚本

**advanced_api_test.jmx** - 包含复杂参数化、动态数据和认证的API测试

```xml
<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.3">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="高级API测试" enabled="true">
      <stringProp name="TestPlan.comments">包含参数化、动态数据、认证和复杂断言的完整API测试</stringProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.tearDown_on_shutdown">true</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
      <elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
        <collectionProp name="Arguments.arguments">
          <elementProp name="BASE_URL" elementType="Argument">
            <stringProp name="Argument.name">BASE_URL</stringProp>
            <stringProp name="Argument.value">https://jsonplaceholder.typicode.com</stringProp>
            <stringProp name="Argument.metadata">=</stringProp>
          </elementProp>
          <elementProp name="TIMEOUT" elementType="Argument">
            <stringProp name="Argument.name">TIMEOUT</stringProp>
            <stringProp name="Argument.value">5000</stringProp>
            <stringProp name="Argument.metadata">=</stringProp>
          </elementProp>
        </collectionProp>
      </elementProp>
      <stringProp name="TestPlan.user_define_classpath"></stringProp>
    </TestPlan>
    <hashTree>
      
      <!-- HTTP Cookie管理器 -->
      <CookieManager guiclass="CookiePanel" testclass="CookieManager" testname="HTTP Cookie管理器" enabled="true">
        <collectionProp name="CookieManager.cookies"/>
        <boolProp name="CookieManager.clearEachIteration">false</boolProp>
        <boolProp name="CookieManager.controlledByThread">false</boolProp>
      </CookieManager>
      <hashTree/>
      
      <!-- 用户定义的变量 -->
      <Arguments guiclass="ArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
        <collectionProp name="Arguments.arguments">
          <elementProp name="api_key" elementType="Argument">
            <stringProp name="Argument.name">api_key</stringProp>
            <stringProp name="Argument.value">test_api_key_12345</stringProp>
            <stringProp name="Argument.metadata">=</stringProp>
          </elementProp>
          <elementProp name="content_type" elementType="Argument">
            <stringProp name="Argument.name">content_type</stringProp>
            <stringProp name="Argument.value">application/json</stringProp>
            <stringProp name="Argument.metadata">=</stringProp>
          </elementProp>
        </collectionProp>
      </Arguments>
      <hashTree/>
      
      <!-- 主要测试线程组 -->
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="API测试线程组" enabled="true">
        <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="循环控制器" enabled="true">
          <boolProp name="LoopController.continue_forever">false</boolProp>
          <stringProp name="LoopController.loops">2</stringProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">3</stringProp>
        <stringProp name="ThreadGroup.ramp_time">5</stringProp>
        <boolProp name="ThreadGroup.scheduler">false</boolProp>
        <stringProp name="ThreadGroup.duration"></stringProp>
        <stringProp name="ThreadGroup.delay"></stringProp>
      </ThreadGroup>
      <hashTree>
        
        <!-- 前置处理器 - 生成动态数据 -->
        <JSR223PreProcessor guiclass="TestBeanGUI" testclass="JSR223PreProcessor" testname="JSR223前置处理器_生成动态数据" enabled="true">
          <stringProp name="cacheKey">false</stringProp>
          <stringProp name="filename"></stringProp>
          <stringProp name="parameters"></stringProp>
          <stringProp name="script">// 生成动态测试数据
import java.util.UUID;
import java.text.SimpleDateFormat;
import java.util.Date;

// 生成随机用户名
String randomUser = "testuser_" + UUID.randomUUID().toString().substring(0, 8);
vars.put("dynamic_username", randomUser);

// 生成随机邮箱
String randomEmail = randomUser + "@test.com";
vars.put("dynamic_email", randomEmail);

// 生成时间戳
SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
String timestamp = sdf.format(new Date());
vars.put("timestamp", timestamp);

// 生成随机ID
int randomId = (int)(Math.random() * 1000) + 1;
vars.put("random_id", String.valueOf(randomId));

log.info("生成动态数据: username=" + randomUser + ", email=" + randomEmail);</stringProp>
          <stringProp name="scriptLanguage">groovy</stringProp>
        </JSR223PreProcessor>
        <hashTree/>
        
        <!-- 用户创建流程 -->
        <TransactionController guiclass="TransactionControllerGui" testclass="TransactionController" testname="用户创建流程" enabled="true">
          <boolProp name="TransactionController.includeTimers">true</boolProp>
          <boolProp name="TransactionController.parent">true</boolProp>
        </TransactionController>
        <hashTree>
          
          <!-- POST创建用户 -->
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="POST_创建用户" enabled="true">
            <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
              <collectionProp name="Arguments.arguments">
                <elementProp name="" elementType="HTTPArgument">
                  <boolProp name="HTTPArgument.always_encode">false</boolProp>
                  <stringProp name="Argument.value">{
  "name": "${dynamic_username}",
  "username": "${dynamic_username}",
  "email": "${dynamic_email}",
  "address": {
    "street": "测试街道",
    "suite": "Apt. 123",
    "city": "测试城市",
    "zipcode": "12345",
    "geo": {
      "lat": "-37.3159",
      "lng": "81.1496"
    }
  },
  "phone": "1-770-736-8031 x56442",
  "website": "hildegard.org",
  "company": {
    "name": "测试公司",
    "catchPhrase": "多层级客户服务器软件",
    "bs": "harness实时市场"
  }
}</stringProp>
                  <stringProp name="Argument.metadata">=</stringProp>
                  <boolProp name="HTTPArgument.use_equals">true</boolProp>
                  <stringProp name="Argument.name"></stringProp>
                </elementProp>
              </collectionProp>
            </elementProp>
            <stringProp name="HTTPSampler.domain"></stringProp>
            <stringProp name="HTTPSampler.port"></stringProp>
            <stringProp name="HTTPSampler.protocol"></stringProp>
            <stringProp name="HTTPSampler.contentEncoding">UTF-8</stringProp>
            <stringProp name="HTTPSampler.path">/users</stringProp>
            <stringProp name="HTTPSampler.method">POST</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
            <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
            <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
            <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
            <stringProp name="HTTPSampler.embedded_url_re"></stringProp>
            <stringProp name="HTTPSampler.connect_timeout">${TIMEOUT}</stringProp>
            <stringProp name="HTTPSampler.response_timeout">${TIMEOUT}</stringProp>
          </HTTPSamplerProxy>
          <hashTree>
            
            <!-- JSON提取器 - 提取用户ID -->
            <JSONPostProcessor guiclass="JSONPostProcessorGui" testclass="JSONPostProcessor" testname="JSON提取器_提取用户ID" enabled="true">
              <stringProp name="JSONPostProcessor.referenceNames">created_user_id</stringProp>
              <stringProp name="JSONPostProcessor.jsonPathExprs">$.id</stringProp>
              <stringProp name="JSONPostProcessor.match_numbers">0</stringProp>
              <stringProp name="JSONPostProcessor.defaultValues">0</stringProp>
            </JSONPostProcessor>
            <hashTree/>
            
            <!-- 响应断言 - 验证创建成功 -->
            <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="响应断言_验证创建成功" enabled="true">
              <collectionProp name="Asserion.test_strings">
                <stringProp name="49586">201</stringProp>
              </collectionProp>
              <stringProp name="Assertion.custom_message">用户创建失败，响应代码应该是201</stringProp>
              <stringProp name="Assertion.test_field">Response Code</stringProp>
              <boolProp name="Assertion.assume_success">false</boolProp>
              <intProp name="Assertion.test_type">8</intProp>
            </ResponseAssertion>
            <hashTree/>
            
            <!-- 持续时间断言 -->
            <DurationAssertion guiclass="DurationAssertionGui" testclass="DurationAssertion" testname="持续时间断言" enabled="true">
              <stringProp name="DurationAssertion.duration">3000</stringProp>
            </DurationAssertion>
            <hashTree/>
            
          </hashTree>
          
          <!-- 查询创建的用户 -->
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="GET_查询用户" enabled="true">
            <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
              <collectionProp name="Arguments.arguments"/>
            </elementProp>
            <stringProp name="HTTPSampler.domain"></stringProp>
            <stringProp name="HTTPSampler.port"></stringProp>
            <stringProp name="HTTPSampler.protocol"></stringProp>
            <stringProp name="HTTPSampler.contentEncoding"></stringProp>
            <stringProp name="HTTPSampler.path">/users/${created_user_id}</stringProp>
            <stringProp name="HTTPSampler.method">GET</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
            <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
            <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
            <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
            <stringProp name="HTTPSampler.embedded_url_re"></stringProp>
            <stringProp name="HTTPSampler.connect_timeout">${TIMEOUT}</stringProp>
            <stringProp name="HTTPSampler.response_timeout">${TIMEOUT}</stringProp>
          </HTTPSamplerProxy>
          <hashTree>
            
            <!-- 大小断言 -->
            <SizeAssertion guiclass="SizeAssertionGui" testclass="SizeAssertion" testname="大小断言" enabled="true">
              <stringProp name="SizeAssertion.size">100</stringProp>
              <stringProp name="SizeAssertion.operator">大于</stringProp>
            </SizeAssertion>
            <hashTree/>
            
          </hashTree>
          
        </hashTree>
        
        <!-- 查询帖子列表 -->
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="GET_查询帖子列表" enabled="true">
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
            <collectionProp name="Arguments.arguments"/>
          </elementProp>
          <stringProp name="HTTPSampler.domain"></stringProp>
          <stringProp name="HTTPSampler.port"></stringProp>
          <stringProp name="HTTPSampler.protocol"></stringProp>
          <stringProp name="HTTPSampler.contentEncoding"></stringProp>
          <stringProp name="HTTPSampler.path">/posts</stringProp>
          <stringProp name="HTTPSampler.method">GET</stringProp>
          <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
          <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
          <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
          <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          <stringProp name="HTTPSampler.embedded_url_re"></stringProp>
          <stringProp name="HTTPSampler.connect_timeout">${TIMEOUT}</stringProp>
          <stringProp name="HTTPSampler.response_timeout">${TIMEOUT}</stringProp>
        </HTTPSamplerProxy>
        <hashTree>
          
          <!-- XPath断言 -->
          <XPathAssertion guiclass="XPathAssertionGui" testclass="XPathAssertion" testname="XPath断言" enabled="true">
            <stringProp name="XPath.xpath">//post</stringProp>
            <boolProp name="XPath.negate">false</boolProp>
            <boolProp name="XPath.tolerant">true</boolProp>
          </XPathAssertion>
          <hashTree/>
          
        </hashTree>
        
        <!-- 创建新帖子 -->
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="POST_创建帖子" enabled="true">
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
            <collectionProp name="Arguments.arguments">
              <elementProp name="" elementType="HTTPArgument">
                <boolProp name="HTTPArgument.always_encode">false</boolProp>
                <stringProp name="Argument.value">{
  "title": "测试帖子标题 ${timestamp}",
  "body": "这是测试帖子内容，发布于${timestamp}。

这是一个多行内容的测试，用于验证JMeter的复杂JSON处理能力。",
  "userId": ${random_id}
}</stringProp>
                <stringProp name="Argument.metadata">=</stringProp>
                <boolProp name="HTTPArgument.use_equals">true</boolProp>
                <stringProp name="Argument.name"></stringProp>
              </elementProp>
            </collectionProp>
          </elementProp>
          <stringProp name="HTTPSampler.domain"></stringProp>
          <stringProp name="HTTPSampler.port"></stringProp>
          <stringProp name="HTTPSampler.protocol"></stringProp>
          <stringProp name="HTTPSampler.contentEncoding">UTF-8</stringProp>
          <stringProp name="HTTPSampler.path">/posts</stringProp>
          <stringProp name="HTTPSampler.method">POST</stringProp>
          <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
          <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
          <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
          <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          <stringProp name="HTTPSampler.embedded_url_re"></stringProp>
          <stringProp name="HTTPSampler.connect_timeout">${TIMEOUT}</stringProp>
          <stringProp name="HTTPSampler.response_timeout">${TIMEOUT}</stringProp>
        </HTTPSamplerProxy>
        <hashTree>
          
          <!-- BeanShell断言 -->
          <BeanShellAssertion guiclass="BeanShellAssertionGui" testclass="BeanShellAssertion" testname="BeanShell断言" enabled="true">
            <stringProp name="BeanShellAssertion.query">// 验证响应包含预期的字段
String response = new String(ResponseData);
if (response.contains("\"id\"") && response.contains("\"title\"") && response.contains("\"body\"")) {
    Failure = false;
    FailureMessage = "";
} else {
    Failure = true;
    FailureMessage = "响应缺少必要字段";
}</stringProp>
            <stringProp name="BeanShellAssertion.filename"></stringProp>
            <stringProp name="BeanShellAssertion.parameters"></stringProp>
            <boolProp name="BeanShellAssertion.resetInterpreter">false</boolProp>
          </BeanShellAssertion>
          <hashTree/>
          
        </hashTree>
        
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

### 2. 文件上传测试脚本

**file_upload_test.jmx** - 多部分文件上传测试

```xml
<!-- 文件上传测试 -->
<HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="文件上传测试" enabled="true">
  <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
    <collectionProp name="Arguments.arguments">
      <elementProp name="file" elementType="HTTPArgument">
        <boolProp name="HTTPArgument.always_encode">false</boolProp>
        <stringProp name="Argument.value"></stringProp>
        <stringProp name="Argument.metadata">=</stringProp>
        <boolProp name="HTTPArgument.use_equals">true</boolProp>
        <stringProp name="Argument.name">file</stringProp>
        <boolProp name="HTTPArgument.image">false</boolProp>
        <stringProp name="Argument.mimetype">image/jpeg</stringProp>
      </elementProp>
      <elementProp name="description" elementType="HTTPArgument">
        <boolProp name="HTTPArgument.always_encode">false</boolProp>
        <stringProp name="Argument.value">测试文件上传</stringProp>
        <stringProp name="Argument.metadata">=</stringProp>
        <boolProp name="HTTPArgument.use_equals">true</boolProp>
        <stringProp name="Argument.name">description</stringProp>
      </elementProp>
    </collectionProp>
  </elementProp>
  <stringProp name="HTTPSampler.domain">file-upload.example.com</stringProp>
  <stringProp name="HTTPSampler.port">443</stringProp>
  <stringProp name="HTTPSampler.protocol">https</stringProp>
  <stringProp name="HTTPSampler.contentEncoding"></stringProp>
  <stringProp name="HTTPSampler.path">/upload</stringProp>
  <stringProp name="HTTPSampler.method">POST</stringProp>
  <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
  <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
  <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
  <boolProp name="HTTPSampler.DO_MULTIPART_POST">true</boolProp>
  <stringProp name="HTTPSampler.embedded_url_re"></stringProp>
  <stringProp name="HTTPSampler.connect_timeout"></stringProp>
  <stringProp name="HTTPSampler.response_timeout"></stringProp>
</HTTPSamplerProxy>
```

### 3. 高级参数化脚本

**parameterization_advanced.jmx** - 包含多种参数化技术的测试

```xml
<!-- 计数器配置 -->
<CounterConfig guiclass="CounterConfigGui" testclass="CounterConfig" testname="计数器配置" enabled="true">
  <stringProp name="CounterConfig.start">1</stringProp>
  <stringProp name="CounterConfig.incr">1</stringProp>
  <stringProp name="CounterConfig.end">10</stringProp>
  <stringProp name="CounterConfig.name">counter</stringProp>
  <stringProp name="CounterConfig.format">USER_0000</stringProp>
  <boolProp name="CounterConfig.per_user">false</boolProp>
</CounterConfig>

<!-- 随机变量配置 -->
<RandomVariableConfig guiclass="TestBeanGUI" testclass="RandomVariableConfig" testname="随机变量配置" enabled="true">
  <stringProp name="maximumValue">1000</stringProp>
  <stringProp name="minimumValue">1</stringProp>
  <stringProp name="outputFormat"></stringProp>
  <stringProp name="randomSeed"></stringProp>
  <stringProp name="variableName">random_value</stringProp>
</RandomVariableConfig>
```

## 运行说明

### 1. 准备测试环境
```bash
# 创建测试目录结构
mkdir -p test_files

# 创建测试文件
echo "这是一个测试文件内容" > test_files/test.txt
echo "{\"test\": \"data\"}" > test_files/test.json
```

### 2. 执行测试
```bash
# 使用GUI模式打开测试脚本
jmeter -t advanced_api_test.jmx

# 使用非GUI模式执行测试
jmeter -n -t advanced_api_test.jmx -l results.jtl -e -o reports/
```

### 3. 验证高级功能
- 验证动态数据生成是否正确
- 检查各种断言的有效性
- 分析事务控制器的性能数据
- 验证文件上传功能

## 高级功能验证

### 1. 动态数据验证
通过查看"查看结果树"，验证前置处理器生成的动态数据：
- 随机用户名是否正确生成
- 时间戳格式是否正确
- 随机ID是否在预期范围内

### 2. 断言功能验证
验证各种断言的效果：
- 响应代码断言
- 持续时间断言
- 大小断言
- XPath断言
- BeanShell断言

### 3. 文件上传验证
验证多部分文件上传功能：
- 文件内容是否正确传输
- 响应是否正确处理
- 错误处理机制

## 练习建议

### 练习1：动态数据生成
1. 修改JSR223前置处理器，生成不同类型的动态数据
2. 添加新的随机变量生成器
3. 创建复杂的数据组合

### 练习2：断言配置
1. 添加新的响应断言规则
2. 配置更复杂的XPath断言
3. 编写自定义的BeanShell断言脚本

### 练习3：文件处理
1. 测试不同文件类型的上传
2. 验证文件大小限制
3. 测试多文件同时上传

## 下一步

完成本章练习后，可以继续学习第4章：JMeter高级测试场景设计，学习更复杂的测试场景和性能优化技巧。