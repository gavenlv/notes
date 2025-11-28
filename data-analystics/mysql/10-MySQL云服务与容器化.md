# 10-MySQL云服务与容器化

## 1. 云数据库服务概述

### 1.1 云数据库服务优势

随着云计算技术的发展，云数据库服务已经成为现代应用系统的主流选择。与传统自建数据库相比，云数据库服务具有以下显著优势：

1. **降低运维负担**：无需关注硬件采购、安装、配置、备份、升级等运维工作
2. **高可用性**：通常提供多副本、自动故障转移等高可用特性
3. **弹性扩展**：可根据业务需求动态调整计算和存储资源
4. **数据安全**：提供多层次的安全防护和合规认证
5. **成本效益**：按需付费，无需前期大量硬件投入
6. **全球部署**：可在多个区域部署，实现就近访问
7. **备份与恢复**：提供自动备份和快速恢复功能

### 1.2 云数据库服务类型

根据提供的管理程度，云数据库服务可以分为以下几类：

#### 1.2.1 基础设施即服务 (IaaS)
- **特点**：提供基础虚拟机资源，用户自行安装和管理数据库
- **优势**：完全控制权，灵活配置
- **劣势**：需要专业DBA团队管理
- **代表产品**：AWS EC2、阿里云ECS、腾讯云CVM

#### 1.2.2 平台即服务 (PaaS)
- **特点**：提供预配置的数据库环境，用户只需关注数据和应用
- **优势**：简化管理，自动扩展，高可用
- **劣势**：控制权受限，定制性较差
- **代表产品**：AWS RDS、阿里云RDS、腾讯云MySQL

#### 1.2.3 数据库即服务 (DBaaS)
- **特点**：完全托管的数据库服务，提供高级功能和自动化管理
- **优势**：零运维，自动优化，智能管理
- **劣势**：成本较高，定制性最差
- **代表产品**：AWS Aurora、阿里云PolarDB、腾讯云TDSQL

### 1.3 主流云数据库服务提供商

#### 1.3.1 Amazon Web Services (AWS)
- **RDS for MySQL**：托管的关系型数据库服务
- **Aurora MySQL**：AWS自研的云原生数据库，兼容MySQL
- **Aurora Serverless**：无服务器架构的MySQL兼容数据库

#### 1.3.2 阿里云
- **RDS MySQL**：稳定可靠的在线数据库服务
- **PolarDB MySQL**：云原生关系型数据库，兼容MySQL
- **PolarDB-X**：分布式关系型数据库服务

#### 1.3.3 腾讯云
- **TencentDB for MySQL**：高性能、高可靠的云数据库
- **TDSQL-C MySQL**：云原生数据库，兼容MySQL

#### 1.3.4 其他云服务商
- **Google Cloud**：Cloud SQL for MySQL
- **Microsoft Azure**：Azure Database for MySQL
- **华为云**：GaussDB(for MySQL)

## 2. 主流云数据库服务详解

### 2.1 Amazon RDS for MySQL

#### 2.1.1 服务特点

Amazon RDS (Relational Database Service) for MySQL 是AWS提供的托管MySQL服务，具有以下特点：

1. **自动化管理**：自动补丁、备份、故障转移
2. **高可用性**：主从复制、自动故障转移
3. **安全隔离**：VPC、安全组、加密
4. **弹性扩展**：垂直扩展、只读副本
5. **监控告警**：CloudWatch集成、性能指标
6. **备份恢复**：自动备份、时间点恢复

#### 2.1.2 创建RDS实例

```bash
# 使用AWS CLI创建RDS MySQL实例
aws rds create-db-instance \
    --db-instance-identifier my-mysql-instance \
    --db-instance-class db.t3.micro \
    --engine mysql \
    --engine-version 8.0.35 \
    --master-username admin \
    --master-user-password MySecurePassword123! \
    --allocated-storage 20 \
    --vpc-security-group-ids sg-12345678 \
    --db-subnet-group-name mydb-subnet-group \
    --backup-retention-period 7 \
    --multi-az \
    --storage-type gp2 \
    --publicly-accessible
```

#### 2.1.3 连接RDS实例

```python
# Python示例：连接AWS RDS MySQL
import pymysql
import boto3

# 获取RDS实例信息
rds = boto3.client('rds', region_name='us-east-1')
response = rds.describe_db_instances(DBInstanceIdentifier='my-mysql-instance')
db_instance = response['DBInstances'][0]

endpoint = db_instance['Endpoint']['Address']
port = db_instance['Endpoint']['Port']
username = db_instance['MasterUsername']

# 连接RDS MySQL
connection = pymysql.connect(
    host=endpoint,
    port=port,
    user=username,
    password='MySecurePassword123!',
    database='mydatabase'
)

print(f"成功连接到RDS实例: {endpoint}:{port}")
```

