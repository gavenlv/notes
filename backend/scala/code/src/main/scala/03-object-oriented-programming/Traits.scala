/**
 * 第3章：面向对象编程 - 特质示例
 */

// 1. 基础特质定义
trait Speaker {
  def speak(): String
}

trait Walker {
  def walk(): String = "Walking..."
  
  // 抽象字段
  val legs: Int
  
  // 具体字段
  val species: String = "Unknown"
}

trait Swimmer {
  def swim(): String = "Swimming..."
}

// 2. 类混入特质
class Human(val name: String) extends Speaker with Walker {
  val legs: Int = 2
  override val species: String = "Homo sapiens"
  
  def speak(): String = s"$name says hello!"
  
  override def walk(): String = s"$name is walking on $legs legs"
}

class Duck(val name: String) extends Speaker with Walker with Swimmer {
  val legs: Int = 2
  override val species: String = "Anas platyrhynchos"
  
  def speak(): String = s"$name quacks!"
  
  override def walk(): String = s"$name waddles on $legs legs"
  
  override def swim(): String = s"$name glides gracefully through water"
}

// 3. 特质中的具体实现
trait Timestamped {
  val createdAt: Long = System.currentTimeMillis()
  
  def timestampInfo(): String = s"Created at: ${new java.util.Date(createdAt)}"
}

trait Identifiable {
  val id: String = java.util.UUID.randomUUID().toString
  
  def identityInfo(): String = s"ID: $id"
}

class Document(val title: String) extends Timestamped with Identifiable {
  def documentInfo(): String = s"Document '$title' ($identityInfo()) $timestampInfo()"
}

// 4. 特质中的抽象和具体成员
trait Logger {
  // 抽象成员
  val logLevel: String
  
  // 具体成员
  def log(message: String): Unit = {
    println(s"[$logLevel] $message")
  }
  
  def debug(message: String): Unit = {
    if (logLevel == "DEBUG" || logLevel == "INFO") log(s"DEBUG: $message")
  }
  
  def info(message: String): Unit = {
    if (logLevel == "INFO") log(s"INFO: $message")
  }
}

trait FileLogger extends Logger {
  val filename: String
  
  abstract override def log(message: String): Unit = {
    // 调用混入该特质左边的log方法
    super.log(message)
    // 添加文件日志功能
    println(s"[FILE] Logged to $filename: $message")
  }
}

class Service extends Logger {
  val logLevel: String = "INFO"
}

class FileService(val filename: String) extends Service with FileLogger {
  // FileLogger中的filename字段需要在这里实现
}

// 5. 特质叠加（Trait Stacking）
trait Incrementer {
  def increment(x: Int): Int = x + 1
}

trait Doubler extends Incrementer {
  abstract override def increment(x: Int): Int = {
    super.increment(x) * 2
  }
}

trait Tripler extends Incrementer {
  abstract override def increment(x: Int): Int = {
    super.increment(x) * 3
  }
}

class BaseIncrementer extends Incrementer

class DoubleIncrementer extends BaseIncrementer with Doubler

class TripleIncrementer extends BaseIncrementer with Tripler

class DoubleTripleIncrementer extends BaseIncrementer with Doubler with Tripler

// 6. 自身类型与特质
trait Database {
  def connect(): String
  def disconnect(): String
}

trait UserService {
  self: Database =>  // UserService需要Database功能
  
  def getUser(id: Int): String = {
    connect()
    val user = s"User $id retrieved"
    disconnect()
    user
  }
}

class MySQLDatabase extends Database {
  def connect(): String = "Connected to MySQL"
  def disconnect(): String = "Disconnected from MySQL"
}

class MySQLUserService extends MySQLDatabase with UserService

// 7. 富接口（Rich Interface）
trait Collection[T] {
  // 基本操作（抽象）
  def add(item: T): Unit
  def remove(item: T): Boolean
  def contains(item: T): Boolean
  def size: Int
  
