#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MySQL监控与运维工具

本模块提供MySQL监控和运维的各种实用工具，包括：
1. 性能指标监控
2. 健康检查工具
3. 慢查询分析器
4. 二进制日志分析器
5. 容量规划工具
6. 故障转移管理器
"""

import argparse
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import pymysql
import requests
from mysql.connector import Error

# 设置中文字体，防止图表中文显示乱码
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class MySQLPerformanceMonitor:
    """MySQL性能指标监控器"""
    
    def __init__(self, host='localhost', user='root', password='', port=3306, socket=None):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.socket = socket
        self.connection = None
        self.connect()
    
    def connect(self) -> bool:
        """连接到MySQL服务器"""
        try:
            if self.socket:
                self.connection = pymysql.connect(
                    unix_socket=self.socket,
                    user=self.user,
                    password=self.password
                )
            else:
                self.connection = pymysql.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    port=self.port
                )
            return True
        except Exception as e:
            print(f"连接失败: {str(e)}")
            return False
    
    def get_basic_metrics(self) -> Dict:
        """获取基础性能指标"""
        if not self.connection:
            return {}
        
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            
            # 获取基础指标
            cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
            threads_connected = cursor.fetchone()["Value"]
            
            cursor.execute("SHOW STATUS LIKE 'Threads_running'")
            threads_running = cursor.fetchone()["Value"]
            
            cursor.execute("SHOW STATUS LIKE 'Connections'")
            connections = cursor.fetchone()["Value"]
            
            cursor.execute("SHOW STATUS LIKE 'Max_used_connections'")
            max_used_connections = cursor.fetchone()["Value"]
            
            cursor.execute("SHOW GLOBAL STATUS LIKE 'Com_select'")
            com_select = cursor.fetchone()["Value"]
            
            cursor.execute("SHOW GLOBAL STATUS LIKE 'Com_insert'")
            com_insert = cursor.fetchone()["Value"]
            
            cursor.execute("SHOW GLOBAL STATUS LIKE 'Com_update'")
            com_update = cursor.fetchone()["Value"]
            
            cursor.execute("SHOW GLOBAL STATUS LIKE 'Com_delete'")
            com_delete = cursor.fetchone()["Value"]
            
            cursor.execute("SHOW GLOBAL STATUS LIKE 'Uptime'")
            uptime = cursor.fetchone()["Value"]
            
            # 计算QPS/TPS
            if int(uptime) > 0:
                qps = round(int(com_select) / int(uptime), 2)
                tps = round((int(com_insert) + int(com_update) + int(com_delete)) / int(uptime), 2)
            else:
                qps = 0
                tps = 0
            
            return {
                "timestamp": datetime.now().isoformat(),
                "threads_connected": int(threads_connected),
                "threads_running": int(threads_running),
                "connections": int(connections),
                "max_used_connections": int(max_used_connections),
                "qps": qps,
                "tps": tps,
                "com_select": int(com_select),
                "com_insert": int(com_insert),
                "com_update": int(com_update),
                "com_delete": int(com_delete),
                "uptime": int(uptime)
            }
        except Exception as e:
            print(f"获取基础指标失败: {str(e)}")
            return {}
    
    def get_buffer_pool_metrics(self) -> Dict:
        """获取InnoDB缓冲池指标"""
        if not self.connection:
            return {}
        
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            
            # 获取缓冲池相关指标
            cursor.execute("SHOW STATUS LIKE 'Innodb_buffer_pool_pages_data'")
            buffer_pool_pages_data = cursor.fetchone()["Value"]
            
            cursor.execute("SHOW STATUS LIKE 'Innodb_buffer_pool_pages_total'")
            buffer_pool_pages_total = cursor.fetchone()["Value"]
            
            cursor.execute("SHOW STATUS LIKE 'Innodb_buffer_pool_reads'")
            buffer_pool_reads = cursor.fetchone()["Value"]
            
            cursor.execute("SHOW STATUS LIKE 'Innodb_buffer_pool_read_requests'")
            buffer_pool_read_requests = cursor.fetchone()["Value"]
            
            # 计算缓冲池命中率
            if int(buffer_pool_read_requests) > 0:
                hit_rate = 100 - (int(buffer_pool_reads) / int(buffer_pool_read_requests)) * 100
                hit_rate = round(hit_rate, 2)
            else:
                hit_rate = 100
            
            return {
                "buffer_pool_pages_data": int(buffer_pool_pages_data),
                "buffer_pool_pages_total": int(buffer_pool_pages_total),
                "buffer_pool_usage_percent": round(
                    int(buffer_pool_pages_data) / int(buffer_pool_pages_total) * 100, 2
                ),
                "buffer_pool_reads": int(buffer_pool_reads),
                "buffer_pool_read_requests": int(buffer_pool_read_requests),
                "hit_rate": hit_rate
            }
        except Exception as e:
            print(f"获取缓冲池指标失败: {str(e)}")
            return {}
    
    def get_replication_metrics(self) -> Dict:
        """获取复制状态指标"""
        if not self.connection:
            return {}
        
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            
            # 检查是否为从库
            try:
                cursor.execute("SHOW SLAVE STATUS")
                slave_status = cursor.fetchone()
                
                if slave_status:
                    return {
                        "is_slave": True,
                        "slave_io_running": slave_status["Slave_IO_Running"],
                        "slave_sql_running": slave_status["Slave_SQL_Running"],
                        "seconds_behind_master": slave_status["Seconds_Behind_Master"],
                        "master_log_file": slave_status["Master_Log_File"],
                        "relay_master_log_file": slave_status["Relay_Master_Log_File"],
                        "read_master_log_pos": slave_status["Read_Master_Log_Pos"],
                        "exec_master_log_pos": slave_status["Exec_Master_Log_Pos"]
                    }
            except:
                pass
            
            # 检查是否为主库
            try:
                cursor.execute("SHOW MASTER STATUS")
                master_status = cursor.fetchone()
                
                if master_status:
                    return {
                        "is_master": True,
                        "master_log_file": master_status["File"],
                        "master_log_position": master_status["Position"],
                        "binlog_file_size": master_status.get("File_size", 0)
                    }
            except:
                pass
            
            return {}
        except Exception as e:
            print(f"获取复制指标失败: {str(e)}")
            return {}
    
    def close(self):
        """关闭连接"""
        if self.connection:
            self.connection.close()


class SlowQueryAnalyzer:
    """慢查询日志分析器"""
    
    def __init__(self, log_file):
        self.log_file = log_file
        self.queries = []
        self.parse_log()
    
    def parse_log(self):
        """解析慢查询日志"""
        try:
            with open(self.log_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            with open(self.log_file, 'r', encoding='latin-1', errors='ignore') as f:
                content = f.read()
        
        # MySQL 5.7+ 格式的慢查询日志
        pattern = r"""# Time: (\d{6}\s+\d{2}:\d{2}:\d{2})
        # User@Host: (.*?) \[(.*?)\] @ (.*?) \[(.*?)\]
        # Thread_id: (\d+)\s+Schema: (.*?)\s+Last_errno: (\d+)\s+Killed: (\d+)
        # Query_time: (\d+\.\d+)\s+Lock_time: (\d+\.\d+)\s+Rows_sent: (\d+)\s+Rows_examined: (\d+)\s+Rows_affected: (\d+)
        (.*?)(?=# Time:|$)"""
        
        matches = re.findall(pattern, content, re.DOTALL)
        
        for match in matches:
            query = {
                "time": match[0],
                "user": match[1],
                "current_user": match[2],
                "host": match[3],
                "ip": match[4],
                "thread_id": int(match[5]),
                "schema": match[6],
                "last_errno": int(match[7]),
                "killed": int(match[8]),
                "query_time": float(match[9]),
                "lock_time": float(match[10]),
                "rows_sent": int(match[11]),
                "rows_examined": int(match[12]),
                "rows_affected": int(match[13]),
                "sql": match[14].strip(),
                "date": datetime.strptime(match[0], "%y%m%d %H:%M:%S")
            }
            
            # 简单的SQL类型分析
            sql_lower = query["sql"].lower()
            if sql_lower.startswith("select"):
                query["type"] = "SELECT"
            elif sql_lower.startswith("insert"):
                query["type"] = "INSERT"
            elif sql_lower.startswith("update"):
                query["type"] = "UPDATE"
            elif sql_lower.startswith("delete"):
                query["type"] = "DELETE"
            else:
                query["type"] = "OTHER"
            
            self.queries.append(query)
    
    def get_top_slow_queries(self, n=10):
        """获取最慢的查询"""
        return sorted(self.queries, key=lambda x: x['query_time'], reverse=True)[:n]
    
    def get_most_frequent_queries(self, n=10):
        """获取最频繁的查询（按SQL模板）"""
        normalized_queries = Counter()
        query_details = {}
        
        for query in self.queries:
            # 简单的查询标准化（去除数字）
            import re
            normalized_sql = re.sub(r'\d+', 'N', query["sql"]).strip()
            
            normalized_queries[normalized_sql] += 1
            
            if normalized_sql not in query_details:
                query_details[normalized_sql] = {
                    "type": query["type"],
                    "example_sql": query["sql"],
                    "total_time": 0,
                    "max_time": 0,
                    "avg_rows_examined": 0,
                    "count": 0
                }
            
            details = query_details[normalized_sql]
            details["total_time"] += query["query_time"]
            if query["query_time"] > details["max_time"]:
                details["max_time"] = query["query_time"]
            details["avg_rows_examined"] += query["rows_examined"]
            details["count"] += 1
        
        # 计算平均值
        for details in query_details.values():
            details["avg_time"] = details["total_time"] / details["count"]
            details["avg_rows_examined"] = details["avg_rows_examined"] / details["count"]
        
        # 按频率排序
        top_frequent = []
        for normalized_sql, count in normalized_queries.most_common(n):
            details = query_details[normalized_sql]
            details["normalized_sql"] = normalized_sql
            details["count"] = count
            top_frequent.append(details)
        
        return top_frequent
    
    def get_queries_by_type(self):
        """按查询类型分组"""
        type_stats = {}
        type_times = defaultdict(list)
        
        for query in self.queries:
            query_type = query["type"]
            query_time = query["query_time"]
            
            if query_type not in type_stats:
                type_stats[query_type] = 0
            type_stats[query_type] += 1
            type_times[query_type].append(query_time)
        
        # 计算时间统计
        result = {}
        for query_type, count in type_stats.items():
            times = type_times[query_type]
            result[query_type] = {
                "count": count,
                "total_time": sum(times),
                "avg_time": sum(times) / len(times),
                "max_time": max(times),
                "min_time": min(times)
            }
        
        return result
    
    def get_hourly_distribution(self):
        """获取按小时分布的查询数"""
        hourly_stats = defaultdict(int)
        
        for query in self.queries:
            hour = query["date"].hour
            hourly_stats[hour] += 1
        
        # 转换为24小时的完整分布
        full_hourly = []
        for hour in range(24):
            full_hourly.append({
                "hour": hour,
                "count": hourly_stats[hour]
            })
        
        return full_hourly
    
    def generate_report(self, output_file=None):
        """生成分析报告"""
        if not self.queries:
            print("慢查询日志中没有找到查询记录")
            return {}
        
        top_slow = self.get_top_slow_queries()
        most_frequent = self.get_most_frequent_queries()
        type_stats = self.get_queries_by_type()
        hourly_stats = self.get_hourly_distribution()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_slow_queries": len(self.queries),
                "date_range": {
                    "start": min(q["date"] for q in self.queries).isoformat(),
                    "end": max(q["date"] for q in self.queries).isoformat()
                }
            },
            "top_slow_queries": top_slow,
            "most_frequent_queries": most_frequent,
            "query_type_distribution": type_stats,
            "hourly_distribution": hourly_stats
        }
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
        
        return report


