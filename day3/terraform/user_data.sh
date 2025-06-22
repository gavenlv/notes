#!/bin/bash
# ClickHouse节点安装和配置脚本
# 模板变量: node_id, cluster_name, shard_num, replica_num

set -e

# 变量定义
NODE_ID="${node_id}"
CLUSTER_NAME="${cluster_name}"
SHARD_NUM="${shard_num}"
REPLICA_NUM="${replica_num}"
CLICKHOUSE_USER="clickhouse"
CLICKHOUSE_PASSWORD="clickhouse123"

# 日志文件
LOG_FILE="/var/log/clickhouse-setup.log"

# 记录日志函数
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

log "开始安装ClickHouse节点 $NODE_ID"

# 更新系统
log "更新系统包..."
apt-get update
apt-get upgrade -y

# 安装必要的包
log "安装必要软件包..."
apt-get install -y \
    curl \
    wget \
    gnupg2 \
    lsb-release \
    apt-transport-https \
    ca-certificates \
    dirmngr \
    htop \
    iotop \
    net-tools

# 添加ClickHouse仓库
log "添加ClickHouse仓库..."
curl -fsSL 'https://packages.clickhouse.com/rpm/lts/repodata/repomd.xml.key' | gpg --dearmor -o /usr/share/keyrings/clickhouse-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/clickhouse-keyring.gpg] https://packages.clickhouse.com/deb stable main" | tee /etc/apt/sources.list.d/clickhouse.list
apt-get update

# 安装ClickHouse
log "安装ClickHouse..."
DEBIAN_FRONTEND=noninteractive apt-get install -y clickhouse-server clickhouse-client

# 配置数据目录
log "配置数据目录..."
mkdir -p /var/lib/clickhouse
mkdir -p /var/log/clickhouse-server
chown clickhouse:clickhouse /var/lib/clickhouse
chown clickhouse:clickhouse /var/log/clickhouse-server

# 挂载数据盘
log "配置数据盘..."
if [ -b /dev/vdb ]; then
    # 格式化数据盘
    mkfs.ext4 /dev/vdb
    
    # 创建挂载点
    mkdir -p /data/clickhouse
    
    # 挂载数据盘
    mount /dev/vdb /data/clickhouse
    
    # 添加到fstab
    echo "/dev/vdb /data/clickhouse ext4 defaults 0 2" >> /etc/fstab
    
    # 设置权限
    chown -R clickhouse:clickhouse /data/clickhouse
    
    # 创建数据目录
    mkdir -p /data/clickhouse/data
    mkdir -p /data/clickhouse/logs
    mkdir -p /data/clickhouse/tmp
    
    chown -R clickhouse:clickhouse /data/clickhouse
fi

