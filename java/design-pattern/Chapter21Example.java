import java.util.*;

/**
 * 第二十一章 策略模式示例代码
 */

// ==================== 基本策略模式实现 ====================

// 策略接口
interface Strategy {
    int doOperation(int num1, int num2);
}

// 具体策略 - 加法
class OperationAdd implements Strategy {
    @Override
    public int doOperation(int num1, int num2) {
        return num1 + num2;
    }
}

// 具体策略 - 减法
class OperationSubtract implements Strategy {
    @Override
    public int doOperation(int num1, int num2) {
        return num1 - num2;
    }
}

// 具体策略 - 乘法
class OperationMultiply implements Strategy {
    @Override
    public int doOperation(int num1, int num2) {
        return num1 * num2;
    }
}

// 上下文
class Context {
    private Strategy strategy;
    
    public Context(Strategy strategy) {
        this.strategy = strategy;
    }
    
    public int executeStrategy(int num1, int num2) {
        return strategy.doOperation(num1, num2);
    }
}

// ==================== 支付系统示例 ====================

// 支付策略接口
interface PaymentStrategy {
    void pay(double amount);
}

// 信用卡支付策略
class CreditCardPayment implements PaymentStrategy {
    private String cardNumber;
    private String cardHolderName;
    private String cvv;
    private String expiryDate;
    
    public CreditCardPayment(String cardNumber, String cardHolderName, String cvv, String expiryDate) {
        this.cardNumber = cardNumber;
        this.cardHolderName = cardHolderName;
        this.cvv = cvv;
        this.expiryDate = expiryDate;
    }
    
    @Override
    public void pay(double amount) {
        System.out.println("使用信用卡支付: ¥" + amount);
        System.out.println("卡号: " + cardNumber);
        System.out.println("持卡人: " + cardHolderName);
        // 处理信用卡支付逻辑
    }
}

// 支付宝支付策略
class AlipayPayment implements PaymentStrategy {
    private String alipayAccount;
    
    public AlipayPayment(String alipayAccount) {
        this.alipayAccount = alipayAccount;
    }
    
    @Override
    public void pay(double amount) {
        System.out.println("使用支付宝支付: ¥" + amount);
        System.out.println("账户: " + alipayAccount);
        // 处理支付宝支付逻辑
    }
}

// 微信支付策略
class WechatPayment implements PaymentStrategy {
    private String wechatAccount;
    
    public WechatPayment(String wechatAccount) {
        this.wechatAccount = wechatAccount;
    }
    
    @Override
    public void pay(double amount) {
        System.out.println("使用微信支付: ¥" + amount);
        System.out.println("账户: " + wechatAccount);
        // 处理微信支付逻辑
    }
}

// 支付上下文
class PaymentContext {
    private PaymentStrategy paymentStrategy;
    
    public void setPaymentStrategy(PaymentStrategy paymentStrategy) {
        this.paymentStrategy = paymentStrategy;
    }
    
    public void executePayment(double amount) {
        if (paymentStrategy == null) {
            System.out.println("请先选择支付方式");
            return;
        }
        paymentStrategy.pay(amount);
    }
}

// ==================== 排序算法选择系统 ====================

// 排序策略接口
interface SortStrategy {
    void sort(List<Integer> list);
}

// 冒泡排序策略
class BubbleSortStrategy implements SortStrategy {
    @Override
    public void sort(List<Integer> list) {
        System.out.println("使用冒泡排序算法");
        int n = list.size();
        for (int i = 0; i < n - 1; i++) {
            for (int j = 0; j < n - i - 1; j++) {
                if (list.get(j) > list.get(j + 1)) {
                    // 交换元素
                    Collections.swap(list, j, j + 1);
                }
            }
        }
    }
}

// 快速排序策略
class QuickSortStrategy implements SortStrategy {
    @Override
    public void sort(List<Integer> list) {
        System.out.println("使用快速排序算法");
        quickSort(list, 0, list.size() - 1);
    }
    
    private void quickSort(List<Integer> list, int low, int high) {
        if (low < high) {
            int pi = partition(list, low, high);
            quickSort(list, low, pi - 1);
            quickSort(list, pi + 1, high);
        }
    }
    
    private int partition(List<Integer> list, int low, int high) {
        int pivot = list.get(high);
        int i = (low - 1);
        
        for (int j = low; j < high; j++) {
            if (list.get(j) <= pivot) {
                i++;
                Collections.swap(list, i, j);
            }
        }
        Collections.swap(list, i + 1, high);
        return i + 1;
    }
}

