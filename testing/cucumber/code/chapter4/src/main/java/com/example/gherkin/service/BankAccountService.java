package com.example.gherkin.service;

import com.example.gherkin.model.BankAccount;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Predicate;
import java.util.stream.Collectors;

/**
 * 银行账户服务类
 */
@Service
public class BankAccountService {
    private final Map<Long, BankAccount> accounts = new HashMap<>();
    private long nextId = 1L;
    
    /**
     * 初始化一些示例账户
     */
    public BankAccountService() {
        initializeSampleAccounts();
    }
    
    /**
     * 创建新账户
     * @param account 要创建的账户
     * @return 创建的账户（带有生成的ID）
     */
    public BankAccount createAccount(BankAccount account) {
        BankAccount newAccount = BankAccount.builder()
                .id(nextId++)
                .accountNumber(account.getAccountNumber())
                .accountHolderName(account.getAccountHolderName())
                .accountType(account.getAccountType())
                .balance(account.getBalance() != null ? account.getBalance() : BigDecimal.ZERO)
                .overdraftLimit(account.getOverdraftLimit() != null ? account.getOverdraftLimit() : BigDecimal.ZERO)
                .active(account.isActive())
                .verified(account.isVerified())
                .createdAt(LocalDateTime.now())
                .build();
        
        accounts.put(newAccount.getId(), newAccount);
        return newAccount;
    }
    
    /**
     * 根据ID获取账户
     * @param id 账户ID
     * @return 账户的Optional对象
     */
    public Optional<BankAccount> getAccountById(Long id) {
        return Optional.ofNullable(accounts.get(id));
    }
    
    /**
     * 根据账号获取账户
     * @param accountNumber 账号
     * @return 账户的Optional对象
     */
    public Optional<BankAccount> getAccountByNumber(String accountNumber) {
        return accounts.values().stream()
                .filter(a -> a.getAccountNumber().equals(accountNumber))
                .findFirst();
    }
    
    /**
     * 获取所有账户
     * @return 所有账户的列表
     */
    public List<BankAccount> getAllAccounts() {
        return new ArrayList<>(accounts.values());
    }
    
    /**
     * 根据条件搜索账户
     * @param predicate 搜索条件
     * @return 符合条件的账户列表
     */
    public List<BankAccount> searchAccounts(Predicate<BankAccount> predicate) {
        return accounts.values().stream()
                .filter(predicate)
                .collect(Collectors.toList());
    }
    
    /**
     * 根据账户持有人姓名搜索账户
     * @param holderName 账户持有人姓名或部分姓名
     * @return 匹配的账户列表
     */
    public List<BankAccount> searchAccountsByHolderName(String holderName) {
        return searchAccounts(a -> 
            a.getAccountHolderName() != null && 
            a.getAccountHolderName().toLowerCase().contains(holderName.toLowerCase()));
    }
    
    /**
     * 根据账户类型搜索账户
     * @param accountType 账户类型
     * @return 匹配的账户列表
     */
    public List<BankAccount> searchAccountsByType(BankAccount.AccountType accountType) {
        return searchAccounts(a -> a.isOfType(accountType));
    }
    
    /**
     * 根据余额范围搜索账户
     * @param minBalance 最低余额（可为null表示无下限）
     * @param maxBalance 最高余额（可为null表示无上限）
     * @return 匹配的账户列表
     */
    public List<BankAccount> searchAccountsByBalanceRange(BigDecimal minBalance, BigDecimal maxBalance) {
        return searchAccounts(a -> {
            if (a.getBalance() == null) return false;
            if (minBalance != null && a.getBalance().compareTo(minBalance) < 0) return false;
            if (maxBalance != null && a.getBalance().compareTo(maxBalance) > 0) return false;
            return true;
        });
    }
    
    /**
     * 搜索活跃账户
     * @return 活跃账户列表
     */
    public List<BankAccount> searchActiveAccounts() {
        return searchAccounts(BankAccount::isActiveAndVerified);
    }
    
    /**
     * 复合搜索：根据持有人姓名、账户类型和余额范围搜索账户
     * @param holderName 账户持有人姓名（可为null）
     * @param accountType 账户类型（可为null）
     * @param minBalance 最低余额（可为null）
     * @param maxBalance 最高余额（可为null）
     * @return 匹配的账户列表
     */
    public List<BankAccount> searchAccounts(String holderName, BankAccount.AccountType accountType, 
                                           BigDecimal minBalance, BigDecimal maxBalance) {
        return searchAccounts(a -> {
            boolean matches = true;
            
            if (holderName != null && !holderName.isEmpty()) {
                matches = matches && (a.getAccountHolderName() != null && 
                    a.getAccountHolderName().toLowerCase().contains(holderName.toLowerCase()));
            }
            
            if (accountType != null) {
                matches = matches && a.isOfType(accountType);
            }
            
            if (a.getBalance() == null) {
                matches = false;
            } else {
                if (minBalance != null && a.getBalance().compareTo(minBalance) < 0) {
                    matches = false;
                }
                if (maxBalance != null && a.getBalance().compareTo(maxBalance) > 0) {
                    matches = false;
                }
            }
            
            return matches;
        });
    }
    
