package taskflow

// 主应用程序入口
object Main {
  
  // 1. 应用程序配置
  case class AppConfig(
    appName: String = "TaskFlow",
    version: String = "1.0.0",
    httpPort: Int = 8080,
    databaseUrl: String = "jdbc:h2:mem:testdb",
    secretKey: String = "secret-key-for-jwt"
  )
  
  // 2. 应用程序组件
  trait AppComponent
  
  // 3. 用户组件
  trait UserComponent extends AppComponent {
    val userRepository: Repository.UserRepository
    val userService: Service.UserService
  }
  
  // 4. 项目组件
  trait ProjectComponent extends AppComponent {
    val projectRepository: Repository.ProjectRepository
    val projectService: Service.ProjectService
  }
  
  // 5. 任务组件
  trait TaskComponent extends AppComponent {
    val taskRepository: Repository.TaskRepository
    val taskService: Service.TaskService
  }
  
  // 6. 通知组件
  trait NotificationComponent extends AppComponent {
    val notificationRepository: Repository.NotificationRepository
    val notificationService: Service.NotificationService
  }
  
  // 7. 事务管理组件
  trait TransactionComponent extends AppComponent {
    val transactionManager: Repository.TransactionManager
  }
  
  // 8. 组件实现
  trait ComponentImplementation {
    // Repositories
    val userRepository: Repository.UserRepository = new Repository.InMemoryUserRepository
    val projectRepository: Repository.ProjectRepository = new Repository.InMemoryProjectRepository
    val taskRepository: Repository.TaskRepository = new Repository.InMemoryTaskRepository
    val notificationRepository: Repository.NotificationRepository = new Repository.InMemoryNotificationRepository
    val transactionManager: Repository.TransactionManager = new Repository.SimpleTransactionManager
    
    // Services
    val userService: Service.UserService = new Service.UserServiceImpl(userRepository, transactionManager)
    val projectService: Service.ProjectService = new Service.ProjectServiceImpl(projectRepository, userRepository, transactionManager)
    val taskService: Service.TaskService = new Service.TaskServiceImpl(taskRepository, userRepository, projectRepository, transactionManager)
    val notificationService: Service.NotificationService = new Service.NotificationServiceImpl(notificationRepository, userRepository)
  }
  
  // 9. 应用程序模块
  object AppModule extends ComponentImplementation
  
  // 10. 应用程序状态
  case class AppState(
    startTime: Long = System.currentTimeMillis(),
    requestCount: Int = 0,
    activeUsers: Set[String] = Set.empty
  )
  
  // 11. 应用程序上下文
  class ApplicationContext(val config: AppConfig) {
    private var state: AppState = AppState()
    
    def getState: AppState = state
    
    def incrementRequestCount(): Unit = {
      state = state.copy(requestCount = state.requestCount + 1)
    }
    
    def addUser(userId: String): Unit = {
      state = state.copy(activeUsers = state.activeUsers + userId)
    }
    
    def removeUser(userId: String): Unit = {
      state = state.copy(activeUsers = state.activeUsers - userId)
    }
  }
  
  // 12. 应用程序生命周期管理
  trait Lifecycle {
    def start(): Unit
    def stop(): Unit
    def isRunning: Boolean
  }
  
  // 13. 主应用程序类
  class Application(config: AppConfig) extends Lifecycle {
    private var running = false
    private val context = new ApplicationContext(config)
    
    def start(): Unit = {
      if (!running) {
        println(s"启动 ${config.appName} v${config.version}...")
        println(s"监听端口: ${config.httpPort}")
        println(s"数据库URL: ${config.databaseUrl}")
        
        // 初始化组件
        initializeComponents()
        
        // 启动HTTP服务器（模拟）
        startHttpServer()
        
        running = true
        println(s"${config.appName} 启动成功!")
      }
    }
    
    def stop(): Unit = {
      if (running) {
        println(s"停止 ${config.appName}...")
        running = false
        println(s"${config.appName} 已停止.")
      }
    }
    
    def isRunning: Boolean = running
    
    private def initializeComponents(): Unit = {
      println("初始化应用程序组件...")
      // 在实际应用中，这里可能会进行数据库迁移、缓存预热等操作
      println("组件初始化完成.")
    }
    
