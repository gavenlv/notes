/**
 * 第三章：栈与队列 - 特殊线性结构及应用场景
 * 代码示例演示了栈和队列的基本操作及实际应用
 */

// 数组实现的栈
class ArrayStack {
    private int[] stack;
    private int top;
    private int capacity;
    
    // 构造函数
    public ArrayStack(int size) {
        this.capacity = size;
        this.stack = new int[capacity];
        this.top = -1;  // -1表示栈为空
    }
    
    // 入栈操作
    public void push(int value) {
        if (isFull()) {
            throw new RuntimeException("栈已满");
        }
        stack[++top] = value;
        System.out.println("入栈: " + value);
    }
    
    // 出栈操作
    public int pop() {
        if (isEmpty()) {
            throw new RuntimeException("栈为空");
        }
        int value = stack[top--];
        System.out.println("出栈: " + value);
        return value;
    }
    
    // 查看栈顶元素
    public int peek() {
        if (isEmpty()) {
            throw new RuntimeException("栈为空");
        }
        return stack[top];
    }
    
    // 判断栈是否为空
    public boolean isEmpty() {
        return top == -1;
    }
    
    // 判断栈是否已满
    public boolean isFull() {
        return top == capacity - 1;
    }
    
    // 获取栈的大小
    public int size() {
        return top + 1;
    }
    
    // 打印栈的内容
    public void printStack() {
        if (isEmpty()) {
            System.out.println("栈为空");
            return;
        }
        System.out.print("栈内容（从栈顶到栈底）: ");
        for (int i = top; i >= 0; i--) {
            System.out.print(stack[i] + " ");
        }
        System.out.println();
    }
}

// 数组实现的队列（循环队列）
class ArrayQueue {
    private int[] queue;
    private int front;
    private int rear;
    private int size;
    private int capacity;
    
    // 构造函数
    public ArrayQueue(int capacity) {
        this.capacity = capacity;
        this.queue = new int[capacity];
        this.front = 0;
        this.rear = -1;
        this.size = 0;
    }
    
    // 入队操作
    public void enqueue(int value) {
        if (isFull()) {
            throw new RuntimeException("队列已满");
        }
        rear = (rear + 1) % capacity;  // 循环队列
        queue[rear] = value;
        size++;
        System.out.println("入队: " + value);
    }
    
    // 出队操作
    public int dequeue() {
        if (isEmpty()) {
            throw new RuntimeException("队列为空");
        }
        int value = queue[front];
        front = (front + 1) % capacity;  // 循环队列
        size--;
        System.out.println("出队: " + value);
        return value;
    }
    
    // 查看队头元素
    public int front() {
        if (isEmpty()) {
            throw new RuntimeException("队列为空");
        }
        return queue[front];
    }
    
    // 判断队列是否为空
    public boolean isEmpty() {
        return size == 0;
    }
    
    // 判断队列是否已满
    public boolean isFull() {
        return size == capacity;
    }
    
    // 获取队列大小
    public int size() {
        return size;
    }
    
    // 打印队列内容
    public void printQueue() {
        if (isEmpty()) {
            System.out.println("队列为空");
            return;
        }
        System.out.print("队列内容（从队头到队尾）: ");
        for (int i = 0; i < size; i++) {
            int index = (front + i) % capacity;
            System.out.print(queue[index] + " ");
        }
        System.out.println();
    }
}

// 括号匹配检查器
class ParenthesesChecker {
    private ArrayStack stack;
    
    public ParenthesesChecker(int size) {
        this.stack = new ArrayStack(size);
    }
    
    public boolean isBalanced(String expression) {
        System.out.println("检查表达式括号是否匹配: " + expression);
        
        for (char ch : expression.toCharArray()) {
            if (ch == '(' || ch == '[' || ch == '{') {
                // 遇到开括号，入栈
                stack.push(ch);
            } else if (ch == ')' || ch == ']' || ch == '}') {
                // 遇到闭括号，检查是否匹配
                if (stack.isEmpty()) {
                    System.out.println("右括号多余");
                    return false;
                }
                
                char top = (char) stack.pop();
                if (!isMatchingPair(top, ch)) {
                    System.out.println("括号不匹配: " + top + " 与 " + ch);
                    return false;
                }
            }
        }
        
        // 最后栈应该为空
        boolean result = stack.isEmpty();
        if (result) {
            System.out.println("括号匹配正确");
        } else {
            System.out.println("左括号多余");
        }
        return result;
    }
    
    private boolean isMatchingPair(char open, char close) {
        return (open == '(' && close == ')') ||
               (open == '[' && close == ']') ||
               (open == '{' && close == '}');
    }
}

// 浏览器后退功能模拟
class BrowserBackFunction {
    private java.util.List<String> backStack;  // 后退栈
    private java.util.List<String> forwardStack;  // 前进栈
    private String currentPage;
    