    /**
     * 更新账户信息
     * @param id 账户ID
     * @param account 更新的账户信息
     * @return 更新后的账户的Optional对象
     */
    public Optional<BankAccount> updateAccount(Long id, BankAccount account) {
        if (!accounts.containsKey(id)) {
            return Optional.empty();
        }
        
        BankAccount existingAccount = accounts.get(id);
        BankAccount updatedAccount = BankAccount.builder()
                .id(id)
                .accountNumber(account.getAccountNumber() != null ? account.getAccountNumber() : existingAccount.getAccountNumber())
                .accountHolderName(account.getAccountHolderName() != null ? account.getAccountHolderName() : existingAccount.getAccountHolderName())
                .accountType(account.getAccountType() != null ? account.getAccountType() : existingAccount.getAccountType())
                .balance(account.getBalance() != null ? account.getBalance() : existingAccount.getBalance())
                .overdraftLimit(account.getOverdraftLimit() != null ? account.getOverdraftLimit() : existingAccount.getOverdraftLimit())
                .active(account.isActive())
                .verified(account.isVerified())
                .createdAt(existingAccount.getCreatedAt())
                .lastTransactionDate(existingAccount.getLastTransactionDate())
                .build();
        
        accounts.put(id, updatedAccount);
        return Optional.of(updatedAccount);
    }
    
    /**
     * 激活账户
     * @param id 账户ID
     * @return 如果激活成功返回true，否则返回false
     */
    public boolean activateAccount(Long id) {
        BankAccount account = accounts.get(id);
        if (account == null) {
            return false;
        }
        
        account.setActive(true);
        return true;
    }
    
    /**
     * 验证账户
     * @param id 账户ID
     * @return 如果验证成功返回true，否则返回false
     */
    public boolean verifyAccount(Long id) {
        BankAccount account = accounts.get(id);
        if (account == null) {
            return false;
        }
        
        account.setVerified(true);
        return true;
    }
    
    /**
     * 存款
     * @param id 账户ID
     * @param amount 存款金额
     * @return 如果存款成功返回true，否则返回false
     */
    public boolean deposit(Long id, BigDecimal amount) {
        BankAccount account = accounts.get(id);
        if (account == null) {
            return false;
        }
        
        return account.deposit(amount);
    }
    
    /**
     * 取款
     * @param id 账户ID
     * @param amount 取款金额
     * @return 如果取款成功返回true，否则返回false
     */
    public boolean withdraw(Long id, BigDecimal amount) {
        BankAccount account = accounts.get(id);
        if (account == null) {
            return false;
        }
        
        return account.withdraw(amount);
    }
    
    /**
     * 转账
     * @param fromId 转出账户ID
     * @param toId 转入账户ID
     * @param amount 转账金额
     * @return 如果转账成功返回true，否则返回false
     */
    public boolean transfer(Long fromId, Long toId, BigDecimal amount) {
        BankAccount fromAccount = accounts.get(fromId);
        BankAccount toAccount = accounts.get(toId);
        
        if (fromAccount == null || toAccount == null) {
            return false;
        }
        
        return fromAccount.transferTo(toAccount, amount);
    }
    
    /**
     * 删除账户
     * @param id 账户ID
     * @return 如果删除成功返回true，否则返回false
     */
    public boolean deleteAccount(Long id) {
        return accounts.remove(id) != null;
    }
    
    /**
     * 初始化一些示例账户
     */
    private void initializeSampleAccounts() {
        createAccount(BankAccount.builder()
                .accountNumber("ACC1001")
                .accountHolderName("张三")
                .accountType(BankAccount.AccountType.CHECKING)
                .balance(new BigDecimal("5000.00"))
                .overdraftLimit(new BigDecimal("1000.00"))
                .active(true)
                .verified(true)
                .build());
                
        createAccount(BankAccount.builder()
                .accountNumber("ACC1002")
                .accountHolderName("李四")
                .accountType(BankAccount.AccountType.SAVINGS)
                .balance(new BigDecimal("12000.00"))
                .overdraftLimit(BigDecimal.ZERO)
                .active(true)
                .verified(true)
                .build());
                
        createAccount(BankAccount.builder()
                .accountNumber("ACC1003")
                .accountHolderName("王五")
                .accountType(BankAccount.AccountType.CREDIT)
                .balance(new BigDecimal("-2000.00"))
                .overdraftLimit(new BigDecimal("5000.00"))
                .active(true)
                .verified(true)
                .build());
                
        createAccount(BankAccount.builder()
                .accountNumber("ACC1004")
                .accountHolderName("赵六")
                .accountType(BankAccount.AccountType.CHECKING)
                .balance(new BigDecimal("3500.00"))
                .overdraftLimit(new BigDecimal("500.00"))
                .active(true)
                .verified(false)
                .build());
                
        createAccount(BankAccount.builder()
                .accountNumber("ACC1005")
                .accountHolderName("钱七")
                .accountType(BankAccount.AccountType.SAVINGS)
                .balance(new BigDecimal("8000.00"))
                .overdraftLimit(BigDecimal.ZERO)
                .active(false)
                .verified(true)
                .build());
    }
}