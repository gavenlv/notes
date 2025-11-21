# 第十三章：备份与恢复策略

## 13.1 备份与恢复概述

在企业环境中，数据安全和业务连续性至关重要。Apache Superset 作为数据分析平台，其配置、元数据和用户创建的内容都需要制定完善的备份与恢复策略，以应对意外情况的发生。

### 备份的重要性

1. **数据保护**：防止因硬件故障、人为误操作或恶意攻击导致的数据丢失
2. **业务连续性**：确保在发生灾难时能够快速恢复系统运行
3. **合规要求**：满足行业法规和企业内部政策对数据保护的要求
4. **版本回退**：当升级或变更出现问题时，能够回退到之前的稳定状态

### 备份策略原则

#### 3-2-1 备份原则

- **3** 个副本：至少保留三份数据副本
- **2** 种介质：使用两种不同的存储介质
- **1** 个异地：至少一份备份存储在异地

#### 备份类型

1. **完全备份**：备份所有数据和配置，恢复速度快但占用空间大
2. **增量备份**：只备份自上次备份以来发生变化的数据，节省空间但恢复复杂
3. **差异备份**：备份自上次完全备份以来发生变化的数据，平衡了空间和恢复复杂度

## 13.2 备份内容识别

### 核心组件备份需求

#### 元数据数据库

Apache Superset 的核心数据存储在关系型数据库中，包括：

- 用户账户和权限信息
- 数据源连接配置
- 数据集定义和配置
- 图表和仪表板定义
- 查询历史和收藏夹
- 注释和告警配置
- 系统配置和设置

#### 配置文件

- `superset_config.py`：主要配置文件
- 环境变量配置
- SSL 证书文件
- 自定义样式和模板文件

#### 缓存数据

- Redis 或 Memcached 中的会话数据
- 查询结果缓存
- 元数据缓存

#### 日志文件

- 应用日志
- 错误日志
- 审计日志

### 备份优先级划分

```python
# 备份优先级定义
BACKUP_PRIORITY = {
    'critical': [
        'metadata_database',     # 元数据数据库（最高优先级）
        'config_files',          # 配置文件
        'ssl_certificates'       # SSL 证书
    ],
    'important': [
        'user_content',          # 用户创建的内容（图表、仪表板）
        'query_cache',           # 查询缓存
        'session_data'           # 会话数据
    ],
    'optional': [
        'logs',                  # 日志文件
        'temp_files',            # 临时文件
        'export_files'           # 导出文件
    ]
}
```

## 13.3 数据库备份策略

### MySQL/MariaDB 备份

```bash
#!/bin/bash
# MySQL 数据库备份脚本

# 配置变量
DB_HOST="localhost"
DB_PORT="3306"
DB_NAME="superset"
DB_USER="superset_backup"
DB_PASS="your_secure_password"
BACKUP_DIR="/backup/superset/database"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${DATE}.sql"

# 创建备份目录
mkdir -p ${BACKUP_DIR}

# 执行备份
mysqldump \
  --host=${DB_HOST} \
  --port=${DB_PORT} \
  --user=${DB_USER} \
  --password=${DB_PASS} \
  --single-transaction \
  --routines \
  --triggers \
  --events \
  --hex-blob \
  --opt \
  ${DB_NAME} > ${BACKUP_FILE}

# 检查备份是否成功
if [ $? -eq 0 ]; then
    echo "Database backup successful: ${BACKUP_FILE}"
    
    # 压缩备份文件
    gzip ${BACKUP_FILE}
    
    # 删除7天前的备份
    find ${BACKUP_DIR} -name "${DB_NAME}_*.sql.gz" -mtime +7 -delete
else
    echo "Database backup failed!"
    exit 1
fi
```

### PostgreSQL 备份

```bash
#!/bin/bash
# PostgreSQL 数据库备份脚本

# 配置变量
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="superset"
DB_USER="superset_backup"
BACKUP_DIR="/backup/superset/database"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${DATE}.sql"

# 创建备份目录
mkdir -p ${BACKUP_DIR}

# 设置环境变量
export PGPASSWORD="your_secure_password"

# 执行备份
pg_dump \
  --host=${DB_HOST} \
  --port=${DB_PORT} \
  --username=${DB_USER} \
  --dbname=${DB_NAME} \
  --clean \
  --create \
  --no-owner \
  --no-privileges \
  --verbose \
  --file=${BACKUP_FILE}

# 检查备份是否成功
if [ $? -eq 0 ]; then
    echo "Database backup successful: ${BACKUP_FILE}"
    
    # 压缩备份文件
    gzip ${BACKUP_FILE}
    
    # 删除7天前的备份
    find ${BACKUP_DIR} -name "${DB_NAME}_*.sql.gz" -mtime +7 -delete
else
    echo "Database backup failed!"
    exit 1
fi
```

