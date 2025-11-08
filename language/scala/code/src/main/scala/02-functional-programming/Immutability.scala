package chapter2

/**
 * 不可变数据结构示例
 * 展示Scala中不可变数据结构的优势和使用方式
 */
object Immutability {
  
  // 1. 不可变变量 vs 可变变量
  def immutableVsMutable(): Unit = {
    // 不可变变量
    val immutableList = List(1, 2, 3)
    // immutableList = List(4, 5, 6) // 编译错误
    
    // 可变变量（不推荐在函数式编程中使用）
    var mutableList = List(1, 2, 3)
    mutableList = List(4, 5, 6) // 可以重新赋值
    
    println(s"不可变列表: $immutableList")
    println(s"可变列表: $mutableList")
  }
  
  // 2. 不可变集合操作
  def immutableCollectionOperations(): Unit = {
    val originalList = List(1, 2, 3, 4, 5)
    
    // 添加元素（返回新列表）
    val newList = originalList :+ 6
    val prependedList = 0 +: originalList
    
    println(s"原始列表: $originalList")
    println(s"添加元素后: $newList")
    println(s"前置元素后: $prependedList")
    
    // 过滤操作
    val filteredList = originalList.filter(_ > 3)
    println(s"过滤后: $filteredList")
    
    // 映射操作
    val mappedList = originalList.map(_ * 2)
    println(s"映射后: $mappedList")
  }
  
  // 3. 不可变Map操作
  def immutableMapOperations(): Unit = {
    val originalMap = Map("a" -> 1, "b" -> 2, "c" -> 3)
    
    // 添加键值对（返回新Map）
    val newMap = originalMap + ("d" -> 4)
    val updatedMap = originalMap.updated("b", 20)
    
    println(s"原始Map: $originalMap")
    println(s"添加元素后: $newMap")
    println(s"更新元素后: $updatedMap")
  }
  
  // 4. 不可变自定义数据结构
  case class Person(name: String, age: Int) {
    // 返回新实例而不是修改当前实例
    def withAge(newAge: Int): Person = this.copy(age = newAge)
    def withName(newName: String): Person = this.copy(name = newName)
  }
  
  // 5. 不可变链表实现
  sealed trait ImmutableList[+A]
  case object Empty extends ImmutableList[Nothing]
  case class Cons[+A](head: A, tail: ImmutableList[A]) extends ImmutableList[A]
  
  object ImmutableList {
    def apply[A](elements: A*): ImmutableList[A] = {
      if (elements.isEmpty) Empty
      else Cons(elements.head, apply(elements.tail: _*))
    }
    
    def prepend[A](element: A, list: ImmutableList[A]): ImmutableList[A] = {
      Cons(element, list)
    }
    
    def append[A](list: ImmutableList[A], element: A): ImmutableList[A] = list match {
      case Empty => Cons(element, Empty)
      case Cons(head, tail) => Cons(head, append(tail, element))
    }
  }
  
  // 6. 不可变二叉树
  sealed trait BinaryTree[+A]
  case object Leaf extends BinaryTree[Nothing]
  case class Node[A](value: A, left: BinaryTree[A], right: BinaryTree[A]) extends BinaryTree[A]
  
  object BinaryTree {
    def insert[A](tree: BinaryTree[A], value: A)(implicit ord: Ordering[A]): BinaryTree[A] = tree match {
      case Leaf => Node(value, Leaf, Leaf)
      case Node(currentValue, left, right) =>
        if (ord.lt(value, currentValue)) {
          Node(currentValue, insert(left, value), right)
        } else {
          Node(currentValue, left, insert(right, value))
        }
    }
    
    def contains[A](tree: BinaryTree[A], value: A)(implicit ord: Ordering[A]): Boolean = tree match {
      case Leaf => false
      case Node(currentValue, left, right) =>
        if (ord.equiv(value, currentValue)) true
        else if (ord.lt(value, currentValue)) contains(left, value)
        else contains(right, value)
    }
  }
  
  // 7. 不可变栈实现
  case class ImmutableStack[A](elements: List[A] = Nil) {
    def push(element: A): ImmutableStack[A] = ImmutableStack(element :: elements)
    def pop: Option[(A, ImmutableStack[A])] = elements match {
      case Nil => None
      case head :: tail => Some((head, ImmutableStack(tail)))
    }
    def peek: Option[A] = elements.headOption
    def isEmpty: Boolean = elements.isEmpty
  }
  
