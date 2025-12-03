import java.util.*;

/**
 * 第九章：查找算法 - 高效检索策略
 * 完整可运行的代码示例
 */
public class Chapter9Example {
    
    /**
     * 顺序查找实现
     */
    static class SequentialSearch {
        /**
         * 顺序查找算法
         * @param arr 待查找的数组
         * @param target 目标值
         * @return 目标值在数组中的索引，未找到返回-1
         */
        public static int sequentialSearch(int[] arr, int target) {
            for (int i = 0; i < arr.length; i++) {
                if (arr[i] == target) {
                    return i;
                }
            }
            return -1;
        }
        
        /**
         * 带哨兵的顺序查找
         * @param arr 待查找的数组
         * @param target 目标值
         * @return 目标值在数组中的索引，未找到返回-1
         */
        public static int sequentialSearchWithSentinel(int[] arr, int target) {
            // 设置哨兵
            int last = arr[arr.length - 1];
            arr[arr.length - 1] = target;
            
            int i = 0;
            while (arr[i] != target) {
                i++;
            }
            
            // 恢复哨兵
            arr[arr.length - 1] = last;
            
            // 判断是否找到
            if (i < arr.length - 1 || last == target) {
                return i;
            }
            return -1;
        }
    }
    
    /**
     * 二分查找实现
     */
    static class BinarySearch {
        /**
         * 二分查找（递归实现）
         * @param arr 有序数组
         * @param target 目标值
         * @param low 起始索引
         * @param high 结束索引
         * @return 目标值在数组中的索引，未找到返回-1
         */
        public static int binarySearchRecursive(int[] arr, int target, int low, int high) {
            if (low > high) {
                return -1;
            }
            
            int mid = low + (high - low) / 2;
            
            if (arr[mid] == target) {
                return mid;
            } else if (arr[mid] > target) {
                return binarySearchRecursive(arr, target, low, mid - 1);
            } else {
                return binarySearchRecursive(arr, target, mid + 1, high);
            }
        }
        
        /**
         * 二分查找（迭代实现）
         * @param arr 有序数组
         * @param target 目标值
         * @return 目标值在数组中的索引，未找到返回-1
         */
        public static int binarySearchIterative(int[] arr, int target) {
            int low = 0;
            int high = arr.length - 1;
            
            while (low <= high) {
                int mid = low + (high - low) / 2;
                
                if (arr[mid] == target) {
                    return mid;
                } else if (arr[mid] > target) {
                    high = mid - 1;
                } else {
                    low = mid + 1;
                }
            }
            
            return -1;
        }
        
        /**
         * 查找第一个等于目标值的元素
         * @param arr 有序数组
         * @param target 目标值
         * @return 第一个等于目标值的元素索引，未找到返回-1
         */
        public static int findFirstEqual(int[] arr, int target) {
            int low = 0;
            int high = arr.length - 1;
            
            while (low <= high) {
                int mid = low + (high - low) / 2;
                
                if (arr[mid] > target) {
                    high = mid - 1;
                } else if (arr[mid] < target) {
                    low = mid + 1;
                } else {
                    // 找到目标值，但需要判断是否是第一个
                    if (mid == 0 || arr[mid - 1] != target) {
                        return mid;
                    }
                    high = mid - 1;
                }
            }
            
            return -1;
        }
        
        /**
         * 查找最后一个等于目标值的元素
         * @param arr 有序数组
         * @param target 目标值
         * @return 最后一个等于目标值的元素索引，未找到返回-1
         */
        public static int findLastEqual(int[] arr, int target) {
            int low = 0;
            int high = arr.length - 1;
            
            while (low <= high) {
                int mid = low + (high - low) / 2;
                
                if (arr[mid] > target) {
                    high = mid - 1;
                } else if (arr[mid] < target) {
                    low = mid + 1;
                } else {
                    // 找到目标值，但需要判断是否是最后一个
                    if (mid == arr.length - 1 || arr[mid + 1] != target) {
                        return mid;
                    }
                    low = mid + 1;
                }
            }
            
            return -1;
        }
    }
    