### 数据库备份验证

```python
# 数据库备份验证脚本
import subprocess
import sys
import gzip
import os

class DatabaseBackupValidator:
    """数据库备份验证器"""
    
    def __init__(self, db_type='mysql'):
        self.db_type = db_type
    
    def validate_backup(self, backup_file):
        """验证备份文件完整性"""
        if not os.path.exists(backup_file):
            print(f"Backup file not found: {backup_file}")
            return False
        
        # 检查文件大小
        file_size = os.path.getsize(backup_file)
        if file_size < 1024:  # 小于1KB可能有问题
            print(f"Backup file too small: {file_size} bytes")
            return False
        
        # 对于压缩文件，尝试解压验证
        if backup_file.endswith('.gz'):
            try:
                with gzip.open(backup_file, 'rt') as f:
                    # 读取前几行检查格式
                    first_lines = [next(f) for _ in range(5)]
                    if self.db_type == 'mysql':
                        # MySQL 备份应该有 CREATE DATABASE 语句
                        if not any('CREATE DATABASE' in line for line in first_lines):
                            print("Invalid MySQL backup format")
                            return False
                    elif self.db_type == 'postgresql':
                        # PostgreSQL 备份应该有 PostgreSQL 版本信息
                        if not any('PostgreSQL' in line for line in first_lines):
                            print("Invalid PostgreSQL backup format")
                            return False
            except Exception as e:
                print(f"Failed to decompress backup file: {e}")
                return False
        
        print(f"Backup file validation passed: {backup_file}")
        return True
    
    def restore_test(self, backup_file, test_db_name):
        """测试恢复到临时数据库"""
        # 这是一个简化的示例，实际使用需要更复杂的逻辑
        print(f"Testing restore to {test_db_name}...")
        # 实际恢复测试逻辑
        return True

# 使用示例
validator = DatabaseBackupValidator('mysql')
backup_file = "/backup/superset/database/superset_20231201_120000.sql.gz"
if validator.validate_backup(backup_file):
    print("Backup validation successful")
else:
    print("Backup validation failed")
    sys.exit(1)
```

## 13.4 文件系统备份

### 配置文件备份

```bash
#!/bin/bash
# 配置文件备份脚本

# 配置变量
CONFIG_DIRS=(
    "/etc/superset"
    "/home/superset/config"
)
BACKUP_DIR="/backup/superset/config"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/config_${DATE}.tar.gz"

# 创建备份目录
mkdir -p ${BACKUP_DIR}

# 执行备份
tar -czf ${BACKUP_FILE} ${CONFIG_DIRS[@]}

# 检查备份是否成功
if [ $? -eq 0 ]; then
    echo "Configuration backup successful: ${BACKUP_FILE}"
    
    # 删除30天前的备份
    find ${BACKUP_DIR} -name "config_*.tar.gz" -mtime +30 -delete
else
    echo "Configuration backup failed!"
    exit 1
fi
```

### 用户内容备份

```bash
# 用户内容备份脚本
#!/bin/bash

# 配置变量
CONTENT_DIRS=(
    "/var/lib/superset/uploads"
    "/var/lib/superset/export"
)
BACKUP_DIR="/backup/superset/content"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/content_${DATE}.tar.gz"

# 创建备份目录
mkdir -p ${BACKUP_DIR}

# 执行备份
tar -czf ${BACKUP_FILE} ${CONTENT_DIRS[@]}

# 检查备份是否成功
if [ $? -eq 0 ]; then
    echo "Content backup successful: ${BACKUP_FILE}"
    
    # 删除15天前的备份
    find ${BACKUP_DIR} -name "content_*.tar.gz" -mtime +15 -delete
else
    echo "Content backup failed!"
    exit 1
fi
```

### 缓存数据备份

```bash
#!/bin/bash
# Redis 缓存备份脚本

# 配置变量
REDIS_HOST="localhost"
REDIS_PORT="6379"
BACKUP_DIR="/backup/superset/cache"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/redis_${DATE}.rdb"

# 创建备份目录
mkdir -p ${BACKUP_DIR}

# 执行 BGSAVE 并等待完成
redis-cli -h ${REDIS_HOST} -p ${REDIS_PORT} BGSAVE

# 等待备份完成
while [ "$(redis-cli -h ${REDIS_HOST} -p ${REDIS_PORT} LASTSAVE)" -lt "$(date +%s)" ]; do
    sleep 1
done

# 复制 RDB 文件
cp /var/lib/redis/dump.rdb ${BACKUP_FILE}

# 检查备份是否成功
if [ $? -eq 0 ]; then
    echo "Redis backup successful: ${BACKUP_FILE}"
    
    # 压缩备份文件
    gzip ${BACKUP_FILE}
    
    # 删除7天前的备份
    find ${BACKUP_DIR} -name "redis_*.rdb.gz" -mtime +7 -delete
else
    echo "Redis backup failed!"
    exit 1
fi
```