#### 2.1.4 RDS高级功能

**1. 只读副本**
```bash
# 创建只读副本
aws rds create-db-instance-read-replica \
    --db-instance-identifier my-mysql-instance-replica \
    --source-db-instance-identifier my-mysql-instance \
    --db-instance-class db.t3.micro
```

**2. 快照管理**
```bash
# 创建手动快照
aws rds create-db-snapshot \
    --db-instance-identifier my-mysql-instance \
    --db-snapshot-identifier my-mysql-snapshot-$(date +%Y%m%d)

# 从快照恢复
aws rds restore-db-instance-from-db-snapshot \
    --db-instance-identifier my-mysql-restore \
    --db-snapshot-identifier my-mysql-snapshot-20231201
```

### 2.2 AWS Aurora MySQL

#### 2.2.1 服务特点

Aurora是AWS自研的云原生数据库，完全兼容MySQL，具有以下特点：

1. **高性能**：性能可达标准MySQL的5倍
2. **高可用**：跨多可用区存储，秒级故障转移
3. **可扩展**：存储自动扩展至128TB
4. **连续备份**：连续备份到S3，支持时间点恢复
5. **快速恢复**：毫秒级时间点恢复
6. **服务器less**：按需自动扩展，无需管理服务器

#### 2.2.2 创建Aurora集群

```bash
# 创建Aurora数据库集群
aws rds create-db-cluster \
    --db-cluster-identifier my-aurora-cluster \
    --engine aurora-mysql \
    --engine-version 8.0.mysql_aurora.3.02.0 \
    --master-username admin \
    --master-user-password MySecurePassword123! \
    --backup-retention-period 7 \
    --preferred-backup-window 03:00-04:00 \
    --preferred-maintenance-window sun:04:00-sun:05:00 \
    --enable-cloudwatch-logs-export '["error","general","slowquery"]' \
    --db-subnet-group-name mydb-subnet-group \
    --vpc-security-group-ids sg-12345678

# 创建集群主实例
aws rds create-db-instance \
    --db-cluster-identifier my-aurora-cluster \
    --db-instance-identifier my-aurora-instance \
    --db-instance-class db.r6g.large \
    --engine aurora-mysql \
    --publicly-accessible
```

#### 2.2.3 Aurora Serverless

```bash
# 创建Aurora Serverless集群
aws rds create-db-cluster \
    --db-cluster-identifier my-serverless-cluster \
    --engine aurora-mysql \
    --engine-version 8.0.mysql_aurora.3.02.0 \
    --scaling-configuration AutoScaling={MinCapacity=2,MaxCapacity=64} \
    --master-username admin \
    --master-user-password MySecurePassword123! \
    --enable-http-endpoint \
    --serverless-v2-scaling-configuration MinCapacity=0.5,MaxCapacity=16
```

### 2.3 阿里云RDS for MySQL

#### 2.3.1 服务特点

阿里云RDS MySQL是阿里云提供的稳定可靠的在线数据库服务，具有以下特点：

1. **高性能**：企业级硬件，优化内核参数
2. **高可用**：主从热备，自动故障转移
3. **安全可靠**：多层次安全防护，数据加密
4. **弹性扩展**：在线升级规格，秒级扩展
5. **自动备份**：自动备份，时间点恢复
6. **监控告警**：实时监控，智能告警

#### 2.3.2 创建RDS实例

```python
# Python示例：使用阿里云SDK创建RDS实例
from aliyunsdkcore.client import AcsClient
from aliyunsdkrds.request.v20140815 import CreateDBInstanceRequest

# 初始化客户端
client = AcsClient(
    access_key_id='your_access_key',
    access_key_secret='your_access_secret',
    region_id='cn-hangzhou'
)

# 创建RDS实例请求
request = CreateDBInstanceRequest.CreateDBInstanceRequest()
request.set_Engine('MySQL')
request.set_EngineVersion('8.0')
request.set_DBInstanceClass('mysql.n2.small.1')
request.set_DBInstanceStorage(20)
request.set_DBInstanceStorageType('cloud_essd')
request.set_SecurityIPList('0.0.0.0/0')
request.set_PayType('Postpaid')

# 发送请求
response = client.do_action_with_exception(request)
print(response)
```

#### 2.3.3 连接RDS实例

