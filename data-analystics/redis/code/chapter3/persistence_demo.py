#!/usr/bin/env python3
"""
Redis持久化示例

这个示例展示Redis的持久化机制，包括RDB和AOF。
"""

import redis
import time
import subprocess
import os

def main():
    """主函数 - 演示持久化机制"""
    
    print("=== Redis持久化示例 ===")
    
    # 连接到Redis
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis连接成功")
    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
        return
    
    # 1. 检查持久化配置
    print("\n1. 检查持久化配置")
    
    try:
        # 获取持久化相关配置
        config = r.config_get('save')
        aof_config = r.config_get('appendonly')
        
        print("RDB持久化配置:")
        print(f"  save配置: {config.get('save', 'N/A')}")
        
        print("AOF持久化配置:")
        print(f"  appendonly: {aof_config.get('appendonly', 'N/A')}")
        
    except Exception as e:
        print(f"获取配置失败: {e}")
    
    # 2. 模拟数据写入
    print("\n2. 模拟数据写入")
    
    # 创建测试数据
    test_data_count = 100
    
    for i in range(test_data_count):
        r.set(f'test_key_{i}', f'test_value_{i}')
        r.hset(f'test_hash_{i}', mapping={
            'field1': f'value1_{i}',
            'field2': f'value2_{i}',
            'field3': f'value3_{i}'
        })
    
    print(f"已创建 {test_data_count} 个测试键和哈希")
    
    # 3. 手动触发RDB持久化
    print("\n3. 手动触发RDB持久化")
    
    try:
        # 保存当前状态到RDB文件
        r.bgsave()  # 后台保存
        print("已触发后台RDB保存")
        
        # 等待保存完成
        time.sleep(2)
        
        # 检查最后一次保存时间
        info = r.info('persistence')
        last_save_time = info.get('rdb_last_save_time', 0)
        last_bgsave_status = info.get('rdb_last_bgsave_status', 'N/A')
        
        print(f"最后一次保存时间: {last_save_time}")
        print(f"最后一次后台保存状态: {last_bgsave_status}")
        
    except Exception as e:
        print(f"RDB保存失败: {e}")
    
    # 4. AOF持久化操作
    print("\n4. AOF持久化操作")
    
    try:
        # 检查AOF状态
        info = r.info('persistence')
        aof_enabled = info.get('aof_enabled', 0)
        aof_rewrite_in_progress = info.get('aof_rewrite_in_progress', 0)
        
        print(f"AOF是否启用: {aof_enabled}")
        print(f"AOF重写是否进行中: {aof_rewrite_in_progress}")
        
        if aof_enabled:
            # 手动触发AOF重写
            r.bgrewriteaof()
            print("已触发后台AOF重写")
            
            # 等待重写完成
            time.sleep(3)
            
            # 检查AOF文件大小
            aof_current_size = info.get('aof_current_size', 0)
            aof_base_size = info.get('aof_base_size', 0)
            
            print(f"AOF当前大小: {aof_current_size} 字节")
            print(f"AOF基础大小: {aof_base_size} 字节")
        
    except Exception as e:
        print(f"AOF操作失败: {e}")
    
    # 5. 持久化统计信息
    print("\n5. 持久化统计信息")
    
    try:
        info = r.info('persistence')
        
        print("RDB统计:")
        print(f"  最后一次保存时间: {info.get('rdb_last_save_time', 'N/A')}")
        print(f"  最后一次保存状态: {info.get('rdb_last_bgsave_status', 'N/A')}")
        print(f"  后台保存进行中: {info.get('rdb_bgsave_in_progress', 'N/A')}")
        
        print("AOF统计:")
        print(f"  AOF启用: {info.get('aof_enabled', 'N/A')}")
        print(f"  AOF重写进行中: {info.get('aof_rewrite_in_progress', 'N/A')}")
        print(f"  最后一次写入状态: {info.get('aof_last_write_status', 'N/A')}")
        print(f"  最后一次重写状态: {info.get('aof_last_bgrewrite_status', 'N/A')}")
        
    except Exception as e:
        print(f"获取统计信息失败: {e}")
    
    # 6. 数据恢复模拟
    print("\n6. 数据恢复模拟")
    
    # 验证数据完整性
    try:
        # 检查测试数据
        key_count = 0
        hash_count = 0
        
        for i in range(test_data_count):
            if r.exists(f'test_key_{i}'):
                key_count += 1
            
            if r.exists(f'test_hash_{i}'):
                hash_count += 1
        
        print(f"键数据完整性: {key_count}/{test_data_count}")
        print(f"哈希数据完整性: {hash_count}/{test_data_count}")
        
        # 验证哈希字段
        if hash_count > 0:
            sample_hash = r.hgetall(f'test_hash_0')
            print(f"示例哈希字段数量: {len(sample_hash)}")
        
    except Exception as e:
        print(f"数据验证失败: {e}")
    
    # 7. 持久化性能测试
    print("\n7. 持久化性能测试")
    
    try:
        # 测试写入性能
        start_time = time.time()
        
        for i in range(1000):
            r.set(f'perf_test_{i}', f'value_{i}')
        
        write_time = time.time() - start_time
        print(f"写入1000个键耗时: {write_time:.3f}秒")
        
        # 手动保存并测量时间
        save_start = time.time()
        r.save()  # 同步保存（会阻塞）
        save_time = time.time() - save_start
        
        print(f"同步保存耗时: {save_time:.3f}秒")
        
    except Exception as e:
        print(f"性能测试失败: {e}")
    
    # 8. 配置持久化策略
    print("\n8. 配置持久化策略")
    
    try:
        # 获取当前配置
        current_save = r.config_get('save')
        print(f"当前RDB保存策略: {current_save.get('save', 'N/A')}")
        
        # 演示配置更改（实际生产环境需谨慎）
        # r.config_set('save', '900 1 300 10 60 10000')
        # print("已更新RDB保存策略")
        
    except Exception as e:
        print(f"配置操作失败: {e}")
    
    # 9. 清理
    print("\n9. 清理测试数据")
    
    # 删除所有测试键
    test_keys = []
    for i in range(test_data_count):
        test_keys.append(f'test_key_{i}')
        test_keys.append(f'test_hash_{i}')
    
    for i in range(1000):
        test_keys.append(f'perf_test_{i}')
    
    # 分批删除避免超时
    batch_size = 100
    for i in range(0, len(test_keys), batch_size):
        batch = test_keys[i:i + batch_size]
        r.delete(*batch)
    
    print(f"已清理 {len(test_keys)} 个测试键")
    
    print("\n=== 持久化示例完成 ===")

if __name__ == "__main__":
    main()