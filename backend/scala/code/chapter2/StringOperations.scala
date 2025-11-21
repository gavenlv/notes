object StringOperations {
  def main(args: Array[String]): Unit = {
    // 基本字符串操作
    val text = "Hello, Scala Programming"
    
    println(s"Original: $text")
    println(s"Length: ${text.length}")
    println(s"Upper case: ${text.toUpperCase}")
    println(s"Lower case: ${text.toLowerCase}")
    println(s"Contains 'Scala': ${text.contains("Scala")}")
    println(s"Starts with 'Hello': ${text.startsWith("Hello")}")
    println(s"Ends with 'Programming': ${text.endsWith("Programming")}")
    println(s"Substring: ${text.substring(7, 12)}")  // 提取"Scala"
    
    // 多行字符串
    val multiLine = """This is a
                      multi-line
                      string in Scala"""
    println("Multi-line string:")
    println(multiLine)
    
    // 带stripMargin的多行字符串
    val cleanMultiLine = 
      """|First line
         |Second line
         |Third line""".stripMargin
    println("Clean multi-line string:")
    println(cleanMultiLine)
    
    // 字符串插值
    val name = "Scala"
    val version = 3.0
    val interpolated = s"The language is $name, version $version"
    println(interpolated)
    
    // 表达式插值
    val x = 10
    val y = 20
    val exprInterpolated = s"The sum of $x and $y is ${x + y}"
    println(exprInterpolated)
    
    // f插值器
    val height = 1.78
    val formatted = f"Height: $height%.2f meters"
    println(formatted)
    
    // 字符串分割
    val sentence = "Scala is a functional programming language"
    val words = sentence.split(" ")
    println(s"Words in sentence: ${words.mkString(", ")}")
    
    // 字符串替换
    val replaced = sentence.replace("functional", "functional and object-oriented")
    println(s"Replaced: $replaced")
    
    // 字符串反转
    val reversed = "hello".reverse
    println(s"Reversed 'hello': $reversed")
    
    // 原始字符串
    val path = raw"C:\Users\Admin\Documents"
    println(s"Path: $path")
  }
}