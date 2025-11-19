package taskflow

// Web API层实现
object API {
  
  // 1. 基础HTTP模型
  case class HttpRequest(
    method: String,
    path: String,
    headers: Map[String, String],
    body: Option[String]
  )
  
  case class HttpResponse(
    statusCode: Int,
    headers: Map[String, String],
    body: String
  )
  
  // 2. JSON处理辅助类
  object JsonHelper {
    import spray.json._
    import spray.json.DefaultJsonProtocol._
    
    // 简化的JSON协议
    implicit val userFormat = jsonFormat7(DomainModel.User)
    implicit val projectFormat = jsonFormat7(DomainModel.Project)
    implicit val taskFormat = jsonFormat11(DomainModel.Task)
    implicit val notificationFormat = jsonFormat7(DomainModel.Notification)
    
    def toJson[T](obj: T)(implicit writer: JsonWriter[T]): String = {
      obj.toJson.compactPrint
    }
    
    def fromJson[T](json: String)(implicit reader: JsonReader[T]): Either[String, T] = {
      try {
        Right(json.parseJson.convertTo[T])
      } catch {
        case e: Exception => Left(e.getMessage)
      }
    }
  }
  
  // 3. API路由特质
  trait Route {
    def handle(request: HttpRequest): HttpResponse
    def matches(request: HttpRequest): Boolean
  }
  
  // 4. 路由管理器
  class Router {
    private val routes = scala.collection.mutable.ListBuffer[Route]()
    
    def addRoute(route: Route): Unit = {
      routes += route
    }
    
    def handle(request: HttpRequest): HttpResponse = {
      routes.find(_.matches(request)) match {
        case Some(route) => route.handle(request)
        case None => HttpResponse(404, Map("Content-Type" -> "application/json"), """{"error": "Not Found"}""")
      }
    }
  }
  
  // 5. 中间件特质
  trait Middleware {
    def apply(next: HttpRequest => HttpResponse): HttpRequest => HttpResponse
  }
  
  // 6. 认证中间件
  class AuthMiddleware extends Middleware {
    def apply(next: HttpRequest => HttpResponse): HttpRequest => HttpResponse = { request =>
      // 简化的认证检查
      request.headers.get("Authorization") match {
        case Some(token) if token.startsWith("Bearer ") =>
          // 在实际应用中，这里会验证token的有效性
          next(request)
        case _ =>
          HttpResponse(401, Map("Content-Type" -> "application/json"), """{"error": "Unauthorized"}""")
      }
    }
  }
  
  // 7. 日志中间件
  class LoggingMiddleware extends Middleware {
    def apply(next: HttpRequest => HttpResponse): HttpRequest => HttpResponse = { request =>
      println(s"[LOG] ${request.method} ${request.path}")
      val response = next(request)
      println(s"[LOG] Response: ${response.statusCode}")
      response
    }
  }
  
  // 8. 错误处理中间件
  class ErrorHandlingMiddleware extends Middleware {
    def apply(next: HttpRequest => HttpResponse): HttpRequest => HttpResponse = { request =>
      try {
        next(request)
      } catch {
        case e: Exception =>
          println(s"[ERROR] ${e.getMessage}")
          HttpResponse(500, Map("Content-Type" -> "application/json"), 
            s"""{"error": "Internal Server Error", "message": "${e.getMessage}"}""")
      }
    }
  }
  
  // 9. 用户API路由
  import DomainModel._
  import Repository._
  import Service._
  
