/**
 * LazyCollections.scala
 * 
 * 演示Scala惰性集合的使用方法
 * 包括Stream/LazyList、View等惰性求值特性
 */

import scala.math.BigInt

// Stream/LazyList示例 (Scala 2.13+中LazyList替代了Stream)
object LazyListDemo {
  def run(): Unit = {
    println("=== LazyList示例 ===")
    
    // 创建LazyList
    val lazyList1 = LazyList(1, 2, 3, 4, 5)
    val lazyList2 = LazyList.from(1)  // 从1开始的无限LazyList
    
    println(s"lazyList1: ${lazyList1.take(5).toList}")
    
    // 使用#::操作符创建LazyList
    def from(n: Int): LazyList[Int] = n #:: from(n + 1)
    val naturals = from(1)
    
    println(s"前10个自然数: ${naturals.take(10).toList}")
    
    // 斐波那契数列
    def fibonacci(a: BigInt, b: BigInt): LazyList[BigInt] = a #:: fibonacci(b, a + b)
    val fib = fibonacci(0, 1)
    
    println(s"前15个斐波那契数: ${fib.take(15).toList}")
    
    // 素数筛法
    def sieve(numbers: LazyList[Int]): LazyList[Int] = {
      numbers.head #:: sieve(
        numbers.tail.filter(_ % numbers.head != 0)
      )
    }
    
    val primes = sieve(LazyList.from(2))
    println(s"前20个素数: ${primes.take(20).toList}")
    
    // LazyList的缓存特性
    println("\nLazyList的缓存特性:")
    val expensiveLazyList = LazyList.from(1).map { x =>
      println(s"计算 $x 的平方")  // 只在需要时计算
      x * x
    }
    
    println("获取前3个元素:")
    println(expensiveLazyList.take(3).toList)  // 计算1, 4, 9
    
    println("再次获取前3个元素:")
    println(expensiveLazyList.take(3).toList)  // 不重新计算，使用缓存
  }
}

// View示例
object ViewDemo {
  def run(): Unit = {
    println("\n=== View示例 ===")
    
    val numbers = (1 to 1000000).toList
    
    // 不使用View - 中间结果会被物化
    println("不使用View的操作:")
    val result1 = numbers
      .map(_ + 1)
      .map(_ * 2)
      .filter(_ % 3 == 0)
      .take(10)
    
    println(s"结果: ${result1.take(10)}")
    
    // 使用View - 操作被延迟执行
    println("\n使用View的操作:")
    val result2 = numbers
      .view  // 转换为View
      .map(_ + 1)
      .map(_ * 2)
      .filter(_ % 3 == 0)
      .take(10)
      .toList  // 最终物化结果
    
    println(s"结果: ${result2}")
    
    // View的性能优势演示
    def timeOperation[T](operation: => T): (T, Long) = {
      val start = System.currentTimeMillis()
      val result = operation
      val end = System.currentTimeMillis()
      (result, end - start)
    }
    
    val largeList = (1 to 100000).toList
    
    val (_, withoutViewTime) = timeOperation {
      largeList
        .map(_ + 1)
        .map(_ * 2)
        .filter(_ % 3 == 0)
        .take(100)
        .sum
    }
    
    val (_, withViewTime) = timeOperation {
      largeList
        .view
        .map(_ + 1)
        .map(_ * 2)
        .filter(_ % 3 == 0)
        .take(100)
        .sum
    }
    
    println(s"\n不使用View耗时: ${withoutViewTime}ms")
    println(s"使用View耗时: ${withViewTime}ms")
  }
}

// 惰性求值的实际应用示例
object LazyEvaluationApplicationsDemo {
  def run(): Unit = {
    println("\n=== 惰性求值的实际应用示例 ===")
    
    // 1. 文件处理
    def readFileLines(filename: String): LazyList[String] = {
      // 模拟文件读取
      println(s"打开文件: $filename")
      LazyList("Line 1", "Line 2", "Line 3", "Error: something wrong", "Line 5")
    }
    
    // 只处理直到遇到错误为止的行
    def processUntilError(lines: LazyList[String]): LazyList[String] = {
      lines.takeWhile(!_.startsWith("Error"))
    }
    
    val fileLines = readFileLines("example.txt")
    val processedLines = processUntilError(fileLines)
    
    println("处理文件行直到错误:")
    processedLines.foreach(println)
    
    // 2. 数据库查询模拟
    case class User(id: Int, name: String, active: Boolean)
    
    def fetchUsersFromDB(): LazyList[User] = {
      println("执行数据库查询...")
      LazyList(
        User(1, "Alice", true),
        User(2, "Bob", false),
        User(3, "Charlie", true),
        User(4, "David", true),
        User(5, "Eve", false)
      )
    }
    
    // 只获取前2个活跃用户
    val activeUsers = fetchUsersFromDB()
      .filter(_.active)
      .take(2)
    
    println("\n获取前2个活跃用户:")
    activeUsers.foreach(user => println(s"  ${user.name}"))
    
    // 3. 无限序列的有限使用
    def powersOfTwo: LazyList[BigInt] = {
      def loop(n: BigInt): LazyList[BigInt] = n #:: loop(n * 2)
      loop(1)
    }
    
    println("\n前10个2的幂:")
    powersOfTwo.take(10).foreach(println)
    
    // 4. 条件求值
    def expensiveComputation(x: Int): Int = {
      println(s"执行昂贵计算: $x")
      x * x
    }
    
    val lazyComputations = LazyList(1, 2, 3, 4, 5).map(expensiveComputation)
    
    println("\n只计算前3个结果:")
    lazyComputations.take(3).foreach(println)
  }
}

