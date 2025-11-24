#!/bin/bash
# ZooKeeper安装和配置脚本
# 用于ClickHouse集群协调

set -e

# 日志文件
LOG_FILE="/var/log/zookeeper-setup.log"

# 记录日志函数
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

log "开始安装ZooKeeper..."

# 更新系统
log "更新系统包..."
apt-get update
apt-get upgrade -y

# 安装Java和必要软件
log "安装Java和必要软件..."
apt-get install -y \
    openjdk-11-jdk \
    curl \
    wget \
    net-tools \
    htop \
    netcat-openbsd

# 设置Java环境变量
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
echo "export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64" >> /etc/environment

# 创建ZooKeeper用户
log "创建ZooKeeper用户..."
useradd -m -s /bin/bash zookeeper

# 下载ZooKeeper
log "下载ZooKeeper..."
ZK_VERSION="3.8.0"
cd /opt
wget https://archive.apache.org/dist/zookeeper/zookeeper-${ZK_VERSION}/apache-zookeeper-${ZK_VERSION}-bin.tar.gz
tar -xzf apache-zookeeper-${ZK_VERSION}-bin.tar.gz
mv apache-zookeeper-${ZK_VERSION}-bin zookeeper
chown -R zookeeper:zookeeper /opt/zookeeper

# 创建ZooKeeper配置目录
log "创建ZooKeeper配置..."
mkdir -p /opt/zookeeper/data
mkdir -p /opt/zookeeper/logs
chown -R zookeeper:zookeeper /opt/zookeeper/data
chown -R zookeeper:zookeeper /opt/zookeeper/logs

# 创建myid文件
echo "1" > /opt/zookeeper/data/myid
chown zookeeper:zookeeper /opt/zookeeper/data/myid

# 创建ZooKeeper配置文件
log "配置ZooKeeper..."
cat > /opt/zookeeper/conf/zoo.cfg << 'EOF'
# ZooKeeper配置文件
tickTime=2000
initLimit=10
syncLimit=5
dataDir=/opt/zookeeper/data
dataLogDir=/opt/zookeeper/logs
clientPort=2181
maxClientCnxns=60

# 集群配置（单节点模式）
server.1=0.0.0.0:2888:3888

# 性能优化
autopurge.snapRetainCount=3
autopurge.purgeInterval=24

# 日志配置
preAllocSize=65536
snapCount=100000

# 4字命令白名单
4lw.commands.whitelist=*
EOF

# 配置ZooKeeper日志
cat > /opt/zookeeper/conf/log4j.properties << 'EOF'
# ZooKeeper日志配置
zookeeper.root.logger=INFO, CONSOLE, ROLLINGFILE
zookeeper.console.threshold=INFO
zookeeper.log.dir=/opt/zookeeper/logs
zookeeper.log.file=zookeeper.log
zookeeper.log.threshold=INFO
zookeeper.log.maxfilesize=256MB
zookeeper.log.maxbackupindex=10

# 控制台输出
log4j.appender.CONSOLE=org.apache.log4j.ConsoleAppender
log4j.appender.CONSOLE.Threshold=${zookeeper.console.threshold}
log4j.appender.CONSOLE.layout=org.apache.log4j.PatternLayout
log4j.appender.CONSOLE.layout.ConversionPattern=%d{ISO8601} [myid:%X{myid}] - %-5p [%t:%C{1}@%L] - %m%n

# 滚动文件输出
log4j.appender.ROLLINGFILE=org.apache.log4j.RollingFileAppender
log4j.appender.ROLLINGFILE.Threshold=${zookeeper.log.threshold}
log4j.appender.ROLLINGFILE.File=${zookeeper.log.dir}/${zookeeper.log.file}
log4j.appender.ROLLINGFILE.MaxFileSize=${zookeeper.log.maxfilesize}
log4j.appender.ROLLINGFILE.MaxBackupIndex=${zookeeper.log.maxbackupindex}
log4j.appender.ROLLINGFILE.layout=org.apache.log4j.PatternLayout
log4j.appender.ROLLINGFILE.layout.ConversionPattern=%d{ISO8601} [myid:%X{myid}] - %-5p [%t:%C{1}@%L] - %m%n