  class UserRoutes(
    userService: UserService
  ) extends Route {
    
    def matches(request: HttpRequest): Boolean = {
      request.path.startsWith("/users") && request.method == "GET" ||
      request.path == "/users/register" && request.method == "POST" ||
      request.path.matches("/users/[^/]+") && request.method == "PUT"
    }
    
    def handle(request: HttpRequest): HttpResponse = {
      request.path match {
        case "/users/register" if request.method == "POST" =>
          handleRegister(request)
        case path if path.matches("/users/[^/]+") && request.method == "PUT" =>
          val userId = path.split("/")(2)
          handleUpdateUser(userId, request)
        case "/users" if request.method == "GET" =>
          handleGetUsers(request)
        case path if path.matches("/users/[^/]+") && request.method == "GET" =>
          val userId = path.split("/")(2)
          handleGetUser(userId)
        case _ =>
          HttpResponse(404, Map("Content-Type" -> "application/json"), """{"error": "Not Found"}""")
      }
    }
    
    private def handleRegister(request: HttpRequest): HttpResponse = {
      import JsonHelper._
      request.body.flatMap(fromJson[Map[String, String]](_).toOption) match {
        case Some(data) =>
          val result = userService.registerUser(
            data.getOrElse("username", ""),
            data.getOrElse("email", ""),
            data.getOrElse("firstName", ""),
            data.getOrElse("lastName", "")
          )
          
          result match {
            case Right(user) =>
              HttpResponse(201, Map("Content-Type" -> "application/json"), toJson(user))
            case Left(ValidationError(messages)) =>
              HttpResponse(400, Map("Content-Type" -> "application/json"), 
                toJson(Map("error" -> "Validation Failed", "messages" -> messages)))
            case Left(ConflictError(message)) =>
              HttpResponse(409, Map("Content-Type" -> "application/json"), 
                toJson(Map("error" -> "Conflict", "message" -> message)))
            case Left(error) =>
              HttpResponse(500, Map("Content-Type" -> "application/json"), 
                toJson(Map("error" -> "Internal Error", "message" -> error.toString)))
          }
        case None =>
          HttpResponse(400, Map("Content-Type" -> "application/json"), """{"error": "Invalid JSON"}""")
      }
    }
    
    private def handleUpdateUser(userId: String, request: HttpRequest): HttpResponse = {
      import JsonHelper._
      request.body.flatMap(fromJson[Map[String, Option[String]]](_).toOption) match {
        case Some(data) =>
          val updates = UserUpdate(
            firstName = data.get("firstName").flatten,
            lastName = data.get("lastName").flatten,
            email = data.get("email").flatten,
            phone = data.get("phone").flatten
          )
          
          val result = userService.updateUser(userId, updates)
          result match {
            case Right(user) =>
              HttpResponse(200, Map("Content-Type" -> "application/json"), toJson(user))
            case Left(NotFoundError(message)) =>
              HttpResponse(404, Map("Content-Type" -> "application/json"), 
                toJson(Map("error" -> "Not Found", "message" -> message)))
            case Left(error) =>
              HttpResponse(500, Map("Content-Type" -> "application/json"), 
                toJson(Map("error" -> "Internal Error", "message" -> error.toString)))
          }
        case None =>
          HttpResponse(400, Map("Content-Type" -> "application/json"), """{"error": "Invalid JSON"}""")
      }
    }
    
    private def handleGetUsers(request: HttpRequest): HttpResponse = {
      import JsonHelper._
      // 解析查询参数
      val params = parseQueryParams(request.path)
      val page = params.get("page").flatMap(_.toIntOption).getOrElse(0)
      val size = params.get("size").flatMap(_.toIntOption).getOrElse(20)
      
      val pageable = PageRequest(page, size)
      val result = userService.getUsers(pageable)
      
      result match {
        case Right(pageData) =>
          HttpResponse(200, Map("Content-Type" -> "application/json"), toJson(pageData))
        case Left(error) =>
          HttpResponse(500, Map("Content-Type" -> "application/json"), 
            toJson(Map("error" -> "Internal Error", "message" -> error.toString)))
      }
    }
    
    private def handleGetUser(userId: String): HttpResponse = {
      import JsonHelper._
      val result = userService.getUser(userId)
      
      result match {
        case Right(user) =>
          HttpResponse(200, Map("Content-Type" -> "application/json"), toJson(user))
        case Left(NotFoundError(message)) =>
          HttpResponse(404, Map("Content-Type" -> "application/json"), 
            toJson(Map("error" -> "Not Found", "message" -> message)))
        case Left(error) =>
          HttpResponse(500, Map("Content-Type" -> "application/json"), 
            toJson(Map("error" -> "Internal Error", "message" -> error.toString)))
      }
    }
    
    private def parseQueryParams(path: String): Map[String, String] = {
      if (path.contains("?")) {
        val queryParams = path.split("\\?", 2)(1)
        queryParams.split("&").map { param =>
          val parts = param.split("=", 2)
          if (parts.length == 2) (parts(0), parts(1)) else (parts(0), "")
        }.toMap
      } else {
        Map.empty
      }
    }
  }
  
