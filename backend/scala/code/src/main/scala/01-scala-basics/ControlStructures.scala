package chapter1

import scala.io.StdIn

/**
 * 第1章：控制结构示例
 * 
 * 演示Scala中的各种控制结构：
 * - 条件语句 (if-else)
 * - 循环结构 (for, while)
 * - 模式匹配 (match-case)
 * - 异常处理 (try-catch-finally)
 */
object ControlStructures {
  
  def main(args: Array[String]): Unit = {
    println("=== Scala控制结构示例 ===")
    
    // 1. 条件语句示例
    println("\n1. 条件语句:")
    conditionalExamples()
    
    // 2. 循环结构示例
    println("\n2. 循环结构:")
    loopExamples()
    
    // 3. 模式匹配示例
    println("\n3. 模式匹配:")
    patternMatchingExamples()
    
    // 4. 异常处理示例
    println("\n4. 异常处理:")
    exceptionHandlingExamples()
    
    // 5. 综合示例：猜数字游戏
    println("\n5. 综合示例 - 猜数字游戏:")
    guessNumberGame()
    
    println("\n=== 控制结构示例完成 ===")
  }
  
  /**
   * 条件语句示例
   */
  def conditionalExamples(): Unit = {
    // 基本if-else
    val x = 10
    val result1 = if (x > 0) "正数" else "非正数"
    println(s"$x 是 $result1")
    
    // 多条件分支
    val score = 85
    val grade = if (score >= 90) "A"
    else if (score >= 80) "B"
    else if (score >= 70) "C"
    else if (score >= 60) "D"
    else "F"
    
    println(s"分数 $score 的等级是: $grade")
    
    // 嵌套条件
    val age = 25
    val canVote = if (age >= 18) {
      if (age >= 65) "可以投票（老年人）"
      else "可以投票（成年人）"
    } else "不能投票（未成年人）"
    
    println(s"年龄 $age: $canVote")
    
    // 条件表达式返回值
    val a = 15
    val b = 10
    val max = if (a > b) a else b
    println(s"$a 和 $b 中较大的数是: $max")
  }
  
  /**
   * 循环结构示例
   */
  def loopExamples(): Unit = {
    // for循环 - 范围遍历
    println("\nfor循环 - 范围遍历:")
    for (i <- 1 to 5) {
      print(s"$i ")
    }
    println()
    
    // for循环 - 直到（不包含结束值）
    println("for循环 - 直到:")
    for (i <- 1 until 5) {
      print(s"$i ")
    }
    println()
    
    // for循环 - 带条件
    println("for循环 - 带条件（偶数）:")
    for (i <- 1 to 10 if i % 2 == 0) {
      print(s"$i ")
    }
    println()
    
    // 多重循环
    println("多重循环 - 乘法表:")
    for (i <- 1 to 3; j <- 1 to 3) {
      print(s"${i * j}\t")
      if (j == 3) println()
    }
    
    // yield生成新集合
    println("使用yield生成新集合:")
    val squares = for (i <- 1 to 5) yield i * i
    println(s"1到5的平方: $squares")
    
    // while循环
    println("\nwhile循环:")
    var count = 1
    while (count <= 5) {
      print(s"$count ")
      count += 1
    }
    println()
    
    // do-while循环
    println("do-while循环:")
    var num = 1
    do {
      print(s"$num ")
      num += 1
    } while (num <= 5)
    println()
    
    // 集合遍历
    println("\n集合遍历:")
    val fruits = List("苹果", "香蕉", "橙子", "葡萄")
    for (fruit <- fruits) {
      print(s"$fruit ")
    }
    println()
    
    // 带索引的遍历
    println("带索引的遍历:")
    for ((fruit, index) <- fruits.zipWithIndex) {
      println(s"$index: $fruit")
    }
  }
  
  /**
   * 模式匹配示例
   */
  def patternMatchingExamples(): Unit = {
    // 基本模式匹配
    val value: Any = "hello"
    
    val result = value match {
      case 1 => "数字1"
      case "hello" => "字符串hello"
      case true => "布尔true"
      case _ => "其他值"
    }
    println(s"值 '$value' 匹配结果: $result")
    
    // 类型匹配
    def describeType(x: Any): String = x match {
      case i: Int => s"整数: $i"
      case s: String => s"字符串: $s"
      case d: Double => s"双精度浮点数: $d"
      case list: List[_] => s"列表，长度: ${list.length}"
      case _ => "未知类型"
    }
    
    println(describeType(42))
    println(describeType("Scala"))
    println(describeType(3.14))
    println(describeType(List(1, 2, 3)))
    
    // 守卫条件
    def checkNumber(x: Int): String = x match {
      case n if n > 0 && n < 10 => "一位正数"
      case n if n >= 10 && n < 100 => "两位数"
      case n if n >= 100 => "三位数或更多"
      case 0 => "零"
      case _ => "负数"
    }
    
    println(s"5: ${checkNumber(5)}")
    println(s"25: ${checkNumber(25)}")
    println(s"-5: ${checkNumber(-5)}")
    
    // 元组匹配
    val pair = ("Alice", 25)
    val personInfo = pair match {
      case (name, age) => s"$name 今年 $age 岁"
      case _ => "未知信息"
    }
    println(personInfo)
  }
  
