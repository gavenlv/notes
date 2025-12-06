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

## 实验8：语法解析与锚点机制深度分析

```yaml
# syntax_analysis.yml
# 语法解析与锚点机制深度分析示例
---
# 锚点引用解析
base_configuration: &base
  timeout: 30
  retries: 3
  log_level: info

# 复杂锚点引用
server_template: &server
  cpu: 2
  memory: 4GB
  os: ubuntu
  services:
    - nginx
    - docker

# 多级锚点引用
network_config: &network
  subnet: 192.168.1.0/24
  gateway: 192.168.1.1
  dns: [8.8.8.8, 8.8.4.4]

# 锚点引用组合
production_servers:
  web_server:
    <<: *server
    <<: *network
    name: web-prod-01
    ip: 192.168.1.10
  db_server:
    <<: *server
    <<: *network
    name: db-prod-01
    ip: 192.168.1.20
    cpu: 8
    memory: 16GB
    services:
      - postgresql
      - redis

# 锚点循环引用检测（应避免）
# 注意：以下示例展示应避免的循环引用
circular_reference_a: &circular_a
  name: "Reference A"
  reference: *circular_b

circular_reference_b: &circular_b
  name: "Reference B"
  reference: *circular_a
```

## 实验9：语法解析与多文档流处理

```yaml
# document_parsing.yml
# 语法解析与多文档流处理示例
---
# 文档1：系统配置
system:
  name: production-system
  version: 1.0.0
  environment: production
...
---
# 文档2：应用配置
application:
  name: web-app
  port: 8080
  database:
    host: localhost
    port: 5432
    name: app_db
...
---
# 文档3：安全配置
security:
  ssl:
    enabled: true
    certificate: /etc/ssl/cert.pem
    key: /etc/ssl/key.pem
  firewall:
    enabled: true
    rules:
      - action: allow
        port: 80
      - action: allow
        port: 443
      - action: deny
        port: 22
...
---
# 文档4：监控配置
monitoring:
  metrics:
    enabled: true
    interval: 30s
  logging:
    level: info
    format: json
    output: /var/log/app.log
...
```

## 实验10：语法解析与自定义类型系统

```yaml
# type_system_parsing.yml
# 语法解析与自定义类型系统示例
---
# 自定义类型定义
custom_types:
  person_type: !person
    schema: &person_schema
      name: string
      age: integer
      email: string
      address: map
  
  address_type: !address
    schema: &address_schema
      street: string
      city: string
      zip: string
      country: string

# 类型验证实例
valid_person: !person
  name: "Alice Johnson"
  age: 28
  email: "alice@example.com"
  address: !address
    street: "789 Oak Street"
    city: "Springfield"
    zip: "12345"
    country: "USA"

# 类型错误实例（应被验证器捕获）
invalid_person: !person
  name: "Bob Smith"
  age: "thirty"  # 错误：应为整数
  email: "not-an-email"  # 错误：无效邮箱格式
  address: !address
    street: 123  # 错误：应为字符串
    city: "New York"
    zip: "10001"
    country: "USA"

# 复杂类型嵌套
company: !company
  name: "Tech Solutions Inc."
  founded: 2015
  employees: 250
  headquarters: !address
    street: "456 Tech Park"
    city: "San Francisco"
    zip: "94105"
    country: "USA"
  departments:
    - !department
      name: "Engineering"
      manager: !person
        name: "Carol Davis"
        age: 35
        email: "carol@techsolutions.com"
      employees: 120
    - !department
      name: "Sales"
      manager: !person
        name: "David Wilson"
        age: 42
        email: "david@techsolutions.com"
      employees: 80
```

## 实验11：语法解析深度验证代码

