# Flink 环境搭建详解 (Day 01) - 从零开始

## 1. 为什么需要学习 Flink？

在大数据时代，数据不再是静态的，而是像水流一样源源不断地产生。想象一下：
- 电商网站每秒都有成千上万的用户下单
- 社交媒体每秒都有海量的帖子、评论和点赞
- 物联网设备每秒都在上传传感器数据

传统的批处理系统（如 MapReduce）需要等所有数据都收集完毕后才能处理，这就像等河流干涸后再去数鱼一样，无法满足实时性需求。

Flink 就是为了解决这个问题而生的，它能够：
- **实时处理**：数据一产生就能立即处理
- **高吞吐**：每秒能处理数百万条数据
- **低延迟**：毫秒级的响应速度
- **精确一次**：即使系统出错也能保证数据不重复不丢失

## 2. 系统要求详解

### Java 环境的重要性

Flink 是用 Java 和 Scala 编写的，因此必须先安装 Java 环境。

#### 为什么推荐 Java 11？

Java 11 是一个长期支持版本（LTS），相比 Java 8：
- 性能更好
- 安全性更高
- 对现代硬件支持更好
- Flink 官方推荐使用

### 硬件要求说明

- **内存 4GB**：Flink 本身运行需要一定内存，加上操作系统和其他程序，4GB 是最低要求
- **磁盘空间 2GB**：Flink 安装包约 200MB，但运行时会产生日志、检查点等文件

## 3. 安装 Java 详细步骤

### Windows 平台安装 Java

#### 步骤 1：下载 JDK