  // 10. 项目API路由
  class ProjectRoutes(
    projectService: ProjectService
  ) extends Route {
    
    def matches(request: HttpRequest): Boolean = {
      request.path.startsWith("/projects") && 
      (request.method == "GET" || request.method == "POST" || request.method == "PUT")
    }
    
    def handle(request: HttpRequest): HttpResponse = {
      request.path match {
        case "/projects" if request.method == "POST" =>
          handleCreateProject(request)
        case path if path.matches("/projects/[^/]+") && request.method == "PUT" =>
          val projectId = path.split("/")(2)
          handleUpdateProject(projectId, request)
        case "/projects" if request.method == "GET" =>
          handleGetProjects(request)
        case path if path.matches("/projects/[^/]+") && request.method == "GET" =>
          val projectId = path.split("/")(2)
          handleGetProject(projectId)
        case _ =>
          HttpResponse(404, Map("Content-Type" -> "application/json"), """{"error": "Not Found"}""")
      }
    }
    
    private def handleCreateProject(request: HttpRequest): HttpResponse = {
      import JsonHelper._
      request.body.flatMap(fromJson[Map[String, String]](_).toOption) match {
        case Some(data) =>
          val ownerId = request.headers.getOrElse("X-User-ID", "")
          if (ownerId.isEmpty) {
            return HttpResponse(400, Map("Content-Type" -> "application/json"), 
              """{"error": "Missing X-User-ID header"}""")
          }
          
          val result = projectService.createProject(
            data.getOrElse("name", ""),
            data.get("description"),
            ownerId
          )
          
          result match {
            case Right(project) =>
              HttpResponse(201, Map("Content-Type" -> "application/json"), toJson(project))
            case Left(ValidationError(messages)) =>
              HttpResponse(400, Map("Content-Type" -> "application/json"), 
                toJson(Map("error" -> "Validation Failed", "messages" -> messages)))
            case Left(NotFoundError(message)) =>
              HttpResponse(404, Map("Content-Type" -> "application/json"), 
                toJson(Map("error" -> "Not Found", "message" -> message)))
            case Left(error) =>
              HttpResponse(500, Map("Content-Type" -> "application/json"), 
                toJson(Map("error" -> "Internal Error", "message" -> error.toString)))
          }
        case None =>
          HttpResponse(400, Map("Content-Type" -> "application/json"), """{"error": "Invalid JSON"}""")
      }
    }
    
    private def handleUpdateProject(projectId: String, request: HttpRequest): HttpResponse = {
      import JsonHelper._
      request.body.flatMap(fromJson[Map[String, Option[String]]](_).toOption) match {
        case Some(data) =>
          val updates = ProjectUpdate(
            name = data.get("name").flatten,
            description = data.get("description").flatten
          )
          
          val result = projectService.updateProject(projectId, updates)
          result match {
            case Right(project) =>
              HttpResponse(200, Map("Content-Type" -> "application/json"), toJson(project))
            case Left(NotFoundError(message)) =>
              HttpResponse(404, Map("Content-Type" -> "application/json"), 
                toJson(Map("error" -> "Not Found", "message" -> message)))
            case Left(error) =>
              HttpResponse(500, Map("Content-Type" -> "application/json"), 
                toJson(Map("error" -> "Internal Error", "message" -> error.toString)))
          }
        case None =>
          HttpResponse(400, Map("Content-Type" -> "application/json"), """{"error": "Invalid JSON"}""")
      }
    }
    
    private def handleGetProjects(request: HttpRequest): HttpResponse = {
      import JsonHelper._
      val ownerId = request.headers.getOrElse("X-User-ID", "")
      if (ownerId.isEmpty) {
        return HttpResponse(400, Map("Content-Type" -> "application/json"), 
          """{"error": "Missing X-User-ID header"}""")
      }
      
      // 解析查询参数
      val params = parseQueryParams(request.path)
      val page = params.get("page").flatMap(_.toIntOption).getOrElse(0)
      val size = params.get("size").flatMap(_.toIntOption).getOrElse(20)
      
      val pageable = PageRequest(page, size)
      val result = projectService.getProjectsByOwner(ownerId, pageable)
      
      result match {
        case Right(pageData) =>
          HttpResponse(200, Map("Content-Type" -> "application/json"), toJson(pageData))
        case Left(NotFoundError(message)) =>
          HttpResponse(404, Map("Content-Type" -> "application/json"), 
            toJson(Map("error" -> "Not Found", "message" -> message)))
        case Left(error) =>
          HttpResponse(500, Map("Content-Type" -> "application/json"), 
            toJson(Map("error" -> "Internal Error", "message" -> error.toString)))
      }
    }
    
    private def handleGetProject(projectId: String): HttpResponse = {
      import JsonHelper._
      val result = projectService.getProject(projectId)
      
      result match {
        case Right(project) =>
          HttpResponse(200, Map("Content-Type" -> "application/json"), toJson(project))
        case Left(NotFoundError(message)) =>
          HttpResponse(404, Map("Content-Type" -> "application/json"), 
            toJson(Map("error" -> "Not Found", "message" -> message)))
        case Left(error) =>
          HttpResponse(500, Map("Content-Type" -> "application/json"), 
            toJson(Map("error" -> "Internal Error", "message" -> error.toString)))
      }
    }
    
    private def parseQueryParams(path: String): Map[String, String] = {
      if (path.contains("?")) {
        val queryParams = path.split("\\?", 2)(1)
        queryParams.split("&").map { param =>
          val parts = param.split("=", 2)
          if (parts.length == 2) (parts(0), parts(1)) else (parts(0), "")
        }.toMap
      } else {
        Map.empty
      }
    }
  }
  
