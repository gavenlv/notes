# RabbitMQ 监控与运维代码示例

本目录包含了RabbitMQ监控与运维相关的代码示例，涵盖系统监控、性能监控、运维自动化和日志分析等功能。

## 文件说明

### 1. system_monitoring.py
**系统监控模块**

**主要功能:**
- 实时监控CPU、内存、磁盘、网络等系统资源
- 支持自定义阈值告警
- 提供性能分析和压力测试功能
- 多线程安全的数据收集

**主要类:**
- `SystemMonitor`: 系统监控器
- `SystemAlertHandler`: 告警处理器
- `AlertLevel`: 告警级别枚举

**演示场景:**
- 基础系统监控
- 告警系统监控
- 性能分析监控
- 压力测试监控

### 2. performance_monitoring.py
**性能监控模块**

**主要功能:**
- RabbitMQ服务性能实时监控
- 队列、连接、通道等资源指标收集
- 自动化的性能告警系统
- 健康度评分和性能报告生成
- 支持多种数据源集成

**主要类:**
- `PerformanceMonitor`: 性能监控器
- `MetricsAggregator`: 指标聚合器
- `RabbitMQAlertManager`: RabbitMQ告警管理器
- `PerformanceReporting`: 性能报告生成器
- `RabbitMQAPIClient`: RabbitMQ API客户端

**演示场景:**
- 连接测试
- 基础性能监控
- 告警系统演示
- 性能报告生成

### 3. operations_automation.py
**运维自动化模块**

**主要功能:**
- 系统诊断和维护管理
- 备份恢复自动化
- 任务调度和执行
- 健康检查和修复
- 维护窗口管理

**主要类:**
- `SystemDiagnostic`: 系统诊断器
- `MaintenanceManager`: 维护管理器
- `BackupManager`: 备份管理器
- `TaskScheduler`: 任务调度器
- `OperationsAutomationDemo`: 运维自动化演示

**演示场景:**
- 系统诊断
- 维护管理
- 备份恢复
- 任务调度

### 4. log_analysis.py
**日志分析模块**

**主要功能:**
- 日志文件解析和分析
- 实时日志监控
- 错误检测和异常告警
- 性能分析和趋势识别
- 支持自定义日志模式

**主要类:**
- `LogParser`: 日志解析器
- `LogFileReader`: 日志文件阅读器
- `LogAnalyzer`: 日志分析器
- `LogAlertManager`: 日志告警管理器
- `LogAnalysisDemo`: 日志分析演示

**演示场景:**
- 日志文件解析
- 实时日志监控
- 错误分析
- 告警系统

## 环境要求

### Python版本
- Python 3.7+

### 依赖包
```bash
# 基础依赖
psutil>=5.8.0        # 系统资源监控
requests>=2.25.0     # HTTP客户端
threading
datetime
dataclasses
enum
collections
pathlib
json
time
typing
logging

# 可选依赖（性能监控）
pika>=1.1.0          # RabbitMQ客户端（可选）

# 可选依赖（日志分析）
re                  # 正则表达式（标准库）
```

### RabbitMQ要求
- RabbitMQ 3.8+
- Management Plugin 启用
- API访问权限配置

## 使用方法

### 1. 系统监控
```python
from system_monitoring import SystemMonitoringDemo

demo = SystemMonitoringDemo()

# 基础监控
demo.demo_basic_monitoring()

# 告警监控
demo.demo_alert_monitoring()

# 性能分析
demo.demo_performance_analysis()

# 压力测试
demo.demo_stress_testing()
```

### 2. 性能监控
```python
from performance_monitoring import PerformanceMonitoringDemo

demo = PerformanceMonitoringDemo()

# 连接测试
demo.demo_connection_test()

# 性能监控
demo.demo_performance_monitoring()

# 告警系统
demo.demo_alert_system()

# 性能报告
demo.demo_performance_reporting()
```

### 3. 运维自动化
```python
from operations_automation import OperationsAutomationDemo

demo = OperationsAutomationDemo()

# 系统诊断
demo.demo_system_diagnostic()

# 维护管理
demo.demo_maintenance_management()

# 备份恢复
demo.demo_backup_restore()

# 任务调度
demo.demo_task_scheduling()
```

### 4. 日志分析
```python
from log_analysis import LogAnalysisDemo

demo = LogAnalysisDemo()

# 日志解析
demo.demo_log_file_parsing()

# 错误分析
demo.demo_error_analysis()

# 告警系统
demo.demo_alert_system()

# 实时监控
demo.demo_real_time_monitoring()
```

### 5. 完整演示
```python
# 运行所有监控功能演示
demo.run_complete_demo()
```

## 配置参数

### 监控阈值配置
```python
# CPU阈值
CPU_WARN_THRESHOLD = 70.0      # CPU使用率警告阈值（%）
CPU_CRIT_THRESHOLD = 90.0      # CPU使用率严重阈值（%）

# 内存阈值
MEMORY_WARN_THRESHOLD = 75.0   # 内存使用率警告阈值（%）
MEMORY_CRIT_THRESHOLD = 90.0   # 内存使用率严重阈值（%）

# 磁盘阈值
DISK_WARN_THRESHOLD = 80.0     # 磁盘使用率警告阈值（%）
DISK_CRIT_THRESHOLD = 95.0     # 磁盘使用率严重阈值（%）
```

