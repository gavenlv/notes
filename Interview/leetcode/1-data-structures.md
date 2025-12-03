# LeetCode数据结构专题

## 📚 简介

数据结构是计算机存储、组织数据的方式，是算法设计的基础。在LeetCode刷题过程中，掌握各种数据结构的特点和应用场景至关重要。本专题将详细介绍LeetCode中常见的数据结构及其应用。

## 🎯 学习目标

- 理解各种数据结构的基本概念和特点
- 掌握各数据结构的实现原理
- 熟悉各数据结构在LeetCode题目中的应用
- 能够根据题目要求选择合适的数据结构

## 🗂️ 数据结构分类

### 1. 数组(Array)和字符串(String)

#### 基本概念
数组是一种线性数据结构，用于存储相同类型的元素。在内存中连续存储，支持通过索引随机访问。

字符串是由字符组成的序列，在大多数编程语言中，字符串是不可变的。

#### 核心操作
- 访问元素：O(1)
- 搜索元素：O(n)
- 插入元素：O(n)
- 删除元素：O(n)

#### 常见技巧
1. **双指针技巧**：适用于有序数组、回文判断等问题
2. **滑动窗口**：解决子数组、子字符串问题
3. **前缀和**：快速计算区间和
4. **哈希表辅助**：快速查找元素位置

