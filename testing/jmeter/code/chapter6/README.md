# 第6章代码示例 - JMeter分布式测试

## 分布式测试配置与脚本

### 1. 完整分布式测试配置

**distributed_test_setup.jmx** - 分布式测试主控节点配置

```xml
<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.3">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="分布式性能测试" enabled="true">
      <stringProp name="TestPlan.comments">分布式性能测试配置，支持多节点协同工作</stringProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.tearDown_on_shutdown">true</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
      <elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
        <collectionProp name="Arguments.arguments">
          <elementProp name="MASTER_IP" elementType="Argument">
            <stringProp name="Argument.name">MASTER_IP</stringProp>
            <stringProp name="Argument.value">192.168.1.100</stringProp>
            <stringProp name="Argument.metadata">=</stringProp>
          </elementProp>
          <elementProp name="SLAVE_NODES" elementType="Argument">
            <stringProp name="Argument.name">SLAVE_NODES</stringProp>
            <stringProp name="Argument.value">192.168.1.101:1099,192.168.1.102:1099,192.168.1.103:1099</stringProp>
            <stringProp name="Argument.metadata">=</stringProp>
          </elementProp>
          <elementProp name="TARGET_HOST" elementType="Argument">
            <stringProp name="Argument.name">TARGET_HOST</stringProp>
            <stringProp name="Argument.value">api.example.com</stringProp>
            <stringProp name="Argument.metadata">=</stringProp>
          </elementProp>
        </collectionProp>
      </elementProp>
      <stringProp name="TestPlan.user_define_classpath"></stringProp>
    </TestPlan>
    <hashTree>
      
      <!-- 分布式测试配置 -->
      <RemoteThreads guiclass="RemoteThreadsGui" testclass="RemoteThreads" testname="远程线程配置" enabled="true">
        <collectionProp name="RemoteThreads.hosts">
          <elementProp name="" elementType="Argument">
            <stringProp name="Argument.name">192.168.1.101</stringProp>
            <stringProp name="Argument.value">192.168.1.101:1099</stringProp>
            <stringProp name="Argument.metadata">=</stringProp>
          </elementProp>
          <elementProp name="" elementType="Argument">
            <stringProp name="Argument.name">192.168.1.102</stringProp>
            <stringProp name="Argument.value">192.168.1.102:1099</stringProp>
            <stringProp name="Argument.metadata">=</stringProp>
          </elementProp>
          <elementProp name="" elementType="Argument">
            <stringProp name="Argument.name">192.168.1.103</stringProp>
            <stringProp name="Argument.value">192.168.1.103:1099</stringProp>
            <stringProp name="Argument.metadata">=</stringProp>
          </elementProp>
        </collectionProp>
      </RemoteThreads>
      <hashTree/>
      
      <!-- 主要测试线程组 -->
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="分布式负载测试" enabled="true">
        <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="循环控制器" enabled="true">
          <boolProp name="LoopController.continue_forever">false</boolProp>
          <stringProp name="LoopController.loops">100</stringProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">50</stringProp>
        <stringProp name="ThreadGroup.ramp_time">300</stringProp>
        <boolProp name="ThreadGroup.scheduler">true</boolProp>
        <stringProp name="ThreadGroup.duration">1800</stringProp>
        <stringProp name="ThreadGroup.delay"></stringProp>
        <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
      </ThreadGroup>
      <hashTree>
        
        <!-- 分布式测试控制器 -->
        <ThroughputController guiclass="ThroughputControllerGui" testclass="ThroughputController" testname="吞吐量控制器" enabled="true">
          <intProp name="ThroughputController.style">0</intProp>
          <stringProp name="ThroughputController.perThread">false</stringProp>
          <stringProp name="ThroughputController.maxThroughput">1000</stringProp>
        </ThroughputController>
        <hashTree>
          
          <!-- API性能测试 -->
          <TransactionController guiclass="TransactionControllerGui" testclass="TransactionController" testname="API性能测试" enabled="true">
            <boolProp name="TransactionController.includeTimers">true</boolProp>
            <boolProp name="TransactionController.parent">true</boolProp>
          </TransactionController>
          <hashTree>
            
            <!-- 用户登录API -->
            <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="POST_用户登录" enabled="true">
              <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
                <collectionProp name="Arguments.arguments">
                  <elementProp name="" elementType="HTTPArgument">
                    <boolProp name="HTTPArgument.always_encode">false</boolProp>
                    <stringProp name="Argument.value">{"username": "user${__threadNum}", "password": "password${__threadNum}"}</stringProp>
                    <stringProp name="Argument.metadata">=</stringProp>
                    <boolProp name="HTTPArgument.use_equals">true</boolProp>
                    <stringProp name="Argument.name"></stringProp>
                  </elementProp>
                </collectionProp>
              </elementProp>
              <stringProp name="HTTPSampler.domain">${TARGET_HOST}</stringProp>
              <stringProp name="HTTPSampler.port">443</stringProp>
              <stringProp name="HTTPSampler.protocol">https</stringProp>
              <stringProp name="HTTPSampler.contentEncoding">UTF-8</stringProp>
              <stringProp name="HTTPSampler.path">/api/v1/auth/login</stringProp>
              <stringProp name="HTTPSampler.method">POST</stringProp>
              <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
              <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
              <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
              <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
              <stringProp name="HTTPSampler.embedded_url_re"></stringProp>
              <stringProp name="HTTPSampler.connect_timeout">10000</stringProp>
              <stringProp name="HTTPSampler.response_timeout">30000</stringProp>
            </HTTPSamplerProxy>
            <hashTree>
              
              <!-- JSON提取器 - 提取token -->
              <JSONPostProcessor guiclass="JSONPostProcessorGui" testclass="JSONPostProcessor" testname="JSON提取器_提取Token" enabled="true">
                <stringProp name="JSONPostProcessor.referenceNames">AUTH_TOKEN</stringProp>
                <stringProp name="JSONPostProcessor.jsonPathExprs">$.data.access_token</stringProp>
                <stringProp name="JSONPostProcessor.match_numbers">0</stringProp>
                <stringProp name="JSONPostProcessor.defaultValues">NOT_FOUND</stringProp>
              </JSONPostProcessor>
              <hashTree/>
              
            </hashTree>
            
            <!-- 查询用户信息 -->
            <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="GET_用户信息" enabled="true">
              <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
                <collectionProp name="Arguments.arguments"/>
              </elementProp>
              <stringProp name="HTTPSampler.domain">${TARGET_HOST}</stringProp>
              <stringProp name="HTTPSampler.port">443</stringProp>
              <stringProp name="HTTPSampler.protocol">https</stringProp>
              <stringProp name="HTTPSampler.contentEncoding"></stringProp>
              <stringProp name="HTTPSampler.path">/api/v1/users/profile</stringProp>
              <stringProp name="HTTPSampler.method">GET</stringProp>
              <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
              <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
              <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
              <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
              <stringProp name="HTTPSampler.embedded_url_re"></stringProp>
              <stringProp name="HTTPSampler.connect_timeout">10000</stringProp>
              <stringProp name="HTTPSampler.response_timeout">30000</stringProp>
            </HTTPSamplerProxy>
            <hashTree>
              
              <!-- 认证头部管理器 -->
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
            
          </hashTree>
          
        </hashTree>
        
      </hashTree>
      
      <!-- 分布式结果收集器 -->
      <ResultCollector guiclass="ResultCollectorGui" testclass="ResultCollector" testname="分布式结果收集" enabled="true">
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
        <stringProp name="filename">distributed_results.jtl</stringProp>
      </ResultCollector>
      <hashTree/>
      
      <!-- 聚合报告 -->
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
        <stringProp name="filename">aggregate_report.jtl</stringProp>
      </ResultCollector>
      <hashTree/>
      
    </hashTree>
  </hashTree>
</jmeterTestPlan>
```