### RabbitMQ配置
```python
RABBITMQ_CONFIG = {
    'host': 'localhost',
    'port': 5672,
    'api_url': 'http://localhost:15672/api',
    'username': 'guest',
    'password': 'guest',
    'vhost': '/',
    'connection_timeout': 30,
    'heartbeat': 60
}
```

### 告警规则配置
```python
# 系统监控告警规则
alert_rules = [
    ('high_cpu', 'cpu_usage_high', 80.0),
    ('high_memory', 'memory_usage_high', 85.0),
    ('disk_full', 'disk_usage_high', 95.0)
]

# 性能监控告警规则
performance_alerts = [
    ('high_error_rate', 'error_rate_high', 5.0),
    ('connection_issues', 'connection_errors', 10.0)
]
```

## 监控指标

### 系统指标
- CPU使用率 (%)
- 内存使用率 (%)
- 磁盘使用率 (%)
- 网络I/O (bytes/sec)
- 进程数
- 系统负载

### RabbitMQ指标
- 队列长度
- 消息速率 (msg/sec)
- 连接数
- 通道数
- 消费者数
- 内存使用量
- 磁盘空间
- 确认率 (%)
- 错误率 (%)

### 业务指标
- 消息处理延迟
- 吞吐量
- 队列积压时间
- 失败消息数
- 重试次数

## 告警级别

1. **INFO (ℹ️)**: 信息性告警
2. **WARNING (⚠️)**: 警告级别
3. **ERROR (❌)**: 错误级别
4. **CRITICAL (🚨)**: 严重级别

## 性能调优建议

### 系统优化
- 调整文件描述符限制
- 优化网络参数
- 配置合适的交换分区
- 定期清理临时文件

### RabbitMQ优化
- 调整内存阈值
- 优化队列配置
- 配置镜像队列
- 使用合适的持久化策略

### 监控优化
- 合理设置采样频率
- 优化告警阈值
- 定期清理历史数据
- 配置日志轮转

## 故障排查

### 常见问题

1. **连接超时**
   - 检查网络连接
   - 验证RabbitMQ服务状态
   - 检查防火墙设置

2. **内存不足**
   - 查看系统内存使用
   - 优化RabbitMQ配置
   - 清理无用队列

3. **磁盘空间不足**
   - 清理日志文件
   - 调整日志轮转配置
   - 监控磁盘使用率

4. **性能下降**
   - 检查CPU使用率
   - 分析网络瓶颈
   - 优化数据库查询

### 日志分析
```python
# 查看错误日志
grep ERROR /var/log/rabbitmq/*.log

# 分析连接问题
grep "connection.*closed" /var/log/rabbitmq/*.log

# 检查队列操作
grep "queue.*error" /var/log/rabbitmq/*.log
```

## 最佳实践

### 监控最佳实践
1. **多维度监控**: 监控所有关键指标
2. **合理阈值**: 根据业务特点设置阈值
3. **及时告警**: 配置自动告警机制
4. **数据保留**: 保留足够的历史数据
5. **定期检查**: 定期检查监控效果

### 运维最佳实践
1. **标准化流程**: 制定标准运维流程
2. **自动化工具**: 使用自动化运维工具
3. **备份策略**: 制定完善的备份策略
4. **应急预案**: 准备故障应急预案
5. **文档维护**: 及时更新运维文档

### 性能优化最佳实践
1. **定期评估**: 定期评估系统性能
2. **容量规划**: 做好容量规划
3. **资源监控**: 持续监控资源使用
4. **优化策略**: 制定优化策略
5. **性能基准**: 建立性能基准

## 扩展开发

### 添加自定义指标
```python
class CustomMetric:
    def __init__(self, name: str, value: float):
        self.name = name
        self.value = value
        self.timestamp = datetime.now()

# 添加到监控器
monitor.add_custom_metric(CustomMetric('custom_metric', 42.0))
```

### 添加自定义告警规则
```python
# 自定义告警规则
def custom_condition(metrics: dict) -> bool:
    return metrics['custom_metric'] > 50.0

alert_manager.add_custom_rule(
    name='custom_alert',
    condition=custom_condition,
    level=AlertLevel.WARNING
)
```

### 添加自定义日志解析器
```python
class CustomLogParser(LogParser):
    def add_custom_pattern(self, pattern: str, event_type: LogEventType):
        # 实现自定义日志解析逻辑
        pass
```

## 注意事项

1. **资源使用**: 监控系统本身也会消耗资源，注意配置合理的采样频率
2. **存储空间**: 历史数据和日志会占用存储空间，需要定期清理
3. **网络影响**: 监控数据采集可能对网络产生影响，需要考虑网络带宽
4. **安全性**: 监控数据包含敏感信息，需要做好安全防护
5. **性能影响**: 避免监控对业务性能产生显著影响

## 版本历史

- v1.0.0: 初始版本，包含基础监控功能
- v1.1.0: 添加性能监控和告警系统
- v1.2.0: 添加运维自动化功能
- v1.3.0: 添加日志分析功能
- v1.4.0: 优化代码性能和稳定性

## 贡献指南

欢迎提交Issue和Pull Request来改进这个监控模块。请遵循以下指南：

1. 代码风格遵循PEP 8
2. 添加适当的文档和注释
3. 包含单元测试
4. 更新版本号和变更日志

## 许可证

本项目采用MIT许可证，详见LICENSE文件。