1. 打开浏览器，访问 [Oracle JDK 下载页面](https://www.oracle.com/java/technologies/downloads/#java11-windows)
2. 找到 "Java SE Development Kit 11.x" 部分
3. 点击 "Windows x64" 下载按钮
4. 下载完成后你会得到一个类似 `jdk-11.x.x_windows-x64_bin.exe` 的文件

#### 步骤 2：安装 JDK

1. 双击下载的 `.exe` 文件
2. 点击 "下一步"
3. 选择安装路径（建议使用默认路径 `C:\Program Files\Java\jdk-11.x.x`）
4. 继续点击 "下一步" 直到安装完成

#### 步骤 3：配置环境变量

环境变量就像告诉计算机程序在哪里找到需要的文件。

1. 右键点击 "此电脑" 或 "我的电脑"
2. 选择 "属性"
3. 点击左侧 "高级系统设置"
4. 点击 "环境变量" 按钮
5. 在 "系统变量" 区域点击 "新建"
6. 变量名输入：`JAVA_HOME`
7. 变量值输入：JDK 的安装路径（如 `C:\Program Files\Java\jdk-11.0.16`）
8. 点击 "确定"
9. 在系统变量中找到 `Path`，选中后点击 "编辑"
10. 点击 "新建"，输入 `%JAVA_HOME%\bin`
11. 点击 "确定" 保存所有设置

#### 步骤 4：验证安装

1. 按下 `Win + R` 键，输入 `cmd`，按回车打开命令提示符
2. 输入命令：`java -version`
3. 如果看到类似以下输出，说明安装成功：
   ```
   java version "11.0.16" 2022-07-19 LTS
   Java(TM) SE Runtime Environment 18.9 (build 11.0.16+8-LTS-18)
   Java HotSpot(TM) 64-Bit Server VM 18.9 (build 11.0.16+8-LTS-18, mixed mode)
   ```

### Linux 平台安装 Java

#### Ubuntu/Debian 系统

```bash
# 更新软件包列表
sudo apt update

# 安装 OpenJDK 11
sudo apt install openjdk-11-jdk

# 验证安装
java -version
```

#### CentOS/RHEL 系统

```bash
# 安装 OpenJDK 11
sudo yum install java-11-openjdk-devel

# 或者使用 dnf（较新版本）
sudo dnf install java-11-openjdk-devel

# 验证安装
java -version
```

## 4. 下载和安装 Flink

### 下载 Flink

1. 打开浏览器，访问 [Flink 官方下载页面](https://flink.apache.org/downloads.html)
2. 找到 "Apache Flink 1.16.0 for Scala 2.12"（或最新稳定版本）
3. 点击链接下载 `flink-1.16.0-bin-scala_2.12.tgz` 文件

### Windows 平台安装 Flink

#### 步骤 1：解压文件

1. 找到下载的文件 `flink-1.16.0-bin-scala_2.12.tgz`
2. 右键点击选择 "解压到当前文件夹" 或使用解压软件
3. 得到 `flink-1.16.0` 文件夹
4. 将该文件夹移动到你想要安装的位置，如 `D:\flink-1.16.0`

#### 步骤 2：配置环境变量

1. 按照前面配置 JAVA_HOME 的方法，新建系统变量
2. 变量名输入：`FLINK_HOME`
3. 变量值输入：Flink 的安装路径（如 `D:\flink-1.16.0`）
4. 编辑系统变量 `Path`，添加 `%FLINK_HOME%\bin`

#### 步骤 3：启动 Flink 集群

Flink 集群就像一个工厂，里面有多个工人（TaskManager）协同工作。

1. 按下 `Win + R` 键，输入 `cmd`，按回车打开命令提示符
2. 输入命令：
   ```cmd
   cd %FLINK_HOME%
   bin\start-cluster.bat
   ```
3. 如果看到类似以下输出，说明启动成功：
   ```
   Starting cluster.
   Starting standalonesession daemon on host DESKTOP-XXXXXXX.
   Starting taskexecutor daemon on host DESKTOP-XXXXXXX.
   ```

### Linux 平台安装 Flink

#### 步骤 1：解压文件

```bash
# 解压文件
tar -xzf flink-1.16.0-bin-scala_2.12.tgz

# 移动到合适位置
sudo mv flink-1.16.0 /opt/flink
```

#### 步骤 2：配置环境变量

```bash
# 编辑用户配置文件
nano ~/.bashrc

# 在文件末尾添加以下内容
export FLINK_HOME=/opt/flink
export PATH=$PATH:$FLINK_HOME/bin

# 保存并退出（Ctrl+X，然后按 Y，最后按回车）

# 使配置生效
source ~/.bashrc
```

#### 步骤 3：启动 Flink 集群

```bash
# 启动集群
start-cluster.sh
```

## 5. 验证安装是否成功

### 访问 Web 界面

Flink 提供了一个可视化的管理界面：

1. 打开浏览器
2. 访问地址：[http://localhost:8081](http://localhost:8081)
3. 如果看到 Flink 的 Web 界面，说明安装成功

### 提交示例作业测试

Flink 安装包中包含了一些示例程序，我们可以运行它们来测试安装。

#### Windows 平台

```cmd
cd %FLINK_HOME%
bin\flink.bat run examples\streaming\WordCount.jar --input README.txt --output /tmp/wordcount-result.txt
```

#### Linux 平台

```bash
flink run $FLINK_HOME/examples/streaming/WordCount.jar --input $FLINK_HOME/README.txt --output /tmp/wordcount-result.txt
```

运行成功后，查看结果文件：
```bash
cat /tmp/wordcount-result.txt
```

你应该能看到类似这样的输出：
```
(a,1)
(Flink,2)
(is,2)
(program,1)
```

## 6. 配置 IDE 开发环境

为了编写 Flink 程序，我们需要一个合适的开发环境。

### 安装 IntelliJ IDEA

IntelliJ IDEA 是一个功能强大的 Java 集成开发环境：

1. 访问 [JetBrains 官网](https://www.jetbrains.com/idea/download/)
2. 下载 Community（免费版）或 Ultimate（付费版）
3. 安装程序并按照提示完成安装

### 配置 Scala 插件

Flink 使用 Scala 编写部分组件，需要安装 Scala 插件：

1. 打开 IntelliJ IDEA
2. 点击 "File" → "Settings"
3. 选择 "Plugins"
4. 搜索 "Scala"
5. 点击 "Install" 安装插件
6. 重启 IntelliJ IDEA

### 创建第一个 Flink 项目

#### 步骤 1：创建 Maven 项目

1. 在 IntelliJ IDEA 中点击 "File" → "New" → "Project"
2. 选择 "Maven"
3. 点击 "Next"
4. 填写项目信息：
   - GroupId: `com.example`
   - ArtifactId: `flink-tutorial`
5. 点击 "Finish"

#### 步骤 2：添加 Flink 依赖

打开 `pom.xml` 文件，替换为以下内容：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example</groupId>
    <artifactId>flink-tutorial</artifactId>
    <version>1.0-SNAPSHOT</version>

    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
        <flink.version>1.16.0</flink.version>
        <scala.binary.version>2.12</scala.binary.version>
    </properties>

    <dependencies>
        <!-- Flink 核心依赖 -->
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-java</artifactId>
            <version>${flink.version}</version>
        </dependency>
        
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-streaming-java</artifactId>
            <version>${flink.version}</version>
        </dependency>
        
        <!-- Flink 客户端依赖（本地运行需要） -->
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-clients</artifactId>
            <version>${flink.version}</version>
        </dependency>
        
        <!-- 日志依赖 -->
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-api</artifactId>
            <version>1.7.32</version>
        </dependency>
        
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-simple</artifactId>
            <version>1.7.32</version>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <!-- Java 编译器插件 -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.8.1</version>
                <configuration>
                    <source>11</source>
                    <target>11</target>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

#### 步骤 3：编写第一个 Flink 程序

1. 在 `src/main/java` 下创建包 `com.example.flink`
2. 在包中创建类 `FirstFlinkJob.java`

```java
package com.example.flink;

import org.apache.flink.api.common.functions.FlatMapFunction;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.util.Collector;

/**
 * 第一个 Flink 程序 - 实时词频统计
 */
public class FirstFlinkJob {
    public static void main(String[] args) throws Exception {
        // 1. 创建执行环境
        // StreamExecutionEnvironment 是 Flink 程序的入口点
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        
        // 2. 创建数据源
        // 从 socket 读取文本数据流
        DataStream<String> text = env.socketTextStream("localhost", 9999);
        
        // 3. 数据转换处理
        DataStream<Tuple2<String, Integer>> wordCounts = text
            // 将每一行文本分割成单词
            .flatMap(new Tokenizer())
            // 按单词分组
            .keyBy(value -> value.f0)
            // 统计每个单词出现的次数
            .sum(1);
        
        // 4. 输出结果
        wordCounts.print();
        
        // 5. 执行程序
        env.execute("First Flink Job");
    }
    
    /**
     * 分词器 - 将文本行分割成单词
     */
    public static class Tokenizer implements FlatMapFunction<String, Tuple2<String, Integer>> {
        @Override
        public void flatMap(String value, Collector<Tuple2<String, Integer>> out) {
            // 按空格分割文本行
            String[] tokens = value.toLowerCase().split("\\W+");
            
            // 输出每个单词，计数为1
            for (String token : tokens) {
                if (token.length() > 0) {
                    out.collect(new Tuple2<>(token, 1));
                }
            }
        }
    }
}
```

## 7. 测试第一个 Flink 程序

### 启动 Socket 服务器

为了测试程序，我们需要一个数据源。最简单的方法是使用 nc（netcat）工具：

#### Windows 平台

Windows 10/11 用户可以使用内置的 netcat：

```cmd
# 在新的命令提示符窗口中运行
nc -l -p 9999
```

如果没有 nc，可以下载 [Nmap](https://nmap.org/download.html)，它包含了 nc 工具。

#### Linux 平台

```bash
# 安装 netcat
sudo apt install netcat  # Ubuntu/Debian
sudo yum install nc      # CentOS/RHEL

# 启动监听
nc -l 9999
```

### 运行 Flink 程序

1. 在 IntelliJ IDEA 中右键点击 `FirstFlinkJob.java`
2. 选择 "Run 'FirstFlinkJob.main()'"
3. 程序会等待从 socket 接收数据

### 发送测试数据

在 nc 命令窗口中输入以下文本：

```
hello world
hello flink
flink is great
```

在 IntelliJ IDEA 的控制台中，你应该能看到类似输出：

```
(hello,1)
(world,1)
(hello,2)
(flink,1)
(flink,2)
(is,1)
(great,1)
```

## 8. 停止 Flink 集群

### Windows 平台

```cmd
cd %FLINK_HOME%
bin\stop-cluster.bat
```

### Linux 平台

```bash
stop-cluster.sh
```

## 9. 常见问题及解决方案

### 问题 1：端口被占用

**现象**：启动 Flink 时提示端口 8081 被占用

**解决方案**：
1. 修改配置文件 `conf/flink-conf.yaml`
2. 添加或修改行：`rest.port: 8082`
3. 重启 Flink 集群

### 问题 2：内存不足

**现象**：Flink 启动失败或运行缓慢

**解决方案**：
1. 修改配置文件 `conf/flink-conf.yaml`
2. 调整以下参数：
   ```yaml
   jobmanager.memory.process.size: 2g
   taskmanager.memory.process.size: 4g
   ```

### 问题 3：Java 版本不兼容

**现象**：运行时出现版本不兼容错误

**解决方案**：
1. 检查 Java 版本：`java -version`
2. 确保使用 Java 8 或 Java 11
3. 重新配置 JAVA_HOME 环境变量

## 10. 本章小结

通过本章的学习，你应该已经：
1. 理解了为什么需要 Flink 以及它的核心优势
2. 成功安装并配置了 Java 环境
3. 成功安装并启动了 Flink 集群
4. 验证了 Flink 安装的正确性
5. 配置了开发环境并编写了第一个 Flink 程序
6. 成功运行了 Flink 程序并看到了实时处理效果

## 11. 下一步学习

成功完成本章后，建议继续学习：
- [Flink 基础概念详解](../day02-introduction/basic-concepts.md) - 深入理解 Flink 的核心概念
- [Flink 基础操作](../day03-basic-operations/basic-operations.md) - 学习 Flink 的基本数据处理操作

## 12. 参考资源

- [Apache Flink 官方文档](https://flink.apache.org/docs/stable/)
- [Oracle JDK 下载](https://www.oracle.com/java/technologies/downloads/#java11-windows)
- [OpenJDK 下载](https://adoptium.net/)
