# 第7章：测试驱动开发(TDD)实践

## 7.1 TDD基础概念

### 7.1.1 什么是TDD

测试驱动开发(Test-Driven Development, TDD)是一种软件开发方法论，其核心思想是在编写功能代码之前先编写测试代码。TDD遵循一个简单的循环，通常称为"红-绿-重构"循环：

```
TDD循环：
┌─────────────┐    ┌─────────────┐    ┌────────────────┐
│    红灯     │ -> │    绿灯     │ -> │     重构      │
│ (编写测试)   │    │ (实现功能)   │    │ (优化代码)     │
│ 测试失败     │    │ 测试通过     │    │ 保持测试通过   │
└─────────────┘    └─────────────┘    └────────────────┘
```

### 7.1.2 TDD的优势

TDD不仅仅是测试技术，更是一种设计方法，具有以下优势：

1. **设计驱动**：迫使开发者思考API设计
2. **即时反馈**：快速验证实现是否正确
3. **文档作用**：测试用例作为功能文档
4. **重构保护**：安全地进行代码重构
5. **质量保证**：提高代码质量和覆盖率

```java
// 传统开发方式 vs TDD方式对比

// 传统方式：先写实现，后写测试
public class CalculatorTraditional {
    public int add(int a, int b) {
        return a + b;
    }
    
    public int subtract(int a, int b) {
        return a - b;
    }
}

// 然后写测试
class CalculatorTraditionalTest {
    @Test
    public void testAdd() {
        Calculator calc = new CalculatorTraditional();
        assertEquals(3, calc.add(1, 2));
    }
}

// TDD方式：先写测试，后写实现
class CalculatorTDDTest {
    @Test
    public void testAdd() {  // 红灯：编写测试，此时还没有实现
        Calculator calc = new CalculatorTDD();
        assertEquals(3, calc.add(1, 2));  // 会编译错误或测试失败
    }
    
    @Test
    public void testSubtract() {
        Calculator calc = new CalculatorTDD();
        assertEquals(-1, calc.subtract(1, 2));
    }
}

// 然后实现功能，让测试通过（绿灯）
public class CalculatorTDD {
    public int add(int a, int b) {
        return a + b;  // 最简单的实现让测试通过
    }
    
    public int subtract(int a, int b) {
        return a - b;  // 最简单的实现让测试通过
    }
}
```

## 7.2 TDD红-绿-重构循环

### 7.2.1 红灯阶段：编写失败的测试

在红灯阶段，我们编写一个小的、具体的测试用例，用于验证我们想要实现的功能。这个测试应该失败，因为我们还没有实现相应的功能。

```java
// 场景：实现一个字符串工具类，包含计算字符串中元音数量的功能

// 红灯1：编写最基本的测试
class StringVowelCounterTest {
    @Test
    public void testEmptyStringHasZeroVowels() {
        // 红灯：编写测试，此时StringVowelCounter还不存在
        StringVowelCounter counter = new StringVowelCounter();
        assertEquals(0, counter.countVowels(""));
    }
}

// 红灯2：添加更多测试用例
@Test
public void testSingleCharacterString() {
    StringVowelCounter counter = new StringVowelCounter();
    assertEquals(1, counter.countVowels("a"));  // 一个元音
    assertEquals(0, counter.countVowels("b"));  // 非元音
}

// 红灯3：测试更复杂的情况
@Test
public void testMultipleVowels() {
    StringVowelCounter counter = new StringVowelCounter();
    assertEquals(2, counter.countVowels("ae"));  // 两个元音
    assertEquals(3, counter.countVowels("hello")); // h e l l o
}

// 红灯4：测试边界情况
@Test
public void testNullString() {
    StringVowelCounter counter = new StringVowelCounter();
    assertThrows(IllegalArgumentException.class, 
        () -> counter.countVowels(null));
}

@Test
public void testCaseInsensitivity() {
    StringVowelCounter counter = new StringVowelCounter();
    assertEquals(2, counter.countVowels("AE"));  // 大写元音
    assertEquals(5, counter.countVowels("HeLLo")); // 混合大小写
}
```

### 7.2.2 绿灯阶段：使测试通过

在绿灯阶段，我们编写最简单的代码实现，使测试通过。重点是让测试通过，而不是编写完美的代码。

```java
// 绿灯1：最简单的实现让第一个测试通过
public class StringVowelCounter {
    public int countVowels(String input) {
        // 最简单的实现让空字符串测试通过
        if (input.isEmpty()) {
            return 0;
        }
        // 其他情况暂时抛出异常，让其他测试失败
        throw new UnsupportedOperationException("Not implemented yet");
    }
}

// 绿灯2：扩展实现，让更多测试通过
public class StringVowelCounter {
    public int countVowels(String input) {
        if (input == null) {
            throw new IllegalArgumentException("Input cannot be null");
        }
        
        if (input.isEmpty()) {
            return 0;
        }
        
        // 简单实现：硬编码处理特定情况
        if (input.equals("a")) return 1;
        if (input.equals("b")) return 0;
        if (input.equals("ae")) return 2;
        if (input.equals("hello")) return 2;  // e和o
        if (input.equals("AE")) return 2;
        if (input.equals("HeLLo")) return 2;
        
        // 默认情况
        return 0;
    }
}

// 绿灯3：更通用的实现
public class StringVowelCounter {
    private static final Set<Character> VOWELS = 
        new HashSet<>(Arrays.asList('a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U'));
    
    public int countVowels(String input) {
        if (input == null) {
            throw new IllegalArgumentException("Input cannot be null");
        }
        
        int count = 0;
        for (char c : input.toCharArray()) {
            if (VOWELS.contains(c)) {
                count++;
            }
        }
        return count;
    }
}
```

