// 类型约束示例

// 1. 上界 (Upper Bounds)
class ComparablePair[T <: Comparable[T]](val first: T, val second: T) {
  def larger: T = if (first.compareTo(second) > 0) first else second
  def smaller: T = if (first.compareTo(second) < 0) first else second
  
  override def toString: String = s"ComparablePair($first, $second)"
}

// 实现Comparable接口的类
class Person(val name: String, val age: Int) extends Comparable[Person] {
  override def compareTo(other: Person): Int = this.age - other.age
  
  override def toString: String = s"Person($name, $age)"
}

// 2. 下界 (Lower Bounds)
class Container[+A](private val elements: List[A]) {
  // 使用下界确保类型安全
  def add[B >: A](element: B): Container[B] = new Container(element :: elements)
  
  def getElements: List[A] = elements
  
  def size: Int = elements.length
  
  override def toString: String = s"Container(${elements.mkString(", ")})"
}

// 3. 上下文界定 (Context Bounds)
class Sorter[T: Ordering](items: List[T]) {
  def sort(): List[T] = items.sorted  // 使用隐式的Ordering[T]
  
  def max(): T = items.max  // 使用隐式的Ordering[T]
  
  def min(): T = items.min  // 使用隐式的Ordering[T]
  
  override def toString: String = s"Sorter(${items.mkString(", ")})"
}

// 用于上下文界定的示例类
case class Book(title: String, author: String, year: Int)

// 为Book创建隐式Ordering
object BookOrdering {
  implicit val bookOrdering: Ordering[Book] = new Ordering[Book] {
    def compare(x: Book, y: Book): Int = x.year.compare(y.year)
  }
}

// 4. 类型约束示例对象
object TypeBoundsExamples extends App {
  // 上界示例
  println("=== 上界示例 ===")
  val alice = new Person("Alice", 30)
  val bob = new Person("Bob", 25)
  val personPair = new ComparablePair(alice, bob)
  
  println(personPair)
  println(s"Older: ${personPair.larger}")
  println(s"Younger: ${personPair.smaller}")
  
  // 下界示例
  println("\n=== 下界示例 ===")
  val intContainer = new Container(List(1, 2, 3))
  println(intContainer)
  
  val anyContainer = intContainer.add("hello")
  println(anyContainer)  // 可以添加Any类型的元素
  
  // 上下文界定示例
  println("\n=== 上下文界定示例 ===")
  import BookOrdering._
  
  val books = List(
    Book("The Hobbit", "J.R.R. Tolkien", 1937),
    Book("1984", "George Orwell", 1949),
    Book("Brave New World", "Aldous Huxley", 1932),
    Book("Fahrenheit 451", "Ray Bradbury", 1953)
  )
  
  val bookSorter = new Sorter(books)
  println("Original books:")
  books.foreach(println)
  
  println("\nSorted by year:")
  bookSorter.sort().foreach(println)
  
  println(s"\nOldest book: ${bookSorter.min()}")
  println(s"Newest book: ${bookSorter.max()}")
}