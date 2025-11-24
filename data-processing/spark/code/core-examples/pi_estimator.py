#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Spark Pi估计器示例
使用蒙特卡洛方法估计π值，这是Spark的另一个经典入门示例。

运行方式:
spark-submit pi_estimator.py [slices]
"""

from pyspark import SparkContext
import sys
import random

def estimate_pi(sc, slices):
    """使用蒙特卡洛方法估计π值"""
    
    # 定义样本数量
    n = 100000 * slices
    
    def is_point_in_circle(_):
        """判断随机点是否在单位圆内"""
        x = random.random() * 2 - 1  # 生成[-1, 1]范围内的随机x坐标
        y = random.random() * 2 - 1  # 生成[-1, 1]范围内的随机y坐标
        return 1 if x*x + y*y <= 1 else 0  # 如果点在圆内返回1，否则返回0
    
    # 创建RDD并执行计算
    count = sc.parallelize(range(1, n + 1), slices).map(is_point_in_circle).sum()
    
    # 估计π值
    pi_est = 4.0 * count / n
    
    return pi_est

def main():
    """主函数"""
    # 创建SparkContext
    sc = SparkContext(appName="PythonPiEstimator")
    
    try:
        # 获取切片数（分区数）
        slices = int(sys.argv[1]) if len(sys.argv) > 1 else 2
        print(f"使用 {slices} 个切片进行计算...")
        
        # 估计π值
        pi_est = estimate_pi(sc, slices)
        
        # 打印结果
        print(f"π的估计值: {pi_est}")
        print(f"与实际值的误差: {abs(pi_est - 3.141592653589793)}")
        
        # 与实际值比较
        actual_pi = 3.141592653589793
        error_percent = abs(pi_est - actual_pi) / actual_pi * 100
        print(f"相对误差: {error_percent:.6f}%")
        
    except Exception as e:
        print(f"Pi估计器执行失败: {str(e)}")
    finally:
        # 停止SparkContext
        sc.stop()

if __name__ == "__main__":
    main()