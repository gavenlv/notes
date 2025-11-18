# 第5章代码示例 - JMeter性能测试与监控

## 性能监控与结果分析脚本

### 1. 完整性能监控测试脚本

**performance_monitoring_test.jmx** - 包含性能监控、结果分析和报告生成的完整测试

```xml
<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.3">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="性能监控测试" enabled="true">
      <stringProp name="TestPlan.comments">包含服务器监控、性能指标收集和详细结果分析的完整性能测试</stringProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.tearDown_on_shutdown">true</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
      <elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
        <collectionProp name="Arguments.arguments">
          <elementProp name="TARGET_HOST" elementType="Argument">
            <stringProp name="Argument.name">TARGET_HOST</stringProp>
            <stringProp name="Argument.value">httpbin.org</stringProp>
            <stringProp name="Argument.metadata">=</stringProp>
          </elementProp>
          <elementProp name="PERF_MONITOR_HOST" elementType="Argument">
            <stringProp name="Argument.name">PERF_MONITOR_HOST</stringProp>
            <stringProp name="Argument.value">localhost</stringProp>
            <stringProp name="Argument.metadata">=</stringProp>
          </elementProp>
          <elementProp name="PERF_MONITOR_PORT" elementType="Argument">
            <stringProp name="Argument.name">PERF_MONITOR_PORT</stringProp>
            <stringProp name="Argument.value">4444</stringProp>
            <stringProp name="Argument.metadata">=</stringProp>
          </elementProp>
        </collectionProp>
      </elementProp>
      <stringProp name="TestPlan.user_define_classpath">lib/jmeter-plugins-standard-1.4.0.jar:lib/jmeter-plugins-extras-1.4.0.jar</stringProp>
    </TestPlan>
    <hashTree>
      
      <!-- 性能监控配置 -->
      <PerfMonCollector guiclass="PerfMonGui" testclass="PerfMonCollector" testname="性能监控收集器" enabled="true">
        <boolProp name="PerfMonCollector.error_logging">false</boolProp>
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
        <stringProp name="filename">perfmon.jtl</stringProp>
        <collectionProp name="PerfMonCollector.metrics">
          <collectionProp name="">
            <stringProp name="">CPU</stringProp>
            <stringProp name="">${PERF_MONITOR_HOST}:${PERF_MONITOR_PORT}</stringProp>
            <stringProp name="">percent</stringProp>
          </collectionProp>
          <collectionProp name="">
            <stringProp name="">Memory</stringProp>
            <stringProp name="">${PERF_MONITOR_HOST}:${PERF_MONITOR_PORT}</stringProp>
            <stringProp name="">percent</stringProp>
          </collectionProp>
          <collectionProp name="">
            <stringProp name="">Swap</stringProp>
            <stringProp name="">${PERF_MONITOR_HOST}:${PERF_MONITOR_PORT}</stringProp>
            <stringProp name="">percent</stringProp>
          </collectionProp>
          <collectionProp name="">
            <stringProp name="">Disks I/O</stringProp>
            <stringProp name="">${PERF_MONITOR_HOST}:${PERF_MONITOR_PORT}</stringProp>
            <stringProp name="">kbpersec</stringProp>
          </collectionProp>
          <collectionProp name="">
            <stringProp name="">Network I/O</stringProp>
            <stringProp name="">${PERF_MONITOR_HOST}:${PERF_MONITOR_PORT}</stringProp>
            <stringProp name="">kbpersec</stringProp>
          </collectionProp>
        </collectionProp>
      </PerfMonCollector>
      <hashTree/>
      
      <!-- 主要测试线程组 -->
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="性能测试线程组" enabled="true">
        <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="循环控制器" enabled="true">
          <boolProp name="LoopController.continue_forever">false</boolProp>
          <stringProp name="LoopController.loops">10</stringProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">20</stringProp>
        <stringProp name="ThreadGroup.ramp_time">60</stringProp>
        <boolProp name="ThreadGroup.scheduler">true</boolProp>
        <stringProp name="ThreadGroup.duration">300</stringProp>
        <stringProp name="ThreadGroup.delay"></stringProp>
      </ThreadGroup>
      <hashTree>
        
        <!-- 性能监控开始 -->
        <PerfMonCollector guiclass="PerfMonGui" testclass="PerfMonCollector" testname="性能监控开始" enabled="true">
          <boolProp name="PerfMonCollector.error_logging">false</boolProp>
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
          <stringProp name="filename">perfmon_start.jtl</stringProp>
          <collectionProp name="PerfMonCollector.metrics">
            <collectionProp name="">
              <stringProp name="">CPU</stringProp>
              <stringProp name="">${PERF_MONITOR_HOST}:${PERF_MONITOR_PORT}</stringProp>
              <stringProp name="">percent</stringProp>
            </collectionProp>
          </collectionProp>
        </PerfMonCollector>
        <hashTree/>
        
        <!-- 基本HTTP请求测试 -->
        <TransactionController guiclass="TransactionControllerGui" testclass="TransactionController" testname="HTTP性能测试" enabled="true">
          <boolProp name="TransactionController.includeTimers">true</boolProp>
          <boolProp name="TransactionController.parent">true</boolProp>
        </TransactionController>
        <hashTree>
          
          <!-- GET请求测试 -->
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="GET_性能测试" enabled="true">
            <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
              <collectionProp name="Arguments.arguments"/>
            </elementProp>
            <stringProp name="HTTPSampler.domain">${TARGET_HOST}</stringProp>
            <stringProp name="HTTPSampler.port">80</stringProp>
            <stringProp name="HTTPSampler.protocol">http</stringProp>
            <stringProp name="HTTPSampler.contentEncoding"></stringProp>
            <stringProp name="HTTPSampler.path">/get</stringProp>
            <stringProp name="HTTPSampler.method">GET</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
            <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
            <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
            <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
            <stringProp name="HTTPSampler.embedded_url_re"></stringProp>
            <stringProp name="HTTPSampler.connect_timeout">5000</stringProp>
            <stringProp name="HTTPSampler.response_timeout">10000</stringProp>
          </HTTPSamplerProxy>
          <hashTree>
            
            <!-- 响应时间断言 -->
            <DurationAssertion guiclass="DurationAssertionGui" testclass="DurationAssertion" testname="响应时间断言" enabled="true">
              <stringProp name="DurationAssertion.duration">2000</stringProp>
            </DurationAssertion>
            <hashTree/>
            
          </hashTree>
          
          <!-- POST请求测试 -->
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="POST_性能测试" enabled="true">
            <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
              <collectionProp name="Arguments.arguments">
                <elementProp name="" elementType="HTTPArgument">
                  <boolProp name="HTTPArgument.always_encode">false</boolProp>
                  <stringProp name="Argument.value">{"test": "performance", "data": "${__Random(1,1000)}"}</stringProp>
                  <stringProp name="Argument.metadata">=</stringProp>
                  <boolProp name="HTTPArgument.use_equals">true</boolProp>
                  <stringProp name="Argument.name"></stringProp>
                </elementProp>
              </collectionProp>
            </elementProp>
            <stringProp name="HTTPSampler.domain">${TARGET_HOST}</stringProp>
            <stringProp name="HTTPSampler.port">80</stringProp>
            <stringProp name="HTTPSampler.protocol">http</stringProp>
            <stringProp name="HTTPSampler.contentEncoding">UTF-8</stringProp>
            <stringProp name="HTTPSampler.path">/post</stringProp>
            <stringProp name="HTTPSampler.method">POST</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
            <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
            <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
            <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
            <stringProp name="HTTPSampler.embedded_url_re"></stringProp>
            <stringProp name="HTTPSampler.connect_timeout">5000</stringProp>
            <stringProp name="HTTPSampler.response_timeout">10000</stringProp>
          </HTTPSamplerProxy>
          <hashTree>
            
            <!-- 响应时间断言 -->
            <DurationAssertion guiclass="DurationAssertionGui" testclass="DurationAssertion" testname="响应时间断言" enabled="true">
              <stringProp name="DurationAssertion.duration">3000</stringProp>
            </DurationAssertion>
            <hashTree/>
            
          </hashTree>
          
        </hashTree>
        
        <!-- 性能监控结束 -->
        <PerfMonCollector guiclass="PerfMonGui" testclass="PerfMonCollector" testname="性能监控结束" enabled="true">
          <boolProp name="PerfMonCollector.error_logging">false</boolProp>
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
          <stringProp name="filename">perfmon_end.jtl</stringProp>
          <collectionProp name="PerfMonCollector.metrics">
            <collectionProp name="">
              <stringProp name="">CPU</stringProp>
              <stringProp name="">${PERF_MONITOR_HOST}:${PERF_MONITOR_PORT}</stringProp>
              <stringProp name="">percent</stringProp>
            </collectionProp>
          </collectionProp>
        </PerfMonCollector>
        <hashTree/>
        
      </hashTree>
      
      <!-- 高级监听器 -->
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
        <stringProp name="filename">aggregate.jtl</stringProp>
      </ResultCollector>
      <hashTree/>
      
      <ResultCollector guiclass="ResponseTimesOverTime" testclass="ResultCollector" testname="响应时间随时间变化" enabled="true">
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
        <stringProp name="filename">response_times.jtl</stringProp>
      </ResultCollector>
      <hashTree/>
      
      <ResultCollector guiclass="TransactionsPerSecond" testclass="ResultCollector" testname="每秒事务数" enabled="true">
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
        <stringProp name="filename">tps.jtl</stringProp>
      </ResultCollector>
      <hashTree/>
      
      <!-- 后端监听器 - 实时结果发送 -->
      <BackendListener guiclass="BackendListenerGui" testclass="BackendListener" testname="后端监听器" enabled="true">
        <stringProp name="classname">org.apache.jmeter.visualizers.backend.influxdb.InfluxdbBackendListenerClient</stringProp>
        <collectionProp name="arguments">
          <elementProp name="influxdbUrl" elementType="Argument">
            <stringProp name="Argument.name">influxdbUrl</stringProp>
            <stringProp name="Argument.value">http://localhost:8086</stringProp>
            <stringProp name="Argument.metadata">=</stringProp>
          </elementProp>
          <elementProp name="application" elementType="Argument">
            <stringProp name="Argument.name">application</stringProp>
            <stringProp name="Argument.value">JMeterPerformanceTest</stringProp>
            <stringProp name="Argument.metadata">=</stringProp>
          </elementProp>
          <elementProp name="measurement" elementType="Argument">
            <stringProp name="Argument.name">measurement</stringProp>
            <stringProp name="Argument.value">jmeter</stringProp>
            <stringProp name="Argument.metadata">=</stringProp>
          </elementProp>
          <elementProp name="summaryOnly" elementType="Argument">
            <stringProp name="Argument.name">summaryOnly</stringProp>
            <stringProp name="Argument.value">false</stringProp>
            <stringProp name="Argument.metadata">=</stringProp>
          </elementProp>
          <elementProp name="samplersRegex" elementType="Argument">
            <stringProp name="Argument.name">samplersRegex</stringProp>
            <stringProp name="Argument.value">.*</stringProp>
            <stringProp name="Argument.metadata">=</stringProp>
          </elementProp>
          <elementProp name="percentiles" elementType="Argument">
            <stringProp name="Argument.name">percentiles</stringProp>
            <stringProp name="Argument.value">90;95;99</stringProp>
            <stringProp name="Argument.metadata">=</stringProp>
          </elementProp>
        </collectionProp>
      </BackendListener>
      <hashTree/>
      
    </hashTree>
  </hashTree>
</jmeterTestPlan>
```

