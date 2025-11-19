# 第1章：BIRT基础介绍与环境搭建

## 1.1 BIRT概述

### 1.1.1 什么是BIRT？

BIRT（Business Intelligence and Reporting Tools）是一个开源的报表系统，主要用于基于Web的应用程序中。它由Eclipse基金会维护，是基于Eclipse平台的开源项目。

BIRT的核心功能包括：
- 数据访问和操作
- 报表设计和生成
- 图表和可视化
- 报表部署和集成

### 1.1.2 BIRT的发展历史

BIRT最初由Actuate公司开发，于2004年捐赠给Eclipse基金会。经过多年发展，BIRT已经成为企业级报表开发的重要工具之一。

主要版本里程碑：
- **2004年**：BIRT项目启动，发布1.0版本
- **2007年**：发布BIRT 2.0，引入更多图表类型和数据源支持
- **2010年**：BIRT 2.5发布，增强Web集成能力
- **2014年**：BIRT 4.3发布，改进UI和性能
- **2017年**：BIRT 4.7发布，支持更多现代Web技术
- **2020年**：BIRT 4.8发布，增强云部署和移动支持
- **2022年**：BIRT 4.9发布，更新依赖库和安全补丁

### 1.1.3 BIRT的核心组件

BIRT由以下几个核心组件构成：

1. **报表设计器**：基于Eclipse的可视化设计工具
2. **报表引擎**：用于处理和生成报表的运行时引擎
3. **图表引擎**：专门处理图表生成的组件
4. **查看器**：用于展示报表的Web组件

### 1.1.4 BIRT的应用场景

BIRT适用于多种业务场景：

- **企业报表**：财务报表、销售报表、库存报表等
- **数据分析**：趋势分析、对比分析、多维分析
- **仪表板**：KPI展示、实时监控面板
- **发票和票据**：格式化输出、批量生成
- **标签和条码**：产品标签、物流标签、资产标签
- **证书和证件**：员工证书、培训证书、资格证件

## 1.2 BIRT的架构

### 1.2.1 整体架构

BIRT采用分层架构设计，从上到下包括：

1. **表示层**：报表查看器和设计器界面
2. **业务逻辑层**：报表引擎和图表引擎
3. **数据访问层**：数据源连接器和ODA（Open Data Access）框架
4. **集成层**：与Java EE、Spring等框架的集成接口

### 1.2.2 ODA框架

ODA（Open Data Access）是BIRT的数据访问框架，它提供了统一的接口来访问各种数据源：

- JDBC数据源：关系型数据库
- XML数据源：XML文件
- Web服务数据源：REST/SOAP服务
- 平面文件数据源：CSV、Excel等
- 自定义数据源：通过扩展实现

### 1.2.3 报表生命周期

报表的完整生命周期包括：

1. **设计阶段**：创建报表布局和数据绑定
2. **预览阶段**：在设计器中查看报表效果
3. **生成阶段**：报表引擎处理报表定义
4. **渲染阶段**：将报表输出为HTML、PDF等格式
5. **交互阶段**：用户通过查看器与报表交互

## 1.3 环境搭建

### 1.3.1 系统要求

在开始之前，请确保您的系统满足以下要求：

**硬件要求：**
- CPU：双核2.0GHz以上
- 内存：4GB以上（推荐8GB）
- 硬盘：至少2GB可用空间

**软件要求：**
- 操作系统：Windows、Linux或macOS
- Java：JDK 8或更高版本（推荐JDK 11）
- 浏览器：Chrome、Firefox、Edge或Safari（最新版本）
- 数据库：任意JDBC兼容数据库（用于示例）

### 1.3.2 下载和安装BIRT

#### 步骤1：下载Java开发环境

首先确保您的系统已安装JDK。可以通过以下命令检查：

```bash
java -version
```

如果未安装，请从Oracle官网或OpenJDK下载并安装JDK。

#### 步骤2：下载Eclipse IDE

BIRT基于Eclipse平台，推荐使用Eclipse IDE for Enterprise Java Developers。

1. 访问Eclipse官网：https://www.eclipse.org/downloads/
2. 下载适合您系统的Eclipse IDE for Enterprise Java Developers
3. 解压到本地目录
4. 运行eclipse.exe（Windows）或eclipse（Linux/macOS）

#### 步骤3：安装BIRT插件

有两种方式安装BIRT插件：

**方法一：通过Eclipse Marketplace**

1. 启动Eclipse
2. 点击菜单：Help → Eclipse Marketplace...
3. 搜索"BIRT"
4. 点击"Install"安装"BIRT Project"

**方法二：通过更新站点**

1. 启动Eclipse
2. 点击菜单：Help → Install New Software...
3. 点击"Add"添加更新站点：
   - Name: BIRT
   - Location: https://download.eclipse.org/birt/update-site/4.9/
4. 选择"BIRT Framework"和"BIRT Chart Engine"
5. 点击"Next"并接受许可协议完成安装

### 1.3.3 配置BIRT

安装完成后，需要配置BIRT以确保正常运行：