### 7.2.3 重构阶段：优化代码

在重构阶段，我们改进代码的结构和性能，同时确保所有测试仍然通过。

```java
// 重构1：优化代码结构，添加辅助方法
public class StringVowelCounter {
    private static final Set<Character> VOWELS = 
        new HashSet<>(Arrays.asList('a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U'));
    
    public int countVowels(String input) {
        validateInput(input);
        return countVowelsInString(input);
    }
    
    private void validateInput(String input) {
        if (input == null) {
            throw new IllegalArgumentException("Input cannot be null");
        }
    }
    
    private int countVowelsInString(String input) {
        return (int) input.chars()
            .filter(c -> VOWELS.contains((char) c))
            .count();
    }
}

// 重构2：提取常量，提高可读性
public class StringVowelCounter {
    private static final String VOWEL_CHARS = "aeiouAEIOU";
    private static final String NULL_INPUT_ERROR = "Input cannot be null";
    
    public int countVowels(String input) {
        validateInput(input);
        return countVowelsInString(input);
    }
    
    private void validateInput(String input) {
        if (input == null) {
            throw new IllegalArgumentException(NULL_INPUT_ERROR);
        }
    }
    
    private int countVowelsInString(String input) {
        return (int) input.chars()
            .filter(this::isVowel)
            .count();
    }
    
    private boolean isVowel(int charCode) {
        return VOWEL_CHARS.indexOf(charCode) >= 0;
    }
}

// 重构3：添加更多功能，支持不同语言
public class StringVowelCounter {
    private static final Map<String, Set<Character>> LANGUAGE_VOWELS = new HashMap<>();
    
    static {
        LANGUAGE_VOWELS.put("en", new HashSet<>(Arrays.asList('a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U')));
        LANGUAGE_VOWELS.put("es", new HashSet<>(Arrays.asList('a', 'e', 'i', 'o', 'u', 'á', 'é', 'í', 'ó', 'ú', 'ü', 'A', 'E', 'I', 'O', 'U', 'Á', 'É', 'Í', 'Ó', 'Ú', 'Ü')));
    }
    
    private final Set<Character> vowels;
    
    public StringVowelCounter() {
        this("en");  // 默认英语
    }
    
    public StringVowelCounter(String language) {
        this.vowels = LANGUAGE_VOWELS.getOrDefault(language, LANGUAGE_VOWELS.get("en"));
    }
    
    public int countVowels(String input) {
        validateInput(input);
        return countVowelsInString(input);
    }
    
    private void validateInput(String input) {
        if (input == null) {
            throw new IllegalArgumentException("Input cannot be null");
        }
    }
    
    private int countVowelsInString(String input) {
        return (int) input.chars()
            .filter(c -> vowels.contains((char) c))
            .count();
    }
}
```

## 7.3 TDD实战案例

### 7.3.1 案例1：实现购物车

让我们通过一个购物车案例来实践TDD：

