# 数据质量框架 v2.0 快速开始

## 🚀 5分钟快速体验

### 1. 环境准备

```bash
# 检查Python版本 (需要3.8+)
python --version

# 安装依赖
pip install PyYAML

# 可选：安装数据库驱动
pip install clickhouse-driver  # ClickHouse
pip install pymysql            # MySQL
pip install psycopg2-binary    # PostgreSQL
```

### 2. 快速验证

```bash
# Windows用户
cd data-quality
run_examples.bat

# Linux/Mac用户
cd data-quality
./run_examples.sh help
```

### 3. 基础命令

```bash
# 查看帮助
python data_quality_runner.py --help

# 列出所有场景
python data_quality_runner.py --list-scenarios

# 验证配置
python data_quality_runner.py --validate-config

# 测试数据库连接（需要先配置数据库）
python data_quality_runner.py --test-connection
```

### 4. 运行示例场景

```bash
# 运行ClickHouse冒烟测试（需要ClickHouse服务）
python data_quality_runner.py --scenario clickhouse_smoke_test

# 在不同环境运行
python data_quality_runner.py --scenario clickhouse_smoke_test --env test

# 自定义输出目录
python data_quality_runner.py --scenario clickhouse_smoke_test --output-dir my_reports/
```

## 📊 查看报告

运行完成后，报告会生成在 `reports/` 目录：

- `*.html` - 自动化测试风格的HTML报告（推荐）
- `*.json` - 机器可读的JSON格式报告
- `*.txt` - 简单的文本格式报告

### HTML报告特点

- ✅ 类似Jest/JUnit的测试结果展示
- 📈 清晰的统计图表和进度条
- 🔍 点击展开查看详细信息
- 📱 支持移动端浏览
- 🎨 现代化的UI设计

## 🔧 自定义配置

### 数据库配置

编辑 `configs/data-quality-config-v2.yml`：

```yaml
database:
  type: "clickhouse"        # 数据库类型
  host: "localhost"         # 主机地址
  port: 9000               # 端口
  database: "your_db"      # 数据库名
  user: "your_user"        # 用户名
  password: "your_pass"    # 密码
```

### 多环境配置

```yaml
environments:
  dev:
    database:
      host: "dev-server"
      database: "dev_db"
  prod:
    database:
      host: "prod-server"
      database: "prod_db"
      secure: true
```

## 📝 创建自定义规则

1. 在 `rules/` 目录创建YAML文件：

```yaml
rule_type: "completeness"
description: "我的自定义规则"

rule:
  name: "my_custom_check"
  description: "检查表的完整性"
  category: "completeness"
  priority: "high"
  
  target:
    database: "my_database"
    table: "my_table"
    
  template: |
    SELECT 
      COUNT(*) as total_rows,
      COUNT(CASE WHEN id IS NULL THEN 1 END) as null_ids,
      CASE 
        WHEN COUNT(CASE WHEN id IS NULL THEN 1 END) > 0 THEN 'FAIL'
        ELSE 'PASS'
      END as check_result
    FROM my_database.my_table
```

2. 将规则添加到场景中：

```yaml
# scenarios/my_scenario.yml
name: "my_scenario"
description: "我的测试场景"

rules:
  paths:
    - "rules/my_custom_rules.yml"
    
database:
  type: "clickhouse"
  host: "localhost"
  # ... 其他配置
```

3. 运行自定义场景：

```bash
python data_quality_runner.py --scenario my_scenario
```

## 🎯 常见使用场景

### 冒烟测试
快速验证核心数据质量：
```bash
python data_quality_runner.py --scenario smoke_test
```

### 回归测试
全面的数据质量检查：
```bash
python data_quality_runner.py --scenario regression --env test
```

### 持续监控
定期检查数据质量：
```bash
python data_quality_runner.py --scenario monitoring --env prod
```

### 多数据库对比
```bash
# ClickHouse环境
python data_quality_runner.py --scenario comparison --database clickhouse_prod

# MySQL环境
python data_quality_runner.py --scenario comparison --database mysql_prod
```

## 🚨 故障排除

### 连接问题
```bash
# 检查数据库连接
python data_quality_runner.py --test-connection

# 查看详细日志
python data_quality_runner.py --scenario test --log-level DEBUG
```

### 配置问题
```bash
# 验证配置文件
python data_quality_runner.py --validate-config

# 查看配置摘要
python data_quality_runner.py --list-scenarios
```

### 依赖问题
```bash
# 检查Python包
pip list | grep -E "(yaml|click)"

# 安装数据库驱动
pip install clickhouse-driver pymysql psycopg2-binary
```

## 🔗 更多资源

- 📖 [完整文档](README-v2.md)
- 🔧 [配置说明](configs/data-quality-config-v2.yml)
- 📝 [规则示例](examples/custom_rule_example.yml)
- 🎮 [交互式示例](run_examples.sh)

## 💡 提示

1. **首次使用**：建议先运行 `--validate-config` 和 `--test-connection`
2. **开发调试**：使用 `--log-level DEBUG` 获取详细信息
3. **生产环境**：配置环境隔离和通知功能
4. **性能优化**：调整 `--max-workers` 参数控制并行度
5. **报告管理**：定期清理旧报告，设置保留策略

开始您的数据质量之旅吧！🎉

