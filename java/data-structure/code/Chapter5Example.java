/**
 * 第五章：堆与优先队列 - 高效的数据管理
 * 示例代码
 */
import java.util.*;
import java.time.LocalDateTime;

// 最小堆实现
class MinHeap {
    private List<Integer> heap;
    
    public MinHeap() {
        this.heap = new ArrayList<>();
    }
    
    // 获取父节点索引
    private int parent(int index) {
        return (index - 1) / 2;
    }
    
    // 获取左子节点索引
    private int leftChild(int index) {
        return 2 * index + 1;
    }
    
    // 获取右子节点索引
    private int rightChild(int index) {
        return 2 * index + 2;
    }
    
    // 交换两个元素
    private void swap(int i, int j) {
        int temp = heap.get(i);
        heap.set(i, heap.get(j));
        heap.set(j, temp);
    }
    
    // 插入元素
    public void insert(int val) {
        heap.add(val);
        heapifyUp(heap.size() - 1);
        System.out.println("插入元素: " + val);
    }
    
    // 上浮操作
    private void heapifyUp(int index) {
        while (index > 0 && heap.get(parent(index)) > heap.get(index)) {
            swap(index, parent(index));
            index = parent(index);
        }
    }
    
    // 删除最小元素
    public int extractMin() {
        if (heap.isEmpty()) {
            throw new IllegalStateException("堆为空");
        }
        
        int min = heap.get(0);
        int lastElement = heap.remove(heap.size() - 1);
        
        if (!heap.isEmpty()) {
            heap.set(0, lastElement);
            heapifyDown(0);
        }
        
        System.out.println("删除最小元素: " + min);
        return min;
    }
    
    // 下沉操作
    private void heapifyDown(int index) {
        int leftChildIndex = leftChild(index);
        int rightChildIndex = rightChild(index);
        int smallest = index;
        
        if (leftChildIndex < heap.size() && heap.get(leftChildIndex) < heap.get(smallest)) {
            smallest = leftChildIndex;
        }
        
        if (rightChildIndex < heap.size() && heap.get(rightChildIndex) < heap.get(smallest)) {
            smallest = rightChildIndex;
        }
        
        if (smallest != index) {
            swap(index, smallest);
            heapifyDown(smallest);
        }
    }
    
    // 获取最小元素（不删除）
    public int peek() {
        if (heap.isEmpty()) {
            throw new IllegalStateException("堆为空");
        }
        return heap.get(0);
    }
    
    // 判断堆是否为空
    public boolean isEmpty() {
        return heap.isEmpty();
    }
    
    // 获取堆的大小
    public int size() {
        return heap.size();
    }
    
    // 打印堆
    public void printHeap() {
        System.out.println("堆内容: " + heap);
    }
    
    // 通过堆化构建堆
    public void buildHeap(List<Integer> array) {
        heap = new ArrayList<>(array);
        for (int i = (heap.size() / 2) - 1; i >= 0; i--) {
            heapifyDown(i);
        }
        System.out.println("通过数组构建堆: " + array);
    }
}

// 自定义优先队列实现（基于最小堆）
class PriorityQueueCustom<T> {
    private List<QueueElement<T>> heap;
    private Comparator<T> comparator;
    
    // 队列元素类，包含元素值和优先级
    private static class QueueElement<T> {
        T value;
        int priority;
        
        QueueElement(T value, int priority) {
            this.value = value;
            this.priority = priority;
        }
    }
    
    // 默认构造函数（数值越小优先级越高）
    public PriorityQueueCustom() {
        this.heap = new ArrayList<>();
        this.comparator = null;
    }
    
    // 使用自定义比较器构造函数
    public PriorityQueueCustom(Comparator<T> comparator) {
        this.heap = new ArrayList<>();
        this.comparator = comparator;
    }
    
    // 获取父节点索引
    private int parent(int index) {
        return (index - 1) / 2;
    }
    
    // 获取左子节点索引
    private int leftChild(int index) {
        return 2 * index + 1;
    }
    
    // 获取右子节点索引
    private int rightChild(int index) {
        return 2 * index + 2;
    }
    
