# 第10章：Scala实战项目

本章将通过一个完整的实战项目，综合应用前面学到的Scala知识。我们将构建一个功能完整的图书管理系统，涵盖领域建模、API设计、数据处理和并发操作等多个方面。

## 10.1 项目概述

### 10.1.1 项目目标

我们将构建一个图书管理系统，具有以下核心功能：
- 图书信息管理（增删改查）
- 用户管理（读者和图书管理员）
- 借阅和归还图书
- 图书搜索和推荐
- 借阅历史统计
- RESTful API接口

### 10.1.2 技术栈

- **编程语言**: Scala 2.13
- **HTTP框架**: Akka HTTP
- **数据持久化**: Slick + H2数据库（可替换为PostgreSQL）
- **JSON处理**: Spray JSON
- **并发处理**: Akka Actors
- **测试框架**: ScalaTest
- **构建工具**: sbt
- **日志**: Logback

### 10.1.3 项目结构

```
library-management-system/
├── build.sbt
├── project/
│   ├── build.properties
│   └── plugins.sbt
├── src/
│   ├── main/
│   │   ├── scala/
│   │   │   └── com/
│   │   │       └── library/
│   │   │           ├── Main.scala
│   │   │           ├── model/
│   │   │           │   ├── Book.scala
│   │   │           │   ├── User.scala
│   │   │           │   ├── Loan.scala
│   │   │           │   └── database/
│   │   │           │       ├── Database.scala
│   │   │           │       ├── BookTable.scala
│   │   │           │       ├── UserTable.scala
│   │   │           │       └── LoanTable.scala
│   │   │           ├── service/
│   │   │           │   ├── BookService.scala
│   │   │           │   ├── UserService.scala
│   │   │           │   ├── LoanService.scala
│   │   │           │   └── RecommendationService.scala
│   │   │           ├── repository/
│   │   │           │   ├── BookRepository.scala
│   │   │           │   ├── UserRepository.scala
│   │   │           │   └── LoanRepository.scala
│   │   │           ├── routes/
│   │   │           │   ├── BookRoutes.scala
│   │   │           │   ├── UserRoutes.scala
│   │   │           │   ├── LoanRoutes.scala
│   │   │           │   └── ApiRoutes.scala
│   │   │           ├── actors/
│   │   │           │   ├── BookActor.scala
│   │   │           │   ├── UserActor.scala
│   │   │           │   └── LoanActor.scala
│   │   │           ├── json/
│   │   │           │   ├── JsonSupport.scala
│   │   │           │   ├── BookJson.scala
│   │   │           │   ├── UserJson.scala
│   │   │           │   └── LoanJson.scala
│   │   │           └── util/
│   │   │               ├── Config.scala
│   │   │               └── DatabaseConfig.scala
│   │   └── resources/
│   │       ├── application.conf
│   │       └── logback.xml
│   └── test/
│       └── scala/
│           └── com/
│               └── library/
│                   ├── model/
│                   ├── service/
│                   ├── repository/
│                   └── routes/
└── README.md
```

## 10.2 项目设置与依赖

### 10.2.1 build.sbt配置

```scala
name := "library-management-system"

version := "1.0.0"

scalaVersion := "2.13.8"

libraryDependencies ++= {
  val akkaVersion = "2.6.19"
  val akkaHttpVersion = "10.2.9"
  val slickVersion = "3.3.3"
  val scalaTestVersion = "3.2.12"
  
  Seq(
    // Akka HTTP
    "com.typesafe.akka" %% "akka-http" % akkaHttpVersion,
    "com.typesafe.akka" %% "akka-http-spray-json" % akkaHttpVersion,
    "com.typesafe.akka" %% "akka-stream" % akkaVersion,
    "com.typesafe.akka" %% "akka-actor-typed" % akkaVersion,
    
    // 数据库
    "com.typesafe.slick" %% "slick" % slickVersion,
    "com.typesafe.slick" %% "slick-hikaricp" % slickVersion,
    "com.h2database" % "h2" % "2.1.212",
    "org.postgresql" % "postgresql" % "42.3.3", // 可选：PostgreSQL驱动
    
    // JSON
    "io.spray" %% "spray-json" % "1.3.6",
    
    // 日志
    "ch.qos.logback" % "logback-classic" % "1.2.11",
    "com.typesafe.akka" %% "akka-slf4j" % akkaVersion,
    
    // 配置
    "com.typesafe" % "config" % "1.4.2",
    
    // 测试
    "org.scalatest" %% "scalatest" % scalaTestVersion % Test,
    "com.typesafe.akka" %% "akka-http-testkit" % akkaHttpVersion % Test,
    "com.typesafe.akka" %% "akka-testkit" % akkaVersion % Test,
    "org.mockito" %% "mockito-scala" % "1.17.5" % Test
  )
}

// 测试选项
Test / parallelExecution := false

// 编译选项
scalacOptions ++= Seq(
  "-deprecation",
  "-feature",
  "-unchecked",
  "-Xlint",
  "-Ywarn-dead-code",
  "-Ywarn-numeric-widen",
  "-Ywarn-value-discard"
)

// 资源目录
Compile / resourceDirectory := baseDirectory.value / "src" / "main" / "resources"

// 启动选项
Compile / run / javaOptions ++= Seq(
  "-Dconfig.file=src/main/resources/application.conf"
)
```

### 10.2.2 项目配置文件

```hocon
# src/main/resources/application.conf
akka {
  loglevel = "INFO"
  loggers = ["akka.event.slf4j.Slf4jLogger"]
  
  http {
    host = "0.0.0.0"
    port = 8080
  }
  
  actor {
    default-dispatcher {
      executor = "fork-join-executor"
      fork-join-executor {
        parallelism-min = 2
        parallelism-factor = 2.0
        parallelism-max = 10
      }
    }
  }
}

# 数据库配置
database {
  url = "jdbc:h2:mem:library;DB_CLOSE_DELAY=-1"
  driver = "org.h2.Driver"
  user = "sa"
  password = ""
  connectionPool = "HikariCP"
  
  # PostgreSQL配置（可选）
  # url = "jdbc:postgresql://localhost:5432/library"
  # driver = "org.postgresql.Driver"
  # user = "library_user"
  # password = "library_password"
}

# 应用程序配置
library {
  max-books-per-user = 5
  max-loan-days = 30
  max-renewal-times = 2
  recommendation-limit = 10
}
```

```xml
<!-- src/main/resources/logback.xml -->
<configuration>
    <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%date{HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>

    <root level="INFO">
        <appender-ref ref="STDOUT" />
    </root>

    <logger name="com.library" level="DEBUG" />
    <logger name="slick" level="INFO" />
</configuration>
```

## 10.3 领域模型与数据访问层

### 10.3.1 核心领域模型

```scala
// src/main/scala/com/library/model/Book.scala
package com.library.model

import java.time.LocalDate

// 图书实体
case class Book(
  id: Option[Long] = None,
  isbn: String,
  title: String,
  author: String,
  publisher: String,
  publishDate: LocalDate,
  category: String,
  description: String,
  available: Boolean = true,
  totalCopies: Int,
  availableCopies: Int
) {
  def borrow(): Book = {
    if (availableCopies > 0) {
      this.copy(availableCopies = availableCopies - 1, available = availableCopies - 1 > 0)
    } else {
      throw new IllegalStateException("No available copies to borrow")
    }
  }
  
  def returnBook(): Book = {
    if (availableCopies < totalCopies) {
      this.copy(availableCopies = availableCopies + 1, available = true)
    } else {
      throw new IllegalStateException("All copies are already available")
    }
  }
}

// 图书搜索条件
case class BookSearchCriteria(
  title: Option[String] = None,
  author: Option[String] = None,
  category: Option[String] = None,
  available: Option[Boolean] = None
)

// 图书更新请求
case class BookUpdateRequest(
  title: Option[String] = None,
  author: Option[String] = None,
  publisher: Option[String] = None,
  publishDate: Option[LocalDate] = None,
  category: Option[String] = None,
  description: Option[String] = None,
  totalCopies: Option[Int] = None
)
```

```scala
// src/main/scala/com/library/model/User.scala
package com.library.model

import java.time.LocalDate

// 用户类型
sealed trait UserType
case object Reader extends UserType
case object Librarian extends UserType

// 用户实体
case class User(
  id: Option[Long] = None,
  username: String,
  password: String, // 在实际应用中应该是加密的
  email: String,
  firstName: String,
  lastName: String,
  userType: UserType,
  joinDate: LocalDate = LocalDate.now(),
  active: Boolean = true
) {
  def fullName: String = s"$firstName $lastName"
  
  def isReader: Boolean = userType == Reader
  
  def isLibrarian: Boolean = userType == Librarian
}

// 用户创建请求
case class UserCreateRequest(
  username: String,
  password: String,
  email: String,
  firstName: String,
  lastName: String,
  userType: UserType
)

// 用户更新请求
case class UserUpdateRequest(
  email: Option[String] = None,
  firstName: Option[String] = None,
  lastName: Option[String] = None,
  active: Option[Boolean] = None
)

// 用户登录请求
case class LoginRequest(username: String, password: String)

// 认证响应
case class AuthResponse(
  token: String,
  user: User
)
```

```scala
// src/main/scala/com/library/model/Loan.scala
package com.library.model

import java.time.LocalDate

// 借阅状态
sealed trait LoanStatus
case object Active extends LoanStatus
case object Returned extends LoanStatus
case object Overdue extends LoanStatus

// 借阅记录
case class Loan(
  id: Option[Long] = None,
  bookId: Long,
  userId: Long,
  loanDate: LocalDate = LocalDate.now(),
  dueDate: LocalDate = LocalDate.now().plusDays(30),
  returnDate: Option[LocalDate] = None,
  status: LoanStatus = Active,
  renewalCount: Int = 0
) {
  def isOverdue(currentDate: LocalDate = LocalDate.now()): Boolean = {
    status == Active && currentDate.isAfter(dueDate)
  }
  
  def canRenew(maxRenewalTimes: Int): Boolean = {
    status == Active && renewalCount < maxRenewalTimes && !isOverdue()
  }
  
  def renew(extendDays: Int): Loan = {
    if (canRenew(0)) {
      this.copy(
        dueDate = dueDate.plusDays(extendDays),
        renewalCount = renewalCount + 1
      )
    } else {
      throw new IllegalStateException("Loan cannot be renewed")
    }
  }
  
  def returnBook(returnedOn: LocalDate = LocalDate.now()): Loan = {
    if (status == Active) {
      this.copy(
        returnDate = Some(returnedOn),
        status = Returned
      )
    } else {
      throw new IllegalStateException("Loan is already returned")
    }
  }
}

// 借阅请求
case class LoanRequest(
  bookId: Long,
  userId: Long,
  days: Int = 30
)

// 续借请求
case class RenewalRequest(
  loanId: Long,
  extendDays: Int = 14
)
```

