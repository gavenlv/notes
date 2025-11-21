// 性能分析工具与示例

import java.lang.management.ManagementFactory
import com.sun.management.OperatingSystemMXBean
import scala.concurrent._
import scala.concurrent.duration._

object PerformanceAnalysis {
  
  // JVM性能监控
  def printJVMStats(): Unit = {
    val runtime = Runtime.getRuntime
    val osBean = ManagementFactory.getOperatingSystemMXBean.asInstanceOf[OperatingSystemMXBean]
    val memoryMXBean = ManagementFactory.getMemoryMXBean
    
    println("=== JVM Stats ===")
    println(s"Available processors: ${runtime.availableProcessors()}")
    println(s"Max memory: ${runtime.maxMemory() / (1024 * 1024)} MB")
    println(s"Total memory: ${runtime.totalMemory() / (1024 * 1024)} MB")
    println(s"Free memory: ${runtime.freeMemory() / (1024 * 1024)} MB")
    println(s"System load average: ${osBean.getSystemLoadAverage}")
    println(s"Process CPU load: ${osBean.getProcessCpuLoad * 100}%")
    println(s"System CPU load: ${osBean.getSystemCpuLoad * 100}%")
    
    val heapMemory = memoryMXBean.getHeapMemoryUsage
    println(s"Heap used: ${heapMemory.getUsed / (1024 * 1024)} MB")
    println(s"Heap max: ${heapMemory.getMax / (1024 * 1024)} MB")
    println(s"Heap committed: ${heapMemory.getCommitted / (1024 * 1024)} MB")
  }
  
  // 内存使用分析
  def measureMemoryUsage[T](block: => T): (T, Long) = {
    val runtime = Runtime.getRuntime
    System.gc()
    Thread.sleep(100)  // 给GC一些时间
    val before = runtime.totalMemory() - runtime.freeMemory()
    
    val result = block
    
    System.gc()
    Thread.sleep(100)
    val after = runtime.totalMemory() - runtime.freeMemory()
    
    (result, after - before)
  }
  
  // 性能测量
  def measureTime[T](iterations: Int = 1000)(block: => T): (Long, T) = {
    // 预热
    for (_ <- 1 to 100) {
      block
    }
    
    System.gc()
    
    val start = System.nanoTime()
    var result: T = null.asInstanceOf[T]
    
    for (_ <- 1 to iterations) {
      result = block
    }
    
    val end = System.nanoTime()
    val avgTime = (end - start) / iterations
    
    (avgTime, result)
  }
  
  // 集合性能比较
  def compareCollections(): Unit = {
    val size = 100000
    
    // 创建集合的性能
    val (listCreationTime, _) = measureTime(100) {
      (1 to size).toList
    }
    
    val (vectorCreationTime, _) = measureTime(100) {
      (1 to size).toVector
    }
    
    val (arrayCreationTime, _) = measureTime(100) {
      (1 to size).toArray
    }
    
    println("=== Collection Creation Performance ===")
    println(s"List creation: ${listCreationTime / 1000000} ms")
    println(s"Vector creation: ${vectorCreationTime / 1000000} ms")
    println(s"Array creation: ${arrayCreationTime / 1000000} ms")
    
    // 随机访问性能
    val list = (1 to size).toList
    val vector = (1 to size).toVector
    val array = (1 to size).toArray
    
    val (listAccessTime, _) = measureTime(10000) {
      list(scala.util.Random.nextInt(size))
    }
    
    val (vectorAccessTime, _) = measureTime(10000) {
      vector(scala.util.Random.nextInt(size))
    }
    
    val (arrayAccessTime, _) = measureTime(10000) {
      array(scala.util.Random.nextInt(size))
    }
    
    println("\n=== Random Access Performance ===")
    println(s"List access: ${listAccessTime / 1000} ns")
    println(s"Vector access: ${vectorAccessTime / 1000} ns")
    println(s"Array access: ${arrayAccessTime / 1000} ns")
    
    // 内存使用比较
    val (_, listMemory) = measureMemoryUsage {
      (1 to size).toList
    }
    
    val (_, vectorMemory) = measureMemoryUsage {
      (1 to size).toVector
    }
    
    val (_, arrayMemory) = measureMemoryUsage {
      (1 to size).toArray
    }
    
    println("\n=== Memory Usage ===")
    println(s"List memory: ${listMemory / 1024} KB")
    println(s"Vector memory: ${vectorMemory / 1024} KB")
    println(s"Array memory: ${arrayMemory / 1024} KB")
  }
  
  // 函数式操作性能比较
  def compareFunctionalOperations(): Unit = {
    val size = 100000
    val list = (1 to size).toList
    val vector = (1 to size).toVector
    
    // filter操作
    val (listFilterTime, _) = measureTime(10) {
      list.filter(_ % 2 == 0)
    }
    
    val (vectorFilterTime, _) = measureTime(10) {
      vector.filter(_ % 2 == 0)
    }
    
    // map操作
    val (listMapTime, _) = measureTime(10) {
      list.map(_ * 2)
    }
    
    val (vectorMapTime, _) = measureTime(10) {
      vector.map(_ * 2)
    }
    
    println("=== Functional Operations Performance ===")
    println(s"List filter: ${listFilterTime / 1000000} ms")
    println(s"Vector filter: ${vectorFilterTime / 1000000} ms")
    println(s"List map: ${listMapTime / 1000000} ms")
    println(s"Vector map: ${vectorMapTime / 1000000} ms")
  }
  