## 13.5 自动化备份方案

### 备份调度脚本

```python
# 统一备份调度器
import schedule
import time
import subprocess
import logging
from datetime import datetime

class BackupScheduler:
    """统一备份调度器"""
    
    def __init__(self, config_file='/etc/superset/backup_config.yaml'):
        self.config_file = config_file
        self.load_config()
        self.setup_logging()
    
    def load_config(self):
        """加载备份配置"""
        import yaml
        with open(self.config_file, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/var/log/superset/backup.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('BackupScheduler')
    
    def schedule_backups(self):
        """安排备份任务"""
        # 数据库备份 - 每天凌晨2点
        schedule.every().day.at("02:00").do(self.backup_database)
        
        # 配置文件备份 - 每周日凌晨3点
        schedule.every().sunday.at("03:00").do(self.backup_config)
        
        # 用户内容备份 - 每天凌晨4点
        schedule.every().day.at("04:00").do(self.backup_content)
        
        # 缓存备份 - 每小时
        schedule.every().hour.do(self.backup_cache)
        
        self.logger.info("Backup schedules configured")
    
    def backup_database(self):
        """数据库备份"""
        self.logger.info("Starting database backup")
        try:
            result = subprocess.run([
                '/usr/local/bin/superset-db-backup.sh'
            ], capture_output=True, text=True, timeout=3600)
            
            if result.returncode == 0:
                self.logger.info("Database backup completed successfully")
            else:
                self.logger.error(f"Database backup failed: {result.stderr}")
        except Exception as e:
            self.logger.error(f"Database backup error: {e}")
    
    def backup_config(self):
        """配置文件备份"""
        self.logger.info("Starting configuration backup")
        try:
            result = subprocess.run([
                '/usr/local/bin/superset-config-backup.sh'
            ], capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                self.logger.info("Configuration backup completed successfully")
            else:
                self.logger.error(f"Configuration backup failed: {result.stderr}")
        except Exception as e:
            self.logger.error(f"Configuration backup error: {e}")
    
    def backup_content(self):
        """用户内容备份"""
        self.logger.info("Starting content backup")
        try:
            result = subprocess.run([
                '/usr/local/bin/superset-content-backup.sh'
            ], capture_output=True, text=True, timeout=1800)
            
            if result.returncode == 0:
                self.logger.info("Content backup completed successfully")
            else:
                self.logger.error(f"Content backup failed: {result.stderr}")
        except Exception as e:
            self.logger.error(f"Content backup error: {e}")
    
    def backup_cache(self):
        """缓存备份"""
        self.logger.info("Starting cache backup")
        try:
            result = subprocess.run([
                '/usr/local/bin/superset-cache-backup.sh'
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.logger.info("Cache backup completed successfully")
            else:
                self.logger.error(f"Cache backup failed: {result.stderr}")
        except Exception as e:
            self.logger.error(f"Cache backup error: {e}")
    
    def run_scheduler(self):
        """运行调度器"""
        self.schedule_backups()
        self.logger.info("Backup scheduler started")
        
        while True:
            schedule.run_pending()
            time.sleep(60)

# 启动备份调度器
if __name__ == "__main__":
    scheduler = BackupScheduler()
    scheduler.run_scheduler()
```

### 备份配置文件

```yaml
# /etc/superset/backup_config.yaml
# 备份配置文件

# 数据库配置
database:
  type: mysql
  host: localhost
  port: 3306
  name: superset
  user: superset_backup
  password: your_secure_password
  backup_dir: /backup/superset/database
  retention_days: 7

# 配置文件配置
config:
  dirs:
    - /etc/superset
    - /home/superset/config
  backup_dir: /backup/superset/config
  retention_days: 30

# 用户内容配置
content:
  dirs:
    - /var/lib/superset/uploads
    - /var/lib/superset/export
  backup_dir: /backup/superset/content
  retention_days: 15

# 缓存配置
cache:
  type: redis
  host: localhost
  port: 6379
  backup_dir: /backup/superset/cache
  retention_days: 7

# 通知配置
notifications:
  email:
    enabled: true
    smtp_server: smtp.example.com
    smtp_port: 587
    username: backup@example.com
    password: email_password
    recipients:
      - admin@example.com
      - ops@example.com
  slack:
    enabled: true
    webhook_url: https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

## 13.6 异地备份策略

### 云存储备份

```python
# AWS S3 备份脚本
import boto3
import os
from datetime import datetime