### 10.3.2 数据库表定义

```scala
// src/main/scala/com/library/model/database/BookTable.scala
package com.library.model.database

import slick.jdbc.H2Profile.api._
import com.library.model.Book
import java.time.LocalDate

// 图书表定义
class BookTable(tag: Tag) extends Table[Book](tag, "BOOKS") {
  def id = column[Long]("ID", O.PrimaryKey, O.AutoInc)
  def isbn = column[String]("ISBN")
  def title = column[String]("TITLE")
  def author = column[String]("AUTHOR")
  def publisher = column[String]("PUBLISHER")
  def publishDate = column[LocalDate]("PUBLISH_DATE")
  def category = column[String]("CATEGORY")
  def description = column[String]("DESCRIPTION")
  def available = column[Boolean]("AVAILABLE")
  def totalCopies = column[Int]("TOTAL_COPIES")
  def availableCopies = column[Int]("AVAILABLE_COPIES")
  
  def * = (id.?, isbn, title, author, publisher, publishDate, category, 
           description, available, totalCopies, availableCopies) <> 
    ((Book.apply _).tupled, Book.unapply)
}

// 图书表查询对象
object BookTable extends TableQuery(new BookTable(_))
```

```scala
// src/main/scala/com/library/model/database/UserTable.scala
package com.library.model.database

import slick.jdbc.H2Profile.api._
import com.library.model.{User, UserType, Reader, Librarian}
import java.time.LocalDate

// 用户表定义
class UserTable(tag: Tag) extends Table[User](tag, "USERS") {
  def id = column[Long]("ID", O.PrimaryKey, O.AutoInc)
  def username = column[String]("USERNAME")
  def password = column[String]("PASSWORD")
  def email = column[String]("EMAIL")
  def firstName = column[String]("FIRST_NAME")
  def lastName = column[String]("LAST_NAME")
  def userType = column[String]("USER_TYPE")
  def joinDate = column[LocalDate]("JOIN_DATE")
  def active = column[Boolean]("ACTIVE")
  
  // 自定义类型映射
  implicit val userTypeMapper: BaseColumnType[UserType] = MappedColumnType.base[UserType, String](
    {
      case Reader => "READER"
      case Librarian => "LIBRARIAN"
    },
    {
      case "READER" => Reader
      case "LIBRARIAN" => Librarian
    }
  )
  
  def * = (id.?, username, password, email, firstName, lastName, 
           userType, joinDate, active) <> 
    ((User.apply _).tupled, User.unapply)
}

// 用户表查询对象
object UserTable extends TableQuery(new UserTable(_))
```

```scala
// src/main/scala/com/library/model/database/LoanTable.scala
package com.library.model.database

import slick.jdbc.H2Profile.api._
import com.library.model.{Loan, LoanStatus, Active, Returned, Overdue}
import java.time.LocalDate

// 借阅记录表定义
class LoanTable(tag: Tag) extends Table[Loan](tag, "LOANS") {
  def id = column[Long]("ID", O.PrimaryKey, O.AutoInc)
  def bookId = column[Long]("BOOK_ID")
  def userId = column[Long]("USER_ID")
  def loanDate = column[LocalDate]("LOAN_DATE")
  def dueDate = column[LocalDate]("DUE_DATE")
  def returnDate = column[Option[LocalDate]]("RETURN_DATE")
  def status = column[String]("STATUS")
  def renewalCount = column[Int]("RENEWAL_COUNT")
  
  // 自定义类型映射
  implicit val loanStatusMapper: BaseColumnType[LoanStatus] = MappedColumnType.base[LoanStatus, String](
    {
      case Active => "ACTIVE"
      case Returned => "RETURNED"
      case Overdue => "OVERDUE"
    },
    {
      case "ACTIVE" => Active
      case "RETURNED" => Returned
      case "OVERDUE" => Overdue
    }
  )
  
  // 外键约束
  def bookFK = foreignKey("BOOK_FK", bookId, BookTable)(_.id)
  def userFK = foreignKey("USER_FK", userId, UserTable)(_.id)
  
  def * = (id.?, bookId, userId, loanDate, dueDate, returnDate, 
           status, renewalCount) <> 
    ((Loan.apply _).tupled, Loan.unapply)
}

// 借阅记录表查询对象
object LoanTable extends TableQuery(new LoanTable(_))
```

### 10.3.3 数据库配置与初始化

```scala
// src/main/scala/com/library/model/database/Database.scala
package com.library.model.database

import slick.jdbc.H2Profile.api._
import com.typesafe.config.Config
import scala.concurrent.{ExecutionContext, Future}
import slick.jdbc.JdbcBackend.Database

// 数据库配置
case class DatabaseConfig(
  url: String,
  driver: String,
  user: String,
  password: String,
  connectionPool: String
)

// 数据库连接
class Database(dbConfig: DatabaseConfig)(implicit ec: ExecutionContext) {
  // 创建数据库连接
  private val database = Database.forURL(
    url = dbConfig.url,
    driver = dbConfig.driver,
    user = dbConfig.user,
    password = dbConfig.password,
    executor = AsyncExecutor("library-db-pool", 5, 5)
  )
  
  // 表对象
  val books = BookTable
  val users = UserTable
  val loans = LoanTable
  
  // 数据库模式
  val schema = books.schema ++ users.schema ++ loans.schema
  
  // 初始化数据库
  def initialize(): Future[Unit] = {
    database.run(schema.create)
  }
  
  // 关闭数据库连接
  def shutdown(): Future[Unit] = {
    database.close()
  }
  
  // 获取数据库实例
  def getDb: Database = database
}

// 数据库伴生对象
object Database {
  def apply(config: Config)(implicit ec: ExecutionContext): Database = {
    val dbConfig = DatabaseConfig(
      url = config.getString("database.url"),
      driver = config.getString("database.driver"),
      user = config.getString("database.user"),
      password = config.getString("database.password"),
      connectionPool = config.getString("database.connectionPool")
    )
    
    new Database(dbConfig)
  }
}
```

## 10.4 数据访问层（Repository）

### 10.4.1 图书Repository

```scala
// src/main/scala/com/library/repository/BookRepository.scala
package com.library.repository

import com.library.model.{Book, BookSearchCriteria}
import com.library.model.database.{BookTable, Database}
import slick.jdbc.H2Profile.api._
import scala.concurrent.{ExecutionContext, Future}
import com.typesafe.scalalogging.LazyLogging

class BookRepository(database: Database)(implicit ec: ExecutionContext) extends LazyLogging {
  import database._
  
  // 获取所有图书
  def findAll(): Future[Seq[Book]] = {
    logger.info("Finding all books")
    database.getDb.run(books.result)
  }
  
  // 根据ID查找图书
  def findById(id: Long): Future[Option[Book]] = {
    logger.info(s"Finding book by id: $id")
    database.getDb.run(books.filter(_.id === id).result.headOption)
  }
  
  // 根据ISBN查找图书
  def findByIsbn(isbn: String): Future[Option[Book]] = {
    logger.info(s"Finding book by ISBN: $isbn")
    database.getDb.run(books.filter(_.isbn === isbn).result.headOption)
  }
  
  // 搜索图书
  def search(criteria: BookSearchCriteria): Future[Seq[Book]] = {
    logger.info(s"Searching books with criteria: $criteria")
    
    var query = books
    
    criteria.title.foreach(title => 
      query = query.filter(_.title.toLowerCase.like(s"%${title.toLowerCase}%"))
    )
    
    criteria.author.foreach(author => 
      query = query.filter(_.author.toLowerCase.like(s"%${author.toLowerCase}%"))
    )
    
    criteria.category.foreach(category => 
      query = query.filter(_.category.toLowerCase === category.toLowerCase)
    )
    
    criteria.available.foreach(available => 
      query = query.filter(_.available === available)
    )
    
    database.getDb.run(query.result)
  }
  
  // 添加新书
  def create(book: Book): Future[Book] = {
    logger.info(s"Creating new book: ${book.title}")
    val insertQuery = (books returning books.map(_.id)) += book
    database.getDb.run(insertQuery).map { generatedId =>
      book.copy(id = Some(generatedId))
    }
  }
  
  // 更新图书
  def update(id: Long, book: Book): Future[Option[Book]] = {
    logger.info(s"Updating book with id: $id")
    val updateQuery = books.filter(_.id === id).update(book)
    
    database.getDb.run(updateQuery).flatMap {
      case 0 => Future.successful(None) // 没有更新任何行
      case _ => database.getDb.run(books.filter(_.id === id).result.headOption)
    }
  }
  
  // 删除图书
  def delete(id: Long): Future[Boolean] = {
    logger.info(s"Deleting book with id: $id")
    val deleteQuery = books.filter(_.id === id).delete
    
    database.getDb.run(deleteQuery).map(_ > 0)
  }
  
  // 获取可用的图书副本
  def findAvailableBooks(limit: Int = 20): Future[Seq[Book]] = {
    logger.info(s"Finding $limit available books")
    database.getDb.run(
      books.filter(_.available === true)
        .filter(_.availableCopies > 0)
        .sortBy(_.title)
        .take(limit)
        .result
    )
  }
  
  // 根据类别获取图书
  def findByCategory(category: String, limit: Int = 20): Future[Seq[Book]] = {
    logger.info(s"Finding books in category: $category")
    database.getDb.run(
      books.filter(_.category.toLowerCase === category.toLowerCase)
        .sortBy(_.title)
        .take(limit)
        .result
    )
  }
  
  // 获取热门图书（基于借阅次数）
  def findPopularBooks(limit: Int = 10): Future[Seq[Book]] = {
    logger.info(s"Finding $limit popular books")
    
    val popularBooksQuery = for {
      (book, loanCount) <- books joinLeft (loans.groupBy(_.bookId).map { case (bookId, loans) => 
        (bookId, loans.length)
      }) on (_.id === _._1)
    } yield (book, loanCount.map(_._2).getOrElse(0))
    
    database.getDb.run(
      popularBooksQuery
        .sortBy(_._2.desc)
        .take(limit)
        .map(_._1)
        .result
    )
  }
  
  // 批量更新图书可用性
  def updateBookAvailability(bookId: Long, availableCopies: Int): Future[Boolean] = {
    logger.info(s"Updating availability for book id: $bookId to $availableCopies")
    val updateQuery = books
      .filter(_.id === bookId)
      .map(b => (b.available, b.availableCopies))
      .update((availableCopies > 0, availableCopies))
    
    database.getDb.run(updateQuery).map(_ > 0)
  }
}
```