  // 8. 不可变队列实现
  case class ImmutableQueue[A](in: List[A] = Nil, out: List[A] = Nil) {
    def enqueue(element: A): ImmutableQueue[A] = ImmutableQueue(element :: in, out)
    
    def dequeue: Option[(A, ImmutableQueue[A])] = out match {
      case head :: tail => Some((head, ImmutableQueue(in, tail)))
      case Nil => in.reverse match {
        case head :: tail => Some((head, ImmutableQueue(Nil, tail)))
        case Nil => None
      }
    }
    
    def isEmpty: Boolean = in.isEmpty && out.isEmpty
  }
  
  // 9. 不可变数据结构的优势演示
  def immutabilityBenefits(): Unit = {
    // 线程安全示例
    val sharedData = List(1, 2, 3, 4, 5)
    
    // 多个线程可以安全地共享和使用不可变数据
    val processed1 = sharedData.map(_ * 2)
    val processed2 = sharedData.filter(_ % 2 == 0)
    
    println(s"原始数据: $sharedData")
    println(s"处理结果1 (乘以2): $processed1")
    println(s"处理结果2 (偶数): $processed2")
    println(s"原始数据保持不变: $sharedData")
  }
  
  // 10. 实践：构建不可变的数据处理管道
  def dataProcessingPipeline(): Unit = {
    case class Employee(name: String, department: String, salary: Double)
    
    val employees = List(
      Employee("Alice", "Engineering", 80000),
      Employee("Bob", "Marketing", 60000),
      Employee("Charlie", "Engineering", 90000),
      Employee("David", "Sales", 70000),
      Employee("Eve", "Engineering", 95000)
    )
    
    // 构建数据处理管道
    val result = employees
      .filter(_.department == "Engineering")  // 过滤工程部员工
      .map(emp => emp.copy(salary = emp.salary * 1.1))  // 加薪10%
      .sortBy(-_.salary)  // 按薪资降序排列
      .take(2)  // 取前两名
    
    println("工程部加薪10%后薪资最高的两名员工:")
    result.foreach(emp => println(s"${emp.name}: ${emp.salary}"))
    
    println("原始员工数据保持不变:")
    employees.foreach(emp => println(s"${emp.name}: ${emp.salary} (${emp.department})"))
  }
  
  // 测试函数
  def testImmutability(): Unit = {
    println("=== 不可变数据结构测试 ===")
    
    println("1. 不可变变量 vs 可变变量:")
    immutableVsMutable()
    
    println("\n2. 不可变集合操作:")
    immutableCollectionOperations()
    
    println("\n3. 不可变Map操作:")
    immutableMapOperations()
    
    println("\n4. 自定义不可变数据结构:")
    val person = Person("Alice", 25)
    val updatedPerson = person.withAge(26)
    println(s"原始人员: $person")
    println(s"更新年龄后: $updatedPerson")
    
    println("\n5. 不可变链表示例:")
    val list = ImmutableList(1, 2, 3, 4, 5)
    val prepended = ImmutableList.prepend(0, list)
    val appended = ImmutableList.append(list, 6)
    println(s"原始链表: $list")
    println(s"前置元素后: $prepended")
    println(s"追加元素后: $appended")
    
    println("\n6. 不可变二叉树示例:")
    implicit val intOrdering: Ordering[Int] = Ordering.Int
    val tree = BinaryTree.insert(BinaryTree.insert(BinaryTree.insert(Leaf, 5), 3), 7)
    println(s"构建的树: $tree")
    println(s"树包含3: ${BinaryTree.contains(tree, 3)}")
    println(s"树包含4: ${BinaryTree.contains(tree, 4)}")
    
    println("\n7. 不可变栈示例:")
    val stack = ImmutableStack[Int]()
      .push(1)
      .push(2)
      .push(3)
    println(s"栈内容: ${stack.elements}")
    val popped = stack.pop
    println(s"弹出元素: ${popped.map(_._1)}")
    println(s"剩余栈: ${popped.map(_._2.elements)}")
    
    println("\n8. 不可变队列示例:")
    val queue = ImmutableQueue[Int]()
      .enqueue(1)
      .enqueue(2)
      .enqueue(3)
    println(s"入队后队列: in=${queue.in}, out=${queue.out}")
    val dequeued = queue.dequeue
    println(s"出队元素: ${dequeued.map(_._1)}")
    println(s"剩余队列: ${dequeued.map(q => s"in=${q._2.in}, out=${q._2.out}")}")
    
    println("\n9. 不可变数据结构优势:")
    immutabilityBenefits()
    
    println("\n10. 数据处理管道:")
    dataProcessingPipeline()
    
    println("=== 测试完成 ===\n")
  }
}

// 主程序入口
object ImmutabilityApp extends App {
  Immutability.testImmutability()
}