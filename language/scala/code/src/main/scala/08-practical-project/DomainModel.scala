package taskflow

// 领域模型定义
object DomainModel {
  
  // 1. 基础类型和值对象
  object Priority extends Enumeration {
    type Priority = Value
    val Low, Medium, High, Critical = Value
  }
  
  object TaskStatus extends Enumeration {
    type TaskStatus = Value
    val Todo, InProgress, Review, Done, Cancelled = Value
  }
  
  // 2. 用户相关模型
  case class UserId(value: String) extends AnyVal
  case class Email(value: String) extends AnyVal
  case class Username(value: String) extends AnyVal
  
  case class UserProfile(
    firstName: String,
    lastName: String,
    email: Email,
    phone: Option[String],
    avatarUrl: Option[String]
  )
  
  case class User(
    id: UserId,
    username: Username,
    profile: UserProfile,
    createdAt: Long,
    isActive: Boolean = true
  ) {
    def fullName: String = s"${profile.firstName} ${profile.lastName}"
    def displayName: String = username.value
  }
  
  // 3. 权限和角色模型
  case class PermissionId(value: String) extends AnyVal
  case class Permission(
    id: PermissionId,
    name: String,
    description: String
  )
  
  case class RoleId(value: String) extends AnyVal
  case class Role(
    id: RoleId,
    name: String,
    permissions: Set[PermissionId]
  )
  
  // 4. 任务相关模型
  case class TaskId(value: String) extends AnyVal
  
  case class Task(
    id: TaskId,
    title: String,
    description: Option[String],
    priority: Priority.Priority,
    status: TaskStatus.TaskStatus,
    assignee: Option[UserId],
    reporter: UserId,
    projectId: ProjectId,
    dueDate: Option[Long],
    createdAt: Long,
    updatedAt: Long
  )
  
  // 5. 项目相关模型
  case class ProjectId(value: String) extends AnyVal
  
  case class Project(
    id: ProjectId,
    name: String,
    description: Option[String],
    ownerId: UserId,
    createdAt: Long,
    updatedAt: Long,
    isActive: Boolean = true
  )
  
  // 6. 团队相关模型
  case class TeamId(value: String) extends AnyVal
  
  case class Team(
    id: TeamId,
    name: String,
    description: Option[String],
    ownerId: UserId,
    createdAt: Long,
    updatedAt: Long
  )
  
  case class Membership(
    userId: UserId,
    teamId: TeamId,
    role: String, // member, admin, owner
    joinedAt: Long
  )
  
  // 7. 通知和消息模型
  case class NotificationId(value: String) extends AnyVal
  
  sealed trait NotificationType
  case object TaskAssigned extends NotificationType
  case object TaskCompleted extends NotificationType
  case object TaskComment extends NotificationType
  case object ProjectUpdate extends NotificationType
  
  case class Notification(
    id: NotificationId,
    userId: UserId,
    `type`: NotificationType,
    title: String,
    message: String,
    isRead: Boolean = false,
    createdAt: Long
  )
  
  case class MessageId(value: String) extends AnyVal
  
  case class Message(
    id: MessageId,
    senderId: UserId,
    receiverId: UserId,
    content: String,
    isRead: Boolean = false,
    sentAt: Long
  )
  
  // 8. 领域事件
  sealed trait DomainEvent {
    def eventId: String
    def timestamp: Long
  }
  
  case class UserRegistered(
    eventId: String,
    timestamp: Long,
    userId: UserId,
    username: Username,
    email: Email
  ) extends DomainEvent
  
  case class UserLoggedIn(
    eventId: String,
    timestamp: Long,
    userId: UserId,
    ipAddress: String
  ) extends DomainEvent
  
  case class TaskCreated(
    eventId: String,
    timestamp: Long,
    taskId: TaskId,
    title: String,
    reporterId: UserId,
    projectId: ProjectId
  ) extends DomainEvent
  
  case class TaskAssigned(
    eventId: String,
    timestamp: Long,
    taskId: TaskId,
    assigneeId: UserId,
    assignedById: UserId
  ) extends DomainEvent
  
