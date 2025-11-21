// 高级类型系统示例

// 1. 路径依赖类型
object PathDependentTypes {
  // 外部类
  class OuterClass {
    // 内部类
    class InnerClass {
      def innerMethod(): String = "Inner method"
    }
  
    def createInner(): InnerClass = new InnerClass
  }

  def demonstrate(): Unit = {
    val outer1 = new OuterClass
    val outer2 = new OuterClass
    
    // 创建内部类实例
    val inner1 = outer1.createInner()
    val inner2 = outer1.createInner()
    val inner3 = outer2.createInner()
    
    // inner1和inner2的类型是 outer1.InnerClass
    // inner3的类型是 outer2.InnerClass
    
    // 这两个类型是不同的，即使它们有相同的结构
    // inner1: outer1.InnerClass
    // inner3: outer2.InnerClass
    
    // 下面的赋值是合法的，因为它们是相同的外部实例
    val sameOuterInner: outer1.InnerClass = inner2
    
    println("Path dependent types demonstrated")
  }
}

// 2. 抽象类型成员
object AbstractTypeMembers {
  // 使用抽象类型成员的特质
  trait Repository {
    // 抽象类型成员
    type ID
    type Entity
    
    // 使用这些类型的方法
    def findById(id: ID): Option[Entity]
    def save(entity: Entity): Entity
    def delete(id: ID): Boolean
  }

  // 具体实现
  class UserRepository extends Repository {
    type ID = Long
    type Entity = User
    
    case class User(id: Long, name: String, email: String)
    
    private var users = Map[Long, User]()
    
    def findById(id: Long): Option[User] = users.get(id)
    
    def save(user: User): User = {
      users = users + (user.id -> user)
      user
    }
    
    def delete(id: Long): Boolean = {
      if (users.contains(id)) {
        users = users - id
        true
      } else {
        false
      }
    }
  }

  // 另一个实现
  class BookRepository extends Repository {
    type ID = String  // ISBN作为ID
    type Entity = Book
    
    case class Book(isbn: String, title: String, author: String)
    
    private var books = Map[String, Book]()
    
    def findById(isbn: String): Option[Book] = books.get(isbn)
    
    def save(book: Book): Book = {
      books = books + (book.isbn -> book)
      book
    }
    
    def delete(isbn: String): Boolean = {
      if (books.contains(isbn)) {
        books = books - isbn
        true
      } else {
        false
      }
    }
  }

  def demonstrate(): Unit = {
    val userRepo = new UserRepository
    val bookRepo = new BookRepository
    
    // 添加用户
    val user = userRepo.User(1L, "Alice", "alice@example.com")
    val savedUser = userRepo.save(user)
    println(s"Saved user: $savedUser")
    
    // 添加图书
    val book = bookRepo.Book("978-3-16-148410-0", "Scala Programming", "Martin Odersky")
    val savedBook = bookRepo.save(book)
    println(s"Saved book: $savedBook")
  }
}

// 3. 高阶类型
object HigherKindedTypes {
  // 类型类，表示容器类型可以被遍历
  trait Functor[F[_]] {
    def map[A, B](fa: F[A])(f: A => B): F[B]
  }

  // Functor实现
  object ListFunctor extends Functor[List] {
    def map[A, B](fa: List[A])(f: A => B): List[B] = fa.map(f)
  }

  object OptionFunctor extends Functor[Option] {
    def map[A, B](fa: Option[A])(f: A => B): Option[B] = fa.map(f)
  }

  // 使用Functor
  def processWithFunctor[F[_], A, B](container: F[A], f: A => B)
                                  (implicit functor: Functor[F]): F[B] = {
    functor.map(container)(f)
  }

  def demonstrate(): Unit = {
    val numbers = List(1, 2, 3, 4, 5)
    val squared = processWithFunctor(numbers, (x: Int) => x * x)
    println(s"Squared numbers: $squared")
    
    val maybeNumber: Option[Int] = Some(42)
    val maybeSquared = processWithFunctor(maybeNumber, (x: Int) => x * x)
    println(s"Maybe squared: $maybeSquared")
  }
}

// 4. 类型类
object TypeClasses {
  // 定义一个可比较的类型类
  trait Equal[T] {
    def equal(x: T, y: T): Boolean
  }

  // Equal实例
  object EqualInstances {
    implicit val intEqual: Equal[Int] = new Equal[Int] {
      def equal(x: Int, y: Int): Boolean = x == y
    }
    
    implicit val stringEqual: Equal[String] = new Equal[String] {
      def equal(x: String, y: String): Boolean = x == y
    }
    
    implicit def listEqual[T](implicit equalT: Equal[T]): Equal[List[T]] = new Equal[List[T]] {
      def equal(x: List[T], y: List[T]): Boolean = {
        if (x.length != y.length) false
        else x.zip(y).forall { case (a, b) => equalT.equal(a, b) }
      }
    }
    
