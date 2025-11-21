object PartialFunctions {
  def main(args: Array[String]): Unit = {
    // 基本偏函数
    val squareRoot: PartialFunction[Int, Double] = {
      case x if x >= 0 => Math.sqrt(x)
    }
    
    println(s"squareRoot.isDefinedAt(9): ${squareRoot.isDefinedAt(9)}")
    println(s"squareRoot.isDefinedAt(-9): ${squareRoot.isDefinedAt(-9)}")
    
    if (squareRoot.isDefinedAt(9)) {
      println(s"squareRoot(9): ${squareRoot(9)}")
    }
    
    // 使用applyOrElse
    val result = squareRoot.applyOrElse(-1, (x: Int) => Double.NaN)
    println(s"applyOrElse(-1): $result")
    
    // 使用lift将偏函数转换为普通函数
    val lifted = squareRoot.lift
    println(s"lifted(9): ${lifted(9)}")
    println(s"lifted(-9): ${lifted(-9)}")
    
    // 使用orElse组合偏函数
    val reciprocal: PartialFunction[Double, Double] = {
      case x if x != 0 => 1.0 / x
    }
    
    val combined = squareRoot.orElse(reciprocal)
    println(s"combined(4): ${combined(4)}")
    println(s"combined(-4): ${combined(-4)}")
    
    // 偏函数在集合操作中的应用
    val mixed = List(1, "hello", 3.14, "world", 42, true)
    
    val stringsUpper = mixed.collect {
      case s: String => s.toUpperCase
    }
    println(s"stringsUpper: $stringsUpper")
    
    val numbers = List(-5, -3, 0, 2, 4, 7, 10)
    val positiveRoots = numbers.collect {
      case x if x > 0 => Math.sqrt(x)
    }
    println(s"positiveRoots: $positiveRoots")
    
    // 偏函数在DSL中的应用
    val textProcessor: PartialFunction[String, String] = {
      case s if s.startsWith("http") => s"URL: $s"
      case s if s.contains("@") => s"Email: $s"
      case s if s.matches("\\d{3}-\\d{2}-\\d{4}") => s"SSN: $s"
    }
    
    val texts = List("hello@example.com", "http://example.com", "123-45-6789", "just text")
    val processed = texts.collect(textProcessor)
    println(s"processed: $processed")
  }
}