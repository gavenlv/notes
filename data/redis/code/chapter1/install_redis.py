#!/usr/bin/env python3
"""
Redis安装和配置示例

这个脚本演示如何在不同的操作系统上安装和配置Redis。
注意：实际安装需要管理员权限，这里主要提供安装指南。
"""

import platform
import subprocess
import sys

def check_redis_installation():
    """检查Redis是否已安装"""
    print("=== 检查Redis安装状态 ===")
    
    system = platform.system().lower()
    
    if system == 'windows':
        # Windows系统
        try:
            result = subprocess.run(['redis-cli', '--version'], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Redis已安装:", result.stdout.strip())
                return True
        except FileNotFoundError:
            print("❌ Redis未安装")
            return False
            
    elif system in ['linux', 'darwin']:  # Linux或macOS
        try:
            result = subprocess.run(['which', 'redis-server'], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Redis已安装，路径:", result.stdout.strip())
                
                # 获取版本信息
                version_result = subprocess.run(['redis-server', '--version'], 
                                             capture_output=True, text=True)
                print("Redis版本信息:", version_result.stdout.strip())
                return True
        except FileNotFoundError:
            print("❌ Redis未安装")
            return False
    
    else:
        print(f"❌ 不支持的操作系统: {system}")
        return False

def get_installation_guide():
    """获取安装指南"""
    print("\n=== Redis安装指南 ===")
    
    system = platform.system().lower()
    
    if system == 'windows':
        print("""
Windows系统安装Redis:

方法1: 使用Microsoft Store
1. 打开Microsoft Store
2. 搜索 "Redis"
3. 安装 "Redis" 应用

方法2: 使用Chocolatey
1. 安装Chocolatey包管理器
2. 运行: choco install redis-64

方法3: 手动安装
1. 访问 https://github.com/microsoftarchive/redis/releases
2. 下载最新版本的Redis for Windows
3. 解压并运行redis-server.exe
""")
    
    elif system == 'linux':
        print("""
Linux系统安装Redis:

Ubuntu/Debian:
1. sudo apt update
2. sudo apt install redis-server
3. sudo systemctl enable redis-server
4. sudo systemctl start redis-server

CentOS/RHEL/Fedora:
1. sudo dnf install redis  # 或 yum install redis
2. sudo systemctl enable redis
3. sudo systemctl start redis

使用Docker:
1. docker pull redis:latest
2. docker run -d -p 6379:6379 --name redis redis:latest
""")
    
    elif system == 'darwin':  # macOS
        print("""
macOS系统安装Redis:

方法1: 使用Homebrew
1. brew install redis
2. brew services start redis

方法2: 使用MacPorts
1. sudo port install redis
2. sudo port load redis

使用Docker:
1. docker pull redis:latest
2. docker run -d -p 6379:6379 --name redis redis:latest
""")
    
    else:
        print(f"不支持的操作系统: {system}")

def check_redis_running():
    """检查Redis服务是否正在运行"""
    print("\n=== 检查Redis服务状态 ===")
    
    system = platform.system().lower()
    
    if system == 'windows':
        try:
            # 检查Redis服务
            result = subprocess.run(['sc', 'query', 'Redis'], 
                                  capture_output=True, text=True)
            if 'RUNNING' in result.stdout:
                print("✅ Redis服务正在运行")
                return True
            else:
                print("❌ Redis服务未运行")
                return False
        except:
            print("❌ 无法检查Redis服务状态")
            return False
    
    elif system in ['linux', 'darwin']:
        try:
            # 检查Redis进程
            result = subprocess.run(['pgrep', 'redis-server'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Redis服务正在运行")
                return True
            else:
                print("❌ Redis服务未运行")
                return False
        except:
            print("❌ 无法检查Redis服务状态")
            return False
    
    else:
        print("❌ 不支持的操作系统")
        return False

def test_redis_connection():
    """测试Redis连接"""
    print("\n=== 测试Redis连接 ===")
    
    try:
        import redis
        
        # 尝试连接Redis
        r = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        
        # 发送PING命令
        response = r.ping()
        
        if response:
            print("✅ Redis连接测试成功")
            
            # 获取服务器信息
            info = r.info()
            print(f"Redis版本: {info.get('redis_version', 'N/A')}")
            print(f"运行模式: {info.get('redis_mode', 'N/A')}")
            print(f"已连接客户端: {info.get('connected_clients', 'N/A')}")
            
            return True
        else:
            print("❌ Redis连接测试失败")
            return False
            
    except ImportError:
        print("❌ 未安装redis-py库")
        print("请运行: pip install redis")
        return False
        
    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
        return False

def main():
    """主函数"""
    print("Redis安装和配置检查")
    print("=" * 50)
    
    # 检查Redis是否已安装
    is_installed = check_redis_installation()
    
    if not is_installed:
        print("\nRedis未安装，提供安装指南...")
        get_installation_guide()
        
        print("\n请按照上述指南安装Redis，然后重新运行此脚本。")
        return
    
    # 检查Redis服务是否运行
    is_running = check_redis_running()
    
    if not is_running:
        print("\nRedis服务未运行，尝试启动...")
        
        system = platform.system().lower()
        if system == 'windows':
            print("请手动启动Redis服务")
        elif system in ['linux', 'darwin']:
            print("可以尝试运行: sudo systemctl start redis")
    
    # 测试Redis连接
    connection_ok = test_redis_connection()
    
    if connection_ok:
        print("\n✅ Redis安装和配置检查完成，一切正常！")
    else:
        print("\n❌ Redis连接存在问题，请检查安装和配置。")
    
    print("\n=== 安装检查完成 ===")

if __name__ == "__main__":
    main()