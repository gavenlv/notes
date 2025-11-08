import scala.concurrent.{Future, ExecutionContext, blocking}
import scala.concurrent.duration._
import java.util.concurrent.{Executors, ForkJoinPool, ConcurrentHashMap}
import scala.util.{Success, Failure, Try}
import scala.language.postfixOps

object PerformanceExamples {
  implicit val ec: ExecutionContext = ExecutionContext.global
  
  // 1. Future性能优化示例
  object FutureOptimization {
    // 避免阻塞操作阻塞线程池
    def blockingOperation(id: Int): Int = {
      Thread.sleep(100) // 模拟阻塞操作
      id * 2
    }
    
    // 正确使用blocking
    def optimizedBlockingOperation(id: Int): Future[Int] = {
      Future {
        blocking {
          Thread.sleep(100) // 使用blocking包装阻塞操作
          id * 2
        }
      }
    }
    
    // 并行处理大量数据
    def parallelProcessing(data: List[Int]): Future[List[Int]] = {
      Future.traverse(data) { item =>
        Future {
          // 模拟CPU密集型操作
          Thread.sleep(10)
          item * item
        }
      }
    }
    
    // 批量处理优化
    def batchProcessing(data: List[Int], batchSize: Int = 100): Future[List[Int]] = {
      val batches = data.grouped(batchSize).toList
      Future.traverse(batches) { batch =>
        Future {
          batch.map { item =>
            // 批量处理
            Thread.sleep(1)
            item * 2
          }
        }
      }.map(_.flatten)
    }
  }
  
  // 2. 并发集合性能示例
  object ConcurrentCollections {
    // 使用ConcurrentHashMap
    val concurrentMap = new ConcurrentHashMap[String, Int]()
    
    // 传统的同步集合
    val synchronizedMap = scala.collection.mutable.Map[String, Int]()
    
    // 并发写入测试
    def concurrentWrites(keyPrefix: String, count: Int): Unit = {
      val futures = (1 to count).map { i =>
        Future {
          concurrentMap.put(s"$keyPrefix$i", i)
        }
      }
      // 等待完成
      futures.foreach(_.value)
    }
    
    // 同步写入测试
    def synchronizedWrites(keyPrefix: String, count: Int): Unit = {
      val futures = (1 to count).map { i =>
        Future {
          synchronizedMap.synchronized {
            synchronizedMap.put(s"$keyPrefix$i", i)
          }
        }
      }
      // 等待完成
      futures.foreach(_.value)
    }
  }
  
  // 3. ExecutionContext优化
  object ExecutionContextOptimization {
    // 自定义优化的ExecutionContext
    val optimizedExecutionContext = ExecutionContext.fromExecutor(
      new ForkJoinPool(
        Runtime.getRuntime.availableProcessors() * 2,
        ForkJoinPool.defaultForkJoinWorkerThreadFactory,
        null, // UncaughtExceptionHandler
        true  // asyncMode
      )
    )
    
    // CPU密集型任务的ExecutionContext
    val cpuIntensiveExecutionContext = ExecutionContext.fromExecutor(
      Executors.newFixedThreadPool(Runtime.getRuntime.availableProcessors())
    )
    
    // IO密集型任务的ExecutionContext
    val ioIntensiveExecutionContext = ExecutionContext.fromExecutor(
      Executors.newCachedThreadPool()
    )
  }
  
  // 4. 内存优化示例
  object MemoryOptimization {
    // 使用视图避免中间集合创建
    def viewExample(data: List[Int]): List[Int] = {
      data.view
        .filter(_ % 2 == 0)
        .map(_ * 2)
        .take(10)
        .toList
    }
    
    // 使用迭代器处理大数据集
    def iteratorExample(data: List[Int]): List[Int] = {
      data.iterator
        .filter(_ % 2 == 0)
        .map(_ * 2)
        .take(10)
        .toList
    }
    
    // 避免内存泄漏的Future链
    def memoryEfficientFutureChain(): Future[Int] = {
      Future(1)
        .map(_ + 1)
        .flatMap(x => Future(x * 2))
        .map(_ + 1)
    }
  }
  
  // 5. 性能测试工具
  object PerformanceTesting {
    def timeIt[T](operation: => T): (T, Long) = {
      val start = System.nanoTime()
      val result = operation
      val end = System.nanoTime()
      (result, (end - start) / 1000000) // 返回毫秒
    }
    
    def timeFuture[T](future: Future[T]): Future[(T, Long)] = {
      val start = System.nanoTime()
      future.map { result =>
        val end = System.nanoTime()
        (result, (end - start) / 1000000)
      }
    }
  }
  
