# 数据质量框架使用示例

## 快速开始

### 1. 环境设置
```bash
# 运行快速启动脚本
quick_start.bat

# 或手动设置
setup_venv.bat
```

### 2. 配置数据库连接
编辑 `config/environment.env` 文件：
```ini
# ClickHouse 连接配置
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8123
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=password
CLICKHOUSE_DATABASE=default

# SSL 配置（可选）
CLICKHOUSE_SSL_ENABLED=false
CLICKHOUSE_SSL_VERIFY=false
```

### 3. 配置数据质量规则
编辑 `config/rules.yml` 文件，参考以下示例：

## 规则使用示例

### 完整性检查示例
```yaml
completeness_rules:
  - name: "用户表主键完整性"
    type: "completeness"
    table: "users"
    column: "user_id"
    description: "检查用户ID字段完整性"
    enabled: true
    threshold: 0.99
    
  - name: "订单关键字段完整性"
    type: "completeness"
    table: "orders"
    columns: ["order_id", "user_id", "amount"]
    description: "检查订单关键字段完整性"
    enabled: true
    threshold: 0.98
```

**运行命令**：
```bash
python src/main.py --check-type completeness
```

### 准确性检查示例
```yaml
accuracy_rules:
  - name: "邮箱格式验证"
    type: "accuracy"
    table: "users"
    column: "email"
    description: "验证邮箱格式正确性"
    enabled: true
    validation_type: "email_format"
    
  - name: "年龄范围验证"
    type: "accuracy"
    table: "users"
    column: "age"
    description: "验证年龄在合理范围内"
    enabled: true
    validation_type: "range"
    min_value: 0
    max_value: 150
```

**运行命令**：
```bash
python src/main.py --check-type accuracy
```

### 自定义SQL检查示例
```yaml
custom_sql_rules:
  - name: "收入一致性检查"
    type: "custom_sql"
    description: "检查用户总收入和订单收入是否一致"
    enabled: true
    sql: |
      SELECT 
        u.user_id,
        u.total_income,
        SUM(o.amount) as order_total
      FROM users u
      LEFT JOIN orders o ON u.user_id = o.user_id
      GROUP BY u.user_id, u.total_income
      HAVING ABS(u.total_income - COALESCE(SUM(o.amount), 0)) > 0.01
    expected_result: "empty"
    
  - name: "数据新鲜度检查"
    type: "custom_sql"
    description: "检查最近7天是否有数据更新"
    enabled: true
    sql: |
      SELECT COUNT(*) as recent_records
      FROM orders 
      WHERE order_date >= DATE_SUB(NOW(), INTERVAL 7 DAY)
    expected_result: "not_empty"
    min_records: 1
```

**运行命令**：
```bash
python src/main.py --check-type custom_sql
```

### 通用检查示例
```yaml
generic_checks:
  - name: "用户表行数检查"
    type: "generic"
    description: "检查用户表是否有数据"
    enabled: true
    check_type: "row_count"
    table: "users"
    min_rows: 1
    max_rows: 1000000
    
  - name: "订单状态分布检查"
    type: "generic"
    description: "检查订单状态分布是否合理"
    enabled: true
    check_type: "value_distribution"
    table: "orders"
    column: "status"
    expected_distribution:
      "pending": 0.1
      "completed": 0.8
      "cancelled": 0.1
```

**运行命令**：
```bash
python src/main.py --check-type generic
```

## 业务场景示例

### 电商业务数据质量检查
```yaml
# 用户数据质量
ecommerce_user_rules:
  - name: "用户注册信息完整性"
    type: "completeness"
    table: "users"
    columns: ["user_id", "email", "phone"]
    threshold: 0.98
    
  - name: "用户行为数据新鲜度"
    type: "custom_sql"
    sql: |
      SELECT COUNT(*) as active_users
      FROM user_sessions 
      WHERE last_activity >= DATE_SUB(NOW(), INTERVAL 7 DAY)
    expected_result: "not_empty"
    min_records: 1000

# 订单数据质量  
ecommerce_order_rules:
  - name: "订单金额合理性"
    type: "accuracy"
    table: "orders"
    column: "amount"
    validation_type: "range"
    min_value: 0.01
    max_value: 10000
    
  - name: "订单状态流转逻辑"
    type: "custom_sql"
    sql: |
      SELECT order_id, status, created_at, updated_at
      FROM orders
      WHERE status = 'completed' AND updated_at < created_at
    expected_result: "empty"
```