  // 11. 任务API路由
  class TaskRoutes(
    taskService: TaskService
  ) extends Route {
    
    def matches(request: HttpRequest): Boolean = {
      request.path.startsWith("/tasks") && 
      (request.method == "GET" || request.method == "POST" || request.method == "PUT")
    }
    
    def handle(request: HttpRequest): HttpResponse = {
      request.path match {
        case "/tasks" if request.method == "POST" =>
          handleCreateTask(request)
        case path if path.matches("/tasks/[^/]+") && request.method == "PUT" =>
          val taskId = path.split("/")(2)
          handleUpdateTask(taskId, request)
        case path if path.matches("/tasks/[^/]+/status") && request.method == "PUT" =>
          val taskId = path.split("/")(2)
          handleChangeTaskStatus(taskId, request)
        case "/tasks" if request.method == "GET" =>
          handleGetTasks(request)
        case path if path.matches("/tasks/[^/]+") && request.method == "GET" =>
          val taskId = path.split("/")(2)
          handleGetTask(taskId)
        case _ =>
          HttpResponse(404, Map("Content-Type" -> "application/json"), """{"error": "Not Found"}""")
      }
    }
    
    private def handleCreateTask(request: HttpRequest): HttpResponse = {
      import JsonHelper._
      request.body.flatMap(fromJson[Map[String, Any]](_).toOption) match {
        case Some(data) =>
          val reporterId = request.headers.getOrElse("X-User-ID", "")
          if (reporterId.isEmpty) {
            return HttpResponse(400, Map("Content-Type" -> "application/json"), 
              """{"error": "Missing X-User-ID header"}""")
          }
          
          // 提取优先级
          val priorityStr = data.get("priority").map(_.toString).getOrElse("Medium")
          val priority = priorityStr match {
            case "Low" => Priority.Low
            case "High" => Priority.High
            case _ => Priority.Medium
          }
          
          val result = taskService.createTask(
            data.get("title").map(_.toString).getOrElse(""),
            data.get("description").map(_.toString),
            priority,
            data.get("assigneeId").map(_.toString),
            reporterId,
            data.get("projectId").map(_.toString).getOrElse("")
          )
          
          result match {
            case Right(task) =>
              HttpResponse(201, Map("Content-Type" -> "application/json"), toJson(task))
            case Left(ValidationError(messages)) =>
              HttpResponse(400, Map("Content-Type" -> "application/json"), 
                toJson(Map("error" -> "Validation Failed", "messages" -> messages)))
            case Left(NotFoundError(message)) =>
              HttpResponse(404, Map("Content-Type" -> "application/json"), 
                toJson(Map("error" -> "Not Found", "message" -> message)))
            case Left(error) =>
              HttpResponse(500, Map("Content-Type" -> "application/json"), 
                toJson(Map("error" -> "Internal Error", "message" -> error.toString)))
          }
        case None =>
          HttpResponse(400, Map("Content-Type" -> "application/json"), """{"error": "Invalid JSON"}""")
      }
    }
    
    private def handleUpdateTask(taskId: String, request: HttpRequest): HttpResponse = {
      import JsonHelper._
      request.body.flatMap(fromJson[Map[String, Option[Any]]](_).toOption) match {
        case Some(data) =>
          // 提取优先级
          val priorityOpt = data.get("priority").flatten.map(_.toString)
          val priority = priorityOpt.map {
            case "Low" => Priority.Low
            case "High" => Priority.High
            case _ => Priority.Medium
          }
          
          val updates = TaskUpdate(
            title = data.get("title").flatten.map(_.toString),
            description = data.get("description").flatten.map(_.toString),
            priority = priority,
            dueDate = data.get("dueDate").flatten.flatMap(_.toString.toLongOption)
          )
          
          val result = taskService.updateTask(taskId, updates)
          result match {
            case Right(task) =>
              HttpResponse(200, Map("Content-Type" -> "application/json"), toJson(task))
            case Left(NotFoundError(message)) =>
              HttpResponse(404, Map("Content-Type" -> "application/json"), 
                toJson(Map("error" -> "Not Found", "message" -> message)))
            case Left(error) =>
              HttpResponse(500, Map("Content-Type" -> "application/json"), 
                toJson(Map("error" -> "Internal Error", "message" -> error.toString)))
          }
        case None =>
          HttpResponse(400, Map("Content-Type" -> "application/json"), """{"error": "Invalid JSON"}""")
      }
    }
    
    private def handleChangeTaskStatus(taskId: String, request: HttpRequest): HttpResponse = {
      import JsonHelper._
      request.body.flatMap(fromJson[Map[String, String]](_).toOption) match {
        case Some(data) =>
          val statusStr = data.getOrElse("status", "Todo")
          val status = statusStr match {
            case "InProgress" => TaskStatus.InProgress
            case "Done" => TaskStatus.Done
            case _ => TaskStatus.Todo
          }
          
          val result = taskService.changeTaskStatus(taskId, status)
          result match {
            case Right(task) =>
              HttpResponse(200, Map("Content-Type" -> "application/json"), toJson(task))
            case Left(NotFoundError(message)) =>
              HttpResponse(404, Map("Content-Type" -> "application/json"), 
                toJson(Map("error" -> "Not Found", "message" -> message)))
            case Left(error) =>
              HttpResponse(500, Map("Content-Type" -> "application/json"), 
                toJson(Map("error" -> "Internal Error", "message" -> error.toString)))
          }
        case None =>
          HttpResponse(400, Map("Content-Type" -> "application/json"), """{"error": "Invalid JSON"}""")
      }
    }
    
    private def handleGetTasks(request: HttpRequest): HttpResponse = {
      import JsonHelper._
      // 解析查询参数
      val params = parseQueryParams(request.path)
      val page = params.get("page").flatMap(_.toIntOption).getOrElse(0)
      val size = params.get("size").flatMap(_.toIntOption).getOrElse(20)
      
      val pageable = PageRequest(page, size)
      // 根据查询参数决定调用哪个服务方法
      val projectIdOpt = params.get("projectId")
      val assigneeIdOpt = params.get("assigneeId")
      
      val result = (projectIdOpt, assigneeIdOpt) match {
        case (Some(projectId), _) =>
          taskService.getTasksByProject(projectId, pageable)
        case (_, Some(assigneeId)) =>
          taskService.getTasksByAssignee(assigneeId, pageable)
        case _ =>
          // 默认获取所有任务
          try {
            val repo = new InMemoryTaskRepository
            Right(repo.findTasksWithPagination(pageable))
          } catch {
            case e: Exception => Left(InternalError(e.getMessage))
          }
      }
      
      result match {
        case Right(pageData) =>
          HttpResponse(200, Map("Content-Type" -> "application/json"), toJson(pageData))
        case Left(NotFoundError(message)) =>
          HttpResponse(404, Map("Content-Type" -> "application/json"), 
            toJson(Map("error" -> "Not Found", "message" -> message)))
        case Left(error) =>
          HttpResponse(500, Map("Content-Type" -> "application/json"), 
            toJson(Map("error" -> "Internal Error", "message" -> error.toString)))
      }
    }
    
    private def handleGetTask(taskId: String): HttpResponse = {
      import JsonHelper._
      val result = taskService.getTask(taskId)
      
      result match {
        case Right(task) =>
          HttpResponse(200, Map("Content-Type" -> "application/json"), toJson(task))
        case Left(NotFoundError(message)) =>
          HttpResponse(404, Map("Content-Type" -> "application/json"), 
            toJson(Map("error" -> "Not Found", "message" -> message)))
        case Left(error) =>
          HttpResponse(500, Map("Content-Type" -> "application/json"), 
            toJson(Map("error" -> "Internal Error", "message" -> error.toString)))
      }
    }
    
    private def parseQueryParams(path: String): Map[String, String] = {
      if (path.contains("?")) {
        val queryParams = path.split("\\?", 2)(1)
        queryParams.split("&").map { param =>
          val parts = param.split("=", 2)
          if (parts.length == 2) (parts(0), parts(1)) else (parts(0), "")
        }.toMap
      } else {
        Map.empty
      }
    }
  }
  