```python
# Python示例：连接阿里云RDS MySQL
import pymysql

# RDS连接信息
rds_host = 'rm-bp1xxxxxxxxxxxx.mysql.rds.aliyuncs.com'
rds_port = 3306
rds_user = 'your_username'
rds_password = 'your_password'
rds_database = 'your_database'

# 连接RDS
connection = pymysql.connect(
    host=rds_host,
    port=rds_port,
    user=rds_user,
    password=rds_password,
    database=rds_database,
    charset='utf8mb4'
)

print(f"成功连接到阿里云RDS实例: {rds_host}")
```

### 2.4 腾讯云TencentDB for MySQL

#### 2.4.1 服务特点

腾讯云TencentDB for MySQL是高性能、高可靠的云数据库服务，具有以下特点：

1. **高性能**：高性能SSD，优化内核
2. **高可用**：主从架构，自动故障转移
3. **安全可靠**：VPC网络，数据加密
4. **弹性扩展**：在线升级，自动扩容
5. **智能运维**：智能分析，自动优化
6. **备份恢复**：自动备份，快速恢复

#### 2.4.2 创建TencentDB实例

```python
# Python示例：使用腾讯云SDK创建TencentDB实例
from tencentcloud.common import credential
from tencentcloud.cdb.v20170320 import cdb_client, models

# 初始化凭证
cred = credential.Credential(
    secret_id='your_secret_id',
    secret_key='your_secret_key'
)

# 初始化客户端
client = cdb_client.CdbClient(cred, "ap-guangzhou")

# 创建实例请求
req = models.CreateInstancesRequest()
params = {
    "GoodsNum": 1,
    "Memory": 1000,
    "Volume": 50,
    "InstanceRole": "master",
    "EngineVersion": "8.0",
    "InstanceType": "CLOUD_PREMIUM",
    "PayType": "POSTPAID",
    "Period": 1,
    "Zone": "ap-guangzhou-2",
    "ProjectId": 0,
    "InstanceName": "test-mysql"
}
req.from_json_string(json.dumps(params))

# 发送请求
resp = client.CreateInstances(req)
print(resp.to_json_string())
```

## 3. 容器化MySQL

### 3.1 Docker容器化MySQL

#### 3.1.1 基础Docker使用

**1. 拉取MySQL镜像**
```bash
# 拉取官方MySQL镜像
docker pull mysql:8.0

# 查看本地镜像
docker images | grep mysql
```

**2. 运行MySQL容器**
```bash
# 基本运行方式
docker run --name my-mysql -e MYSQL_ROOT_PASSWORD=my-secret-pw -d mysql:8.0

# 带数据持久化的运行方式
docker run --name my-mysql \
  -e MYSQL_ROOT_PASSWORD=my-secret-pw \
  -e MYSQL_DATABASE=mydb \
  -e MYSQL_USER=myuser \
  -e MYSQL_PASSWORD=mypassword \
  -v /my/custom/mysql/conf.d:/etc/mysql/conf.d \
  -v /my/custom/mysql/data:/var/lib/mysql \
  -p 3306:3306 \
  -d mysql:8.0
```

**3. 连接MySQL容器**
```bash
# 使用docker exec连接
docker exec -it my-mysql mysql -uroot -p

# 使用mysql客户端连接
mysql -h 127.0.0.1 -P 3306 -u root -p
```

#### 3.1.2 自定义配置

**1. 创建配置文件**
```ini
# /my/custom/mysql/conf.d/my.cnf
[mysqld]
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci
max_connections=1000
innodb_buffer_pool_size=256M
log-error=/var/log/mysql/error.log
slow_query_log=1
slow_query_log_file=/var/log/mysql/slow.log
long_query_time=2
```

**2. 带配置运行容器**
```bash
docker run --name my-mysql \
  -e MYSQL_ROOT_PASSWORD=my-secret-pw \
  -v /my/custom/mysql/conf.d:/etc/mysql/conf.d \
  -v /my/custom/mysql/data:/var/lib/mysql \
  -v /my/custom/mysql/logs:/var/log/mysql \
  -p 3306:3306 \
  -d mysql:8.0
```

#### 3.1.3 数据备份与恢复

**1. 数据备份**
```bash
# 从容器内备份
docker exec my-mysql sh -c 'exec mysqldump --all-databases -uroot -p"$MYSQL_ROOT_PASSWORD"' > backup.sql

# 从容器外备份
docker exec -it my-mysql mysqldump -uroot -pmy-secret-pw --all-databases > backup.sql
```

**2. 数据恢复**
```bash
# 恢复到容器
docker exec -i my-mysql mysql -uroot -pmy-secret-pw < backup.sql
```

#### 3.1.4 Docker Compose配置

