/**
 * CollectionOperations.scala
 * 
 * 演示Scala集合的各种操作方法
 * 包括转换操作、聚合操作、分组操作等
 */

// 转换操作示例
object TransformationOperationsDemo {
  def run(): Unit = {
    println("=== 转换操作示例 ===")
    
    val numbers = List(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    val words = List("apple", "banana", "cherry", "date", "elderberry")
    
    // map操作
    val doubled = numbers.map(_ * 2)
    println(s"原数字: $numbers")
    println(s"每个数字乘以2: $doubled")
    
    // 转换字符串为大写
    val upperWords = words.map(_.toUpperCase)
    println(s"原单词: $words")
    println(s"转换为大写: $upperWords")
    
    // flatMap操作
    val flatMapped = words.flatMap(_.toList)
    println(s"单词展开为字符: $flatMapped")
    
    // filter操作
    val evens = numbers.filter(_ % 2 == 0)
    println(s"筛选偶数: $evens")
    
    // filterNot操作
    val odds = numbers.filterNot(_ % 2 == 0)
    println(s"筛选奇数: $odds")
    
    // collect操作
    val collected = numbers.collect {
      case x if x % 2 == 0 => x * 10
    }
    println(s"收集偶数并乘以10: $collected")
    
    // take和drop操作
    println(s"取前5个元素: ${numbers.take(5)}")
    println(s"跳过前5个元素: ${numbers.drop(5)}")
    println(s"取最后3个元素: ${numbers.takeRight(3)}")
    println(s"跳过最后3个元素: ${numbers.dropRight(3)}")
    
    // slice操作
    println(s"切片(2, 7): ${numbers.slice(2, 7)}")
  }
}

// 聚合操作示例
object AggregationOperationsDemo {
  def run(): Unit = {
    println("\n=== 聚合操作示例 ===")
    
    val numbers = List(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    val words = List("a", "bb", "ccc", "dddd", "eeeee")
    
    // fold操作
    val sum = numbers.fold(0)(_ + _)
    println(s"数字求和(fold): $sum")
    
    val product = numbers.fold(1)(_ * _)
    println(s"数字乘积(fold): $product")
    
    // foldLeft操作
    val foldLeftResult = numbers.foldLeft("")((acc, n) => acc + n.toString)
    println(s"foldLeft连接数字: $foldLeftResult")
    
    // foldRight操作
    val foldRightResult = numbers.foldRight("")((n, acc) => n.toString + acc)
    println(s"foldRight连接数字: $foldRightResult")
    
    // reduce操作
    val reducedSum = numbers.reduce(_ + _)
    println(s"数字求和(reduce): $reducedSum")
    
    val longestWord = words.reduce((w1, w2) => if (w1.length > w2.length) w1 else w2)
    println(s"最长的单词: $longestWord")
    
    // scan操作
    val scanResult = numbers.scan(0)(_ + _)
    println(s"累积求和(scan): $scanResult")
    
    // 其他聚合操作
    println(s"最大值: ${numbers.max}")
    println(s"最小值: ${numbers.min}")
    println(s"平均值: ${numbers.sum.toDouble / numbers.length}")
    println(s"是否存在偶数: ${numbers.exists(_ % 2 == 0)}")
    println(s"是否都是正数: ${numbers.forall(_ > 0)}")
  }
}

// 分组和分区操作示例
object GroupingOperationsDemo {
  def run(): Unit = {
    println("\n=== 分组和分区操作示例 ===")
    
    case class Person(name: String, age: Int, city: String)
    
    val people = List(
      Person("Alice", 25, "Beijing"),
      Person("Bob", 30, "Shanghai"),
      Person("Charlie", 35, "Beijing"),
      Person("David", 28, "Guangzhou"),
      Person("Eve", 32, "Shanghai")
    )
    
    // groupBy操作
    val groupedByCity = people.groupBy(_.city)
    println("按城市分组:")
    groupedByCity.foreach { case (city, persons) =>
      println(s"  $city: ${persons.map(_.name).mkString(", ")}")
    }
    
    // partition操作
    val (adults, minors) = people.partition(_.age >= 30)
    println(s"\n成年人: ${adults.map(_.name).mkString(", ")}")
    println(s"未成年人: ${minors.map(_.name).mkString(", ")}")
    
    // groupMap操作
    val cityAges = people.groupMap(_.city)(_.age)
    println(s"\n各城市的年龄分布: $cityAges")
    
    // groupMapReduce操作
    val cityAverageAge = people.groupMapReduce(_.city)(_.age)((age1, age2) => age1 + age2)
    println(s"各城市的年龄总和: $cityAverageAge")
  }
}

// 拉链和其他操作示例
object ZipAndOtherOperationsDemo {
  def run(): Unit = {
    println("\n=== 拉链和其他操作示例 ===")
    
    val numbers = List(1, 2, 3, 4, 5)
    val letters = List("a", "b", "c", "d", "e")
    val moreNumbers = List(10, 20, 30)
    
    // zip操作
    val zipped = numbers.zip(letters)
    println(s"数字和字母拉链: $zipped")
    
    // zipWithIndex操作
    val indexed = letters.zipWithIndex
    println(s"带索引的字母: $indexed")
    
    // zipAll操作
    val zippedAll = numbers.zipAll(moreNumbers, 0, 0)
    println(s"完全拉链: $zippedAll")
    
    // unzip操作
    val (unzippedNumbers, unzippedLetters) = zipped.unzip
    println(s"解压缩数字: $unzippedNumbers")
    println(s"解压缩字母: $unzippedLetters")
    
    // sliding操作
    val slidingWindows = numbers.sliding(3)
    println(s"滑动窗口(size=3): ${slidingWindows.toList}")
    
    // grouped操作
    val grouped = numbers.grouped(3)
    println(s"分组(size=3): ${grouped.toList}")
    
    // distinct操作
    val duplicates = List(1, 2, 2, 3, 3, 3, 4, 4, 4, 4)
    println(s"去重前: $duplicates")
    println(s"去重后: ${duplicates.distinct}")
  }
}

// 组合操作示例
object CombinedOperationsDemo {
  def run(): Unit = {
    println("\n=== 组合操作示例 ===")
    
    case class Order(id: Int, customer: String, amount: Double, status: String)
    
    val orders = List(
      Order(1, "Alice", 100.0, "completed"),
      Order(2, "Bob", 150.0, "pending"),
      Order(3, "Charlie", 200.0, "completed"),
      Order(4, "David", 75.0, "cancelled"),
      Order(5, "Eve", 300.0, "completed"),
      Order(6, "Frank", 120.0, "pending")
    )
    
    // 复杂的组合操作
    val result = orders
      .filter(_.status == "completed")           // 筛选已完成订单
      .map(o => (o.customer, o.amount))          // 提取客户和金额
      .groupBy(_._1)                             // 按客户分组
      .mapValues(_.map(_._2).sum)                // 计算每个客户的总金额
      .toList                                    // 转换为List
      .sortBy(-_._2)                             // 按金额降序排列
    
    println("已完成订单的客户总金额(降序):")
    result.foreach { case (customer, total) =>
      println(s"  $customer: $$${total}")
    }
  }
}

// 主程序入口
object CollectionOperationsDemo extends App {
  TransformationOperationsDemo.run()
  AggregationOperationsDemo.run()
  GroupingOperationsDemo.run()
  ZipAndOtherOperationsDemo.run()
  CombinedOperationsDemo.run()
}