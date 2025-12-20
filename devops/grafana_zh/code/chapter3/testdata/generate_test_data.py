#!/usr/bin/env python3
"""
测试数据生成器 - 为第3章仪表板示例生成模拟数据
"""

import time
import random
import json
from datetime import datetime, timedelta

def generate_system_metrics():
    """生成系统指标数据"""
    metrics = []
    base_time = datetime.now() - timedelta(hours=24)
    
    for i in range(288):  # 24小时，每5分钟一个数据点
        timestamp = base_time + timedelta(minutes=i*5)
        
        # CPU使用率 (20-80%)
        cpu_usage = random.uniform(20, 80)
        
        # 内存使用率 (30-70%)
        memory_usage = random.uniform(30, 70)
        
        # 磁盘使用率 (40-90%)
        disk_usage = random.uniform(40, 90)
        
        # 网络流量 (MB)
        network_rx = random.randint(100, 1000)
        network_tx = random.randint(50, 500)
        
        metrics.append({
            'timestamp': timestamp.isoformat(),
            'cpu_usage': round(cpu_usage, 2),
            'memory_usage': round(memory_usage, 2),
            'disk_usage': round(disk_usage, 2),
            'network_rx': network_rx,
            'network_tx': network_tx
        })
    
    return metrics

def generate_application_metrics():
    """生成应用指标数据"""
    applications = ['web-api', 'auth-service', 'database-service', 'cache-service']
    metrics = []
    base_time = datetime.now() - timedelta(hours=24)
    
    for i in range(144):  # 24小时，每10分钟一个数据点
        timestamp = base_time + timedelta(minutes=i*10)
        
        for app in applications:
            # 响应时间 (ms)
            response_time = random.uniform(10, 200)
            
            # 错误率 (0-5%)
            error_rate = random.uniform(0, 5)
            
            # 请求量
            request_count = random.randint(100, 1000)
            
            metrics.append({
                'timestamp': timestamp.isoformat(),
                'application': app,
                'response_time': round(response_time, 2),
                'error_rate': round(error_rate, 2),
                'request_count': request_count
            })
    
    return metrics

def generate_business_metrics():
    """生成业务指标数据"""
    products = ['Product A', 'Product B', 'Product C']
    regions = ['North America', 'Europe', 'Asia', 'Global']
    metrics = []
    base_time = datetime.now() - timedelta(days=30)
    
    for i in range(30):  # 30天数据
        timestamp = base_time + timedelta(days=i)
        
        for product in products:
            for region in regions:
                # 收入
                revenue = random.uniform(5000, 20000)
                
                # 用户数
                users = random.randint(500, 5000)
                
                # 转化率
                conversion_rate = random.uniform(0.01, 0.05)
                
                metrics.append({
                    'timestamp': timestamp.isoformat(),
                    'product': product,
                    'region': region,
                    'revenue': round(revenue, 2),
                    'users': users,
                    'conversion_rate': round(conversion_rate, 4)
                })
    
    return metrics

def main():
    """主函数"""
    print("开始生成测试数据...")
    
    # 生成各类数据
    system_metrics = generate_system_metrics()
    application_metrics = generate_application_metrics()
    business_metrics = generate_business_metrics()
    
    # 保存数据到文件
    with open('system_metrics.json', 'w') as f:
        json.dump(system_metrics, f, indent=2)
    
    with open('application_metrics.json', 'w') as f:
        json.dump(application_metrics, f, indent=2)
    
    with open('business_metrics.json', 'w') as f:
        json.dump(business_metrics, f, indent=2)
    
    print(f"生成完成:")
    print(f"- 系统指标: {len(system_metrics)} 条记录")
    print(f"- 应用指标: {len(application_metrics)} 条记录")
    print(f"- 业务指标: {len(business_metrics)} 条记录")
    print("数据文件已保存到当前目录")

if __name__ == "__main__":
    main()