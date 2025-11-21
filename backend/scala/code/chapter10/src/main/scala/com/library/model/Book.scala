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