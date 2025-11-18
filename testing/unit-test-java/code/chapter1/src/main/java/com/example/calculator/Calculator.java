package com.example.calculator;

/**
 * 简单的计算器类，用于演示基本的单元测试
 */
public class Calculator {
    
    /**
     * 加法运算
     * @param a 第一个数
     * @param b 第二个数
     * @return 两个数的和
     */
    public int add(int a, int b) {
        return a + b;
    }
    
    /**
     * 减法运算
     * @param a 第一个数
     * @param b 第二个数
     * @return 两个数的差
     */
    public int subtract(int a, int b) {
        return a - b;
    }
    
    /**
     * 乘法运算
     * @param a 第一个数
     * @param b 第二个数
     * @return 两个数的积
     */
    public int multiply(int a, int b) {
        return a * b;
    }
    
    /**
     * 除法运算
     * @param a 被除数
     * @param b 除数
     * @return 两个数的商
     * @throws IllegalArgumentException 当除数为0时抛出异常
     */
    public double divide(int a, int b) {
        if (b == 0) {
            throw new IllegalArgumentException("除数不能为0");
        }
        return (double) a / b;
    }
    
    /**
     * 幂运算
     * @param base 底数
     * @param exponent 指数
     * @return base的exponent次方
     */
    public double power(int base, int exponent) {
        return Math.pow(base, exponent);
    }
    
    /**
     * 平方根运算
     * @param number 要计算平方根的数
     * @return 数字的平方根
     * @throws IllegalArgumentException 当数字为负数时抛出异常
     */
    public double sqrt(int number) {
        if (number < 0) {
            throw new IllegalArgumentException("不能计算负数的平方根");
        }
        return Math.sqrt(number);
    }
}