# 根日志器
log4j.rootLogger=${zookeeper.root.logger}
EOF

# 设置环境变量
cat > /opt/zookeeper/conf/zookeeper-env.sh << 'EOF'
#!/bin/bash
# ZooKeeper环境变量配置

export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export ZOO_LOG_DIR=/opt/zookeeper/logs
export ZOO_LOG4J_PROP="INFO,ROLLINGFILE"
export JVMFLAGS="-Xmx1024m -Xms512m"
EOF

chmod +x /opt/zookeeper/conf/zookeeper-env.sh
chown zookeeper:zookeeper /opt/zookeeper/conf/zookeeper-env.sh

# 创建systemd服务文件
log "创建systemd服务..."
cat > /etc/systemd/system/zookeeper.service << 'EOF'
[Unit]
Description=Apache ZooKeeper
Documentation=http://zookeeper.apache.org/doc/current/
Requires=network.target
After=network.target

[Service]
Type=forking
User=zookeeper
Group=zookeeper
WorkingDirectory=/opt/zookeeper
Environment=JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
Environment=ZOO_LOG_DIR=/opt/zookeeper/logs
ExecStart=/opt/zookeeper/bin/zkServer.sh start
ExecStop=/opt/zookeeper/bin/zkServer.sh stop
ExecReload=/opt/zookeeper/bin/zkServer.sh restart
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=zookeeper

[Install]
WantedBy=multi-user.target
EOF

# 设置权限
chown -R zookeeper:zookeeper /opt/zookeeper

# 启动ZooKeeper服务
log "启动ZooKeeper服务..."
systemctl daemon-reload
systemctl enable zookeeper
systemctl start zookeeper

# 等待服务启动
sleep 15

# 检查服务状态
log "检查ZooKeeper服务状态..."
systemctl status zookeeper

# 测试ZooKeeper连接
log "测试ZooKeeper连接..."
for i in {1..10}; do
    if echo "ruok" | nc localhost 2181; then
        log "ZooKeeper连接测试成功"
        break
    else
        log "等待ZooKeeper启动... (尝试 $i/10)"
        sleep 10
    fi
done

# 显示ZooKeeper状态
echo "stat" | nc localhost 2181

# 创建健康检查脚本
log "创建健康检查脚本..."
cat > /usr/local/bin/zookeeper-health-check.sh << 'EOF'
#!/bin/bash
# ZooKeeper健康检查脚本

# 检查服务状态
if ! systemctl is-active --quiet zookeeper; then
    echo "ERROR: ZooKeeper service is not running"
    exit 1
fi

# 检查端口
if ! nc -z localhost 2181; then
    echo "ERROR: ZooKeeper port 2181 is not accessible"
    exit 1
fi

# 检查四字命令
RESPONSE=$(echo "ruok" | nc localhost 2181 2>/dev/null)
if [ "$RESPONSE" != "imok" ]; then
    echo "ERROR: ZooKeeper health check failed"
    exit 1
fi

echo "OK: ZooKeeper is healthy"
EOF

chmod +x /usr/local/bin/zookeeper-health-check.sh

# 创建基础数据结构
log "创建ClickHouse所需的ZooKeeper数据结构..."
sleep 5

# 使用ZooKeeper客户端创建目录结构
/opt/zookeeper/bin/zkCli.sh -server localhost:2181 << 'EOF'
create /clickhouse
create /clickhouse/tables
create /clickhouse/task_queue
create /clickhouse/task_queue/ddl
quit
EOF

log "ZooKeeper安装配置完成!"
log "ZooKeeper状态信息:"
log "- 端口: 2181"
log "- 数据目录: /opt/zookeeper/data"
log "- 日志目录: /opt/zookeeper/logs"
log "- 配置文件: /opt/zookeeper/conf/zoo.cfg"

# 显示最终状态
echo "conf" | nc localhost 2181 