### 10.4.2 用户Repository

```scala
// src/main/scala/com/library/repository/UserRepository.scala
package com.library.repository

import com.library.model.{User, UserType}
import com.library.model.database.{UserTable, Database}
import slick.jdbc.H2Profile.api._
import scala.concurrent.{ExecutionContext, Future}
import com.typesafe.scalalogging.LazyLogging

class UserRepository(database: Database)(implicit ec: ExecutionContext) extends LazyLogging {
  import database._
  
  // 获取所有用户
  def findAll(): Future[Seq[User]] = {
    logger.info("Finding all users")
    database.getDb.run(users.result)
  }
  
  // 根据ID查找用户
  def findById(id: Long): Future[Option[User]] = {
    logger.info(s"Finding user by id: $id")
    database.getDb.run(users.filter(_.id === id).result.headOption)
  }
  
  // 根据用户名查找用户
  def findByUsername(username: String): Future[Option[User]] = {
    logger.info(s"Finding user by username: $username")
    database.getDb.run(users.filter(_.username === username).result.headOption)
  }
  
  // 根据用户类型查找用户
  def findByUserType(userType: UserType): Future[Seq[User]] = {
    logger.info(s"Finding users by type: $userType")
    database.getDb.run(users.filter(_.userType === userType).result)
  }
  
  // 创建新用户
  def create(user: User): Future[User] = {
    logger.info(s"Creating new user: ${user.username}")
    val insertQuery = (users returning users.map(_.id)) += user
    database.getDb.run(insertQuery).map { generatedId =>
      user.copy(id = Some(generatedId))
    }
  }
  
  // 更新用户
  def update(id: Long, user: User): Future[Option[User]] = {
    logger.info(s"Updating user with id: $id")
    val updateQuery = users.filter(_.id === id).update(user)
    
    database.getDb.run(updateQuery).flatMap {
      case 0 => Future.successful(None) // 没有更新任何行
      case _ => database.getDb.run(users.filter(_.id === id).result.headOption)
    }
  }
  
  // 删除用户
  def delete(id: Long): Future[Boolean] = {
    logger.info(s"Deleting user with id: $id")
    val deleteQuery = users.filter(_.id === id).delete
    
    database.getDb.run(deleteQuery).map(_ > 0)
  }
  
  // 激活/停用用户
  def updateActiveStatus(id: Long, active: Boolean): Future[Boolean] = {
    logger.info(s"Updating active status for user id: $id to $active")
    val updateQuery = users.filter(_.id === id).map(_.active).update(active)
    
    database.getDb.run(updateQuery).map(_ > 0)
  }
  
  // 验证用户登录
  def authenticate(username: String, password: String): Future[Option[User]] = {
    logger.info(s"Authenticating user: $username")
    database.getDb.run(
      users.filter(u => u.username === username && u.password === password && u.active === true)
        .result.headOption
    )
  }
}
```

### 10.4.3 借阅Repository

```scala
// src/main/scala/com/library/repository/LoanRepository.scala
package com.library.repository

import com.library.model.{Loan, LoanStatus, Active, Returned, Overdue}
import com.library.model.database.{LoanTable, Database}
import slick.jdbc.H2Profile.api._
import scala.concurrent.{ExecutionContext, Future}
import com.typesafe.scalalogging.LazyLogging
import java.time.LocalDate

class LoanRepository(database: Database)(implicit ec: ExecutionContext) extends LazyLogging {
  import database._
  
  // 获取所有借阅记录
  def findAll(): Future[Seq[Loan]] = {
    logger.info("Finding all loans")
    database.getDb.run(loans.result)
  }
  
  // 根据ID查找借阅记录
  def findById(id: Long): Future[Option[Loan]] = {
    logger.info(s"Finding loan by id: $id")
    database.getDb.run(loans.filter(_.id === id).result.headOption)
  }
  
  // 根据用户ID查找借阅记录
  def findByUserId(userId: Long): Future[Seq[Loan]] = {
    logger.info(s"Finding loans by user id: $userId")
    database.getDb.run(loans.filter(_.userId === userId).result)
  }
  
  // 根据图书ID查找借阅记录
  def findByBookId(bookId: Long): Future[Seq[Loan]] = {
    logger.info(s"Finding loans by book id: $bookId")
    database.getDb.run(loans.filter(_.bookId === bookId).result)
  }
  
  // 获取用户的活跃借阅
  def findActiveLoansByUser(userId: Long): Future[Seq[Loan]] = {
    logger.info(s"Finding active loans for user id: $userId")
    database.getDb.run(
      loans.filter(loan => loan.userId === userId && loan.status === (Active: LoanStatus)).result
    )
  }
  
  // 获取过期借阅
  def findOverdueLoans(): Future[Seq[Loan]] = {
    logger.info("Finding overdue loans")
    val today = LocalDate.now()
    
    database.getDb.run(
      loans.filter(loan => 
        loan.status === (Active: LoanStatus) && loan.dueDate < today
      ).result
    )
  }
  
  // 获取用户借阅历史
  def findLoanHistory(userId: Long, limit: Int = 20): Future[Seq[Loan]] = {
    logger.info(s"Finding loan history for user id: $userId")
    database.getDb.run(
      loans.filter(_.userId === userId)
        .sortBy(_.loanDate.desc)
        .take(limit)
        .result
    )
  }
  
  // 创建新借阅记录
  def create(loan: Loan): Future[Loan] = {
    logger.info(s"Creating new loan for book id: ${loan.bookId}, user id: ${loan.userId}")
    val insertQuery = (loans returning loans.map(_.id)) += loan
    database.getDb.run(insertQuery).map { generatedId =>
      loan.copy(id = Some(generatedId))
    }
  }
  
  // 更新借阅记录
  def update(id: Long, loan: Loan): Future[Option[Loan]] = {
    logger.info(s"Updating loan with id: $id")
    val updateQuery = loans.filter(_.id === id).update(loan)
    
    database.getDb.run(updateQuery).flatMap {
      case 0 => Future.successful(None) // 没有更新任何行
      case _ => database.getDb.run(loans.filter(_.id === id).result.headOption)
    }
  }
  
  // 更新过期借阅状态
  def updateOverdueLoans(): Future[Int] = {
    logger.info("Updating overdue loans")
    val today = LocalDate.now()
    
    val updateQuery = loans
      .filter(loan => loan.status === (Active: LoanStatus) && loan.dueDate < today)
      .map(_.status)
      .update(Overdue: LoanStatus)
    
    database.getDb.run(updateQuery)
  }
  
  // 获取统计信息
  def getLoanStatistics(): Future[LoanStatistics] = {
    logger.info("Getting loan statistics")
    
    val totalLoansQuery = loans.length.result
    val activeLoansQuery = loans.filter(_.status === (Active: LoanStatus)).length.result
    val overdueLoansQuery = loans.filter(_.status === (Overdue: LoanStatus)).length.result
    
    for {
      totalLoans <- totalLoansQuery
      activeLoans <- activeLoansQuery
      overdueLoans <- overdueLoansQuery
    } yield LoanStatistics(
      totalLoans = totalLoans,
      activeLoans = activeLoans,
      overdueLoans = overdueLoans
    )
  }
}

// 借阅统计信息
case class LoanStatistics(
  totalLoans: Int,
  activeLoans: Int,
  overdueLoans: Int
)
```

## 10.5 服务层

### 10.5.1 图书服务

```scala
// src/main/scala/com/library/service/BookService.scala
package com.library.service

import com.library.model._
import com.library.repository.BookRepository
import scala.concurrent.{ExecutionContext, Future}
import com.typesafe.scalalogging.LazyLogging
import java.time.LocalDate

class BookService(bookRepository: BookRepository)(implicit ec: ExecutionContext) extends LazyLogging {
  
  // 获取所有图书
  def getAllBooks(): Future[Seq[Book]] = {
    logger.info("Getting all books")
    bookRepository.findAll()
  }
  
  // 根据ID获取图书
  def getBookById(id: Long): Future[Option[Book]] = {
    logger.info(s"Getting book by id: $id")
    bookRepository.findById(id)
  }
  
  // 搜索图书
  def searchBooks(criteria: BookSearchCriteria): Future[Seq[Book]] = {
    logger.info(s"Searching books with criteria: $criteria")
    bookRepository.search(criteria)
  }
  
  // 添加新书
  def addBook(book: Book): Future[Either[String, Book]] = {
    logger.info(s"Adding new book: ${book.title}")
    
    // 检查ISBN是否已存在
    bookRepository.findByIsbn(book.isbn).flatMap {
      case Some(existingBook) => 
        Future.successful(Left(s"Book with ISBN ${book.isbn} already exists"))
      case None => 
        bookRepository.create(book).map(Right(_))
    }
  }
  
  // 更新图书
  def updateBook(id: Long, request: BookUpdateRequest): Future[Either[String, Book]] = {
    logger.info(s"Updating book with id: $id")
    
    bookRepository.findById(id).flatMap {
      case None => 
        Future.successful(Left(s"Book with id $id not found"))
      case Some(book) =>
        val updatedBook = book.copy(
          title = request.title.getOrElse(book.title),
          author = request.author.getOrElse(book.author),
          publisher = request.publisher.getOrElse(book.publisher),
          publishDate = request.publishDate.getOrElse(book.publishDate),
          category = request.category.getOrElse(book.category),
          description = request.description.getOrElse(book.description),
          totalCopies = request.totalCopies.getOrElse(book.totalCopies)
        )
        
        bookRepository.update(id, updatedBook).map {
          case None => Left(s"Failed to update book with id $id")
          case Some(updated) => Right(updated)
        }
    }
  }
  
  // 删除图书
  def deleteBook(id: Long): Future[Either[String, Boolean]] = {
    logger.info(s"Deleting book with id: $id")
    
    // 检查是否有活跃的借阅
    bookRepository.findById(id).flatMap {
      case None => 
        Future.successful(Left(s"Book with id $id not found"))
      case Some(book) =>
        // 实际应用中应该检查是否有活跃借阅，这里简化处理
        bookRepository.delete(id).map(Left(_))
    }
  }
  
  // 借出图书
  def borrowBook(id: Long): Future[Either[String, Book]] = {
    logger.info(s"Borrowing book with id: $id")
    
    bookRepository.findById(id).flatMap {
      case None => 
        Future.successful(Left(s"Book with id $id not found"))
      case Some(book) =>
        if (!book.available || book.availableCopies <= 0) {
          Future.successful(Left(s"Book ${book.title} is not available"))
        } else {
          val borrowedBook = book.borrow()
          bookRepository.updateBookAvailability(id, borrowedBook.availableCopies).map { success =>
            if (success) Right(borrowedBook)
            else Left(s"Failed to update book availability")
          }
        }
    }
  }
  
  // 归还图书
  def returnBook(id: Long): Future[Either[String, Book]] = {
    logger.info(s"Returning book with id: $id")
    
    bookRepository.findById(id).flatMap {
      case None => 
        Future.successful(Left(s"Book with id $id not found"))
      case Some(book) =>
        if (book.availableCopies >= book.totalCopies) {
          Future.successful(Left(s"All copies of book ${book.title} are already available"))
        } else {
          val returnedBook = book.returnBook()
          bookRepository.updateBookAvailability(id, returnedBook.availableCopies).map { success =>
            if (success) Right(returnedBook)
            else Left(s"Failed to update book availability")
          }
        }
    }
  }
  
  // 获取热门图书
  def getPopularBooks(limit: Int = 10): Future[Seq[Book]] = {
    logger.info(s"Getting $limit popular books")
    bookRepository.findPopularBooks(limit)
  }
  
  // 根据类别获取图书
  def getBooksByCategory(category: String, limit: Int = 20): Future[Seq[Book]] = {
    logger.info(s"Getting books in category: $category")
    bookRepository.findByCategory(category, limit)
  }
  
  // 获取可用图书
  def getAvailableBooks(limit: Int = 20): Future[Seq[Book]] = {
    logger.info(s"Getting $limit available books")
    bookRepository.findAvailableBooks(limit)
  }
}
```