  /**
   * 异常处理示例
   */
  def exceptionHandlingExamples(): Unit = {
    // 基本异常处理
    def safeDivide(a: Int, b: Int): Int = {
      try {
        a / b
      } catch {
        case e: ArithmeticException =>
          println("捕获到算术异常: 除零错误")
          0
        case e: Exception =>
          println(s"捕获到其他异常: ${e.getMessage}")
          -1
      } finally {
        println("除法操作完成（finally块执行）")
      }
    }
    
    println(s"10 / 2 = ${safeDivide(10, 2)}")
    println(s"10 / 0 = ${safeDivide(10, 0)}")
    
    // 使用Option处理可能失败的操作
    def divideOption(a: Int, b: Int): Option[Int] = {
      if (b != 0) Some(a / b) else None
    }
    
    val result1 = divideOption(10, 2)
    val result2 = divideOption(10, 0)
    
    println(s"Option结果1: $result1")
    println(s"Option结果2: $result2")
    
    // 使用Try处理异常
    import scala.util.{Try, Success, Failure}
    
    def divideTry(a: Int, b: Int): Try[Int] = Try(a / b)
    
    val tryResult1 = divideTry(10, 2)
    val tryResult2 = divideTry(10, 0)
    
    println(s"Try结果1: $tryResult1")
    println(s"Try结果2: $tryResult2")
    
    // 处理Try结果
    tryResult1 match {
      case Success(value) => println(s"成功: $value")
      case Failure(exception) => println(s"失败: ${exception.getMessage}")
    }
    
    tryResult2 match {
      case Success(value) => println(s"成功: $value")
      case Failure(exception) => println(s"失败: ${exception.getMessage}")
    }
  }
  
  /**
   * 猜数字游戏 - 综合示例
   */
  def guessNumberGame(): Unit = {
    val secretNumber = scala.util.Random.nextInt(100) + 1
    var attempts = 0
    var guessed = false
    
    println("欢迎来到猜数字游戏！")
    println("我已经想了一个1到100之间的数字，试试猜出来吧！")
    
    while (!guessed && attempts < 10) {
      print(s"第${attempts + 1}次尝试，请输入你的猜测: ")
      
      try {
        val guess = StdIn.readInt()
        attempts += 1
        
        guess match {
          case g if g == secretNumber =>
            println(s"恭喜！你猜对了！数字就是 $secretNumber")
            println(s"你用了 $attempts 次尝试")
            guessed = true
            
          case g if g < secretNumber =>
            println("太小了，再大一点！")
            
          case g if g > secretNumber =>
            println("太大了，再小一点！")
            
          case _ =>
            println("无效输入")
        }
        
        // 提示剩余机会
        val remaining = 10 - attempts
        if (!guessed && remaining > 0) {
          println(s"你还有 $remaining 次机会")
        }
        
      } catch {
        case _: NumberFormatException =>
          println("请输入有效的数字！")
        case e: Exception =>
          println(s"发生错误: ${e.getMessage}")
      }
    }
    
    if (!guessed) {
      println(s"游戏结束！正确的数字是 $secretNumber")
    }
    
    // 询问是否再玩一次
    print("是否再玩一次？(y/n): ")
    val playAgain = StdIn.readLine().toLowerCase
    
    if (playAgain == "y" || playAgain == "yes") {
      guessNumberGame()
    } else {
      println("谢谢游玩！")
    }
  }
}

/**
 * 控制结构的高级用法示例
 */
object AdvancedControlStructures {
  
  /**
   * 使用for推导式处理嵌套结构
   */
  def processNestedData(): Unit = {
    val numbers = List(1, 2, 3)
    val letters = List('A', 'B', 'C')
    
    // 生成所有组合
    val combinations = for {
      n <- numbers
      l <- letters
    } yield s"$n$l"
    
    println(s"所有组合: $combinations")
  }
  
  /**
   * 模式匹配在函数中的应用
   */
  def factorial(n: Int): Int = n match {
    case 0 => 1
    case x if x > 0 => x * factorial(x - 1)
    case _ => throw new IllegalArgumentException("负数没有阶乘")
  }
  
  /**
   * 使用模式匹配处理列表
   */
  def processList(list: List[Int]): String = list match {
    case Nil => "空列表"
    case head :: Nil => s"只有一个元素: $head"
    case head :: tail => s"第一个元素: $head, 剩余元素: $tail"
  }
}