**docker-compose.yml文件示例：**
```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: mysql-server
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: my-secret-pw
      MYSQL_DATABASE: mydb
      MYSQL_USER: myuser
      MYSQL_PASSWORD: mypassword
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - mysql_config:/etc/mysql/conf.d
      - mysql_logs:/var/log/mysql
    networks:
      - mysql_net
    command: --default-authentication-plugin=mysql_native_password

  mysql-admin:
    image: phpmyadmin:5.2
    container_name: mysql-admin
    restart: always
    ports:
      - "8080:80"
    environment:
      PMA_HOST: mysql
      PMA_USER: root
      PMA_PASSWORD: my-secret-pw
    networks:
      - mysql_net

volumes:
  mysql_data:
    driver: local
  mysql_config:
    driver: local
  mysql_logs:
    driver: local

networks:
  mysql_net:
    driver: bridge
```

**使用Docker Compose启动：**
```bash
# 启动服务
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs mysql

# 停止服务
docker-compose down
```

### 3.2 Kubernetes上的MySQL

#### 3.2.1 部署架构

在Kubernetes上部署MySQL通常采用以下架构：

1. **StatefulSet**：保证Pod的唯一性和稳定的网络标识
2. **PersistentVolume**：提供持久化存储
3. **Service**：提供稳定的访问端点
4. **ConfigMap**：存储配置文件
5. **Secret**：存储敏感信息如密码

#### 3.2.2 单节点MySQL部署

**1. 创建命名空间**
```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: mysql
```

**2. 创建Secret**
```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: mysql-secret
  namespace: mysql
type: Opaque
data:
  # echo -n 'my-secret-pw' | base64
  mysql-root-password: bXktc2VjcmV0LXB3
  # echo -n 'myuser' | base64
  mysql-user: bXl1c2Vy
  # echo -n 'mypassword' | base64
  mysql-password: bXlwYXNzd29yZA==
```

**3. 创建ConfigMap**
```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mysql-config
  namespace: mysql
data:
  my.cnf: |
    [mysqld]
    character-set-server=utf8mb4
    collation-server=utf8mb4_unicode_ci
    max_connections=1000
    innodb_buffer_pool_size=256M
    log-error=/var/log/mysql/error.log
    slow_query_log=1
    slow_query_log_file=/var/log/mysql/slow.log
    long_query_time=2
```

**4. 创建PersistentVolume**
```yaml
# pv.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: mysql-pv
  namespace: mysql
spec:
  capacity:
    storage: 20Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: standard
  hostPath:
    path: /data/mysql
```

**5. 创建PersistentVolumeClaim**
```yaml
# pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-pvc
  namespace: mysql
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
  storageClassName: standard
```

**6. 创建StatefulSet**
```yaml
# statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
  namespace: mysql
spec:
  serviceName: mysql
  replicas: 1
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        ports:
        - containerPort: 3306
          name: mysql
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: mysql-root-password
        - name: MYSQL_DATABASE
          value: mydb
        - name: MYSQL_USER
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: mysql-user
        - name: MYSQL_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: mysql-password
        volumeMounts:
        - name: mysql-storage
          mountPath: /var/lib/mysql
        - name: mysql-config
          mountPath: /etc/mysql/conf.d
        - name: mysql-logs
          mountPath: /var/log/mysql
      volumes:
      - name: mysql-config
        configMap:
          name: mysql-config
      - name: mysql-logs
        emptyDir: {}
  volumeClaimTemplates:
  - metadata:
      name: mysql-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 20Gi
      storageClassName: standard
```

**7. 创建Service**
```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: mysql-service
  namespace: mysql
spec:
  selector:
    app: mysql
  ports:
  - port: 3306
    targetPort: 3306
  type: ClusterIP
```

**8. 部署所有资源**
```bash
# 应用所有YAML文件
kubectl apply -f namespace.yaml
kubectl apply -f secret.yaml
kubectl apply -f configmap.yaml
kubectl apply -f pv.yaml
kubectl apply -f pvc.yaml
kubectl apply -f statefulset.yaml
kubectl apply -f service.yaml

# 查看部署状态
kubectl get all -n mysql

# 查看Pod日志
kubectl logs -f mysql-0 -n mysql
```

#### 3.2.3 MySQL主从复制

**1. 主节点StatefulSet**
```yaml
# mysql-master.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql-master
  namespace: mysql
spec:
  serviceName: mysql-master
  replicas: 1
  selector:
    matchLabels:
      app: mysql-master
  template:
    metadata:
      labels:
        app: mysql-master
    spec:
      containers:
      - name: mysql-master
        image: mysql:8.0
        ports:
        - containerPort: 3306
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: mysql-root-password
        volumeMounts:
        - name: mysql-master-storage
          mountPath: /var/lib/mysql
        - name: mysql-config
          mountPath: /etc/mysql/conf.d
      volumes:
      - name: mysql-config
        configMap:
          name: mysql-config-master
  volumeClaimTemplates:
  - metadata:
      name: mysql-master-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 20Gi
```

