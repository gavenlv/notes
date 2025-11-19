import scala.concurrent.{Future, ExecutionContext}
import scala.concurrent.duration._
import scala.util.{Success, Failure, Try}
import scala.language.postfixOps
import scala.async.Async.{async, await}

object AsyncExamples {
  // 隐式ExecutionContext
  implicit val ec: ExecutionContext = ExecutionContext.global
  
  // 模拟异步操作
  def fetchUser(id: Int): Future[String] = Future {
    Thread.sleep(1000)
    s"User$id"
  }
  
  def fetchOrder(userId: String): Future[String] = Future {
    Thread.sleep(1000)
    s"Order for $userId"
  }
  
  def processPayment(orderId: String): Future[String] = Future {
    Thread.sleep(1000)
    s"Payment processed for $orderId"
  }
  
  // 传统Future组合方式
  def traditionalAsync(): Future[String] = {
    fetchUser(123).flatMap { user =>
      fetchOrder(user).flatMap { order =>
        processPayment(order)
      }
    }
  }
  
  // 使用for-comprehension
  def forComprehensionAsync(): Future[String] = {
    for {
      user <- fetchUser(123)
      order <- fetchOrder(user)
      payment <- processPayment(order)
    } yield payment
  }
  
  // 使用Scala Async库（需要额外依赖）
  // 注意：这个示例需要scala-async库支持
  /*
  def asyncAwaitExample(): Future[String] = {
    async {
      val user = await(fetchUser(123))
      val order = await(fetchOrder(user))
      val payment = await(processPayment(order))
      payment
    }
  }
  */
  
  // 异步错误处理示例
  def asyncWithErrorHandling(): Future[String] = {
    for {
      user <- fetchUser(123).recover {
        case ex: Exception => "DefaultUser"
      }
      order <- fetchOrder(user)
      payment <- processPayment(order).recoverWith {
        case ex: Exception =>
          println(s"支付处理失败: ${ex.getMessage}")
          Future.successful("Payment failed")
      }
    } yield payment
  }
  
  // 并行执行多个Future
  def parallelExecution(): Future[(String, String, String)] = {
    val userFuture = fetchUser(123)
    val orderFuture = fetchOrder("User123")
    val paymentFuture = processPayment("Order123")
    
    // 等待所有Future完成
    for {
      user <- userFuture
      order <- orderFuture
      payment <- paymentFuture
    } yield (user, order, payment)
  }
  
  // 使用Future.traverse进行批量操作
  def batchProcessing(): Future[List[String]] = {
    val userIds = List(1, 2, 3, 4, 5)
    Future.traverse(userIds) { id =>
      fetchUser(id)
    }
  }
  
  // 超时处理
  def withTimeout(): Future[String] = {
    val future = fetchUser(123)
    // 注意：scala.concurrent.Future没有内置超时方法
    // 需要使用第三方库如scala-java8-compat或自定义实现
    future
  }
  
  // 异步流处理示例（使用Akka Streams）
  /*
  def asyncStreamExample(): Unit = {
    import akka.actor.ActorSystem
    import akka.stream.scaladsl.{Source, Sink}
    import akka.stream.ActorMaterializer
    
    implicit val system = ActorSystem("StreamSystem")
    implicit val materializer = ActorMaterializer()
    
    val source = Source(1 to 10)
    val sink = Sink.foreach(println)
    
    source.mapAsync(parallelism = 4) { i =>
      fetchUser(i)
    }.runWith(sink)
  }
  */
  
  def main(args: Array[String]): Unit = {
    println("=== 异步编程示例 ===")
    
    // 1. 传统Future组合
    println("\n--- 传统Future组合 ---")
    traditionalAsync().onComplete {
      case Success(result) => println(s"传统方式结果: $result")
      case Failure(ex) => println(s"传统方式失败: ${ex.getMessage}")
    }
    
    // 2. for-comprehension方式
    println("\n--- for-comprehension方式 ---")
    forComprehensionAsync().onComplete {
      case Success(result) => println(s"for-comprehension结果: $result")
      case Failure(ex) => println(s"for-comprehension失败: ${ex.getMessage}")
    }
    
    // 3. 错误处理
    println("\n--- 异步错误处理 ---")
    asyncWithErrorHandling().onComplete {
      case Success(result) => println(s"错误处理结果: $result")
      case Failure(ex) => println(s"错误处理失败: ${ex.getMessage}")
    }
    
    // 4. 并行执行
    println("\n--- 并行执行 ---")
    parallelExecution().onComplete {
      case Success((user, order, payment)) => 
        println(s"并行执行结果: User=$user, Order=$order, Payment=$payment")
      case Failure(ex) => 
        println(s"并行执行失败: ${ex.getMessage}")
    }
    
    // 5. 批量处理
    println("\n--- 批量处理 ---")
    batchProcessing().onComplete {
      case Success(results) => println(s"批量处理结果: $results")
      case Failure(ex) => println(s"批量处理失败: ${ex.getMessage}")
    }
    
    // 等待所有异步操作完成
    Thread.sleep(5000)
    println("所有异步示例完成")
  }
}