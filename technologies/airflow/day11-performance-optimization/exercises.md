# Day 11: Airflow性能优化实践练习

## 概述

本练习旨在通过实际操作加深对Airflow性能优化技术的理解和掌握。通过完成以下练习，你将能够：
- 识别和分析Airflow性能瓶颈
- 调整配置参数优化系统性能
- 实现监控和告警机制
- 应用最佳实践提升系统稳定性

## 基础练习

### 练习1: 配置参数调优

#### 目标
调整Airflow核心配置参数，观察系统性能变化，找到最优配置组合。

#### 步骤
1. 备份当前Airflow配置文件
2. 调整以下参数并记录初始值：
   - `parallelism`: 并发任务数
   - `max_active_runs_per_dag`: DAG最大并发运行数
   - `dag_concurrency`: DAG并发任务数
3. 创建测试DAG执行性能基准测试
4. 逐步调整参数并记录性能变化
5. 分析结果找到最优配置

#### 代码示例
```python
# test_performance_dag.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import time
import random

def cpu_intensive_task(**kwargs):
    """模拟CPU密集型任务"""
    # 模拟计算密集型操作
    start_time = time.time()
    result = sum(i * i for i in range(1000000))
    execution_time = time.time() - start_time
    print(f"Task completed in {execution_time:.2f} seconds")
    return result

def io_intensive_task(**kwargs):
    """模拟I/O密集型任务"""
    # 模拟I/O操作
    time.sleep(random.uniform(1, 3))
    return "IO task completed"

# 定义DAG
dag = DAG(
    'performance_test_dag',
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
        'start_date': datetime(2024, 1, 1),
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    description='Performance test DAG',
    schedule_interval=None,
    catchup=False,
    tags=['performance', 'test'],
)

# 创建任务
cpu_task = PythonOperator(
    task_id='cpu_intensive_task',
    python_callable=cpu_intensive_task,
    dag=dag,
)

io_task = PythonOperator(
    task_id='io_intensive_task',
    python_callable=io_intensive_task,
    dag=dag,
)

# 设置任务依赖
cpu_task >> io_task
```

#### 性能测试脚本
```python
# performance_benchmark.py
import time
import subprocess
import json
from datetime import datetime

def run_performance_test(dag_id, num_runs=5):
    """运行性能测试"""
    results = []
    
    for i in range(num_runs):
        print(f"Running test {i+1}/{num_runs}")
        
        start_time = time.time()
        
        # 触发DAG执行
        result = subprocess.run([
            'airflow', 'dags', 'trigger', dag_id
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error triggering DAG: {result.stderr}")
            continue
            
        # 等待DAG执行完成
        time.sleep(30)  # 简单等待，实际应检查状态
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        results.append({
            'run': i+1,
            'execution_time': execution_time,
            'timestamp': datetime.now().isoformat()
        })
        
        print(f"Execution time: {execution_time:.2f} seconds")
        time.sleep(10)  # 运行间隔
    
    return results

def analyze_results(results):
    """分析测试结果"""
    if not results:
        print("No results to analyze")
        return
        
    execution_times = [r['execution_time'] for r in results]
    avg_time = sum(execution_times) / len(execution_times)
    min_time = min(execution_times)
    max_time = max(execution_times)
    
    print(f"\nPerformance Analysis:")
    print(f"Average execution time: {avg_time:.2f}s")
    print(f"Min execution time: {min_time:.2f}s")
    print(f"Max execution time: {max_time:.2f}s")
    
    return {
        'average': avg_time,
        'min': min_time,
        'max': max_time,
        'results': results
    }

# 运行测试
if __name__ == "__main__":
    dag_id = "performance_test_dag"
    results = run_performance_test(dag_id)
    analysis = analyze_results(results)
    
    # 保存结果
    with open('performance_results.json', 'w') as f:
        json.dump(analysis, f, indent=2)
```

### 练习2: 执行器性能对比

#### 目标
搭建不同执行器环境，对比执行效率和资源消耗。

#### 步骤
1. 配置SequentialExecutor环境
2. 配置LocalExecutor环境
3. 配置CeleryExecutor环境（可选）
4. 使用相同测试DAG在不同环境中执行
5. 记录并对比执行时间、资源使用情况

