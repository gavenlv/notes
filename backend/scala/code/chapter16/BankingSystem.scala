// 银行账户管理系统DDD实现

import java.time.LocalDateTime
import java.util.UUID
import scala.concurrent.{ExecutionContext, Future}
import scala.util.{Success, Failure}

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
  
  override def toString: String = s"$amount $currency"
}

// 2. 实体基类
trait Entity[ID] {
  def id: ID
}

// 3. 领域事件基类
trait DomainEvent {
  def eventId: String
  def timestamp: LocalDateTime
  def aggregateId: String
}

// 4. 领域事件发布接口
trait DomainEventPublisher {
  def publish(event: DomainEvent): Unit
  def publish(events: List[DomainEvent]): Unit
}

// 5. 简单内存事件发布器
class InMemoryDomainEventPublisher extends DomainEventPublisher {
  private val publishedEvents = scala.collection.mutable.ListBuffer.empty[DomainEvent]
  
  def publish(event: DomainEvent): Unit = publishedEvents += event
  def publish(events: List[DomainEvent]): Unit = publishedEvents ++= events
  
  def getPublishedEvents: List[DomainEvent] = publishedEvents.toList
  def clear(): Unit = publishedEvents.clear()
}

// 6. 账户状态
sealed trait AccountStatus
object AccountStatus {
  case object Active extends AccountStatus
  case object Frozen extends AccountStatus
  case object Closed extends AccountStatus
}

// 7. 银行账户聚合根
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
      val withdrawalResult = withdraw(amount, description.map(d => s"Transfer to ${targetAccount.accountNumber.value}: $d"))
      
      if (withdrawalResult.isLeft) {
        withdrawalResult
      } else {
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
  
  // 获取最后修改时间
  def getLastModifiedDate: LocalDateTime = lastModifiedDate
}

// 8. 账户相关领域事件
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

// 9. 银行账户仓储
trait BankAccountRepository {
  def findById(accountId: AccountId): Future[Option[BankAccount]]
  def findByAccountNumber(accountNumber: AccountNumber): Future[Option[BankAccount]]
  def findByOwnerName(ownerName: String): Future[List[BankAccount]]
  def save(account: BankAccount): Future[BankAccount]
}

// 10. 简单内存仓储实现
class InMemoryBankAccountRepository extends BankAccountRepository {
  private val accounts = scala.collection.mutable.Map.empty[AccountId, BankAccount]
  private val accountNumbers = scala.collection.mutable.Map.empty[AccountNumber, AccountId]
  private val ownerNames = scala.collection.mutable.Map.empty[String, scala.collection.mutable.Set[AccountId]]
  
  def findById(accountId: AccountId): Future[Option[BankAccount]] = {
    Future.successful(accounts.get(accountId))
  }
  
  def findByAccountNumber(accountNumber: AccountNumber): Future[Option[BankAccount]] = {
    Future.successful(accountNumbers.get(accountNumber).flatMap(id => accounts.get(id)))
  }
  
  def findByOwnerName(ownerName: String): Future[List[BankAccount]] = {
    val accountIds = ownerNames.getOrElse(ownerName, scala.collection.mutable.Set.empty)
    Future.successful(accountIds.map(accounts).toList)
  }
  
  def save(account: BankAccount): Future[BankAccount] = {
    val isNew = !accounts.contains(account.id)
    
    accounts(account.id) = account
    accountNumbers(account.accountNumber) = account.id
    
    if (isNew) {
      val ownerAccounts = ownerNames.getOrElseUpdate(account.ownerName, scala.collection.mutable.Set.empty)
      ownerAccounts += account.id
    }
    
    Future.successful(account)
  }
  
  def count(): Int = accounts.size
  def getAll(): List[BankAccount] = accounts.values.toList
}

// 11. 银行账户应用服务
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
    Future.successful {
      // 生成账户号码
      val accountNumber = AccountNumber(generateAccountNumber())
      val accountId = AccountId(UUID.randomUUID().toString)
      
      // 创建账户
      val now = LocalDateTime.now()
      val account = new BankAccount(
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
      val depositResult = if (initialBalance.amount > 0) {
        account.deposit(initialBalance, Some("Initial deposit"))
      } else {
        Right(())
      }
      
      depositResult match {
        case Left(error) => Left(error)
        case Right(_) =>
          // 保存账户
          val savedAccount = accountRepository.save(account)
          
          // 发布事件
          domainEventPublisher.publish(
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
          
          Right(account)
      }
    }.flatten
  }
  
  // 存款
  def deposit(
    accountId: AccountId,
    amount: Money,
    description: Option[String] = None
  ): Future[Either[String, BankAccount]] = {
    for {
      accountOpt <- accountRepository.findById(accountId)
      account <- Future.successful(accountOpt.toRight(s"Account with ID ${accountId.value} not found"))
      result <- Future.successful(account.deposit(amount, description))
      savedAccount <- result.fold(
        error => Future.successful(Left(error)),
        _ => accountRepository.save(account)
      )
    } yield savedAccount
  }
  
  // 取款
  def withdraw(
    accountId: AccountId,
    amount: Money,
    description: Option[String] = None
  ): Future[Either[String, BankAccount]] = {
    for {
      accountOpt <- accountRepository.findById(accountId)
      account <- Future.successful(accountOpt.toRight(s"Account with ID ${accountId.value} not found"))
      result <- Future.successful(account.withdraw(amount, description))
      savedAccount <- result.fold(
        error => Future.successful(Left(error)),
        _ => accountRepository.save(account)
      )
    } yield savedAccount
  }
  
  // 转账
  def transfer(
    fromAccountId: AccountId,
    toAccountId: AccountId,
    amount: Money,
    description: Option[String] = None
  ): Future[Either[String, (BankAccount, BankAccount)]] = {
    for {
      fromAccountOpt <- accountRepository.findById(fromAccountId)
      toAccountOpt <- accountRepository.findById(toAccountId)
      
      fromAccount <- Future.successful(fromAccountOpt.toRight(s"Source account with ID ${fromAccountId.value} not found"))
      toAccount <- Future.successful(toAccountOpt.toRight(s"Destination account with ID ${toAccountId.value} not found"))
      
      result <- Future.successful(fromAccount.transferTo(toAccount, amount, description))
      
      savedAccounts <- result.fold(
        error => Future.successful(Left(error)),
        _ => for {
          savedFrom <- accountRepository.save(fromAccount)
          savedTo <- accountRepository.save(toAccount)
        } yield (savedFrom, savedTo)
      )
    } yield savedAccounts
  }
  
  // 生成账户号码（简化实现）
  private def generateAccountNumber(): String = {
    s"${(100000000 + scala.util.Random.nextInt(900000000)).toString}"
  }
  
  // 获取账户详情
  def getAccountDetails(accountId: AccountId): Future[Option[AccountDetails]] = {
    for {
      accountOpt <- accountRepository.findById(accountId)
    } yield accountOpt.map(account =>
      AccountDetails(
        id = account.id,
        accountNumber = account.accountNumber,
        ownerName = account.ownerName,
        accountType = account.accountType,
        balance = account.getBalance,
        status = account.getStatus,
        openedDate = account.openedDate,
        lastModifiedDate = account.getLastModifiedDate
      )
    )
  }
  
  // 按客户名称查找账户
  def findAccountsByOwnerName(ownerName: String): Future[List[AccountSummary]] = {
    for {
      accounts <- accountRepository.findByOwnerName(ownerName)
    } yield accounts.map(account =>
      AccountSummary(
        id = account.id,
        accountNumber = account.accountNumber,
        ownerName = account.ownerName,
        accountType = account.accountType,
        balance = account.getBalance,
        status = account.getStatus
      )
    )
  }
}

