// 高级类型系统示例
object AdvancedTypeExamples {
  
  // 1. 存在类型 (Existential Types)
  def processList[T](list: List[T]): Int = list.length
  
  // 使用存在类型
  def processAnyList(list: List[T] forSome { type T }): Int = list.length
  
  // 2. 自类型注解 (Self-type Annotations)
  trait User {
    def username: String
  }
  
  trait TweetService {
    self: User =>  // 自类型注解
    def tweet(message: String): String = s"$username tweets: $message"
  }
  
  class TwitterUser(val username: String) extends User with TweetService
  
  // 3. 抽象类型成员 vs 类型参数
  trait ContainerAbstract {
    type T
    def value: T
    def setValue(newValue: T): Unit
  }
  
  trait ContainerParameterized[T] {
    def value: T
    def setValue(newValue: T): Unit
  }
  
  class StringContainerAbstract extends ContainerAbstract {
    type T = String
    private var _value: String = ""
    def value: T = _value
    def setValue(newValue: T): Unit = _value = newValue
  }
  
  class StringContainerParameterized extends ContainerParameterized[String] {
    private var _value: String = ""
    def value: String = _value
    def setValue(newValue: String): Unit = _value = newValue
  }
  
  // 4. 依赖方法类型 (Dependent Method Types)
  trait Resource {
    type Handle
    def open(): Handle
    def close(handle: Handle): Unit
  }
  
  class FileResource extends Resource {
    type Handle = String
    def open(): Handle = "file_handle"
    def close(handle: Handle): Unit = println(s"Closing file: $handle")
  }
  
  // 依赖方法类型示例
  def useResource[R <: Resource](resource: R)(op: (resource.Handle) => Unit): Unit = {
    val handle = resource.open()
    try {
      op(handle)
    } finally {
      resource.close(handle)
    }
  }
  
  // 5. 高阶多态 (Higher-kinded Polymorphism)
  trait Functor[F[_]] {
    def map[A, B](fa: F[A])(f: A => B): F[B]
  }
  
  object Functor {
    implicit val listFunctor: Functor[List] = new Functor[List] {
      def map[A, B](fa: List[A])(f: A => B): List[B] = fa.map(f)
    }
    
    implicit val optionFunctor: Functor[Option] = new Functor[Option] {
      def map[A, B](fa: Option[A])(f: A => B): Option[B] = fa.map(f)
    }
  }
  
  // 6. 类型类派生 (Type Class Derivation)
  trait Show[A] {
    def show(a: A): String
  }
  
  object Show {
    implicit val stringShow: Show[String] = new Show[String] {
      def show(a: String): String = s""""$a""""
    }
    
    implicit val intShow: Show[Int] = new Show[Int] {
      def show(a: Int): String = a.toString
    }
    
    // 为元组派生Show实例
    implicit def tuple2Show[A, B](
      implicit sa: Show[A], sb: Show[B]
    ): Show[(A, B)] = new Show[(A, B)] {
      def show(ab: (A, B)): String = {
        val (a, b) = ab
        s"(${sa.show(a)}, ${sb.show(b)})"
      }
    }
  }
  
  // 7. 隐式参数和证据参数
  def sorted[T](list: List[T])(implicit ord: Ordering[T]): List[T] = list.sorted
  
  // 使用证据参数的替代方式
  def sortedEvidence[T](list: List[T])(ev: Ordering[T]): List[T] = list.sorted
  
  // 8. 类型边界 (Type Bounds)
  // 上界
  def processUpperBound[A <: Comparable[A]](a: A, b: A): Int = a.compareTo(b)
  
  // 下界
  def processLowerBound[A, B >: A](a: A, b: B): Unit = {
    println(s"a: $a, b: $b")
  }
  
  // 9. 视图边界 (View Bounds) - 已废弃，但为了完整性展示
  // def processViewBound[A <% Comparable[A]](a: A, b: A): Int = a.compareTo(b)
  
  // 10. 上下文边界 (Context Bounds)
  def processWithContextBound[A: Ordering](list: List[A]): List[A] = list.sorted
  
  // 等价于
  def processWithContextBoundExplicit[A](list: List[A])(implicit ord: Ordering[A]): List[A] = 
    list.sorted
  
  // 11. 复合类型 (Compound Types)
  trait Cloneable extends java.lang.Cloneable {
    override def clone(): Any = super.clone()
  }
  
  trait Resetable {
    def reset(): Unit
  }
  
  def cloneAndReset(obj: Cloneable with Resetable): Cloneable = {
    val cloned = obj.clone().asInstanceOf[Cloneable]
    obj.reset()
    cloned
  }
  
  // 12. refined types (细化类型)
  // 使用字面量类型
  val port: 8080 = 8080
  
  // 13. 幻影类型 (Phantom Types)
  sealed trait Status
  sealed trait Open extends Status
  sealed trait Closed extends Status
  
  class Connection[S <: Status] private () {
    def write(data: String)(implicit ev: S =:= Open): Unit = 
      println(s"Writing: $data")
    
    def open(): Connection[Open] = new Connection[Open]()
    
    def close(): Connection[Closed] = new Connection[Closed]()
  }
  
  object Connection {
    def create(): Connection[Closed] = new Connection[Closed]()
  }
  