    /**
     * 插值查找实现
     */
    static class InterpolationSearch {
        /**
         * 插值查找
         * @param arr 有序数组（均匀分布效果最好）
         * @param target 目标值
         * @return 目标值在数组中的索引，未找到返回-1
         */
        public static int interpolationSearch(int[] arr, int target) {
            int low = 0;
            int high = arr.length - 1;
            
            while (low <= high && target >= arr[low] && target <= arr[high]) {
                // 防止除零错误
                if (low == high) {
                    if (arr[low] == target) {
                        return low;
                    }
                    return -1;
                }
                
                // 计算插值位置
                int pos = low + ((target - arr[low]) * (high - low)) / (arr[high] - arr[low]);
                
                if (arr[pos] == target) {
                    return pos;
                } else if (arr[pos] < target) {
                    low = pos + 1;
                } else {
                    high = pos - 1;
                }
            }
            
            return -1;
        }
    }
    
    /**
     * 斐波那契查找实现
     */
    static class FibonacciSearch {
        /**
         * 斐波那契查找
         * @param arr 有序数组
         * @param target 目标值
         * @return 目标值在数组中的索引，未找到返回-1
         */
        public static int fibonacciSearch(int[] arr, int target) {
            int n = arr.length;
            
            // 构造斐波那契数列
            int[] fib = new int[20];
            fib[0] = 0;
            fib[1] = 1;
            for (int i = 2; i < 20; i++) {
                fib[i] = fib[i - 1] + fib[i - 2];
            }
            
            // 找到最小的斐波那契数使得fib[k] >= n
            int k = 0;
            while (fib[k] < n) {
                k++;
            }
            
            // 创建临时数组
            int[] temp = new int[fib[k]];
            System.arraycopy(arr, 0, temp, 0, n);
            // 用最大值填充扩展部分
            for (int i = n; i < fib[k]; i++) {
                temp[i] = arr[n - 1];
            }
            
            int low = 0;
            int high = n - 1;
            
            while (low <= high) {
                int mid = low + fib[k - 1] - 1;
                
                if (temp[mid] > target) {
                    high = mid - 1;
                    k = k - 1;
                } else if (temp[mid] < target) {
                    low = mid + 1;
                    k = k - 2;
                } else {
                    if (mid <= high) {
                        return mid;
                    } else {
                        return high;
                    }
                }
                
                if (k < 2) {
                    break;
                }
            }
            
            return -1;
        }
    }
    
    /**
     * 树表查找实现
     */
    static class TreeSearch {
        // 二叉搜索树节点定义
        static class TreeNode {
            int val;
            TreeNode left;
            TreeNode right;
            
            TreeNode(int val) {
                this.val = val;
            }
        }
        
        /**
         * 二叉搜索树查找
         * @param root 树的根节点
         * @param target 目标值
         * @return 包含目标值的节点，未找到返回null
         */
        public static TreeNode bstSearch(TreeNode root, int target) {
            if (root == null || root.val == target) {
                return root;
            }
            
            if (target < root.val) {
                return bstSearch(root.left, target);
            } else {
                return bstSearch(root.right, target);
            }
        }
        
        /**
         * 二叉搜索树查找（迭代实现）
         * @param root 树的根节点
         * @param target 目标值
         * @return 包含目标值的节点，未找到返回null
         */
        public static TreeNode bstSearchIterative(TreeNode root, int target) {
            TreeNode current = root;
            
            while (current != null) {
                if (target == current.val) {
                    return current;
                } else if (target < current.val) {
                    current = current.left;
                } else {
                    current = current.right;
                }
            }
            
            return null;
        }
    }
    
    /**
     * 分块查找实现
     */
    static class BlockSearch {
        // 索引表项
        static class IndexItem {
            int maxValue;  // 块中的最大值
            int start;     // 块的起始位置
            int end;       // 块的结束位置
            
            IndexItem(int maxValue, int start, int end) {
                this.maxValue = maxValue;
                this.start = start;
                this.end = end;
            }
        }
        
