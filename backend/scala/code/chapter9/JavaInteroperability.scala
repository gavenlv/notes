// Scala与Java互操作示例

import java.util.{ArrayList, HashMap, List as JList, Map as JMap}
import java.time.{LocalDate, LocalDateTime}
import java.io.{File, FileReader}
import scala.jdk.CollectionConverters._
import scala.util.{Try, Success, Failure}

// 1. 在Scala中使用Java类库
object UsingJavaLibraries {
  // 导入和使用Java集合
  def demonstrateJavaCollections(): Unit = {
    // 创建Java列表
    val javaList = new ArrayList[String]()
    javaList.add("Scala")
    javaList.add("Java")
    javaList.add("Kotlin")
    
    // 在Scala中使用Java列表
    println("Java list size: " + javaList.size())
    println("Element at index 0: " + javaList.get(0))
    
    // 转换为Scala集合
    val scalaList: List[String] = javaList.asScala.toList
    println("Scala list: " + scalaList)
    
    // 创建Java映射
    val javaMap = new HashMap[String, Integer]()
    javaMap.put("one", 1)
    javaMap.put("two", 2)
    javaMap.put("three", 3)
    
    // 转换为Scala映射
    val scalaMap: Map[String, Int] = javaMap.asScala.toMap
    println("Scala map: " + scalaMap)
  }
  
  // 使用Java时间API
  def demonstrateJavaTimeAPI(): Unit = {
    // 当前日期和时间
    val today = LocalDate.now()
    val now = LocalDateTime.now()
    
    println(s"Today: $today")
    println(s"Now: $now")
    
    // 创建特定日期
    val birthday = LocalDate.of(1990, java.time.Month.JANUARY, 15)
    println(s"Birthday: $birthday")
    
    // 日期计算
    val nextWeek = today.plusWeeks(1)
    val lastMonth = today.minusMonths(1)
    
    println(s"Next week: $nextWeek")
    println(s"Last month: $lastMonth")
    
    // 格式化日期
    val formatter = java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")
    val formattedDateTime = now.format(formatter)
    println(s"Formatted datetime: $formattedDateTime")
    
    // 解析日期
    val parsedDate = LocalDate.parse("2023-12-25")
    println(s"Parsed date: $parsedDate")
    
    // 计算两个日期之间的天数
    val daysBetween = java.time.temporal.ChronoUnit.DAYS.between(birthday, today)
    println(s"Days between birthday and today: $daysBetween")
  }
  
  // Java异常处理
  def demonstrateJavaExceptions(): Unit = {
    // 使用Try包装Java异常
    def readFileFunctional(filepath: String): Try[String] = Try {
      val reader = new FileReader(filepath)
      val content = reader.read().toString
      reader.close()
      content
    }
    
    val fileExists = "existing_file.txt"  // 假设此文件存在
    val fileNotExists = "non_existing_file.txt"  // 此文件不存在
    
    // 处理可能存在的文件
    val result1 = readFileFunctional(fileExists)
    val result2 = readFileFunctional(fileNotExists)
    
    result1 match {
      case Success(content) => println(s"File content: $content")
      case Failure(ex) => println(s"Error reading file: ${ex.getMessage}")
    }
    
    result2 match {
      case Success(content) => println(s"File content: $content")
      case Failure(ex) => println(s"Error reading file: ${ex.getMessage}")
    }
  }
}

// 2. 在Java中可调用的Scala代码
class ScalaClass(private var name: String) {
  // 公共方法
  def getName: String = name
  
  def setName(name: String): Unit = {
    this.name = name
  }
  
  // 带默认参数的方法
  def greet(greeting: String = "Hello"): String = s"$greeting, $name!"
  
  // 使用Scala特性
  def processList[T](list: List[T]): List[T] = list.filter(_ != null)
  
  // 选项类型
  def findElement[T](list: List[T], element: T): Option[T] = list.find(_ == element)
  
  // 元组返回值
  def divideAndRemainder(dividend: Int, divisor: Int): (Int, Int) = (dividend / divisor, dividend % divisor)
}

// Scala对象（单例）
object ScalaUtils {
  def add(a: Int, b: Int): Int = a + b
  
  def multiply(a: Int, b: Int): Int = a * b
  
  def factorial(n: Int): BigInt = {
    if (n <= 1) 1
    else n * factorial(n - 1)
  }
}

// Scala case class
case class Person(name: String, age: Int) {
  def isAdult: Boolean = age >= 18
  
  def greet: String = s"Hi, I'm $name and I'm $age years old"
}

