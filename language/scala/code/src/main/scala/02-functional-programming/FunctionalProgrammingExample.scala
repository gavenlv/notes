package chapter2

/**
 * 函数式编程综合示例
 * 展示如何将纯函数、不可变数据、高阶函数、递归、模式匹配等概念结合使用
 */
object FunctionalProgrammingExample {
  
  // 业务场景：处理电商订单数据
  
  // 1. 定义数据模型（使用样例类确保不可变性）
  case class Customer(id: String, name: String, email: String)
  case class Product(id: String, name: String, price: Double)
  case class OrderItem(product: Product, quantity: Int)
  case class Order(id: String, customer: Customer, items: List[OrderItem], status: OrderStatus)
  
  // 2. 使用密封特质定义枚举类型
  sealed trait OrderStatus
  case object Pending extends OrderStatus
  case object Processing extends OrderStatus
  case object Shipped extends OrderStatus
  case object Delivered extends OrderStatus
  case object Cancelled extends OrderStatus
  
  // 3. 纯函数：计算订单项小计
  def calculateItemSubtotal(item: OrderItem): Double = {
    item.product.price * item.quantity
  }
  
  // 4. 纯函数：计算订单总金额
  def calculateOrderTotal(order: Order): Double = {
    order.items.map(calculateItemSubtotal).sum
  }
  
  // 5. 纯函数：应用折扣
  def applyDiscount(order: Order, discountRate: Double): Order = {
    // 在函数式编程中，我们不修改原始订单，而是返回一个新订单
    order.copy() // 这里简化处理，实际应用中可能需要更复杂的逻辑
  }
  
  // 6. 高阶函数：过滤订单
  def filterOrders(orders: List[Order], predicate: Order => Boolean): List[Order] = {
    orders.filter(predicate)
  }
  
  // 7. 高阶函数：映射订单
  def mapOrders[A](orders: List[Order], f: Order => A): List[A] = {
    orders.map(f)
  }
  
  // 8. 递归函数：计算订单总数（演示尾递归优化）
  def countOrders(orders: List[Order]): Int = {
    @annotation.tailrec
    def countHelper(orders: List[Order], acc: Int): Int = orders match {
      case Nil => acc
      case _ :: tail => countHelper(tail, acc + 1)
    }
    countHelper(orders, 0)
  }
  
  // 9. 模式匹配：处理订单状态
  def processOrderStatus(status: OrderStatus): String = status match {
    case Pending => "订单待处理"
    case Processing => "订单处理中"
    case Shipped => "订单已发货"
    case Delivered => "订单已送达"
    case Cancelled => "订单已取消"
  }
  
  // 10. 模式匹配：根据客户类型提供个性化服务
  def provideCustomerService(customer: Customer): String = customer match {
    case Customer(id, name, email) if name.startsWith("VIP") => s"尊敬的VIP客户 $name，为您提供专属服务"
    case Customer(id, name, email) if email.endsWith("@company.com") => s"企业客户 $name，为您提供商务服务"
    case Customer(id, name, email) => s"普通客户 $name，为您提供标准服务"
  }
  
  // 11. 组合函数：创建订单处理管道
  def createOrderProcessingPipeline(orders: List[Order]): List[(String, Double, String)] = {
    orders
      .filter(_.status == Pending)  // 过滤待处理订单
      .map(order => (order.id, calculateOrderTotal(order), processOrderStatus(order.status)))  // 映射为(id, total, status)
      .sortBy(-_._2)  // 按总金额降序排列
  }
  
  // 12. 函数组合：创建复杂的业务逻辑
  def composeBusinessLogic(orders: List[Order]): List[String] = {
    // 定义一些基础函数
    val getCustomerId: Order => String = _.customer.id
    val getOrderTotal: Order => Double = calculateOrderTotal
    val formatOrderInfo: (String, Double) => String = (id, total) => s"订单 $id: ¥${total.formatted("%.2f")}"
    
    // 使用函数组合
    val processOrder: Order => String = (getCustomerId andThen (id => (id, getOrderTotal(orders.find(_.customer.id == id).get)))) andThen (tuple => formatOrderInfo.tupled(tuple))
    
    // 应用到订单列表
    orders.map(order => formatOrderInfo(order.id, getOrderTotal(order)))
  }
  
