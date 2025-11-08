// 定义类型类
trait Semigroup[A] {
  def combine(x: A, y: A): A
}

trait Monoid[A] extends Semigroup[A] {
  def empty: A
}

// 为不同类型提供类型类实例
object MonoidInstances {
  implicit val intMonoid: Monoid[Int] = new Monoid[Int] {
    def empty: Int = 0
    def combine(x: Int, y: Int): Int = x + y
  }

  implicit val stringMonoid: Monoid[String] = new Monoid[String] {
    def empty: String = ""
    def combine(x: String, y: String): String = x + y
  }

  implicit def listMonoid[A]: Monoid[List[A]] = new Monoid[List[A]] {
    def empty: List[A] = List.empty
    def combine(x: List[A], y: List[A]): List[A] = x ++ y
  }

  implicit def optionMonoid[A]: Monoid[Option[A]] = new Monoid[Option[A]] {
    def empty: Option[A] = None
    def combine(x: Option[A], y: Option[A]): Option[A] = x.orElse(y)
  }
}

// 定义接口对象
object Monoid {
  def empty[A](implicit monoid: Monoid[A]): A = monoid.empty
  
  def combine[A](x: A, y: A)(implicit monoid: Monoid[A]): A = monoid.combine(x, y)
  
  // 语法糖
  implicit class MonoidOps[A](value: A) {
    def |+|(other: A)(implicit monoid: Monoid[A]): A = monoid.combine(value, other)
  }
}

// 使用类型类的函数
object MonoidSyntax {
  def combineAll[A](list: List[A])(implicit monoid: Monoid[A]): A =
    list.foldLeft(monoid.empty)(monoid.combine)
    
  def foldMap[A, B](list: List[A])(f: A => B)(implicit monoid: Monoid[B]): B =
    list.map(f).foldLeft(monoid.empty)(monoid.combine)
}

object TypeClassExamples {
  import MonoidInstances._
  import MonoidSyntax._
  
  def main(args: Array[String]): Unit = {
    // 使用类型类实例
    println(Monoid.combine(1, 2)) // 输出: 3
    println(Monoid.combine("Hello, ", "World!")) // 输出: Hello, World!
    
    // 使用语法糖
    println(1 |+| 2 |+| 3) // 输出: 6
    println("a" |+| "b" |+| "c") // 输出: abc
    
    // 使用类型类函数
    println(combineAll(List(1, 2, 3, 4))) // 输出: 10
    println(combineAll(List("a", "b", "c"))) // 输出: abc
    
    // 使用foldMap
    println(foldMap(List("a", "b", "c"))(_.toUpperCase)) // 输出: ABC
    println(foldMap(List(1, 2, 3))(_.toString)) // 输出: 123
  }
}