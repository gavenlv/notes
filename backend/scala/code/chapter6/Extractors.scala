object Extractors {
  def main(args: Array[String]): Unit = {
    // 基本提取器
    object Even {
      def unapply(x: Int): Option[Int] = if (x % 2 == 0) Some(x) else None
    }
    
    object Odd {
      def unapply(x: Int): Option[Int] = if (x % 2 != 0) Some(x) else None
    }
    
    def describeNumber(num: Int): String = num match {
      case Even(x) => s"$x is even"
      case Odd(x) => s"$x is odd"
    }
    
    println(describeNumber(2))  // 2 is even
    println(describeNumber(3))  // 3 is odd
    
    // 返回多个值的提取器
    object NameExtractor {
      def unapply(name: String): Option[(String, Option[String])] = {
        val parts = name.split(" ", 2)
        if (parts.length >= 1) {
          val firstName = parts(0)
          val lastName = if (parts.length == 2) Some(parts(1)) else None
          Some((firstName, lastName))
        } else None
      }
    }
    
    def greet(name: String): String = name match {
      case NameExtractor(firstName, Some(lastName)) => 
        s"Hello, Mr./Ms. $lastName"
      case NameExtractor(firstName, None) => 
        s"Hello, $firstName"
    }
    
    println(greet("John Doe"))    // Hello, Mr./Ms. Doe
    println(greet("Alice"))       // Hello, Alice
    
    // 布尔提取器
    object Capitalized {
      def unapply(s: String): Boolean = s.nonEmpty && s.charAt(0).isUpper
    }
    
    def checkCapitalization(text: String): String = text match {
      case Capitalized() => s"'$text' starts with a capital letter"
      case _ => s"'$text' does not start with a capital letter"
    }
    
    println(checkCapitalization("Hello"))    // 'Hello' starts with a capital letter
    println(checkCapitalization("world"))    // 'world' does not start with a capital letter
    
    // 序列提取器
    object FirstTwo {
      def unapplySeq(list: List[Int]): Option[Seq[Int]] = {
        if (list.length >= 2) Some(Seq(list.head, list(1)))
        else None
      }
    }
    
    def extractFirstTwo(list: List[Int]): String = list match {
      case FirstTwo(a, b, _*) => s"First two elements: $a, $b"
      case List(a) => s"Only one element: $a"
      case Nil => "Empty list"
    }
    
    println(extractFirstTwo(List(1, 2, 3, 4)))  // First two elements: 1, 2
    println(extractFirstTwo(List(5)))           // Only one element: 5
    println(extractFirstTwo(List()))             // Empty list
    
    // 自定义序列提取器
    object EvenNumbers {
      def unapplySeq(numbers: List[Int]): Option[Seq[Int]] = {
        val evens = numbers.filter(_ % 2 == 0)
        if (evens.nonEmpty) Some(evens) else None
      }
    }
    
    def extractEvenNumbers(numbers: List[Int]): String = numbers match {
      case EvenNumbers(evens @ _*) => s"Even numbers: ${evens.mkString(", ")}"
      case _ => "No even numbers found"
    }
    
    println(extractEvenNumbers(List(1, 2, 3, 4, 5)))  // Even numbers: 2, 4
    println(extractEvenNumbers(List(1, 3, 5)))         // No even numbers found
    
    // 提取器与集合操作结合
    object HeadAndTail {
      def unapply[A](list: List[A]): Option[(A, List[A])] = {
        if (list.nonEmpty) Some((list.head, list.tail)) else None
      }
    }
    
    def processList[A](list: List[A]): String = list match {
      case HeadAndTail(head, tail) if tail.isEmpty => s"Single element list: $head"
      case HeadAndTail(head, tail) => s"Head: $head, Tail size: ${tail.size}"
      case _ => "Empty list"
    }
    
    println(processList(List(1)))                  // Single element list: 1
    println(processList(List(1, 2, 3, 4, 5)))     // Head: 1, Tail size: 4
    println(processList(List()))                    // Empty list
    
    // 复杂提取器：URL解析
    object Url {
      def unapply(url: String): Option[(String, String, Option[Int], Option[String], Option[Map[String, String]])] = {
        val urlPattern = """(https?)://([^/:]+)(:[0-9]+)?(/[^?]*)?(\?.*)?""".r
        
        url match {
          case urlPattern(protocol, host, port, path, query) =>
            val portNum = if (port != null) Some(port.substring(1).toInt) else None
            val pathStr = if (path != null) Some(path) else None
            
            val queryParams = if (query != null) {
              val params = query.substring(1).split("&")
              val paramMap = params.map { param =>
                val keyValue = param.split("=", 2)
                if (keyValue.length == 2) (keyValue(0) -> keyValue(1))
                else (keyValue(0) -> "")
              }.toMap
              Some(paramMap)
            } else None
            
            Some((protocol, host, portNum, pathStr, queryParams))
          case _ => None
        }
      }
    }
    
    def parseUrl(url: String): String = url match {
      case Url(protocol, host, Some(port), Some(path), Some(params)) => 
        s"$protocol://$host:$port$path with params: ${params.mkString(", ")}"
      case Url(protocol, host, Some(port), Some(path), None) => 
        s"$protocol://$host:$port$path"
      case Url(protocol, host, None, Some(path), Some(params)) => 
        s"$protocol://$host$path with params: ${params.mkString(", ")}"
      case Url(protocol, host, None, Some(path), None) => 
        s"$protocol://$host$path"
      case Url(protocol, host, _, None, _) => 
        s"$protocol://$host"
      case _ => "Invalid URL"
    }
    
    println(parseUrl("https://example.com:8080/path/to/resource?param1=value1&param2=value2"))
    // https://example.com:8080/path/to/resource with params: param1 -> value1, param2 -> value2
    
    println(parseUrl("http://example.com/path"))
    // http://example.com/path
    
    println(parseUrl("ftp://files.example.com"))
    // ftp://files.example.com
    
    // 自定义提取器：货币
    object Currency {
      def unapply(amount: String): Option[(Double, String)] = {
        val currencyPattern = """([0-9]*\.?[0-9]+)\s*([A-Z]{3})""".r
        
        amount match {
          case currencyPattern(value, currency) => Some((value.toDouble, currency))
          case _ => None
        }
      }
    }
    
    def processAmount(amount: String): String = amount match {
      case Currency(value, "USD") => f"$$value%.2f USD"
      case Currency(value, "EUR") => f"€$value%.2f EUR"
      case Currency(value, currency) => f"$value%.2f $currency"
      case _ => s"Invalid amount format: $amount"
    }
    
    println(processAmount("123.45 USD"))    // $123.45 USD
    println(processAmount("99.99 EUR"))     // €99.99 EUR
    println(processAmount("50.00 GBP"))      // 50.00 GBP
    println(processAmount("invalid amount"))  // Invalid amount format: invalid amount
    
    // 提取器用于验证
    object PositiveInt {
      def unapply(x: Int): Option[Int] = if (x > 0) Some(x) else None
    }
    
    object NegativeInt {
      def unapply(x: Int): Option[Int] = if (x < 0) Some(x) else None
    }
    
    object Prime {
      def unapply(x: Int): Option[Int] = {
        def isPrime(n: Int): Boolean = {
          if (n <= 1) false
          else if (n <= 3) true
          else if (n % 2 == 0 || n % 3 == 0) false
          else {
            var i = 5
            while (i * i <= n && n % i != 0 && n % (i + 2) != 0) {
              i += 6
            }
            i * i > n
          }
        }
        
        if (isPrime(x)) Some(x) else None
      }
    }
    
    def analyzeNumberAdvanced(num: Int): String = num match {
      case PositiveInt(n) if Prime.unapply(n).isDefined => s"$n is a positive prime"
      case PositiveInt(n) => s"$n is positive but not prime"
      case NegativeInt(n) if n % 2 == 0 => s"$n is a negative even number"
      case NegativeInt(n) => s"$n is negative and odd"
      case 0 => "Zero"
    }
    
    println(analyzeNumberAdvanced(7))   // 7 is a positive prime
    println(analyzeNumberAdvanced(9))   // 9 is positive but not prime
    println(analyzeNumberAdvanced(-4))  // -4 is a negative even number
    println(analyzeNumberAdvanced(-5))  // -5 is negative and odd
    println(analyzeNumberAdvanced(0))   // Zero
  }
}