#### 配置示例

**SequentialExecutor配置**:
```ini
# airflow.cfg
[core]
executor = SequentialExecutor

[database]
sql_alchemy_conn = sqlite:///./airflow.db
```

**LocalExecutor配置**:
```ini
# airflow.cfg
[core]
executor = LocalExecutor

[database]
sql_alchemy_conn = postgresql+psycopg2://airflow:airflow@localhost:5432/airflow
```

**CeleryExecutor配置**:
```ini
# airflow.cfg
[core]
executor = CeleryExecutor

[celery]
broker_url = redis://localhost:6379/0
result_backend = redis://localhost:6379/0
worker_concurrency = 4
```

## 进阶练习

### 练习3: 数据库优化实践

#### 目标
优化元数据库配置和查询，提升系统响应速度。

#### 步骤
1. 分析当前数据库性能瓶颈
2. 添加推荐索引
3. 优化慢查询
4. 调整连接池配置
5. 验证优化效果

#### SQL脚本
```sql
-- 添加推荐索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_dag_run_dag_id_state 
ON dag_run (dag_id, state);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_task_instance_dag_id_state 
ON task_instance (dag_id, state);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_task_instance_state 
ON task_instance (state);

-- 分析查询性能
EXPLAIN ANALYZE 
SELECT * FROM task_instance 
WHERE dag_id = 'example_dag' 
AND state = 'success' 
ORDER BY start_date DESC 
LIMIT 100;

-- 数据库连接池配置检查
SHOW max_connections;
SHOW shared_buffers;
SHOW work_mem;
```

#### Python优化脚本
```python
# database_optimizer.py
import psycopg2
from sqlalchemy import create_engine, text
import pandas as pd

class DatabaseOptimizer:
    def __init__(self, database_url):
        self.engine = create_engine(database_url)
    
    def analyze_slow_queries(self):
        """分析慢查询"""
        query = """
        SELECT query, calls, total_time, mean_time, rows
        FROM pg_stat_statements
        ORDER BY total_time DESC
        LIMIT 10;
        """
        
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            slow_queries = result.fetchall()
            
        print("Top 10 slow queries:")
        for query in slow_queries:
            print(f"Query: {query[0][:100]}...")
            print(f"Calls: {query[1]}, Total Time: {query[2]:.2f}s, Mean Time: {query[3]:.2f}s")
            print("-" * 50)
    
    def check_missing_indexes(self):
        """检查缺失的索引"""
        query = """
        SELECT
            relname AS table_name,
            seq_scan,
            idx_scan,
            seq_tup_read,
            idx_tup_fetch
        FROM pg_stat_user_tables
        WHERE seq_scan > 0
        ORDER BY seq_tup_read DESC;
        """
        
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            tables = result.fetchall()
            
        print("Tables with sequential scans (potential missing indexes):")
        for table in tables:
            if table[2] == 0:  # No index scans
                print(f"Table: {table[0]}, Seq Scans: {table[1]}, Seq Rows: {table[3]}")
    
    def optimize_connection_pool(self):
        """优化连接池配置"""
        # 检查当前连接数
        query = "SELECT count(*) FROM pg_stat_activity;"
        
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            connection_count = result.fetchone()[0]
            
        print(f"Current active connections: {connection_count}")
        
        # 建议的连接池配置
        print("\nRecommended connection pool settings:")
        print("SQLALCHEMY_ENGINE_OPTIONS = {")
        print("    'pool_size': 20,")
        print("    'pool_recycle': 3600,")
        print("    'pool_pre_ping': True,")
        print("    'max_overflow': 30,")
        print("}")

# 使用示例
if __name__ == "__main__":
    db_url = "postgresql://airflow:airflow@localhost:5432/airflow"
    optimizer = DatabaseOptimizer(db_url)
    optimizer.analyze_slow_queries()
    optimizer.check_missing_indexes()
    optimizer.optimize_connection_pool()
```

### 练习4: 监控仪表板构建

#### 目标
集成Prometheus和Grafana，构建Airflow性能监控仪表板。

