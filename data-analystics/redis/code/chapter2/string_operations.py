#!/usr/bin/env python3
"""
Redis字符串操作示例

这个示例展示Redis字符串数据类型的各种操作。
"""

import redis
import time

def main():
    """主函数 - 演示字符串操作"""
    
    print("=== Redis字符串操作示例 ===")
    
    # 连接到Redis
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis连接成功")
    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
        return
    
    # 1. 基本字符串操作
    print("\n1. 基本字符串操作")
    
    # 设置和获取
    r.set('username', 'john_doe')
    username = r.get('username')
    print(f"用户名: {username}")
    
    # 设置带过期时间的键
    r.setex('session_token', 30, 'abc123xyz')
    
    # 检查键是否存在
    exists = r.exists('username')
    print(f"'username'键是否存在: {exists}")
    
    # 2. 字符串操作
    print("\n2. 字符串操作")
    
    # 设置并获取旧值
    old_value = r.getset('counter', '100')
    print(f"旧值: {old_value}, 新值: {r.get('counter')}")
    
    # 获取字符串长度
    length = r.strlen('username')
    print(f"'username'长度: {length}")
    
    # 3. 数字操作
    print("\n3. 数字操作")
    
    # 设置数字
    r.set('age', '25')
    
    # 递增操作
    r.incr('age')  # 26
    r.incr('age', 5)  # 31
    print(f"递增后年龄: {r.get('age')}")
    
    # 递减操作
    r.decr('age', 3)  # 28
    print(f"递减后年龄: {r.get('age')}")
    
    # 4. 位操作
    print("\n4. 位操作")
    
    # 设置位图
    r.setbit('user_flags', 0, 1)  # 第0位设为1
    r.setbit('user_flags', 2, 1)  # 第2位设为1
    r.setbit('user_flags', 5, 1)  # 第5位设为1
    
    # 获取位值
    bit0 = r.getbit('user_flags', 0)
    bit1 = r.getbit('user_flags', 1)
    bit2 = r.getbit('user_flags', 2)
    
    print(f"位0: {bit0}, 位1: {bit1}, 位2: {bit2}")
    
    # 统计位为1的数量
    bit_count = r.bitcount('user_flags')
    print(f"位为1的数量: {bit_count}")
    
    # 5. 批量操作
    print("\n5. 批量操作")
    
    # 批量设置
    user_data = {
        'user:1001:name': 'Alice',
        'user:1001:email': 'alice@example.com',
        'user:1001:age': '28',
        'user:1002:name': 'Bob',
        'user:1002:email': 'bob@example.com',
        'user:1002:age': '32'
    }
    
    r.mset(user_data)
    
    # 批量获取
    keys = ['user:1001:name', 'user:1001:email', 'user:1002:name', 'user:1002:email']
    values = r.mget(keys)
    
    for key, value in zip(keys, values):
        print(f"{key}: {value}")
    
    # 6. 追加操作
    print("\n6. 追加操作")
    
    # 初始值
    r.set('log', '开始日志: ')
    
    # 追加内容
    r.append('log', '用户登录')
    r.append('log', ', 浏览商品')
    r.append('log', ', 下单购买')
    
    log_content = r.get('log')
    print(f"日志内容: {log_content}")
    
    # 7. 范围操作
    print("\n7. 范围操作")
    
    # 设置长字符串
    long_text = "Redis是一个开源的内存数据结构存储系统"
    r.set('long_text', long_text)
    
    # 获取子字符串
    substring = r.getrange('long_text', 0, 4)  # 前5个字符
    print(f"前5个字符: {substring}")
    
    # 设置子字符串
    r.setrange('long_text', 5, '高性能的')
    modified_text = r.get('long_text')
    print(f"修改后文本: {modified_text}")
    
    # 8. 过期时间操作
    print("\n8. 过期时间操作")
    
    # 设置过期时间
    r.expire('session_token', 60)  # 60秒后过期
    
    # 获取剩余时间
    ttl = r.ttl('session_token')
    print(f"'session_token'剩余时间: {ttl}秒")
    
    # 持久化键（移除过期时间）
    r.persist('session_token')
    ttl_after = r.ttl('session_token')
    print(f"持久化后剩余时间: {ttl_after}秒")
    
    # 9. 高级操作
    print("\n9. 高级操作")
    
    # 条件设置（仅当键不存在时）
    result1 = r.setnx('unique_key', 'value1')
    result2 = r.setnx('unique_key', 'value2')  # 不会设置成功
    
    print(f"第一次设置结果: {result1}")
    print(f"第二次设置结果: {result2}")
    print(f"最终值: {r.get('unique_key')}")
    
    # 10. 清理
    print("\n10. 清理测试数据")
    
    # 删除所有测试键
    test_keys = [
        'username', 'session_token', 'counter', 'age',
        'user_flags', 'log', 'long_text', 'unique_key'
    ] + keys
    
    r.delete(*test_keys)
    print(f"已清理 {len(test_keys)} 个测试键")
    
    print("\n=== 字符串操作示例完成 ===")

if __name__ == "__main__":
    main()