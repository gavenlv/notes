// 线程基础与同步示例

import java.lang.Thread
import java.util.concurrent.{Executors, ExecutorService, CountDownLatch, CyclicBarrier, Semaphore}
import java.util.concurrent.atomic.AtomicInteger
import scala.concurrent._
import ExecutionContext.Implicits.global

// 1. 基本线程示例
class SimpleTask extends Runnable {
  def run(): Unit = {
    println(s"Thread ${Thread.currentThread().getName} is running")
    Thread.sleep(1000)
    println(s"Thread ${Thread.currentThread().getName} finished")
  }
}

// 2. 线程安全的计数器
class Counter {
  private var value = 0
  
  def increment(): Unit = synchronized {
    value += 1
  }
  
  def get: Int = synchronized {
    value
  }
}

// 3. 原子计数器
class AtomicCounter {
  private val value = new AtomicInteger(0)
  
  def increment(): Int = value.incrementAndGet()
  def get: Int = value.get()
}

// 4. CountDownLatch示例
object CountDownLatchExample {
  def runTaskWithLatch(latch: CountDownLatch, taskId: Int): Future[Unit] = Future {
    Thread.sleep((math.random() * 1000).toLong)
    println(s"Task $taskId completed")
    latch.countDown()
  }
  
  def demo(): Unit = {
    val taskCount = 5
    val latch = new CountDownLatch(taskCount)
    
    for (i <- 1 to taskCount) {
      runTaskWithLatch(latch, i)
    }
    
    latch.await()  // 等待所有任务完成
    println("All tasks completed!")
  }
}

// 5. CyclicBarrier示例
object CyclicBarrierExample {
  def runTaskWithBarrier(barrier: CyclicBarrier, taskId: Int): Future[Unit] = Future {
    println(s"Task $taskId started")
    Thread.sleep((math.random() * 2000).toLong)
    println(s"Task $taskId reached barrier, waiting...")
    
    barrier.await()  // 等待其他任务
    
    println(s"Task $taskId passed barrier, continuing...")
  }
  
  def demo(): Unit = {
    val partyCount = 3
    val barrier = new CyclicBarrier(partyCount, () => {
      println("All parties reached barrier! Barrier action executed.")
    })
    
    for (i <- 1 to partyCount) {
      runTaskWithBarrier(barrier, i)
    }
  }
}

// 6. Semaphore示例
object SemaphoreExample {
  def demo(): Unit = {
    val semaphore = new Semaphore(2)  // 最多允许2个并发访问
    
    for (i <- 1 to 5) {
      Future {
        semaphore.acquire()
        try {
          println(s"Thread $i acquired permit")
          Thread.sleep(1000)
        } finally {
          println(s"Thread $i releasing permit")
          semaphore.release()
        }
      }
    }
  }
}

// 7. 生产者-消费者示例
class Buffer[T](capacity: Int) {
  private val buffer = new java.util.LinkedList[T]()
  private val notEmpty = new Object()
  private val notFull = new Object()
  
  def put(item: T): Unit = {
    notFull.synchronized {
      while (buffer.size() >= capacity) {
        notFull.wait()
      }
      buffer.add(item)
      notEmpty.notify()
    }
  }
  
  def take(): T = {
    notEmpty.synchronized {
      while (buffer.isEmpty) {
        notEmpty.wait()
      }
      val item = buffer.remove()
      notFull.notify()
      item
    }
  }
}

// 8. 读写锁示例
class ReadWriteLockMap[K, V] {
  private val map = scala.collection.mutable.Map[K, V]()
  private val readWriteLock = new java.util.concurrent.locks.ReentrantReadWriteLock()
  private val readLock = readWriteLock.readLock()
  private val writeLock = readWriteLock.writeLock()
  
  def get(key: K): Option[V] = {
    readLock.lock()
    try {
      map.get(key)
    } finally {
      readLock.unlock()
    }
  }
  
  def put(key: K, value: V): Unit = {
    writeLock.lock()
    try {
      map(key) = value
    } finally {
      writeLock.unlock()
    }
  }
  
  def remove(key: K): Option[V] = {
    writeLock.lock()
    try {
      map.remove(key)
    } finally {
      writeLock.unlock()
    }
  }
}

// 9. 主程序
object ThreadBasicsDemo extends App {
  // 1. 基本线程示例
  println("=== 基本线程示例 ===")
  val thread1 = new Thread(new SimpleTask)
  thread1.setName("Worker-1")
  thread1.start()
  
  val thread2 = new Thread(new SimpleTask)
  thread2.setName("Worker-2")
  thread2.start()
  
  // 2. 线程池示例
  println("\n=== 线程池示例 ===")
  val executor: ExecutorService = Executors.newFixedThreadPool(3)
  
  for (i <- 1 to 6) {
    executor.submit(new Runnable {
      def run(): Unit = {
        println(s"Pool Task $i running on ${Thread.currentThread().getName}")
        Thread.sleep(500)
      }
    })
  }
  
  executor.shutdown()
  executor.awaitTermination(10, TimeUnit.SECONDS)
  
  // 3. 计数器比较示例
  println("\n=== 计数器比较示例 ===")
  val iterations = 1000
  
  // 使用synchronized的计数器
  val counter = new Counter()
  val futures = List.fill(iterations)(Future { counter.increment() })
  Future.sequence(futures).onComplete(_ => println(s"Synchronized counter: ${counter.get}"))
  
  // 使用AtomicInteger的计数器
  val atomicCounter = new AtomicCounter()
  val atomicFutures = List.fill(iterations)(Future { atomicCounter.increment() })
  Future.sequence(atomicFutures).onComplete(_ => println(s"Atomic counter: ${atomicCounter.get}"))
  
  // 4. CountDownLatch示例
  println("\n=== CountDownLatch示例 ===")
  CountDownLatchExample.demo()
  
  Thread.sleep(2000)
  
  // 5. CyclicBarrier示例
  println("\n=== CyclicBarrier示例 ===")
  CyclicBarrierExample.demo()
  
  Thread.sleep(4000)
  
  // 6. Semaphore示例
  println("\n=== Semaphore示例 ===")
  SemaphoreExample.demo()
  
  Thread.sleep(3000)
  
  // 7. 生产者-消费者示例
  println("\n=== 生产者-消费者示例 ===")
  val buffer = new Buffer[Int](5)
  
  // 生产者
  for (i <- 1 to 2) {
    Future {
      for (item <- 1 to 5) {
        buffer.put(item)
        println(s"Producer put: $item")
        Thread.sleep((math.random() * 500).toLong)
      }
    }
  }
  
  // 消费者
  for (i <- 1 to 2) {
    Future {
      for (_ <- 1 to 5) {
        val item = buffer.take()
        println(s"Consumer took: $item")
        Thread.sleep((math.random() * 800).toLong)
      }
    }
  }
  
  Thread.sleep(6000)
  
  // 8. 读写锁示例
  println("\n=== 读写锁示例 ===")
  val rwMap = new ReadWriteLockMap[String, Int]()
  
  // 写入操作
  Future {
    rwMap.put("Scala", 1)
    println("Write: Scala -> 1")
  }
  
  // 读取操作（可以并行）
  for (i <- 1 to 5) {
    Future {
      val value = rwMap.get("Scala")
      println(s"Reader $i got: $value")
    }
  }
  
  Thread.sleep(1000)
  
  println("Thread basics demo completed!")
}