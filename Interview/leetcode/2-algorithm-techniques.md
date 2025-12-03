# LeetCode算法技巧专题

## 📚 简介

算法技巧是在解决特定类型问题时经常使用的通用方法和策略。掌握这些技巧可以帮助我们更高效地解决LeetCode上的各类问题。本专题将介绍一些常用的算法技巧及其应用。

## 🎯 学习目标

- 理解各种算法技巧的基本思想
- 掌握各技巧的适用场景
- 熟练运用这些技巧解决实际问题
- 培养算法思维，提高解题效率

## 🗂️ 算法技巧分类

### 1. 双指针技巧(Two Pointers)

#### 基本思想
使用两个指针在数据结构上协同移动，通常用于数组、链表等线性结构。

#### 应用场景
1. 有序数组中的两数之和问题
2. 反转数组或链表
3. 移除数组中的特定元素
4. 滑动窗口问题

#### 经典例题
1. [两数之和 II - 输入有序数组](https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/)
2. [移除元素](https://leetcode.com/problems/remove-element/)
3. [移动零](https://leetcode.com/problems/move-zeroes/)
4. [删除有序数组中的重复项](https://leetcode.com/problems/remove-duplicates-from-sorted-array/)
5. [盛最多水的容器](https://leetcode.com/problems/container-with-most-water/)
6. [三数之和](https://leetcode.com/problems/3sum/)
7. [最接近的三数之和](https://leetcode.com/problems/3sum-closest/)
8. [四数之和](https://leetcode.com/problems/4sum/)

#### 代码模板

```java
// 对撞指针 - 有序数组两数之和
public int[] twoSum(int[] numbers, int target) {
    int left = 0, right = numbers.length - 1;
    
    while (left < right) {
        int sum = numbers[left] + numbers[right];
        if (sum == target) {
            return new int[]{left + 1, right + 1}; // 返回1-indexed
        } else if (sum < target) {
            left++; // 和太小，增大左指针
        } else {
            right--; // 和太大，减小右指针
        }
    }
    
    return new int[]{-1, -1}; // 无解
}

// 快慢指针 - 移除元素
public int removeElement(int[] nums, int val) {
    int slow = 0;
    
    for (int fast = 0; fast < nums.length; fast++) {
        if (nums[fast] != val) {
            nums[slow++] = nums[fast];
        }
    }
    
    return slow;
}

// 滑动窗口 - 最小覆盖子串
public String minWindow(String s, String t) {
    Map<Character, Integer> need = new HashMap<>();
    Map<Character, Integer> window = new HashMap<>();
    
    for (char c : t.toCharArray()) {
        need.put(c, need.getOrDefault(c, 0) + 1);
    }
    
    int left = 0, right = 0;
    int valid = 0;
    int start = 0, len = Integer.MAX_VALUE;
    
    while (right < s.length()) {
        char c = s.charAt(right);
        right++;
        
        if (need.containsKey(c)) {
            window.put(c, window.getOrDefault(c, 0) + 1);
            if (window.get(c).equals(need.get(c))) {
                valid++;
            }
        }
        
        while (valid == need.size()) {
            if (right - left < len) {
                start = left;
                len = right - left;
            }
            
            char d = s.charAt(left);
            left++;
            
            if (need.containsKey(d)) {
                if (window.get(d).equals(need.get(d))) {
                    valid--;
                }
                window.put(d, window.get(d) - 1);
            }
        }
    }
    
    return len == Integer.MAX_VALUE ? "" : s.substring(start, start + len);
}
```

### 2. 滑动窗口(Sliding Window)

#### 基本思想
维护一个窗口，通过扩展和收缩窗口来解决问题，常用于子数组、子字符串问题。

#### 应用场景
1. 最大/最小子数组和问题
2. 包含特定字符的最短子串
3. 无重复字符的最长子串
4. 至多包含K个不同字符的最长子串

#### 经典例题
1. [无重复字符的最长子串](https://leetcode.com/problems/longest-substring-without-repeating-characters/)
2. [最小覆盖子串](https://leetcode.com/problems/minimum-window-substring/)
3. [串联所有单词的子串](https://leetcode.com/problems/substring-with-concatenation-of-all-words/)
4. [长度最小的子数组](https://leetcode.com/problems/minimum-size-subarray-sum/)
5. [滑动窗口最大值](https://leetcode.com/problems/sliding-window-maximum/)
6. [字符串的排列](https://leetcode.com/problems/permutation-in-string/)
7. [找到字符串中所有字母异位词](https://leetcode.com/problems/find-all-anagrams-in-a-string/)
8. [至多包含两个不同字符的最长子串](https://leetcode.com/problems/longest-substring-with-at-most-two-distinct-characters/)

#### 代码模板

```java
// 滑动窗口通用模板
public int slidingWindowTemplate(int[] nums) {
    int left = 0, right = 0;
    int result = 0;
    
    // 用于记录窗口状态的数据结构
    // 如：HashMap<Character, Integer> window = new HashMap<>();
    
    while (right < nums.length) {
        // 扩大窗口
        // int c = nums[right];
        // right++;
        // 更新窗口数据
        
        // 判断左侧窗口是否要收缩
        while (windowNeedsShrink) {
            // int d = nums[left];
            // left++;
            // 更新窗口数据
        }
        
        // 更新结果
        // result = Math.max(result, right - left);
    }
    
    return result;
}

// 无重复字符的最长子串
public int lengthOfLongestSubstring(String s) {
    Map<Character, Integer> window = new HashMap<>();
    int left = 0, right = 0;
    int res = 0;
    
    while (right < s.length()) {
        char c = s.charAt(right);
        right++;
        
        window.put(c, window.getOrDefault(c, 0) + 1);
        
        while (window.get(c) > 1) {
            char d = s.charAt(left);
            left++;
            window.put(d, window.get(d) - 1);
        }
        
        res = Math.max(res, right - left);
    }
    
    return res;
}
```

### 3. 二分查找(Binary Search)

#### 基本思想
在有序数组中查找特定元素，每次将搜索范围缩小一半，时间复杂度为O(log n)。

#### 应用场景
1. 在有序数组中查找目标值
2. 寻找峰值元素
3. 搜索旋转排序数组
4. 在排序数组中查找元素的第一个和最后一个位置
5. 寻找插入位置

#### 经典例题
1. [二分查找](https://leetcode.com/problems/binary-search/)
2. [搜索插入位置](https://leetcode.com/problems/search-insert-position/)
3. [在排序数组中查找元素的第一个和最后一个位置](https://leetcode.com/problems/find-first-and-last-position-of-element-in-sorted-array/)
4. [搜索旋转排序数组](https://leetcode.com/problems/search-in-rotated-sorted-array/)
5. [搜索旋转排序数组 II](https://leetcode.com/problems/search-in-rotated-sorted-array-ii/)
6. [寻找峰值](https://leetcode.com/problems/find-peak-element/)
7. [寻找旋转排序数组中的最小值](https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/)
8. [寻找旋转排序数组中的最小值 II](https://leetcode.com/problems/find-minimum-in-rotated-sorted-array-ii/)
9. [搜索二维矩阵](https://leetcode.com/problems/search-a-2d-matrix/)
10. [在排序数组中查找数字 I](https://leetcode.com/problems/find-numbers-with-even-number-of-digits/)

#### 代码模板

```java
// 基本二分查找
public int binarySearch(int[] nums, int target) {
    int left = 0, right = nums.length - 1;
    
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (nums[mid] == target) {
            return mid;
        } else if (nums[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    
    return -1; // 未找到
}

// 寻找左侧边界的二分查找
public int leftBound(int[] nums, int target) {
    int left = 0, right = nums.length;
    
    while (left < right) {
        int mid = left + (right - left) / 2;
        if (nums[mid] >= target) {
            right = mid;
        } else {
            left = mid + 1;
        }
    }
    
    return left;
}

// 寻找右侧边界的二分查找
public int rightBound(int[] nums, int target) {
    int left = 0, right = nums.length;
    
    while (left < right) {
        int mid = left + (right - left) / 2;
        if (nums[mid] <= target) {
            left = mid + 1;
        } else {
            right = mid;
        }
    }
    
    return left - 1;
}

// 搜索旋转排序数组
public int search(int[] nums, int target) {
    int left = 0, right = nums.length - 1;
    
    while (left <= right) {
        int mid = left + (right - left) / 2;
        
        if (nums[mid] == target) {
            return mid;
        }
        
        // 判断哪一部分是有序的
        if (nums[left] <= nums[mid]) {
            // 左半部分有序
            if (nums[left] <= target && target < nums[mid]) {
                right = mid - 1;
            } else {
                left = mid + 1;
            }
        } else {
            // 右半部分有序
            if (nums[mid] < target && target <= nums[right]) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
    }
    
    return -1;
}
```

### 4. 分治法(Divide and Conquer)

#### 基本思想
将问题分解为若干个规模较小的相同问题，递归求解，然后将子问题的解合并得到原问题的解。

#### 应用场景
1. 归并排序、快速排序
2. 合并K个有序链表
3. 最大子数组和
4. 计算逆序对
5. 大整数乘法

#### 经典例题
1. [合并K个升序链表](https://leetcode.com/problems/merge-k-sorted-lists/)
2. [不同的二叉搜索树](https://leetcode.com/problems/unique-binary-search-trees/)
3. [不同的二叉搜索树 II](https://leetcode.com/problems/unique-binary-search-trees-ii/)
4. [为运算表达式设计优先级](https://leetcode.com/problems/different-ways-to-add-parentheses/)
5. [数组中的逆序对](https://leetcode.com/problems/shu-zu-zhong-de-ni-xu-dui-lcof/)
6. [翻转对](https://leetcode.com/problems/reverse-pairs/)
7. [区间和的个数](https://leetcode.com/problems/count-of-range-sum/)
8. [戳气球](https://leetcode.com/problems/burst-balloons/)

#### 代码模板

```java
// 分治法通用模板
public Result divideAndConquer(Problem problem) {
    // 基本情况
    if (problem.size() <= threshold) {
        return solveDirectly(problem);
    }
    
    // 分解问题
    Problem[] subProblems = split(problem);
    
    // 递归求解子问题
    Result[] subResults = new Result[subProblems.length];
    for (int i = 0; i < subProblems.length; i++) {
        subResults[i] = divideAndConquer(subProblems[i]);
    }
    
    // 合并结果
    return combine(subResults);
}

// 合并K个升序链表
public ListNode mergeKLists(ListNode[] lists) {
    if (lists == null || lists.length == 0) return null;
    return merge(lists, 0, lists.length - 1);
}

private ListNode merge(ListNode[] lists, int left, int right) {
    if (left == right) return lists[left];
    if (left > right) return null;
    
    int mid = left + (right - left) / 2;
    ListNode l1 = merge(lists, left, mid);
    ListNode l2 = merge(lists, mid + 1, right);
    
    return mergeTwoLists(l1, l2);
}

private ListNode mergeTwoLists(ListNode l1, ListNode l2) {
    if (l1 == null) return l2;
    if (l2 == null) return l1;
    
    if (l1.val < l2.val) {
        l1.next = mergeTwoLists(l1.next, l2);
        return l1;
    } else {
        l2.next = mergeTwoLists(l1, l2.next);
        return l2;
    }
}
```

### 5. 回溯法(Backtracking)

#### 基本思想
通过递归尝试所有可能的解，在搜索过程中如果发现不满足约束条件就回退到上一步，尝试其他分支。

#### 应用场景
1. 全排列、组合问题
2. N皇后问题
3. 解数独
4. 单词搜索
5. 分割回文串

#### 经典例题
1. [全排列](https://leetcode.com/problems/permutations/)
2. [全排列 II](https://leetcode.com/problems/permutations-ii/)
3. [组合](https://leetcode.com/problems/combinations/)
4. [组合总和](https://leetcode.com/problems/combination-sum/)
5. [组合总和 II](https://leetcode.com/problems/combination-sum-ii/)
6. [组合总和 III](https://leetcode.com/problems/combination-sum-iii/)
7. [子集](https://leetcode.com/problems/subsets/)
8. [子集 II](https://leetcode.com/problems/subsets-ii/)
9. [N 皇后](https://leetcode.com/problems/n-queens/)
10. [解数独](https://leetcode.com/problems/sudoku-solver/)

#### 代码模板

```java
// 回溯法通用模板
public void backtrack(路径, 选择列表) {
    if (满足结束条件) {
        result.add(路径);
        return;
    }
    
    for (选择 : 选择列表) {
        做选择;
        backtrack(路径, 选择列表);
        撤销选择;
    }
}

// 全排列
public List<List<Integer>> permute(int[] nums) {
    List<List<Integer>> result = new ArrayList<>();
    List<Integer> track = new ArrayList<>();
    boolean[] used = new boolean[nums.length];
    backtrack(nums, track, used, result);
    return result;
}

private void backtrack(int[] nums, List<Integer> track, boolean[] used, List<List<Integer>> result) {
    // 结束条件
    if (track.size() == nums.length) {
        result.add(new ArrayList<>(track));
        return;
    }
    
    for (int i = 0; i < nums.length; i++) {
        // 排除不合法的选择
        if (used[i]) continue;
        
        // 做选择
        track.add(nums[i]);
        used[i] = true;
        
        // 进入下一层决策树
        backtrack(nums, track, used, result);
        
        // 撤销选择
        track.remove(track.size() - 1);
        used[i] = false;
    }
}

// N皇后
public List<List<String>> solveNQueens(int n) {
    List<List<String>> result = new ArrayList<>();
    char[][] board = new char[n][n];
    
    // 初始化棋盘
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            board[i][j] = '.';
        }
    }
    
    backtrack(board, 0, result);
    return result;
}

private void backtrack(char[][] board, int row, List<List<String>> result) {
    if (row == board.length) {
        result.add(construct(board));
        return;
    }
    
    for (int col = 0; col < board.length; col++) {
        if (!isValid(board, row, col)) continue;
        
        board[row][col] = 'Q';
        backtrack(board, row + 1, result);
        board[row][col] = '.';
    }
}

private boolean isValid(char[][] board, int row, int col) {
    // 检查列是否有冲突
    for (int i = 0; i < row; i++) {
        if (board[i][col] == 'Q') return false;
    }
    
    // 检查右上方是否有冲突
    for (int i = row - 1, j = col + 1; i >= 0 && j < board.length; i--, j++) {
        if (board[i][j] == 'Q') return false;
    }
    
    // 检查左上方是否有冲突
    for (int i = row - 1, j = col - 1; i >= 0 && j >= 0; i--, j--) {
        if (board[i][j] == 'Q') return false;
    }
    
    return true;
}

private List<String> construct(char[][] board) {
    List<String> result = new ArrayList<>();
    for (int i = 0; i < board.length; i++) {
        result.add(new String(board[i]));
    }
    return result;
}
```

### 6. 动态规划(Dynamic Programming)

#### 基本思想
将复杂问题分解为简单的子问题，通过保存子问题的解来避免重复计算，从而提高效率。

#### 应用场景
1. 最优子结构问题
2. 重叠子问题
3. 计数问题
4. 存在性问题
5. 最值问题

#### 经典例题
1. [斐波那契数](https://leetcode.com/problems/fibonacci-number/)
2. [爬楼梯](https://leetcode.com/problems/climbing-stairs/)
3. [使用最小花费爬楼梯](https://leetcode.com/problems/min-cost-climbing-stairs/)
4. [不同路径](https://leetcode.com/problems/unique-paths/)
5. [不同路径 II](https://leetcode.com/problems/unique-paths-ii/)
6. [最小路径和](https://leetcode.com/problems/minimum-path-sum/)
7. [三角形最小路径和](https://leetcode.com/problems/triangle/)
8. [最大子数组和](https://leetcode.com/problems/maximum-subarray/)
9. [乘积最大子数组](https://leetcode.com/problems/maximum-product-subarray/)
10. [打家劫舍](https://leetcode.com/problems/house-robber/)

#### 代码模板

```java
// 动态规划通用模板
public int dp(Problem problem) {
    // 定义dp数组/变量
    int[] dp = new int[n+1];
    
    // 初始化base case
    dp[0] = base_case_0;
    dp[1] = base_case_1;
    
    // 状态转移方程
    for (int i = 2; i <= n; i++) {
        dp[i] = dp[i-1] + dp[i-2]; // 示例状态转移方程
    }
    
    return dp[n];
}

// 爬楼梯
public int climbStairs(int n) {
    if (n <= 2) return n;
    
    int[] dp = new int[n+1];
    dp[1] = 1;
    dp[2] = 2;
    
    for (int i = 3; i <= n; i++) {
        dp[i] = dp[i-1] + dp[i-2];
    }
    
    return dp[n];
}

// 最大子数组和
public int maxSubArray(int[] nums) {
    int[] dp = new int[nums.length];
    dp[0] = nums[0];
    int max = dp[0];
    
    for (int i = 1; i < nums.length; i++) {
        dp[i] = Math.max(nums[i], dp[i-1] + nums[i]);
        max = Math.max(max, dp[i]);
    }
    
    return max;
}

// 不同路径
public int uniquePaths(int m, int n) {
    int[][] dp = new int[m][n];
    
    // 初始化第一行和第一列
    for (int i = 0; i < m; i++) dp[i][0] = 1;
    for (int j = 0; j < n; j++) dp[0][j] = 1;
    
    // 状态转移
    for (int i = 1; i < m; i++) {
        for (int j = 1; j < n; j++) {
            dp[i][j] = dp[i-1][j] + dp[i][j-1];
        }
    }
    
    return dp[m-1][n-1];
}
```

### 7. 贪心算法(Greedy Algorithm)

#### 基本思想
在每一步选择中都采取在当前状态下最好或最优的选择，从而希望导致结果是最好或最优的算法。

#### 应用场景
1. 活动选择问题
2. 分数背包问题
3. 最小生成树(Kruskal, Prim算法)
4. 单源最短路径(Dijkstra算法)
5. Huffman编码

#### 经典例题
1. [分发饼干](https://leetcode.com/problems/assign-cookies/)
2. [摆动序列](https://leetcode.com/problems/wiggle-subsequence/)
3. [最长连续递增序列](https://leetcode.com/problems/longest-continuous-increasing-subsequence/)
4. [买卖股票的最佳时机 II](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-ii/)
5. [跳跃游戏](https://leetcode.com/problems/jump-game/)
6. [跳跃游戏 II](https://leetcode.com/problems/jump-game-ii/)
7. [加油站](https://leetcode.com/problems/gas-station/)
8. [分发糖果](https://leetcode.com/problems/candy/)
9. [根据身高重建队列](https://leetcode.com/problems/queue-reconstruction-by-height/)
10. [用最少数量的箭引爆气球](https://leetcode.com/problems/minimum-number-of-arrows-to-burst-balloons/)

#### 代码模板

```java
// 贪心算法通用模板
public int greedy(Problem problem) {
    // 对数据进行排序或其他预处理
    
    int result = 0;
    
    for (int i = 0; i < data.length; i++) {
        // 根据贪心策略做出选择
        if (满足贪心条件) {
            result++;
            // 更新状态
        }
    }
    
    return result;
}

// 分发饼干
public int findContentChildren(int[] g, int[] s) {
    Arrays.sort(g); // 孩子胃口值排序
    Arrays.sort(s); // 饼干尺寸排序
    
    int child = 0;
    
    for (int cookie = 0; child < g.length && cookie < s.length; cookie++) {
        if (s[cookie] >= g[child]) {
            child++; // 满足一个孩子
        }
    }
    
    return child;
}

// 跳跃游戏
public boolean canJump(int[] nums) {
    int maxReach = 0;
    
    for (int i = 0; i < nums.length; i++) {
        if (i > maxReach) return false; // 无法到达当前位置
        maxReach = Math.max(maxReach, i + nums[i]); // 更新最远可达位置
    }
    
    return true;
}

// 买卖股票的最佳时机 II
public int maxProfit(int[] prices) {
    int profit = 0;
    
    for (int i = 1; i < prices.length; i++) {
        if (prices[i] > prices[i-1]) {
            profit += prices[i] - prices[i-1];
        }
    }
    
    return profit;
}
```

## 📚 总结

掌握这些算法技巧对于解决LeetCode问题非常重要。在实际应用中，一个问题可能需要结合多种技巧来解决。建议：

1. **理解每种技巧的核心思想和适用场景**
2. **熟练掌握各种技巧的经典例题**
3. **学会识别问题属于哪种技巧范畴**
4. **多练习，培养算法直觉**

在下一章节中，我们将深入探讨动态规划专题，这是LeetCode中最重要也是最难掌握的技巧之一。