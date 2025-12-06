# 第5章示例代码

## 实验1：YAML语法规范演进

```yaml
# yaml-1.0-example.yml
# YAML 1.0 语法示例
%YAML 1.0
---
# 1.0版本特性
basic_types:
  string: "plain string"
  number: 123
  boolean: true
  null_value: null

# 序列和映射
sequence:
  - item1
  - item2
  - item3

mapping:
  key1: value1
  key2: value2

# 多文档流
---
document2:
  content: "second document"
```

```yaml
# yaml-1.1-example.yml
# YAML 1.1 语法示例
%YAML 1.1
---
# 1.1版本新增特性
# 显式类型标签
tagged_values:
  !!str "explicit string"
  !!int 123
  !!bool true
  !!null null

# 合并键（<<）
base_config: &base
  host: "localhost"
  port: 8080
  timeout: 30

app_config:
  <<: *base
  name: "MyApp"
  env: "production"

# 锚点和别名
user_template: &user
  id: !!int
  name: !!str
  email: !!str

user1:
  <<: *user
  id: 1
  name: "Alice"
  email: "alice@example.com"

user2:
  <<: *user
  id: 2
  name: "Bob"
  email: "bob@example.com"
```

```yaml
# yaml-1.2-example.yml
# YAML 1.2 语法示例
%YAML 1.2
---
# 1.2版本改进
# JSON兼容性改进
json_compatible:
  "string": "value"
  "number": 123.45
  "boolean": true
  "null": null
  "array": [1, 2, 3]
  "object": {"key": "value"}

# 改进的字符串处理
strings:
  plain: plain string
  single_quoted: 'single quoted'
  double_quoted: "double quoted"
  literal: |
    literal block
    with multiple lines
  folded: >
    folded block that
    spans multiple lines

# 改进的标签处理
tags:
  !!str "explicit string"
  !!int "123"  # 字符串转换为整数
  !!float "3.14"  # 字符串转换为浮点数
  !!bool "true"  # 字符串转换为布尔值
```

## 实验2：解析器工作原理

```yaml
# parsing-example.yml
# 解析器处理示例
# 词法分析阶段
lexical_elements:
  # 标识符
  simple_key: value
  "quoted key": "quoted value"
  'single quoted': 'single quoted value'

  # 标量
  scalar_types:
    plain: plain scalar
    single_quoted: 'single quoted scalar'
    double_quoted: "double quoted scalar with \\n escape"
    literal: |
      literal block scalar
      with multiple lines
    folded: >
      folded block scalar
      that spans lines

  # 集合
  sequence: [item1, item2, item3]
  mapping: {key1: value1, key2: value2}

# 语法分析阶段
syntax_structure:
  # 文档结构
  document: &doc_anchor
    metadata:
      version: 1.0
      author: "YAML Parser"
    content:
      - section1
      - section2

  # 流样式
  flow_styles:
    inline_sequence: [a, b, c]
    inline_mapping: {x: 1, y: 2}

  # 块样式
  block_styles:
    block_sequence:
      - first item
      - second item
      - third item
    block_mapping:
      key1: value1
      key2: value2
      nested:
        subkey: subvalue

# 语义分析阶段
semantic_elements:
  # 锚点和别名
  template: &template
    type: "object"
    properties: {}
    required: []

  user_schema:
    <<: *template
    properties:
      id: {type: "integer"}
      name: {type: "string"}
    required: [id, name]

  # 合并键
  base_settings: &base
    logging:
      level: "info"
      format: "json"
    database:
      host: "localhost"
      port: 5432

  app_settings:
    <<: *base
    app:
      name: "MyApp"
      version: "1.0.0"
```

## 实验3：类型系统与标签机制