**2. 从节点StatefulSet**
```yaml
# mysql-slave.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql-slave
  namespace: mysql
spec:
  serviceName: mysql-slave
  replicas: 2
  selector:
    matchLabels:
      app: mysql-slave
  template:
    metadata:
      labels:
        app: mysql-slave
    spec:
      containers:
      - name: mysql-slave
        image: mysql:8.0
        ports:
        - containerPort: 3306
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: mysql-root-password
        volumeMounts:
        - name: mysql-slave-storage
          mountPath: /var/lib/mysql
        - name: mysql-config
          mountPath: /etc/mysql/conf.d
      volumes:
      - name: mysql-config
        configMap:
          name: mysql-config-slave
  volumeClaimTemplates:
  - metadata:
      name: mysql-slave-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 20Gi
```

**3. 配置主从复制**
```sql
-- 在主节点执行
CREATE USER 'repl_user'@'%' IDENTIFIED BY 'repl_password';
GRANT REPLICATION SLAVE ON *.* TO 'repl_user'@'%';
FLUSH PRIVILEGES;

-- 获取主节点状态
SHOW MASTER STATUS;
```

```sql
-- 在从节点执行
CHANGE MASTER TO
  MASTER_HOST='mysql-master-service',
  MASTER_USER='repl_user',
  MASTER_PASSWORD='repl_password',
  MASTER_LOG_FILE='mysql-bin.000001',
  MASTER_LOG_POS=123;

START SLAVE;

-- 检查从节点状态
SHOW SLAVE STATUS\G;
```

### 3.3 Helm Chart部署MySQL

#### 3.3.1 Helm简介

Helm是Kubernetes的包管理工具，可以简化Kubernetes应用的部署和管理。通过Helm，可以:

1. 管理复杂的Kubernetes应用
2. 版本控制和回滚
3. 共享和复用应用模板
4. 参数化配置

#### 3.3.2 使用官方MySQL Helm Chart

**1. 添加Helm仓库**
```bash
# 添加bitnami仓库
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# 搜索MySQL Chart
helm search repo mysql
```

**2. 自定义values.yaml**
```yaml
# values.yaml
auth:
  rootPassword: my-secret-pw
  database: mydb
  username: myuser
  password: mypassword

primary:
  persistence:
    enabled: true
    size: 20Gi
  configuration: |
    [mysqld]
    character-set-server=utf8mb4
    collation-server=utf8mb4_unicode_ci
    max_connections=1000
    innodb_buffer_pool_size=256M

secondary:
  replicaCount: 2
  persistence:
    enabled: true
    size: 20Gi

metrics:
  enabled: true
  serviceMonitor:
    enabled: true
    namespace: mysql

initdbScripts:
  my-init.sql: |
    CREATE TABLE users (
      id INT PRIMARY KEY AUTO_INCREMENT,
      username VARCHAR(50) NOT NULL,
      email VARCHAR(100) NOT NULL
    );
```

**3. 安装MySQL**
```bash
# 创建命名空间
kubectl create namespace mysql-helm

# 安装MySQL
helm install mysql bitnami/mysql \
  --namespace mysql-helm \
  --values values.yaml

# 查看部署状态
helm list -n mysql-helm
kubectl get all -n mysql-helm
```

**4. 连接到MySQL**
```bash
# 获取root密码
kubectl get secret --namespace mysql-helm mysql -o jsonpath="{.data.mysql-root-password}" | base64 -d

# 转发端口
kubectl port-forward --namespace mysql-helm svc/mysql 3306:3306 &

# 连接MySQL
mysql -h 127.0.0.1 -P 3306 -u root -p
```

**5. 升级MySQL**
```bash
# 更新values.yaml后
helm upgrade mysql bitnami/mysql \
  --namespace mysql-helm \
  --values values.yaml
```

**6. 回滚MySQL**
```bash
# 查看历史版本
helm history mysql -n mysql-helm

# 回滚到指定版本
helm rollback mysql 1 -n mysql-helm
```

#### 3.3.3 创建自定义MySQL Helm Chart

**1. 创建Chart结构**
```bash
# 创建Chart
helm create custom-mysql

# 目录结构
custom-mysql/
├── Chart.yaml          # Chart元信息
├── values.yaml         # 默认配置值
├── templates/          # Kubernetes资源模板
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── pvc.yaml
│   └── ingress.yaml
└── charts/            # 依赖的子Chart
```

