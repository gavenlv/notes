import java.util.*;

/**
 * 第十一章：算法设计与分析基础
 * 完整可运行的代码示例
 */
public class Chapter11Example {
    
    /**
     * 复杂度分析示例
     */
    static class ComplexityExamples {
        // O(1) 常数时间复杂度
        public int getFirstElement(int[] array) {
            return array[0]; // 不管数组多大，都只需要一次操作
        }
        
        // O(n) 线性时间复杂度
        public int sumArray(int[] array) {
            int sum = 0;
            for (int i = 0; i < array.length; i++) {
                sum += array[i]; // 需要遍历整个数组
            }
            return sum;
        }
        
        // O(n²) 平方时间复杂度
        public void printPairs(int[] array) {
            for (int i = 0; i < array.length; i++) {
                for (int j = 0; j < array.length; j++) {
                    System.out.println(array[i] + "," + array[j]);
                }
            }
        }
        
        // O(log n) 对数时间复杂度
        public boolean binarySearch(int[] array, int target) {
            int left = 0;
            int right = array.length - 1;
            
            while (left <= right) {
                int mid = left + (right - left) / 2;
                if (array[mid] == target) {
                    return true;
                } else if (array[mid] < target) {
                    left = mid + 1;
                } else {
                    right = mid - 1;
                }
            }
            return false;
        }
    }
    
    /**
     * 分治法示例：归并排序
     */
    static class MergeSort {
        public void mergeSort(int[] array, int left, int right) {
            if (left < right) {
                int mid = left + (right - left) / 2;
                
                // 分解
                mergeSort(array, left, mid);
                mergeSort(array, mid + 1, right);
                
                // 合并
                merge(array, left, mid, right);
            }
        }
        
        private void merge(int[] array, int left, int mid, int right) {
            // 创建临时数组
            int[] temp = new int[right - left + 1];
            int i = left, j = mid + 1, k = 0;
            
            // 合并两个有序数组
            while (i <= mid && j <= right) {
                if (array[i] <= array[j]) {
                    temp[k++] = array[i++];
                } else {
                    temp[k++] = array[j++];
                }
            }
            
            // 复制剩余元素
            while (i <= mid) {
                temp[k++] = array[i++];
            }
            while (j <= right) {
                temp[k++] = array[j++];
            }
            
            // 将临时数组复制回原数组
            for (int p = 0; p < temp.length; p++) {
                array[left + p] = temp[p];
            }
        }
    }
    
    /**
     * 贪心算法示例：活动选择问题
     */
    static class ActivitySelection {
        static class Activity {
            int start, finish;
            
            public Activity(int start, int finish) {
                this.start = start;
                this.finish = finish;
            }
        }
        
        public static List<Activity> selectActivities(Activity[] activities) {
            // 按结束时间排序
            Arrays.sort(activities, (a, b) -> a.finish - b.finish);
            
            List<Activity> selected = new ArrayList<>();
            int i = 0;
            selected.add(activities[i]);
            
            // 贪心选择：总是选择下一个与前一个兼容且结束时间最早的活动
            for (int j = 1; j < activities.length; j++) {
                if (activities[j].start >= activities[i].finish) {
                    selected.add(activities[j]);
                    i = j;
                }
            }
            
            return selected;
        }
    }
    
    /**
     * 动态规划示例：斐波那契数列
     */
    static class FibonacciDP {
        // 自顶向下（记忆化搜索）
        public static int fibonacciMemo(int n, int[] memo) {
            if (n <= 1) return n;
            if (memo[n] != 0) return memo[n];
            
            memo[n] = fibonacciMemo(n - 1, memo) + fibonacciMemo(n - 2, memo);
            return memo[n];
        }
        
        // 自底向上（表格法）
        public static int fibonacciTabulation(int n) {
            if (n <= 1) return n;
            
            int[] dp = new int[n + 1];
            dp[0] = 0;
            dp[1] = 1;
            
            for (int i = 2; i <= n; i++) {
                dp[i] = dp[i - 1] + dp[i - 2];
            }
            
            return dp[n];
        }
    }
    
    /**
     * 动态规划示例：0-1背包问题
     */
    static class KnapsackProblem {
        public static int knapsack(int W, int[] weights, int[] values, int n) {
            // dp[i][w] 表示前i个物品在重量限制为w时的最大价值
            int[][] dp = new int[n + 1][W + 1];
            
            // 填充dp表
            for (int i = 1; i <= n; i++) {
                for (int w = 1; w <= W; w++) {
                    // 如果当前物品重量超过背包容量，则不能放入
                    if (weights[i - 1] > w) {
                        dp[i][w] = dp[i - 1][w];
                    } else {
                        // 比较放入和不放入当前物品的价值
                        dp[i][w] = Math.max(
                            dp[i - 1][w],  // 不放入
                            dp[i - 1][w - weights[i - 1]] + values[i - 1]  // 放入
                        );
                    }
                }
            }
            
            return dp[n][W];
        }
    }
    