// 3. 隐式转换与类型适配
object ConversionsAndAdapters {
  // 隐式转换类，方便Java和Scala类型之间的转换
  object JavaConversions {
    // Java Date -> Scala LocalDate
    implicit def dateToLocalDate(date: java.util.Date): LocalDate = {
      date.toInstant.atZone(java.time.ZoneId.systemDefault()).toLocalDate
    }
    
    // LocalDate -> Java Date
    implicit def localDateToDate(date: LocalDate): java.util.Date = {
      java.sql.Date.valueOf(date)
    }
    
    // Java List -> Scala List
    implicit def javaListToScalaList[T](javaList: JList[T]): List[T] = {
      javaList.asScala.toList
    }
    
    // Scala List -> Java List
    implicit def scalaListToJavaList[T](scalaList: List[T]): JList[T] = {
      scalaList.asJava
    }
  }
  
  // 隐式类增强Java集合
  implicit class RichJavaList[T](list: JList[T]) {
    def filter(predicate: T => Boolean): JList[T] = {
      val filtered = list.asScala.filter(predicate)
      filtered.asJava
    }
    
    def map[R](mapper: T => R): JList[R] = {
      val mapped = list.asScala.map(mapper)
      mapped.asJava
    }
  }
  
  // 隐式类增强Java字符串
  implicit class RichJavaString(str: String) {
    def isPalindrome: Boolean = str == str.reverse
    
    def wordCount: Int = str.split("\\s+").length
    
    def capitalizeWords: String = {
      str.split("\\s+").map(_.capitalize).mkString(" ")
    }
  }
  
  // 演示隐式转换
  def demonstrate(): Unit = {
    import JavaConversions._
    
    // 使用隐式转换
    val javaDate = new java.util.Date()
    val scalaDate: LocalDate = javaDate  // 自动转换
    println(s"Converted date: $scalaDate")
    
    // 使用隐式类
    val javaList: JList[String] = new java.util.ArrayList()
    javaList.add("apple")
    javaList.add("banana")
    javaList.add("cherry")
    
    // 使用增强的方法
    val filtered = javaList.filter(_.length > 5)
    val mapped = javaList.map(_.toUpperCase)
    
    println(s"Filtered: ${filtered}")
    println(s"Mapped: ${mapped}")
    
    // 使用字符串增强
    val sentence = "hello world from scala"
    println(s"Is palindrome: ${sentence.isPalindrome}")
    println(s"Word count: ${sentence.wordCount}")
    println(s"Capitalized: ${sentence.capitalizeWords}")
  }
}

// 4. JSON处理示例（使用Jackson）
object JsonProcessing {
  import com.fasterxml.jackson.annotation.{JsonProperty, JsonIgnoreProperties}
  import com.fasterxml.jackson.databind.{ObjectMapper, SerializationFeature}
  import com.fasterxml.jackson.module.scala.DefaultScalaModule
  import com.fasterxml.jackson.module.scala.experimental.ScalaObjectMapper
  
  // JSON序列化的类
  @JsonIgnoreProperties(ignoreUnknown = true)
  case class User(
    @JsonProperty("id") id: Long,
    @JsonProperty("name") name: String,
    @JsonProperty("email") email: String,
    @JsonProperty("roles") roles: List[String]
  )
  
  // 创建配置了Scala模块的ObjectMapper
  val mapper = new ObjectMapper() with ScalaObjectMapper
  mapper.registerModule(DefaultScalaModule)
  mapper.configure(SerializationFeature.FAIL_ON_EMPTY_BEANS, false)
  
  def serializeToJson(obj: AnyRef): String = {
    mapper.writeValueAsString(obj)
  }
  
  def deserializeFromJson[T](json: String, clazz: Class[T]): T = {
    mapper.readValue(json, clazz)
  }
  
  def demonstrate(): Unit = {
    // 创建用户对象
    val user = User(1, "John Doe", "john@example.com", List("user", "admin"))
    
    // 序列化为JSON
    val userJson = serializeToJson(user)
    println(s"Serialized user: $userJson")
    
    // 反序列化回对象
    val parsedUser = deserializeFromJson(userJson, classOf[User])
    println(s"Parsed user: $parsedUser")
    
    // 处理集合
    val users = List(
      User(1, "Alice", "alice@example.com", List("user")),
      User(2, "Bob", "bob@example.com", List("user", "admin")),
      User(3, "Charlie", "charlie@example.com", List("admin"))
    )
    
    val usersJson = serializeToJson(users)
    println(s"Serialized users: $usersJson")
    
    // 反序列化集合
    val parsedUsers = mapper.readValue(usersJson, classOf[List[User]])
    println(s"Parsed users: ${parsedUsers.mkString(", ")}")
  }
}

