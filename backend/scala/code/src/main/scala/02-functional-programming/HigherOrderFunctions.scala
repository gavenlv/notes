package chapter2

/**
 * 高阶函数示例
 * 展示Scala中高阶函数的使用，包括函数作为参数、函数作为返回值、函数组合等
 */
object HigherOrderFunctions {
  
  // 1. 函数作为参数
  def applyFunction(f: Int => Int, x: Int): Int = f(x)
  
  // 2. 函数作为返回值
  def multiplier(factor: Int): Int => Int = (x: Int) => x * factor
  
  // 3. 高阶函数示例：map
  def mapList[A, B](list: List[A], f: A => B): List[B] = {
    list.map(f)
  }
  
  // 4. 高阶函数示例：filter
  def filterList[A](list: List[A], predicate: A => Boolean): List[A] = {
    list.filter(predicate)
  }
  
  // 5. 高阶函数示例：reduce
  def reduceList[A](list: List[A], f: (A, A) => A): A = {
    list.reduce(f)
  }
  
  // 6. 函数组合
  def compose[A, B, C](f: B => C, g: A => B): A => C = {
    (x: A) => f(g(x))
  }
  
  // 7. 柯里化函数
  def curriedAdd(x: Int)(y: Int): Int = x + y
  
  // 8. 部分应用函数
  def partialApplicationExample(): Unit = {
    val add5 = curriedAdd(5)_
    println(s"部分应用函数：add5(3) = ${add5(3)}")
  }
  
  // 9. 匿名函数（Lambda表达式）
  def lambdaExample(): Unit = {
    val numbers = List(1, 2, 3, 4, 5)
    
    // 使用匿名函数
    val doubled = numbers.map(x => x * 2)
    val evenNumbers = numbers.filter(_ % 2 == 0)
    
    println(s"匿名函数示例：doubled = $doubled")
    println(s"匿名函数示例：evenNumbers = $evenNumbers")
  }
  
  // 10. 高阶函数实践
  def processNumbers(numbers: List[Int]): List[Int] = {
    numbers
      .filter(_ > 0)        // 过滤正数
      .map(_ * 2)           // 乘以2
      .filter(_ < 20)       // 过滤小于20的数
  }
  
  // 测试函数
  def testHigherOrderFunctions(): Unit = {
    println("=== 高阶函数测试 ===")
    
    val numbers = List(1, 2, 3, 4, 5)
    
    // 测试函数作为参数
    val square = (x: Int) => x * x
    println(s"applyFunction(square, 5) = ${applyFunction(square, 5)}")
    
    // 测试函数作为返回值
    val double = multiplier(2)
    val triple = multiplier(3)
    println(s"double(5) = ${double(5)}")
    println(s"triple(5) = ${triple(5)}")
    
    // 测试map
    val squaredNumbers = mapList(numbers, square)
    println(s"mapList(numbers, square) = $squaredNumbers")
    
    // 测试filter
    val evenNumbers = filterList(numbers, _ % 2 == 0)
    println(s"filterList(numbers, even) = $evenNumbers")
    
    // 测试reduce
    val sum = reduceList(numbers, _ + _)
    println(s"reduceList(numbers, +) = $sum")
    
    // 测试函数组合
    val add1 = (x: Int) => x + 1
    val multiply2 = (x: Int) => x * 2
    val addThenMultiply = compose(multiply2, add1)
    println(s"compose(multiply2, add1)(3) = ${addThenMultiply(3)}")
    
    // 测试柯里化
    println(s"curriedAdd(2)(3) = ${curriedAdd(2)(3)}")
    
    // 测试部分应用
    partialApplicationExample()
    
    // 测试匿名函数
    lambdaExample()
    
    // 测试高阶函数实践
    val processed = processNumbers(List(-1, 2, 3, 10, 15))
    println(s"processNumbers = $processed")
    
    println("=== 测试完成 ===\n")
  }
}

// 主程序入口
object HigherOrderFunctionsApp extends App {
  HigherOrderFunctions.testHigherOrderFunctions()
}