// LazyList与普通集合的对比
object LazyVsStrictDemo {
  def run(): Unit = {
    println("\n=== LazyList与普通集合的对比 ===")
    
    // 内存使用对比
    println("创建大型集合:")
    
    // 普通List会立即分配内存
    val strictList = (1 to 1000000).toList
    println(s"严格求值List大小: ${strictList.size}")
    
    // LazyList不会立即分配内存
    val lazyList = (1 to 1000000).to(LazyList)
    println(s"惰性求值LazyList创建完成")
    println(s"只取前10个元素: ${lazyList.take(10).toList}")
    
    // 异常处理对比
    def riskyOperation(x: Int): Int = {
      if (x == 5) throw new RuntimeException("出错了!")
      x * 2
    }
    
    val strictNumbers = List(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    val lazyNumbers = LazyList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    
    println("\n异常处理对比:")
    
    try {
      val strictResult = strictNumbers.map(riskyOperation)
      println(s"严格求值结果: $strictResult")
    } catch {
      case e: Exception => println(s"严格求值过程中发生异常: ${e.getMessage}")
    }
    
    val lazyMapped = lazyNumbers.map(riskyOperation)
    println("惰性求值映射完成（尚未执行）")
    
    try {
      val lazyResult = lazyMapped.take(4).toList  // 只执行前4个元素
      println(s"惰性求值前4个结果: $lazyResult")
    } catch {
      case e: Exception => println(s"惰性求值过程中发生异常: ${e.getMessage}")
    }
  }
}

// 自定义惰性集合示例
object CustomLazyCollectionDemo {
  def run(): Unit = {
    println("\n=== 自定义惰性集合示例 ===")
    
    // 简单的自定义惰性列表
    sealed trait LazySequence[+A] {
      def head: A
      def tail: LazySequence[A]
      def isEmpty: Boolean
      
      def take(n: Int): LazySequence[A] = {
        if (n <= 0 || isEmpty) Empty
        else Cons(() => head, () => tail.take(n - 1))
      }
      
      def map[B](f: A => B): LazySequence[B] = {
        if (isEmpty) Empty
        else Cons(() => f(head), () => tail.map(f))
      }
      
      def filter(p: A => Boolean): LazySequence[A] = {
        if (isEmpty) Empty
        else if (p(head)) Cons(() => head, () => tail.filter(p))
        else tail.filter(p)
      }
      
      def toList: List[A] = {
        if (isEmpty) Nil
        else head :: tail.toList
      }
    }
    
    case object Empty extends LazySequence[Nothing] {
      def head = throw new NoSuchElementException("Empty.head")
      def tail = throw new NoSuchElementException("Empty.tail")
      def isEmpty = true
    }
    
    case class Cons[+A](
      headF: () => A,
      tailF: () => LazySequence[A]
    ) extends LazySequence[A] {
      lazy val head = headF()
      lazy val tail = tailF()
      def isEmpty = false
    }
    
    object LazySequence {
      def apply[A](as: A*): LazySequence[A] = {
        if (as.isEmpty) Empty
        else Cons(() => as.head, () => apply(as.tail: _*))
      }
      
      def from(n: Int): LazySequence[Int] = {
        Cons(() => n, () => from(n + 1))
      }
    }
    
    // 使用自定义惰性列表
    val customLazySeq = LazySequence(1, 2, 3, 4, 5)
    println(s"自定义惰性列表: ${customLazySeq.toList}")
    
    val mappedSeq = customLazySeq.map(_ * 2)
    println(s"映射后: ${mappedSeq.take(3).toList}")
    
    val filteredSeq = customLazySeq.filter(_ % 2 == 0)
    println(s"过滤偶数: ${filteredSeq.toList}")
    
    // 无限序列
    val infiniteSeq = LazySequence.from(1)
    println(s"无限序列前10个: ${infiniteSeq.take(10).toList}")
  }
}

// 主程序入口
object LazyCollectionsDemo extends App {
  LazyListDemo.run()
  ViewDemo.run()
  LazyEvaluationApplicationsDemo.run()
  LazyVsStrictDemo.run()
  CustomLazyCollectionDemo.run()
}