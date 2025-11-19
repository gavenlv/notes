object ImplicitExamples {
  // 隐式转换类
  implicit class IntOps(i: Int) {
    def squared: Int = i * i
    def times(action: => Unit): Unit = (1 to i).foreach(_ => action)
  }

  // 隐式参数
  trait Show[T] {
    def show(value: T): String
  }

  object Show {
    implicit val intShow: Show[Int] = new Show[Int] {
      def show(value: Int): String = value.toString
    }

    implicit val stringShow: Show[String] = new Show[String] {
      def show(value: String): String = s""""$value""""
    }
  }

  // 使用隐式参数的函数
  def display[T](value: T)(implicit s: Show[T]): Unit = {
    println(s.show(value))
  }

  // 上下文边界
  def process[T: Show](value: T): String = {
    implicitly[Show[T]].show(value)
  }

  // 隐式值
  implicit val delimiter: String = "---"

  // 使用隐式值的函数
  def printWithDelimiter(msg: String)(implicit sep: String): Unit = {
    println(s"$sep$msg$sep")
  }

  def main(args: Array[String]): Unit = {
    // 使用隐式转换
    println(5.squared) // 输出: 25
    
    // 使用隐式参数
    display(42)
    display("Hello, Scala!")
    
    // 使用上下文边界
    println(process(100))
    
    // 使用隐式值
    printWithDelimiter("Implicit Values")
    
    // 隐式转换类的使用
    3.times(println("Hello!"))
  }
}