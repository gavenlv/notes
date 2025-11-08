package taskflow

// 业务逻辑层实现
object Service {
  
  // 1. 基础服务特质
  trait Service[T] {
    def validate(entity: T): Either[List[String], T]
    def transform(entity: T): T
  }
  
  // 2. 错误处理和验证
  sealed trait ServiceError
  case class ValidationError(messages: List[String]) extends ServiceError
  case class NotFoundError(message: String) extends ServiceError
  case class ConflictError(message: String) extends ServiceError
  case class InternalError(message: String) extends ServiceError
  
  // 3. 服务结果类型
  type ServiceResult[T] = Either[ServiceError, T]
  
  // 4. 用户服务
  import DomainModel._
  import Repository._
  
  trait UserService {
    def registerUser(username: String, email: String, firstName: String, lastName: String): ServiceResult[User]
    def updateUser(userId: String, updates: UserUpdate): ServiceResult[User]
    def deactivateUser(userId: String): ServiceResult[Boolean]
    def getUser(userId: String): ServiceResult[User]
    def authenticate(username: String, password: String): ServiceResult[User]
    def changePassword(userId: String, oldPassword: String, newPassword: String): ServiceResult[Boolean]
    def getUsers(pageable: PageRequest): ServiceResult[Page[User]]
  }
  
  // 5. 用户更新数据类
  case class UserUpdate(
    firstName: Option[String] = None,
    lastName: Option[String] = None,
    email: Option[String] = None,
    phone: Option[String] = None
  )
  
  // 6. 用户服务实现
  class UserServiceImpl(
    userRepository: UserRepository,
    transactionManager: TransactionManager
  ) extends UserService {
    
    def registerUser(username: String, email: String, firstName: String, lastName: String): ServiceResult[User] = {
      // 验证输入
      val validationErrors = List.newBuilder[String]
      
      if (username.isEmpty) validationErrors += "用户名不能为空"
      if (email.isEmpty || !email.contains("@")) validationErrors += "邮箱格式不正确"
      if (firstName.isEmpty) validationErrors += "名字不能为空"
      if (lastName.isEmpty) validationErrors += "姓氏不能为空"
      
      val errors = validationErrors.result()
      if (errors.nonEmpty) {
        return Left(ValidationError(errors))
      }
      
      // 检查用户名和邮箱是否已存在
      val usernameObj = Username(username)
      val emailObj = Email(email)
      
      userRepository.findByUsername(usernameObj) match {
        case Some(_) => Left(ConflictError(s"用户名 '$username' 已存在"))
        case None =>
          userRepository.findByEmail(emailObj) match {
            case Some(_) => Left(ConflictError(s"邮箱 '$email' 已被使用"))
            case None =>
              // 创建新用户
              val userId = UserId(s"user-${System.currentTimeMillis()}")
              val profile = UserProfile(firstName, lastName, emailObj, None, None)
              val user = User(userId, usernameObj, profile, System.currentTimeMillis())
              
              val savedUser = userRepository.save(user)
              Right(savedUser)
          }
      }
    }
    
    def updateUser(userId: String, updates: UserUpdate): ServiceResult[User] = {
      userRepository.findById(userId) match {
        case None => Left(NotFoundError(s"用户ID '$userId' 不存在"))
        case Some(user) =>
          // 应用更新
          val updatedProfile = user.profile.copy(
            firstName = updates.firstName.getOrElse(user.profile.firstName),
            lastName = updates.lastName.getOrElse(user.profile.lastName),
            email = updates.email.map(Email(_)).getOrElse(user.profile.email),
            phone = updates.phone.orElse(user.profile.phone)
          )
          
          val updatedUser = user.copy(profile = updatedProfile)
          val savedUser = userRepository.save(updatedUser)
          Right(savedUser)
      }
    }
    
    def deactivateUser(userId: String): ServiceResult[Boolean] = {
      userRepository.findById(userId) match {
        case None => Left(NotFoundError(s"用户ID '$userId' 不存在"))
        case Some(user) =>
          val deactivatedUser = user.copy(isActive = false)
          userRepository.save(deactivatedUser)
          Right(true)
      }
    }
    
    def getUser(userId: String): ServiceResult[User] = {
      userRepository.findById(userId) match {
        case None => Left(NotFoundError(s"用户ID '$userId' 不存在"))
        case Some(user) => Right(user)
      }
    }
    
    def authenticate(username: String, password: String): ServiceResult[User] = {
      // 在实际应用中，这里会进行密码验证
      // 为了简化示例，我们只检查用户是否存在
      val usernameObj = Username(username)
      userRepository.findByUsername(usernameObj) match {
        case None => Left(NotFoundError(s"用户名 '$username' 不存在"))
        case Some(user) => Right(user)
      }
    }
    
    def changePassword(userId: String, oldPassword: String, newPassword: String): ServiceResult[Boolean] = {
      // 在实际应用中，这里会验证旧密码并更新新密码
      // 为了简化示例，我们假设操作总是成功
      userRepository.findById(userId) match {
        case None => Left(NotFoundError(s"用户ID '$userId' 不存在"))
        case Some(_) => Right(true)
      }
    }
    
    def getUsers(pageable: PageRequest): ServiceResult[Page[User]] = {
      try {
        val page = userRepository.findActiveUsers(pageable)
        Right(page)
      } catch {
        case e: Exception => Left(InternalError(s"获取用户列表失败: ${e.getMessage}"))
      }
    }
  }
  
