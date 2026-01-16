@echo off
chcp 65001 >nul

echo.
echo ========================================
echo   第6章：dbt最佳实践与项目结构
echo ========================================
echo.

echo [1/10] 检查dbt环境配置...
dbt --version
echo.

if errorlevel 1 (
    echo ❌ dbt环境未正确配置，请先安装dbt
    echo 安装命令: pip install dbt-core dbt-postgres
    pause
    exit /b 1
)

echo [2/10] 显示项目配置信息...
echo 项目名称: 电商数据平台 - 最佳实践示例
echo 项目路径: %CD%
echo 目标环境: development
echo.

echo [3/10] 验证数据库连接...
dbt debug
if errorlevel 1 (
    echo ❌ 数据库连接失败，请检查profiles.yml配置
    pause
    exit /b 1
)

echo [4/10] 编译项目模型...
dbt compile
if errorlevel 1 (
    echo ❌ 模型编译失败
    pause
    exit /b 1
)

echo [5/10] 运行数据测试...
dbt test
if errorlevel 1 (
    echo ⚠️ 部分测试失败，继续执行...
)

echo [6/10] 运行模型构建...
dbt run
if errorlevel 1 (
    echo ❌ 模型运行失败
    pause
    exit /b 1
)

echo [7/10] 生成项目文档...
dbt docs generate
if errorlevel 1 (
    echo ⚠️ 文档生成失败，跳过此步骤
)

echo [8/10] 显示数据血缘关系...
dbt docs serve --port 8080 &
echo 文档服务器已启动: http://localhost:8080
echo.

echo [9/10] 运行特定模型测试...
dbt test --select stg_customers
dbt test --select int_customer_metrics
dbt test --select dim_customers
echo.

echo [10/10] 显示项目结构总结...
echo.
echo 📁 项目结构:
echo ├── models/              - 数据模型
echo │   ├── staging/         - 数据清洗层
echo │   ├── intermediate/    - 业务逻辑层  
echo │   ├── marts/           - 数据集市层
echo │   ├── seeds/           - 种子数据
echo │   └── docs/            - 文档配置
echo ├── macros/              - 可复用宏
echo │   └── utils/           - 工具宏
echo ├── tests/               - 测试配置
echo │   ├── models/          - 模型测试
echo │   └── custom/          - 自定义测试
echo ├── data/                - 种子数据文件
echo ├── dbt_project.yml      - 项目配置
echo └── profiles.yml         - 连接配置
echo.

echo ✅ 第6章最佳实践示例运行完成！
echo.

echo 📚 学习要点总结:
echo 1. 标准化项目结构设计
echo 2. 分层数据建模方法
echo 3. 配置管理和环境隔离
echo 4. 测试覆盖和质量保障
echo 5. 文档化和可维护性
echo 6. 性能优化和安全实践
echo.

echo 🚀 下一步操作建议:
echo 1. 查看生成的文档: http://localhost:8080
echo 2. 修改模型配置测试不同场景
echo 3. 添加新的自定义测试用例
echo 4. 扩展项目支持更多业务领域
echo 5. 配置CI/CD自动化流程
echo.

pause