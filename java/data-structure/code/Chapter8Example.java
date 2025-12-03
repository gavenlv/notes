import java.util.*;

/**
 * 第八章：排序算法 - 数据有序化之道
 * 完整可运行的代码示例
 */
public class Chapter8Example {
    
    // 1. 冒泡排序
    static class BubbleSort {
        public static void bubbleSort(int[] arr) {
            int n = arr.length;
            System.out.println("冒泡排序过程:");
            for (int i = 0; i < n - 1; i++) {
                boolean swapped = false;
                System.out.print("  第" + (i + 1) + "轮: ");
                for (int j = 0; j < n - 1 - i; j++) {
                    if (arr[j] > arr[j + 1]) {
                        // 交换元素
                        int temp = arr[j];
                        arr[j] = arr[j + 1];
                        arr[j + 1] = temp;
                        swapped = true;
                        System.out.print("交换(" + arr[j + 1] + "," + arr[j] + ") ");
                    }
                }
                System.out.println(Arrays.toString(arr));
                if (!swapped) {
                    System.out.println("  数组已有序，提前结束");
                    break;
                }
            }
        }
    }
    
    // 2. 选择排序
    static class SelectionSort {
        public static void selectionSort(int[] arr) {
            int n = arr.length;
            System.out.println("选择排序过程:");
            for (int i = 0; i < n - 1; i++) {
                int minIndex = i;
                // 找到未排序部分的最小元素索引
                for (int j = i + 1; j < n; j++) {
                    if (arr[j] < arr[minIndex]) {
                        minIndex = j;
                    }
                }
                // 交换找到的最小元素与未排序部分的第一个元素
                if (minIndex != i) {
                    int temp = arr[i];
                    arr[i] = arr[minIndex];
                    arr[minIndex] = temp;
                    System.out.println("  第" + (i + 1) + "轮: 交换(" + arr[minIndex] + "," + arr[i] + ") -> " + Arrays.toString(arr));
                } else {
                    System.out.println("  第" + (i + 1) + "轮: 无需交换 -> " + Arrays.toString(arr));
                }
            }
        }
    }
    
    // 3. 插入排序
    static class InsertionSort {
        public static void insertionSort(int[] arr) {
            int n = arr.length;
            System.out.println("插入排序过程:");
            for (int i = 1; i < n; i++) {
                int key = arr[i];
                int j = i - 1;
                System.out.print("  插入元素" + key + ": ");
                
                // 将大于key的元素向后移动
                while (j >= 0 && arr[j] > key) {
                    arr[j + 1] = arr[j];
                    j--;
                }
                // 插入key到正确位置
                arr[j + 1] = key;
                System.out.println(Arrays.toString(arr));
            }
        }
    }
    
    // 4. 希尔排序
    static class ShellSort {
        public static void shellSort(int[] arr) {
            int n = arr.length;
            System.out.println("希尔排序过程:");
            // 初始增量为数组长度的一半，每次减半
            for (int gap = n / 2; gap > 0; gap /= 2) {
                System.out.println("  增量=" + gap + ":");
                // 对各个子序列进行插入排序
                for (int i = gap; i < n; i++) {
                    int key = arr[i];
                    int j = i;
                    
                    // 在子序列中进行插入排序
                    while (j >= gap && arr[j - gap] > key) {
                        arr[j] = arr[j - gap];
                        j -= gap;
                    }
                    arr[j] = key;
                }
                System.out.println("    结果: " + Arrays.toString(arr));
            }
        }
    }
    
    // 5. 归并排序
    static class MergeSort {
        public static void mergeSort(int[] arr) {
            if (arr.length <= 1) return;
            System.out.println("归并排序过程:");
            mergeSortHelper(arr, 0, arr.length - 1);
        }
        