  // 7. 项目服务
  trait ProjectService {
    def createProject(name: String, description: Option[String], ownerId: String): ServiceResult[Project]
    def updateProject(projectId: String, updates: ProjectUpdate): ServiceResult[Project]
    def getProject(projectId: String): ServiceResult[Project]
    def getProjectsByOwner(ownerId: String, pageable: PageRequest): ServiceResult[Page[Project]]
    def addMemberToProject(projectId: String, userId: String): ServiceResult[Boolean]
    def removeMemberFromProject(projectId: String, userId: String): ServiceResult[Boolean]
  }
  
  // 8. 项目更新数据类
  case class ProjectUpdate(
    name: Option[String] = None,
    description: Option[String] = None
  )
  
  // 9. 项目服务实现
  class ProjectServiceImpl(
    projectRepository: ProjectRepository,
    userRepository: UserRepository,
    transactionManager: TransactionManager
  ) extends ProjectService {
    
    def createProject(name: String, description: Option[String], ownerId: String): ServiceResult[Project] = {
      // 验证输入
      if (name.isEmpty) {
        return Left(ValidationError(List("项目名称不能为空")))
      }
      
      // 验证所有者是否存在
      userRepository.findById(ownerId) match {
        case None => Left(NotFoundError(s"用户ID '$ownerId' 不存在"))
        case Some(_) =>
          // 创建项目
          val projectId = ProjectId(s"project-${System.currentTimeMillis()}")
          val project = Project(
            projectId,
            name,
            description,
            UserId(ownerId),
            System.currentTimeMillis(),
            System.currentTimeMillis()
          )
          
          val savedProject = projectRepository.save(project)
          Right(savedProject)
      }
    }
    
    def updateProject(projectId: String, updates: ProjectUpdate): ServiceResult[Project] = {
      projectRepository.findById(projectId) match {
        case None => Left(NotFoundError(s"项目ID '$projectId' 不存在"))
        case Some(project) =>
          val updatedProject = project.copy(
            name = updates.name.getOrElse(project.name),
            description = updates.description.orElse(project.description),
            updatedAt = System.currentTimeMillis()
          )
          
          val savedProject = projectRepository.save(updatedProject)
          Right(savedProject)
      }
    }
    
    def getProject(projectId: String): ServiceResult[Project] = {
      projectRepository.findById(projectId) match {
        case None => Left(NotFoundError(s"项目ID '$projectId' 不存在"))
        case Some(project) => Right(project)
      }
    }
    
    def getProjectsByOwner(ownerId: String, pageable: PageRequest): ServiceResult[Page[Project]] = {
      userRepository.findById(ownerId) match {
        case None => Left(NotFoundError(s"用户ID '$ownerId' 不存在"))
        case Some(_) =>
          try {
            val page = projectRepository.findActiveProjects(pageable)
            Right(page)
          } catch {
            case e: Exception => Left(InternalError(s"获取项目列表失败: ${e.getMessage}"))
          }
      }
    }
    
    def addMemberToProject(projectId: String, userId: String): ServiceResult[Boolean] = {
      for {
        _ <- projectRepository.findById(projectId).toRight(NotFoundError(s"项目ID '$projectId' 不存在"))
        _ <- userRepository.findById(userId).toRight(NotFoundError(s"用户ID '$userId' 不存在"))
      } yield {
        // 在实际应用中，这里会将用户添加到项目的成员列表中
        // 为了简化示例，我们返回true表示成功
        true
      }
    }
    
    def removeMemberFromProject(projectId: String, userId: String): ServiceResult[Boolean] = {
      for {
        _ <- projectRepository.findById(projectId).toRight(NotFoundError(s"项目ID '$projectId' 不存在"))
        _ <- userRepository.findById(userId).toRight(NotFoundError(s"用户ID '$userId' 不存在"))
      } yield {
        // 在实际应用中，这里会将用户从项目的成员列表中移除
        // 为了简化示例，我们返回true表示成功
        true
      }
    }
  }
  