        /**
         * 分块查找
         * @param arr 数据数组
         * @param indices 索引表
         * @param target 目标值
         * @return 目标值在数组中的索引，未找到返回-1
         */
        public static int blockSearch(int[] arr, List<IndexItem> indices, int target) {
            // 在索引表中查找目标值所在的块
            int blockIndex = -1;
            for (int i = 0; i < indices.size(); i++) {
                if (target <= indices.get(i).maxValue) {
                    blockIndex = i;
                    break;
                }
            }
            
            // 如果未找到合适的块，说明目标值不存在
            if (blockIndex == -1) {
                return -1;
            }
            
            // 在对应的块中进行顺序查找
            IndexItem block = indices.get(blockIndex);
            for (int i = block.start; i <= block.end; i++) {
                if (arr[i] == target) {
                    return i;
                }
            }
            
            return -1;
        }
        
        /**
         * 构建索引表
         * @param arr 数据数组
         * @param blockSize 块大小
         * @return 索引表
         */
        public static List<IndexItem> buildIndex(int[] arr, int blockSize) {
            List<IndexItem> indices = new ArrayList<>();
            
            for (int i = 0; i < arr.length; i += blockSize) {
                int end = Math.min(i + blockSize - 1, arr.length - 1);
                int maxValue = arr[i];
                
                // 找到块中的最大值
                for (int j = i + 1; j <= end; j++) {
                    if (arr[j] > maxValue) {
                        maxValue = arr[j];
                    }
                }
                
                indices.add(new IndexItem(maxValue, i, end));
            }
            
            return indices;
        }
    }
    
    /**
     * 哈希查找实现
     */
    static class HashSearch {
        // 链地址法实现哈希表
        static class ChainedHashTable {
            private List<List<Integer>> table;
            private int size;
            private int capacity;
            
            public ChainedHashTable(int capacity) {
                this.capacity = capacity;
                this.size = 0;
                this.table = new ArrayList<>(capacity);
                for (int i = 0; i < capacity; i++) {
                    table.add(new LinkedList<>());
                }
            }
            
            // 哈希函数
            private int hash(int key) {
                return key % capacity;
            }
            
            // 插入元素
            public void insert(int key) {
                int index = hash(key);
                table.get(index).add(key);
                size++;
            }
            
            // 查找元素
            public boolean search(int key) {
                int index = hash(key);
                return table.get(index).contains(key);
            }
            
            // 删除元素
            public boolean delete(int key) {
                int index = hash(key);
                boolean removed = table.get(index).remove(Integer.valueOf(key));
                if (removed) {
                    size--;
                }
                return removed;
            }
            
            public int getSize() {
                return size;
            }
        }
    }
    
    /**
     * 性能测试工具类
     */
    static class SearchPerformanceTest {
        /**
         * 测试顺序查找性能
         */
        public static void testSequentialSearch() {
            System.out.println("=== 顺序查找性能测试 ===");
            int[] sizes = {1000, 10000, 100000};
            
            for (int size : sizes) {
                int[] arr = new int[size];
                for (int i = 0; i < size; i++) {
                    arr[i] = i;
                }
                
                long startTime = System.nanoTime();
                int result = SequentialSearch.sequentialSearch(arr, size / 2);
                long endTime = System.nanoTime();
                
                System.out.printf("数组大小: %d, 查找结果: %d, 耗时: %.2f ms%n", 
                    size, result, (endTime - startTime) / 1_000_000.0);
            }
        }
        
        /**
         * 测试二分查找性能
         */
        public static void testBinarySearch() {
            System.out.println("\n=== 二分查找性能测试 ===");
            int[] sizes = {1000, 10000, 100000, 1000000};
            
            for (int size : sizes) {
                int[] arr = new int[size];
                for (int i = 0; i < size; i++) {
                    arr[i] = i;
                }
                
                long startTime = System.nanoTime();
                int result = BinarySearch.binarySearchIterative(arr, size / 2);
                long endTime = System.nanoTime();
                
                System.out.printf("数组大小: %d, 查找结果: %d, 耗时: %.2f ms%n", 
                    size, result, (endTime - startTime) / 1_000_000.0);
            }
        }
        
        /**
         * 测试哈希查找性能
         */
        public static void testHashSearch() {
            System.out.println("\n=== 哈希查找性能测试 ===");
            int[] sizes = {1000, 10000, 100000, 1000000};
            
            for (int size : sizes) {
                HashSearch.ChainedHashTable hashTable = new HashSearch.ChainedHashTable(size / 10);
                
                // 插入数据
                for (int i = 0; i < size; i++) {
                    hashTable.insert(i);
                }
                
                long startTime = System.nanoTime();
                boolean result = hashTable.search(size / 2);
                long endTime = System.nanoTime();
                
                System.out.printf("数据量: %d, 查找结果: %b, 耗时: %.2f ms%n", 
                    size, result, (endTime - startTime) / 1_000_000.0);
            }
        }
    }
    
