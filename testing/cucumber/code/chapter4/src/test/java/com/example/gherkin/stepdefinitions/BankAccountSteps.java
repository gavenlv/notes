package com.example.gherkin.stepdefinitions;

import com.example.gherkin.model.BankAccount;
import com.example.gherkin.service.BankAccountService;
import com.example.gherkin.transformer.BankAccountTransformer;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import io.cucumber.java.en.And;
import io.cucumber.datatable.DataTable;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * 银行账户管理功能的步骤定义
 */
@SpringBootTest
public class BankAccountSteps {
    
    @Autowired
    private BankAccountService accountService;
    
    private List<BankAccount> searchResults;
    private BankAccount currentAccount;
    private boolean operationResult;
    private BankAccountTransformer transformer = new BankAccountTransformer();
    
    @Given("系统中有以下银行账户")
    public void thereAreFollowingBankAccounts(DataTable dataTable) {
        List<Map<String, String>> accounts = dataTable.asMaps();
        
        for (Map<String, String> accountData : accounts) {
            BankAccount account = BankAccount.builder()
                    .accountNumber(accountData.get("账号"))
                    .accountHolderName(accountData.get("持有人"))
                    .accountType(transformer.accountType(accountData.get("账户类型")))
                    .balance(new BigDecimal(accountData.get("余额")))
                    .overdraftLimit(new BigDecimal(accountData.get("透支限额")))
                    .active(Boolean.parseBoolean(accountData.get("活跃")))
                    .verified(Boolean.parseBoolean(accountData.get("已验证")))
                    .build();
            
            accountService.createAccount(account);
        }
    }
    
    @Given("系统中存在银行账户 {bankAccount}")
    public void bankAccountExistsInSystem(BankAccount account) {
        accountService.createAccount(account);
    }
    
    @When("用户搜索持有人姓名包含 {string} 的账户")
    public void userSearchesForAccountsWithHolderNameContaining(String holderName) {
        searchResults = accountService.searchAccountsByHolderName(holderName);
    }
    
    @When("用户搜索类型为 {accountType} 的账户")
    public void userSearchesForAccountsWithType(BankAccount.AccountType accountType) {
        searchResults = accountService.searchAccountsByType(accountType);
    }
    
    @When("用户搜索余额在 {string} 到 {string} 之间的账户")
    public void userSearchesForAccountsWithBalanceBetween(String minBalance, String maxBalance) {
        BigDecimal min = minBalance.isEmpty() ? null : new BigDecimal(minBalance);
        BigDecimal max = maxBalance.isEmpty() ? null : new BigDecimal(maxBalance);
        searchResults = accountService.searchAccountsByBalanceRange(min, max);
    }
    
    @When("用户搜索活跃账户")
    public void userSearchesForActiveAccounts() {
        searchResults = accountService.searchActiveAccounts();
    }
    
    @When("用户使用以下条件搜索账户")
    public void userSearchesWithFollowingConditions(DataTable dataTable) {
        Map<String, String> searchCriteria = dataTable.asMap();
        
        String holderName = searchCriteria.get("持有人姓名");
        String accountType = searchCriteria.get("账户类型");
        String minBalance = searchCriteria.get("最低余额");
        String maxBalance = searchCriteria.get("最高余额");
        
        BankAccount.AccountType type = accountType != null && !accountType.isEmpty() ? 
                                       transformer.accountType(accountType) : null;
        BigDecimal min = minBalance != null && !minBalance.isEmpty() ? 
                         new BigDecimal(minBalance) : null;
        BigDecimal max = maxBalance != null && !maxBalance.isEmpty() ? 
                         new BigDecimal(maxBalance) : null;
        
        searchResults = accountService.searchAccounts(holderName, type, min, max);
    }
    
    @When("用户使用场景大纲参数搜索账户: 持有人 {string}, 账户类型 {string}, 余额范围 {string} 到 {string}")
    public void userSearchesWithScenarioOutlineParameters(String holderName, String accountType, String minBalance, String maxBalance) {
        String searchHolderName = holderName.isEmpty() ? null : holderName;
        BankAccount.AccountType type = accountType.isEmpty() ? null : transformer.accountType(accountType);
        
        BigDecimal min = minBalance.isEmpty() ? null : new BigDecimal(minBalance);
        BigDecimal max = maxBalance.isEmpty() ? null : new BigDecimal(maxBalance);
        
        searchResults = accountService.searchAccounts(searchHolderName, type, min, max);
    }
    
