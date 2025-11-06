@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   数据质量框架快速启动脚本
echo ========================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python环境，请先安装Python 3.7+
    pause
    exit /b 1
)

REM 检查虚拟环境
if not exist "venv" (
    echo [信息] 创建Python虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
echo [信息] 安装依赖包...
pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

REM 检查配置文件
if not exist "config\environment.env" (
    echo [信息] 创建环境配置文件...
    if exist "config\environment.env.example" (
        copy "config\environment.env.example" "config\environment.env"
        echo [提示] 请编辑 config\environment.env 文件配置数据库连接信息
    ) else (
        echo [警告] 未找到环境配置文件模板
    )
)

if not exist "config\rules.yml" (
    echo [信息] 创建规则配置文件...
    if exist "config\example_rules.yml" (
        copy "config\example_rules.yml" "config\rules.yml"
        echo [提示] 请编辑 config\rules.yml 文件配置数据质量规则
    ) else (
        echo [警告] 未找到规则配置文件模板
    )
)

echo.
echo ========================================
echo   快速启动菜单
echo ========================================
echo.
echo 1. 运行完整性检查
echo 2. 运行准确性检查
echo 3. 运行自定义SQL检查
echo 4. 运行所有规则检查
echo 5. 生成测试报告
echo 6. 查看规则指南
echo 7. 退出
echo.

set /p choice=请选择操作 (1-7): 

echo.

if "%choice%"=="1" (
    echo [信息] 运行完整性检查...
    python src\main.py --check-type completeness
) else if "%choice%"=="2" (
    echo [信息] 运行准确性检查...
    python src\main.py --check-type accuracy
) else if "%choice%"=="3" (
    echo [信息] 运行自定义SQL检查...
    python src\main.py --check-type custom_sql
) else if "%choice%"=="4" (
    echo [信息] 运行所有规则检查...
    python src\main.py --all-checks
) else if "%choice%"=="5" (
    echo [信息] 生成测试报告...
    python src\main.py --generate-report
) else if "%choice%"=="6" (
    echo [信息] 打开规则指南...
    if exist "RULES_GUIDE.md" (
        start "" "RULES_GUIDE.md"
    ) else (
        echo [错误] 未找到规则指南文件
    )
) else if "%choice%"=="7" (
    echo [信息] 退出...
    goto :exit
) else (
    echo [错误] 无效选择
    goto :menu
)

if errorlevel 1 (
    echo [错误] 执行失败，请检查配置
    pause
    exit /b 1
)

:menu
echo.
set /p continue=是否继续？(y/n): 
if /i "%continue%"=="y" goto :menu_start

:exit
echo.
echo ========================================
echo   框架使用提示
echo ========================================
echo.
echo 1. 配置数据库连接：编辑 config\environment.env
echo 2. 自定义规则：编辑 config\rules.yml
echo 3. 查看详细文档：阅读 RULES_GUIDE.md
echo 4. 运行测试：python -m pytest tests\
echo.
echo 感谢使用数据质量框架！
echo.
pause

:menu_start
call quick_start.bat