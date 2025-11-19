// 类型类示例
object TypeClassExamples {
  
  // 1. 基础类型类定义
  trait Show[A] {
    def show(a: A): String
  }
  
  // 2. 类型类实例
  object Show {
    // 为基本类型提供实例
    implicit val stringShow: Show[String] = new Show[String] {
      def show(a: String): String = s""""$a""""
    }
    
    implicit val intShow: Show[Int] = new Show[Int] {
      def show(a: Int): String = a.toString
    }
    
    implicit val booleanShow: Show[Boolean] = new Show[Boolean] {
      def show(a: Boolean): String = a.toString
    }
    
    // 为Option提供实例
    implicit def optionShow[A](implicit sa: Show[A]): Show[Option[A]] = new Show[Option[A]] {
      def show(a: Option[A]): String = a match {
        case Some(value) => s"Some(${sa.show(value)})"
        case None => "None"
      }
    }
    
    // 为List提供实例
    implicit def listShow[A](implicit sa: Show[A]): Show[List[A]] = new Show[List[A]] {
      def show(a: List[A]): String = 
        a.map(sa.show).mkString("List(", ", ", ")")
    }
  }
  
  // 3. 接口对象
  object ShowOps {
    def show[A](a: A)(implicit sa: Show[A]): String = sa.show(a)
    
    // 语法糖
    implicit class ShowSyntax[A](a: A) {
      def show(implicit sa: Show[A]): String = sa.show(a)
    }
  }
  
  // 4. 更复杂的类型类：Equal
  trait Equal[A] {
    def equal(a1: A, a2: A): Boolean
  }
  
  object Equal {
    implicit val stringEqual: Equal[String] = new Equal[String] {
      def equal(a1: String, a2: String): Boolean = a1 == a2
    }
    
    implicit val intEqual: Equal[Int] = new Equal[Int] {
      def equal(a1: Int, a2: Int): Boolean = a1 == a2
    }
    
    // 为Option提供实例
    implicit def optionEqual[A](implicit ea: Equal[A]): Equal[Option[A]] = new Equal[Option[A]] {
      def equal(a1: Option[A], a2: Option[A]): Boolean = (a1, a2) match {
        case (Some(v1), Some(v2)) => ea.equal(v1, v2)
        case (None, None) => true
        case _ => false
      }
    }
  }
  
  // 5. 类型类约束
  def compareIfExists[A](a1: Option[A], a2: Option[A])(implicit ea: Equal[A]): Boolean = {
    Equal.optionEqual(ea).equal(a1, a2)
  }
  
  // 6. Semigroup类型类
  trait Semigroup[A] {
    def combine(a1: A, a2: A): A
  }
  
  object Semigroup {
    implicit val intSemigroup: Semigroup[Int] = new Semigroup[Int] {
      def combine(a1: Int, a2: Int): Int = a1 + a2
    }
    
    implicit val stringSemigroup: Semigroup[String] = new Semigroup[String] {
      def combine(a1: String, a2: String): String = a1 + a2
    }
    
    implicit def optionSemigroup[A](implicit sa: Semigroup[A]): Semigroup[Option[A]] = new Semigroup[Option[A]] {
      def combine(a1: Option[A], a2: Option[A]): Option[A] = (a1, a2) match {
        case (Some(v1), Some(v2)) => Some(sa.combine(v1, v2))
        case (Some(v1), None) => Some(v1)
        case (None, Some(v2)) => Some(v2)
        case (None, None) => None
      }
    }
  }
  
  // 7. Monoid类型类（继承Semigroup）
  trait Monoid[A] extends Semigroup[A] {
    def empty: A
  }
  
  object Monoid {
    implicit val intMonoid: Monoid[Int] = new Monoid[Int] {
      def empty: Int = 0
      def combine(a1: Int, a2: Int): Int = a1 + a2
    }
    
    implicit val stringMonoid: Monoid[String] = new Monoid[String] {
      def empty: String = ""
      def combine(a1: String, a2: String): String = a1 + a2
    }
  }
  
  // 8. 使用Monoid进行折叠
  def fold[A](list: List[A])(implicit ma: Monoid[A]): A = {
    list.foldLeft(ma.empty)(ma.combine)
  }
  
  // 9. Functor类型类
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
  
  // 10. 类型类的高级应用：JSON序列化
  sealed trait Json
  case object JsonNull extends Json
  case class JsonString(value: String) extends Json
  case class JsonNumber(value: Double) extends Json
  case class JsonBoolean(value: Boolean) extends Json
  case class JsonArray(values: List[Json]) extends Json
  case class JsonObject(fields: Map[String, Json]) extends Json
  
  trait JsonEncoder[A] {
    def encode(a: A): Json
  }
  
  object JsonEncoder {
    implicit val stringEncoder: JsonEncoder[String] = new JsonEncoder[String] {
      def encode(a: String): Json = JsonString(a)
    }
    