  // 12. HTTP服务器模拟
  class HttpServer(port: Int) {
    private val router = new Router()
    private val middlewares = scala.collection.mutable.ListBuffer[Middleware]()
    
    def addRoute(route: Route): Unit = {
      router.addRoute(route)
    }
    
    def use(middleware: Middleware): Unit = {
      middlewares += middleware
    }
    
    def start(): Unit = {
      println(s"服务器启动在端口 $port")
      println("可用端点:")
      println("  POST /users/register - 注册用户")
      println("  PUT /users/{id} - 更新用户")
      println("  GET /users - 获取用户列表")
      println("  GET /users/{id} - 获取用户详情")
      println("  POST /projects - 创建项目")
      println("  PUT /projects/{id} - 更新项目")
      println("  GET /projects - 获取项目列表")
      println("  GET /projects/{id} - 获取项目详情")
      println("  POST /tasks - 创建任务")
      println("  PUT /tasks/{id} - 更新任务")
      println("  PUT /tasks/{id}/status - 更改任务状态")
      println("  GET /tasks - 获取任务列表")
      println("  GET /tasks/{id} - 获取任务详情")
      println("\n注意: 这只是一个模拟服务器，不会真正监听端口")
    }
    
    // 模拟处理请求的方法
    def handleRequest(request: HttpRequest): HttpResponse = {
      // 应用中间件
      val handler = middlewares.reverse.foldLeft(router.handle _)(_ apply _)
      handler(request)
    }
  }
  
