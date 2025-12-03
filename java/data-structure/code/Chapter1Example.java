/**
 * 第一章：数据结构与算法入门 - 基础概念与复杂度分析
 * 代码示例演示了不同时间复杂度和空间复杂度的算法
 */

public class Chapter1Example {
    
    // O(1) - 常数时间复杂度示例
    public static int getFirstElement(int[] array) {
        System.out.println("获取数组第一个元素 - O(1)");
        return array[0];
    }
    
    // O(n) - 线性时间复杂度示例
    public static int sumArray(int[] array) {
        System.out.println("计算数组元素之和 - O(n)");
        int sum = 0;
        for (int i = 0; i < array.length; i++) {
            sum += array[i];
        }
        return sum;
    }
    
    // O(n²) - 平方时间复杂度示例
    public static void printPairs(int[] array) {
        System.out.println("打印数组中所有元素对 - O(n²)");
        for (int i = 0; i < array.length; i++) {
            for (int j = 0; j < array.length; j++) {
                System.out.print("(" + array[i] + "," + array[j] + ") ");
            }
            System.out.println();
        }
    }
    
    // O(1) - 常数空间复杂度示例
    public static int add(int a, int b) {
        System.out.println("两数相加 - O(1) 空间复杂度");
        return a + b;
    }
    
    // O(n) - 线性空间复杂度示例
    public static int[] copyArray(int[] array) {
        System.out.println("复制数组 - O(n) 空间复杂度");
        int[] newArray = new int[array.length];
        for (int i = 0; i < array.length; i++) {
            newArray[i] = array[i];
        }
        return newArray;
    }
    
    // 测试方法
    public static void main(String[] args) {
        System.out.println("=== 第一章：数据结构与算法入门示例 ===\n");
        
        // 创建测试数组
        int[] testArray = {1, 2, 3, 4, 5};
        
        // 测试 O(1) 时间复杂度
        int firstElement = getFirstElement(testArray);
        System.out.println("第一个元素: " + firstElement + "\n");
        
        // 测试 O(n) 时间复杂度
        int sum = sumArray(testArray);
        System.out.println("数组元素之和: " + sum + "\n");
        
        // 测试 O(n²) 时间复杂度
        printPairs(testArray);
        System.out.println();
        
        // 测试 O(1) 空间复杂度
        int result = add(5, 3);
        System.out.println("加法结果: " + result + "\n");
        
        // 测试 O(n) 空间复杂度
        int[] copiedArray = copyArray(testArray);
        System.out.print("复制后的数组: ");
        for (int value : copiedArray) {
            System.out.print(value + " ");
        }
        System.out.println("\n");
        
        System.out.println("=== 示例结束 ===");
    }
}