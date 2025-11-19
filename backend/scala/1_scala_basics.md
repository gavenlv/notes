# 第1章：Scala基础入门

本章将带领零基础的开发者进入Scala编程世界，从最基础的概念开始，逐步掌握Scala的核心语法和编程范式。

## 📋 本章内容

### 1.1 Scala语言概述
- Scala的设计哲学
- JVM平台优势
- 函数式与面向对象融合

### 1.2 开发环境配置
- Scala安装与配置
- IDE选择与设置
- 第一个Scala程序

### 1.3 基础语法
- 变量与常量
- 数据类型系统
- 基本运算符

### 1.4 控制结构
- 条件语句
- 循环结构
- 模式匹配基础

### 1.5 函数定义
- 方法定义语法
- 函数作为一等公民
- 默认参数与命名参数

### 1.6 基础I/O操作
- 控制台输入输出
- 文件读写操作
- 异常处理基础

## 🎯 学习目标

完成本章后，你将能够：
- ✅ 配置Scala开发环境
- ✅ 编写简单的Scala程序
- ✅ 理解Scala的基本语法规则
- ✅ 使用控制结构处理逻辑
- ✅ 定义和使用基本函数
- ✅ 进行基础的I/O操作

## 🔧 环境要求

- Java 8或更高版本
- Scala 2.13.x
- sbt 1.8.x
- 推荐：IntelliJ IDEA + Scala插件

## 📝 详细内容

### 1.1 Scala语言概述

Scala是一种多范式编程语言，设计目标是"可扩展的语言"。它结合了面向对象编程和函数式编程的最佳特性。

**主要特点：**
- **静态类型系统**：编译时类型检查，减少运行时错误
- **类型推断**：编译器自动推断类型，减少代码冗余
- **函数式特性**：支持高阶函数、不可变数据、模式匹配
- **面向对象**：纯面向对象，所有值都是对象
- **JVM兼容**：完全兼容Java生态，可调用Java库

### 1.2 开发环境配置

#### 安装Scala
```bash
# 使用SDKMAN（推荐）
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"
sdk install scala 2.13.10
sdk install sbt 1.8.2

# 验证安装
scala -version
sbt sbtVersion
```

#### 第一个Scala程序
创建 `HelloWorld.scala`：
```scala
object HelloWorld {
  def main(args: Array[String]): Unit = {
    println("Hello, Scala!")
  }
}
```

编译运行：
```bash
scalac HelloWorld.scala
scala HelloWorld
```

### 1.3 基础语法

#### 变量与常量
```scala
// 不可变变量（推荐）
val name: String = "Scala"
val age = 25  // 类型推断

// 可变变量（谨慎使用）
var count: Int = 0
count = 1

// 惰性求值
lazy val expensiveValue: String = {
  println("计算中...")
  "计算结果"
}
```

#### 数据类型
Scala的数据类型系统基于Java，但更加丰富：

| 类型 | 描述 | 示例 |
|------|------|------|
| `Byte` | 8位有符号整数 | `val b: Byte = 127` |
| `Short` | 16位有符号整数 | `val s: Short = 32767` |
| `Int` | 32位有符号整数 | `val i: Int = 2147483647` |
| `Long` | 64位有符号整数 | `val l: Long = 9223372036854775807L` |
| `Float` | 32位浮点数 | `val f: Float = 3.14f` |
| `Double` | 64位浮点数 | `val d: Double = 3.1415926535` |
| `Char` | 16位Unicode字符 | `val c: Char = 'A'` |
| `Boolean` | 布尔值 | `val flag: Boolean = true` |
| `String` | 字符串 | `val str: String = "Hello"` |
| `Unit` | 无返回值 | `def f(): Unit = ()` |

#### 运算符
Scala支持所有Java运算符，并添加了一些新特性：

```scala
// 算术运算符
val sum = 1 + 2
val product = 3 * 4

// 比较运算符
val isEqual = 1 == 1  // true
val isGreater = 2 > 1 // true

// 逻辑运算符
val andResult = true && false  // false
val orResult = true || false   // true

// 位运算符
val bitAnd = 5 & 3  // 1
val bitOr = 5 | 3   // 7
```

### 1.4 控制结构

