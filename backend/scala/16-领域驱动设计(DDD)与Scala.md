# 第16章：领域驱动设计(DDD)与Scala

## 16.1 DDD基础概念

### 16.1.1 领域驱动设计概述

领域驱动设计（Domain-Driven Design，DDD）是一种软件开发方法，它将复杂的业务领域作为设计的中心，强调软件的核心是解决特定领域的问题。Scala的函数式特性和强大的类型系统使其成为实现DDD的理想语言。

```scala
// DDD基础概念示例

// 1. 领域模型
package domain.model

// 实体（Entity）- 具有唯一标识的对象
trait Entity[ID] {
  def id: ID
}

// 值对象（Value Object）- 没有标识的对象，通过属性值相等
case class Address(street: String, city: String, postalCode: String, country: String)

// 聚合（Aggregate）- 数据修改的单元，由实体和值对象组成
case class CustomerId(value: String) extends AnyVal
case class Customer(id: CustomerId, name: String, email: Email, address: Option[Address])

// 领域服务（Domain Service）- 不属于实体或值对象的业务逻辑
class CustomerValidationService {
  def isValidEmail(email: String): Boolean = email.contains("@")
  def isValidAddress(address: Address): Boolean = 
    address.street.nonEmpty && address.city.nonEmpty && address.postalCode.nonEmpty
}

// 仓储（Repository）- 聚合的持久化和检索
trait CustomerRepository {
  def findById(id: CustomerId): Option[Customer]
  def save(customer: Customer): Customer
  def delete(id: CustomerId): Unit
}

// 工厂（Factory）- 创建复杂对象
class CustomerFactory {
  def create(name: String, email: Email): Customer = {
    val id = CustomerId(java.util.UUID.randomUUID().toString)
    Customer(id, name, email, None)
  }
}
```

### 16.1.2 领域事件

```scala
// 领域事件定义

package domain.events

import java.time.LocalDateTime

// 领域事件基类
trait DomainEvent {
  def eventId: String
  def timestamp: LocalDateTime
  def aggregateId: String
}

// 具体领域事件
case class CustomerCreated(eventId: String, timestamp: LocalDateTime, aggregateId: String, 
                          customerId: CustomerId, name: String, email: String) extends DomainEvent

case class CustomerEmailChanged(eventId: String, timestamp: LocalDateTime, aggregateId: String,
                               customerId: CustomerId, oldEmail: String, newEmail: String) extends DomainEvent

case class CustomerAddressUpdated(eventId: String, timestamp: LocalDateTime, aggregateId: String,
                                 customerId: CustomerId, address: Address) extends DomainEvent

// 事件发布接口
trait DomainEventPublisher {
  def publish(event: DomainEvent): Unit
  def publish(events: List[DomainEvent]): Unit
}

// 简单内存实现
class InMemoryDomainEventPublisher extends DomainEventPublisher {
  private val publishedEvents = scala.collection.mutable.ListBuffer.empty[DomainEvent]
  
  def publish(event: DomainEvent): Unit = publishedEvents += event
  def publish(events: List[DomainEvent]): Unit = publishedEvents ++= events
  
  def getPublishedEvents: List[DomainEvent] = publishedEvents.toList
  def clear(): Unit = publishedEvents.clear()
}

// 实体与事件聚合
class EventSourcedCustomer(
  val id: CustomerId, 
  var name: String, 
  var email: Email, 
  var address: Option[Address] = None,
  private val pendingEvents: scala.collection.mutable.ListBuffer[DomainEvent] = 
    scala.collection.mutable.ListBuffer.empty
) extends Entity[CustomerId] {
  
  // 更改邮箱
  def changeEmail(newEmail: Email, eventPublisher: DomainEventPublisher): Unit = {
    val oldEmail = email.value
    this.email = newEmail
    
    val event = CustomerEmailChanged(
      eventId = java.util.UUID.randomUUID().toString,
      timestamp = java.time.LocalDateTime.now(),
      aggregateId = id.value,
      customerId = id,
      oldEmail = oldEmail,
      newEmail = newEmail.value
    )
    
    pendingEvents += event
    eventPublisher.publish(event)
  }
  
  // 更新地址
  def updateAddress(newAddress: Address, eventPublisher: DomainEventPublisher): Unit = {
    val oldAddress = this.address
    this.address = Some(newAddress)
    
    val event = CustomerAddressUpdated(
      eventId = java.util.UUID.randomUUID().toString,
      timestamp = java.time.LocalDateTime.now(),
      aggregateId = id.value,
      customerId = id,
      address = newAddress
    )
    
    pendingEvents += event
    eventPublisher.publish(event)
  }
  
  // 获取待发布事件
  def getUncommittedEvents: List[DomainEvent] = pendingEvents.toList
  
  // 清空待发布事件
  def markEventsAsCommitted(): Unit = pendingEvents.clear()
}
```

### 16.1.3 聚合根

```scala
// 聚合根实现

package domain.aggregate

// 订单聚合根
case class OrderId(value: String) extends AnyVal
case class ProductId(value: String) extends AnyVal

case class Money(amount: BigDecimal, currency: String) {
  def +(other: Money): Money = {
    if (currency != other.currency) {
      throw new IllegalArgumentException("Cannot add money with different currencies")
    }
    Money(amount + other.amount, currency)
  }
  
  def *(quantity: Int): Money = Money(amount * quantity, currency)
  
  def isPositive: Boolean = amount > 0
}

case class OrderLine(productId: ProductId, productName: String, quantity: Int, unitPrice: Money) {
  def total: Money = unitPrice * quantity
  
  def withQuantity(newQuantity: Int): OrderLine = {
    if (newQuantity <= 0) {
      throw new IllegalArgumentException("Quantity must be positive")
    }
    copy(quantity = newQuantity)
  }
}

sealed trait OrderStatus
object OrderStatus {
  case object Pending extends OrderStatus
  case object Confirmed extends OrderStatus
  case object Shipped extends OrderStatus
  case object Delivered extends OrderStatus
  case object Cancelled extends OrderStatus
}

// 订单聚合根
class Order(
  val id: OrderId,
  val customerId: CustomerId,
  var status: OrderStatus,
  var orderLines: List[OrderLine],
  val createdAt: java.time.LocalDateTime,
  val eventPublisher: DomainEventPublisher
) extends Entity[OrderId] {
  
  // 添加订单项
  def addOrderLine(productId: ProductId, productName: String, quantity: Int, unitPrice: Money): Unit = {
    if (status != OrderStatus.Pending && status != OrderStatus.Confirmed) {
      throw new IllegalStateException(s"Cannot add line to order in status: $status")
    }
    
    val newLine = OrderLine(productId, productName, quantity, unitPrice)
    orderLines = orderLines :+ newLine
    
    // 发布领域事件
    val event = OrderLineAdded(
      eventId = java.util.UUID.randomUUID().toString,
      timestamp = java.time.LocalDateTime.now(),
      aggregateId = id.value,
      orderId = id,
      productId = productId,
      quantity = quantity,
      unitPrice = unitPrice
    )
    
    eventPublisher.publish(event)
  }
  
  // 更新订单项数量
  def updateOrderLineQuantity(productId: ProductId, newQuantity: Int): Unit = {
    if (status != OrderStatus.Pending && status != OrderStatus.Confirmed) {
      throw new IllegalStateException(s"Cannot update line in order with status: $status")
    }
    
    orderLines.find(_.productId == productId) match {
      case Some(line) =>
        val updatedLine = line.withQuantity(newQuantity)
        orderLines = orderLines.map {
          case line if line.productId == productId => updatedLine
          case other => other
        }
        
        // 发布领域事件
        val event = OrderLineUpdated(
          eventId = java.util.UUID.randomUUID().toString,
          timestamp = java.time.LocalDateTime.now(),
          aggregateId = id.value,
          orderId = id,
          productId = productId,
          oldQuantity = line.quantity,
          newQuantity = newQuantity
        )
        
        eventPublisher.publish(event)
        
      case None =>
        throw new IllegalArgumentException(s"No order line found for product: $productId")
    }
  }
  
  // 计算订单总额
  def total: Money = {
    orderLines.map(_.total).foldLeft(Money(0, "USD"))(_ + _)
  }
  
  // 确认订单
  def confirm(): Unit = {
    if (status != OrderStatus.Pending) {
      throw new IllegalStateException(s"Cannot confirm order in status: $status")
    }
    
    if (orderLines.isEmpty) {
      throw new IllegalStateException("Cannot confirm order with no items")
    }
    
    status = OrderStatus.Confirmed
    
    // 发布领域事件
    val event = OrderConfirmed(
      eventId = java.util.UUID.randomUUID().toString,
      timestamp = java.time.LocalDateTime.now(),
      aggregateId = id.value,
      orderId = id,
      customerId = customerId
    )
    
    eventPublisher.publish(event)
  }
  
  // 发货订单
  def ship(): Unit = {
    if (status != OrderStatus.Confirmed) {
      throw new IllegalStateException(s"Cannot ship order in status: $status")
    }
    
    status = OrderStatus.Shipped
    
    // 发布领域事件
    val event = OrderShipped(
      eventId = java.util.UUID.randomUUID().toString,
      timestamp = java.time.LocalDateTime.now(),
      aggregateId = id.value,
      orderId = id,
      customerId = customerId
    )
    
    eventPublisher.publish(event)
  }
  
  // 取消订单
  def cancel(reason: String): Unit = {
    if (status == OrderStatus.Delivered || status == OrderStatus.Cancelled) {
      throw new IllegalStateException(s"Cannot cancel order in status: $status")
    }
    
    status = OrderStatus.Cancelled
    
    // 发布领域事件
    val event = OrderCancelled(
      eventId = java.util.UUID.randomUUID().toString,
      timestamp = java.time.LocalDateTime.now(),
      aggregateId = id.value,
      orderId = id,
      customerId = customerId,
      reason = reason
    )
    
    eventPublisher.publish(event)
  }
}

// 订单相关领域事件
case class OrderLineAdded(eventId: String, timestamp: LocalDateTime, aggregateId: String,
                        orderId: OrderId, productId: ProductId, quantity: Int, unitPrice: Money) extends DomainEvent

case class OrderLineUpdated(eventId: String, timestamp: LocalDateTime, aggregateId: String,
                          orderId: OrderId, productId: ProductId, oldQuantity: Int, newQuantity: Int) extends DomainEvent

case class OrderConfirmed(eventId: String, timestamp: LocalDateTime, aggregateId: String,
                         orderId: OrderId, customerId: CustomerId) extends DomainEvent

case class OrderShipped(eventId: String, timestamp: LocalDateTime, aggregateId: String,
                       orderId: OrderId, customerId: CustomerId) extends DomainEvent

case class OrderCancelled(eventId: String, timestamp: LocalDateTime, aggregateId: String,
                         orderId: OrderId, customerId: CustomerId, reason: String) extends DomainEvent
```