    /**
     * 回溯法示例：N皇后问题
     */
    static class NQueens {
        private int[] queens;  // queens[i] 表示第i行皇后所在的列
        private List<int[]> solutions; // 解的集合
        
        public NQueens(int n) {
            queens = new int[n];
            solutions = new ArrayList<>();
        }
        
        // 检查在(row, col)放置皇后是否合法
        private boolean isValid(int row, int col) {
            for (int i = 0; i < row; i++) {
                // 检查列冲突和对角线冲突
                if (queens[i] == col || 
                    Math.abs(queens[i] - col) == Math.abs(i - row)) {
                    return false;
                }
            }
            return true;
        }
        
        // 回溯求解
        public void solve(int row) {
            if (row == queens.length) {
                // 找到一个解，保存副本
                solutions.add(Arrays.copyOf(queens, queens.length));
                return;
            }
            
            for (int col = 0; col < queens.length; col++) {
                if (isValid(row, col)) {
                    queens[row] = col;
                    solve(row + 1);
                    // 回溯：不需要显式重置，因为下次循环会覆盖
                }
            }
        }
        
        // 获取所有解
        public List<int[]> getSolutions() {
            return solutions;
        }
        
        // 打印解决方案
        public void printSolutions() {
            System.out.println("总共找到 " + solutions.size() + " 个解决方案");
            for (int s = 0; s < solutions.size(); s++) {
                System.out.println("解决方案 #" + (s + 1) + ":");
                int[] solution = solutions.get(s);
                for (int i = 0; i < solution.length; i++) {
                    for (int j = 0; j < solution.length; j++) {
                        if (solution[i] == j) {
                            System.out.print("Q ");
                        } else {
                            System.out.print(". ");
                        }
                    }
                    System.out.println();
                }
                System.out.println();
            }
        }
    }
    
    /**
     * 循环不变式示例：选择排序
     */
    static class SelectionSortProof {
        /*
         * 循环不变式：在第i次迭代开始时，数组的前i个元素包含了数组中最小的i个元素，
         * 并且它们已经按升序排列。
         * 
         * 初始化：i=0时，前0个元素为空，不变式显然成立。
         * 保持：第i次迭代中，我们找到剩余元素中的最小值并将其放到位置i，
         *      因此前i+1个元素包含了最小的i+1个元素并且已排序。
         * 终止：循环结束时i=n，整个数组已排序。
         */
        public static void selectionSort(int[] array) {
            int n = array.length;
            
            for (int i = 0; i < n - 1; i++) {
                // 循环不变式：array[0..i-1]已排序且包含最小的i个元素
                
                // 找到未排序部分的最小元素
                int minIndex = i;
                for (int j = i + 1; j < n; j++) {
                    if (array[j] < array[minIndex]) {
                        minIndex = j;
                    }
                }
                
                // 交换元素
                int temp = array[minIndex];
                array[minIndex] = array[i];
                array[i] = temp;
                
                // 循环结束后，array[0..i]已排序且包含最小的i+1个元素
            }
        }
    }
    
    /**
     * 算法性能测试工具类
     */
    static class AlgorithmPerformanceTest {
        /**
         * 测试排序算法性能
         */
        public static void testSortingAlgorithms() {
            System.out.println("=== 排序算法性能测试 ===");
            
            // 生成测试数据
            int[] sizes = {1000, 5000, 10000};
            for (int size : sizes) {
                int[] data = generateRandomArray(size);
                
                // 测试归并排序
                int[] mergeSortData = Arrays.copyOf(data, data.length);
                long startTime = System.nanoTime();
                MergeSort mergeSort = new MergeSort();
                mergeSort.mergeSort(mergeSortData, 0, mergeSortData.length - 1);
                long endTime = System.nanoTime();
                System.out.printf("归并排序 (%d元素): %.2f ms%n", size, (endTime - startTime) / 1_000_000.0);
                
                // 测试选择排序
                int[] selectionSortData = Arrays.copyOf(data, data.length);
                startTime = System.nanoTime();
                SelectionSortProof.selectionSort(selectionSortData);
                endTime = System.nanoTime();
                System.out.printf("选择排序 (%d元素): %.2f ms%n", size, (endTime - startTime) / 1_000_000.0);
            }
        }
        
        /**
         * 测试动态规划算法性能
         */
        public static void testDynamicProgramming() {
            System.out.println("\n=== 动态规划算法性能测试 ===");
            
            // 测试斐波那契数列
            int n = 40;
            
            // 测试记忆化搜索
            long startTime = System.nanoTime();
            int[] memo = new int[n + 1];
            int result1 = FibonacciDP.fibonacciMemo(n, memo);
            long endTime = System.nanoTime();
            System.out.printf("斐波那契数列第%d项（记忆化搜索）: %d, 耗时: %.2f ms%n", 
                n, result1, (endTime - startTime) / 1_000_000.0);
            
            // 测试表格法
            startTime = System.nanoTime();
            int result2 = FibonacciDP.fibonacciTabulation(n);
            endTime = System.nanoTime();
            System.out.printf("斐波那契数列第%d项（表格法）: %d, 耗时: %.2f ms%n", 
                n, result2, (endTime - startTime) / 1_000_000.0);
        }
        
