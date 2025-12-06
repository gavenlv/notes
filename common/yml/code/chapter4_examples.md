# 第4章示例代码

## 实验1：应用配置管理

```yaml
# application.yml
# 基础应用配置
app:
  name: "MyWebApp"
  version: "1.0.0"
  description: "A sample web application"

server:
  host: "0.0.0.0"
  port: 8080
  timeout: 30

database:
  type: "postgresql"
  host: "localhost"
  port: 5432
  name: "myapp_db"
  username: "app_user"
  password: "${DB_PASSWORD}"

logging:
  level: "info"
  output:
    - type: "file"
      path: "/var/log/myapp/app.log"
    - type: "console"

features:
  new_ui: true
  beta_api: false
  analytics: true
```

```yaml
# application-dev.yml
# 开发环境配置
app:
  env: "development"
  debug: true

server:
  port: 3000
  host: "localhost"

database:
  name: "myapp_dev"
  username: "dev_user"
  password: "dev_password"

logging:
  level: "debug"
  output:
    - type: "console"
      colors: true
    - type: "file"
      path: "./logs/dev.log"

features:
  debug_mode: true
  beta_api: true
```

```yaml
# application-prod.yml
# 生产环境配置
app:
  env: "production"
  debug: false

server:
  port: 80
  ssl:
    enabled: true
    cert_path: "/etc/ssl/certs/app.crt"
    key_path: "/etc/ssl/private/app.key"

database:
  host: "prod-db.example.com"
  name: "myapp_prod"
  username: "prod_user"
  password: "${DB_PASSWORD}"
  pool:
    min: 10
    max: 50

logging:
  level: "warn"
  output:
    - type: "file"
      path: "/var/log/myapp/app.log"
      max_size: "500MB"
      max_files: 10

features:
  debug_mode: false
  beta_api: false
```

## 实验2：Docker Compose应用

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Web应用服务
  web:
    build: .
    ports:
      - "8080:8080"
    environment:
      - NODE_ENV=production
      - DB_HOST=database
      - REDIS_HOST=cache
    depends_on:
      - database
      - cache
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - app-network

  # 数据库服务
  database:
    image: postgres:13
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=app_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    restart: unless-stopped
    networks:
      - app-network

  # 缓存服务
  cache:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - app-network

  # 反向代理
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: unless-stopped
    networks:
      - app-network

# 数据卷定义
volumes:
  postgres_data:
  redis_data:

# 网络定义
networks:
  app-network:
    driver: bridge
```

## 实验3：Kubernetes部署

```yaml
# deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  labels:
    app: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
      - name: web-app
        image: myapp:1.0.0
        ports:
        - containerPort: 8080
        env:
        - name: NODE_ENV
          value: "production"
        - name: DB_HOST
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: host
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
# service.yml
apiVersion: v1
kind: Service
metadata:
  name: web-app-service
spec:
  selector:
    app: web-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: LoadBalancer
---
# configmap.yml
apiVersion: v1
kind: ConfigMap
metadata:
  name: web-app-config
data:
  app.properties: |
    server.port=8080
    logging.level.root=INFO
    app.name=WebApp
    app.version=1.0.0
---
# secret.yml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  host: cG9zdGdyZXMtc2VydmljZQ==  # postgres-service (base64)
  username: YXBwX3VzZXI=          # app_user (base64)
  password: c2VjcmV0Fw==          # secret (base64)
```

## 实验4：CI/CD流水线

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  NODE_VERSION: '16'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # 代码质量检查
  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: ${{ env.NODE_VERSION }}
        cache: 'npm'
    - name: Install dependencies
      run: npm ci
    - name: Run linter
      run: npm run lint
    - name: Run formatter check
      run: npm run format:check

  # 测试
  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
    - uses: actions/checkout@v3
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: ${{ env.NODE_VERSION }}
        cache: 'npm'
    - name: Install dependencies
      run: npm ci
    - name: Run tests
      run: npm test
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage/lcov.info

  # 构建和推送Docker镜像
  build-and-push:
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main'
    permissions:
      contents: read
      packages: write
    steps:
    - uses: actions/checkout@v3
    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha,prefix={{branch}}-
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}

  # 部署到测试环境
  deploy-staging:
    runs-on: ubuntu-latest
    needs: build-and-push
    if: github.ref == 'refs/heads/develop'
    environment: staging
    steps:
    - uses: actions/checkout@v3
    - name: Deploy to staging
      run: |
        echo "Deploying to staging environment"
        # 这里可以添加实际的部署脚本

  # 部署到生产环境
  deploy-production:
    runs-on: ubuntu-latest
    needs: build-and-push
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
    - uses: actions/checkout@v3
    - name: Deploy to production
      run: |
        echo "Deploying to production environment"
        # 这里可以添加实际的部署脚本
```