```python
# syntax_parser.py
import yaml
import re
from typing import Dict, List, Any, Set, Tuple
from collections import deque

class YAMLSyntaxParser:
    """YAML语法解析器"""
    
    def __init__(self):
        self.anchors = {}
        self.aliases = {}
        self.circular_references = []
        self.syntax_errors = []
        self.warnings = []
    
    def parse_anchors_and_aliases(self, file_path: str) -> Dict[str, Any]:
        """解析锚点和别名"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # 解析锚点
            anchor_pattern = r'&([a-zA-Z_][a-zA-Z0-9_]*)'
            anchors = re.findall(anchor_pattern, content)
            
            # 解析别名
            alias_pattern = r'\*([a-zA-Z_][a-zA-Z0-9_]*)'
            aliases = re.findall(alias_pattern, content)
            
            # 检查未定义的别名
            undefined_aliases = set(aliases) - set(anchors)
            
            # 检查未使用的锚点
            unused_anchors = set(anchors) - set(aliases)
            
            return {
                'anchors': anchors,
                'aliases': aliases,
                'undefined_aliases': list(undefined_aliases),
                'unused_anchors': list(unused_anchors)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def detect_circular_references(self, file_path: str) -> List[List[str]]:
        """检测循环引用"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # 构建引用图
            graph = {}
            
            # 解析锚点和别名对
            lines = content.split('\n')
            current_anchor = None
            
            for i, line in enumerate(lines, 1):
                # 查找锚点定义
                anchor_match = re.search(r'^\s*([a-zA-Z_][a-zA-Z0-9_]*):\s*&([a-zA-Z_][a-zA-Z0-9_]*)', line)
                if anchor_match:
                    current_anchor = anchor_match.group(2)
                    graph[current_anchor] = set()
                
                # 查找别名引用
                alias_match = re.search(r'\*([a-zA-Z_][a-zA-Z0-9_]*)', line)
                if alias_match and current_anchor:
                    referenced_anchor = alias_match.group(1)
                    graph[current_anchor].add(referenced_anchor)
            
            # 检测循环引用
            def find_cycles():
                visited = set()
                recursion_stack = set()
                cycles = []
                
                def dfs(node, path):
                    if node in recursion_stack:
                        cycle_start = path.index(node)
                        cycles.append(path[cycle_start:] + [node])
                        return
                    
                    if node in visited:
                        return
                    
                    visited.add(node)
                    recursion_stack.add(node)
                    
                    for neighbor in graph.get(node, set()):
                        dfs(neighbor, path + [node])
                    
                    recursion_stack.remove(node)
                
                for node in graph:
                    if node not in visited:
                        dfs(node, [])
                
                return cycles
            
            return find_cycles()
            
        except Exception as e:
            return [['error', str(e)]]
    
    def analyze_document_structure(self, file_path: str) -> Dict[str, Any]:
        """分析文档结构"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                documents = list(yaml.safe_load_all(file))
            
            analysis = {
                'document_count': len(documents),
                'documents': [],
                'structure_analysis': {}
            }
            
            for i, doc in enumerate(documents, 1):
                doc_analysis = {
                    'document_number': i,
                    'type': type(doc).__name__,
                    'size': len(str(doc)),
                    'keys': list(doc.keys()) if isinstance(doc, dict) else [],
                    'nested_depth': self._calculate_nested_depth(doc)
                }
                analysis['documents'].append(doc_analysis)
            
            # 结构分析
            if documents:
                analysis['structure_analysis'] = {
                    'average_depth': sum(d['nested_depth'] for d in analysis['documents']) / len(documents),
                    'max_depth': max(d['nested_depth'] for d in analysis['documents']),
                    'total_keys': sum(len(d['keys']) for d in analysis['documents']),
                    'unique_keys': len(set(key for d in analysis['documents'] for key in d['keys']))
                }
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_nested_depth(self, obj: Any, current_depth: int = 0) -> int:
        """计算嵌套深度"""
        if isinstance(obj, dict):
            if not obj:
                return current_depth + 1
            return max(self._calculate_nested_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return current_depth + 1
            return max(self._calculate_nested_depth(item, current_depth + 1) for item in obj)
        else:
            return current_depth
    
    def validate_yaml_syntax(self, file_path: str) -> Dict[str, Any]:
        """验证YAML语法"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # 基本语法检查
            syntax_checks = {
                'indentation_errors': self._check_indentation(content),
                'duplicate_keys': self._check_duplicate_keys(content),
                'invalid_characters': self._check_invalid_characters(content),
                'unclosed_quotes': self._check_unclosed_quotes(content),
                'invalid_anchors': self._check_invalid_anchors(content)
            }
            
            # 尝试解析YAML
            try:
                yaml.safe_load(content)
                syntax_checks['parsable'] = True
            except yaml.YAMLError as e:
                syntax_checks['parsable'] = False
                syntax_checks['parse_error'] = str(e)
            
            return syntax_checks
            
        except Exception as e:
            return {'error': str(e)}
    
    def _check_indentation(self, content: str) -> List[Tuple[int, str]]:
        """检查缩进错误"""
        errors = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            if line.strip() and not line.startswith(' '):
                # 检查是否有混合制表符和空格
                if '\t' in line:
                    errors.append((i, "混合使用制表符和空格"))
                
                # 检查缩进级别
                if i > 1 and lines[i-2].strip() and not lines[i-2].startswith(' '):
                    # 前一行有内容但未缩进，当前行也不应缩进
                    if line.startswith(' '):
                        errors.append((i, "意外的缩进"))
        
        return errors
    
    def _check_duplicate_keys(self, content: str) -> List[Tuple[int, str]]:
        """检查重复键"""
        errors = []
        lines = content.split('\n')
        key_pattern = r'^\s*([a-zA-Z_][a-zA-Z0-9_]*):'
        
        current_keys = set()
        current_indent = 0
        
        for i, line in enumerate(lines, 1):
            match = re.match(key_pattern, line)
            if match:
                key = match.group(1)
                indent = len(line) - len(line.lstrip())
                
                if indent == current_indent and key in current_keys:
                    errors.append((i, f"重复键: {key}"))
                elif indent < current_indent:
                    # 缩进减少，重置当前键集合
                    current_keys = set()
                    current_indent = indent
                
                current_keys.add(key)
        
        return errors
    
    def _check_invalid_characters(self, content: str) -> List[Tuple[int, str]]:
        """检查无效字符"""
        errors = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # 检查控制字符（除了制表符和换行符）
            for j, char in enumerate(line):
                if ord(char) < 32 and char not in ('\t', '\n', '\r'):
                    errors.append((i, f"位置 {j+1}: 无效控制字符"))
        
        return errors
    
    def _check_unclosed_quotes(self, content: str) -> List[Tuple[int, str]]:
        """检查未闭合的引号"""
        errors = []
        lines = content.split('\n')
        
        in_quotes = False
        quote_char = None
        
        for i, line in enumerate(lines, 1):
            j = 0
            while j < len(line):
                char = line[j]
                
                if not in_quotes and char in ('"', "'"):
                    in_quotes = True
                    quote_char = char
                elif in_quotes and char == quote_char:
                    # 检查转义
                    if j > 0 and line[j-1] == '\\':
                        j += 1
                        continue
                    in_quotes = False
                    quote_char = None
                
                j += 1
        
        if in_quotes:
            errors.append((len(lines), f"未闭合的{quote_char}引号"))
        
        return errors
    
    def _check_invalid_anchors(self, content: str) -> List[Tuple[int, str]]:
        """检查无效锚点"""
        errors = []
        lines = content.split('\n')
        
        anchor_pattern = r'&([a-zA-Z_][a-zA-Z0-9_]*)'
        
        for i, line in enumerate(lines, 1):
            matches = re.findall(anchor_pattern, line)
            for anchor in matches:
                if not anchor.replace('_', '').isalnum():
                    errors.append((i, f"无效锚点名称: {anchor}"))
        
        return errors
    
    def comprehensive_syntax_analysis(self, file_path: str) -> Dict[str, Any]:
        """综合语法分析"""
        analysis = {
            'file': file_path,
            'anchor_analysis': self.parse_anchors_and_aliases(file_path),
            'circular_references': self.detect_circular_references(file_path),
            'document_structure': self.analyze_document_structure(file_path),
            'syntax_validation': self.validate_yaml_syntax(file_path)
        }
        
        return analysis
    
    def print_syntax_analysis(self, file_path: str):
        """打印语法分析结果"""
        print(f"\n语法分析: {file_path}")
        print("=" * 60)
        
        analysis = self.comprehensive_syntax_analysis(file_path)
        
        if 'error' in analysis:
            print(f"分析失败: {analysis['error']}")
            return
        
        # 打印锚点分析
        anchor_analysis = analysis['anchor_analysis']
        print("\n锚点与别名分析:")
        print(f"  锚点数量: {len(anchor_analysis.get('anchors', []))}")
        print(f"  别名数量: {len(anchor_analysis.get('aliases', []))}")
        
        if anchor_analysis.get('undefined_aliases'):
            print(f"  未定义别名: {anchor_analysis['undefined_aliases']}")
        else:
            print("  未定义别名: ✓ 无")
        
        if anchor_analysis.get('unused_anchors'):
            print(f"  未使用锚点: {anchor_analysis['unused_anchors']}")
        else:
            print("  未使用锚点: ✓ 无")
        
        # 打印循环引用检测
        circular_refs = analysis['circular_references']
        if circular_refs and not (len(circular_refs) == 1 and circular_refs[0][0] == 'error'):
            print("\n循环引用检测:")
            for cycle in circular_refs:
                print(f"  ⚠ 循环引用: {' -> '.join(cycle)}")
        else:
            print("\n循环引用检测: ✓ 无循环引用")
        
        # 打印文档结构分析
        doc_structure = analysis['document_structure']
        if 'document_count' in doc_structure:
            print(f"\n文档结构分析:")
            print(f"  文档数量: {doc_structure['document_count']}")
            print(f"  平均嵌套深度: {doc_structure['structure_analysis'].get('average_depth', 0):.2f}")
            print(f"  最大嵌套深度: {doc_structure['structure_analysis'].get('max_depth', 0)}")
            print(f"  总键数量: {doc_structure['structure_analysis'].get('total_keys', 0)}")
            print(f"  唯一键数量: {doc_structure['structure_analysis'].get('unique_keys', 0)}")
        
        # 打印语法验证
        syntax_validation = analysis['syntax_validation']
        print(f"\n语法验证:")
        print(f"  可解析: {'✓' if syntax_validation.get('parsable') else '✗'}")
        
        if not syntax_validation.get('parsable'):
            print(f"  解析错误: {syntax_validation.get('parse_error')}")
        
        # 检查各种语法错误
        error_types = ['indentation_errors', 'duplicate_keys', 'invalid_characters', 'unclosed_quotes', 'invalid_anchors']
        
        for error_type in error_types:
            errors = syntax_validation.get(error_type, [])
            if errors:
                print(f"  {error_type.replace('_', ' ').title()}:")
                for line_num, message in errors[:3]:  # 只显示前3个错误
                    print(f"    第{line_num}行: {message}")
                if len(errors) > 3:
                    print(f"    ... 还有 {len(errors) - 3} 个错误")
            else:
                print(f"  {error_type.replace('_', ' ').title()}: ✓ 无错误")

# 使用示例
if __name__ == "__main__":
    parser = YAMLSyntaxParser()
    
    # 分析所有YAML文件
    test_files = [
        'anchors_and_aliases.yml',
        'multi_document.yml',
        'advanced_strings.yml',
        'custom_types.yml',
        'merge_keys.yml',
        'conditional_and_loop.yml',
        'schema_example.yml',
        'syntax_analysis.yml',
        'document_parsing.yml',
        'type_system_parsing.yml'
    ]
    
    for test_file in test_files:
        parser.print_syntax_analysis(test_file)
        print("-" * 60)

# 高级语法分析工具
def analyze_yaml_complexity(file_path: str) -> Dict[str, Any]:
    """分析YAML文件复杂度"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            data = yaml.safe_load(content)
        
        def calculate_complexity(obj: Any, depth: int = 0) -> Dict[str, int]:
            """计算复杂度指标"""
            if isinstance(obj, dict):
                complexity = {
                    'nodes': 1,
                    'leaves': 0,
                    'max_depth': depth,
                    'total_depth': depth
                }
                
                for value in obj.values():
                    child_complexity = calculate_complexity(value, depth + 1)
                    complexity['nodes'] += child_complexity['nodes']
                    complexity['leaves'] += child_complexity['leaves']
                    complexity['max_depth'] = max(complexity['max_depth'], child_complexity['max_depth'])
                    complexity['total_depth'] += child_complexity['total_depth']
                
                return complexity
            
            elif isinstance(obj, list):
                complexity = {
                    'nodes': 1,
                    'leaves': 0,
                    'max_depth': depth,
                    'total_depth': depth
                }
                
                for item in obj:
                    child_complexity = calculate_complexity(item, depth + 1)
                    complexity['nodes'] += child_complexity['nodes']
                    complexity['leaves'] += child_complexity['leaves']
                    complexity['max_depth'] = max(complexity['max_depth'], child_complexity['max_depth'])
                    complexity['total_depth'] += child_complexity['total_depth']
                
                return complexity
            
            else:
                return {
                    'nodes': 1,
                    'leaves': 1,
                    'max_depth': depth,
                    'total_depth': depth
                }
        
        complexity = calculate_complexity(data)
        
        return {
            'file': file_path,
            'complexity': complexity,
            'average_depth': complexity['total_depth'] / complexity['nodes'] if complexity['nodes'] > 0 else 0,
            'leaf_ratio': complexity['leaves'] / complexity['nodes'] if complexity['nodes'] > 0 else 0
        }
        
    except Exception as e:
        return {'error': str(e)}

# 运行复杂度分析
print("\nYAML文件复杂度分析:")
print("=" * 60)

for test_file in test_files:
    result = analyze_yaml_complexity(test_file)
    if 'error' not in result:
        print(f"\n{test_file}:")
        print(f"  节点总数: {result['complexity']['nodes']}")
        print(f"  叶子节点: {result['complexity']['leaves']}")
        print(f"  最大深度: {result['complexity']['max_depth']}")
        print(f"  平均深度: {result['average_depth']:.2f}")
        print(f"  叶子比例: {result['leaf_ratio']:.2f}")
    else:
        print(f"\n{test_file}: 分析失败 - {result['error']}")
```