  // 14. 标记特质 (Tagged Traits)
  trait Meter
  trait Kilogram
  
  case class Distance(value: Double) extends AnyVal
  case class Mass(value: Double) extends AnyVal
  
  // 15. 值类 (Value Classes)
  implicit class RichInt(val value: Int) extends AnyVal {
    def squared: Int = value * value
    def cubed: Int = value * value * value
  }
  
  // 16. 通用特性 (Universal Traits)
  trait Printable extends Any {
    def print(): Unit = println(this)
  }
  
  case class MyInt(value: Int) extends AnyVal with Printable
  
  // 17. 类型别名 vs 抽象类型
  type Email = String
  type UserId = String
  
  trait UserService {
    type Id  // 抽象类型
    def getUser(id: Id): Option[String]
  }
  
  class ConcreteUserService extends UserService {
    type Id = Int
    private val users = Map(1 -> "Alice", 2 -> "Bob")
    
    def getUser(id: Id): Option[String] = users.get(id)
  }
  
  // 18. 类型投影 (#) vs 路径依赖 (.)
  class Outer {
    class Inner
    val inner: Inner = new Inner
  }
  
  val outer1 = new Outer
  val outer2 = new Outer
  
  // 路径依赖类型
  val inner1: outer1.Inner = outer1.inner
  val inner2: outer2.Inner = outer2.inner
  
  // 类型投影
  val anyInner: Outer#Inner = outer1.inner
  
  // 19. 多重继承和线性化
  trait A {
    def method: String = "A"
  }
  
  trait B extends A {
    override def method: String = "B -> " + super.method
  }
  
  trait C extends A {
    override def method: String = "C -> " + super.method
  }
  
  class D extends B with C
  class E extends C with B
  
  // 20. 使用示例
  def main(args: Array[String]): Unit = {
    println("=== 高级类型系统示例 ===")
    
    // 1. 存在类型示例
    println("\n--- 存在类型 ---")
    val intList = List(1, 2, 3)
    val stringList = List("a", "b", "c")
    
    println(s"Int list length: ${processAnyList(intList)}")
    println(s"String list length: ${processAnyList(stringList)}")
    
    // 2. 自类型注解示例
    println("\n--- 自类型注解 ---")
    val twitterUser = new TwitterUser("ScalaUser")
    println(twitterUser.tweet("Hello Scala!"))
    
    // 3. 抽象类型成员 vs 类型参数示例
    println("\n--- 抽象类型成员 vs 类型参数 ---")
    val absContainer = new StringContainerAbstract
    absContainer.setValue("Hello")
    println(s"Abstract container value: ${absContainer.value}")
    
    val paramContainer = new StringContainerParameterized
    paramContainer.setValue("World")
    println(s"Parameterized container value: ${paramContainer.value}")
    
    // 4. 依赖方法类型示例
    println("\n--- 依赖方法类型 ---")
    val fileResource = new FileResource
    useResource(fileResource) { handle =>
      println(s"Using resource with handle: $handle")
    }
    
    // 5. 高阶多态示例
    println("\n--- 高阶多态 ---")
    val numbers = List(1, 2, 3, 4, 5)
    val maybeNumber = Some(42)
    
    println(s"Mapped list: ${Functor.listFunctor.map(numbers)(_ * 2)}")
    println(s"Mapped option: ${Functor.optionFunctor.map(maybeNumber)(_.toString)}")
    
    // 6. 类型类派生示例
    println("\n--- 类型类派生 ---")
    val tuple = ("Hello", 42)
    println(s"Tuple show: ${Show.tuple2Show(Show.stringShow, Show.intShow).show(tuple)}")
    
    // 7. 隐式参数示例
    println("\n--- 隐式参数 ---")
    val unsortedList = List(3, 1, 4, 1, 5, 9, 2, 6)
    println(s"Sorted list: ${sorted(unsortedList)}")
    
    // 8. 类型边界示例
    println("\n--- 类型边界 ---")
    val result = processUpperBound("apple", "banana")
    println(s"String comparison result: $result")
    
    processLowerBound("hello", "world": Any)
    
    // 9. 上下文边界示例
    println("\n--- 上下文边界 ---")
    val words = List("scala", "java", "python")
    println(s"Sorted words: ${processWithContextBound(words)}")
    
    // 10. 复合类型示例
    println("\n--- 复合类型 ---")
    // 注意：Cloneable在Scala中使用较少，这里仅作演示
    
    // 11. 幻影类型示例
    println("\n--- 幻影类型 ---")
    val connection = Connection.create()
    val openConnection = connection.open()
    openConnection.write("Hello, world!")
    val closedConnection = openConnection.close()
    // openConnection.write("This would cause a compile error")
    
    // 12. 值类示例
    println("\n--- 值类 ---")
    val number = 5
    println(s"$number squared: ${number.squared}")
    println(s"$number cubed: ${number.cubed}")
    
    // 13. 通用特性示例
    println("\n--- 通用特性 ---")
    val myInt = MyInt(42)
    myInt.print()
    
    // 14. 多重继承线性化示例
    println("\n--- 多重继承线性化 ---")
    val d = new D
    val e = new E
    println(s"D method result: ${d.method}")
    println(s"E method result: ${e.method}")
    
    println("\n所有高级类型系统示例完成")
  }
}