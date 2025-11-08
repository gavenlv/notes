/**
 * 第3章：面向对象编程 - 设计模式示例
 */

// 1. 单例模式（Scala中通过object自然实现）
object Configuration {
  private var _databaseUrl: String = "localhost:5432"
  private var _maxConnections: Int = 10
  
  def databaseUrl: String = _databaseUrl
  def databaseUrl_=(url: String): Unit = _databaseUrl = url
  
  def maxConnections: Int = _maxConnections
  def maxConnections_=(max: Int): Unit = _maxConnections = max
  
  def getConfigInfo: String = s"DB: $databaseUrl, Max Connections: $maxConnections"
}

// 2. 工厂模式
// 产品抽象
abstract class DatabaseConnection {
  def connect(): String
  def disconnect(): String
  def executeQuery(query: String): String
}

// 具体产品
class MySQLConnection extends DatabaseConnection {
  def connect(): String = "Connected to MySQL"
  def disconnect(): String = "Disconnected from MySQL"
  def executeQuery(query: String): String = s"MySQL executing: $query"
}

class PostgreSQLConnection extends DatabaseConnection {
  def connect(): String = "Connected to PostgreSQL"
  def disconnect(): String = "Disconnected from PostgreSQL"
  def executeQuery(query: String): String = s"PostgreSQL executing: $query"
}

class MongoDBConnection extends DatabaseConnection {
  def connect(): String = "Connected to MongoDB"
  def disconnect(): String = "Disconnected from MongoDB"
  def executeQuery(query: String): String = s"MongoDB executing: $query"
}

// 工厂
object DatabaseConnectionFactory {
  def createConnection(dbType: String): DatabaseConnection = {
    dbType.toLowerCase match {
      case "mysql" => new MySQLConnection
      case "postgresql" => new PostgreSQLConnection
      case "mongodb" => new MongoDBConnection
      case _ => throw new IllegalArgumentException(s"Unsupported database type: $dbType")
    }
  }
}

// 3. 建造者模式
case class Computer(
  cpu: String,
  ram: String,
  storage: String,
  gpu: Option[String] = None,
  motherboard: Option[String] = None
) {
  override def toString: String = {
    s"Computer(CPU: $cpu, RAM: $ram, Storage: $storage, GPU: ${gpu.getOrElse("None")}, Motherboard: ${motherboard.getOrElse("None")})"
  }
}

class ComputerBuilder {
  private var cpu: String = _
  private var ram: String = _
  private var storage: String = _
  private var gpu: Option[String] = None
  private var motherboard: Option[String] = None
  
  def setCpu(cpu: String): ComputerBuilder = {
    this.cpu = cpu
    this
  }
  
  def setRam(ram: String): ComputerBuilder = {
    this.ram = ram
    this
  }
  
  def setStorage(storage: String): ComputerBuilder = {
    this.storage = storage
    this
  }
  
  def setGpu(gpu: String): ComputerBuilder = {
    this.gpu = Some(gpu)
    this
  }
  
  def setMotherboard(motherboard: String): ComputerBuilder = {
    this.motherboard = Some(motherboard)
    this
  }
  
  def build(): Computer = {
    if (cpu == null || ram == null || storage == null) {
      throw new IllegalStateException("CPU, RAM and Storage must be set")
    }
    Computer(cpu, ram, storage, gpu, motherboard)
  }
}

// 4. 装饰器模式
trait Coffee {
  def cost(): Double
  def description(): String
}

class SimpleCoffee extends Coffee {
  def cost(): Double = 2.0
  def description(): String = "Simple coffee"
}

trait CoffeeDecorator extends Coffee {
  protected val coffee: Coffee
  
  def cost(): Double = coffee.cost()
  def description(): String = coffee.description()
}

class Milk(coffee: Coffee) extends CoffeeDecorator {
  override val coffee: Coffee = coffee
  
  override def cost(): Double = coffee.cost() + 0.5
  override def description(): String = coffee.description() + ", milk"
}

class Sugar(coffee: Coffee) extends CoffeeDecorator {
  override val coffee: Coffee = coffee
  
  override def cost(): Double = coffee.cost() + 0.2
  override def description(): String = coffee.description() + ", sugar"
}

class Whip(coffee: Coffee) extends CoffeeDecorator {
  override val coffee: Coffee = coffee
  