### 10.5.2 用户服务

```scala
// src/main/scala/com/library/service/UserService.scala
package com.library.service

import com.library.model._
import com.library.repository.UserRepository
import scala.concurrent.{ExecutionContext, Future}
import com.typesafe.scalalogging.LazyLogging
import java.util.UUID

class UserService(userRepository: UserRepository)(implicit ec: ExecutionContext) extends LazyLogging {
  
  // 获取所有用户
  def getAllUsers(): Future[Seq[User]] = {
    logger.info("Getting all users")
    userRepository.findAll()
  }
  
  // 根据ID获取用户
  def getUserById(id: Long): Future[Option[User]] = {
    logger.info(s"Getting user by id: $id")
    userRepository.findById(id)
  }
  
  // 创建新用户
  def createUser(request: UserCreateRequest): Future[Either[String, User]] = {
    logger.info(s"Creating new user: ${request.username}")
    
    // 检查用户名是否已存在
    userRepository.findByUsername(request.username).flatMap {
      case Some(existingUser) => 
        Future.successful(Left(s"Username ${request.username} already exists"))
      case None => 
        val newUser = User(
          username = request.username,
          password = hashPassword(request.password), // 实际应用中应该使用更安全的哈希方式
          email = request.email,
          firstName = request.firstName,
          lastName = request.lastName,
          userType = request.userType
        )
        
        userRepository.create(newUser).map(Right(_))
    }
  }
  
  // 更新用户
  def updateUser(id: Long, request: UserUpdateRequest): Future[Either[String, User]] = {
    logger.info(s"Updating user with id: $id")
    
    userRepository.findById(id).flatMap {
      case None => 
        Future.successful(Left(s"User with id $id not found"))
      case Some(user) =>
        val updatedUser = user.copy(
          email = request.email.getOrElse(user.email),
          firstName = request.firstName.getOrElse(user.firstName),
          lastName = request.lastName.getOrElse(user.lastName),
          active = request.active.getOrElse(user.active)
        )
        
        userRepository.update(id, updatedUser).map {
          case None => Left(s"Failed to update user with id $id")
          case Some(updated) => Right(updated)
        }
    }
  }
  
  // 删除用户
  def deleteUser(id: Long): Future[Either[String, Boolean]] = {
    logger.info(s"Deleting user with id: $id")
    
    userRepository.findById(id).flatMap {
      case None => 
        Future.successful(Left(s"User with id $id not found"))
      case Some(_) =>
        userRepository.delete(id).map(Right(_))
    }
  }
  
  // 用户登录
  def login(request: LoginRequest): Future[Either[String, AuthResponse]] = {
    logger.info(s"Login attempt for user: ${request.username}")
    
    userRepository.authenticate(request.username, request.password).flatMap {
      case None => 
        Future.successful(Left("Invalid username or password"))
      case Some(user) =>
        generateToken(user).map { token =>
          Right(AuthResponse(token, user))
        }
    }
  }
  
  // 激活/停用用户
  def updateUserActiveStatus(id: Long, active: Boolean): Future[Either[String, Boolean]] = {
    logger.info(s"Updating active status for user id: $id to $active")
    
    userRepository.findById(id).flatMap {
      case None => 
        Future.successful(Left(s"User with id $id not found"))
      case Some(_) =>
        userRepository.updateActiveStatus(id, active).map(Right(_))
    }
  }
  
  // 根据用户类型获取用户
  def getUsersByType(userType: UserType): Future[Seq[User]] = {
    logger.info(s"Getting users by type: $userType")
    userRepository.findByUserType(userType)
  }
  
  // 密码哈希（简化示例，实际应用中应使用更安全的方式）
  private def hashPassword(password: String): String = {
    // 实际应用中应使用bcrypt或scrypt等安全哈希算法
    s"hashed_$password"
  }
  
  // 生成认证令牌（简化示例，实际应用中应使用JWT）
  private def generateToken(user: User): Future[String] = {
    Future {
      // 实际应用中应生成JWT令牌，包含用户ID、角色等信息
      s"token_${UUID.randomUUID().toString}_${user.id.getOrElse(0)}"
    }
  }
}
```

### 10.5.3 借阅服务

```scala
// src/main/scala/com/library/service/LoanService.scala
package com.library.service

import com.library.model._
import com.library.repository.{LoanRepository, BookRepository, UserRepository}
import scala.concurrent.{ExecutionContext, Future}
import com.typesafe.scalalogging.LazyLogging
import java.time.LocalDate

class LoanService(
  loanRepository: LoanRepository,
  bookRepository: BookRepository,
  userRepository: UserRepository
)(implicit ec: ExecutionContext) extends LazyLogging {
  
  // 获取所有借阅记录
  def getAllLoans(): Future[Seq[Loan]] = {
    logger.info("Getting all loans")
    loanRepository.findAll()
  }
  
  // 获取用户借阅记录
  def getUserLoans(userId: Long): Future[Seq[Loan]] = {
    logger.info(s"Getting loans for user id: $userId")
    loanRepository.findByUserId(userId)
  }
  
  // 获取图书借阅记录
  def getBookLoans(bookId: Long): Future[Seq[Loan]] = {
    logger.info(s"Getting loans for book id: $bookId")
    loanRepository.findByBookId(bookId)
  }
  
  // 借出图书
  def borrowBook(request: LoanRequest): Future[Either[String, Loan]] = {
    logger.info(s"Borrowing book id: ${request.bookId} for user id: ${request.userId}")
    
    // 验证用户和图书存在
    for {
      userOpt <- userRepository.findById(request.userId)
      bookOpt <- bookRepository.findById(request.bookId)
    } yield (userOpt, bookOpt) match {
      case (None, _) => Left("User not found")
      case (_, None) => Left("Book not found")
      case (Some(user), Some(book)) if !user.active => Left("User account is inactive")
      case (Some(user), Some(book)) if !book.available || book.availableCopies <= 0 => 
        Left("Book is not available")
      case (Some(user), Some(book)) =>
        // 检查用户是否有活跃借阅
        for {
          activeLoans <- loanRepository.findActiveLoansByUser(request.userId)
        } yield {
          // 实际应用中应该检查借阅限制，这里简化处理
          if (activeLoans.length >= 5) {
            Left("User has reached maximum loan limit")
          } else {
            // 创建借阅记录
            val loan = Loan(
              bookId = request.bookId,
              userId = request.userId,
              dueDate = LocalDate.now().plusDays(request.days)
            )
            
            // 在实际应用中，这里应该处理创建借阅记录和更新图书可用性的事务
            Right(loan)
          }
        }
    }
  }.flatten
  
  // 归还图书
  def returnBook(loanId: Long): Future[Either[String, Loan]] = {
    logger.info(s"Returning loan with id: $loanId")
    
    loanRepository.findById(loanId).flatMap {
      case None => 
        Future.successful(Left(s"Loan with id $loanId not found"))
      case Some(loan) if loan.status != Active => 
        Future.successful(Left("Loan is already returned or overdue"))
      case Some(loan) =>
        val returnedLoan = loan.returnBook()
        
        // 在实际应用中，这里应该处理更新借阅记录和图书可用性的事务
        loanRepository.update(loanId, returnedLoan).map {
          case None => Left(s"Failed to update loan with id $loanId")
          case Some(updated) => Right(updated)
        }
    }
  }
  
  // 续借
  def renewLoan(request: RenewalRequest): Future[Either[String, Loan]] = {
    logger.info(s"Renewing loan with id: ${request.loanId}")
    
    loanRepository.findById(request.loanId).flatMap {
      case None => 
        Future.successful(Left(s"Loan with id ${request.loanId} not found"))
      case Some(loan) if loan.status != Active => 
        Future.successful(Left("Loan is not active and cannot be renewed"))
      case Some(loan) if !loan.canRenew(2) => // 假设最大续借次数为2
        Future.successful(Left("Loan cannot be renewed"))
      case Some(loan) =>
        val renewedLoan = loan.renew(request.extendDays)
        
        loanRepository.update(request.loanId, renewedLoan).map {
          case None => Left(s"Failed to update loan with id ${request.loanId}")
          case Some(updated) => Right(updated)
        }
    }
  }
  
  // 获取用户借阅历史
  def getUserLoanHistory(userId: Long, limit: Int = 20): Future[Seq[Loan]] = {
    logger.info(s"Getting loan history for user id: $userId")
    loanRepository.findLoanHistory(userId, limit)
  }
  
  // 获取过期借阅
  def getOverdueLoans(): Future[Seq[Loan]] = {
    logger.info("Getting overdue loans")
    loanRepository.findOverdueLoans()
  }
  
  // 更新过期借阅状态
  def updateOverdueLoans(): Future[Int] = {
    logger.info("Updating overdue loans")
    loanRepository.updateOverdueLoans()
  }
  
  // 获取借阅统计
  def getLoanStatistics(): Future[LoanStatistics] = {
    logger.info("Getting loan statistics")
    loanRepository.getLoanStatistics()
  }
}
```

### 10.5.4 推荐服务

