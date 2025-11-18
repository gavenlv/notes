# 第1章代码示例

## 环境验证脚本

### 1. Java环境检查脚本

**check_java.bat** (Windows)
```batch
@echo off
echo 检查Java环境...
java -version
echo.
echo 检查Java安装路径...
java -XshowSettings:properties -version 2>&1 | findstr "java.home"
echo.
echo 检查JAVA_HOME环境变量...
echo %JAVA_HOME%
echo.
pause
```

**check_java.sh** (Linux/macOS)
```bash
#!/bin/bash
echo "检查Java环境..."
java -version
echo
echo "检查Java安装路径..."
java -XshowSettings:properties -version 2>&1 | grep "java.home"
echo
echo "检查JAVA_HOME环境变量..."
echo $JAVA_HOME
echo
```

### 2. JMeter安装验证脚本

**verify_jmeter.bat** (Windows)
```batch
@echo off
echo 验证JMeter安装...
cd /d %JMETER_HOME%
bin\jmeter.bat --version
echo.
echo 检查JMeter目录结构...
dir /b
echo.
pause
```

**verify_jmeter.sh** (Linux/macOS)
```bash
#!/bin/bash
echo "验证JMeter安装..."
cd $JMETER_HOME
bin/jmeter.sh --version
echo
echo "检查JMeter目录结构..."
ls -la
echo
```

### 3. 第一个HTTP测试脚本

**first_test.jmx**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.3">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="第一个JMeter测试" enabled="true">
      <stringProp name="TestPlan.comments">这是一个简单的HTTP测试示例</stringProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.tearDown_on_shutdown">true</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
      <elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
        <collectionProp name="Arguments.arguments"/>
      </elementProp>
      <stringProp name="TestPlan.user_define_classpath"></stringProp>
    </TestPlan>
    <hashTree>
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="线程组" enabled="true">
        <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="循环控制器" enabled="true">
          <boolProp name="LoopController.continue_forever">false</boolProp>
          <stringProp name="LoopController.loops">1</stringProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">1</stringProp>
        <stringProp name="ThreadGroup.ramp_time">1</stringProp>
        <boolProp name="ThreadGroup.scheduler">false</boolProp>
        <stringProp name="ThreadGroup.duration"></stringProp>
        <stringProp name="ThreadGroup.delay"></stringProp>
      </ThreadGroup>
      <hashTree>
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="HTTP请求" enabled="true">
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
            <collectionProp name="Arguments.arguments"/>
          </elementProp>
          <stringProp name="HTTPSampler.domain">www.baidu.com</stringProp>
          <stringProp name="HTTPSampler.port">80</stringProp>
          <stringProp name="HTTPSampler.protocol">http</stringProp>
          <stringProp name="HTTPSampler.contentEncoding"></stringProp>
          <stringProp name="HTTPSampler.path">/</stringProp>
          <stringProp name="HTTPSampler.method">GET</stringProp>
          <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
          <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
          <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
          <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          <stringProp name="HTTPSampler.embedded_url_re"></stringProp>
          <stringProp name="HTTPSampler.connect_timeout"></stringProp>
          <stringProp name="HTTPSampler.response_timeout"></stringProp>
        </HTTPSamplerProxy>
        <hashTree/>
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
  </hashTree>
</jmeterTestPlan>
```

### 4. 配置文件示例

**jmeter.properties优化配置**
```properties
# 语言设置
language=zh_CN

# 默认保存路径
jmeter.save.saveservice.base_dir=./results

# 响应数据编码
sampleresult.default.encoding=UTF-8

# 默认线程数
jmeter.threads=10

# 日志级别
log_level.jmeter=INFO
log_level.jmeter.junit=DEBUG

# 分布式测试配置
# remote_hosts=127.0.0.1
# server_port=1099
# client.rmi.localport=4000
# server.rmi.localport=4000

# HTTP配置
httpclient4.retrycount=1
httpclient4.time_to_live=30000

# 结果保存配置
jmeter.save.saveservice.output_format=csv
jmeter.save.saveservice.print_field_names=true
```

**user.properties个性化配置**
```properties
# 界面主题
jmeter.theme=Darklaf

# 默认监听器
jmeter.gui.action.listeners=ViewResultsTree,SummaryReport

# 字体设置
jsyntaxtextarea.font.family=Consolas
jsyntaxtextarea.font.size=14

# 自动保存
jmeter.gui.action.save_automatically=false
jmeter.gui.action.save_interval=300000
```

## 运行说明

### 1. 环境检查
```bash
# 运行环境检查脚本
./check_java.sh
./verify_jmeter.sh
```

### 2. 执行测试
```bash
# 使用GUI模式打开测试脚本
jmeter -t first_test.jmx

# 使用非GUI模式执行测试
jmeter -n -t first_test.jmx -l results.jtl -e -o reports/
```

### 3. 查看结果
- 在JMeter GUI中查看"查看结果树"和"汇总报告"
- 或在浏览器中打开生成的HTML报告

## 常见问题

### 问题1: Java环境问题
**症状**: 启动时提示"Java not found"
**解决**: 检查Java安装和环境变量配置

### 问题2: 内存不足
**症状**: 出现OutOfMemoryError
**解决**: 修改jmeter.bat/jmeter.sh中的内存设置

### 问题3: 中文乱码
**症状**: 界面或响应内容显示乱码
**解决**: 在jmeter.properties中设置UTF-8编码

## 下一步

完成本章练习后，可以继续学习第2章：JMeter基础概念与核心组件