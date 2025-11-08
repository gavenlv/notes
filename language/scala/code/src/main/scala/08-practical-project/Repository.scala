package taskflow

// 数据访问层实现
object Repository {
  
  // 1. 基础Repository特质
  trait Repository[T] {
    def findById(id: String): Option[T]
    def findAll(): List[T]
    def save(entity: T): T
    def delete(id: String): Boolean
  }
  
  // 2. 分页和排序支持
  case class Page[T](
    content: List[T],
    page: Int,
    size: Int,
    totalElements: Long
  ) {
    def totalPages: Int = math.ceil(totalElements.toDouble / size).toInt
    def hasNext: Boolean = page < totalPages - 1
    def hasPrevious: Boolean = page > 0
  }
  
  trait Pageable {
    def page: Int
    def size: Int
    def sortBy: Option[String]
    def sortOrder: Option[String] // asc or desc
  }
  
  case class PageRequest(
    page: Int = 0,
    size: Int = 20,
    sortBy: Option[String] = None,
    sortOrder: Option[String] = Some("asc")
  ) extends Pageable
  
  // 3. 查询DSL特质
  trait Query[T] {
    def filter(predicate: T => Boolean): Query[T]
    def map[R](f: T => R): Query[R]
    def sortBy[U](f: T => U)(implicit ord: Ordering[U]): Query[T]
    def limit(n: Int): Query[T]
    def offset(n: Int): Query[T]
    def result(): List[T]
  }
  
  // 4. 用户Repository
  import DomainModel._
  
  trait UserRepository extends Repository[User] {
    def findByUsername(username: Username): Option[User]
    def findByEmail(email: Email): Option[User]
    def findByProjectId(projectId: ProjectId): List[User]
    def findByTeamId(teamId: TeamId): List[User]
    def findActiveUsers(pageable: PageRequest): Page[User]
  }
  
  // 5. 内存中的用户Repository实现
  class InMemoryUserRepository extends UserRepository {
    private val users = scala.collection.mutable.Map[String, User]()
    
    def findById(id: String): Option[User] = users.get(id)
    
    def findAll(): List[User] = users.values.toList
    
    def save(entity: User): User = {
      users(entity.id.value) = entity
      entity
    }
    
    def delete(id: String): Boolean = users.remove(id).isDefined
    
    def findByUsername(username: Username): Option[User] = 
      users.values.find(_.username == username)
    
    def findByEmail(email: Email): Option[User] = 
      users.values.find(_.profile.email == email)
    
    def findByProjectId(projectId: ProjectId): List[User] = 
      users.values.filter(_.id.value.startsWith("user-")).toList
    
    def findByTeamId(teamId: TeamId): List[User] = 
      users.values.filter(_.id.value.startsWith("user-")).toList
    
    def findActiveUsers(pageable: PageRequest): Page[User] = {
      val activeUsers = users.values.filter(_.isActive).toList
      val totalElements = activeUsers.length
      val start = pageable.page * pageable.size
      val end = math.min(start + pageable.size, totalElements)
      val pageContent = activeUsers.slice(start, end)
      
      Page(pageContent, pageable.page, pageable.size, totalElements)
    }
  }
  
  // 6. 任务Repository
  trait TaskRepository extends Repository[Task] {
    def findByProjectId(projectId: ProjectId): List[Task]
    def findByAssigneeId(assigneeId: UserId): List[Task]
    def findByStatus(status: TaskStatus.TaskStatus): List[Task]
    def findByPriority(priority: Priority.Priority): List[Task]
    def findOverdueTasks(): List[Task]
    def findTasksByProjectAndStatus(projectId: ProjectId, status: TaskStatus.TaskStatus): List[Task]
    def findTasksWithPagination(pageable: PageRequest): Page[Task]
  }
  
  // 7. 内存中的任务Repository实现
  class InMemoryTaskRepository extends TaskRepository {
    private val tasks = scala.collection.mutable.Map[String, Task]()
    
    def findById(id: String): Option[Task] = tasks.get(id)
    
    def findAll(): List[Task] = tasks.values.toList
    
    def save(entity: Task): Task = {
      tasks(entity.id.value) = entity
      entity
    }
    
    def delete(id: String): Boolean = tasks.remove(id).isDefined
    
    def findByProjectId(projectId: ProjectId): List[Task] = 
      tasks.values.filter(_.projectId == projectId).toList
    
    def findByAssigneeId(assigneeId: UserId): List[Task] = 
      tasks.values.filter(_.assignee.contains(assigneeId)).toList
    
    def findByStatus(status: TaskStatus.TaskStatus): List[Task] = 
      tasks.values.filter(_.status == status).toList
    
    def findByPriority(priority: Priority.Priority): List[Task] = 
      tasks.values.filter(_.priority == priority).toList
    
    def findOverdueTasks(): List[Task] = {
      val now = System.currentTimeMillis()
      tasks.values.filter(task => 
        task.dueDate.exists(_ < now) && task.status != TaskStatus.Done
      ).toList
    }
    
