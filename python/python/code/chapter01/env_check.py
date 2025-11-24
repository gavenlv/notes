#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
env_check.py - Python环境检查工具
检查Python版本、已安装的库等信息
"""

import sys
import platform

def print_header(title):
    """打印格式化的标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def check_python_version():
    """检查Python版本"""
    print_header("Python环境信息")
    
    print(f"Python版本: {sys.version}")
    print(f"Python解释器路径: {sys.executable}")
    print(f"Python版本信息: {sys.version_info}")
    
    # 检查版本是否 >= 3.8
    if sys.version_info >= (3, 8):
        print("✓ Python版本符合要求 (>= 3.8)")
    else:
        print("✗ Python版本过低,建议升级到3.8或更高版本")

def check_system_info():
    """检查系统信息"""
    print_header("系统信息")
    
    print(f"操作系统: {platform.system()}")
    print(f"系统版本: {platform.release()}")
    print(f"系统架构: {platform.machine()}")
    print(f"处理器: {platform.processor()}")
    print(f"Python实现: {platform.python_implementation()}")

def check_libraries():
    """检查常用库是否安装"""
    print_header("已安装的常用库")
    
    libraries = [
        'pip',
        'numpy',
        'pandas',
        'matplotlib',
        'requests',
        'flask',
        'django',
        'jupyter',
        'pytest'
    ]
    
    installed_count = 0
    
    for lib in libraries:
        try:
            module = __import__(lib)
            version = getattr(module, '__version__', '未知版本')
            print(f"✓ {lib:20s} {version}")
            installed_count += 1
        except ImportError:
            print(f"✗ {lib:20s} 未安装")
    
    print(f"\n已安装: {installed_count}/{len(libraries)} 个库")

def check_pip():
    """检查pip信息"""
    print_header("pip信息")
    
    import subprocess
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', '--version'],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        
        print("✓ pip可用")
    except Exception as e:
        print(f"✗ pip检查失败: {e}")

def main():
    """主函数"""
    print("\n" + "🐍" * 30)
    print(" " * 20 + "Python环境检查工具")
    print("🐍" * 30)
    
    check_python_version()
    check_system_info()
    check_pip()
    check_libraries()
    
    print("\n" + "=" * 60)
    print("  检查完成!")
    print("=" * 60 + "\n")

if __name__ == '__main__':
    main()