class S3Backup:
    """AWS S3 备份"""
    
    def __init__(self, bucket_name, aws_access_key, aws_secret_key, region='us-east-1'):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )
    
    def upload_backup(self, local_file_path, remote_path=None):
        """上传备份文件到 S3"""
        if remote_path is None:
            filename = os.path.basename(local_file_path)
            date_prefix = datetime.now().strftime('%Y/%m/%d')
            remote_path = f"superset-backups/{date_prefix}/{filename}"
        
        try:
            self.s3_client.upload_file(local_file_path, self.bucket_name, remote_path)
            print(f"Successfully uploaded {local_file_path} to s3://{self.bucket_name}/{remote_path}")
            return True
        except Exception as e:
            print(f"Failed to upload {local_file_path}: {e}")
            return False
    
    def sync_local_backups(self, local_backup_dir):
        """同步本地备份到 S3"""
        for root, dirs, files in os.walk(local_backup_dir):
            for file in files:
                if file.endswith(('.sql.gz', '.tar.gz', '.rdb.gz')):
                    local_file_path = os.path.join(root, file)
                    self.upload_backup(local_file_path)

# Azure Blob Storage 备份
from azure.storage.blob import BlobServiceClient

class AzureBackup:
    """Azure Blob Storage 备份"""
    
    def __init__(self, connection_string, container_name):
        self.container_name = container_name
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    
    def upload_backup(self, local_file_path, blob_name=None):
        """上传备份文件到 Azure Blob Storage"""
        if blob_name is None:
            filename = os.path.basename(local_file_path)
            date_prefix = datetime.now().strftime('%Y/%m/%d')
            blob_name = f"superset-backups/{date_prefix}/{filename}"
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, 
                blob=blob_name
            )
            
            with open(local_file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            
            print(f"Successfully uploaded {local_file_path} to Azure Blob Storage")
            return True
        except Exception as e:
            print(f"Failed to upload {local_file_path}: {e}")
            return False

# Google Cloud Storage 备份
from google.cloud import storage

class GCSBackup:
    """Google Cloud Storage 备份"""
    
    def __init__(self, bucket_name, credentials_path=None):
        if credentials_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        self.bucket_name = bucket_name
        self.storage_client = storage.Client()
    
    def upload_backup(self, local_file_path, blob_name=None):
        """上传备份文件到 GCS"""
        if blob_name is None:
            filename = os.path.basename(local_file_path)
            date_prefix = datetime.now().strftime('%Y/%m/%d')
            blob_name = f"superset-backups/{date_prefix}/{filename}"
        
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(local_file_path)
            
            print(f"Successfully uploaded {local_file_path} to GCS")
            return True
        except Exception as e:
            print(f"Failed to upload {local_file_path}: {e}")
            return False
```

### 多地域备份策略

```python
# 多地域备份管理器
class MultiRegionBackupManager:
    """多地域备份管理器"""
    
    def __init__(self, config):
        self.config = config
        self.backup_destinations = []
        self.initialize_destinations()
    
    def initialize_destinations(self):
        """初始化备份目的地"""
        # AWS S3 存储桶（主区域）
        if 'aws_s3' in self.config:
            self.backup_destinations.append({
                'name': 'aws_primary',
                'type': 's3',
                'client': S3Backup(**self.config['aws_s3']),
                'priority': 1
            })
        
        # Azure Blob Storage（备选区域）
        if 'azure_blob' in self.config:
            self.backup_destinations.append({
                'name': 'azure_secondary',
                'type': 'azure',
                'client': AzureBackup(**self.config['azure_blob']),
                'priority': 2
            })
        
        # Google Cloud Storage（备选区域）
        if 'gcs' in self.config:
            self.backup_destinations.append({
                'name': 'gcs_tertiary',
                'type': 'gcs',
                'client': GCSBackup(**self.config['gcs']),
                'priority': 3
            })
    
    def backup_to_all_destinations(self, local_file_path):
        """备份到所有目的地"""
        success_count = 0
        total_destinations = len(self.backup_destinations)
        
        for destination in self.backup_destinations:
            try:
                client = destination['client']
                if client.upload_backup(local_file_path):
                    success_count += 1
                    print(f"Backup to {destination['name']} successful")
                else:
                    print(f"Backup to {destination['name']} failed")
            except Exception as e:
                print(f"Error backing up to {destination['name']}: {e}")
        
        print(f"Backup completed: {success_count}/{total_destinations} destinations successful")
        return success_count == total_destinations
    
    def backup_to_priority_destinations(self, local_file_path, max_priority=2):
        """备份到指定优先级的目的地"""
        success_count = 0
        
        for destination in self.backup_destinations:
            if destination['priority'] <= max_priority:
                try:
                    client = destination['client']
                    if client.upload_backup(local_file_path):
                        success_count += 1
                        print(f"Backup to {destination['name']} successful")
                    else:
                        print(f"Backup to {destination['name']} failed")
                except Exception as e:
                    print(f"Error backing up to {destination['name']}: {e}")
        
        return success_count > 0

# 配置示例
MULTI_REGION_CONFIG = {
    'aws_s3': {
        'bucket_name': 'superset-backups-primary',
        'aws_access_key': 'YOUR_AWS_ACCESS_KEY',
        'aws_secret_key': 'YOUR_AWS_SECRET_KEY',
        'region': 'us-east-1'
    },
    'azure_blob': {
        'connection_string': 'YOUR_AZURE_CONNECTION_STRING',
        'container_name': 'superset-backups-secondary'
    },
    'gcs': {
        'bucket_name': 'superset-backups-tertiary',
        'credentials_path': '/path/to/gcs-credentials.json'
    }
}
```

## 13.7 恢复策略与流程

### 恢复前检查清单

```markdown
# 恢复前检查清单

## 系统状态确认
- [ ] 确认当前系统状态（正常/故障/维护）
- [ ] 确认备份文件的完整性和可用性
- [ ] 确认目标环境的兼容性
- [ ] 确认有足够的存储空间
- [ ] 确认网络连接正常

## 依赖服务检查
- [ ] 数据库服务状态
- [ ] 缓存服务状态
- [ ] 文件系统权限
- [ ] 必要的服务进程状态

## 恢复风险评估
- [ ] 影响范围评估
- [ ] 恢复时间估算
- [ ] 回滚计划确认
- [ ] 通知相关人员
```

### 数据库恢复流程

```bash
#!/bin/bash
# 数据库恢复脚本

# 配置变量
DB_HOST="localhost"
DB_PORT="3306"
DB_NAME="superset"
DB_USER="superset_admin"
DB_PASS="your_secure_password"
BACKUP_FILE="/backup/superset/database/superset_20231201_120000.sql.gz"

# 恢复前检查
echo "Checking backup file..."
if [ ! -f "${BACKUP_FILE}" ]; then
    echo "Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

# 确认恢复操作
echo "WARNING: This will overwrite the current database!"
echo "Backup file: ${BACKUP_FILE}"
read -p "Continue with recovery? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Recovery cancelled"
    exit 0
fi

# 停止 Superset 服务
echo "Stopping Superset services..."
sudo systemctl stop superset-web
sudo systemctl stop superset-worker
sudo systemctl stop superset-beat

# 备份当前数据库（可选）
echo "Creating current database backup..."
CURRENT_BACKUP="/tmp/${DB_NAME}_before_recovery_$(date +%Y%m%d_%H%M%S).sql"
mysqldump \
  --host=${DB_HOST} \
  --port=${DB_PORT} \
  --user=${DB_USER} \
  --password=${DB_PASS} \
  ${DB_NAME} > ${CURRENT_BACKUP}
echo "Current database backed up to: ${CURRENT_BACKUP}"

# 解压备份文件
echo "Extracting backup file..."
gunzip -c ${BACKUP_FILE} > /tmp/restore_temp.sql

# 恢复数据库
echo "Restoring database..."
mysql \
  --host=${DB_HOST} \
  --port=${DB_PORT} \
  --user=${DB_USER} \
  --password=${DB_PASS} \
  ${DB_NAME} < /tmp/restore_temp.sql

# 检查恢复结果
if [ $? -eq 0 ]; then
    echo "Database recovery successful"
    
    # 清理临时文件
    rm /tmp/restore_temp.sql
    
    # 启动 Superset 服务
    echo "Starting Superset services..."
    sudo systemctl start superset-web
    sudo systemctl start superset-worker
    sudo systemctl start superset-beat
    
    echo "Recovery completed successfully"
else
    echo "Database recovery failed!"
    exit 1
fi
```

### 配置文件恢复

```bash
#!/bin/bash
# 配置文件恢复脚本

# 配置变量
BACKUP_FILE="/backup/superset/config/config_20231201_030000.tar.gz"
CONFIG_TARGET="/etc/superset"

# 恢复前检查
echo "Checking backup file..."
if [ ! -f "${BACKUP_FILE}" ]; then
    echo "Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

# 确认恢复操作
echo "WARNING: This will overwrite current configuration files!"
echo "Backup file: ${BACKUP_FILE}"
read -p "Continue with recovery? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Recovery cancelled"
    exit 0
fi

# 备份当前配置（可选）
echo "Creating current configuration backup..."
CURRENT_BACKUP="/tmp/config_before_recovery_$(date +%Y%m%d_%H%M%S).tar.gz"
tar -czf ${CURRENT_BACKUP} ${CONFIG_TARGET}
echo "Current configuration backed up to: ${CURRENT_BACKUP}"

# 停止相关服务
echo "Stopping related services..."
sudo systemctl stop superset-web

# 恢复配置文件
echo "Restoring configuration files..."
tar -xzf ${BACKUP_FILE} -C /

# 检查恢复结果
if [ $? -eq 0 ]; then
    echo "Configuration recovery successful"
    
    # 重启服务
    echo "Restarting services..."
    sudo systemctl start superset-web
    
    echo "Configuration recovery completed successfully"
else
    echo "Configuration recovery failed!"
    exit 1
fi
```

## 13.8 灾难恢复演练

### 演练计划模板

```markdown
# 灾难恢复演练计划

## 演练目标
- 验证备份数据的完整性和可用性
- 测试恢复流程的有效性
- 评估恢复时间目标(RTO)和恢复点目标(RPO)
- 提升团队应急响应能力

## 演练场景
1. **数据库故障恢复**：模拟数据库服务器宕机
2. **配置文件损坏**：模拟配置文件意外删除或损坏
3. **完全系统重建**：模拟整个系统需要重新部署

## 演练步骤

### 场景1：数据库故障恢复
1. 停止数据库服务
2. 执行数据库恢复流程
3. 验证数据完整性
4. 重新启动应用服务
5. 验证应用功能

### 场景2：配置文件损坏
1. 删除关键配置文件
2. 执行配置文件恢复流程
3. 验证配置正确性
4. 重启相关服务
5. 验证服务功能

### 场景3：完全系统重建
1. 准备新的服务器环境
2. 安装必要的软件包
3. 恢复配置文件
4. 恢复数据库
5. 恢复用户内容
6. 验证整体系统功能

## 成功标准
- 恢复时间不超过RTO目标
- 数据丢失不超过RPO目标
- 系统功能恢复正常
- 用户数据完整性得到保证

## 演练记录
| 时间 | 场景 | 负责人 | 开始时间 | 结束时间 | 耗时 | 结果 | 备注 |
|------|------|--------|----------|----------|------|------|------|
|      |      |        |          |          |      |      |      |
```

### 演练自动化脚本

```python
# 灾难恢复演练自动化工具
import unittest
import subprocess
import time
import requests
from datetime import datetime

class DisasterRecoveryTest(unittest.TestCase):
    """灾难恢复演练测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.start_time = datetime.now()
        print(f"Starting disaster recovery test at {self.start_time}")
    
    def tearDown(self):
        """测试后清理"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        print(f"Test completed at {end_time}, duration: {duration}")
    
    def test_database_recovery(self):
        """测试数据库恢复"""
        print("Testing database recovery...")
        
        # 1. 停止数据库服务
        result = subprocess.run(['sudo', 'systemctl', 'stop', 'mysql'], 
                              capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, "Failed to stop database service")
        
        # 2. 执行恢复脚本
        result = subprocess.run(['/usr/local/bin/superset-db-restore.sh'], 
                              capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, "Database recovery failed")
        
        # 3. 验证数据库连接
        import mysql.connector
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='superset',
                password='password',
                database='superset'
            )
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM ab_user")
            count = cursor.fetchone()[0]
            self.assertGreater(count, 0, "No users found in restored database")
            conn.close()
        except Exception as e:
            self.fail(f"Database connection test failed: {e}")
        
        print("Database recovery test passed")
    
    def test_application_functionality(self):
        """测试应用功能"""
        print("Testing application functionality...")
        
        # 等待应用启动
        time.sleep(30)
        
        # 检查应用健康状态
        try:
            response = requests.get('http://localhost:8088/health')
            self.assertEqual(response.status_code, 200, 
                           "Application health check failed")
        except Exception as e:
            self.fail(f"Application health check failed: {e}")
        
        # 检查登录页面
        try:
            response = requests.get('http://localhost:8088/login/')
            self.assertIn('Login', response.text, 
                         "Login page not accessible")
        except Exception as e:
            self.fail(f"Login page test failed: {e}")
        
        print("Application functionality test passed")
    
    def test_data_integrity(self):
        """测试数据完整性"""
        print("Testing data integrity...")
        
        # 这里可以添加更多具体的数据完整性检查
        # 例如检查特定用户的仪表板是否存在等
        
        print("Data integrity test passed")

