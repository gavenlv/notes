// 蛋糕模式示例

// 核心领域模型
trait User {
  def id: Long
  def name: String
  def email: String
}

case class UserImpl(id: Long, name: String, email: String) extends User

// 服务层组件
trait UserRepositoryComponent {
  // 抽象类型成员
  type UserRepository
  
  // 抽象值
  def userRepository: UserRepository
  
  // 服务接口
  trait UserRepository {
    def findById(id: Long): Option[User]
    def findAll(): List[User]
    def save(user: User): Unit
    def delete(id: Long): Boolean
  }
}

// 实现组件
trait UserRepositoryComponentImpl extends UserRepositoryComponent {
  // 具体实现
  lazy val userRepository: UserRepository = new UserRepositoryImpl
  
  // 具体实现类
  class UserRepositoryImpl extends UserRepository {
    private var users: Map[Long, User] = Map(
      1L -> UserImpl(1, "Alice", "alice@example.com"),
      2L -> UserImpl(2, "Bob", "bob@example.com")
    )
    
    def findById(id: Long): Option[User] = users.get(id)
    def findAll(): List[User] = users.values.toList
    def save(user: User): Unit = {
      users = users + (user.id -> user)
      println(s"Saved user: ${user.name}")
    }
    def delete(id: Long): Boolean = {
      users.get(id) match {
        case Some(user) =>
          users = users - id
          println(s"Deleted user: ${user.name}")
          true
        case None => 
          println(s"User with id $id not found")
          false
      }
    }
  }
}

// 业务逻辑组件
trait UserServiceComponent {
  // 依赖其他组件
  this: UserRepositoryComponent =>
  
  // 抽象类型成员
  type UserService
  
  // 抽象值
  def userService: UserService
  
  // 服务接口
  trait UserService {
    def getUser(id: Long): Option[User]
    def getAllUsers(): List[User]
    def createUser(name: String, email: String): User
    def removeUser(id: Long): Boolean
  }
}

// 业务逻辑实现
trait UserServiceComponentImpl extends UserServiceComponent with UserRepositoryComponent {
  // 具体实现
  lazy val userService: UserService = new UserServiceImpl
  
  // 具体实现类
  class UserServiceImpl extends UserService {
    def getUser(id: Long): Option[User] = userRepository.findById(id)
    def getAllUsers(): List[User] = userRepository.findAll()
    def createUser(name: String, email: String): User = {
      val id = System.currentTimeMillis() // 简单ID生成
      val user = UserImpl(id, name, email)
      userRepository.save(user)
      user
    }
    def removeUser(id: Long): Boolean = userRepository.delete(id)
  }
}

// 应用程序组件
trait ApplicationComponent {
  // 声明所有依赖的组件
  this: UserServiceComponent with UserRepositoryComponent =>
  
  // 应用程序入口点
  def run(): Unit = {
    println("Starting application...")
    
    // 使用服务
    val users = userService.getAllUsers()
    println(s"Found ${users.size} users")
    
    users.foreach(user => println(s"- ${user.name} (${user.email})"))
    
    // 创建新用户
    val newUser = userService.createUser("Charlie", "charlie@example.com")
    println(s"Created new user with ID: ${newUser.id}")
    
    // 获取特定用户
    val user = userService.getUser(newUser.id)
    user.foreach(u => println(s"Retrieved user: ${u.name}"))
    
    println("Application finished.")
  }
}

// 组件装配
object ComponentRegistry extends ApplicationComponent 
                          with UserServiceComponentImpl 
                          with UserRepositoryComponentImpl

// 主应用程序
object CakePattern {
  def main(args: Array[String]): Unit = {
    // 运行应用程序
    ComponentRegistry.run()
  }
}