```java
// 步骤1：红灯 - 编写第一个测试
class ShoppingCartTest {
    @Test
    public void testEmptyCartHasZeroItems() {
        ShoppingCart cart = new ShoppingCart();
        assertEquals(0, cart.getItemCount());
        assertEquals(0.0, cart.getTotalPrice(), 0.001);
    }
    
    @Test
    public void testAddSingleItem() {
        ShoppingCart cart = new ShoppingCart();
        Product product = new Product("Book", 10.0);
        cart.addItem(product, 1);
        
        assertEquals(1, cart.getItemCount());
        assertEquals(10.0, cart.getTotalPrice(), 0.001);
    }
    
    @Test
    public void testAddMultipleItems() {
        ShoppingCart cart = new ShoppingCart();
        Product book = new Product("Book", 10.0);
        Product pen = new Product("Pen", 2.0);
        
        cart.addItem(book, 2);
        cart.addItem(pen, 3);
        
        assertEquals(5, cart.getItemCount());
        assertEquals(26.0, cart.getTotalPrice(), 0.001);
    }
    
    @Test
    public void testRemoveItem() {
        ShoppingCart cart = new ShoppingCart();
        Product product = new Product("Book", 10.0);
        cart.addItem(product, 2);
        
        cart.removeItem(product, 1);
        
        assertEquals(1, cart.getItemCount());
        assertEquals(10.0, cart.getTotalPrice(), 0.001);
    }
    
    @Test
    public void testRemoveAllItems() {
        ShoppingCart cart = new ShoppingCart();
        Product product = new Product("Book", 10.0);
        cart.addItem(product, 2);
        
        cart.removeItem(product, 2);
        
        assertEquals(0, cart.getItemCount());
        assertEquals(0.0, cart.getTotalPrice(), 0.001);
    }
    
    @Test
    public void testRemoveNonExistentItemThrowsException() {
        ShoppingCart cart = new ShoppingCart();
        Product product = new Product("Book", 10.0);
        
        assertThrows(IllegalArgumentException.class, () -> {
            cart.removeItem(product, 1);
        });
    }
    
    @Test
    public void testClearCart() {
        ShoppingCart cart = new ShoppingCart();
        Product product = new Product("Book", 10.0);
        cart.addItem(product, 2);
        
        cart.clear();
        
        assertEquals(0, cart.getItemCount());
        assertEquals(0.0, cart.getTotalPrice(), 0.001);
    }
    
    @Test
    public void testApplyDiscount() {
        ShoppingCart cart = new ShoppingCart();
        Product product = new Product("Book", 10.0);
        cart.addItem(product, 2);
        
        cart.applyDiscount(0.1);  // 10% discount
        
        assertEquals(18.0, cart.getTotalPrice(), 0.001);  // 20 - 2
    }
}

// 步骤2：绿灯 - 实现最基本的购物车
public class ShoppingCart {
    private List<CartItem> items = new ArrayList<>();
    
    public int getItemCount() {
        return items.stream().mapToInt(CartItem::getQuantity).sum();
    }
    
    public double getTotalPrice() {
        return items.stream()
            .mapToDouble(item -> item.getProduct().getPrice() * item.getQuantity())
            .sum();
    }
    
    public void addItem(Product product, int quantity) {
        // 查找是否已存在该商品
        Optional<CartItem> existingItem = items.stream()
            .filter(item -> item.getProduct().equals(product))
            .findFirst();
            
        if (existingItem.isPresent()) {
            // 如果已存在，增加数量
            CartItem item = existingItem.get();
            item.setQuantity(item.getQuantity() + quantity);
        } else {
            // 如果不存在，添加新商品
            items.add(new CartItem(product, quantity));
        }
    }
    
    public void removeItem(Product product, int quantity) {
        // 查找商品
        Optional<CartItem> existingItem = items.stream()
            .filter(item -> item.getProduct().equals(product))
            .findFirst();
            
        if (!existingItem.isPresent()) {
            throw new IllegalArgumentException("商品不在购物车中");
        }
        
        CartItem item = existingItem.get();
        int newQuantity = item.getQuantity() - quantity;
        
        if (newQuantity > 0) {
            item.setQuantity(newQuantity);
        } else {
            items.remove(item);
        }
    }
    
    public void clear() {
        items.clear();
    }
    
    public void applyDiscount(double discountRate) {
        if (discountRate < 0 || discountRate > 1) {
            throw new IllegalArgumentException("折扣率必须在0到1之间");
        }
        
        // 应用折扣（简化实现，不修改原价）
        // 在实际应用中，可能需要更复杂的折扣逻辑
    }
}

// 辅助类
class Product {
    private String name;
    private double price;
    
    public Product(String name, double price) {
        this.name = name;
        this.price = price;
    }
    
    public String getName() { return name; }
    public double getPrice() { return price; }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Product product = (Product) o;
        return Double.compare(product.price, price) == 0 && 
               Objects.equals(name, product.name);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(name, price);
    }
}

class CartItem {
    private Product product;
    private int quantity;
    
    public CartItem(Product product, int quantity) {
        this.product = product;
        this.quantity = quantity;
    }
    
    public Product getProduct() { return product; }
    public int getQuantity() { return quantity; }
    public void setQuantity(int quantity) { this.quantity = quantity; }
}
```

### 7.3.2 案例2：实现简单的银行账户

让我们通过银行账户案例进一步实践TDD：