  // 13. 实践：生成订单报告
  def generateOrderReport(orders: List[Order]): String = {
    val totalOrders = countOrders(orders)
    val pendingOrders = filterOrders(orders, _.status == Pending)
    val totalRevenue = orders.map(calculateOrderTotal).sum
    
    val reportLines = List(
      "========== 订单报告 ==========",
      s"总订单数: $totalOrders",
      s"待处理订单数: ${pendingOrders.length}",
      s"总收入: ¥${totalRevenue.formatted("%.2f")}",
      "",
      "订单详情:",
      "-----------------------------"
    ) ++ 
    orders.map { order =>
      s"订单ID: ${order.id} | 客户: ${order.customer.name} | 总额: ¥${calculateOrderTotal(order).formatted("%.2f")} | 状态: ${processOrderStatus(order.status)}"
    }
    
    reportLines.mkString("\n")
  }
  
  // 14. 实践：客户分析
  def analyzeCustomers(orders: List[Order]): Map[String, Int] = {
    orders
      .flatMap(_.items)  // 展平所有订单项
      .groupBy(_.product.id)  // 按产品ID分组
      .view
      .mapValues(items => items.map(_.quantity).sum)  // 计算每个产品的总销量
      .toMap
  }
  
  // 测试函数
  def testFunctionalProgramming(): Unit = {
    println("=== 函数式编程综合示例 ===")
    
    // 创建测试数据
    val customer1 = Customer("C001", "Alice", "alice@example.com")
    val customer2 = Customer("C002", "VIP Bob", "vipbob@example.com")
    val customer3 = Customer("C003", "Charlie", "charlie@company.com")
    
    val product1 = Product("P001", "笔记本电脑", 8999.0)
    val product2 = Product("P002", "无线鼠标", 299.0)
    val product3 = Product("P003", "机械键盘", 599.0)
    
    val order1 = Order("O001", customer1, List(
      OrderItem(product1, 1),
      OrderItem(product2, 2)
    ), Pending)
    
    val order2 = Order("O002", customer2, List(
      OrderItem(product1, 1),
      OrderItem(product3, 1)
    ), Processing)
    
    val order3 = Order("O003", customer3, List(
      OrderItem(product2, 5)
    ), Shipped)
    
    val orders = List(order1, order2, order3)
    
    // 测试纯函数
    println("1. 纯函数测试:")
    println(s"订单 ${order1.id} 总金额: ¥${calculateOrderTotal(order1).formatted("%.2f")}")
    println(s"订单 ${order2.id} 总金额: ¥${calculateOrderTotal(order2).formatted("%.2f")}")
    
    // 测试高阶函数
    println("\n2. 高阶函数测试:")
    val pendingOrders = filterOrders(orders, _.status == Pending)
    println(s"待处理订单数: ${pendingOrders.length}")
    
    val orderTotals = mapOrders(orders, calculateOrderTotal)
    println(s"所有订单金额: ${orderTotals.map(_.formatted("%.2f")).mkString(", ")}")
    
    // 测试递归函数
    println("\n3. 递归函数测试:")
    println(s"订单总数: ${countOrders(orders)}")
    
    // 测试模式匹配
    println("\n4. 模式匹配测试:")
    orders.foreach(order => println(s"订单 ${order.id} 状态: ${processOrderStatus(order.status)}"))
    orders.foreach(order => println(provideCustomerService(order.customer)))
    
    // 测试函数组合
    println("\n5. 函数组合测试:")
    val pipelineResult = createOrderProcessingPipeline(orders)
    pipelineResult.foreach(println)
    
    // 测试订单报告生成
    println("\n6. 订单报告:")
    println(generateOrderReport(orders))
    
    // 测试客户分析
    println("\n7. 产品销量分析:")
    val productSales = analyzeCustomers(orders)
    productSales.foreach { case (productId, quantity) =>
      val product = List(product1, product2, product3).find(_.id == productId)
      product.foreach(p => println(s"${p.name} (ID: $productId): 销量 $quantity 件"))
    }
    
    println("=== 测试完成 ===\n")
  }
}

// 主程序入口
object FunctionalProgrammingExampleApp extends App {
  FunctionalProgrammingExample.testFunctionalProgramming()
}