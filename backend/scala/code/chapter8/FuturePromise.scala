// Future和Promise示例

import scala.concurrent._
import ExecutionContext.Implicits.global
import scala.concurrent.duration._
import scala.util.{Success, Failure, Try}
import java.util.concurrent.TimeoutException

// 1. Future基础示例
object FutureBasics {
  // 创建Future的不同方式
  def createFutures(): Unit = {
    // 使用Future.apply
    val future1 = Future {
      Thread.sleep(1000)
      42
    }
    
    // 使用Future.successful创建已完成的Future
    val future2 = Future.successful("Already done")
    
    // 使用Future.failed创建失败的Future
    val future3 = Future.failed(new RuntimeException("Failed"))
    
    // 处理结果
    future1.onComplete {
      case Success(value) => println(s"Future1 completed with: $value")
      case Failure(exception) => println(s"Future1 failed with: ${exception.getMessage}")
    }
    
    future2.onComplete {
      case Success(value) => println(s"Future2 completed with: $value")
      case Failure(exception) => println(s"Future2 failed with: ${exception.getMessage}")
    }
    
    future3.onComplete {
      case Success(value) => println(s"Future3 completed with: $value")
      case Failure(exception) => println(s"Future3 failed with: ${exception.getMessage}")
    }
  }
  
  // 组合Future
  def combineFutures(): Unit = {
    val future1 = Future {
      Thread.sleep(500)
      "Hello"
    }
    
    val future2 = Future {
      Thread.sleep(1000)
      "World"
    }
    
    // 使用for组合
    val combined = for {
      hello <- future1
      world <- future2
    } yield s"$hello $world"
    
    combined.foreach(println)
    
    // 使用zip组合
    val zipped = future1.zip(future2).map { case (h, w) => s"$h $w" }
    zipped.foreach(result => println(s"Zipped result: $result"))
  }
  
  // 序列Future
  def sequenceFutures(): Unit = {
    val futures = (1 to 5).map { i =>
      Future {
        Thread.sleep(i * 100)
        i * i
      }
    }
    
    // 使用Future.sequence
    val sequence = Future.sequence(futures)
    sequence.foreach(results => println(s"Sequence result: $results"))
    
    // 使用Future.traverse
    val traverse = Future.traverse((1 to 5).toList) { i =>
      Future {
        Thread.sleep(i * 100)
        i * i
      }
    }
    traverse.foreach(results => println(s"Traverse result: $results"))
  }
}

// 2. Promise基础示例
object PromiseBasics {
  // 基本Promise使用
  def basicPromise(): Unit = {
    val promise = Promise[String]()
    val future = promise.future
    
    // 处理结果
    future.foreach(println)
    
    // 在另一个线程中完成Promise
    Future {
      Thread.sleep(1000)
      promise.success("Hello from Promise!")
    }
  }
  
  // 模拟异步操作
  def simulateAsyncOperation(input: Int): Future[Int] = {
    val promise = Promise[Int]()
    
    Future {
      Thread.sleep((math.random() * 1000).toLong)
      if (input > 0) {
        promise.success(input * 2)
      } else {
        promise.failure(new IllegalArgumentException("Input must be positive"))
      }
    }
    
    promise.future
  }
  
  // 使用Promise转换回调为Future
  def callbackToFuture[T](callback: (T => Unit) => Unit): Future[T] = {
    val promise = Promise[T]()
    
    callback { result =>
      promise.success(result)
    }
    
    promise.future
  }
  
  // 使用Promise协调多个Future
  def coordinateFutures(): Unit = {
    val stringPromise = Promise[String]()
    val intPromise = Promise[Int]()
    
    Future {
      Thread.sleep(500)
      stringPromise.success("Hello")
    }
    
    Future {
      Thread.sleep(1000)
      intPromise.success(42)
    }
    
    val combined = for {
      str <- stringPromise.future
      num <- intPromise.future
    } yield (str, num)
    
    combined.foreach { case (str, num) =>
      println(s"Coordinated result: $str, $num")
    }
  }
}

// 3. 并发工具示例
object ConcurrentUtils {
  // 限制并发数
  def limitConcurrent[T](tasks: List[() => T], maxConcurrency: Int): List[Future[T]] = {
    val semaphore = new java.util.concurrent.Semaphore(maxConcurrency)
    
    tasks.map { task =>
      Future {
        semaphore.acquire()
        try {
          task()
        } finally {
          semaphore.release()
        }
      }
    }
  }
  
  // 超时处理
  def withTimeout[T](future: Future[T], timeout: FiniteDuration): Future[T] = {
    val timeoutFuture = Future {
      Thread.sleep(timeout.toMillis)
      throw new TimeoutException(s"Operation timed out after $timeout")
    }
    
    Future.firstCompletedOf(List(future, timeoutFuture))
  }
  
  // 重试机制
  def retry[T](operation: () => Future[T], maxRetries: Int): Future[T] = {
    operation().recoverWith {
      case _ if maxRetries > 0 =>
        Thread.sleep(100)
        retry(operation, maxRetries - 1)
      case ex if maxRetries <= 0 =>
        Future.failed(new RuntimeException(s"Operation failed after $maxRetries retries", ex))
    }
  }
  
