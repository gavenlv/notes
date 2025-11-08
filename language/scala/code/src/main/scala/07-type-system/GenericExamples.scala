// 泛型编程示例
object GenericExamples {
  
  // 1. 基础泛型类
  class Container[A](value: A) {
    def get: A = value
    def map[B](f: A => B): Container[B] = new Container(f(value))
  }
  
  // 2. 泛型特质
  trait Repository[T] {
    def save(entity: T): Unit
    def findById(id: Long): Option[T]
    def findAll(): List[T]
  }
  
  // 3. 具体实现
  case class User(id: Long, name: String, email: String)
  
  class UserRepository extends Repository[User] {
    private var users = Map[Long, User]()
    
    def save(entity: User): Unit = {
      users = users + (entity.id -> entity)
    }
    
    def findById(id: Long): Option[User] = users.get(id)
    
    def findAll(): List[User] = users.values.toList
  }
  
  // 4. 泛型方法
  object Utils {
    def swap[A, B](tuple: (A, B)): (B, A) = (tuple._2, tuple._1)
    
    def duplicate[A](value: A): (A, A) = (value, value)
    
    def zipLists[A, B](list1: List[A], list2: List[B]): List[(A, B)] = {
      list1.zip(list2)
    }
  }
  
  // 5. 类型边界
  // 上界 <: 
  def printSequencable[A <: Seq[_]](seq: A): Unit = {
    println(s"序列长度: ${seq.length}")
  }
  
  // 下界 >:
  class Animal
  class Dog extends Animal
  class Puppy extends Dog
  
  def addDog[A >: Dog](dogs: List[A]): List[A] = {
    new Dog() :: dogs
  }
  
  // 6. 视图边界 <% (已废弃，使用隐式参数替代)
  def sortIfOrdered[A](list: List[A])(implicit ord: Ordering[A]): List[A] = {
    list.sorted
  }
  
  // 7. 上下文边界 : 
  def processWithSerializer[A: Serializer](data: A): String = {
    implicitly[Serializer[A]].serialize(data)
  }
  
  // 8. 隐式证据参数
  def sumIfNumeric[A](list: List[A])(implicit numeric: Numeric[A]): A = {
    list.reduce(numeric.plus)
  }
  
  // 9. 类型约束
  def equalIfSameType[A, B](a: A, b: B)(implicit ev: A =:= B): Boolean = {
    a == b
  }
  
  // 10. 协变、逆变和不变
  // 协变 +A: 如果A是B的子类型，则Container[A]是Container[B]的子类型
  class CovariantContainer[+A](value: A) {
    def get: A = value
  }
  
  // 逆变 -A: 如果A是B的子类型，则Container[B]是Container[A]的子类型
  abstract class ContravariantContainer[-A] {
    def process(a: A): Unit
  }
  
  // 不变 A: 没有子类型关系
  class InvariantContainer[A](var value: A)
  
  // 11. 类型投影
  class Outer {
    class Inner
    def createInner: Inner = new Inner
  }
  
  // 12. 辅助类型类
  trait Serializer[A] {
    def serialize(value: A): String
  }
  
  object Serializer {
    implicit val stringSerializer: Serializer[String] = new Serializer[String] {
      def serialize(value: String): String = s""""$value""""
    }
    
    implicit val intSerializer: Serializer[Int] = new Serializer[Int] {
      def serialize(value: Int): String = value.toString
    }
  }
  
  // 13. 泛型代数数据类型
  sealed trait Tree[A]
  case class Leaf[A](value: A) extends Tree[A]
  case class Branch[A](left: Tree[A], right: Tree[A]) extends Tree[A]
  
  object Tree {
    def map[A, B](tree: Tree[A])(f: A => B): Tree[B] = tree match {
      case Leaf(value) => Leaf(f(value))
      case Branch(left, right) => Branch(map(left)(f), map(right)(f))
    }
    
    def fold[A, B](tree: Tree[A])(leafFn: A => B)(branchFn: (B, B) => B): B = tree match {
      case Leaf(value) => leafFn(value)
      case Branch(left, right) => branchFn(fold(left)(leafFn)(branchFn), fold(right)(leafFn)(branchFn))
    }
  }
  
  def main(args: Array[String]): Unit = {
    println("=== 泛型编程示例 ===")
    
    // 1. 基础泛型类使用
    println("\n--- 基础泛型类 ---")
    val stringContainer = new Container("Hello")
    println(s"容器值: ${stringContainer.get}")
    val intContainer = stringContainer.map(_.length)
    println(s"映射后容器值: ${intContainer.get}")
    
    // 2. 泛型特质使用
    println("\n--- 泛型特质 ---")
    val userRepository = new UserRepository()
    val user = User(1, "Alice", "alice@example.com")
    userRepository.save(user)
    println(s"查找用户: ${userRepository.findById(1)}")
    
    // 3. 泛型方法使用
    println("\n--- 泛型方法 ---")
    val swapped = Utils.swap(("Hello", 123))
    println(s"交换元组: $swapped")
    
    val duplicated = Utils.duplicate("Scala")
    println(s"复制值: $duplicated")
    
    // 4. 类型边界使用
    println("\n--- 类型边界 ---")
    printSequencable(List(1, 2, 3, 4, 5))
    printSequencable("Hello")
    
    val dogs = List(new Dog(), new Dog())
    val moreDogs = addDog(dogs)
    println(s"狗列表大小: ${moreDogs.length}")
    
    // 5. 隐式参数使用
    println("\n--- 隐式参数 ---")
    val sortedNumbers = sortIfOrdered(List(3, 1, 4, 1, 5))
    println(s"排序数字: $sortedNumbers")
    
    val sortedStrings = sortIfOrdered(List("banana", "apple", "cherry"))
    println(s"排序字符串: $sortedStrings")
    
    // 6. 上下文边界使用
    println("\n--- 上下文边界 ---")
    val serializedString = processWithSerializer("Hello, World!")
    println(s"序列化字符串: $serializedString")
    
    val serializedInt = processWithSerializer(42)
    println(s"序列化整数: $serializedInt")
    
    // 7. 隐式证据参数使用
    println("\n--- 隐式证据参数 ---")
    val sum = sumIfNumeric(List(1, 2, 3, 4, 5))
    println(s"数字列表求和: $sum")
    
    // 8. 类型约束使用
    println("\n--- 类型约束 ---")
    val isEqual = equalIfSameType(42, 42)
    println(s"相同类型比较: $isEqual")
    
    // 9. 泛型代数数据类型使用
    println("\n--- 泛型ADT ---")
    val tree: Tree[Int] = Branch(
      Leaf(1),
      Branch(
        Leaf(2),
        Leaf(3)
      )
    )
    
    val mappedTree = Tree.map(tree)(_ * 2)
    println(s"映射后的树: $mappedTree")
    
    val sumResult = Tree.fold(tree)(identity)(_ + _)
    println(s"树节点求和: $sumResult")
    
    println("\n所有泛型示例完成")
  }
}