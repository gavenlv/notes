# Apache Airflow 故障排除指南

本文档提供了一套全面的故障排除指南，帮助您诊断和解决在生产环境中可能遇到的各种Airflow问题。我们将按照不同的组件类别进行组织，并提供详细的诊断步骤和解决方案。

## 1. 调度器问题

### 1.1 调度器无法启动

**症状：**
- 调度器进程崩溃或无法启动
- 日志中出现错误信息

**诊断步骤：**
```bash
# 1. 检查调度器日志
kubectl logs -n airflow deployment/airflow-scheduler

# 2. 检查调度器状态
kubectl get pods -n airflow | grep scheduler

# 3. 检查配置文件
airflow config list | grep scheduler

# 4. 验证数据库连接
airflow db check
```

**常见原因及解决方案：**

1. **数据库连接问题**
   ```bash
   # 检查数据库连接
   nc -zv airflow-postgresql 5432
   
   # 如果连接失败，检查以下配置：
   # - postgresql服务是否正常运行
   # - 网络策略是否允许连接
   # - 数据库凭证是否正确
   ```

2. **配置错误**
   ```bash
   # 验证配置文件语法
   airflow config list
   
   # 检查关键配置项
   airflow config get-value core sql_alchemy_conn
   airflow config get-value core executor
   airflow config get-value scheduler catchup_by_default
   ```

3. **资源不足**
   ```bash
   # 检查Pod资源使用情况
   kubectl top pods -n airflow | grep scheduler
   
   # 检查节点资源
   kubectl describe nodes
   ```

### 1.2 DAG无法被调度

**症状：**
- DAG在UI中显示但不运行
- 任务卡在"None"状态

**诊断步骤：**
```bash
# 1. 检查DAG是否启用
airflow dags list | grep your_dag_id

# 2. 检查DAG是否有导入错误
airflow dags list-import-errors

# 3. 检查调度器日志中的DAG处理信息
kubectl logs -n airflow deployment/airflow-scheduler | grep your_dag_id

# 4. 验证DAG文件语法
python /opt/airflow/dags/your_dag.py
```

**解决方案：**

1. **启用DAG**
   ```bash
   airflow dags unpause your_dag_id
   ```

2. **修复导入错误**
   ```bash
   # 查看具体的导入错误
   airflow dags list-import-errors
   
   # 修复DAG文件中的语法错误或依赖问题
   ```

3. **调整调度器配置**
   ```ini
   [scheduler]
   # 增加DAG文件处理频率
   dag_dir_list_interval = 300
   
   # 增加最大线程数
   parsing_processes = 4
   
   # 启用DAG序列化
   store_serialized_dags = True
   ```

### 1.3 调度器性能问题

**症状：**
- 调度延迟
- 大量DAG积压

**诊断步骤：**
```bash
# 1. 检查调度器指标
curl -s http://airflow-webserver:8080/metrics | grep scheduler

# 2. 检查任务队列状态
airflow tasks states-for-dag-run your_dag_id your_dag_run_id

# 3. 分析慢查询
kubectl exec -it airflow-postgresql-0 -- psql -U airflow -c "SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 5;"
```

**优化建议：**

1. **调整调度器参数**
   ```ini
   [scheduler]
   # 减少处理器数量以降低资源消耗
   max_threads = 2
   
   # 增加心跳间隔
   scheduler_heartbeat_sec = 5
   
   # 启用DAG序列化
   store_serialized_dags = True
   ```

2. **优化数据库**
   ```sql
   -- 创建必要的索引
   CREATE INDEX idx_task_instance_ti_dr ON task_instance (dag_id, task_id, run_id);
   CREATE INDEX idx_dag_run_dr ON dag_run (dag_id, run_id);
   ```

## 2. Worker问题

### 2.1 Worker无法连接到队列

**症状：**
- 任务长时间处于"queued"状态
- Worker日志显示连接错误

**诊断步骤：**
```bash
# 1. 检查Worker日志
kubectl logs -n airflow deployment/airflow-worker

# 2. 验证Redis连接
redis-cli -h airflow-redis-master -p 6379 ping

# 3. 检查队列状态
redis-cli -h airflow-redis-master -p 6379 llen airflow
```

