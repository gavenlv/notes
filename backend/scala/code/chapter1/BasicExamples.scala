// Scala基本示例

object BasicExamples {
  def main(args: Array[String]): Unit = {
    // 变量定义
    val name = "Scala"  // 不可变变量
    var age = 10        // 可变变量
    age = age + 1
    
    println(s"$name is $age years old")
    
    // 函数定义
    def add(a: Int, b: Int): Int = a + b
    val result = add(5, 3)
    println(s"5 + 3 = $result")
    
    // 集合操作
    val numbers = List(1, 2, 3, 4, 5)
    val evenNumbers = numbers.filter(_ % 2 == 0)
    val doubled = numbers.map(_ * 2)
    
    println(s"Original: $numbers")
    println(s"Even numbers: $evenNumbers")
    println(s"Doubled: $doubled")
  }
}