```java
// 红灯：编写银行账户测试
class BankAccountTest {
    @Test
    public void testNewAccountHasZeroBalance() {
        BankAccount account = new BankAccount("John Doe");
        assertEquals("John Doe", account.getAccountHolder());
        assertEquals(0.0, account.getBalance(), 0.001);
    }
    
    @Test
    public void testDepositIncreasesBalance() {
        BankAccount account = new BankAccount("Jane Smith");
        account.deposit(100.0);
        assertEquals(100.0, account.getBalance(), 0.001);
        
        account.deposit(50.0);
        assertEquals(150.0, account.getBalance(), 0.001);
    }
    
    @Test
    public void testWithdrawDecreasesBalance() {
        BankAccount account = new BankAccount("Bob Johnson");
        account.deposit(200.0);
        account.withdraw(50.0);
        assertEquals(150.0, account.getBalance(), 0.001);
    }
    
    @Test
    public void testWithdrawMoreThanBalanceThrowsException() {
        BankAccount account = new BankAccount("Alice Brown");
        account.deposit(100.0);
        
        assertThrows(IllegalArgumentException.class, () -> {
            account.withdraw(150.0);
        });
        assertEquals(100.0, account.getBalance(), 0.001);  // 余额不变
    }
    
    @Test
    public void testNegativeDepositThrowsException() {
        BankAccount account = new BankAccount("Charlie Davis");
        assertThrows(IllegalArgumentException.class, () -> {
            account.deposit(-50.0);
        });
        assertEquals(0.0, account.getBalance(), 0.001);
    }
    
    @Test
    public void testNegativeWithdrawThrowsException() {
        BankAccount account = new BankAccount("Diana Evans");
        assertThrows(IllegalArgumentException.class, () -> {
            account.withdraw(-50.0);
        });
    }
    
    @Test
    public void testTransferBetweenAccounts() {
        BankAccount source = new BankAccount("Eve Frank");
        BankAccount target = new BankAccount("Frank Grace");
        
        source.deposit(200.0);
        target.deposit(50.0);
        
        source.transfer(100.0, target);
        
        assertEquals(100.0, source.getBalance(), 0.001);
        assertEquals(150.0, target.getBalance(), 0.001);
    }
    
    @Test
    public void testTransferMoreThanBalanceThrowsException() {
        BankAccount source = new BankAccount("George Harris");
        BankAccount target = new BankAccount("Henry Ivy");
        
        source.deposit(50.0);
        
        assertThrows(IllegalArgumentException.class, () -> {
            source.transfer(100.0, target);
        });
        assertEquals(50.0, source.getBalance(), 0.001);
        assertEquals(0.0, target.getBalance(), 0.001);
    }
    
    @Test
    public void testTransactionHistory() {
        BankAccount account = new BankAccount("Ian Johnson");
        
        account.deposit(100.0);
        account.withdraw(20.0);
        account.deposit(50.0);
        
        List<Transaction> history = account.getTransactionHistory();
        assertEquals(3, history.size());
        
        assertEquals(100.0, history.get(0).getAmount(), 0.001);
        assertEquals(TransactionType.DEPOSIT, history.get(0).getType());
        
        assertEquals(-20.0, history.get(1).getAmount(), 0.001);
        assertEquals(TransactionType.WITHDRAWAL, history.get(1).getType());
        
        assertEquals(50.0, history.get(2).getAmount(), 0.001);
        assertEquals(TransactionType.DEPOSIT, history.get(2).getType());
    }
}

// 绿灯：实现银行账户
public class BankAccount {
    private String accountHolder;
    private double balance;
    private List<Transaction> transactionHistory = new ArrayList<>();
    
    public BankAccount(String accountHolder) {
        this.accountHolder = accountHolder;
        this.balance = 0.0;
    }
    
    public String getAccountHolder() {
        return accountHolder;
    }
    
    public double getBalance() {
        return balance;
    }
    
    public void deposit(double amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("存款金额必须为正数");
        }
        
        balance += amount;
        transactionHistory.add(new Transaction(amount, TransactionType.DEPOSIT));
    }
    
    public void withdraw(double amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("取款金额必须为正数");
        }
        
        if (amount > balance) {
            throw new IllegalArgumentException("余额不足");
        }
        
        balance -= amount;
        transactionHistory.add(new Transaction(-amount, TransactionType.WITHDRAWAL));
    }
    
    public void transfer(double amount, BankAccount targetAccount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("转账金额必须为正数");
        }
        
        if (amount > balance) {
            throw new IllegalArgumentException("余额不足");
        }
        
        withdraw(amount);
        targetAccount.deposit(amount);
        transactionHistory.add(new Transaction(-amount, TransactionType.TRANSFER));
    }
    
    public List<Transaction> getTransactionHistory() {
        return new ArrayList<>(transactionHistory);  // 返回副本，保护内部状态
    }
}

// 辅助类
enum TransactionType {
    DEPOSIT, WITHDRAWAL, TRANSFER
}

class Transaction {
    private final double amount;
    private final TransactionType type;
    private final LocalDateTime timestamp;
    
    public Transaction(double amount, TransactionType type) {
        this.amount = amount;
        this.type = type;
        this.timestamp = LocalDateTime.now();
    }
    
    public double getAmount() { return amount; }
    public TransactionType getType() { return type; }
    public LocalDateTime getTimestamp() { return timestamp; }
}
```

## 7.4 TDD重构技巧

### 7.4.1 识别代码异味

通过TDD开发过程中，我们需要关注代码异味并及时重构：

```java
// 重构前：包含代码异味的实现
public class BankAccount {
    private String accountHolder;
    private double balance;
    private List<Transaction> transactionHistory = new ArrayList<>();
    
    // 长方法：包含太多逻辑
    public void processTransaction(TransactionRequest request) {
        if (request.getAmount() <= 0) {
            throw new IllegalArgumentException("金额必须为正数");
        }
        
        if (request.getType() == TransactionType.DEPOSIT) {
            if (request.getAmount() > 10000) {
                // 大额存款需要特殊处理
                balance += request.getAmount();
                transactionHistory.add(new Transaction(request.getAmount(), TransactionType.DEPOSIT));
                // 发送通知
                NotificationService.sendNotification(accountHolder, "大额存款通知");
            } else {
                balance += request.getAmount();
                transactionHistory.add(new Transaction(request.getAmount(), TransactionType.DEPOSIT));
            }
        } else if (request.getType() == TransactionType.WITHDRAWAL) {
            if (request.getAmount() > balance) {
                throw new IllegalArgumentException("余额不足");
            }
            
            if (request.getAmount() > 5000) {
                // 大额取款需要特殊处理
                balance -= request.getAmount();
                transactionHistory.add(new Transaction(-request.getAmount(), TransactionType.WITHDRAWAL));
                // 发送通知
                NotificationService.sendNotification(accountHolder, "大额取款通知");
            } else {
                balance -= request.getAmount();
                transactionHistory.add(new Transaction(-request.getAmount(), TransactionType.WITHDRAWAL));
            }
        } else {
            throw new IllegalArgumentException("不支持的交易类型");
        }
    }
}

// 重构后：消除代码异味
public class BankAccount {
    private String accountHolder;
    private double balance;
    private List<Transaction> transactionHistory = new ArrayList<>();
    private final TransactionProcessor transactionProcessor;
    private final NotificationService notificationService;
    
    public BankAccount(String accountHolder) {
        this(accountHolder, new StandardTransactionProcessor(), new EmailNotificationService());
    }
    
    // 依赖注入，提高可测试性
    public BankAccount(String accountHolder, TransactionProcessor processor, NotificationService notification) {
        this.accountHolder = accountHolder;
        this.balance = 0.0;
        this.transactionProcessor = processor;
        this.notificationService = notification;
    }
    
    // 提取方法，单一职责
    public void processTransaction(TransactionRequest request) {
        validateTransaction(request);
        executeTransaction(request);
        recordTransaction(request);
        sendNotificationIfNecessary(request);
    }
    
    private void validateTransaction(TransactionRequest request) {
        transactionProcessor.validate(request, balance);
    }
    
    private void executeTransaction(TransactionRequest request) {
        balance = transactionProcessor.process(request, balance);
    }
    
    private void recordTransaction(TransactionRequest request) {
        Transaction transaction = transactionProcessor.createTransaction(request);
        transactionHistory.add(transaction);
    }
    
    private void sendNotificationIfNecessary(TransactionRequest request) {
        if (shouldSendNotification(request)) {
            String message = createNotificationMessage(request);
            notificationService.sendNotification(accountHolder, message);
        }
    }
    
    private boolean shouldSendNotification(TransactionRequest request) {
        return Math.abs(request.getAmount()) > 5000;
    }
    
    private String createNotificationMessage(TransactionRequest request) {
        String type = request.getType() == TransactionType.DEPOSIT ? "存款" : "取款";
        return String.format("大额%s通知：金额 %.2f", type, Math.abs(request.getAmount()));
    }
}

// 策略模式：处理不同类型的交易
interface TransactionProcessor {
    void validate(TransactionRequest request, double currentBalance);
    double process(TransactionRequest request, double currentBalance);
    Transaction createTransaction(TransactionRequest request);
}

class StandardTransactionProcessor implements TransactionProcessor {
    @Override
    public void validate(TransactionRequest request, double currentBalance) {
        if (request.getAmount() <= 0) {
            throw new IllegalArgumentException("金额必须为正数");
        }
        
        if (request.getType() == TransactionType.WITHDRAWAL && 
            request.getAmount() > currentBalance) {
            throw new IllegalArgumentException("余额不足");
        }
    }
    
    @Override
    public double process(TransactionRequest request, double currentBalance) {
        if (request.getType() == TransactionType.DEPOSIT) {
            return currentBalance + request.getAmount();
        } else if (request.getType() == TransactionType.WITHDRAWAL) {
            return currentBalance - request.getAmount();
        } else {
            throw new IllegalArgumentException("不支持的交易类型");
        }
    }
    
    @Override
    public Transaction createTransaction(TransactionRequest request) {
        double amount = request.getType() == TransactionType.DEPOSIT ? 
            request.getAmount() : -request.getAmount();
        return new Transaction(amount, request.getType());
    }
}
```