        private static void mergeSortHelper(int[] arr, int left, int right) {
            if (left < right) {
                int mid = left + (right - left) / 2;
                System.out.println("  分割: [" + left + ", " + right + "] -> [" + left + ", " + mid + "] 和 [" + (mid + 1) + ", " + right + "]");
                
                // 递归排序左半部分
                mergeSortHelper(arr, left, mid);
                // 递归排序右半部分
                mergeSortHelper(arr, mid + 1, right);
                // 合并两个有序部分
                merge(arr, left, mid, right);
            }
        }
        
        private static void merge(int[] arr, int left, int mid, int right) {
            // 创建临时数组存储合并结果
            int[] temp = new int[right - left + 1];
            int i = left, j = mid + 1, k = 0;
            
            System.out.print("    合并 [" + left + ", " + mid + "] 和 [" + (mid + 1) + ", " + right + "]: ");
            
            // 合并两个有序数组
            while (i <= mid && j <= right) {
                if (arr[i] <= arr[j]) {
                    temp[k++] = arr[i++];
                } else {
                    temp[k++] = arr[j++];
                }
            }
            
            // 复制剩余元素
            while (i <= mid) {
                temp[k++] = arr[i++];
            }
            while (j <= right) {
                temp[k++] = arr[j++];
            }
            
            // 将临时数组复制回原数组
            System.arraycopy(temp, 0, arr, left, temp.length);
            System.out.println(Arrays.toString(temp) + " -> " + Arrays.toString(Arrays.copyOfRange(arr, left, right + 1)));
        }
    }
    
    // 6. 快速排序
    static class QuickSort {
        public static void quickSort(int[] arr) {
            if (arr.length <= 1) return;
            System.out.println("快速排序过程:");
            quickSortHelper(arr, 0, arr.length - 1);
        }
        
        private static void quickSortHelper(int[] arr, int low, int high) {
            if (low < high) {
                System.out.println("  排序区间 [" + low + ", " + high + "]");
                // 获取分区点
                int pivotIndex = partition(arr, low, high);
                System.out.println("    基准元素 " + arr[pivotIndex] + " 的最终位置: " + pivotIndex);
                System.out.println("    分区后: " + Arrays.toString(arr));
                
                // 递归排序基准左边的元素
                quickSortHelper(arr, low, pivotIndex - 1);
                // 递归排序基准右边的元素
                quickSortHelper(arr, pivotIndex + 1, high);
            }
        }
        
        private static int partition(int[] arr, int low, int high) {
            // 选择最后一个元素作为基准
            int pivot = arr[high];
            int i = low - 1; // 小于基准的元素的索引
            
            System.out.print("    以 " + pivot + " 为基准进行分区: ");
            
            for (int j = low; j < high; j++) {
                // 如果当前元素小于或等于基准
                if (arr[j] <= pivot) {
                    i++;
                    if (i != j) {
                        swap(arr, i, j);
                    }
                }
            }
            
            // 将基准放到正确位置
            swap(arr, i + 1, high);
            return i + 1;
        }
        
        private static void swap(int[] arr, int i, int j) {
            int temp = arr[i];
            arr[i] = arr[j];
            arr[j] = temp;
        }
    }
    
    // 7. 堆排序
    static class HeapSort {
        public static void heapSort(int[] arr) {
            int n = arr.length;
            System.out.println("堆排序过程:");
            
            // 构建最大堆
            System.out.println("  构建最大堆:");
            for (int i = n / 2 - 1; i >= 0; i--) {
                heapify(arr, n, i);
            }
            System.out.println("    初始最大堆: " + Arrays.toString(arr));
            
            // 逐个提取元素
            System.out.println("  排序过程:");
            for (int i = n - 1; i > 0; i--) {
                // 将当前最大元素移到末尾
                swap(arr, 0, i);
                System.out.println("    将 " + arr[i] + " 移到位置 " + i + ": " + Arrays.toString(arr));
                
                // 重新调整堆
                heapify(arr, i, 0);
                System.out.println("    调整堆后: " + Arrays.toString(Arrays.copyOf(arr, i)));
            }
        }
        