## 16.2 领域建模与类型系统

### 16.2.1 使用类型增强领域表达

```scala
// 使用Scala类型系统增强领域模型

package domain.types

// 1. 使用特定类型而非原始类型
case class CustomerId(value: String) extends AnyVal
case class ProductId(value: String) extends AnyVal
case class OrderId(value: String) extends AnyVal

// 2. 邮箱类型
sealed trait Email {
  def value: String
}

object Email {
  // 安全邮箱构造器
  def fromString(value: String): Either[String, ValidEmail] = {
    if (value.matches("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$")) {
      Right(ValidEmail(value))
    } else {
      Left(s"Invalid email format: $value")
    }
  }
}

case class ValidEmail(value: String) extends Email

// 3. 价格类型
sealed trait Price {
  def amount: BigDecimal
  def currency: String
}

object Price {
  def fromAmount(amount: BigDecimal, currency: String): Either[String, ValidPrice] = {
    if (amount > 0) {
      Right(ValidPrice(amount, currency))
    } else {
      Left("Price must be positive")
    }
  }
}

case class ValidPrice(amount: BigDecimal, currency: String) extends Price

// 4. 日期类型
case class LocalDate private(value: java.time.LocalDate) {
  def isBefore(other: LocalDate): Boolean = value.isBefore(other.value)
  def isAfter(other: LocalDate): Boolean = value.isAfter(other.value)
}

object LocalDate {
  def of(year: Int, month: Int, day: Int): Option[LocalDate] = {
    try {
      Some(LocalDate(java.time.LocalDate.of(year, month, day)))
    } catch {
      case _: java.time.DateTimeException => None
    }
  }
  
  def now(): LocalDate = LocalDate(java.time.LocalDate.now())
}

// 5. 时段类型
case class DateRange(start: LocalDate, end: LocalDate) {
  def contains(date: LocalDate): Boolean = 
    !date.isBefore(start) && !date.isAfter(end)
  
  def overlaps(other: DateRange): Boolean = 
    !(end.isBefore(other.start) || start.isAfter(other.end))
}

// 6. 使用ADT建模业务规则
sealed trait ProductStatus
object ProductStatus {
  case object Available extends ProductStatus
  case object OutOfStock extends ProductStatus
  case object Discontinued extends ProductStatus
}

// 7. 不可变实体
case class Product(
  id: ProductId,
  name: String,
  description: String,
  price: ValidPrice,
  status: ProductStatus
) {
  
  // 更新价格
  def withPrice(newPrice: ValidPrice): Product = copy(price = newPrice)
  
  // 更改状态
  def withStatus(newStatus: ProductStatus): Product = copy(status = newStatus)
  
  // 缺货
  def markOutOfStock(): Product = copy(status = ProductStatus.OutOfStock)
  
  // 补货
  def markAvailable(): Product = copy(status = ProductStatus.Available)
  
  // 停产
  def discontinue(): Product = copy(status = ProductStatus.Discontinued)
}

// 8. 使用typeclass实现多态
trait TaxCalculator[T] {
  def calculateTax(amount: BigDecimal, taxRate: BigDecimal): BigDecimal
}

object TaxCalculator {
  implicit val standardTaxCalculator: TaxCalculator[Product] = new TaxCalculator[Product] {
    def calculateTax(amount: BigDecimal, taxRate: BigDecimal): BigDecimal = amount * taxRate
  }
  
  implicit val discountedTaxCalculator: TaxCalculator[Product] = new TaxCalculator[Product] {
    def calculateTax(amount: BigDecimal, taxRate: BigDecimal): BigDecimal = {
      val discountedAmount = amount * 0.9  // 10%折扣
      discountedAmount * taxRate
    }
  }
}

// 9. 领域服务使用typeclass
class PricingService {
  def calculatePriceWithTax[T](price: ValidPrice, taxRate: BigDecimal)
                               (implicit taxCalculator: TaxCalculator[T]): Either[String, BigDecimal] = {
    val tax = taxCalculator.calculateTax(price.amount, taxRate)
    Right(price.amount + tax)
  }
  
  def applyDiscount(price: ValidPrice, discountPercentage: BigDecimal): Either[String, ValidPrice] = {
    if (discountPercentage < 0 || discountPercentage > 100) {
      Left("Discount percentage must be between 0 and 100")
    } else {
      val discountedAmount = price.amount * (1 - discountPercentage / 100)
      ValidPrice.fromAmount(discountedAmount, price.currency)
    }
  }
}
```

### 16.2.2 领域不变量

```scala
// 使用类型系统强制领域不变量

package domain.invariants

// 1. 使用密封类型表示有效值
sealed trait NonEmptyString {
  def value: String
}

object NonEmptyString {
  def fromString(value: String): Either[String, NonEmptyStringImpl] = {
    if (value.nonEmpty && value.trim.nonEmpty) {
      Right(NonEmptyStringImpl(value.trim))
    } else {
      Left("String cannot be empty or whitespace")
    }
  }
}

case class NonEmptyStringImpl(value: String) extends NonEmptyString

// 2. 正整数类型
sealed trait PositiveInt {
  def value: Int
}

object PositiveInt {
  def fromInt(value: Int): Either[String, PositiveIntImpl] = {
    if (value > 0) {
      Right(PositiveIntImpl(value))
    } else {
      Left(s"Value must be positive, got: $value")
    }
  }
}

case class PositiveIntImpl(value: Int) extends PositiveInt

// 3. 非负整数类型
sealed trait NonNegativeInt {
  def value: Int
}

object NonNegativeInt {
  def fromInt(value: Int): Either[String, NonNegativeIntImpl] = {
    if (value >= 0) {
      Right(NonNegativeIntImpl(value))
    } else {
      Left(s"Value must be non-negative, got: $value")
    }
  }
}

case class NonNegativeIntImpl(value: Int) extends NonNegativeInt

// 4. 百分比类型
sealed trait Percentage {
  def value: BigDecimal
}

object Percentage {
  def fromBigDecimal(value: BigDecimal): Either[String, PercentageImpl] = {
    if (value >= 0 && value <= 100) {
      Right(PercentageImpl(value))
    } else {
      Left(s"Percentage must be between 0 and 100, got: $value")
    }
  }
}

case class PercentageImpl(value: BigDecimal) extends Percentage {
  def asDecimal: BigDecimal = value / 100
}

// 5. 货币金额类型
case class CurrencyCode(value: String) extends AnyVal

sealed trait MoneyAmount {
  def amount: BigDecimal
  def currency: CurrencyCode
  
  def +(other: MoneyAmount): Either[String, MoneyAmount]
  def -(other: MoneyAmount): Either[String, MoneyAmount]
  def *(factor: BigDecimal): Either[String, MoneyAmount]
}

object MoneyAmount {
  def create(amount: BigDecimal, currency: CurrencyCode): Either[String, MoneyAmountImpl] = {
    if (amount >= 0) {
      Right(MoneyAmountImpl(amount, currency))
    } else {
      Left("Amount cannot be negative")
    }
  }
}

case class MoneyAmountImpl(amount: BigDecimal, currency: CurrencyCode) extends MoneyAmount {
  def +(other: MoneyAmount): Either[String, MoneyAmount] = {
    if (currency != other.currency) {
      Left("Cannot add money with different currencies")
    } else {
      MoneyAmount.create(amount + other.amount, currency)
    }
  }
  
  def -(other: MoneyAmount): Either[String, MoneyAmount] = {
    if (currency != other.currency) {
      Left("Cannot subtract money with different currencies")
    } else {
      MoneyAmount.create(amount - other.amount, currency)
    }
  }
  
  def *(factor: BigDecimal): Either[String, MoneyAmount] = {
    if (factor < 0) {
      Left("Factor must be non-negative")
    } else {
      MoneyAmount.create(amount * factor, currency)
    }
  }
}

// 6. 领域不变量实体
case class OrderLine private(
  productId: ProductId,
  productName: NonEmptyStringImpl,
  quantity: PositiveIntImpl,
  unitPrice: MoneyAmountImpl
) {
  
  // 计算行项总额
  def total: Either[String, MoneyAmount] = {
    unitPrice *(BigDecimal(quantity.value))
  }
  
  // 更新数量
  def withQuantity(newQuantity: PositiveIntImpl): Either[String, OrderLine] = {
    // 业务规则：不能更改产品ID
    Right(OrderLine(productId, productName, newQuantity, unitPrice))
  }
  
  // 更新单价
  def withUnitPrice(newUnitPrice: MoneyAmountImpl): Either[String, OrderLine] = {
    // 业务规则：不能更改产品ID
    Right(OrderLine(productId, productName, quantity, newUnitPrice))
  }
}

object OrderLine {
  def create(
    productId: ProductId,
    productName: NonEmptyStringImpl,
    quantity: PositiveIntImpl,
    unitPrice: MoneyAmountImpl
  ): Either[String, OrderLine] = {
    // 业务规则验证
    if (quantity.value > 100) {
      Left("Quantity cannot exceed 100")
    } else if (unitPrice.amount > BigDecimal(10000)) {
      Left("Unit price cannot exceed 10000")
    } else {
      Right(OrderLine(productId, productName, quantity, unitPrice))
    }
  }
}

// 7. 使用typeclass进行验证
trait Validator[T] {
  def validate(value: T): Either[String, T]
}

object Validator {
  implicit val emailValidator: Validator[String] = new Validator[String] {
    def validate(email: String): Either[String, String] = {
      if (email.matches("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$")) {
        Right(email)
      } else {
        Left(s"Invalid email format: $email")
      }
    }
  }
  
  implicit val phoneNumberValidator: Validator[String] = new Validator[String] {
    def validate(phoneNumber: String): Either[String, String] = {
      if (phoneNumber.matches("^[+]?[0-9\\-\\s]{10,}$")) {
        Right(phoneNumber)
      } else {
        Left(s"Invalid phone number format: $phoneNumber")
      }
    }
  }
}

// 8. 验证函数
object Validation {
  def validate[T](value: T)(implicit validator: Validator[T]): Either[String, T] = {
    validator.validate(value)
  }
  
  def validateAll[T](values: List[T])(implicit validator: Validator[T]): Either[List[String], List[T]] = {
    val results = values.map(validate)
    
    val errors = results.collect { case Left(error) => error }
    val validValues = results.collect { case Right(value) => value }
    
    if (errors.nonEmpty) {
      Left(errors)
    } else {
      Right(validValues)
    }
  }
}

// 9. 使用验证的领域服务
class OrderLineValidationService {
  def validateOrderLine(
    productId: ProductId,
    productName: String,
    quantity: Int,
    unitPriceAmount: BigDecimal,
    unitPriceCurrency: String
  ): Either[String, OrderLine] = {
    for {
      validProductName <- NonEmptyString.fromString(productName)
      validQuantity <- PositiveInt.fromInt(quantity)
      currencyCode = CurrencyCode(unitPriceCurrency)
      validUnitPrice <- MoneyAmount.create(unitPriceAmount, currencyCode)
      orderLine <- OrderLine.create(productId, validProductName, validQuantity, validUnitPrice)
    } yield orderLine
  }
}
```