### 金融业务数据质量检查
```yaml
# 账户数据质量
financial_account_rules:
  - name: "账户余额非负检查"
    type: "accuracy"
    table: "accounts"
    column: "balance"
    validation_type: "range"
    min_value: 0
    max_value: 10000000
    
  - name: "账户状态有效性"
    type: "accuracy"
    table: "accounts"
    column: "status"
    validation_type: "enum"
    allowed_values: ["active", "inactive", "frozen", "closed"]

# 交易数据质量
financial_transaction_rules:
  - name: "交易金额异常检测"
    type: "custom_sql"
    sql: |
      SELECT transaction_id, amount, account_id
      FROM transactions
      WHERE amount > (
        SELECT AVG(amount) + 3 * STDDEV(amount) 
        FROM transactions 
        WHERE transaction_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
      )
      AND transaction_date >= DATE_SUB(NOW(), INTERVAL 1 DAY)
    expected_result: "not_empty"
    max_records: 10
```

## 高级使用技巧

### 1. 并行执行检查
```bash
# 启用并行检查（默认）
python src/main.py --all-checks

# 禁用并行检查
python src/main.py --check-type all --no-parallel
```

### 2. 生成多种格式报告
```bash
# HTML 格式报告（默认）
python src/main.py --output-format html

# JSON 格式报告
python src/main.py --output-format json

# 自定义输出目录
python src/main.py --output-dir ./quality_reports
```

### 3. 仅验证配置
```bash
# 验证配置而不执行检查
python src/main.py --validate-only
```

### 4. 仅生成报告
```bash
# 跳过检查，仅生成报告（用于测试报告格式）
python src/main.py --generate-report
```

### 5. 详细日志输出
```bash
# 启用详细日志
python src/main.py --verbose
```

## 集成到CI/CD流程

### GitHub Actions 示例
```yaml
name: Data Quality Check
on: [push, pull_request]

jobs:
  data-quality:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run data quality checks
      run: |
        python src/main.py --all-checks --output-format json
      env:
        CLICKHOUSE_HOST: ${{ secrets.CLICKHOUSE_HOST }}
        CLICKHOUSE_USER: ${{ secrets.CLICKHOUSE_USER }}
        CLICKHOUSE_PASSWORD: ${{ secrets.CLICKHOUSE_PASSWORD }}
    
    - name: Upload quality report
      uses: actions/upload-artifact@v2
      with:
        name: data-quality-report
        path: reports/
```

### Jenkins Pipeline 示例
```groovy
pipeline {
    agent any
    stages {
        stage('Data Quality Check') {
            steps {
                script {
                    bat '''
                        call venv\\Scripts\\activate.bat
                        python src\\main.py --all-checks --output-format html
                    '''
                }
            }
            post {
                always {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'reports',
                        reportFiles: 'data_quality_report.html',
                        reportName: 'Data Quality Report'
                    ])
                }
            }
        }
    }
}
```

## 故障排除

### 常见问题及解决方案

1. **数据库连接失败**
   - 检查 `environment.env` 配置文件
   - 验证数据库服务是否运行
   - 检查网络连接和防火墙设置

2. **规则执行失败**
   - 检查规则配置语法
   - 验证SQL语句的正确性
   - 查看详细日志：`python src/main.py --verbose`

3. **报告生成失败**
   - 检查输出目录权限
   - 验证模板文件是否存在
   - 查看模板语法错误

4. **性能问题**
   - 减少并行检查数量
   - 优化SQL查询语句
   - 增加超时时间设置

### 调试技巧

```bash
# 启用调试模式
set LOG_LEVEL=DEBUG
python src/main.py --verbose

# 检查单个规则
python src/main.py --rules "用户表主键完整性"

# 生成详细日志文件
python src/main.py --all-checks 2>&1 | tee quality_check.log
```

## 扩展开发

如需添加新的规则类型，请参考现有实现：

1. 在 `rule_engine.py` 中添加新的执行方法
2. 在 `DataQualityRule` 类中支持新的规则类型
3. 更新配置解析逻辑
4. 添加相应的测试用例

---

*更多详细信息请参考框架文档和源代码注释。*