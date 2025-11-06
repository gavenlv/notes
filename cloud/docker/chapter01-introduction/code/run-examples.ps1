# Windows PowerShell脚本 - 运行第1章所有示例
# 用法: .\run-examples.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Docker第1章 - 验证和实践示例" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Docker是否安装
Write-Host "1. 检查Docker安装..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker已安装: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker未安装或未启动，请先安装Docker Desktop" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 检查Docker是否运行
Write-Host "2. 检查Docker服务状态..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "✅ Docker服务正在运行" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker服务未运行，请启动Docker Desktop" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 显示Docker详细信息
Write-Host "3. Docker详细信息:" -ForegroundColor Yellow
docker version
Write-Host ""

# 示例1: 运行hello-world
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "示例1: 运行hello-world容器" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "这是最简单的Docker容器，用于验证安装" -ForegroundColor Gray
Write-Host ""
docker run hello-world
Write-Host ""
Read-Host "按Enter继续..."

# 示例2: 运行Nginx Web服务器
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "示例2: 运行Nginx Web服务器" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "启动一个Nginx容器，映射到8080端口" -ForegroundColor Gray
Write-Host ""

# 清理之前的容器
docker rm -f demo-nginx 2>$null

Write-Host "启动Nginx容器..." -ForegroundColor Yellow
docker run -d -p 8080:80 --name demo-nginx nginx

Write-Host ""
Write-Host "✅ Nginx容器已启动！" -ForegroundColor Green
Write-Host "   访问地址: http://localhost:8080" -ForegroundColor Green
Write-Host ""

# 显示容器信息
Write-Host "容器信息:" -ForegroundColor Yellow
docker ps --filter "name=demo-nginx" --format "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
Write-Host ""

Write-Host "请在浏览器中访问 http://localhost:8080 查看Nginx欢迎页面" -ForegroundColor Cyan
Read-Host "按Enter继续..."

# 查看容器日志
Write-Host ""
Write-Host "查看Nginx容器日志:" -ForegroundColor Yellow
docker logs demo-nginx
Write-Host ""
Read-Host "按Enter继续..."

# 示例3: 交互式运行Ubuntu
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "示例3: 交互式Ubuntu容器" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "启动一个Ubuntu容器并执行命令" -ForegroundColor Gray
Write-Host ""

Write-Host "在Ubuntu容器中执行命令..." -ForegroundColor Yellow
docker run --rm ubuntu bash -c "cat /etc/os-release && echo '' && echo '✅ Ubuntu容器运行成功！'"
Write-Host ""
Read-Host "按Enter继续..."

# 示例4: 查看镜像列表
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "示例4: 查看本地镜像" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
docker images
Write-Host ""
Read-Host "按Enter继续..."

# 示例5: 查看所有容器
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "示例5: 查看所有容器" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "运行中的容器:" -ForegroundColor Yellow
docker ps
Write-Host ""
Write-Host "所有容器（包括停止的）:" -ForegroundColor Yellow
docker ps -a
Write-Host ""
Read-Host "按Enter继续..."

# 清理演示资源
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "清理演示资源" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
$cleanup = Read-Host "是否清理本次演示创建的容器？(y/n)"

if ($cleanup -eq 'y') {
    Write-Host ""
    Write-Host "停止并删除Nginx容器..." -ForegroundColor Yellow
    docker stop demo-nginx
    docker rm demo-nginx
    Write-Host "✅ 清理完成" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "保留容器，稍后可以手动清理：" -ForegroundColor Yellow
    Write-Host "  docker stop demo-nginx" -ForegroundColor Gray
    Write-Host "  docker rm demo-nginx" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "所有示例运行完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "学习要点总结：" -ForegroundColor Yellow
Write-Host "1. ✅ 验证了Docker安装" -ForegroundColor White
Write-Host "2. ✅ 运行了第一个容器(hello-world)" -ForegroundColor White
Write-Host "3. ✅ 启动了Web服务器(Nginx)" -ForegroundColor White
Write-Host "4. ✅ 学习了容器的基本操作" -ForegroundColor White
Write-Host "5. ✅ 查看了镜像和容器列表" -ForegroundColor White
Write-Host ""
Write-Host "下一步：学习第2章 - Docker基础概念" -ForegroundColor Cyan
Write-Host ""
