// 方差示例

// 1. 不变性 (Invariance)
class InvariantContainer[T](val value: T) {
  override def toString: String = s"InvariantContainer($value)"
}

// 2. 协变 (Covariance)
class CovariantContainer[+A](val value: A) {
  override def toString: String = s"CovariantContainer($value)"
}

// 3. 逆变 (Contravariance)
class ContravariantConsumer[-A] {
  def consume(value: A): Unit = println(s"Consuming: $value")
  
  override def toString: String = "ContravariantConsumer"
}

// 4. 生产者示例 - 协变
trait Producer[+A] {
  def produce(): A
}

class IntProducer extends Producer[Int] {
  def produce(): Int = 42
}

class StringProducer extends Producer[String] {
  def produce(): String = "Hello"
}

// 5. 消费者示例 - 逆变
trait Consumer[-A] {
  def consume(item: A): Unit
}

class AnyConsumer extends Consumer[Any] {
  def consume(item: Any): Unit = println(s"Consuming any: $item")
}

class IntConsumer extends Consumer[Int] {
  def consume(item: Int): Unit = println(s"Consuming int: $item")
}

// 6. 不可变队列示例 - 协变
sealed abstract class ImmutableQueue[+A] {
  def enqueue[B >: A](elem: B): ImmutableQueue[B]
  def dequeue: (A, ImmutableQueue[A])
  def peek: Option[A]
  def size: Int
}

object ImmutableQueue {
  private case class NonEmptyQueue[+A](
    private val leading: List[A],
    private val trailing: List[A]
  ) extends ImmutableQueue[A] {
    def enqueue[B >: A](elem: B): ImmutableQueue[B] = 
      new NonEmptyQueue(leading, elem :: trailing)
      
    def dequeue: (A, ImmutableQueue[A]) = (leading, trailing) match {
      case (Nil, Nil) => throw new NoSuchElementException("Queue is empty")
      case (head :: tail, _) => 
        (head, makeQueue(tail, trailing))
      case (Nil, _) =>
        val reversed = trailing.reverse
        (reversed.head, makeQueue(reversed.tail, Nil))
    }
    
    def peek: Option[A] = (leading ::: trailing.reverse).headOption
    
    def size: Int = leading.length + trailing.length
    
    private def makeQueue[B >: A](lead: List[B], trail: List[B]): ImmutableQueue[B] = 
      new NonEmptyQueue(lead, trail)
  }
  
  private case object EmptyQueue extends ImmutableQueue[Nothing] {
    def enqueue[B >: Nothing](elem: B): ImmutableQueue[B] = 
      new NonEmptyQueue(List(elem), Nil)
    
    def dequeue: (Nothing, ImmutableQueue[Nothing]) = 
      throw new NoSuchElementException("Cannot dequeue from empty queue")
    
    def peek: Option[Nothing] = None
    def size: Int = 0
  }
  
  def empty[A]: ImmutableQueue[A] = EmptyQueue
  
  def apply[A](elements: A*): ImmutableQueue[A] = 
    elements.foldLeft(empty[A])(_.enqueue(_))
}

// 7. 方差示例对象
object VarianceExamples extends App {
  // 不变性示例
  println("=== 不变性示例 ===")
  val intContainer: InvariantContainer[Int] = new InvariantContainer(42)
  // val anyContainer: InvariantContainer[Any] = intContainer  // 编译错误
  println(intContainer)
  
  // 协变示例
  println("\n=== 协变示例 ===")
  val intCovariant: CovariantContainer[Int] = new CovariantContainer(42)
  val anyCovariant: CovariantContainer[Any] = intCovariant  // 正确，因为Int是Any的子类型
  println(intCovariant)
  println(anyCovariant)
  
  // 逆变示例
  println("\n=== 逆变示例 ===")
  val anyConsumer: ContravariantConsumer[Any] = new ContravariantConsumer()
  val intConsumer: ContravariantConsumer[Int] = anyConsumer  // 正确，因为Any是Int的超类型
  intConsumer.consume(42)  // 可以消费Int类型的值
  
  // 生产者示例
  println("\n=== 生产者示例 ===")
  val intProducer: Producer[Int] = new IntProducer
  val anyProducer: Producer[Any] = intProducer  // 正确，Producer是协变的
  println(s"Produced: ${anyProducer.produce()}")  // 输出: 42
  
  // 消费者示例
  println("\n=== 消费者示例 ===")
  val anyCons: Consumer[Any] = new AnyConsumer
  val intCons: Consumer[Int] = anyCons  // 正确，Consumer是逆变的
  intCons.consume(42)  // 可以消费Int类型的值
  
  // 不可变队列示例
  println("\n=== 不可变队列示例 ===")
  val queue = ImmutableQueue(1, 2, 3)
  println(s"Queue: $queue")
  println(s"Queue size: ${queue.size}")
  
  val (first, queue2) = queue.dequeue
  println(s"First element: $first")
  println(s"Queue after dequeue: $queue2")
  
  val queue3 = queue2.enqueue(4)
  println(s"Queue after enqueue 4: $queue3")
  
  // 协变队列示例
  val intQueue: ImmutableQueue[Int] = ImmutableQueue(1, 2, 3)
  val anyQueue: ImmutableQueue[Any] = intQueue  // 正确，队列是协变的
  println(s"Any queue: $anyQueue")
}