object FunctionalBasics {
  def main(args: Array[String]): Unit = {
    // 高阶函数
    val numbers = List(1, 2, 3, 4, 5)
    
    // map函数
    val doubled = numbers.map(_ * 2)
    println(s"Doubled: $doubled")
    
    // filter函数
    val evenNumbers = numbers.filter(_ % 2 == 0)
    println(s"Even numbers: $evenNumbers")
    
    // reduce函数
    val sum = numbers.reduce(_ + _)
    println(s"Sum: $sum")
    
    // flatMap函数
    val sentences = List("Hello world", "Scala is fun")
    val words = sentences.flatMap(_.split(" "))
    println(s"Words: $words")
    
    // 函数组合
    val add5: Int => Int = _ + 5
    val multiplyBy2: Int => Int = _ * 2
    
    val add5ThenMultiply = add5.andThen(multiplyBy2)
    println(s"add5ThenMultiply(3): ${add5ThenMultiply(3)}")
    
    val multiplyThenAdd5 = multiplyBy2.compose(add5)
    println(s"multiplyThenAdd5(3): ${multiplyThenAdd5(3)}")
    
    // 柯里化
    def curriedAdd(a: Int)(b: Int): Int = a + b
    val add5Curried: Int => Int = curriedAdd(5)
    println(s"add5Curried(3): ${add5Curried(3)}")
    
    // 部分应用
    def multiply(a: Int, b: Int): Int = a * b
    val double: Int => Int = multiply(2, _: Int)
    println(s"double(5): ${double(5)}")
    
    // 闭包
    def makeMultiplier(factor: Int): Int => Int = (x: Int) => x * factor
    val triple = makeMultiplier(3)
    println(s"triple(5): ${triple(5)}")
    
    // 纯函数与副作用
    def add(a: Int, b: Int): Int = a + b  // 纯函数
    println(s"add(2, 3): ${add(2, 3)}")
    
    // 处理可能的副作用
    def safeDivide(a: Int, b: Int): Option[Int] = {
      if (b != 0) Some(a / b)
      else None
    }
    
    println(s"safeDivide(10, 2): ${safeDivide(10, 2)}")
    println(s"safeDivide(10, 0): ${safeDivide(10, 0)}")
    
    // 递归
    def factorial(n: Int): Int = {
      if (n <= 1) 1
      else n * factorial(n - 1)
    }
    
    println(s"factorial(5): ${factorial(5)}")
    
    // 尾递归
    def factorialTail(n: Int): Int = {
      @annotation.tailrec
      def loop(n: Int, accumulator: Int): Int = {
        if (n <= 1) accumulator
        else loop(n - 1, n * accumulator)
      }
      
      loop(n, 1)
    }
    
    println(s"factorialTail(5): ${factorialTail(5)}")
  }
}