  case class TaskStatusChanged(
    eventId: String,
    timestamp: Long,
    taskId: TaskId,
    oldStatus: TaskStatus.TaskStatus,
    newStatus: TaskStatus.TaskStatus,
    changedById: UserId
  ) extends DomainEvent
  
  case class TaskCompleted(
    eventId: String,
    timestamp: Long,
    taskId: TaskId,
    completedById: UserId
  ) extends DomainEvent
  
  case class ProjectCreated(
    eventId: String,
    timestamp: Long,
    projectId: ProjectId,
    name: String,
    ownerId: UserId
  ) extends DomainEvent
  
  case class TeamCreated(
    eventId: String,
    timestamp: Long,
    teamId: TeamId,
    name: String,
    ownerId: UserId
  ) extends DomainEvent
  
  case class UserAddedToTeam(
    eventId: String,
    timestamp: Long,
    userId: UserId,
    teamId: TeamId,
    addedById: UserId
  ) extends DomainEvent
  
  case class NotificationSent(
    eventId: String,
    timestamp: Long,
    notificationId: NotificationId,
    userId: UserId,
    `type`: NotificationType,
    title: String,
    message: String
  ) extends DomainEvent
  
  // 9. 聚合根标记特质
  trait AggregateRoot {
    def id: Any
  }
  
  // 10. 实体标记特质
  trait Entity {
    def id: Any
  }
  
  // 11. 值对象标记特质
  trait ValueObject
  
  // 12. 使用示例
  def main(args: Array[String]): Unit = {
    println("=== 领域模型示例 ===")
    
    // 创建用户
    val userId = UserId("user-001")
    val username = Username("alice")
    val email = Email("alice@example.com")
    val profile = UserProfile("Alice", "Smith", email, Some("+1234567890"), None)
    val user = User(userId, username, profile, System.currentTimeMillis())
    
    println(s"User: ${user.displayName} (${user.fullName})")
    println(s"Email: ${user.profile.email.value}")
    
    // 创建项目
    val projectId = ProjectId("project-001")
    val project = Project(
      projectId, 
      "TaskFlow Development", 
      Some("Task management system development"), 
      userId, 
      System.currentTimeMillis(), 
      System.currentTimeMillis()
    )
    
    println(s"Project: ${project.name}")
    println(s"Owner: ${project.ownerId.value}")
    
    // 创建任务
    val taskId = TaskId("task-001")
    val task = Task(
      taskId,
      "Implement domain model",
      Some("Create all domain models for the task management system"),
      Priority.High,
      TaskStatus.Todo,
      None,
      userId,
      projectId,
      Some(System.currentTimeMillis() + 7 * 24 * 60 * 60 * 1000), // 一周后到期
      System.currentTimeMillis(),
      System.currentTimeMillis()
    )
    
    println(s"Task: ${task.title}")
    println(s"Priority: ${task.priority}")
    println(s"Status: ${task.status}")
    
    // 创建团队
    val teamId = TeamId("team-001")
    val team = Team(
      teamId,
      "Development Team",
      Some("Core development team"),
      userId,
      System.currentTimeMillis(),
      System.currentTimeMillis()
    )
    
    println(s"Team: ${team.name}")
    println(s"Owner: ${team.ownerId.value}")
    
    // 创建通知
    val notificationId = NotificationId("notif-001")
    val notification = Notification(
      notificationId,
      userId,
      TaskAssigned,
      "Task Assigned",
      "You have been assigned a new task: Implement domain model",
      isRead = false,
      System.currentTimeMillis()
    )
    
    println(s"Notification: ${notification.title}")
    println(s"Type: ${notification.`type`}")
    
    // 创建领域事件
    val taskCreatedEvent = TaskCreated(
      "event-001",
      System.currentTimeMillis(),
      taskId,
      "Implement domain model",
      userId,
      projectId
    )
    
    println(s"Domain Event: ${taskCreatedEvent.eventId}")
    println(s"Task ID: ${taskCreatedEvent.taskId.value}")
    println(s"Reporter ID: ${taskCreatedEvent.reporterId.value}")
    
    println("\n所有领域模型示例完成")
  }
}