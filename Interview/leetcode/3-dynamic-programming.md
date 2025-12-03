# LeetCode动态规划专题

## 📚 简介

动态规划(Dynamic Programming, DP)是解决具有重叠子问题和最优子结构性质的问题的一种算法设计技术。它将复杂问题分解为简单的子问题，并通过保存子问题的解来避免重复计算，从而提高效率。

## 🎯 学习目标

- 理解动态规划的基本概念和核心思想
- 掌握动态规划问题的识别方法
- 熟练运用动态规划解决各类问题
- 培养动态规划思维，提高算法设计能力

## 🔍 动态规划核心要素

### 1. 最优子结构(Optimal Substructure)
问题的最优解包含子问题的最优解。

### 2. 重叠子问题(Overlapping Subproblems)
在求解过程中，同样的子问题会被多次求解。

### 3. 状态转移方程(State Transition Equation)
描述状态之间关系的数学表达式。

### 4. 边界条件(Boundary Conditions)
递推的初始条件，通常是问题的最基本情况。

## 🧠 动态规划设计步骤

1. **确定DP状态**：明确dp[i]或dp[i][j]表示什么含义
2. **确定状态转移方程**：找出dp[i]与之前状态的关系
3. **初始化边界条件**：确定初始值
4. **确定遍历顺序**：保证计算dp[i]时所需的dp值已经计算过
5. **返回最终结果**：确定最终的答案在哪个dp状态中

## 🗂️ 动态规划分类

### 1. 线性DP