1. **重启Eclipse**：安装完成后重启Eclipse
2. **切换到BIRT透视图**：Window → Perspective → Open Perspective → Other... → Report Design
3. **验证安装**：File → New → Report，看是否能创建新报表

### 1.3.4 下载示例数据库

为了学习方便，我们将使用经典的电影租赁数据库作为示例：

1. 下载示例数据库脚本
2. 创建数据库并导入数据
3. 配置JDBC连接

## 1.4 创建第一个BIRT报表

### 1.4.1 创建报表项目

让我们开始创建第一个BIRT报表：

1. 启动Eclipse并切换到BIRT透视图
2. 创建新项目：File → New → Project...
3. 选择"Report Project"，点击"Next"
4. 输入项目名称"MyFirstBIRT"，点击"Finish"

### 1.4.2 创建数据源

数据源是BIRT报表的数据基础：

1. 右键项目，选择New → Data Source
2. 选择"JDBC Data Source"，点击"Next"
3. 输入数据源名称，如"MovieRentalDS"
4. 配置数据库连接信息：
   - Driver Class: 根据您的数据库选择
   - URL: 数据库连接URL
   - User Name: 用户名
   - Password: 密码
5. 点击"Test Connection"测试连接
6. 点击"Finish"保存数据源

### 1.4.3 创建数据集

数据集定义了从数据源中获取哪些数据：

1. 右键数据源，选择New → Data Set
2. 输入数据集名称，如"MoviesList"
3. 选择"SQL Select Query"作为查询类型
4. 编写SQL查询语句，例如：
   ```sql
   SELECT movie_id, title, release_year, rating 
   FROM movies 
   ORDER BY release_year DESC
   ```
5. 点击"Finish"保存数据集
6. 在预览窗口查看数据

### 1.4.4 设计报表布局

现在我们来设计报表的基本布局：

1. 创建新报表：File → New → Report
2. 输入报表名称"MovieListReport"，点击"Finish"
3. 从"Data Explorer"视图拖动数据集到报表
4. 在布局编辑器中设计报表结构：
   - 添加报表标题
   - 添加表格显示电影列表
   - 设置表格样式

### 1.4.5 预览和运行报表

完成设计后，可以预览报表效果：

1. 点击报表编辑器底部的"Preview"标签
2. 查看生成的报表效果
3. 如果需要调整，返回设计视图修改

## 1.5 BIRT与Eclipse集成

### 1.5.1 BIRT透视图

BIRT提供了专门的透视图，包含以下视图：

- **Report Design**：报表设计编辑器
- **Data Explorer**：数据源和数据集管理
- **Palette**：可用组件拖放面板
- **Property Editor**：属性编辑器
- **Outline**：报表结构大纲
- **Preview**：报表预览窗口

### 1.5.2 常用工具栏

BIRT透视图中的常用工具栏按钮：

- **New Report**：创建新报表
- **New Data Source**：创建新数据源
- **New Data Set**：创建新数据集
- **Preview**：预览报表
- **Save**：保存报表

### 1.5.3 首选项配置

通过Window → Preferences → Report Design可以配置BIRT的默认设置：

- **字体和颜色**：设置默认字体和颜色方案
- **数据源**：配置默认数据源设置
- **预览**：设置预览选项
- **性能**：调整性能相关设置

## 1.6 最佳实践

### 1.6.1 项目组织

良好的项目组织是成功的基础：

1. **命名规范**：使用有意义的名称，如"SalesReport"、"CustomerData"等
2. **目录结构**：按功能模块组织报表和数据源
3. **版本控制**：使用Git等版本控制系统管理项目
4. **文档记录**：为复杂报表编写文档说明

### 1.6.2 环境配置建议

1. **JVM设置**：为大型报表项目增加JVM内存
2. **字体配置**：确保使用支持多语言的字体
3. **编码设置**：统一使用UTF-8编码
4. **定期备份**：定期备份项目文件

### 1.6.3 学习路径建议

对于初学者，建议按以下路径学习：

1. 先掌握基本报表设计
2. 学习数据源和数据集配置
3. 掌握图表和可视化
4. 学习脚本和高级功能
5. 最后研究部署和集成

## 1.7 本章小结

本章介绍了BIRT的基础知识和环境搭建过程。我们学习了：

- BIRT的概念、历史和应用场景
- BIRT的架构和核心组件
- 如何安装和配置BIRT开发环境
- 创建第一个简单报表的完整流程
- BIRT与Eclipse集成的相关知识

通过本章的学习，您应该已经搭建好了BIRT开发环境，并成功创建了第一个报表。在下一章中，我们将深入学习BIRT的数据源和数据集管理，这是报表开发的基础。

## 1.8 实践练习

为了巩固本章知识，请完成以下练习：

1. 安装配置BIRT开发环境
2. 创建一个包含员工信息的数据库表
3. 创建数据源和数据集连接到该表
4. 设计一个简单的员工列表报表
5. 尝试修改报表样式，添加标题和页脚

完成练习后，您将为下一章的学习打下坚实基础。