### 2. 从节点启动脚本

**slave_node_start.sh** - Linux从节点启动脚本

```bash
#!/bin/bash
# JMeter分布式测试从节点启动脚本

# 设置环境变量
export JMETER_HOME=/opt/jmeter
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk
export PATH=$JAVA_HOME/bin:$PATH

# 配置参数
SLAVE_HOST="0.0.0.0"  # 监听所有接口
SLAVE_PORT="1099"     # RMI端口
MASTER_HOST="192.168.1.100"  # 主节点IP
SERVER_PORT="1099"     # 服务器端口

# 检查JMeter安装
if [ ! -d "$JMETER_HOME" ]; then
    echo "错误: JMeter未安装或路径不正确"
    exit 1
fi

# 检查Java环境
if ! command -v java &> /dev/null; then
    echo "错误: Java未安装"
    exit 1
fi

# 设置JMeter参数
JMETER_OPTS="-Xms512m -Xmx2048m -Djava.rmi.server.hostname=$SLAVE_HOST"

# 启动从节点服务
echo "启动JMeter从节点服务..."
echo "主机: $SLAVE_HOST"
echo "端口: $SLAVE_PORT"
echo "主节点: $MASTER_HOST"

cd $JMETER_HOME

# 启动从节点
java $JMETER_OPTS \
  -jar $JMETER_HOME/bin/ApacheJMeter.jar \
  -s \
  -j $JMETER_HOME/logs/slave.log \
  -Dserver.rmi.localport=$SLAVE_PORT \
  -Dserver_port=$SERVER_PORT \
  -Djava.rmi.server.hostname=$SLAVE_HOST &

# 获取进程ID
SLAVE_PID=$!
echo "从节点服务已启动，PID: $SLAVE_PID"

# 保存PID到文件
echo $SLAVE_PID > /var/run/jmeter-slave.pid

# 等待服务启动
sleep 5

# 检查服务状态
if ps -p $SLAVE_PID > /dev/null; then
    echo "JMeter从节点服务启动成功"
    echo "日志文件: $JMETER_HOME/logs/slave.log"
    echo "PID文件: /var/run/jmeter-slave.pid"
else
    echo "错误: JMeter从节点服务启动失败"
    exit 1
fi

# 监控服务状态
echo "监控服务状态，按Ctrl+C停止..."
while true; do
    if ! ps -p $SLAVE_PID > /dev/null; then
        echo "JMeter从节点服务已停止"
        break
    fi
    sleep 10
done
```

