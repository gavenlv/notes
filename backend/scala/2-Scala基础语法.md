# 第2章 Scala基础语法

## 目录
- [2.1 值与变量](#21-值与变量)
- [2.2 数据类型](#22-数据类型)
- [2.3 字符串操作](#23-字符串操作)
- [2.4 操作符](#24-操作符)
- [2.5 控制结构](#25-控制结构)
- [2.6 循环结构](#26-循环结构)
- [2.7 函数基础](#27-函数基础)
- [2.8 数组与元组](#28-数组与元组)
- [2.9 输入与输出](#29-输入与输出)
- [2.10 代码风格与最佳实践](#210-代码风格与最佳实践)

## 2.1 值与变量

### val和var的区别

在Scala中，有两种方式定义变量：`val`（不可变）和`var`（可变）。

```scala
// val定义不可变变量（类似于Java的final）
val name: String = "Scala"
// name = "New Value"  // 编译错误：val不可重新赋值

// var定义可变变量
var age: Int = 25
age = 26  // 允许重新赋值
```

### 类型推断

Scala具有强大的类型推断能力，可以省略类型声明：

```scala
// 显式类型声明
val x: Int = 10
val y: String = "Hello"

// 类型推断
val x = 10  // 自动推断为Int
val y = "Hello"  // 自动推断为String
val z = 3.14  // 自动推断为Double
```

### 最佳实践

- 优先使用`val`而不是`var`，这有助于编写更安全、更函数式的代码
- 当变量逻辑上不会改变时，使用`val`
- 只在必要时使用`var`，例如计数器或累积器

## 2.2 数据类型

### 基本数据类型

Scala没有Java中的基本数据类型（如int、double等），所有类型都是对象：

```scala
// 数值类型
val byteValue: Byte = 127        // 8位有符号整数
val shortValue: Short = 32767   // 16位有符号整数
val intValue: Int = 2147483647  // 32位有符号整数
val longValue: Long = 9223372036854775807L  // 64位有符号整数
val floatValue: Float = 3.14f   // 32位浮点数
val doubleValue: Double = 3.141592653589793  // 64位浮点数

// 字符类型
val charValue: Char = 'A'        // 16位Unicode字符

// 布尔类型
val boolValue: Boolean = true    // true或false
```

### 字符串字面量

Scala支持多种字符串字面量形式：

```scala
// 普通字符串
val s1 = "Hello, Scala"

// 多行字符串（使用三个引号）
val s2 = """This is a
multi-line
string in Scala"""

// 多行字符串去除前导空格（使用stripMargin）
val s3 = 
  """|First line
     |Second line
     |Third line""".stripMargin

// 插值字符串（s插值器）
val name = "Scala"
val version = 3.0
val s4 = s"The language is $name, version $version"

// 表达式插值
val x = 10
val y = 20
val s5 = s"The sum of $x and $y is ${x + y}"

// f插值器（类似printf）
val height = 1.78
val s6 = f"Height: $height%.2f meters"

// 原始字符串（raw插值器）
val path = raw"C:\Users\Admin\Documents"
```

## 2.3 字符串操作

### 常用字符串方法

```scala
val str = "Hello, Scala Programming"

// 获取长度
val length = str.length

// 转换大小写
val upper = str.toUpperCase
val lower = str.toLowerCase

// 查找和检查
val containsScala = str.contains("Scala")
val startsWith = str.startsWith("Hello")
val endsWith = str.endsWith("Programming")

// 提取子串
val substring = str.substring(7, 12)  // 提取"Scala"

// 分割字符串
val words = str.split(" ")  // 返回Array[String]

// 替换
val replaced = str.replace("Scala", "Java")

// 去除首尾空格
val trimmed = "  hello  ".trim

// 反转字符串
val reversed = "hello".reverse
```

### 正则表达式操作

```scala
import scala.util.matching.Regex

// 定义正则表达式
val pattern: Regex = """\d{3}-\d{2}-\d{4}""".r

// 查找第一个匹配
val text = "SSN: 123-45-6789, Another: 987-65-4321"
val firstMatch = pattern.findFirstIn(text)

// 查找所有匹配
val allMatches = pattern.findAllIn(text).toList

// 替换匹配
val replaced = pattern.replaceAllIn(text, "XXX-XX-XXXX")

// 提取组
val datePattern = """(\d{4})-(\d{2})-(\d{2})""".r
val date = "2023-12-25"
val datePattern(year, month, day) = date  // 解构匹配
```

## 2.4 操作符

### 算术操作符

```scala
val a = 10
val b = 3

// 基本算术操作
val sum = a + b          // 13
val difference = a - b   // 7
val product = a * b      // 30
val quotient = a / b     // 3 (整数除法)
val remainder = a % b    // 1 (取模)
```

### 关系操作符

```scala
val x = 5
val y = 10

// 比较操作
val equal = x == y       // false
val notEqual = x != y    // true
val greater = x > y      // false
val less = x < y         // true
val greaterEqual = x >= y // false
val lessEqual = x <= y   // true
```

### 逻辑操作符

```scala
val a = true
val b = false

// 逻辑操作
val and = a && b         // false
val or = a || b          // true
val not = !a             // false
```

### 位操作符

```scala
val x = 6  // 二进制: 110
val y = 3  // 二进制: 011

// 位操作
val bitwiseAnd = x & y   // 2 (二进制: 010)
val bitwiseOr = x | y    // 7 (二进制: 111)
val bitwiseXor = x ^ y   // 5 (二进制: 101)
val leftShift = x << 1   // 12 (二进制: 1100)
val rightShift = x >> 1  // 3 (二进制: 011)
val bitwiseNot = ~x      // -7 (二进制补码)
```

### 操作符重载

Scala允许自定义操作符：

```scala
class Counter(var value: Int = 0) {
  // 自定义增量操作符
  def ++ : Counter = {
    value += 1
    this
  }
  
  // 自定义减量操作符
  def -- : Counter = {
    value -= 1
    this
  }
  
  // 自定义加法
  def +(amount: Int): Counter = {
    value += amount
    this
  }
  
  override def toString: String = s"Counter($value)"
}

val counter = new Counter()
counter.++  // 调用++方法
counter + 5 // 调用+方法
```

## 2.5 控制结构

### if-else表达式

Scala的if-else是表达式，可以返回值：

```scala
val age = 18

// 简单if
if (age >= 18) {
  println("Adult")
}

// if-else
if (age >= 18) {
  println("Adult")
} else {
  println("Minor")
}

// 作为表达式使用
val message = if (age >= 18) "Adult" else "Minor"
println(message)

// 多分支if-else
val grade = 85
val category = if (grade >= 90) "A" 
               else if (grade >= 80) "B"
               else if (grade >= 70) "C"
               else if (grade >= 60) "D"
               else "F"

println(s"Grade: $category")
```

### match表达式（模式匹配）

Scala的match表达式比Java的switch更强大：

```scala
val day = 3

// 基本match
val dayName = day match {
  case 1 => "Monday"
  case 2 => "Tuesday"
  case 3 => "Wednesday"
  case 4 => "Thursday"
  case 5 => "Friday"
  case 6 => "Saturday"
  case 7 => "Sunday"
  case _ => "Unknown day"  // 默认分支，类似于default
}

// 多种情况匹配
val month = 2
val season = month match {
  case 12 | 1 | 2 => "Winter"
  case 3 | 4 | 5 => "Spring"
  case 6 | 7 | 8 => "Summer"
  case 9 | 10 | 11 => "Fall"
  case _ => "Unknown"
}

// 模式匹配带条件（守卫）
val age = 20
val category = age match {
  case x if x < 0 => "Invalid age"
  case x if x < 13 => "Child"
  case x if x < 20 => "Teenager"
  case x if x < 65 => "Adult"
  case _ => "Senior"
}

// 类型匹配
val value: Any = "Hello"
val description = value match {
  case s: String => s"It's a string of length ${s.length}"
  case i: Int => s"It's an integer: $i"
  case d: Double => s"It's a double: $d"
  case list: List[_] => s"It's a list with ${list.size} elements"
  case _ => "Unknown type"
}
```

## 2.6 循环结构

### while循环

```scala
// while循环
var i = 0
while (i < 5) {
  println(s"i = $i")
  i += 1
}

// do-while循环
var j = 0
do {
  println(s"j = $j")
  j += 1
} while (j < 5)
```

### for循环（for comprehension）

Scala的for循环比Java的更强大，称为for comprehension：

```scala
// 基本for循环
for (i <- 1 to 5) {
  println(s"i = $i")
}

// 使用until（不包含上限）
for (i <- 1 until 5) {
  println(s"i = $i")  // 输出1, 2, 3, 4
}

// 遍历集合
val fruits = List("apple", "banana", "orange")
for (fruit <- fruits) {
  println(s"Fruit: $fruit")
}

// 多重循环
for (i <- 1 to 3; j <- 1 to 3) {
  println(s"($i, $j)")
}

// 带条件的循环
for (i <- 1 to 10 if i % 2 == 0) {
  println(s"Even number: $i")
}

// for comprehension作为表达式
val numbers = 1 to 10
val doubled = for (i <- numbers) yield i * 2
println(doubled)  // Vector(2, 4, 6, 8, 10, 12, 14, 16, 18, 20)

// 复杂的for comprehension
val result = for {
  i <- 1 to 5 if i % 2 == 0
  j <- 1 to 3 if j > 1
  if i * j < 10
} yield (i, j, i * j)
```

### break和continue（没有内置支持）

Scala没有Java的break和continue关键字，但可以通过其他方式实现：

```scala
// 使用标志变量模拟break
var found = false
for (i <- 1 to 10 if !found) {
  if (i == 5) {
    found = true
    println("Found 5, breaking")
  } else {
    println(i)
  }
}

// 使用函数式方式（推荐）
def processUntil[T](items: Seq[T])(predicate: T => Boolean)(process: T => Unit): Unit = {
  for (item <- items) {
    if (predicate(item)) return
    process(item)
  }
}

processUntil(1 to 10)(_ == 5)(println)

// 使用递归实现break-like行为
def processRecursively(list: List[Int]): Unit = list match {
  case Nil => // 空列表，结束
  case 5 :: _ => println("Found 5, breaking") // break
  case head :: tail =>
    println(head)
    processRecursively(tail)
}

processRecursively((1 to 10).toList)
```

## 2.7 函数基础

### 函数定义

```scala
// 基本函数定义
def add(a: Int, b: Int): Int = {
  return a + b
}

// 简化写法（省略return，最后表达式作为返回值）
def subtract(a: Int, b: Int): Int = {
  a - b
}

// 更简化的写法（单行函数）
def multiply(a: Int, b: Int): Int = a * b

// 无参函数
def greet(): String = "Hello, Scala!"

// 无返回值函数（Unit类型，类似于Java的void）
def printMessage(msg: String): Unit = {
  println(msg)
}

// 无参无返回值函数
def sayHello(): Unit = println("Hello!")

// 无返回值可以省略Unit和=
def printMessage2(msg: String) {
  println(msg)
}
```

### 函数字面量和函数值

```scala
// 函数字面量（匿名函数）
val add = (a: Int, b: Int) => a + b
println(add(5, 3))  // 8

// 更简洁的写法（参数类型推断）
val numbers = List(1, 2, 3, 4, 5)
val doubled = numbers.map(x => x * 2)  // List(2, 4, 6, 8, 10)

// 使用下划线作为占位符（当参数只使用一次时）
val doubled2 = numbers.map(_ * 2)  // List(2, 4, 6, 8, 10)

// 多参数函数
val sum = (a: Int, b: Int, c: Int) => a + b + c
println(sum(1, 2, 3))  // 6
```

### 函数作为参数和返回值

```scala
// 接受函数作为参数的高阶函数
def operateOnNumbers(a: Int, b: Int, operation: (Int, Int) => Int): Int = {
  operation(a, b)
}

val sum = operateOnNumbers(5, 3, (x, y) => x + y)  // 8
val product = operateOnNumbers(5, 3, (x, y) => x * y)  // 15

// 函数作为返回值
def createMultiplier(factor: Int): Int => Int = {
  (x: Int) => x * factor
}

val double = createMultiplier(2)
val triple = createMultiplier(3)

println(double(5))  // 10
println(triple(5))  // 15
```

### 柯里化（Currying）

```scala
// 柯里化函数：将接受多个参数的函数转换为一系列接受单个参数的函数
def add(a: Int)(b: Int): Int = a + b

// 调用柯里化函数
val result = add(5)(3)  // 8

// 部分应用
val add5 = add(5) _  // 创建一个新函数，固定第一个参数为5
val result2 = add5(3)  // 8

// 普通函数转换为柯里化函数
def add3(a: Int, b: Int, c: Int): Int = a + b + c
val curriedAdd3 = (add3 _).curried

val step1 = curriedAdd3(1)  // 返回一个函数
val step2 = step1(2)        // 返回另一个函数
val result3 = step2(3)      // 6

// 部分应用普通函数
val add10 = add3(10, _: Int, _: Int)  // 固定第一个参数
val result4 = add10(20, 30)  // 60
```

### 可变参数函数

```scala
// 可变参数函数
def sumAll(numbers: Int*): Int = {
  numbers.sum
}

// 调用可变参数函数
val total1 = sumAll(1, 2, 3)        // 6
val total2 = sumAll(1, 2, 3, 4, 5)  // 15

// 传递序列作为参数
val nums = List(1, 2, 3, 4, 5)
val total3 = sumAll(nums: _*)       // 15

// 可变参数函数示例
def printAll(items: Any*): Unit = {
  items.foreach(println)
}

printAll("Hello", 42, true, List(1, 2, 3))
```

## 2.8 数组与元组

### 数组

Scala中的数组是可变的、固定大小的集合：

```scala
// 创建数组
val array1 = new Array[Int](5)           // 长度为5的整数数组，初始化为0
val array2 = Array(1, 2, 3, 4, 5)       // 使用初始化值创建数组
val array3 = Array.fill(5)(0)           // 填充5个0

// 访问和修改元素
array2(0) = 10                          // 修改第一个元素
val first = array2(0)                    // 读取第一个元素

// 数组操作
val array = Array(1, 2, 3, 4, 5)
val length = array.length                // 数组长度
val contains = array.contains(3)        // 检查是否包含元素
val indexOf = array.indexOf(3)           // 查找元素索引

// 数组转换（返回新数组）
val reversed = array.reverse
val sorted = array.sorted
val distinct = array.distinct

// 数组过滤和映射
val filtered = array.filter(_ % 2 == 0)  // Array(2, 4)
val mapped = array.map(_ * 2)            // Array(2, 4, 6, 8, 10)

// 数组连接
val array4 = Array(1, 2, 3)
val array5 = Array(4, 5, 6)
val combined = array4 ++ array5          // Array(1, 2, 3, 4, 5, 6)
```

### 元组

元组是不可变的、可以包含不同类型元素的集合：

```scala
// 创建元组
val tuple1 = (1, "hello", true)           // 元组3
val tuple2 = Tuple2("key", "value")       // 显式创建元组2

// 访问元组元素
val first = tuple1._1                    // 1
val second = tuple1._2                   // "hello"
val third = tuple1._3                     // true

// 元组解构
val (num, str, bool) = tuple1
println(num, str, bool)                  // 1, hello, true

// 元组模式匹配
val result = tuple1 match {
  case (1, s, b) => s"First element is 1, second is $s"
  case (n, s, b) => s"First element is $n, second is $s"
}

// 使用元组作为函数返回值（返回多个值）
def divideAndRemainder(dividend: Int, divisor: Int): (Int, Int) = {
  (dividend / divisor, dividend % divisor)
}

val (quotient, remainder) = divideAndRemainder(10, 3)
println(s"10 divided by 3 is $quotient with remainder $remainder")

// 元组比较
val tuple3 = (1, 2)
val tuple4 = (1, 2)
val isEqual = tuple3 == tuple4            // true

// 元组大小最大为22，如果需要更多元素可以使用嵌套元组或集合
```

## 2.9 输入与输出

### 控制台输出

```scala
// 基本输出
println("Hello, Scala!")                 // 带换行
print("Hello, Scala!")                   // 不带换行

// 字符串插值输出
val name = "Scala"
val version = 3.0
println(s"The language is $name, version $version")
println(f"The language is $name%-10s version $version%5.2f")

// 使用格式化输出
printf("Name: %s, Age: %d\n", "Alice", 30)

// 输出多行文本
println("""This is a
multi-line
string""")
```

### 控制台输入

```scala
import scala.io.StdIn

// 读取一行文本
print("Enter your name: ")
val name = StdIn.readLine()
println(s"Hello, $name!")

// 读取整数
print("Enter your age: ")
val age = StdIn.readInt()
println(s"Next year you will be ${age + 1}")

// 读取浮点数
print("Enter a decimal: ")
val decimal = StdIn.readDouble()
println(s"You entered: $decimal")

// 读取布尔值
print("Enter true or false: ")
val boolValue = StdIn.readBoolean()
println(s"You entered: $boolValue")
```

### 文件读写

```scala
import scala.io.Source
import java.io.{File, PrintWriter}

// 读取文件
def readFile(filename: String): String = {
  val source = Source.fromFile(filename)
  try {
    source.mkString
  } finally {
    source.close()
  }
}

// 逐行读取文件
def readFileLines(filename: String): Unit = {
  val source = Source.fromFile(filename)
  try {
    for (line <- source.getLines()) {
      println(line)
    }
  } finally {
    source.close()
  }
}

// 写入文件
def writeFile(filename: String, content: String): Unit = {
  val writer = new PrintWriter(new File(filename))
  try {
    writer.write(content)
  } finally {
    writer.close()
  }
}

// 追加到文件
def appendToFile(filename: String, content: String): Unit = {
  val writer = new PrintWriter(new FileWriter(filename, true))
  try {
    writer.append(content)
  } finally {
    writer.close()
  }
}

// 使用资源（try-with-resources的Scala方式）
import scala.util.{Try, Success, Failure}

def using[A <: { def close(): Unit }, B](resource: A)(block: A => B): Try[B] = {
  Try(block(resource)).map { result =>
    resource.close()
    result
  }.recoverWith { case e: Exception =>
    try {
      resource.close()
    } catch {
      case suppressed: Exception => e.addSuppressed(suppressed)
    }
    Failure(e)
  }
}

// 使用using读取文件
using(Source.fromFile("example.txt")) { source =>
  val lines = source.getLines().toList
  println(s"Read ${lines.length} lines")
  lines
}
```

## 2.10 代码风格与最佳实践

### 命名约定

```scala
// 类名：大驼峰命名法（UpperCamelCase）
class MyScalaClass
object MyScalaObject

// 方法名和变量名：小驼峰命名法（lowerCamelCase）
def calculateSum(): Int = {
  val firstNumber = 10
  val secondNumber = 20
  firstNumber + secondNumber
}

// 常量：全大写，下划线分隔
val MAX_SIZE = 100
val DEFAULT_TIMEOUT = 5000

// 包名：全小写，通常使用域名反向
package com.example.project

// 类型参数：通常使用单个大写字母
class MyGenericClass[T, U]
def processList[A](list: List[A]): List[A] = list
```

### 代码组织

```scala
// 导入语句
import scala.collection.mutable._
import java.util.{List => JavaList, Map => JavaMap}
import scala.concurrent.{Future, ExecutionContext}

// 类定义
class ExampleClass(param1: String, param2: Int) {
  // 私有成员
  private val internalState = "initialized"
  
  // 公共方法
  def publicMethod(): String = {
    privateHelper()
    s"Result: $internalState"
  }
  
  // 私有方法
  private def privateHelper(): Unit = {
    // 实现细节
  }
}

// 伴生对象
object ExampleClass {
  def apply(param1: String, param2: Int): ExampleClass = {
    new ExampleClass(param1, param2)
  }
  
  def factoryMethod(): ExampleClass = {
    new ExampleClass("default", 0)
  }
}
```

### 注释

```scala
/** 
 * 这是一个示例类，展示Scala文档注释风格
 * 
 * @constructor 创建一个示例实例
 * @param param1 第一个参数，用于演示
 * @param param2 第二个参数，用于演示
 */
class DocumentationExample(param1: String, param2: Int) {
  /**
   * 计算两个数的和
   * 
   * @param a 第一个加数
   * @param b 第二个加数
   * @return 两数之和
   */
  def add(a: Int, b: Int): Int = a + b
  
  // 这是一个单行注释
  
  /*
   * 这是一个多行注释
   * 可以跨越多行
   */
  
  /**
   * 处理集合元素
   * 
   * @param numbers 数字列表
   * @return 处理后的列表
   * @throws IllegalArgumentException 如果列表为空
   * @example
   * {{{
   * val example = new DocumentationExample("test", 1)
   * val result = example.processList(List(1, 2, 3))
   * println(result)  // 输出处理后的列表
   * }}}
   */
  def processList(numbers: List[Int]): List[Int] = {
    if (numbers.isEmpty) {
      throw new IllegalArgumentException("List cannot be empty")
    }
    
    numbers.map(_ * 2).filter(_ > 5)
  }
}
```

### 错误处理

```scala
import scala.util.{Try, Success, Failure}

// 使用Try进行异常处理
def divide(a: Int, b: Int): Try[Int] = {
  Try(a / b)
}

// 处理结果
val result = divide(10, 2)
result match {
  case Success(value) => println(s"Result: $value")
  case Failure(exception) => println(s"Error: ${exception.getMessage}")
}

// 使用map和flatMap链式处理
val finalResult = divide(10, 2)
  .map(_ * 2)
  .filter(_ > 10)
  .getOrElse(0)

// 使用Option处理可能为空的值
def findUser(id: Int): Option[String] = {
  if (id > 0) Some(s"User$id")
  else None
}

// 使用模式匹配处理Option
val user = findUser(1)
user match {
  case Some(name) => println(s"Found user: $name")
  case None => println("User not found")
}

// 使用getOrElse提供默认值
val userName = findUser(-1).getOrElse("Unknown")
```

## 总结

本章介绍了Scala的基础语法，包括值与变量、数据类型、字符串操作、操作符、控制结构、循环、函数、数组、元组以及输入输出。这些基础知识是学习Scala的基石，为后续学习面向对象编程和函数式编程打下了坚实基础。

Scala的语法设计简洁而强大，特别是其表达式特性（如if-else和match表达式可以返回值）和函数式特性（如函数作为一等公民）为编写简洁而富有表现力的代码提供了可能。

下一章将深入探讨Scala的面向对象编程特性，包括类、对象、继承和特质等概念。