**2. 编辑Chart.yaml**
```yaml
# Chart.yaml
apiVersion: v2
name: custom-mysql
description: A Helm chart for custom MySQL deployment
type: application
version: 0.1.0
appVersion: "8.0.35"
keywords:
  - mysql
  - database
  - sql
home: https://www.mysql.com/
sources:
  - https://github.com/mysql/mysql-server
maintainers:
  - name: MySQL Team
    email: mysql-team@oracle.com
```

**3. 编辑values.yaml**
```yaml
# values.yaml
# 默认配置
global:
  imageRegistry: ""
  imagePullSecrets: []
  storageClass: ""

image:
  registry: docker.io
  repository: mysql
  tag: "8.0.35"
  pullPolicy: IfNotPresent

auth:
  rootPassword: ""
  database: ""
  username: ""
  password: ""

service:
  type: ClusterIP
  port: 3306

persistence:
  enabled: true
  size: 20Gi
  # storageClass: ""

resources:
  limits:
    cpu: 1000m
    memory: 2Gi
  requests:
    cpu: 500m
    memory: 1Gi

configuration: |
  [mysqld]
  character-set-server=utf8mb4
  collation-server=utf8mb4_unicode_ci

replicaCount: 1
```

**4. 创建模板文件**
```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "custom-mysql.fullname" . }}
  labels:
    {{- include "custom-mysql.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "custom-mysql.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "custom-mysql.selectorLabels" . | nindent 8 }}
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.registry }}/{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        ports:
        - name: mysql
          containerPort: 3306
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: {{ include "custom-mysql.fullname" . }}
              key: mysql-root-password
        {{- if .Values.auth.database }}
        - name: MYSQL_DATABASE
          value: {{ .Values.auth.database }}
        {{- end }}
        {{- if .Values.auth.username }}
        - name: MYSQL_USER
          valueFrom:
            secretKeyRef:
              name: {{ include "custom-mysql.fullname" . }}
              key: mysql-user
        - name: MYSQL_PASSWORD
          valueFrom:
            secretKeyRef:
              name: {{ include "custom-mysql.fullname" . }}
              key: mysql-password
        {{- end }}
        volumeMounts:
        - name: mysql-data
          mountPath: /var/lib/mysql
        - name: mysql-config
          mountPath: /etc/mysql/conf.d
        resources:
          {{- toYaml .Values.resources | nindent 12 }}
      volumes:
      - name: mysql-data
        {{- if .Values.persistence.enabled }}
        persistentVolumeClaim:
          claimName: {{ include "custom-mysql.fullname" . }}
        {{- else }}
        emptyDir: {}
        {{- end }}
      - name: mysql-config
        configMap:
          name: {{ include "custom-mysql.fullname" . }}-config
```

## 4. 云原生MySQL最佳实践

### 4.1 高可用设计

#### 4.1.1 多可用区部署

```yaml
# 在多可用区部署MySQL StatefulSet
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql-ha
spec:
  replicas: 3
  template:
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchLabels:
                app: mysql-ha
            topologyKey: "kubernetes.io/hostname"
      containers:
      - name: mysql
        image: mysql:8.0
        # ...其他配置
```

#### 4.1.2 故障转移配置

```yaml
# 故障转移脚本示例
apiVersion: v1
kind: ConfigMap
metadata:
  name: failover-script
data:
  failover.sh: |
    #!/bin/bash
    
    # 检查主节点健康状态
    function check_master_health() {
      mysqladmin ping -h $MASTER_HOST -u root -p$MYSQL_ROOT_PASSWORD >/dev/null 2>&1
      return $?
    }
    
    # 执行故障转移
    function perform_failover() {
      # 停止从节点的复制
      mysql -h $SLAVE_HOST -u root -p$MYSQL_ROOT_PASSWORD -e "STOP SLAVE;"
      
      # 设置从节点为新的主节点
      mysql -h $SLAVE_HOST -u root -p$MYSQL_ROOT_PASSWORD -e "RESET MASTER;"
      
      # 更新Service指向新的主节点
      kubectl patch service mysql-service -p '{"spec":{"selector":{"app":"mysql-slave"}}}'
    }
    
    # 主循环
    while true; do
      if ! check_master_health; then
        perform_failover
        break
      fi
      sleep 10
    done
```

### 4.2 性能优化

#### 4.2.1 资源配置优化

```yaml
# 根据工作负载配置资源限制
resources:
  # 高性能配置
  limits:
    cpu: 2000m
    memory: 4Gi
    ephemeral-storage: 10Gi
  requests:
    cpu: 1500m
    memory: 3Gi
    
  # 标准配置
  limits:
    cpu: 1000m
    memory: 2Gi
    ephemeral-storage: 5Gi
  requests:
    cpu: 500m
    memory: 1Gi
```

