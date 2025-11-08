package chapter1

import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers
import java.io.{ByteArrayOutputStream, PrintStream}

/**
 * 第1章测试规范
 * 测试所有基础语法和控制结构
 */
class Chapter1Spec extends AnyFlatSpec with Matchers {
  
  "HelloWorld对象" should "正确输出问候语" in {
    // 测试标准输出
    val outContent = new ByteArrayOutputStream()
    Console.withOut(outContent) {
      HelloWorld.main(Array.empty)
    }
    
    val output = outContent.toString
    output should include ("=== Scala基础语法示例 ===")
    output should include ("你好，世界！")
    output should include ("=== 基础语法示例完成 ===")
  }
  
  "HelloWorld对象" should "正确计算基本运算" in {
    HelloWorld.add(5, 3) shouldBe 8
    HelloWorld.subtract(10, 4) shouldBe 6
    HelloWorld.multiply(3, 4) shouldBe 12
    HelloWorld.divide(15, 3) shouldBe 5
  }
  
  "HelloWorld对象" should "正确处理字符串操作" in {
    HelloWorld.greet("Scala") shouldBe "你好，Scala！"
    HelloWorld.greet("World") shouldBe "你好，World！"
  }
  
  "ControlStructures对象" should "正确执行条件语句" in {
    val outContent = new ByteArrayOutputStream()
    Console.withOut(outContent) {
      ControlStructures.conditionalExamples()
    }
    
    val output = outContent.toString
    output should include ("10 是 正数")
    output should include ("分数 85 的等级是: B")
    output should include ("年龄 25: 可以投票（成年人）")
  }
  
  "ControlStructures对象" should "正确执行循环结构" in {
    val outContent = new ByteArrayOutputStream()
    Console.withOut(outContent) {
      ControlStructures.loopExamples()
    }
    
    val output = outContent.toString
    output should include ("1 2 3 4 5")
    output should include ("1到5的平方: Vector(1, 4, 9, 16, 25)")
  }
  
  "ControlStructures对象" should "正确执行模式匹配" in {
    val outContent = new ByteArrayOutputStream()
    Console.withOut(outContent) {
      ControlStructures.patternMatchingExamples()
    }
    
    val output = outContent.toString
    output should include ("值 'hello' 匹配结果: 字符串hello")
    output should include ("整数: 42")
    output should include ("字符串: Scala")
  }
  
  "ControlStructures对象" should "正确处理异常" in {
    ControlStructures.safeDivide(10, 2) shouldBe 5
    ControlStructures.safeDivide(10, 0) shouldBe 0
  }
  
  "Functions对象" should "正确执行基本函数" in {
    Functions.add(3, 5) shouldBe 8
    Functions.greetPerson("张三") shouldBe "你好，张三！"
    Functions.greetPerson() shouldBe "你好，访客！"
  }
  
  "Functions对象" should "正确执行高阶函数" in {
    Functions.operateOnNumbers(10, 20, Functions.add) shouldBe 30
    Functions.operateOnNumbers(10, 20, Functions.multiply) shouldBe 200
  }
  
  "Functions对象" should "正确执行递归函数" in {
    Functions.factorial(5) shouldBe 120
    Functions.factorial(0) shouldBe 1
    Functions.fibonacci(5) shouldBe 5
  }
  
  "FunctionalProgrammingPractice对象" should "演示纯函数特性" in {
    val outContent = new ByteArrayOutputStream()
    Console.withOut(outContent) {
      FunctionalProgrammingPractice.pureFunctionExamples()
    }
    
    val output = outContent.toString
    output should include ("纯函数结果: 5")
    output should include ("非纯函数结果: 5")
  }
  
  "FunctionalProgrammingPractice对象" should "演示不可变数据" in {
    val outContent = new ByteArrayOutputStream()
    Console.withOut(outContent) {
      FunctionalProgrammingPractice.immutableDataExamples()
    }
    
    val output = outContent.toString
    output should include ("原列表: List(1, 2, 3)")
    output should include ("新列表: List(1, 2, 3, 4)")
  }
  
