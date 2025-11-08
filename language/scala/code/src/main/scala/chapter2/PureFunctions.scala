package chapter2

/**
 * 第2章：纯函数示例
 * 
 * 演示函数式编程的核心概念：
 * - 纯函数的定义和特性
 * - 副作用和引用透明性
 * - 不可变数据
 * - 函数组合的数学基础
 */
object PureFunctions {
  
  def main(args: Array[String]): Unit = {
    println("=== 纯函数示例 ===")
    
    // 1. 纯函数示例
    println("\n1. 纯函数示例:")
    pureFunctionExamples()
    
    // 2. 副作用示例
    println("\n2. 副作用示例:")
    sideEffectExamples()
    
    // 3. 引用透明性
    println("\n3. 引用透明性:")
    referentialTransparencyExamples()
    
    // 4. 不可变数据
    println("\n4. 不可变数据:")
    immutableDataExamples()
    
    // 5. 纯函数实践
    println("\n5. 纯函数实践:")
    pureFunctionPractice()
    
    println("\n=== 纯函数示例完成 ===")
  }
  
  /**
   * 纯函数示例
   */
  def pureFunctionExamples(): Unit = {
    // 纯函数：相同的输入总是产生相同的输出，没有副作用
    
    // 示例1：数学函数
    def square(x: Int): Int = x * x
    def add(a: Int, b: Int): Int = a + b
    
    println(s"square(5) = ${square(5)}")  // 总是25
    println(s"add(3, 7) = ${add(3, 7)}")  // 总是10
    
    // 示例2：字符串处理
    def toUpperCase(s: String): String = s.toUpperCase
    def reverseString(s: String): String = s.reverse
    
    println(s"toUpperCase(\"hello\") = ${toUpperCase("hello")}")  // 总是"HELLO"
    println(s"reverseString(\"scala\") = ${reverseString("scala")}")  // 总是"alacs"
    
    // 示例3：数据转换
    case class Point(x: Int, y: Int)
    def movePoint(p: Point, dx: Int, dy: Int): Point = Point(p.x + dx, p.y + dy)
    
    val original = Point(1, 2)
    val moved = movePoint(original, 3, 4)
    println(s"移动点: $original -> $moved")  // 原对象不变
    
    // 纯函数的特性验证
    println("\n纯函数特性验证:")
    
    // 相同输入相同输出
    val result1 = square(5)
    val result2 = square(5)
    println(s"square(5) 第一次调用: $result1")
    println(s"square(5) 第二次调用: $result2")
    println(s"两次调用结果相同: ${result1 == result2}")
    
    // 可以安全替换
    val expression1 = add(square(2), square(3))
    val expression2 = add(4, 9)  // square(2)=4, square(3)=9
    println(s"表达式1: $expression1")
    println(s"表达式2: $expression2")
    println(s"表达式等价: ${expression1 == expression2}")
  }
  
  /**
   * 副作用示例
   */
  def sideEffectExamples(): Unit = {
    // 非纯函数：有副作用
    
    var counter = 0  // 外部状态
    
    // 有副作用的函数：修改外部状态
    def impureIncrement(): Int = {
      counter += 1  // 副作用：修改外部变量
      counter
    }
    
    // 有副作用的函数：执行I/O操作
    def impurePrint(message: String): Unit = {
      println(s"打印: $message")  // 副作用：控制台输出
    }
    
    // 有副作用的函数：依赖外部状态
    def impureGetCurrentTime(): Long = {
      System.currentTimeMillis()  // 副作用：依赖系统时间
    }
    
    println("有副作用函数测试:")
    
    // 相同的调用产生不同的结果
    println(s"第一次调用: ${impureIncrement()}")
    println(s"第二次调用: ${impureIncrement()}")
    println(s"第三次调用: ${impureIncrement()}")
    
    // I/O操作
    impurePrint("这是一条消息")
    impurePrint("这是另一条消息")
    
    // 时间依赖
    val time1 = impureGetCurrentTime()
    Thread.sleep(100)  // 等待100毫秒
    val time2 = impureGetCurrentTime()
    println(s"时间1: $time1")
    println(s"时间2: $time2")
    println(s"时间不同: ${time1 != time2}")
    
    // 将副作用函数转换为纯函数
    println("\n转换为纯函数:")
    
    // 纯函数版本：显式传递状态
    def pureIncrement(current: Int): (Int, Int) = {
      val newCounter = current + 1
      (newCounter, newCounter)
    }
    
    // 使用状态传递
    val (state1, result1) = pureIncrement(0)
    val (state2, result2) = pureIncrement(state1)
    val (state3, result3) = pureIncrement(state2)
    
    println(s"第一次调用结果: $result1, 新状态: $state1")
    println(s"第二次调用结果: $result2, 新状态: $state2")
    println(s"第三次调用结果: $result3, 新状态: $state3")
  }
  