线性DP是最基础的动态规划类型，状态通常是一维或二维的，按照线性顺序进行状态转移。

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
11. [打家劫舍 II](https://leetcode.com/problems/house-robber-ii/)
12. [删除并获得点数](https://leetcode.com/problems/delete-and-earn/)

#### 代码模板

```java
// 斐波那契数
public int fib(int n) {
    if (n <= 1) return n;
    
    int[] dp = new int[n + 1];
    dp[0] = 0;
    dp[1] = 1;
    
    for (int i = 2; i <= n; i++) {
        dp[i] = dp[i - 1] + dp[i - 2];
    }
    
    return dp[n];
}

// 爬楼梯
public int climbStairs(int n) {
    if (n <= 2) return n;
    
    int[] dp = new int[n + 1];
    dp[1] = 1;
    dp[2] = 2;
    
    for (int i = 3; i <= n; i++) {
        dp[i] = dp[i - 1] + dp[i - 2];
    }
    
    return dp[n];
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
            dp[i][j] = dp[i - 1][j] + dp[i][j - 1];
        }
    }
    
    return dp[m - 1][n - 1];
}

// 最大子数组和 - Kadane算法
public int maxSubArray(int[] nums) {
    int[] dp = new int[nums.length];
    dp[0] = nums[0];
    int max = dp[0];
    
    for (int i = 1; i < nums.length; i++) {
        dp[i] = Math.max(nums[i], dp[i - 1] + nums[i]);
        max = Math.max(max, dp[i]);
    }
    
    return max;
}

// 打家劫舍
public int rob(int[] nums) {
    if (nums.length == 0) return 0;
    if (nums.length == 1) return nums[0];
    
    int[] dp = new int[nums.length];
    dp[0] = nums[0];
    dp[1] = Math.max(nums[0], nums[1]);
    
    for (int i = 2; i < nums.length; i++) {
        dp[i] = Math.max(dp[i - 1], dp[i - 2] + nums[i]);
    }
    
    return dp[nums.length - 1];
}
```

### 2. 区间DP

区间DP的状态通常表示为dp[i][j]，表示区间[i,j]上的最优解。

#### 经典例题
1. [戳气球](https://leetcode.com/problems/burst-balloons/)
2. [矩阵链乘](https://leetcode.com/problems/minimum-score-triangulation-of-polygon/)
3. [合并石头的最低成本](https://leetcode.com/problems/minimum-cost-to-merge-stones/)
4. [不同的子序列](https://leetcode.com/problems/distinct-subsequences/)
5. [两个字符串的删除操作](https://leetcode.com/problems/delete-operation-for-two-strings/)
6. [编辑距离](https://leetcode.com/problems/edit-distance/)
7. [最长公共子序列](https://leetcode.com/problems/longest-common-subsequence/)
8. [交错字符串](https://leetcode.com/problems/interleaving-string/)
9. [恢复数组](https://leetcode.com/problems/restore-the-array/)
10. [奇怪的打印机](https://leetcode.com/problems/strange-printer/)

#### 代码模板

```java
// 最长公共子序列
public int longestCommonSubsequence(String text1, String text2) {
    int m = text1.length(), n = text2.length();
    int[][] dp = new int[m + 1][n + 1];
    
    for (int i = 1; i <= m; i++) {
        for (int j = 1; j <= n; j++) {
            if (text1.charAt(i - 1) == text2.charAt(j - 1)) {
                dp[i][j] = dp[i - 1][j - 1] + 1;
            } else {
                dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
            }
        }
    }
    
    return dp[m][n];
}

// 编辑距离
public int minDistance(String word1, String word2) {
    int m = word1.length(), n = word2.length();
    int[][] dp = new int[m + 1][n + 1];
    
    // 初始化边界
    for (int i = 0; i <= m; i++) dp[i][0] = i;
    for (int j = 0; j <= n; j++) dp[0][j] = j;
    
    for (int i = 1; i <= m; i++) {
        for (int j = 1; j <= n; j++) {
            if (word1.charAt(i - 1) == word2.charAt(j - 1)) {
                dp[i][j] = dp[i - 1][j - 1];
            } else {
                dp[i][j] = Math.min(Math.min(dp[i - 1][j], dp[i][j - 1]), dp[i - 1][j - 1]) + 1;
            }
        }
    }
    
    return dp[m][n];
}
```

### 3. 背包DP

背包问题是动态规划的经典应用，包括0-1背包、完全背包、多重背包等多种变体。

#### 经典例题
1. [分割等和子集](https://leetcode.com/problems/partition-equal-subset-sum/)
2. [最后一块石头的重量 II](https://leetcode.com/problems/last-stone-weight-ii/)
3. [目标和](https://leetcode.com/problems/target-sum/)
4. [一和零](https://leetcode.com/problems/ones-and-zeroes/)
5. [零钱兑换](https://leetcode.com/problems/coin-change/)
6. [零钱兑换 II](https://leetcode.com/problems/coin-change-2/)
7. [组合总和 Ⅳ](https://leetcode.com/problems/combination-sum-iv/)
8. [掷骰子等于目标和的方法数](https://leetcode.com/problems/number-of-dice-rolls-with-target-sum/)
9. [盈利计划](https://leetcode.com/problems/profitable-schemes/)

#### 代码模板

```java
// 0-1背包问题模板
public boolean canPartition(int[] nums) {
    int sum = 0;
    for (int num : nums) sum += num;
    
    if (sum % 2 != 0) return false;
    
    int target = sum / 2;
    boolean[] dp = new boolean[target + 1];
    dp[0] = true;
    
    for (int num : nums) {
        for (int j = target; j >= num; j--) {
            dp[j] = dp[j] || dp[j - num];
        }
    }
    
    return dp[target];
}

// 完全背包问题模板
public int coinChange(int[] coins, int amount) {
    int[] dp = new int[amount + 1];
    Arrays.fill(dp, amount + 1);
    dp[0] = 0;
    
    for (int coin : coins) {
        for (int j = coin; j <= amount; j++) {
            dp[j] = Math.min(dp[j], dp[j - coin] + 1);
        }
    }
    
    return dp[amount] > amount ? -1 : dp[amount];
}

// 零钱兑换 II - 求方案数
public int change(int amount, int[] coins) {
    int[] dp = new int[amount + 1];
    dp[0] = 1;
    
    for (int coin : coins) {
        for (int j = coin; j <= amount; j++) {
            dp[j] += dp[j - coin];
        }
    }
    
    return dp[amount];
}
```

### 4. 状态压缩DP

当DP的状态维度较高但每一维的取值范围较小时，可以用二进制数来表示状态，从而降低空间复杂度。

#### 经典例题
1. [青蛙过河](https://leetcode.com/problems/frog-jump/)
2. [最大的幻方](https://leetcode.com/problems/largest-magic-square/)
3. [最大兼容性评分和](https://leetcode.com/problems/maximum-compatibility-score-sum/)
4. [旅行商问题](https://leetcode.com/problems/find-the-shortest-superstring/)
5. [访问所有节点的最短路径](https://leetcode.com/problems/shortest-path-visiting-all-nodes/)

#### 代码模板

```java
// 状态压缩DP通用模板
public int dpWithBitmask(Problem problem) {
    int n = problem.size();
    int[][] dp = new int[1 << n][n]; // 状态压缩
    
    // 初始化
    for (int i = 0; i < (1 << n); i++) {
        Arrays.fill(dp[i], INF);
    }
    
    // 设置初始状态
    for (int i = 0; i < n; i++) {
        dp[1 << i][i] = 0;
    }
    
    // 状态转移
    for (int mask = 0; mask < (1 << n); mask++) {
        for (int u = 0; u < n; u++) {
            if ((mask & (1 << u)) == 0) continue;
            
            for (int v = 0; v < n; v++) {
                if ((mask & (1 << v)) != 0) continue;
                
                int newMask = mask | (1 << v);
                dp[newMask][v] = Math.min(dp[newMask][v], dp[mask][u] + cost[u][v]);
            }
        }
    }
    
    // 返回结果
    int result = INF;
    for (int i = 0; i < n; i++) {
        result = Math.min(result, dp[(1 << n) - 1][i]);
    }
    
    return result;
}
```

### 5. 树形DP

树形DP是在树结构上进行的动态规划，状态通常表示以某个节点为根的子树的信息。

#### 经典例题
1. [没有上司的舞会](https://leetcode.com/problems/house-robber-iii/)
2. [二叉树中的最大路径和](https://leetcode.com/problems/binary-tree-maximum-path-sum/)
3. [二叉树的直径](https://leetcode.com/problems/diameter-of-binary-tree/)
4. [二叉树中最长的同值路径](https://leetcode.com/problems/longest-univalue-path/)
5. [监控二叉树](https://leetcode.com/problems/binary-tree-cameras/)
6. [最大BST子树](https://leetcode.com/problems/largest-bst-subtree/)

#### 代码模板

```java
// 树形DP通用模板
public int treeDP(TreeNode root) {
    int[] result = dfs(root);
    return Math.max(result[0], result[1]); // 返回选或不选根节点的最大值
}

// 返回值: [0]表示不选当前节点的最大值, [1]表示选当前节点的最大值
private int[] dfs(TreeNode node) {
    if (node == null) return new int[]{0, 0};
    
    int[] left = dfs(node.left);
    int[] right = dfs(node.right);
    
    // 不选当前节点: 左右子节点可选可不选，取较大值
    int notSelect = Math.max(left[0], left[1]) + Math.max(right[0], right[1]);
    
    // 选当前节点: 左右子节点都不能选
    int select = node.val + left[0] + right[0];
    
    return new int[]{notSelect, select};
}

// 二叉树中的最大路径和
public int maxPathSum(TreeNode root) {
    int[] maxSum = {Integer.MIN_VALUE};
    maxPathSumHelper(root, maxSum);
    return maxSum[0];
}

private int maxPathSumHelper(TreeNode node, int[] maxSum) {
    if (node == null) return 0;
    
    // 递归计算左右子树的最大贡献值
    int leftGain = Math.max(maxPathSumHelper(node.left, maxSum), 0);
    int rightGain = Math.max(maxPathSumHelper(node.right, maxSum), 0);
    
    // 节点的最大路径和
    int priceNewPath = node.val + leftGain + rightGain;
    
    // 更新全局最大值
    maxSum[0] = Math.max(maxSum[0], priceNewPath);
    
    // 返回节点的最大贡献值
    return node.val + Math.max(leftGain, rightGain);
}
```

### 6. 数位DP

数位DP是用来解决与数字相关的问题，通过对数字的每一位进行处理来求解。

#### 经典例题
1. [数字 1 的个数](https://leetcode.com/problems/number-of-digit-one/)
2. [不含连续1的非负整数](https://leetcode.com/problems/non-negative-integers-without-consecutive-ones/)
3. [第N个数字](https://leetcode.com/problems/nth-digit/)
4. [最大为 N 的数字组合](https://leetcode.com/problems/numbers-at-most-n-given-digit-set/)

#### 代码模板

```java
// 数位DP通用模板
public int digitDP(int n) {
    String sn = String.valueOf(n);
    int len = sn.length();
    int[][] memo = new int[len][2]; // 记忆化数组
    
    for (int i = 0; i < len; i++) {
        Arrays.fill(memo[i], -1);
    }
    
    return dfs(sn, 0, 0, true, memo);
}

private int dfs(String s, int pos, int mask, boolean limit, int[][] memo) {
    if (pos == s.length()) return 1;
    
    if (!limit && memo[pos][mask] != -1) {
        return memo[pos][mask];
    }
    
    int up = limit ? s.charAt(pos) - '0' : 9;
    int res = 0;
    
    for (int i = 0; i <= up; i++) {
        // 根据具体问题添加约束条件
        if (/* 满足约束条件 */) {
            res += dfs(s, pos + 1, /* 更新mask */, limit && i == up, memo);
        }
    }
    
    if (!limit) memo[pos][mask] = res;
    return res;
}
```

## 🧩 动态规划优化技巧

### 1. 滚动数组优化
当状态转移只依赖于前几轮的状态时，可以使用滚动数组来节省空间。

```java
// 使用滚动数组优化空间复杂度
public int climbStairsOptimized(int n) {
    if (n <= 2) return n;
    
    int prev2 = 1, prev1 = 2;
    for (int i = 3; i <= n; i++) {
        int curr = prev1 + prev2;
        prev2 = prev1;
        prev1 = curr;
    }
    
    return prev1;
}
```

### 2. 记忆化搜索
将递归与动态规划结合，避免重复计算。

```java
// 记忆化搜索模板
public int memoizationSearch(int n) {
    int[] memo = new int[n + 1];
    Arrays.fill(memo, -1);
    return dfs(n, memo);
}

private int dfs(int n, int[] memo) {
    if (n <= 1) return n;
    
    if (memo[n] != -1) return memo[n];
    
    memo[n] = dfs(n - 1, memo) + dfs(n - 2, memo);
    return memo[n];
}
```

## 📚 总结

动态规划是LeetCode中最重要也是最具挑战性的算法技巧之一。掌握动态规划需要大量的练习和积累。建议：

1. **理解动态规划的核心思想**：最优子结构和重叠子问题
2. **熟练掌握各类DP问题的解题模板**
3. **学会识别问题属于哪种DP类型**
4. **多做练习，培养DP思维**
5. **注意边界条件和初始化**

在下一章节中，我们将探讨图论算法专题，这是另一个重要的算法领域。