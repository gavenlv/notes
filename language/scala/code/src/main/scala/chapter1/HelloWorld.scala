package chapter1

/**
 * 第1章：Scala基础入门 - Hello World示例
 * 
 * 这个文件展示了Scala程序的基本结构，包括：
 * - 包声明
 * - 对象定义
 * - 主方法
 * - 基础语法
 */
object HelloWorld {
  
  /**
   * 程序入口点
   * @param args 命令行参数
   */
  def main(args: Array[String]): Unit = {
    println("=== Scala基础入门示例 ===")
    
    // 1. 基础输出
    println("\n1. 基础输出:")
    println("Hello, Scala!")
    
    // 2. 变量和常量
    println("\n2. 变量和常量:")
    val name: String = "Scala Learner"  // 不可变变量
    var age: Int = 25                    // 可变变量
    val language = "Scala"               // 类型推断
    
    println(s"姓名: $name")
    println(s"年龄: $age")
    println(s"语言: $language")
    
    // 修改可变变量
    age = 26
    println(s"修改后年龄: $age")
    
    // 3. 数据类型演示
    println("\n3. 数据类型:")
    val byteValue: Byte = 127
    val shortValue: Short = 32767
    val intValue: Int = 2147483647
    val longValue: Long = 9223372036854775807L
    val floatValue: Float = 3.14159f
    val doubleValue: Double = 3.141592653589793
    val charValue: Char = 'A'
    val boolValue: Boolean = true
    
    println(s"Byte: $byteValue")
    println(s"Short: $shortValue")
    println(s"Int: $intValue")
    println(s"Long: $longValue")
    println(s"Float: $floatValue")
    println(s"Double: $doubleValue")
    println(s"Char: $charValue")
    println(s"Boolean: $boolValue")
    
    // 4. 运算符演示
    println("\n4. 运算符:")
    val a = 10
    val b = 3
    
    println(s"$a + $b = ${a + b}")
    println(s"$a - $b = ${a - b}")
    println(s"$a * $b = ${a * b}")
    println(s"$a / $b = ${a / b}")
    println(s"$a % $b = ${a % b}")
    
    // 5. 字符串操作
    println("\n5. 字符串操作:")
    val str1 = "Hello"
    val str2 = "World"
    val combined = str1 + " " + str2
    val interpolated = s"$str1 $str2"
    
    println(s"拼接: $combined")
    println(s"插值: $interpolated")
    println(s"长度: ${interpolated.length}")
    println(s"大写: ${interpolated.toUpperCase}")
    println(s"小写: ${interpolated.toLowerCase}")
    
    // 6. 调用其他函数
    println("\n6. 函数调用:")
    val sumResult = add(15, 25)
    val factorialResult = factorial(5)
    val greetResult = greet("Alice")
    
    println(s"15 + 25 = $sumResult")
    println(s"5! = $factorialResult")
    println(greetResult)
    
    println("\n=== 示例运行完成 ===")
  }
  
  /**
   * 加法函数
   * @param a 第一个数
   * @param b 第二个数
   * @return 两数之和
   */
  def add(a: Int, b: Int): Int = a + b
  
  /**
   * 计算阶乘
   * @param n 要计算阶乘的数
   * @return n的阶乘
   */
  def factorial(n: Int): Int = {
    if (n <= 1) 1
    else n * factorial(n - 1)
  }
  
  /**
   * 问候函数
   * @param name 姓名
   * @return 问候语
   */
  def greet(name: String): String = {
    s"你好, $name! 欢迎学习Scala!"
  }
}

/**
 * 伴生对象示例
 */
object HelloWorldCompanion {
  
  /**
   * 静态方法示例
   */
  def staticMethod(): String = "这是一个静态方法"
}

/**
 * 应用程序特质示例
 * 可以省略main方法
 */
object SimpleApp extends App {
  println("使用App特质的简单程序")
  println("不需要显式定义main方法")
}