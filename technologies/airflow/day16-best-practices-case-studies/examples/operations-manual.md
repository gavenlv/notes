# Apache Airflow 运维手册

本文档为Apache Airflow生产环境的运维提供了全面的指导，涵盖了日常操作、监控、维护、故障排除和最佳实践等方面。

## 1. 日常操作

### 1.1 启动和停止服务

#### 启动Airflow集群

```bash
# 1. 启动数据库
kubectl apply -f postgresql-deployment.yaml

# 2. 启动Redis（如果使用CeleryExecutor）
kubectl apply -f redis-deployment.yaml

# 3. 初始化数据库
kubectl exec -it airflow-webserver-0 -- airflow db init

# 4. 创建管理员用户
kubectl exec -it airflow-webserver-0 -- airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com

# 5. 启动核心服务
kubectl apply -f airflow-deployment.yaml
```

#### 停止Airflow集群

```bash
# 1. 停止核心服务
kubectl delete -f airflow-deployment.yaml

# 2. 停止Redis（如果使用CeleryExecutor）
kubectl delete -f redis-deployment.yaml

# 3. 停止数据库（注意：这将丢失数据，除非使用持久化存储）
kubectl delete -f postgresql-deployment.yaml
```

### 1.2 DAG管理

#### 部署新DAG

```bash
# 1. 验证DAG语法
python your_dag.py

# 2. 检查导入错误
airflow dags list-import-errors

# 3. 部署DAG文件
kubectl cp your_dag.py airflow-webserver-0:/opt/airflow/dags/

# 4. 启用DAG
airflow dags unpause your_dag_id
```

#### 更新现有DAG

```bash
# 1. 暂停DAG执行
airflow dags pause your_dag_id

# 2. 更新DAG文件
kubectl cp updated_dag.py airflow-webserver-0:/opt/airflow/dags/

# 3. 验证更新
airflow dags list | grep your_dag_id

# 4. 重新启用DAG
airflow dags unpause your_dag_id
```

#### 删除DAG

```bash
# 1. 暂停DAG
airflow dags pause your_dag_id

# 2. 删除DAG文件
kubectl exec -it airflow-webserver-0 -- rm /opt/airflow/dags/your_dag.py

# 3. 清理数据库中的DAG记录（可选）
airflow dags delete your_dag_id --yes
```

### 1.3 用户和权限管理

#### 创建用户

```bash
# 创建具有特定角色的用户
airflow users create \
    --username analyst \
    --firstname Data \
    --lastname Analyst \
    --role User \
    --email analyst@example.com
```

#### 更新用户权限

```bash
# 更改用户角色
airflow users add-role \
    --username analyst \
    --role Op

# 移除用户角色
airflow users remove-role \
    --username analyst \
    --role User
```

#### 删除用户

```bash
# 删除用户
airflow users delete --username analyst
```

## 2. 监控和告警

### 2.1 关键指标监控

#### Airflow核心指标

```yaml
# Prometheus监控配置
scrape_configs:
  - job_name: 'airflow'
    static_configs:
      - targets: ['airflow-webserver:8080']
    metrics_path: '/admin/metrics/'
```

关键监控指标：
- `airflow_task_successes` - 任务成功执行次数
- `airflow_task_failures` - 任务失败次数
- `airflow_dagbag_size` - DAG数量
- `airflow_scheduler_heartbeat` - 调度器心跳
- `airflow_pool_open_slots` - 连接池可用槽位

#### 数据库监控

```sql
-- 监控数据库性能的关键查询
-- 1. 检查活动连接数
SELECT count(*) FROM pg_stat_activity;

-- 2. 查看慢查询
SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 5;

-- 3. 检查表大小
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables WHERE schemaname='public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 2.2 告警配置

#### Prometheus告警规则

```yaml
groups:
- name: airflow.rules
  rules:
  - alert: AirflowSchedulerDown
    expr: airflow_scheduler_heartbeat < 1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Airflow调度器宕机"
      description: "Airflow调度器在过去5分钟内没有发送心跳"

  - alert: HighTaskFailureRate
    expr: rate(airflow_task_failures[5m]) > 0.05
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "任务失败率过高"
      description: "任务失败率超过5%: {{ $value }}"

  - alert: DatabaseConnectionIssues
    expr: airflow_db_failures > 10
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "数据库连接问题"
      description: "数据库连接失败次数过多: {{ $value }}"