    public BrowserBackFunction() {
        backStack = new java.util.ArrayList<>();
        forwardStack = new java.util.ArrayList<>();
        currentPage = "";
    }
    
    // 访问新页面
    public void visit(String url) {
        if (!currentPage.isEmpty()) {
            backStack.add(currentPage);
        }
        currentPage = url;
        forwardStack.clear();  // 访问新页面后清空前进栈
        System.out.println("访问页面: " + url);
    }
    
    // 后退
    public void back() {
        if (backStack.isEmpty()) {
            System.out.println("无法后退");
            return;
        }
        
        forwardStack.add(currentPage);
        currentPage = backStack.remove(backStack.size() - 1);
        System.out.println("后退到: " + currentPage);
    }
    
    // 前进
    public void forward() {
        if (forwardStack.isEmpty()) {
            System.out.println("无法前进");
            return;
        }
        
        backStack.add(currentPage);
        currentPage = forwardStack.remove(forwardStack.size() - 1);
        System.out.println("前进到: " + currentPage);
    }
    
    // 显示当前页面
    public String getCurrentPage() {
        return currentPage;
    }
}

public class Chapter3Example {
    
    // 演示栈的基本操作
    public static void demonstrateStackOperations() {
        System.out.println("=== 栈的基本操作演示 ===");
        
        ArrayStack stack = new ArrayStack(5);
        
        // 入栈操作
        stack.push(10);
        stack.push(20);
        stack.push(30);
        stack.printStack();
        
        // 查看栈顶
        System.out.println("栈顶元素: " + stack.peek());
        
        // 出栈操作
        stack.pop();
        stack.printStack();
        
        // 获取栈大小
        System.out.println("栈大小: " + stack.size());
        System.out.println();
    }
    
    // 演示队列的基本操作
    public static void demonstrateQueueOperations() {
        System.out.println("=== 队列的基本操作演示 ===");
        
        ArrayQueue queue = new ArrayQueue(5);
        
        // 入队操作
        queue.enqueue(100);
        queue.enqueue(200);
        queue.enqueue(300);
        queue.printQueue();
        
        // 查看队头
        System.out.println("队头元素: " + queue.front());
        
        // 出队操作
        queue.dequeue();
        queue.printQueue();
        
        // 获取队列大小
        System.out.println("队列大小: " + queue.size());
        System.out.println();
    }
    
    // 演示括号匹配检查
    public static void demonstrateParenthesesChecking() {
        System.out.println("=== 括号匹配检查演示 ===");
        
        ParenthesesChecker checker1 = new ParenthesesChecker(10);
        checker1.isBalanced("()[]{}");
        
        ParenthesesChecker checker2 = new ParenthesesChecker(10);
        checker2.isBalanced("([{}])");
        
        ParenthesesChecker checker3 = new ParenthesesChecker(10);
        checker3.isBalanced("([)]");
        
        System.out.println();
    }
    
    // 演示浏览器后退功能
    public static void demonstrateBrowserBackFunction() {
        System.out.println("=== 浏览器后退功能演示 ===");
        
        BrowserBackFunction browser = new BrowserBackFunction();
        browser.visit("home.com");
        browser.visit("google.com");
        browser.visit("github.com");
        browser.visit("stackoverflow.com");
        
        browser.back();  // 回到 github.com
        browser.back();  // 回到 google.com
        browser.forward(); // 前进到 github.com
        System.out.println();
    }
    
    // 性能比较测试
    public static void performanceComparison() {
        System.out.println("=== 栈与队列性能比较 ===");
        
        int size = 10000;
        
        // 栈操作测试
        long startTime = System.nanoTime();
        ArrayStack stack = new ArrayStack(size);
        for (int i = 0; i < size; i++) {
            stack.push(i);
        }
        for (int i = 0; i < size; i++) {
            stack.pop();
        }
        long stackTime = System.nanoTime() - startTime;
        
        // 队列操作测试
        startTime = System.nanoTime();
        ArrayQueue queue = new ArrayQueue(size);
        for (int i = 0; i < size; i++) {
            queue.enqueue(i);
        }
        for (int i = 0; i < size; i++) {
            queue.dequeue();
        }
        long queueTime = System.nanoTime() - startTime;
        
        System.out.println("栈操作 " + (size*2) + " 次耗时: " + stackTime / 1000 + " 微秒");
        System.out.println("队列操作 " + (size*2) + " 次耗时: " + queueTime / 1000 + " 微秒");
        System.out.println();
    }
    
    // 测试方法
    public static void main(String[] args) {
        System.out.println("=== 第三章：栈与队列演示 ===\n");
        
        // 演示栈操作
        demonstrateStackOperations();
        
        // 演示队列操作
        demonstrateQueueOperations();
        
        // 演示括号匹配检查
        demonstrateParenthesesChecking();
        
        // 演示浏览器后退功能
        demonstrateBrowserBackFunction();
        
        // 性能比较
        performanceComparison();
        
        System.out.println("=== 演示结束 ===");
    }
}