  override def cost(): Double = coffee.cost() + 0.7
  override def description(): String = coffee.description() + ", whip"
}

// 5. 观察者模式
trait Observer {
  def update(subject: Subject): Unit
}

trait Subject {
  private var observers: List[Observer] = List()
  
  def addObserver(observer: Observer): Unit = {
    observers = observer :: observers
  }
  
  def removeObserver(observer: Observer): Unit = {
    observers = observers.filter(_ != observer)
  }
  
  def notifyObservers(): Unit = {
    observers.foreach(_.update(this))
  }
}

class NewsAgency extends Subject {
  private var news: String = ""
  
  def publishNews(news: String): Unit = {
    this.news = news
    notifyObservers()
  }
  
  def getNews: String = news
}

class NewsChannel(val name: String) extends Observer {
  def update(subject: Subject): Unit = {
    subject match {
      case agency: NewsAgency =>
        println(s"$name received news: ${agency.getNews}")
      case _ =>
    }
  }
}

// 6. 策略模式
trait SortStrategy[T] {
  def sort(data: List[T]): List[T]
}

class BubbleSort[T <% Ordered[T]] extends SortStrategy[T] {
  def sort(data: List[T]): List[T] = {
    // 简化的冒泡排序实现
    data.sortWith(_ < _)
  }
}

class QuickSort[T <% Ordered[T]] extends SortStrategy[T] {
  def sort(data: List[T]): List[T] = {
    if (data.length <= 1) {
      data
    } else {
      val pivot = data.head
      val (smaller, bigger) = data.tail.partition(_ < pivot)
      sort(smaller) ::: pivot :: sort(bigger)
    }
  }
}

class SortContext[T <% Ordered[T]](var strategy: SortStrategy[T]) {
  def setStrategy(strategy: SortStrategy[T]): Unit = {
    this.strategy = strategy
  }
  
  def executeSort(data: List[T]): List[T] = {
    strategy.sort(data)
  }
}

// 7. 模板方法模式
abstract class DataProcessor {
  // 模板方法，定义算法骨架
  def processData(): Unit = {
    readData()
    processDataInternal()
    writeData()
    hook()
  }
  
  // 具体方法
  private def readData(): Unit = {
    println("Reading data...")
  }
  
  private def writeData(): Unit = {
    println("Writing data...")
  }
  
  // 抽象方法，由子类实现
  protected def processDataInternal(): Unit
  
  // 钩子方法，可选实现
  protected def hook(): Unit = {}
}

class CSVDataProcessor extends DataProcessor {
  protected def processDataInternal(): Unit = {
    println("Processing CSV data...")
  }
  
  override protected def hook(): Unit = {
    println("Validating CSV data...")
  }
}

class JSONDataProcessor extends DataProcessor {
  protected def processDataInternal(): Unit = {
    println("Processing JSON data...")
  }
}

// 8. 适配器模式
trait MediaPlayer {
  def play(audioType: String, fileName: String): Unit
}

class AudioPlayer extends MediaPlayer {
  def play(audioType: String, fileName: String): Unit = {
    audioType.toLowerCase match {
      case "mp3" => println(s"Playing MP3 file: $fileName")
      case "mp4" | "vlc" => 
        val adapter = new MediaAdapter(audioType)
        adapter.play(audioType, fileName)
      case _ => println(s"Invalid media type: $audioType")
    }
  }
}

trait AdvancedMediaPlayer {
  def playVlc(fileName: String): Unit
  def playMp4(fileName: String): Unit
}

class VlcPlayer extends AdvancedMediaPlayer {
  def playVlc(fileName: String): Unit = println(s"Playing VLC file: $fileName")
  def playMp4(fileName: String): Unit = {} // 空实现
}

class Mp4Player extends AdvancedMediaPlayer {
  def playVlc(fileName: String): Unit = {} // 空实现
  def playMp4(fileName: String): Unit = println(s"Playing MP4 file: $fileName")
}

class MediaAdapter(audioType: String) extends MediaPlayer {
  private var advancedMusicPlayer: AdvancedMediaPlayer = _
  
  if (audioType.equalsIgnoreCase("vlc")) {
    advancedMusicPlayer = new VlcPlayer()
  } else if (audioType.equalsIgnoreCase("mp4")) {
    advancedMusicPlayer = new Mp4Player()
  }
  
