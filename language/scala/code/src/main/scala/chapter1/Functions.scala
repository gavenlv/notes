package chapter1

/**
 * 第1章：函数定义和使用示例
 * 
 * 演示Scala中的函数特性：
 * - 函数定义和方法声明
 * - 参数和返回值
 * - 高阶函数
 * - 匿名函数（lambda）
 * - 函数组合
 * - 偏应用函数
 * - 柯里化
 */
object Functions {
  
  def main(args: Array[String]): Unit = {
    println("=== Scala函数示例 ===")
    
    // 1. 基本函数示例
    println("\n1. 基本函数:")
    basicFunctionExamples()
    
    // 2. 高阶函数示例
    println("\n2. 高阶函数:")
    higherOrderFunctionExamples()
    
    // 3. 匿名函数示例
    println("\n3. 匿名函数:")
    anonymousFunctionExamples()
    
    // 4. 函数组合示例
    println("\n4. 函数组合:")
    functionCompositionExamples()
    
    // 5. 偏应用函数和柯里化
    println("\n5. 偏应用函数和柯里化:")
    partialApplicationAndCurryingExamples()
    
    // 6. 递归函数示例
    println("\n6. 递归函数:")
    recursiveFunctionExamples()
    
    println("\n=== 函数示例完成 ===")
  }
  
  /**
   * 基本函数示例
   */
  def basicFunctionExamples(): Unit = {
    // 无参数函数
    def greet(): String = "你好，Scala！"
    println(greet())
    
    // 带参数函数
    def add(a: Int, b: Int): Int = a + b
    println(s"3 + 5 = ${add(3, 5)}")
    
    // 默认参数
    def greetPerson(name: String = "访客"): String = s"你好，$name！"
    println(greetPerson("张三"))
    println(greetPerson()) // 使用默认参数
    
    // 命名参数
    def createPerson(name: String, age: Int, city: String = "北京"): String = 
      s"姓名: $name, 年龄: $age, 城市: $city"
    
    println(createPerson("李四", 25))
    println(createPerson(age = 30, name = "王五")) // 命名参数
    
    // 可变参数
    def sum(numbers: Int*): Int = numbers.sum
    println(s"1+2+3 = ${sum(1, 2, 3)}")
    println(s"1到5的和 = ${sum(1, 2, 3, 4, 5)}")
    
    // 过程（无返回值函数）
    def printInfo(name: String, age: Int): Unit = {
      println(s"信息 - 姓名: $name, 年龄: $age")
    }
    printInfo("赵六", 28)
    
    // 返回多个值（使用元组）
    def minMax(numbers: List[Int]): (Int, Int) = {
      (numbers.min, numbers.max)
    }
    
    val (minVal, maxVal) = minMax(List(3, 1, 4, 1, 5, 9, 2))
    println(s"最小值: $minVal, 最大值: $maxVal")
  }
  
  /**
   * 高阶函数示例
   */
  def higherOrderFunctionExamples(): Unit = {
    // 接受函数作为参数的函数
    def operateOnNumbers(a: Int, b: Int, operation: (Int, Int) => Int): Int = {
      operation(a, b)
    }
    
    // 定义一些操作函数
    def add(x: Int, y: Int): Int = x + y
    def multiply(x: Int, y: Int): Int = x * y
    
    println(s"10 + 20 = ${operateOnNumbers(10, 20, add)}")
    println(s"10 * 20 = ${operateOnNumbers(10, 20, multiply)}")
    
    // 返回函数的函数
    def createMultiplier(factor: Int): Int => Int = {
      (x: Int) => x * factor
    }
    
    val double = createMultiplier(2)
    val triple = createMultiplier(3)
    
    println(s"5的双倍: ${double(5)}")
    println(s"5的三倍: ${triple(5)}")
    
    // 集合的高阶函数
    val numbers = List(1, 2, 3, 4, 5)
    
    // map: 转换每个元素
    val squares = numbers.map(x => x * x)
    println(s"平方: $squares")
    
    // filter: 过滤元素
    val evens = numbers.filter(_ % 2 == 0)
    println(s"偶数: $evens")
    
    // reduce: 聚合元素
    val sum = numbers.reduce(_ + _)
    println(s"总和: $sum")
    
    // fold: 带初始值的聚合
    val product = numbers.fold(1)(_ * _)
    println(s"乘积: $product")
  }
  
