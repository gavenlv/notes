# 第1章 Scala简介与环境搭建

## 目录
- [1.1 Scala历史与特点](#11-scala历史与特点)
- [1.2 为什么选择Scala](#12-为什么选择scala)
- [1.3 Scala应用领域](#13-scala应用领域)
- [1.4 安装JDK](#14-安装jdk)
- [1.5 安装Scala](#15-安装scala)
- [1.6 配置IDE](#16-配置ide)
- [1.7 使用sbt构建项目](#17-使用sbt构建项目)
- [1.8 第一个Scala程序](#18-第一个scala程序)
- [1.9 Scala REPL](#19-scala-repl)
- [1.10 常见问题与解决方案](#110-常见问题与解决方案)

## 1.1 Scala历史与特点

### Scala的历史

Scala（Scalable Language）是由瑞士洛桑联邦理工学院（EPFL）的Martin Odersky教授于2001年开始设计，并于2003年首次公开发布。Martin Odersky也是Java泛型的设计者和javac编译器的作者，这使得Scala与Java有着深厚的渊源。

Scala的发展历程：
- **2001年** - Martin Odersky开始设计Scala
- **2003年** - Scala首次公开发布
- **2006年** - Scala 2.0发布
- **2011年** - Scala 2.9引入并行集合
- **2016年** - Scala 2.12发布，完全兼容Java 8
- **2021年** - Scala 3.0发布，引入了多项重大改进

### Scala的特点

Scala是一门融合了面向对象编程（OOP）和函数式编程（FP）思想的多范式编程语言，具有以下特点：

#### 1. 多范式编程
```scala
// 面向对象风格
class Person(name: String, age: Int) {
  def greet(): String = s"Hello, I'm $name and I'm $age years old"
}

val person = new Person("Alice", 30)
println(person.greet())

// 函数式风格
val numbers = List(1, 2, 3, 4, 5)
val doubled = numbers.map(_ * 2).filter(_ > 5)
```

#### 2. 静态类型
Scala拥有强大的静态类型系统，可以在编译时捕获大量错误：

```scala
// 类型推断
val name = "Scala"  // 自动推断为String类型
val age = 20        // 自动推断为Int类型

// 显式类型声明
val list: List[Int] = List(1, 2, 3)
```

#### 3. 简洁性
Scala可以用更少的代码表达相同的功能：

```java
// Java版本
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
    
    public static void main(String[] args) {
        Calculator calc = new Calculator();
        System.out.println(calc.add(5, 3));
    }
}

// Scala版本
class Calculator {
  def add(a: Int, b: Int): Int = a + b
}

object Calculator {
  def add(a: Int, b: Int): Int = a + b
  def main(args: Array[String]): Unit = println(add(5, 3))
}
```

#### 4. 可扩展性
Scala的名称意为"可扩展的语言"，允许开发者添加新的控制结构和数据类型：

```scala
// 自定义控制结构
def repeat(times: Int)(block: => Unit): Unit = {
  for (_ <- 1 to times) block
}

// 使用自定义结构
repeat(3) {
  println("Scala!")
}

// 扩展现有类型
implicit class StringEnhancements(s: String) {
  def shout: String = s.toUpperCase + "!"
}

println("Scala".shout) // 输出: SCALA!
```

#### 5. 与Java的互操作性
Scala可以无缝使用Java的所有库和框架：

```scala
import java.util.{ArrayList, HashMap}
import java.time.LocalDate

// 使用Java集合
val javaList = new ArrayList[String]()
javaList.add("Scala")
javaList.add("Java")

// 使用Java时间API
val today = LocalDate.now()
println(s"Today is $today")
```

## 1.2 为什么选择Scala

### 1. 表达力强
Scala提供了丰富的语法特性，可以用更简洁的代码表达复杂的思想：

```java
// Java版本
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);
List<Integer> result = new ArrayList<>();
for (Integer n : numbers) {
    if (n % 2 == 0) {
        result.add(n * 2);
    }
}

// Scala版本
val numbers = List(1, 2, 3, 4, 5)
val result = numbers.filter(_ % 2 == 0).map(_ * 2)
```

### 2. 适合大数据处理
Scala是Apache Spark、Apache Kafka等大数据框架的首选语言：

```scala
// Spark Scala API示例
val spark = SparkSession.builder()
  .appName("WordCount")
  .master("local[*]")
  .getOrCreate()

import spark.implicits._

val textFile = spark.read.textFile("README.md")
val wordCounts = textFile.flatMap(line => line.split(" "))
  .groupByKey(identity)
  .count()

wordCounts.show()
```

### 3. 函数式编程支持
Scala提供强大的函数式编程特性，使代码更加模块化和可测试：

```scala
// 不可变数据结构
case class User(id: Long, name: String, email: String)

// 纯函数
def validateEmail(email: String): Boolean = {
  val emailRegex = """^[a-zA-Z0-9\.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$""".r
  emailRegex.findFirstMatchIn(email).isDefined
}

// 函数组合
def createUser(id: Long, name: String, email: String): Option[User] = {
  if (validateEmail(email)) Some(User(id, name, email))
  else None
}
```

### 4. 强大的并发支持
Scala通过Actor模型和Future/Promise提供出色的并发编程能力：

```scala
import scala.concurrent.Future
import scala.concurrent.ExecutionContext.Implicits.global

// 异步计算
val futureResult: Future[Int] = Future {
  // 长时间运行的计算
  Thread.sleep(1000)
  42
}

// 组合多个Future
val combinedFuture = for {
  a <- Future { computeA() }
  b <- Future { computeB() }
} yield a + b
```

## 1.3 Scala应用领域

### 1. 大数据处理
- **Apache Spark** - 分布式计算框架
- **Apache Kafka** - 分布式流处理平台
- **Apache Flink** - 流处理和批处理框架

### 2. Web后端开发
- **Play Framework** - 高性能Web框架
- **Akka HTTP** - 基于Actor模型的HTTP工具包
- **http4s** - 纯函数式HTTP服务

### 3. 数据科学
- **Spark MLlib** - 机器学习库
- **Breeze** - 数值计算库
- **ScalaNLP** - 自然语言处理

### 4. 微服务架构
- **Akka** - 用于构建并发和分布式应用的工具包
- **Lagom** - 微服务框架
- **Finagle** - Twitter开发的RPC系统

### 5. 企业级应用
- 许多金融、电信公司使用Scala构建高性能系统
- 适合需要高并发、高可用的系统

## 1.4 安装JDK

Scala运行在JVM上，首先需要安装Java Development Kit（JDK）。

### 检查Java版本
```bash
# Windows
java -version

# macOS/Linux
java -version
javac -version
```

### 安装JDK

#### Windows
1. 访问[Oracle JDK官网](https://www.oracle.com/java/technologies/downloads/)或[Adoptium](https://adoptium.net/)
2. 下载适合您系统的JDK版本（推荐JDK 11或更高版本）
3. 运行安装程序，按照向导完成安装
4. 配置环境变量：
   - `JAVA_HOME`: 指向JDK安装目录
   - `Path`: 添加 `%JAVA_HOME%\bin`

#### macOS
```bash
# 使用Homebrew安装
brew install openjdk@11

# 设置JAVA_HOME
echo 'export JAVA_HOME=/usr/local/opt/openjdk@11' >> ~/.zshrc
source ~/.zshrc
```

#### Linux (Ubuntu/Debian)
```bash
# 更新包列表
sudo apt update

# 安装OpenJDK
sudo apt install openjdk-11-jdk

# 验证安装
java -version
```

### 验证JDK安装
```bash
java -version
javac -version
echo $JAVA_HOME
```

## 1.5 安装Scala

### 使用Coursier安装（推荐）

Coursier是Scala生态系统的现代安装器和管理器：

```bash
# Windows (PowerShell)
iwr -useb https://git.io/coursier-cli-windows.ps1 | iex
coursier install scala

# macOS/Linux
curl -fL https://git.io/coursier-cli-linux | bash
./coursier install scala
```

### 使用SDKMAN安装（Linux/macOS）

```bash
# 安装SDKMAN
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"

# 安装Scala
sdk install scala
```

### 验证Scala安装
```bash
scala -version
```

## 1.6 配置IDE

### IntelliJ IDEA
1. 下载[IntelliJ IDEA](https://www.jetbrains.com/idea/)
2. 安装Scala插件：
   - 打开File → Settings → Plugins
   - 搜索"Scala"并安装
   - 重启IDE
3. 创建新的Scala项目：
   - File → New → Project
   - 选择Scala项目类型
   - 选择Scala SDK（如果没有，会提示下载）

### VS Code
1. 下载[VS Code](https://code.visualstudio.com/)
2. 安装Scala扩展（Metals）：
   - 打开扩展面板（Ctrl+Shift+X）
   - 搜索"Metals"并安装
   - 按提示安装Java和Scala

### Eclipse
1. 下载[Eclipse](https://www.eclipse.org/downloads/)
2. 安装Scala IDE插件：
   - Help → Eclipse Marketplace
   - 搜索"Scala IDE"并安装

## 1.7 使用sbt构建项目

sbt（Simple Build Tool）是Scala的标准构建工具。

### 安装sbt

#### Windows
```powershell
# 使用sbt官方安装脚本
iwr -useb https://raw.githubusercontent.com/coursier/launchers/master/cs-x86_64-pc-win32.zip -OutFile cs.zip
Expand-Archive cs.zip -DestinationPath .
.\cs setup --yes
.\cs install sbt
```

#### macOS/Linux
```bash
# 使用Coursier安装
curl -fL https://github.com/coursier/launchers/raw/master/cs-x86_64-pc-linux.gz | gzip -d > cs && chmod +x cs
./cs setup --yes
./cs install sbt
```

### 创建sbt项目

#### 项目结构
```
my-scala-project/
├── build.sbt          # 项目构建配置
├── project/            # 项目配置文件
│   ├── build.properties
│   └── plugins.sbt
├── src/
│   ├── main/
│   │   └── scala/      # 主要源代码
│   └── test/
│       └── scala/      # 测试代码
└── target/             # 编译输出
```

#### 创建项目
```bash
mkdir my-scala-project
cd my-scala-project
```

创建`build.sbt`：
```scala
ThisBuild / scalaVersion := "3.3.0"
ThisBuild / version := "0.1.0-SNAPSHOT"
ThisBuild / organization := "com.example"

lazy val root = (project in file("."))
  .settings(
    name := "MyScalaProject",
    libraryDependencies += "org.scalatest" %% "scalatest" % "3.2.15" % Test
  )
```

创建`project/build.properties`：
```properties
sbt.version=1.9.0
```

创建`project/plugins.sbt`：
```scala
addSbtPlugin("com.github.sbt" % "sbt-javacv" % "1.0.9")
```

#### 常用sbt命令
```bash
# 编译项目
sbt compile

# 运行项目
sbt run

# 运行测试
sbt test

# 打包项目
sbt package

# 进入交互模式
sbt

# 清理编译文件
sbt clean

# 更新依赖
sbt update

# 查看项目设置
sbt settings
```

#### 添加依赖
在`build.sbt`中添加：
```scala
libraryDependencies ++= Seq(
  "org.typelevel" %% "cats-core" % "2.9.0",
  "org.apache.spark" %% "spark-core" % "3.4.0",
  "com.typesafe.akka" %% "akka-actor-typed" % "2.8.0",
  "org.scalatest" %% "scalatest" % "3.2.15" % Test
)
```

### 常用sbt插件
```scala
// project/plugins.sbt
addSbtPlugin("com.eed3si9n" % "sbt-assembly" % "1.2.0")        // 打成fat JAR
addSbtPlugin("org.scoverage" % "sbt-scoverage" % "2.0.6")     // 代码覆盖率
addSbtPlugin("com.github.sbt" % "sbt-jacoco" % "3.4.0")        // 测试覆盖率
addSbtPlugin("org.scalameta" % "sbt-scalafmt" % "2.5.0")       // 代码格式化
addSbtPlugin("com.timushev.sbt" % "sbt-updates" % "0.6.3")     // 依赖更新检查
```

## 1.8 第一个Scala程序

### Hello World示例
创建文件`HelloWorld.scala`：
```scala
object HelloWorld {
  def main(args: Array[String]): Unit = {
    println("Hello, Scala World!")
  }
}
```

### 编译和运行
```bash
# 编译
scalac HelloWorld.scala

# 运行
scala HelloWorld

# 输出: Hello, Scala World!
```

### 使用sbt运行
1. 创建项目结构：
```
hello-world/
├── build.sbt
└── src/
    └── main/
        └── scala/
            └── HelloWorld.scala
```

2. `HelloWorld.scala`内容：
```scala
object HelloWorld {
  def main(args: Array[String]): Unit = {
    println("Hello, Scala World!")
    println("Program arguments: " + args.mkString(", "))
  }
}
```

3. `build.sbt`内容：
```scala
ThisBuild / scalaVersion := "3.3.0"
lazy val root = (project in file("."))
  .settings(
    name := "HelloWorld"
  )
```

4. 运行项目：
```bash
sbt run
```

## 1.9 Scala REPL

REPL（Read-Eval-Print Loop）是Scala的交互式解释器，非常适合学习和小实验。

### 启动REPL
```bash
# 启动Scala REPL
scala

# 或使用sbt
sbt console
```

### REPL基本使用
```scala
scala> // 定义变量
scala> val name = "Scala"
val name: String = Scala

scala> val version = 3.0
val version: Double = 3.0

scala> // 表达式求值
scala> 1 + 2 * 3
val res0: Int = 7

scala> // 函数定义
scala> def add(a: Int, b: Int): Int = a + b
def add(a: Int, b: Int): Int

scala> add(5, 3)
val res1: Int = 8

scala> // 列表操作
scala> List(1, 2, 3, 4, 5)
val res2: List[Int] = List(1, 2, 3, 4, 5)

scala> res2.filter(_ % 2 == 0).map(_ * 2)
val res3: List[Int] = List(4, 8)
```

### REPL高级功能
```scala
// 查看类型
scala> :type List(1, 2, 3)
List[Int]

// 导入包
scala> import scala.collection.mutable._
import scala.collection.mutable._

// 查看导入的包
scala> :imports
  import scala.collection.mutable._

// 加载外部文件
scala> :load MyScript.scala

// 查看历史命令
scala> :history

// 清空REPL
scala> :reset

// 退出REPL
scala> :quit
```

## 1.10 常见问题与解决方案

### 1. CLASSPATH问题
**问题**：运行Scala程序时出现"NoClassDefFoundError"

**解决方案**：
```bash
# 明确指定classpath
scalac -cp ".:lib/*" MyClass.scala
scala -cp ".:lib/*" MyClass

# Windows下使用分号
scalac -cp ".;lib/*" MyClass.scala
scala -cp ".;lib/*" MyClass
```

### 2. 内存不足
**问题**：编译或运行大型项目时内存溢出

**解决方案**：
```bash
# 增加JVM堆内存
export SBT_OPTS="-Xmx2G -XX:MaxPermSize=512M"

# 或在sbt中设置
scala> set javaOptions += "-Xmx2G"
```

### 3. 版本不兼容
**问题**：Scala版本与依赖库不兼容

**解决方案**：
```scala
// 在build.sbt中明确指定版本
scalaVersion := "2.13.10"

// 使用%%确保库版本与Scala版本匹配
libraryDependencies += "org.typelevel" %% "cats-core" % "2.9.0"
```

### 4. sbt下载依赖慢
**问题**：sbt下载依赖速度慢

**解决方案**：
```scala
// 在project/plugins.sbt中添加国内镜像
resolvers += Resolver.mavenLocal

// 在build.sbt中添加
resolvers ++= Seq(
  "Aliyun Maven Repository" at "https://maven.aliyun.com/repository/public",
  "Typesafe Repository" at "https://repo.typesafe.com/typesafe/releases/"
)
```

### 5. 在IDE中无法导入项目
**问题**：IDE无法识别sbt项目

**解决方案**：
```bash
# 重新生成项目文件
sbt gen-idea
# 或
sbt eclipse
```

### 6. Scala 2与Scala 3不兼容
**问题**：Scala 3的语法与Scala 2不完全兼容

**解决方案**：
```scala
// 在build.sbt中设置编译器选项
scalacOptions ++= Seq(
  "-source:3.0-migration"
)
```

### 7. 运行时找不到main方法
**问题**：编译成功但运行时报找不到main方法

**解决方案**：
1. 确保main方法签名正确：`def main(args: Array[String]): Unit = { ... }`
2. 或使用App特质：`object MyApp extends App { println("Hello") }`
3. 检查类名与文件名是否匹配

### 8. 编码问题
**问题**：Scala文件中有中文注释导致编译错误

**解决方案**：
```bash
# 指定编码
scalac -encoding UTF-8 MyClass.scala

# 或在build.sbt中设置
scalacOptions += "-encoding UTF-8"
```

## 总结

本章介绍了Scala的历史、特点和应用领域，详细讲解了如何搭建Scala开发环境，包括安装JDK、Scala编译器、IDE和sbt构建工具。通过编写简单的Hello World程序，您已经迈出了Scala编程的第一步。下一章我们将深入学习Scala的基础语法。