**解决方案：**

1. **检查网络连接**
   ```bash
   # 在Worker容器中测试连接
   nc -zv airflow-redis-master 6379
   ```

2. **验证配置**
   ```ini
   [celery]
   broker_url = redis://:password@airflow-redis-master:6379/1
   result_backend = redis://:password@airflow-redis-master:6379/1
   ```

3. **重启Worker**
   ```bash
   kubectl rollout restart deployment/airflow-worker
   ```

### 2.2 Worker内存泄漏

**症状：**
- Worker内存使用持续增长
- Pod频繁被OOMKilled

**诊断步骤：**
```bash
# 1. 监控内存使用
kubectl top pods -n airflow | grep worker

# 2. 检查Pod事件
kubectl describe pod -n airflow <worker-pod-name> | grep -A 10 Events

# 3. 分析内存转储（如果启用）
kubectl exec -it <worker-pod-name> -- pip install memory-profiler
```

**解决方案：**

1. **调整资源限制**
   ```yaml
   resources:
     requests:
       memory: "2Gi"
     limits:
       memory: "4Gi"
   ```

2. **优化任务代码**
   ```python
   # 确保及时释放资源
   def cleanup_resources():
       gc.collect()
   
   # 使用上下文管理器
   with tempfile.TemporaryDirectory() as tmpdir:
       # 处理临时文件
       pass
   ```

## 3. Webserver问题

### 3.1 Web界面响应缓慢

**症状：**
- 页面加载时间过长
- API响应超时

**诊断步骤：**
```bash
# 1. 检查Webserver日志
kubectl logs -n airflow deployment/airflow-webserver

# 2. 监控响应时间
curl -w "@curl-format.txt" -o /dev/null -s http://airflow-webserver:8080/

# curl-format.txt内容：
#     time_namelookup:  %{time_namelookup}\n
#        time_connect:  %{time_connect}\n
#     time_appconnect:  %{time_appconnect}\n
#    time_pretransfer:  %{time_pretransfer}\n
#       time_redirect:  %{time_redirect}\n
#  time_starttransfer:  %{time_starttransfer}\n
#                     ----------\n
#          time_total:  %{time_total}\n

# 3. 检查数据库查询性能
kubectl exec -it airflow-postgresql-0 -- psql -U airflow -c "SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 5;"
```

**优化建议：**

1. **启用缓存**
   ```ini
   [webserver]
   # 启用缓存
   cache_timeout = 300
   
   # 启用静态文件缓存
   static_hash_cache = True
   ```

2. **优化数据库查询**
   ```sql
   -- 创建必要索引
   CREATE INDEX idx_task_instance_dr_state ON task_instance (dag_id, run_id, state);
   CREATE INDEX idx_log_dr ON log (dag_id, task_id, run_id);
   ```

### 3.2 认证和授权问题

**症状：**
- 登录失败
- 权限不足错误

**诊断步骤：**
```bash
# 1. 检查认证配置
airflow config get-value webserver authenticate
airflow config get-value webserver auth_backend

# 2. 验证用户权限
airflow users list

# 3. 检查角色权限
airflow roles list
```

**解决方案：**

1. **重置用户密码**
   ```bash
   airflow users create \
       --username admin \
       --firstname Admin \
       --lastname User \
       --role Admin \
       --email admin@example.com
   ```

2. **更新角色权限**
   ```bash
   airflow roles export airflow_roles.json
   # 修改角色权限后重新导入
   airflow roles import airflow_roles.json
   ```

## 4. 数据库问题

### 4.1 数据库连接池耗尽

**症状：**
- 连接超时错误
- "Too many connections"错误

**诊断步骤：**
```bash
# 1. 检查当前连接数
kubectl exec -it airflow-postgresql-0 -- psql -U airflow -c "SELECT count(*) FROM pg_stat_activity;"

# 2. 查看活动连接详情
kubectl exec -it airflow-postgresql-0 -- psql -U airflow -c "SELECT datname, usename, application_name, state, query FROM pg_stat_activity WHERE state != 'idle';"

# 3. 检查连接池配置
airflow config get-value core sql_alchemy_pool_size
airflow config get-value core sql_alchemy_max_overflow
```

