# Day 6: 高级DAG设计练习题

## 练习1: 工厂模式DAG实现

### 题目要求
创建一个使用工厂模式的DAG，实现以下功能：

1. 创建一个数据处理工厂函数，能够生成不同类型的处理任务
2. 实现数据提取、转换、加载三个标准任务类型
3. 支持自定义处理函数和参数
4. 实现错误处理和日志记录

### 提示代码
```python
# 基础框架
class TaskFactory:
    def create_task(self, task_type, task_id, **kwargs):
        # 实现工厂方法
        pass
```

### 练习目标
- 理解工厂模式在DAG设计中的应用
- 掌握可重用任务组件的创建
- 学习参数化任务配置

## 练习2: 配置驱动DAG构建器

### 题目要求
设计一个配置驱动的DAG构建器，要求：

1. 从YAML配置文件读取DAG定义
2. 支持多种任务类型（PythonOperator、BashOperator等）
3. 自动解析任务依赖关系
4. 实现配置验证和错误处理

### 配置文件示例
```yaml
dag:
  id: "config_driven_example"
  description: "配置驱动的数据管道"
  schedule: "@daily"

tasks:
  - id: "extract_data"
    type: "python"
    function: "extract_function"
    args:
      source: "database"
  
  - id: "transform_data"
    type: "python"
    function: "transform_function"
    depends_on: ["extract_data"]
```

### 练习目标
- 掌握配置与代码分离的设计思想
- 学习动态DAG生成技术
- 理解配置验证的重要性

## 练习3: 动态DAG生成器

### 题目要求
创建一个动态DAG生成器，能够：

1. 从数据库读取工作流配置
2. 根据配置动态生成DAG
3. 支持多种数据源（文件、API、数据库）
4. 实现配置缓存和刷新机制

### 数据库表结构建议
```sql
CREATE TABLE workflow_configs (
    id INT PRIMARY KEY,
    dag_id VARCHAR(100),
    config JSON,
    is_active BOOLEAN,
    created_at TIMESTAMP
);
```

### 练习目标
- 理解动态DAG的应用场景
- 掌握数据库驱动的配置管理
- 学习配置缓存和性能优化

## 练习4: 子DAG设计与实现

### 题目要求
设计一个包含子DAG的复杂工作流：

1. 创建数据提取子DAG
2. 创建数据处理子DAG
3. 创建数据加载子DAG
4. 在主DAG中协调子DAG的执行

### 子DAG接口设计
```python
def create_extraction_subdag(parent_dag_name, child_dag_name, args):
    """数据提取子DAG"""
    pass

def create_processing_subdag(parent_dag_name, child_dag_name, args):
    """数据处理子DAG"""
    pass
```

### 练习目标
- 掌握子DAG的设计和使用
- 理解复杂工作流的模块化分解
- 学习子DAG之间的协调机制

## 练习5: 条件分支与并行执行

### 题目要求
实现一个包含条件分支和并行执行的DAG：

1. 基于数据质量检查结果选择处理路径
2. 实现数据分区的并行处理
3. 使用不同的触发规则控制任务执行
4. 实现错误处理和重试机制

### 分支逻辑示例
```python
def decide_processing_branch(**kwargs):
    quality_score = kwargs['ti'].xcom_pull(task_ids='quality_check')
    
    if quality_score >= 95:
        return 'high_quality_path'
    elif quality_score >= 80:
        return 'standard_path'
    else:
        return 'reprocess_path'
```

### 练习目标
- 掌握条件分支的实现
- 学习并行执行优化
- 理解触发规则的应用

## 练习6: 高级错误处理机制

### 题目要求
设计一个健壮的错误处理系统：

1. 实现任务级别的错误捕获和处理
2. 创建全局错误处理任务
3. 支持多种错误处理策略（重试、告警、跳过）
4. 实现错误日志和指标收集

### 错误处理策略
```python
error_handlers = {
    'retry': {
        'max_retries': 3,
        'delay': timedelta(minutes=5)
    },
    'alert': {
        'channels': ['email', 'slack'],
        'threshold': 3
    },
    'skip': {
        'conditions': ['data_not_available']
    }
}
```

### 练习目标
- 掌握高级错误处理技术
- 学习错误恢复策略
- 理解监控和告警集成

## 练习7: 性能优化实践

### 题目要求
优化一个现有的DAG，提高其性能：

1. 分析DAG执行瓶颈
2. 优化任务执行时间
3. 合理配置资源池
4. 实现任务并行化

### 性能指标
```python
performance_metrics = {
    'total_execution_time': '目标: 减少30%',
    'task_parallelism': '目标: 提高50%',
    'resource_utilization': '目标: 优化资源分配'
}
```

### 练习目标
- 掌握DAG性能分析方法
- 学习任务优化技术
- 理解资源管理策略

## 练习8: 监控与指标收集

### 题目要求
为DAG添加全面的监控和指标收集：

1. 实现自定义业务指标
2. 集成外部监控系统
3. 创建性能仪表板
4. 实现告警规则

### 监控指标示例
```python
metrics_to_collect = [
    'task_execution_time',
    'data_processing_volume',
    'error_rate',
    'success_rate',
    'resource_consumption'
]
```

### 练习目标
- 掌握DAG监控技术
- 学习指标收集和分析
- 理解告警系统集成

## 综合练习: 完整的数据管道设计

### 题目要求
设计并实现一个完整的数据管道，包含：

1. **配置管理**: 使用YAML配置驱动DAG生成
2. **模块化设计**: 使用工厂模式和子DAG
3. **错误处理**: 实现全面的错误恢复机制
4. **性能优化**: 优化任务执行和资源使用
5. **监控告警**: 集成监控和告警系统

### 管道架构
```
配置管理 → DAG生成 → 任务执行 → 监控告警
    ↓           ↓           ↓           ↓
YAML配置   工厂模式   错误处理   指标收集
```

### 练习目标
- 综合运用所有高级DAG设计技术
- 理解完整数据管道的架构设计
- 掌握端到端的DAG开发流程

## 练习评估标准

### 代码质量（40%）
- 代码可读性和结构清晰
- 遵循Python最佳实践
- 适当的注释和文档

### 功能完整性（30%）
- 所有要求功能正确实现
- 错误处理机制完善
- 配置和参数化支持

### 设计模式应用（20%）
- 合理使用设计模式
- 模块化和可扩展性
- 代码复用性

### 性能优化（10%）
- 任务执行效率
- 资源使用优化
- 监控指标实现

## 练习提交要求

1. 每个练习提交完整的Python代码文件
2. 包含必要的配置文件和测试数据
3. 提供README说明使用方法和设计思路
4. 包含单元测试和集成测试
5. 性能优化练习需要提供优化前后的对比数据

## 学习建议

1. **循序渐进**: 从简单练习开始，逐步挑战复杂练习
2. **实践为主**: 多动手编写代码，理解设计模式的应用
3. **代码审查**: 与同学互相review代码，学习最佳实践
4. **文档记录**: 记录学习心得和遇到的问题
5. **持续改进**: 根据反馈不断优化代码设计

通过完成这些练习，您将全面掌握Airflow高级DAG设计的核心技能，能够构建复杂、健壮的数据工作流系统。