# 获取内网IP地址
PRIVATE_IP=$(curl -s http://100.100.100.200/latest/meta-data/private-ipv4)
log "节点私网IP: $PRIVATE_IP"

# 等待ZooKeeper启动
log "等待ZooKeeper服务启动..."
for i in {1..30}; do
    if nc -z 10.0.1.10 2181; then
        log "ZooKeeper连接成功"
        break
    fi
    sleep 10
done

# 配置ClickHouse
log "配置ClickHouse..."
cat > /etc/clickhouse-server/config.xml << 'EOF'
<?xml version="1.0"?>
<yandex>
    <!-- 基础配置 -->
    <logger>
        <level>information</level>
        <log>/var/log/clickhouse-server/clickhouse-server.log</log>
        <errorlog>/var/log/clickhouse-server/clickhouse-server.err.log</errorlog>
        <size>1000M</size>
        <count>10</count>
    </logger>

    <http_port>8123</http_port>
    <tcp_port>9000</tcp_port>
    <mysql_port>9004</mysql_port>
    <postgresql_port>9005</postgresql_port>
    <interserver_http_port>9009</interserver_http_port>

    <!-- 监听所有网络接口 -->
    <listen_host>::</listen_host>
    <listen_host>0.0.0.0</listen_host>

    <!-- 数据路径配置 -->
    <path>/data/clickhouse/data/</path>
    <tmp_path>/data/clickhouse/tmp/</tmp_path>
    <user_files_path>/data/clickhouse/user_files/</user_files_path>
    <format_schema_path>/data/clickhouse/format_schemas/</format_schema_path>

    <!-- 用户目录 -->
    <users_config>users.xml</users_config>

    <!-- 默认配置文件 -->
    <default_profile>default</default_profile>
    <default_database>default</default_database>

    <!-- ZooKeeper配置 -->
    <zookeeper>
        <node index="1">
            <host>10.0.1.10</host>
            <port>2181</port>
        </node>
    </zookeeper>

    <!-- 宏定义 -->
    <macros>
        <cluster>${cluster_name}</cluster>
        <shard>${shard_num}</shard>
        <replica>${replica_num}</replica>
    </macros>

    <!-- 集群配置 -->
    <remote_servers>
        <${cluster_name}>
            <shard>
                <replica>
                    <host>REPLACE_NODE1_IP</host>
                    <port>9000</port>
                </replica>
                <replica>
                    <host>REPLACE_NODE3_IP</host>
                    <port>9000</port>
                </replica>
            </shard>
            <shard>
                <replica>
                    <host>REPLACE_NODE2_IP</host>
                    <port>9000</port>
                </replica>
            </shard>
        </${cluster_name}>
    </remote_servers>

    <!-- 性能优化配置 -->
    <max_connections>4096</max_connections>
    <keep_alive_timeout>3</keep_alive_timeout>
    <max_concurrent_queries>100</max_concurrent_queries>
    <uncompressed_cache_size>8589934592</uncompressed_cache_size>
    <mark_cache_size>5368709120</mark_cache_size>

    <!-- 压缩配置 -->
    <compression>
        <case>
            <min_part_size>10000000000</min_part_size>
            <min_part_size_ratio>0.01</min_part_size_ratio>
            <method>lz4</method>
        </case>
    </compression>

    <!-- 分布式DDL -->
    <distributed_ddl>
        <path>/clickhouse/task_queue/ddl</path>
    </distributed_ddl>

    <!-- 系统配置 -->
    <builtin_dictionaries_reload_interval>3600</builtin_dictionaries_reload_interval>
    <max_session_timeout>3600</max_session_timeout>
    <default_session_timeout>60</default_session_timeout>
</yandex>
EOF

# 配置用户
log "配置ClickHouse用户..."
cat > /etc/clickhouse-server/users.xml << 'EOF'
<?xml version="1.0"?>
<yandex>
    <profiles>
        <default>
            <max_memory_usage>10000000000</max_memory_usage>
            <use_uncompressed_cache>0</use_uncompressed_cache>
            <load_balancing>random</load_balancing>
        </default>
        <readonly>
            <readonly>1</readonly>
        </readonly>
    </profiles>

    <users>
        <default>
            <password></password>
            <networks incl="networks" replace="replace">
                <ip>::/0</ip>
            </networks>
            <profile>default</profile>
            <quota>default</quota>
        </default>
        
        <clickhouse>
            <password_sha256_hex>8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92</password_sha256_hex>
            <networks incl="networks" replace="replace">
                <ip>::/0</ip>
            </networks>
            <profile>default</profile>
            <quota>default</quota>
        </clickhouse>
    </users>

    <quotas>
        <default>
            <interval>
                <duration>3600</duration>
                <queries>0</queries>
                <errors>0</errors>
                <result_rows>0</result_rows>
                <read_rows>0</read_rows>
                <execution_time>0</execution_time>
            </interval>
        </default>
    </quotas>
</yandex>
EOF

# 等待其他节点启动并获取IP
log "等待其他节点启动..."
sleep 60

# 获取所有节点的IP地址（这里需要通过元数据服务或其他方式获取）
# 临时使用固定IP，实际部署时会被Terraform替换
NODE1_IP="10.0.1.20"
NODE2_IP="10.0.1.21"
NODE3_IP="10.0.1.22"

# 替换配置文件中的IP地址
sed -i "s/REPLACE_NODE1_IP/$NODE1_IP/g" /etc/clickhouse-server/config.xml
sed -i "s/REPLACE_NODE2_IP/$NODE2_IP/g" /etc/clickhouse-server/config.xml
sed -i "s/REPLACE_NODE3_IP/$NODE3_IP/g" /etc/clickhouse-server/config.xml

# 创建必要的目录
mkdir -p /data/clickhouse/data
mkdir -p /data/clickhouse/tmp
mkdir -p /data/clickhouse/user_files
mkdir -p /data/clickhouse/format_schemas
chown -R clickhouse:clickhouse /data/clickhouse

# 启动ClickHouse服务
log "启动ClickHouse服务..."
systemctl enable clickhouse-server
systemctl start clickhouse-server

# 等待服务启动
sleep 30

# 检查服务状态
log "检查ClickHouse服务状态..."
systemctl status clickhouse-server

# 测试连接
log "测试ClickHouse连接..."
for i in {1..10}; do
    if clickhouse-client --query "SELECT version()"; then
        log "ClickHouse连接测试成功"
        break
    else
        log "等待ClickHouse启动... (尝试 $i/10)"
        sleep 10
    fi
done

# 创建测试数据库和表
log "创建测试数据库..."
clickhouse-client --query "CREATE DATABASE IF NOT EXISTS test_db" || true

# 创建集群表
log "创建集群测试表..."
clickhouse-client --query "
CREATE TABLE IF NOT EXISTS test_db.test_table ON CLUSTER $CLUSTER_NAME (
    id UInt64,
    name String,
    timestamp DateTime
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/test_table', '{replica}')
ORDER BY id
" || true

# 记录完成
log "ClickHouse节点 $NODE_ID 安装配置完成"
log "节点IP: $PRIVATE_IP"
log "Shard: $SHARD_NUM, Replica: $REPLICA_NUM"

# 输出配置信息
log "配置信息:"
log "- HTTP端口: 8123"
log "- TCP端口: 9000"
log "- 集群名称: $CLUSTER_NAME"
log "- 数据目录: /data/clickhouse/data"
log "- 日志目录: /var/log/clickhouse-server"

# 创建健康检查脚本
cat > /usr/local/bin/clickhouse-health-check.sh << 'EOF'
#!/bin/bash
# ClickHouse健康检查脚本

# 检查服务状态
if ! systemctl is-active --quiet clickhouse-server; then
    echo "ERROR: ClickHouse service is not running"
    exit 1
fi

# 检查端口
if ! nc -z localhost 8123; then
    echo "ERROR: ClickHouse HTTP port 8123 is not accessible"
    exit 1
fi

if ! nc -z localhost 9000; then
    echo "ERROR: ClickHouse TCP port 9000 is not accessible"
    exit 1
fi

# 检查查询
if ! clickhouse-client --query "SELECT 1" > /dev/null 2>&1; then
    echo "ERROR: ClickHouse query test failed"
    exit 1
fi

echo "OK: ClickHouse is healthy"
EOF

chmod +x /usr/local/bin/clickhouse-health-check.sh

log "健康检查脚本已创建: /usr/local/bin/clickhouse-health-check.sh"
log "ClickHouse节点 $NODE_ID 安装完成!" 