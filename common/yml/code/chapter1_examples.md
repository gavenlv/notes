# 第1章示例代码

## 实验1：基本YAML结构

```yaml
# experiment1.yml
# 实验1：基本YAML结构
---
# 个人信息
name: "张三"
age: 25
student: true

# 地址信息
address:
  street: "北京市朝阳区"
  city: "北京"
  zip: "100000"

# 兴趣爱好
hobbies:
  - "阅读"
  - "游泳"
  - "编程"
```

## 实验2：YAML与JSON对比

```yaml
# json_to_yaml.yml
# 从JSON转换而来的YAML示例
name: John Doe
age: 30
married: true
children:
  - name: Alice
    age: 5
  - name: Bob
    age: 3
address:
  street: 123 Main St
  city: Anytown
  zip: "12345"
```

## 实验3：配置文件示例

```yaml
# app_config.yml
# 应用配置示例
app:
  name: "MyApplication"
  version: "1.0.0"
  debug: true
  
database:
  host: "localhost"
  port: 5432
  name: "mydb"
  user: "admin"
  password: "secret"
  
logging:
  level: "info"
  file: "/var/log/app.log"
  max_size: "10MB"
```

## 实验4：Docker Compose示例

```yaml
# docker-compose.yml
# Docker Compose配置示例
version: '3'
services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./html:/usr/share/nginx/html
    depends_on:
      - db
  db:
    image: postgres:latest
    environment:
      POSTGRES_PASSWORD: example
      POSTGRES_DB: myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## 实验5：GitHub Actions示例

```yaml
# github-actions.yml
# GitHub Actions工作流示例
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python -m pytest tests/
```

## 实验6：多文档YAML

```yaml
# multi_document.yml
# 多文档YAML示例
---
# 文档1：用户信息
user:
  name: "张三"
  age: 25
  email: "zhangsan@example.com"
...
---
# 文档2：用户设置
settings:
  theme: "dark"
  notifications: true
  language: "zh-CN"
...
---
# 文档3：用户权限
permissions:
  - "read"
  - "write"
  - "delete"
...
```

## Python验证代码

```python
# validate_yaml.py
import yaml
import json

def validate_yaml_file(file_path):
    """验证YAML文件语法"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            print(f"✓ {file_path} 语法正确")
            return data
    except yaml.YAMLError as e:
        print(f"✗ {file_path} 语法错误: {e}")
        return None

def yaml_to_json(yaml_file, json_file):
    """将YAML转换为JSON"""
    data = validate_yaml_file(yaml_file)
    if data:
        with open(json_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        print(f"✓ 已转换为 {json_file}")

def json_to_yaml(json_file, yaml_file):
    """将JSON转换为YAML"""
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        with open(yaml_file, 'w', encoding='utf-8') as file:
            yaml.dump(data, file, allow_unicode=True, indent=2)
        print(f"✓ 已转换为 {yaml_file}")
    except Exception as e:
        print(f"✗ 转换失败: {e}")

def print_yaml_structure(yaml_file):
    """打印YAML文件结构"""
    data = validate_yaml_file(yaml_file)
    if data:
        print(f"\n{yaml_file} 结构:")
        print(json.dumps(data, ensure_ascii=False, indent=2))

# 验证所有YAML文件
yaml_files = [
    'experiment1.yml',
    'json_to_yaml.yml',
    'app_config.yml',
    'docker-compose.yml',
    'github-actions.yml',
    'multi_document.yml'
]

for yaml_file in yaml_files:
    print_yaml_structure(yaml_file)
    print("-" * 50)

# 示例：将YAML转换为JSON
yaml_to_json('experiment1.yml', 'experiment1.json')

# 示例：创建Python对象并转换为YAML
person = {
    'name': '李四',
    'age': 30,
    'married': False,
    'children': ['小明', '小红'],
    'address': {
        'street': '上海市浦东新区',
        'city': '上海',
        'zip': '200000'
    }
}

with open('python_to_yaml.yml', 'w', encoding='utf-8') as file:
    yaml.dump(person, file, allow_unicode=True, indent=2)

print("\nPython对象转换为YAML:")
print_yaml_structure('python_to_yaml.yml')
```

## 实验说明

1. **experiment1.yml**: 基本YAML结构示例，包含标量、映射和列表
2. **json_to_yaml.yml**: 展示JSON与YAML的对应关系
3. **app_config.yml**: 应用配置文件示例
4. **docker-compose.yml**: Docker Compose配置示例
5. **github-actions.yml**: GitHub Actions工作流示例
6. **multi_document.yml**: 多文档YAML示例
7. **validate_yaml.py**: Python验证代码，用于验证和转换YAML文件

运行验证代码：
```bash
python validate_yaml.py
```

这将验证所有YAML文件的语法，并打印它们的结构。