    implicit def optionEqual[T](implicit equalT: Equal[T]): Equal[Option[T]] = new Equal[Option[T]] {
      def equal(x: Option[T], y: Option[T]): Boolean = (x, y) match {
        case (None, None) => true
        case (Some(a), Some(b)) => equalT.equal(a, b)
        case _ => false
      }
    }
  }

  // 使用类型类的函数
  import EqualInstances._
  
  // 使用扩展方法语法
  implicit class EqualOps[T](x: T)(implicit equal: Equal[T]) {
    def ===(y: T): Boolean = equal.equal(x, y)
  }

  def demonstrate(): Unit = {
    // 使用扩展方法语法
    println(s"5 === 5: ${5 === 5}")
    println(s"List(1,2,3) === List(1,2,3): ${List(1, 2, 3) === List(1, 2, 3)}")
    println(s"List(1,2,3) === List(1,2,4): ${List(1, 2, 3) === List(1, 2, 4)}")
    println(s"Some(5) === Some(5): ${Some(5) === Some(5)}")
    println(s"Some(5) === None: ${Some(5) === None}")
  }
}

// 5. Monoid类型类
object MonoidTypeClass {
  // Monoid类型类：表示一个有结合律和单位元的操作
  trait Monoid[T] {
    def empty: T
    def combine(x: T, y: T): T
  }

  // Monoid实例
  object MonoidInstances {
    implicit val intAdditionMonoid: Monoid[Int] = new Monoid[Int] {
      def empty: Int = 0
      def combine(x: Int, y: Int): Int = x + y
    }
    
    implicit val stringMonoid: Monoid[String] = new Monoid[String] {
      def empty: String = ""
      def combine(x: String, y: String): String = x + y
    }
    
    implicit def listMonoid[T]: Monoid[List[T]] = new Monoid[List[T]] {
      def empty: List[T] = List.empty
      def combine(x: List[T], y: List[T]): List[T] = x ::: y
    }
  }

  // 使用Monoid的函数
  import MonoidInstances._
  
  // 组合列表中的所有元素
  def combineAll[T](list: List[T])(implicit monoid: Monoid[T]): T = {
    list.foldLeft(monoid.empty)(monoid.combine)
  }

  def demonstrate(): Unit = {
    // 使用Int加法Monoid
    println(s"Sum of List(1,2,3,4,5): ${combineAll(List(1, 2, 3, 4, 5))}")
    
    // 使用String Monoid
    println(s"Concatenation of List(\"Hello\", \" \", \"World\"): ${combineAll(List("Hello", " ", "World"))}")
    
    // 使用List Monoid
    println(s"Concatenation of List(List(1,2), List(3,4), List(5)): ${combineAll(List(List(1, 2), List(3, 4), List(5)))}")
  }
}

// 6. Phantom类型
object PhantomTypes {
  // 使用Phantom类型表示状态
  sealed trait FileState
  trait Closed extends FileState
  trait Open extends FileState
  trait Reading extends FileState
  trait Writing extends FileState

  // 带有Phantom类型的文件类
  class File[S <: FileState] private (private val path: String, private var isOpen: Boolean) {
    // 文件打开操作，从Closed状态变为Open状态
    def open(implicit ev: S =:= Closed): File[Open] = {
      // 模拟打开文件
      println(s"Opening file: $path")
      new File(path, true).asInstanceOf[File[Open]]
    }
    
    // 文件关闭操作，从Open状态变为Closed状态
    def close(implicit ev: S =:= Open): File[Closed] = {
      // 模拟关闭文件
      println(s"Closing file: $path")
      new File(path, false).asInstanceOf[File[Closed]]
    }
    
    // 文件读取操作，从Open状态变为Reading状态
    def read(implicit ev: S =:= Open): (File[Reading], String) = {
      // 模拟读取文件
      println(s"Reading from file: $path")
      val content = s"Content of $path"
      (new File(path, true).asInstanceOf[File[Reading]], content)
    }
    
    // 文件写入操作，从Open状态变为Writing状态
    def write(content: String)(implicit ev: S =:= Open): File[Writing] = {
      // 模拟写入文件
      println(s"Writing to file: $path: $content")
      new File(path, true).asInstanceOf[File[Writing]]
    }
    
    // 完成读取操作，返回到Open状态
    def doneReading(implicit ev: S =:= Reading): File[Open] = {
      println(s"Finished reading from file: $path")
      this.asInstanceOf[File[Open]]
    }
    
    // 完成写入操作，返回到Open状态
    def doneWriting(implicit ev: S =:= Writing): File[Open] = {
      println(s"Finished writing to file: $path")
      this.asInstanceOf[File[Open]]
    }
  }

  // 伴生对象提供工厂方法
  object File {
    def apply(path: String): File[Closed] = new File(path, false)
  }

