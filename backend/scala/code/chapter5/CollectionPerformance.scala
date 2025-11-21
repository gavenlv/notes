import scala.collection.immutable.{List, Vector}
import scala.collection.mutable.{ArrayBuffer, ListBuffer}
import scala.util.Random

object CollectionPerformance {
  def main(args: Array[String]): Unit = {
    // 性能比较
    println("=== 性能比较 ===")
    
    val dataSize = 100000
    val random = new Random(42)
    val data = List.fill(dataSize)(random.nextInt(1000))
    
    // 测试前置操作性能
    def prependTest[T, Coll <: Seq[T]](factory: Int => T, coll: Coll): Long = {
      val start = System.nanoTime()
      val result = factory(0) +: coll
      val end = System.nanoTime()
      end - start
    }
    
    // 测试追加操作性能
    def appendTest[T, Coll <: Seq[T]](factory: Int => T, coll: Coll): Long = {
      val start = System.nanoTime()
      val result = coll :+ factory(dataSize)
      val end = System.nanoTime()
      end - start
    }
    
    // 测试随机访问性能
    def randomAccessTest[T, Coll <: Seq[T]](coll: Coll): Long = {
      val start = System.nanoTime()
      for (i <- 0 until 1000) {
        coll(random.nextInt(coll.length))
      }
      val end = System.nanoTime()
      end - start
    }
    
    // 测试前置操作性能
    val listPrependTime = prependTest(identity, data)
    val vectorPrependTime = prependTest(identity, data.toVector)
    val arrayBufferPrependTime = prependTest(identity, ArrayBuffer(data: _*))
    val listBufferPrependTime = prependTest(identity, ListBuffer(data: _*))
    
    println("前置操作性能 (ns):")
    println(s"List: $listPrependTime")
    println(s"Vector: $vectorPrependTime")
    println(s"ArrayBuffer: $arrayBufferPrependTime")
    println(s"ListBuffer: $listBufferPrependTime")
    
    // 测试追加操作性能
    val listAppendTime = appendTest(identity, data)
    val vectorAppendTime = appendTest(identity, data.toVector)
    val arrayBufferAppendTime = appendTest(identity, ArrayBuffer(data: _*))
    val listBufferAppendTime = appendTest(identity, ListBuffer(data: _*))
    
    println("\n追加操作性能 (ns):")
    println(s"List: $listAppendTime")
    println(s"Vector: $vectorAppendTime")
    println(s"ArrayBuffer: $arrayBufferAppendTime")
    println(s"ListBuffer: $listBufferAppendTime")
    
    // 测试随机访问性能
    val listRandomAccessTime = randomAccessTest(data)
    val vectorRandomAccessTime = randomAccessTest(data.toVector)
    val arrayBufferRandomAccessTime = randomAccessTest(ArrayBuffer(data: _*))
    val listBufferRandomAccessTime = randomAccessTest(ListBuffer(data: _*))
    
    println("\n随机访问性能 (ns):")
    println(s"List: $listRandomAccessTime")
    println(s"Vector: $vectorRandomAccessTime")
    println(s"ArrayBuffer: $arrayBufferRandomAccessTime")
    println(s"ListBuffer: $listBufferRandomAccessTime")
    
    // 视图与集合比较
    println("\n=== 视图与集合比较 ===")
    
    val largeData = (1 to 100000).toList
    
    // 传统方式：创建多个中间集合
    val start1 = System.nanoTime()
    val result1 = largeData
      .map(_ * 2)
      .filter(_ % 3 == 0)
      .map(_ * 4)
      .take(100)
    val end1 = System.nanoTime()
    
    // 使用视图：避免创建中间集合
    val start2 = System.nanoTime()
    val result2 = largeData
      .view
      .map(_ * 2)
      .filter(_ % 3 == 0)
      .map(_ * 4)
      .take(100)
      .toList
    val end2 = System.nanoTime()
    
    println(s"传统方式时间: ${(end1 - start1) / 1000000} ms")
    println(s"视图方式时间: ${(end2 - start2) / 1000000} ms")
    println(s"结果相同: ${result1 == result2}")
    
    // 并行集合性能比较
    println("\n=== 并行集合性能比较 ===")
    
    val largeList = (1 to 1000000).toList
    val parallelList = largeList.par
    
    // 串行操作
    val start3 = System.nanoTime()
    val serialSum = largeList.map(_ * 2).sum
    val end3 = System.nanoTime()
    
    // 并行操作
    val start4 = System.nanoTime()
    val parallelSum = parallelList.map(_ * 2).sum
    val end4 = System.nanoTime()
    
    println(s"串行操作时间: ${(end3 - start3) / 1000000} ms")
    println(s"并行操作时间: ${(end4 - start4) / 1000000} ms")
    println(s"结果相同: ${serialSum == parallelSum}")
    
    // 不同操作类型的性能比较
    println("\n=== 不同操作类型的性能比较 ===")
    
    // 操作1：多次转换操作
    def multiTransform(list: List[Int]): List[Int] = {
      list
        .map(_ * 2)
        .filter(_ % 3 == 0)
        .map(_ * 5)
        .filter(_ % 10 == 0)
        .map(_ / 10)
    }
    
    // 操作2：单一转换操作
    def singleTransform(list: List[Int]): List[Int] = {
      list.collect {
        case x if (x * 2) % 3 == 0 => (x * 2 / 3) * 5 / 10
      }
    }
    
    val start5 = System.nanoTime()
    val result3 = multiTransform(largeList)
    val end5 = System.nanoTime()
    
    val start6 = System.nanoTime()
    val result4 = singleTransform(largeList)
    val end6 = System.nanoTime()
    
    println(s"多次转换操作时间: ${(end5 - start5) / 1000000} ms")
    println(s"单一转换操作时间: ${(end6 - start6) / 1000000} ms")
    
    // 集合类型对性能的影响
    println("\n=== 集合类型对性能的影响 ===")
    
    // 基于不同集合类型的相同操作
    val smallList = List(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    val smallVector = Vector(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    val smallArray = Array(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    
    // 随机访问测试
    def randomAccessSeq(seq: Seq[Int]): Long = {
      val start = System.nanoTime()
      for (i <- 0 until 10000) {
        val idx = random.nextInt(seq.length)
        seq(idx)
      }
      System.nanoTime() - start
    }
    
    def randomAccessArray(arr: Array[Int]): Long = {
      val start = System.nanoTime()
      for (i <- 0 until 10000) {
        val idx = random.nextInt(arr.length)
        arr(idx)
      }
      System.nanoTime() - start
    }
    
    val listAccessTime = randomAccessSeq(smallList)
    val vectorAccessTime = randomAccessSeq(smallVector)
    val arrayAccessTime = randomAccessArray(smallArray)
    
    println(s"List随机访问时间: $listAccessTime ns")
    println(s"Vector随机访问时间: $vectorAccessTime ns")
    println(s"Array随机访问时间: $arrayAccessTime ns")
  }
}