  "变量和常量" should "正确声明和使用" in {
    // 测试变量声明
    val x = 10
    var y = 20
    
    x shouldBe 10
    y shouldBe 20
    
    // 变量可以重新赋值
    y = 30
    y shouldBe 30
    
    // 常量不能重新赋值（编译时检查）
    // x = 20  // 这行代码会导致编译错误
  }
  
  "数据类型" should "正确识别和转换" in {
    // 整数类型
    val intVal: Int = 42
    val longVal: Long = 42L
    
    intVal shouldBe 42
    longVal shouldBe 42L
    
    // 浮点类型
    val floatVal: Float = 3.14f
    val doubleVal: Double = 3.14
    
    floatVal shouldBe 3.14f +- 0.001f
    doubleVal shouldBe 3.14 +- 0.001
    
    // 布尔类型
    val trueVal: Boolean = true
    val falseVal: Boolean = false
    
    trueVal shouldBe true
    falseVal shouldBe false
    
    // 字符和字符串
    val charVal: Char = 'A'
    val stringVal: String = "Hello"
    
    charVal shouldBe 'A'
    stringVal shouldBe "Hello"
  }
  
  "字符串操作" should "正确执行各种操作" in {
    val str = "Hello Scala"
    
    str.length shouldBe 11
    str.toUpperCase shouldBe "HELLO SCALA"
    str.toLowerCase shouldBe "hello scala"
    str.contains("Scala") shouldBe true
    str.startsWith("Hello") shouldBe true
    str.endsWith("Scala") shouldBe true
    
    // 字符串插值
    val name = "World"
    val interpolated = s"Hello, $name!"
    interpolated shouldBe "Hello, World!"
    
    // 多行字符串
    val multiLine = """第一行
第二行
第三行"""
    multiLine should include ("第一行")
    multiLine should include ("第二行")
    multiLine should include ("第三行")
  }
  
  "集合操作" should "正确执行基本集合操作" in {
    val list = List(1, 2, 3, 4, 5)
    
    list.head shouldBe 1
    list.tail shouldBe List(2, 3, 4, 5)
    list.last shouldBe 5
    list.size shouldBe 5
    list.isEmpty shouldBe false
    
    // 映射操作
    val doubled = list.map(_ * 2)
    doubled shouldBe List(2, 4, 6, 8, 10)
    
    // 过滤操作
    val evens = list.filter(_ % 2 == 0)
    evens shouldBe List(2, 4)
    
    // 聚合操作
    val sum = list.sum
    sum shouldBe 15
    
    val product = list.product
    product shouldBe 120
  }
  
  "控制流" should "正确执行各种控制结构" in {
    // if-else 表达式
    val result1 = if (10 > 5) "greater" else "less"
    result1 shouldBe "greater"
    
    val result2 = if (5 > 10) "greater" else "less"
    result2 shouldBe "less"
    
    // for 循环
    var sum = 0
    for (i <- 1 to 5) {
      sum += i
    }
    sum shouldBe 15
    
    // while 循环
    var count = 0
    while (count < 3) {
      count += 1
    }
    count shouldBe 3
  }
  
  "模式匹配" should "正确匹配各种模式" in {
    def matchNumber(x: Int): String = x match {
      case 1 => "one"
      case 2 => "two"
      case _ => "other"
    }
    
    matchNumber(1) shouldBe "one"
    matchNumber(2) shouldBe "two"
    matchNumber(3) shouldBe "other"
    
    def matchType(x: Any): String = x match {
      case s: String => s"string: $s"
      case i: Int => s"int: $i"
      case _ => "unknown"
    }
    
    matchType("hello") shouldBe "string: hello"
    matchType(42) shouldBe "int: 42"
    matchType(3.14) shouldBe "unknown"
  }
  
  "异常处理" should "正确捕获和处理异常" in {
    def safeDivide(a: Int, b: Int): Either[String, Int] = {
      try {
        Right(a / b)
      } catch {
        case _: ArithmeticException => Left("除零错误")
        case e: Exception => Left(s"其他错误: ${e.getMessage}")
      }
    }
    
    safeDivide(10, 2) shouldBe Right(5)
    safeDivide(10, 0) shouldBe Left("除零错误")
  }
}