// 结构化类型示例

// 定义结构化类型
type HasName = {
  def name: String
}

type HasAge = {
  val age: Int
}

type Printable = {
  def print(): Unit
}

// 使用反射实现结构化类型（需要导入）
import scala.language.reflectiveCalls

// 定义一些符合结构化类型的类
class Person(val name: String, val age: Int) {
  def print(): Unit = println(s"Person($name, $age)")
}

class Animal(val name: String) {
  val age = 5
  def print(): Unit = println(s"Animal($name, $age)")
}

class Book(val title: String) {
  def name: String = title
  def age: Int = 0
  def print(): Unit = println(s"Book($title)")
}

// 结构化类型函数
object StructuralTypeUtils {
  def printName(obj: HasName): Unit = {
    println(s"Name: ${obj.name}")
  }
  
  def printAge(obj: HasAge): Unit = {
    println(s"Age: ${obj.age}")
  }
  
  def invokePrint(obj: Printable): Unit = {
    obj.print()
  }
  
  // 复合结构化类型
  def processEntity(entity: HasName with HasAge with Printable): Unit = {
    println("Processing entity:")
    printName(entity)
    printAge(entity)
    invokePrint(entity)
  }
}

// 使用反射的动态调用
object DynamicInvocation {
  import scala.reflect.runtime.universe._
  
  // 简单的动态调用示例
  def callMethodIfExists(obj: Any, methodName: String): Unit = {
    // 注意：这只是一个简化示例，实际的反射调用会更复杂
    println(s"Attempting to call $methodName on $obj")
  }
}

object StructuralTypes {
  def main(args: Array[String]): Unit = {
    val person = new Person("Alice", 30)
    val animal = new Animal("Dog")
    val book = new Book("Scala Programming")
    
    // 使用结构化类型
    StructuralTypeUtils.printName(person)  // 输出: Name: Alice
    StructuralTypeUtils.printAge(person)   // 输出: Age: 30
    StructuralTypeUtils.invokePrint(person) // 输出: Person(Alice, 30)
    
    StructuralTypeUtils.printName(animal)  // 输出: Name: Dog
    StructuralTypeUtils.printAge(animal)   // 输出: Age: 5
    StructuralTypeUtils.invokePrint(animal) // 输出: Animal(Dog, 5)
    
    StructuralTypeUtils.printName(book)    // 输出: Name: Scala Programming
    StructuralTypeUtils.printAge(book)     // 输出: Age: 0
    StructuralTypeUtils.invokePrint(book)   // 输出: Book(Scala Programming)
    
    // 使用复合结构化类型
    StructuralTypeUtils.processEntity(person)
    // 输出:
    // Processing entity:
    // Name: Alice
    // Age: 30
    // Person(Alice, 30)
    
    // 动态调用示例
    DynamicInvocation.callMethodIfExists(person, "print")
    DynamicInvocation.callMethodIfExists(animal, "print")
  }
}