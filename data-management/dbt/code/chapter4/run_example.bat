@echo off
echo ========================================
echo 第4章：dbt宏与Jinja模板 - 运行示例
echo ========================================

REM 检查dbt是否安装
echo 检查dbt安装...
dbt --version >nul 2>&1
if errorlevel 1 (
    echo 错误: dbt未安装或未配置
    echo 请先安装dbt: pip install dbt-core
    pause
    exit /b 1
)

echo dbt已安装，继续执行...

REM 检查dbt项目配置
echo 检查dbt项目配置...
if not exist "dbt_project.yml" (
    echo 错误: dbt_project.yml文件不存在
    pause
    exit /b 1
)

echo 项目配置正常，开始执行...

REM 步骤1: 编译模型，查看宏生成的SQL
echo.
echo 步骤1: 编译模型，查看宏生成的SQL...
dbt compile --models tag:chapter4
if errorlevel 1 (
    echo 错误: 模型编译失败
    pause
    exit /b 1
)

echo 编译成功！可以在target/compiled目录查看生成的SQL

REM 步骤2: 运行模型
echo.
echo 步骤2: 运行模型...
dbt run --models tag:chapter4
if errorlevel 1 (
    echo 错误: 模型运行失败
    pause
    exit /b 1
)

echo 模型运行成功！

REM 步骤3: 测试宏功能
echo.
echo 步骤3: 测试宏功能...
dbt test --models tag:chapter4
if errorlevel 1 (
    echo 警告: 部分测试失败，但这是正常的演示过程
) else (
    echo 所有测试通过！
)

REM 步骤4: 生成文档
echo.
echo 步骤4: 生成文档...
dbt docs generate
if errorlevel 1 (
    echo 警告: 文档生成失败，但可以继续
) else (
    echo 文档生成成功！
)

REM 步骤5: 查看宏使用情况
echo.
echo 步骤5: 查看宏使用情况...
echo.
echo 已创建的宏文件:
dir macros\*.sql /b
echo.
echo 在模型中使用的宏示例:
echo - format_date: 日期格式化
echo - trim_string: 字符串去空格
echo - conditional_sum: 条件求和
echo - generate_dynamic_model: 动态模型生成
echo - validate_email_format: 邮箱格式验证

REM 步骤6: 查看编译后的SQL
echo.
echo 步骤6: 查看编译后的SQL示例...
if exist "target\compiled\dbt_macros_example\models\staging\stg_customers.sql" (
    echo 编译后的stg_customers.sql前10行:
    echo ========================================
    powershell -Command "Get-Content 'target\compiled\dbt_macros_example\models\staging\stg_customers.sql' | Select-Object -First 10"
    echo ========================================
)

echo.
echo ========================================
echo 第4章示例运行完成！
echo ========================================
echo.
echo 学习要点总结:
echo 1. 宏的基本语法和参数传递
echo 2. 常用宏模式（日期、字符串、条件聚合）
echo 3. 动态SQL生成技术
echo 4. 数据验证和错误处理
echo 5. 宏的模块化和重用
echo.
echo 下一步操作建议:
echo 1. 查看target/compiled目录下的编译后SQL，了解宏展开效果
echo 2. 修改宏参数，观察生成的SQL变化
echo 3. 创建新的宏来扩展功能
echo 4. 运行dbt docs serve查看文档
echo.

pause