        private static void heapify(int[] arr, int n, int i) {
            int largest = i; // 初始化最大为根
            int left = 2 * i + 1; // 左子节点
            int right = 2 * i + 2; // 右子节点
            
            // 如果左子节点存在且大于根
            if (left < n && arr[left] > arr[largest]) {
                largest = left;
            }
            
            // 如果右子节点存在且大于当前最大
            if (right < n && arr[right] > arr[largest]) {
                largest = right;
            }
            
            // 如果最大不是根
            if (largest != i) {
                swap(arr, i, largest);
                System.out.println("      交换 " + arr[largest] + " 和 " + arr[i]);
                
                // 递归调整受影响的子树
                heapify(arr, n, largest);
            }
        }
        
        private static void swap(int[] arr, int i, int j) {
            int temp = arr[i];
            arr[i] = arr[j];
            arr[j] = temp;
        }
    }
    
    // 8. 计数排序
    static class CountingSort {
        public static void countingSort(int[] arr) {
            if (arr.length <= 1) return;
            System.out.println("计数排序过程:");
            System.out.println("  原数组: " + Arrays.toString(arr));
            
            // 找到最大值和最小值
            int max = arr[0], min = arr[0];
            for (int num : arr) {
                max = Math.max(max, num);
                min = Math.min(min, num);
            }
            System.out.println("  最大值: " + max + ", 最小值: " + min);
            
            // 计算范围
            int range = max - min + 1;
            int[] count = new int[range];
            int[] output = new int[arr.length];
            
            // 统计每个元素出现的次数
            System.out.print("  计数统计: ");
            for (int num : arr) {
                count[num - min]++;
            }
            for (int i = 0; i < range; i++) {
                if (count[i] > 0) {
                    System.out.print((i + min) + ":" + count[i] + " ");
                }
            }
            System.out.println();
            
            // 计算累积计数
            System.out.print("  累积计数: ");
            for (int i = 1; i < range; i++) {
                count[i] += count[i - 1];
                System.out.print(count[i] + " ");
            }
            System.out.println();
            
            // 构建输出数组
            System.out.print("  构建输出数组: ");
            for (int i = arr.length - 1; i >= 0; i--) {
                output[count[arr[i] - min] - 1] = arr[i];
                count[arr[i] - min]--;
                System.out.print(output[count[arr[i] - min]] + " ");
            }
            System.out.println();
            
            // 复制回原数组
            System.arraycopy(output, 0, arr, 0, arr.length);
        }
    }
    
    // 9. 桶排序
    static class BucketSort {
        public static void bucketSort(float[] arr) {
            if (arr.length <= 1) return;
            System.out.println("桶排序过程:");
            System.out.println("  原数组: " + Arrays.toString(arr));
            
            // 创建桶
            int bucketCount = arr.length;
            List<List<Float>> buckets = new ArrayList<>(bucketCount);
            
            // 初始化桶
            for (int i = 0; i < bucketCount; i++) {
                buckets.add(new ArrayList<>());
            }
            
            // 将元素分配到桶中
            System.out.print("  分配到桶中: ");
            for (float num : arr) {
                int bucketIndex = (int) (num * bucketCount);
                // 处理边界情况
                if (bucketIndex >= bucketCount) {
                    bucketIndex = bucketCount - 1;
                }
                buckets.get(bucketIndex).add(num);
                System.out.print(num + "->桶" + bucketIndex + " ");
            }
            System.out.println();
            
            // 显示每个桶的内容
            for (int i = 0; i < buckets.size(); i++) {
                if (!buckets.get(i).isEmpty()) {
                    System.out.println("    桶" + i + ": " + buckets.get(i));
                }
            }
            
            // 对每个桶进行排序
            System.out.println("  对每个桶排序:");
            for (int i = 0; i < buckets.size(); i++) {
                if (!buckets.get(i).isEmpty()) {
                    Collections.sort(buckets.get(i));
                    System.out.println("    桶" + i + "排序后: " + buckets.get(i));
                }
            }
            
            // 合并桶中的元素
            int index = 0;
            System.out.print("  合并结果: ");
            for (List<Float> bucket : buckets) {
                for (float num : bucket) {
                    arr[index++] = num;
                    System.out.print(num + " ");
                }
            }
            System.out.println();
        }
    }
    
