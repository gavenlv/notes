@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 第5章：dbt数据源与连接配置 - 运行示例脚本
REM 演示数据源定义、多环境配置、连接测试等特性

echo.
echo ========================================
echo   第5章：dbt数据源与连接配置
echo ========================================
echo.

REM 检查dbt是否安装
where dbt >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ dbt未安装或不在PATH中
    echo 请先安装dbt: pip install dbt-core
    exit /b 1
)

REM 检查当前目录是否为dbt项目
if not exist "dbt_project.yml" (
    echo ❌ 当前目录不是dbt项目根目录
    echo 请在dbt项目根目录运行此脚本
    exit /b 1
)

echo ✅ dbt环境检查通过
echo.

REM 步骤1：显示项目配置信息
echo 步骤1: 显示项目配置信息
echo ----------------------------------------
dbt debug --config-file
if %errorlevel% neq 0 (
    echo ❌ 项目配置检查失败
    exit /b 1
)
echo.

REM 步骤2：测试数据库连接
echo 步骤2: 测试数据库连接
echo ----------------------------------------
echo 测试开发环境连接...
dbt debug --target dev
if %errorlevel% neq 0 (
    echo ⚠️ 开发环境连接失败（这是正常的，因为没有真实数据库）
    echo 继续演示其他功能...
) else (
    echo ✅ 开发环境连接成功
)
echo.

REM 步骤3：显示数据源定义
echo 步骤3: 显示数据源定义
echo ----------------------------------------
echo 列出所有数据源...
dbt source list
if %errorlevel% neq 0 (
    echo ⚠️ 数据源列表获取失败（可能没有真实数据源）
) else (
    echo ✅ 数据源列表成功获取
)
echo.

REM 步骤4：编译模型查看SQL
echo 步骤4: 编译模型查看生成的SQL
echo ----------------------------------------
echo 编译staging层模型...
dbt compile --select staging.* --target dev
if %errorlevel% neq 0 (
    echo ⚠️ 模型编译失败（没有真实数据库）
    echo 继续演示其他功能...
) else (
    echo ✅ 模型编译成功
    echo 编译后的SQL文件位于target/compiled目录
)
echo.

REM 步骤5：运行Python连接测试脚本
echo 步骤5: 运行连接测试脚本
echo ----------------------------------------
if exist "scripts\test_connections.py" (
    echo 运行Python连接测试脚本...
    python scripts\test_connections.py
    if %errorlevel% neq 0 (
        echo ⚠️ 连接测试脚本运行失败（预期行为，因为没有真实数据库）
    ) else (
        echo ✅ 连接测试脚本运行成功
    )
) else (
    echo ❌ 连接测试脚本不存在
)
echo.

REM 步骤6：生成文档
echo 步骤6: 生成项目文档
echo ----------------------------------------
echo 生成dbt文档...
dbt docs generate
if %errorlevel% neq 0 (
    echo ⚠️ 文档生成失败（可能缺少依赖）
) else (
    echo ✅ 文档生成成功
    echo 文档文件位于target目录
)
echo.

REM 步骤7：显示数据血缘关系
echo 步骤7: 显示数据血缘关系
echo ----------------------------------------
echo 生成数据血缘图...
dbt docs generate
if %errorlevel% eq 0 (
    echo ✅ 数据血缘图生成成功
    echo 使用 dbt docs serve 查看交互式文档
) else (
    echo ⚠️ 数据血缘图生成失败
)
echo.

REM 步骤8：环境配置演示
echo 步骤8: 环境配置演示
echo ----------------------------------------
echo 显示可用的目标环境...
dbt debug --config-dir
if %errorlevel% neq 0 (
    echo ⚠️ 环境配置显示失败
) else (
    echo ✅ 环境配置显示成功
)
echo.

REM 步骤9：数据源测试配置演示
echo 步骤9: 数据源测试配置演示
echo ----------------------------------------
echo 显示数据源测试配置...
if exist "tests\sources\test_sources.yml" (
    type tests\sources\test_sources.yml | head -20
    echo ...
    echo ✅ 数据源测试配置加载成功
) else (
    echo ❌ 数据源测试配置文件不存在
)
echo.

REM 步骤10：多环境配置演示
echo 步骤10: 多环境配置演示
echo ----------------------------------------
echo 显示环境配置示例...
if exist "config\env_configs.yml" (
    type config\env_configs.yml | head -30
    echo ...
    echo ✅ 环境配置示例加载成功
) else (
    echo ❌ 环境配置文件不存在
)
echo.

REM 学习要点总结
echo.
echo ========================================
echo   学习要点总结
echo ========================================
echo.
echo ✅ 数据源定义: 使用sources.yml定义外部数据源
echo ✅ 多环境配置: 支持开发、测试、生产等环境
echo ✅ 连接配置: 通过profiles.yml管理数据库连接
echo ✅ 数据新鲜度: 监控数据源的新鲜度状态
echo ✅ 环境变量: 使用环境变量管理敏感信息
echo ✅ 连接测试: 自动化测试数据库连接
echo ✅ 数据血缘: 可视化数据源到模型的转换关系
echo.

REM 下一步操作建议
echo ========================================
echo   下一步操作建议
echo ========================================
echo.
echo 1. 配置真实的数据库连接信息:
echo    - 编辑 profiles.yml 文件
echo    - 设置正确的数据库连接参数
echo.
echo 2. 运行完整的数据源测试:
echo    - dbt source freshness
echo    - dbt test --select source:*
echo.
echo 3. 查看数据血缘关系:
echo    - dbt docs serve
echo    - 在浏览器中查看交互式文档
echo.
echo 4. 实践环境切换:
echo    - dbt run --target dev
echo    - dbt run --target prod (如果配置了生产环境)
echo.
echo 5. 学习第6章: dbt最佳实践与项目结构
echo.

echo 脚本执行完成!
echo 请查看上面的输出了解第5章的核心概念
echo.

pause