### 7.4.2 测试驱动重构

使用测试保护重构过程，确保重构不会破坏功能：

```java
// 重构前：实现简单但不够灵活
public class StringProcessor {
    public String process(String input) {
        if (input == null) {
            return "";
        }
        
        // 移除所有空格
        String noSpaces = input.replaceAll("\\s+", "");
        
        // 转换为大写
        String uppercase = noSpaces.toUpperCase();
        
        // 添加前缀和后缀
        return "PROCESSED_" + uppercase + "_END";
    }
}

// 测试用例
class StringProcessorTest {
    @Test
    public void testNullInputReturnsEmptyString() {
        StringProcessor processor = new StringProcessor();
        assertEquals("", processor.process(null));
    }
    
    @Test
    public void testEmptyString() {
        StringProcessor processor = new StringProcessor();
        assertEquals("PROCESSED_END", processor.process(""));
    }
    
    @Test
    public void testSingleWord() {
        StringProcessor processor = new StringProcessor();
        assertEquals("PROCESSED_HELLO_END", processor.process("hello"));
    }
    
    @Test
    public void testMultipleWords() {
        StringProcessor processor = new StringProcessor();
        assertEquals("PROCESSED_Helloworld_END", processor.process("hello world"));
    }
    
    @Test
    public void testMixedCaseAndSpaces() {
        StringProcessor processor = new StringProcessor();
        assertEquals("PROCESSED_JAVATESTING_END", processor.process("Java Testing"));
    }
}

// 重构后：更灵活、可扩展的实现
public class StringProcessor {
    private final String prefix;
    private final String suffix;
    private final TextTransformer transformer;
    
    // 默认构造函数
    public StringProcessor() {
        this("PROCESSED_", "_END", new DefaultTextTransformer());
    }
    
    // 灵活的构造函数，支持依赖注入
    public StringProcessor(String prefix, String suffix, TextTransformer transformer) {
        this.prefix = prefix;
        this.suffix = suffix;
        this.transformer = transformer;
    }
    
    public String process(String input) {
        String normalizedInput = normalizeInput(input);
        String transformedInput = transformer.transform(normalizedInput);
        return addPrefixAndSuffix(transformedInput);
    }
    
    private String normalizeInput(String input) {
        return input == null ? "" : input;
    }
    
    private String addPrefixAndSuffix(String input) {
        return prefix + input + suffix;
    }
}

// 策略接口：文本转换
interface TextTransformer {
    String transform(String input);
}

// 默认实现：移除空格并转为大写
class DefaultTextTransformer implements TextTransformer {
    @Override
    public String transform(String input) {
        String noSpaces = input.replaceAll("\\s+", "");
        return noSpaces.toUpperCase();
    }
}

// 其他实现：支持不同的转换策略
class LowerCaseTransformer implements TextTransformer {
    @Override
    public String transform(String input) {
        String noSpaces = input.replaceAll("\\s+", "");
        return noSpaces.toLowerCase();
    }
}

class PreserveSpacesTransformer implements TextTransformer {
    @Override
    public String transform(String input) {
        return input.toUpperCase();  // 不移除空格
    }
}

// 重构后的测试：验证重构后的行为一致
class StringProcessorRefactoredTest {
    @Test
    public void testDefaultProcessorBehavior() {
        StringProcessor processor = new StringProcessor();
        
        assertEquals("", processor.process(null));
        assertEquals("PROCESSED_END", processor.process(""));
        assertEquals("PROCESSED_HELLO_END", processor.process("hello"));
        assertEquals("PROCESSED_Helloworld_END", processor.process("hello world"));
        assertEquals("PROCESSED_JAVATESTING_END", processor.process("Java Testing"));
    }
    
    @Test
    public void testCustomProcessorBehavior() {
        TextTransformer lowerCaseTransformer = new LowerCaseTransformer();
        StringProcessor processor = new StringProcessor("START_", "_FINISH", lowerCaseTransformer);
        
        assertEquals("START_hello_FINISH", processor.process("HELLO"));
        assertEquals("START_helloworld_FINISH", processor.process("Hello World"));
    }
    
    @Test
    public void testPreserveSpacesProcessorBehavior() {
        TextTransformer preserveTransformer = new PreserveSpacesTransformer();
        StringProcessor processor = new StringProcessor("", "", preserveTransformer);
        
        assertEquals("HELLO WORLD", processor.process("Hello World"));
        assertEquals("JAVA TESTING", processor.process("Java Testing"));
    }
}
```