    private def startHttpServer(): Unit = {
      println("启动HTTP服务器...")
      // 创建API路由
      val userRoutes = new API.UserRoutes(AppModule.userService)
      val projectRoutes = new API.ProjectRoutes(AppModule.projectService)
      val taskRoutes = new API.TaskRoutes(AppModule.taskService)
      
      // 创建服务器
      val server = new API.HttpServer(config.httpPort)
      
      // 添加路由
      server.addRoute(userRoutes)
      server.addRoute(projectRoutes)
      server.addRoute(taskRoutes)
      
      // 添加中间件
      server.use(new API.LoggingMiddleware())
      server.use(new API.ErrorHandlingMiddleware())
      // 注意：在实际应用中，我们会使用AuthMiddleware，但在示例中省略以简化
      
      // 启动服务器（模拟）
      server.start()
      
      println("HTTP服务器启动完成.")
    }
    
    // 获取应用程序上下文
    def getContext: ApplicationContext = context
  }
  
  // 14. 应用程序工厂
  object ApplicationFactory {
    def createApplication(config: AppConfig = AppConfig()): Application = {
      new Application(config)
    }
  }
  
  // 15. 健康检查服务
  object HealthCheck {
    def checkDatabase(): Boolean = {
      // 在实际应用中，这里会检查数据库连接
      println("检查数据库连接...")
      Thread.sleep(100) // 模拟检查延迟
      println("数据库连接正常.")
      true
    }
    
    def checkExternalServices(): List[(String, Boolean)] = {
      // 在实际应用中，这里会检查外部服务的连接
      println("检查外部服务...")
      Thread.sleep(50) // 模拟检查延迟
      val services = List(
        ("邮件服务", true),
        ("消息队列", true),
        ("文件存储", true)
      )
      services.foreach { case (name, status) =>
        println(s"$name: ${if (status) "正常" else "异常"}")
      }
      services
    }
    
    def performHealthCheck(): Map[String, Any] = {
      val dbStatus = checkDatabase()
      val serviceStatuses = checkExternalServices()
      
      Map(
        "status" -> (if (dbStatus && serviceStatuses.forall(_._2)) "UP" else "DOWN"),
        "database" -> dbStatus,
        "services" -> serviceStatuses.toMap,
        "timestamp" -> System.currentTimeMillis()
      )
    }
  }
  
  // 16. 性能监控
  object PerformanceMonitor {
    private val startTime = System.nanoTime()
    
    def getUptime(): Long = {
      (System.nanoTime() - startTime) / 1000000 // 转换为毫秒
    }
    
    def getMemoryUsage(): (Long, Long) = {
      val runtime = Runtime.getRuntime
      val totalMemory = runtime.totalMemory()
      val freeMemory = runtime.freeMemory()
      val usedMemory = totalMemory - freeMemory
      (usedMemory, totalMemory)
    }
    
    def printStats(): Unit = {
      val uptime = getUptime()
      val (usedMemory, totalMemory) = getMemoryUsage()
      
      println(s"运行时间: ${uptime}ms")
      println(f"内存使用: $usedMemory%,d / $totalMemory%,d bytes (${(usedMemory.toDouble/totalMemory*100).formatted("%.2f")}%)")
    }
  }
  
  // 17. 示例数据生成器
  object SampleDataGenerator {
    import DomainModel._
    import Repository._
    import Service._
    
    def generateSampleData(app: Application): Unit = {
      println("生成示例数据...")
      
      // 获取服务实例
      val userService = AppModule.userService
      val projectService = AppModule.projectService
      val taskService = AppModule.taskService
      
      // 创建示例用户
      val userResult = userService.registerUser("alice", "alice@example.com", "Alice", "Smith")
      userResult match {
        case Right(user) =>
          println(s"创建用户: ${user.displayName}")
          val userId = user.id.value
          
          // 创建示例项目
          val projectResult = projectService.createProject("TaskFlow开发", Some("任务管理系统开发项目"), userId)
          projectResult match {
            case Right(project) =>
              println(s"创建项目: ${project.name}")
              val projectId = project.id.value
              
              // 创建示例任务
              val taskResult = taskService.createTask(
                "实现用户功能",
                Some("实现用户注册、登录和管理功能"),
                Priority.High,
                Some(userId),
                userId,
                projectId
              )
              
              taskResult match {
                case Right(task) =>
                  println(s"创建任务: ${task.title}")
                  
                  // 创建更多任务
                  val task2Result = taskService.createTask(
                    "设计数据库模型",
                    Some("设计和实现数据库表结构"),
                    Priority.Medium,
                    Some(userId),
                    userId,
                    projectId
                  )
                  
                  task2Result match {
                    case Right(task2) =>
                      println(s"创建任务: ${task2.title}")
                    case Left(error) =>
                      println(s"创建任务失败: $error")
                  }
                case Left(error) =>
                  println(s"创建任务失败: $error")
              }
            case Left(error) =>
              println(s"创建项目失败: $error")
          }
        case Left(error) =>
          println(s"创建用户失败: $error")
      }
      
      println("示例数据生成完成.")
    }
  }
  