  // 10. 任务服务
  trait TaskService {
    def createTask(title: String, description: Option[String], priority: Priority.Priority, 
                   assigneeId: Option[String], reporterId: String, projectId: String): ServiceResult[Task]
    def updateTask(taskId: String, updates: TaskUpdate): ServiceResult[Task]
    def getTask(taskId: String): ServiceResult[Task]
    def getTasksByProject(projectId: String, pageable: PageRequest): ServiceResult[Page[Task]]
    def getTasksByAssignee(assigneeId: String, pageable: PageRequest): ServiceResult[Page[Task]]
    def changeTaskStatus(taskId: String, status: TaskStatus.TaskStatus): ServiceResult[Task]
    def assignTask(taskId: String, assigneeId: String): ServiceResult[Task]
    def getOverdueTasks(): ServiceResult[List[Task]]
  }
  
  // 11. 任务更新数据类
  case class TaskUpdate(
    title: Option[String] = None,
    description: Option[String] = None,
    priority: Option[Priority.Priority] = None,
    dueDate: Option[Long] = None
  )
  
  // 12. 任务服务实现
  class TaskServiceImpl(
    taskRepository: TaskRepository,
    userRepository: UserRepository,
    projectRepository: ProjectRepository,
    transactionManager: TransactionManager
  ) extends TaskService {
    
    def createTask(title: String, description: Option[String], priority: Priority.Priority,
                   assigneeId: Option[String], reporterId: String, projectId: String): ServiceResult[Task] = {
      // 验证输入
      if (title.isEmpty) {
        return Left(ValidationError(List("任务标题不能为空")))
      }
      
      // 验证相关人员和项目是否存在
      val reporterValidation = userRepository.findById(reporterId) match {
        case None => Left(NotFoundError(s"报告人ID '$reporterId' 不存在"))
        case Some(_) => Right(())
      }
      
      val assigneeValidation = assigneeId match {
        case Some(id) => userRepository.findById(id) match {
          case None => Left(NotFoundError(s"指派人ID '$id' 不存在"))
          case Some(_) => Right(())
        }
        case None => Right(())
      }
      
      val projectValidation = projectRepository.findById(projectId) match {
        case None => Left(NotFoundError(s"项目ID '$projectId' 不存在"))
        case Some(_) => Right(())
      }
      
      // 合并验证结果
      val validations = List(reporterValidation, assigneeValidation, projectValidation)
      val errors = validations.collect { case Left(error) => error }
      
      if (errors.nonEmpty) {
        return Left(errors.head) // 返回第一个错误
      }
      
      // 创建任务
      val taskId = TaskId(s"task-${System.currentTimeMillis()}")
      val task = Task(
        taskId,
        title,
        description,
        priority,
        TaskStatus.Todo,
        assigneeId.map(UserId(_)),
        UserId(reporterId),
        ProjectId(projectId),
        None, // dueDate将在后续更新中设置
        System.currentTimeMillis(),
        System.currentTimeMillis()
      )
      
      val savedTask = taskRepository.save(task)
      Right(savedTask)
    }
    
    def updateTask(taskId: String, updates: TaskUpdate): ServiceResult[Task] = {
      taskRepository.findById(taskId) match {
        case None => Left(NotFoundError(s"任务ID '$taskId' 不存在"))
        case Some(task) =>
          val updatedTask = task.copy(
            title = updates.title.getOrElse(task.title),
            description = updates.description.orElse(task.description),
            priority = updates.priority.getOrElse(task.priority),
            dueDate = updates.dueDate.orElse(task.dueDate),
            updatedAt = System.currentTimeMillis()
          )
          
          val savedTask = taskRepository.save(updatedTask)
          Right(savedTask)
      }
    }
    
    def getTask(taskId: String): ServiceResult[Task] = {
      taskRepository.findById(taskId) match {
        case None => Left(NotFoundError(s"任务ID '$taskId' 不存在"))
        case Some(task) => Right(task)
      }
    }
    
    def getTasksByProject(projectId: String, pageable: PageRequest): ServiceResult[Page[Task]] = {
      projectRepository.findById(projectId) match {
        case None => Left(NotFoundError(s"项目ID '$projectId' 不存在"))
        case Some(_) =>
          try {
            val page = taskRepository.findTasksWithPagination(pageable)
            Right(page)
          } catch {
            case e: Exception => Left(InternalError(s"获取任务列表失败: ${e.getMessage}"))
          }
      }
    }
    
    def getTasksByAssignee(assigneeId: String, pageable: PageRequest): ServiceResult[Page[Task]] = {
      userRepository.findById(assigneeId) match {
        case None => Left(NotFoundError(s"用户ID '$assigneeId' 不存在"))
        case Some(_) =>
          try {
            val page = taskRepository.findTasksWithPagination(pageable)
            Right(page)
          } catch {
            case e: Exception => Left(InternalError(s"获取任务列表失败: ${e.getMessage}"))
          }
      }
    }
    
    def changeTaskStatus(taskId: String, status: TaskStatus.TaskStatus): ServiceResult[Task] = {
      taskRepository.findById(taskId) match {
        case None => Left(NotFoundError(s"任务ID '$taskId' 不存在"))
        case Some(task) =>
          val updatedTask = task.copy(
            status = status,
            updatedAt = System.currentTimeMillis()
          )
          
          val savedTask = taskRepository.save(updatedTask)
          Right(savedTask)
      }
    }
    
    def assignTask(taskId: String, assigneeId: String): ServiceResult[Task] = {
      for {
        task <- taskRepository.findById(taskId).toRight(NotFoundError(s"任务ID '$taskId' 不存在"))
        _ <- userRepository.findById(assigneeId).toRight(NotFoundError(s"用户ID '$assigneeId' 不存在"))
      } yield {
        val updatedTask = task.copy(
          assignee = Some(UserId(assigneeId)),
          updatedAt = System.currentTimeMillis()
        )
        
        taskRepository.save(updatedTask)
      }
    }
    
    def getOverdueTasks(): ServiceResult[List[Task]] = {
      try {
        val overdueTasks = taskRepository.findOverdueTasks()
        Right(overdueTasks)
      } catch {
        case e: Exception => Left(InternalError(s"获取逾期任务失败: ${e.getMessage}"))
      }
    }
  }
  