### 2. 性能分析脚本

**performance_analysis.py** - Python脚本用于性能数据分析

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JMeter性能测试结果分析脚本
支持多种格式的结果文件分析
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
import sys

class JMeterPerformanceAnalyzer:
    def __init__(self, jtl_file_path):
        """初始化分析器"""
        self.jtl_file = jtl_file_path
        self.data = None
        
    def load_jtl_data(self):
        """加载JTL文件数据"""
        try:
            # 读取CSV格式的JTL文件
            self.data = pd.read_csv(self.jtl_file, delimiter=',')
            print(f"成功加载数据，共 {len(self.data)} 条记录")
            return True
        except Exception as e:
            print(f"加载数据失败: {e}")
            return False
    
    def basic_statistics(self):
        """基础统计分析"""
        if self.data is None:
            print("请先加载数据")
            return
            
        print("\n=== 基础统计信息 ===")
        
        # 响应时间统计
        response_times = self.data['elapsed'].dropna()
        print(f"平均响应时间: {response_times.mean():.2f} ms")
        print(f"最小响应时间: {response_times.min():.2f} ms")
        print(f"最大响应时间: {response_times.max():.2f} ms")
        print(f"响应时间标准差: {response_times.std():.2f} ms")
        
        # 成功率统计
        success_count = self.data['success'].sum()
        total_count = len(self.data)
        success_rate = (success_count / total_count) * 100
        print(f"成功率: {success_rate:.2f}% ({success_count}/{total_count})")
        
        # 吞吐量统计
        start_time = self.data['timeStamp'].min()
        end_time = self.data['timeStamp'].max()
        duration_seconds = (end_time - start_time) / 1000
        throughput = total_count / duration_seconds
        print(f"测试持续时间: {duration_seconds:.2f} 秒")
        print(f"平均吞吐量: {throughput:.2f} 请求/秒")
        
    def percentile_analysis(self):
        """百分位数分析"""
        if self.data is None:
            print("请先加载数据")
            return
            
        print("\n=== 百分位数分析 ===")
        
        response_times = self.data['elapsed'].dropna()
        
        percentiles = [50, 75, 90, 95, 99, 99.9]
        for p in percentiles:
            value = np.percentile(response_times, p)
            print(f"{p}% 响应时间: {value:.2f} ms")
    
    def error_analysis(self):
        """错误分析"""
        if self.data is None:
            print("请先加载数据")
            return
            
        print("\n=== 错误分析 ===")
        
        # 错误请求统计
        error_data = self.data[self.data['success'] == False]
        
        if len(error_data) > 0:
            print(f"错误请求数量: {len(error_data)}")
            
            # 错误类型分布
            error_types = error_data['responseCode'].value_counts()
            print("错误类型分布:")
            for code, count in error_types.items():
                print(f"  {code}: {count} 次")
            
            # 错误率最高的采样器
            sampler_errors = error_data['label'].value_counts().head(5)
            print("错误率最高的采样器:")
            for sampler, count in sampler_errors.items():
                print(f"  {sampler}: {count} 次错误")
        else:
            print("无错误请求")
    
    def response_time_trend(self):
        """响应时间趋势分析"""
        if self.data is None:
            print("请先加载数据")
            return
            
        # 按时间窗口分组分析
        self.data['time_window'] = pd.cut(self.data['timeStamp'], 
                                        bins=10, 
                                        labels=range(10))
        
        window_stats = self.data.groupby('time_window')['elapsed'].agg([
            'mean', 'std', 'count'
        ]).reset_index()
        
        print("\n=== 响应时间趋势分析 ===")
        for _, row in window_stats.iterrows():
            print(f"时间窗口 {row['time_window']}: "
                  f"平均响应时间 {row['mean']:.2f} ms, "
                  f"标准差 {row['std']:.2f} ms, "
                  f"请求数 {row['count']}")
    
    def create_visualizations(self):
        """创建可视化图表"""
        if self.data is None:
            print("请先加载数据")
            return
            
        # 设置图表样式
        plt.style.use('seaborn-v0_8')
        
        # 1. 响应时间分布直方图
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 2, 1)
        response_times = self.data['elapsed'].dropna()
        plt.hist(response_times, bins=50, alpha=0.7, color='skyblue')
        plt.xlabel('响应时间 (ms)')
        plt.ylabel('频次')
        plt.title('响应时间分布')
        plt.grid(True, alpha=0.3)
        
        # 2. 响应时间箱线图
        plt.subplot(2, 2, 2)
        sampler_response_times = self.data.groupby('label')['elapsed'].apply(list)
        plt.boxplot(sampler_response_times.values, 
                   labels=sampler_response_times.index)
        plt.xticks(rotation=45)
        plt.ylabel('响应时间 (ms)')
        plt.title('各采样器响应时间分布')
        plt.grid(True, alpha=0.3)
        
        # 3. 吞吐量趋势图
        plt.subplot(2, 2, 3)
        self.data['minute'] = pd.to_datetime(self.data['timeStamp'], unit='ms').dt.floor('min')
        throughput = self.data.groupby('minute').size()
        plt.plot(throughput.index, throughput.values, marker='o')
        plt.xlabel('时间')
        plt.ylabel('请求数/分钟')
        plt.title('吞吐量趋势')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        
        # 4. 错误率饼图
        plt.subplot(2, 2, 4)
        success_count = self.data['success'].sum()
        error_count = len(self.data) - success_count
        labels = ['成功', '失败']
        sizes = [success_count, error_count]
        colors = ['lightgreen', 'lightcoral']
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.title('请求成功率')
        
        plt.tight_layout()
        plt.savefig('performance_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_report(self):
        """生成性能分析报告"""
        if self.data is None:
            print("请先加载数据")
            return
            
        report = {
            "timestamp": datetime.now().isoformat(),
            "file_analyzed": self.jtl_file,
            "total_requests": len(self.data),
            "success_rate": (self.data['success'].sum() / len(self.data)) * 100,
            "avg_response_time": self.data['elapsed'].mean(),
            "min_response_time": self.data['elapsed'].min(),
            "max_response_time": self.data['elapsed'].max(),
            "percentiles": {}
        }
        
        # 计算百分位数
        response_times = self.data['elapsed'].dropna()
        for p in [50, 75, 90, 95, 99]:
            report["percentiles"][f"p{p}"] = np.percentile(response_times, p)
        
        # 保存报告
        with open('performance_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print("\n性能分析报告已保存到 performance_report.json")
        
        return report

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python performance_analysis.py <jtl文件路径>")
        return
    
    jtl_file = sys.argv[1]
    
    # 创建分析器实例
    analyzer = JMeterPerformanceAnalyzer(jtl_file)
    
    # 加载数据
    if not analyzer.load_jtl_data():
        return
    
    # 执行分析
    analyzer.basic_statistics()
    analyzer.percentile_analysis()
    analyzer.error_analysis()
    analyzer.response_time_trend()
    
    # 生成可视化图表
    analyzer.create_visualizations()
    
    # 生成报告
    report = analyzer.generate_report()
    
    print("\n=== 分析完成 ===")
    print(f"报告文件: performance_report.json")
    print(f"图表文件: performance_analysis.png")

if __name__ == "__main__":
    main()
```

### 3. 性能监控配置

**perfmon_agent_config.xml** - 性能监控代理配置

```xml
<!-- 性能监控代理配置 -->
<ServerAgentConfig>
    <service>
        <name>ServerAgent</name>
        <description>JMeter性能监控代理</description>
        <connector>org.apache.jmeter.protocol.java.sampler.JavaSampler</connector>
    </service>
    
    <metric>
        <name>CPU</name>
        <description>CPU使用率监控</description>
        <collector>org.apache.jmeter.protocol.java.sampler.JavaSampler</collector>
        <interval>5000</interval>
    </metric>
    
    <metric>
        <name>Memory</name>
        <description>内存使用率监控</description>
        <collector>org.apache.jmeter.protocol.java.sampler.JavaSampler</collector>
        <interval>5000</interval>
    </metric>
    
    <metric>
        <name>DiskIO</name>
        <description>磁盘IO监控</description>
        <collector>org.apache.jmeter.protocol.java.sampler.JavaSampler</collector>
        <interval>10000</interval>
    </metric>
    
    <metric>
        <name>NetworkIO</name>
        <description>网络IO监控</description>
        <collector>org.apache.jmeter.protocol.java.sampler.JavaSampler</collector>
        <interval>10000</interval>
    </metric>
</ServerAgentConfig>
```

## 运行说明

### 1. 安装性能监控插件
```bash
# 下载JMeter插件管理器
wget https://repo1.maven.org/maven2/kg/apc/jmeter-plugins-manager/1.7/jmeter-plugins-manager-1.7.jar

# 将插件管理器放入JMeter的lib/ext目录
cp jmeter-plugins-manager-1.7.jar $JMETER_HOME/lib/ext/

# 启动JMeter GUI，通过插件管理器安装性能监控插件
jmeter
```

### 2. 启动性能监控代理
```bash
# 启动ServerAgent（需要先下载ServerAgent）
cd ServerAgent-2.2.3
./startAgent.sh --tcp-port 4444 --udp-port 4444
```

### 3. 执行性能测试
```bash
# 使用非GUI模式执行性能测试
jmeter -n -t performance_monitoring_test.jmx -l results.jtl -e -o reports/

# 使用Python脚本分析结果
python performance_analysis.py results.jtl
```

## 性能监控验证

### 1. 监控数据验证
- 验证CPU、内存、磁盘、网络监控数据是否正确收集
- 分析监控数据的准确性和实时性
- 验证监控数据的完整性

### 2. 性能指标验证
- 验证响应时间、吞吐量、错误率等关键指标
- 分析性能数据的统计准确性
- 验证性能趋势的可信度

### 3. 报告生成验证
- 验证分析报告的内容完整性
- 检查可视化图表的准确性
- 验证报告格式的可读性

## 练习建议

### 练习1：性能监控配置
1. 调整监控参数，观察监控效果变化
2. 配置不同的监控指标组合
3. 测试监控数据的实时性

### 练习2：数据分析优化
1. 优化Python分析脚本的性能
2. 添加新的分析指标和图表
3. 测试不同规模数据的分析效果

### 练习3：报告定制
1. 定制个性化的分析报告格式
2. 添加业务相关的性能指标
3. 优化报告的可读性和实用性

## 下一步

完成本章练习后，可以继续学习第6章：JMeter分布式测试，学习大规模测试的分布式部署和执行。