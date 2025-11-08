package chapter2

/**
 * 递归函数示例
 * 展示Scala中递归的使用，包括尾递归优化、递归模式等
 */
object Recursion {
  
  // 1. 基本递归：阶乘计算（非尾递归）
  def factorial(n: Int): Int = {
    if (n <= 1) 1
    else n * factorial(n - 1)
  }
  
  // 2. 尾递归优化：阶乘计算
  def factorialTailRecursive(n: Int): Int = {
    @annotation.tailrec
    def factorialHelper(n: Int, acc: Int): Int = {
      if (n <= 1) acc
      else factorialHelper(n - 1, n * acc)
    }
    factorialHelper(n, 1)
  }
  
  // 3. 斐波那契数列（非尾递归）
  def fibonacci(n: Int): Int = {
    if (n <= 1) n
    else fibonacci(n - 1) + fibonacci(n - 2)
  }
  
  // 4. 尾递归优化：斐波那契数列
  def fibonacciTailRecursive(n: Int): Int = {
    @annotation.tailrec
    def fibHelper(n: Int, a: Int, b: Int): Int = {
      if (n <= 0) a
      else fibHelper(n - 1, b, a + b)
    }
    fibHelper(n, 0, 1)
  }
  
  // 5. 列表求和（递归实现）
  def sumList(list: List[Int]): Int = list match {
    case Nil => 0
    case head :: tail => head + sumList(tail)
  }
  
  // 6. 尾递归优化：列表求和
  def sumListTailRecursive(list: List[Int]): Int = {
    @annotation.tailrec
    def sumHelper(list: List[Int], acc: Int): Int = list match {
      case Nil => acc
      case head :: tail => sumHelper(tail, acc + head)
    }
    sumHelper(list, 0)
  }
  
  // 7. 列表反转（递归实现）
  def reverseList[A](list: List[A]): List[A] = list match {
    case Nil => Nil
    case head :: tail => reverseList(tail) :+ head
  }
  
  // 8. 尾递归优化：列表反转
  def reverseListTailRecursive[A](list: List[A]): List[A] = {
    @annotation.tailrec
    def reverseHelper(list: List[A], acc: List[A]): List[A] = list match {
      case Nil => acc
      case head :: tail => reverseHelper(tail, head :: acc)
    }
    reverseHelper(list, Nil)
  }
  
  // 9. 递归深度计算
  def calculateDepth[A](tree: Tree[A]): Int = tree match {
    case Leaf(_) => 1
    case Node(_, children) => 1 + children.map(calculateDepth).max
  }
  
  // 10. 递归模式：映射树结构
  def mapTree[A, B](tree: Tree[A])(f: A => B): Tree[B] = tree match {
    case Leaf(value) => Leaf(f(value))
    case Node(value, children) => Node(f(value), children.map(mapTree(_)(f)))
  }
  
  // 11. 递归实践：目录遍历模拟
  def traverseDirectory(dir: Directory): List[String] = {
    def traverseHelper(dir: Directory, acc: List[String]): List[String] = {
      val currentFiles = dir.files.map(file => s"${dir.name}/$file")
      val subdirFiles = dir.subdirectories.flatMap(traverseHelper(_, Nil))
      currentFiles ++ subdirFiles
    }
    traverseHelper(dir, Nil)
  }
  
  // 测试函数
  def testRecursion(): Unit = {
    println("=== 递归函数测试 ===")
    
    // 测试阶乘
    println(s"factorial(5) = ${factorial(5)}")
    println(s"factorialTailRecursive(5) = ${factorialTailRecursive(5)}")
    
    // 测试斐波那契
    println(s"fibonacci(6) = ${fibonacci(6)}")
    println(s"fibonacciTailRecursive(6) = ${fibonacciTailRecursive(6)}")
    
    // 测试列表操作
    val numbers = List(1, 2, 3, 4, 5)
    println(s"sumList($numbers) = ${sumList(numbers)}")
    println(s"sumListTailRecursive($numbers) = ${sumListTailRecursive(numbers)}")
    println(s"reverseList($numbers) = ${reverseList(numbers)}")
    println(s"reverseListTailRecursive($numbers) = ${reverseListTailRecursive(numbers)}")
    
    // 测试树结构
    val tree = Node(1, List(
      Leaf(2),
      Node(3, List(Leaf(4), Leaf(5))),
      Leaf(6)
    ))
    println(s"树深度: ${calculateDepth(tree)}")
    
    val doubledTree = mapTree(tree)(_ * 2)
    println(s"映射后的树: $doubledTree")
    
    // 测试目录遍历
    val dir = Directory("root", List("file1.txt", "file2.txt"), List(
      Directory("subdir1", List("file3.txt"), Nil),
      Directory("subdir2", List("file4.txt", "file5.txt"), Nil)
    ))
    println(s"目录遍历结果: ${traverseDirectory(dir)}")
    
    println("=== 测试完成 ===\n")
  }
}

// 树结构定义
sealed trait Tree[+A]
case class Leaf[A](value: A) extends Tree[A]
case class Node[A](value: A, children: List[Tree[A]]) extends Tree[A]

// 目录结构定义
case class Directory(name: String, files: List[String], subdirectories: List[Directory])

// 主程序入口
object RecursionApp extends App {
  Recursion.testRecursion()
}