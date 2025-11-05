# Day 16: 最佳实践与案例研究 - 实践练习

## 练习1: 高可用架构设计练习

### 目标
设计一个支持多区域部署的Airflow高可用架构，并配置负载均衡和故障转移机制。

### 步骤
1. 设计主备区域的Airflow部署架构
2. 配置数据库主从复制
3. 设置Redis集群
4. 配置负载均衡器
5. 实现故障检测和自动切换

### 要求
- 绘制架构图
- 提供配置文件示例
- 编写故障切换测试脚本

```yaml
# 示例：高可用架构配置
# docker-compose.yml
version: '3.8'
services:
  # 主区域Webserver
  webserver-primary:
    image: apache/airflow:2.7.0
    environment:
      - AIRFLOW__CORE__EXECUTOR=CeleryExecutor
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql://airflow:airflow@postgres-primary:5432/airflow
      - AIRFLOW__CELERY__BROKER_URL=redis://redis:6379/0
    ports:
      - "8080:8080"
    depends_on:
      - postgres-primary
      - redis

  # 备区域Webserver
  webserver-standby:
    image: apache/airflow:2.7.0
    environment:
      - AIRFLOW__CORE__EXECUTOR=CeleryExecutor
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql://airflow:airflow@postgres-standby:5432/airflow
      - AIRFLOW__CELERY__BROKER_URL=redis://redis:6379/0
    ports:
      - "8081:8080"
    depends_on:
      - postgres-standby
      - redis

  # 主数据库
  postgres-primary:
    image: postgres:13
    environment:
      - POSTGRES_USER=airflow
      - POSTGRES_PASSWORD=airflow
      - POSTGRES_DB=airflow
    volumes:
      - postgres_primary_data:/var/lib/postgresql/data

  # 备数据库
  postgres-standby:
    image: postgres:13
    environment:
      - POSTGRES_USER=airflow
      - POSTGRES_PASSWORD=airflow
      - POSTGRES_DB=airflow
    volumes:
      - postgres_standby_data:/var/lib/postgresql/data

  # Redis
  redis:
    image: redis:6

volumes:
  postgres_primary_data:
  postgres_standby_data:
```

## 练习2: 性能调优实践

### 目标
分析现有DAG的性能瓶颈，实施优化策略并验证效果。

### 步骤
1. 选择一个复杂的DAG进行分析
2. 使用Airflow UI和日志识别性能瓶颈
3. 实施优化策略
4. 验证优化效果

### 要求
- 提供性能分析报告
- 展示优化前后的对比数据
- 编写优化后的DAG代码

```python
# 示例：性能优化前的DAG
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

def inefficient_task(**context):
    """低效的任务示例"""
    # 模拟低效的数据处理
    data = []
    for i in range(100000):
        data.append(i * 2)
    
    # 低效的数据库操作
    for item in data:
        # 模拟逐条插入数据库
        insert_to_db(item)

def optimized_task(**context):
    """优化后的任务示例"""
    # 批量处理数据
    batch_size = 1000
    data = [i * 2 for i in range(100000)]
    
    # 批量插入数据库
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        bulk_insert_to_db(batch)

# 低效的DAG
inefficient_dag = DAG(
    'inefficient_dag',
    default_args={
        'owner': 'data-team',
        'start_date': datetime(2023, 1, 1),
        'retries': 1,
    },
    schedule_interval=timedelta(days=1),
)

inefficient_task_op = PythonOperator(
    task_id='inefficient_task',
    python_callable=inefficient_task,
    dag=inefficient_dag
)

# 优化后的DAG
optimized_dag = DAG(
    'optimized_dag',
    default_args={
        'owner': 'data-team',
        'start_date': datetime(2023, 1, 1),
        'retries': 1,
    },
    schedule_interval=timedelta(days=1),
)

optimized_task_op = PythonOperator(
    task_id='optimized_task',
    python_callable=optimized_task,
    dag=optimized_dag
)
```

## 练习3: 安全配置实践

### 目标
配置基于角色的访问控制，实施数据加密和密钥管理。

### 步骤
1. 设计角色和权限模型
2. 配置用户认证和授权
3. 实施数据加密
4. 配置密钥管理

### 要求
- 提供RBAC配置文件
- 展示加密配置示例
- 编写密钥管理脚本

```python
# 示例：RBAC配置
from airflow.models import DagBag
from airflow.www.security import AirflowSecurityManager

class CustomRBACManager(AirflowSecurityManager):
    """自定义RBAC管理器"""
    
    def init_roles(self):
        """初始化角色"""
        # 管理员角色
        admin_perms = [
            'can_read',
            'can_edit',
            'can_delete',
            'can_create'
        ]
        self.init_role('Admin', admin_perms)
        
        # 数据工程师角色
        engineer_perms = [
            'can_read',
            'can_edit'
        ]
        self.init_role('DataEngineer', engineer_perms)
        
        # 分析师角色
        analyst_perms = [
            'can_read'
        ]
        self.init_role('Analyst', analyst_perms)

# 示例：加密配置
# airflow.cfg
[core]
fernet_key = your_fernet_key_here
hide_sensitive_variable_fields = True

[webserver]
secret_key = your_secret_key_here

[database]
sql_alchemy_conn = postgresql://user:encrypted_password@host:port/db
```

## 练习4: 监控告警配置

### 目标
设置关键指标监控，配置多级告警策略。

### 步骤
1. 确定关键监控指标
2. 配置Prometheus监控
3. 设置Grafana仪表板
4. 配置告警规则

### 要求
- 提供监控配置文件
- 展示Grafana仪表板配置
- 编写告警规则