```scala
// src/main/scala/com/library/service/RecommendationService.scala
package com.library.service

import com.library.model.{Book, User, Loan}
import com.library.repository.{BookRepository, LoanRepository}
import scala.concurrent.{ExecutionContext, Future}
import com.typesafe.scalalogging.LazyLogging
import scala.collection.mutable

class RecommendationService(
  bookRepository: BookRepository,
  loanRepository: LoanRepository
)(implicit ec: ExecutionContext) extends LazyLogging {
  
  // 为用户推荐图书
  def recommendBooksForUser(userId: Long, limit: Int = 5): Future[Seq[Book]] = {
    logger.info(s"Recommending books for user id: $userId")
    
    // 获取用户借阅历史
    loanRepository.findLoanHistory(userId, 20).flatMap { userLoans =>
      // 分析用户借阅的类别
      val categoryCount = mutable.Map[String, Int]()
      userLoans.foreach { loan =>
        // 在实际应用中，需要通过bookRepository获取图书信息
        // 这里简化处理
        val category = "fiction" // 假设的类别
        categoryCount(category) = categoryCount.getOrElse(category, 0) + 1
      }
      
      // 获取用户最常借阅的类别
      val topCategories = categoryCount.toSeq.sortBy(-_._2).take(3).map(_._1)
      
      // 为每个类别推荐图书
      val recommendations = topCategories.flatMap { category =>
        bookRepository.findByCategory(category, limit / topCategories.length + 1)
      }
      
      Future.successful(recommendations.distinctBy(_.id).take(limit))
    }
  }
  
  // 基于内容的推荐
  def recommendSimilarBooks(bookId: Long, limit: Int = 5): Future[Seq[Book]] = {
    logger.info(s"Recommending books similar to book id: $bookId")
    
    bookRepository.findById(bookId).flatMap {
      case None => Future.successful(Seq.empty)
      case Some(book) =>
        // 查找同类别、同作者的图书
        for {
          sameCategory <- bookRepository.findByCategory(book.category, limit)
          allBooks <- bookRepository.findAll()
        } yield {
          // 过滤掉自身，并基于多个因素推荐
          val recommendations = sameCategory.filter(_.id != book.id) ++
            allBooks.filter(b => b.author == book.author && b.id != book.id)
          
          recommendations.distinctBy(_.id).take(limit)
        }
    }
  }
  
  // 获取热门图书
  def getPopularBooks(limit: Int = 10): Future[Seq[Book]] = {
    logger.info(s"Getting $limit popular books")
    bookRepository.findPopularBooks(limit)
  }
  
  // 获取最新上架的图书
  def getNewBooks(limit: Int = 10): Future[Seq[Book]] = {
    logger.info(s"Getting $limit new books")
    
    bookRepository.findAll().map { allBooks =>
      // 实际应用中应该有上架日期字段，这里简化处理
      allBooks.sortBy(_.publishDate).reverse.take(limit)
    }
  }
}
```

## 10.6 JSON支持

### 10.6.1 通用JSON支持

```scala
// src/main/scala/com/library/json/JsonSupport.scala
package com.library.json

import spray.json._
import java.time.LocalDate
import java.time.format.DateTimeFormatter

// 自定义日期格式
object DateJsonProtocol {
  val formatter = DateTimeFormatter.ISO_LOCAL_DATE
  
  implicit object LocalDateJsonFormat extends RootJsonFormat[LocalDate] {
    def write(date: LocalDate): JsValue = JsString(date.format(formatter))
    
    def read(value: JsValue): LocalDate = value match {
      case JsString(dateString) => LocalDate.parse(dateString, formatter)
      _ => throw DeserializationException("Expected date in ISO format")
    }
  }
}

// 自定义枚举类型支持
trait EnumJsonSupport[T <: scala.Enumeration] {
  def enum: T
  
  implicit def enumFormat: RootJsonFormat[enum.Value] = new RootJsonFormat[enum.Value] {
    def write(obj: enum.Value): JsValue = JsString(obj.toString)
    
    def read(value: JsValue): enum.Value = value match {
      case JsString(str) => enum.withName(str)
      _ => throw DeserializationException(s"Expected string value for enum ${enum.toString}")
    }
  }
}
```

### 10.6.2 图书JSON支持

```scala
// src/main/scala/com/library/json/BookJson.scala
package com.library.json

import spray.json._
import com.library.model.{Book, BookSearchCriteria, BookUpdateRequest}
import java.time.LocalDate

object BookJsonProtocol extends DefaultJsonProtocol with DateJsonProtocol {
  // 图书JSON格式
  implicit val bookFormat: RootJsonFormat[Book] = jsonFormat12(Book.apply)
  
  // 图书搜索条件JSON格式
  implicit object BookSearchCriteriaJsonFormat extends RootJsonFormat[BookSearchCriteria] {
    def write(criteria: BookSearchCriteria): JsValue = {
      val fields = List(
        criteria.title.map("title" -> JsString(_)),
        criteria.author.map("author" -> JsString(_)),
        criteria.category.map("category" -> JsString(_)),
        criteria.available.map("available" -> JsBoolean(_))
      ).flatten
      
      JsObject(fields: _*)
    }
    
    def read(value: JsValue): BookSearchCriteria = value.asJsObject.getFields(
      "title", "author", "category", "available"
    ) match {
      case Seq(titleOpt, authorOpt, categoryOpt, availableOpt) =>
        BookSearchCriteria(
          title = titleOpt.convertTo[Option[String]],
          author = authorOpt.convertTo[Option[String]],
          category = categoryOpt.convertTo[Option[String]],
          available = availableOpt.convertTo[Option[Boolean]]
        )
      case _ => throw DeserializationException("Expected BookSearchCriteria object")
    }
  }
  
  // 图书更新请求JSON格式
  implicit object BookUpdateRequestJsonFormat extends RootJsonFormat[BookUpdateRequest] {
    def write(request: BookUpdateRequest): JsValue = {
      val fields = List(
        request.title.map("title" -> JsString(_)),
        request.author.map("author" -> JsString(_)),
        request.publisher.map("publisher" -> JsString(_)),
        request.publishDate.map("publishDate" -> _.toJson),
        request.category.map("category" -> JsString(_)),
        request.description.map("description" -> JsString(_)),
        request.totalCopies.map("totalCopies" -> JsNumber(_))
      ).flatten
      
      JsObject(fields: _*)
    }
    
    def read(value: JsValue): BookUpdateRequest = value.asJsObject.getFields(
      "title", "author", "publisher", "publishDate", "category", "description", "totalCopies"
    ) match {
      case Seq(titleOpt, authorOpt, publisherOpt, publishDateOpt, categoryOpt, descriptionOpt, totalCopiesOpt) =>
        BookUpdateRequest(
          title = titleOpt.convertTo[Option[String]],
          author = authorOpt.convertTo[Option[String]],
          publisher = publisherOpt.convertTo[Option[String]],
          publishDate = publishDateOpt.convertTo[Option[LocalDate]],
          category = categoryOpt.convertTo[Option[String]],
          description = descriptionOpt.convertTo[Option[String]],
          totalCopies = totalCopiesOpt.convertTo[Option[Int]]
        )
      case _ => throw DeserializationException("Expected BookUpdateRequest object")
    }
  }
}
```

### 10.6.3 用户JSON支持

```scala
// src/main/scala/com/library/json/UserJson.scala
package com.library.json

import spray.json._
import com.library.model.{User, UserType, UserCreateRequest, UserUpdateRequest, LoginRequest, AuthResponse}
import com.library.model.UserType.{Reader, Librarian}
import java.time.LocalDate

object UserJsonProtocol extends DefaultJsonProtocol with DateJsonProtocol {
  // 用户类型JSON格式
  implicit object UserTypeJsonFormat extends RootJsonFormat[UserType] {
    def write(userType: UserType): JsValue = userType match {
      case Reader => JsString("READER")
      case Librarian => JsString("LIBRARIAN")
    }
    
    def read(value: JsValue): UserType = value match {
      case JsString("READER") => Reader
      case JsString("LIBRARIAN") => Librarian
      case _ => throw DeserializationException("Expected USER_TYPE to be 'READER' or 'LIBRARIAN'")
    }
  }
  
  // 用户JSON格式
  implicit val userFormat: RootJsonFormat[User] = jsonFormat9(User.apply)
  
  // 用户创建请求JSON格式
  implicit val userCreateRequestFormat: RootJsonFormat[UserCreateRequest] = jsonFormat6(UserCreateRequest.apply)
  
  // 用户更新请求JSON格式
  implicit object UserUpdateRequestJsonFormat extends RootJsonFormat[UserUpdateRequest] {
    def write(request: UserUpdateRequest): JsValue = {
      val fields = List(
        request.email.map("email" -> JsString(_)),
        request.firstName.map("firstName" -> JsString(_)),
        request.lastName.map("lastName" -> JsString(_)),
        request.active.map("active" -> JsBoolean(_))
      ).flatten
      
      JsObject(fields: _*)
    }
    
    def read(value: JsValue): UserUpdateRequest = value.asJsObject.getFields(
      "email", "firstName", "lastName", "active"
    ) match {
      case Seq(emailOpt, firstNameOpt, lastNameOpt, activeOpt) =>
        UserUpdateRequest(
          email = emailOpt.convertTo[Option[String]],
          firstName = firstNameOpt.convertTo[Option[String]],
          lastName = lastNameOpt.convertTo[Option[String]],
          active = activeOpt.convertTo[Option[Boolean]]
        )
      case _ => throw DeserializationException("Expected UserUpdateRequest object")
    }
  }
  
  // 登录请求JSON格式
  implicit val loginRequestFormat: RootJsonFormat[LoginRequest] = jsonFormat2(LoginRequest.apply)
  
  // 认证响应JSON格式
  implicit val authResponseFormat: RootJsonFormat[AuthResponse] = jsonFormat2(AuthResponse.apply)
}
```

### 10.6.4 借阅JSON支持