  def play(audioType: String, fileName: String): Unit = {
    if (audioType.equalsIgnoreCase("vlc")) {
      advancedMusicPlayer.playVlc(fileName)
    } else if (audioType.equalsIgnoreCase("mp4")) {
      advancedMusicPlayer.playMp4(fileName)
    }
  }
}

// 主程序入口
object DesignPatternsDemo extends App {
  println("=== 设计模式示例 ===")
  
  // 1. 单例模式演示
  println("\n=== 单例模式演示 ===")
  println(Configuration.getConfigInfo)
  Configuration.databaseUrl = "prod.db.server:5432"
  Configuration.maxConnections = 20
  println(s"Updated config: ${Configuration.getConfigInfo}")
  
  // 2. 工厂模式演示
  println("\n=== 工厂模式演示 ===")
  val mysqlConn = DatabaseConnectionFactory.createConnection("mysql")
  val postgresConn = DatabaseConnectionFactory.createConnection("postgresql")
  val mongoConn = DatabaseConnectionFactory.createConnection("mongodb")
  
  println(mysqlConn.connect())
  println(mysqlConn.executeQuery("SELECT * FROM users"))
  println(mysqlConn.disconnect())
  
  println(postgresConn.connect())
  println(postgresConn.executeQuery("SELECT * FROM products"))
  println(postgresConn.disconnect())
  
  println(mongoConn.connect())
  println(mongoConn.executeQuery("{find: 'users'}"))
  println(mongoConn.disconnect())
  
  // 3. 建造者模式演示
  println("\n=== 建造者模式演示 ===")
  val computer = new ComputerBuilder()
    .setCpu("Intel i9")
    .setRam("32GB DDR4")
    .setStorage("1TB SSD")
    .setGpu("NVIDIA RTX 4090")
    .setMotherboard("ASUS ROG")
    .build()
  
  println(computer)
  
  // 4. 装饰器模式演示
  println("\n=== 装饰器模式演示 ===")
  val simpleCoffee = new SimpleCoffee
  println(s"${simpleCoffee.description()}: $${simpleCoffee.cost()}")
  
  val coffeeWithMilk = new Milk(simpleCoffee)
  println(s"${coffeeWithMilk.description()}: $${coffeeWithMilk.cost()}")
  
  val coffeeWithMilkAndSugar = new Sugar(coffeeWithMilk)
  println(s"${coffeeWithMilkAndSugar.description()}: $${coffeeWithMilkAndSugar.cost()}")
  
  val luxuryCoffee = new Whip(new Sugar(new Milk(new SimpleCoffee)))
  println(s"${luxuryCoffee.description()}: $${luxuryCoffee.cost()}")
  
  // 5. 观察者模式演示
  println("\n=== 观察者模式演示 ===")
  val agency = new NewsAgency
  val cnn = new NewsChannel("CNN")
  val bbc = new NewsChannel("BBC")
  val fox = new NewsChannel("Fox News")
  
  agency.addObserver(cnn)
  agency.addObserver(bbc)
  agency.addObserver(fox)
  
  agency.publishNews("Breaking: New Scala version released!")
  
  agency.removeObserver(fox)
  agency.publishNews("Update: Scala 3.5 adds new features")
  
  // 6. 策略模式演示
  println("\n=== 策略模式演示 ===")
  val bubbleSort = new BubbleSort[Int]
  val quickSort = new QuickSort[Int]
  
  val context = new SortContext[Int](bubbleSort)
  val data = List(64, 34, 25, 12, 22, 11, 90)
  
  println(s"Original data: $data")
  println(s"Bubble sorted: ${context.executeSort(data)}")
  
  context.setStrategy(quickSort)
  println(s"Quick sorted: ${context.executeSort(data)}")
  
  // 7. 模板方法模式演示
  println("\n=== 模板方法模式演示 ===")
  val csvProcessor = new CSVDataProcessor
  val jsonProcessor = new JSONDataProcessor
  
  println("Processing CSV data:")
  csvProcessor.processData()
  
  println("\nProcessing JSON data:")
  jsonProcessor.processData()
  
  // 8. 适配器模式演示
  println("\n=== 适配器模式演示 ===")
  val player = new AudioPlayer
  
  player.play("mp3", "song.mp3")
  player.play("mp4", "movie.mp4")
  player.play("vlc", "video.vlc")
  player.play("avi", "clip.avi")
}