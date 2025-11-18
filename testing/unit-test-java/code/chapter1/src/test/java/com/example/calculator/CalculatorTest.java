package com.example.calculator;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Calculator类的单元测试
 */
public class CalculatorTest {
    
    private final Calculator calculator = new Calculator();
    
    @Test
    public void testAdd() {
        // 测试正常情况
        assertEquals(5, calculator.add(2, 3), "2 + 3 应该等于 5");
        assertEquals(-1, calculator.add(-2, 1), "-2 + 1 应该等于 -1");
        assertEquals(0, calculator.add(0, 0), "0 + 0 应该等于 0");
    }
    
    @Test
    public void testSubtract() {
        // 测试正常情况
        assertEquals(1, calculator.subtract(3, 2), "3 - 2 应该等于 1");
        assertEquals(-3, calculator.subtract(-2, 1), "-2 - 1 应该等于 -3");
        assertEquals(0, calculator.subtract(0, 0), "0 - 0 应该等于 0");
    }
    
    @Test
    public void testMultiply() {
        // 测试正常情况
        assertEquals(6, calculator.multiply(2, 3), "2 * 3 应该等于 6");
        assertEquals(-2, calculator.multiply(-2, 1), "-2 * 1 应该等于 -2");
        assertEquals(0, calculator.multiply(0, 5), "0 * 5 应该等于 0");
    }
    
    @Test
    public void testDivide() {
        // 测试正常情况
        assertEquals(2.5, calculator.divide(5, 2), "5 / 2 应该等于 2.5", 0.0001);
        assertEquals(0.5, calculator.divide(1, 2), "1 / 2 应该等于 0.5", 0.0001);
        assertEquals(0, calculator.divide(0, 5), "0 / 5 应该等于 0", 0.0001);
        assertEquals(-2.5, calculator.divide(-5, 2), "-5 / 2 应该等于 -2.5", 0.0001);
    }
    
    @Test
    public void testDivideByZero() {
        // 测试异常情况
        Exception exception = assertThrows(IllegalArgumentException.class, 
            () -> calculator.divide(5, 0), "除数为0应该抛出IllegalArgumentException");
        
        assertEquals("除数不能为0", exception.getMessage(), 
            "异常消息应该为'除数不能为0'");
    }
    
    @Test
    public void testPower() {
        // 测试正常情况
        assertEquals(8, calculator.power(2, 3), "2的3次方应该等于8");
        assertEquals(1, calculator.power(5, 0), "任何数的0次方应该等于1");
        assertEquals(0.25, calculator.power(2, -2), "2的-2次方应该等于0.25", 0.0001);
    }
    
    @Test
    public void testSqrt() {
        // 测试正常情况
        assertEquals(3, calculator.sqrt(9), "9的平方根应该等于3", 0.0001);
        assertEquals(2, calculator.sqrt(4), "4的平方根应该等于2", 0.0001);
        assertEquals(0, calculator.sqrt(0), "0的平方根应该等于0", 0.0001);
        assertEquals(1.4142, calculator.sqrt(2), "2的平方根约等于1.4142", 0.0001);
    }
    
    @Test
    public void testSqrtNegative() {
        // 测试异常情况
        Exception exception = assertThrows(IllegalArgumentException.class, 
            () -> calculator.sqrt(-4), "负数的平方根应该抛出IllegalArgumentException");
        
        assertEquals("不能计算负数的平方根", exception.getMessage(), 
            "异常消息应该为'不能计算负数的平方根'");
    }
}