#### 步骤
1. 配置Airflow Prometheus指标导出
2. 安装和配置Prometheus
3. 安装和配置Grafana
4. 创建性能监控仪表板
5. 设置告警规则

#### Prometheus配置
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'airflow'
    static_configs:
      - targets: ['localhost:8080']
    metrics_path: '/admin/metrics/'

  - job_name: 'airflow-exporter'
    static_configs:
      - targets: ['localhost:9102']
```

#### Grafana仪表板配置
```json
{
  "dashboard": {
    "id": null,
    "title": "Airflow Performance Dashboard",
    "tags": ["airflow", "performance"],
    "timezone": "browser",
    "schemaVersion": 16,
    "version": 0,
    "panels": [
      {
        "id": 1,
        "type": "graph",
        "title": "Task Execution Time",
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum(rate(airflow_task_duration_seconds_bucket[5m])) by (le))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "id": 2,
        "type": "stat",
        "title": "Active Tasks",
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "airflow_task_running",
            "legendFormat": "Active Tasks"
          }
        ]
      }
    ]
  }
}
```

## 挑战练习

### 练习5: 自动化性能优化工具

#### 目标
开发一个自动化工具，能够监控Airflow性能并自动调整配置参数。

#### 功能要求
1. 实时监控关键性能指标
2. 根据性能数据自动调整配置
3. 生成性能报告
4. 发送告警通知

#### 代码实现
```python
# auto_optimizer.py
import time
import psutil
import subprocess
import json
from datetime import datetime
from typing import Dict, List
import smtplib
from email.mime.text import MIMEText

