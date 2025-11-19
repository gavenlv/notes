// 高阶类型示例
import scala.language.higherKinds

object HigherKindedTypes {
  
  // 1. 高阶类型定义
  // Functor是一个高阶类型类，接受一个类型构造器F[_]作为参数
  trait Functor[F[_]] {
    def map[A, B](fa: F[A])(f: A => B): F[B]
  }
  
  // 2. Option的Functor实例
  implicit val optionFunctor: Functor[Option] = new Functor[Option] {
    def map[A, B](fa: Option[A])(f: A => B): Option[B] = fa.map(f)
  }
  
  // 3. List的Functor实例
  implicit val listFunctor: Functor[List] = new Functor[List] {
    def map[A, B](fa: List[A])(f: A => B): List[B] = fa.map(f)
  }
  
  // 4. 高阶多态函数
  def liftOption[A, B](f: A => B): Option[A] => Option[B] = 
    optionFunctor.map(_)(f)
  
  def liftList[A, B](f: A => B): List[A] => List[B] = 
    listFunctor.map(_)(f)
  
  // 5. Monad类型类
  trait Monad[F[_]] extends Functor[F] {
    def pure[A](a: A): F[A]
    def flatMap[A, B](fa: F[A])(f: A => F[B]): F[B]
    
    // 从flatMap派生map
    def map[A, B](fa: F[A])(f: A => B): F[B] = 
      flatMap(fa)(a => pure(f(a)))
  }
  
  // 6. Option的Monad实例
  implicit val optionMonad: Monad[Option] = new Monad[Option] {
    def pure[A](a: A): Option[A] = Some(a)
    def flatMap[A, B](fa: Option[A])(f: A => Option[B]): Option[B] = 
      fa.flatMap(f)
  }
  
  // 7. List的Monad实例
  implicit val listMonad: Monad[List] = new Monad[List] {
    def pure[A](a: A): List[A] = List(a)
    def flatMap[A, B](fa: List[A])(f: A => List[B]): List[B] = 
      fa.flatMap(f)
  }
  
  // 8. 高阶多态的使用
  def sequence[F[_], A](list: List[F[A]])(implicit monad: Monad[F]): F[List[A]] = {
    list.foldRight(monad.pure(List.empty[A])) { (fa, acc) =>
      monad.flatMap(fa) { a =>
        monad.map(acc)(a :: _)
      }
    }
  }
  
  // 9. Applicative类型类
  trait Applicative[F[_]] extends Functor[F] {
    def pure[A](a: A): F[A]
    def ap[A, B](ff: F[A => B])(fa: F[A]): F[B]
    
    // 从ap派生map
    def map[A, B](fa: F[A])(f: A => B): F[B] = 
      ap(pure(f))(fa)
  }
  
  // 10. Option的Applicative实例
  implicit val optionApplicative: Applicative[Option] = new Applicative[Option] {
    def pure[A](a: A): Option[A] = Some(a)
    def ap[A, B](ff: Option[A => B])(fa: Option[A]): Option[B] = 
      for {
        f <- ff
        a <- fa
      } yield f(a)
  }
  
  // 11. 高阶类型的应用：验证
  sealed trait Validated[+E, +A]
  case class Valid[A](value: A) extends Validated[Nothing, A]
  case class Invalid[E](error: E) extends Validated[E, Nothing]
  
  // 12. Validated的Applicative实例
  implicit def validatedApplicative[E](implicit semigroup: Semigroup[E]): Applicative[Validated[E, *]] = 
    new Applicative[Validated[E, *]] {
      def pure[A](a: A): Validated[E, A] = Valid(a)
      def ap[A, B](ff: Validated[E, A => B])(fa: Validated[E, A]): Validated[E, B] = 
        (ff, fa) match {
          case (Valid(f), Valid(a)) => Valid(f(a))
          case (Invalid(e1), Invalid(e2)) => Invalid(semigroup.combine(e1, e2))
          case (Invalid(e), _) => Invalid(e)
          case (_, Invalid(e)) => Invalid(e)
        }
    }
  
  // 13. Semigroup类型类
  trait Semigroup[A] {
    def combine(x: A, y: A): A
  }
  
  // 14. String的Semigroup实例
  implicit val stringSemigroup: Semigroup[String] = new Semigroup[String] {
    def combine(x: String, y: String): String = x + y
  }
  