  // 6. 并发性能对比示例
  object ConcurrencyComparison {
    // 串行处理
    def sequentialProcessing(data: List[Int]): List[Int] = {
      data.map { item =>
        Thread.sleep(1) // 模拟处理时间
        item * 2
      }
    }
    
    // 并行处理
    def parallelProcessing(data: List[Int])(implicit ec: ExecutionContext): Future[List[Int]] = {
      Future.traverse(data) { item =>
        Future {
          Thread.sleep(1) // 模拟处理时间
          item * 2
        }
      }
    }
    
    // 使用并行集合
    def parallelCollectionProcessing(data: List[Int]): List[Int] = {
      data.par.map { item =>
        Thread.sleep(1) // 模拟处理时间
        item * 2
      }.toList
    }
  }
  
  def main(args: Array[String]): Unit = {
    println("=== 并发编程性能优化示例 ===")
    
    import PerformanceTesting._
    
    // 1. Future性能优化示例
    println("\n--- Future性能优化示例 ---")
    val data = (1 to 1000).toList
    
    // 并行处理性能测试
    val (parallelResult, parallelTime) = timeIt {
      val future = FutureOptimization.parallelProcessing(data.take(100))
      // 等待结果
      future.value
    }
    println(s"并行处理时间: $parallelTime ms")
    
    // 批量处理性能测试
    val (batchResult, batchTime) = timeIt {
      val future = FutureOptimization.batchProcessing(data.take(100))
      future.value
    }
    println(s"批量处理时间: $batchTime ms")
    
    // 2. 并发集合性能对比
    println("\n--- 并发集合性能对比 ---")
    val testCount = 1000
    
    // ConcurrentHashMap性能测试
    val (concurrentWrites, concurrentTime) = timeIt {
      ConcurrentCollections.concurrentWrites("concurrent", testCount)
    }
    println(s"ConcurrentHashMap写入时间: $concurrentTime ms")
    
    // Synchronized Map性能测试
    val (syncWrites, syncTime) = timeIt {
      ConcurrentCollections.synchronizedWrites("sync", testCount)
    }
    println(s"Synchronized Map写入时间: $syncTime ms")
    
    println(s"ConcurrentHashMap比Synchronized Map快 ${syncTime.toDouble / concurrentTime.toDouble} 倍")
    
    // 3. 内存优化示例
    println("\n--- 内存优化示例 ---")
    val largeData = (1 to 10000).toList
    
    val (viewResult, viewTime) = timeIt {
      MemoryOptimization.viewExample(largeData)
    }
    println(s"View操作时间: $viewTime ms")
    
    val (iteratorResult, iteratorTime) = timeIt {
      MemoryOptimization.iteratorExample(largeData)
    }
    println(s"Iterator操作时间: $iteratorTime ms")
    
    // 4. 并发处理性能对比
    println("\n--- 并发处理性能对比 ---")
    val testData = (1 to 100).toList
    
    // 串行处理
    val (seqResult, seqTime) = timeIt {
      ConcurrencyComparison.sequentialProcessing(testData)
    }
    println(s"串行处理时间: $seqTime ms")
    
    // 并行处理
    val parallelFuture = ConcurrencyComparison.parallelProcessing(testData)
    Thread.sleep(1000) // 等待完成
    // 注意：准确测量Future的时间需要更复杂的处理
    
    println("并发处理通常比串行处理更快，特别是在CPU密集型任务中")
    
    // 5. ExecutionContext优化示例
    println("\n--- ExecutionContext优化示例 ---")
    println(s"可用处理器核心数: ${Runtime.getRuntime.availableProcessors()}")
    println("已创建优化的ExecutionContext用于不同场景")
    
    // 6. 阻塞操作优化
    println("\n--- 阻塞操作优化 ---")
    val blockingStart = System.currentTimeMillis()
    val blockingFutures = (1 to 10).map { i =>
      FutureOptimization.optimizedBlockingOperation(i)
    }
    Thread.sleep(2000) // 等待完成
    val blockingEnd = System.currentTimeMillis()
    println(s"优化的阻塞操作完成时间: ${blockingEnd - blockingStart} ms")
    
    println("\n所有性能优化示例完成")
    println("\n性能优化要点总结:")
    println("1. 使用blocking包装阻塞操作")
    println("2. 选择合适的ExecutionContext")
    println("3. 使用并发集合如ConcurrentHashMap")
    println("4. 利用视图和迭代器避免中间集合")
    println("5. 合理使用并行处理和批量操作")
    println("6. 避免Future链中的内存泄漏")
  }
}