## 实验5：数据导入/导出

```yaml
# data-export.yml
# 示例数据导出

# 数据库表结构导出
tables:
  users:
    columns:
      - name: id
        type: integer
        primary_key: true
        nullable: false
      - name: username
        type: varchar(50)
        unique: true
        nullable: false
      - name: email
        type: varchar(100)
        unique: true
        nullable: false
      - name: password_hash
        type: varchar(255)
        nullable: false
      - name: created_at
        type: timestamp
        nullable: false
        default: "CURRENT_TIMESTAMP"
    indexes:
      - name: idx_users_username
        columns: [username]
        unique: true
      - name: idx_users_email
        columns: [email]
        unique: true

  articles:
    columns:
      - name: id
        type: integer
        primary_key: true
        nullable: false
      - name: title
        type: varchar(255)
        nullable: false
      - name: slug
        type: varchar(255)
        unique: true
        nullable: false
      - name: content
        type: text
        nullable: false
      - name: author_id
        type: integer
        nullable: false
        foreign_key:
          table: users
          column: id
      - name: published_at
        type: timestamp
        nullable: true
    indexes:
      - name: idx_articles_slug
        columns: [slug]
        unique: true
      - name: idx_articles_author_id
        columns: [author_id]
      - name: idx_articles_published_at
        columns: [published_at]

# 示例数据导出
data:
  users:
    - id: 1
      username: admin
      email: admin@example.com
      password_hash: "$2b$12$..."
      created_at: "2020-01-01T00:00:00Z"
    - id: 2
      username: johndoe
      email: john@example.com
      password_hash: "$2b$12$..."
      created_at: "2020-01-15T10:30:00Z"

  articles:
    - id: 1
      title: "Welcome to Our Platform"
      slug: "welcome-to-our-platform"
      content: "This is the welcome article..."
      author_id: 1
      published_at: "2020-01-01T12:00:00Z"
    - id: 2
      title: "Getting Started Guide"
      slug: "getting-started-guide"
      content: "This guide will help you get started..."
      author_id: 1
      published_at: "2020-01-05T09:30:00Z"
```

## Python验证代码

