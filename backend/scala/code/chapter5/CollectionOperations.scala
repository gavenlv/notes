object CollectionOperations {
  def main(args: Array[String]): Unit = {
    val numbers = List(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    val words = List("scala", "java", "python", "javascript", "ruby")
    
    // 转换操作
    println("=== 转换操作 ===")
    
    // map
    val doubled = numbers.map(_ * 2)
    println(s"doubled: $doubled")
    
    val lengths = words.map(_.length)
    println(s"lengths: $lengths")
    
    // flatMap
    val chars = words.flatMap(_.toList)
    println(s"chars: $chars")
    
    val pairs = numbers.flatMap(i => List(i, i * 10))
    println(s"pairs: $pairs")
    
    // collect
    val evenSquares = numbers.collect {
      case x if x % 2 == 0 => x * x
    }
    println(s"evenSquares: $evenSquares")
    
    // filter
    val evenNumbers = numbers.filter(_ % 2 == 0)
    println(s"evenNumbers: $evenNumbers")
    
    val longWords = words.filter(_.length > 4)
    println(s"longWords: $longWords")
    
    // partition
    val (evens, odds) = numbers.partition(_ % 2 == 0)
    println(s"evens: $evens, odds: $odds")
    
    // groupBy
    val groupedByLength = words.groupBy(_.length)
    println(s"groupedByLength: $groupedByLength")
    
    // 分割和连接
    val taken = numbers.take(5)
    val dropped = numbers.drop(5)
    val sliced = numbers.slice(2, 8)
    
    println(s"taken: $taken")
    println(s"dropped: $dropped")
    println(s"sliced: $sliced")
    
    // 排序
    val sorted = numbers.sorted
    val reversed = numbers.reverse
    val sortByLength = words.sortBy(_.length)
    
    println(s"sorted: $sorted")
    println(s"reversed: $reversed")
    println(s"sortByLength: $sortByLength")
    
    // 聚合操作
    println("\n=== 聚合操作 ===")
    
    // reduce
    val sum = numbers.reduce(_ + _)
    val product = numbers.reduce(_ * _)
    
    println(s"sum: $sum")
    println(s"product: $product")
    
    // fold
    val sumWithInit = numbers.fold(0)(_ + _)
    val productWithInit = numbers.fold(1)(_ * _)
    
    println(s"sumWithInit: $sumWithInit")
    println(s"productWithInit: $productWithInit")
    
    // 直接聚合方法
    val sumDirect = numbers.sum
    val min = numbers.min
    val max = numbers.max
    val count = numbers.count(_ % 2 == 0)
    
    println(s"sumDirect: $sumDirect")
    println(s"min: $min")
    println(s"max: $max")
    println(s"count: $count")
    
    // 信息操作
    println("\n=== 信息操作 ===")
    
    val size = numbers.size
    val isEmpty = numbers.isEmpty
    val nonEmpty = numbers.nonEmpty
    val contains = numbers.contains(5)
    val exists = numbers.exists(_ > 9)
    val forall = numbers.forall(_ > 0)
    
    println(s"size: $size")
    println(s"isEmpty: $isEmpty")
    println(s"nonEmpty: $nonEmpty")
    println(s"contains: $contains")
    println(s"exists: $exists")
    println(s"forall: $forall")
    
    // 链式操作示例
    println("\n=== 链式操作 ===")
    
    val result = numbers
      .filter(_ % 2 == 0)
      .map(_ * 3)
      .take(3)
    
    println(s"chain result: $result")
    
    val wordResult = words
      .filter(_.length > 4)
      .map(_.toUpperCase)
      .sortBy(-_.length)
    
    println(s"word chain result: $wordResult")
  }
}