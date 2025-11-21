package com.library

import akka.actor.typed.ActorSystem
import akka.actor.typed.scaladsl.Behaviors
import akka.http.scaladsl.Http
import akka.http.scaladsl.server.Route
import com.library.actors.{BookActor, UserActor, LoanActor}
import com.library.model.database.Database
import com.library.repository.{BookRepository, UserRepository, LoanRepository}
import com.library.routes.{ApiRoutes}
import com.library.service.{BookService, UserService, LoanService, RecommendationService}
import com.library.util.{ConfigComponent, DatabaseConfigComponent, ExecutionContextComponent}
import com.typesafe.config.ConfigFactory
import scala.util.{Success, Failure}
import scala.concurrent.Future

object Main extends App with ConfigComponent with DatabaseConfigComponent with ExecutionContextComponent {
  
  // 初始化数据库
  val initFuture = database.initialize()
  initFuture.onComplete {
    case Success(_) => println("Database initialized successfully")
    case Failure(ex) => println(s"Failed to initialize database: ${ex.getMessage}")
  }
  
  // 创建Repository实例
  val bookRepository = new BookRepository(database)
  val userRepository = new UserRepository(database)
  val loanRepository = new LoanRepository(database)
  
  // 创建Service实例
  val bookService = new BookService(bookRepository)
  val userService = new UserService(userRepository)
  val loanService = new LoanService(loanRepository, bookRepository, userRepository)
  val recommendationService = new RecommendationService(bookRepository, loanRepository)
  
  // 创建API路由
  val apiRoutes = new ApiRoutes(bookService, userService, loanService)
  
  // 启动HTTP服务器
  val host = config.getString("akka.http.host")
  val port = config.getInt("akka.http.port")
  
  val bindingFuture = Http().newServerAt(host, port).bind(apiRoutes.routes)
  
  bindingFuture.onComplete {
    case Success(binding) =>
      val address = binding.localAddress
      println(s"Server online at http://${address.getHostString}:${address.getPort}/")
      
      // 添加关闭钩子
      sys.addShutdownHook {
        println("Shutting down server...")
        binding.unbind()
        database.shutdown()
      }
      
    case Failure(exception) =>
      println(s"Failed to bind HTTP server: ${exception.getMessage}")
      System.exit(1)
  }
  
  // 创建Actor系统
  val guardianBehavior = Behaviors.setup { context =>
    // 创建Actor引用
    val bookActor = context.spawn(BookActor(bookService), "bookActor")
    val userActor = context.spawn(UserActor(userService), "userActor")
    val loanActor = context.spawn(LoanActor(loanService), "loanActor")
    
    Behaviors.empty
  }
  
  val system = ActorSystem[Nothing](guardianBehavior, "library-management-system")
}