#!/usr/bin/env python3
"""
Redis教程 - 运行所有示例代码

这个脚本会按顺序运行所有章节的示例代码，展示Redis的完整功能。
"""

import os
import sys
import importlib.util
import time
from pathlib import Path

def run_chapter(chapter_dir, chapter_name):
    """运行指定章节的所有Python文件"""
    print(f"\n{'='*60}")
    print(f"运行第{chapter_name}章示例")
    print(f"{'='*60}")
    
    chapter_path = Path(chapter_dir)
    
    if not chapter_path.exists():
        print(f"警告：章节目录 {chapter_dir} 不存在")
        return
    
    # 获取所有Python文件
    py_files = sorted([f for f in chapter_path.glob("*.py") if f.name != "__init__.py"])
    
    if not py_files:
        print(f"章节 {chapter_name} 没有Python示例文件")
        return
    
    for py_file in py_files:
        print(f"\n执行: {py_file.name}")
        print("-" * 40)
        
        try:
            # 动态导入并执行模块
            spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 如果模块有main函数，则执行
            if hasattr(module, 'main'):
                module.main()
            
            time.sleep(1)  # 短暂暂停，便于观察输出
            
        except Exception as e:
            print(f"执行 {py_file.name} 时出错: {e}")
            continue

def main():
    """主函数"""
    print("Redis从入门到专家 - 完整示例运行")
    print("=" * 60)
    
    # 章节目录映射
    chapters = {
        "chapter1": "Redis简介与安装",
        "chapter2": "Redis数据结构与命令", 
        "chapter3": "Redis持久化与复制",
        "chapter4": "Redis高级特性与事务",
        "chapter5": "Redis集群与高可用",
        "chapter6": "Redis性能优化与监控",
        "chapter7": "Redis应用场景与最佳实践"
    }
    
    # 检查Redis连接
    print("检查Redis连接...")
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis连接正常")
    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
        print("请确保Redis服务正在运行")
        return
    
    # 运行所有章节
    for chapter_dir, chapter_name in chapters.items():
        run_chapter(chapter_dir, chapter_name)
    
    print(f"\n{'='*60}")
    print("所有示例运行完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()