```

### 2.3 日志监控

#### 集中日志收集配置

```yaml
# Fluentd配置示例
<source>
  @type tail
  path /opt/airflow/logs/**/*.log
  pos_file /var/log/td-agent/airflow.log.pos
  tag airflow.*
  format json
  time_key time
  time_format %Y-%m-%dT%H:%M:%S
</source>

<match airflow.**>
  @type elasticsearch
  host elasticsearch
  port 9200
  logstash_format true
</match>
```

## 3. 维护操作

### 3.1 定期清理

#### 清理历史数据

```bash
#!/bin/bash
# airflow-cleanup.sh

# 清理超过90天的DAG运行记录
airflow dags delete-run \
    --dag-id your_dag_id \
    --run-id your_run_id \
    --yes

# 清理超过30天的任务实例
psql -U airflow -d airflow -c "
DELETE FROM task_instance 
WHERE dag_id IN (SELECT dag_id FROM dag WHERE is_paused IS TRUE) 
AND state = 'success' 
AND start_date < NOW() - INTERVAL '30 days';
"

# 清理日志文件
find /opt/airflow/logs -type f -mtime +30 -delete
```

#### 清理数据库

```sql
-- 清理任务实例表
DELETE FROM task_instance 
WHERE dag_id IN (
    SELECT dag_id FROM dag WHERE is_paused IS TRUE
) AND state = 'success' AND start_date < NOW() - INTERVAL '30 days';

-- 清理日志表
DELETE FROM log WHERE dttm < NOW() - INTERVAL '90 days';

-- 清理作业表
DELETE FROM job WHERE latest_heartbeat < NOW() - INTERVAL '30 days';

-- 优化表
VACUUM ANALYZE task_instance;
VACUUM ANALYZE log;
VACUUM ANALYZE job;
```

### 3.2 数据库维护

#### 数据库备份

```bash
#!/bin/bash
# database-backup.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="$BACKUP_DIR/airflow-db-$DATE.sql"

# 创建备份
pg_dump -U airflow airflow > $BACKUP_FILE

# 压缩备份
gzip $BACKUP_FILE

# 上传到S3
aws s3 cp $BACKUP_FILE.gz s3://your-backup-bucket/database/

# 删除本地备份（保留最近7天）
find $BACKUP_DIR -name "airflow-db-*.sql.gz" -mtime +7 -delete
```

#### 数据库优化

```sql
-- 更新表统计信息
ANALYZE;

-- 重建索引
REINDEX TABLE task_instance;
REINDEX TABLE dag_run;
REINDEX TABLE log;

-- 检查并修复表
VACUUM FULL task_instance;
VACUUM FULL dag_run;
VACUUM FULL log;
```

### 3.3 系统更新

#### Airflow版本升级

```bash
# 1. 备份当前配置
kubectl cp airflow-webserver-0:/opt/airflow/airflow.cfg ./backup/

# 2. 备份DAG文件
kubectl cp airflow-webserver-0:/opt/airflow/dags/ ./backup/dags/

# 3. 备份数据库
./scripts/database-backup.sh

# 4. 更新Helm Chart或部署文件
helm repo update
helm upgrade airflow apache-airflow/airflow --version 1.7.0

# 5. 验证升级
kubectl get pods -n airflow
airflow version
```

## 4. 安全操作

### 4.1 密钥管理

#### 轮换密钥

```bash
# 1. 生成新的Fernet密钥
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 2. 更新配置
kubectl patch configmap airflow-config -p='{"data":{"fernet-key": "your_new_key"}}'

# 3. 重启服务
kubectl rollout restart deployment/airflow-webserver
kubectl rollout restart deployment/airflow-scheduler
```

#### 管理连接信息

```bash
# 1. 添加新的连接
airflow connections add 'my_db' \
    --conn-type 'postgres' \
    --conn-host 'localhost' \
    --conn-port '5432' \
    --conn-login 'airflow' \
    --conn-password 'secure_password'

