// 结构化类型示例
object StructuralTypes {
  
  // 1. 基础结构化类型
  type HasName = {
    def name: String
  }
  
  type HasAge = {
    val age: Int
  }
  
  type HasNameAndAge = HasName with HasAge
  
  // 2. 使用结构化类型的方法
  def greet(obj: HasName): String = s"Hello, ${obj.name}!"
  
  def getAgeInfo(obj: HasAge): String = s"Age: ${obj.age}"
  
  def getFullInfo(obj: HasNameAndAge): String = s"Name: ${obj.name}, Age: ${obj.age}"
  
  // 3. 实现结构化类型的类
  class Person(val name: String, val age: Int) {
    def greet(): String = s"Hi, I'm $name"
  }
  
  class Dog(val name: String) {
    val age: Int = 5
  }
  
  case class Employee(name: String, age: Int, salary: Double)
  
  // 4. 反射式结构化类型
  import scala.language.reflectiveCalls
  
  type Quackable = {
    def quack(): String
  }
  
  type Flyable = {
    def fly(): String
  }
  
  type DuckLike = Quackable with Flyable
  
  class Duck {
    def quack(): String = "Quack! Quack!"
    def fly(): String = "Flying high"
  }
  
  class ToyDuck {
    def quack(): String = "Squeak! Squeak!"
    def fly(): String = "I can't really fly"
  }
  
  // 5. 结构化类型与函数
  type Callable[T] = {
    def apply(): T
  }
  
  def executeCallable[T](callable: Callable[T]): T = callable()
  
  class RandomNumberGenerator {
    def apply(): Int = scala.util.Random.nextInt(100)
  }
  
  // 6. 复杂结构化类型
  type Repository[T] = {
    def save(entity: T): Unit
    def findById(id: Long): Option[T]
    def findAll(): List[T]
    def delete(entity: T): Unit
  }
  
  case class User(id: Long, username: String, email: String)
  
  class InMemoryUserRepository {
    private val users = scala.collection.mutable.Map[Long, User]()
    private var nextId = 1L
    
    def save(entity: User): Unit = {
      val userWithId = if (entity.id == 0) entity.copy(id = nextId) else entity
      users(userWithId.id) = userWithId
      if (entity.id == 0) nextId += 1
    }
    
    def findById(id: Long): Option[User] = users.get(id)
    
    def findAll(): List[User] = users.values.toList
    
    def delete(entity: User): Unit = users.remove(entity.id)
  }
  
  // 7. 结构化类型与泛型
  type Builder[T] = {
    def build(): T
  }
  
  case class Car(brand: String, model: String)
  
  class CarBuilder {
    private var brand: String = ""
    private var model: String = ""
    
    def withBrand(b: String): CarBuilder = {
      brand = b
      this
    }
    
    def withModel(m: String): CarBuilder = {
      model = m
      this
    }
    
    def build(): Car = Car(brand, model)
  }
  
  // 8. 结构化类型约束
  def processEntity[T <: { def id: Long; def name: String }](entity: T): String = {
    s"Processing entity ${entity.name} with id ${entity.id}"
  }
  
  case class Product(id: Long, name: String, price: Double)
  case class Category(id: Long, name: String, description: String)
  
  // 9. 结构化类型与伴生对象
  type MathOperations = {
    def add(a: Int, b: Int): Int
    def multiply(a: Int, b: Int): Int
  }
  
  object BasicMath {
    def add(a: Int, b: Int): Int = a + b
    def multiply(a: Int, b: Int): Int = a * b
  }
  
  // 10. 高级结构化类型示例
  type Configurable = {
    type Config
    def configure(config: Config): Unit
    def getConfig: Config
  }
  
  class DatabaseConfig(val host: String, val port: Int)
  
  class DatabaseConnection {
    type Config = DatabaseConfig
    private var config: DatabaseConfig = _
    
    def configure(config: DatabaseConfig): Unit = {
      this.config = config
      println(s"Database configured with host: ${config.host}, port: ${config.port}")
    }
    
    def getConfig: DatabaseConfig = config
  }
  
  // 11. 结构化类型与隐式转换
  implicit def stringToHasLength(s: String): { def length: Int } = new {
    def length: Int = s.length
  }
  
  def printLength(obj: { def length: Int }): Unit = {
    println(s"Length: ${obj.length}")
  }
  
  // 12. 使用示例
  def main(args: Array[String]): Unit = {
    println("=== 结构化类型示例 ===")
    
    // 1. 基础结构化类型使用
    println("\n--- 基础结构化类型 ---")
    val person = new Person("Alice", 25)
    val dog = new Dog("Buddy")
    val employee = Employee("Bob", 30, 50000.0)
    
    println(greet(person))
    println(getAgeInfo(dog))
    println(getFullInfo(employee))
    
    // 2. Duck typing示例
    println("\n--- Duck typing ---")
    val duck = new Duck
    val toyDuck = new ToyDuck
    
    def makeDuckSound(d: Quackable): Unit = println(d.quack())
    def testFlight(d: Flyable): Unit = println(d.fly())
    
    makeDuckSound(duck)
    makeDuckSound(toyDuck)
    testFlight(duck)
    testFlight(toyDuck)
    
    // 3. Callable示例
    println("\n--- Callable示例 ---")
    val rng = new RandomNumberGenerator
    val randomNum = executeCallable(rng)
    println(s"Random number: $randomNum")
    
    // 4. Repository示例
    println("\n--- Repository示例 ---")
    val userRepository = new InMemoryUserRepository
    val user1 = User(0, "alice", "alice@example.com")
    val user2 = User(0, "bob", "bob@example.com")
    
    userRepository.save(user1)
    userRepository.save(user2)
    
    println(s"All users: ${userRepository.findAll()}")
    println(s"User with id 1: ${userRepository.findById(1)}")
    
    // 5. Builder示例
    println("\n--- Builder示例 ---")
    val carBuilder = new CarBuilder
    val car = carBuilder.withBrand("Toyota").withModel("Camry").build()
    println(s"Built car: $car")
    
    // 6. 结构化类型约束示例
    println("\n--- 结构化类型约束 ---")
    val product = Product(1, "Laptop", 999.99)
    val category = Category(1, "Electronics", "Electronic devices")
    
    println(processEntity(product))
    println(processEntity(category))
    
    // 7. Math operations示例
    println("\n--- Math operations ---")
    def performMathOps(math: MathOperations): Unit = {
      println(s"Addition: ${math.add(5, 3)}")
      println(s"Multiplication: ${math.multiply(5, 3)}")
    }
    
    performMathOps(BasicMath)
    
    // 8. Database configuration示例
    println("\n--- Database configuration ---")
    val dbConnection = new DatabaseConnection
    val dbConfig = new DatabaseConfig("localhost", 5432)
    dbConnection.configure(dbConfig)
    println(s"Current config: ${dbConnection.getConfig}")
    
    // 9. 隐式转换示例
    println("\n--- 隐式转换 ---")
    printLength("Hello Scala")
    printLength(Array(1, 2, 3, 4, 5))
    
    // 10. 综合示例
    println("\n--- 综合示例 ---")
    def processAnyObject(obj: { 
      def name: String
      def toString: String
      def equals(other: Any): Boolean
    }): Unit = {
      println(s"Object name: ${obj.name}")
      println(s"Object toString: ${obj.toString}")
    }
    
    processAnyObject(person)
    processAnyObject(employee)
    
    println("\n所有结构化类型示例完成")
  }
}