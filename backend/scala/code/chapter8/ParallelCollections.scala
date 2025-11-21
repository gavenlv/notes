// 并行集合示例

import scala.collection.parallel.CollectionConverters._
import scala.util.Random

// 1. 基本并行操作
object BasicParallelOperations {
  def parallelMapFilter(): Unit = {
    val data = (1 to 1000000).toList
    val parallelData = data.par
    
    // 顺序操作时间
    val sequentialStart = System.nanoTime()
    val sequentialResult = data.map(_ * 2).filter(_ % 3 == 0).take(100)
    val sequentialTime = System.nanoTime() - sequentialStart
    
    // 并行操作时间
    val parallelStart = System.nanoTime()
    val parallelResult = parallelData.map(_ * 2).filter(_ % 3 == 0).take(100)
    val parallelTime = System.nanoTime() - parallelStart
    
    println(s"Sequential time: ${sequentialTime / 1000000} ms")
    println(s"Parallel time: ${parallelTime / 1000000} ms")
    println(s"Speedup: ${sequentialTime.toDouble / parallelTime}")
    
    // 验证结果一致性
    println(s"Results equal: ${sequentialResult == parallelResult}")
  }
  
  def parallelReduction(): Unit = {
    val data = (1 to 1000000).toList
    val parallelData = data.par
    
    // 不同归约操作的性能比较
    // sum
    val sumStart = System.nanoTime()
    val sum = parallelData.sum
    val sumTime = System.nanoTime() - sumStart
    println(s"Parallel sum time: ${sumTime / 1000000} ms, result: $sum")
    
    // reduce
    val reduceStart = System.nanoTime()
    val product = parallelData.reduce(_ * _)
    val reduceTime = System.nanoTime() - reduceStart
    println(s"Parallel product time: ${reduceTime / 1000000} ms, result: $product")
    
    // fold
    val foldStart = System.nanoTime()
    val foldResult = parallelData.fold(0)(_ + _)
    val foldTime = System.nanoTime() - foldStart
    println(s"Parallel fold time: ${foldTime / 1000000} ms, result: $foldResult")
    
    // aggregate (更复杂的并行操作)
    val aggregateStart = System.nanoTime()
    val maxProduct = parallelData.aggregate(Int.MinValue)(
      (max, elem) => math.max(max, elem),
      (max1, max2) => math.max(max1, max2)
    )
    val aggregateTime = System.nanoTime() - aggregateStart
    println(s"Parallel aggregate time: ${aggregateTime / 1000000} ms, max: $maxProduct")
  }
}

// 2. 并行集合陷阱
object ParallelPitfalls {
  def sideEffects(): Unit = {
    println("=== 副作用问题 ===")
    val list = (1 to 10).toList
    var sum = 0
    
    // 有问题：副作用操作的顺序不确定
    list.par.foreach(x => sum += x)
    println(s"Side effect sum (might be incorrect): $sum")
    
    // 正确方式：使用无副操作
    val correctSum = list.par.reduce(_ + _)
    println(s"Correct sum: $correctSum")
    
    // 另一个副作用的例子
    val results = scala.collection.mutable.ListBuffer[Int]()
    list.par.foreach(x => results += x * 2)
    println(s"Side effect results (order not guaranteed): $results")
    
    // 正确方式：使用不可变操作
    val correctResults = list.par.map(_ * 2).toList
    println(s"Correct results (sorted): ${correctResults.sorted}")
  }
  
  def nonAssociativeOperations(): Unit = {
    println("\n=== 非结合操作问题 ===")
    val data = (1 to 1000).toList
    val parallelData = data.par
    
    // 浮点数加法不是完全结合的
    val sequentialSum = data.map(0.1 + _).sum
    val parallelSum = parallelData.map(0.1 + _).sum
    
    println(s"Sequential sum: $sequentialSum")
    println(s"Parallel sum: $parallelSum")
    println(s"Results equal: ${math.abs(sequentialSum - parallelSum) < 0.000001}")
    
    // 非结合操作如字符串连接
    val strings = (1 to 100).map(_.toString).toList
    
    val sequentialConcat = strings.reduce(_ + _)
    val parallelConcat = strings.par.reduce(_ + _)
    
    println(s"Sequential concat length: ${sequentialConcat.length}")
    println(s"Parallel concat length: ${parallelConcat.length}")
    println(s"Results equal: ${sequentialConcat == parallelConcat}")
    
    // 对于非结合操作，使用更安全的组合方式
    val safeParallelConcat = strings.par.fold("")(_ + _)
    println(s"Safe parallel concat length: ${safeParallelConcat.length}")
    println(s"Safe and sequential equal: ${safeParallelConcat == sequentialConcat}")
  }
  
