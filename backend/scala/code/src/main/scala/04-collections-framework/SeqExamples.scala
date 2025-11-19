/**
 * SeqExamples.scala
 * 
 * 演示Scala中序列（Seq）集合的使用方法
 * 包括List、Vector、Array、Range等常用序列类型
 */

// List示例 - 不可变链表
object ListDemo {
  def run(): Unit = {
    println("=== List 示例 ===")
    
    // 创建List
    val list1 = List(1, 2, 3, 4, 5)
    val list2 = 1 :: 2 :: 3 :: Nil  // 使用cons操作符
    val emptyList = List.empty[Int]
    
    println(s"list1: $list1")
    println(s"list2: $list2")
    println(s"emptyList: $emptyList")
    
    // 基本操作
    println(s"head: ${list1.head}")
    println(s"tail: ${list1.tail}")
    println(s"last: ${list1.last}")
    
    // 添加元素
    val newList = 0 :: list1  // 在头部添加
    println(s"在头部添加0: $newList")
    
    val appendedList = list1 :+ 6  // 在尾部添加
    println(s"在尾部添加6: $appendedList")
    
    // 连接列表
    val concatenated = list1 ++ List(6, 7, 8)
    println(s"连接两个列表: $concatenated")
    
    // 访问元素
    println(s"第3个元素: ${list1(2)}")  // 索引从0开始
    
    // 查找元素
    println(s"查找元素3的位置: ${list1.indexOf(3)}")
    println(s"是否存在元素5: ${list1.contains(5)}")
  }
}

// Vector示例 - 高效的不可变索引序列
object VectorDemo {
  def run(): Unit = {
    println("\n=== Vector 示例 ===")
    
    // 创建Vector
    val vector1 = Vector(1, 2, 3, 4, 5)
    val vector2 = Vector.empty[String]
    
    println(s"vector1: $vector1")
    println(s"vector2: $vector2")
    
    // Vector的操作与List类似，但随机访问更高效
    println(s"第2个元素: ${vector1(1)}")
    
    // 更新元素（返回新的Vector）
    val updatedVector = vector1.updated(2, 10)
    println(s"将索引2的元素更新为10: $updatedVector")
    
    // 添加元素
    val prepended = 0 +: vector1  // 在头部添加
    val appended = vector1 :+ 6   // 在尾部添加
    println(s"在头部添加0: $prepended")
    println(s"在尾部添加6: $appended")
  }
}

// Array示例 - 可变数组
object ArrayDemo {
  def run(): Unit = {
    println("\n=== Array 示例 ===")
    
    // 创建Array
    val array1 = Array(1, 2, 3, 4, 5)
    val array2 = new Array[String](3)  // 创建指定大小的空数组
    
    println(s"array1: ${array1.mkString(", ")}")
    
    // 修改元素（Array是可变的）
    array1(2) = 10
    println(s"修改索引2的元素为10: ${array1.mkString(", ")}")
    
    // 添加元素需要创建新数组
    val extendedArray = array1 :+ 6
    println(s"添加元素6: ${extendedArray.mkString(", ")}")
    
    // 数组转换
    val listFromArr = array1.toList
    val vectorFromArr = array1.toVector
    println(s"转换为List: $listFromArr")
    println(s"转换为Vector: $vectorFromArr")
  }
}

// ArrayBuffer示例 - 可变数组缓冲区
object ArrayBufferDemo {
  def run(): Unit = {
    println("\n=== ArrayBuffer 示例 ===")
    
    import scala.collection.mutable.ArrayBuffer
    
    // 创建ArrayBuffer
    val buffer = ArrayBuffer(1, 2, 3)
    
    println(s"初始buffer: ${buffer.mkString(", ")}")
    
    // 添加元素
    buffer += 4  // 添加单个元素
    buffer ++= List(5, 6, 7)  // 添加多个元素
    
    println(s"添加元素后: ${buffer.mkString(", ")}")
    
    // 插入元素
    buffer.insert(0, 0)  // 在索引0处插入元素0
    println(s"在头部插入0: ${buffer.mkString(", ")}")
    
    // 删除元素
    buffer.remove(0)  // 删除索引0处的元素
    println(s"删除头部元素: ${buffer.mkString(", ")}")
    
    // 修改元素
    buffer(2) = 10
    println(s"修改索引2的元素为10: ${buffer.mkString(", ")}")
    
    // 转换为不可变序列
    val immutableSeq = buffer.toSeq
    println(s"转换为不可变序列: $immutableSeq")
  }
}

// Range示例 - 范围序列
object RangeDemo {
  def run(): Unit = {
    println("\n=== Range 示例 ===")
    
    // 创建Range
    val range1 = 1 to 10
    val range2 = 1 until 10
    val range3 = 1 to 20 by 2  // 步长为2
    val range4 = 10 to 1 by -1  // 递减
    
    println(s"1 to 10: ${range1.mkString(", ")}")
    println(s"1 until 10: ${range2.mkString(", ")}")
    println(s"1 to 20 by 2: ${range3.mkString(", ")}")
    println(s"10 to 1 by -1: ${range4.mkString(", ")}")
    
    // Range转换
    val listFromRange = range1.toList
    val vectorFromRange = range1.toVector
    
    println(s"转换为List: ${listFromRange.mkString(", ")}")
    println(s"转换为Vector: ${vectorFromRange.mkString(", ")}")
    
    // Range操作
    println(s"Range长度: ${range1.length}")
    println(s"Range求和: ${range1.sum}")
    println(s"Range最大值: ${range1.max}")
  }
}

// 主程序入口
object SeqExamplesDemo extends App {
  ListDemo.run()
  VectorDemo.run()
  ArrayDemo.run()
  ArrayBufferDemo.run()
  RangeDemo.run()
}