  // 批量处理
  def batchProcess[T, R](items: List[T], batchSize: Int, 
                         processor: List[T] => Future[List[R]]): Future[List[R]] = {
    if (items.isEmpty) {
      Future.successful(List.empty[R])
    } else {
      val (batch, remaining) = items.splitAt(batchSize)
      val batchResult = processor(batch)
      val remainingResult = batchProcess(remaining, batchSize, processor)
      
      for {
        batchRes <- batchResult
        remainingRes <- remainingResult
      } yield batchRes ::: remainingRes
    }
  }
  
  // 限流操作
  def rateLimited[T](operations: List[() => T], ratePerSecond: Int): List[Future[T]] = {
    val interval = 1000 / ratePerSecond
    
    operations.zipWithIndex.map { case (op, index) =>
      val delay = index * interval
      Future {
        Thread.sleep(delay)
        op()
      }
    }
  }
}

// 4. Future性能示例
object FuturePerformance {
  // 顺序vs并行比较
  def sequentialVsParallel(): Unit = {
    def processData(item: Int): Int = {
      Thread.sleep(100)  // 模拟处理时间
      item * 2
    }
    
    val data = (1 to 10).toList
    
    // 顺序处理
    val sequentialStart = System.currentTimeMillis()
    val sequentialResult = data.map(processData)
    val sequentialTime = System.currentTimeMillis() - sequentialStart
    
    // 并行处理
    val parallelStart = System.currentTimeMillis()
    val parallelResultFuture = Future.sequence(data.map(item => Future(processData(item))))
    val parallelResult = Await.result(parallelResultFuture, 10.seconds)
    val parallelTime = System.currentTimeMillis() - parallelStart
    
    println(s"Sequential time: ${sequentialTime}ms")
    println(s"Parallel time: ${parallelTime}ms")
    println(s"Speedup: ${sequentialTime.toDouble / parallelTime}")
    
    assert(sequentialResult == parallelResult)
  }
  
  // Future组合性能测试
  def compositionPerformance(): Unit = {
    def createNestedFutures(depth: Int): Future[Int] = {
      if (depth <= 0) {
        Future.successful(0)
      } else {
        val current = Future {
          Thread.sleep(10)
          depth
        }
        
        current.flatMap { value =>
          createNestedFutures(depth - 1).map(_ + value)
        }
      }
    }
    
    val depths = List(5, 10, 15, 20)
    
    depths.foreach { depth =>
      val start = System.currentTimeMillis()
      val result = Await.result(createNestedFutures(depth), 30.seconds)
      val time = System.currentTimeMillis() - start
      
      println(s"Depth $depth: time=${time}ms, result=$result")
    }
  }
}

// 5. 主程序
object FuturePromiseDemo extends App {
  // 1. Future基础示例
  println("=== Future基础示例 ===")
  FutureBasics.createFutures()
  Thread.sleep(2000)
  
  FutureBasics.combineFutures()
  Thread.sleep(2000)
  
  FutureBasics.sequenceFutures()
  Thread.sleep(2000)
  
  // 2. Promise基础示例
  println("\n=== Promise基础示例 ===")
  PromiseBasics.basicPromise()
  Thread.sleep(2000)
  
  // 异步操作示例
  (1 to 3).foreach { i =>
    val future = PromiseBasics.simulateAsyncOperation(i)
    future.onComplete {
      case Success(result) => println(s"Operation $i succeeded: $result")
      case Failure(exception) => println(s"Operation $i failed: ${exception.getMessage}")
    }
  }
  Thread.sleep(2000)
  
  PromiseBasics.coordinateFutures()
  Thread.sleep(2000)
  
  // 3. 并发工具示例
  println("\n=== 并发工具示例 ===")
  
  // 限制并发数示例
  val tasks = (1 to 10).toList.map(i => () => {
    Thread.sleep(500)
    i * i
  })
  
  val limitedFutures = ConcurrentUtils.limitConcurrent(tasks, 3)
  limitedFutures.foreach(_.foreach(result => println(s"Task completed: $result")))
  
  // 超时处理示例
  val longOperation = Future {
    Thread.sleep(2000)
    "Completed"
  }
  
  val withTimeout = ConcurrentUtils.withTimeout(longOperation, 1.second)
  withTimeout.onComplete {
    case Success(value) => println(s"Operation succeeded: $value")
    case Failure(_: TimeoutException) => println("Operation timed out")
    case Failure(ex) => println(s"Operation failed: ${ex.getMessage}")
  }
  
  Thread.sleep(3000)
  
  // 重试机制示例
  val flakyOperation = () => Future {
    if (math.random() > 0.7) {
      "Success"
    } else {
      throw new RuntimeException("Random failure")
    }
  }
  
  val retryResult = ConcurrentUtils.retry(flakyOperation, 5)
  retryResult.onComplete {
    case Success(value) => println(s"Retry succeeded: $value")
    case Failure(ex) => println(s"Retry failed after all attempts: ${ex.getMessage}")
  }
  
  Thread.sleep(3000)
  
  // 4. 性能测试
  println("\n=== 性能测试 ===")
  FuturePerformance.sequentialVsParallel()
  Thread.sleep(3000)
  
  FuturePerformance.compositionPerformance()
  Thread.sleep(5000)
  
  println("Future and Promise demo completed!")
}