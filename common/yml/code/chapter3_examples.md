# 第3章示例代码

## 实验1：锚点与别名

```yaml
# anchors_and_aliases.yml
# 锚点与别名示例
---
# 基本锚点和别名
defaults: &defaults
  timeout: 30
  retries: 3
  log_level: info

production:
  <<: *defaults
  host: prod.example.com
  port: 443

staging:
  <<: *defaults
  host: staging.example.com
  port: 8443
  log_level: debug  # 覆盖默认值

# 嵌套锚点
database: &database
  host: localhost
  port: 5432
  user: admin
  password: secret

services:
  web:
    database: *database
    port: 8080
  api:
    database: *database
    port: 8081
    timeout: 60  # 覆盖默认值

# 多个锚点
http_config: &http_config
  protocol: http
  timeout: 30

https_config: &https_config
  protocol: https
  timeout: 60
  verify_ssl: true

servers:
  web:
    <<: *http_config
    port: 80
  secure_web:
    <<: *https_config
    port: 443
  api:
    <<: *http_config
    port: 8080
  secure_api:
    <<: *https_config
    port: 8443
```

## 实验2：多文档流

```yaml
# multi_document.yml
# 多文档流示例
---
# 文档1：用户信息
name: John Doe
age: 30
email: john@example.com
...
---
# 文档2：用户设置
theme: dark
notifications: true
language: en-US
...
---
# 文档3：用户权限
permissions:
  - read
  - write
  - delete
roles:
  - admin
  - editor
...
---
# 文档4：用户活动
last_login: 2023-05-15T14:30:00Z
login_count: 42
failed_attempts: 2
...
```

## 实验3：高级字符串处理

```yaml
# advanced_strings.yml
# 高级字符串处理示例
---
# 块标量
literal_block: |
  This is a literal block
  It preserves all line breaks
  And indentation exactly as written

folded_block: >
  This is a folded block
  It converts line breaks to spaces
  Creating a single paragraph

# 带缩进的块标量
indented_literal: |2
  This block has 2 spaces of indentation
  All lines are indented by at least 2 spaces
  Relative indentation is preserved

# 带缩进的折叠标量
indented_folded: >2
  This folded block has 2 spaces of indentation
  Line breaks are converted to spaces
  But the overall indentation is preserved

# 特殊字符
escaped_chars: "This contains a \"quote\" and a \\ backslash"
unicode_chars: "Unicode: 中文测试"
newlines: "Line 1\nLine 2"
tabs: "Column1\tColumn2"

# 多行字符串保留换行
multiline_with_breaks: |-
  First line
  Second line
  Third line

# 多行字符串去除末尾换行
multiline_without_break: |+
  First line
  Second line
  Third line
```

## 实验4：自定义类型

```yaml
# custom_types.yml
# 自定义类型示例
---
# 自定义类型定义
person: !person
  name: John Doe
  age: 30
  email: john@example.com

address: !address
  street: 123 Main St
  city: Anytown
  zip: 12345

# 复杂自定义类型
company: !company
  name: Tech Corp
  founded: 2010
  employees: 150
  address: !address
    street: 456 Business Ave
    city: San Francisco
    zip: 94105
  ceo: !person
    name: Jane Smith
    age: 45
    email: jane@techcorp.com

# 全局标签
string_value: !!str 123
integer_value: !!int "456"
float_value: !!float "3.14"
boolean_value: !!bool "true"
null_value: !!null "null"
timestamp_value: !!timestamp "2023-05-15T14:30:00Z"
binary_value: !!binary R0lGODlhDAAMAIQAAP//9/X17unp5WZmZgAAAOfn515eXvPz7Y6OjuDg4J+fn5OTk6enp56enmleECcgggoBADs=
```

## 实验5：合并键示例

```yaml
# merge_keys.yml
# 合并键示例
---
# 单个映射合并
base_config: &base_config
  timeout: 30
  retries: 3
  log_level: info

development:
  <<: *base_config
  debug: true
  host: dev.example.com

# 多个映射合并
personal_info: &personal_info
  name: Jane
  age: 25

contact_info: &contact_info
  email: jane@example.com
  phone: 555-1234

full_profile:
  <<: *personal_info
  <<: *contact_info
  occupation: Designer

# 合并顺序与覆盖
first: &first
  key1: value1
  key2: value2

second: &second
  key2: new_value2  # 会覆盖first中的key2
  key3: value3

merged:
  <<: *first
  <<: *second
  key4: value4
```

## 实验6：条件与循环模拟

```yaml
# conditional_and_loop.yml
# 条件与循环模拟示例
---
# 使用锚点模拟条件
default_config: &default_config
  timeout: 30
  retries: 3

development_config: &development_config
  <<: *default_config
  debug: true
  log_level: debug

production_config: &production_config
  <<: *default_config
  debug: false
  log_level: info

# 根据环境选择配置
environment: development
config: 
  <<: *development_config

# 使用序列模拟循环
server_template: &server_template
  cpu: 2
  memory: 4GB
  disk: 20GB
  os: Ubuntu 20.04

servers:
  - <<: *server_template
    name: web-1
    ip: 192.168.1.10
  - <<: *server_template
    name: web-2
    ip: 192.168.1.11
  - <<: *server_template
    name: web-3
    ip: 192.168.1.12
  - <<: *server_template
    name: db-1
    ip: 192.168.1.20
    cpu: 4
    memory: 8GB
    disk: 100GB
```

