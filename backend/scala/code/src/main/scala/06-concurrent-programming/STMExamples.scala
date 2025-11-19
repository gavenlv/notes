import scala.concurrent.{Future, ExecutionContext}
import scala.concurrent.duration._
import java.util.concurrent.atomic.AtomicInteger
import scala.language.postfixOps

// 简化的STM实现示例
object STMExamples {
  implicit val ec: ExecutionContext = ExecutionContext.global
  
  // 1. 基于AtomicReference的简单STM实现
  import java.util.concurrent.atomic.AtomicReference
  
  // 事务引用
  class TRef[A](initial: A) {
    private val ref = new AtomicReference[A](initial)
    
    def get(): A = ref.get()
    def set(value: A): Unit = ref.set(value)
    def compareAndSet(expect: A, update: A): Boolean = ref.compareAndSet(expect, update)
  }
  
  // 简单的事务实现
  class Transaction {
    private val reads = scala.collection.mutable.Map[TRef[_], Any]()
    private val writes = scala.collection.mutable.Map[TRef[_], Any]()
    
    def read[A](ref: TRef[A]): A = {
      val value = ref.get()
      reads.put(ref, value)
      value.asInstanceOf[A]
    }
    
    def write[A](ref: TRef[A], value: A): Unit = {
      writes.put(ref, value)
    }
    
    def commit(): Boolean = {
      // 简化的提交逻辑
      // 实际的STM实现会更复杂，需要验证读操作期间值没有改变
      writes.foreach { case (ref, value) =>
        ref.set(value)
      }
      true
    }
  }
  
  // 2. 银行账户示例
  class BankAccount(val id: String, initialBalance: Int) {
    private val balance = new TRef[Int](initialBalance)
    
    def getBalance(): Int = balance.get()
    
    def deposit(amount: Int): Unit = {
      val transaction = new Transaction()
      val currentBalance = transaction.read(balance)
      transaction.write(balance, currentBalance + amount)
      transaction.commit()
      println(s"账户 $id 存入 $amount，余额: ${getBalance()}")
    }
    
    def withdraw(amount: Int): Boolean = {
      val transaction = new Transaction()
      val currentBalance = transaction.read(balance)
      if (currentBalance >= amount) {
        transaction.write(balance, currentBalance - amount)
        transaction.commit()
        println(s"账户 $id 取出 $amount，余额: ${getBalance()}")
        true
      } else {
        println(s"账户 $id 余额不足，当前余额: $currentBalance")
        false
      }
    }
    
    def transferTo(target: BankAccount, amount: Int): Boolean = {
      // 简化的转账实现
      if (withdraw(amount)) {
        target.deposit(amount)
        true
      } else {
        false
      }
    }
  }
  
  // 3. 使用Akka STM（需要额外依赖）
  /*
  // 注意：这需要akka-agent依赖
  import akka.agent.Agent
  
  class AkkaSTMExample {
    val account1 = Agent(1000)
    val account2 = Agent(500)
    
    def transfer(amount: Int): Unit = {
      if (account1.get() >= amount) {
        // 原子性转账操作
        Agent.atomic { txn =>
          account1.send(account1.get() - amount)(txn)
          account2.send(account2.get() + amount)(txn)
        }
      }
    }
  }
  */
  
  // 4. 无锁计数器示例
  class LockFreeCounter {
    private val counter = new AtomicInteger(0)
    
    def increment(): Int = counter.incrementAndGet()
    def decrement(): Int = counter.decrementAndGet()
    def get(): Int = counter.get()
    def compareAndSwap(expect: Int, update: Int): Boolean = counter.compareAndSet(expect, update)
  }
  
  // 5. 生产者-消费者示例
  import java.util.concurrent.ConcurrentLinkedQueue
  
  class ProducerConsumerExample {
    private val queue = new ConcurrentLinkedQueue[String]()
    private val lockFreeCounter = new LockFreeCounter()
    
    def produce(item: String): Unit = {
      queue.offer(item)
      lockFreeCounter.increment()
      println(s"生产: $item，队列大小: ${queue.size()}")
    }
    
    def consume(): Option[String] = {
      val item = queue.poll()
      if (item != null) {
        lockFreeCounter.decrement()
        println(s"消费: $item，队列大小: ${queue.size()}")
        Some(item)
      } else {
        None
      }
    }
    
    def size(): Int = lockFreeCounter.get()
  }
  
  // 6. 读写锁示例
  import java.util.concurrent.locks.ReentrantReadWriteLock
  
  class ReadWriteLockExample {
    private val data = new TRef[String]("Initial Data")
    private val lock = new ReentrantReadWriteLock()
    
    def readData(): String = {
      val readLock = lock.readLock()
      readLock.lock()
      try {
        data.get()
      } finally {
        readLock.unlock()
      }
    }
    
    def writeData(newData: String): Unit = {
      val writeLock = lock.writeLock()
      writeLock.lock()
      try {
        data.set(newData)
        println(s"数据更新为: $newData")
      } finally {
        writeLock.unlock()
      }
    }
  }
  
  def main(args: Array[String]): Unit = {
    println("=== STM和无锁编程示例 ===")
    
    // 1. 银行账户示例
    println("\n--- 银行账户示例 ---")
    val account1 = new BankAccount("ACC001", 1000)
    val account2 = new BankAccount("ACC002", 500)
    
    println(s"初始余额 - 账户1: ${account1.getBalance()}, 账户2: ${account2.getBalance()}")
    
    // 存款
    account1.deposit(200)
    account2.deposit(100)
    
    // 取款
    account1.withdraw(150)
    account2.withdraw(700) // 余额不足
    
    // 转账
    account1.transferTo(account2, 300)
    
    println(s"最终余额 - 账户1: ${account1.getBalance()}, 账户2: ${account2.getBalance()}")
    
    // 2. 生产者-消费者示例
    println("\n--- 生产者-消费者示例 ---")
    val pc = new ProducerConsumerExample()
    
    // 生产
    pc.produce("Item1")
    pc.produce("Item2")
    pc.produce("Item3")
    
    // 消费
    pc.consume()
    pc.consume()
    
    println(s"当前队列大小: ${pc.size()}")
    
    // 3. 读写锁示例
    println("\n--- 读写锁示例 ---")
    val rwExample = new ReadWriteLockExample()
    
    println(s"初始数据: ${rwExample.readData()}")
    
    // 写入数据
    rwExample.writeData("Updated Data")
    
    // 读取数据
    println(s"更新后数据: ${rwExample.readData()}")
    
    // 4. 并发测试
    println("\n--- 并发测试 ---")
    val counter = new LockFreeCounter()
    
    // 创建多个并发任务
    val futures = (1 to 10).map { i =>
      Future {
        (1 to 100).foreach { _ =>
          counter.increment()
        }
      }
    }
    
    // 等待所有任务完成
    Thread.sleep(2000)
    
    println(s"并发计数结果: ${counter.get()}")
    
    println("所有STM示例完成")
  }
}