def run_disaster_recovery_drill():
    """运行灾难恢复演练"""
    print("Starting disaster recovery drill...")
    
    # 创建测试套件
    suite = unittest.TestSuite()
    suite.addTest(DisasterRecoveryTest('test_database_recovery'))
    suite.addTest(DisasterRecoveryTest('test_application_functionality'))
    suite.addTest(DisasterRecoveryTest('test_data_integrity'))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果
    if result.wasSuccessful():
        print("All disaster recovery tests passed!")
        return True
    else:
        print("Some disaster recovery tests failed!")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        return False

if __name__ == "__main__":
    success = run_disaster_recovery_drill()
    exit(0 if success else 1)
```

## 13.9 监控与告警

### 备份状态监控

```python
# 备份状态监控
import os
import time
from datetime import datetime, timedelta

class BackupMonitor:
    """备份状态监控器"""
    
    def __init__(self, backup_dirs, expected_intervals):
        self.backup_dirs = backup_dirs
        self.expected_intervals = expected_intervals  # 期望的时间间隔（小时）
    
    def check_backup_status(self):
        """检查备份状态"""
        status_report = {}
        
        for backup_type, backup_dir in self.backup_dirs.items():
            status_report[backup_type] = self.check_single_backup(
                backup_type, backup_dir
            )
        
        return status_report
    
    def check_single_backup(self, backup_type, backup_dir):
        """检查单个备份类型的状态"""
        if not os.path.exists(backup_dir):
            return {
                'status': 'error',
                'message': f'Backup directory not found: {backup_dir}',
                'last_backup': None
            }
        
        # 查找最新的备份文件
        latest_backup = self.find_latest_backup(backup_dir)
        
        if not latest_backup:
            return {
                'status': 'error',
                'message': 'No backup files found',
                'last_backup': None
            }
        
        # 检查备份时间
        backup_time = datetime.fromtimestamp(os.path.getctime(latest_backup))
        time_since_backup = datetime.now() - backup_time
        
        # 根据期望间隔判断状态
        expected_interval = self.expected_intervals.get(backup_type, 24)  # 默认24小时
        warning_threshold = expected_interval * 1.5  # 警告阈值
        error_threshold = expected_interval * 2      # 错误阈值
        
        if time_since_backup.total_seconds() > error_threshold * 3600:
            status = 'error'
            message = f'Backup is {time_since_backup.days} days old (expected: {expected_interval}h)'
        elif time_since_backup.total_seconds() > warning_threshold * 3600:
            status = 'warning'
            message = f'Backup is {time_since_backup.days} days old (expected: {expected_interval}h)'
        else:
            status = 'ok'
            message = f'Backup is current ({time_since_backup.days} days old)'
        
        return {
            'status': status,
            'message': message,
            'last_backup': backup_time.isoformat(),
            'backup_file': latest_backup
        }
    
    def find_latest_backup(self, backup_dir):
        """查找最新的备份文件"""
        backup_files = []
        
        for root, dirs, files in os.walk(backup_dir):
            for file in files:
                if file.endswith(('.sql.gz', '.tar.gz', '.rdb.gz')):
                    file_path = os.path.join(root, file)
                    backup_files.append(file_path)
        
        if not backup_files:
            return None
        
        # 返回最新的文件
        return max(backup_files, key=os.path.getctime)
    
    def generate_report(self):
        """生成备份状态报告"""
        status = self.check_backup_status()
        
        report = "=== Backup Status Report ===\n"
        report += f"Generated at: {datetime.now().isoformat()}\n\n"
        
        for backup_type, info in status.items():
            report += f"{backup_type.upper()} BACKUP:\n"
            report += f"  Status: {info['status']}\n"
            report += f"  Message: {info['message']}\n"
            if info['last_backup']:
                report += f"  Last Backup: {info['last_backup']}\n"
            report += "\n"
        
        return report