  // 13. 通知服务
  trait NotificationService {
    def sendNotification(userId: String, title: String, content: String, notificationType: String): ServiceResult[Notification]
    def markAsRead(notificationId: String): ServiceResult[Boolean]
    def getUnreadNotifications(userId: String): ServiceResult[List[Notification]]
    def getRecentNotifications(userId: String, limit: Int): ServiceResult[List[Notification]]
  }
  
  // 14. 通知服务实现
  class NotificationServiceImpl(
    notificationRepository: NotificationRepository,
    userRepository: UserRepository
  ) extends NotificationService {
    
    def sendNotification(userId: String, title: String, content: String, notificationType: String): ServiceResult[Notification] = {
      userRepository.findById(userId) match {
        case None => Left(NotFoundError(s"用户ID '$userId' 不存在"))
        case Some(_) =>
          val notificationId = NotificationId(s"notification-${System.currentTimeMillis()}")
          val notification = Notification(
            notificationId,
            UserId(userId),
            title,
            content,
            notificationType,
            false,
            System.currentTimeMillis()
          )
          
          val savedNotification = notificationRepository.save(notification)
          Right(savedNotification)
      }
    }
    
    def markAsRead(notificationId: String): ServiceResult[Boolean] = {
      try {
        val result = notificationRepository.markAsRead(NotificationId(notificationId))
        if (result) {
          Right(true)
        } else {
          Left(NotFoundError(s"通知ID '$notificationId' 不存在"))
        }
      } catch {
        case e: Exception => Left(InternalError(s"标记通知为已读失败: ${e.getMessage}"))
      }
    }
    
    def getUnreadNotifications(userId: String): ServiceResult[List[Notification]] = {
      userRepository.findById(userId) match {
        case None => Left(NotFoundError(s"用户ID '$userId' 不存在"))
        case Some(_) =>
          try {
            val notifications = notificationRepository.findUnreadByUserId(UserId(userId))
            Right(notifications)
          } catch {
            case e: Exception => Left(InternalError(s"获取未读通知失败: ${e.getMessage}"))
          }
      }
    }
    
    def getRecentNotifications(userId: String, limit: Int): ServiceResult[List[Notification]] = {
      userRepository.findById(userId) match {
        case None => Left(NotFoundError(s"用户ID '$userId' 不存在"))
        case Some(_) =>
          try {
            val notifications = notificationRepository.findRecentNotifications(UserId(userId), limit)
            Right(notifications)
          } catch {
            case e: Exception => Left(InternalError(s"获取最近通知失败: ${e.getMessage}"))
          }
      }
    }
  }
  