**解决方案：**

1. **调整连接池配置**
   ```ini
   [core]
   sql_alchemy_pool_size = 20
   sql_alchemy_max_overflow = 30
   sql_alchemy_pool_recycle = 3600
   sql_alchemy_pool_pre_ping = True
   ```

2. **优化PostgreSQL配置**
   ```yaml
   # postgresql.conf
   max_connections = 200
   shared_buffers = 256MB
   effective_cache_size = 1GB
   ```

### 4.2 数据库性能问题

**症状：**
- 查询响应缓慢
- 系统整体变慢

**诊断步骤：**
```bash
# 1. 启用查询统计
kubectl exec -it airflow-postgresql-0 -- psql -U airflow -c "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;"

# 2. 查看慢查询
kubectl exec -it airflow-postgresql-0 -- psql -U airflow -c "SELECT query, calls, total_time, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# 3. 检查表大小
kubectl exec -it airflow-postgresql-0 -- psql -U airflow -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size FROM pg_tables WHERE schemaname='public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"
```

**优化建议：**

1. **创建索引**
   ```sql
   -- 为常用查询字段创建索引
   CREATE INDEX idx_task_instance_state ON task_instance (state);
   CREATE INDEX idx_dag_run_state ON dag_run (state);
   CREATE INDEX idx_log_dag_id ON log (dag_id);
   ```

2. **定期清理历史数据**
   ```sql
   -- 清理超过90天的日志
   DELETE FROM log WHERE dttm < NOW() - INTERVAL '90 days';
   
   -- 清理已完成的任务实例
   DELETE FROM task_instance WHERE dag_id IN (
       SELECT dag_id FROM dag WHERE is_paused IS TRUE
   ) AND state = 'success' AND start_date < NOW() - INTERVAL '30 days';
   ```

## 5. 监控和日志

### 5.1 日志收集问题

**症状：**
- 日志缺失或不完整
- 无法通过UI查看日志

**诊断步骤：**
```bash
# 1. 检查日志配置
airflow config get-value logging remote_logging
airflow config get-value logging remote_base_log_folder

# 2. 验证存储访问权限
kubectl exec -it airflow-worker-0 -- aws s3 ls s3://your-log-bucket/

# 3. 检查日志写入权限
kubectl exec -it airflow-worker-0 -- touch /tmp/test.log
```

**解决方案：**

1. **修正日志配置**
   ```ini
   [logging]
   remote_logging = True
   remote_base_log_folder = s3://your-airflow-logs/
   remote_log_conn_id = aws_default
   encrypt_s3_logs = False
   ```

2. **验证云存储连接**
   ```bash
   # 检查连接ID配置
   airflow connections get aws_default
   ```

### 5.2 监控告警误报

**症状：**
- 收到大量无关告警
- 告警触发条件不合理

**诊断步骤：**
```bash
# 1. 检查Prometheus规则
kubectl get prometheusrules -n monitoring

# 2. 验证指标数据
curl -s http://prometheus-server:9090/api/v1/query?query=airflow_task_duration

# 3. 检查告警历史
kubectl get alertmanagers -n monitoring
```

**优化建议：**

1. **调整告警阈值**
   ```yaml
   # 修改告警规则中的阈值
   - alert: HighTaskFailureRate
     expr: rate(airflow_task_failures[5m]) > 0.1  # 从0.05调整到0.1
     for: 5m
   ```

2. **增加告警抑制规则**
   ```yaml
   inhibit_rules:
     - source_match:
         alertname: DatabaseDown
       target_match:
         alertname: HighTaskFailureRate
       equal: ['instance']
   ```

## 6. 安全问题

### 6.1 密钥泄露

**症状：**
- 敏感信息出现在日志中
- 未经授权的访问

**诊断步骤：**
```bash
# 1. 检查变量和连接
airflow variables list
airflow connections list

# 2. 搜索日志中的敏感信息
kubectl logs -n airflow deployment/airflow-webserver | grep -i "password\|secret\|key"

# 3. 验证密钥隐藏配置
airflow config get-value core hide_sensitive_var_conn_fields
```