# 使用示例
BACKUP_DIRS = {
    'database': '/backup/superset/database',
    'config': '/backup/superset/config',
    'content': '/backup/superset/content',
    'cache': '/backup/superset/cache'
}

EXPECTED_INTERVALS = {
    'database': 24,   # 每24小时
    'config': 168,    # 每周
    'content': 24,    # 每24小时
    'cache': 1        # 每小时
}

monitor = BackupMonitor(BACKUP_DIRS, EXPECTED_INTERVALS)
print(monitor.generate_report())
```

### 告警通知

```python
# 告警通知系统
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class AlertNotifier:
    """告警通知器"""
    
    def __init__(self, config):
        self.config = config
    
    def send_email_alert(self, subject, message, recipients=None):
        """发送邮件告警"""
        if not self.config.get('email', {}).get('enabled', False):
            return
        
        email_config = self.config['email']
        recipients = recipients or email_config.get('recipients', [])
        
        if not recipients:
            print("No recipients configured for email alerts")
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = email_config['username']
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            server.send_message(msg)
            server.quit()
            
            print(f"Email alert sent to {', '.join(recipients)}")
        except Exception as e:
            print(f"Failed to send email alert: {e}")
    
    def send_slack_alert(self, message):
        """发送 Slack 告警"""
        if not self.config.get('slack', {}).get('enabled', False):
            return
        
        slack_config = self.config['slack']
        
        try:
            payload = {
                'text': message,
                'username': 'Superset Backup Monitor',
                'icon_emoji': ':warning:'
            }
            
            response = requests.post(slack_config['webhook_url'], json=payload)
            if response.status_code == 200:
                print("Slack alert sent successfully")
            else:
                print(f"Failed to send Slack alert: {response.text}")
        except Exception as e:
            print(f"Failed to send Slack alert: {e}")
    
    def send_alert(self, alert_type, message, severity='warning'):
        """发送告警"""
        subject = f"[{severity.upper()}] Superset Backup Alert - {alert_type}"
        
        # 发送邮件
        self.send_email_alert(subject, message)
        
        # 发送 Slack 通知
        slack_message = f"*{subject}*\n{message}"
        self.send_slack_alert(slack_message)