```yaml
# 示例：Prometheus监控配置
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'airflow'
    static_configs:
      - targets: ['airflow-webserver:8080']
    metrics_path: '/admin/metrics/'

# 示例：告警规则
# alerts.yml
groups:
  - name: airflow_alerts
    rules:
      - alert: AirflowSchedulerDown
        expr: absent(airflow_scheduler_heartbeat) > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Airflow scheduler is down"
          description: "Airflow scheduler has not sent heartbeat for more than 1 minute"

      - alert: HighTaskFailureRate
        expr: rate(airflow_task_failures_total[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High task failure rate"
          description: "Task failure rate is above 10% in the last 5 minutes"
```

## 练习5: 案例研究分析

### 目标
分析一个实际的行业案例，提出改进建议和优化方案。

### 步骤
1. 选择一个行业案例（电商、金融、IoT等）
2. 分析现有架构和流程
3. 识别问题和改进点
4. 提出优化方案

### 要求
- 提供案例分析报告
- 展示优化方案架构图
- 编写实施计划

```python
# 示例：电商案例分析
class EcommerceCaseStudy:
    """电商行业案例分析"""
    
    def __init__(self):
        self.current_architecture = {
            'data_sources': ['web_logs', 'transaction_db', 'inventory_system'],
            'processing_pipeline': 'batch_processing',
            'storage': 'data_warehouse',
            'visualization': 'bi_tools'
        }
        
    def analyze_bottlenecks(self):
        """分析瓶颈"""
        bottlenecks = [
            '数据延迟高',
            '处理能力不足',
            '监控不完善',
            '扩展性差'
        ]
        return bottlenecks
        
    def propose_solutions(self):
        """提出解决方案"""
        solutions = {
            'real_time_processing': '使用Kafka和Spark Streaming实现实时处理',
            'microservices_architecture': '采用微服务架构提高扩展性',
            'enhanced_monitoring': '集成Prometheus和Grafana',
            'auto_scaling': '配置Kubernetes自动扩缩容'
        }
        return solutions

# 使用示例
case_study = EcommerceCaseStudy()
print("瓶颈分析:", case_study.analyze_bottlenecks())
print("解决方案:", case_study.propose_solutions())
```

## 练习6: 灾难恢复演练

### 目标
制定备份和恢复计划，进行恢复演练并评估效果。

### 步骤
1. 制定备份策略
2. 编写备份脚本
3. 制定恢复计划
4. 进行恢复演练

### 要求
- 提供备份策略文档
- 展示备份和恢复脚本
- 编写演练报告

```bash
#!/bin/bash

# 示例：Airflow备份脚本
# backup_airflow.sh

set -e

# 配置变量
BACKUP_DIR="/backup/airflow"
DATE=$(date +%Y%m%d_%H%M%S)
AIRFLOW_HOME="/opt/airflow"

# 创建备份目录
mkdir -p $BACKUP_DIR/$DATE

# 备份DAGs
tar -czf $BACKUP_DIR/$DATE/dags.tar.gz -C $AIRFLOW_HOME dags

# 备份配置文件
tar -czf $BACKUP_DIR/$DATE/config.tar.gz -C $AIRFLOW_HOME airflow.cfg

# 备份数据库
pg_dump -h postgres -U airflow airflow > $BACKUP_DIR/$DATE/database.sql

# 备份日志（可选）
tar -czf $BACKUP_DIR/$DATE/logs.tar.gz -C $AIRFLOW_HOME logs

# 创建备份元数据
cat > $BACKUP_DIR/$DATE/metadata.json << EOF
{
  "backup_time": "$(date)",
  "airflow_version": "$(airflow version)",
  "backup_size": "$(du -sh $BACKUP_DIR/$DATE | cut -f1)",
  "components": ["dags", "config", "database", "logs"]
}
EOF

echo "备份完成: $BACKUP_DIR/$DATE"

# 示例：Airflow恢复脚本
# restore_airflow.sh

#!/bin/bash

set -e

# 配置变量
BACKUP_DIR="/backup/airflow"
RESTORE_DATE=$1

if [ -z "$RESTORE_DATE" ]; then
  echo "请提供恢复日期，格式: YYYYMMDD_HHMMSS"
  exit 1
fi

# 停止Airflow服务
airflow webserver --daemon --stop
airflow scheduler --daemon --stop

# 恢复DAGs
tar -xzf $BACKUP_DIR/$RESTORE_DATE/dags.tar.gz -C $AIRFLOW_HOME

# 恢复配置文件
tar -xzf $BACKUP_DIR/$RESTORE_DATE/config.tar.gz -C $AIRFLOW_HOME

# 恢复数据库
psql -h postgres -U airflow airflow < $BACKUP_DIR/$RESTORE_DATE/database.sql

# 恢复日志（可选）
tar -xzf $BACKUP_DIR/$RESTORE_DATE/logs.tar.gz -C $AIRFLOW_HOME

echo "恢复完成: $RESTORE_DATE"
```

## 附加挑战练习

### 挑战1: 多环境部署策略
设计开发、测试、生产环境的部署策略，确保环境一致性。

### 挑战2: 自定义指标监控
实现自定义业务指标监控，如数据质量检查、业务KPI跟踪等。

### 挑战3: 自动扩缩容配置
配置基于负载的自动扩缩容策略，优化资源使用。

### 挑战4: 零停机升级方案
设计并实现Airflow版本升级的零停机方案。

完成这些练习将帮助您深入理解Airflow在生产环境中的最佳实践，提升解决实际问题的能力。