    @When("用户使用转换器搜索账户: 持有人 {string}, 账户类型 {accountType}, 余额 {balancePredicate}")
    public void userSearchesWithTransformerParameters(String holderName, BankAccount.AccountType accountType, BankAccountTransformer.BalancePredicate balancePredicate) {
        String searchHolderName = holderName.isEmpty() ? null : holderName;
        
        // 使用余额谓词确定余额范围
        BigDecimal minBalance = null;
        BigDecimal maxBalance = null;
        
        if (balancePredicate != null) {
            switch (balancePredicate.getOperator()) {
                case "=":
                    minBalance = balancePredicate.getValue();
                    maxBalance = balancePredicate.getValue();
                    break;
                case ">":
                case ">=":
                    minBalance = balancePredicate.getValue();
                    break;
                case "<":
                case "<=":
                    maxBalance = balancePredicate.getValue();
                    break;
            }
        }
        
        searchResults = accountService.searchAccounts(searchHolderName, accountType, minBalance, maxBalance);
    }
    
    @When("用户使用余额范围 {balanceRange} 搜索账户")
    public void userSearchesWithBalanceRange(BigDecimal[] balanceRange) {
        BigDecimal minBalance = balanceRange.length > 0 ? balanceRange[0] : null;
        BigDecimal maxBalance = balanceRange.length > 1 ? balanceRange[1] : null;
        
        searchResults = accountService.searchAccountsByBalanceRange(minBalance, maxBalance);
    }
    
    @When("用户执行转账操作 {transferParams}")
    public void userPerformsTransferOperation(BankAccountTransformer.TransferParams transferParams) {
        Optional<BankAccount> fromAccount = accountService.getAccountByNumber(transferParams.getFromAccount());
        Optional<BankAccount> toAccount = accountService.getAccountByNumber(transferParams.getToAccount());
        
        if (fromAccount.isPresent() && toAccount.isPresent()) {
            operationResult = accountService.transfer(
                    fromAccount.get().getId(), 
                    toAccount.get().getId(), 
                    transferParams.getAmount());
        } else {
            operationResult = false;
        }
    }
    
    @When("用户向账户 {string} 存款 {string}")
    public void userDepositsToAccount(String accountNumber, String amount) {
        Optional<BankAccount> account = accountService.getAccountByNumber(accountNumber);
        if (account.isPresent()) {
            operationResult = accountService.deposit(account.get().getId(), new BigDecimal(amount));
        } else {
            operationResult = false;
        }
    }
    
    @When("用户从账户 {string} 取款 {string}")
    public void userWithdrawsFromAccount(String accountNumber, String amount) {
        Optional<BankAccount> account = accountService.getAccountByNumber(accountNumber);
        if (account.isPresent()) {
            operationResult = accountService.withdraw(account.get().getId(), new BigDecimal(amount));
        } else {
            operationResult = false;
        }
    }
    
    @When("用户激活账户 {string}")
    public void userActivatesAccount(String accountNumber) {
        Optional<BankAccount> account = accountService.getAccountByNumber(accountNumber);
        if (account.isPresent()) {
            operationResult = accountService.activateAccount(account.get().getId());
        } else {
            operationResult = false;
        }
    }
    
    @When("用户验证账户 {string}")
    public void userVerifiesAccount(String accountNumber) {
        Optional<BankAccount> account = accountService.getAccountByNumber(accountNumber);
        if (account.isPresent()) {
            operationResult = accountService.verifyAccount(account.get().getId());
        } else {
            operationResult = false;
        }
    }
    
    @When("用户查看账户 {string} 的详细信息")
    public void userViewsAccountDetails(String accountNumber) {
        Optional<BankAccount> account = accountService.getAccountByNumber(accountNumber);
        currentAccount = account.orElse(null);
    }
    
