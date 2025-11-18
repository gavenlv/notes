# Superset二次开发入门与环境搭建

## 1. 开发环境要求

### 1.1 系统要求

Superset开发环境需要以下基础组件：

- **操作系统**：Linux, macOS, 或 Windows (推荐Linux或macOS，Windows可能需要额外配置)
- **Python**：3.9 或 3.10 (不建议使用Python 3.11+，可能存在兼容性问题)
- **Node.js**：16.x LTS 或 18.x LTS (前端开发必需)
- **npm/yarn**：与Node.js版本兼容的包管理器
- **数据库**：
  - PostgreSQL 10+ (首选)
  - MySQL 8.0+ (可选)
  - SQLite (仅开发环境使用)
- **Redis**：用于缓存和任务队列
- **Git**：代码版本控制
- **浏览器**：Chrome, Firefox, Safari 或 Edge 的最新版本

### 1.2 系统资源建议

- **CPU**：至少 4 核心
- **内存**：至少 8GB RAM (推荐 16GB+)
- **磁盘空间**：至少 20GB 可用空间

## 2. 源码获取与安装

### 2.1 从GitHub克隆代码

```bash
# 克隆官方仓库
git clone https://github.com/apache/superset.git
cd superset

# 或者克隆特定分支
git checkout <branch-name>
```

### 2.2 创建虚拟环境

推荐使用Python虚拟环境隔离开发依赖：

```bash
# 使用venv创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate

# 升级pip
pip install --upgrade pip
```

### 2.3 安装后端依赖

```bash
# 安装开发依赖
pip install -e "[development]"

# 安装额外依赖（根据需要）
pip install -e "[postgresql]"  # PostgreSQL支持
pip install -e "[mysql]"        # MySQL支持
```

### 2.4 安装前端依赖

```bash
# 切换到前端目录
cd superset-frontend

# 安装依赖（使用npm或yarn）
npm install
# 或者
yarn install

# 回到根目录
cd ..
```

## 3. 开发环境配置

### 3.1 数据库配置

#### 3.1.1 PostgreSQL配置（推荐）

1. **创建数据库和用户**:

```bash
# 连接到PostgreSQL
psql postgres

# 创建用户和数据库
CREATE USER superset WITH PASSWORD 'superset';
CREATE DATABASE superset;
GRANT ALL PRIVILEGES ON DATABASE superset TO superset;
\q
```

2. **更新配置文件**:

创建或修改 `.env` 文件：

```bash
# 复制示例配置
cp .env.example .env
```

编辑 `.env` 文件，配置数据库连接：

```
# 数据库连接字符串
SQLALCHEMY_DATABASE_URI=postgresql://superset:superset@localhost:5432/superset

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 加密密钥（务必修改）
SECRET_KEY="YOUR_SECRET_KEY_HERE"
```

### 3.2 初始化数据库

```bash
# 初始化数据库
superset db upgrade

# 创建默认管理员账户
superset fab create-admin

# 初始化数据
superset init
```

### 3.3 配置Redis（推荐）

安装并启动Redis服务，然后在配置文件中设置：

```
REDIS_URL=redis://localhost:6379/0
```

### 3.4 开发模式启动

#### 3.4.1 启动后端服务

在一个终端中启动Flask开发服务器：

```bash
# 使用开发模式启动后端
superset run -p 8088 --with-threads --reload
```

#### 3.4.2 启动前端开发服务器

在另一个终端中启动前端开发服务器：

```bash
cd superset-frontend
npm run dev
```

### 3.5 浏览器访问

前端开发服务器启动后，访问：http://localhost:9000

后端API访问地址：http://localhost:8088

## 4. 开发工作流

### 4.1 开发模式配置

#### 4.1.1 后端开发模式

确保启用了以下配置：

```python
# superset/config.py 或自定义配置
DEBUG = True
TALISMAN_ENABLED = False  # 禁用安全头以便调试
```

#### 4.1.2 前端开发模式

前端开发服务器已配置热重载，无需手动刷新浏览器。

### 4.2 代码风格检查

Superset使用flake8和black进行代码风格检查：

```bash
# 检查后端代码
flake8 superset
black --check superset

# 检查前端代码
cd superset-frontend
npm run lint
```

### 4.3 运行测试

#### 4.3.1 单元测试

```bash
# 运行后端单元测试
pytest -xvs superset/tests/core

# 运行前端单元测试
cd superset-frontend
npm test
```

#### 4.3.2 集成测试

```bash
# 运行集成测试
pytest -xvs superset/tests/integration
```

## 5. 开发环境调试技巧

### 5.1 后端调试

#### 5.1.1 使用VS Code调试