    // 10. 基数排序
    static class RadixSort {
        public static void radixSort(int[] arr) {
            if (arr.length <= 1) return;
            System.out.println("基数排序过程:");
            System.out.println("  原数组: " + Arrays.toString(arr));
            
            // 找到最大数以确定位数
            int max = getMax(arr);
            System.out.println("  最大数: " + max + ", 位数: " + String.valueOf(max).length());
            
            // 对每一位进行计数排序
            for (int exp = 1; max / exp > 0; exp *= 10) {
                System.out.println("  按第" + (String.valueOf(exp).length()) + "位排序 (exp=" + exp + "):");
                countingSortByDigit(arr, exp);
                System.out.println("    结果: " + Arrays.toString(arr));
            }
        }
        
        private static int getMax(int[] arr) {
            int max = arr[0];
            for (int i = 1; i < arr.length; i++) {
                if (arr[i] > max) {
                    max = arr[i];
                }
            }
            return max;
        }
        
        private static void countingSortByDigit(int[] arr, int exp) {
            int n = arr.length;
            int[] output = new int[n];
            int[] count = new int[10];
            
            // 统计每个数字出现的次数
            for (int i = 0; i < n; i++) {
                count[(arr[i] / exp) % 10]++;
            }
            
            // 计算累积计数
            for (int i = 1; i < 10; i++) {
                count[i] += count[i - 1];
            }
            
            // 构建输出数组
            for (int i = n - 1; i >= 0; i--) {
                output[count[(arr[i] / exp) % 10] - 1] = arr[i];
                count[(arr[i] / exp) % 10]--;
            }
            
            // 复制回原数组
            System.arraycopy(output, 0, arr, 0, n);
        }
    }
    
    // 性能测试工具类
    static class SortingPerformanceTest {
        public static void testSortingPerformance() {
            System.out.println("\n=== 排序算法性能测试 ===");
            
            // 测试不同规模的数据
            int[] sizes = {1000, 5000, 10000};
            
            for (int size : sizes) {
                System.out.println("\n测试规模: " + size + " 个元素");
                
                // 生成随机数据
                int[] randomData = generateRandomArray(size);
                
                // 测试各种排序算法
                testAlgorithm("冒泡排序", randomData.clone(), BubbleSort::bubbleSort);
                testAlgorithm("选择排序", randomData.clone(), SelectionSort::selectionSort);
                testAlgorithm("插入排序", randomData.clone(), InsertionSort::insertionSort);
                testAlgorithm("希尔排序", randomData.clone(), ShellSort::shellSort);
                testAlgorithm("归并排序", randomData.clone(), MergeSort::mergeSort);
                testAlgorithm("快速排序", randomData.clone(), QuickSort::quickSort);
                testAlgorithm("堆排序", randomData.clone(), HeapSort::heapSort);
                testAlgorithm("计数排序", randomData.clone(), CountingSort::countingSort);
                testAlgorithm("基数排序", randomData.clone(), RadixSort::radixSort);
            }
        }
        
        private static int[] generateRandomArray(int size) {
            Random random = new Random();
            int[] arr = new int[size];
            for (int i = 0; i < size; i++) {
                arr[i] = random.nextInt(1000); // 生成0-999的随机数
            }
            return arr;
        }
        
        private static void testAlgorithm(String name, int[] arr, SortFunction sorter) {
            long startTime = System.nanoTime();
            sorter.sort(arr);
            long endTime = System.nanoTime();
            
            double duration = (endTime - startTime) / 1_000_000.0; // 转换为毫秒
            System.out.printf("  %-10s: %.2f ms%n", name, duration);
        }
        
        @FunctionalInterface
        interface SortFunction {
            void sort(int[] arr);
        }
    }
    