# 告警配置
ALERT_CONFIG = {
    'email': {
        'enabled': True,
        'smtp_server': 'smtp.example.com',
        'smtp_port': 587,
        'username': 'backup@example.com',
        'password': 'your_email_password',
        'recipients': ['admin@example.com', 'ops@example.com']
    },
    'slack': {
        'enabled': True,
        'webhook_url': 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
    }
}

# 集成监控和告警
def monitor_and_alert():
    """监控并发送告警"""
    monitor = BackupMonitor(BACKUP_DIRS, EXPECTED_INTERVALS)
    notifier = AlertNotifier(ALERT_CONFIG)
    
    status = monitor.check_backup_status()
    
    for backup_type, info in status.items():
        if info['status'] in ['warning', 'error']:
            alert_message = f"""
Backup Alert for {backup_type.upper()}

Status: {info['status']}
Message: {info['message']}
Last Backup: {info.get('last_backup', 'Unknown')}
Backup Directory: {BACKUP_DIRS[backup_type]}

Please check the backup system immediately.
            """
            notifier.send_alert(f'{backup_type}_backup', alert_message, info['status'])

# 定期运行监控
if __name__ == "__main__":
    import schedule
    import time
    
    # 每小时检查一次
    schedule.every().hour.do(monitor_and_alert)
    
    while True:
        schedule.run_pending()
        time.sleep(60)