// 12. 查询数据传输对象（DTO）
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

// 13. 示例运行器
object BankingSystemExample {
  def main(args: Array[String]): Unit = {
    implicit val ec: ExecutionContext = ExecutionContext.global
    val eventPublisher = new InMemoryDomainEventPublisher()
    val accountRepository = new InMemoryBankAccountRepository()
    val accountService = new BankAccountApplicationService(accountRepository, eventPublisher)
    
    println("=== Banking System DDD Example ===")
    
    // 开设账户
    val aliceAccountFuture = accountService.openAccount(
      "Alice Smith",
      AccountType.Checking,
      Money(1000.00, "USD")
    )
    
    val bobAccountFuture = accountService.openAccount(
      "Bob Johnson",
      AccountType.Savings,
      Money(500.00, "USD")
    )
    
    // 等待账户创建
    val aliceAccount = Await.result(aliceAccountFuture, 2.seconds).right.get
    val bobAccount = Await.result(bobAccountFuture, 2.seconds).right.get
    
    println(s"Created Alice's account: ${aliceAccount.accountNumber.value}")
    println(s"Created Bob's account: ${bobAccount.accountNumber.value}")
    
    // 存款
    val aliceDepositFuture = accountService.deposit(
      aliceAccount.id,
      Money(200.00, "USD"),
      Some("Initial deposit")
    )
    
    val bobDepositFuture = accountService.deposit(
      bobAccount.id,
      Money(150.00, "USD"),
      Some("Initial deposit")
    )
    
    // 等待存款完成
    val aliceDepositResult = Await.result(aliceDepositFuture, 2.seconds)
    val bobDepositResult = Await.result(bobDepositFuture, 2.seconds)
    
    println(s"Alice deposit result: ${aliceDepositResult.fold(identity, _.getBalance)}")
    println(s"Bob deposit result: ${bobDepositResult.fold(identity, _.getBalance)}")
    
    // 转账
    val transferFuture = accountService.transfer(
      aliceAccount.id,
      bobAccount.id,
      Money(100.00, "USD"),
      Some("Payment for services")
    )
    
    // 等待转账完成
    val transferResult = Await.result(transferFuture, 2.seconds)
    transferResult match {
      case Left(error) => println(s"Transfer failed: $error")
      case Right((fromAccount, toAccount)) =>
        println(s"Transfer successful:")
        println(s"  Alice's balance: ${fromAccount.getBalance}")
        println(s"  Bob's balance: ${toAccount.getBalance}")
    }
    
    // 获取账户详情
    val aliceDetailsFuture = accountService.getAccountDetails(aliceAccount.id)
    val aliceDetails = Await.result(aliceDetailsFuture, 2.seconds).get
    
    println(s"\nAlice's account details:")
    println(s"  Account number: ${aliceDetails.accountNumber.value}")
    println(s"  Owner: ${aliceDetails.ownerName}")
    println(s"  Type: ${aliceDetails.accountType}")
    println(s"  Balance: ${aliceDetails.balance}")
    println(s"  Status: ${aliceDetails.status}")
    
    // 按客户名称查找账户
    val aliceAccountsFuture = accountService.findAccountsByOwnerName("Alice Smith")
    val aliceAccounts = Await.result(aliceAccountsFuture, 2.seconds)
    
    println(s"\nFound ${aliceAccounts.length} accounts for Alice Smith:")
    aliceAccounts.foreach { account =>
      println(s"  Account ${account.accountNumber.value}: ${account.balance}")
    }
    
    // 显示发布的事件
    println(s"\nPublished events: ${eventPublisher.getPublishedEvents.size}")
    eventPublisher.getPublishedEvents.take(3).foreach { event =>
      println(s"  Event: ${event.getClass.getSimpleName}")
    }
  }
}