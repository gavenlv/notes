# 第1章：Gatling简介与环境搭建

## 1.1 什么是Gatling

Gatling是一款高性能的开源负载测试工具，专为测试Web应用程序而设计。它由法国公司Gatling Corp开发，使用Scala语言编写，提供了一个强大的DSL（领域特定语言）来定义测试场景。

### 1.1.1 Gatling的特点

1. **高性能**：Gatling基于Akka和Netty框架构建，能够高效处理大量并发请求
2. **易于编写**：提供简洁的DSL，使测试脚本编写变得直观
3. **实时监控**：提供实时HTML报告，无需等待测试结束即可查看结果
4. **协议支持**：支持HTTP、HTTPS、WebSocket、JMS等多种协议
5. **可扩展性**：支持插件机制，可以扩展功能

### 1.1.2 与其他性能测试工具的比较

| 特性 | Gatling | JMeter | LoadRunner |
|------|---------|--------|------------|
| 编写语言 | Scala/Java | Java | C/C++ |
| 学习曲线 | 中等 | 较低 | 较高 |
| 性能 | 高 | 中等 | 高 |
| 资源消耗 | 低 | 高 | 高 |
| 报告功能 | 优秀 | 良好 | 优秀 |
| 开源 | 是 | 是 | 否 |

## 1.2 Gatling的应用场景

Gatling适用于以下场景：

1. **Web应用性能测试**：测试Web服务器在高并发下的响应能力
2. **API性能测试**：测试RESTful API的性能表现
3. **压力测试**：确定系统的最大承载能力
4. **稳定性测试**：长时间运行测试以检测内存泄漏等问题
5. **回归测试**：确保新代码不会影响系统性能

## 1.3 Gatling架构概述

Gatling采用以下架构设计：

1. **模拟引擎**：负责生成虚拟用户和执行测试场景
2. **HTTP引擎**：处理HTTP/HTTPS请求和响应
3. **报告引擎**：生成实时和最终测试报告
4. **配置系统**：管理测试配置和参数

## 1.4 环境要求

在安装Gatling之前，需要确保系统满足以下要求：

1. **Java环境**：Java 8或更高版本（推荐Java 11）
2. **操作系统**：Windows、Linux或macOS
3. **内存**：至少2GB可用内存（推荐4GB或更多）
4. **磁盘空间**：至少500MB可用空间

## 1.5 安装Gatling

### 1.5.1 下载Gatling

1. 访问Gatling官方网站：https://gatling.io/
2. 点击"Download"按钮
3. 选择最新稳定版本（如Gatling 3.x）
4. 下载ZIP压缩包

### 1.5.2 安装步骤

#### Windows系统

1. 将下载的ZIP文件解压到目标目录（如`C:\gatling`）
2. 设置环境变量：
   - 创建`GATLING_HOME`变量，值为Gatling安装目录
   - 将`%GATLING_HOME%\bin`添加到`PATH`变量中
3. 验证安装：打开命令提示符，输入`gatling -version`

#### Linux/macOS系统

1. 将下载的ZIP文件解压到目标目录（如`/opt/gatling`）
2. 设置环境变量：
   ```bash
   export GATLING_HOME=/opt/gatling
   export PATH=$PATH:$GATLING_HOME/bin
   ```
3. 将上述命令添加到`~/.bashrc`或`~/.zshrc`文件中
4. 重新加载配置：`source ~/.bashrc`
5. 验证安装：在终端中输入`gatling -version`

### 1.5.3 使用包管理器安装（可选）

#### 使用Homebrew（macOS）

```bash
brew install gatling
```

#### 使用SDKMAN!

```bash
sdk install gatling
```

## 1.6 Gatling目录结构

解压Gatling后，主要目录结构如下：

```
gatling/
├── bin/                    # 可执行脚本
├── conf/                   # 配置文件
│   ├── gatling.conf        # Gatling主配置文件
│   ├── logback.xml         # 日志配置
│   └── recorder.conf       # 录制器配置
├── lib/                    # 依赖库
├── results/                # 测试结果目录
├── target/                 # 编译输出目录
├── user-files/             # 用户文件目录
│   ├── bodies/             # 请求体文件
│   ├── data/               # 测试数据文件
│   └── simulations/        # 测试脚本目录
└── README.md
```

## 1.7 配置Gatling

### 1.7.1 基本配置

打开`conf/gatling.conf`文件，主要配置项如下：

```hocon
gatling {
  core {
    # 输出目录
    outputDirectory = "results"
    
    # 是否生成报告
    generateReport = true
    
    # 请求超时时间（毫秒）
    timeOut = 30000
    
    # 模拟类路径
    simulationClass = ""
  }
  
  http {
    # HTTP配置
    baseUrls = []
    
    # 默认请求头
    headers = []
    
    # 是否遵循重定向
    followRedirect = true
    
    # 最大重定向次数
    maxRedirects = 20
  }
  
  data {
    # 数据目录
    dataDirectory = "user-files/data"
    
    # 请求体目录
    bodiesDirectory = "user-files/bodies"
    
    # 模拟目录
    simulationsDirectory = "user-files/simulations"
  }
}
```

