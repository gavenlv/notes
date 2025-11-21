object FunctionsExamples {
  def main(args: Array[String]): Unit = {
    // 基本函数
    def add(a: Int, b: Int): Int = a + b
    def multiply(a: Int, b: Int): Int = a * b
    
    println(s"add(5, 3) = ${add(5, 3)}")
    println(s"multiply(5, 3) = ${multiply(5, 3)}")
    
    // 无参函数
    def greet(): String = "Hello, Scala!"
    println(greet())
    
    // 函数字面量（匿名函数）
    val add2 = (a: Int, b: Int) => a + b
    println(s"add2(5, 3) = ${add2(5, 3)}")
    
    // 高阶函数：接受函数作为参数
    def operateOnNumbers(a: Int, b: Int, operation: (Int, Int) => Int): Int = {
      operation(a, b)
    }
    
    val sum = operateOnNumbers(5, 3, (x, y) => x + y)
    val product = operateOnNumbers(5, 3, (x, y) => x * y)
    val difference = operateOnNumbers(5, 3, (x, y) => x - y)
    
    println(s"5 + 3 = $sum")
    println(s"5 * 3 = $product")
    println(s"5 - 3 = $difference")
    
    // 函数作为返回值
    def createMultiplier(factor: Int): Int => Int = {
      (x: Int) => x * factor
    }
    
    val double = createMultiplier(2)
    val triple = createMultiplier(3)
    
    println(s"double(5) = ${double(5)}")
    println(s"triple(5) = ${triple(5)}")
    
    // 柯里化函数
    def curriedAdd(a: Int)(b: Int): Int = a + b
    println(s"curriedAdd(5)(3) = ${curriedAdd(5)(3)}")
    
    // 部分应用
    val add5 = curriedAdd(5) _
    println(s"add5(3) = ${add5(3)}")
    
    // 可变参数函数
    def sumAll(numbers: Int*): Int = {
      numbers.sum
    }
    
    println(s"sumAll(1, 2, 3) = ${sumAll(1, 2, 3)}")
    println(s"sumAll(1, 2, 3, 4, 5) = ${sumAll(1, 2, 3, 4, 5)}")
    
    // 传递序列作为参数
    val numbers = List(1, 2, 3, 4, 5)
    println(s"sumAll(numbers: _*) = ${sumAll(numbers: _*)}")
    
    // 集合操作与函数
    val list = List(1, 2, 3, 4, 5)
    val doubled = list.map(_ * 2)
    val evenNumbers = list.filter(_ % 2 == 0)
    val sum = list.reduce(_ + _)
    
    println(s"Original: $list")
    println(s"Doubled: $doubled")
    println(s"Even numbers: $evenNumbers")
    println(s"Sum: $sum")
    
    // 链式操作
    val result = list
      .filter(_ > 2)
      .map(_ * 3)
      .take(2)
    
    println(s"Chained operation result: $result")
  }
}