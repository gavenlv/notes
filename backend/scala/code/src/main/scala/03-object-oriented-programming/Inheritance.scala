/**
 * 第3章：面向对象编程 - 继承示例
 */

// 1. 基础继承结构
abstract class Vehicle(val brand: String, val model: String) {
  // 抽象字段
  val maxSpeed: Int
  
  // 抽象方法
  def startEngine(): String
  
  // 具体方法
  def stopEngine(): String = s"$brand $model engine stopped"
  
  // 可重写的方法
  def drive(): String = s"$brand $model is driving"
  
  override def toString: String = s"Vehicle(brand=$brand, model=$model)"
}

// 2. 具体实现类
class Car(brand: String, model: String, val doors: Int) extends Vehicle(brand, model) {
  val maxSpeed: Int = 200
  
  override def startEngine(): String = s"Car $brand $model engine started with a roar"
  
  override def drive(): String = s"Car $brand $model is driving smoothly on the road"
  
  // Car特有的方法
  def honk(): String = "Beep beep!"
  
  override def toString: String = s"Car(brand=$brand, model=$model, doors=$doors)"
}

class Motorcycle(brand: String, model: String, val engineCC: Int) extends Vehicle(brand, model) {
  val maxSpeed: Int = 300
  
  override def startEngine(): String = s"Motorcycle $brand $model engine started with a vroom"
  
  override def drive(): String = s"Motorcycle $brand $model is zooming down the highway"
  
  // Motorcycle特有的方法
  def wheelie(): String = "Performing a wheelie!"
  
  override def toString: String = s"Motorcycle(brand=$brand, model=$model, engineCC=$engineCC)"
}

// 3. 多层继承
class SportsCar(brand: String, model: String, doors: Int, val turbo: Boolean) 
  extends Car(brand, model, doors) {
  
  override val maxSpeed: Int = if (turbo) 350 else 280
  
  override def startEngine(): String = {
    val base = super.startEngine()
    if (turbo) s"$base with turbo boost!" else base
  }
  
  override def drive(): String = {
    val base = super.drive()
    s"$base at high speed"
  }
  
  def activateTurbo(): String = {
    if (turbo) "Turbo activated! Maximum speed reached!" 
    else "No turbo available"
  }
  
  override def toString: String = s"SportsCar(brand=$brand, model=$model, doors=$doors, turbo=$turbo)"
}

// 4. 密封类（Sealed Classes）
sealed abstract class Shape {
  def area: Double
  def perimeter: Double
}

case class Circle(radius: Double) extends Shape {
  def area: Double = math.Pi * radius * radius
  def perimeter: Double = 2 * math.Pi * radius
}

case class Rectangle(width: Double, height: Double) extends Shape {
  def area: Double = width * height
  def perimeter: Double = 2 * (width + height)
}

case class Triangle(a: Double, b: Double, c: Double) extends Shape {
  def area: Double = {
    // 使用海伦公式计算三角形面积
    val s = (a + b + c) / 2
    math.sqrt(s * (s - a) * (s - b) * (s - c))
  }
  
  def perimeter: Double = a + b + c
}

// 5. 参数化类型和继承
abstract class Container[T] {
  def put(item: T): Unit
  def get(): T
  def isEmpty: Boolean
}

class SimpleContainer[T] extends Container[T] {
  private var item: Option[T] = None
  
  def put(item: T): Unit = {
    this.item = Some(item)
  }
  
  def get(): T = {
    item.getOrElse(throw new NoSuchElementException("Container is empty"))
  }
  
  def isEmpty: Boolean = item.isEmpty
}

class Stack[T] extends Container[T] {
  private var items: List[T] = List.empty
  
  def push(item: T): Unit = {
    items = item :: items
  }
  
  def pop(): T = {
    items match {
      case head :: tail =>
        items = tail
        head
      case Nil =>
        throw new NoSuchElementException("Stack is empty")
    }
  }
  
  // 实现Container接口
  def put(item: T): Unit = push(item)
  def get(): T = pop()
  def isEmpty: Boolean = items.isEmpty
  