  // 并行性能比较
  def compareParallelPerformance(): Unit = {
    val size = 1000000
    val data = (1 to size).toVector
    
    // 顺序处理
    val (sequentialFilterTime, _) = measureTime(5) {
      data.filter(_ % 2 == 0)
    }
    
    val (sequentialMapTime, _) = measureTime(5) {
      data.map(_ * 2)
    }
    
    val (sequentialReduceTime, _) = measureTime(5) {
      data.reduce(_ + _)
    }
    
    // 并行处理
    val (parallelFilterTime, _) = measureTime(5) {
      data.par.filter(_ % 2 == 0)
    }
    
    val (parallelMapTime, _) = measureTime(5) {
      data.par.map(_ * 2)
    }
    
    val (parallelReduceTime, _) = measureTime(5) {
      data.par.reduce(_ + _)
    }
    
    println("=== Sequential vs Parallel Performance ===")
    println(s"Sequential filter: ${sequentialFilterTime / 1000000} ms")
    println(s"Parallel filter: ${parallelFilterTime / 1000000} ms")
    println(s"Filter speedup: ${sequentialFilterTime.toDouble / parallelFilterTime}x")
    
    println(s"Sequential map: ${sequentialMapTime / 1000000} ms")
    println(s"Parallel map: ${parallelMapTime / 1000000} ms")
    println(s"Map speedup: ${sequentialMapTime.toDouble / parallelMapTime}x")
    
    println(s"Sequential reduce: ${sequentialReduceTime / 1000000} ms")
    println(s"Parallel reduce: ${parallelReduceTime / 1000000} ms")
    println(s"Reduce speedup: ${sequentialReduceTime.toDouble / parallelReduceTime}x")
  }
  
  // 方法调用性能比较
  def compareMethodCall(): Unit = {
    val iterations = 10000000
    
    // 直接方法调用
    def directAdd(a: Int, b: Int): Int = a + b
    
    val (directTime, _) = measureTime(iterations) {
      directAdd(1, 2)
    }
    
    // 函数值调用
    val funcAdd = (a: Int, b: Int) => a + b
    
    val (funcTime, _) = measureTime(iterations) {
      funcAdd(1, 2)
    }
    
    // 部分应用函数
    val partialAdd = (a: Int) => a + 2
    
    val (partialTime, _) = measureTime(iterations) {
      partialAdd(1)
    }
    
    // 柯里化函数
    def curriedAdd(a: Int)(b: Int): Int = a + b
    val curriedAdd1 = curriedAdd(1)_
    
    val (curriedTime, _) = measureTime(iterations) {
      curriedAdd1(2)
    }
    
    println("=== Method Call Performance ===")
    println(s"Direct call: ${directTime / 1000} ns")
    println(s"Function call: ${funcTime / 1000} ns")
    println(s"Partial application: ${partialTime / 1000} ns")
    println(s"Curried call: ${curriedTime / 1000} ns")
  }
  
  // 字符串操作性能
  def compareStringOperations(): Unit = {
    val iterations = 10000
    val list = (1 to 1000).toList
    
    // 字符串连接
    val (stringConcatTime, _) = measureTime(iterations) {
      var result = ""
      for (i <- 1 to 100) {
        result += i.toString
      }
      result
    }
    
    val (StringBuilderTime, _) = measureTime(iterations) {
      val builder = new StringBuilder()
      for (i <- 1 to 100) {
        builder.append(i.toString)
      }
      builder.toString()
    }
    
    val (mkStringTime, _) = measureTime(iterations) {
      (1 to 100).map(_.toString).mkString
    }
    
    println("=== String Operations Performance ===")
    println(s"String concatenation: ${stringConcatTime / 1000000} ms")
    println(s"StringBuilder: ${StringBuilderTime / 1000000} ms")
    println(s"mkString: ${mkStringTime / 1000000} ms")
    
    // 字符串格式化
    val (formatTime, _) = measureTime(iterations) {
      String.format("Value: %d, Name: %s", 42.asInstanceOf[AnyRef], "Scala")
    }
    
    val (sInterpolationTime, _) = measureTime(iterations) {
      s"Value: ${42}, Name: ${"Scala"}"
    }
    
    val (fInterpolationTime, _) = measureTime(iterations) {
      f"Value: ${42}%d, Name: ${"Scala"}%s"
    }
    
    println("\n=== String Formatting Performance ===")
    println(s"String.format: ${formatTime / 1000} ns")
    println(s"s-interpolation: ${sInterpolationTime / 1000} ns")
    println(s"f-interpolation: ${fInterpolationTime / 1000} ns")
  }
  
  // Future vs 同步操作性能比较
  def compareAsyncPerformance(): Unit = {
    import scala.concurrent.ExecutionContext.Implicits.global
    
    val iterations = 1000
    
    // 同步操作
    val (syncTime, _) = measureTime(iterations) {
      var sum = 0
      for (i <- 1 to 100) {
        sum += i
      }
      sum
    }
    
    // 异步操作
    val (asyncTime, _) = measureTime(1) {
      val futures = (1 to iterations).map { _ =>
        Future {
          var sum = 0
          for (i <- 1 to 100) {
            sum += i
          }
          sum
        }
      }
      
      Await.ready(Future.sequence(futures), 10.seconds)
    }
    
    println("=== Sync vs Async Performance ===")
    println(s"Synchronous: ${syncTime / 1000000} ms")
    println(s"Asynchronous: ${asyncTime / 1000000} ms")
    println(s"Overhead: ${asyncTime.toDouble / syncTime}x")
  }
  
  def runAll(): Unit = {
    println("Performance Analysis Demo")
    println("=========================\n")
    
    printJVMStats()
    println()
    
    compareCollections()
    println()
    
    compareFunctionalOperations()
    println()
    
    compareParallelPerformance()
    println()
    
    compareMethodCall()
    println()
    
    compareStringOperations()
    println()
    
    compareAsyncPerformance()
  }
}