    // 交换两个元素
    private void swap(int i, int j) {
        QueueElement<T> temp = heap.get(i);
        heap.set(i, heap.get(j));
        heap.set(j, temp);
    }
    
    // 比较两个元素的优先级
    private boolean hasHigherPriority(int i, int j) {
        if (comparator != null) {
            // 使用自定义比较器
            return comparator.compare(heap.get(i).value, heap.get(j).value) < 0;
        } else {
            // 默认比较优先级数值（数值越小优先级越高）
            return heap.get(i).priority < heap.get(j).priority;
        }
    }
    
    // 入队操作
    public void enqueue(T value, int priority) {
        heap.add(new QueueElement<>(value, priority));
        heapifyUp(heap.size() - 1);
        System.out.println("入队元素: " + value + " (优先级: " + priority + ")");
    }
    
    // 上浮操作
    private void heapifyUp(int index) {
        while (index > 0 && hasHigherPriority(index, parent(index))) {
            swap(index, parent(index));
            index = parent(index);
        }
    }
    
    // 出队操作
    public T dequeue() {
        if (heap.isEmpty()) {
            throw new IllegalStateException("队列为空");
        }
        
        T value = heap.get(0).value;
        QueueElement<T> lastElement = heap.remove(heap.size() - 1);
        
        if (!heap.isEmpty()) {
            heap.set(0, lastElement);
            heapifyDown(0);
        }
        
        System.out.println("出队元素: " + value);
        return value;
    }
    
    // 下沉操作
    private void heapifyDown(int index) {
        int leftChildIndex = leftChild(index);
        int rightChildIndex = rightChild(index);
        int highestPriority = index;
        
        if (leftChildIndex < heap.size() && hasHigherPriority(leftChildIndex, highestPriority)) {
            highestPriority = leftChildIndex;
        }
        
        if (rightChildIndex < heap.size() && hasHigherPriority(rightChildIndex, highestPriority)) {
            highestPriority = rightChildIndex;
        }
        
        if (highestPriority != index) {
            swap(index, highestPriority);
            heapifyDown(highestPriority);
        }
    }
    
    // 查看队首元素（不删除）
    public T peek() {
        if (heap.isEmpty()) {
            throw new IllegalStateException("队列为空");
        }
        return heap.get(0).value;
    }
    
    // 判断队列是否为空
    public boolean isEmpty() {
        return heap.isEmpty();
    }
    
    // 获取队列大小
    public int size() {
        return heap.size();
    }
    
    // 打印队列
    public void printQueue() {
        System.out.print("队列内容: ");
        for (QueueElement<T> element : heap) {
            System.out.print("(" + element.value + ", " + element.priority + ") ");
        }
        System.out.println();
    }
}

// 寻找Top K元素
class TopKElements {
    // 寻找前K个最大的元素（使用最小堆）
    public static List<Integer> findKLargest(int[] nums, int k) {
        // 使用最小堆维护K个最大元素
        PriorityQueue<Integer> minHeap = new PriorityQueue<>();
        
        for (int num : nums) {
            if (minHeap.size() < k) {
                minHeap.offer(num);
            } else if (num > minHeap.peek()) {
                minHeap.poll();
                minHeap.offer(num);
            }
        }
        
        return new ArrayList<>(minHeap);
    }
    
    // 寻找前K个最小的元素（使用最大堆）
    public static List<Integer> findKSmallest(int[] nums, int k) {
        // 使用最大堆维护K个最小元素
        PriorityQueue<Integer> maxHeap = new PriorityQueue<>(Collections.reverseOrder());
        
        for (int num : nums) {
            if (maxHeap.size() < k) {
                maxHeap.offer(num);
            } else if (num < maxHeap.peek()) {
                maxHeap.poll();
                maxHeap.offer(num);
            }
        }
        
        return new ArrayList<>(maxHeap);
    }
}

// 链表节点定义
class ListNode {
    int val;
    ListNode next;
    ListNode() {}
    ListNode(int val) { this.val = val; }
    ListNode(int val, ListNode next) { this.val = val; this.next = next; }
}