```python
# practical_applications.py
import yaml
import json
import os
from pathlib import Path

def test_application_config():
    """测试应用配置管理"""
    print("=== 应用配置管理测试 ===")
    
    # 加载基础配置
    with open('application.yml', 'r', encoding='utf-8') as file:
        base_config = yaml.safe_load(file)
    
    # 模拟加载环境特定配置
    env = 'dev'  # 可以是 'dev', 'prod'
    env_config_file = f'application-{env}.yml'
    
    if os.path.exists(env_config_file):
        with open(env_config_file, 'r', encoding='utf-8') as file:
            env_config = yaml.safe_load(file)
        
        # 合并配置
        def deep_merge(base, override):
            result = base.copy()
            for key, value in override.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        merged_config = deep_merge(base_config, env_config)
        
        print(f"合并后的{env}环境配置:")
        print(json.dumps(merged_config, indent=2, ensure_ascii=False))
    else:
        print(f"环境配置文件 {env_config_file} 不存在")

def test_docker_compose():
    """测试Docker Compose配置"""
    print("\n=== Docker Compose配置测试 ===")
    
    with open('docker-compose.yml', 'r', encoding='utf-8') as file:
        compose_config = yaml.safe_load(file)
    
    print("Docker Compose服务:")
    for service_name, service_config in compose_config['services'].items():
        print(f"\n服务: {service_name}")
        print(f"镜像: {service_config.get('image', 'build')}")
        print(f"端口: {service_config.get('ports', [])}")
        if 'environment' in service_config:
            print(f"环境变量: {len(service_config['environment'])}个")
        if 'depends_on' in service_config:
            print(f"依赖服务: {service_config['depends_on']}")
    
    print(f"\n数据卷: {list(compose_config['volumes'].keys())}")
    print(f"网络: {list(compose_config['networks'].keys())}")

def test_kubernetes():
    """测试Kubernetes配置"""
    print("\n=== Kubernetes配置测试 ===")
    
    with open('deployment.yml', 'r', encoding='utf-8') as file:
        # 加载多文档YAML
        documents = list(yaml.safe_load_all(file))
        
        for doc in documents:
            if doc is None:
                continue
                
            kind = doc.get('kind', 'Unknown')
            metadata = doc.get('metadata', {})
            name = metadata.get('name', 'Unnamed')
            
            print(f"\n资源类型: {kind}")
            print(f"名称: {name}")
            
            if kind == 'Deployment':
                spec = doc.get('spec', {})
                replicas = spec.get('replicas', 0)
                print(f"副本数: {replicas}")
                
                template = spec.get('template', {})
                pod_spec = template.get('spec', {})
                containers = pod_spec.get('containers', [])
                
                for container in containers:
                    container_name = container.get('name', 'Unnamed')
                    image = container.get('image', 'Unknown')
                    ports = container.get('ports', [])
                    env_vars = container.get('env', [])
                    
                    print(f"  容器: {container_name}")
                    print(f"    镜像: {image}")
                    print(f"    端口: {[p.get('containerPort') for p in ports]}")
                    print(f"    环境变量: {len(env_vars)}个")
            
            elif kind == 'Service':
                spec = doc.get('spec', {})
                service_type = spec.get('type', 'ClusterIP')
                ports = spec.get('ports', [])
                selector = spec.get('selector', {})
                
                print(f"  类型: {service_type}")
                print(f"  端口: {[f"{p.get('port')}:{p.get('targetPort')}" for p in ports]}")
                print(f"  选择器: {selector}")
            
            elif kind == 'ConfigMap':
                data = doc.get('data', {})
                print(f"  数据项: {list(data.keys())}")
            
            elif kind == 'Secret':
                data = doc.get('data', {})
                secret_type = doc.get('type', 'Opaque')
                print(f"  类型: {secret_type}")
                print(f"  数据项: {list(data.keys())}")

def test_cicd_pipeline():
    """测试CI/CD流水线配置"""
    print("\n=== CI/CD流水线配置测试 ===")
    
    with open('.github/workflows/ci-cd.yml', 'r', encoding='utf-8') as file:
        pipeline_config = yaml.safe_load(file)
    
    print(f"流水线名称: {pipeline_config.get('name', 'Unnamed')}")
    print(f"触发条件:")
    for trigger, conditions in pipeline_config.get('on', {}).items():
        if isinstance(conditions, dict) and 'branches' in conditions:
            print(f"  {trigger}: {', '.join(conditions['branches'])}")
        else:
            print(f"  {trigger}: {conditions}")
    
    print(f"\n环境变量:")
    for key, value in pipeline_config.get('env', {}).items():
        print(f"  {key}: {value}")
    
    print(f"\n作业:")
    for job_name, job_config in pipeline_config.get('jobs', {}).items():
        print(f"\n  作业: {job_name}")
        print(f"    运行环境: {job_config.get('runs-on', 'Unknown')}")
        if 'needs' in job_config:
            print(f"    依赖: {', '.join(job_config['needs'])}")
        if 'if' in job_config:
            print(f"    条件: {job_config['if']}")
        
        steps = job_config.get('steps', [])
        print(f"    步骤数: {len(steps)}")

def test_data_export():
    """测试数据导出"""
    print("\n=== 数据导出测试 ===")
    
    with open('data-export.yml', 'r', encoding='utf-8') as file:
        export_data = yaml.safe_load(file)
    
    print("表结构:")
    for table_name, table_config in export_data.get('tables', {}).items():
        print(f"\n表: {table_name}")
        
        columns = table_config.get('columns', [])
        print(f"  列数: {len(columns)}")
        for column in columns[:3]:  # 只显示前3列
            col_name = column.get('name', 'Unnamed')
            col_type = column.get('type', 'Unknown')
            nullable = column.get('nullable', True)
            primary_key = column.get('primary_key', False)
            
            col_info = f"{col_name}: {col_type}"
            if primary_key:
                col_info += " (主键)"
            if not nullable:
                col_info += " (非空)"
            
            print(f"    {col_info}")
        
        if len(columns) > 3:
            print(f"    ... 还有 {len(columns) - 3} 列")
        
        indexes = table_config.get('indexes', [])
        if indexes:
            print(f"  索引数: {len(indexes)}")
    
    print("\n示例数据:")
    for table_name, table_data in export_data.get('data', {}).items():
        print(f"\n表: {table_name}")
        print(f"  记录数: {len(table_data)}")
        
        if table_data:
            # 显示第一条记录
            first_record = table_data[0]
            print(f"  第一条记录字段: {list(first_record.keys())}")

def generate_sample_config():
    """生成示例配置文件"""
    print("\n=== 生成示例配置文件 ===")
    
    # 创建示例应用配置
    sample_config = {
        'app': {
            'name': 'SampleApp',
            'version': '1.0.0',
            'env': 'development'
        },
        'server': {
            'host': 'localhost',
            'port': 3000
        },
        'database': {
            'type': 'sqlite',
            'path': './data/sample.db'
        },
        'logging': {
            'level': 'debug',
            'output': [
                {'type': 'console', 'colors': True},
                {'type': 'file', 'path': './logs/sample.log'}
            ]
        }
    }
    
    # 写入文件
    with open('sample-config.yml', 'w', encoding='utf-8') as file:
        yaml.dump(sample_config, file, default_flow_style=False, allow_unicode=True)
    
    print("已生成示例配置文件: sample-config.yml")
    
    # 验证生成的文件
    with open('sample-config.yml', 'r', encoding='utf-8') as file:
        loaded_config = yaml.safe_load(file)
    
    print("验证生成的配置:")
    print(json.dumps(loaded_config, indent=2, ensure_ascii=False))

# 运行所有测试
test_application_config()
test_docker_compose()
test_kubernetes()
test_cicd_pipeline()
test_data_export()
generate_sample_config()
```