## 16.3 应用服务与领域服务

### 16.3.1 应用服务

```scala
// 应用服务实现

package application

import domain.model._
import domain.aggregate._
import domain.events._
import domain.repository._
import domain.service._
import cats.data.EitherT
import cats.implicits._
import scala.concurrent.{ExecutionContext, Future}

// 1. 订单应用服务
class OrderApplicationService(
  orderRepository: OrderRepository,
  customerRepository: CustomerRepository,
  productRepository: ProductRepository,
  domainEventPublisher: DomainEventPublisher
)(implicit ec: ExecutionContext) {
  
  // 创建订单
  def createOrder(
    customerId: CustomerId,
    productQuantities: Map[ProductId, Int]
  ): Future[Either[String, Order]] = {
    
    val result = for {
      // 检查客户是否存在
      customer <- EitherT.fromOptionF(
        customerRepository.findById(customerId),
        "Customer not found"
      )
      
      // 验证所有产品并获取价格
      productLines <- EitherT.liftF(
        Future.sequence(productQuantities.map { case (productId, quantity) =>
          productRepository.findById(productId).map {
            case Some(product) if product.status == ProductStatus.Available => 
              Right((product, quantity))
            case Some(product) => 
              Left(s"Product ${productId.value} is not available")
            case None => 
              Left(s"Product ${productId.value} not found")
          }
        }.toList)
      )
      
      // 检查是否有无效产品
      validatedLines <- EitherT.fromEither[Future](
        productLines.sequence
      )
      
      // 创建订单项
      orderLines <- EitherT.fromEither[Future](
        validatedLines.traverse { case (product, quantity) =>
          OrderLine.create(
            product.id,
            product.name,
            quantity,
            product.price
          ).leftMap(error => s"Invalid order line: $error")
        }
      )
      
      // 创建订单
      orderId = OrderId(java.util.UUID.randomUUID().toString)
      order = new Order(
        id = orderId,
        customerId = customerId,
        status = OrderStatus.Pending,
        orderLines = orderLines,
        createdAt = java.time.LocalDateTime.now(),
        eventPublisher = domainEventPublisher
      )
      
      // 保存订单
      savedOrder <- EitherT.right[String](
        orderRepository.save(order)
      )
      
    } yield savedOrder
    
    result.value
  }
  
  // 更新订单项
  def updateOrderItem(
    orderId: OrderId,
    productId: ProductId,
    newQuantity: Int
  ): Future[Either[String, Order]] = {
    
    val result = for {
      // 获取订单
      order <- EitherT.fromOptionF(
        orderRepository.findById(orderId),
        "Order not found"
      )
      
      // 检查订单状态
      _ <- EitherT.cond[Future](
        order.status == OrderStatus.Pending,
        (),
        s"Cannot update order in status: ${order.status}"
      )
      
      // 验证数量
      validQuantity <- EitherT.fromEither[Future](
        PositiveInt.fromInt(newQuantity)
      )
      
      // 更新订单项
      _ = order.updateOrderLineQuantity(productId, newQuantity)
      
      // 保存订单
      savedOrder <- EitherT.right[String](
        orderRepository.save(order)
      )
      
    } yield savedOrder
    
    result.value
  }
  
  // 确认订单
  def confirmOrder(orderId: OrderId): Future[Either[String, Order]] = {
    
    val result = for {
      // 获取订单
      order <- EitherT.fromOptionF(
        orderRepository.findById(orderId),
        "Order not found"
      )
      
      // 确认订单
      _ = order.confirm()
      
      // 保存订单
      savedOrder <- EitherT.right[String](
        orderRepository.save(order)
      )
      
    } yield savedOrder
    
    result.value
  }
  
  // 发货订单
  def shipOrder(orderId: OrderId): Future[Either[String, Order]] = {
    
    val result = for {
      // 获取订单
      order <- EitherT.fromOptionF(
        orderRepository.findById(orderId),
        "Order not found"
      )
      
      // 发货订单
      _ = order.ship()
      
      // 保存订单
      savedOrder <- EitherT.right[String](
        orderRepository.save(order)
      )
      
    } yield savedOrder
    
    result.value
  }
  
  // 取消订单
  def cancelOrder(orderId: OrderId, reason: String): Future[Either[String, Order]] = {
    
    val result = for {
      // 获取订单
      order <- EitherT.fromOptionF(
        orderRepository.findById(orderId),
        "Order not found"
      )
      
      // 取消订单
      _ = order.cancel(reason)
      
      // 保存订单
      savedOrder <- EitherT.right[String](
        orderRepository.save(order)
      )
      
    } yield savedOrder
    
    result.value
  }
}

// 2. 客户应用服务
class CustomerApplicationService(
  customerRepository: CustomerRepository,
  emailService: EmailService,
  domainEventPublisher: DomainEventPublisher
)(implicit ec: ExecutionContext) {
  
  // 创建客户
  def createCustomer(name: String, emailString: String): Future[Either[String, Customer]] = {
    
    val result = for {
      // 验证邮箱
      email <- EitherT.fromEither[Future](
        Email.fromString(emailString)
      )
      
      // 创建客户
      customerId = CustomerId(java.util.UUID.randomUUID().toString)
      customer = Customer(customerId, name, email, None)
      
      // 保存客户
      savedCustomer <- EitherT.right[String](
        customerRepository.save(customer)
      )
      
      // 发布事件
      _ = domainEventPublisher.publish(
        CustomerCreated(
          eventId = java.util.UUID.randomUUID().toString,
          timestamp = java.time.LocalDateTime.now(),
          aggregateId = customerId.value,
          customerId = customerId,
          name = name,
          email = email.value
        )
      )
      
      // 发送欢迎邮件
      _ = emailService.sendWelcomeEmail(email)
      
    } yield savedCustomer
    
    result.value
  }
  
  // 更新客户邮箱
  def updateCustomerEmail(customerId: CustomerId, newEmailString: String): Future[Either[String, Customer]] = {
    
    val result = for {
      // 验证邮箱
      newEmail <- EitherT.fromEither[Future](
        Email.fromString(newEmailString)
      )
      
      // 获取客户
      customer <- EitherT.fromOptionF(
        customerRepository.findById(customerId),
        "Customer not found"
      )
      
      // 更新邮箱
      updatedCustomer = customer.copy(email = newEmail)
      
      // 保存客户
      savedCustomer <- EitherT.right[String](
        customerRepository.save(updatedCustomer)
      )
      
      // 发布事件
      _ = domainEventPublisher.publish(
        CustomerEmailChanged(
          eventId = java.util.UUID.randomUUID().toString,
          timestamp = java.time.LocalDateTime.now(),
          aggregateId = customerId.value,
          customerId = customerId,
          oldEmail = customer.email.value,
          newEmail = newEmail.value
        )
      )
      
    } yield savedCustomer
    
    result.value
  }
}

// 3. 产品应用服务
class ProductApplicationService(
  productRepository: ProductRepository,
  domainEventPublisher: DomainEventPublisher
)(implicit ec: ExecutionContext) {
  
  // 创建产品
  def createProduct(
    name: String,
    description: String,
    priceAmount: BigDecimal,
    currency: String
  ): Future[Either[String, Product]] = {
    
    val result = for {
      // 创建价格
      price <- EitherT.fromEither[Future](
        Price.fromAmount(priceAmount, currency)
      )
      
      // 创建产品
      productId = ProductId(java.util.UUID.randomUUID().toString)
      product = Product(productId, name, description, price, ProductStatus.Available)
      
      // 保存产品
      savedProduct <- EitherT.right[String](
        productRepository.save(product)
      )
      
      // 发布事件
      _ = domainEventPublisher.publish(
        ProductCreated(
          eventId = java.util.UUID.randomUUID().toString,
          timestamp = java.time.LocalDateTime.now(),
          aggregateId = productId.value,
          productId = productId,
          name = name,
          description = description,
          priceAmount = price.amount,
          currency = price.currency
        )
      )
      
    } yield savedProduct
    
    result.value
  }
  
  // 更新产品价格
  def updateProductPrice(
    productId: ProductId,
    newPriceAmount: BigDecimal
  ): Future[Either[String, Product]] = {
    
    val result = for {
      // 获取产品
      product <- EitherT.fromOptionF(
        productRepository.findById(productId),
        "Product not found"
      )
      
      // 创建新价格
      newPrice <- EitherT.fromEither[Future](
        Price.fromAmount(newPriceAmount, product.price.currency)
      )
      
      // 更新产品
      updatedProduct = product.withPrice(newPrice)
      
      // 保存产品
      savedProduct <- EitherT.right[String](
        productRepository.save(updatedProduct)
      )
      
      // 发布事件
      _ = domainEventPublisher.publish(
        ProductPriceChanged(
          eventId = java.util.UUID.randomUUID().toString,
          timestamp = java.time.LocalDateTime.now(),
          aggregateId = productId.value,
          productId = productId,
          oldPriceAmount = product.price.amount,
          newPriceAmount = newPrice.amount
        )
      )
      
    } yield savedProduct
    
    result.value
  }
  
  // 标记产品为缺货
  def markProductOutOfStock(productId: ProductId): Future[Either[String, Product]] = {
    
    val result = for {
      // 获取产品
      product <- EitherT.fromOptionF(
        productRepository.findById(productId),
        "Product not found"
      )
      
      // 更新产品状态
      updatedProduct = product.markOutOfStock()
      
      // 保存产品
      savedProduct <- EitherT.right[String](
        productRepository.save(updatedProduct)
      )
      
      // 发布事件
      _ = domainEventPublisher.publish(
        ProductOutOfStock(
          eventId = java.util.UUID.randomUUID().toString,
          timestamp = java.time.LocalDateTime.now(),
          aggregateId = productId.value,
          productId = productId
        )
      )
      
    } yield savedProduct
    
    result.value
  }
}

// 4. 邮件服务
trait EmailService {
  def sendWelcomeEmail(email: Email): Unit
  def sendOrderConfirmationEmail(customer: Customer, order: Order): Unit
  def sendOrderShippedEmail(customer: Customer, order: Order): Unit
}

// 简单内存实现
class InMemoryEmailService extends EmailService {
  private val sentEmails = scala.collection.mutable.ListBuffer.empty[String]
  
  def sendWelcomeEmail(email: Email): Unit = {
    val message = s"Welcome email sent to: ${email.value}"
    sentEmails += message
    println(message)
  }
  
  def sendOrderConfirmationEmail(customer: Customer, order: Order): Unit = {
    val message = s"Order confirmation email sent to ${customer.email.value} for order ${order.id.value}"
    sentEmails += message
    println(message)
  }
  
  def sendOrderShippedEmail(customer: Customer, order: Order): Unit = {
    val message = s"Order shipped email sent to ${customer.email.value} for order ${order.id.value}"
    sentEmails += message
    println(message)
  }
  
  def getSentEmails: List[String] = sentEmails.toList
  def clear(): Unit = sentEmails.clear()
}
```