// 合并K个有序链表
class MergeKSortedLists {
    // 合并K个有序链表
    public static ListNode mergeKLists(ListNode[] lists) {
        if (lists == null || lists.length == 0) {
            return null;
        }
        
        // 使用最小堆维护各个链表的头节点
        PriorityQueue<ListNode> minHeap = new PriorityQueue<>((a, b) -> a.val - b.val);
        
        // 将所有非空链表的头节点加入堆中
        for (ListNode list : lists) {
            if (list != null) {
                minHeap.offer(list);
            }
        }
        
        // 构建合并后的链表
        ListNode dummy = new ListNode(0);
        ListNode current = dummy;
        
        while (!minHeap.isEmpty()) {
            // 取出最小节点
            ListNode node = minHeap.poll();
            current.next = node;
            current = current.next;
            
            // 如果该节点还有下一个节点，将其加入堆中
            if (node.next != null) {
                minHeap.offer(node.next);
            }
        }
        
        return dummy.next;
    }
    
    // 辅助方法：创建链表
    public static ListNode createList(int[] values) {
        if (values.length == 0) return null;
        
        ListNode head = new ListNode(values[0]);
        ListNode current = head;
        
        for (int i = 1; i < values.length; i++) {
            current.next = new ListNode(values[i]);
            current = current.next;
        }
        
        return head;
    }
    
    // 辅助方法：打印链表
    public static void printList(ListNode head) {
        while (head != null) {
            System.out.print(head.val + " ");
            head = head.next;
        }
        System.out.println();
    }
}

// 任务类
class Task {
    String name;
    LocalDateTime executionTime;
    int priority;
    
    public Task(String name, LocalDateTime executionTime, int priority) {
        this.name = name;
        this.executionTime = executionTime;
        this.priority = priority;
    }
    
    @Override
    public String toString() {
        return "Task{name='" + name + "', time=" + executionTime + ", priority=" + priority + "}";
    }
}

// 基于时间和优先级的任务调度器
class TaskScheduler {
    // 任务调度优先队列（按执行时间和优先级排序）
    private PriorityQueue<Task> taskQueue;
    
    public TaskScheduler() {
        // 比较器：首先按执行时间排序，时间相同的按优先级排序
        this.taskQueue = new PriorityQueue<>((t1, t2) -> {
            int timeComparison = t1.executionTime.compareTo(t2.executionTime);
            if (timeComparison != 0) {
                return timeComparison;
            }
            return Integer.compare(t1.priority, t2.priority);
        });
    }
    
    // 添加任务
    public void addTask(Task task) {
        taskQueue.offer(task);
        System.out.println("添加任务: " + task);
    }
    
    // 获取下一个要执行的任务
    public Task getNextTask() {
        if (taskQueue.isEmpty()) {
            return null;
        }
        return taskQueue.poll();
    }
    
    // 查看下一个任务（不移除）
    public Task peekNextTask() {
        if (taskQueue.isEmpty()) {
            return null;
        }
        return taskQueue.peek();
    }
    
    // 获取待处理任务数量
    public int getPendingTasksCount() {
        return taskQueue.size();
    }
}