**slave_node_start.bat** - Windows从节点启动脚本

```batch
@echo off
REM JMeter分布式测试从节点启动脚本 (Windows)

REM 设置环境变量
set JMETER_HOME=C:\apache-jmeter-5.6.3
set JAVA_HOME=C:\Program Files\Java\jdk-11
set PATH=%JAVA_HOME%\bin;%PATH%

REM 配置参数
set SLAVE_HOST=0.0.0.0
set SLAVE_PORT=1099
set MASTER_HOST=192.168.1.100
set SERVER_PORT=1099

REM 检查JMeter安装
if not exist "%JMETER_HOME%" (
    echo 错误: JMeter未安装或路径不正确
    pause
    exit /b 1
)

REM 检查Java环境
java -version >nul 2>&1
if errorlevel 1 (
    echo 错误: Java未安装或未配置
    pause
    exit /b 1
)

REM 设置JMeter参数
set JMETER_OPTS=-Xms512m -Xmx2048m -Djava.rmi.server.hostname=%SLAVE_HOST%

REM 启动从节点服务
echo 启动JMeter从节点服务...
echo 主机: %SLAVE_HOST%
echo 端口: %SLAVE_PORT%
echo 主节点: %MASTER_HOST%

cd /d %JMETER_HOME%

REM 启动从节点
start "JMeter Slave" /min java %JMETER_OPTS% ^
  -jar bin\ApacheJMeter.jar ^
  -s ^
  -j logs\slave.log ^
  -Dserver.rmi.localport=%SLAVE_PORT% ^
  -Dserver_port=%SERVER_PORT% ^
  -Djava.rmi.server.hostname=%SLAVE_HOST%

echo JMeter从节点服务已启动
echo 日志文件: %JMETER_HOME%\logs\slave.log

pause
```

### 3. 主节点控制脚本