### 16.3.2 领域服务

```scala
// 领域服务实现

package domain.service

import domain.model._
import domain.aggregate._
import domain.types._
import cats.data.EitherT
import cats.implicits._

// 1. 定价服务
class PricingService {
  
  // 计算订单总额
  def calculateOrderTotal(orderLines: List[OrderLine]): Either[String, MoneyAmount] = {
    orderLines.traverse(_.total).flatMap { totals =>
      totals.reduceOption(_ + _).getOrElse(
        Right(MoneyAmountImpl(0, CurrencyCode("USD")))
      )
    }
  }
  
  // 计算含税价格
  def calculatePriceWithTax(price: MoneyAmount, taxRate: Percentage): Either[String, MoneyAmount] = {
    val taxAmount = price.amount * taxRate.asDecimal
    price + MoneyAmountImpl(taxAmount, price.currency)
  }
  
  // 应用折扣
  def applyDiscount(price: MoneyAmount, discountPercentage: Percentage): Either[String, MoneyAmount] = {
    val discountAmount = price.amount * discountPercentage.asDecimal
    price - MoneyAmountImpl(discountAmount, price.currency)
  }
  
  // 批量折扣计算
  def calculateBulkDiscount(
    basePrice: MoneyAmount,
    quantity: Int,
    discountRules: List[DiscountRule]
  ): Either[String, MoneyAmount] = {
    val applicableRules = discountRules.filter(_.isApplicable(quantity))
    
    if (applicableRules.isEmpty) {
      Right(basePrice)
    } else {
      val maxDiscount = applicableRules.map(_.discountPercentage).maxBy(_.value)
      applyDiscount(basePrice, maxDiscount)
    }
  }
}

// 2. 折扣规则
case class DiscountRule(
  minQuantity: Int,
  discountPercentage: Percentage
) {
  def isApplicable(quantity: Int): Boolean = quantity >= minQuantity
}

object DiscountRule {
  // 创建折扣规则
  def create(minQuantity: Int, discountPercentage: BigDecimal): Either[String, DiscountRule] = {
    for {
      validMinQuantity <- PositiveInt.fromInt(minQuantity)
      validPercentage <- Percentage.fromBigDecimal(discountPercentage)
    } yield DiscountRule(validMinQuantity.value, validPercentage)
  }
  
  // 预定义折扣规则
  val standardRules: List[DiscountRule] = List(
    DiscountRule(5, PercentageImpl(5)),   // 5件5%折扣
    DiscountRule(10, PercentageImpl(10)), // 10件10%折扣
    DiscountRule(20, PercentageImpl(15)), // 20件15%折扣
  )
}

// 3. 库存服务
class InventoryService {
  
  // 检查产品库存
  def checkStock(productId: ProductId, quantity: Int): Future[Either[String, Boolean]] = {
    // 在实际应用中，这会查询库存数据库
    Future.successful(Right(true)) // 简化实现
  }
  
  // 预留库存
  def reserveStock(
    productId: ProductId,
    quantity: Int,
    orderId: OrderId
  ): Future[Either[String, ReservationId]] = {
    // 在实际应用中，这会在库存系统中预留库存
    Future.successful(Right(ReservationId(java.util.UUID.randomUUID().toString)))
  }
  
  // 释放预留库存
  def releaseReservation(reservationId: ReservationId): Future[Either[String, Unit]] = {
    // 在实际应用中，这会释放预留的库存
    Future.successful(Right(()))
  }
  
  // 确认库存扣减
  def confirmReservation(reservationId: ReservationId): Future[Either[String, Unit]] = {
    // 在实际应用中，这会永久扣减库存
    Future.successful(Right(()))
  }
}

case class ReservationId(value: String) extends AnyVal

// 4. 推荐服务
class RecommendationService(
  productRepository: ProductRepository,
  orderRepository: OrderRepository
) {
  
  // 基于客户订单历史推荐产品
  def recommendProductsForCustomer(customerId: CustomerId, limit: Int): Future[Either[String, List[Product]]] = {
    for {
      orders <- orderRepository.findByCustomerId(customerId)
      productIds = orders.flatMap(_.orderLines.map(_.productId)).distinct
      recommendedProducts <- getRelatedProducts(productIds, limit)
    } yield recommendedProducts
  }
  
  // 获取相关产品
  def getRelatedProducts(productIds: List[ProductId], limit: Int): Future[Either[String, List[Product]]] = {
    // 在实际应用中，这会使用更复杂的算法
    Future.successful(Right(List.empty)) // 简化实现
  }
  
  // 基于产品推荐相关产品
  def getRelatedProducts(productId: ProductId, limit: Int): Future[Either[String, List[Product]]] = {
    // 在实际应用中，这会使用产品属性、分类等来计算相似性
    Future.successful(Right(List.empty)) // 简化实现
  }
}

// 5. 支付服务
class PaymentService {
  
  // 处理支付
  def processPayment(
    orderId: OrderId,
    amount: MoneyAmount,
    paymentMethod: PaymentMethod
  ): Future[Either[String, PaymentResult]] = {
    // 在实际应用中，这会调用支付网关
    Future.successful(Right(PaymentSuccess(PaymentId(java.util.UUID.randomUUID().toString))))
  }
  
  // 退款
  def processRefund(
    paymentId: PaymentId,
    amount: MoneyAmount,
    reason: String
  ): Future[Either[String, RefundResult]] = {
    // 在实际应用中，这会调用支付网关
    Future.successful(Right(RefundSuccess(RefundId(java.util.UUID.randomUUID().toString))))
  }
}

// 6. 支付相关类型
sealed trait PaymentMethod
object PaymentMethod {
  case class CreditCard(number: String, expiry: String, cvv: String) extends PaymentMethod
  case class PayPal(email: Email) extends PaymentMethod
  case class BankTransfer(iban: String, accountHolder: String) extends PaymentMethod
}

sealed trait PaymentResult
object PaymentResult {
  case class PaymentSuccess(paymentId: PaymentId) extends PaymentResult
  case class PaymentFailure(error: String) extends PaymentResult
}

case class PaymentId(value: String) extends AnyVal

sealed trait RefundResult
object RefundResult {
  case class RefundSuccess(refundId: RefundId) extends RefundResult
  case class RefundFailure(error: String) extends RefundResult
}

case class RefundId(value: String) extends AnyVal

// 7. 发货服务
class ShippingService {
  
  // 计算运费
  def calculateShippingFee(
    address: Address,
    orderLines: List[OrderLine],
    shippingMethod: ShippingMethod
  ): Either[String, MoneyAmount] = {
    // 简化实现，实际中会更复杂
    val baseFee = shippingMethod match {
      case StandardShipping => MoneyAmountImpl(BigDecimal(5.99), CurrencyCode("USD"))
      case ExpressShipping => MoneyAmountImpl(BigDecimal(12.99), CurrencyCode("USD"))
      case InternationalShipping => MoneyAmountImpl(BigDecimal(25.99), CurrencyCode("USD"))
    }
    
    Right(baseFee)
  }
  
  // 创建发货
  def createShipment(
    orderId: OrderId,
    address: Address,
    shippingMethod: ShippingMethod
  ): Future[Either[String, Shipment]] = {
    // 在实际应用中，这会调用物流API
    Future.successful(Right(Shipment(
      id = ShipmentId(java.util.UUID.randomUUID().toString),
      orderId = orderId,
      address = address,
      shippingMethod = shippingMethod,
      status = ShipmentStatus.Preparing,
      trackingNumber = None
    )))
  }
  
  // 跟踪发货
  def trackShipment(shipmentId: ShipmentId): Future[Either[String, ShipmentTracking]] = {
    // 在实际应用中，这会调用物流API
    Future.successful(Right(ShipmentTracking(
      shipmentId = shipmentId,
      status = ShipmentStatus.InTransit,
      estimatedDelivery = java.time.LocalDate.now().plusDays(3),
      events = List.empty
    )))
  }
}

// 8. 发货相关类型
sealed trait ShippingMethod
object ShippingMethod {
  case object StandardShipping extends ShippingMethod
  case object ExpressShipping extends ShippingMethod
  case object InternationalShipping extends ShippingMethod
}

case class Shipment(
  id: ShipmentId,
  orderId: OrderId,
  address: Address,
  shippingMethod: ShippingMethod,
  status: ShipmentStatus,
  trackingNumber: Option[String]
)

case class ShipmentId(value: String) extends AnyVal

sealed trait ShipmentStatus
object ShipmentStatus {
  case object Preparing extends ShipmentStatus
  case object InTransit extends ShipmentStatus
  case object Delivered extends ShipmentStatus
  case object Failed extends ShipmentStatus
}

case class ShipmentTracking(
  shipmentId: ShipmentId,
  status: ShipmentStatus,
  estimatedDelivery: java.time.LocalDate,
  events: List[ShippingEvent]
)

case class ShippingEvent(
  timestamp: java.time.LocalDateTime,
  status: ShipmentStatus,
  location: String,
  description: String
)
```

## 16.4 事件溯源与CQRS

### 16.4.1 事件溯源