**解决方案：**

1. **启用敏感信息隐藏**
   ```ini
   [core]
   hide_sensitive_var_conn_fields = True
   sensitive_var_conn_names = password,secret,key,private_key
   ```

2. **轮换密钥**
   ```bash
   # 更新连接信息
   airflow connections add 'my_db' \
       --conn-type 'postgres' \
       --conn-host 'localhost' \
       --conn-port '5432' \
       --conn-login 'airflow' \
       --conn-password 'new_secure_password'
   ```

### 6.2 权限提升攻击

**症状：**
- 用户权限异常变化
- 未授权的操作记录

**诊断步骤：**
```bash
# 1. 检查用户和角色变更历史
airflow users list
airflow roles list

# 2. 审计日志分析
kubectl logs -n airflow deployment/airflow-webserver | grep -E "(user|role|permission)"

# 3. 检查API访问日志
kubectl logs -n airflow deployment/airflow-webserver | grep "/api/"
```

**预防措施：**

1. **实施最小权限原则**
   ```bash
   # 创建受限角色
   airflow roles create 'LimitedUser'
   
   # 只授予必要权限
   airflow roles add-perms -r 'LimitedUser' -a 'can_read' -v 'DagRun'
   ```

2. **启用审计日志**
   ```ini
   [logging]
   audit_log_file = /var/log/airflow/audit.log
   audit_log_format = %(asctime)s - %(name)s - %(levelname)s - %(message)s
   ```

## 7. 性能优化

### 7.1 任务执行缓慢

**症状：**
- 任务运行时间超出预期
- 资源利用率低

**诊断步骤：**
```bash
# 1. 分析任务执行时间
airflow tasks states-for-dag-run your_dag_id your_dag_run_id

# 2. 检查Worker资源使用
kubectl top pods -n airflow | grep worker

# 3. 分析Python代码性能
kubectl exec -it airflow-worker-0 -- pip install py-spy
kubectl exec -it airflow-worker-0 -- py-spy top --pid 1
```

**优化建议：**

1. **并行化任务**
   ```python
   # 将大任务拆分为多个小任务并行执行
   from airflow.decorators import task_group
   
   @task_group
   def process_data_group():
       tasks = []
       for i in range(10):
           task = process_chunk.override(task_id=f'process_chunk_{i}')()
           tasks.append(task)
       return tasks
   ```

2. **优化数据处理**
   ```python
   # 使用更高效的数据处理库
   import pandas as pd
   import dask.dataframe as dd
   
   # 对于大数据集使用Dask
   df = dd.read_csv('large_dataset.csv')
   result = df.groupby('category').sum().compute()
   ```

### 7.2 资源浪费

**症状：**
- 资源使用率低
- 成本过高

**诊断步骤：**
```bash
# 1. 分析资源使用情况
kubectl top nodes
kubectl top pods -n airflow

# 2. 检查HPA状态
kubectl get hpa -n airflow

# 3. 分析成本分布
kubectl get pods -n airflow -o json | jq '.items[].spec.containers[].resources'
```

**优化建议：**

1. **调整资源请求和限制**
   ```yaml
   resources:
     requests:
       cpu: "500m"
       memory: "1Gi"
     limits:
       cpu: "1"
       memory: "2Gi"
   ```

2. **实施自动扩缩容**
   ```yaml
   # HPA配置
   apiVersion: autoscaling/v2
   kind: HorizontalPodAutoscaler
   metadata:
     name: airflow-worker-hpa
   spec:
     scaleTargetRef:
       apiVersion: apps/v1
       kind: Deployment
       name: airflow-worker
     minReplicas: 2
     maxReplicas: 10
     metrics:
     - type: Resource
       resource:
         name: cpu
         target:
           type: Utilization
           averageUtilization: 70
   ```

## 8. 备份和恢复

### 8.1 备份失败

**症状：**
- 备份作业失败
- 备份文件损坏或不完整