**master_control.py** - Python主节点控制脚本

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JMeter分布式测试主节点控制脚本
支持多节点管理和监控
"""

import subprocess
import time
import threading
import json
import os
from datetime import datetime

class JMeterMasterController:
    def __init__(self, config_file="distributed_config.json"):
        """初始化主控制器"""
        self.config_file = config_file
        self.slave_nodes = []
        self.jmeter_home = ""
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.jmeter_home = config.get('jmeter_home', '/opt/jmeter')
            self.slave_nodes = config.get('slave_nodes', [])
            
            print(f"加载配置成功: {len(self.slave_nodes)} 个从节点")
            for node in self.slave_nodes:
                print(f"  从节点: {node['host']}:{node['port']}")
                
        except FileNotFoundError:
            print("配置文件不存在，使用默认配置")
            self.create_default_config()
        except Exception as e:
            print(f"加载配置失败: {e}")
    
    def create_default_config(self):
        """创建默认配置"""
        default_config = {
            "jmeter_home": "/opt/jmeter",
            "slave_nodes": [
                {"host": "192.168.1.101", "port": "1099"},
                {"host": "192.168.1.102", "port": "1099"},
                {"host": "192.168.1.103", "port": "1099"}
            ]
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        print("已创建默认配置文件")
    
    def check_slave_status(self, host, port):
        """检查从节点状态"""
        try:
            # 使用ping检查节点连通性
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "1", host],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # 检查JMeter服务端口
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((host, int(port)))
                sock.close()
                
                return result == 0
            
        except Exception as e:
            print(f"检查从节点 {host}:{port} 状态失败: {e}")
        
        return False
    
    def start_distributed_test(self, test_plan, results_dir="results"):
        """启动分布式测试"""
        if not os.path.exists(test_plan):
            print(f"测试计划文件不存在: {test_plan}")
            return False
        
        # 创建结果目录
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
        
        # 构建从节点列表
        remote_hosts = ",".join([f"{node['host']}:{node['port']}" for node in self.slave_nodes])
        
        # 构建JMeter命令
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        jtl_file = os.path.join(results_dir, f"distributed_test_{timestamp}.jtl")
        report_dir = os.path.join(results_dir, f"report_{timestamp}")
        
        jmeter_cmd = [
            os.path.join(self.jmeter_home, "bin", "jmeter"),
            "-n",  # 非GUI模式
            "-t", test_plan,  # 测试计划
            "-R", remote_hosts,  # 远程主机
            "-l", jtl_file,  # 结果文件
            "-e",  # 生成报告
            "-o", report_dir  # 报告目录
        ]
        
        print(f"启动分布式测试...")
        print(f"测试计划: {test_plan}")
        print(f"从节点: {remote_hosts}")
        print(f"结果文件: {jtl_file}")
        print(f"报告目录: {report_dir}")
        
        try:
            # 执行JMeter命令
            process = subprocess.Popen(
                jmeter_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # 实时输出
            def output_reader(pipe, pipe_name):
                for line in iter(pipe.readline, ''):
                    print(f"[{pipe_name}] {line.strip()}")
                pipe.close()
            
            # 启动输出线程
            stdout_thread = threading.Thread(
                target=output_reader,
                args=(process.stdout, "STDOUT")
            )
            stderr_thread = threading.Thread(
                target=output_reader,
                args=(process.stderr, "STDERR")
            )
            
            stdout_thread.start()
            stderr_thread.start()
            
            # 等待进程完成
            return_code = process.wait()
            
            stdout_thread.join()
            stderr_thread.join()
            
            if return_code == 0:
                print("分布式测试执行成功")
                print(f"测试报告: file://{os.path.abspath(report_dir)}/index.html")
                return True
            else:
                print(f"分布式测试执行失败，返回码: {return_code}")
                return False
                
        except Exception as e:
            print(f"执行分布式测试失败: {e}")
            return False
    
    def monitor_slaves(self):
        """监控从节点状态"""
        print("\n=== 从节点状态监控 ===")
        
        while True:
            status_report = []
            
            for node in self.slave_nodes:
                host = node['host']
                port = node['port']
                
                is_online = self.check_slave_status(host, port)
                status = "在线" if is_online else "离线"
                status_report.append(f"{host}:{port} - {status}")
            
            # 清屏并显示状态
            os.system('cls' if os.name == 'nt' else 'clear')
            print("=== JMeter从节点状态监控 ===")
            print(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("\n从节点状态:")
            for status in status_report:
                print(f"  {status}")
            
            print("\n按 Ctrl+C 停止监控")
            time.sleep(5)  # 每5秒更新一次
    
    def generate_report(self, jtl_file):
        """生成测试报告"""
        if not os.path.exists(jtl_file):
            print(f"结果文件不存在: {jtl_file}")
            return
        
        report_dir = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        jmeter_cmd = [
            os.path.join(self.jmeter_home, "bin", "jmeter"),
            "-g", jtl_file,  # 生成报告
            "-o", report_dir  # 报告目录
        ]
        
        try:
            subprocess.run(jmeter_cmd, check=True)
            print(f"测试报告已生成: file://{os.path.abspath(report_dir)}/index.html")
        except subprocess.CalledProcessError as e:
            print(f"生成报告失败: {e}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='JMeter分布式测试控制器')
    parser.add_argument('action', choices=['start', 'monitor', 'report'], 
                       help='执行动作: start-启动测试, monitor-监控节点, report-生成报告')
    parser.add_argument('--test-plan', help='测试计划文件路径')
    parser.add_argument('--jtl-file', help='JTL结果文件路径')
    
    args = parser.parse_args()
    
    controller = JMeterMasterController()
    
    if args.action == 'start':
        if not args.test_plan:
            print("请提供测试计划文件路径: --test-plan <file>")
            return
        
        controller.start_distributed_test(args.test_plan)
    
    elif args.action == 'monitor':
        try:
            controller.monitor_slaves()
        except KeyboardInterrupt:
            print("\n监控已停止")
    
    elif args.action == 'report':
        if not args.jtl_file:
            print("请提供JTL结果文件路径: --jtl-file <file>")
            return
        
        controller.generate_report(args.jtl_file)

if __name__ == "__main__":
    main()
```

## 运行说明

### 1. 配置分布式环境
```bash
# 创建配置文件
echo '{
  "jmeter_home": "/opt/jmeter",
  "slave_nodes": [
    {"host": "192.168.1.101", "port": "1099"},
    {"host": "192.168.1.102", "port": "1099"},
    {"host": "192.168.1.103", "port": "1099"}
  ]
}' > distributed_config.json

# 在所有从节点上启动JMeter服务
./slave_node_start.sh
```

### 2. 启动分布式测试
```bash
# 使用Python控制器启动测试
python master_control.py start --test-plan distributed_test_setup.jmx

# 或者直接使用JMeter命令
jmeter -n -t distributed_test_setup.jmx -R 192.168.1.101:1099,192.168.1.102:1099 -l results.jtl -e -o reports/
```

### 3. 监控从节点状态
```bash
# 实时监控从节点状态
python master_control.py monitor
```

## 分布式测试验证

### 1. 节点连通性验证
- 验证主节点与从节点的网络连通性
- 检查RMI服务端口是否正常
- 验证节点间的通信稳定性

### 2. 负载分布验证
- 验证负载是否均匀分布到各个从节点
- 检查各节点的资源使用情况
- 验证负载均衡策略的有效性

### 3. 结果一致性验证
- 验证分布式测试结果的准确性
- 检查数据同步和一致性
- 验证结果合并的正确性

## 练习建议

### 练习1：分布式环境配置
1. 配置多节点分布式环境
2. 测试不同网络环境下的性能
3. 优化节点间的通信配置

### 练习2：负载均衡策略
1. 测试不同的负载分配策略
2. 分析负载均衡对性能的影响
3. 优化负载分配算法

### 练习3：容错处理
1. 测试节点故障时的处理机制
2. 验证数据备份和恢复策略
3. 优化系统的容错能力

## 下一步

完成本章练习后，可以继续学习第7章：JMeter最佳实践与优化，学习性能调优和最佳实践。