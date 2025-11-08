#!/usr/bin/env python3
"""
Redis哈希操作示例

这个示例展示Redis哈希数据类型的各种操作。
"""

import redis
import json

def main():
    """主函数 - 演示哈希操作"""
    
    print("=== Redis哈希操作示例 ===")
    
    # 连接到Redis
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis连接成功")
    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
        return
    
    # 1. 基本哈希操作
    print("\n1. 基本哈希操作")
    
    # 创建用户信息哈希
    user_info = {
        'name': '张三',
        'age': '28',
        'email': 'zhangsan@example.com',
        'city': '北京',
        'phone': '13800138000'
    }
    
    # 批量设置哈希字段
    r.hset('user:1001', mapping=user_info)
    print("用户信息哈希创建完成")
    
    # 获取单个字段
    name = r.hget('user:1001', 'name')
    email = r.hget('user:1001', 'email')
    print(f"姓名: {name}, 邮箱: {email}")
    
    # 2. 获取所有字段
    print("\n2. 获取所有字段")
    
    # 获取所有字段和值
    all_fields = r.hgetall('user:1001')
    print("所有字段:")
    for field, value in all_fields.items():
        print(f"  {field}: {value}")
    
    # 3. 字段操作
    print("\n3. 字段操作")
    
    # 检查字段是否存在
    has_age = r.hexists('user:1001', 'age')
    has_gender = r.hexists('user:1001', 'gender')
    print(f"'age'字段是否存在: {has_age}")
    print(f"'gender'字段是否存在: {has_gender}")
    
    # 获取字段数量
    field_count = r.hlen('user:1001')
    print(f"哈希字段数量: {field_count}")
    
    # 4. 数字操作
    print("\n4. 数字操作")
    
    # 设置数字字段
    r.hset('user:1001', 'score', '100')
    
    # 递增数字字段
    r.hincrby('user:1001', 'score', 10)  # 110
    r.hincrby('user:1001', 'score', -5)  # 105
    
    # 递增浮点数字段
    r.hincrbyfloat('user:1001', 'balance', 50.5)
    r.hincrbyfloat('user:1001', 'balance', -10.2)
    
    score = r.hget('user:1001', 'score')
    balance = r.hget('user:1001', 'balance')
    print(f"分数: {score}, 余额: {balance}")
    
    # 5. 批量操作
    print("\n5. 批量操作")
    
    # 获取多个字段
    fields = ['name', 'age', 'email', 'score']
    values = r.hmget('user:1001', fields)
    
    print("批量获取字段:")
    for field, value in zip(fields, values):
        print(f"  {field}: {value}")
    
    # 6. 字段管理
    print("\n6. 字段管理")
    
    # 获取所有字段名
    field_names = r.hkeys('user:1001')
    print(f"所有字段名: {field_names}")
    
    # 获取所有字段值
    field_values = r.hvals('user:1001')
    print(f"所有字段值: {field_values}")
    
    # 7. 删除操作
    print("\n7. 删除操作")
    
    # 删除单个字段
    r.hdel('user:1001', 'phone')
    print("已删除 'phone' 字段")
    
    # 删除多个字段
    r.hdel('user:1001', 'balance', 'score')
    print("已删除 'balance' 和 'score' 字段")
    
    # 检查删除结果
    remaining_fields = r.hkeys('user:1001')
    print(f"剩余字段: {remaining_fields}")
    
    # 8. 高级操作
    print("\n8. 高级操作")
    
    # 条件设置（仅当字段不存在时）
    result1 = r.hsetnx('user:1001', 'nickname', '张三丰')
    result2 = r.hsetnx('user:1001', 'nickname', '张无忌')  # 不会设置成功
    
    print(f"第一次设置昵称结果: {result1}")
    print(f"第二次设置昵称结果: {result2}")
    print(f"最终昵称: {r.hget('user:1001', 'nickname')}")
    
    # 9. 扫描操作（处理大哈希）
    print("\n9. 扫描操作")
    
    # 使用HSCAN迭代哈希字段
    cursor = 0
    print("使用HSCAN迭代字段:")
    
    while True:
        cursor, data = r.hscan('user:1001', cursor=cursor, count=2)
        for field, value in data.items():
            print(f"  {field}: {value}")
        
        if cursor == 0:
            break
    
    # 10. 实际应用示例
    print("\n10. 实际应用示例")
    
    # 购物车实现
    cart_items = {
        'product:1001': '2',  # 商品ID: 数量
        'product:1002': '1',
        'product:1003': '3'
    }
    
    r.hset('cart:user:1001', mapping=cart_items)
    print("购物车创建完成")
    
    # 添加商品到购物车
    r.hincrby('cart:user:1001', 'product:1001', 1)  # 增加数量
    r.hset('cart:user:1001', 'product:1004', '1')   # 添加新商品
    
    # 获取购物车信息
    cart = r.hgetall('cart:user:1001')
    print("购物车内容:")
    for product, quantity in cart.items():
        print(f"  {product}: {quantity}件")
    
    # 11. 清理
    print("\n11. 清理测试数据")
    
    # 删除所有测试键
    test_keys = ['user:1001', 'cart:user:1001']
    r.delete(*test_keys)
    
    print(f"已清理 {len(test_keys)} 个测试键")
    
    print("\n=== 哈希操作示例完成 ===")

if __name__ == "__main__":
    main()