@echo off
REM 第7章：dbt高级特性与自定义操作运行脚本
REM 演示完整的高级特性项目运行流程

echo ========================================
echo dbt高级特性与自定义操作 - 第7章
echo ========================================
echo.

REM 设置环境变量
set PROJECT_DIR=%~dp0
set DBT_PROJECT_FILE=%PROJECT_DIR%dbt_project.yml
set PACKAGES_FILE=%PROJECT_DIR%packages.yml

REM 检查dbt安装
echo [1/10] 检查dbt环境...
dbt --version
if %errorlevel% neq 0 (
    echo 错误: dbt未正确安装或配置
    exit /b 1
)
echo dbt环境检查通过

REM 检查项目配置
echo.
echo [2/10] 检查项目配置文件...
if not exist "%DBT_PROJECT_FILE%" (
    echo 错误: dbt_project.yml文件不存在
    exit /b 1
)
if not exist "%PACKAGES_FILE%" (
    echo 错误: packages.yml文件不存在
    exit /b 1
)
echo 项目配置文件检查通过

REM 显示项目配置
echo.
echo [3/10] 显示项目配置信息...
dbt debug --config-dir
dbt debug --project-dir "%PROJECT_DIR%"
echo.

REM 安装包依赖
echo [4/10] 安装包依赖...
dbt deps --project-dir "%PROJECT_DIR%"
if %errorlevel% neq 0 (
    echo 警告: 包依赖安装过程中出现警告
)
echo 包依赖安装完成

REM 编译项目
echo.
echo [5/10] 编译dbt项目...
dbt compile --project-dir "%PROJECT_DIR%" --target dev
if %errorlevel% neq 0 (
    echo 错误: 项目编译失败
    exit /b 1
)
echo 项目编译成功

REM 运行数据测试
echo.
echo [6/10] 运行数据测试...
dbt test --project-dir "%PROJECT_DIR%" --target dev
if %errorlevel% neq 0 (
    echo 警告: 部分测试失败，继续执行...
)
echo 数据测试完成

REM 构建高级模型
echo.
echo [7/10] 构建高级特性模型...
echo 构建复杂宏模型...
dbt run --model tag:complex-macros --project-dir "%PROJECT_DIR%" --target dev
if %errorlevel% neq 0 (
    echo 错误: 复杂宏模型构建失败
    exit /b 1
)

echo 构建自定义物料化模型...
dbt run --model tag:custom --project-dir "%PROJECT_DIR%" --target dev
if %errorlevel% neq 0 (
    echo 错误: 自定义物料化模型构建失败
    exit /b 1
)

echo 构建钩子函数模型...
dbt run --model tag:hooks --project-dir "%PROJECT_DIR%" --target dev
if %errorlevel% neq 0 (
    echo 错误: 钩子函数模型构建失败
    exit /b 1
)

echo 高级特性模型构建完成

REM 生成文档
echo.
echo [8/10] 生成项目文档...
dbt docs generate --project-dir "%PROJECT_DIR%"
if %errorlevel% neq 0 (
    echo 警告: 文档生成过程中出现警告
)
echo 项目文档生成完成

REM 显示数据血缘关系
echo.
echo [9/10] 显示数据血缘关系...
dbt docs serve --project-dir "%PROJECT_DIR%" --port 8080 &
echo 文档服务器启动在 http://localhost:8080
echo 按Ctrl+C停止服务器

REM 运行特定高级测试
echo.
echo [10/10] 运行高级特性测试...
dbt test --model tag:advanced-testing --project-dir "%PROJECT_DIR%" --target dev
if %errorlevel% neq 0 (
    echo 警告: 高级测试部分失败
)
echo 高级特性测试完成

REM 项目结构总结
echo.
echo ========================================
echo 项目运行总结
echo ========================================
echo.
echo 项目目录结构:
dir "%PROJECT_DIR%" /B
echo.

echo 模型文件:
dir "%PROJECT_DIR%models" /B /S
echo.

echo 宏文件:
dir "%PROJECT_DIR%macros" /B /S
echo.

echo 测试文件:
dir "%PROJECT_DIR%tests" /B /S
echo.

REM 学习要点总结
echo ========================================
echo 学习要点总结
echo ========================================
echo.
echo 1. 高级宏开发
echo    - 动态SQL生成器
echo    - 递归CTE处理
echo    - 模板继承模式
echo    - 宏包管理
echo.

echo 2. 自定义物料化策略
echo    - 增量模型高级配置
echo    - 分区增量策略
echo    - 物化视图优化
echo    - 条件物料化
echo.

echo 3. 钩子函数与事件处理
echo    - 模型级钩子配置
echo    - 项目级钩子管理
echo    - 错误处理机制
echo    - 性能监控集成
echo.

echo 4. 包管理与依赖
echo    - 多层包依赖管理
echo    - 版本控制策略
echo    - 安全配置选项
echo    - 性能优化配置
echo.

echo 5. 性能优化高级技巧
echo    - 查询优化策略
echo    - 内存管理优化
echo    - 并发控制配置
echo    - 缓存策略实施
echo.

REM 下一步操作建议
echo.
echo ========================================
echo 下一步操作建议
echo ========================================
echo.
echo 1. 查看生成的文档: http://localhost:8080
echo 2. 审查模型血缘关系和依赖图
echo 3. 测试自定义宏和物料化策略
echo 4. 验证钩子函数的执行效果
echo 5. 优化包依赖配置
echo 6. 实施性能监控和调优
echo 7. 集成到CI/CD流水线
echo 8. 扩展自定义功能和插件
echo.

echo 运行完成时间: %date% %time%
echo ========================================

REM 等待用户输入后退出
pause