  /**
   * 匿名函数示例
   */
  def anonymousFunctionExamples(): Unit = {
    // 基本匿名函数
    val add = (x: Int, y: Int) => x + y
    println(s"匿名函数加法: ${add(3, 7)}")
    
    // 使用下划线简化
    val square: Int => Int = _ * _
    println(s"平方函数: ${square(5)}")
    
    val isEven: Int => Boolean = _ % 2 == 0
    println(s"5是偶数吗: ${isEven(5)}")
    
    // 在集合操作中使用匿名函数
    val numbers = List(1, 2, 3, 4, 5)
    
    // 完整写法
    val doubled = numbers.map((x: Int) => x * 2)
    println(s"加倍: $doubled")
    
    // 简化写法
    val tripled = numbers.map(_ * 3)
    println(s"三倍: $tripled")
    
    // 复杂匿名函数
    val processNumber = (x: Int) => {
      val squared = x * x
      val doubled = squared * 2
      doubled + 1
    }
    
    println(s"处理数字5: ${processNumber(5)}")
    
    // 多参数匿名函数
    val combineStrings = (s1: String, s2: String) => s"$s1-$s2"
    println(s"字符串组合: ${combineStrings("Hello", "World")}")
  }
  
  /**
   * 函数组合示例
   */
  def functionCompositionExamples(): Unit = {
    // 定义一些基础函数
    def addOne(x: Int): Int = x + 1
    def double(x: Int): Int = x * 2
    def square(x: Int): Int = x * x
    
    // 函数组合：先加1，再平方
    val addThenSquare = square _ compose addOne
    println(s"(3+1)^2 = ${addThenSquare(3)}")
    
    // 函数组合：先平方，再加1
    val squareThenAdd = addOne _ compose square
    println(s"3^2+1 = ${squareThenAdd(3)}")
    
    // 使用andThen（从左到右）
    val pipeline1 = addOne _ andThen double andThen square
    println(s"(3+1)*2^2 = ${pipeline1(3)}")
    
    val pipeline2 = square _ andThen addOne andThen double
    println(s"(3^2+1)*2 = ${pipeline2(3)}")
    
    // 字符串处理函数组合
    def toUpper(s: String): String = s.toUpperCase
    def addExclamation(s: String): String = s + "!"
    def reverse(s: String): String = s.reverse
    
    val processString = toUpper _ andThen addExclamation andThen reverse
    println(s"字符串处理: ${processString("hello")}")
    
    // 更复杂的函数组合
    def parseNumber(s: String): Int = s.toInt
    def isPrime(n: Int): Boolean = {
      if (n <= 1) false
      else if (n == 2) true
      else !(2 to math.sqrt(n).toInt).exists(n % _ == 0)
    }
    
    val isStringPrime = parseNumber _ andThen isPrime
    println(s"\"7\"是质数吗: ${isStringPrime("7")}")
    println(s"\"8\"是质数吗: ${isStringPrime("8")}")
  }
  
  /**
   * 偏应用函数和柯里化示例
   */
  def partialApplicationAndCurryingExamples(): Unit = {
    // 偏应用函数
    def log(level: String, message: String): Unit = {
      println(s"[$level] $message")
    }
    
    // 创建偏应用函数
    val infoLog = log("INFO", _: String)
    val errorLog = log("ERROR", _: String)
    
    infoLog("应用程序启动")
    errorLog("发生错误")
    
    // 柯里化函数
    def addCurried(a: Int)(b: Int): Int = a + b
    
    // 使用柯里化
    val addFive = addCurried(5)_
    println(s"5 + 3 = ${addFive(3)}")
    println(s"5 + 10 = ${addFive(10)}")
    
    // 更实用的柯里化示例
    def sendEmail(from: String)(to: String)(subject: String)(body: String): Unit = {
      println(s"发送邮件:")
      println(s"发件人: $from")
      println(s"收件人: $to")
      println(s"主题: $subject")
      println(s"内容: $body")
      println("-" * 30)
    }
    
    // 创建邮件发送器
    val companyEmail = sendEmail("noreply@company.com")_
    val toManager = companyEmail("manager@company.com")_
    val weeklyReport = toManager("每周报告")
    
    weeklyReport("这是本周的工作报告...")
    weeklyReport("本周项目进展顺利...")
    
    // 数学函数的柯里化
    def power(exponent: Double)(base: Double): Double = 
      math.pow(base, exponent)
    
    val square = power(2)_
    val cube = power(3)_
    val sqrt = power(0.5)_
    
    println(s"5的平方: ${square(5)}")
    println(s"5的立方: ${cube(5)}")
    println(s"25的平方根: ${sqrt(25)}")
  }
  
