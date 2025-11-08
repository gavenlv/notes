package chapter2

/**
 * 模式匹配示例
 * 展示Scala中强大的模式匹配功能，包括基本模式、类型模式、守卫条件等
 */
object PatternMatching {
  
  // 1. 基本模式匹配
  def describe(x: Any): String = x match {
    case 1 => "数字一"
    case "hello" => "打招呼"
    case true => "布尔真"
    case _ => "其他值"
  }
  
  // 2. 类型模式匹配
  def processValue(x: Any): String = x match {
    case s: String => s"字符串: $s"
    case i: Int => s"整数: $i"
    case d: Double => s"浮点数: $d"
    case list: List[_] => s"列表: $list"
    case _ => "未知类型"
  }
  
  // 3. 列表模式匹配
  def processList(list: List[Int]): String = list match {
    case Nil => "空列表"
    case head :: Nil => s"只有一个元素: $head"
    case head :: second :: Nil => s"两个元素: $head, $second"
    case head :: tail => s"多个元素，首元素: $head，剩余: $tail"
  }
  
  // 4. 元组模式匹配
  def processTuple(tuple: (Int, String)): String = tuple match {
    case (1, "one") => "匹配特定元组"
    case (x, y) => s"任意元组: ($x, $y)"
  }
  
  // 5. 守卫条件（Guard）
  def checkNumber(x: Int): String = x match {
    case n if n > 0 && n < 10 => "一位正数"
    case n if n >= 10 && n < 100 => "两位数"
    case n if n >= 100 => "三位数或更大"
    case n if n < 0 => "负数"
    case 0 => "零"
  }
  
  // 6. 样例类模式匹配
  def processPerson(person: Person): String = person match {
    case Person("Alice", age) if age < 18 => "未成年Alice"
    case Person("Alice", age) if age >= 18 => "成年Alice"
    case Person(name, age) if age < 18 => s"未成年人: $name"
    case Person(name, age) => s"成年人: $name, $age岁"
  }
  
  // 7. 密封类模式匹配
  def processExpression(expr: Expression): Int = expr match {
    case Number(value) => value
    case Add(left, right) => processExpression(left) + processExpression(right)
    case Subtract(left, right) => processExpression(left) - processExpression(right)
    case Multiply(left, right) => processExpression(left) * processExpression(right)
    case Divide(left, right) => processExpression(left) / processExpression(right)
  }
  
  // 8. 模式匹配在for循环中的应用
  def patternMatchingInFor(): Unit = {
    val pairs = List((1, "one"), (2, "two"), (3, "three"))
    
    for ((num, word) <- pairs) {
      println(s"数字 $num 对应单词 $word")
    }
    
    // 带守卫条件的模式匹配
    for ((num, word) <- pairs if num % 2 == 1) {
      println(s"奇数数字 $num 对应单词 $word")
    }
  }
  
  // 9. 提取器模式匹配
  def processEmail(email: String): String = email match {
    case Email(user, domain) => s"用户名: $user, 域名: $domain"
    case _ => "无效的邮箱格式"
  }
  
  // 10. 模式匹配实践：JSON解析模拟
  def parseJson(json: JsonValue): String = json match {
    case JsonString(value) => s"字符串: $value"
    case JsonNumber(value) => s"数字: $value"
    case JsonBoolean(value) => s"布尔: $value"
    case JsonArray(elements) => s"数组: ${elements.mkString(", ")}"
    case JsonObject(fields) => 
      val fieldStrs = fields.map { case (k, v) => s"$k: ${parseJson(v)}" }
      s"对象: {${fieldStrs.mkString(", ")}}"
    case JsonNull => "null"
  }
  
  // 测试函数
  def testPatternMatching(): Unit = {
    println("=== 模式匹配测试 ===")
    
    // 测试基本模式匹配
    println(s"describe(1) = ${describe(1)}")
    println(s"describe(\"hello\") = ${describe("hello")}")
    println(s"describe(3.14) = ${describe(3.14)}")
    
    // 测试类型模式匹配
    println(s"processValue(\"test\") = ${processValue("test")}")
    println(s"processValue(42) = ${processValue(42)}")
    println(s"processValue(List(1,2,3)) = ${processValue(List(1,2,3))}")
    
    // 测试列表模式匹配
    println(s"processList(List()) = ${processList(List())}")
    println(s"processList(List(1)) = ${processList(List(1))}")
    println(s"processList(List(1,2)) = ${processList(List(1,2))}")
    println(s"processList(List(1,2,3)) = ${processList(List(1,2,3))}")
    
    // 测试守卫条件
    println(s"checkNumber(5) = ${checkNumber(5)}")
    println(s"checkNumber(25) = ${checkNumber(25)}")
    println(s"checkNumber(-5) = ${checkNumber(-5)}")
    
    // 测试样例类模式匹配
    val alice = Person("Alice", 16)
    val bob = Person("Bob", 25)
    println(s"processPerson($alice) = ${processPerson(alice)}")
    println(s"processPerson($bob) = ${processPerson(bob)}")
    
    // 测试表达式模式匹配
    val expr = Add(Multiply(Number(2), Number(3)), Subtract(Number(10), Number(4)))
    println(s"表达式: $expr")
    println(s"计算结果: ${processExpression(expr)}")
    
    // 测试for循环中的模式匹配
    println("for循环模式匹配:")
    patternMatchingInFor()
    
    // 测试提取器
    println(s"processEmail(\"user@example.com\") = ${processEmail("user@example.com")}")
    
    // 测试JSON解析
    val json = JsonObject(Map(
      "name" -> JsonString("Alice"),
      "age" -> JsonNumber(25),
      "active" -> JsonBoolean(true),
      "hobbies" -> JsonArray(List(JsonString("reading"), JsonString("coding")))
    ))
    println(s"JSON解析结果: ${parseJson(json)}")
    
    println("=== 测试完成 ===\n")
  }
}

// 样例类定义
case class Person(name: String, age: Int)

// 表达式密封类
sealed trait Expression
case class Number(value: Int) extends Expression
case class Add(left: Expression, right: Expression) extends Expression
case class Subtract(left: Expression, right: Expression) extends Expression
case class Multiply(left: Expression, right: Expression) extends Expression
case class Divide(left: Expression, right: Expression) extends Expression

// 邮箱提取器
object Email {
  def unapply(str: String): Option[(String, String)] = {
    val parts = str.split("@")
    if (parts.length == 2) Some((parts(0), parts(1)))
    else None
  }
}

// JSON值定义
sealed trait JsonValue
case class JsonString(value: String) extends JsonValue
case class JsonNumber(value: Int) extends JsonValue
case class JsonBoolean(value: Boolean) extends JsonValue
case class JsonArray(elements: List[JsonValue]) extends JsonValue
case class JsonObject(fields: Map[String, JsonValue]) extends JsonValue
case object JsonNull extends JsonValue

// 主程序入口
object PatternMatchingApp extends App {
  PatternMatching.testPatternMatching()
}