  /**
   * 引用透明性示例
   */
  def referentialTransparencyExamples(): Unit = {
    // 引用透明性：表达式可以被其值替换而不改变程序行为
    
    // 纯函数具有引用透明性
    def double(x: Int): Int = x * 2
    
    // 表达式 double(5) 可以安全替换为 10
    val expressionA = double(5) + double(5)
    val expressionB = 10 + 10  // 替换后的表达式
    
    println(s"表达式A: double(5) + double(5) = $expressionA")
    println(s"表达式B: 10 + 10 = $expressionB")
    println(s"表达式等价: ${expressionA == expressionB}")
    
    // 更复杂的例子
    def factorial(n: Int): Int = {
      if (n <= 1) 1
      else n * factorial(n - 1)
    }
    
    // 引用透明性验证
    val complexExpression = factorial(3) + factorial(4)
    val replacedExpression = 6 + 24  // factorial(3)=6, factorial(4)=24
    
    println(s"复杂表达式: factorial(3) + factorial(4) = $complexExpression")
    println(s"替换后表达式: 6 + 24 = $replacedExpression")
    println(s"表达式等价: ${complexExpression == replacedExpression}")
    
    // 非引用透明的例子
    var globalCounter = 0
    
    def impureCounter(): Int = {
      globalCounter += 1
      globalCounter
    }
    
    // 非引用透明：不能安全替换
    val impureExpression = impureCounter() + impureCounter()
    
    // 如果我们尝试替换
    globalCounter = 0  // 重置
    val firstCall = impureCounter()  // 1
    val secondCall = impureCounter() // 2
    val manualSum = firstCall + secondCall  // 3
    
    println(s"非纯表达式: impureCounter() + impureCounter() = $impureExpression")
    println(s"手动计算: 1 + 2 = $manualSum")
    println(s"结果不同: ${impureExpression != manualSum}")  // 通常为true
  }
  
  /**
   * 不可变数据示例
   */
  def immutableDataExamples(): Unit = {
    // 不可变数据：创建后不能修改
    
    // 不可变变量
    val immutableValue = 42
    // immutableValue = 43  // 编译错误：不能重新赋值
    
    // 不可变集合
    val immutableList = List(1, 2, 3)
    // immutableList(0) = 10  // 编译错误：不能修改元素
    
    // 创建新集合而不是修改原集合
    val newList = immutableList :+ 4  // 添加元素，创建新列表
    val filteredList = immutableList.filter(_ > 1)  // 过滤，创建新列表
    
    println(s"原列表: $immutableList")
    println(s"添加元素后的新列表: $newList")
    println(s"过滤后的新列表: $filteredList")
    println(s"原列表保持不变: $immutableList")
    
    // 不可变数据结构的优势
    case class Person(name: String, age: Int)
    
    val person1 = Person("Alice", 25)
    val person2 = person1.copy(age = 26)  // 创建新对象，原对象不变
    
    println(s"原对象: $person1")
    println(s"新对象: $person2")
    println(s"原对象保持不变: $person1")
    
    // 函数式数据转换
    val people = List(
      Person("Alice", 25),
      Person("Bob", 30),
      Person("Charlie", 35)
    )
    
    // 纯函数式转换：不修改原数据，返回新数据
    val adults = people.filter(_.age >= 18)
    val names = people.map(_.name)
    val totalAge = people.map(_.age).sum
    
    println(s"所有人: $people")
    println(s"成年人: $adults")
    println(s"姓名列表: $names")
    println(s"年龄总和: $totalAge")
    println(s"原数据保持不变: $people")
    
    // 不可变性的线程安全优势
    println("\n不可变性的线程安全:")
    
    val sharedData = List(1, 2, 3, 4, 5)
    
    // 多个线程可以安全地读取相同的数据
    // 因为数据是不可变的，不会发生竞态条件
    
    def processData(data: List[Int]): List[Int] = {
      // 安全操作：不会修改原数据
      data.map(_ * 2).filter(_ > 5)
    }
    
    val result1 = processData(sharedData)
    val result2 = processData(sharedData)
    
    println(s"共享数据: $sharedData")
    println(s"线程1结果: $result1")
    println(s"线程2结果: $result2")
    println(s"共享数据保持不变: $sharedData")
  }
  
