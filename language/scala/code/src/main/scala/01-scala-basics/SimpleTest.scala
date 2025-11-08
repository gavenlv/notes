package chapter1

/**
 * 简单的测试对象，用于验证Scala代码语法
 */
object SimpleTest {
  
  def main(args: Array[String]): Unit = {
    println("=== Scala语法验证测试 ===")
    
    // 测试基本语法
    testBasicSyntax()
    
    // 测试控制结构
    testControlStructures()
    
    // 测试函数
    testFunctions()
    
    println("=== 所有测试通过 ===")
  }
  
  def testBasicSyntax(): Unit = {
    println("\n1. 基本语法测试:")
    
    // 变量和常量
    val x = 10
    var y = 20
    
    println(s"常量 x = $x")
    println(s"变量 y = $y")
    
    // 重新赋值变量
    y = 30
    println(s"重新赋值后 y = $y")
    
    // 数据类型
    val name: String = "Scala"
    val age: Int = 25
    val height: Double = 175.5
    val isStudent: Boolean = true
    
    println(s"姓名: $name, 年龄: $age, 身高: $height, 学生: $isStudent")
    
    // 字符串操作
    val greeting = s"你好，$name！"
    println(greeting)
    
    // 集合操作
    val numbers = List(1, 2, 3, 4, 5)
    val doubled = numbers.map(_ * 2)
    println(s"原列表: $numbers")
    println(s"加倍后: $doubled")
  }
  
  def testControlStructures(): Unit = {
    println("\n2. 控制结构测试:")
    
    // if-else表达式
    val score = 85
    val grade = if (score >= 90) "A"
    else if (score >= 80) "B"
    else if (score >= 70) "C"
    else "D"
    
    println(s"分数 $score 的等级是: $grade")
    
    // for循环
    println("1到5的数字:")
    for (i <- 1 to 5) {
      print(s"$i ")
    }
    println()
    
    // 模式匹配
    val value: Any = "hello"
    val result = value match {
      case 1 => "数字1"
      case "hello" => "字符串hello"
      case _ => "其他值"
    }
    println(s"模式匹配结果: $result")
    
    // 异常处理
    try {
      val division = 10 / 2
      println(s"10 / 2 = $division")
    } catch {
      case e: ArithmeticException => println("除零错误")
    } finally {
      println("异常处理完成")
    }
  }
  
  def testFunctions(): Unit = {
    println("\n3. 函数测试:")
    
    // 基本函数
    def add(a: Int, b: Int): Int = a + b
    println(s"3 + 5 = ${add(3, 5)}")
    
    // 高阶函数
    def operate(a: Int, b: Int, op: (Int, Int) => Int): Int = op(a, b)
    val multiply = (x: Int, y: Int) => x * y
    println(s"4 * 6 = ${operate(4, 6, multiply)}")
    
    // 匿名函数
    val square: Int => Int = x => x * x
    println(s"5的平方 = ${square(5)}")
    
    // 递归函数
    def factorial(n: Int): Int = {
      if (n <= 1) 1
      else n * factorial(n - 1)
    }
    println(s"5的阶乘 = ${factorial(5)}")
    
    // 函数组合
    def addOne(x: Int): Int = x + 1
    def double(x: Int): Int = x * 2
    
    val pipeline = addOne _ andThen double
    println(s"(3+1)*2 = ${pipeline(3)}")
  }
}

/**
 * 伴生对象示例
 */
class Person(val name: String, val age: Int) {
  def introduce(): String = s"我是$name，今年$age岁"
}

object Person {
  def apply(name: String, age: Int): Person = new Person(name, age)
  
  def createAdult(name: String): Person = new Person(name, 18)
}