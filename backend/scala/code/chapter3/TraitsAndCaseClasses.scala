object TraitsAndCaseClasses {
  def main(args: Array[String]): Unit = {
    // 特质定义与使用
    trait Swimmer {
      def swim(): Unit
      
      def dive(): Unit = println("Diving deep!")
      
      val maxDepth: Int = 100
    }
    
    trait Flyer {
      def fly(): Unit
      
      def takeOff(): Unit = println("Taking off")
      def land(): Unit = println("Landing")
    }
    
    class Duck extends Swimmer with Flyer {
      def swim(): Unit = println("Swimming like a duck")
      
      def fly(): Unit = println("Flying like a duck")
      
      def quack(): Unit = println("Quack!")
    }
    
    val duck = new Duck()
    duck.swim()
    duck.dive()
    duck.fly()
    duck.takeOff()
    duck.land()
    duck.quack()
    
    // 样例类
    case class Person(name: String, age: Int, email: String)
    
    val person1 = Person("Alice", 30, "alice@example.com")
    val person2 = Person("Bob", 25, "bob@example.com")
    
    // 自动生成的toString
    println(person1)
    
    // 自动生成的equals方法
    val person3 = Person("Alice", 30, "alice@example.com")
    println(person1 == person3)  // true
    println(person1 == person2)  // false
    
    // 自动生成的copy方法
    val olderPerson = person1.copy(age = person1.age + 1)
    println(olderPerson)
    
    // 解构
    val Person(name, age, email) = person1
    println(s"Name: $name, Age: $age, Email: $email")
    
    // 样例对象
    sealed trait Message
    case class TextMessage(content: String) extends Message
    case class ImageMessage(url: String, caption: String) extends Message
    case object ShutdownMessage extends Message
    
    def processMessage(message: Message): Unit = {
      message match {
        case TextMessage(content) => println(s"Text: $content")
        case ImageMessage(url, caption) => println(s"Image: $url ($caption)")
        case ShutdownMessage => println("Shutting down...")
      }
    }
    
    processMessage(TextMessage("Hello, world!"))
    processMessage(ImageMessage("http://example.com/image.jpg", "A cat"))
    processMessage(ShutdownMessage)
    
    // 嵌套样例类
    case class Address(street: String, city: String, zipCode: String)
    case class PersonWithAddress(name: String, age: Int, address: Address)
    
    val address = Address("123 Main St", "Anytown", "12345")
    val personWithAddress = PersonWithAddress("John Doe", 35, address)
    
    // 深度解构
    val PersonWithAddress(name, age, Address(street, city, zipCode)) = personWithAddress
    println(s"$name lives at $street in $city ($zipCode)")
    
    // 可堆叠特质修改
    trait IntQueue {
      def get(): Int
      def put(x: Int): Unit
    }
    
    class BasicIntQueue extends IntQueue {
      private val buf = new scala.collection.mutable.Queue[Int]()
      
      def get(): Int = buf.dequeue()
      def put(x: Int): Unit = buf.enqueue(x)
    }
    
    trait Doubling extends IntQueue {
      abstract override def put(x: Int): Unit = {
        super.put(2 * x)
      }
    }
    
    trait Incrementing extends IntQueue {
      abstract override def put(x: Int): Unit = {
        super.put(x + 1)
      }
    }
    
    trait Filtering extends IntQueue {
      abstract override def put(x: Int): Unit = {
        if (x >= 0) super.put(x)
      }
    }
    
    val queue1 = new BasicIntQueue
    queue1.put(10)
    queue1.put(20)
    println(queue1.get())
    println(queue1.get())
    
    val queue2 = new BasicIntQueue with Incrementing with Filtering
    queue2.put(-1)
    queue2.put(0)
    queue2.put(1)
    println(queue2.get())
    println(queue2.get())
    
    val queue3 = new BasicIntQueue with Doubling with Incrementing with Filtering
    queue3.put(-1)
    queue3.put(0)
    queue3.put(1)
    println(queue3.get())
    println(queue3.get())
  }
}