    def findTasksByProjectAndStatus(projectId: ProjectId, status: TaskStatus.TaskStatus): List[Task] = 
      tasks.values.filter(task => 
        task.projectId == projectId && task.status == status
      ).toList
    
    def findTasksWithPagination(pageable: PageRequest): Page[Task] = {
      val allTasks = tasks.values.toList
      val totalElements = allTasks.length
      val start = pageable.page * pageable.size
      val end = math.min(start + pageable.size, totalElements)
      val pageContent = allTasks.slice(start, end)
      
      Page(pageContent, pageable.page, pageable.size, totalElements)
    }
  }
  
  // 8. 项目Repository
  trait ProjectRepository extends Repository[Project] {
    def findByName(name: String): Option[Project]
    def findByOwnerId(ownerId: UserId): List[Project]
    def findActiveProjects(pageable: PageRequest): Page[Project]
  }
  
  // 9. 内存中的项目Repository实现
  class InMemoryProjectRepository extends ProjectRepository {
    private val projects = scala.collection.mutable.Map[String, Project]()
    
    def findById(id: String): Option[Project] = projects.get(id)
    
    def findAll(): List[Project] = projects.values.toList
    
    def save(entity: Project): Project = {
      projects(entity.id.value) = entity
      entity
    }
    
    def delete(id: String): Boolean = projects.remove(id).isDefined
    
    def findByName(name: String): Option[Project] = 
      projects.values.find(_.name == name)
    
    def findByOwnerId(ownerId: UserId): List[Project] = 
      projects.values.filter(_.ownerId == ownerId).toList
    
    def findActiveProjects(pageable: PageRequest): Page[Project] = {
      val activeProjects = projects.values.filter(_.isActive).toList
      val totalElements = activeProjects.length
      val start = pageable.page * pageable.size
      val end = math.min(start + pageable.size, totalElements)
      val pageContent = activeProjects.slice(start, end)
      
      Page(pageContent, pageable.page, pageable.size, totalElements)
    }
  }
  
  // 10. 团队Repository
  trait TeamRepository extends Repository[Team] {
    def findByName(name: String): Option[Team]
    def findByOwnerId(ownerId: UserId): List[Team]
    def findTeamsByUserId(userId: UserId): List[Team]
  }
  
  // 11. 内存中的团队Repository实现
  class InMemoryTeamRepository extends TeamRepository {
    private val teams = scala.collection.mutable.Map[String, Team]()
    private val memberships = scala.collection.mutable.Map[(UserId, TeamId), Membership]()
    
    def findById(id: String): Option[Team] = teams.get(id)
    
    def findAll(): List[Team] = teams.values.toList
    
    def save(entity: Team): Team = {
      teams(entity.id.value) = entity
      entity
    }
    
    def delete(id: String): Boolean = teams.remove(id).isDefined
    
    def findByName(name: String): Option[Team] = 
      teams.values.find(_.name == name)
    
    def findByOwnerId(ownerId: UserId): List[Team] = 
      teams.values.filter(_.ownerId == ownerId).toList
    
    def findTeamsByUserId(userId: UserId): List[Team] = {
      val teamIds = memberships.collect {
        case ((uId, teamId), _) if uId == userId => teamId
      }.toSet
      
      teams.values.filter(team => teamIds.contains(team.id)).toList
    }
    
    // Membership相关方法
    def saveMembership(membership: Membership): Unit = {
      memberships((membership.userId, membership.teamId)) = membership
    }
    
    def findMembershipsByTeamId(teamId: TeamId): List[Membership] = {
      memberships.values.filter(_.teamId == teamId).toList
    }
  }
  
  // 12. 通知Repository
  trait NotificationRepository extends Repository[Notification] {
    def findByUserId(userId: UserId): List[Notification]
    def findUnreadByUserId(userId: UserId): List[Notification]
    def markAsRead(notificationId: NotificationId): Boolean
    def findRecentNotifications(userId: UserId, limit: Int): List[Notification]
  }
  
  // 13. 内存中的通知Repository实现
  class InMemoryNotificationRepository extends NotificationRepository {
    private val notifications = scala.collection.mutable.Map[String, Notification]()
    
    def findById(id: String): Option[Notification] = notifications.get(id)
    
    def findAll(): List[Notification] = notifications.values.toList
    
    def save(entity: Notification): Notification = {
      notifications(entity.id.value) = entity
      entity
    }
    
    def delete(id: String): Boolean = notifications.remove(id).isDefined
    
    def findByUserId(userId: UserId): List[Notification] = 
      notifications.values.filter(_.userId == userId).toList
    
    def findUnreadByUserId(userId: UserId): List[Notification] = 
      notifications.values.filter(n => n.userId == userId && !n.isRead).toList
    
    def markAsRead(notificationId: NotificationId): Boolean = {
      notifications.get(notificationId.value) match {
        case Some(notification) =>
          val updated = notification.copy(isRead = true)
          notifications(notificationId.value) = updated
          true
        case None => false
      }
    }
    