  // 15. List的Semigroup实例
  implicit def listSemigroup[A]: Semigroup[List[A]] = new Semigroup[List[A]] {
    def combine(x: List[A], y: List[A]): List[A] = x ++ y
  }
  
  // 16. 高阶类型的使用示例
  def validateUser(name: String, age: Int): Validated[String, (String, Int)] = {
    implicit val stringSemigroup: Semigroup[String] = new Semigroup[String] {
      def combine(x: String, y: String): String = s"$x; $y"
    }
    
    val nameValidation = 
      if (name.nonEmpty) Valid(name) 
      else Invalid("Name cannot be empty")
      
    val ageValidation = 
      if (age > 0) Valid(age) 
      else Invalid("Age must be positive")
    
    // 使用Applicative组合验证
    val applicative = validatedApplicative[String]
    applicative.ap(
      applicative.ap(
        applicative.pure((name: String, age: Int) => (name, age))
      )(nameValidation)
    )(ageValidation)
  }
  
  // 17. 抽象类型成员
  trait Container {
    type A
    def value: A
  }
  
  class StringContainer(val value: String) extends Container {
    type A = String
  }
  
  class IntContainer(val value: Int) extends Container {
    type A = Int
  }
  
  // 18. 依赖方法类型
  def processContainer(c: Container): c.A = c.value
  
  // 19. Kind投影
  trait FunctorK {
    type F[_[_]]
  }
  
  // 20. 高阶类型的实际应用
  def main(args: Array[String]): Unit = {
    println("=== 高阶类型示例 ===")
    
    // 1. Functor使用示例
    println("\n--- Functor使用示例 ---")
    val optionResult = optionFunctor.map(Some(5))(_ * 2)
    println(s"Option Functor: $optionResult")
    
    val listResult = listFunctor.map(List(1, 2, 3))(_ * 2)
    println(s"List Functor: $listResult")
    
    // 2. Monad使用示例
    println("\n--- Monad使用示例 ---")
    val optionMonadResult = optionMonad.flatMap(Some(5))(x => Some(x * 2))
    println(s"Option Monad: $optionMonadResult")
    
    val listMonadResult = listMonad.flatMap(List(1, 2, 3))(x => List(x, x * 2))
    println(s"List Monad: $listMonadResult")
    
    // 3. 高阶多态函数使用示例
    println("\n--- 高阶多态函数 ---")
    val liftedOptionFunction = liftOption((x: Int) => x * 2)
    println(s"提升的Option函数: ${liftedOptionFunction(Some(5))}")
    
    val liftedListFunction = liftList((x: Int) => x * 2)
    println(s"提升的List函数: ${liftedListFunction(List(1, 2, 3))}")
    
    // 4. sequence函数使用示例
    println("\n--- Sequence函数 ---")
    val optionList = List(Some(1), Some(2), Some(3))
    val sequencedOption = sequence(optionList)(optionMonad)
    println(s"Option序列化: $sequencedOption")
    
    val optionListWithNone = List(Some(1), None, Some(3))
    val sequencedOptionWithNone = sequence(optionListWithNone)(optionMonad)
    println(s"带None的Option序列化: $sequencedOptionWithNone")
    
    // 5. 验证示例
    println("\n--- 验证示例 ---")
    val validUser = validateUser("Alice", 25)
    println(s"有效用户验证: $validUser")
    
    val invalidUser = validateUser("", -5)
    println(s"无效用户验证: $invalidUser")
    
    // 6. 抽象类型成员使用示例
    println("\n--- 抽象类型成员 ---")
    val stringContainer = new StringContainer("Hello")
    val intContainer = new IntContainer(42)
    
    println(s"String容器值: ${processContainer(stringContainer)}")
    println(s"Int容器值: ${processContainer(intContainer)}")
    
    println("\n所有高阶类型示例完成")
  }
}

// 伴生对象用于组织类型类实例
object Semigroup {
  def apply[A](implicit instance: Semigroup[A]): Semigroup[A] = instance
}

object Monad {
  def apply[F[_]](implicit instance: Monad[F]): Monad[F] = instance
}

object Functor {
  def apply[F[_]](implicit instance: Functor[F]): Functor[F] = instance
}