package com.example.gherkin.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Objects;

/**
 * 银行账户模型类
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class BankAccount {
    private Long id;
    private String accountNumber;
    private String accountHolderName;
    private AccountType accountType;
    private BigDecimal balance;
    private BigDecimal overdraftLimit;
    private boolean active;
    private boolean verified;
    private LocalDateTime createdAt;
    private LocalDateTime lastTransactionDate;
    
    /**
     * 账户类型枚举
     */
    public enum AccountType {
        CHECKING("支票账户"),
        SAVINGS("储蓄账户"),
        CREDIT("信用账户");
        
        private final String displayName;
        
        AccountType(String displayName) {
            this.displayName = displayName;
        }
        
        public String getDisplayName() {
            return displayName;
        }
    }
    
    /**
     * 检查账户是否活跃且已验证
     * @return 如果账户活跃且已验证返回true，否则返回false
     */
    public boolean isActiveAndVerified() {
        return active && verified;
    }
    
    /**
     * 检查账户是否可以提取指定金额
     * @param amount 要提取的金额
     * @return 如果可以提取返回true，否则返回false
     */
    public boolean canWithdraw(BigDecimal amount) {
        if (amount == null || amount.compareTo(BigDecimal.ZERO) <= 0) {
            return false;
        }
        
        if (!isActiveAndVerified()) {
            return false;
        }
        
        BigDecimal availableBalance = balance.add(overdraftLimit != null ? overdraftLimit : BigDecimal.ZERO);
        return availableBalance.compareTo(amount) >= 0;
    }
    
    /**
     * 提取金额
     * @param amount 要提取的金额
     * @return 如果成功提取返回true，否则返回false
     */
    public boolean withdraw(BigDecimal amount) {
        if (!canWithdraw(amount)) {
            return false;
        }
        
        balance = balance.subtract(amount);
        lastTransactionDate = LocalDateTime.now();
        return true;
    }
    
    /**
     * 存入金额
     * @param amount 要存入的金额
     * @return 如果成功存入返回true，否则返回false
     */
    public boolean deposit(BigDecimal amount) {
        if (amount == null || amount.compareTo(BigDecimal.ZERO) <= 0) {
            return false;
        }
        
        if (!isActiveAndVerified()) {
            return false;
        }
        
        balance = balance.add(amount);
        lastTransactionDate = LocalDateTime.now();
        return true;
    }
    
    /**
     * 转账到另一个账户
     * @param targetAccount 目标账户
     * @param amount 转账金额
     * @return 如果转账成功返回true，否则返回false
     */
    public boolean transferTo(BankAccount targetAccount, BigDecimal amount) {
        if (targetAccount == null || !canWithdraw(amount)) {
            return false;
        }
        
        if (!this.withdraw(amount)) {
            return false;
        }
        
        return targetAccount.deposit(amount);
    }
    
    /**
     * 计算账户的可用余额（包括透支额度）
     * @return 可用余额
     */
    public BigDecimal getAvailableBalance() {
        return balance.add(overdraftLimit != null ? overdraftLimit : BigDecimal.ZERO);
    }
    
    /**
     * 检查账户是否为指定类型
     * @param type 要检查的账户类型
     * @return 如果是指定类型返回true，否则返回false
     */
    public boolean isOfType(AccountType type) {
        return Objects.equals(this.accountType, type);
    }
}