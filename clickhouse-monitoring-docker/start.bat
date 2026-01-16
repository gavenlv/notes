@echo off
chcp 65001 >nul

echo ==========================================
echo ClickHouse + Prometheus + Grafana 监控系统
echo ==========================================

REM 检查Docker是否安装
docker version >nul 2>&1
if errorlevel 1 (
    echo 错误: Docker未安装，请先安装Docker
    pause
    exit /b 1
)

REM 检查Docker Compose是否安装
docker-compose version >nul 2>&1
if errorlevel 1 (
    echo 错误: Docker Compose未安装，请先安装Docker Compose
    pause
    exit /b 1
)

REM 创建必要的目录
echo 创建必要的目录...
if not exist ".\clickhouse" mkdir ".\clickhouse"
if not exist ".\prometheus" mkdir ".\prometheus"
if not exist ".\grafana\provisioning\datasources" mkdir ".\grafana\provisioning\datasources"
if not exist ".\grafana\provisioning\dashboards" mkdir ".\grafana\provisioning\dashboards"
if not exist ".\grafana\dashboards" mkdir ".\grafana\dashboards"

REM 启动服务
echo 启动监控服务...
docker-compose up -d

REM 等待服务启动
echo 等待服务启动...
timeout /t 30 /nobreak >nul

REM 检查服务状态
echo 检查服务状态...
set services=clickhouse prometheus grafana clickhouse-exporter node-exporter

for %%s in (%services%) do (
    docker ps | findstr "%%s" >nul
    if errorlevel 1 (
        echo ✗ %%s 启动失败
    ) else (
        echo ✓ %%s 运行正常
    )
)

echo.
echo ==========================================
echo 服务访问地址:
echo ==========================================
echo ClickHouse HTTP接口: http://localhost:8123
echo ClickHouse TCP接口: localhost:9000
echo Prometheus: http://localhost:9090
echo Grafana: http://localhost:3000
echo Node Exporter: http://localhost:9100
echo ClickHouse Exporter: http://localhost:9333
echo.
echo Grafana登录信息:
echo 用户名: admin
echo 密码: admin123
echo.
echo ClickHouse连接信息:
echo 用户名: admin
echo 密码: admin123
echo 数据库: monitoring
echo.
echo ==========================================
echo 常用命令:
echo ==========================================
echo 查看服务状态: docker-compose ps
echo 查看日志: docker-compose logs [服务名]
echo 停止服务: docker-compose down
echo 重启服务: docker-compose restart
echo ==========================================

pause