```scala
// 事件溯源实现

package eventsourcing

import java.time.LocalDateTime
import java.util.UUID

// 1. 事件基础
trait Event {
  def eventId: String
  def aggregateId: String
  def timestamp: LocalDateTime
  def version: Int
}

// 2. 聚合基础
trait Aggregate {
  type Id <: AnyVal
  type State <: AnyRef
  type Command <: AnyRef
  
  def id: Id
  def state: State
  def version: Int
  
  def process(command: Command): Either[String, List[Event]]
  def apply(event: Event): Aggregate
}

// 3. 事件存储
trait EventStore[E <: Event] {
  def save(aggregateId: String, events: List[E], expectedVersion: Int): Future[Either[String, Unit]]
  def getEvents(aggregateId: String): Future[Either[String, List[E]]]
  def getEvents(aggregateId: String, fromVersion: Int): Future[Either[String, List[E]]]
}

// 4. 购物车相关事件
case class ShoppingCartId(value: String) extends AnyVal

sealed trait ShoppingCartEvent extends Event

case class ShoppingCartCreated(
  eventId: String,
  aggregateId: String,
  timestamp: LocalDateTime,
  version: Int,
  cartId: ShoppingCartId,
  customerId: CustomerId
) extends ShoppingCartEvent

case class ItemAddedToCart(
  eventId: String,
  aggregateId: String,
  timestamp: LocalDateTime,
  version: Int,
  cartId: ShoppingCartId,
  productId: ProductId,
  productName: String,
  unitPrice: MoneyAmount,
  quantity: PositiveInt
) extends ShoppingCartEvent

case class ItemRemovedFromCart(
  eventId: String,
  aggregateId: String,
  timestamp: LocalDateTime,
  version: Int,
  cartId: ShoppingCartId,
  productId: ProductId
) extends ShoppingCartEvent

case class ItemQuantityUpdated(
  eventId: String,
  aggregateId: String,
  timestamp: LocalDateTime,
  version: Int,
  cartId: ShoppingCartId,
  productId: ProductId,
  newQuantity: PositiveInt
) extends ShoppingCartEvent

case class CartCheckedOut(
  eventId: String,
  aggregateId: String,
  timestamp: LocalDateTime,
  version: Int,
  cartId: ShoppingCartId,
  checkoutDate: java.time.LocalDate,
  totalAmount: MoneyAmount
) extends ShoppingCartEvent

case class CartAbandoned(
  eventId: String,
  aggregateId: String,
  timestamp: LocalDateTime,
  version: Int,
  cartId: ShoppingCartId,
  reason: String
) extends ShoppingCartEvent

// 5. 购物车相关命令
sealed trait ShoppingCartCommand

case class CreateShoppingCart(
  cartId: ShoppingCartId,
  customerId: CustomerId
) extends ShoppingCartCommand

case class AddItemToCart(
  cartId: ShoppingCartId,
  productId: ProductId,
  productName: String,
  unitPrice: MoneyAmount,
  quantity: PositiveInt
) extends ShoppingCartCommand

case class RemoveItemFromCart(
  cartId: ShoppingCartId,
  productId: ProductId
) extends ShoppingCartCommand

case class UpdateItemQuantity(
  cartId: ShoppingCartId,
  productId: ProductId,
  newQuantity: PositiveInt
) extends ShoppingCartCommand

case class CheckoutCart(
  cartId: ShoppingCartId
) extends ShoppingCartCommand

case class AbandonCart(
  cartId: ShoppingCartId,
  reason: String
) extends ShoppingCartCommand

// 6. 购物车状态
case class ShoppingCartItem(
  productId: ProductId,
  productName: String,
  unitPrice: MoneyAmount,
  quantity: PositiveInt
) {
  def total: MoneyAmount = unitPrice * quantity.value
}

sealed trait ShoppingCartStatus
object ShoppingCartStatus {
  case object Active extends ShoppingCartStatus
  case object CheckedOut extends ShoppingCartStatus
  case object Abandoned extends ShoppingCartStatus
}

case class ShoppingCartState(
  id: ShoppingCartId,
  customerId: CustomerId,
  status: ShoppingCartStatus,
  items: List[ShoppingCartItem],
  createdDate: LocalDateTime,
  lastModifiedDate: LocalDateTime
)

// 7. 购物车聚合
class ShoppingCart(
  val id: ShoppingCartId,
  val state: ShoppingCartState,
  val version: Int
) extends Aggregate {
  
  type Id = ShoppingCartId
  type State = ShoppingCartState
  type Command = ShoppingCartCommand
  
  // 处理命令
  def process(command: ShoppingCartCommand): Either[String, List[ShoppingCartEvent]] = {
    command match {
      case CreateShoppingCart(cartId, customerId) =>
        if (state.status != ShoppingCartStatus.Active) {
          Left(s"Cannot create cart that is already in ${state.status} state")
        } else {
          Right(List(
            ShoppingCartCreated(
              eventId = UUID.randomUUID().toString,
              aggregateId = id.value,
              timestamp = LocalDateTime.now(),
              version = version + 1,
              cartId = cartId,
              customerId = customerId
            )
          ))
        }
        
      case AddItemToCart(cartId, productId, productName, unitPrice, quantity) =>
        if (state.status != ShoppingCartStatus.Active) {
          Left(s"Cannot add item to cart in ${state.status} state")
        } else {
          Right(List(
            ItemAddedToCart(
              eventId = UUID.randomUUID().toString,
              aggregateId = id.value,
              timestamp = LocalDateTime.now(),
              version = version + 1,
              cartId = cartId,
              productId = productId,
              productName = productName,
              unitPrice = unitPrice,
              quantity = quantity
            )
          ))
        }
        
      case RemoveItemFromCart(cartId, productId) =>
        if (state.status != ShoppingCartStatus.Active) {
          Left(s"Cannot remove item from cart in ${state.status} state")
        } else if (!state.items.exists(_.productId == productId)) {
          Left(s"Item $productId not found in cart")
        } else {
          Right(List(
            ItemRemovedFromCart(
              eventId = UUID.randomUUID().toString,
              aggregateId = id.value,
              timestamp = LocalDateTime.now(),
              version = version + 1,
              cartId = cartId,
              productId = productId
            )
          ))
        }
        
      case UpdateItemQuantity(cartId, productId, newQuantity) =>
        if (state.status != ShoppingCartStatus.Active) {
          Left(s"Cannot update item quantity in cart in ${state.status} state")
        } else if (!state.items.exists(_.productId == productId)) {
          Left(s"Item $productId not found in cart")
        } else if (newQuantity.value <= 0) {
          Left("Quantity must be positive")
        } else {
          Right(List(
            ItemQuantityUpdated(
              eventId = UUID.randomUUID().toString,
              aggregateId = id.value,
              timestamp = LocalDateTime.now(),
              version = version + 1,
              cartId = cartId,
              productId = productId,
              newQuantity = newQuantity
            )
          ))
        }
        
      case CheckoutCart(cartId) =>
        if (state.status != ShoppingCartStatus.Active) {
          Left(s"Cannot checkout cart in ${state.status} state")
        } else if (state.items.isEmpty) {
          Left("Cannot checkout empty cart")
        } else {
          val totalAmount = state.items.map(_.total).foldLeft(MoneyAmount(BigDecimal(0), CurrencyCode("USD")))(_ + _)
          
          Right(List(
            CartCheckedOut(
              eventId = UUID.randomUUID().toString,
              aggregateId = id.value,
              timestamp = LocalDateTime.now(),
              version = version + 1,
              cartId = cartId,
              checkoutDate = java.time.LocalDate.now(),
              totalAmount = totalAmount
            )
          ))
        }
        
      case AbandonCart(cartId, reason) =>
        if (state.status != ShoppingCartStatus.Active) {
          Left(s"Cannot abandon cart in ${state.status} state")
        } else {
          Right(List(
            CartAbandoned(
              eventId = UUID.randomUUID().toString,
              aggregateId = id.value,
              timestamp = LocalDateTime.now(),
              version = version + 1,
              cartId = cartId,
              reason = reason
            )
          ))
        }
    }
  }
  
  // 应用事件
  def apply(event: ShoppingCartEvent): ShoppingCart = {
    event match {
      case ShoppingCartCreated(_, _, _, _, cartId, customerId) =>
        val now = LocalDateTime.now()
        new ShoppingCart(
          id = cartId,
          state = ShoppingCartState(
            id = cartId,
            customerId = customerId,
            status = ShoppingCartStatus.Active,
            items = List.empty,
            createdDate = now,
            lastModifiedDate = now
          ),
          version = event.version
        )
        
      case ItemAddedToCart(_, _, _, _, cartId, productId, productName, unitPrice, quantity) =>
        val existingItem = state.items.find(_.productId == productId)
        val updatedItems = existingItem match {
          case Some(item) =>
            // 更新现有项的数量
            val newQuantity = PositiveInt(item.quantity.value + quantity.value).right.get
            val updatedItem = item.copy(quantity = newQuantity)
            state.items.map {
              case item if item.productId == productId => updatedItem
              case item => item
            }
          case None =>
            // 添加新项
            val newItem = ShoppingCartItem(
              productId = productId,
              productName = productName,
              unitPrice = unitPrice,
              quantity = quantity
            )
            state.items :+ newItem
        }
        
        new ShoppingCart(
          id = id,
          state = state.copy(
            items = updatedItems,
            lastModifiedDate = event.timestamp
          ),
          version = event.version
        )
        
      case ItemRemovedFromCart(_, _, _, _, cartId, productId) =>
        val updatedItems = state.items.filterNot(_.productId == productId)
        
        new ShoppingCart(
          id = id,
          state = state.copy(
            items = updatedItems,
            lastModifiedDate = event.timestamp
          ),
          version = event.version
        )
        
      case ItemQuantityUpdated(_, _, _, _, cartId, productId, newQuantity) =>
        val updatedItems = state.items.map {
          case item if item.productId == productId => item.copy(quantity = newQuantity)
          case item => item
        }
        
        new ShoppingCart(
          id = id,
          state = state.copy(
            items = updatedItems,
            lastModifiedDate = event.timestamp
          ),
          version = event.version
        )
        
      case CartCheckedOut(_, _, _, _, cartId, checkoutDate, totalAmount) =>
        new ShoppingCart(
          id = id,
          state = state.copy(
            status = ShoppingCartStatus.CheckedOut,
            lastModifiedDate = event.timestamp
          ),
          version = event.version
        )
        
      case CartAbandoned(_, _, _, _, cartId, reason) =>
        new ShoppingCart(
          id = id,
          state = state.copy(
            status = ShoppingCartStatus.Abandoned,
            lastModifiedDate = event.timestamp
          ),
          version = event.version
        )
    }
  }
}

// 8. 事件存储实现
class InMemoryEventStore[E <: Event] extends EventStore[E] {
  private val events = scala.collection.mutable.Map.empty[String, List[E]]
  
  def save(aggregateId: String, newEvents: List[E], expectedVersion: Int): Future[Either[String, Unit]] = {
    Future.successful {
      events.get(aggregateId) match {
        case Some(existingEvents) if existingEvents.size != expectedVersion =>
          Left(s"Concurrency conflict: expected version $expectedVersion, but was ${existingEvents.size}")
        case _ =>
          val allEvents = events.getOrElse(aggregateId, List.empty) ++ newEvents
          events(aggregateId) = allEvents
          Right(())
      }
    }
  }
  
  def getEvents(aggregateId: String): Future[Either[String, List[E]]] = {
    Future.successful(Right(events.getOrElse(aggregateId, List.empty)))
  }
  
  def getEvents(aggregateId: String, fromVersion: Int): Future[Either[String, List[E]]] = {
    Future.successful {
      val allEvents = events.getOrElse(aggregateId, List.empty)
      val filteredEvents = allEvents.filter(_.version >= fromVersion)
      Right(filteredEvents)
    }
  }
}

// 9. 购物车仓储
class ShoppingCartRepository(
  eventStore: EventStore[ShoppingCartEvent]
) {
  
  def save(cart: ShoppingCart): Future[Either[String, Unit]] = {
    // 获取当前状态的事件数量
    val expectedVersion = cart.version - cart.state.items.size
    
    // 获取新事件（这里简化实现，实际中应该跟踪哪些事件是新事件）
    eventStore.save(cart.id.value, List.empty, expectedVersion)
  }
  
  def getById(cartId: ShoppingCartId): Future[Either[String, ShoppingCart]] = {
    for {
      events <- eventStore.getEvents(cartId.value)
      cart <- events.foldLeft(Right(new ShoppingCart(
        cartId, 
        ShoppingCartState(cartId, CustomerId(""), ShoppingCartStatus.Active, List.empty, LocalDateTime.now(), LocalDateTime.now()),
        0
      )): Either[String, ShoppingCart]) { (acc, event) =>
        acc.map(cart => cart.apply(event))
      }
    } yield cart
  }
}

// 10. 购物车应用服务
class ShoppingCartApplicationService(
  eventStore: EventStore[ShoppingCartEvent],
  repository: ShoppingCartRepository
)(implicit ec: ExecutionContext) {
  
  private val repository = new ShoppingCartRepository(eventStore)
  
  def createCart(cartId: ShoppingCartId, customerId: CustomerId): Future[Either[String, ShoppingCart]] = {
    for {
      // 创建新购物车
      cart = new ShoppingCart(
        cartId,
        ShoppingCartState(cartId, customerId, ShoppingCartStatus.Active, List.empty, LocalDateTime.now(), LocalDateTime.now()),
        0
      )
      
      // 处理命令
      command = CreateShoppingCart(cartId, customerId)
      events <- cart.process(command)
      
      // 保存事件
      _ <- eventStore.save(cartId.value, events, 0)
      
      // 重建购物车状态
      updatedCart <- repository.getById(cartId)
    } yield updatedCart
  }
  
  def addItemToCart(
    cartId: ShoppingCartId,
    productId: ProductId,
    productName: String,
    unitPrice: MoneyAmount,
    quantity: PositiveInt
  ): Future[Either[String, ShoppingCart]] = {
    for {
      // 获取当前购物车
      cart <- repository.getById(cartId)
      
      // 处理命令
      command = AddItemToCart(cartId, productId, productName, unitPrice, quantity)
      events <- cart.process(command)
      
      // 保存事件
      _ <- eventStore.save(cartId.value, events, cart.version)
      
      // 重建购物车状态
      updatedCart <- repository.getById(cartId)
    } yield updatedCart
  }
  
  def checkoutCart(cartId: ShoppingCartId): Future[Either[String, ShoppingCart]] = {
    for {
      // 获取当前购物车
      cart <- repository.getById(cartId)
      
      // 处理命令
      command = CheckoutCart(cartId)
      events <- cart.process(command)
      
      // 保存事件
      _ <- eventStore.save(cartId.value, events, cart.version)
      
      // 重建购物车状态
      updatedCart <- repository.getById(cartId)
    } yield updatedCart
  }
}
```