  /**
   * 递归函数示例
   */
  def recursiveFunctionExamples(): Unit = {
    // 阶乘函数
    def factorial(n: Int): Int = {
      if (n <= 1) 1
      else n * factorial(n - 1)
    }
    
    println(s"5的阶乘: ${factorial(5)}")
    println(s"10的阶乘: ${factorial(10)}")
    
    // 斐波那契数列
    def fibonacci(n: Int): Int = {
      if (n <= 1) n
      else fibonacci(n - 1) + fibonacci(n - 2)
    }
    
    println("斐波那契数列前10项:")
    for (i <- 0 until 10) {
      print(s"${fibonacci(i)} ")
    }
    println()
    
    // 尾递归优化（使用@tailrec注解）
    import scala.annotation.tailrec
    
    @tailrec
    def factorialTailrec(n: Int, accumulator: Int = 1): Int = {
      if (n <= 1) accumulator
      else factorialTailrec(n - 1, n * accumulator)
    }
    
    println(s"尾递归阶乘(5): ${factorialTailrec(5)}")
    
    // 列表处理递归
    def sumList(list: List[Int]): Int = list match {
      case Nil => 0
      case head :: tail => head + sumList(tail)
    }
    
    val numbers = List(1, 2, 3, 4, 5)
    println(s"列表 $numbers 的和: ${sumList(numbers)}")
    
    // 尾递归列表处理
    @tailrec
    def sumListTailrec(list: List[Int], accumulator: Int = 0): Int = list match {
      case Nil => accumulator
      case head :: tail => sumListTailrec(tail, accumulator + head)
    }
    
    println(s"尾递归列表和: ${sumListTailrec(numbers)}")
    
    // 递归深度示例
    def recursiveDepth(n: Int, depth: Int = 0): Int = {
      if (n <= 0) depth
      else {
        println(s"深度 $depth: n = $n")
        recursiveDepth(n - 1, depth + 1)
      }
    }
    
    println(s"递归深度: ${recursiveDepth(5)}")
  }
}

/**
 * 函数式编程实践示例
 */
object FunctionalProgrammingPractice {
  
  /**
   * 纯函数示例
   */
  def pureFunctionExamples(): Unit = {
    // 纯函数：相同的输入总是产生相同的输出，没有副作用
    def pureAdd(a: Int, b: Int): Int = a + b
    
    // 非纯函数：有副作用（修改外部状态）
    var counter = 0
    def impureAdd(a: Int, b: Int): Int = {
      counter += 1  // 副作用
      a + b
    }
    
    println(s"纯函数结果: ${pureAdd(2, 3)}")
    println(s"非纯函数结果: ${impureAdd(2, 3)}, 计数器: $counter")
    println(s"再次调用非纯函数: ${impureAdd(2, 3)}, 计数器: $counter")
  }
  
  /**
   * 不可变数据示例
   */
  def immutableDataExamples(): Unit = {
    // 使用val声明不可变变量
    val immutableList = List(1, 2, 3)
    
    // 不能修改，但可以创建新列表
    val newList = immutableList :+ 4  // 创建新列表，原列表不变
    
    println(s"原列表: $immutableList")
    println(s"新列表: $newList")
    
    // 函数式处理：不修改原数据，返回新数据
    val processed = immutableList
      .filter(_ % 2 != 0)  // 过滤奇数
      .map(_ * 2)           // 加倍
      .reverse              // 反转
    
    println(s"处理后的列表: $processed")
    println(s"原列表保持不变: $immutableList")
  }
  
  /**
   * 函数作为一等公民
   */
  def firstClassFunctions(): Unit = {
    // 函数可以赋值给变量
    val mathOperation: (Int, Int) => Int = (a, b) => a + b
    
    // 函数可以作为参数传递
    def applyOperation(x: Int, y: Int, op: (Int, Int) => Int): Int = op(x, y)
    
    // 函数可以作为返回值
    def createMultiplier(factor: Int): Int => Int = (x: Int) => x * factor
    
    println(s"直接调用: ${mathOperation(5, 3)}")
    println(s"作为参数: ${applyOperation(5, 3, mathOperation)}")
    
    val doubler = createMultiplier(2)
    println(s"作为返回值: ${doubler(5)}")
  }
}