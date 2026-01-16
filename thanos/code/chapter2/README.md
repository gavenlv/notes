# 第2章代码示例：单机环境安装和配置

## 目录结构

```
chapter2/
├── README.md                 # 本章说明文档
├── docker-compose/           # Docker Compose部署
│   ├── docker-compose.yml
│   ├── config/
│   │   ├── prometheus.yml
│   │   └── minio-bucket.yaml
│   └── scripts/
│       ├── deploy.sh
│       └── cleanup.sh
├── binary-install/           # 二进制安装
│   ├── install-scripts/
│   │   ├── install-thanos.sh
│   │   └── install-prometheus.sh
│   └── configs/
│       ├── thanos-sidecar.service
│       └── thanos-query.service
└── verification/             # 验证脚本
    ├── verify-services.sh
    ├── verify-data-upload.sh
    └── monitor-resources.sh
```

## 代码示例说明

### 1. Docker Compose部署
完整的容器化部署方案，包含：
- **docker-compose.yml**: 服务编排文件
- **config/**: 各组件配置文件
- **scripts/**: 部署和清理脚本

### 2. 二进制安装
传统二进制安装方式，包含：
- **install-scripts/**: 自动化安装脚本
- **configs/**: systemd服务配置文件

### 3. 验证脚本
部署后的验证和监控脚本：
- 服务状态检查
- 数据上传验证
- 资源使用监控

## 使用说明

### Docker Compose方式（推荐）
```bash
cd docker-compose
chmod +x scripts/*.sh
./scripts/deploy.sh
```

### 二进制安装方式
```bash
cd binary-install
chmod +x install-scripts/*.sh
./install-scripts/install-thanos.sh
```

### 验证部署
```bash
cd verification
chmod +x *.sh
./verify-services.sh
```

## 注意事项

- Docker方式需要先安装Docker和Docker Compose
- 二进制方式需要手动下载Thanos二进制文件
- 所有配置文件需要根据实际环境修改
- 生产环境建议使用Docker方式部署