class AirflowAutoOptimizer:
    def __init__(self, config_file: str = "optimizer_config.json"):
        self.config = self.load_config(config_file)
        self.metrics_history = []
        
    def load_config(self, config_file: str) -> Dict:
        """加载配置文件"""
        default_config = {
            "monitoring_interval": 60,
            "performance_thresholds": {
                "cpu_usage": 80,
                "memory_usage": 85,
                "queue_length": 100
            },
            "optimization_rules": {
                "high_cpu": {"parallelism": -2},
                "high_memory": {"parallelism": -4},
                "long_queue": {"parallelism": +2}
            },
            "alert_email": "admin@example.com"
        }
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            return {**default_config, **config}
        except FileNotFoundError:
            print(f"Config file {config_file} not found, using defaults")
            return default_config
    
    def collect_metrics(self) -> Dict:
        """收集系统和Airflow指标"""
        # 系统指标
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Airflow指标（通过CLI或API获取）
        queue_length = self.get_task_queue_length()
        active_runs = self.get_active_runs_count()
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "queue_length": queue_length,
            "active_runs": active_runs
        }
        
        self.metrics_history.append(metrics)
        return metrics
    
    def get_task_queue_length(self) -> int:
        """获取任务队列长度"""
        try:
            result = subprocess.run([
                'airflow', 'tasks', 'list', '--state', 'queued'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                # 简单计数，实际应解析输出
                return len(result.stdout.split('\n')) - 1
            return 0
        except Exception as e:
            print(f"Error getting queue length: {e}")
            return 0
    
    def get_active_runs_count(self) -> int:
        """获取活跃运行数"""
        try:
            result = subprocess.run([
                'airflow', 'dags', 'list-runs', '--state', 'running'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return len(result.stdout.split('\n')) - 1
            return 0
        except Exception as e:
            print(f"Error getting active runs: {e}")
            return 0
    
    def analyze_performance(self, metrics: Dict) -> List[str]:
        """分析性能问题"""
        issues = []
        thresholds = self.config["performance_thresholds"]
        
        if metrics["cpu_percent"] > thresholds["cpu_usage"]:
            issues.append("high_cpu")
            
        if metrics["memory_percent"] > thresholds["memory_usage"]:
            issues.append("high_memory")
            
        if metrics["queue_length"] > thresholds["queue_length"]:
            issues.append("long_queue")
            
        return issues
    
    def optimize_configuration(self, issues: List[str]):
        """优化配置参数"""
        if not issues:
            return
            
        rules = self.config["optimization_rules"]
        changes = {}
        
        for issue in issues:
            if issue in rules:
                for param, change in rules[issue].items():
                    changes[param] = changes.get(param, 0) + change
        
        if changes:
            self.apply_configuration_changes(changes)
    
    def apply_configuration_changes(self, changes: Dict):
        """应用配置更改"""
        print(f"Applying configuration changes: {changes}")
        # 这里应该实际修改配置文件并重启服务
        # 为安全起见，这里只打印建议
        
        for param, change in changes.items():
            print(f"Recommend changing {param} by {change}")
    
    def send_alert(self, issues: List[str], metrics: Dict):
        """发送告警"""
        if not issues:
            return
            
        subject = f"Airflow Performance Alert: {', '.join(issues)}"
        body = f"""
Airflow Performance Alert Detected!

Issues: {', '.join(issues)}

Current Metrics:
- CPU Usage: {metrics['cpu_percent']:.1f}%
- Memory Usage: {metrics['memory_percent']:.1f}%
- Queue Length: {metrics['queue_length']}
- Active Runs: {metrics['active_runs']}

Time: {metrics['timestamp']}
        """
        
        print(f"Alert: {subject}")
        print(body)
        # 实际发送邮件代码省略
    
    def generate_report(self) -> Dict:
        """生成性能报告"""
        if not self.metrics_history:
            return {}
            
        recent_metrics = self.metrics_history[-10:]  # 最近10次数据
        
        avg_cpu = sum(m['cpu_percent'] for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m['memory_percent'] for m in recent_metrics) / len(recent_metrics)
        avg_queue = sum(m['queue_length'] for m in recent_metrics) / len(recent_metrics)
        
        report = {
            "period": f"Last {len(recent_metrics)} measurements",
            "average_cpu": round(avg_cpu, 2),
            "average_memory": round(avg_memory, 2),
            "average_queue_length": round(avg_queue, 2),
            "recommendations": self.get_recommendations()
        }
        
        return report
    
    def get_recommendations(self) -> List[str]:
        """获取优化建议"""
        if not self.metrics_history:
            return ["No data available for recommendations"]
            
        recent_metrics = self.metrics_history[-10:]
        recommendations = []
        
        avg_cpu = sum(m['cpu_percent'] for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m['memory_percent'] for m in recent_metrics) / len(recent_metrics)
        avg_queue = sum(m['queue_length'] for m in recent_metrics) / len(recent_metrics)
        
        if avg_cpu > 75:
            recommendations.append("Consider reducing parallelism to decrease CPU load")
            
        if avg_memory > 80:
            recommendations.append("Monitor memory usage and consider optimizing DAGs")
            
        if avg_queue > 50:
            recommendations.append("Increase worker capacity or optimize task scheduling")
            
        if not recommendations:
            recommendations.append("System performance is within acceptable range")
            
        return recommendations
    
    def run(self):
        """运行优化器"""
        print("Starting Airflow Auto Optimizer...")
        print(f"Monitoring interval: {self.config['monitoring_interval']} seconds")
        
        try:
            while True:
                # 收集指标
                metrics = self.collect_metrics()
                print(f"Metrics collected: {metrics}")
                
                # 分析性能
                issues = self.analyze_performance(metrics)
                
                # 优化配置
                self.optimize_configuration(issues)
                
                # 发送告警
                self.send_alert(issues, metrics)
                
                # 休眠到下次检查
                time.sleep(self.config["monitoring_interval"])
                
        except KeyboardInterrupt:
            print("\nStopping optimizer...")
            # 生成最终报告
            report = self.generate_report()
            print("\nFinal Performance Report:")
            print(json.dumps(report, indent=2, ensure_ascii=False))

# 使用示例
if __name__ == "__main__":
    optimizer = AirflowAutoOptimizer()
    optimizer.run()
```

## 总结

通过完成这些练习，你将掌握：
1. 如何识别和分析Airflow性能瓶颈
2. 如何通过配置调优提升系统性能
3. 如何实现监控和告警机制
4. 如何应用最佳实践确保系统稳定性

建议按顺序完成练习，从基础到进阶，逐步提升技能水平。每个练习都提供了完整的代码示例和详细说明，帮助你更好地理解和应用所学知识。