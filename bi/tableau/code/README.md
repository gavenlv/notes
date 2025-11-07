# Tableau教程代码示例

本目录包含了Tableau从入门到专家教程中使用的所有代码示例和文件。这些代码按照章节组织，与教程内容相对应。

## 目录结构

```
code/
├── chapter1/                    # 第1章：Tableau基础入门
│   ├── sales-data.xlsx          # 示例销售数据Excel文件
│   └── create-first-dashboard.twb # 第一个仪表盘示例
│
├── chapter2/                    # 第2章：Tableau数据连接与准备
│   └── multiple-datasources.tds  # 多数据源连接示例
│
├── chapter3/                    # 第3章：Tableau可视化基础
│   └── advanced-charts.twb       # 高级图表示例
│
├── chapter4/                    # 第4章：Tableau高级可视化
│   └── calculated-fields.txt     # 计算字段示例
│
├── chapter5/                    # 第5章：Tableau仪表盘与故事
│   └── executive-dashboard.twb   # 执行仪表盘示例
│
├── chapter6/                    # 第6章：Tableau高级分析功能
│   └── trend-analysis.twb       # 趋势分析示例
│
├── chapter7/                    # 第7章：Tableau服务器与共享
│   ├── server-setup.sh          # Linux服务器安装脚本
│   └── user-management.py       # 用户管理脚本
│
├── chapter8/                    # 第8章：Tableau企业级应用
│   └── enterprise-deployment.yaml # Kubernetes企业部署配置
│
└── README.md                    # 本文件
```

## 使用说明

### 文件说明

1. **Excel数据文件** (`.xlsx`)
   - 包含示例销售数据
   - 可直接在Tableau Desktop中连接使用

2. **Tableau工作簿** (`.twb`)
   - 包含可视化示例
   - 可在Tableau Desktop中打开查看和学习

3. **Tableau数据源** (`.tds`)
   - 包含数据源连接配置
   - 可在Tableau Desktop中导入使用

4. **脚本文件** (`.sh`, `.py`)
   - 包含自动化和管理脚本
   - 在命令行环境中执行

5. **配置文件** (`.yaml`, `.txt`)
   - 包含配置和示例代码
   - 根据说明调整后使用

### 数据准备

1. 下载所有代码文件
2. 将Excel文件放在可访问的位置
3. 使用Tableau Desktop打开工作簿文件
4. 根据需要修改脚本文件中的配置

### 环境要求

1. **Tableau Desktop 2023.1或更高版本**
   - 用于打开和编辑工作簿文件
   - 连接数据源和创建可视化

2. **Python 3.6或更高版本** (可选)
   - 用于运行Python管理脚本
   - 安装必要的库：`pip install requests`

3. **Bash环境** (可选)
   - 用于运行服务器安装脚本
   - 支持Linux或WSL环境

4. **Kubernetes集群** (可选)
   - 用于企业级部署配置
   - 需要配置kubectl和集群访问权限

## 代码说明

### Chapter 1: Tableau基础入门

- **sales-data.xlsx**: 包含订单、客户、产品和区域数据的示例Excel文件
- **create-first-dashboard.twb**: 展示如何创建第一个仪表盘的示例工作簿

### Chapter 2: Tableau数据连接与准备

- **multiple-datasources.tds**: 展示如何连接和融合多个数据源的示例

### Chapter 3: Tableau可视化基础

- **advanced-charts.twb**: 包含各种高级图表类型的示例，如双轴图、树状图等

### Chapter 4: Tableau高级可视化

- **calculated-fields.txt**: 包含各种常用计算字段的公式和示例

### Chapter 5: Tableau仪表盘与故事

- **executive-dashboard.twb**: 企业级仪表盘设计示例，展示最佳实践

### Chapter 6: Tableau高级分析功能

- **trend-analysis.twb**: 趋势分析、聚类分析和高级分析功能示例

### Chapter 7: Tableau服务器与共享

- **server-setup.sh**: 在Linux上安装和配置Tableau Server的脚本
- **user-management.py**: 使用REST API管理用户和组的Python脚本

### Chapter 8: Tableau企业级应用

- **enterprise-deployment.yaml**: 在Kubernetes上部署Tableau Server的配置文件

## 常见问题

### Q: 为什么我无法打开.twb或.tds文件？
A: 请确保您已安装Tableau Desktop 2023.1或更高版本。如果使用旧版本，可能不兼容。

### Q: 如何使用Python脚本？
A: 1) 安装Python 3.6或更高版本；2) 安装requests库：`pip install requests`；3) 根据您的Tableau Server信息修改脚本；4) 运行脚本：`python user-management.py`

### Q: 如何执行Shell脚本？
A: 1) 确保在Linux或WSL环境；2) 给脚本添加执行权限：`chmod +x server-setup.sh`；3) 以root权限执行：`sudo ./server-setup.sh`

### Q: Kubernetes部署配置如何使用？
A: 1) 确保已配置kubectl和Kubernetes集群；2) 创建必要的命名空间和密钥；3) 应用配置：`kubectl apply -f enterprise-deployment.yaml`

## 扩展与贡献

这些代码示例旨在配合教程使用，您可以根据实际需求进行修改和扩展。如果您有改进建议或发现问题，欢迎提交反馈。

## 许可证

这些代码示例仅用于学习和非商业用途。请遵循Tableau的许可协议和使用条款。