#### 4.2.2 存储优化

```yaml
# 使用高性能存储类
persistence:
  enabled: true
  storageClass: "ssd"  # 使用SSD存储类
  size: 100Gi
  accessModes:
    - ReadWriteOnce
  annotations:
    volume.beta.kubernetes.io/storage-class: "fast-ssd"
```

#### 4.2.3 MySQL配置优化

```yaml
# 针对云环境优化的MySQL配置
configuration: |
  [mysqld]
  # 基本配置
  character-set-server=utf8mb4
  collation-server=utf8mb4_unicode_ci
  
  # 内存配置（根据Pod内存调整）
  innodb_buffer_pool_size=2G
  innodb_buffer_pool_instances=2
  key_buffer_size=256M
  
  # 连接配置
  max_connections=500
  max_connect_errors=1000
  
  # 日志配置
  log-error=/var/log/mysql/error.log
  slow_query_log=1
  slow_query_log_file=/var/log/mysql/slow.log
  long_query_time=2
  
  # InnoDB配置
  innodb_flush_log_at_trx_commit=2  # 平衡性能和安全性
  innodb_flush_method=O_DIRECT     # 避免双重缓冲
  innodb_file_per_table=1         # 独立表空间
  
  # 云环境特定优化
  skip-name-resolve               # 避免DNS解析延迟
  sync_binlog=0                   # 减少IO（根据安全需求调整）
```

### 4.3 安全实践

#### 4.3.1 网络安全

```yaml
# 限制Service访问范围
apiVersion: v1
kind: Service
metadata:
  name: mysql-service
  annotations:
    # 限制只能从特定命名空间访问
    networking.istio.io/exportTo: "app-namespace"
spec:
  type: ClusterIP
  selector:
    app: mysql
  ports:
  - port: 3306
    targetPort: 3306

# 使用NetworkPolicy限制访问
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: mysql-netpol
spec:
  podSelector:
    matchLabels:
      app: mysql
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: app-namespace
    ports:
    - protocol: TCP
      port: 3306
```

#### 4.3.2 数据加密

```yaml
# 使用KMS管理密钥
apiVersion: v1
kind: Secret
metadata:
  name: mysql-secret
  annotations:
    # 使用云提供商的KMS加密Secret
    kms-encryption: "enabled"
type: Opaque
data:
  # 加密的密码
  mysql-root-password: <base64-encoded-encrypted-password>

# 启用MySQL传输加密
configuration: |
  [mysqld]
  # 启用SSL/TLS
  require_secure_transport=ON
  ssl-ca=/etc/mysql/ssl/ca.pem
  ssl-cert=/etc/mysql/ssl/server-cert.pem
  ssl-key=/etc/mysql/ssl/server-key.pem
```

### 4.4 监控与告警

#### 4.4.1 Prometheus监控配置

```yaml
# 使用Sidecar模式部署MySQL Exporter
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql-exporter
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mysql-exporter
  template:
    metadata:
      labels:
        app: mysql-exporter
    spec:
      containers:
      - name: mysql-exporter
        image: prom/mysqld-exporter:latest
        env:
        - name: DATA_SOURCE_NAME
          value: "user:password@(mysql-service:3306)/"
        ports:
        - containerPort: 9104
          name: metrics
```

```yaml
# ServiceMonitor配置
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: mysql-monitor
  labels:
    app: mysql
spec:
  selector:
    matchLabels:
      app: mysql
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

#### 4.4.2 告警规则配置

```yaml
# PrometheusRule定义告警规则
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: mysql-alerts
spec:
  groups:
  - name: mysql.rules
    rules:
    - alert: MySQLDown
      expr: up{job="mysql"} == 0
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "MySQL instance is down"
        description: "MySQL instance has been down for more than 1 minute."
    
    - alert: MySQLSlowQueries
      expr: mysql_global_status_slow_queries > 10
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "MySQL slow queries detected"
        description: "MySQL has more than 10 slow queries in the last 5 minutes."
    
    - alert: MySQLConnectionsHigh
      expr: mysql_global_status_threads_connected / mysql_global_variables_max_connections > 0.8
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "MySQL connections high"
        description: "MySQL connections are above 80% of max connections."
```

### 4.5 备份与恢复策略

#### 4.5.1 自动备份CronJob

```yaml
# 定时备份CronJob
apiVersion: batch/v1
kind: CronJob
metadata:
  name: mysql-backup
