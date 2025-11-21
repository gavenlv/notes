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