public class Chapter5Example {
    public static void main(String[] args) {
        System.out.println("=== 第五章：堆与优先队列示例 ===\n");
        
        // 1. 最小堆操作演示
        System.out.println("1. 最小堆操作演示:");
        MinHeap minHeap = new MinHeap();
        int[] values = {4, 1, 3, 2, 16, 9, 10, 14, 8, 7};
        
        System.out.println("插入元素:");
        for (int val : values) {
            minHeap.insert(val);
        }
        minHeap.printHeap();
        
        System.out.println("删除最小元素:");
        while (!minHeap.isEmpty()) {
            int min = minHeap.extractMin();
            if (!minHeap.isEmpty()) {
                minHeap.printHeap();
            }
        }
        System.out.println();
        
        // 2. 通过数组构建堆
        System.out.println("2. 通过数组构建堆:");
        List<Integer> array = Arrays.asList(4, 1, 3, 2, 16, 9, 10, 14, 8, 7);
        MinHeap heapFromList = new MinHeap();
        heapFromList.buildHeap(array);
        heapFromList.printHeap();
        System.out.println();
        
        // 3. 自定义优先队列演示
        System.out.println("3. 自定义优先队列演示:");
        PriorityQueueCustom<String> customPQ = new PriorityQueueCustom<>();
        customPQ.enqueue("低优先级任务", 3);
        customPQ.enqueue("高优先级任务", 1);
        customPQ.enqueue("中优先级任务", 2);
        customPQ.printQueue();
        
        System.out.println("出队元素:");
        while (!customPQ.isEmpty()) {
            String task = customPQ.dequeue();
            if (!customPQ.isEmpty()) {
                customPQ.printQueue();
            }
        }
        System.out.println();
        
        // 4. Top K元素查找演示
        System.out.println("4. Top K元素查找演示:");
        int[] nums = {3, 2, 1, 5, 6, 4};
        int k = 2;
        
        List<Integer> largest = TopKElements.findKLargest(nums, k);
        System.out.println("数组: " + Arrays.toString(nums));
        System.out.println("前" + k + "个最大元素: " + largest);
        
        List<Integer> smallest = TopKElements.findKSmallest(nums, k);
        System.out.println("前" + k + "个最小元素: " + smallest);
        System.out.println();
        
        // 5. 合并K个有序链表演示
        System.out.println("5. 合并K个有序链表演示:");
        ListNode list1 = MergeKSortedLists.createList(new int[]{1, 4, 5});
        ListNode list2 = MergeKSortedLists.createList(new int[]{1, 3, 4});
        ListNode list3 = MergeKSortedLists.createList(new int[]{2, 6});
        
        System.out.print("链表1: ");
        MergeKSortedLists.printList(list1);
        System.out.print("链表2: ");
        MergeKSortedLists.printList(list2);
        System.out.print("链表3: ");
        MergeKSortedLists.printList(list3);
        
        ListNode[] lists = {list1, list2, list3};
        ListNode merged = MergeKSortedLists.mergeKLists(lists);
        System.out.print("合并后: ");
        MergeKSortedLists.printList(merged);
        System.out.println();
        
        // 6. 任务调度演示
        System.out.println("6. 任务调度演示:");
        TaskScheduler scheduler = new TaskScheduler();
        LocalDateTime now = LocalDateTime.now();
        
        scheduler.addTask(new Task("任务C", now.plusMinutes(10), 3));
        scheduler.addTask(new Task("任务A", now.plusMinutes(5), 1));
        scheduler.addTask(new Task("任务B", now.plusMinutes(5), 2)); // 与任务A同一时间但优先级较低
        scheduler.addTask(new Task("任务D", now.plusMinutes(2), 1)); // 最早执行
        
        System.out.println("待处理任务数量: " + scheduler.getPendingTasksCount());
        System.out.println("下一个任务: " + scheduler.peekNextTask());
        
        System.out.println("执行任务:");
        while (scheduler.getPendingTasksCount() > 0) {
            Task task = scheduler.getNextTask();
            System.out.println("执行: " + task);
        }
        System.out.println();
        
        // 7. Java标准库PriorityQueue演示
        System.out.println("7. Java标准库PriorityQueue演示:");
        PriorityQueue<Integer> javaMinHeap = new PriorityQueue<>();
        int[] javaValues = {4, 1, 3, 2, 16, 9, 10, 14, 8, 7};
        
        System.out.println("插入元素到Java最小堆:");
        for (int val : javaValues) {
            javaMinHeap.offer(val);
            System.out.print(val + " ");
        }
        System.out.println("\nJava最小堆内容: " + javaMinHeap);
        
        System.out.println("依次取出最小元素:");
        while (!javaMinHeap.isEmpty()) {
            System.out.print(javaMinHeap.poll() + " ");
        }
        System.out.println("\n");
        
        // Java最大堆演示
        PriorityQueue<Integer> javaMaxHeap = new PriorityQueue<>(Collections.reverseOrder());
        System.out.println("插入元素到Java最大堆:");
        for (int val : javaValues) {
            javaMaxHeap.offer(val);
            System.out.print(val + " ");
        }
        System.out.println("\nJava最大堆内容: " + javaMaxHeap);
        
        System.out.println("依次取出最大元素:");
        while (!javaMaxHeap.isEmpty()) {
            System.out.print(javaMaxHeap.poll() + " ");
        }
        System.out.println();
    }
}