  def synchronizationIssues(): Unit = {
    println("\n=== 同步问题 ===")
    val list = (1 to 1000).toList
    val mutableSet = scala.collection.mutable.Set[Int]()
    
    // 问题：共享可变状态导致数据竞争
    list.par.foreach(mutableSet += _)
    println(s"Mutable set size (might be incorrect): ${mutableSet.size}")
    
    // 正确方式：使用不可变操作
    val immutableSet = list.par.toSet
    println(s"Immutable set size (correct): ${immutableSet.size}")
  }
}

// 3. 并行集合高级用法
object AdvancedParallelCollections {
  def customTaskSplitting(): Unit = {
    println("=== 自定义任务分割 ===")
    val data = (1 to 100000).toList
    
    // 默认并行集合
    val defaultParallel = data.par
    println(s"Default parallel tasks: ${defaultParallel.tasksupport.parallelism}")
    
    // 自定义并行度
    import scala.collection.parallel.ForkJoinTasks
    import scala.concurrent.forkjoin.ForkJoinPool
    
    val customThreadPool = new ForkJoinPool(8)
    val customTaskSupport = new scala.collection.parallel.ForkJoinTaskSupport(customThreadPool)
    
    val customParallel = data.par
    customParallel.tasksupport = customTaskSupport
    
    val customResult = customParallel.map(x => {
      Thread.sleep(1)  // 模拟计算
      x * x
    }).sum
    
    println(s"Custom parallelism result: $customResult")
    
    customThreadPool.shutdown()
  }
  
  def parallelAggregation(): Unit = {
    println("\n=== 并行聚合 ===")
    case class Sale(product: String, category: String, amount: Double)
    
    val sales = (1 to 100000).map { i =>
      val products = List("Laptop", "Phone", "Tablet", "Monitor", "Keyboard")
      val categories = List("Electronics", "Accessories", "Peripherals")
      
      Sale(
        products(Random.nextInt(products.length)),
        categories(Random.nextInt(categories.length)),
        Random.nextDouble() * 1000
      )
    }
    
    // 按类别计算总销售额
    val salesByCategory = sales.par.groupBy(_.category).map {
      case (category, categorySales) => 
        category -> categorySales.map(_.amount).sum
    }.seq.toMap
    
    salesByCategory.foreach { case (category, total) =>
      println(f"Category: $category, Total: $total%.2f")
    }
    
    // 计算每个产品的平均销售额
    val productStats = sales.par.groupBy(_.product).map {
      case (product, productSales) => 
        val total = productSales.map(_.amount).sum
        val count = productSales.length
        val avg = total / count
        product -> (total, count, avg)
    }.seq.toMap
    
    productStats.foreach { case (product, (total, count, avg)) =>
      println(f"Product: $product, Total: $total%.2f, Count: $count, Average: $avg%.2f")
    }
  }
  
  def parallelSorting(): Unit = {
    println("\n=== 并行排序 ===")
    val data = Random.shuffle((1 to 100000).toList)
    
    // 顺序排序
    val sequentialSortStart = System.nanoTime()
    val sequentialSorted = data.sorted
    val sequentialSortTime = System.nanoTime() - sequentialSortStart
    
    // 并行排序
    val parallelSortStart = System.nanoTime()
    val parallelSorted = data.par.sorted
    val parallelSortTime = System.nanoTime() - parallelSortStart
    
    println(s"Sequential sort time: ${sequentialSortTime / 1000000} ms")
    println(s"Parallel sort time: ${parallelSortTime / 1000000} ms")
    println(s"Speedup: ${sequentialSortTime.toDouble / parallelSortTime}")
    println(s"Results equal: ${sequentialSorted == parallelSorted}")
  }
  
  def parallelSearching(): Unit = {
    println("\n=== 并行搜索 ===")
    val data = (1 to 1000000).toList
    
    // 查找满足条件的元素
    val target = 987654
    
    // 顺序查找
    val sequentialFindStart = System.nanoTime()
    val sequentialFound = data.find(_ == target)
    val sequentialFindTime = System.nanoTime() - sequentialFindStart
    
    // 并行查找
    val parallelFindStart = System.nanoTime()
    val parallelFound = data.par.find(_ == target)
    val parallelFindTime = System.nanoTime() - parallelFindStart
    
    println(s"Sequential find time: ${sequentialFindTime / 1000000} ms, result: $sequentialFound")
    println(s"Parallel find time: ${parallelFindTime / 1000000} ms, result: $parallelFound")
    
    // 查找多个匹配项
    val predicate = (x: Int) => x % 12345 == 0
    
    val sequentialFilterStart = System.nanoTime()
    val sequentialMatches = data.filter(predicate)
    val sequentialFilterTime = System.nanoTime() - sequentialFilterStart
    
    val parallelFilterStart = System.nanoTime()
    val parallelMatches = data.par.filter(predicate)
    val parallelFilterTime = System.nanoTime() - parallelFilterStart
    
    println(s"Sequential filter time: ${sequentialFilterTime / 1000000} ms, matches: ${sequentialMatches.length}")
    println(s"Parallel filter time: ${parallelFilterTime / 1000000} ms, matches: ${parallelMatches.length}")
    println(s"Results equal: ${sequentialMatches.sorted == parallelMatches.toList.sorted}")
  }
}

