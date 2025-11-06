#!/bin/bash
# Linux/Mac Shell脚本 - 运行第1章所有示例
# 用法: chmod +x run-examples.sh && ./run-examples.sh

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}Docker第1章 - 验证和实践示例${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# 检查Docker是否安装
echo -e "${YELLOW}1. 检查Docker安装...${NC}"
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo -e "${GREEN}✅ Docker已安装: $DOCKER_VERSION${NC}"
else
    echo -e "${RED}❌ Docker未安装，请先安装Docker${NC}"
    exit 1
fi

echo ""

# 检查Docker是否运行
echo -e "${YELLOW}2. 检查Docker服务状态...${NC}"
if docker info &> /dev/null; then
    echo -e "${GREEN}✅ Docker服务正在运行${NC}"
else
    echo -e "${RED}❌ Docker服务未运行，请启动Docker服务${NC}"
    exit 1
fi

echo ""

# 显示Docker详细信息
echo -e "${YELLOW}3. Docker详细信息:${NC}"
docker version
echo ""

# 示例1: 运行hello-world
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}示例1: 运行hello-world容器${NC}"
echo -e "${CYAN}========================================${NC}"
echo "这是最简单的Docker容器，用于验证安装"
echo ""
docker run hello-world
echo ""
read -p "按Enter继续..."

# 示例2: 运行Nginx Web服务器
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}示例2: 运行Nginx Web服务器${NC}"
echo -e "${CYAN}========================================${NC}"
echo "启动一个Nginx容器，映射到8080端口"
echo ""

# 清理之前的容器
docker rm -f demo-nginx 2>/dev/null

echo -e "${YELLOW}启动Nginx容器...${NC}"
docker run -d -p 8080:80 --name demo-nginx nginx

echo ""
echo -e "${GREEN}✅ Nginx容器已启动！${NC}"
echo -e "${GREEN}   访问地址: http://localhost:8080${NC}"
echo ""

# 显示容器信息
echo -e "${YELLOW}容器信息:${NC}"
docker ps --filter "name=demo-nginx" --format "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo -e "${CYAN}请在浏览器中访问 http://localhost:8080 查看Nginx欢迎页面${NC}"
read -p "按Enter继续..."

# 查看容器日志
echo ""
echo -e "${YELLOW}查看Nginx容器日志:${NC}"
docker logs demo-nginx
echo ""
read -p "按Enter继续..."

# 示例3: 交互式运行Ubuntu
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}示例3: 交互式Ubuntu容器${NC}"
echo -e "${CYAN}========================================${NC}"
echo "启动一个Ubuntu容器并执行命令"
echo ""

echo -e "${YELLOW}在Ubuntu容器中执行命令...${NC}"
docker run --rm ubuntu bash -c "cat /etc/os-release && echo '' && echo '✅ Ubuntu容器运行成功！'"
echo ""
read -p "按Enter继续..."

# 示例4: 查看镜像列表
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}示例4: 查看本地镜像${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
docker images
echo ""
read -p "按Enter继续..."

# 示例5: 查看所有容器
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}示例5: 查看所有容器${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "${YELLOW}运行中的容器:${NC}"
docker ps
echo ""
echo -e "${YELLOW}所有容器（包括停止的）:${NC}"
docker ps -a
echo ""
read -p "按Enter继续..."

# 清理演示资源
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}清理演示资源${NC}"
echo -e "${CYAN}========================================${NC}"
read -p "是否清理本次演示创建的容器？(y/n) " cleanup

if [ "$cleanup" = "y" ]; then
    echo ""
    echo -e "${YELLOW}停止并删除Nginx容器...${NC}"
    docker stop demo-nginx
    docker rm demo-nginx
    echo -e "${GREEN}✅ 清理完成${NC}"
else
    echo ""
    echo -e "${YELLOW}保留容器，稍后可以手动清理：${NC}"
    echo "  docker stop demo-nginx"
    echo "  docker rm demo-nginx"
fi

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${GREEN}所有示例运行完成！${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "${YELLOW}学习要点总结：${NC}"
echo "1. ✅ 验证了Docker安装"
echo "2. ✅ 运行了第一个容器(hello-world)"
echo "3. ✅ 启动了Web服务器(Nginx)"
echo "4. ✅ 学习了容器的基本操作"
echo "5. ✅ 查看了镜像和容器列表"
echo ""
echo -e "${CYAN}下一步：学习第2章 - Docker基础概念${NC}"
echo ""