  def size: Int = items.length
}

// 6. 自身类型（Self-type）
trait User {
  def username: String
  def email: String
}

trait UserRepository {
  self: User =>  // 自身类型声明
  
  def save(): String = s"Saving user $username with email $email"
  def validate(): Boolean = email.contains("@")
}

class RegisteredUser(val username: String, val email: String) extends User with UserRepository

// 7. 构造器继承和初始化顺序
class Animal(val name: String) {
  val animalType: String = "Generic Animal"
  println(s"Animal constructor: $name, type: $animalType")
  
  def makeSound(): String = "Some generic sound"
}

class Mammal(name: String, val furColor: String) extends Animal(name) {
  override val animalType: String = "Mammal"
  println(s"Mammal constructor: $name, fur color: $furColor")
  
  override def makeSound(): String = "Mammal sound"
}

class Dog2(name: String, furColor: String, val breed: String) extends Mammal(name, furColor) {
  override val animalType: String = "Dog"
  println(s"Dog constructor: $name, breed: $breed")
  
  override def makeSound(): String = s"$breed dog barks"
}

// 主程序入口
object InheritanceDemo extends App {
  println("=== 继承示例 ===")
  
  // 1. 基础继承演示
  val car = new Car("Toyota", "Camry", 4)
  val motorcycle = new Motorcycle("Harley-Davidson", "Street 750", 750)
  val sportsCar = new SportsCar("Ferrari", "F8 Tributo", 2, true)
  
  println(car.startEngine())
  println(motorcycle.startEngine())
  println(sportsCar.startEngine())
  
  println(car.drive())
  println(motorcycle.drive())
  println(sportsCar.drive())
  
  println(car.honk())
  println(motorcycle.wheelie())
  println(sportsCar.activateTurbo())
  
  // 2. 多态性演示
  val vehicles: Array[Vehicle] = Array(car, motorcycle, sportsCar)
  
  println("\n=== 多态性演示 ===")
  vehicles.foreach { vehicle =>
    println(vehicle.startEngine())
    println(vehicle.drive())
    println(vehicle.stopEngine())
    println("---")
  }
  
  // 3. 密封类模式匹配
  println("\n=== 密封类模式匹配 ===")
  val shapes: Array[Shape] = Array(
    Circle(5.0),
    Rectangle(4.0, 6.0),
    Triangle(3.0, 4.0, 5.0)
  )
  
  shapes.foreach { shape =>
    shape match {
      case Circle(radius) => 
        println(f"Circle - Area: ${shape.area}%.2f, Perimeter: ${shape.perimeter}%.2f")
      case Rectangle(width, height) => 
        println(f"Rectangle - Area: ${shape.area}%.2f, Perimeter: ${shape.perimeter}%.2f")
      case Triangle(a, b, c) => 
        println(f"Triangle - Area: ${shape.area}%.2f, Perimeter: ${shape.perimeter}%.2f")
    }
  }
  
  // 4. 参数化类型继承
  println("\n=== 参数化类型继承 ===")
  val container = new SimpleContainer[String]()
  container.put("Hello, Scala!")
  println(s"Container content: ${container.get()}")
  
  val stack = new Stack[Int]()
  stack.push(1)
  stack.push(2)
  stack.push(3)
  println(s"Stack size: ${stack.size}")
  println(s"Popped: ${stack.pop()}")
  println(s"Popped: ${stack.pop()}")
  println(s"Stack size: ${stack.size}")
  
  // 5. 自身类型演示
  println("\n=== 自身类型演示 ===")
  val user = new RegisteredUser("john_doe", "john@example.com")
  println(user.save())
  println(s"User validation: ${user.validate()}")
  
  val invalidUser = new RegisteredUser("jane", "invalid-email")
  println(s"Invalid user validation: ${invalidUser.validate()}")
  
  // 6. 构造器初始化顺序
  println("\n=== 构造器初始化顺序 ===")
  val dog = new Dog2("Buddy", "Brown", "Golden Retriever")
  println(dog.makeSound())
}