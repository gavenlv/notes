"""
PostgreSQL第10章：监控和诊断 - Python示例
演示如何使用Python进行PostgreSQL数据库监控和诊断
"""

import psycopg2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import time
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import warnings
warnings.filterwarnings('ignore')

class PostgreSQLMonitor:
    """PostgreSQL数据库监控类"""
    
    def __init__(self, connection_params):
        """
        初始化监控器
        
        Args:
            connection_params (dict): 数据库连接参数
                {
                    'host': 'localhost',
                    'port': 5432,
                    'database': 'your_db',
                    'user': 'your_user',
                    'password': 'your_password'
                }
        """
        self.connection_params = connection_params
        self.connection = None
        self.connect()
    
    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = psycopg2.connect(**self.connection_params)
            self.connection.autocommit = True
            print("✓ 数据库连接成功")
        except Exception as e:
            print(f"✗ 数据库连接失败: {e}")
            raise
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            print("✓ 数据库连接已关闭")
    
    def execute_query(self, query, params=None):
        """执行SQL查询"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                if cursor.description:  # 如果有结果集
                    columns = [desc[0] for desc in cursor.description]
                    return pd.DataFrame(cursor.fetchall(), columns=columns)
                else:
                    return None
        except Exception as e:
            print(f"查询执行失败: {e}")
            return None
    
    # ================================================
    # 1. 系统性能监控
    # ================================================
    
    def get_database_status(self):
        """获取数据库整体状态"""
        query = """
        SELECT 
            'Database Size' as metric_name,
            pg_size_pretty(pg_database_size(current_database())) as current_value,
            CASE 
                WHEN pg_database_size(current_database()) < 100*1024*1024*1024 THEN 'GOOD'
                WHEN pg_database_size(current_database()) < 500*1024*1024*1024 THEN 'WARNING'
                ELSE 'CRITICAL'
            END as status,
            '100 GB' as threshold_value
        UNION ALL
        SELECT 
            'Active Connections',
            COUNT(*)::TEXT,
            CASE 
                WHEN COUNT(*) < 50 THEN 'GOOD'
                WHEN COUNT(*) < 100 THEN 'WARNING'
                ELSE 'CRITICAL'
            END,
            '50'
        FROM pg_stat_activity 
        WHERE state = 'active'
        UNION ALL
        SELECT 
            'Cache Hit Ratio',
            ROUND(100.0 * SUM(blks_hit) / (SUM(blks_hit) + SUM(blks_read)), 2)::TEXT || '%',
            CASE 
                WHEN (100.0 * SUM(blks_hit) / (SUM(blks_hit) + SUM(blks_read))) > 95 THEN 'GOOD'
                WHEN (100.0 * SUM(blks_hit) / (SUM(blks_hit) + SUM(blks_read))) > 90 THEN 'WARNING'
                ELSE 'CRITICAL'
            END,
            '95%'
        FROM pg_stat_database;
        """
        
        result = self.execute_query(query)
        if result is not None:
            print("数据库状态监控结果:")
            print(result.to_string(index=False))
            return result
        return None
    
    def get_system_resources(self):
        """监控系统资源使用情况（模拟）"""
        # 模拟系统资源数据
        resources = {
            'timestamp': datetime.now(),
            'cpu_usage': np.random.uniform(10, 90),
            'memory_usage': np.random.uniform(20, 85),
            'disk_usage': np.random.uniform(15, 75),
            'network_io': np.random.uniform(50, 800)
        }
        
        # 根据使用率设置告警级别
        def get_alert_level(usage, thresholds):
            if usage > thresholds['critical']:
                return 'CRITICAL'
            elif usage > thresholds['warning']:
                return 'WARNING'
            return 'NORMAL'
        
        thresholds = {
            'cpu': {'warning': 75, 'critical': 90},
            'memory': {'warning': 80, 'critical': 90},
            'disk': {'warning': 70, 'critical': 85}
        }
        
        status_data = []
        for resource, value in resources.items():
            if resource != 'timestamp':
                if resource == 'network_io':
                    alert_level = 'HIGH' if value > 400 else 'NORMAL'
                else:
                    alert_level = get_alert_level(value, thresholds.get(resource, {'warning': 70, 'critical': 85}))
                
                status_data.append({
                    'resource_type': resource.replace('_', ' ').title(),
                    'usage_value': round(value, 2),
                    'usage_unit': 'MB/s' if resource == 'network_io' else '%',
                    'alert_level': alert_level
                })
        
        df = pd.DataFrame(status_data)
        print("\n系统资源监控结果:")
        print(df.to_string(index=False))
        return df
    
    def monitor_connections(self):
        """监控数据库连接"""
        query = """
        SELECT 
            COALESCE(client_addr::TEXT, 'local') as client_ip,
            usename as user_name,
            COALESCE(application_name, 'Unknown') as application_name,
            state,
            query_start,
            EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - query_start)) as duration_seconds,
            query
        FROM pg_stat_activity
        WHERE state != 'idle'
        ORDER BY query_start
        LIMIT 20;
        """
        
        result = self.execute_query(query)
        if result is not None:
            print(f"\n当前活动连接数: {len(result)}")
            if not result.empty:
                # 显示连接状态分布
                state_counts = result['state'].value_counts()
                print("\n连接状态分布:")
                for state, count in state_counts.items():
                    print(f"  {state}: {count}")
            
            # 显示最长的查询
            if 'duration_seconds' in result.columns:
                longest_query = result.loc[result['duration_seconds'].idxmax()]
                print(f"\n最长运行查询:")
                print(f"  时长: {longest_query['duration_seconds']:.1f}秒")
                print(f"  用户: {longest_query['user_name']}")
                print(f"  应用: {longest_query['application_name']}")
        
        return result
    
    # ================================================
    # 2. 慢查询分析
    # ================================================
    
    def analyze_slow_queries(self, min_time=1000):
        """分析慢查询（需要pg_stat_statements扩展）"""
        query = """
        SELECT 
            query,
            calls,
            total_time,
            ROUND(mean_time, 2) as mean_time,
            min_time,
            max_time,
            ROUND(100.0 * total_time / NULLIF(SUM(total_time) OVER (), 0), 2) as percent_time
        FROM pg_stat_statements
        WHERE mean_time >= %s
        ORDER BY total_time DESC
        LIMIT 10;
        """
        
        try:
            result = self.execute_query(query, (min_time,))
            if result is not None and not result.empty:
                print(f"\n慢查询分析 (执行时间 >= {min_time}ms):")
                print(result.to_string(index=False))
                return result
            else:
                print(f"没有发现执行时间超过{min_time}ms的查询")
                return None
        except Exception as e:
            print(f"慢查询分析失败: {e}")
            print("请确保pg_stat_statements扩展已安装并启用")
            return None
    
    def get_query_plan_analysis(self, query_text):
        """获取查询执行计划分析"""
        try:
            # 使用EXPLAIN ANALYZE获取执行计划
            explain_query = f"EXPLAIN ANALYZE {query_text}"
            result = self.execute_query(explain_query)
            
            if result is not None:
                print(f"\n查询执行计划分析:")
                for _, row in result.iterrows():
                    print(f"  {row[0]}")
                return result
        except Exception as e:
            print(f"执行计划分析失败: {e}")
            return None
    
    def monitor_query_performance(self):
        """监控查询性能趋势"""
        # 模拟查询性能数据
        queries = [
            "SELECT * FROM orders WHERE status = 'pending'",
            "INSERT INTO users (name, email) VALUES (%s, %s)",
            "UPDATE products SET price = %s WHERE id = %s",
            "SELECT count(*) FROM events WHERE date >= %s",
            "DELETE FROM sessions WHERE expired = true"
        ]
        
        performance_data = []
        base_time = 50  # 基础执行时间(ms)
        
        for i, query in enumerate(queries):
            execution_count = np.random.randint(5000, 15000)
            avg_time = base_time + np.random.normal(0, 20)
            trend = np.random.choice(['IMPROVING', 'DEGRADING', 'STABLE'], p=[0.4, 0.3, 0.3])
            
            performance_data.append({
                'query_pattern': query[:50] + '...' if len(query) > 50 else query,
                'execution_count': execution_count,
                'avg_execution_time_ms': round(avg_time, 2),
                'trend_direction': trend,
                'performance_change_pct': round(np.random.uniform(-15, 15), 1)
            })
        
        df = pd.DataFrame(performance_data)
        print("\n查询性能趋势分析:")
        print(df.to_string(index=False))
        return df
    
    # ================================================
    # 3. 锁监控
    # ================================================
    
    def monitor_locks(self):
        """监控数据库锁状态"""
        query = """
        SELECT 
            l.locktype as lock_type,
            COALESCE(c.relname, 'Unknown') as table_name,
            l.mode as lock_mode,
            l.granted,
            a.usename as user_name,
            LEFT(a.query, 100) as query_preview,
            EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - a.query_start)) as wait_duration_seconds
        FROM pg_locks l
        LEFT JOIN pg_class c ON l.relation = c.oid
        LEFT JOIN pg_stat_activity a ON a.pid = l.pid
        WHERE NOT l.granted
        ORDER BY wait_duration_seconds DESC
        LIMIT 10;
        """
        
        result = self.execute_query(query)
        if result is not None and not result.empty:
            print(f"\n锁等待情况 (未授予的锁):")
            print(result.to_string(index=False))
            
            # 统计锁类型
            lock_counts = result['lock_type'].value_counts()
            print("\n锁类型分布:")
            for lock_type, count in lock_counts.items():
                print(f"  {lock_type}: {count}")
        else:
            print("\n当前没有锁等待情况")
        
        return result
    
    def detect_deadlocks(self):
        """检测死锁（模拟）"""
        # 死锁检测通常需要通过日志分析
        deadlock_scenarios = [
            {
                'scenario_id': 1,
                'description': 'Transaction A等待Transaction B持有的锁',
                'table_involved': 'users',
                'resolution_action': 'ROLLBACK transaction_A',
                'detection_time': datetime.now() - timedelta(minutes=5)
            },
            {
                'scenario_id': 2,
                'description': 'Transaction B等待Transaction A持有的锁',
                'table_involved': 'orders',
                'resolution_action': 'ROLLBACK transaction_B',
                'detection_time': datetime.now() - timedelta(minutes=5)
            }
        ]
        
        if deadlock_scenarios:
            df = pd.DataFrame(deadlock_scenarios)
            print(f"\n死锁检测结果:")
            print(df.to_string(index=False))
            return df
        else:
            print("\n近期未检测到死锁")
            return None
    
    # ================================================
    # 4. 表和索引监控
    # ================================================
    
    def monitor_table_sizes(self):
        """监控表大小"""
        query = """
        SELECT 
            schemaname || '.' || tablename as table_name,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
            pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as index_size,
            n_tup_ins + n_tup_upd + n_tup_del as total_changes,
            n_live_tup as live_rows,
            n_dead_tup as dead_rows
        FROM pg_stat_user_tables
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        LIMIT 20;
        """
        
        result = self.execute_query(query)
        if result is not None:
            print(f"\n表大小监控 (前20个最大表):")
            print(result.to_string(index=False))
            
            # 统计死行比例
            if 'live_rows' in result.columns and 'dead_rows' in result.columns:
                result['dead_row_ratio'] = result['dead_rows'] / (result['live_rows'] + result['dead_rows']) * 100
                high_dead_ratio = result[result['dead_row_ratio'] > 10]
                if not high_dead_ratio.empty:
                    print(f"\n需要清理的表 (死行比例 > 10%):")
                    print(high_dead_ratio[['table_name', 'dead_row_ratio']].to_string(index=False))
        
        return result
    
    def analyze_index_usage(self):
        """分析索引使用情况"""
        query = """
        SELECT 
            schemaname || '.' || relname as table_name,
            indexrelname as index_name,
            idx_scan as index_scans,
            idx_tup_read as tuples_read,
            idx_tup_fetch as tuples_fetched,
            pg_size_pretty(pg_relation_size(indexrelid)) as index_size
        FROM pg_stat_user_indexes
        ORDER BY idx_scan DESC
        LIMIT 20;
        """
        
        result = self.execute_query(query)
        if result is not None:
            print(f"\n索引使用情况分析:")
            print(result.to_string(index=False))
            
            # 标识低使用率索引
            if 'index_scans' in result.columns:
                low_usage = result[result['index_scans'] < 100]
                if not low_usage.empty:
                    print(f"\n低使用率索引 (扫描次数 < 100):")
                    print(low_usage[['index_name', 'index_scans', 'index_size']].to_string(index=False))
        
        return result
    
    def analyze_table_bloat(self):
        """分析表膨胀情况"""
        query = """
        SELECT 
            schemaname || '.' || tablename as table_name,
            n_live_tup as live_rows,
            n_dead_tup as dead_rows,
            ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) as dead_row_percentage,
            last_vacuum,
            last_autovacuum,
            last_analyze,
            last_autoanalyze
        FROM pg_stat_user_tables
        WHERE schemaname = 'public'
        ORDER BY dead_rows DESC
        LIMIT 20;
        """
        
        result = self.execute_query(query)
        if result is not None:
            print(f"\n表膨胀分析:")
            print(result.to_string(index=False))
            
            # 标识需要VACUUM的表
            if 'dead_row_percentage' in result.columns:
                needs_vacuum = result[result['dead_row_percentage'] > 20]
                if not needs_vacuum.empty:
                    print(f"\n需要VACUUM的表 (死行比例 > 20%):")
                    print(needs_vacuum[['table_name', 'dead_row_percentage', 'dead_rows']].to_string(index=False))
        
        return result
    
    # ================================================
    # 5. 健康检查
    # ================================================
    
    def comprehensive_health_check(self):
        """综合健康检查"""
        health_results = []
        
        # 检查缓存命中率
        cache_query = """
        SELECT 
            100.0 * SUM(blks_hit) / (SUM(blks_hit) + SUM(blks_read)) as cache_hit_ratio
        FROM pg_stat_database;
        """
        
        cache_result = self.execute_query(cache_query)
        if cache_result is not None and not cache_result.empty:
            cache_ratio = cache_result.iloc[0]['cache_hit_ratio']
            health_results.append({
                'category': 'Performance',
                'metric': 'Cache Hit Ratio',
                'value': f"{cache_ratio:.2f}%",
                'status': 'GOOD' if cache_ratio > 95 else 'WARNING' if cache_ratio > 90 else 'CRITICAL',
                'recommendation': 'Increase shared_buffers' if cache_ratio <= 95 else 'Cache performance optimal'
            })
        
        # 检查连接数
        connection_query = "SELECT COUNT(*) as total_connections FROM pg_stat_activity;"
        conn_result = self.execute_query(connection_query)
        if conn_result is not None:
            conn_count = conn_result.iloc[0]['total_connections']
            health_results.append({
                'category': 'Connections',
                'metric': 'Active Connections',
                'value': str(conn_count),
                'status': 'GOOD' if conn_count < 50 else 'WARNING' if conn_count < 100 else 'CRITICAL',
                'recommendation': 'Consider connection pooling' if conn_count > 80 else 'Connection usage normal'
            })
        
        # 检查数据库大小
        size_query = "SELECT pg_database_size(current_database()) / 1024.0 / 1024.0 / 1024.0 as db_size_gb;"
        size_result = self.execute_query(size_query)
        if size_result is not None:
            db_size = size_result.iloc[0]['db_size_gb']
            health_results.append({
                'category': 'Storage',
                'metric': 'Database Size',
                'value': f"{db_size:.2f} GB",
                'status': 'GOOD' if db_size < 100 else 'WARNING',
                'recommendation': 'Monitor storage usage' if db_size > 50 else 'Storage usage normal'
            })
        
        # 检查长期运行查询
        long_query_query = """
        SELECT COUNT(*) as long_running_queries
        FROM pg_stat_activity
        WHERE state = 'active' 
        AND (CURRENT_TIMESTAMP - query_start) > INTERVAL '5 minutes';
        """
        long_query_result = self.execute_query(long_query_query)
        if long_query_result is not None:
            long_queries = long_query_result.iloc[0]['long_running_queries']
            health_results.append({
                'category': 'Performance',
                'metric': 'Long Running Queries',
                'value': str(long_queries),
                'status': 'GOOD' if long_queries == 0 else 'WARNING',
                'recommendation': 'Investigate long running queries' if long_queries > 0 else 'No long running queries'
            })
        
        df = pd.DataFrame(health_results)
        print(f"\n数据库综合健康检查:")
        print(df.to_string(index=False))
        
        # 总体健康状态
        critical_count = len(df[df['status'] == 'CRITICAL'])
        warning_count = len(df[df['status'] == 'WARNING'])
        
        if critical_count > 0:
            overall_status = 'CRITICAL'
        elif warning_count > 0:
            overall_status = 'WARNING'
        else:
            overall_status = 'GOOD'
        
        print(f"\n总体健康状态: {overall_status}")
        return df
    
    # ================================================
    # 6. 告警管理
    # ================================================
    
    def check_alerts(self):
        """检查告警条件"""
        alerts = []
        
        # 检查缓存命中率
        cache_query = """
        SELECT 100.0 * SUM(blks_hit) / (SUM(blks_hit) + SUM(blks_read)) as cache_hit_ratio
        FROM pg_stat_database;
        """
        
        cache_result = self.execute_query(cache_query)
        if cache_result is not None:
            cache_ratio = cache_result.iloc[0]['cache_hit_ratio']
            if cache_ratio < 90:
                alerts.append({
                    'metric': 'Cache Hit Ratio',
                    'value': f"{cache_ratio:.2f}%",
                    'threshold': '90%',
                    'level': 'CRITICAL',
                    'message': '缓存命中率过低，可能影响性能'
                })
        
        # 检查连接数
        conn_query = "SELECT COUNT(*) as total_connections FROM pg_stat_activity;"
        conn_result = self.execute_query(conn_query)
        if conn_result is not None:
            conn_count = conn_result.iloc[0]['total_connections']
            if conn_count > 150:
                alerts.append({
                    'metric': 'Active Connections',
                    'value': str(conn_count),
                    'threshold': '150',
                    'level': 'WARNING',
                    'message': '连接数过高，考虑增加连接池'
                })
        
        # 检查死锁（通过日志分析）
        # 这里模拟死锁检测
        if np.random.random() < 0.1:  # 10%概率检测到死锁
            alerts.append({
                'metric': 'Deadlock Detection',
                'value': '1',
                'threshold': '0',
                'level': 'CRITICAL',
                'message': '检测到死锁，需要立即处理'
            })
        
        if alerts:
            df = pd.DataFrame(alerts)
            print(f"\n告警信息:")
            print(df.to_string(index=False))
        else:
            print(f"\n当前没有告警")
        
        return alerts
    
    # ================================================
    # 7. 性能基线比较
    # ================================================
    
    def compare_with_baseline(self):
        """与性能基线比较"""
        # 获取当前性能指标
        current_metrics = {}
        
        # 缓存命中率
        cache_query = "SELECT 100.0 * SUM(blks_hit) / (SUM(blks_hit) + SUM(blks_read)) as cache_hit_ratio FROM pg_stat_database;"
        result = self.execute_query(cache_query)
        if result is not None:
            current_metrics['cache_hit_ratio'] = result.iloc[0]['cache_hit_ratio']
        
        # 连接数
        conn_query = "SELECT COUNT(*) as connection_count FROM pg_stat_activity;"
        result = self.execute_query(conn_query)
        if result is not None:
            current_metrics['connection_count'] = result.iloc[0]['connection_count']
        
        # 模拟基线值
        baseline_metrics = {
            'cache_hit_ratio': 95.0,
            'connection_count': 80
        }
        
        comparison_data = []
        for metric, current_value in current_metrics.items():
            baseline_value = baseline_metrics.get(metric, 0)
            deviation = ((current_value - baseline_value) / baseline_value) * 100
            
            comparison_data.append({
                'metric': metric,
                'current_value': round(current_value, 2),
                'baseline_value': round(baseline_value, 2),
                'deviation_pct': round(deviation, 2),
                'status': 'NORMAL' if abs(deviation) < 10 else 'WARNING' if abs(deviation) < 20 else 'ALERT'
            })
        
        df = pd.DataFrame(comparison_data)
        print(f"\n性能基线比较:")
        print(df.to_string(index=False))
        return df
    
    # ================================================
    # 8. 实时监控循环
    # ================================================
    
    def start_monitoring(self, duration_minutes=10, interval_seconds=30):
        """启动实时监控"""
        print(f"开始实时监控，持续{duration_minutes}分钟，每{interval_seconds}秒采样一次...")
        
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        sample_count = 0
        
        while datetime.now() < end_time:
            sample_count += 1
            print(f"\n=== 采样 {sample_count} ({datetime.now().strftime('%H:%M:%S')}) ===")
            
            # 获取关键指标
            self.get_database_status()
            self.get_system_resources()
            self.check_alerts()
            
            # 等待下次采样
            if datetime.now() < end_time:
                print(f"等待{interval_seconds}秒...")
                time.sleep(interval_seconds)
        
        print(f"\n监控完成，共采样{sample_count}次")
    
    # ================================================
    # 9. 监控报告生成
    # ================================================
    
    def generate_monitoring_report(self):
        """生成监控报告"""
        print("正在生成综合监控报告...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'database_status': self.get_database_status().to_dict('records') if self.get_database_status() is not None else [],
            'table_sizes': self.monitor_table_sizes().to_dict('records') if self.monitor_table_sizes() is not None else [],
            'index_usage': self.analyze_index_usage().to_dict('records') if self.analyze_index_usage() is not None else [],
            'health_check': self.comprehensive_health_check().to_dict('records') if self.comprehensive_health_check() is not None else [],
            'alerts': self.check_alerts()
        }
        
        # 保存报告到JSON文件
        report_filename = f"postgresql_monitoring_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            print(f"监控报告已保存到: {report_filename}")
        except Exception as e:
            print(f"保存报告失败: {e}")
        
        return report

# ================================================
# 示例用法
# ================================================

def main():
    """主函数 - 演示监控功能"""
    
    # 数据库连接参数（请根据实际情况修改）
    connection_params = {
        'host': 'localhost',
        'port': 5432,
        'database': 'your_database',
        'user': 'your_user',
        'password': 'your_password'
    }
    
    # 创建监控器实例
    monitor = PostgreSQLMonitor(connection_params)
    
    try:
        # 演示各种监控功能
        print("=" * 60)
        print("PostgreSQL 数据库监控演示")
        print("=" * 60)
        
        # 1. 系统状态监控
        print("\n1. 数据库状态监控")
        monitor.get_database_status()
        
        # 2. 资源监控
        print("\n2. 系统资源监控")
        monitor.get_system_resources()
        
        # 3. 连接监控
        print("\n3. 连接监控")
        monitor.monitor_connections()
        
        # 4. 慢查询分析
        print("\n4. 慢查询分析")
        monitor.analyze_slow_queries(1000)  # 1000ms
        
        # 5. 锁监控
        print("\n5. 锁监控")
        monitor.monitor_locks()
        
        # 6. 表大小监控
        print("\n6. 表大小监控")
        monitor.monitor_table_sizes()
        
        # 7. 索引使用分析
        print("\n7. 索引使用分析")
        monitor.analyze_index_usage()
        
        # 8. 健康检查
        print("\n8. 综合健康检查")
        monitor.comprehensive_health_check()
        
        # 9. 告警检查
        print("\n9. 告警检查")
        monitor.check_alerts()
        
        # 10. 基线比较
        print("\n10. 性能基线比较")
        monitor.compare_with_baseline()
        
        # 11. 生成监控报告
        print("\n11. 生成监控报告")
        report = monitor.generate_monitoring_report()
        
        # 12. 实时监控（可选，取消注释启用）
        # print("\n12. 实时监控")
        # monitor.start_monitoring(duration_minutes=2, interval_seconds=10)
        
    except Exception as e:
        print(f"监控过程中发生错误: {e}")
    
    finally:
        # 关闭连接
        monitor.close()

if __name__ == "__main__":
    main()

"""
使用说明：

1. 确保PostgreSQL服务正在运行
2. 修改connection_params中的连接参数
3. 安装必要的依赖包：pip install psycopg2-binary pandas numpy matplotlib seaborn
4. 运行脚本：python monitoring_diagnostics.py

注意事项：

1. pg_stat_statements扩展：
   - 用于慢查询分析
   - 安装命令：CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

2. 监控权限：
   - 确保用户有足够的权限访问pg_stat_*视图
   - 通常这些权限会自动授予给相应角色

3. 监控频率：
   - 避免过于频繁的监控查询
   - 根据实际需要调整采样间隔

4. 数据保留：
   - 定期清理历史监控数据
   - 考虑使用专门的监控工具如Prometheus + Grafana

5. 告警设置：
   - 根据实际业务需求设置告警阈值
   - 配置多种通知方式（邮件、短信、Slack等）
"""
