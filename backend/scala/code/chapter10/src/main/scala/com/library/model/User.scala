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