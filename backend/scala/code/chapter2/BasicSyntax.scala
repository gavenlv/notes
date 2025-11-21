object BasicSyntax {
  def main(args: Array[String]): Unit = {
    // 值与变量
    val immutable = "I cannot be changed"
    var mutable = 10
    mutable = 20  // 可以重新赋值
    
    println(s"Immutable: $immutable")
    println(s"Mutable: $mutable")
    
    // 基本数据类型
    val intVal: Int = 42
    val doubleVal: Double = 3.14159
    val stringVal: String = "Scala"
    val booleanVal: Boolean = true
    val charVal: Char = 'S'
    
    println(s"Int: $intVal, Double: $doubleVal")
    println(s"String: $stringVal, Boolean: $booleanVal, Char: $charVal")
    
    // 字符串插值
    val name = "Scala"
    val version = 3.0
    println(s"The language is $name, version $version")
    
    // if表达式
    val age = 25
    val category = if (age < 18) "Minor" else "Adult"
    println(s"Age $age is a $category")
    
    // match表达式
    val day = 3
    val dayName = day match {
      case 1 => "Monday"
      case 2 => "Tuesday"
      case 3 => "Wednesday"
      case 4 => "Thursday"
      case 5 => "Friday"
      case 6 => "Saturday"
      case 7 => "Sunday"
      case _ => "Unknown day"
    }
    println(s"Day $day is $dayName")
    
    // for循环
    println("Numbers 1 to 5:")
    for (i <- 1 to 5) {
      print(s"$i ")
    }
    println()
    
    // while循环
    var j = 0
    println("While loop:")
    while (j < 3) {
      println(s"j = $j")
      j += 1
    }
    
    // 函数
    def add(a: Int, b: Int): Int = a + b
    val sum = add(5, 3)
    println(s"5 + 3 = $sum")
    
    // 高阶函数
    val numbers = List(1, 2, 3, 4, 5)
    val doubled = numbers.map(_ * 2)
    println(s"Original: $numbers")
    println(s"Doubled: $doubled")
    
    // 数组
    val array = Array(1, 2, 3, 4, 5)
    array(0) = 10  // 修改第一个元素
    println(s"Array first element: ${array(0)}")
    
    // 元组
    val tuple = (1, "hello", true)
    val (num, str, bool) = tuple
    println(s"Tuple: num=$num, str=$str, bool=$bool")
  }
}