    implicit val intEncoder: JsonEncoder[Int] = new JsonEncoder[Int] {
      def encode(a: Int): Json = JsonNumber(a.toDouble)
    }
    
    implicit val booleanEncoder: JsonEncoder[Boolean] = new JsonEncoder[Boolean] {
      def encode(a: Boolean): Json = JsonBoolean(a)
    }
    
    implicit def listEncoder[A](implicit ea: JsonEncoder[A]): JsonEncoder[List[A]] = 
      new JsonEncoder[List[A]] {
        def encode(a: List[A]): Json = JsonArray(a.map(ea.encode))
      }
    
    implicit def optionEncoder[A](implicit ea: JsonEncoder[A]): JsonEncoder[Option[A]] = 
      new JsonEncoder[Option[A]] {
        def encode(a: Option[A]): Json = a match {
          case Some(value) => ea.encode(value)
          case None => JsonNull
        }
      }
  }
  
  // 11. JSON编码工具
  object JsonOps {
    def toJson[A](a: A)(implicit ea: JsonEncoder[A]): Json = ea.encode(a)
    
    implicit class JsonSyntax[A](a: A) {
      def toJson(implicit ea: JsonEncoder[A]): Json = ea.encode(a)
    }
  }
  
  // 12. 实际应用类
  case class Person(name: String, age: Int)
  case class Company(name: String, employees: List[Person])
  
  object Person {
    implicit val personEncoder: JsonEncoder[Person] = new JsonEncoder[Person] {
      def encode(p: Person): Json = JsonObject(Map(
        "name" -> JsonString(p.name),
        "age" -> JsonNumber(p.age.toDouble)
      ))
    }
  }
  
  object Company {
    implicit val companyEncoder: JsonEncoder[Company] = new JsonEncoder[Company] {
      def encode(c: Company): Json = JsonObject(Map(
        "name" -> JsonString(c.name),
        "employees" -> JsonArray(c.employees.map(_.toJson))
      ))
    }
  }
  
  // 13. 类型类派生
  trait Default[A] {
    def default: A
  }
  
  object Default {
    implicit val intDefault: Default[Int] = new Default[Int] {
      def default: Int = 0
    }
    
    implicit val stringDefault: Default[String] = new Default[String] {
      def default: String = ""
    }
    
    implicit val booleanDefault: Default[Boolean] = new Default[Boolean] {
      def default: Boolean = false
    }
    
    implicit def optionDefault[A]: Default[Option[A]] = new Default[Option[A]] {
      def default: Option[A] = None
    }
  }
  
  // 14. 使用示例
  def main(args: Array[String]): Unit = {
    println("=== 类型类示例 ===")
    
    import ShowOps._
    
    // 1. Show类型类使用
    println("\n--- Show类型类 ---")
    println(s"String显示: ${"Hello".show}")
    println(s"Int显示: ${42.show}")
    println(s"Boolean显示: ${true.show}")
    println(s"Option显示: ${Some("Scala").show}")
    println(s"List显示: ${List(1, 2, 3).show}")
    
    // 2. Equal类型类使用
    println("\n--- Equal类型类 ---")
    println(s"字符串相等: ${Equal.stringEqual.equal("Hello", "Hello")}")
    println(s"Option相等: ${compareIfExists(Some(42), Some(42))}")
    
    // 3. Semigroup和Monoid使用
    println("\n--- Semigroup和Monoid ---")
    println(s"Int组合: ${Semigroup.intSemigroup.combine(1, 2)}")
    println(s"String组合: ${Semigroup.stringSemigroup.combine("Hello", " World")}")
    println(s"List折叠: ${fold(List(1, 2, 3, 4, 5))}")
    println(s"String折叠: ${fold(List("Hello", " ", "World"))}")
    
    // 4. Functor使用
    println("\n--- Functor ---")
    println(s"List映射: ${Functor.listFunctor.map(List(1, 2, 3))(_ * 2)}")
    println(s"Option映射: ${Functor.optionFunctor.map(Some(5))(_ * 2)}")
    
    // 5. JSON编码
    println("\n--- JSON编码 ---")
    import JsonOps._
    
    val person = Person("Alice", 25)
    val jsonPerson = person.toJson
    println(s"Person JSON: $jsonPerson")
    
    val company = Company("Scala Inc.", List(person, Person("Bob", 30)))
    val jsonCompany = company.toJson
    println(s"Company JSON: $jsonCompany")
    
    // 6. 默认值
    println("\n--- 默认值 ---")
    println(s"Int默认值: ${Default.intDefault.default}")
    println(s"String默认值: ${Default.stringDefault.default}")
    println(s"Option默认值: ${Default.optionDefault[String].default}")
    
    println("\n所有类型类示例完成")
  }
}