// 归并排序策略
class MergeSortStrategy implements SortStrategy {
    @Override
    public void sort(List<Integer> list) {
        System.out.println("使用归并排序算法");
        mergeSort(list, 0, list.size() - 1);
    }
    
    private void mergeSort(List<Integer> list, int left, int right) {
        if (left < right) {
            int mid = (left + right) / 2;
            mergeSort(list, left, mid);
            mergeSort(list, mid + 1, right);
            merge(list, left, mid, right);
        }
    }
    
    private void merge(List<Integer> list, int left, int mid, int right) {
        List<Integer> leftList = new ArrayList<>(list.subList(left, mid + 1));
        List<Integer> rightList = new ArrayList<>(list.subList(mid + 1, right + 1));
        
        int i = 0, j = 0, k = left;
        
        while (i < leftList.size() && j < rightList.size()) {
            if (leftList.get(i) <= rightList.get(j)) {
                list.set(k++, leftList.get(i++));
            } else {
                list.set(k++, rightList.get(j++));
            }
        }
        
        while (i < leftList.size()) {
            list.set(k++, leftList.get(i++));
        }
        
        while (j < rightList.size()) {
            list.set(k++, rightList.get(j++));
        }
    }
}

// 排序上下文
class SortContext {
    private SortStrategy sortStrategy;
    
    public void setSortStrategy(SortStrategy sortStrategy) {
        this.sortStrategy = sortStrategy;
    }
    
    public void executeSort(List<Integer> list) {
        if (sortStrategy == null) {
            System.out.println("请先选择排序算法");
            return;
        }
        sortStrategy.sort(list);
    }
}

// ==================== 主类 ====================
public class Chapter21Example {
    public static void main(String[] args) {
        System.out.println("=== 策略模式示例 ===\n");
        
        // 基本策略模式示例
        basicStrategyExample();
        
        System.out.println("\n=== 支付系统示例 ===\n");
        paymentSystemExample();
        
        System.out.println("\n=== 排序算法选择系统示例 ===\n");
        sortingAlgorithmExample();
    }
    
    /**
     * 基本策略模式示例
     */
    public static void basicStrategyExample() {
        System.out.println("1. 基本策略模式示例:");
        Context context = new Context(new OperationAdd());
        System.out.println("10 + 5 = " + context.executeStrategy(10, 5));
        
        context = new Context(new OperationSubtract());
        System.out.println("10 - 5 = " + context.executeStrategy(10, 5));
        
        context = new Context(new OperationMultiply());
        System.out.println("10 * 5 = " + context.executeStrategy(10, 5));
    }
    
    /**
     * 支付系统示例
     */
    public static void paymentSystemExample() {
        System.out.println("2. 支付系统示例:");
        PaymentContext paymentContext = new PaymentContext();
        
        // 使用信用卡支付
        paymentContext.setPaymentStrategy(new CreditCardPayment(
            "1234-5678-9012-3456", "张三", "123", "12/25"));
        paymentContext.executePayment(100.0);
        
        System.out.println();
        
        // 使用支付宝支付
        paymentContext.setPaymentStrategy(new AlipayPayment("zhangsan@example.com"));
        paymentContext.executePayment(200.0);
        
        System.out.println();
        
        // 使用微信支付
        paymentContext.setPaymentStrategy(new WechatPayment("zhangsan_wechat"));
        paymentContext.executePayment(300.0);
    }
    
    /**
     * 排序算法选择系统示例
     */
    public static void sortingAlgorithmExample() {
        System.out.println("3. 排序算法选择系统示例:");
        SortContext sortContext = new SortContext();
        
        // 准备数据
        List<Integer> numbers = new ArrayList<>(Arrays.asList(64, 34, 25, 12, 22, 11, 90));
        System.out.println("原始数组: " + numbers);
        
        // 使用冒泡排序
        List<Integer> bubbleSortNumbers = new ArrayList<>(numbers);
        sortContext.setSortStrategy(new BubbleSortStrategy());
        sortContext.executeSort(bubbleSortNumbers);
        System.out.println("冒泡排序结果: " + bubbleSortNumbers);
        
        System.out.println();
        
        // 使用快速排序
        List<Integer> quickSortNumbers = new ArrayList<>(numbers);
        sortContext.setSortStrategy(new QuickSortStrategy());
        sortContext.executeSort(quickSortNumbers);
        System.out.println("快速排序结果: " + quickSortNumbers);
        
        System.out.println();
        
        // 使用归并排序
        List<Integer> mergeSortNumbers = new ArrayList<>(numbers);
        sortContext.setSortStrategy(new MergeSortStrategy());
        sortContext.executeSort(mergeSortNumbers);
        System.out.println("归并排序结果: " + mergeSortNumbers);
    }
}