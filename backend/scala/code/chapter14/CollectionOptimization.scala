// 集合优化示例

import scala.collection.mutable
import scala.concurrent._
import scala.concurrent.duration._

object CollectionOptimization {
  
  // 1. 集合类型选择
  def demonstrateCollectionTypes(): Unit = {
    println("=== Collection Type Performance ===")
    
    // List - 适合头部操作
    val list = (1 to 100000).toList
    
    // Vector - 适合随机访问
    val vector = (1 to 100000).toVector
    
    // ArrayBuffer - 可变数组
    val arrayBuffer = mutable.ArrayBuffer[Int]()
    arrayBuffer ++= (1 to 100000)
    
    // HashSet - 快速查找
    val hashSet = mutable.HashSet((1 to 100000): _*)
    
    // 测试头部操作
    val (listPrependTime, _) = measureTime {
      var newList = list
      for (i <- 1 to 1000) {
        newList = 0 :: newList
      }
      newList
    }
    
    val (vectorPrependTime, _) = measureTime {
      var newVector = vector
      for (i <- 1 to 1000) {
        newVector = 0 +: newVector
      }
      newVector
    }
    
    // 测试随机访问
    val (listAccessTime, _) = measureTime {
      for (_ <- 1 to 10000) {
        list(scala.util.Random.nextInt(100000))
      }
    }
    
    val (vectorAccessTime, _) = measureTime {
      for (_ <- 1 to 10000) {
        vector(scala.util.Random.nextInt(100000))
      }
    }
    
    // 测试查找
    val (listFindTime, _) = measureTime {
      for (_ <- 1 to 1000) {
        list.contains(50000)
      }
    }
    
    val (setFindTime, _) = measureTime {
      for (_ <- 1 to 1000) {
        hashSet.contains(50000)
      }
    }
    
    println(s"List prepend: ${listPrependTime / 1000000} ms")
    println(s"Vector prepend: ${vectorPrependTime / 1000000} ms")
    println(s"List random access: ${listAccessTime / 1000000} ms")
    println(s"Vector random access: ${vectorAccessTime / 1000000} ms")
    println(s"List contains: ${listFindTime / 1000000} ms")
    println(s"Set contains: ${setFindTime / 1000000} ms")
  }
  
  // 2. 视图与惰性计算
  def demonstrateViews(): Unit = {
    println("\n=== Views and Lazy Computation ===")
    
    val data = (1 to 100000).toVector
    
    // 没有视图 - 创建多个中间集合
    val (withoutViewTime, withoutViewResult) = measureTime {
      data.filter(_ % 2 == 0)
          .map(_ * 3)
          .filter(_ < 1000)
          .take(10)
    }
    
    // 使用视图 - 避免中间集合
    val (withViewTime, withViewResult) = measureTime {
      data.view
        .filter(_ % 2 == 0)
        .map(_ * 3)
        .filter(_ < 1000)
        .take(10)
        .toList
    }
    
    println(s"Without view: ${withoutViewTime / 1000000} ms, result size: ${withoutViewResult.size}")
    println(s"With view: ${withViewTime / 1000000} ms, result size: ${withViewResult.size}")
    
    // Stream - 惰性序列
    def infiniteStream(): Stream[Int] = {
      def loop(i: Int): Stream[Int] = i #:: loop(i + 1)
      loop(1)
    }
    
    val stream = infiniteStream()
    val streamResult = stream.filter(_ % 2 == 0).take(10).toList
    println(s"Stream result: $streamResult")
  }
  
  // 3. 并行集合
  def demonstrateParallelCollections(): Unit = {
    println("\n=== Parallel Collections ===")
    
    val data = (1 to 10000000).toVector
    
    // 顺序处理
    val (sequentialTime, sequentialResult) = measureTime {
      data.filter(_ % 2 == 0)
          .map(_ * 2)
          .filter(_ < 1000)
    }
    
    // 并行处理
    val (parallelTime, parallelResult) = measureTime {
      data.par.filter(_ % 2 == 0)
          .map(_ * 2)
          .filter(_ < 1000)
          .seq  // 转回顺序集合
    }
    
    println(s"Sequential: ${sequentialTime / 1000000} ms, result size: ${sequentialResult.size}")
    println(s"Parallel: ${parallelTime / 1000000} ms, result size: ${parallelResult.size}")
    println(s"Speedup: ${sequentialTime.toDouble / parallelTime}x")
  }
  
  // 4. 集合构建器
  def demonstrateBuilders(): Unit = {
    println("\n=== Collection Builders ===")
    
    // 使用++=构建
    val (withPlusEqualsTime, _) = measureTime {
      var list = List.empty[Int]
      for (i <- 1 to 100000) {
        list = list :+ i  // 低效的尾部添加
      }
      list
    }
    
    // 使用构建器
    val (withBuilderTime, _) = measureTime {
      val builder = List.newBuilder[Int]
      for (i <- 1 to 100000) {
        builder += i
      }
      builder.result()
    }
    
    // 使用ArrayBuffer然后转换
    val (withArrayBufferTime, _) = measureTime {
      val buffer = mutable.ArrayBuffer[Int]()
      for (i <- 1 to 100000) {
        buffer += i
      }
      buffer.toList
    }
    
    println(s"With +=: ${withPlusEqualsTime / 1000000} ms")
    println(s"With builder: ${withBuilderTime / 1000000} ms")
    println(s"With ArrayBuffer: ${withArrayBufferTime / 1000000} ms")
  }
  
