# 第十五章：使用Flask-AppBuilder构建REST API - 代码示例

本章展示了如何使用Flask-AppBuilder构建REST API的完整示例。

## 目录结构

```
chapter15/
├── app/                 # 应用核心代码
│   ├── __init__.py      # 应用工厂函数
│   ├── models.py        # 数据模型
│   ├── api/             # API端点
│   │   ├── __init__.py
│   │   ├── schemas.py   # 数据序列化Schema
│   │   ├── category.py  # 类别API
│   │   ├── product.py   # 产品API
│   │   ├── order.py     # 订单API
│   │   ├── user.py      # 用户API
│   │   └── auth.py      # 认证API
│   └── commands.py      # Flask CLI命令
├── tests/               # 测试代码
├── requirements.txt     # 依赖包
├── config.py            # 配置文件
├── run.py               # 应用启动文件
├── wsgi.py              # WSGI入口
├── Dockerfile           # Docker构建文件
├── docker-compose.yml   # Docker编排文件
├── Makefile             # 常用命令
└── README.md            # 说明文档
```

## 功能特性

1. **完整的REST API**：
   - 类别管理API
   - 产品管理API
   - 订单管理API
   - 用户管理API
   - 认证API

2. **数据验证**：
   - 使用Marshmallow进行数据序列化和验证
   - 自定义验证规则

3. **安全特性**：
   - JWT令牌认证
   - 基于角色的访问控制

4. **高级功能**：
   - 分页和排序
   - 搜索和过滤
   - 自定义API行为

5. **开发工具**：
   - Docker支持
   - Docker Compose编排
   - Makefile常用命令
   - Swagger API文档

## 快速开始

### 本地运行

1. 安装依赖：
   ```bash
   make install
   ```

2. 初始化数据库：
   ```bash
   make init-db
   ```

3. 填充示例数据：
   ```bash
   make seed-data
   ```

4. 运行开发服务器：
   ```bash
   make run
   ```

### Docker运行

1. 构建并启动服务：
   ```bash
   make start-docker
   ```

2. 填充示例数据：
   ```bash
   make shell-docker
   # 在容器内执行
   flask seed-data
   ```

## API端点

### 认证相关
- `POST /api/v1/auth/` - 用户登录，获取JWT令牌
- `GET /api/v1/auth/` - 获取当前用户信息

### 类别管理
- `GET /api/v1/category/` - 获取类别列表
- `POST /api/v1/category/` - 创建新类别
- `GET /api/v1/category/<id>` - 获取类别详情
- `PUT /api/v1/category/<id>` - 更新类别
- `DELETE /api/v1/category/<id>` - 删除类别

### 产品管理
- `GET /api/v1/product/` - 获取产品列表
- `POST /api/v1/product/` - 创建新产品
- `GET /api/v1/product/<id>` - 获取产品详情
- `PUT /api/v1/product/<id>` - 更新产品
- `DELETE /api/v1/product/<id>` - 删除产品

### 订单管理
- `GET /api/v1/order/` - 获取订单列表
- `POST /api/v1/order/` - 创建新订单
- `GET /api/v1/order/<id>` - 获取订单详情
- `PUT /api/v1/order/<id>` - 更新订单
- `DELETE /api/v1/order/<id>` - 删除订单

### 用户管理
- `GET /api/v1/user/` - 获取用户列表
- `POST /api/v1/user/` - 创建新用户
- `GET /api/v1/user/<id>` - 获取用户详情
- `PUT /api/v1/user/<id>` - 更新用户
- `DELETE /api/v1/user/<id>` - 删除用户

### 用户资料
- `GET /api/v1/user-profile/` - 获取当前用户资料
- `PUT /api/v1/user-profile/` - 更新当前用户资料

## 配置说明

主要配置项在`config.py`文件中：

- `SECRET_KEY`: Flask密钥
- `SQLALCHEMY_DATABASE_URI`: 数据库连接URI
- `JWT_SECRET_KEY`: JWT密钥
- `CACHE_TYPE`: 缓存类型
- `CACHE_REDIS_URL`: Redis缓存URL

## API文档

启动服务后，可以通过以下URL访问Swagger API文档：
- 本地运行：http://localhost:5000/apidocs
- Docker运行：http://localhost:8080 (Swagger UI)

## CLI命令

本项目提供了两个CLI命令用于数据库管理：

- `flask init-db` - 初始化数据库表结构
- `flask seed-data` - 填充示例数据

也可以通过Makefile命令执行：
```bash
make init-db    # 等同于 flask init-db
make seed-data  # 等同于 flask seed-data
```

## 测试

运行测试：
```bash
make test
```

## 部署

使用Gunicorn部署：
```bash
gunicorn --bind 0.0.0.0:5000 wsgi:application
```

## 许可证

MIT License