    def findRecentNotifications(userId: UserId, limit: Int): List[Notification] = {
      notifications.values
        .filter(_.userId == userId)
        .toList
        .sortBy(_.createdAt)(Ordering.Long.reverse)
        .take(limit)
    }
  }
  
  // 14. 事务管理器
  trait TransactionManager {
    def withTransaction[T](operation: => T): T
    def beginTransaction(): Unit
    def commit(): Unit
    def rollback(): Unit
  }
  
  // 15. 简单的事务管理器实现
  class SimpleTransactionManager extends TransactionManager {
    private var transactionActive = false
    
    def withTransaction[T](operation: => T): T = {
      beginTransaction()
      try {
        val result = operation
        commit()
        result
      } catch {
        case e: Exception =>
          rollback()
          throw e
      }
    }
    
    def beginTransaction(): Unit = {
      if (transactionActive) {
        throw new IllegalStateException("Transaction already active")
      }
      transactionActive = true
      println("Transaction started")
    }
    
    def commit(): Unit = {
      if (!transactionActive) {
        throw new IllegalStateException("No active transaction")
      }
      transactionActive = false
      println("Transaction committed")
    }
    
    def rollback(): Unit = {
      if (!transactionActive) {
        throw new IllegalStateException("No active transaction")
      }
      transactionActive = false
      println("Transaction rolled back")
    }
  }
  
  // 16. 使用示例
  def main(args: Array[String]): Unit = {
    println("=== 数据访问层示例 ===")
    
    // 创建Repository实例
    val userRepo = new InMemoryUserRepository
    val taskRepo = new InMemoryTaskRepository
    val projectRepo = new InMemoryProjectRepository
    val teamRepo = new InMemoryTeamRepository
    val notificationRepo = new InMemoryNotificationRepository
    val transactionManager = new SimpleTransactionManager
    
    // 创建测试数据
    import DomainModel._
    
    val userId = UserId("user-001")
    val username = Username("alice")
    val email = Email("alice@example.com")
    val profile = UserProfile("Alice", "Smith", email, Some("+1234567890"), None)
    val user = User(userId, username, profile, System.currentTimeMillis())
    
    val projectId = ProjectId("project-001")
    val project = Project(
      projectId, 
      "TaskFlow Development", 
      Some("Task management system development"), 
      userId, 
      System.currentTimeMillis(), 
      System.currentTimeMillis()
    )
    
    val taskId = TaskId("task-001")
    val task = Task(
      taskId,
      "Implement domain model",
      Some("Create all domain models for the task management system"),
      Priority.High,
      TaskStatus.Todo,
      Some(userId),
      userId,
      projectId,
      Some(System.currentTimeMillis() + 7 * 24 * 60 * 60 * 1000),
      System.currentTimeMillis(),
      System.currentTimeMillis()
    )
    
    // 保存数据
    userRepo.save(user)
    projectRepo.save(project)
    taskRepo.save(task)
    
    println("数据保存完成")
    
    // 查询数据
    println("\n--- 查询用户 ---")
    userRepo.findById("user-001") match {
      case Some(u) => println(s"找到用户: ${u.displayName}")
      case None => println("未找到用户")
    }
    
    println("\n--- 查询项目 ---")
    projectRepo.findByName("TaskFlow Development") match {
      case Some(p) => println(s"找到项目: ${p.name}")
      case None => println("未找到项目")
    }
    
    println("\n--- 查询任务 ---")
    val tasks = taskRepo.findByProjectId(projectId)
    println(s"项目中的任务数量: ${tasks.length}")
    tasks.foreach(t => println(s"  - ${t.title} (${t.status})"))
    
    // 分页查询
    println("\n--- 分页查询任务 ---")
    val pageRequest = PageRequest(0, 10, Some("createdAt"), Some("desc"))
    val taskPage = taskRepo.findTasksWithPagination(pageRequest)
    println(s"任务分页结果: 第${taskPage.page + 1}页，共${taskPage.totalPages}页，总计${taskPage.totalElements}条")
    taskPage.content.foreach(t => println(s"  - ${t.title}"))
    
    // 事务示例
    println("\n--- 事务示例 ---")
    try {
      transactionManager.withTransaction {
        // 在事务中执行操作
        val newUser = user.copy(isActive = false)
        userRepo.save(newUser)
        println("在事务中更新了用户状态")
        
        // 模拟异常情况
        // throw new RuntimeException("模拟异常")
      }
      println("事务成功提交")
    } catch {
      case e: Exception =>
        println(s"事务回滚，原因: ${e.getMessage}")
    }
    
    // 验证数据
    userRepo.findById("user-001") match {
      case Some(u) => println(s"用户状态: ${if (u.isActive) "活跃" else "非活跃"}")
      case None => println("未找到用户")
    }
    
    println("\n所有数据访问层示例完成")
  }
}