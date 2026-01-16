@echo off
REM Windows批处理脚本：运行第1章dbt示例

echo ========================================
echo 第1章 dbt基础概念与入门 - 示例运行脚本
echo ========================================

REM 检查dbt是否安装
echo 检查dbt安装...
dbt --version
if %errorlevel% neq 0 (
    echo 错误：dbt未安装或不在PATH中
    echo 请先安装dbt：pip install dbt-postgres
    pause
    exit /b 1
)

echo.
echo 步骤1：编译模型...
dbt compile
if %errorlevel% neq 0 (
    echo 编译失败，请检查模型语法
    pause
    exit /b 1
)

echo.
echo 步骤2：运行模型...
dbt run
if %errorlevel% neq 0 (
    echo 模型运行失败，请检查数据库连接
    pause
    exit /b 1
)

echo.
echo 步骤3：运行测试...
dbt test
if %errorlevel% neq 0 (
    echo 测试失败，请检查数据质量
    pause
    exit /b 1
)

echo.
echo 步骤4：生成文档...
dbt docs generate
if %errorlevel% neq 0 (
    echo 文档生成失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 示例运行完成！
echo ========================================
echo.
echo 下一步操作：
echo 1. 查看文档：dbt docs serve
echo 2. 在浏览器中打开 http://localhost:8080
echo 3. 查看生成的数据模型
echo.

pause