  // 15. 使用示例
  def main(args: Array[String]): Unit = {
    println("=== 业务逻辑层示例 ===")
    
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
    
    // 注册用户
    println("\n--- 注册用户 ---")
    val userResult = userService.registerUser("alice", "alice@example.com", "Alice", "Smith")
    userResult match {
      case Right(user) => 
        println(s"用户注册成功: ${user.displayName} (${user.username.value})")
        val userId = user.id.value
        
        // 创建项目
        println("\n--- 创建项目 ---")
        val projectResult = projectService.createProject("TaskFlow开发", Some("任务管理系统开发项目"), userId)
        projectResult match {
          case Right(project) =>
            println(s"项目创建成功: ${project.name}")
            val projectId = project.id.value
            
            // 创建任务
            println("\n--- 创建任务 ---")
            val taskResult = taskService.createTask(
              "实现用户服务",
              Some("实现用户注册、登录等功能"),
              Priority.High,
              Some(userId),
              userId,
              projectId
            )
            
            taskResult match {
              case Right(task) =>
                println(s"任务创建成功: ${task.title}")
                
                // 更新任务状态
                println("\n--- 更新任务状态 ---")
                val statusResult = taskService.changeTaskStatus(task.id.value, TaskStatus.InProgress)
                statusResult match {
                  case Right(updatedTask) => println(s"任务状态更新为: ${updatedTask.status}")
                  case Left(error) => println(s"更新任务状态失败: $error")
                }
                
                // 发送通知
                println("\n--- 发送通知 ---")
                val notificationResult = notificationService.sendNotification(
                  userId,
                  "任务分配",
                  s"您有一个新任务: ${task.title}",
                  "TASK_ASSIGNED"
                )
                
                notificationResult match {
                  case Right(notification) => println(s"通知发送成功: ${notification.title}")
                  case Left(error) => println(s"发送通知失败: $error")
                }
                
              case Left(error) => println(s"创建任务失败: $error")
            }
            
          case Left(error) => println(s"创建项目失败: $error")
        }
        
      case Left(error) => println(s"用户注册失败: $error")
    }
    
    // 获取用户信息
    println("\n--- 获取用户信息 ---")
    userResult match {
      case Right(user) =>
        val getResult = userService.getUser(user.id.value)
        getResult match {
          case Right(foundUser) => println(s"找到用户: ${foundUser.displayName}")
          case Left(error) => println(s"获取用户失败: $error")
        }
        
        // 分页获取用户列表
        println("\n--- 分页获取用户列表 ---")
        val pageResult = userService.getUsers(PageRequest(0, 10))
        pageResult match {
          case Right(page) => 
            println(s"用户列表: 共${page.totalElements}个用户")
            page.content.foreach(u => println(s"  - ${u.displayName}"))
          case Left(error) => println(s"获取用户列表失败: $error")
        }
        
      case Left(_) => // 忽略错误情况
    }
    
    println("\n所有业务逻辑层示例完成")
  }
}