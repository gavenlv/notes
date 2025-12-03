/**
 * 第二章：数组与链表 - 线性数据结构详解
 * 代码示例演示了数组和链表的基本操作及性能差异
 */

// 链表节点类
class ListNode {
    int val;
    ListNode next;
    
    ListNode() {}
    ListNode(int val) { this.val = val; }
    ListNode(int val, ListNode next) { this.val = val; this.next = next; }
}

// 双向链表节点类
class DoublyListNode {
    int val;
    DoublyListNode next;
    DoublyListNode prev;
    
    DoublyListNode() {}
    DoublyListNode(int val) { this.val = val; }
    DoublyListNode(int val, DoublyListNode next, DoublyListNode prev) {
        this.val = val;
        this.next = next;
        this.prev = prev;
    }
}

// 简单链表实现
class LinkedList {
    private ListNode head;
    
    public LinkedList() {
        this.head = null;
    }
    
    // 在链表头部插入元素
    public void insertAtHead(int val) {
        ListNode newNode = new ListNode(val);
        newNode.next = head;
        head = newNode;
        System.out.println("在链表头部插入元素: " + val);
    }
    
    // 在链表尾部插入元素
    public void insertAtTail(int val) {
        ListNode newNode = new ListNode(val);
        if (head == null) {
            head = newNode;
            System.out.println("在链表头部插入元素: " + val);
            return;
        }
        
        ListNode current = head;
        while (current.next != null) {
            current = current.next;
        }
        current.next = newNode;
        System.out.println("在链表尾部插入元素: " + val);
    }
    
    // 删除指定值的节点
    public boolean delete(int val) {
        if (head == null) {
            System.out.println("链表为空，无法删除元素: " + val);
            return false;
        }
        
        // 如果要删除的是头节点
        if (head.val == val) {
            head = head.next;
            System.out.println("删除链表头部元素: " + val);
            return true;
        }
        
        ListNode current = head;
        while (current.next != null && current.next.val != val) {
            current = current.next;
        }
        
        if (current.next != null) {
            current.next = current.next.next;
            System.out.println("删除链表元素: " + val);
            return true;
        }
        
        System.out.println("未找到要删除的元素: " + val);
        return false;
    }
    
    // 查找元素
    public boolean search(int val) {
        ListNode current = head;
        while (current != null) {
            if (current.val == val) {
                System.out.println("找到元素: " + val);
                return true;
            }
            current = current.next;
        }
        System.out.println("未找到元素: " + val);
        return false;
    }
    
    // 打印链表
    public void printList() {
        System.out.print("链表内容: ");
        ListNode current = head;
        while (current != null) {
            System.out.print(current.val + " -> ");
            current = current.next;
        }
        System.out.println("null");
    }
}

// 浏览器历史记录模拟
class BrowserHistory {
    private DoublyListNode currentPage;
    private DoublyListNode head;
    
    public BrowserHistory(String homepage) {
        head = new DoublyListNode(homepage);
        currentPage = head;
        System.out.println("打开首页: " + homepage);
    }
    
    // 访问新的页面
    public void visit(String url) {
        DoublyListNode newNode = new DoublyListNode(url);
        currentPage.next = newNode;
        newNode.prev = currentPage;
        currentPage = newNode;
        System.out.println("访问页面: " + url);
    }
    
    // 后退
    public String back(int steps) {
        while (steps > 0 && currentPage.prev != null) {
            currentPage = currentPage.prev;
            steps--;
        }
        System.out.println("后退到页面: " + currentPage.val);
        return currentPage.val;
    }
    
    // 前进
    public String forward(int steps) {
        while (steps > 0 && currentPage.next != null) {
            currentPage = currentPage.next;
            steps--;
        }
        System.out.println("前进到页面: " + currentPage.val);
        return currentPage.val;
    }
    
    // 显示当前页面
    public String getCurrentPage() {
        return currentPage.val;
    }
}

public class Chapter2Example {
    
    // 演示数组操作
    public static void demonstrateArrayOperations() {
        System.out.println("=== 数组操作演示 ===");
        
        // 创建和初始化数组
        int[] array = {1, 2, 3, 4, 5};
        System.out.print("初始数组: ");
        printArray(array);
        
        // 访问数组元素
        System.out.println("访问索引2的元素: " + array[2]);
        
        // 修改数组元素
        array[2] = 10;
        System.out.print("修改后数组: ");
        printArray(array);
        
        // 遍历数组
        System.out.print("遍历数组: ");
        for (int i = 0; i < array.length; i++) {
            System.out.print(array[i] + " ");
        }
        System.out.println("\n");
    }
    
    // 演示链表操作
    public static void demonstrateLinkedListOperations() {
        System.out.println("=== 链表操作演示 ===");
        
        LinkedList list = new LinkedList();
        
        // 插入元素
        list.insertAtHead(1);
        list.insertAtHead(2);
        list.insertAtTail(3);
        list.insertAtTail(4);
        list.printList();
        
        // 查找元素
        list.search(2);
        list.search(5);
        
        // 删除元素
        list.delete(2);
        list.printList();
        list.delete(1);
        list.printList();
        System.out.println();
    }
    
    // 演示浏览器历史记录
    public static void demonstrateBrowserHistory() {
        System.out.println("=== 浏览器历史记录演示 ===");
        
        BrowserHistory browser = new BrowserHistory("home.com");
        browser.visit("google.com");
        browser.visit("github.com");
        browser.visit("stackoverflow.com");
        
        browser.back(1);  // 回到 github.com
        browser.back(1);  // 回到 google.com
        browser.forward(2); // 前进到 stackoverflow.com
        System.out.println();
    }
    
    // 辅助方法：打印数组
    public static void printArray(int[] array) {
        for (int value : array) {
            System.out.print(value + " ");
        }
        System.out.println();
    }
    
    // 性能比较测试
    public static void performanceComparison() {
        System.out.println("=== 数组与链表性能比较 ===");
        
        int size = 10000;
        
        // 数组插入测试
        long startTime = System.nanoTime();
        int[] array = new int[size];
        for (int i = 0; i < size; i++) {
            array[i] = i;
        }
        long arrayTime = System.nanoTime() - startTime;
        
        // 链表插入测试
        startTime = System.nanoTime();
        LinkedList list = new LinkedList();
        for (int i = 0; i < size; i++) {
            list.insertAtTail(i);
        }
        long listTime = System.nanoTime() - startTime;
        
        System.out.println("数组插入 " + size + " 个元素耗时: " + arrayTime / 1000 + " 微秒");
        System.out.println("链表插入 " + size + " 个元素耗时: " + listTime / 1000 + " 微秒");
        System.out.println("注意：这只是简单的性能比较，实际情况会因操作类型而异\n");
    }
    
    // 测试方法
    public static void main(String[] args) {
        System.out.println("=== 第二章：数组与链表演示 ===\n");
        
        // 演示数组操作
        demonstrateArrayOperations();
        
        // 演示链表操作
        demonstrateLinkedListOperations();
        
        // 演示浏览器历史记录
        demonstrateBrowserHistory();
        
        // 性能比较
        performanceComparison();
        
        System.out.println("=== 演示结束 ===");
    }
}