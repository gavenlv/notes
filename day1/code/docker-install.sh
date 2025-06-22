#!/bin/bash

# ClickHouse Docker安装脚本
# 作者: ClickHouse学习教程
# 版本: 1.0

set -e

echo "🚀 开始安装ClickHouse (Docker方式)"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Docker是否已安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker未安装，请先安装Docker${NC}"
        echo "安装命令: curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh"
        exit 1
    fi
    echo -e "${GREEN}✅ Docker已安装${NC}"
}

# 创建必要的目录
create_directories() {
    echo "📁 创建ClickHouse目录..."
    
    CLICKHOUSE_HOME="${HOME}/clickhouse"
    mkdir -p "${CLICKHOUSE_HOME}"/{data,logs,config}
    
    echo -e "${GREEN}✅ 目录创建完成${NC}"
    echo "   数据目录: ${CLICKHOUSE_HOME}/data"
    echo "   日志目录: ${CLICKHOUSE_HOME}/logs"
    echo "   配置目录: ${CLICKHOUSE_HOME}/config"
}

# 停止并删除已存在的容器
cleanup_existing() {
    if docker ps -a | grep -q clickhouse-server; then
        echo -e "${YELLOW}⚠️  发现已存在的ClickHouse容器，正在清理...${NC}"
        docker stop clickhouse-server 2>/dev/null || true
        docker rm clickhouse-server 2>/dev/null || true
        echo -e "${GREEN}✅ 清理完成${NC}"
    fi
}

# 启动ClickHouse容器
start_clickhouse() {
    echo "🐳 启动ClickHouse容器..."
    
    CLICKHOUSE_HOME="${HOME}/clickhouse"
    
    docker run -d \
        --name clickhouse-server \
        --publish 8123:8123 \
        --publish 9000:9000 \
        --volume "${CLICKHOUSE_HOME}/data":/var/lib/clickhouse \
        --volume "${CLICKHOUSE_HOME}/logs":/var/log/clickhouse-server \
        --restart unless-stopped \
        clickhouse/clickhouse-server:latest
    
    echo -e "${GREEN}✅ ClickHouse容器启动成功${NC}"
}

# 等待服务启动
wait_for_service() {
    echo "⏳ 等待ClickHouse服务启动..."
    
    for i in {1..30}; do
        if curl -s http://localhost:8123/ >/dev/null 2>&1; then
            echo -e "${GREEN}✅ ClickHouse服务已就绪${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
    done
    
    echo -e "${RED}❌ ClickHouse服务启动超时${NC}"
    exit 1
}

# 测试连接
test_connection() {
    echo "🔍 测试ClickHouse连接..."
    
    # 测试HTTP接口
    echo "测试HTTP接口..."
    VERSION=$(curl -s 'http://localhost:8123/' --data-urlencode 'query=SELECT version()')
    echo -e "${GREEN}✅ HTTP接口正常，版本: ${VERSION}${NC}"
    
    # 测试TCP接口
    echo "测试TCP接口..."
    docker run --rm --link clickhouse-server:clickhouse-server \
        clickhouse/clickhouse-client:latest \
        --host clickhouse-server \
        --query "SELECT 'TCP连接正常' as status"
    
    echo -e "${GREEN}✅ TCP接口正常${NC}"
}