// 4. 并行集合应用场景
object ParallelCollectionUseCases {
  def dataProcessing(): Unit = {
    println("=== 数据处理场景 ===")
    
    // 模拟传感器数据
    case class SensorReading(sensorId: Int, timestamp: Long, value: Double)
    
    val readings = (1 to 1000000).map { i =>
      SensorReading(
        i % 100,  // 100个不同的传感器
        System.currentTimeMillis() - i * 1000,  // 时间戳
        Random.nextDouble() * 100  // 随机读数
      )
    }
    
    // 计算每个传感器的统计数据
    val sensorStats = readings.par.groupBy(_.sensorId).map {
      case (sensorId, sensorReadings) =>
        val values = sensorReadings.map(_.value)
        val min = values.min
        val max = values.max
        val avg = values.sum / values.length
        val stdDev = math.sqrt(values.map(x => math.pow(x - avg, 2)).sum / values.length)
        
        (sensorId, (min, max, avg, stdDev))
    }.seq.toMap
    
    println(s"Processed ${sensorStats.size} sensors")
    sensorStats.take(5).foreach { case (id, (min, max, avg, stdDev)) =>
      println(f"Sensor $id: Min=$min%.2f, Max=$max%.2f, Avg=$avg%.2f, StdDev=$stdDev%.2f")
    }
  }
  
  def matrixOperations(): Unit = {
    println("\n=== 矩阵操作场景 ===")
    
    def createMatrix(rows: Int, cols: Int): Array[Array[Double]] = {
      Array.ofDim[Double](rows, cols).map { row =>
        Array.fill(cols)(Random.nextDouble())
      }
    }
    
    val matrix = createMatrix(1000, 1000)
    
    // 矩阵转置
    val transposeStart = System.nanoTime()
    val transposed = matrix.par.map(_.zipWithIndex).flatten
      .groupBy(_._2).map { case (col, values) => 
        values.sortBy(_._2).map(_._1).toArray
      }.toArray
    val transposeTime = System.nanoTime() - transposeStart
    
    println(s"Matrix transpose time: ${transposeTime / 1000000} ms")
    println(s"Original dimensions: ${matrix.length}x${matrix(0).length}")
    println(s"Transposed dimensions: ${transposed.length}x${transposed(0).length}")
    
    // 计算行和
    val rowSumStart = System.nanoTime()
    val rowSums = matrix.par.map(_.sum)
    val rowSumTime = System.nanoTime() - rowSumStart
    
    println(s"Row sum time: ${rowSumTime / 1000000} ms")
    println(s"First 5 row sums: ${rowSums.take(5)}")
  }
  
  def textProcessing(): Unit = {
    println("\n=== 文本处理场景 ===")
    
    // 模拟文本数据
    val words = List.fill(100000)(Random.alphanumeric.take(Random.nextInt(10) + 3).mkString)
    
    // 单词长度分布
    val lengthDist = words.par.groupBy(_.length).map {
      case (length, wordList) => length -> wordList.length
    }.seq.toMap
    
    println("Word length distribution:")
    lengthDist.toSeq.sorted.take(10).foreach { case (length, count) =>
      println(s"Length $length: $count words")
    }
    
    // 找出所有回文
    val palindromes = words.par.filter(word => word == word.reverse).toList
    println(s"Found ${palindromes.length} palindromes")
    palindromes.take(5).foreach(println)
    
    // 单词长度平方和
    val lengthSquaredSum = words.par.map(word => math.pow(word.length, 2)).sum
    println(s"Sum of squared word lengths: $lengthSquaredSum")
  }
}

// 5. 主程序
object ParallelCollectionsDemo extends App {
  // 1. 基本并行操作
  println("=== 基本并行操作 ===")
  BasicParallelOperations.parallelMapFilter()
  BasicParallelOperations.parallelReduction()
  
  Thread.sleep(2000)
  
  // 2. 并行集合陷阱
  println("\n=== 并行集合陷阱 ===")
  ParallelPitfalls.sideEffects()
  ParallelPitfalls.nonAssociativeOperations()
  ParallelPitfalls.synchronizationIssues()
  
  Thread.sleep(2000)
  
  // 3. 并行集合高级用法
  println("\n=== 并行集合高级用法 ===")
  AdvancedParallelCollections.customTaskSplitting()
  AdvancedParallelCollections.parallelAggregation()
  AdvancedParallelCollections.parallelSorting()
  AdvancedParallelCollections.parallelSearching()
  
  Thread.sleep(2000)
  
  // 4. 应用场景
  println("\n=== 应用场景 ===")
  ParallelCollectionUseCases.dataProcessing()
  ParallelCollectionUseCases.matrixOperations()
  ParallelCollectionUseCases.textProcessing()
  
  println("\nParallel collections demo completed!")
}