  // 18. 命令行界面
  object CLI {
    def printWelcome(): Unit = {
      println("=" * 50)
      println("         TaskFlow 应用程序")
      println("    基于Scala的现代任务管理系统")
      println("=" * 50)
    }
    
    def printMenu(): Unit = {
      println("\n请选择操作:")
      println("1. 启动应用程序")
      println("2. 停止应用程序")
      println("3. 健康检查")
      println("4. 性能监控")
      println("5. 生成示例数据")
      println("6. 退出")
    }
    
    def handleCommand(command: String, app: Application): Boolean = {
      command match {
        case "1" =>
          if (!app.isRunning) {
            app.start()
          } else {
            println("应用程序已在运行中.")
          }
          false
        case "2" =>
          if (app.isRunning) {
            app.stop()
          } else {
            println("应用程序未运行.")
          }
          false
        case "3" =>
          val health = HealthCheck.performHealthCheck()
          println(s"健康检查结果: ${health("status")}")
          println(s"数据库状态: ${health("database")}")
          println("服务状态:")
          health("services").asInstanceOf[Map[String, Boolean]].foreach { case (name, status) =>
            println(s"  $name: ${if (status) "正常" else "异常"}")
          }
          false
        case "4" =>
          println("性能监控信息:")
          PerformanceMonitor.printStats()
          false
        case "5" =>
          if (app.isRunning) {
            SampleDataGenerator.generateSampleData(app)
          } else {
            println("请先启动应用程序.")
          }
          false
        case "6" =>
          if (app.isRunning) {
            app.stop()
          }
          true // 退出
        case _ =>
          println("无效的命令，请重新选择.")
          false
      }
    }
  }
  
  // 19. 主函数
  def main(args: Array[String]): Unit = {
    CLI.printWelcome()
    
    // 创建应用程序实例
    val config = AppConfig()
    val app = ApplicationFactory.createApplication(config)
    
    // 如果提供了命令行参数，则执行相应操作
    if (args.length > 0) {
      args.foreach { arg =>
        arg match {
          case "--start" =>
            app.start()
          case "--generate-data" =>
            if (app.isRunning) {
              SampleDataGenerator.generateSampleData(app)
            } else {
              println("生成示例数据前需要启动应用程序.")
            }
          case "--health" =>
            val health = HealthCheck.performHealthCheck()
            println(s"健康检查: ${health("status")}")
          case "--version" =>
            println(s"${config.appName} v${config.version}")
          case _ =>
            println(s"未知参数: $arg")
        }
      }
    } else {
      // 交互式模式
      var shouldExit = false
      while (!shouldExit) {
        CLI.printMenu()
        print("请输入选项: ")
        val input = scala.io.StdIn.readLine()
        shouldExit = CLI.handleCommand(input, app)
      }
    }
    
    println("感谢使用TaskFlow!")
  }
  
  // 20. 测试入口点
  object TestMain {
    def runIntegrationTest(): Unit = {
      println("=== 运行集成测试 ===")
      
      // 创建测试配置
      val testConfig = AppConfig(appName = "TaskFlow-Test")
      val app = ApplicationFactory.createApplication(testConfig)
      
      // 启动应用程序
      app.start()
      
      // 执行健康检查
      val health = HealthCheck.performHealthCheck()
      assert(health("status") == "UP", "健康检查应该通过")
      
      // 生成示例数据
      SampleDataGenerator.generateSampleData(app)
      
      // 测试用户服务
      val userService = AppModule.userService
      val userResult = userService.registerUser("testuser", "test@example.com", "Test", "User")
      assert(userResult.isRight, "用户注册应该成功")
      
      // 测试项目服务
      val userId = userResult.right.get.id.value
      val projectService = AppModule.projectService
      val projectResult = projectService.createProject("测试项目", Some("用于测试的项目"), userId)
      assert(projectResult.isRight, "项目创建应该成功")
      
      // 测试任务服务
      val projectId = projectResult.right.get.id.value
      val taskService = AppModule.taskService
      val taskResult = taskService.createTask("测试任务", Some("用于测试的任务"), Priority.Medium, Some(userId), userId, projectId)
      assert(taskResult.isRight, "任务创建应该成功")
      
      // 验证数据
      val tasksResult = taskService.getTasksByProject(projectId, Repository.PageRequest(0, 10))
      assert(tasksResult.isRight && tasksResult.right.get.content.nonEmpty, "应该能够获取到创建的任务")
      
      println("所有集成测试通过!")
      
      // 停止应用程序
      app.stop()
    }
    
    def main(args: Array[String]): Unit = {
      runIntegrationTest()
    }
  }
}