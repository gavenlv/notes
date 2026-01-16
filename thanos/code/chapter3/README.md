# 第3章代码示例：与Prometheus集成

## 目录结构

```
chapter3/
├── README.md                 # 本章说明文档
├── sidecar-config/           # Sidecar配置
│   ├── sidecar-config.yaml
│   ├── start-sidecar.sh
│   └── monitor-sidecar.sh
├── query-config/             # Query配置
│   ├── query-config.yaml
│   ├── start-query.sh
│   └── query-test.sh
├── storage-config/           # 存储配置
│   ├── minio-bucket.yaml
│   ├── s3-bucket.yaml
│   └── gcs-bucket.yaml
├── verification/             # 验证脚本
│   ├── verify-upload.sh
│   ├── verify-query.sh
│   └── verify-consistency.sh
└── advanced/                 # 高级配置
    ├── multi-cluster/
    ├── tls-config/
    └── high-availability/
```

## 代码示例说明

### 1. Sidecar配置
Thanos Sidecar与Prometheus集成的完整配置：
- **sidecar-config.yaml**: Sidecar详细配置
- **start-sidecar.sh**: Sidecar启动脚本
- **monitor-sidecar.sh**: Sidecar监控脚本

### 2. Query配置
Query组件的配置和测试：
- **query-config.yaml**: Query详细配置
- **start-query.sh**: Query启动脚本
- **query-test.sh**: 查询功能测试脚本

### 3. 存储配置
多种对象存储的配置模板：
- **minio-bucket.yaml**: MinIO配置
- **s3-bucket.yaml**: AWS S3配置
- **gcs-bucket.yaml**: Google Cloud Storage配置

### 4. 验证脚本
集成后的验证和监控：
- 数据上传验证
- 查询功能验证
- 数据一致性验证

### 5. 高级配置
生产环境的高级配置示例：
- 多集群集成
- TLS安全配置
- 高可用性配置

## 使用说明

### 基础集成配置
```bash
# 配置Sidecar
cd sidecar-config
chmod +x *.sh
./start-sidecar.sh

# 配置Query
cd ../query-config
chmod +x *.sh
./start-query.sh
```

### 存储配置
根据实际环境选择对应的存储配置文件：
- 开发环境：使用minio-bucket.yaml
- 生产环境：使用s3-bucket.yaml或gcs-bucket.yaml

### 验证集成
```bash
cd verification
chmod +x *.sh
./verify-upload.sh    # 验证数据上传
./verify-query.sh     # 验证查询功能
./verify-consistency.sh  # 验证数据一致性
```

## 注意事项

- Sidecar必须与Prometheus实例部署在同一主机或网络可达
- 对象存储配置需要正确的访问凭证
- 生产环境建议启用TLS加密
- 多集群集成需要合理规划网络和标签配置