```scala
// src/main/scala/com/library/json/LoanJson.scala
package com.library.json

import spray.json._
import com.library.model.{Loan, LoanStatus, LoanRequest, RenewalRequest, LoanStatistics}
import com.library.model.LoanStatus.{Active, Returned, Overdue}
import java.time.LocalDate

object LoanJsonProtocol extends DefaultJsonProtocol with DateJsonProtocol {
  // 借阅状态JSON格式
  implicit object LoanStatusJsonFormat extends RootJsonFormat[LoanStatus] {
    def write(status: LoanStatus): JsValue = status match {
      case Active => JsString("ACTIVE")
      case Returned => JsString("RETURNED")
      case Overdue => JsString("OVERDUE")
    }
    
    def read(value: JsValue): LoanStatus = value match {
      case JsString("ACTIVE") => Active
      case JsString("RETURNED") => Returned
      case JsString("OVERDUE") => Overdue
      case _ => throw DeserializationException("Expected LOAN_STATUS to be 'ACTIVE', 'RETURNED' or 'OVERDUE'")
    }
  }
  
  // 借阅记录JSON格式
  implicit val loanFormat: RootJsonFormat[Loan] = jsonFormat8(Loan.apply)
  
  // 借阅请求JSON格式
  implicit val loanRequestFormat: RootJsonFormat[LoanRequest] = jsonFormat3(LoanRequest.apply)
  
  // 续借请求JSON格式
  implicit val renewalRequestFormat: RootJsonFormat[RenewalRequest] = jsonFormat2(RenewalRequest.apply)
  
  // 借阅统计JSON格式
  implicit val loanStatisticsFormat: RootJsonFormat[LoanStatistics] = jsonFormat3(LoanStatistics.apply)
}
```

## 10.7 RESTful API路由

### 10.7.1 图书路由

```scala
// src/main/scala/com/library/routes/BookRoutes.scala
package com.library.routes

import akka.http.scaladsl.model.StatusCodes
import akka.http.scaladsl.server.Directives._
import com.library.json.BookJsonProtocol._
import com.library.model._
import com.library.service.BookService
import spray.json._

class BookRoutes(bookService: BookService) {
  val routes = pathPrefix("books") {
    get {
      pathEndOrSingleSlash {
        complete {
          bookService.getAllBooks().map { books =>
            StatusCodes.OK -> books.toJson
          }
        }
      } ~
      path(LongNumber) { id =>
        complete {
          bookService.getBookById(id).map {
            case None => StatusCodes.NotFound -> JsObject("error" -> JsString(s"Book with id $id not found"))
            case Some(book) => StatusCodes.OK -> book.toJson
          }
        }
      } ~
      path("search") {
        parameters("title".?, "author".?, "category".?, "available".as[Boolean]?) {
          (title, author, category, available) =>
            val criteria = BookSearchCriteria(title, author, category, available)
            complete {
              bookService.searchBooks(criteria).map { books =>
                StatusCodes.OK -> books.toJson
              }
            }
        }
      } ~
      path("available") {
        parameters("limit".as[Int].?(20)) { limit =>
          complete {
            bookService.getAvailableBooks(limit).map { books =>
              StatusCodes.OK -> books.toJson
            }
          }
        }
      } ~
      path("popular") {
        parameters("limit".as[Int].?(10)) { limit =>
          complete {
            bookService.getPopularBooks(limit).map { books =>
              StatusCodes.OK -> books.toJson
            }
          }
        }
      } ~
      path(Segment) { category =>
        parameters("limit".as[Int].?(20)) { limit =>
          complete {
            bookService.getBooksByCategory(category, limit).map { books =>
              StatusCodes.OK -> books.toJson
            }
          }
        }
      }
    } ~
    post {
      pathEndOrSingleSlash {
        entity(as[Book]) { book =>
          complete {
            bookService.addBook(book).map {
              case Right(createdBook) => StatusCodes.Created -> createdBook.toJson
              case Left(error) => StatusCodes.BadRequest -> JsObject("error" -> JsString(error))
            }
          }
        }
      } ~
      path(LongNumber / "borrow") { id =>
        complete {
          bookService.borrowBook(id).map {
            case Right(book) => StatusCodes.OK -> book.toJson
            case Left(error) => StatusCodes.BadRequest -> JsObject("error" -> JsString(error))
          }
        }
      } ~
      path(LongNumber / "return") { id =>
        complete {
          bookService.returnBook(id).map {
            case Right(book) => StatusCodes.OK -> book.toJson
            case Left(error) => StatusCodes.BadRequest -> JsObject("error" -> JsString(error))
          }
        }
      }
    } ~
    put {
      path(LongNumber) { id =>
        entity(as[BookUpdateRequest]) { request =>
          complete {
            bookService.updateBook(id, request).map {
              case Right(updatedBook) => StatusCodes.OK -> updatedBook.toJson
              case Left(error) => StatusCodes.NotFound -> JsObject("error" -> JsString(error))
            }
          }
        }
      }
    } ~
    delete {
      path(LongNumber) { id =>
        complete {
          bookService.deleteBook(id).map {
            case Right(success) => StatusCodes.OK -> JsObject("success" -> JsBoolean(success))
            case Left(error) => StatusCodes.NotFound -> JsObject("error" -> JsString(error))
          }
        }
      }
    }
  }
}
```

### 10.7.2 用户路由

```scala
// src/main/scala/com/library/routes/UserRoutes.scala
package com.library.routes

import akka.http.scaladsl.model.StatusCodes
import akka.http.scaladsl.server.Directives._
import com.library.json.UserJsonProtocol._
import com.library.model._
import com.library.service.UserService
import spray.json._

class UserRoutes(userService: UserService) {
  val routes = pathPrefix("users") {
    get {
      pathEndOrSingleSlash {
        complete {
          userService.getAllUsers().map { users =>
            StatusCodes.OK -> users.toJson
          }
        }
      } ~
      path(LongNumber) { id =>
        complete {
          userService.getUserById(id).map {
            case None => StatusCodes.NotFound -> JsObject("error" -> JsString(s"User with id $id not found"))
            case Some(user) => StatusCodes.OK -> user.toJson
          }
        }
      } ~
      path("type" / Segment) { userTypeString =>
        val userType = userTypeString.toUpperCase match {
          case "READER" => Reader
          case "LIBRARIAN" => Librarian
          case _ => throw new IllegalArgumentException(s"Invalid user type: $userTypeString")
        }
        
        complete {
          userService.getUsersByType(userType).map { users =>
            StatusCodes.OK -> users.toJson
          }
        }
      }
    } ~
    post {
      pathEndOrSingleSlash {
        entity(as[UserCreateRequest]) { request =>
          complete {
            userService.createUser(request).map {
              case Right(createdUser) => StatusCodes.Created -> createdUser.toJson
              case Left(error) => StatusCodes.BadRequest -> JsObject("error" -> JsString(error))
            }
          }
        }
      } ~
      path("login") {
        entity(as[LoginRequest]) { request =>
          complete {
            userService.login(request).map {
              case Right(authResponse) => StatusCodes.OK -> authResponse.toJson
              case Left(error) => StatusCodes.Unauthorized -> JsObject("error" -> JsString(error))
            }
          }
        }
      }
    } ~
    put {
      path(LongNumber) { id =>
        entity(as[UserUpdateRequest]) { request =>
          complete {
            userService.updateUser(id, request).map {
              case Right(updatedUser) => StatusCodes.OK -> updatedUser.toJson
              case Left(error) => StatusCodes.NotFound -> JsObject("error" -> JsString(error))
            }
          }
        }
      } ~
      path(LongNumber / "active" / Segment) { (id, status) =>
        val active = status.toBoolean
        complete {
          userService.updateUserActiveStatus(id, active).map {
            case Right(success) => StatusCodes.OK -> JsObject("success" -> JsBoolean(success))
            case Left(error) => StatusCodes.NotFound -> JsObject("error" -> JsString(error))
          }
        }
      }
    } ~
    delete {
      path(LongNumber) { id =>
        complete {
          userService.deleteUser(id).map {
            case Right(success) => StatusCodes.OK -> JsObject("success" -> JsBoolean(success))
            case Left(error) => StatusCodes.NotFound -> JsObject("error" -> JsString(error))
          }
        }
      }
    }
  }
}
```

### 10.7.3 借阅路由

```scala
// src/main/scala/com/library/routes/LoanRoutes.scala
package com.library.routes

import akka.http.scaladsl.model.StatusCodes
import akka.http.scaladsl.server.Directives._
import com.library.json.LoanJsonProtocol._
import com.library.model._
import com.library.service.LoanService
import spray.json._

class LoanRoutes(loanService: LoanService) {
  val routes = pathPrefix("loans") {
    get {
      pathEndOrSingleSlash {
        complete {
          loanService.getAllLoans().map { loans =>
            StatusCodes.OK -> loans.toJson
          }
        }
      } ~
      path(LongNumber) { id =>
        complete {
          loanService.getUserLoans(id).map { loans =>
            StatusCodes.OK -> loans.toJson
          }
        }
      } ~
      path("book" / LongNumber) { bookId =>
        complete {
          loanService.getBookLoans(bookId).map { loans =>
            StatusCodes.OK -> loans.toJson
          }
        }
      } ~
      path("user" / LongNumber / "history") { userId =>
        parameters("limit".as[Int].?(20)) { limit =>
          complete {
            loanService.getUserLoanHistory(userId, limit).map { loans =>
              StatusCodes.OK -> loans.toJson
            }
          }
        }
      } ~
      path("overdue") {
        complete {
          loanService.getOverdueLoans().map { loans =>
            StatusCodes.OK -> loans.toJson
          }
        }
      } ~
      path("statistics") {
        complete {
          loanService.getLoanStatistics().map { stats =>
            StatusCodes.OK -> stats.toJson
          }
        }
      }
    } ~
    post {
      path("borrow") {
        entity(as[LoanRequest]) { request =>
          complete {
            loanService.borrowBook(request).map {
              case Right(loan) => StatusCodes.Created -> loan.toJson
              case Left(error) => StatusCodes.BadRequest -> JsObject("error" -> JsString(error))
            }
          }
        }
      } ~
      path(LongNumber / "return") { loanId =>
        complete {
          loanService.returnBook(loanId).map {
            case Right(loan) => StatusCodes.OK -> loan.toJson
            case Left(error) => StatusCodes.BadRequest -> JsObject("error" -> JsString(error))
          }
        }
      } ~
      path("renew") {
        entity(as[RenewalRequest]) { request =>
          complete {
            loanService.renewLoan(request).map {
              case Right(loan) => StatusCodes.OK -> loan.toJson
              case Left(error) => StatusCodes.BadRequest -> JsObject("error" -> JsString(error))
            }
          }
        }
      }
    } ~
    put {
      path("overdue" / "update") {
        complete {
          loanService.updateOverdueLoans().map { count =>
            StatusCodes.OK -> JsObject("updated" -> JsNumber(count))
          }
        }
      }
    }
  }
}
```

### 10.7.4 API路由组合

