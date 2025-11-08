// 路径依赖类型示例
object PathDependentTypes {
  
  // 1. 基础路径依赖类型示例
  class Graph {
    class Node {
      var connectedNodes: List[Node] = Nil
      
      def connectTo(node: Node): Unit = {
        connectedNodes = node :: connectedNodes
      }
    }
    
    val nodes: scala.collection.mutable.ListBuffer[Node] = scala.collection.mutable.ListBuffer()
    
    def newNode: Node = {
      val node = new Node
      nodes += node
      node
    }
  }
  
  // 2. 抽象类型成员
  abstract class Food
  abstract class Animal {
    type SuitableFood <: Food
    def eat(food: SuitableFood): Unit
  }
  
  class Grass extends Food
  class Cow extends Animal {
    type SuitableFood = Grass
    override def eat(food: Grass): Unit = println(s"Cow eating $food")
  }
  
  class Fish extends Food
  class Shark extends Animal {
    type SuitableFood = Fish
    override def eat(food: Fish): Unit = println(s"Shark eating $food")
  }
  
  // 3. 路径依赖类型的实际应用
  class Database {
    class Connection {
      def executeQuery(query: String): ResultSet = {
        println(s"Executing query: $query")
        new ResultSet(s"Result of $query")
      }
    }
    
    def getConnection: Connection = new Connection
    
    class ResultSet(val data: String) {
      def getData: String = data
    }
  }
  
  // 4. 依赖类型与类型投影
  class Outer {
    class Inner
    
    def createInner: Inner = new Inner
  }
  
  // 5. 高级路径依赖类型示例
  class Network {
    class Device(val name: String) {
      var connections: List[Network#Device] = Nil
      
      def connectTo(device: Network#Device): Unit = {
        connections = device :: connections
        println(s"${this.name} connected to ${device.name}")
      }
      
      override def toString: String = s"Device($name)"
    }
    
    def createDevice(name: String): Device = new Device(name)
  }
  
  // 6. 类型成员投影
  trait Container {
    type T
    var value: T
    
    def getValue: T = value
    def setValue(newValue: T): Unit = value = newValue
  }
  
  class StringContainer extends Container {
    type T = String
    var value: String = ""
  }
  
  class IntContainer extends Container {
    type T = Int
    var value: Int = 0
  }
  
  // 7. 结构化类型依赖
  class Factory {
    class Product(val id: Int, val name: String) {
      override def toString: String = s"Product($id, $name)"
    }
    
    private var nextId = 1
    
    def createProduct(name: String): Product = {
      val product = new Product(nextId, name)
      nextId += 1
      product
    }
  }
  
  // 8. 类型边界与路径依赖
  abstract class Vehicle {
    type Fuel
    def refuel(fuel: Fuel): Unit
  }
  
  class Gasoline
  class Electric
  
  class Car extends Vehicle {
    type Fuel = Gasoline
    def refuel(fuel: Gasoline): Unit = println("Car refueled with gasoline")
  }
  
  class Tesla extends Vehicle {
    type Fuel = Electric
    def refuel(fuel: Electric): Unit = println("Tesla charged with electricity")
  }
  
  // 9. 路径依赖类型的安全性
  class Bank {
    class Account(val number: String) {
      private var balance: Double = 0.0
      
      def deposit(amount: Double): Unit = {
        balance += amount
        println(s"Deposited $amount to account $number. New balance: $balance")
      }
      
      def withdraw(amount: Double): Unit = {
        if (balance >= amount) {
          balance -= amount
          println(s"Withdrew $amount from account $number. New balance: $balance")
        } else {
          println(s"Insufficient funds in account $number")
        }
      }
      
      def getBalance: Double = balance
    }
    
    def createAccount(number: String): Account = new Account(number)
  }
  
  // 10. 复杂的路径依赖示例
  class Compiler {
    class Symbol(val name: String) {
      var isPublic: Boolean = false
      var isFinal: Boolean = false
      