### 1.7.2 日志配置

打开`conf/logback.xml`文件，可以配置日志级别和输出格式。

## 1.8 第一个Gatling测试

### 1.8.1 创建测试脚本

在`user-files/simulations`目录下创建一个新的Scala文件，例如`BasicSimulation.scala`：

```scala
import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._

class BasicSimulation extends Simulation {

  // HTTP配置
  val httpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com") // 基础URL
    .acceptHeader("application/json") // 默认请求头

  // 场景定义
  val scn = scenario("Basic Test")
    .exec(http("Get All Posts")
      .get("/posts")
      .check(status.is(200))) // 检查响应状态码为200

  // 设置负载
  setUp(
    scn.inject(atOnceUsers(1)) // 注入1个用户
  ).protocols(httpProtocol)
}
```

### 1.8.2 运行测试

有两种方式运行测试：

1. **使用命令行**：
   ```bash
   gatling -s BasicSimulation
   ```

2. **使用批处理脚本**：
   - Windows：运行`bin/gatling.bat`
   - Linux/macOS：运行`bin/gatling.sh`

### 1.8.3 查看结果

测试完成后，Gatling会生成HTML报告，存储在`results`目录下。可以通过浏览器打开`index.html`文件查看详细的测试结果。

## 1.9 IDE集成

### 1.9.1 IntelliJ IDEA

1. 创建新的Scala项目
2. 添加Gatling依赖到`build.sbt`：
   ```scala
   libraryDependencies += "io.gatling.highcharts" % "gatling-charts-highcharts" % "3.7.0" % "test,it"
   libraryDependencies += "io.gatling"            % "gatling-test-framework"    % "3.7.0" % "test,it"
   ```
3. 将Gatling的`user-files`目录设置为资源目录
4. 创建测试类并运行

### 1.9.2 Eclipse

1. 安装Scala IDE插件
2. 创建Scala项目
3. 添加Gatling依赖库
4. 配置构建路径

### 1.9.3 VS Code

1. 安装Scala扩展包
2. 创建项目并配置`build.sbt`
3. 添加Gatling依赖

## 1.10 常见问题与解决方案

### 1.10.1 Java版本不兼容

**问题**：运行Gatling时出现Java版本错误
**解决方案**：确保使用Java 8或更高版本，可以通过`java -version`命令检查

### 1.10.2 内存不足

**问题**：运行大规模测试时出现内存不足错误
**解决方案**：增加JVM堆内存大小，修改`bin/gatling.bat`或`bin/gatling.sh`文件中的JVM参数

### 1.10.3 端口占用

**问题**：Gatling报告服务器端口被占用
**解决方案**：修改`conf/gatling.conf`中的`charting.noReports`和`charting.port`配置

## 1.11 实验一：安装并运行第一个Gatling测试

### 实验目标

1. 成功安装Gatling
2. 创建并运行第一个简单的测试脚本
3. 理解Gatling的基本工作流程

### 实验步骤

1. **安装Java环境**
   - 确保已安装Java 8或更高版本
   - 设置JAVA_HOME环境变量

2. **下载并安装Gatling**
   - 从官方网站下载Gatling
   - 解压到目标目录
   - 设置GATLING_HOME环境变量

3. **创建测试脚本**
   - 在`user-files/simulations`目录下创建`MyFirstSimulation.scala`
   - 编写一个简单的GET请求测试

4. **运行测试**
   - 使用命令行运行测试
   - 观察控制台输出

5. **查看结果**
   - 打开生成的HTML报告
   - 分析测试结果

### 实验代码

```scala
import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._

class MyFirstSimulation extends Simulation {

  // HTTP配置
  val httpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .acceptHeader("application/json")

  // 场景定义
  val scn = scenario("My First Test")
    .exec(http("Get All Posts")
      .get("/posts")
      .check(status.is(200)))
    .pause(5) // 暂停5秒

  // 设置负载
  setUp(
    scn.inject(atOnceUsers(3))
  ).protocols(httpProtocol)
}
```

### 实验总结

通过本实验，你应该：
- 成功安装了Gatling环境
- 创建并运行了第一个测试脚本
- 理解了Gatling的基本结构和工作流程
- 能够查看和分析简单的测试报告

## 1.12 本章小结

本章介绍了Gatling的基本概念、特点和应用场景，详细讲解了如何安装和配置Gatling环境，并通过一个简单的示例演示了如何创建和运行第一个Gatling测试。通过本章的学习，读者应该对Gatling有了初步的认识，并能够搭建起基本的测试环境。

在下一章中，我们将深入探讨Gatling的基础概念和核心组件，包括模拟、场景、负载注入等关键概念，为编写更复杂的测试脚本打下基础。