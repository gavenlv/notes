# 第一天：安装与设置

## 用户故事1：使用Docker安装Superset

**标题**：作为一名开发者，我希望使用Docker快速安装Superset，以便在没有复杂环境设置的情况下开始学习。

**描述**：
Docker提供了最快的方式来运行Superset，只需最少的配置。这种方法非常适合开发和学习目的。

**验收标准**：
- [ ] Superset容器成功启动
- [ ] Web界面可通过http://localhost:8088访问
- [ ] 默认管理员凭据有效
- [ ] 数据库连接已建立
- [ ] 所有核心功能正常运行

**分步指南**：

1. **前提条件检查**
   ```bash
   # 确保Docker已安装
   docker --version
   docker-compose --version
   ```

2. **克隆Superset仓库**
   ```bash
   git clone https://github.com/apache/superset.git
   cd superset
   ```

3. **使用Docker Compose启动**
   ```bash
   # 使用提供的docker-compose.yml
   docker-compose up -d
   ```

4. **初始化数据库**
   ```bash
   # 创建管理员用户
   docker-compose exec superset superset fab create-admin \
     --username admin \
     --firstname Superset \
     --lastname Admin \
     --email admin@superset.com \
     --password admin
   
   # 初始化数据库
   docker-compose exec superset superset db upgrade
   
   # 加载示例
   docker-compose exec superset superset load_examples
   
   # 初始化
   docker-compose exec superset superset init
   ```

5. **访问Superset**
   - 打开浏览器：http://localhost:8088
   - 登录：admin/admin

**参考文档**：
- [官方Docker安装指南](https://superset.apache.org/docs/installation/installing-superset-using-docker-compose)
- [Docker Compose配置](https://github.com/apache/superset/blob/master/docker-compose.yml)

---

## 用户故事2：使用pip安装Superset

**标题**：作为系统管理员，我希望使用pip安装Superset，以便完全控制安装和配置。

**描述**：
pip安装提供了对Superset环境的最大灵活性和控制力，适用于生产部署。

**验收标准**：
- [ ] Python虚拟环境已创建
- [ ] Superset通过pip安装
- [ ] 数据库已配置并初始化
- [ ] Web服务器成功启动
- [ ] 管理员用户已创建

**分步指南**：

1. **创建虚拟环境**
   ```bash
   python -m venv superset_env
   source superset_env/bin/activate  # 在Windows上：superset_env\Scripts\activate
   ```

2. **安装Superset**
   ```bash
   pip install apache-superset
   ```

3. **设置环境变量**
   ```bash
   export FLASK_APP=superset
   export SUPERSET_HOME=/path/to/superset
   ```

4. **初始化数据库**
   ```bash
   # 初始化数据库
   superset db upgrade
   
   # 创建管理员用户
   superset fab create-admin \
     --username admin \
     --firstname Superset \
     --lastname Admin \
     --email admin@superset.com \
     --password admin
   
   # 加载示例
   superset load_examples
   
   # 初始化
   superset init
   ```

5. **启动Superset**
   ```bash
   superset run -p 8088 --with-threads --reload --host=0.0.0.0
   ```

**参考文档**：
- [官方pip安装指南](https://superset.apache.org/docs/installation/installing-superset-from-scratch)
- [配置参考](https://superset.apache.org/docs/installation/configuring-superset)

---

## 用户故事3：使用自定义数据库安装Superset

**标题**：作为生产工程师，我希望为Superset配置生产数据库，使其能够处理企业级工作负载。

**描述**：
生产部署需要像PostgreSQL或MySQL这样的强大数据库后端，以获得更好的性能和可靠性。

**验收标准**：
- [ ] 生产数据库已配置
- [ ] 数据库连接已测试
- [ ] Superset成功连接到数据库
- [ ] 性能已针对生产使用进行了优化

**分步指南**：

1. **安装数据库依赖**
   ```bash
   # 对于PostgreSQL
   pip install psycopg2-binary
   
   # 对于MySQL
   pip install mysqlclient
   ```

2. **配置数据库URL**
   ```bash
   # PostgreSQL
   export SQLALCHEMY_DATABASE_URI="postgresql://user:password@localhost:5432/superset"
   
   # MySQL
   export SQLALCHEMY_DATABASE_URI="mysql://user:password@localhost:3306/superset"
   ```

3. **创建数据库**
   ```sql
   -- PostgreSQL
   CREATE DATABASE superset;
   CREATE USER superset WITH PASSWORD 'superset';
   GRANT ALL PRIVILEGES ON DATABASE superset TO superset;
   
   -- MySQL
   CREATE DATABASE superset CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'superset'@'localhost' IDENTIFIED BY 'superset';
   GRANT ALL PRIVILEGES ON superset.* TO 'superset'@'localhost';
   FLUSH PRIVILEGES;
   ```

4. **使用自定义数据库初始化**
   ```bash
   superset db upgrade
   superset fab create-admin
   superset init
   ```

**参考文档**：
- [数据库配置](https://superset.apache.org/docs/installation/configuring-superset#database)
- [生产部署指南](https://superset.apache.org/docs/installation/running-on-production)

---

## 用户故事4：安装带Redis缓存的Superset

**标题**：作为性能工程师，我希望为Superset配置Redis缓存，使仪表板查询更快、响应更迅速。

**描述**：
Redis缓存通过缓存查询结果和会话数据显著提高Superset性能。

**验收标准**：
- [ ] Redis服务器已安装并运行
- [ ] Superset已配置为使用Redis
- [ ] 缓存对仪表板查询有效
- [ ] 性能提升可测量

**分步指南**：

1. **安装Redis**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install redis-server
   
   # macOS
   brew install redis
   
   # Windows
   # 从https://redis.io/download下载
   ```

2. **安装Redis Python客户端**
   ```bash
   pip install redis
   ```

3. **为Redis配置Superset**
   ```python
   # 在superset_config.py中
   CACHE_CONFIG = {
       'CACHE_TYPE': 'redis',
       'CACHE_DEFAULT_TIMEOUT': 300,
       'CACHE_KEY_PREFIX': 'superset_',
       'CACHE_REDIS_HOST': 'localhost',
       'CACHE_REDIS_PORT': 6379,
       'CACHE_REDIS_DB': 1,
       'CACHE_REDIS_URL': 'redis://localhost:6379/1'
   }
   
   # 会话配置
   SESSION_TYPE = 'redis'
   SESSION_REDIS = redis.from_url('redis://localhost:6379/2')
   ```

4. **测试缓存**
   ```bash
   # 测试Redis连接
   redis-cli ping
   
   # 重启Superset
   superset run -p 8088
   ```

**参考文档**：
- [缓存配置](https://superset.apache.org/docs/installation/configuring-superset#caching)
- [Redis文档](https://redis.io/documentation)

---

## 常见问题排查

### 问题1：端口已被占用
```bash
# 检查什么在使用端口8088
lsof -i :8088
# 终止进程或更改端口
superset run -p 8089
```

### 问题2：数据库连接失败
```bash
# 测试数据库连接
python -c "from sqlalchemy import create_engine; engine = create_engine('your_database_url'); engine.connect()"
```

### 问题3：权限被拒绝
```bash
# 修复文件权限
chmod -R 755 /path/to/superset
```

### 问题4：内存问题
```bash
# 增加Docker内存
docker-compose down
docker system prune
docker-compose up -d
```

## 下一步

完成安装后，请继续：
- [介绍与基本概念](introduction.md)
- [配置与管理](configuration.md)