创建 `.vscode/launch.json` 文件：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Superset Debug",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/superset/cli/main.py",
      "args": ["run", "-p", "8088", "--with-threads"],
      "env": {
        "FLASK_ENV": "development",
        "PYTHONPATH": "${workspaceFolder}"
      },
      "justMyCode": false
    }
  ]
}
```

#### 5.1.2 日志配置

在 `.env` 文件中添加：

```
# 启用详细日志
LOG_LEVEL=DEBUG
FLASK_ENV=development
```

### 5.2 前端调试

#### 5.2.1 浏览器开发工具

使用Chrome/Firefox开发工具检查组件状态和性能。

#### 5.2.2 React开发工具

安装React Developer Tools浏览器扩展，用于检查React组件树。

#### 5.2.3 启用前端开发模式日志

```bash
# 启动前端并开启日志
cd superset-frontend
DEBUG=1 npm run dev
```

## 6. 项目结构概览

### 6.1 目录结构

```
superset/
├── superset/           # 后端主代码目录
│   ├── assets/         # 静态资源
│   ├── charts/         # 图表相关后端代码
│   ├── commands/       # CLI命令实现
│   ├── connectors/     # 数据库连接器
│   ├── dashboards/     # 仪表板相关代码
│   ├── db_engine_specs/ # 数据库引擎规范
│   ├── embed/          # 嵌入相关功能
│   ├── export/         # 导出功能
│   ├── filters/        # 过滤器相关代码
│   ├── jinja_context/  # Jinja模板上下文
│   ├── migrations/     # 数据库迁移脚本
│   ├── models/         # ORM模型
│   ├── queries/        # 查询相关代码
│   ├── security/       # 安全相关代码
│   ├── sql_lab/        # SQL Lab功能
│   ├── tasks/          # 异步任务
│   ├── utils/          # 工具函数
│   └── views/          # 视图和路由
├── superset-frontend/  # 前端代码目录
│   ├── cypress/        # Cypress测试
│   ├── i18n/           # 国际化文件
│   ├── src/            # 源代码
│   │   ├── assets/     # 静态资源
│   │   ├── components/ # React组件
│   │   ├── dashboard/  # 仪表板相关组件
│   │   ├── explore/    # 探索界面相关组件
│   │   ├── features/   # 功能模块
│   │   ├── redux/      # Redux状态管理
│   │   ├── services/   # API服务
│   │   ├── setup/      # 初始化配置
│   │   ├── sqllab/     # SQL Lab前端代码
│   │   ├── types/      # TypeScript类型定义
│   │   └── utils/      # 工具函数
│   └── stories/        # Storybook组件库
├── tests/              # 测试目录
├── scripts/            # 辅助脚本
├── setup.py            # 包安装配置
└── requirements/       # 依赖要求文件
```

### 6.2 关键配置文件

- **`superset/config.py`**：主配置文件
- **`.env`**：环境变量配置
- **`superset-frontend/package.json`**：前端依赖和脚本
- **`superset-frontend/webpack.config.js`**：前端构建配置

## 7. 常见问题与解决方案

### 7.1 安装问题

#### 7.1.1 Python依赖安装失败

**问题**：安装特定Python包失败

**解决方案**：
```bash
# 更新pip和setuptools
pip install --upgrade pip setuptools wheel

# 安装编译工具（Linux）
sudo apt-get install build-essential

# 安装特定依赖
pip install <package-name> --no-binary :all:
```

#### 7.1.2 前端依赖安装失败

**问题**：npm install失败

**解决方案**：
```bash
# 清理npm缓存
npm cache clean --force

# 使用yarn代替npm
yarn install

# 或使用npm代理
npm config set proxy http://your-proxy:port
```

### 7.2 运行时问题

#### 7.2.1 数据库连接失败

**问题**：无法连接到数据库

**解决方案**：
- 检查数据库服务是否运行
- 验证连接字符串配置是否正确
- 确保数据库用户有正确权限

#### 7.2.2 前端与后端API通信失败

**问题**：前端无法连接到后端API

**解决方案**：
```bash
# 检查后端服务是否正在运行
ps aux | grep superset

# 检查CORS配置
# 在配置中添加
ENABLE_CORS = True
CORS_OPTIONS = {
    'supports_credentials': True,
    'allow_headers': ['*'],
    'resources': ['*'],
    'origins': ['*'],
}
```

## 8. 开发最佳实践

### 8.1 代码组织

- 遵循现有的代码结构和命名规范
- 将相关功能组织在同一目录下
- 保持模块间的低耦合

### 8.2 开发流程

1. 创建新分支进行开发
2. 编写功能和单元测试
3. 运行代码风格检查
4. 提交PR前确保所有测试通过
5. 添加详细的提交信息和PR描述

### 8.3 文档更新

- 更新相关文档以反映代码变更
- 为新功能添加文档说明
- 确保API文档的准确性

### 8.4 协作与版本控制

- 定期从主分支拉取最新代码
- 编写清晰的提交信息
- 遵循PR流程并接受代码审查

通过以上步骤，您可以成功搭建Superset开发环境并开始二次开发工作。接下来，我们将详细介绍如何进行自定义图表开发和后端功能扩展。