    // 主测试方法
    public static void main(String[] args) {
        System.out.println("=== 第八章：排序算法 - 数据有序化之道 ===\n");
        
        // 1. 测试冒泡排序
        System.out.println("1. 冒泡排序测试:");
        int[] bubbleArr = {64, 34, 25, 12, 22, 11, 90};
        System.out.println("  原数组: " + Arrays.toString(bubbleArr));
        BubbleSort.bubbleSort(bubbleArr);
        System.out.println("  排序后: " + Arrays.toString(bubbleArr));
        System.out.println();
        
        // 2. 测试选择排序
        System.out.println("2. 选择排序测试:");
        int[] selectionArr = {64, 34, 25, 12, 22, 11, 90};
        System.out.println("  原数组: " + Arrays.toString(selectionArr));
        SelectionSort.selectionSort(selectionArr);
        System.out.println("  排序后: " + Arrays.toString(selectionArr));
        System.out.println();
        
        // 3. 测试插入排序
        System.out.println("3. 插入排序测试:");
        int[] insertionArr = {64, 34, 25, 12, 22, 11, 90};
        System.out.println("  原数组: " + Arrays.toString(insertionArr));
        InsertionSort.insertionSort(insertionArr);
        System.out.println("  排序后: " + Arrays.toString(insertionArr));
        System.out.println();
        
        // 4. 测试希尔排序
        System.out.println("4. 希尔排序测试:");
        int[] shellArr = {64, 34, 25, 12, 22, 11, 90};
        System.out.println("  原数组: " + Arrays.toString(shellArr));
        ShellSort.shellSort(shellArr);
        System.out.println("  排序后: " + Arrays.toString(shellArr));
        System.out.println();
        
        // 5. 测试归并排序
        System.out.println("5. 归并排序测试:");
        int[] mergeArr = {64, 34, 25, 12, 22, 11, 90};
        System.out.println("  原数组: " + Arrays.toString(mergeArr));
        MergeSort.mergeSort(mergeArr);
        System.out.println("  排序后: " + Arrays.toString(mergeArr));
        System.out.println();
        
        // 6. 测试快速排序
        System.out.println("6. 快速排序测试:");
        int[] quickArr = {64, 34, 25, 12, 22, 11, 90};
        System.out.println("  原数组: " + Arrays.toString(quickArr));
        QuickSort.quickSort(quickArr);
        System.out.println("  排序后: " + Arrays.toString(quickArr));
        System.out.println();
        
        // 7. 测试堆排序
        System.out.println("7. 堆排序测试:");
        int[] heapArr = {64, 34, 25, 12, 22, 11, 90};
        System.out.println("  原数组: " + Arrays.toString(heapArr));
        HeapSort.heapSort(heapArr);
        System.out.println("  排序后: " + Arrays.toString(heapArr));
        System.out.println();
        
        // 8. 测试计数排序
        System.out.println("8. 计数排序测试:");
        int[] countingArr = {4, 2, 2, 8, 3, 3, 1};
        System.out.println("  原数组: " + Arrays.toString(countingArr));
        CountingSort.countingSort(countingArr);
        System.out.println("  排序后: " + Arrays.toString(countingArr));
        System.out.println();
        
        // 9. 测试桶排序
        System.out.println("9. 桶排序测试:");
        float[] bucketArr = {0.42f, 0.32f, 0.33f, 0.52f, 0.37f, 0.47f, 0.51f};
        System.out.println("  原数组: " + Arrays.toString(bucketArr));
        BucketSort.bucketSort(bucketArr);
        System.out.println("  排序后: " + Arrays.toString(bucketArr));
        System.out.println();
        
        // 10. 测试基数排序
        System.out.println("10. 基数排序测试:");
        int[] radixArr = {170, 45, 75, 90, 2, 802, 24, 66};
        System.out.println("  原数组: " + Arrays.toString(radixArr));
        RadixSort.radixSort(radixArr);
        System.out.println("  排序后: " + Arrays.toString(radixArr));
        System.out.println();
        
        // 11. 性能测试
        SortingPerformanceTest.testSortingPerformance();
    }
}