### 16.4.2 CQRS（命令查询职责分离）

```scala
// CQRS实现

package cqrs

import java.time.LocalDateTime
import scala.concurrent.{ExecutionContext, Future}

// 1. 命令基类
trait Command {
  def commandId: String
  def aggregateId: String
  def timestamp: LocalDateTime
}

// 2. 查询基类
trait Query[+R] {
  def queryId: String
}

// 3. 命令处理基类
trait CommandHandler[C <: Command] {
  def handle(command: C): Future[Either[String, Unit]]
}

// 4. 查询处理基类
trait QueryHandler[Q <: Query[R], R] {
  def handle(query: Q): Future[Either[String, R]]
}

// 5. 命令总线
trait CommandBus {
  def dispatch[C <: Command](command: C): Future[Either[String, Unit]]
  def register[C <: Command](handler: CommandHandler[C]): Unit
}

// 6. 查询总线
trait QueryBus {
  def ask[Q <: Query[R], R](query: Q): Future[Either[String, R]]
  def register[Q <: Query[R], R](handler: QueryHandler[Q, R]): Unit
}

// 7. 简单内存命令总线实现
class InMemoryCommandBus(implicit ec: ExecutionContext) extends CommandBus {
  private val handlers = scala.collection.mutable.Map.empty[Class[_], CommandHandler[_]]
  
  def dispatch[C <: Command](command: C): Future[Either[String, Unit]] = {
    handlers.get(command.getClass) match {
      case Some(handler) =>
        handler.asInstanceOf[CommandHandler[C]].handle(command)
      case None =>
        Future.successful(Left(s"No handler registered for command: ${command.getClass.getSimpleName}"))
    }
  }
  
  def register[C <: Command](handler: CommandHandler[C]): Unit = {
    // 获取命令类型的实际类，需要反射或类型标记
    // 这里简化实现
  }
}

// 8. 简单内存查询总线实现
class InMemoryQueryBus(implicit ec: ExecutionContext) extends QueryBus {
  private val handlers = scala.collection.mutable.Map.empty[Class[_], QueryHandler[_, _]]
  
  def ask[Q <: Query[R], R](query: Q): Future[Either[String, R]] = {
    handlers.get(query.getClass) match {
      case Some(handler) =>
        handler.asInstanceOf[QueryHandler[Q, R]].handle(query)
      case None =>
        Future.successful(Left(s"No handler registered for query: ${query.getClass.getSimpleName}"))
    }
  }
  
  def register[Q <: Query[R], R](handler: QueryHandler[Q, R]): Unit = {
    // 获取查询类型的实际类，需要反射或类型标记
    // 这里简化实现
  }
}

// 9. 产品命令
case class ProductId(value: String) extends AnyVal

sealed trait ProductCommand extends Command

case class CreateProduct(
  commandId: String,
  aggregateId: String,
  timestamp: LocalDateTime,
  productId: ProductId,
  name: String,
  description: String,
  price: MoneyAmount
) extends ProductCommand

case class UpdateProductPrice(
  commandId: String,
  aggregateId: String,
  timestamp: LocalDateTime,
  productId: ProductId,
  newPrice: MoneyAmount
) extends ProductCommand

case class DiscontinueProduct(
  commandId: String,
  aggregateId: String,
  timestamp: LocalDateTime,
  productId: ProductId
) extends ProductCommand

// 10. 产品查询
sealed trait ProductQuery[R] extends Query[R]

case class GetProductById(
  queryId: String,
  productId: ProductId
) extends ProductQuery[Option[ProductReadModel]]

case class SearchProducts(
  queryId: String,
  name: Option[String] = None,
  category: Option[String] = None,
  minPrice: Option[BigDecimal] = None,
  maxPrice: Option[BigDecimal] = None,
  page: Int = 1,
  pageSize: Int = 10
) extends ProductQuery[PagedResult[ProductReadModel]]

// 11. 产品读模型
case class ProductReadModel(
  id: ProductId,
  name: String,
  description: String,
  price: MoneyAmount,
  status: ProductStatus,
  createdAt: LocalDateTime,
  updatedAt: LocalDateTime
)

case class PagedResult[T](
  items: List[T],
  totalCount: Int,
  page: Int,
  pageSize: Int,
  totalPages: Int
)

// 12. 产品命令处理器
class ProductCommandHandler(
  productRepository: ProductRepository,
  domainEventPublisher: DomainEventPublisher
)(implicit ec: ExecutionContext) extends CommandHandler[ProductCommand] {
  
  def handle(command: ProductCommand): Future[Either[String, Unit]] = {
    command match {
      case CreateProduct(cmdId, aggId, timestamp, productId, name, description, price) =>
        for {
          // 检查产品是否已存在
          existingProduct <- productRepository.findById(productId)
          _ <- existingProduct match {
            case Some(_) => Future.successful(Left(s"Product with ID ${productId.value} already exists"))
            case None =>
              for {
                // 创建产品
                product = Product(productId, name, description, price, ProductStatus.Available)
                
                // 保存产品
                _ <- productRepository.save(product)
                
                // 发布领域事件
                _ = domainEventPublisher.publish(
                  ProductCreated(
                    eventId = java.util.UUID.randomUUID().toString,
                    timestamp = timestamp,
                    aggregateId = aggId,
                    productId = productId,
                    name = name,
                    description = description,
                    priceAmount = price.amount,
                    currency = price.currency.value
                  )
                )
              } yield Right(())
          }
        } yield ()
        
      case UpdateProductPrice(cmdId, aggId, timestamp, productId, newPrice) =>
        for {
          // 获取产品
          product <- productRepository.findById(productId)
          _ <- product match {
            case None => Future.successful(Left(s"Product with ID ${productId.value} not found"))
            case Some(p) if p.status == ProductStatus.Discontinued =>
              Future.successful(Left(s"Cannot update price for discontinued product"))
            case Some(p) =>
              for {
                // 更新产品
                updatedProduct = p.withPrice(newPrice)
                
                // 保存产品
                _ <- productRepository.save(updatedProduct)
                
                // 发布领域事件
                _ = domainEventPublisher.publish(
                  ProductPriceChanged(
                    eventId = java.util.UUID.randomUUID().toString,
                    timestamp = timestamp,
                    aggregateId = aggId,
                    productId = productId,
                    oldPriceAmount = p.price.amount,
                    newPriceAmount = newPrice.amount
                  )
                )
              } yield Right(())
          }
        } yield ()
        
      case DiscontinueProduct(cmdId, aggId, timestamp, productId) =>
        for {
          // 获取产品
          product <- productRepository.findById(productId)
          _ <- product match {
            case None => Future.successful(Left(s"Product with ID ${productId.value} not found"))
            case Some(p) if p.status == ProductStatus.Discontinued =>
              Future.successful(Left(s"Product is already discontinued"))
            case Some(p) =>
              for {
                // 更新产品
                updatedProduct = p.discontinue()
                
                // 保存产品
                _ <- productRepository.save(updatedProduct)
                
                // 发布领域事件
                _ = domainEventPublisher.publish(
                  ProductDiscontinued(
                    eventId = java.util.UUID.randomUUID().toString,
                    timestamp = timestamp,
                    aggregateId = aggId,
                    productId = productId,
                    name = p.name
                  )
                )
              } yield Right(())
          }
        } yield ()
    }
  }
}

// 13. 产品查询处理器
class ProductQueryHandler(
  productReadModelRepository: ProductReadModelRepository
)(implicit ec: ExecutionContext) extends QueryHandler[ProductQuery[_], Any] {
  
  def handle[Q <: ProductQuery[R], R](query: Q): Future[Either[String, R]] = {
    query match {
      case GetProductById(queryId, productId) =>
        productReadModelRepository.findById(productId).map(Right(_))
        
      case SearchProducts(queryId, name, category, minPrice, maxPrice, page, pageSize) =>
        productReadModelRepository.search(name, category, minPrice, maxPrice, page, pageSize).map(Right(_))
    }
  }
}

// 14. 产品读模型仓储
trait ProductReadModelRepository {
  def findById(productId: ProductId): Future[Option[ProductReadModel]]
  def search(
    name: Option[String],
    category: Option[String],
    minPrice: Option[BigDecimal],
    maxPrice: Option[BigDecimal],
    page: Int,
    pageSize: Int
  ): Future[PagedResult[ProductReadModel]]
  def save(product: ProductReadModel): Future[Unit]
}

// 15. 简单内存产品读模型仓储实现
class InMemoryProductReadModelRepository(
  initialProducts: List[ProductReadModel] = List.empty
)(implicit ec: ExecutionContext) extends ProductReadModelRepository {
  
  private val products = scala.collection.mutable.ListBuffer(initialProducts: _*)
  
  def findById(productId: ProductId): Future[Option[ProductReadModel]] = {
    Future.successful(products.find(_.id == productId))
  }
  
  def search(
    name: Option[String],
    category: Option[String],
    minPrice: Option[BigDecimal],
    maxPrice: Option[BigDecimal],
    page: Int,
    pageSize: Int
  ): Future[PagedResult[ProductReadModel]] = {
    var filteredProducts = products.toList
    
    // 应用过滤条件
    name.foreach(n => filteredProducts = filteredProducts.filter(_.name.toLowerCase.contains(n.toLowerCase)))
    category.foreach(c => filteredProducts = filteredProducts.filter(_.description.toLowerCase.contains(c.toLowerCase)))
    minPrice.foreach(p => filteredProducts = filteredProducts.filter(_.price.amount >= p))
    maxPrice.foreach(p => filteredProducts = filteredProducts.filter(_.price.amount <= p))
    
    // 分页
    val totalCount = filteredProducts.size
    val totalPages = math.ceil(totalCount.toDouble / pageSize).toInt
    val startIndex = (page - 1) * pageSize
    val endIndex = Math.min(startIndex + pageSize, totalCount)
    val pagedProducts = if (startIndex < totalCount) filteredProducts.slice(startIndex, endIndex) else List.empty
    
    Future.successful(PagedResult(
      items = pagedProducts,
      totalCount = totalCount,
      page = page,
      pageSize = pageSize,
      totalPages = totalPages
    ))
  }
  
  def save(product: ProductReadModel): Future[Unit] = {
    products.indexWhere(_.id == product.id) match {
      case -1 => products += product
      case index => products.update(index, product)
    }
    Future.successful(())
  }
}

// 16. 事件处理器
trait EventHandler[E <: DomainEvent] {
  def handle(event: E): Future[Unit]
}

// 17. 产品事件处理器
class ProductEventHandler(
  productReadModelRepository: ProductReadModelRepository
)(implicit ec: ExecutionContext) extends EventHandler[ProductEvent] {
  
  def handle(event: ProductEvent): Future[Unit] = {
    event match {
      case ProductCreated(eventId, timestamp, aggregateId, productId, name, description, priceAmount, currency) =>
        val readModel = ProductReadModel(
          id = productId,
          name = name,
          description = description,
          price = MoneyAmount(priceAmount, CurrencyCode(currency)),
          status = ProductStatus.Available,
          createdAt = timestamp,
          updatedAt = timestamp
        )
        productReadModelRepository.save(readModel)
        
      case ProductPriceChanged(eventId, timestamp, aggregateId, productId, oldPriceAmount, newPriceAmount) =>
        for {
          product <- productReadModelRepository.findById(productId)
          _ <- product match {
            case Some(p) =>
              val updatedProduct = p.copy(
                price = MoneyAmount(newPriceAmount, p.price.currency),
                updatedAt = timestamp
              )
              productReadModelRepository.save(updatedProduct)
            case None =>
              Future.successful(())
          }
        } yield ()
        
      case ProductDiscontinued(eventId, timestamp, aggregateId, productId, name) =>
        for {
          product <- productReadModelRepository.findById(productId)
          _ <- product match {
            case Some(p) =>
              val updatedProduct = p.copy(
                status = ProductStatus.Discontinued,
                updatedAt = timestamp
              )
              productReadModelRepository.save(updatedProduct)
            case None =>
              Future.successful(())
          }
        } yield ()
    }
  }
}
```