**诊断步骤：**
```bash
# 1. 检查备份作业日志
kubectl logs -n airflow deployment/airflow-backup-job

# 2. 验证存储访问
kubectl exec -it airflow-backup-job -- aws s3 ls s3://your-backup-bucket/

# 3. 检查备份脚本
cat /scripts/backup.sh
```

**解决方案：**

1. **修正备份脚本**
   ```bash
   #!/bin/bash
   set -e
   
   # 创建临时目录
   TMP_DIR=$(mktemp -d)
   trap "rm -rf $TMP_DIR" EXIT
   
   # 备份DAGs
   cp -r /opt/airflow/dags $TMP_DIR/
   
   # 备份配置
   cp /opt/airflow/airflow.cfg $TMP_DIR/
   
   # 备份数据库
   pg_dump -U airflow airflow > $TMP_DIR/airflow.sql
   
   # 上传到S3
   aws s3 sync $TMP_DIR s3://your-backup-bucket/$(date +%Y%m%d-%H%M%S)/
   ```

2. **验证备份完整性**
   ```bash
   # 添加校验和验证
   md5sum $TMP_DIR/*.sql > $TMP_DIR/checksums.md5
   
   # 在恢复时验证
   md5sum -c $TMP_DIR/checksums.md5
   ```

### 8.2 恢复失败

**症状：**
- 恢复过程出错
- 恢复后系统不稳定

**诊断步骤：**
```bash
# 1. 检查恢复日志
kubectl logs -n airflow deployment/airflow-restore-job

# 2. 验证备份文件完整性
aws s3 ls s3://your-backup-bucket/latest/

# 3. 检查数据库版本兼容性
kubectl exec -it airflow-postgresql-0 -- psql -U airflow -c "SELECT version();"
```

**解决方案：**

1. **分步恢复**
   ```bash
   # 1. 先恢复数据库结构
   psql -U airflow airflow < schema_backup.sql
   
   # 2. 再恢复数据
   psql -U airflow airflow < data_backup.sql
   
   # 3. 最后恢复DAGs和配置
   cp -r /backup/dags/* /opt/airflow/dags/
   cp /backup/airflow.cfg /opt/airflow/airflow.cfg
   ```

2. **版本兼容性检查**
   ```bash
   # 在恢复前检查Airflow版本
   airflow version
   
   # 确保备份是在兼容版本上创建的
   cat /backup/version.txt
   ```

## 9. 常用诊断命令

### 9.1 系统状态检查

```bash
# 检查所有组件状态
kubectl get pods -n airflow

# 检查服务状态
kubectl get svc -n airflow

# 检查配置映射
kubectl get configmap -n airflow

# 检查密钥
kubectl get secret -n airflow
```

### 9.2 日志分析

```bash
# 实时查看调度器日志
kubectl logs -f -n airflow deployment/airflow-scheduler

# 查看最近的错误日志
kubectl logs -n airflow deployment/airflow-webserver --since=1h | grep ERROR

# 按标签过滤日志
kubectl logs -l app=airflow -n airflow --tail=100
```

### 9.3 性能监控

```bash
# 监控Pod资源使用
watch -n 5 'kubectl top pods -n airflow'

# 检查节点资源
kubectl describe nodes | grep -A 5 "Allocated resources"

# 查看事件
kubectl get events -n airflow --sort-by='.lastTimestamp'
```

## 10. 最佳实践总结

1. **定期维护**
   - 定期清理历史数据
   - 更新安全补丁
   - 轮换密钥和证书

2. **监控覆盖**
   - 设置全面的监控指标
   - 配置合理的告警阈值
   - 定期审查告警规则

3. **备份策略**
   - 实施多重备份机制
   - 定期测试恢复流程
   - 保持备份版本兼容性

4. **安全加固**
   - 实施最小权限原则
   - 启用敏感信息保护
   - 定期进行安全审计

5. **性能优化**
   - 根据负载调整资源配置
   - 实施自动扩缩容
   - 优化数据库查询和索引

通过遵循这些故障排除指南和最佳实践，您可以有效诊断和解决大部分Airflow生产环境问题，确保系统的稳定性和可靠性。