  // 5. 集合大小优化
  def demonstrateSizeOptimization(): Unit = {
    println("\n=== Collection Size Optimization ===")
    
    val targetSize = 1000000
    
    // 动态扩容
    val (dynamicTime, _) = measureTime {
      val buffer = mutable.ArrayBuffer[Int]()
      for (i <- 1 to targetSize) {
        buffer += i
      }
      buffer.size
    }
    
    // 预分配大小
    val (preallocatedTime, _) = measureTime {
      val buffer = mutable.ArrayBuffer[Int](targetSize)
      for (i <- 1 to targetSize) {
        buffer += i
      }
      buffer.size
    }
    
    // 初始大小 + 增长因子
    val (initialPlusGrowthTime, _) = measureTime {
      val buffer = mutable.ArrayBuffer[Int](100000)  // 初始大小
      for (i <- 1 to targetSize) {
        buffer += i
      }
      buffer.size
    }
    
    println(s"Dynamic allocation: ${dynamicTime / 1000000} ms")
    println(s"Preallocated: ${preallocatedTime / 1000000} ms")
    println(s"Initial + growth: ${initialPlusGrowthTime / 1000000} ms")
    println(s"Preallocation speedup: ${dynamicTime.toDouble / preallocatedTime}x")
  }
  
  // 6. 内存高效的数据结构
  def demonstrateMemoryEfficiency(): Unit = {
    println("\n=== Memory Efficient Structures ===")
    
    // 使用原始类型
    val (boxedMemory, _) = measureMemoryUsage {
      Array.fill(1000000)(Integer.valueOf(1))  // 装箱的整数
    }
    
    val (primitiveMemory, _) = measureMemoryUsage {
      Array.fill(1000000)(1)  // 原始整数
    }
    
    println(s"Boxed Integers: ${boxedMemory / 1024} KB")
    println(s"Primitive Integers: ${primitiveMemory / 1024} KB")
    println(s"Memory savings: ${(boxedMemory - primitiveMemory) / 1024} KB")
    
    // 使用更紧凑的集合类型
    val (listMemory, _) = measureMemoryUsage {
      (1 to 1000000).toList
    }
    
    val (vectorMemory, _) = measureMemoryUsage {
      (1 to 1000000).toVector
    }
    
    val (arrayMemory, _) = measureMemoryUsage {
      (1 to 1000000).toArray
    }
    
    println(s"List: ${listMemory / 1024} KB")
    println(s"Vector: ${vectorMemory / 1024} KB")
    println(s"Array: ${arrayMemory / 1024} KB")
  }
  
  // 7. 避免不必要的转换
  def demonstrateAvoidingConversions(): Unit = {
    println("\n=== Avoiding Unnecessary Conversions ===")
    
    val seq: Seq[Int] = (1 to 100000).toVector
    
    // 不必要的转换
    val (withConversionsTime, _) = measureTime {
      val list = seq.toList
      val vector = list.toVector
      val set = vector.toSet
      val result = set.map(_ * 2).toList
      result.size
    }
    
    // 最小化转换
    val (withoutConversionsTime, _) = measureTime {
      val result = seq.map(_ * 2)
      result.size
    }
    
    println(s"With unnecessary conversions: ${withConversionsTime / 1000000} ms")
    println(s"Without unnecessary conversions: ${withoutConversionsTime / 1000000} ms")
    println(s"Performance improvement: ${withConversionsTime.toDouble / withoutConversionsTime}x")
  }
  
  // 8. 自定义集合操作
  def demonstrateCustomOperations(): Unit = {
    println("\n=== Custom Collection Operations ===")
    
    val data = (1 to 100000).toVector
    
    // 使用标准库函数
    val (standardTime, _) = measureTime {
      data.filter(_ % 2 == 0).map(_ * 2).filter(_ < 10000)
    }
    
    // 自定义组合操作
    def filterMapFilter[A](source: Vector[A])(
      p1: A => Boolean,
      f: A => A,
      p2: A => Boolean
    ): Vector[A] = {
      val builder = Vector.newBuilder[A]
      for (x <- source) {
        if (p1(x)) {
          val y = f(x)
          if (p2(y)) {
            builder += y
          }
        }
      }
      builder.result()
    }
    
    val (customTime, _) = measureTime {
      filterMapFilter(data)(_ % 2 == 0, _ * 2, _ < 10000)
    }
    
    println(s"Standard library: ${standardTime / 1000000} ms")
    println(s"Custom operation: ${customTime / 1000000} ms")
    
    // 使用fold进行更复杂的操作
    def customFold[A, B](
      source: Vector[A]
    )(
      init: B
    )(
      filter: A => Boolean,
      transform: A => B,
      combine: (B, B) => B
    ): B = {
      source.foldLeft(init) { (acc, x) =>
        if (filter(x)) {
          combine(acc, transform(x))
        } else {
          acc
        }
      }
    }
    
    val (foldTime, _) = measureTime {
      customFold(data)(0)(_ % 2 == 0, _ * 2, _ + _)
    }
    
    println(s"Custom fold: ${foldTime / 1000000} ms")
  }
  
  // 性能测量辅助函数
  def measureTime[T](block: => T): (Long, T) = {
    val start = System.nanoTime()
    val result = block
    val end = System.nanoTime()
    (end - start, result)
  }
  
  def measureMemoryUsage[T](block: => T): (T, Long) = {
    val runtime = Runtime.getRuntime
    System.gc()
    Thread.sleep(100)
    val before = runtime.totalMemory() - runtime.freeMemory()
    
    val result = block
    
    System.gc()
    Thread.sleep(100)
    val after = runtime.totalMemory() - runtime.freeMemory()
    
    (result, after - before)
  }
  
  def runAll(): Unit = {
    demonstrateCollectionTypes()
    demonstrateViews()
    demonstrateParallelCollections()
    demonstrateBuilders()
    demonstrateSizeOptimization()
    demonstrateMemoryEfficiency()
    demonstrateAvoidingConversions()
    demonstrateCustomOperations()
  }
}