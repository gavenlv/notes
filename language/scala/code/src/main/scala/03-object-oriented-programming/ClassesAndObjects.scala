/**
 * 第3章：面向对象编程 - 类和对象示例
 */

// 1. 基本类定义
class Person(val name: String, val age: Int) {
  // 字段和方法
  private var _address: String = ""
  
  // getter 和 setter
  def address: String = _address
  def address_=(addr: String): Unit = {
    _address = addr
  }
  
  // 方法定义
  def introduce(): String = {
    s"Hi, I'm $name, $age years old, living in $address"
  }
  
  // 重写toString方法
  override def toString: String = s"Person(name=$name, age=$age, address=$address)"
}

// 2. 辅助构造器
class Employee(val name: String, val age: Int, val department: String) extends Person(name, age) {
  private var _salary: Double = 0.0
  
  def this(name: String, age: Int, department: String, salary: Double) = {
    this(name, age, department)
    _salary = salary
  }
  
  def salary: Double = _salary
  def salary_=(newSalary: Double): Unit = {
    if (newSalary >= 0) _salary = newSalary
  }
  
  override def introduce(): String = {
    s"${super.introduce()}, working in $department with salary $$${salary}"
  }
  
  override def toString: String = s"Employee(name=$name, age=$age, department=$department, salary=$salary)"
}

// 3. 抽象类
abstract class Animal {
  val species: String
  var energy: Int = 100
  
  def makeSound(): String
  def move(): String = {
    energy -= 10
    s"$species is moving, energy left: $energy"
  }
  
  def eat(food: String): String = {
    energy += 20
    s"$species is eating $food, energy increased to $energy"
  }
}

// 4. 具体实现类
class Dog(val name: String) extends Animal {
  val species: String = "Dog"
  
  override def makeSound(): String = s"$name says Woof!"
  
  override def move(): String = {
    energy -= 5  // Dogs are more energetic
    s"$name the dog is running, energy left: $energy"
  }
}

class Cat(val name: String) extends Animal {
  val species: String = "Cat"
  
  override def makeSound(): String = s"$name says Meow!"
  
  // 重写父类方法
  override def eat(food: String): String = {
    energy += 15  // Cats eat less
    s"$name the cat is eating $food delicately, energy increased to $energy"
  }
}

// 5. 伴生对象
object MathUtils {
  val PI = 3.14159
  
  def add(a: Int, b: Int): Int = a + b
  def multiply(a: Int, b: Int): Int = a * b
  def circleArea(radius: Double): Double = PI * radius * radius
  
  // apply方法用于创建实例
  def apply(name: String, age: Int): Person = new Person(name, age)
}

// 6. 伴生类和伴生对象
class Point(val x: Double, val y: Double) {
  def distanceFrom(other: Point): Double = {
    val dx = this.x - other.x
    val dy = this.y - other.y
    math.sqrt(dx * dx + dy * dy)
  }
  
  override def toString: String = s"Point($x, $y)"
}

object Point {
  // 伴生对象中的apply方法
  def apply(x: Double, y: Double): Point = new Point(x, y)
  
  // 常量
  val Origin: Point = new Point(0, 0)
  
  // 工具方法
  def midpoint(p1: Point, p2: Point): Point = {
    new Point((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)
  }
}

// 7. 单例对象
object Counter {
  private var count = 0
  
  def increment(): Int = {
    count += 1
    count
  }
  
  def currentCount: Int = count
  
  def reset(): Unit = {
    count = 0
  }
}

// 8. 枚举（Scala 3特性）
object Color extends Enumeration {
  type Color = Value
  val Red, Green, Blue = Value
}

// 主程序入口
object ClassesAndObjectsDemo extends App {
  println("=== 类和对象示例 ===")
  
  // 1. 创建Person实例
  val person = new Person("Alice", 25)
  person.address = "New York"
  println(person.introduce())
  
  // 2. 使用辅助构造器
  val employee1 = new Employee("Bob", 30, "Engineering")
  employee1.salary = 75000
  println(employee1.introduce())
  
  val employee2 = new Employee("Charlie", 35, "Marketing", 80000)
  println(employee2.toString)
  
  // 3. 动物类演示
  val dog = new Dog("Buddy")
  val cat = new Cat("Whiskers")
  
  println(dog.makeSound())
  println(cat.makeSound())
  
  println(dog.move())
  println(cat.eat("fish"))
  
  // 4. 伴生对象使用
  println(s"PI = ${MathUtils.PI}")
  println(s"5 + 3 = ${MathUtils.add(5, 3)}")
  println(s"Circle area with radius 5 = ${MathUtils.circleArea(5.0)}")
  
  // 使用伴生对象的apply方法创建实例
  val person2 = MathUtils("David", 28)
  println(person2.introduce())
  
  // 5. Point类和伴生对象演示
  val point1 = Point(3.0, 4.0)  // 使用伴生对象的apply方法
  val point2 = Point(6.0, 8.0)
  val origin = Point.Origin
  
  println(s"Point1: $point1")
  println(s"Point2: $point2")
  println(s"Origin: $origin")
  println(s"Distance between point1 and point2: ${point1.distanceFrom(point2)}")
  println(s"Midpoint: ${Point.midpoint(point1, point2)}")
  
  // 6. 计数器单例演示
  println("\n=== 计数器演示 ===")
  println(s"Initial count: ${Counter.currentCount}")
  println(s"After increment: ${Counter.increment()}")
  println(s"After increment: ${Counter.increment()}")
  println(s"Current count: ${Counter.currentCount}")
  Counter.reset()
  println(s"After reset: ${Counter.currentCount}")
  
  // 7. 枚举示例
  println("\n=== 枚举示例 ===")
  val red: Color.Value = Color.Red
  val blue: Color.Value = Color.Blue
  println(s"Colors: $red, $blue")
  
  // 遍历枚举值
  Color.values.foreach(color => println(s"Color: $color"))
}