## 7.5 TDD高级技巧

### 7.5.1 测试替身在TDD中的应用

在TDD中，测试替身可以帮助我们专注于当前要开发的功能，而不被依赖所阻碍：

```java
// 场景：实现订单服务，依赖库存服务和支付服务

// 红灯：编写订单服务测试
class OrderServiceTest {
    @Mock
    private InventoryService inventoryService;
    
    @Mock
    private PaymentService paymentService;
    
    @InjectMocks
    private OrderService orderService;
    
    @Test
    public void testSuccessfulOrder() {
        // 设置测试数据
        Product product = new Product("Laptop", 999.99);
        OrderRequest request = new OrderRequest(product, 1, "customer@example.com");
        
        // 配置Mock行为
        when(inventoryService.checkAvailability(product, 1))
            .thenReturn(true);
        when(inventoryService.reserve(product, 1))
            .thenReturn(new Reservation("RES123", product, 1));
        when(paymentService.processPayment(any(PaymentRequest.class)))
            .thenReturn(new PaymentResult("PAY456", true, "Payment successful"));
        
        // 执行操作
        OrderResult result = orderService.placeOrder(request);
        
        // 验证结果
        assertTrue(result.isSuccess());
        assertNotNull(result.getOrderId());
        assertEquals("RES123", result.getReservationId());
        assertEquals("PAY456", result.getPaymentId());
        
        // 验证交互
        verify(inventoryService).checkAvailability(product, 1);
        verify(inventoryService).reserve(product, 1);
        verify(paymentService).processPayment(any(PaymentRequest.class));
    }
    
    @Test
    public void testOrderFailsWhenProductNotAvailable() {
        Product product = new Product("Smartphone", 699.99);
        OrderRequest request = new OrderRequest(product, 1, "customer@example.com");
        
        when(inventoryService.checkAvailability(product, 1))
            .thenReturn(false);
        
        OrderResult result = orderService.placeOrder(request);
        
        assertFalse(result.isSuccess());
        assertEquals("Product not available", result.getErrorMessage());
        
        verify(inventoryService).checkAvailability(product, 1);
        verify(inventoryService, never()).reserve(any(Product.class), anyInt());
        verify(paymentService, never()).processPayment(any(PaymentRequest.class));
    }
    
    @Test
    public void testOrderFailsWhenPaymentDeclined() {
        Product product = new Product("Tablet", 299.99);
        OrderRequest request = new OrderRequest(product, 1, "customer@example.com");
        
        when(inventoryService.checkAvailability(product, 1))
            .thenReturn(true);
        when(inventoryService.reserve(product, 1))
            .thenReturn(new Reservation("RES789", product, 1));
        when(paymentService.processPayment(any(PaymentRequest.class)))
            .thenReturn(new PaymentResult("PAY123", false, "Payment declined"));
        
        OrderResult result = orderService.placeOrder(request);
        
        assertFalse(result.isSuccess());
        assertEquals("Payment declined", result.getErrorMessage());
        
        verify(inventoryService).checkAvailability(product, 1);
        verify(inventoryService).reserve(product, 1);
        verify(inventoryService).releaseReservation("RES789");
        verify(paymentService).processPayment(any(PaymentRequest.class));
    }
}

// 绿灯：实现订单服务
public class OrderService {
    private final InventoryService inventoryService;
    private final PaymentService paymentService;
    private final OrderIdGenerator orderIdGenerator;
    
    public OrderService(InventoryService inventoryService, 
                        PaymentService paymentService,
                        OrderIdGenerator orderIdGenerator) {
        this.inventoryService = inventoryService;
        this.paymentService = paymentService;
        this.orderIdGenerator = orderIdGenerator;
    }
    
    public OrderResult placeOrder(OrderRequest request) {
        // 检查产品可用性
        if (!inventoryService.checkAvailability(request.getProduct(), request.getQuantity())) {
            return OrderResult.failure("Product not available");
        }
        
        // 预留库存
        Reservation reservation = inventoryService.reserve(
            request.getProduct(), request.getQuantity());
        
        // 处理支付
        PaymentRequest paymentRequest = new PaymentRequest(
            request.getProduct().getPrice() * request.getQuantity(),
            request.getCustomerEmail()
        );
        
        PaymentResult paymentResult = paymentService.processPayment(paymentRequest);
        
        if (paymentResult.isSuccessful()) {
            // 支付成功，完成订单
            String orderId = orderIdGenerator.generate();
            return OrderResult.success(orderId, reservation.getId(), paymentResult.getId());
        } else {
            // 支付失败，释放预留库存
            inventoryService.releaseReservation(reservation.getId());
            return OrderResult.failure(paymentResult.getMessage());
        }
    }
}

// 辅助类和接口
interface InventoryService {
    boolean checkAvailability(Product product, int quantity);
    Reservation reserve(Product product, int quantity);
    void releaseReservation(String reservationId);
}

interface PaymentService {
    PaymentResult processPayment(PaymentRequest request);
}

interface OrderIdGenerator {
    String generate();
}

class Product {
    private String name;
    private double price;
    
    public Product(String name, double price) {
        this.name = name;
        this.price = price;
    }
    
    public String getName() { return name; }
    public double getPrice() { return price; }
}

class OrderRequest {
    private Product product;
    private int quantity;
    private String customerEmail;
    
    public OrderRequest(Product product, int quantity, String customerEmail) {
        this.product = product;
        this.quantity = quantity;
        this.customerEmail = customerEmail;
    }
    
    public Product getProduct() { return product; }
    public int getQuantity() { return quantity; }
    public String getCustomerEmail() { return customerEmail; }
}

class OrderResult {
    private boolean success;
    private String orderId;
    private String reservationId;
    private String paymentId;
    private String errorMessage;
    
    // 静态工厂方法
    public static OrderResult success(String orderId, String reservationId, String paymentId) {
        OrderResult result = new OrderResult();
        result.success = true;
        result.orderId = orderId;
        result.reservationId = reservationId;
        result.paymentId = paymentId;
        return result;
    }
    
    public static OrderResult failure(String errorMessage) {
        OrderResult result = new OrderResult();
        result.success = false;
        result.errorMessage = errorMessage;
        return result;
    }
    
    // Getters
    public boolean isSuccess() { return success; }
    public String getOrderId() { return orderId; }
    public String getReservationId() { return reservationId; }
    public String getPaymentId() { return paymentId; }
    public String getErrorMessage() { return errorMessage; }
}

class Reservation {
    private String id;
    private Product product;
    private int quantity;
    
    public Reservation(String id, Product product, int quantity) {
        this.id = id;
        this.product = product;
        this.quantity = quantity;
    }
    
    public String getId() { return id; }
    public Product getProduct() { return product; }
    public int getQuantity() { return quantity; }
}

class PaymentRequest {
    private double amount;
    private String customerEmail;
    
    public PaymentRequest(double amount, String customerEmail) {
        this.amount = amount;
        this.customerEmail = customerEmail;
    }
    
    public double getAmount() { return amount; }
    public String getCustomerEmail() { return customerEmail; }
}

class PaymentResult {
    private String id;
    private boolean successful;
    private String message;
    
    public PaymentResult(String id, boolean successful, String message) {
        this.id = id;
        this.successful = successful;
        this.message = message;
    }
    
    public String getId() { return id; }
    public boolean isSuccessful() { return successful; }
    public String getMessage() { return message; }
}
```

