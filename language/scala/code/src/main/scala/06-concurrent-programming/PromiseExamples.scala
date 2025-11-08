import scala.concurrent.{Future, Promise, ExecutionContext, TimeoutException}
import scala.concurrent.duration._
import scala.util.{Success, Failure, Try}
import scala.language.postfixOps

// 使用默认的全局ExecutionContext
import ExecutionContext.Implicits.global

object PromiseExamples {
  // 模拟异步操作
  def asyncOperation(): Future[String] = {
    val promise = Promise[String]()
    
    // 在另一个线程中执行操作
    Future {
      Thread.sleep(1000)
      promise.success("操作完成")
    }
    
    promise.future
  }
  
  // 模拟可能失败的异步操作
  def riskyAsyncOperation(shouldFail: Boolean): Future[Int] = {
    val promise = Promise[Int]()
    
    Future {
      Thread.sleep(500)
      if (shouldFail) {
        promise.failure(new RuntimeException("操作失败"))
      } else {
        promise.success(42)
      }
    }
    
    promise.future
  }
  
  // 模拟回调风格的API转换为Future
  def callbackToFutureStyle(): Future[String] = {
    val promise = Promise[String]()
    
    // 模拟回调API
    simulateCallbackAPI { result =>
      promise.success(result)
    }
    
    promise.future
  }
  
  // 模拟回调风格的API
  def simulateCallbackAPI(callback: String => Unit): Unit = {
    Future {
      Thread.sleep(800)
      callback("回调结果")
    }
  }
  
  // 超时处理
  def timeoutExample(): Future[String] = {
    val promise = Promise[String]()
    
    Future {
      Thread.sleep(2000) // 模拟长时间运行的操作
      promise.success("长时间操作完成")
    }
    
    // 设置超时
    Future {
      Thread.sleep(1000)
      if (!promise.isCompleted) {
        promise.failure(new TimeoutException("操作超时"))
      }
    }
    
    promise.future
  }
  
  // 手动完成Promise
  def manualPromiseCompletion(): Unit = {
    val promise = Promise[String]()
    
    // 在另一个线程中监听Promise
    Future {
      promise.future.foreach(result => println(s"Promise完成，结果: $result"))
    }
    
    // 手动完成Promise
    Future {
      Thread.sleep(500)
      promise.success("手动完成")
    }
  }
  
  def main(args: Array[String]): Unit = {
    println("=== Promise 基本使用示例 ===")
    
    // 1. 基本Promise使用
    val future1 = asyncOperation()
    future1.foreach(result => println(s"异步操作结果: $result"))
    
    // 2. 处理可能失败的Promise
    val future2 = riskyAsyncOperation(false)
    future2.onComplete {
      case Success(result) => println(s"成功结果: $result")
      case Failure(exception) => println(s"失败异常: ${exception.getMessage}")
    }
    
    val future3 = riskyAsyncOperation(true)
    future3.onComplete {
      case Success(result) => println(s"成功结果: $result")
      case Failure(exception) => println(s"失败异常: ${exception.getMessage}")
    }
    
    // 3. 回调转Future
    val future4 = callbackToFutureStyle()
    future4.foreach(result => println(s"回调转换结果: $result"))
    
    // 4. 超时处理
    val future5 = timeoutExample()
    future5.onComplete {
      case Success(result) => println(s"超时示例结果: $result")
      case Failure(exception) => println(s"超时示例异常: ${exception.getMessage}")
    }
    
    // 5. 手动完成Promise
    manualPromiseCompletion()
    
    // 6. Promise链式操作
    val promiseChain = Promise[Int]()
    val futureChain = promiseChain.future
    
    // 链式处理
    futureChain
      .map(_ * 2)
      .flatMap(x => Future(x + 10))
      .foreach(result => println(s"链式处理结果: $result"))
    
    // 完成Promise
    Future {
      Thread.sleep(1000)
      promiseChain.success(5)
    }
    
    // 7. Promise组合
    val promiseA = Promise[String]()
    val promiseB = Promise[String]()
    
    val combinedFuture = for {
      a <- promiseA.future
      b <- promiseB.future
    } yield s"$a and $b"
    
    combinedFuture.foreach(result => println(s"组合结果: $result"))
    
    // 分别完成Promise
    Future {
      Thread.sleep(600)
      promiseA.success("A完成")
    }
    
    Future {
      Thread.sleep(1200)
      promiseB.success("B完成")
    }
    
    // 等待所有示例完成
    Thread.sleep(3000)
    println("所有Promise示例完成")
  }
}