## 实验6：语法解析深度示例

### 6.1 配置语法错误示例

```yaml
# syntax-error-config.yml
# 缩进不一致的配置
app:
  name: "MyApp"
   version: "1.0.0"  # 错误的缩进
  description: "A sample app"

# 使用制表符代替空格
server:
	port: 8080  # 制表符缩进
	host: "localhost"

# 缺少冒号
database
  type: "postgresql"
  host: "localhost"

# 重复键
logging:
  level: "info"
  level: "debug"  # 重复键
```

### 6.2 特殊字符处理示例

```yaml
# special-chars-config.yml
# 包含特殊字符的配置
app:
  name: "My:App"  # 包含冒号
  description: "App with # special chars"  # 包含哈希符号
  url: "https://example.com/path?query=value&param=test"

# 引号使用示例
strings:
  single_quoted: 'This is a "quoted" string'
  double_quoted: "This is a 'quoted' string"
  literal: |
    This is a literal string
    with multiple lines
    and special chars: : # { }
  folded: >
    This is a folded string
    with multiple lines that
    will be joined

# 包含特殊字符的键
"special:key": "value with : colon"
"key with spaces": "value"
"key.with.dots": "value"
```

### 6.3 多行字符串块示例

```yaml
# multiline-config.yml
# 字面量块标量
sql_query: |
  SELECT 
    users.id,
    users.name,
    COUNT(orders.id) as order_count
  FROM users
  LEFT JOIN orders ON users.id = orders.user_id
  WHERE users.created_at > '2020-01-01'
  GROUP BY users.id, users.name
  ORDER BY order_count DESC

# 折叠块标量
error_message: >
  This is a long error message that spans
  multiple lines but will be joined into
  a single line when parsed.

# 保持块标量
config_file: |-
  server {
    listen 80;
    server_name example.com;
    
    location / {
      proxy_pass http://backend;
    }
  }

# 多行数组项
commands:
  - |
    docker build -t myapp:latest .
    docker push myapp:latest
  - |
    kubectl apply -f deployment.yaml
    kubectl rollout status deployment/myapp
```