# 创建测试数据
create_test_data() {
    echo "📊 创建测试数据..."
    
    # 创建测试数据库
    curl -s 'http://localhost:8123/' --data-urlencode 'query=CREATE DATABASE IF NOT EXISTS tutorial'
    
    # 创建测试表
    curl -s 'http://localhost:8123/' --data-urlencode 'query=
    CREATE TABLE tutorial.hits (
        WatchID UInt64,
        JavaEnable UInt8,
        Title String,
        GoodEvent Int16,
        EventTime DateTime,
        EventDate Date,
        CounterID UInt32,
        ClientIP UInt32,
        RegionID UInt32,
        UserID UInt64,
        CounterClass Int8,
        OS UInt8,
        UserAgent UInt8,
        URL String,
        Referer String,
        IsRefresh UInt8,
        RefererCategoryID UInt16,
        RefererRegionID UInt32,
        URLCategoryID UInt16,
        URLRegionID UInt32,
        ResolutionWidth UInt16,
        ResolutionHeight UInt16,
        ResolutionDepth UInt8,
        FlashMajor UInt8,
        FlashMinor UInt8,
        FlashMinor2 String,
        NetMajor UInt8,
        NetMinor UInt8,
        UserAgentMajor UInt16,
        UserAgentMinor FixedString(2),
        CookieEnable UInt8,
        JavascriptEnable UInt8,
        IsMobile UInt8,
        MobilePhone UInt8,
        MobilePhoneModel String,
        Params String,
        IPNetworkID UInt32,
        TraficSourceID Int8,
        SearchEngineID UInt16,
        SearchPhrase String,
        AdvEngineID UInt8,
        IsArtifical UInt8,
        WindowClientWidth UInt16,
        WindowClientHeight UInt16,
        ClientTimeZone Int16,
        ClientEventTime DateTime,
        SilverlightVersion1 UInt8,
        SilverlightVersion2 UInt8,
        SilverlightVersion3 UInt32,
        SilverlightVersion4 UInt16,
        PageCharset String,
        CodeVersion UInt32,
        IsLink UInt8,
        IsDownload UInt8,
        IsNotBounce UInt8,
        FUniqID UInt64,
        OriginalURL String,
        HID UInt32,
        IsOldCounter UInt8,
        IsEvent UInt8,
        IsParameter UInt8,
        DontCountHits UInt8,
        WithHash UInt8,
        HitColor FixedString(1),
        LocalEventTime DateTime,
        Age UInt8,
        Sex UInt8,
        Income UInt8,
        Interests UInt16,
        Robotness UInt8,
        RemoteIP UInt32,
        WindowName Int32,
        OpenerName Int32,
        HistoryLength Int16,
        BrowserLanguage FixedString(2),
        BrowserCountry FixedString(2),
        SocialNetwork String,
        SocialAction String,
        HTTPError UInt16,
        SendTiming Int32,
        DNSTiming Int32,
        ConnectTiming Int32,
        ResponseStartTiming Int32,
        ResponseEndTiming Int32,
        FetchTiming Int32,
        SocialSourceNetworkID UInt8,
        SocialSourcePage String,
        ParamPrice Int64,
        ParamOrderID String,
        ParamCurrency FixedString(3),
        ParamCurrencyID UInt16,
        OpenstatServiceName String,
        OpenstatCampaignID String,
        OpenstatAdID String,
        OpenstatSourceID String,
        UTMSource String,
        UTMMedium String,
        UTMCampaign String,
        UTMContent String,
        UTMTerm String,
        FromTag String,
        HasGCLID UInt8,
        RefererHash UInt64,
        URLHash UInt64,
        CLID UInt32
    )
    ENGINE = MergeTree()
    ORDER BY (CounterID, EventDate, intHash32(UserID))
    SAMPLE BY intHash32(UserID)
    '
    
    echo -e "${GREEN}✅ 测试数据创建完成${NC}"
}

# 显示使用信息
show_usage_info() {
    echo ""
    echo "🎉 ClickHouse安装完成！"
    echo ""
    echo "📋 连接信息:"
    echo "   HTTP端口: 8123"
    echo "   TCP端口:  9000"
    echo "   默认用户: default (无密码)"
    echo ""
    echo "🔧 常用命令:"
    echo "   # 使用命令行客户端连接"
    echo "   docker exec -it clickhouse-server clickhouse-client"
    echo ""
    echo "   # 使用HTTP接口查询"
    echo "   curl 'http://localhost:8123/' --data-urlencode 'query=SELECT version()'"
    echo ""
    echo "   # 查看容器状态"
    echo "   docker ps | grep clickhouse"
    echo ""
    echo "   # 查看日志"
    echo "   docker logs clickhouse-server"
    echo ""
    echo "   # 停止服务"
    echo "   docker stop clickhouse-server"
    echo ""
    echo "   # 启动服务"
    echo "   docker start clickhouse-server"
    echo ""
    echo "📁 数据目录: ${HOME}/clickhouse"
    echo ""
    echo "📚 下一步: 阅读 notes/week1/day2-installation.md 学习更多配置选项"
}

# 主函数
main() {
    echo "============================================"
    echo "      ClickHouse Docker 安装脚本"
    echo "============================================"
    
    check_docker
    create_directories
    cleanup_existing
    start_clickhouse
    wait_for_service
    test_connection
    create_test_data
    show_usage_info
    
    echo ""
    echo -e "${GREEN}🎊 安装完成！祝学习愉快！${NC}"
}

# 执行主函数
main "$@" 