package com.example.utils;

/**
 * 字符串处理工具类，用于演示各种断言方法
 */
public class StringHelper {
    
    /**
     * 检查字符串是否为空或null
     * @param str 要检查的字符串
     * @return 如果字符串为null或长度为0返回true，否则返回false
     */
    public static boolean isEmpty(String str) {
        return str == null || str.length() == 0;
    }
    
    /**
     * 检查字符串是否包含指定内容
     * @param str 原始字符串
     * @param substr 要查找的子字符串
     * @return 如果包含返回true，否则返回false
     * @throws IllegalArgumentException 如果任一参数为null
     */
    public static boolean contains(String str, String substr) {
        if (str == null || substr == null) {
            throw new IllegalArgumentException("参数不能为null");
        }
        return str.contains(substr);
    }
    
    /**
     * 反转字符串
     * @param str 要反转的字符串
     * @return 反转后的字符串
     * @throws IllegalArgumentException 如果参数为null
     */
    public static String reverse(String str) {
        if (str == null) {
            throw new IllegalArgumentException("参数不能为null");
        }
        return new StringBuilder(str).reverse().toString();
    }
    
    /**
     * 将字符串转换为大写
     * @param str 要转换的字符串
     * @return 转换为大写的字符串
     */
    public static String toUpperCase(String str) {
        if (str == null) {
            return null;
        }
        return str.toUpperCase();
    }
    
    /**
     * 将字符串转换为小写
     * @param str 要转换的字符串
     * @return 转换为小写的字符串
     */
    public static String toLowerCase(String str) {
        if (str == null) {
            return null;
        }
        return str.toLowerCase();
    }
    
    /**
     * 去除字符串两端的空白字符
     * @param str 要处理的字符串
     * @return 去除空白后的字符串
     */
    public static String trim(String str) {
        if (str == null) {
            return null;
        }
        return str.trim();
    }
}