#### 经典例题
1. [两数之和](https://leetcode.com/problems/two-sum/)
2. [盛最多水的容器](https://leetcode.com/problems/container-with-most-water/)
3. [三数之和](https://leetcode.com/problems/3sum/)
4. [最接近的三数之和](https://leetcode.com/problems/3sum-closest/)
5. [删除有序数组中的重复项](https://leetcode.com/problems/remove-duplicates-from-sorted-array/)
6. [移动零](https://leetcode.com/problems/move-zeroes/)
7. [旋转数组](https://leetcode.com/problems/rotate-array/)
8. [反转字符串](https://leetcode.com/problems/reverse-string/)
9. [翻转字符串里的单词](https://leetcode.com/problems/reverse-words-in-a-string/)
10. [无重复字符的最长子串](https://leetcode.com/problems/longest-substring-without-repeating-characters/)

#### 代码模板

```java
// 双指针遍历数组
public void twoPointers(int[] nums) {
    int left = 0, right = nums.length - 1;
    while (left < right) {
        // 根据条件移动指针
        if (condition) {
            left++;
        } else {
            right--;
        }
    }
}

// 滑动窗口
public int slidingWindow(int[] nums) {
    int left = 0, right = 0;
    int result = 0;
    
    while (right < nums.length) {
        // 扩展右边界
        // 更新结果
        
        // 收缩左边界
        while (windowNeedsShrink) {
            // 更新窗口信息
            left++;
        }
        
        right++;
    }
    
    return result;
}
```

### 2. 链表(Linked List)

#### 基本概念
链表是一种线性数据结构，其中的元素不是在内存中连续存储的。每个元素（节点）包含数据和指向下一个节点的引用。

#### 核心操作
- 访问元素：O(n)
- 搜索元素：O(n)
- 插入元素：O(1)
- 删除元素：O(1)

#### 常见技巧
1. **哑节点(Dummy Node)**：简化头节点操作
2. **双指针技巧**：快慢指针找中点、检测环等
3. **反转链表**：递归和迭代两种方法
4. **合并链表**：类似归并排序的合并过程

#### 经典例题
1. [反转链表](https://leetcode.com/problems/reverse-linked-list/)
2. [反转链表 II](https://leetcode.com/problems/reverse-linked-list-ii/)
3. [合并两个有序链表](https://leetcode.com/problems/merge-two-sorted-lists/)
4. [合并K个升序链表](https://leetcode.com/problems/merge-k-sorted-lists/)
5. [两两交换链表中的节点](https://leetcode.com/problems/swap-nodes-in-pairs/)
6. [K 个一组翻转链表](https://leetcode.com/problems/reverse-nodes-in-k-group/)
7. [删除链表的倒数第 N 个结点](https://leetcode.com/problems/remove-nth-node-from-end-of-list/)
8. [环形链表](https://leetcode.com/problems/linked-list-cycle/)
9. [环形链表 II](https://leetcode.com/problems/linked-list-cycle-ii/)
10. [相交链表](https://leetcode.com/problems/intersection-of-two-linked-lists/)

#### 代码模板

```java
// 链表节点定义
class ListNode {
    int val;
    ListNode next;
    ListNode() {}
    ListNode(int val) { this.val = val; }
    ListNode(int val, ListNode next) { this.val = val; this.next = next; }
}

// 反转链表 - 迭代
public ListNode reverseList(ListNode head) {
    ListNode prev = null;
    ListNode curr = head;
    
    while (curr != null) {
        ListNode next = curr.next;
        curr.next = prev;
        prev = curr;
        curr = next;
    }
    
    return prev;
}

// 反转链表 - 递归
public ListNode reverseListRecursive(ListNode head) {
    if (head == null || head.next == null) {
        return head;
    }
    
    ListNode newHead = reverseListRecursive(head.next);
    head.next.next = head;
    head.next = null;
    
    return newHead;
}

// 快慢指针找中点
public ListNode findMiddle(ListNode head) {
    ListNode slow = head, fast = head;
    
    while (fast != null && fast.next != null) {
        slow = slow.next;
        fast = fast.next.next;
    }
    
    return slow;
}
```

### 3. 栈(Stack)和队列(Queue)

#### 基本概念
栈是一种后进先出(LIFO)的数据结构，队列是一种先进先出(FIFO)的数据结构。

#### 核心操作
栈操作：
- push：O(1)
- pop：O(1)
- top/peek：O(1)

队列操作：
- enqueue：O(1)
- dequeue：O(1)
- front：O(1)

#### 常见技巧
1. **单调栈**：维护元素的单调性，解决Next Greater Element等问题
2. **双端队列**：滑动窗口最大值等问题
3. **BFS遍历**：使用队列实现广度优先搜索
4. **函数调用栈**：递归问题的理解

#### 经典例题
1. [有效的括号](https://leetcode.com/problems/valid-parentheses/)
2. [每日温度](https://leetcode.com/problems/daily-temperatures/)
3. [柱状图中最大的矩形](https://leetcode.com/problems/largest-rectangle-in-histogram/)
4. [接雨水](https://leetcode.com/problems/trapping-rain-water/)
5. [用栈实现队列](https://leetcode.com/problems/implement-queue-using-stacks/)
6. [用队列实现栈](https://leetcode.com/problems/implement-stack-using-queues/)
7. [二叉树的层序遍历](https://leetcode.com/problems/binary-tree-level-order-traversal/)
8. [打开转盘锁](https://leetcode.com/problems/open-the-lock/)
9. [滑动窗口最大值](https://leetcode.com/problems/sliding-window-maximum/)
10. [字符串解码](https://leetcode.com/problems/decode-string/)

#### 代码模板

```java
import java.util.*;

// 单调栈模板 - 下一个更大元素
public int[] nextGreaterElement(int[] nums) {
    int[] result = new int[nums.length];
    Stack<Integer> stack = new Stack<>();
    
    for (int i = nums.length - 1; i >= 0; i--) {
        while (!stack.isEmpty() && stack.peek() <= nums[i]) {
            stack.pop();
        }
        
        result[i] = stack.isEmpty() ? -1 : stack.peek();
        stack.push(nums[i]);
    }
    
    return result;
}

// BFS模板
public void bfs(TreeNode root) {
    if (root == null) return;
    
    Queue<TreeNode> queue = new LinkedList<>();
    queue.offer(root);
    
    while (!queue.isEmpty()) {
        int size = queue.size();
        
        for (int i = 0; i < size; i++) {
            TreeNode node = queue.poll();
            // 处理当前节点
            
            if (node.left != null) {
                queue.offer(node.left);
            }
            
            if (node.right != null) {
                queue.offer(node.right);
            }
        }
    }
}
```

### 4. 树(Tree)

#### 基本概念
树是一种非线性数据结构，由节点组成，每个节点可以有零个或多个子节点。二叉树是最常见的树结构，每个节点最多有两个子节点。

#### 核心操作
- 遍历：O(n)
- 搜索：O(log n)（平衡二叉树）
- 插入：O(log n)（平衡二叉树）
- 删除：O(log n)（平衡二叉树）

#### 常见技巧
1. **递归遍历**：前序、中序、后序遍历
2. **迭代遍历**：使用栈模拟递归
3. **层次遍历**：使用队列实现BFS
4. **Morris遍历**：O(1)空间复杂度遍历

#### 经典例题
1. [二叉树的前序遍历](https://leetcode.com/problems/binary-tree-preorder-traversal/)
2. [二叉树的中序遍历](https://leetcode.com/problems/binary-tree-inorder-traversal/)
3. [二叉树的后序遍历](https://leetcode.com/problems/binary-tree-postorder-traversal/)
4. [二叉树的层序遍历](https://leetcode.com/problems/binary-tree-level-order-traversal/)
5. [二叉树的最大深度](https://leetcode.com/problems/maximum-depth-of-binary-tree/)
6. [二叉树的直径](https://leetcode.com/problems/diameter-of-binary-tree/)
7. [翻转二叉树](https://leetcode.com/problems/invert-binary-tree/)
8. [对称二叉树](https://leetcode.com/problems/symmetric-tree/)
9. [路径总和](https://leetcode.com/problems/path-sum/)
10. [从中序与后序遍历序列构造二叉树](https://leetcode.com/problems/construct-binary-tree-from-inorder-and-postorder-traversal/)

#### 代码模板

```java
// 二叉树节点定义
class TreeNode {
    int val;
    TreeNode left;
    TreeNode right;
    TreeNode() {}
    TreeNode(int val) { this.val = val; }
    TreeNode(int val, TreeNode left, TreeNode right) {
        this.val = val;
        this.left = left;
        this.right = right;
    }
}

// 前序遍历 - 递归
public List<Integer> preorderTraversal(TreeNode root) {
    List<Integer> result = new ArrayList<>();
    preorderHelper(root, result);
    return result;
}

private void preorderHelper(TreeNode node, List<Integer> result) {
    if (node == null) return;
    
    result.add(node.val);
    preorderHelper(node.left, result);
    preorderHelper(node.right, result);
}

// 前序遍历 - 迭代
public List<Integer> preorderTraversalIterative(TreeNode root) {
    List<Integer> result = new ArrayList<>();
    if (root == null) return result;
    
    Stack<TreeNode> stack = new Stack<>();
    stack.push(root);
    
    while (!stack.isEmpty()) {
        TreeNode node = stack.pop();
        result.add(node.val);
        
        if (node.right != null) {
            stack.push(node.right);
        }
        
        if (node.left != null) {
            stack.push(node.left);
        }
    }
    
    return result;
}

// 层序遍历
public List<List<Integer>> levelOrder(TreeNode root) {
    List<List<Integer>> result = new ArrayList<>();
    if (root == null) return result;
    
    Queue<TreeNode> queue = new LinkedList<>();
    queue.offer(root);
    
    while (!queue.isEmpty()) {
        int size = queue.size();
        List<Integer> level = new ArrayList<>();
        
        for (int i = 0; i < size; i++) {
            TreeNode node = queue.poll();
            level.add(node.val);
            
            if (node.left != null) {
                queue.offer(node.left);
            }
            
            if (node.right != null) {
                queue.offer(node.right);
            }
        }
        
        result.add(level);
    }
    
    return result;
}
```

### 5. 堆(Heap)和优先队列(Priority Queue)

#### 基本概念
堆是一种特殊的完全二叉树，分为最大堆和最小堆。优先队列是一种抽象数据类型，堆是其实现方式之一。

#### 核心操作
- 插入元素：O(log n)
- 删除最值：O(log n)
- 获取最值：O(1)

#### 常见技巧
1. **Top K问题**：使用堆维护前K个元素
2. **合并K个有序链表**：使用最小堆
3. **数据流中的中位数**：使用两个堆
4. **定时任务调度**：使用最小堆维护最近的任务

#### 经典例题
1. [数组中的第K个最大元素](https://leetcode.com/problems/kth-largest-element-in-an-array/)
2. [前 K 个高频元素](https://leetcode.com/problems/top-k-frequent-elements/)
3. [合并K个升序链表](https://leetcode.com/problems/merge-k-sorted-lists/)
4. [最小栈](https://leetcode.com/problems/min-stack/)
5. [数据流的中位数](https://leetcode.com/problems/find-median-from-data-stream/)
6. [查找和最小的K对数字](https://leetcode.com/problems/find-k-pairs-with-smallest-sums/)
7. [超级丑数](https://leetcode.com/problems/super-ugly-number/)
8. [ IPO ](https://leetcode.com/problems/ipo/)
9. [重构字符串](https://leetcode.com/problems/reorganize-string/)
10. [任务调度器](https://leetcode.com/problems/task-scheduler/)

#### 代码模板

```java
import java.util.*;

// 最小堆
PriorityQueue<Integer> minHeap = new PriorityQueue<>();

// 最大堆
PriorityQueue<Integer> maxHeap = new PriorityQueue<>(Collections.reverseOrder());

// 自定义比较器的堆
PriorityQueue<int[]> heap = new PriorityQueue<>((a, b) -> a[0] - b[0]);

// Top K问题模板
public int[] topKFrequent(int[] nums, int k) {
    // 统计频率
    Map<Integer, Integer> freqMap = new HashMap<>();
    for (int num : nums) {
        freqMap.put(num, freqMap.getOrDefault(num, 0) + 1);
    }
    
    // 使用最小堆维护前K个高频元素
    PriorityQueue<Integer> minHeap = new PriorityQueue<>(
        (a, b) -> freqMap.get(a) - freqMap.get(b)
    );
    
    for (int key : freqMap.keySet()) {
        minHeap.offer(key);
        if (minHeap.size() > k) {
            minHeap.poll();
        }
    }
    
    // 构造结果
    int[] result = new int[k];
    for (int i = k - 1; i >= 0; i--) {
        result[i] = minHeap.poll();
    }
    
    return result;
}
```

### 6. 哈希表(Hash Table)

#### 基本概念
哈希表是一种通过哈希函数将键映射到值的数据结构，支持快速的插入、删除和查找操作。

#### 核心操作
- 插入：O(1)
- 查找：O(1)
- 删除：O(1)

#### 常见技巧
1. **统计频次**：使用哈希表统计元素出现次数
2. **去重**：使用HashSet去除重复元素
3. **映射关系**：建立元素间的映射关系
4. **滑动窗口**：配合滑动窗口解决子数组问题

#### 经典例题
1. [两数之和](https://leetcode.com/problems/two-sum/)
2. [三数之和](https://leetcode.com/problems/3sum/)
3. [四数之和](https://leetcode.com/problems/4sum/)
4. [字母异位词分组](https://leetcode.com/problems/group-anagrams/)
5. [最长连续序列](https://leetcode.com/problems/longest-consecutive-sequence/)
6. [LRU 缓存](https://leetcode.com/problems/lru-cache/)
7. [存在重复元素](https://leetcode.com/problems/contains-duplicate/)
8. [只出现一次的数字](https://leetcode.com/problems/single-number/)
9. [快乐数](https://leetcode.com/problems/happy-number/)
10. [同构字符串](https://leetcode.com/problems/isomorphic-strings/)

#### 代码模板

```java
import java.util.*;

// 基本哈希表操作
Map<String, Integer> map = new HashMap<>();
map.put("key", 1);           // 插入
int value = map.get("key");  // 查找
map.remove("key");           // 删除

// HashSet去重
Set<Integer> set = new HashSet<>();
set.add(1);
boolean contains = set.contains(1);

// 统计频次模板
public Map<Integer, Integer> countFrequency(int[] nums) {
    Map<Integer, Integer> freqMap = new HashMap<>();
    for (int num : nums) {
        freqMap.put(num, freqMap.getOrDefault(num, 0) + 1);
    }
    return freqMap;
}

// 两数之和模板
public int[] twoSum(int[] nums, int target) {
    Map<Integer, Integer> map = new HashMap<>();
    
    for (int i = 0; i < nums.length; i++) {
        int complement = target - nums[i];
        if (map.containsKey(complement)) {
            return new int[]{map.get(complement), i};
        }
        map.put(nums[i], i);
    }
    
    return new int[]{}; // 无解
}
```

## 📚 总结

掌握这些基本数据结构是解决LeetCode问题的基础。在实际解题过程中，往往需要结合多种数据结构来解决问题。建议：

1. **熟练掌握每种数据结构的基本操作**
2. **理解各种数据结构的时间复杂度和空间复杂度**
3. **积累常见题型的解题模板**
4. **多做练习，培养直觉**

在下一章节中，我们将探讨算法技巧专题，包括双指针、滑动窗口、二分查找等常用算法技巧。