spec:
  schedule: "0 2 * * *"  # 每天凌晨2点执行
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: mysql-backup
            image: mysql:8.0
            command:
            - /bin/bash
            - -c
            - |
              DATE=$(date +%Y%m%d_%H%M%S)
              BACKUP_FILE="/backup/mysql_backup_${DATE}.sql"
              
              # 创建备份
              mysqldump -h mysql-service -u root -p$MYSQL_ROOT_PASSWORD --all-databases > $BACKUP_FILE
              
              # 压缩备份文件
              gzip $BACKUP_FILE
              
              # 上传到对象存储（示例为AWS S3）
              aws s3 cp ${BACKUP_FILE}.gz s3://my-backup-bucket/mysql/
              
              # 清理本地文件
              rm ${BACKUP_FILE}.gz
              
              # 清理7天前的备份
              aws s3 ls s3://my-backup-bucket/mysql/ | while read -r line; do
                createDate=$(echo "$line" | awk '{print $1" "$2}')
                createDate=$(date -d"$createDate" +%s)
                olderThan=$(date -d"7 days ago" +%s)
                if [[ $createDate -lt $olderThan ]]; then
                  fileName=$(echo "$line" | awk '{print $4}')
                  aws s3 rm "s3://my-backup-bucket/mysql/$fileName"
                fi
              done
            env:
            - name: MYSQL_ROOT_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mysql-secret
                  key: mysql-root-password
            - name: AWS_ACCESS_KEY_ID
              valueFrom:
                secretKeyRef:
                  name: aws-credentials
                  key: access-key-id
            - name: AWS_SECRET_ACCESS_KEY
              valueFrom:
                secretKeyRef:
                  name: aws-credentials
                  key: secret-access-key
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: backup-storage
            emptyDir: {}
          restartPolicy: OnFailure
```

#### 4.5.2 恢复Job

```yaml
# 恢复数据Job
apiVersion: batch/v1
kind: Job
metadata:
  name: mysql-restore
spec:
  template:
    spec:
      containers:
      - name: mysql-restore
        image: mysql:8.0
        command:
        - /bin/bash
        - -c
        - |
          # 从对象存储下载备份
          aws s3 cp s3://my-backup-bucket/mysql/mysql_backup_${BACKUP_DATE}.sql.gz /tmp/
          
          # 解压备份
          gunzip /tmp/mysql_backup_${BACKUP_DATE}.sql.gz
          
          # 停止应用访问（可选）
          kubectl scale deployment app --replicas=0
          
          # 恢复数据库
          mysql -h mysql-service -u root -p$MYSQL_ROOT_PASSWORD < /tmp/mysql_backup_${BACKUP_DATE}.sql
          
          # 恢复应用访问
          kubectl scale deployment app --replicas=3
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: mysql-root-password
        - name: BACKUP_DATE
          value: "20231201_020000"  # 指定要恢复的备份日期
        - name: AWS_ACCESS_KEY_ID
          valueFrom:
            secretKeyRef:
              name: aws-credentials
              key: access-key-id
        - name: AWS_SECRET_ACCESS_KEY
          valueFrom:
            secretKeyRef:
              name: aws-credentials
              key: secret-access-key
      restartPolicy: Never
```

## 总结

本章全面介绍了MySQL在云环境和容器化环境中的部署和管理。我们探讨了从基础的云数据库服务到高级的云原生部署方式，包括：

### 云数据库服务
1. **AWS RDS for MySQL**：完全托管的关系型数据库服务
2. **AWS Aurora MySQL**：高性能、高可用的云原生数据库
3. **阿里云RDS MySQL**：稳定可靠的在线数据库服务
4. **腾讯云TencentDB MySQL**：高性能、高可靠的云数据库

### 容器化部署
1. **Docker容器化**：单机容器部署，适合开发测试环境
2. **Kubernetes部署**：生产级容器编排，支持高可用和自动扩展
3. **Helm Chart管理**：简化Kubernetes应用的部署和管理

### 最佳实践
1. **高可用设计**：多可用区部署、故障转移机制
2. **性能优化**：资源配置、存储优化、MySQL参数调优
3. **安全实践**：网络安全、数据加密、访问控制
4. **监控告警**：Prometheus监控、自定义告警规则
5. **备份恢复**：自动备份策略、灾难恢复方案

随着云计算和容器技术的发展，MySQL的部署方式正在从传统的物理机/虚拟机向云原生方向演进。选择合适的部署方式需要综合考虑业务需求、运维能力、成本预算和未来发展规划。

云数据库服务适合希望降低运维负担、快速上线的应用；容器化部署适合需要高度定制化、自动化的应用；而云原生方案则适合需要极致弹性、大规模部署的现代应用。

无论选择哪种部署方式，都需要遵循最佳实践，确保数据库的高可用、高性能和安全可靠，为业务提供稳定的数据服务。