### 7.5.2 测试金字塔和TDD

在TDD实践中，应该遵循测试金字塔原则，更多地编写单元测试而非集成测试：

```java
// 单元测试（金字塔底层）- 快速、独立、大量
class UserRepositoryUnitTest {
    
    @Mock
    private DataSource dataSource;
    
    @Mock
    private Connection connection;
    
    @Mock
    private PreparedStatement statement;
    
    @Mock
    private ResultSet resultSet;
    
    @InjectMocks
    private UserRepository userRepository;
    
    @Test
    public void testFindUserByIdReturnsUserWhenFound() throws SQLException {
        // 设置Mock行为
        when(dataSource.getConnection()).thenReturn(connection);
        when(connection.prepareStatement(anyString())).thenReturn(statement);
        when(statement.executeQuery()).thenReturn(resultSet);
        when(resultSet.next()).thenReturn(true);
        when(resultSet.getLong("id")).thenReturn(123L);
        when(resultSet.getString("name")).thenReturn("John Doe");
        when(resultSet.getString("email")).thenReturn("john@example.com");
        
        // 执行测试
        Optional<User> result = userRepository.findById(123L);
        
        // 验证结果
        assertTrue(result.isPresent());
        User user = result.get();
        assertEquals(123L, user.getId());
        assertEquals("John Doe", user.getName());
        assertEquals("john@example.com", user.getEmail());
        
        // 验证交互
        verify(statement).setLong(1, 123L);
        verify(statement).executeQuery();
    }
}

// 集成测试（金字塔中层）- 测试组件间交互
class UserServiceIntegrationTest {
    
    private static EmbeddedDatabase db;
    
    private UserRepository userRepository;
    private UserService userService;
    
    @BeforeAll
    static void setupDatabase() {
        db = EmbeddedDatabaseBuilder()
            .setType(EmbeddedDatabaseType.H2)
            .addScript("schema.sql")
            .addScript("test-data.sql")
            .build();
    }
    
    @AfterAll
    static void shutdownDatabase() {
        db.shutdown();
    }
    
    @BeforeEach
    void setup() {
        userRepository = new JdbcUserRepository(db);
        userService = new UserService(userRepository);
    }
    
    @Test
    public void testCreateUserAndRetrieve() {
        // 创建新用户
        User newUser = new User(null, "Alice", "alice@example.com");
        User createdUser = userService.createUser(newUser);
        
        // 验证创建结果
        assertNotNull(createdUser.getId());
        assertEquals("Alice", createdUser.getName());
        assertEquals("alice@example.com", createdUser.getEmail());
        
        // 通过ID检索用户
        Optional<User> retrievedUser = userService.getUserById(createdUser.getId());
        assertTrue(retrievedUser.isPresent());
        assertEquals(createdUser, retrievedUser.get());
    }
}

// 端到端测试（金字塔顶层）- 测试完整场景
class UserControllerEndToEndTest {
    
    private static MockMvc mockMvc;
    
    @BeforeAll
    static void setup() {
        // 设置完整的Spring应用上下文
        mockMvc = MockMvcBuilders
            .webAppContextSetup(webApplicationContext)
            .apply(springSecurity())
            .build();
    }
    
    @Test
    void testCreateUserAndRetrieve() throws Exception {
        // 创建用户请求
        String createUserRequest = "{\"name\":\"Bob\",\"email\":\"bob@example.com\"}";
        
        // 发送创建用户请求
        ResultActions createResult = mockMvc.perform(post("/api/users")
            .contentType(MediaType.APPLICATION_JSON)
            .content(createUserRequest));
        
        // 验证创建响应
        createResult
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.id").exists())
            .andExpect(jsonPath("$.name").value("Bob"))
            .andExpect(jsonPath("$.email").value("bob@example.com"));
        
        // 获取创建的用户ID
        String response = createResult.andReturn().getResponse().getContentAsString();
        JsonNode jsonNode = new ObjectMapper().readTree(response);
        Long userId = jsonNode.get("id").asLong();
        
        // 发送获取用户请求
        mockMvc.perform(get("/api/users/" + userId))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.id").value(userId))
            .andExpect(jsonPath("$.name").value("Bob"))
            .andExpect(jsonPath("$.email").value("bob@example.com"));
    }
}
```