#### 条件语句
```scala
// if-else表达式（有返回值）
val result = if (x > 0) "正数" else "非正数"

// 多条件分支
val grade = if (score >= 90) "A"
else if (score >= 80) "B"
else if (score >= 70) "C"
else "D"
```

#### 循环结构
```scala
// while循环
var i = 0
while (i < 5) {
  println(i)
  i += 1
}

// for循环（推荐）
for (i <- 1 to 5) {
  println(i)
}

// 带条件的for循环
for (i <- 1 to 10 if i % 2 == 0) {
  println(s"偶数: $i")
}

// 多重循环
for (i <- 1 to 3; j <- 1 to 3) {
  println(s"($i, $j)")
}
```

#### 模式匹配基础
```scala
val x: Any = "hello"

x match {
  case 1 => println("数字1")
  case "hello" => println("字符串hello")
  case true => println("布尔true")
  case _ => println("其他")
}
```

### 1.5 函数定义

#### 基本函数定义
```scala
// 无参数函数
def greet(): String = "Hello, World!"

// 带参数函数
def add(a: Int, b: Int): Int = a + b

// 过程（无返回值）
def printMessage(msg: String): Unit = {
  println(msg)
}

// 多行函数体
def factorial(n: Int): Int = {
  if (n <= 1) 1
  else n * factorial(n - 1)
}
```

#### 默认参数和命名参数
```scala
def greet(name: String = "Guest", greeting: String = "Hello"): String = {
  s"$greeting, $name!"
}

// 使用默认参数
greet()  // "Hello, Guest!"

// 命名参数
greet(greeting = "Hi", name = "Alice")  // "Hi, Alice!"
```

#### 高阶函数基础
```scala
// 函数作为参数
def applyFunction(f: Int => Int, x: Int): Int = f(x)

// 匿名函数
val square = (x: Int) => x * x
val result = applyFunction(square, 5)  // 25

// 更简洁的写法
applyFunction(x => x * x, 5)
```

### 1.6 基础I/O操作

#### 控制台I/O
```scala
import scala.io.StdIn

// 输出
println("Hello, World!")
print("请输入你的名字: ")

// 输入
val name = StdIn.readLine()
println(s"你好, $name!")

// 读取数字
print("请输入年龄: ")
val age = StdIn.readInt()
println(s"年龄: $age")
```

#### 文件操作
```scala
import scala.io.Source
import java.io.{PrintWriter, File}

// 读取文件
val source = Source.fromFile("data.txt")
val lines = source.getLines().toList
source.close()

// 写入文件
val writer = new PrintWriter(new File("output.txt"))
writer.write("Hello, File!")
writer.close()

// 使用try-with-resources风格
import scala.util.Using

Using(Source.fromFile("data.txt")) { source =>
  source.getLines().foreach(println)
}
```

#### 异常处理
```scala
// 基本异常处理
def safeDivide(a: Int, b: Int): Int = {
  try {
    a / b
  } catch {
    case e: ArithmeticException => 
      println("除零错误")
      0
  } finally {
    println("计算完成")
  }
}

// 使用Option处理可能失败的操作
def divideOption(a: Int, b: Int): Option[Int] = {
  if (b != 0) Some(a / b) else None
}

// 使用Try处理异常
import scala.util.Try

def divideTry(a: Int, b: Int): Try[Int] = Try(a / b)
```

## 💻 实践练习

### 练习1：温度转换
编写一个函数，将摄氏温度转换为华氏温度。

### 练习2：斐波那契数列
实现一个函数，计算第n个斐波那契数。

### 练习3：字符串处理
编写函数统计字符串中字符出现的频率。

### 练习4：文件操作
读取一个文本文件，统计其中单词的数量。

## 🔍 深入理解

### 类型推断的工作原理
Scala编译器如何推断变量类型？

### val vs var
为什么推荐使用val而不是var？

### 表达式 vs 语句
Scala中几乎所有结构都是表达式，这意味着什么？

## 📚 扩展阅读

- [Scala语言规范](https://www.scala-lang.org/files/archive/spec/2.13/)
- [Scala API文档](https://www.scala-lang.org/api/2.13.10/)
- 《Programming in Scala》第1-3章

## 🚀 下一步

完成本章学习后，继续学习第2章：函数式编程基础，深入理解Scala的函数式特性。

---

**记住：实践是最好的学习方式！每个概念都要动手编写代码验证。**