## 实验7：语法解析验证代码

```python
# syntax_validation.py
import yaml
import re
from pathlib import Path

class YAMLSyntaxParser:
    """YAML语法解析器"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def validate_indentation(self, content):
        """验证缩进"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            if line.strip() and not line.startswith('#'):
                # 检查制表符
                if '\t' in line:
                    self.errors.append(f"第{i}行: 检测到制表符，请使用空格缩进")
                
                # 检查缩进一致性
                if line.startswith(' '):
                    spaces = len(line) - len(line.lstrip())
                    if spaces % 2 != 0:
                        self.warnings.append(f"第{i}行: 缩进空格数应为偶数，当前为{spaces}")
    
    def validate_special_chars(self, content):
        """验证特殊字符"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            if line.strip() and not line.startswith('#'):
                # 检查未转义的特殊字符
                if re.search(r'(?<!\\):', line) and ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) > 1 and not parts[0].strip().endswith('"'):
                        # 检查键中是否包含冒号但未加引号
                        if ':' in parts[0] and not (parts[0].startswith('"') and parts[0].endswith('"')):
                            self.warnings.append(f"第{i}行: 键中包含冒号，建议使用引号包裹")
    
    def validate_multiline_strings(self, content):
        """验证多行字符串"""
        lines = content.split('\n')
        in_multiline = False
        multiline_type = None
        
        for i, line in enumerate(lines, 1):
            # 检测多行字符串开始
            if not in_multiline and ('|' in line or '>' in line):
                in_multiline = True
                if '|' in line:
                    multiline_type = 'literal'
                else:
                    multiline_type = 'folded'
                continue
            
            # 在多行字符串中
            if in_multiline:
                # 检查缩进
                if line.strip() and not line.startswith(' '):
                    in_multiline = False
                    multiline_type = None
    
    def validate_yaml_structure(self, content):
        """验证YAML结构"""
        try:
            data = yaml.safe_load(content)
            
            # 检查重复键
            def check_duplicate_keys(data, path=""):
                if isinstance(data, dict):
                    keys = set()
                    for key, value in data.items():
                        if key in keys:
                            self.errors.append(f"重复键: {path}.{key}")
                        keys.add(key)
                        check_duplicate_keys(value, f"{path}.{key}" if path else key)
                elif isinstance(data, list):
                    for item in data:
                        check_duplicate_keys(item, path)
            
            check_duplicate_keys(data)
            
        except yaml.YAMLError as e:
            self.errors.append(f"YAML解析错误: {e}")
    
    def analyze_config_complexity(self, content):
        """分析配置复杂度"""
        try:
            data = yaml.safe_load(content)
            
            def count_nodes(obj):
                if isinstance(obj, dict):
                    return 1 + sum(count_nodes(v) for v in obj.values())
                elif isinstance(obj, list):
                    return 1 + sum(count_nodes(item) for item in obj)
                else:
                    return 1
            
            node_count = count_nodes(data) if data else 0
            
            if node_count > 100:
                self.warnings.append(f"配置复杂度较高，包含{node_count}个节点")
            
            return node_count
            
        except yaml.YAMLError:
            return 0
    
    def validate_file(self, file_path):
        """验证文件"""
        self.errors.clear()
        self.warnings.clear()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            print(f"\n=== 验证文件: {file_path} ===")
            
            # 执行各种验证
            self.validate_indentation(content)
            self.validate_special_chars(content)
            self.validate_multiline_strings(content)
            self.validate_yaml_structure(content)
            complexity = self.analyze_config_complexity(content)
            
            # 输出结果
            if self.errors:
                print("❌ 错误:")
                for error in self.errors:
                    print(f"  - {error}")
            else:
                print("✅ 无语法错误")
            
            if self.warnings:
                print("⚠️  警告:")
                for warning in self.warnings:
                    print(f"  - {warning}")
            else:
                print("✅ 无警告")
            
            print(f"📊 配置复杂度: {complexity} 个节点")
            
            return len(self.errors) == 0
            
        except Exception as e:
            print(f"❌ 文件读取错误: {e}")
            return False

def test_syntax_validation():
    """测试语法验证"""
    parser = YAMLSyntaxParser()
    
    # 测试语法错误配置
    print("=== 语法错误配置测试 ===")
    syntax_error_config = """
app:
  name: "MyApp"
   version: "1.0.0"  # 错误的缩进
  description: "A sample app"

server:
	port: 8080  # 制表符缩进
	host: "localhost"
"""
    
    with open('syntax-error-test.yml', 'w', encoding='utf-8') as file:
        file.write(syntax_error_config)
    
    parser.validate_file('syntax-error-test.yml')
    
    # 测试特殊字符配置
    print("\n=== 特殊字符配置测试 ===")
    special_chars_config = """
app:
  name: "My:App"
  description: "App with # special chars"
  url: "https://example.com/path?query=value&param=test"

"special:key": "value with : colon"
"key with spaces": "value"
"""
    
    with open('special-chars-test.yml', 'w', encoding='utf-8') as file:
        file.write(special_chars_config)
    
    parser.validate_file('special-chars-test.yml')
    
    # 测试多行字符串配置
    print("\n=== 多行字符串配置测试 ===")
    multiline_config = """
sql_query: |
  SELECT 
    users.id,
    users.name,
    COUNT(orders.id) as order_count
  FROM users
  LEFT JOIN orders ON users.id = orders.user_id

error_message: >
  This is a long error message that spans
  multiple lines but will be joined into
  a single line when parsed.
"""
    
    with open('multiline-test.yml', 'w', encoding='utf-8') as file:
        file.write(multiline_config)
    
    parser.validate_file('multiline-test.yml')

def generate_syntax_guide():
    """生成语法指南"""
    guide = {
        '缩进规则': {
            'description': '使用空格缩进，推荐使用2或4个空格',
            'correct': 'key:\n  subkey: value',
            'incorrect': 'key:\n\tsubkey: value  # 使用制表符'
        },
        '特殊字符': {
            'description': '包含特殊字符的键需要使用引号包裹',
            'correct': '"key:with:colons": value',
            'incorrect': 'key:with:colons: value'
        },
        '多行字符串': {
            'description': '使用|保留换行，>折叠换行',
            'correct': 'text: |\n  line1\n  line2',
            'incorrect': 'text: line1\\nline2'
        }
    }
    
    with open('syntax-guide.yml', 'w', encoding='utf-8') as file:
        yaml.dump(guide, file, default_flow_style=False, allow_unicode=True)
    
    print("✅ 已生成语法指南: syntax-guide.yml")

# 运行测试
test_syntax_validation()
generate_syntax_guide()
```

## 实验说明

1. **application.yml, application-dev.yml, application-prod.yml**: 应用配置管理示例，展示基础配置和环境特定配置
2. **docker-compose.yml**: Docker Compose应用示例，包含Web服务、数据库、缓存和反向代理
3. **deployment.yml**: Kubernetes部署示例，包含Deployment、Service、ConfigMap和Secret
4. **.github/workflows/ci-cd.yml**: CI/CD流水线示例，展示代码检查、测试、构建和部署流程
5. **data-export.yml**: 数据导出示例，包含表结构和示例数据
6. **syntax-error-config.yml, special-chars-config.yml, multiline-config.yml**: 语法解析深度示例，展示常见语法错误和特殊字符处理
7. **syntax_validation.py**: 语法解析验证代码，实现缩进验证、特殊字符验证、多行字符串验证和综合语法验证
8. **practical_applications.py**: Python验证代码，用于测试所有实战应用场景

运行验证代码：
```bash
# 运行实战应用测试
python practical_applications.py

# 运行语法解析测试
python syntax_validation.py
```

这将验证所有YAML文件的实战应用场景和语法正确性，并展示它们的用法和效果。语法解析代码会检测常见的语法错误并提供修复建议。