## 7.6 TDD与持续集成

### 7.6.1 CI/CD中的TDD实践

TDD在持续集成环境中的关键点：

1. **频繁提交**：每个红-绿-重构循环后提交代码
2. **自动构建**：CI系统自动运行所有测试
3. **快速反馈**：测试失败立即通知开发团队
4. **质量门控**：测试通过是代码合并的前提条件

```yaml
# 示例：GitHub Actions工作流文件
name: Java CI with TDD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up JDK 11
      uses: actions/setup-java@v2
      with:
        java-version: '11'
        distribution: 'adopt'
        
    - name: Cache Maven dependencies
      uses: actions/cache@v2
      with:
        path: ~/.m2
        key: ${{ runner.os }}-m2-${{ hashFiles('**/pom.xml') }}
        restore-keys: ${{ runner.os }}-m2-
        
    - name: Run tests
      run: mvn test
      
    - name: Generate test report
      run: mvn jacoco:report
      
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v2
      with:
        file: ./target/site/jacoco/jacoco.xml
        flags: unittests
        name: codecov-umbrella
```

### 7.6.2 代码质量指标

在TDD实践中，关注以下质量指标：

1. **测试覆盖率**：代码覆盖率应该达到80%以上
2. **代码复杂度**：圈复杂度应保持在较低水平
3. **技术债务**：定期评估和减少技术债务
4. **缺陷密度**：缺陷数量与代码行数的比率

```java
// 示例：使用JaCoCo生成代码覆盖率报告
// 在pom.xml中添加JaCoCo插件
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.7</version>
    <executions>
        <execution>
            <goals>
                <goal>prepare-agent</goal>
            </goals>
        </execution>
        <execution>
            <id>report</id>
            <phase>test</phase>
            <goals>
                <goal>report</goal>
            </goals>
        </execution>
        <execution>
            <id>check</id>
            <goals>
                <goal>check</goal>
            </goals>
            <configuration>
                <rules>
                    <rule>
                        <element>BUNDLE</element>
                        <limits>
                            <limit>
                                <counter>INSTRUCTION</counter>
                                <value>COVEREDRATIO</value>
                                <minimum>0.80</minimum>
                            </limit>
                        </limits>
                    </rule>
                </rules>
            </configuration>
        </execution>
    </executions>
</plugin>
```

## 7.7 小结

本章深入讲解了测试驱动开发(TDD)的实践方法，主要内容包括：

1. **TDD基础概念**：红-绿-重构循环和TDD的优势
2. **TDD实践案例**：购物车和银行账户的完整TDD实现
3. **TDD重构技巧**：识别代码异味和测试驱动重构
4. **TDD高级技巧**：测试替身应用和测试金字塔
5. **TDD与持续集成**：CI/CD中的TDD实践和质量指标

掌握TDD方法论可以大大提高代码质量和开发效率，使开发过程更加可控和可预测。在最后一章中，我们将总结Java单元测试的最佳实践和代码质量保证方法。

## 7.8 实践练习

### 练习1：TDD红-绿-重构实践
1. 选择一个简单的功能（如计算器、字符串处理）
2. 遵循TDD循环：先写失败的测试，再实现功能，最后重构
3. 重复循环，逐步增加功能复杂度

### 练习2：TDD项目实战
1. 选择一个小型项目（如待办事项列表、简单的博客系统）
2. 完全使用TDD方法开发整个项目
3. 记录TDD过程中的挑战和解决方案

### 练习3：TDD重构练习
1. 找到一个现有的非TDD代码库
2. 先编写测试覆盖现有功能（表征测试）
3. 在测试保护下重构代码，改进设计
4. 比较重构前后的代码质量

通过这些练习，您将深入理解TDD方法论，能够在实际项目中应用TDD提高代码质量和开发效率。