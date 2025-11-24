#!/usr/bin/env python3
"""
Redis基础操作示例

这个示例展示Redis的基本操作，包括连接、键值操作、数据类型等。
"""

import redis
import time

def main():
    """主函数 - 演示Redis基础操作"""
    
    print("=== Redis基础操作示例 ===")
    
    # 1. 连接到Redis
    print("\n1. 连接Redis服务器")
    try:
        # 创建Redis客户端
        r = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True,  # 自动解码响应
            socket_connect_timeout=5,  # 连接超时
            socket_timeout=5  # 操作超时
        )
        
        # 测试连接
        response = r.ping()
        print(f"✅ Redis连接成功: {response}")
        
    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
        print("请确保Redis服务正在运行")
        return
    
    # 2. 基本键值操作
    print("\n2. 基本键值操作")
    
    # 设置键值
    r.set('name', 'Redis Learner')
    r.set('age', '25')
    r.set('city', 'Beijing')
    
    # 获取键值
    name = r.get('name')
    age = r.get('age')
    city = r.get('city')
    
    print(f"姓名: {name}")
    print(f"年龄: {age}")
    print(f"城市: {city}")
    
    # 3. 带过期时间的键
    print("\n3. 带过期时间的键")
    
    # 设置10秒后过期的键
    r.setex('temp_key', 10, '这个键将在10秒后过期')
    
    # 检查键是否存在
    exists_before = r.exists('temp_key')
    print(f"设置后键是否存在: {exists_before}")
    
    # 获取剩余过期时间
    ttl = r.ttl('temp_key')
    print(f"剩余过期时间: {ttl}秒")
    
    # 4. 批量操作
    print("\n4. 批量操作")
    
    # 批量设置
    data = {
        'user:1:name': 'Alice',
        'user:1:email': 'alice@example.com',
        'user:1:age': '30',
        'user:2:name': 'Bob',
        'user:2:email': 'bob@example.com',
        'user:2:age': '28'
    }
    
    r.mset(data)
    
    # 批量获取
    keys = ['user:1:name', 'user:1:email', 'user:2:name', 'user:2:email']
    values = r.mget(keys)
    
    for key, value in zip(keys, values):
        print(f"{key}: {value}")
    
    # 5. 原子操作
    print("\n5. 原子操作")
    
    # 计数器
    r.set('counter', '0')
    
    # 递增操作
    for i in range(5):
        new_value = r.incr('counter')
        print(f"第{i+1}次递增: {new_value}")
    
    # 递减操作
    for i in range(3):
        new_value = r.decr('counter')
        print(f"第{i+1}次递减: {new_value}")
    
    # 6. 键管理
    print("\n6. 键管理")
    
    # 获取所有键（生产环境慎用，可能返回大量数据）
    all_keys = r.keys('*')
    print(f"当前数据库中的键数量: {len(all_keys)}")
    print("前10个键:", all_keys[:10])
    
    # 键模式匹配
    user_keys = r.keys('user:*')
    print(f"用户相关键: {user_keys}")
    
    # 7. 删除操作
    print("\n7. 删除操作")
    
    # 删除单个键
    r.delete('name')
    print("已删除键 'name'")
    
    # 删除多个键
    r.delete('age', 'city')
    print("已删除键 'age' 和 'city'")
    
    # 检查删除结果
    name_exists = r.exists('name')
    age_exists = r.exists('age')
    print(f"'name'键是否存在: {name_exists}")
    print(f"'age'键是否存在: {age_exists}")
    
    # 8. 数据库信息
    print("\n8. 数据库信息")
    
    # 获取Redis信息
    info = r.info()
    
    print("Redis服务器信息:")
    print(f"  Redis版本: {info.get('redis_version', 'N/A')}")
    print(f"  运行模式: {info.get('redis_mode', 'N/A')}")
    print(f"  操作系统: {info.get('os', 'N/A')}")
    print(f"  进程ID: {info.get('process_id', 'N/A')}")
    print(f"  运行时间: {info.get('uptime_in_seconds', 'N/A')}秒")
    print(f"  已连接客户端: {info.get('connected_clients', 'N/A')}")
    print(f"  使用内存: {info.get('used_memory_human', 'N/A')}")
    
    # 9. 等待临时键过期
    print("\n9. 等待临时键过期演示")
    
    # 检查临时键是否还存在
    time.sleep(3)  # 等待3秒
    ttl_remaining = r.ttl('temp_key')
    print(f"3秒后剩余过期时间: {ttl_remaining}秒")
    
    # 清理
    print("\n10. 清理测试数据")
    
    # 删除所有测试键
    test_keys = ['temp_key', 'counter'] + user_keys
    r.delete(*test_keys)
    
    print(f"已清理 {len(test_keys)} 个测试键")
    
    print("\n=== 基础操作示例完成 ===")

if __name__ == "__main__":
    main()