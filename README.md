# ClickHouse 学习教程 - 从入门到精通

> 一个完整的ClickHouse学习教程，从基础入门到生产实践，帮助您系统掌握ClickHouse的各个方面。

## 🎯 学习目标

通过14天的系统学习，您将掌握：
- ClickHouse的环境搭建和配置
- 核心概念和架构原理  
- 云端集群部署和管理
- 高级查询优化技巧
- 生产环境最佳实践
- 运维监控和故障排除

## 📚 学习路径

### **核心学习路径 (Day 1-3)**
- **Day 1**: 环境搭建与配置 ✅
- **Day 2**: 核心概念与架构原理 ✅  
- **Day 3**: 阿里云集群部署 ✅

### **进阶学习路径 (Day 4-14)**
- **Day 4**: SQL语法和数据类型
- **Day 5**: 表引擎详解
- **Day 6**: 查询优化技巧
- **Day 7**: 数据导入导出
- **Day 8**: 集群管理和分布式
- **Day 9**: 监控和运维
- **Day 10**: 性能优化
- **Day 11**: 安全和权限管理
- **Day 12**: 数据备份恢复
- **Day 13**: 最佳实践
- **Day 14**: 项目实战

## 🗂️ 目录结构

```
day1/                           # Day 1: 环境搭建
├── notes/
│   └── installation.md        # 环境搭建文档
├── code/                       # 安装脚本
│   ├── docker-install.sh      # Docker安装脚本
│   ├── install-native.sh      # 原生安装脚本
│   ├── benchmark.sh           # 性能测试脚本
│   └── check-config.sh        # 配置检查脚本
├── configs/                    # 配置文件模板
│   ├── config.xml             # 主配置文件
│   └── users.xml              # 用户配置文件
└── examples/
    └── quick-start.sql         # 快速开始示例

day2/                           # Day 2: 核心概念
├── notes/
│   └── introduction.md        # 核心概念文档
├── examples/
│   └── basic-queries.sql      # 基础查询示例
└── cheatsheets/
    └── clickhouse-commands.md # 命令速查表

day3/                           # Day 3: 云端部署  
├── notes/
│   └── aliyun-deployment.md   # 阿里云部署文档
└── terraform/                 # Terraform配置
    ├── main.tf                # 主配置文件
    ├── variables.tf           # 变量定义
    ├── outputs.tf             # 输出定义
    ├── user_data.sh           # ClickHouse安装脚本
    ├── zookeeper_user_data.sh # ZooKeeper安装脚本
    ├── setup_aliyun.ps1       # 阿里云配置脚本
    └── generate-ssh-key.ps1   # SSH密钥生成脚本

day4/...day14/                  # 后续学习内容
├── notes/                      # 学习笔记
├── code/                       # 代码示例
├── examples/                   # 实践示例
└── projects/                   # 项目实战
```

## 🚀 快速开始

### 本地学习环境

1. **环境搭建 (Day 1)**
   ```bash
   # Docker方式 (推荐)
   chmod +x day1/code/docker-install.sh
   ./day1/code/docker-install.sh
   
   # 或原生安装
   chmod +x day1/code/install-native.sh  
   ./day1/code/install-native.sh
   ```

2. **验证安装**
   ```bash
   # 运行快速开始示例
   clickhouse-client < day1/examples/quick-start.sql
   
   # 执行配置检查
   chmod +x day1/code/check-config.sh
   ./day1/code/check-config.sh
   ```

### 阿里云集群部署

1. **准备工作**
   - 确保您有阿里云账户和AccessKey
   - AccessKey文件位置：`C:\Users\mingbo\aliyun\AccessKey.csv`

2. **一键部署**
   ```powershell
   # 生成SSH密钥
   .\day3\terraform\generate-ssh-key.ps1
   
   # 部署集群
   .\day3\terraform\setup_aliyun.ps1 -Action apply
   ```

3. **连接集群**
   ```bash
   # 查看连接信息
   terraform output -state=day3/terraform/terraform.tfstate
   
   # SSH连接
   ssh -i day3/terraform/clickhouse_key ubuntu@<public_ip>
   ```

## 🔧 技术特色

- **渐进式学习**: 从环境搭建到生产实践，循序渐进
- **理论实践结合**: 每个概念都有对应的实操练习
- **生产级部署**: 使用Terraform进行云端基础设施管理
- **多平台支持**: Linux、macOS、Windows全平台兼容
- **中文友好**: 全中文教程，适合中文开发者学习

## 📋 学习建议

### 学习顺序建议
1. **必学核心路径**: Day 1-3 (环境→理论→部署)
2. **技能深化**: Day 4-7 (SQL→引擎→优化→数据)
3. **运维进阶**: Day 8-11 (集群→监控→性能→安全)
4. **综合实践**: Day 12-14 (备份→实践→项目)

### 时间安排建议
- **快速入门**: 3天 (Day 1-3)
- **基础掌握**: 1周 (Day 1-7)  
- **全面精通**: 2周 (Day 1-14)

### 学习方式建议
- 每天完成对应的学习内容
- 动手实践所有代码示例
- 理解概念后再进入下一天
- 遇到问题及时查阅文档

## 🛠️ 环境要求

### 系统要求
- **操作系统**: Linux (推荐)、macOS、Windows 10+
- **内存**: 最少2GB，推荐8GB+
- **存储**: 最少10GB可用空间
- **网络**: 稳定的互联网连接

### 软件依赖
- Docker (推荐安装方式)
- 或者 ClickHouse 原生安装
- Terraform (云端部署需要)
- SSH客户端 (远程连接需要)

## 🔒 安全提醒

- 请妥善保管您的阿里云AccessKey
- SSH私钥文件请严格保密
- 生产环境请修改默认密码
- 建议启用防火墙和安全组规则

## 📖 参考资源

- [ClickHouse官方文档](https://clickhouse.com/docs/)
- [ClickHouse中文社区](https://clickhouse.com.cn/)
- [阿里云ECS文档](https://www.alibabacloud.com/help/ecs)
- [Terraform官方文档](https://www.terraform.io/docs/)

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个教程：
- 报告文档错误或不清楚的地方
- 提供更好的代码示例
- 分享您的学习心得和实践经验
- 建议新的学习内容或改进建议

## 📄 许可证

本项目采用 MIT 许可证，详情请参见 [LICENSE](LICENSE) 文件。

---

**开始您的ClickHouse学习之旅吧！** 🎉

*最后更新：2024年*
