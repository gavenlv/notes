package com.example.gherkin.transformer;

import com.example.gherkin.model.BankAccount;
import io.cucumber.java.ParameterType;

import java.math.BigDecimal;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

/**
 * 银行账户参数转换器
 */
public class BankAccountTransformer {
    
    /**
     * 将字符串转换为BigDecimal
     */
    @ParameterType(".*")
    public BigDecimal bigDecimal(String value) {
        try {
            return new BigDecimal(value);
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("无法将 '" + value + "' 转换为BigDecimal");
        }
    }
    
    /**
     * 将字符串转换为布尔值
     * 接受的值: true, false, yes, no, 1, 0
     */
    @ParameterType("true|false|yes|no|1|0")
    public boolean booleanValue(String value) {
        return Arrays.asList("true", "yes", "1").contains(value.toLowerCase());
    }
    
    /**
     * 将字符串转换为账户类型
     */
    @ParameterType("支票账户|储蓄账户|信用账户")
    public BankAccount.AccountType accountType(String value) {
        switch (value) {
            case "支票账户":
                return BankAccount.AccountType.CHECKING;
            case "储蓄账户":
                return BankAccount.AccountType.SAVINGS;
            case "信用账户":
                return BankAccount.AccountType.CREDIT;
            default:
                throw new IllegalArgumentException("未知的账户类型: " + value);
        }
    }
    
    /**
     * 将字符串转换为银行账户对象
     * 格式: "账号:持有人:账户类型:余额:透支限额:活跃:已验证"
     */
    @ParameterType("([^:]+):([^:]+):([^:]+):([^:]+):([^:]*):([^:]+):([^:]+)")
    public BankAccount bankAccount(String accountNumber, String accountHolderName, 
                                  String accountType, String balance, String overdraftLimit, 
                                  String active, String verified) {
        
        try {
            return BankAccount.builder()
                    .accountNumber(accountNumber.trim())
                    .accountHolderName(accountHolderName.trim())
                    .accountType(accountType(accountType.trim()))
                    .balance(new BigDecimal(balance.trim()))
                    .overdraftLimit(overdraftLimit.trim().isEmpty() ? 
                                   BigDecimal.ZERO : new BigDecimal(overdraftLimit.trim()))
                    .active(booleanValue(active.trim()))
                    .verified(booleanValue(verified.trim()))
                    .build();
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("无效的银行账户参数: " + e.getMessage());
        }
    }
    
    /**
     * 将逗号分隔的字符串转换为账户类型列表
     */
    @ParameterType("([^,]+(?:,[^,]+)*)")
    public List<BankAccount.AccountType> accountTypeList(String types) {
        return Arrays.asList(types.split(","))
                .stream()
                .map(this::accountType)
                .collect(java.util.stream.Collectors.toList());
    }
    
    /**
     * 将余额范围字符串转换为余额范围数组
     * 格式: "1000-5000" 或 "1000-" 或 "-5000"
     */
    @ParameterType("([0-9.]+)?-([0-9.]+)?")
    public BigDecimal[] balanceRange(String minBalance, String maxBalance) {
        BigDecimal min = minBalance != null && !minBalance.isEmpty() ? 
                        new BigDecimal(minBalance) : null;
        BigDecimal max = maxBalance != null && !maxBalance.isEmpty() ? 
                        new BigDecimal(maxBalance) : null;
        return new BigDecimal[]{min, max};
    }
    
    /**
     * 将余额比较操作符转换为谓词
     * 格式: ">1000", "<5000", "=2000", ">=1000", "<=5000"
     */
    @ParameterType("(>=|<=|>|<|=)([0-9.]+)")
    public BalancePredicate balancePredicate(String operator, String value) {
        BigDecimal balance = new BigDecimal(value);
        return new BalancePredicate(operator, balance);
    }
    
    /**
     * 将转账操作字符串转换为转账参数
     * 格式: "从ACC1001转账1000到ACC1002"
     */
    @ParameterType("从([^:]+)转账([0-9.]+)到([^:]+)")
    public TransferParams transferParams(String fromAccount, String amount, String toAccount) {
        return new TransferParams(fromAccount.trim(), new BigDecimal(amount.trim()), toAccount.trim());
    }
    
    /**
     * 将账户状态字符串转换为账户状态
     */
    @ParameterType("活跃|非活跃|已验证|未验证|活跃且已验证|活跃但未验证|非活跃但已验证|非活跃且未验证")
    public AccountStatus accountStatus(String status) {
        switch (status) {
            case "活跃":
                return new AccountStatus(true, null);
            case "非活跃":
                return new AccountStatus(false, null);
            case "已验证":
                return new AccountStatus(null, true);
            case "未验证":
                return new AccountStatus(null, false);
            case "活跃且已验证":
                return new AccountStatus(true, true);
            case "活跃但未验证":
                return new AccountStatus(true, false);
            case "非活跃但已验证":
                return new AccountStatus(false, true);
            case "非活跃且未验证":
                return new AccountStatus(false, false);
            default:
                throw new IllegalArgumentException("未知的账户状态: " + status);
        }
    }
    
    /**
     * 余额谓词类，用于封装余额比较操作
     */
    public static class BalancePredicate {
        private final String operator;
        private final BigDecimal value;
        
        public BalancePredicate(String operator, BigDecimal value) {
            this.operator = operator;
            this.value = value;
        }
        
        public boolean test(BigDecimal balance) {
            if (balance == null) return false;
            
            switch (operator) {
                case ">":
                    return balance.compareTo(value) > 0;
                case "<":
                    return balance.compareTo(value) < 0;
                case "=":
                    return balance.compareTo(value) == 0;
                case ">=":
                    return balance.compareTo(value) >= 0;
                case "<=":
                    return balance.compareTo(value) <= 0;
                default:
                    return false;
            }
        }
        
        public String getOperator() {
            return operator;
        }
        
        public BigDecimal getValue() {
            return value;
        }
    }
    
    /**
     * 转账参数类，用于封装转账操作参数
     */
    public static class TransferParams {
        private final String fromAccount;
        private final BigDecimal amount;
        private final String toAccount;
        
        public TransferParams(String fromAccount, BigDecimal amount, String toAccount) {
            this.fromAccount = fromAccount;
            this.amount = amount;
            this.toAccount = toAccount;
        }
        
        public String getFromAccount() {
            return fromAccount;
        }
        
        public BigDecimal getAmount() {
            return amount;
        }
        
        public String getToAccount() {
            return toAccount;
        }
    }
    
    /**
     * 账户状态类，用于封装账户状态
     */
    public static class AccountStatus {
        private final Boolean active;
        private final Boolean verified;
        
        public AccountStatus(Boolean active, Boolean verified) {
            this.active = active;
            this.verified = verified;
        }
        
        public boolean matches(BankAccount account) {
            if (account == null) return false;
            
            boolean activeMatch = active == null || account.isActive() == active;
            boolean verifiedMatch = verified == null || account.isVerified() == verified;
            
            return activeMatch && verifiedMatch;
        }
        
        public Boolean getActive() {
            return active;
        }
        
        public Boolean getVerified() {
            return verified;
        }
        
        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder();
            
            if (active != null) {
                sb.append(active ? "活跃" : "非活跃");
            }
            
            if (verified != null) {
                if (sb.length() > 0) {
                    sb.append("且");
                }
                sb.append(verified ? "已验证" : "未验证");
            }
            
            return sb.toString();
        }
    }
}