  // 富接口（基于基本操作的具体实现）
  def isEmpty: Boolean = size == 0
  
  def addAll(items: Iterable[T]): Unit = {
    items.foreach(add)
  }
  
  def removeAll(items: Iterable[T]): Int = {
    items.count(remove)
  }
  
  def filter(predicate: T => Boolean): List[T] = {
    // 这是一个简化实现，实际应该返回一个新的Collection
    var result = List[T]()
    // 遍历集合并应用谓词的逻辑在这里省略
    result
  }
}

class StringSet extends Collection[String] {
  private var items = Set[String]()
  
  def add(item: String): Unit = {
    items += item
  }
  
  def remove(item: String): Boolean = {
    val contained = items.contains(item)
    items -= item
    contained
  }
  
  def contains(item: String): Boolean = items.contains(item)
  
  def size: Int = items.size
}

// 8. 特质参数（Scala 3特性）
trait Configurable(config: Map[String, String]) {
  def getConfig(key: String): Option[String] = config.get(key)
  def getAllConfig: Map[String, String] = config
}

class AppConfig(config: Map[String, String]) extends Configurable(config)

// 主程序入口
object TraitsDemo extends App {
  println("=== 特质示例 ===")
  
  // 1. 基础特质演示
  val human = new Human("Alice")
  val duck = new Duck("Donald")
  
  println(human.speak())
  println(human.walk())
  println(s"Species: ${human.species}")
  
  println(duck.speak())
  println(duck.walk())
  println(duck.swim())
  println(s"Species: ${duck.species}")
  
  // 2. 特质中的具体实现
  println("\n=== 特质中的具体实现 ===")
  val document = new Document("Scala Guide")
  println(document.documentInfo())
  
  // 3. 特质叠加演示
  println("\n=== 特质叠加演示 ===")
  val service = new FileService("app.log")
  service.log("Application started")
  service.debug("Debug information")
  service.info("Information message")
  
  // 4. 特质叠加顺序
  println("\n=== 特质叠加顺序 ===")
  val baseInc = new BaseIncrementer
  val doubleInc = new DoubleIncrementer
  val tripleInc = new TripleIncrementer
  val doubleTripleInc = new DoubleTripleIncrementer
  
  println(s"Base increment of 5: ${baseInc.increment(5)}")
  println(s"Double increment of 5: ${doubleInc.increment(5)}")
  println(s"Triple increment of 5: ${tripleInc.increment(5)}")
  println(s"Double then triple increment of 5: ${doubleTripleInc.increment(5)}")
  
  // 5. 自身类型演示
  println("\n=== 自身类型演示 ===")
  val userService = new MySQLUserService
  println(userService.getUser(123))
  
  // 6. 富接口演示
  println("\n=== 富接口演示 ===")
  val stringSet = new StringSet
  stringSet.add("Scala")
  stringSet.add("Java")
  stringSet.add("Python")
  
  println(s"Set size: ${stringSet.size}")
  println(s"Contains Scala: ${stringSet.contains("Scala")}")
  println(s"Is empty: ${stringSet.isEmpty}")
  
  stringSet.remove("Java")
  println(s"Set size after removing Java: ${stringSet.size}")
  
  stringSet.addAll(List("Go", "Rust"))
  println(s"Set size after adding Go and Rust: ${stringSet.size}")
  
  // 7. 特质参数演示（如果使用Scala 3）
  println("\n=== 特质参数演示 ===")
  val config = Map("host" -> "localhost", "port" -> "8080", "debug" -> "true")
  val appConfig = new AppConfig(config)
  
  println(s"Host: ${appConfig.getConfig("host").getOrElse("Not found")}")
  println(s"Port: ${appConfig.getConfig("port").getOrElse("Not found")}")
  println(s"Debug: ${appConfig.getConfig("debug").getOrElse("Not found")}")
  println(s"All config: ${appConfig.getAllConfig}")
}