// 5. 性能考虑
object PerformanceConsiderations {
  // 集合转换开销
  def collectionConversionOverhead(): Unit = {
    val scalaList = List.range(0, 1000000)
    
    // 避免不必要的转换
    // 不好：在循环中反复转换
    def inefficientProcessing(): Int = {
      var sum = 0
      for (i <- 0 until 100) {
        val javaList = scalaList.asJava  // 每次都创建新的Java列表
        // 处理javaList...
        sum += javaList.size()
      }
      sum
    }
    
    // 好：转换一次，多次使用
    def efficientProcessing(): Int = {
      val javaList = scalaList.asJava  // 转换一次
      var sum = 0
      for (i <- 0 until 100) {
        // 使用已转换的javaList
        sum += javaList.size()
      }
      sum
    }
    
    println("Comparing collection conversion performance:")
    val start1 = System.currentTimeMillis()
    val result1 = inefficientProcessing()
    val time1 = System.currentTimeMillis() - start1
    
    val start2 = System.currentTimeMillis()
    val result2 = efficientProcessing()
    val time2 = System.currentTimeMillis() - start2
    
    println(s"Inefficient: $time1 ms, Efficient: $time2 ms")
    println(s"Results: $result1, $result2")
  }
  
  // boxing/unboxing开销
  def boxingUnboxingOverhead(): Unit = {
    // 不好：在密集循环中反复装箱/拆箱
    def inefficientSum(): Int = {
      val javaList = new java.util.ArrayList[Integer]()
      javaList.add(1)
      javaList.add(2)
      javaList.add(3)
      
      var sum = 0
      for (i <- 0 until javaList.size()) {
        sum += javaList.get(i)  // 每次访问都需要拆箱
      }
      sum
    }
    
    // 好：批量转换为Scala类型后处理
    def efficientSum(): Int = {
      import scala.jdk.CollectionConverters._
      val javaList = new java.util.ArrayList[Integer]()
      javaList.add(1)
      javaList.add(2)
      javaList.add(3)
      
      val scalaList = javaList.asScala.toList  // 转换一次
      scalaList.sum  // 使用Scala的高效实现
    }
    
    println("Comparing boxing/unboxing performance:")
    val start1 = System.currentTimeMillis()
    val result1 = inefficientSum()
    val time1 = System.currentTimeMillis() - start1
    
    val start2 = System.currentTimeMillis()
    val result2 = efficientSum()
    val time2 = System.currentTimeMillis() - start2
    
    println(s"Inefficient: $time1 ms, Efficient: $time2 ms")
    println(s"Results: $result1, $result2")
  }
}

// 6. 主程序
object JavaInteroperabilityDemo extends App {
  // 1. 在Scala中使用Java类库
  println("=== 在Scala中使用Java类库 ===")
  UsingJavaLibraries.demonstrateJavaCollections()
  UsingJavaLibraries.demonstrateJavaTimeAPI()
  UsingJavaLibraries.demonstrateJavaExceptions()
  
  Thread.sleep(1000)
  
  // 2. 演示Scala类（可供Java调用）
  println("\n=== Scala类（可供Java调用） ===")
  val scalaObj = new ScalaClass("Alice")
  println(s"Name: ${scalaObj.getName()}")
  println(s"Greeting: ${scalaObj.greet()}")
  
  // 处理Scala List
  val scalaList = List("A", null, "B", null, "C")
  val filteredList = scalaObj.processList(scalaList)
  println(s"Filtered list: $filteredList")
  
  // 处理Option
  val found = scalaObj.findElement(scalaList, "B")
  println(s"Found B: $found")
  
  // 处理元组
  val (quotient, remainder) = scalaObj.divideAndRemainder(17, 5)
  println(s"17 / 5 = $quotient remainder $remainder")
  
  // 调用Scala对象
  val sum = ScalaUtils.add(5, 3)
  val product = ScalaUtils.multiply(4, 7)
  println(s"Sum: $sum, Product: $product")
  
  // 使用Scala case class
  val person = Person("Charlie", 25)
  println(s"Person: $person")
  println(s"Is adult: ${person.isAdult()}")
  println(person.greet)
  
  Thread.sleep(1000)
  
  // 3. 隐式转换与类型适配
  println("\n=== 隐式转换与类型适配 ===")
  ConversionsAndAdapters.demonstrate()
  
  Thread.sleep(1000)
  
  // 4. JSON处理
  println("\n=== JSON处理 ===")
  JsonProcessing.demonstrate()
  
  Thread.sleep(1000)
  
  // 5. 性能考虑
  println("\n=== 性能考虑 ===")
  PerformanceConsiderations.collectionConversionOverhead()
  PerformanceConsiderations.boxingUnboxingOverhead()
  
  println("\nJava interoperability demo completed!")
}