```yaml
# type-system-example.yml
# 类型系统示例
# 核心标量类型
scalar_types:
  # 字符串类型
  string_types:
    plain: plain string
    single_quoted: 'single quoted'
    double_quoted: "double quoted with \\"quotes\\""
    literal: |
      literal
      multi-line
      string
    folded: >
      folded multi-line
      string that continues

  # 数值类型
  numeric_types:
    integer: 42
    negative_int: -123
    hex_int: 0x2A
    octal_int: 0o52
    binary_int: 0b101010
    float: 3.14159
    scientific: 6.02e23
    infinity: .inf
    negative_infinity: -.inf
    not_a_number: .nan

  # 布尔类型
  boolean_types:
    true_values: [true, True, TRUE, yes, Yes, YES, on, On, ON]
    false_values: [false, False, FALSE, no, No, NO, off, Off, OFF]

  # 空值
  null_values: [null, Null, NULL, ~]

  # 时间类型
  timestamp_types:
    iso8601: 2001-12-15T02:59:43.1Z
    spaced: 2001-12-14 21:59:43.10 -5
    date: 2002-12-14

# 显式类型标签
explicit_tags:
  # 核心类型标签
  core_tags:
    str_tag: !!str "123"
    int_tag: !!int "456"
    float_tag: !!float "3.14"
    bool_tag: !!bool "true"
    null_tag: !!null ""

  # 特定类型标签
  specific_tags:
    binary: !!binary |
      R0lGODlhDAAMAIQAAP//9/X
      17unp5WZmZgAAAOfn515eXv
      Pz7Y6OjuDg4J+fn5OTk6enp
      56enmleECcgggoBADs=
    timestamp: !!timestamp "2001-12-15T02:59:43.1Z"
    set: !!set
      ? item1
      ? item2
      ? item3
    omap: !!omap
      - key1: value1
      - key2: value2
      - key3: value3

# 自定义类型标签
custom_tags:
  # 自定义标量类型
  custom_scalar: !custom_type "custom value"
  
  # 自定义集合类型
  custom_sequence: !custom_list
    - item1
    - item2
    - item3
  
  custom_mapping: !custom_map
    key1: value1
    key2: value2

  # 复杂自定义类型
  person: !person
    name: "John Doe"
    age: 30
    email: "john@example.com"
    address: !address
      street: "123 Main St"
      city: "Anytown"
      zip: "12345"
```

## 实验4：锚点与别名机制

```yaml
# anchor-alias-example.yml
# 锚点与别名机制示例
# 基础锚点使用
base_config: &base_config
  app:
    name: "MyApplication"
    version: "1.0.0"
  database:
    host: "localhost"
    port: 5432
    name: "myapp"

# 别名引用
development_config:
  <<: *base_config
  app:
    env: "development"
    debug: true
  database:
    name: "myapp_dev"

production_config:
  <<: *base_config
  app:
    env: "production"
    debug: false
  database:
    host: "prod-db.example.com"
    name: "myapp_prod"

# 嵌套锚点
user_template: &user_template
  schema:
    type: "object"
    properties:
      id:
        type: "integer"
        minimum: 1
      name:
        type: "string"
        minLength: 1
      email:
        type: "string"
        format: "email"
    required: [id, name, email]

admin_template: &admin_template
  <<: *user_template
  schema:
    properties:
      permissions:
        type: "array"
        items:
          type: "string"
          enum: ["read", "write", "delete"]
    required: [id, name, email, permissions]

# 实际用户数据
user1:
  <<: *user_template
  data:
    id: 1
    name: "Alice"
    email: "alice@example.com"

admin1:
  <<: *admin_template
  data:
    id: 100
    name: "Admin User"
    email: "admin@example.com"
    permissions: ["read", "write", "delete"]

# 复杂锚点结构
api_endpoints: &api_base
  base_url: "https://api.example.com"
  version: "v1"
  headers:
    Content-Type: "application/json"
    Accept: "application/json"

users_endpoint:
  <<: *api_base
  path: "/users"
  methods: ["GET", "POST", "PUT", "DELETE"]
  parameters:
    - name: "page"
      type: "integer"
      required: false
    - name: "limit"
      type: "integer"
      required: false

posts_endpoint:
  <<: *api_base
  path: "/posts"
  methods: ["GET", "POST"]
  parameters:
    - name: "user_id"
      type: "integer"
      required: true

# 循环引用检测（应避免）
# node1: &node1
#   name: "Node 1"
#   next: *node2
# 
# node2: &node2
#   name: "Node 2"
#   next: *node1
```

## 实验5：合并键机制

