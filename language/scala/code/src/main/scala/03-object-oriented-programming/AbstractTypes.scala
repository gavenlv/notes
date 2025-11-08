/**
 * 第3章：面向对象编程 - 抽象类型示例
 */

// 1. 抽象类型基础
trait Buffer {
  // 抽象类型
  type T
  val element: T
}

trait SeqBuffer extends Buffer {
  // 具体化抽象类型
  type T = Seq[Int]
  val element: T = List(1, 2, 3)
}

// 2. 参数化类型 vs 抽象类型
// 使用参数化类型
trait Container[T] {
  def put(item: T): Unit
  def get(): T
}

// 使用抽象类型
trait Container2 {
  type T
  def put(item: T): Unit
  def get(): T
}

class IntContainer extends Container[Int] {
  private var item: Int = 0
  def put(item: Int): Unit = this.item = item
  def get(): Int = item
}

class StringContainer2 extends Container2 {
  type T = String
  private var item: String = ""
  def put(item: T): Unit = this.item = item
  def get(): T = item
}

// 3. 抽象类型成员
trait Food
class Grass extends Food
class Fish extends Food

abstract class Animal {
  // 抽象类型成员
  type SuitableFood <: Food
  def eat(food: SuitableFood): String
}

class Cow extends Animal {
  // 具体化抽象类型
  type SuitableFood = Grass
  override def eat(food: Grass): String = "Cow is eating grass"
}

class Cat extends Animal {
  type SuitableFood = Fish
  override def eat(food: Fish): String = "Cat is eating fish"
}

// 4. 路径依赖类型
class FoodStore {
  class Meat
  class Vegetable
  
  // 路径依赖类型
  def processMeat(meat: Meat): String = "Processing meat"
  def processVegetable(veg: Vegetable): String = "Processing vegetable"
}

// 5. 自身类型与抽象类型
trait Config {
  type ConfigType
  def getConfig: ConfigType
}

trait DatabaseConfig {
  self: Config =>  // 需要混入Config特质
  
  // 使用Config特质中的抽象类型
  def connect(config: ConfigType): String = s"Connecting with config: $config"
}

class AppConfig extends Config {
  type ConfigType = Map[String, String]
  def getConfig: ConfigType = Map("host" -> "localhost", "port" -> "5432")
}

class AppDatabaseConfig extends AppConfig with DatabaseConfig

// 6. 高级抽象类型约束
trait Collection[T] {
  type ElementType = T
  def add(element: ElementType): Unit
  def contains(element: ElementType): Boolean
}

class IntList extends Collection[Int] {
  private var elements: List[Int] = List()
  
  def add(element: ElementType): Unit = {
    elements = element :: elements
  }
  
  def contains(element: ElementType): Boolean = {
    elements.contains(element)
  }
  
  def getAll: List[ElementType] = elements
}

// 7. 抽象类型上界和下界
trait Animal2
class Dog3 extends Animal2
class Puppy extends Dog3

trait Shelter {
  // 抽象类型上界约束
  type AnimalType <: Animal2
  def adopt(): AnimalType
}

class DogShelter extends Shelter {
  // 具体化抽象类型，使用上界约束
  type AnimalType = Dog3
  
  def adopt(): AnimalType = new Dog3
}

// 8. 结构化类型（使用反射）
import scala.reflect.runtime.universe._

trait TypeTagged[T] {
  val tag: TypeTag[T]
  def getTypeInfo: String = tag.tpe.toString
}

class StringTypeTagged extends TypeTagged[String] {
  val tag: TypeTag[String] = typeTag[String]
}

class IntTypeTagged extends TypeTagged[Int] {
  val tag: TypeTag[Int] = typeTag[Int]
}

// 主程序入口
object AbstractTypesDemo extends App {
  println("=== 抽象类型示例 ===")
  
  // 1. 基础抽象类型演示
  val buffer = new SeqBuffer {}
  println(s"Buffer element: ${buffer.element}")
  println(s"Buffer type: ${buffer.element.getClass.getSimpleName}")
  
  // 2. 参数化类型 vs 抽象类型
  println("\n=== 参数化类型 vs 抽象类型 ===")
  val intContainer = new IntContainer
  intContainer.put(42)
  println(s"Int container value: ${intContainer.get()}")
  
  val stringContainer = new StringContainer2
  stringContainer.put("Hello, Scala!")
  println(s"String container value: ${stringContainer.get()}")
  
  // 3. 抽象类型成员演示
  println("\n=== 抽象类型成员演示 ===")
  val cow = new Cow
  val grass = new Grass
  println(cow.eat(grass))
  
  val cat = new Cat
  val fish = new Fish
  println(cat.eat(fish))
  
  // 4. 路径依赖类型演示
  println("\n=== 路径依赖类型演示 ===")
  val store = new FoodStore
  val meat = new store.Meat
  val vegetable = new store.Vegetable
  
  println(store.processMeat(meat))
  println(store.processVegetable(vegetable))
  
  // 5. 自身类型与抽象类型演示
  println("\n=== 自身类型与抽象类型演示 ===")
  val appConfig = new AppDatabaseConfig
  val config = appConfig.getConfig
  println(appConfig.connect(config))
  
  // 6. 高级抽象类型约束演示
  println("\n=== 高级抽象类型约束演示 ===")
  val intList = new IntList
  intList.add(1)
  intList.add(2)
  intList.add(3)
  
  println(s"List contains 2: ${intList.contains(2)}")
  println(s"List contains 5: ${intList.contains(5)}")
  println(s"All elements: ${intList.getAll}")
  
  // 7. 抽象类型上界约束演示
  println("\n=== 抽象类型上界约束演示 ===")
  val dogShelter = new DogShelter
  val adoptedDog = dogShelter.adopt()
  println(s"Adopted animal: ${adoptedDog.getClass.getSimpleName}")
  
  // 8. 结构化类型演示
  println("\n=== 结构化类型演示 ===")
  val stringTagged = new StringTypeTagged
  val intTagged = new IntTypeTagged
  
  println(s"String type info: ${stringTagged.getTypeInfo}")
  println(s"Int type info: ${intTagged.getTypeInfo}")
}