```

## 13.10 最佳实践总结

### 备份策略建议

1. **制定完整的备份计划**：
   - 明确备份内容和优先级
   - 设定合理的备份频率
   - 制定异地备份策略

2. **定期测试恢复流程**：
   - 每季度进行一次完整的恢复演练
   - 验证备份数据的完整性和可用性
   - 优化恢复流程，减少恢复时间

3. **实施监控和告警**：
   - 实时监控备份状态
   - 设置合理的告警阈值
   - 及时响应备份异常

4. **文档化所有流程**：
   - 详细的备份操作手册
   - 完整的恢复流程文档
   - 定期更新文档内容

### 关键要点回顾

- 采用 3-2-1 备份原则确保数据安全
- 区分不同类型数据的备份策略
- 实施自动化备份减少人工干预
- 建立异地备份机制防范区域性灾难
- 定期演练恢复流程验证有效性
- 建立监控告警机制及时发现问题

## 13.11 小结

本章详细介绍了 Apache Superset 的备份与恢复策略，涵盖了数据库备份、文件系统备份、自动化备份方案、异地备份策略、恢复流程、灾难恢复演练以及监控告警等多个方面。通过建立完善的备份与恢复体系，可以有效保障 Superset 系统的数据安全和业务连续性。

在下一章中，我们将探讨 Apache Superset 的容器化部署方案。