class MySQLHealthChecker:
    """MySQL健康检查器"""
    
    def __init__(self, host='localhost', user='root', password='', port=3306, socket=None):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.socket = socket
        self.connection = None
        self.health_status = {
            'timestamp': datetime.now().isoformat(),
            'status': 'unknown',
            'checks': {
                'connection': {'status': 'unknown'},
                'connections': {'status': 'unknown'},
                'replication': {'status': 'unknown'},
                'disk_space': {'status': 'unknown'},
                'slow_queries': {'status': 'unknown'}
            }
        }
    
    def connect(self) -> bool:
        """连接到MySQL服务器"""
        try:
            if self.socket:
                self.connection = pymysql.connect(
                    unix_socket=self.socket,
                    user=self.user,
                    password=self.password
                )
            else:
                self.connection = pymysql.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    port=self.port
                )
            return True
        except Exception as e:
            self.health_status['status'] = 'error'
            self.health_status['checks']['connection'] = {
                'status': 'critical',
                'message': f"连接失败: {str(e)}"
            }
            return False
    
    def check_connection(self):
        """检查数据库连接"""
        if not self.connection:
            self.health_status['checks']['connection'] = {
                'status': 'critical',
                'message': "数据库连接不可用"
            }
            return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            
            if result[0] == 1:
                self.health_status['checks']['connection'] = {
                    'status': 'ok',
                    'message': "数据库连接正常"
                }
                return True
            else:
                self.health_status['checks']['connection'] = {
                    'status': 'critical',
                    'message': "数据库查询结果异常"
                }
                return False
        except Exception as e:
            self.health_status['checks']['connection'] = {
                'status': 'critical',
                'message': f"连接检查失败: {str(e)}"
            }
            return False
    
    def check_connections(self):
        """检查连接数"""
        if not self.connection:
            self.health_status['checks']['connections'] = {
                'status': 'critical',
                'message': "数据库连接不可用"
            }
            return False
        
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            
            # 获取连接数相关指标
            cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
            threads_connected = cursor.fetchone()["Value"]
            
            cursor.execute("SHOW STATUS LIKE 'Threads_running'")
            threads_running = cursor.fetchone()["Value"]
            
            cursor.execute("SHOW VARIABLES LIKE 'max_connections'")
            max_connections = cursor.fetchone()["Value"]
            
            # 计算连接使用率
            connection_usage = round(int(threads_connected) / int(max_connections) * 100, 2)
            
            # 判断连接状态
            status = "ok"
            if connection_usage > 90:
                status = 'critical'
            elif connection_usage > 80:
                status = 'warning'
            
            self.health_status['checks']['connections'] = {
                'status': status,
                'max_connections': int(max_connections),
                'threads_connected': int(threads_connected),
                'threads_running': int(threads_running),
                'usage_percent': connection_usage,
                'message': f"当前连接数 {threads_connected}，最大连接数 {max_connections}"
            }
            
            return status != 'critical'
        except Exception as e:
            self.health_status['checks']['connections'] = {
                'status': 'critical',
                'message': f"连接检查失败: {str(e)}"
            }
            return False
    
    def check_replication(self):
        """检查复制状态"""
        if not self.connection:
            self.health_status['checks']['replication'] = {
                'status': 'critical',
                'message': "数据库连接不可用"
            }
            return False
        
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            
            # 检查是否为从库
            try:
                cursor.execute("SHOW SLAVE STATUS")
                slave_status = cursor.fetchone()
                
                if slave_status:
                    io_running = slave_status['Slave_IO_Running']
                    sql_running = slave_status['Slave_SQL_Running']
                    seconds_behind = slave_status.get('Seconds_Behind_Master', 0)
                    
                    if io_running == 'Yes' and sql_running == 'Yes':
                        if seconds_behind is not None and seconds_behind <= 30:
                            status = 'ok'
                            message = f"从库复制正常，延迟 {seconds_behind} 秒"
                        else:
                            status = 'warning'
                            if seconds_behind is None:
                                message = "从库复制状态未知"
                            else:
                                message = f"从库复制延迟过高: {seconds_behind} 秒"
                    else:
                        status = 'critical'
                        message = f"从库复制异常: IO={io_running}, SQL={sql_running}"
                    
                    self.health_status['checks']['replication'] = {
                        'status': status,
                        'io_running': io_running,
                        'sql_running': sql_running,
                        'seconds_behind': seconds_behind,
                        'message': message
                    }
                    
                    return status != 'critical'
            except:
                pass
            
            # 检查是否为主库
            try:
                cursor.execute("SHOW MASTER STATUS")
                master_status = cursor.fetchone()
                
                if master_status:
                    self.health_status['checks']['replication'] = {
                        'status': 'info',
                        'message': "运行在主库模式，无从库信息"
                    }
            except:
                pass
            
            # 未找到复制信息
            if 'message' not in self.health_status['checks']['replication']:
                self.health_status['checks']['replication'] = {
                    'status': 'info',
                    'message': "未配置复制"
                }
            
            return True
        except Exception as e:
            self.health_status['checks']['replication'] = {
                'status': 'critical',
                'message': f"复制检查失败: {str(e)}"
            }
            return False
    
    def check_disk_space(self):
        """检查磁盘空间"""
        if not self.connection:
            self.health_status['checks']['disk_space'] = {
                'status': 'critical',
                'message': "数据库连接不可用"
            }
            return False
        
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            
            # 获取数据目录
            cursor.execute("SHOW VARIABLES LIKE 'datadir'")
            datadir = cursor.fetchone()["Value"]
            
            # 检查磁盘使用情况
            total, used, free = shutil.disk_usage(datadir)
            
            # 计算使用率
            usage_percent = round(used / total * 100, 2)
            
            # 判断状态
            status = "ok"
            if usage_percent > 90:
                status = 'critical'
            elif usage_percent > 80:
                status = 'warning'
            
            self.health_status['checks']['disk_space'] = {
                'status': status,
                'datadir': datadir,
                'total_gb': round(total / (1024**3), 2),
                'used_gb': round(used / (1024**3), 2),
                'free_gb': round(free / (1024**3), 2),
                'usage_percent': usage_percent,
                'message': f"磁盘使用率 {usage_percent}%，剩余空间 {round(free / (1024**3), 2)}GB"
            }
            
            return status != 'critical'
        except Exception as e:
            self.health_status['checks']['disk_space'] = {
                'status': 'critical',
                'message': f"磁盘空间检查失败: {str(e)}"
            }
            return False
    
    def check_slow_queries(self):
        """检查慢查询"""
        if not self.connection:
            self.health_status['checks']['slow_queries'] = {
                'status': 'critical',
                'message': "数据库连接不可用"
            }
            return False
        
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            
            # 获取慢查询日志配置
            cursor.execute("SHOW VARIABLES LIKE 'slow_query_log'")
            slow_query_log = cursor.fetchone()["Value"]
            
            # 获取慢查询数量
            cursor.execute("SHOW GLOBAL STATUS LIKE 'Slow_queries'")
            slow_queries = cursor.fetchone()["Value"]
            
            # 获取系统运行时间，计算慢查询率
            cursor.execute("SHOW GLOBAL STATUS LIKE 'Uptime'")
            uptime = cursor.fetchone()["Value"]
            
            slow_query_rate = round(int(slow_queries) / int(uptime) * 3600, 2)  # 每小时慢查询数
            
            # 判断状态
            status = "ok"
            if slow_query_log == "OFF":
                status = 'warning'
                message = "慢查询日志未开启"
            elif slow_query_rate > 10:
                status = 'warning'
                message = f"慢查询率较高: {slow_query_rate}/小时"
            else:
                message = f"慢查询正常: {slow_query_rate}/小时"
            
            self.health_status['checks']['slow_queries'] = {
                'status': status,
                'slow_queries': int(slow_queries),
                'slow_query_log': slow_query_log,
                'slow_query_rate': slow_query_rate,
                'message': message
            }
            
            return status != 'critical'
        except Exception as e:
            self.health_status['checks']['slow_queries'] = {
                'status': 'critical',
                'message': f"慢查询检查失败: {str(e)}"
            }
            return False
    
    def run_all_checks(self):
        """运行所有健康检查"""
        # 连接数据库
        if not self.connect():
            return self.health_status
        
        # 执行各项检查
        self.check_connection()
        self.check_connections()
        self.check_replication()
        self.check_disk_space()
        self.check_slow_queries()
        
        # 确定总体状态
        worst_status = 'ok'
        for check_name, check_result in self.health_status['checks'].items():
            if check_result['status'] == 'critical':
                worst_status = 'critical'
                break
            elif check_result['status'] == 'warning' and worst_status != 'critical':
                worst_status = 'warning'
        
        self.health_status['status'] = worst_status
        
        return self.health_status
    
    def close(self):
        """关闭连接"""
        if self.connection:
            self.connection.close()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='MySQL监控与运维工具')
    parser.add_argument('--mode', choices=['monitor', 'health', 'slow_query'], 
                       default='monitor', help='运行模式')
    parser.add_argument('--host', default='localhost', help='MySQL服务器地址')
    parser.add_argument('--port', type=int, default=3306, help='MySQL服务器端口')
    parser.add_argument('--user', default='root', help='MySQL用户名')
    parser.add_argument('--password', default='', help='MySQL密码')
    parser.add_argument('--socket', help='MySQL Socket文件路径')
    parser.add_argument('--count', type=int, default=1, help='监控次数')
    parser.add_argument('--interval', type=int, default=60, help='监控间隔(秒)')
    parser.add_argument('--slow_query_log', help='慢查询日志文件路径')
    parser.add_argument('--output', help='输出文件路径')
    
    args = parser.parse_args()
    
    if args.mode == 'monitor':
        """性能监控模式"""
        monitor = MySQLPerformanceMonitor(
            host=args.host,
            user=args.user,
            password=args.password,
            port=args.port,
            socket=args.socket
        )
        
        for i in range(args.count):
            basic_metrics = monitor.get_basic_metrics()
            buffer_metrics = monitor.get_buffer_pool_metrics()
            replication_metrics = monitor.get_replication_metrics()
            
            print(f"===== 监控报告 #{i+1} =====")
            print(f"时间: {basic_metrics.get('timestamp')}")
            print(f"连接数: {basic_metrics.get('threads_connected')}")
            print(f"活跃线程: {basic_metrics.get('threads_running')}")
            print(f"QPS: {basic_metrics.get('qps')}")
            print(f"TPS: {basic_metrics.get('tps')}")
            print(f"缓冲池命中率: {buffer_metrics.get('hit_rate'):.2f}%")
            
            if replication_metrics:
                if replication_metrics.get('is_slave'):
                    print(f"从库状态: IO={replication_metrics.get('slave_io_running')}, "
                          f"SQL={replication_metrics.get('slave_sql_running')}")
                    print(f"复制延迟: {replication_metrics.get('seconds_behind_master')} 秒")
                elif replication_metrics.get('is_master'):
                    print(f"主库状态: 二进制日志 {replication_metrics.get('master_log_file')}")
            
            print("")
            
            if i < args.count - 1:
                time.sleep(args.interval)
        
        monitor.close()
        
    elif args.mode == 'health':
        """健康检查模式"""
        checker = MySQLHealthChecker(
            host=args.host,
            user=args.user,
            password=args.password,
            port=args.port,
            socket=args.socket
        )
        
        health_status = checker.run_all_checks()
        
        # 输出结果
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(health_status, f, indent=2, default=str)
            print(f"健康检查结果已保存到 {args.output}")
        else:
            print(json.dumps(health_status, indent=2, default=str))
        
        # 根据总体状态设置退出代码
        exit_code = 0
        if health_status['status'] == 'critical':
            exit_code = 2
        elif health_status['status'] == 'warning':
            exit_code = 1
        
        checker.close()
        return exit_code
        
    elif args.mode == 'slow_query':
        """慢查询分析模式"""
        if not args.slow_query_log:
            print("错误: 慢查询分析模式需要指定 --slow_query_log 参数")
            return 1
        
        analyzer = SlowQueryAnalyzer(args.slow_query_log)
        report = analyzer.generate_report(args.output)
        
        # 打印报告摘要
        print("=== 慢查询分析报告 ===")
        print(f"总慢查询数: {report['summary']['total_slow_queries']}")
        
        # 显示最慢的查询
        print("\n最慢的5个查询:")
        for i, query in enumerate(report['top_slow_queries'][:5], 1):
            print(f"{i}. 类型={query['type']}, 耗时={query['query_time']}s, "
                  f"SQL={query['sql'][:50]}...")
        
        # 显示查询类型分布
        print("\n查询类型分布:")
        for query_type, stats in report['query_type_distribution'].items():
            print(f"  {query_type}: 数量={stats['count']}, "
                  f"平均耗时={stats['avg_time']:.2f}s")
        
        # 保存完整报告
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"\n完整报告已保存到 {args.output}")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())