```scala
// src/main/scala/com/library/routes/ApiRoutes.scala
package com.library.routes

import akka.http.scaladsl.model._
import akka.http.scaladsl.server.Directives._
import com.library.service.{BookService, UserService, LoanService}
import spray.json._

class ApiRoutes(
  bookService: BookService,
  userService: UserService,
  loanService: LoanService
) {
  // 创建路由实例
  private val bookRoutes = new BookRoutes(bookService)
  private val userRoutes = new UserRoutes(userService)
  private val loanRoutes = new LoanRoutes(loanService)
  
  // 组合所有路由
  val routes = pathPrefix("api") {
    // API版本控制
    pathPrefix("v1") {
      bookRoutes.routes ~
      userRoutes.routes ~
      loanRoutes.routes
    }
  } ~
  // API文档路由
  path("docs") {
    getFromResource("api-docs.html")
  } ~
  // 健康检查
  path("health") {
    get {
      complete(StatusCodes.OK, JsObject("status" -> JsString("UP")))
    }
  }
}
```

## 10.8 Actor并发模型

### 10.8.1 图书Actor

```scala
// src/main/scala/com/library/actors/BookActor.scala
package com.library.actors

import akka.actor.typed.{ActorRef, Behavior}
import akka.actor.typed.scaladsl.Behaviors
import com.library.model.{Book, BookUpdateRequest}
import com.library.service.BookService
import spray.json._
import scala.concurrent.ExecutionContext

// 图书Actor消息
sealed trait BookCommand
case class GetBook(id: Long, replyTo: ActorRef[BookResponse]) extends BookCommand
case class SearchBooks(criteria: String, replyTo: ActorRef[BooksResponse]) extends BookCommand
case class CreateBook(book: Book, replyTo: ActorRef[BookResponse]) extends BookCommand
case class UpdateBook(id: Long, request: BookUpdateRequest, replyTo: ActorRef[BookResponse]) extends BookCommand
case class DeleteBook(id: Long, replyTo: ActorRef[DeleteResponse]) extends BookCommand
case class BorrowBook(id: Long, replyTo: ActorRef[BookResponse]) extends BookCommand
case class ReturnBook(id: Long, replyTo: ActorRef[BookResponse]) extends BookCommand

// 图书Actor响应
sealed trait BookResponse
case class BookFound(book: Option[Book]) extends BookResponse
case class BookCreated(book: Book) extends BookResponse
case class BookUpdated(book: Book) extends BookResponse
case class BookError(message: String) extends BookResponse

case class BooksResponse(books: Seq[Book])
case class DeleteResponse(success: Boolean, message: String)

// 图书Actor
object BookActor {
  def apply(bookService: BookService)(implicit ec: ExecutionContext): Behavior[BookCommand] = {
    Behaviors.receiveMessage {
      case GetBook(id, replyTo) =>
        bookService.getBookById(id).map {
          case Some(book) => replyTo ! BookFound(Some(book))
          case None => replyTo ! BookFound(None)
        }
        Behaviors.same
        
      case SearchBooks(criteria, replyTo) =>
        // 解析搜索条件并执行搜索
        // 这里简化处理，实际应用中应该解析查询参数
        bookService.getAllBooks().map { books =>
          replyTo ! BooksResponse(books)
        }
        Behaviors.same
        
      case CreateBook(book, replyTo) =>
        bookService.addBook(book).map {
          case Right(createdBook) => replyTo ! BookCreated(createdBook)
          case Left(error) => replyTo ! BookError(error)
        }
        Behaviors.same
        
      case UpdateBook(id, request, replyTo) =>
        bookService.updateBook(id, request).map {
          case Right(updatedBook) => replyTo ! BookUpdated(updatedBook)
          case Left(error) => replyTo ! BookError(error)
        }
        Behaviors.same
        
      case DeleteBook(id, replyTo) =>
        bookService.deleteBook(id).map {
          case Right(success) => replyTo ! DeleteResponse(success, "Book deleted successfully")
          case Left(error) => replyTo ! DeleteResponse(false, error)
        }
        Behaviors.same
        
      case BorrowBook(id, replyTo) =>
        bookService.borrowBook(id).map {
          case Right(book) => replyTo ! BookUpdated(book)
          case Left(error) => replyTo ! BookError(error)
        }
        Behaviors.same
        
      case ReturnBook(id, replyTo) =>
        bookService.returnBook(id).map {
          case Right(book) => replyTo ! BookUpdated(book)
          case Left(error) => replyTo ! BookError(error)
        }
        Behaviors.same
    }
  }
}
```

### 10.8.2 用户Actor

```scala
// src/main/scala/com/library/actors/UserActor.scala
package com.library.actors

import akka.actor.typed.{ActorRef, Behavior}
import akka.actor.typed.scaladsl.Behaviors
import com.library.model.{User, UserCreateRequest, UserUpdateRequest, LoginRequest, AuthResponse}
import com.library.service.UserService
import spray.json._
import scala.concurrent.ExecutionContext

// 用户Actor消息
sealed trait UserCommand
case class GetUser(id: Long, replyTo: ActorRef[UserResponse]) extends UserCommand
case class CreateUser(request: UserCreateRequest, replyTo: ActorRef[UserResponse]) extends UserCommand
case class UpdateUser(id: Long, request: UserUpdateRequest, replyTo: ActorRef[UserResponse]) extends UserCommand
case class DeleteUser(id: Long, replyTo: ActorRef[DeleteResponse]) extends UserCommand
case class Login(request: LoginRequest, replyTo: ActorRef[AuthResponseWrapper]) extends UserCommand
case class UpdateUserStatus(id: Long, active: Boolean, replyTo: ActorRef[UpdateStatusResponse]) extends UserCommand

// 用户Actor响应
sealed trait UserResponse
case class UserFound(user: Option[User]) extends UserResponse
case class UserCreated(user: User) extends UserResponse
case class UserUpdated(user: User) extends UserResponse
case class UserError(message: String) extends UserResponse

case class AuthResponseWrapper(response: Either[String, AuthResponse])
case class UpdateStatusResponse(success: Boolean, message: String)

// 用户Actor
object UserActor {
  def apply(userService: UserService)(implicit ec: ExecutionContext): Behavior[UserCommand] = {
    Behaviors.receiveMessage {
      case GetUser(id, replyTo) =>
        userService.getUserById(id).map {
          case Some(user) => replyTo ! UserFound(Some(user))
          case None => replyTo ! UserFound(None)
        }
        Behaviors.same
        
      case CreateUser(request, replyTo) =>
        userService.createUser(request).map {
          case Right(createdUser) => replyTo ! UserCreated(createdUser)
          case Left(error) => replyTo ! UserError(error)
        }
        Behaviors.same
        
      case UpdateUser(id, request, replyTo) =>
        userService.updateUser(id, request).map {
          case Right(updatedUser) => replyTo ! UserUpdated(updatedUser)
          case Left(error) => replyTo ! UserError(error)
        }
        Behaviors.same
        
      case DeleteUser(id, replyTo) =>
        userService.deleteUser(id).map {
          case Right(success) => replyTo ! DeleteResponse(success, "User deleted successfully")
          case Left(error) => replyTo ! DeleteResponse(false, error)
        }
        Behaviors.same
        
      case Login(request, replyTo) =>
        userService.login(request).map { response =>
          replyTo ! AuthResponseWrapper(response)
        }
        Behaviors.same
        
      case UpdateUserStatus(id, active, replyTo) =>
        userService.updateUserActiveStatus(id, active).map {
          case Right(success) => replyTo ! UpdateStatusResponse(success, "User status updated successfully")
          case Left(error) => replyTo ! UpdateStatusResponse(false, error)
        }
        Behaviors.same
    }
  }
}
```

### 10.8.3 借阅Actor

```scala
// src/main/scala/com/library/actors/LoanActor.scala
package com.library.actors

import akka.actor.typed.{ActorRef, Behavior}
import akka.actor.typed.scaladsl.Behaviors
import com.library.model.{Loan, LoanRequest, RenewalRequest, LoanStatistics}
import com.library.service.LoanService
import spray.json._
import scala.concurrent.ExecutionContext

// 借阅Actor消息
sealed trait LoanCommand
case class GetUserLoans(userId: Long, replyTo: ActorRef[LoansResponse]) extends LoanCommand
case class GetBookLoans(bookId: Long, replyTo: ActorRef[LoansResponse]) extends LoanCommand
case class BorrowBook(request: LoanRequest, replyTo: ActorRef[LoanResponse]) extends LoanCommand
case class ReturnBook(loanId: Long, replyTo: ActorRef[LoanResponse]) extends LoanCommand
case class RenewLoan(request: RenewalRequest, replyTo: ActorRef[LoanResponse]) extends LoanCommand
case class GetOverdueLoans(replyTo: ActorRef[LoansResponse]) extends LoanCommand
case class UpdateOverdueLoans(replyTo: ActorRef[UpdateOverdueResponse]) extends LoanCommand
case class GetLoanStatistics(replyTo: ActorRef[LoanStatisticsResponse]) extends LoanCommand

// 借阅Actor响应
sealed trait LoanResponse
case class LoanCreated(loan: Loan) extends LoanResponse
case class LoanUpdated(loan: Loan) extends LoanResponse
case class LoanError(message: String) extends LoanResponse

case class LoansResponse(loans: Seq[Loan])
case class UpdateOverdueResponse(count: Int)
case class LoanStatisticsResponse(stats: LoanStatistics)

// 借阅Actor
object LoanActor {
  def apply(loanService: LoanService)(implicit ec: ExecutionContext): Behavior[LoanCommand] = {
    Behaviors.receiveMessage {
      case GetUserLoans(userId, replyTo) =>
        loanService.getUserLoans(userId).map { loans =>
          replyTo ! LoansResponse(loans)
        }
        Behaviors.same
        
      case GetBookLoans(bookId, replyTo) =>
        loanService.getBookLoans(bookId).map { loans =>
          replyTo ! LoansResponse(loans)
        }
        Behaviors.same
        
      case BorrowBook(request, replyTo) =>
        loanService.borrowBook(request).map {
          case Right(loan) => replyTo ! LoanCreated(loan)
          case Left(error) => replyTo ! LoanError(error)
        }
        Behaviors.same
        
      case ReturnBook(loanId, replyTo) =>
        loanService.returnBook(loanId).map {
          case Right(loan) => replyTo ! LoanUpdated(loan)
          case Left(error) => replyTo ! LoanError(error)
        }
        Behaviors.same
        
      case RenewLoan(request, replyTo) =>
        loanService.renewLoan(request).map {
          case Right(loan) => replyTo ! LoanUpdated(loan)
          case Left(error) => replyTo ! LoanError(error)
        }
        Behaviors.same
        
      case GetOverdueLoans(replyTo) =>
        loanService.getOverdueLoans().map { loans =>
          replyTo ! LoansResponse(loans)
        }
        Behaviors.same
        
      case UpdateOverdueLoans(replyTo) =>
        loanService.updateOverdueLoans().map { count =>
          replyTo ! UpdateOverdueResponse(count)
        }
        Behaviors.same
        
      case GetLoanStatistics(replyTo) =>
        loanService.getLoanStatistics().map { stats =>
          replyTo ! LoanStatisticsResponse(stats)
        }
        Behaviors.same
    }
  }
}
```