## 实验7：YAML Schema验证

```yaml
# schema_example.yml
# YAML Schema验证示例
---
# 用户数据
user:
  name: John Doe
  age: 30
  email: john@example.com
  address:
    street: 123 Main St
    city: Anytown
    zip: 12345

# 产品数据
product:
  id: 12345
  name: "Awesome Product"
  price: 99.99
  in_stock: true
  tags:
    - electronics
    - gadgets
    - new
```

## Python验证代码

```python
# advanced_features.py
import yaml
import json
from datetime import datetime

def test_anchors_and_aliases():
    """测试锚点与别名"""
    print("=== 锚点与别名测试 ===")
    with open('anchors_and_aliases.yml', 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
        print("生产环境配置:")
        print(json.dumps(data['production'], indent=2))
        print("\nAPI服务配置:")
        print(json.dumps(data['services']['api'], indent=2))
        print("\n安全API服务器配置:")
        print(json.dumps(data['servers']['secure_api'], indent=2))

def test_multi_document():
    """测试多文档流"""
    print("\n=== 多文档流测试 ===")
    with open('multi_document.yml', 'r', encoding='utf-8') as file:
        documents = list(yaml.safe_load_all(file))
        for i, doc in enumerate(documents, 1):
            print(f"\n文档 {i}:")
            print(json.dumps(doc, indent=2, ensure_ascii=False))

def test_advanced_strings():
    """测试高级字符串处理"""
    print("\n=== 高级字符串处理测试 ===")
    with open('advanced_strings.yml', 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
        
        print("字面量块:")
        print(repr(data['literal_block']))
        print("\n折叠块:")
        print(repr(data['folded_block']))
        print("\n缩进字面量块:")
        print(repr(data['indented_literal']))
        print("\n缩进折叠块:")
        print(repr(data['indented_folded']))
        print("\n特殊字符:")
        print(f"转义字符: {data['escaped_chars']}")
        print(f"Unicode字符: {data['unicode_chars']}")
        print(f"换行符: {repr(data['newlines'])}")
        print(f"制表符: {repr(data['tabs'])}")

def test_custom_types():
    """测试自定义类型"""
    print("\n=== 自定义类型测试 ===")
    with open('custom_types.yml', 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
        print("人物信息:")
        print(json.dumps(data['person'], indent=2, ensure_ascii=False))
        print("\n地址信息:")
        print(json.dumps(data['address'], indent=2, ensure_ascii=False))
        print("\n公司信息:")
        print(json.dumps(data['company'], indent=2, ensure_ascii=False))
        print("\n全局标签:")
        print(f"字符串值: {data['string_value']} (类型: {type(data['string_value']).__name__})")
        print(f"整数值: {data['integer_value']} (类型: {type(data['integer_value']).__name__})")
        print(f"浮点数值: {data['float_value']} (类型: {type(data['float_value']).__name__})")
        print(f"布尔值: {data['boolean_value']} (类型: {type(data['boolean_value']).__name__})")
        print(f"时间戳值: {data['timestamp_value']} (类型: {type(data['timestamp_value']).__name__})")
        print(f"二进制值: {data['binary_value'][:20]}... (类型: {type(data['binary_value']).__name__})")

def test_merge_keys():
    """测试合并键"""
    print("\n=== 合并键测试 ===")
    with open('merge_keys.yml', 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
        print("开发环境配置:")
        print(json.dumps(data['development'], indent=2))
        print("\n完整用户档案:")
        print(json.dumps(data['full_profile'], indent=2))
        print("\n合并结果:")
        print(json.dumps(data['merged'], indent=2))

def test_conditional_and_loop():
    """测试条件与循环模拟"""
    print("\n=== 条件与循环模拟测试 ===")
    with open('conditional_and_loop.yml', 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
        print("当前环境配置:")
        print(json.dumps(data['config'], indent=2))
        print("\n服务器列表:")
        for i, server in enumerate(data['servers']):
            print(f"服务器 {i+1}:")
            print(json.dumps(server, indent=2))

def test_schema_validation():
    """测试Schema验证"""
    print("\n=== Schema验证测试 ===")
    
    # 定义schema
    user_schema = {
        "type": "map",
        "required": True,
        "mapping": {
            "name": {"type": "str", "required": True},
            "age": {"type": "int", "required": True, "range": [0, 150]},
            "email": {"type": "str", "required": False, "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"},
            "address": {
                "type": "map",
                "required": False,
                "mapping": {
                    "street": {"type": "str"},
                    "city": {"type": "str"},
                    "zip": {"type": "str"}
                }
            }
        }
    }
    
    product_schema = {
        "type": "map",
        "required": True,
        "mapping": {
            "id": {"type": "int", "required": True},
            "name": {"type": "str", "required": True},
            "price": {"type": "float", "required": True, "range": [0, None]},
            "in_stock": {"type": "bool", "required": True},
            "tags": {
                "type": "seq",
                "required": False,
                "sequence": [
                    {"type": "str"}
                ]
            }
        }
    }
    
    # 验证YAML数据
    with open('schema_example.yml', 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
        
        # 简单验证（实际应用中应使用专门的验证库）
        def validate_schema(data, schema, path=""):
            errors = []
            
            if schema.get("type") == "map":
                if not isinstance(data, dict):
                    errors.append(f"{path}: Expected map, got {type(data).__name__}")
                    return errors
                
                # 检查必需字段
                for key, value_schema in schema.get("mapping", {}).items():
                    if value_schema.get("required", False) and key not in data:
                        errors.append(f"{path}.{key}: Required field missing")
                    
                    if key in data:
                        errors.extend(validate_schema(data[key], value_schema, f"{path}.{key}"))
            
            elif schema.get("type") == "seq":
                if not isinstance(data, list):
                    errors.append(f"{path}: Expected sequence, got {type(data).__name__}")
                    return errors
                
                item_schema = schema.get("sequence", [{}])[0]
                for i, item in enumerate(data):
                    errors.extend(validate_schema(item, item_schema, f"{path}[{i}]"))
            
            elif schema.get("type") == "str":
                if not isinstance(data, str):
                    errors.append(f"{path}: Expected string, got {type(data).__name__}")
                elif "pattern" in schema:
                    import re
                    if not re.match(schema["pattern"], data):
                        errors.append(f"{path}: String does not match pattern {schema['pattern']}")
            
            elif schema.get("type") == "int":
                if not isinstance(data, int):
                    errors.append(f"{path}: Expected integer, got {type(data).__name__}")
                elif "range" in schema:
                    min_val, max_val = schema["range"]
                    if (min_val is not None and data < min_val) or (max_val is not None and data > max_val):
                        errors.append(f"{path}: Integer {data} out of range {schema['range']}")
            
            elif schema.get("type") == "float":
                if not isinstance(data, (int, float)):
                    errors.append(f"{path}: Expected number, got {type(data).__name__}")
                elif "range" in schema:
                    min_val, max_val = schema["range"]
                    if (min_val is not None and data < min_val) or (max_val is not None and data > max_val):
                        errors.append(f"{path}: Number {data} out of range {schema['range']}")
            
            elif schema.get("type") == "bool":
                if not isinstance(data, bool):
                    errors.append(f"{path}: Expected boolean, got {type(data).__name__}")
            
            return errors
        
        # 验证用户数据
        user_errors = validate_schema(data['user'], user_schema, "user")
        if user_errors:
            print("用户数据验证失败:")
            for error in user_errors:
                print(f"  - {error}")
        else:
            print("用户数据验证成功")
        
        # 验证产品数据
        product_errors = validate_schema(data['product'], product_schema, "product")
        if product_errors:
            print("产品数据验证失败:")
            for error in product_errors:
                print(f"  - {error}")
        else:
            print("产品数据验证成功")

def test_security():
    """测试YAML安全性"""
    print("\n=== YAML安全性测试 ===")
    
    # 安全加载
    safe_yaml = "name: John\nage: 30"
    safe_data = yaml.safe_load(safe_yaml)
    print(f"安全加载: {safe_data}")
    
    # 不安全加载（仅作演示，实际应用中避免使用）
    try:
        # 这里只是演示，实际不要加载不可信的YAML
        unsafe_yaml = "name: !!python/object/apply:os.system ['echo Hello']"
        # unsafe_data = yaml.load(unsafe_yaml)  # 不安全，可能执行代码
        print("不安全加载示例已跳过，以避免执行潜在危险代码")
    except Exception as e:
        print(f"不安全加载失败: {e}")

# 运行所有测试
test_anchors_and_aliases()
test_multi_document()
test_advanced_strings()
test_custom_types()
test_merge_keys()
test_conditional_and_loop()
test_schema_validation()
test_security()
```

## 实验说明

1. **anchors_and_aliases.yml**: 锚点与别名示例，展示基本锚点、嵌套锚点和多个锚点的使用
2. **multi_document.yml**: 多文档流示例，包含多个独立的YAML文档
3. **advanced_strings.yml**: 高级字符串处理示例，展示块标量、特殊字符处理等
4. **custom_types.yml**: 自定义类型示例，展示自定义类型和全局标签的使用
5. **merge_keys.yml**: 合并键示例，展示单个映射合并、多个映射合并和合并顺序
6. **conditional_and_loop.yml**: 条件与循环模拟示例，展示如何使用锚点和序列模拟编程逻辑
7. **schema_example.yml**: YAML Schema验证示例，包含用户数据和产品数据
8. **advanced_features.py**: Python验证代码，用于测试所有高级特性

运行验证代码：
```bash
python advanced_features.py
```

这将验证所有YAML文件的高级特性，并展示它们的用法和效果。