  /**
   * 纯函数实践
   */
  def pureFunctionPractice(): Unit = {
    // 实际应用中的纯函数
    
    // 1. 数据处理管道
    def processText(text: String): Map[Char, Int] = {
      text.toLowerCase
        .filter(_.isLetter)  // 过滤字母
        .groupBy(identity)    // 按字符分组
        .view.mapValues(_.length).toMap  // 计算频率
    }
    
    val text = "Hello Functional Programming in Scala!"
    val charFrequency = processText(text)
    
    println(s"原文: $text")
    println(s"字符频率: $charFrequency")
    
    // 2. 数学计算
    def calculateStatistics(numbers: List[Double]): (Double, Double, Double) = {
      val mean = numbers.sum / numbers.length
      val variance = numbers.map(x => math.pow(x - mean, 2)).sum / numbers.length
      val stdDev = math.sqrt(variance)
      (mean, variance, stdDev)
    }
    
    val data = List(1.0, 2.0, 3.0, 4.0, 5.0)
    val (mean, variance, stdDev) = calculateStatistics(data)
    
    println(s"数据: $data")
    println(f"均值: $mean%.2f")
    println(f"方差: $variance%.2f")
    println(f"标准差: $stdDev%.2f")
    
    // 3. 业务逻辑
    case class Order(item: String, quantity: Int, price: Double)
    
    def calculateTotal(orders: List[Order]): Double = {
      orders.map(order => order.quantity * order.price).sum
    }
    
    def applyDiscount(total: Double, discountRate: Double): Double = {
      total * (1 - discountRate)
    }
    
    def formatCurrency(amount: Double): String = {
      f"$$$amount%.2f"
    }
    
    val orders = List(
      Order("Book", 2, 25.0),
      Order("Pen", 5, 2.5),
      Order("Notebook", 1, 15.0)
    )
    
    val total = calculateTotal(orders)
    val discounted = applyDiscount(total, 0.1)  // 10%折扣
    val formatted = formatCurrency(discounted)
    
    println(s"订单: $orders")
    println(s"总金额: ${formatCurrency(total)}")
    println(s"折扣后: $formatted")
    
    // 4. 纯函数组合
    val processOrder = (orders: List[Order]) => 
      formatCurrency(applyDiscount(calculateTotal(orders), 0.1))
    
    val result = processOrder(orders)
    println(s"组合函数结果: $result")
  }
}

/**
 * 纯函数的高级特性
 */
object PureFunctionAdvanced {
  
  /**
   * 记忆化 (Memoization)
   * 纯函数可以安全地进行记忆化缓存
   */
  def memoizedFibonacci(): Int => Int = {
    var cache = Map.empty[Int, Int]
    
    def fib(n: Int): Int = {
      if (cache.contains(n)) {
        cache(n)
      } else {
        val result = if (n <= 1) n else fib(n - 1) + fib(n - 2)
        cache += (n -> result)
        result
      }
    }
    
    fib
  }
  
  /**
   * 函数组合的数学性质
   */
  def functionCompositionProperties(): Unit = {
    // 结合律: (f ∘ g) ∘ h = f ∘ (g ∘ h)
    def f(x: Int): Int = x + 1
    def g(x: Int): Int = x * 2
    def h(x: Int): Int = x - 3
    
    val leftAssociative = (f _ compose g _ compose h _)(5)
    val rightAssociative = (f _ compose (g _ compose h _))(5)
    
    println(s"左结合: $leftAssociative")
    println(s"右结合: $rightAssociative")
    println(s"结合律成立: ${leftAssociative == rightAssociative}")
    
    // 单位元: f ∘ id = id ∘ f = f
    def identity[A](x: A): A = x
    
    val withIdentity = (f _ compose identity[Int] _)(5)
    val identityWith = (identity[Int] _ compose f _)(5)
    
    println(s"f ∘ id: $withIdentity")
    println(s"id ∘ f: $identityWith")
    println(s"f(5): ${f(5)}")
    println(s"单位元性质成立: ${withIdentity == f(5) && identityWith == f(5)}")
  }
  
  /**
   * 纯函数的测试优势
   */
  def testingAdvantages(): Unit = {
    // 纯函数易于测试
    def pureAdd(a: Int, b: Int): Int = a + b
    
    // 测试用例
    val testCases = List(
      (1, 1) -> 2,
      (0, 0) -> 0,
      (-1, 1) -> 0,
      (100, 200) -> 300
    )
    
    println("纯函数测试:")
    testCases.foreach { case ((a, b), expected) =>
      val actual = pureAdd(a, b)
      val passed = actual == expected
      println(s"pureAdd($a, $b) = $actual, 期望: $expected, 通过: $passed")
    }
    
    // 与非纯函数对比
    var state = 0
    def impureAdd(a: Int, b: Int): Int = {
      state += 1
      a + b + state
    }
    
    println("\n非纯函数测试问题:")
    // 相同的输入可能产生不同的输出
    println(s"第一次调用: ${impureAdd(2, 3)}")  // 6
    println(s"第二次调用: ${impureAdd(2, 3)}")  // 7
    println(s"测试不可靠，因为依赖外部状态")
  }
}