  def fileOperations(): Unit = {
    // 创建一个关闭的文件
    val closedFile = File("/tmp/example.txt")
    println(s"Created closed file")
    
    // 打开文件
    val openFile = closedFile.open()
    println(s"Opened file")
    
    // 读取文件
    val (readingFile, content) = openFile.read()
    println(s"Read content: $content")
    
    // 完成读取
    val openFileAgain = readingFile.doneReading()
    
    // 写入文件
    val writingFile = openFileAgain.write("New content")
    
    // 完成写入
    val openFileFinal = writingFile.doneWriting()
    
    // 关闭文件
    val closedFileFinal = openFileFinal.close()
    println(s"Closed file")
    
    // 下面的代码会导致编译错误，因为类型不匹配：
    // val error = closedFile.read()  // 编译错误：File[Closed]不能read
    
    // 这提供了编译时的状态安全性
    println("File operations completed safely with phantom types")
  }

  def demonstrate(): Unit = {
    fileOperations()
  }
}

// 7. 类型级自然数
object TypeLevelNumbers {
  // 类型级自然数的表示
  sealed trait Nat {
    type Plus[M <: Nat] <: Nat
  }

  // 零
  final class _0 extends Nat {
    type Plus[M <: Nat] = M
  }

  // 后继
  final class Succ[N <: Nat] extends Nat {
    type Plus[M <: Nat] = Succ[N#Plus[M]]
  }

  // 类型别名，便于使用
  type _1 = Succ[_0]
  type _2 = Succ[_1]
  type _3 = Succ[_2]
  type _4 = Succ[_3]
  type _5 = Succ[_4]

  // 类型类：将类型级自然数转换为值级自然数
  trait ToValue[N <: Nat] {
    def value: Int
  }

  // ToValue实例
  object ToValueInstances {
    implicit val zeroToValue: ToValue[_0] = new ToValue[_0] {
      def value: Int = 0
    }
    
    implicit def succToValue[N <: Nat](implicit toValueN: ToValue[N]): ToValue[Succ[N]] = 
      new ToValue[Succ[N]] {
        def value: Int = 1 + toValueN.value
      }
  }

  // 将类型级自然数转换为值
  def toValue[N <: Nat](implicit toValue: ToValue[N]): Int = toValue.value
  
  def demonstrate(): Unit = {
    // 验证类型级计算结果
    val three = toValue[_3]  // 3
    println(s"Value of _3: $three")
    
    // 这展示了类型级编程的概念
    println("Type-level natural numbers demonstrated")
  }
}

// 8. 类型安全状态机
object TypeSafeStateMachine {
  // 使用类型构建类型安全的状态机
  sealed trait DoorState
  trait Closed extends DoorState
  trait Open extends DoorState
  trait Locked extends DoorState

  // 带状态的门类
  class Door[S <: DoorState] private () {
    // 开门操作
    def open(implicit ev: S =:= Closed): Door[Open] = {
      println("Opening door")
      new Door[Open]()
    }
    
    // 关门操作
    def close(implicit ev: S =:= Open): Door[Closed] = {
      println("Closing door")
      new Door[Closed]()
    }
    
    // 锁门操作
    def lock(implicit ev: S =:= Closed): Door[Locked] = {
      println("Locking door")
      new Door[Locked]()
    }
    
    // 解锁操作
    def unlock(implicit ev: S =:= Locked): Door[Closed] = {
      println("Unlocking door")
      new Door[Closed]()
    }
  }

  // 伴生对象
  object Door {
    def apply(): Door[Closed] = new Door[Closed]()
  }

  def demonstrate(): Unit = {
    // 创建一个关闭的门
    val closedDoor = Door()
    
    // 关门 -> 开门
    val openDoor = closedDoor.open()
    
    // 开门 -> 关门
    val closedAgain = openDoor.close()
    
    // 关门 -> 锁门
    val lockedDoor = closedAgain.lock()
    
    // 锁门 -> 解锁
    val unlockedDoor = lockedDoor.unlock()
    
    // 下面的代码会导致编译错误，因为状态不匹配：
    // val error = closedDoor.open().close().open().open()  // 开门状态不能再次开门
    
    println("State machine operations completed successfully with type safety")
  }
}

// 9. 主程序
object AdvancedTypesDemo extends App {
  println("=== 路径依赖类型 ===")
  PathDependentTypes.demonstrate()
  
  Thread.sleep(500)
  
  println("\n=== 抽象类型成员 ===")
  AbstractTypeMembers.demonstrate()
  
  Thread.sleep(500)
  
  println("\n=== 高阶类型 ===")
  HigherKindedTypes.demonstrate()
  
  Thread.sleep(500)
  
  println("\n=== 类型类 ===")
  TypeClasses.demonstrate()
  
  Thread.sleep(500)
  
  println("\n=== Monoid类型类 ===")
  MonoidTypeClass.demonstrate()
  
  Thread.sleep(500)
  
  println("\n=== Phantom类型 ===")
  PhantomTypes.demonstrate()
  
  Thread.sleep(500)
  
  println("\n=== 类型级自然数 ===")
  TypeLevelNumbers.demonstrate()
  
  Thread.sleep(500)
  
  println("\n=== 类型安全状态机 ===")
  TypeSafeStateMachine.demonstrate()
  
  println("\nAdvanced types demo completed!")
}