# 2. 更新现有连接
airflow connections update 'my_db' \
    --conn-password 'new_secure_password'

# 3. 删除连接
airflow connections delete 'my_db'
```

### 4.2 安全审计

#### 定期安全检查

```bash
# 1. 检查暴露的端口
kubectl get svc -n airflow

# 2. 验证网络策略
kubectl get networkpolicy -n airflow

# 3. 检查RBAC配置
kubectl get roles,rolebindings -n airflow

# 4. 审计用户权限
airflow users list
airflow roles list
```

#### SSL/TLS配置检查

```bash
# 1. 检查证书有效期
openssl x509 -in /etc/ssl/certs/airflow.crt -text -noout | grep "Not After"

# 2. 验证TLS配置
curl -kv https://airflow-webserver:8080/

# 3. 更新证书
kubectl create secret tls airflow-tls \
    --cert=/path/to/cert.pem \
    --key=/path/to/key.pem \
    --dry-run=client -o yaml | kubectl apply -f -
```

## 5. 故障排除

### 5.1 常见问题诊断

#### 调度器问题

```bash
# 1. 检查调度器日志
kubectl logs -n airflow deployment/airflow-scheduler

# 2. 检查调度器状态
kubectl get pods -n airflow | grep scheduler

# 3. 验证数据库连接
kubectl exec -it airflow-scheduler-0 -- airflow db check

# 4. 检查DAG处理
kubectl exec -it airflow-scheduler-0 -- airflow dags list-import-errors
```

#### Worker问题

```bash
# 1. 检查Worker日志
kubectl logs -n airflow deployment/airflow-worker

# 2. 验证队列连接
kubectl exec -it airflow-worker-0 -- redis-cli -h airflow-redis-master ping

# 3. 检查资源使用
kubectl top pods -n airflow | grep worker
```

### 5.2 性能调优

#### 调整调度器性能

```ini
# airflow.cfg 调度器配置优化
[scheduler]
# 增加处理DAG文件的进程数
parsing_processes = 4

# 减少DAG目录扫描间隔
dag_dir_list_interval = 300

# 启用DAG序列化以减少数据库负载
store_serialized_dags = True

# 调整心跳间隔
scheduler_heartbeat_sec = 5

# 限制最大线程数
max_threads = 2
```

#### 优化Worker性能

```yaml
# Kubernetes部署配置优化
resources:
  requests:
    cpu: "1"
    memory: "2Gi"
  limits:
    cpu: "2"
    memory: "4Gi"

# 添加节点选择器
nodeSelector:
  node-type: "high-performance"

# 添加污点容忍
tolerations:
  - key: "dedicated"
    operator: "Equal"
    value: "airflow-worker"
    effect: "NoSchedule"
```

## 6. 备份和恢复

### 6.1 备份策略

#### 全量备份脚本

```bash
#!/bin/bash
# full-backup.sh

BACKUP_BASE="/backups"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="$BACKUP_BASE/$DATE"

mkdir -p $BACKUP_DIR

# 1. 备份DAG文件
kubectl cp airflow-webserver-0:/opt/airflow/dags/ $BACKUP_DIR/dags/

# 2. 备份配置文件
kubectl cp airflow-webserver-0:/opt/airflow/airflow.cfg $BACKUP_DIR/airflow.cfg

# 3. 备份数据库
pg_dump -U airflow airflow > $BACKUP_DIR/airflow.sql

# 4. 备份变量和连接
airflow variables export $BACKUP_DIR/variables.json
airflow connections export $BACKUP_DIR/connections.json

# 5. 压缩备份
tar -czf $BACKUP_DIR.tar.gz -C $BACKUP_BASE $DATE

# 6. 上传到云存储
aws s3 cp $BACKUP_DIR.tar.gz s3://your-backup-bucket/full-backups/

