object PatternMatching {
  def main(args: Array[String]): Unit = {
    // 基本模式匹配
    def describe(x: Any): String = x match {
      case 1 => "One"
      case 2 => "Two"
      case "hello" => "Greeting"
      case true => "Truth"
      case _ => "Unknown"
    }
    
    println(describe(1))      // One
    println(describe(3))      // Unknown
    println(describe("hello")) // Greeting
    
    // 常量模式与变量模式
    def matchVariable(x: Any): String = x match {
      case x => s"Got value: $x"
      case y => s"This case is unreachable"
    }
    
    println(matchVariable(42))      // Got value: 42
    println(matchVariable("hello")) // Got value: hello
    
    // 构造器模式
    case class Point(x: Int, y: Int)
    
    val p1 = Point(2, 3)
    def describePoint(p: Point): String = p match {
      case Point(0, 0) => "Origin"
      case Point(x, 0) => s"On x-axis at $x"
      case Point(0, y) => s"On y-axis at $y"
      case Point(x, y) => s"Point at ($x, $y)"
    }
    
    println(describePoint(Point(0, 0)))  // Origin
    println(describePoint(Point(2, 0)))  // On x-axis at 2
    println(describePoint(Point(0, 3)))  // On y-axis at 3
    println(describePoint(Point(2, 3)))  // Point at (2, 3)
    
    // 序列模式
    def describeList(lst: List[Int]): String = lst match {
      case Nil => "Empty list"
      case List(x) => s"Single element list: $x"
      case List(x, y) => s"Two element list: $x, $y"
      case x :: y :: rest => s"List starting with $x, $y and ${rest.size} more elements"
    }
    
    println(describeList(List()))               // Empty list
    println(describeList(List(1)))              // Single element list: 1
    println(describeList(List(1, 2)))           // Two element list: 1, 2
    println(describeList(List(1, 2, 3, 4, 5)))  // List starting with 1, 2 and 3 more elements
    
    // 元组模式
    def describeTuple(tuple: Any): String = tuple match {
      case () => "Empty tuple"
      case (x, y) => s"2-tuple: $x, $y"
      case (x, y, z) => s"3-tuple: $x, $y, $z"
      case (x, y, rest @ _*) => s"Tuple starting with $x, $y and ${rest.size} more elements"
    }
    
    println(describeTuple(()))                              // Empty tuple
    println(describeTuple((1, 2)))                           // 2-tuple: 1, 2
    println(describeTuple((1, 2, 3)))                        // 3-tuple: 1, 2, 3
    println(describeTuple((1, 2, 3, 4, 5, 6)))               // Tuple starting with 1, 2 and 4 more elements
    
    // 类型模式
    def typeMatch(x: Any): String = x match {
      case s: String => s"String: $s"
      case i: Int => s"Int: $i"
      case d: Double => s"Double: $d"
      case b: Boolean => s"Boolean: $b"
      case l: List[_] => s"List with ${l.size} elements"
      case m: Map[_, _] => s"Map with ${m.size} key-value pairs"
      case _ => s"Unknown type: ${x.getClass.getSimpleName}"
    }
    
    println(typeMatch("Hello"))                // String: Hello
    println(typeMatch(42))                      // Int: 42
    println(typeMatch(3.14))                    // Double: 3.14
    println(typeMatch(true))                     // Boolean: true
    println(typeMatch(List(1, 2, 3)))           // List with 3 elements
    println(typeMatch(Map("key" -> "value")))    // Map with 1 key-value pairs
    
    // 模式守卫
    def describeNumber(num: Int): String = num match {
      case n if n > 0 => s"$n is positive"
      case n if n < 0 => s"$n is negative"
      case 0 => "Zero"
    }
    
    println(describeNumber(10))  // 10 is positive
    println(describeNumber(-5))  // -5 is negative
    println(describeNumber(0))   // Zero
    
    // 密封类模式匹配
    sealed trait DayOfWeek
    case object Monday extends DayOfWeek
    case object Tuesday extends DayOfWeek
    case object Wednesday extends DayOfWeek
    case object Thursday extends DayOfWeek
    case object Friday extends DayOfWeek
    case object Saturday extends DayOfWeek
    case object Sunday extends DayOfWeek
    
    def isWeekday(day: DayOfWeek): Boolean = day match {
      case Monday | Tuesday | Wednesday | Thursday | Friday => true
      case Saturday | Sunday => false
    }
    
    println(isWeekday(Monday))    // true
    println(isWeekday(Saturday))  // false
  }
}