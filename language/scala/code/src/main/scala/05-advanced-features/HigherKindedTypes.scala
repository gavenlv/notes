// 高阶多态示例
// 使用类型构造器定义高阶类型

// Functor类型类
trait Functor[F[_]] {
  def map[A, B](fa: F[A])(f: A => B): F[B]
}

// Monad类型类
trait Monad[F[_]] extends Functor[F] {
  def pure[A](a: A): F[A]
  def flatMap[A, B](fa: F[A])(f: A => F[B]): F[B]
  
  override def map[A, B](fa: F[A])(f: A => B): F[B] =
    flatMap(fa)(a => pure(f(a)))
    
  def flatten[A](ffa: F[F[A]]): F[A] =
    flatMap(ffa)(identity)
}

// 为Option实现Functor
object OptionFunctor extends Functor[Option] {
  def map[A, B](fa: Option[A])(f: A => B): Option[B] = fa.map(f)
}

// 为Option实现Monad
object OptionMonad extends Monad[Option] {
  def pure[A](a: A): Option[A] = Some(a)
  def flatMap[A, B](fa: Option[A])(f: A => Option[B]): Option[B] = fa.flatMap(f)
}

// 为List实现Functor
object ListFunctor extends Functor[List] {
  def map[A, B](fa: List[A])(f: A => B): List[B] = fa.map(f)
}

// 为List实现Monad
object ListMonad extends Monad[List] {
  def pure[A](a: A): List[A] = List(a)
  def flatMap[A, B](fa: List[A])(f: A => List[B]): List[B] = fa.flatMap(f)
}

// 高阶多态函数示例
object HigherOrderFunctions {
  // 这个函数可以适用于任何实现了Functor的类型
  def transform[F[_], A, B](fa: F[A])(f: A => B)(implicit functor: Functor[F]): F[B] =
    functor.map(fa)(f)
    
  // 这个函数可以适用于任何实现了Monad的类型
  def sequence[F[_], A](list: List[F[A]])(implicit monad: Monad[F]): F[List[A]] = {
    list match {
      case Nil => monad.pure(Nil)
      case head :: tail =>
        monad.flatMap(head) { a =>
          monad.flatMap(sequence(tail)) { as =>
            monad.pure(a :: as)
          }
        }
    }
  }
}

// 使用高阶多态的示例
object HigherKindedTypes {
  def main(args: Array[String]): Unit = {
    import HigherOrderFunctions._
    
    // 使用Option Functor
    val optResult = transform(Some(5))(_ * 2)
    println(optResult) // 输出: Some(10)
    
    // 使用List Functor
    val listResult = transform(List(1, 2, 3))(_ * 2)
    println(listResult) // 输出: List(2, 4, 6)
    
    // 使用Option Monad sequence
    val optSequence = sequence(List(Some(1), Some(2), Some(3)))
    println(optSequence) // 输出: Some(List(1, 2, 3))
    
    // 使用List Monad sequence
    val listSequence = sequence(List(List(1, 2), List(3, 4)))
    println(listSequence) // 输出: List(List(1, 2, 3), List(1, 2, 4), List(1, 3, 3), List(1, 3, 4), List(2, 2, 3), List(2, 2, 4), List(2, 3, 3), List(2, 3, 4))
  }
}