    @Then("搜索结果应包含 {int} 个账户")
    public void searchResultsShouldContainAccounts(int count) {
        assertThat(searchResults).hasSize(count);
    }
    
    @Then("搜索结果应包含账户 {string}")
    public void searchResultsShouldContainAccount(String accountNumber) {
        assertThat(searchResults)
                .extracting(BankAccount::getAccountNumber)
                .contains(accountNumber);
    }
    
    @Then("搜索结果不应包含账户 {string}")
    public void searchResultsShouldNotContainAccount(String accountNumber) {
        assertThat(searchResults)
                .extracting(BankAccount::getAccountNumber)
                .doesNotContain(accountNumber);
    }
    
    @Then("搜索结果中的所有账户都是 {accountType} 类型")
    public void allAccountsInSearchResultsShouldBeOfType(BankAccount.AccountType accountType) {
        assertThat(searchResults)
                .allMatch(account -> account.isOfType(accountType));
    }
    
    @Then("搜索结果中的所有账户余额都在 {string} 到 {string} 之间")
    public void allAccountsInSearchResultsShouldHaveBalanceBetween(String minBalance, String maxBalance) {
        BigDecimal min = new BigDecimal(minBalance);
        BigDecimal max = new BigDecimal(maxBalance);
        
        assertThat(searchResults)
                .allMatch(account -> {
                    BigDecimal balance = account.getBalance();
                    return balance.compareTo(min) >= 0 && balance.compareTo(max) <= 0;
                });
    }
    
    @Then("搜索结果中的所有账户都是活跃且已验证的")
    public void allAccountsInSearchResultsShouldBeActiveAndVerified() {
        assertThat(searchResults)
                .allMatch(BankAccount::isActiveAndVerified);
    }
    
    @Then("搜索结果中的所有账户持有人姓名都包含 {string}")
    public void allAccountsInSearchResultsShouldHaveHolderNameContaining(String holderName) {
        assertThat(searchResults)
                .allMatch(account -> account.getAccountHolderName().toLowerCase().contains(holderName.toLowerCase()));
    }
    
    @Then("操作应该成功")
    public void operationShouldBeSuccessful() {
        assertThat(operationResult).isTrue();
    }
    
    @Then("操作应该失败")
    public void operationShouldFail() {
        assertThat(operationResult).isFalse();
    }
    
    @Then("账户 {string} 的余额应该是 {string}")
    public void accountBalanceShouldBe(String accountNumber, String expectedBalance) {
        Optional<BankAccount> account = accountService.getAccountByNumber(accountNumber);
        assertThat(account).isPresent();
        assertThat(account.get().getBalance()).isEqualTo(new BigDecimal(expectedBalance));
    }
    
    @Then("账户 {string} 应该是 {accountStatus}")
    public void accountShouldHaveStatus(String accountNumber, BankAccountTransformer.AccountStatus status) {
        Optional<BankAccount> account = accountService.getAccountByNumber(accountNumber);
        assertThat(account).isPresent();
        assertThat(status.matches(account.get())).isTrue();
    }
    
    @Then("当前账户的持有人应该是 {string}")
    public void currentAccountHolderShouldBe(String expectedHolderName) {
        assertThat(currentAccount).isNotNull();
        assertThat(currentAccount.getAccountHolderName()).isEqualTo(expectedHolderName);
    }
    
    @Then("当前账户的余额应该是 {string}")
    public void currentAccountBalanceShouldBe(String expectedBalance) {
        assertThat(currentAccount).isNotNull();
        assertThat(currentAccount.getBalance()).isEqualTo(new BigDecimal(expectedBalance));
    }
    
    @Then("当前账户应该是 {accountType} 类型")
    public void currentAccountShouldBeOfType(BankAccount.AccountType accountType) {
        assertThat(currentAccount).isNotNull();
        assertThat(currentAccount.isOfType(accountType)).isTrue();
    }
    
    @And("搜索结果应包含账户 {bankAccount}")
    public void searchResultsShouldContainAccount(BankAccount account) {
        assertThat(searchResults)
                .anyMatch(a -> a.getAccountNumber().equals(account.getAccountNumber()) && 
                             a.getAccountHolderName().equals(account.getAccountHolderName()));
    }
}