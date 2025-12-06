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

## 实验7：语法解析深度示例

### 7.1 缩进与语法错误示例

```yaml
# syntax_errors.yml
# 语法错误示例
correct:
  level1:
    level2: value
    level3: value  # 正确缩进

incorrect:
level1:            # 错误：没有缩进
    level2: value
  level3: value    # 错误：缩进不一致

mixed_tabs:
	level1: value    # 错误：使用制表符
  level2: value
```

### 7.2 注释与特殊字符处理

```yaml
# comments_and_special_chars.yml
# 注释和特殊字符处理
basic_comment: value  # 这是行内注释

# 这是块注释
# 可以跨多行
multiline_comment:
  - item1  # 注释1
  - item2  # 注释2

special_chars:
  colon_in_value: "value:with:colons"
  hash_in_value: "value#with#hash"
  quotes_in_value: "value with 'single' and \"double\" quotes"
  newline_in_value: |
    value with
    multiple lines
  
  # 需要引号的情况
  requires_quotes: "true"  # 避免被解析为布尔值
  numeric_string: "123"    # 避免被解析为数字
```

### 7.3 多行字符串处理

```yaml
# multiline_strings.yml
# 多行字符串示例
literal_block: |
  这是字面量块
  保留所有换行符
  和缩进

folded_block: >
  这是折叠块
  将换行符转换为空格
  适合长段落文本

preserved_newlines: |-
  去掉末尾换行符
  但保留内部换行

chomping_examples:
  strip: |-
    去掉末尾换行符
  clip: |
    保留末尾换行符（默认）
  keep: |+
    保留所有末尾换行符
```

## 实验8：语法解析验证代码

```python
# syntax_parser.py
import yaml
import re
from typing import Dict, List, Any

class YAMLSyntaxParser:
    """YAML语法解析器"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_indentation(self, content: str) -> List[str]:
        """验证缩进语法"""
        lines = content.split('\n')
        errors = []
        
        for i, line in enumerate(lines, 1):
            stripped = line.lstrip()
            if not stripped or stripped.startswith('#'):
                continue  # 跳过空行和注释
            
            # 检查制表符
            if '\t' in line:
                errors.append(f"第{i}行: 检测到制表符，YAML应使用空格缩进")
            
            # 检查缩进一致性
            leading_spaces = len(line) - len(line.lstrip())
            if leading_spaces % 2 != 0:
                errors.append(f"第{i}行: 缩进应为偶数个空格")
        
        return errors
    
    def validate_special_chars(self, content: str) -> List[str]:
        """验证特殊字符处理"""
        errors = []
        
        # 检查未转义的特殊字符
        pattern = r'^[^#\n]*[^\\]:[^\\s]'
        matches = re.finditer(pattern, content, re.MULTILINE)
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            errors.append(f"第{line_num}行: 冒号后应有空格")
        
        return errors
    
    def validate_multiline_strings(self, content: str) -> List[str]:
        """验证多行字符串语法"""
        errors = []
        lines = content.split('\n')
        
        in_multiline = False
        multiline_indent = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.lstrip()
            
            # 检测多行字符串开始
            if stripped.startswith(('|', '>')):
                in_multiline = True
                multiline_indent = len(line) - len(stripped)
                continue
            
            # 在多行字符串中检查缩进
            if in_multiline and stripped:
                current_indent = len(line) - len(stripped)
                if current_indent <= multiline_indent and not stripped.startswith('#'):
                    errors.append(f"第{i}行: 多行字符串内容缩进不足")
                
                # 检测多行字符串结束
                if current_indent < multiline_indent:
                    in_multiline = False
        
        return errors
    
    def comprehensive_validation(self, file_path: str) -> Dict[str, List[str]]:
        """综合语法验证"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # 执行各种验证
            results = {
                'indentation_errors': self.validate_indentation(content),
                'special_char_errors': self.validate_special_chars(content),
                'multiline_errors': self.validate_multiline_strings(content),
                'yaml_parse_errors': []
            }
            
            # 使用PyYAML验证语法
            try:
                yaml.safe_load(content)
            except yaml.YAMLError as e:
                results['yaml_parse_errors'].append(str(e))
            
            return results
            
        except Exception as e:
            return {'error': [f"文件读取失败: {e}"]}
    
    def print_validation_results(self, file_path: str):
        """打印验证结果"""
        print(f"\n验证文件: {file_path}")
        print("=" * 50)
        
        results = self.comprehensive_validation(file_path)
        
        total_errors = 0
        for category, errors in results.items():
            if errors:
                print(f"\n{category.replace('_', ' ').title()}:")
                for error in errors:
                    print(f"  ✗ {error}")
                    total_errors += 1
            else:
                print(f"\n{category.replace('_', ' ').title()}: ✓ 通过")
        
        print(f"\n总计错误: {total_errors}")
        if total_errors == 0:
            print("✓ 语法验证通过")
        else:
            print("✗ 发现语法错误")

# 使用示例
if __name__ == "__main__":
    parser = YAMLSyntaxParser()
    
    # 验证所有YAML文件
    test_files = [
        'experiment1.yml',
        'json_to_yaml.yml',
        'app_config.yml',
        'docker-compose.yml',
        'github-actions.yml',
        'multi_document.yml',
        'syntax_errors.yml',
        'comments_and_special_chars.yml',
        'multiline_strings.yml'
    ]
    
    for test_file in test_files:
        parser.print_validation_results(test_file)
        print("-" * 50)

# 高级语法分析函数
def analyze_yaml_structure(file_path: str):
    """分析YAML文件结构"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        
        def count_structure(obj, depth=0):
            """递归统计结构信息"""
            if isinstance(obj, dict):
                return {
                    'type': 'mapping',
                    'count': len(obj),
                    'depth': depth,
                    'children': [count_structure(v, depth+1) for v in obj.values()]
                }
            elif isinstance(obj, list):
                return {
                    'type': 'sequence',
                    'count': len(obj),
                    'depth': depth,
                    'children': [count_structure(item, depth+1) for item in obj]
                }
            else:
                return {
                    'type': 'scalar',
                    'value_type': type(obj).__name__,
                    'depth': depth
                }
        
        structure = count_structure(data)
        print(f"\n{file_path} 结构分析:")
        print(yaml.dump(structure, allow_unicode=True, indent=2))
        
    except Exception as e:
        print(f"分析失败: {e}")

# 运行结构分析
for test_file in test_files:
    analyze_yaml_structure(test_file)
```

## 实验说明

1. **experiment1.yml**: 基本YAML结构示例，包含标量、映射和列表
2. **json_to_yaml.yml**: 展示JSON与YAML的对应关系
3. **app_config.yml**: 应用配置文件示例
4. **docker-compose.yml**: Docker Compose配置示例
5. **github-actions.yml**: GitHub Actions工作流示例
6. **multi_document.yml**: 多文档YAML示例
7. **syntax_errors.yml**: 语法错误示例，用于测试验证器
8. **comments_and_special_chars.yml**: 注释和特殊字符处理示例
9. **multiline_strings.yml**: 多行字符串处理示例
10. **validate_yaml.py**: 基础验证代码
11. **syntax_parser.py**: 高级语法解析和验证代码

运行验证代码：
```bash
# 基础验证
python validate_yaml.py

# 高级语法解析
python syntax_parser.py
```

这将验证所有YAML文件的语法，进行深度结构分析，并检测各种语法错误。