## 16.5 实战案例

### 16.5.1 银行账户管理系统

```scala
// 银行账户管理系统DDD实现

package banking

import java.time.LocalDateTime
import java.util.UUID
import scala.concurrent.{ExecutionContext, Future}

// 1. 账户相关值对象
case class AccountNumber(value: String) extends AnyVal
case class AccountId(value: String) extends AnyVal

sealed trait AccountType
object AccountType {
  case object Checking extends AccountType
  case object Savings extends AccountType
}

case class Money(amount: BigDecimal, currency: String) {
  def +(other: Money): Money = {
    if (currency != other.currency) {
      throw new IllegalArgumentException("Cannot add money with different currencies")
    }
    Money(amount + other.amount, currency)
  }
  
  def -(other: Money): Money = {
    if (currency != other.currency) {
      throw new IllegalArgumentException("Cannot subtract money with different currencies")
    }
    Money(amount - other.amount, currency)
  }
  
  def >(other: Money): Boolean = {
    if (currency != other.currency) {
      throw new IllegalArgumentException("Cannot compare money with different currencies")
    }
    amount > other.amount
  }
  
  def >=(other: Money): Boolean = this > other || this == other
  
  def ==(other: Money): Boolean = {
    if (currency != other.currency) {
      throw new IllegalArgumentException("Cannot compare money with different currencies")
    }
    amount == other.amount
  }
  
  def isPositive: Boolean = amount > 0
  def isNonNegative: Boolean = amount >= 0
}

// 2. 银行账户聚合根
class BankAccount(
  val id: AccountId,
  val accountNumber: AccountNumber,
  val ownerName: String,
  val accountType: AccountType,
  private var balance: Money,
  private var status: AccountStatus,
  val openedDate: LocalDateTime,
  private var lastModifiedDate: LocalDateTime,
  val eventPublisher: DomainEventPublisher
) extends Entity[AccountId] {
  
  // 存款
  def deposit(amount: Money, description: Option[String] = None): Either[String, Unit] = {
    if (status != AccountStatus.Active) {
      Left(s"Cannot deposit to account in ${status} status")
    } else if (!amount.isPositive) {
      Left("Deposit amount must be positive")
    } else {
      val oldBalance = balance
      balance = balance + amount
      lastModifiedDate = LocalDateTime.now()
      
      // 发布事件
      eventPublisher.publish(
        MoneyDeposited(
          eventId = UUID.randomUUID().toString,
          timestamp = LocalDateTime.now(),
          aggregateId = id.value,
          accountId = id,
          amount = amount,
          balanceAfter = balance,
          description = description.getOrElse("Deposit")
        )
      )
      
      Right(())
    }
  }
  
  // 取款
  def withdraw(amount: Money, description: Option[String] = None): Either[String, Unit] = {
    if (status != AccountStatus.Active) {
      Left(s"Cannot withdraw from account in ${status} status")
    } else if (!amount.isPositive) {
      Left("Withdrawal amount must be positive")
    } else if (amount > balance) {
      Left("Insufficient funds")
    } else {
      val oldBalance = balance
      balance = balance - amount
      lastModifiedDate = LocalDateTime.now()
      
      // 发布事件
      eventPublisher.publish(
        MoneyWithdrawn(
          eventId = UUID.randomUUID().toString,
          timestamp = LocalDateTime.now(),
          aggregateId = id.value,
          accountId = id,
          amount = amount,
          balanceAfter = balance,
          description = description.getOrElse("Withdrawal")
        )
      )
      
      Right(())
    }
  }
  
  // 转账
  def transferTo(
    targetAccount: BankAccount,
    amount: Money,
    description: Option[String] = None
  ): Either[String, Unit] = {
    if (status != AccountStatus.Active) {
      Left(s"Cannot transfer from account in ${status} status")
    } else if (targetAccount.status != AccountStatus.Active) {
      Left(s"Cannot transfer to account in ${targetAccount.status} status")
    } else if (amount > balance) {
      Left("Insufficient funds for transfer")
    } else {
      // 执行转账
      withdraw(amount, description.map(d => s"Transfer to ${targetAccount.accountNumber.value}: $d"))
      targetAccount.receiveTransferFrom(this, amount, description.map(d => s"Transfer from ${accountNumber.value}: $d"))
      
      // 发布事件
      eventPublisher.publish(
        MoneyTransferred(
          eventId = UUID.randomUUID().toString,
          timestamp = LocalDateTime.now(),
          aggregateId = id.value,
          fromAccountId = id,
          toAccountId = targetAccount.id,
          amount = amount,
          description = description.getOrElse("Transfer")
        )
      )
      
      Right(())
    }
  }
  
  // 接收转账（内部方法）
  private def receiveTransferFrom(
    fromAccount: BankAccount,
    amount: Money,
    description: Option[String]
  ): Either[String, Unit] = {
    if (status != AccountStatus.Active) {
      Left(s"Cannot receive transfer to account in ${status} status")
    } else {
      val oldBalance = balance
      balance = balance + amount
      lastModifiedDate = LocalDateTime.now()
      
      Right(())
    }
  }
  
  // 冻结账户
  def freeze(reason: String): Either[String, Unit] = {
    if (status != AccountStatus.Active) {
      Left(s"Cannot freeze account in ${status} status")
    } else {
      val oldStatus = status
      status = AccountStatus.Frozen
      lastModifiedDate = LocalDateTime.now()
      
      // 发布事件
      eventPublisher.publish(
        AccountFrozen(
          eventId = UUID.randomUUID().toString,
          timestamp = LocalDateTime.now(),
          aggregateId = id.value,
          accountId = id,
          reason = reason
        )
      )
      
      Right(())
    }
  }
  
  // 解冻账户
  def unfreeze(): Either[String, Unit] = {
    if (status != AccountStatus.Frozen) {
      Left(s"Cannot unfreeze account in ${status} status")
    } else {
      val oldStatus = status
      status = AccountStatus.Active
      lastModifiedDate = LocalDateTime.now()
      
      // 发布事件
      eventPublisher.publish(
        AccountUnfrozen(
          eventId = UUID.randomUUID().toString,
          timestamp = LocalDateTime.now(),
          aggregateId = id.value,
          accountId = id
        )
      )
      
      Right(())
    }
  }
  
  // 关闭账户
  def close(): Either[String, Unit] = {
    if (status != AccountStatus.Active) {
      Left(s"Cannot close account in ${status} status")
    } else if (!balance.isNonNegative) {
      Left("Cannot close account with negative balance")
    } else {
      val oldStatus = status
      status = AccountStatus.Closed
      lastModifiedDate = LocalDateTime.now()
      
      // 发布事件
      eventPublisher.publish(
        AccountClosed(
          eventId = UUID.randomUUID().toString,
          timestamp = LocalDateTime.now(),
          aggregateId = id.value,
          accountId = id,
          finalBalance = balance
        )
      )
      
      Right(())
    }
  }
  
  // 获取余额
  def getBalance: Money = balance
  
  // 获取状态
  def getStatus: AccountStatus = status
}

// 3. 账户状态
sealed trait AccountStatus
object AccountStatus {
  case object Active extends AccountStatus
  case object Frozen extends AccountStatus
  case object Closed extends AccountStatus
}

// 4. 账户相关领域事件
case class AccountOpened(
  eventId: String,
  timestamp: LocalDateTime,
  aggregateId: String,
  accountId: AccountId,
  accountNumber: AccountNumber,
  ownerName: String,
  accountType: AccountType,
  initialBalance: Money
) extends DomainEvent

case class MoneyDeposited(
  eventId: String,
  timestamp: LocalDateTime,
  aggregateId: String,
  accountId: AccountId,
  amount: Money,
  balanceAfter: Money,
  description: String
) extends DomainEvent

case class MoneyWithdrawn(
  eventId: String,
  timestamp: LocalDateTime,
  aggregateId: String,
  accountId: AccountId,
  amount: Money,
  balanceAfter: Money,
  description: String
) extends DomainEvent

case class MoneyTransferred(
  eventId: String,
  timestamp: LocalDateTime,
  aggregateId: String,
  fromAccountId: AccountId,
  toAccountId: AccountId,
  amount: Money,
  description: String
) extends DomainEvent

case class AccountFrozen(
  eventId: String,
  timestamp: LocalDateTime,
  aggregateId: String,
  accountId: AccountId,
  reason: String
) extends DomainEvent

case class AccountUnfrozen(
  eventId: String,
  timestamp: LocalDateTime,
  aggregateId: String,
  accountId: AccountId
) extends DomainEvent

case class AccountClosed(
  eventId: String,
  timestamp: LocalDateTime,
  aggregateId: String,
  accountId: AccountId,
  finalBalance: Money
) extends DomainEvent

// 5. 银行账户仓储
trait BankAccountRepository {
  def findById(accountId: AccountId): Future[Option[BankAccount]]
  def findByAccountNumber(accountNumber: AccountNumber): Future[Option[BankAccount]]
  def findByOwnerName(ownerName: String): Future[List[BankAccount]]
  def save(account: BankAccount): Future[BankAccount]
}

// 6. 银行账户应用服务
class BankAccountApplicationService(
  accountRepository: BankAccountRepository,
  domainEventPublisher: DomainEventPublisher
)(implicit ec: ExecutionContext) {
  
  // 开设账户
  def openAccount(
    ownerName: String,
    accountType: AccountType,
    initialBalance: Money
  ): Future[Either[String, BankAccount]] = {
    for {
      // 生成账户号码
      accountNumber = AccountNumber(generateAccountNumber())
      accountId = AccountId(UUID.randomUUID().toString)
      
      // 创建账户
      now = LocalDateTime.now()
      account = new BankAccount(
        id = accountId,
        accountNumber = accountNumber,
        ownerName = ownerName,
        accountType = accountType,
        balance = initialBalance,
        status = AccountStatus.Active,
        openedDate = now,
        lastModifiedDate = now,
        eventPublisher = domainEventPublisher
      )
      
      // 如果初始余额不为零，存款
      _ <- if (initialBalance.amount > 0) {
        account.deposit(initialBalance, Some("Initial deposit"))
      } else {
        Future.successful(Right(()))
      }
      
      // 保存账户
      savedAccount <- accountRepository.save(account)
      
      // 发布事件
      _ = domainEventPublisher.publish(
        AccountOpened(
          eventId = UUID.randomUUID().toString,
          timestamp = LocalDateTime.now(),
          aggregateId = accountId.value,
          accountId = accountId,
          accountNumber = accountNumber,
          ownerName = ownerName,
          accountType = accountType,
          initialBalance = initialBalance
        )
      )
    } yield savedAccount
  }
  
  // 存款
  def deposit(
    accountId: AccountId,
    amount: Money,
    description: Option[String] = None
  ): Future[Either[String, BankAccount]] = {
    for {
      account <- accountRepository.findById(accountId).map {
        case None => Left(s"Account with ID ${accountId.value} not found")
        case Some(acc) => Right(acc)
      }
      
      _ <- account.fold(
        error => Future.successful(Left(error)),
        acc => Future.successful(acc.deposit(amount, description))
      )
      
      updatedAccount <- account.fold(
        error => Future.successful(Left(error)),
        acc => accountRepository.save(acc)
      )
    } yield updatedAccount
  }
  
  // 取款
  def withdraw(
    accountId: AccountId,
    amount: Money,
    description: Option[String] = None
  ): Future[Either[String, BankAccount]] = {
    for {
      account <- accountRepository.findById(accountId).map {
        case None => Left(s"Account with ID ${accountId.value} not found")
        case Some(acc) => Right(acc)
      }
      
      _ <- account.fold(
        error => Future.successful(Left(error)),
        acc => Future.successful(acc.withdraw(amount, description))
      )
      
      updatedAccount <- account.fold(
        error => Future.successful(Left(error)),
        acc => accountRepository.save(acc)
      )
    } yield updatedAccount
  }
  
  // 转账
  def transfer(
    fromAccountId: AccountId,
    toAccountId: AccountId,
    amount: Money,
    description: Option[String] = None
  ): Future[Either[String, (BankAccount, BankAccount)]] = {
    for {
      fromAccount <- accountRepository.findById(fromAccountId).map {
        case None => Left(s"Source account with ID ${fromAccountId.value} not found")
        case Some(acc) => Right(acc)
      }
      
      toAccount <- accountRepository.findById(toAccountId).map {
        case None => Left(s"Destination account with ID ${toAccountId.value} not found")
        case Some(acc) => Right(acc)
      }
      
      result <- fromAccount.fold(
        error => Future.successful(Left(error)),
        from => toAccount.fold(
          error => Future.successful(Left(error)),
          to => Future.successful(from.transferTo(to, amount, description))
        )
      )
      
      savedAccounts <- result.fold(
        error => Future.successful(Left(error)),
        _ => for {
          savedFrom <- accountRepository.save(fromAccount.get)
          savedTo <- accountRepository.save(toAccount.get)
        } yield (savedFrom, savedTo)
      )
    } yield savedAccounts
  }
  
  // 生成账户号码（简化实现）
  private def generateAccountNumber(): String = {
    s"${(100000000 + scala.util.Random.nextInt(900000000)).toString}"
  }
}

// 7. 银行账户查询服务
class BankAccountQueryService(
  accountRepository: BankAccountRepository
)(implicit ec: ExecutionContext) {
  
  // 获取账户详情
  def getAccountDetails(accountId: AccountId): Future[Option[AccountDetails]] = {
    accountRepository.findById(accountId).map(_.map(account =>
      AccountDetails(
        id = account.id,
        accountNumber = account.accountNumber,
        ownerName = account.ownerName,
        accountType = account.accountType,
        balance = account.getBalance,
        status = account.getStatus,
        openedDate = account.openedDate,
        lastModifiedDate = account.lastModifiedDate
      )
    ))
  }
  
  // 获取账户余额
  def getAccountBalance(accountId: AccountId): Future[Either[String, Money]] = {
    accountRepository.findById(accountId).map {
      case None => Left(s"Account with ID ${accountId.value} not found")
      case Some(account) => Right(account.getBalance)
    }
  }
  
  // 按客户名称查找账户
  def findAccountsByOwnerName(ownerName: String): Future[List[AccountSummary]] = {
    accountRepository.findByOwnerName(ownerName).map(accounts =>
      accounts.map(account =>
        AccountSummary(
          id = account.id,
          accountNumber = account.accountNumber,
          ownerName = account.ownerName,
          accountType = account.accountType,
          balance = account.getBalance,
          status = account.getStatus
        )
      )
    )
  }
}

// 8. 查询数据传输对象（DTO）
case class AccountDetails(
  id: AccountId,
  accountNumber: AccountNumber,
  ownerName: String,
  accountType: AccountType,
  balance: Money,
  status: AccountStatus,
  openedDate: LocalDateTime,
  lastModifiedDate: LocalDateTime
)

case class AccountSummary(
  id: AccountId,
  accountNumber: AccountNumber,
  ownerName: String,
  accountType: AccountType,
  balance: Money,
  status: AccountStatus
)

// 9. 领域服务
class BankingRulesService {
  // 检查转账限制
  def checkTransferLimits(
    fromAccount: BankAccount,
    toAccount: BankAccount,
    amount: Money
  ): Either[String, Unit] = {
    // 简化示例：同一人账户间转账不受限制
    if (fromAccount.ownerName == toAccount.ownerName) {
      Right(())
    } else {
      // 检查日转账限制
      val dailyLimit = Money(10000, "USD")
      if (amount > dailyLimit) {
        Left(s"Transfer amount exceeds daily limit of ${dailyLimit.amount}")
      } else {
        Right(())
      }
    }
  }
  
  // 检查账户是否符合某些业务规则
  def validateAccount(account: BankAccount): Either[String, Unit] = {
    if (account.accountType == AccountType.Savings && account.getBalance.amount < 100) {
      Left("Savings account must maintain minimum balance of 100")
    } else {
      Right(())
    }
  }
}
```

本章详细介绍了领域驱动设计(DDD)与Scala的结合使用，包括DDD基础概念、领域建模与类型系统、应用服务与领域服务、事件溯源与CQRS，以及一个银行账户管理系统的实战案例。通过这些技术和模式，开发者可以构建出更加健壮、可维护和可扩展的业务应用程序。Scala的强类型系统和函数式特性非常适合实现DDD的各种概念和模式。