```yaml
# merge-key-example.yml
# 合并键机制示例
# 基础合并键使用
base_settings: &base_settings
  logging:
    level: "info"
    format: "json"
    output: "console"
  database:
    pool:
      min: 5
      max: 20
      idle_timeout: 300

# 单层合并
development: &dev_settings
  <<: *base_settings
  logging:
    level: "debug"
  database:
    host: "localhost"
    name: "dev_db"

production: &prod_settings
  <<: *base_settings
  logging:
    level: "warn"
    output: "file"
  database:
    host: "prod-db.example.com"
    name: "prod_db"
    pool:
      min: 10
      max: 50

# 多层合并
app_base: &app_base
  app:
    name: "MyApp"
    version: "1.0.0"
  server:
    port: 8080
    timeout: 30

logging_base: &logging_base
  logging:
    level: "info"
    handlers:
      - type: "console"
        format: "simple"
      - type: "file"
        path: "/var/log/app.log"

complete_config:
  <<: [*app_base, *logging_base]
  app:
    env: "production"
    debug: false
  server:
    host: "0.0.0.0"
  logging:
    level: "warn"
    handlers:
      - type: "file"
        path: "/var/log/app-prod.log"
        max_size: "100MB"

# 复杂合并场景
user_profile_base: &user_profile_base
  profile:
    settings:
      theme: "light"
      language: "en"
      notifications: true
    preferences:
      email_notifications: true
      push_notifications: false

admin_profile_base: &admin_profile_base
  profile:
    settings:
      theme: "dark"
      admin_access: true
    permissions:
      - "user_management"
      - "content_moderation"
      - "system_configuration"

user_config:
  <<: *user_profile_base
  user:
    id: 1
    name: "Regular User"

admin_config:
  <<: [*user_profile_base, *admin_profile_base]
  user:
    id: 100
    name: "Administrator"
    role: "admin"
  profile:
    settings:
      theme: "dark"  # 覆盖为dark
      language: "en"  # 保持不变
      admin_access: true  # 新增
    preferences:
      email_notifications: true  # 保持不变
      push_notifications: false  # 保持不变
    permissions:  # 新增权限
      - "user_management"
      - "content_moderation"
      - "system_configuration"
```

## 实验6：多文档流处理

```yaml
# multi-document-example.yml
# 多文档流示例
---
# 文档1：配置元数据
%YAML 1.2
%TAG ! tag:example.com,2024:app/
---
metadata:
  version: "1.0.0"
  created: 2024-01-15T10:30:00Z
  author: "YAML Processor"
  description: "Application configuration"

---
# 文档2：应用配置
app:
  name: "MyApplication"
  version: "1.0.0"
  environment: "production"
  
server:
  host: "0.0.0.0"
  port: 8080
  ssl:
    enabled: true
    cert_file: "/etc/ssl/cert.pem"
    key_file: "/etc/ssl/key.pem"

---
# 文档3：数据库配置
database:
  primary:
    host: "db-primary.example.com"
    port: 5432
    name: "app_primary"
    user: "app_user"
    password: "${DB_PASSWORD}"
    
  replica:
    host: "db-replica.example.com"
    port: 5432
    name: "app_replica"
    user: "app_user"
    password: "${DB_PASSWORD}"

---
# 文档4：功能标志
feature_flags:
  new_ui: true
  beta_features: false
  experimental_api: true
  
  rollout:
    percentage: 25
    users: ["user1", "user2", "user3"]

---
# 文档5：监控配置
monitoring:
  metrics:
    enabled: true
    interval: 30
    exporters:
      - type: "prometheus"
        port: 9090
      - type: "statsd"
        host: "localhost"
        port: 8125
        
  logging:
    level: "info"
    format: "json"
    outputs:
      - type: "file"
        path: "/var/log/app.log"
        max_size: "100MB"
      - type: "stdout"

---
# 文档6：自定义类型定义
!app/ConfigSchema
name: "Application Configuration Schema"
version: "1.0"

properties:
  app:
    type: "object"
    properties:
      name: {type: "string"}
      version: {type: "string"}
      environment: {type: "string", enum: ["development", "staging", "production"]}
    required: [name, version, environment]
    
  server:
    type: "object"
    properties:
      host: {type: "string"}
      port: {type: "integer", minimum: 1, maximum: 65535}
      ssl:
        type: "object"
        properties:
          enabled: {type: "boolean"}
          cert_file: {type: "string"}
          key_file: {type: "string"}
        required: [enabled]
    required: [host, port]
```