        /**
         * 生成随机数组
         */
        private static int[] generateRandomArray(int size) {
            Random random = new Random();
            int[] array = new int[size];
            for (int i = 0; i < size; i++) {
                array[i] = random.nextInt(1000);
            }
            return array;
        }
    }
    
    /**
     * 主方法 - 演示各种算法设计技巧
     */
    public static void main(String[] args) {
        System.out.println("第十一章：算法设计与分析基础");
        System.out.println("=========================\n");
        
        // 1. 复杂度分析示例
        System.out.println("1. 复杂度分析示例:");
        ComplexityExamples complexity = new ComplexityExamples();
        int[] array = {1, 2, 3, 4, 5};
        
        System.out.printf("获取数组第一个元素: %d (O(1))%n", complexity.getFirstElement(array));
        System.out.printf("数组元素求和: %d (O(n))%n", complexity.sumArray(array));
        System.out.printf("二分查找元素3: %b (O(log n))%n", complexity.binarySearch(array, 3));
        
        // 2. 分治法示例：归并排序
        System.out.println("\n2. 分治法示例 - 归并排序:");
        int[] unsortedArray = {64, 34, 25, 12, 22, 11, 90};
        System.out.printf("排序前: %s%n", Arrays.toString(unsortedArray));
        MergeSort mergeSort = new MergeSort();
        mergeSort.mergeSort(unsortedArray, 0, unsortedArray.length - 1);
        System.out.printf("排序后: %s%n", Arrays.toString(unsortedArray));
        
        // 3. 贪心算法示例：活动选择问题
        System.out.println("\n3. 贪心算法示例 - 活动选择问题:");
        ActivitySelection.Activity[] activities = {
            new ActivitySelection.Activity(1, 4),
            new ActivitySelection.Activity(3, 5),
            new ActivitySelection.Activity(0, 6),
            new ActivitySelection.Activity(5, 7),
            new ActivitySelection.Activity(3, 9),
            new ActivitySelection.Activity(5, 9),
            new ActivitySelection.Activity(6, 10),
            new ActivitySelection.Activity(8, 11),
            new ActivitySelection.Activity(8, 12),
            new ActivitySelection.Activity(2, 14),
            new ActivitySelection.Activity(12, 16)
        };
        
        List<ActivitySelection.Activity> selected = ActivitySelection.selectActivities(activities);
        System.out.println("选中的活动:");
        for (ActivitySelection.Activity activity : selected) {
            System.out.printf("  (%d, %d)%n", activity.start, activity.finish);
        }
        
        // 4. 动态规划示例：斐波那契数列
        System.out.println("\n4. 动态规划示例 - 斐波那契数列:");
        int n = 10;
        int[] memo = new int[n + 1];
        int fibMemo = FibonacciDP.fibonacciMemo(n, memo);
        int fibTab = FibonacciDP.fibonacciTabulation(n);
        System.out.printf("斐波那契数列第%d项（记忆化搜索）: %d%n", n, fibMemo);
        System.out.printf("斐波那契数列第%d项（表格法）: %d%n", n, fibTab);
        
        // 5. 动态规划示例：0-1背包问题
        System.out.println("\n5. 动态规划示例 - 0-1背包问题:");
        int[] values = {60, 100, 120};
        int[] weights = {10, 20, 30};
        int W = 50;
        int maxValue = KnapsackProblem.knapsack(W, weights, values, values.length);
        System.out.printf("背包容量: %d, 最大价值: %d%n", W, maxValue);
        
        // 6. 回溯法示例：N皇后问题
        System.out.println("\n6. 回溯法示例 - N皇后问题:");
        NQueens nQueens = new NQueens(4);
        nQueens.solve(0);
        nQueens.printSolutions();
        
        // 7. 循环不变式示例：选择排序
        System.out.println("\n7. 循环不变式示例 - 选择排序:");
        int[] unsortedArray2 = {64, 34, 25, 12, 22, 11, 90};
        System.out.printf("排序前: %s%n", Arrays.toString(unsortedArray2));
        SelectionSortProof.selectionSort(unsortedArray2);
        System.out.printf("排序后: %s%n", Arrays.toString(unsortedArray2));
        
        // 8. 算法性能测试
        System.out.println("\n8. 算法性能测试:");
        AlgorithmPerformanceTest.testSortingAlgorithms();
        AlgorithmPerformanceTest.testDynamicProgramming();
    }
}