## 实验说明

1. **anchors_and_aliases.yml**: 锚点与别名示例，展示基本锚点、嵌套锚点和多个锚点的使用
2. **multi_document.yml**: 多文档流示例，包含多个独立的YAML文档
3. **advanced_strings.yml**: 高级字符串处理示例，展示块标量、特殊字符处理等
4. **custom_types.yml**: 自定义类型示例，展示自定义类型和全局标签的使用
5. **merge_keys.yml**: 合并键示例，展示单个映射合并、多个映射合并和合并顺序
6. **conditional_and_loop.yml**: 条件与循环模拟示例，展示如何使用锚点和序列模拟编程逻辑
7. **schema_example.yml**: YAML Schema验证示例，包含用户数据和产品数据
8. **syntax_analysis.yml**: 语法解析与锚点机制深度分析示例
9. **document_parsing.yml**: 语法解析与多文档流处理示例
10. **type_system_parsing.yml**: 语法解析与自定义类型系统示例
11. **advanced_features.py**: 基础验证代码
12. **syntax_parser.py**: 高级语法解析和验证代码

运行验证代码：
```bash
# 基础验证
python advanced_features.py

# 高级语法分析
python syntax_parser.py
```

这将验证所有YAML文件的高级特性，进行深度语法分析，检测循环引用、语法错误，并分析文档结构和复杂度。