## Python验证代码

```python
# syntax_deep_analysis.py
import yaml
import re
from datetime import datetime
from pathlib import Path

class YAMLDeepParser:
    """YAML语法深度解析器"""
    
    def __init__(self):
        self.analysis_results = {}
        
    def analyze_yaml_version(self, content):
        """分析YAML版本特性"""
        version_info = {
            'version': 'unknown',
            'features': []
        }
        
        # 检测YAML指令
        if '%YAML 1.0' in content:
            version_info['version'] = '1.0'
            version_info['features'] = ['基础类型', '序列映射', '多文档']
        elif '%YAML 1.1' in content:
            version_info['version'] = '1.1'
            version_info['features'] = ['显式类型标签', '合并键', '锚点别名']
        elif '%YAML 1.2' in content:
            version_info['version'] = '1.2'
            version_info['features'] = ['JSON兼容性', '改进字符串处理', '标签处理']
        else:
            version_info['version'] = '1.2 (默认)'
            version_info['features'] = ['现代YAML特性']
            
        return version_info
    
    def analyze_parsing_stages(self, content):
        """分析解析阶段"""
        stages = {
            'lexical': {'elements': [], 'count': 0},
            'syntactic': {'structures': [], 'count': 0},
            'semantic': {'elements': [], 'count': 0}
        }
        
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # 词法分析：标识符、标量、集合
            if ':' in line and not line.startswith(' '):
                stages['lexical']['elements'].append('标识符')
            elif line.startswith('- '):
                stages['lexical']['elements'].append('序列项')
            elif re.search(r'[\[\]\{\}]', line):
                stages['lexical']['elements'].append('流样式')
            
            # 语法分析：文档结构
            if line == '---':
                stages['syntactic']['structures'].append('文档分隔符')
            elif '&' in line or '*' in line:
                stages['syntactic']['structures'].append('锚点别名')
            elif '<<' in line:
                stages['syntactic']['structures'].append('合并键')
            
            # 语义分析：类型标签
            if '!!' in line:
                stages['semantic']['elements'].append('显式类型标签')
            elif '!' in line and '!!' not in line:
                stages['semantic']['elements'].append('自定义标签')
        
        # 统计数量
        for stage in stages:
            stages[stage]['count'] = len(stages[stage]['elements'])
            
        return stages
    
    def analyze_type_system(self, content):
        """分析类型系统"""
        type_analysis = {
            'scalar_types': {},
            'explicit_tags': [],
            'custom_tags': []
        }
        
        try:
            data = yaml.safe_load(content)
            
            def analyze_value(value, path=""):
                if isinstance(value, str):
                    type_analysis['scalar_types'].setdefault('string', 0)
                    type_analysis['scalar_types']['string'] += 1
                elif isinstance(value, int):
                    type_analysis['scalar_types'].setdefault('integer', 0)
                    type_analysis['scalar_types']['integer'] += 1
                elif isinstance(value, float):
                    type_analysis['scalar_types'].setdefault('float', 0)
                    type_analysis['scalar_types']['float'] += 1
                elif isinstance(value, bool):
                    type_analysis['scalar_types'].setdefault('boolean', 0)
                    type_analysis['scalar_types']['boolean'] += 1
                elif value is None:
                    type_analysis['scalar_types'].setdefault('null', 0)
                    type_analysis['scalar_types']['null'] += 1
                elif isinstance(value, list):
                    type_analysis['scalar_types'].setdefault('sequence', 0)
                    type_analysis['scalar_types']['sequence'] += 1
                    for i, item in enumerate(value):
                        analyze_value(item, f"{path}[{i}]")
                elif isinstance(value, dict):
                    type_analysis['scalar_types'].setdefault('mapping', 0)
                    type_analysis['scalar_types']['mapping'] += 1
                    for key, item in value.items():
                        analyze_value(item, f"{path}.{key}")
            
            if data:
                analyze_value(data)
            
        except yaml.YAMLError:
            pass
        
        # 分析显式标签
        if '!!' in content:
            tags = re.findall(r'!![a-zA-Z]+', content)
            type_analysis['explicit_tags'] = list(set(tags))
        
        # 分析自定义标签
        if '!' in content and '!!' not in content:
            custom_tags = re.findall(r'![a-zA-Z_][a-zA-Z0-9_]*', content)
            type_analysis['custom_tags'] = list(set(custom_tags))
            
        return type_analysis
    
    def analyze_anchor_alias(self, content):
        """分析锚点与别名机制"""
        anchor_analysis = {
            'anchors': [],
            'aliases': [],
            'merge_keys': [],
            'complexity': 0
        }
        
        # 提取锚点
        anchors = re.findall(r'&([a-zA-Z_][a-zA-Z0-9_]*)', content)
        anchor_analysis['anchors'] = list(set(anchors))
        
        # 提取别名
        aliases = re.findall(r'\*([a-zA-Z_][a-zA-Z0-9_]*)', content)
        anchor_analysis['aliases'] = list(set(aliases))
        
        # 提取合并键
        merge_keys = re.findall(r'<<:\s*\*[a-zA-Z_][a-zA-Z0-9_]*', content)
        anchor_analysis['merge_keys'] = merge_keys
        
        # 计算复杂度
        anchor_analysis['complexity'] = len(anchors) + len(aliases) + len(merge_keys)
        
        return anchor_analysis
    
    def analyze_multi_document(self, content):
        """分析多文档流"""
        doc_analysis = {
            'document_count': 0,
            'directives': [],
            'tags': [],
            'document_types': []
        }
        
        # 统计文档数量
        doc_analysis['document_count'] = content.count('---') + 1
        
        # 提取指令
        directives = re.findall(r'%[A-Z]+\s+[^\n]+', content)
        doc_analysis['directives'] = directives
        
        # 提取标签
        tags = re.findall(r'%TAG\s+[^\n]+', content)
        doc_analysis['tags'] = tags
        
        # 分析文档类型
        documents = content.split('---')
        for doc in documents:
            doc = doc.strip()
            if doc:
                if 'metadata' in doc.lower():
                    doc_analysis['document_types'].append('metadata')
                elif 'app' in doc.lower() or 'config' in doc.lower():
                    doc_analysis['document_types'].append('configuration')
                elif 'schema' in doc.lower() or 'type' in doc.lower():
                    doc_analysis['document_types'].append('schema')
                else:
                    doc_analysis['document_types'].append('data')
        
        return doc_analysis
    
    def comprehensive_analysis(self, file_path):
        """综合分析"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            print(f"\n=== YAML语法深度分析: {file_path} ===")
            
            # 执行各种分析
            version_info = self.analyze_yaml_version(content)
            parsing_stages = self.analyze_parsing_stages(content)
            type_system = self.analyze_type_system(content)
            anchor_alias = self.analyze_anchor_alias(content)
            multi_doc = self.analyze_multi_document(content)
            
            # 输出分析结果
            print(f"\n📋 YAML版本分析:")
            print(f"   版本: {version_info['version']}")
            print(f"   特性: {', '.join(version_info['features'])}")
            
            print(f"\n🔍 解析阶段分析:")
            for stage, info in parsing_stages.items():
                print(f"   {stage}: {info['count']}个元素")
                if info['elements']:
                    unique_elements = list(set(info['elements']))
                    print(f"     元素类型: {', '.join(unique_elements[:3])}")
            
            print(f"\n🎯 类型系统分析:")
            if type_system['scalar_types']:
                print(f"   标量类型分布:")
                for type_name, count in type_system['scalar_types'].items():
                    print(f"     {type_name}: {count}")
            
            if type_system['explicit_tags']:
                print(f"   显式标签: {', '.join(type_system['explicit_tags'])}")
            
            if type_system['custom_tags']:
                print(f"   自定义标签: {', '.join(type_system['custom_tags'])}")
            
            print(f"\n🔗 锚点别名分析:")
            print(f"   锚点: {len(anchor_alias['anchors'])}")
            print(f"   别名: {len(anchor_alias['aliases'])}")
            print(f"   合并键: {len(anchor_alias['merge_keys'])}")
            print(f"   复杂度: {anchor_alias['complexity']}")
            
            print(f"\n📄 多文档流分析:")
            print(f"   文档数量: {multi_doc['document_count']}")
            print(f"   文档类型: {', '.join(multi_doc['document_types'])}")
            if multi_doc['directives']:
                print(f"   指令: {len(multi_doc['directives'])}个")
            if multi_doc['tags']:
                print(f"   标签: {len(multi_doc['tags'])}个")
            
            return True
            
        except Exception as e:
            print(f"❌ 分析错误: {e}")
            return False

def test_yaml_versions():
    """测试不同YAML版本"""
    parser = YAMLDeepParser()
    
    # 测试YAML 1.0
    print("=== YAML 1.0 测试 ===")
    yaml_1_0 = """
%YAML 1.0
---
basic_types:
  string: "plain string"
  number: 123
  boolean: true
  null_value: null

sequence:
  - item1
  - item2
  - item3

mapping:
  key1: value1
  key2: value2
"""
    
    with open('yaml-1.0-test.yml', 'w', encoding='utf-8') as file:
        file.write(yaml_1_0)
    
    parser.comprehensive_analysis('yaml-1.0-test.yml')
    
    # 测试YAML 1.1
    print("\n=== YAML 1.1 测试 ===")
    yaml_1_1 = """
%YAML 1.1
---
tagged_values:
  !!str "explicit string"
  !!int 123
  !!bool true

base_config: &base
  host: "localhost"
  port: 8080

app_config:
  <<: *base
  name: "MyApp"
"""
    
    with open('yaml-1.1-test.yml', 'w', encoding='utf-8') as file:
        file.write(yaml_1_1)
    
    parser.comprehensive_analysis('yaml-1.1-test.yml')
    
    # 测试YAML 1.2
    print("\n=== YAML 1.2 测试 ===")
    yaml_1_2 = """
%YAML 1.2
---
json_compatible:
  "string": "value"
  "number": 123.45
  "boolean": true
  "array": [1, 2, 3]

strings:
  plain: plain string
  literal: |
    literal block
    with multiple lines
"""
    
    with open('yaml-1.2-test.yml', 'w', encoding='utf-8') as file:
        file.write(yaml_1_2)
    
    parser.comprehensive_analysis('yaml-1.2-test.yml')

def test_complex_structures():
    """测试复杂结构"""
    parser = YAMLDeepParser()
    
    print("\n=== 复杂结构测试 ===")
    complex_yaml = """
%YAML 1.2
%TAG ! tag:example.com,2024:app/
---
# 多文档流示例
metadata:
  version: "1.0.0"
  author: "YAML Processor"

---
app_config: &app_base
  app:
    name: "MyApp"
    version: "1.0.0"
  server:
    host: "localhost"
    port: 8080

---
production_config:
  <<: *app_base
  app:
    env: "production"
  server:
    host: "0.0.0.0"

---
!app/ConfigSchema
properties:
  app:
    type: "object"
    properties:
      name: !!str
      version: !!str
"""
    
    with open('complex-test.yml', 'w', encoding='utf-8') as file:
        file.write(complex_yaml)
    
    parser.comprehensive_analysis('complex-test.yml')

# 运行测试
test_yaml_versions()
test_complex_structures()
```

## 实验说明

1. **yaml-1.0-example.yml, yaml-1.1-example.yml, yaml-1.2-example.yml**: YAML语法规范演进示例，展示不同版本的语法特性
2. **parsing-example.yml**: 解析器工作原理示例，展示词法分析、语法分析和语义分析阶段
3. **type-system-example.yml**: 类型系统与标签机制示例，包含核心标量类型、显式类型标签和自定义类型标签
4. **anchor-alias-example.yml**: 锚点与别名机制示例，展示基础锚点使用、嵌套锚点和复杂锚点结构
5. **merge-key-example.yml**: 合并键机制示例，包含基础合并、多层合并和复杂合并场景
6. **multi-document-example.yml**: 多文档流处理示例，展示多文档配置和自定义类型定义
7. **syntax_deep_analysis.py**: Python验证代码，实现YAML语法深度分析功能

运行验证代码：
```bash
python syntax_deep_analysis.py
```

这将分析不同YAML版本的语法特性、解析器工作原理、类型系统、锚点别名机制、合并键机制和多文档流处理，提供详细的语法深度分析报告。