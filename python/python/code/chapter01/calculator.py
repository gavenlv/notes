#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
calculator.py - 简单计算器
演示Python基础输入输出和算术运算
"""

print("=" * 50)
print("           简单计算器")
print("=" * 50)

# 输入两个数字
print("\n请输入两个数字,我会帮你计算:")
num1 = float(input("第一个数字: "))
num2 = float(input("第二个数字: "))

# 执行四则运算
print("\n" + "=" * 50)
print("计算结果:")
print("=" * 50)

print(f"{num1} + {num2} = {num1 + num2}")
print(f"{num1} - {num2} = {num1 - num2}")
print(f"{num1} × {num2} = {num1 * num2}")

if num2 != 0:
    print(f"{num1} ÷ {num2} = {num1 / num2}")
    print(f"{num1} ÷ {num2} (整除) = {num1 // num2}")
    print(f"{num1} % {num2} (余数) = {num1 % num2}")
else:
    print(f"{num1} ÷ {num2} = 错误! 除数不能为0")

print(f"{num1} ^ {num2} (幂运算) = {num1 ** num2}")

print("\n" + "=" * 50)
print("感谢使用!")
print("=" * 50)