      override def toString: String = s"Symbol($name)"
    }
    
    class Scope {
      private val symbols = scala.collection.mutable.Map[String, Symbol]()
      
      def defineSymbol(name: String): Symbol = {
        val symbol = new Symbol(name)
        symbols(name) = symbol
        symbol
      }
      
      def lookupSymbol(name: String): Option[Symbol] = symbols.get(name)
    }
    
    def createScope: Scope = new Scope
  }
  
  // 11. 使用示例
  def main(args: Array[String]): Unit = {
    println("=== 路径依赖类型示例 ===")
    
    // 1. 图节点示例
    println("\n--- 图节点示例 ---")
    val graph1 = new Graph
    val graph2 = new Graph
    
    val node1 = graph1.newNode
    val node2 = graph1.newNode
    val node3 = graph2.newNode
    
    node1.connectTo(node2)  // 合法：同一图内的节点
    // node1.connectTo(node3)  // 编译错误：不同图的节点
    
    // 2. 动物和食物示例
    println("\n--- 动物和食物示例 ---")
    val cow = new Cow
    val shark = new Shark
    val grass = new Grass
    val fish = new Fish
    
    cow.eat(grass)    // 合法
    shark.eat(fish)   // 合法
    // cow.eat(fish)     // 编译错误：牛不能吃鱼
    
    // 3. 数据库连接示例
    println("\n--- 数据库连接示例 ---")
    val db = new Database
    val conn = db.getConnection
    val result = conn.executeQuery("SELECT * FROM users")
    println(s"Query result: ${result.getData}")
    
    // 4. 网络设备示例
    println("\n--- 网络设备示例 ---")
    val network = new Network
    val device1 = network.createDevice("Router")
    val device2 = network.createDevice("Switch")
    val device3 = network.createDevice("Computer")
    
    device1.connectTo(device2)
    device2.connectTo(device3)
    
    // 5. 容器示例
    println("\n--- 容器示例 ---")
    val stringContainer = new StringContainer
    val intContainer = new IntContainer
    
    stringContainer.setValue("Hello Scala")
    intContainer.setValue(42)
    
    println(s"String container value: ${stringContainer.getValue}")
    println(s"Int container value: ${intContainer.getValue}")
    
    // 6. 工厂产品示例
    println("\n--- 工厂产品示例 ---")
    val factory = new Factory
    val product1 = factory.createProduct("Laptop")
    val product2 = factory.createProduct("Phone")
    
    println(s"Created products: $product1, $product2")
    
    // 7. 车辆加油示例
    println("\n--- 车辆加油示例 ---")
    val car = new Car
    val tesla = new Tesla
    val gasoline = new Gasoline
    val electric = new Electric
    
    car.refuel(gasoline)    // 合法
    tesla.refuel(electric)  // 合法
    // car.refuel(electric)    // 编译错误：汽车不能充电
    
    // 8. 银行账户示例
    println("\n--- 银行账户示例 ---")
    val bank = new Bank
    val account1 = bank.createAccount("ACC001")
    val account2 = bank.createAccount("ACC002")
    
    account1.deposit(1000)
    account1.withdraw(200)
    account2.deposit(500)
    
    println(s"Account1 balance: ${account1.getBalance}")
    println(s"Account2 balance: ${account2.getBalance}")
    
    // 9. 编译器符号示例
    println("\n--- 编译器符号示例 ---")
    val compiler = new Compiler
    val scope = compiler.createScope
    
    val symbol1 = scope.defineSymbol("main")
    val symbol2 = scope.defineSymbol("helper")
    
    symbol1.isPublic = true
    symbol2.isFinal = true
    
    scope.lookupSymbol("main") match {
      case Some(symbol) => println(s"Found symbol: $symbol")
      case None => println("Symbol not found")
    }
    
    println("\n所有路径依赖类型示例完成")
  }
}