import scala.concurrent.{Future, ExecutionContext}
import scala.concurrent.duration._
import java.util.concurrent.{Executors, ForkJoinPool, ThreadPoolExecutor}
import scala.language.postfixOps

object ExecutionContextExamples {
  // 自定义ExecutionContext示例
  object CustomExecutionContexts {
    // 固定大小线程池
    val fixedThreadPool = ExecutionContext.fromExecutor(Executors.newFixedThreadPool(4))
    
    // 缓存线程池
    val cachedThreadPool = ExecutionContext.fromExecutor(Executors.newCachedThreadPool())
    
    // 单线程执行上下文
    val singleThreadExecutionContext = ExecutionContext.fromExecutor(Executors.newSingleThreadExecutor())
    
    // ForkJoinPool执行上下文
    val forkJoinExecutionContext = ExecutionContext.fromExecutor(new ForkJoinPool(8))
    
    // 自定义ThreadPoolExecutor
    val customThreadPool = {
      val executor = new ThreadPoolExecutor(
        2,  // 核心线程数
        10, // 最大线程数
        60L, // 空闲线程存活时间
        java.util.concurrent.TimeUnit.SECONDS,
        new java.util.concurrent.LinkedBlockingQueue[Runnable]()
      )
      ExecutionContext.fromExecutor(executor)
    }
  }
  
  // 阻塞操作示例
  def blockingOperation(id: Int): Int = {
    println(s"开始阻塞操作 $id 在线程: ${Thread.currentThread().getName}")
    Thread.sleep(2000) // 模拟阻塞操作
    println(s"完成阻塞操作 $id 在线程: ${Thread.currentThread().getName}")
    id * 2
  }
  
  // 非阻塞操作示例
  def nonBlockingOperation(id: Int): Int = {
    println(s"开始非阻塞操作 $id 在线程: ${Thread.currentThread().getName}")
    id * 3
  }
  
  def main(args: Array[String]): Unit = {
    println("=== ExecutionContext 使用示例 ===")
    
    import CustomExecutionContexts._
    
    // 1. 使用不同的ExecutionContext
    println("\n--- 使用固定线程池 ---")
    val futures1 = (1 to 3).map { i =>
      Future {
        blockingOperation(i)
      }(fixedThreadPool)
    }
    
    // 等待完成
    Thread.sleep(3000)
    
    // 2. 使用缓存线程池
    println("\n--- 使用缓存线程池 ---")
    val futures2 = (1 to 5).map { i =>
      Future {
        nonBlockingOperation(i)
      }(cachedThreadPool)
    }
    
    futures2.foreach(_.foreach(result => println(s"缓存线程池结果: $result")))
    
    // 3. 使用单线程执行上下文
    println("\n--- 使用单线程执行上下文 ---")
    val futures3 = (1 to 3).map { i =>
      Future {
        nonBlockingOperation(i)
      }(singleThreadExecutionContext)
    }
    
    futures3.foreach(_.foreach(result => println(s"单线程结果: $result")))
    
    // 4. 使用ForkJoinPool执行上下文
    println("\n--- 使用ForkJoinPool执行上下文 ---")
    val futures4 = (1 to 4).map { i =>
      Future {
        blockingOperation(i)
      }(forkJoinExecutionContext)
    }
    
    // 等待完成
    Thread.sleep(3000)
    
    // 5. 使用自定义ThreadPoolExecutor
    println("\n--- 使用自定义ThreadPoolExecutor ---")
    val futures5 = (1 to 6).map { i =>
      Future {
        nonBlockingOperation(i)
      }(customThreadPool)
    }
    
    futures5.foreach(_.foreach(result => println(s"自定义线程池结果: $result")))
    
    // 6. 阻塞操作的最佳实践
    println("\n--- 阻塞操作最佳实践 ---")
    // 对于阻塞操作，应该使用专门的阻塞线程池
    val blockingExecutor = ExecutionContext.fromExecutor(Executors.newCachedThreadPool())
    
    val blockingFutures = (1 to 3).map { i =>
      Future {
        blockingOperation(i)
      }(blockingExecutor)
    }
    
    // 等待完成
    Thread.sleep(3000)
    
    // 7. ExecutionContext的阻塞感知
    println("\n--- 使用scala.concurrent.blocking ---")
    import scala.concurrent.blocking
    
    val blockingAwareFutures = (1 to 2).map { i =>
      Future {
        blocking {
          blockingOperation(i)
        }
      }
    }
    
    // 等待完成
    Thread.sleep(3000)
    
    // 关闭自定义执行器
    // 注意：在实际应用中，应该在应用关闭时正确关闭执行器
    println("\n所有ExecutionContext示例完成")
  }
}