# 7. 清理本地备份（保留最近7天）
find $BACKUP_BASE -mindepth 1 -maxdepth 1 -type d -mtime +7 -exec rm -rf {} \;
find $BACKUP_BASE -name "*.tar.gz" -mtime +7 -delete
```

### 6.2 恢复流程

#### 灾难恢复步骤

```bash
# 1. 停止当前服务
kubectl delete -f airflow-deployment.yaml

# 2. 恢复数据库
# 从S3下载备份
aws s3 cp s3://your-backup-bucket/full-backups/latest.tar.gz /tmp/
tar -xzf /tmp/latest.tar.gz -C /tmp/

# 恢复数据库
psql -U airflow airflow < /tmp/latest/airflow.sql

# 3. 恢复DAG文件
kubectl cp /tmp/latest/dags/ airflow-webserver-0:/opt/airflow/dags/

# 4. 恢复配置
kubectl cp /tmp/latest/airflow.cfg airflow-webserver-0:/opt/airflow/airflow.cfg

# 5. 恢复变量和连接
airflow variables import /tmp/latest/variables.json
airflow connections import /tmp/latest/connections.json

# 6. 启动服务
kubectl apply -f airflow-deployment.yaml
```

## 7. 最佳实践

### 7.1 配置管理

#### 使用配置映射

```yaml
# airflow-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: airflow-config
  namespace: airflow
data:
  airflow.cfg: |
    [core]
    executor = KubernetesExecutor
    sql_alchemy_conn = postgresql+psycopg2://airflow:airflow@airflow-postgresql:5432/airflow
    
    [webserver]
    rbac = True
    authenticate = True
    
    [scheduler]
    store_serialized_dags = True
    dag_dir_list_interval = 300
```

### 7.2 资源管理

#### 资源配额设置

```yaml
# resource-quota.yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: airflow-quota
  namespace: airflow
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    persistentvolumeclaims: "10"
    services.loadbalancers: "2"
```

### 7.3 网络安全

#### 网络策略配置

```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: airflow-policy
  namespace: airflow
spec:
  podSelector:
    matchLabels:
      app: airflow
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: database
    ports:
    - protocol: TCP
      port: 5432
```

### 7.4 监控和日志

#### 统一日志格式

```python
# logging_config.py
import logging
from airflow.config_templates.airflow_local_settings import DEFAULT_LOGGING_CONFIG

LOGGING_CONFIG = DEFAULT_LOGGING_CONFIG.copy()

LOGGING_CONFIG['formatters']['airflow']['format'] = (
    '[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s'
)

LOGGING_CONFIG['handlers']['console']['formatter'] = 'airflow'
```

## 8. 应急响应

### 8.1 故障响应流程

#### 关键故障处理

1. **立即响应**
   - 确认故障影响范围
   - 通知相关人员
   - 启动应急响应计划

2. **故障诊断**
   - 检查系统状态
   - 查看日志信息
   - 确定根本原因

3. **故障恢复**
   - 实施修复措施
   - 验证系统功能
   - 监控恢复情况

4. **事后分析**
   - 记录故障详情
   - 分析根本原因
   - 制定预防措施

#### 应急联系人

```yaml
# emergency-contacts.yaml
contacts:
  primary:
    name: "运维团队"
    phone: "+1-555-0123"
    email: "ops@company.com"
  
  secondary:
    name: "开发团队"
    phone: "+1-555-0124"
    email: "dev@company.com"
  
  vendor:
    name: "云服务商支持"
    phone: "+1-800-CLOUD-SUPPORT"
    email: "support@cloudprovider.com"
```

### 8.2 灾难恢复

#### 灾难恢复计划

1. **数据恢复**
   - 从最近备份恢复数据库
   - 恢复DAG文件和配置
   - 验证数据完整性

2. **服务恢复**
   - 重新部署Airflow集群
   - 恢复用户和权限
   - 验证服务功能

3. **业务验证**
   - 运行测试DAG确认功能
   - 验证关键业务流程
   - 通知业务方恢复完成

通过遵循本运维手册，您可以有效地管理Apache Airflow生产环境，确保其稳定、安全和高效运行。定期审查和更新本手册以适应环境变化和技术发展。