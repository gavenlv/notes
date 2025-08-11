@echo off
REM 数据质量框架 v2.0 Windows示例运行脚本

echo 数据质量框架 v2.0 示例演示
echo ================================

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Python未安装或未添加到PATH
    pause
    exit /b 1
)

echo Python环境检查通过

:menu
echo.
echo 请选择要运行的示例:
echo 1^) 显示帮助信息
echo 2^) 列出可用场景
echo 3^) 列出支持的数据库
echo 4^) 验证配置文件
echo 5^) 测试数据库连接
echo 6^) 运行ClickHouse冒烟测试
echo 7^) 生成HTML报告示例
echo 8^) 查看生成的报告
echo 9^) 快速测试
echo 0^) 运行基础示例
echo q^) 退出
echo.

set /p choice=请输入选择 [1-9/0/q]: 

if "%choice%"=="1" goto help
if "%choice%"=="2" goto scenarios
if "%choice%"=="3" goto databases
if "%choice%"=="4" goto validate
if "%choice%"=="5" goto testconn
if "%choice%"=="6" goto smoke
if "%choice%"=="7" goto reports
if "%choice%"=="8" goto view
if "%choice%"=="9" goto quick
if "%choice%"=="0" goto basic
if "%choice%"=="q" goto exit
if "%choice%"=="Q" goto exit

echo 无效选择，请重新输入
goto menu

:help
echo 显示帮助信息...
python data_quality_runner.py --help
pause
goto menu

:scenarios
echo 列出所有可用的测试场景...
python data_quality_runner.py --list-scenarios
pause
goto menu

:databases
echo 列出支持的数据库类型...
python data_quality_runner.py --list-databases
pause
goto menu

:validate
echo 验证配置文件...
python data_quality_runner.py --validate-config
pause
goto menu

:testconn
echo 测试数据库连接...
python data_quality_runner.py --test-connection
pause
goto menu

:smoke
echo 运行ClickHouse冒烟测试...
python data_quality_runner.py --scenario clickhouse_smoke_test
pause
goto menu

:reports
echo 生成HTML报告示例...
python data_quality_runner.py --scenario clickhouse_smoke_test --output-dir reports\demo
if exist "reports\demo" (
    echo 报告已生成到 reports\demo 目录
    dir reports\demo
)
pause
goto menu

:view
echo 查看生成的报告文件...
if exist "reports" (
    echo 报告目录结构:
    dir reports /s *.html *.json *.txt 2>nul
    echo.
    echo 可以用浏览器打开HTML文件查看详细报告
) else (
    echo 没有找到报告目录
)
pause
goto menu

:quick
echo 运行快速测试...
echo 1. 验证配置
python data_quality_runner.py --validate-config
echo.
echo 2. 测试连接
python data_quality_runner.py --test-connection
echo.
echo 3. 列出场景
python data_quality_runner.py --list-scenarios
pause
goto menu

:basic
echo 运行基础示例...
echo 1. 显示帮助
python data_quality_runner.py --help
echo.
echo 2. 列出场景
python data_quality_runner.py --list-scenarios
echo.
echo 3. 列出数据库
python data_quality_runner.py --list-databases
echo.
echo 4. 验证配置
python data_quality_runner.py --validate-config
pause
goto menu

:exit
echo 退出示例程序
exit /b 0