## 10.9 应用程序启动类

### 10.9.1 应用程序配置

```scala
// src/main/scala/com/library/util/Config.scala
package com.library.util

import com.typesafe.config.{Config, ConfigFactory}

trait ConfigComponent {
  def config: Config = ConfigFactory.load()
}

trait DatabaseConfigComponent extends ConfigComponent {
  import com.library.model.database.Database
  
  lazy val database = Database(config)
}

trait ExecutionContextComponent {
  import scala.concurrent.ExecutionContext
  
  implicit lazy val ec: ExecutionContext = ExecutionContext.global
}
```

### 10.9.2 应用程序主类

```scala
// src/main/scala/com/library/Main.scala
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
  
  // 创建Actor实例
  val guardianBehavior = Behaviors.setup { context =>
    // 创建Actor引用
    val bookActor = context.spawn(BookActor(bookService), "bookActor")
    val userActor = context.spawn(UserActor(userService), "userActor")
    val loanActor = context.spawn(LoanActor(loanService), "loanActor")
    
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
    
    Behaviors.empty
  }
  
  // 启动Actor系统
  val system = ActorSystem[Nothing](guardianBehavior, "library-management-system")
}
```

## 10.10 测试

### 10.10.1 服务层测试

```scala
// src/test/scala/com/library/service/BookServiceTest.scala
package com.library.service

import com.library.model._
import com.library.repository.BookRepository
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers
import org.mockito.MockitoSugar
import scala.concurrent.{ExecutionContext, Future}
import java.time.LocalDate

class BookServiceTest extends AnyFlatSpec with Matchers with MockitoSugar {
  implicit val ec: ExecutionContext = ExecutionContext.global
  
  val mockBookRepository = mock[BookRepository]
  val bookService = new BookService(mockBookRepository)
  
  "BookService" should "get all books" in {
    val books = Seq(
      Book(Some(1), "978-3-16-148410-0", "Scala Programming", "Martin Odersky", 
            "O'Reilly", LocalDate.of(2016, 11, 24), "Programming", 
            "A comprehensive guide to Scala programming", true, 3, 3),
      Book(Some(2), "978-1-4919-5086-5", "Akka in Action", " Raymond Roestenburg", 
            "Manning", LocalDate.of(2016, 9, 30), "Programming", 
            "A hands-on guide to building distributed systems with Akka", true, 2, 2)
    )
    
    when(mockBookRepository.findAll()).thenReturn(Future.successful(books))
    
    val result = bookService.getAllBooks()
    result.futureValue shouldEqual books
  }
  
  it should "add a new book successfully" in {
    val book = Book(None, "978-0-321-76611-0", "Programming in Scala", "Martin Odersky", 
                   "Artima", LocalDate.of(2010, 12, 15), "Programming", 
                   "A comprehensive step-by-step guide", true, 5, 5)
    
    val createdBook = book.copy(id = Some(3))
    
    when(mockBookRepository.findByIsbn(book.isbn)).thenReturn(Future.successful(None))
    when(mockBookRepository.create(book)).thenReturn(Future.successful(createdBook))
    
    val result = bookService.addBook(book)
    result.futureValue shouldEqual Right(createdBook)
  }
  
  it should "fail to add a book with existing ISBN" in {
    val existingBook = Book(Some(1), "978-3-16-148410-0", "Existing Book", "Author", 
                            "Publisher", LocalDate.now(), "Category", 
                            "Description", true, 1, 1)
    
    val newBook = Book(None, "978-3-16-148410-0", "New Book", "Author", 
                      "Publisher", LocalDate.now(), "Category", 
                      "Description", true, 1, 1)
    
    when(mockBookRepository.findByIsbn(newBook.isbn)).thenReturn(Future.successful(Some(existingBook)))
    
    val result = bookService.addBook(newBook)
    result.futureValue shouldEqual Left("Book with ISBN 978-3-16-148410-0 already exists")
  }
  
  it should "borrow a book successfully" in {
    val book = Book(Some(1), "978-3-16-148410-0", "Scala Programming", "Martin Odersky", 
                   "O'Reilly", LocalDate.of(2016, 11, 24), "Programming", 
                   "A comprehensive guide to Scala programming", true, 3, 2)
    
    val borrowedBook = book.copy(availableCopies = 1, available = true)
    
    when(mockBookRepository.findById(1)).thenReturn(Future.successful(Some(book)))
    when(mockBookRepository.updateBookAvailability(1, 1)).thenReturn(Future.successful(true))
    
    val result = bookService.borrowBook(1)
    result.futureValue shouldEqual Right(borrowedBook)
  }
  
  it should "fail to borrow an unavailable book" in {
    val book = Book(Some(1), "978-3-16-148410-0", "Scala Programming", "Martin Odersky", 
                   "O'Reilly", LocalDate.of(2016, 11, 24), "Programming", 
                   "A comprehensive guide to Scala programming", false, 0, 0)
    
    when(mockBookRepository.findById(1)).thenReturn(Future.successful(Some(book)))
    
    val result = bookService.borrowBook(1)
    result.futureValue shouldEqual Left("Book Scala Programming is not available")
  }
}
```

### 10.10.2 API路由测试

```scala
// src/test/scala/com/library/routes/BookRoutesTest.scala
package com.library.routes

import akka.actor.ActorSystem
import akka.http.scaladsl.model.StatusCodes
import akka.http.scaladsl.testkit.ScalatestRouteTest
import com.library.json.BookJsonProtocol._
import com.library.model.Book
import com.library.service.BookService
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers
import org.mockito.MockitoSugar
import spray.json._
import java.time.LocalDate

class BookRoutesTest extends AnyFlatSpec with Matchers with ScalatestRouteTest with MockitoSugar {
  import com.library.json.BookJsonProtocol._
  
  implicit val system: ActorSystem = ActorSystem("test-system")
  
  val mockBookService = mock[BookService]
  val bookRoutes = new BookRoutes(mockBookService)
  
  "BookRoutes" should "return all books" in {
    val books = Seq(
      Book(Some(1), "978-3-16-148410-0", "Scala Programming", "Martin Odersky", 
            "O'Reilly", LocalDate.of(2016, 11, 24), "Programming", 
            "A comprehensive guide to Scala programming", true, 3, 3),
      Book(Some(2), "978-1-4919-5086-5", "Akka in Action", " Raymond Roestenburg", 
            "Manning", LocalDate.of(2016, 9, 30), "Programming", 
            "A hands-on guide to building distributed systems with Akka", true, 2, 2)
    )
    
    when(mockBookService.getAllBooks()).thenReturn(Future.successful(books))
    
    Get("/api/v1/books") ~> bookRoutes.routes ~> check {
      status shouldEqual StatusCodes.OK
      responseAs[String].parseJson shouldEqual books.toJson
    }
  }
  
  it should "return a specific book by ID" in {
    val book = Book(Some(1), "978-3-16-148410-0", "Scala Programming", "Martin Odersky", 
                   "O'Reilly", LocalDate.of(2016, 11, 24), "Programming", 
                   "A comprehensive guide to Scala programming", true, 3, 3)
    
    when(mockBookService.getBookById(1)).thenReturn(Future.successful(Some(book)))
    
    Get("/api/v1/books/1") ~> bookRoutes.routes ~> check {
      status shouldEqual StatusCodes.OK
      responseAs[String].parseJson shouldEqual book.toJson
    }
  }
  
  it should "return 404 for non-existent book" in {
    when(mockBookService.getBookById(999)).thenReturn(Future.successful(None))
    
    Get("/api/v1/books/999") ~> bookRoutes.routes ~> check {
      status shouldEqual StatusCodes.NotFound
    }
  }
  
  it should "create a new book" in {
    val book = Book(None, "978-0-321-76611-0", "Programming in Scala", "Martin Odersky", 
                   "Artima", LocalDate.of(2010, 12, 15), "Programming", 
                   "A comprehensive step-by-step guide", true, 5, 5)
    
    val createdBook = book.copy(id = Some(3))
    
    when(mockBookService.addBook(book)).thenReturn(Future.successful(Right(createdBook)))
    
    Post("/api/v1/books", book.toJson) ~> bookRoutes.routes ~> check {
      status shouldEqual StatusCodes.Created
      responseAs[String].parseJson shouldEqual createdBook.toJson
    }
  }
}
```

## 10.11 部署指南

### 10.11.1 构建应用

使用sbt构建应用程序：

```bash
# 编译项目
sbt compile

# 运行测试
sbt test

# 打包应用
sbt assembly

# 运行应用
sbt run
```

### 10.11.2 Docker部署

创建Dockerfile：

```dockerfile
FROM openjdk:11-jre-slim

WORKDIR /app

# 复制打包好的JAR文件
COPY target/scala-2.13/library-management-system-assembly-1.0.0.jar app.jar

# 暴露端口
EXPOSE 8080

# 运行应用
ENTRYPOINT ["java", "-jar", "app.jar"]
```

构建Docker镜像：

```bash
docker build -t library-management-system .
docker run -p 8080:8080 library-management-system
```

### 10.11.3 Kubernetes部署

创建Kubernetes部署文件：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: library-management-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: library-management-system
  template:
    metadata:
      labels:
        app: library-management-system
    spec:
      containers:
      - name: library-management-system
        image: library-management-system:latest
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          value: "jdbc:postgresql://postgres:5432/library"
        - name: DATABASE_USER
          value: "library_user"
        - name: DATABASE_PASSWORD
          value: "library_password"
---
apiVersion: v1
kind: Service
metadata:
  name: library-management-system-service
spec:
  selector:
    app: library-management-system
  ports:
  - protocol: TCP
    port: 8080
    targetPort: 8080
  type: LoadBalancer
```

## 总结

本章通过一个完整的图书管理系统项目，展示了如何综合应用前面学到的Scala知识。该项目涵盖了：

1. **领域建模**：使用Scala的case class、sealed trait等特性构建类型安全的领域模型
2. **数据访问层**：使用Slick构建类型安全的数据库访问
3. **服务层**：实现业务逻辑和错误处理
4. **并发处理**：使用Akka Actors实现并发处理
5. **RESTful API**：使用Akka HTTP构建高性能的Web服务
6. **测试**：使用ScalaTest和Mockito进行单元测试和集成测试

这个项目展示了Scala在实际企业级应用中的强大能力，包括类型安全、函数式编程、并发处理等特性。通过这个项目，读者可以更好地理解如何将Scala知识应用到实际开发中。