    /**
     * 主方法 - 演示各种查找算法的使用
     */
    public static void main(String[] args) {
        System.out.println("第九章：查找算法 - 高效检索策略");
        System.out.println("=====================================\n");
        
        // 1. 顺序查找演示
        System.out.println("1. 顺序查找演示:");
        int[] arr1 = {64, 34, 25, 12, 22, 11, 90};
        int target1 = 22;
        int result1 = SequentialSearch.sequentialSearch(arr1, target1);
        System.out.printf("在数组 %s 中查找 %d 的结果: 索引 %d%n", 
            Arrays.toString(arr1), target1, result1);
        
        // 2. 二分查找演示
        System.out.println("\n2. 二分查找演示:");
        int[] sortedArr = {11, 12, 22, 25, 34, 64, 90};
        int target2 = 25;
        int result2 = BinarySearch.binarySearchIterative(sortedArr, target2);
        System.out.printf("在有序数组 %s 中查找 %d 的结果: 索引 %d%n", 
            Arrays.toString(sortedArr), target2, result2);
        
        // 3. 插值查找演示
        System.out.println("\n3. 插值查找演示:");
        int[] uniformArr = {10, 20, 30, 40, 50, 60, 70, 80, 90, 100};
        int target3 = 70;
        int result3 = InterpolationSearch.interpolationSearch(uniformArr, target3);
        System.out.printf("在均匀分布数组 %s 中查找 %d 的结果: 索引 %d%n", 
            Arrays.toString(uniformArr), target3, result3);
        
        // 4. 斐波那契查找演示
        System.out.println("\n4. 斐波那契查找演示:");
        int[] fibArr = {1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25};
        int target4 = 13;
        int result4 = FibonacciSearch.fibonacciSearch(fibArr, target4);
        System.out.printf("在数组 %s 中查找 %d 的结果: 索引 %d%n", 
            Arrays.toString(fibArr), target4, result4);
        
        // 5. 树表查找演示
        System.out.println("\n5. 树表查找演示:");
        TreeSearch.TreeNode root = new TreeSearch.TreeNode(50);
        root.left = new TreeSearch.TreeNode(30);
        root.right = new TreeSearch.TreeNode(70);
        root.left.left = new TreeSearch.TreeNode(20);
        root.left.right = new TreeSearch.TreeNode(40);
        root.right.left = new TreeSearch.TreeNode(60);
        root.right.right = new TreeSearch.TreeNode(80);
        
        int target5 = 60;
        TreeSearch.TreeNode result5 = TreeSearch.bstSearch(root, target5);
        System.out.printf("在二叉搜索树中查找 %d 的结果: %s%n", 
            target5, result5 != null ? "找到节点 " + result5.val : "未找到");
        
        // 6. 分块查找演示
        System.out.println("\n6. 分块查找演示:");
        int[] blockArr = {1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25};
        List<BlockSearch.IndexItem> indices = BlockSearch.buildIndex(blockArr, 4);
        int target6 = 15;
        int result6 = BlockSearch.blockSearch(blockArr, indices, target6);
        System.out.printf("在数组 %s 中查找 %d 的结果: 索引 %d%n", 
            Arrays.toString(blockArr), target6, result6);
        
        // 7. 哈希查找演示
        System.out.println("\n7. 哈希查找演示:");
        HashSearch.ChainedHashTable hashTable = new HashSearch.ChainedHashTable(10);
        int[] hashData = {15, 25, 35, 45, 55, 65, 75};
        for (int value : hashData) {
            hashTable.insert(value);
        }
        int target7 = 45;
        boolean result7 = hashTable.search(target7);
        System.out.printf("在哈希表中查找 %d 的结果: %b%n", target7, result7);
        
        // 8. 性能测试
        System.out.println("\n8. 查找算法性能测试:");
        SearchPerformanceTest.testSequentialSearch();
        SearchPerformanceTest.testBinarySearch();
        SearchPerformanceTest.testHashSearch();
    }
}