  // 13. 使用示例
  def main(args: Array[String]): Unit = {
    println("=== Web API层示例 ===")
    
    // 创建Repository实例
    val userRepo = new InMemoryUserRepository
    val projectRepo = new InMemoryProjectRepository
    val taskRepo = new InMemoryTaskRepository
    val notificationRepo = new InMemoryNotificationRepository
    val transactionManager = new SimpleTransactionManager
    
    // 创建Service实例
    val userService = new UserServiceImpl(userRepo, transactionManager)
    val projectService = new ProjectServiceImpl(projectRepo, userRepo, transactionManager)
    val taskService = new TaskServiceImpl(taskRepo, userRepo, projectRepo, transactionManager)
    val notificationService = new NotificationServiceImpl(notificationRepo, userRepo)
    
    // 创建API路由
    val userRoutes = new UserRoutes(userService)
    val projectRoutes = new ProjectRoutes(projectService)
    val taskRoutes = new TaskRoutes(taskService)
    
    // 创建服务器
    val server = new HttpServer(8080)
    
    // 添加路由
    server.addRoute(userRoutes)
    server.addRoute(projectRoutes)
    server.addRoute(taskRoutes)
    
    // 添加中间件
    server.use(new LoggingMiddleware())
    server.use(new ErrorHandlingMiddleware())
    server.use(new AuthMiddleware())
    
    // 启动服务器
    server.start()
    
    // 模拟一些请求
    println("\n--- 模拟API请求 ---")
    
    // 1. 用户注册
    println("\n1. 用户注册请求:")
    val registerRequest = HttpRequest(
      "POST",
      "/users/register",
      Map("Content-Type" -> "application/json"),
      Some("""{"username": "bob", "email": "bob@example.com", "firstName": "Bob", "lastName": "Johnson"}""")
    )
    
    val registerResponse = server.handleRequest(registerRequest)
    println(s"响应状态码: ${registerResponse.statusCode}")
    println(s"响应体: ${registerResponse.body}")
    
    // 2. 获取用户列表
    println("\n2. 获取用户列表请求:")
    val getUsersRequest = HttpRequest(
      "GET",
      "/users?page=0&size=10",
      Map("Content-Type" -> "application/json", "Authorization" -> "Bearer token123"),
      None
    )
    
    val getUsersResponse = server.handleRequest(getUsersRequest)
    println(s"响应状态码: ${getUsersResponse.statusCode}")
    println(s"响应体: ${getUsersResponse.body}")
    
    // 3. 创建项目
    println("\n3. 创建项目请求:")
    val createProjectRequest = HttpRequest(
      "POST",
      "/projects",
      Map("Content-Type" -> "application/json", "Authorization" -> "Bearer token123", "X-User-ID" -> "user-001"),
      Some("""{"name": "API开发", "description": "Web API开发项目"}""")
    )
    
    val createProjectResponse = server.handleRequest(createProjectRequest)
    println(s"响应状态码: ${createProjectResponse.statusCode}")
    println(s"响应体: ${createProjectResponse.body}")
    
    println("\n所有Web API层示例完成")
    println("\n注意: 在实际应用中，你需要使用真正的Web框架如Akka HTTP、Play Framework或http4s来实现API。")
  }
}