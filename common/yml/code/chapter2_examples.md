# 第2章示例代码

## 实验1：数据类型示例

```yaml
# data_types.yml
# 包含各种数据类型的YAML示例
---
# 标量类型
string_value: "Hello, World!"
integer_value: 42
float_value: 3.14
boolean_value: true
date_value: 2023-05-15
null_value: null

# 序列类型
simple_list:
  - item1
  - item2
  - item3

mixed_list:
  - "string"
  - 123
  - true
  - null

nested_list:
  - - nested_item1
    - nested_item2
  - - nested_item3
    - nested_item4

# 映射类型
simple_mapping:
  key1: value1
  key2: value2
  key3: value3

nested_mapping:
  outer_key1:
    inner_key1: inner_value1
    inner_key2: inner_value2
  outer_key2:
    inner_key3: inner_value3
    inner_key4: inner_value4

# 复杂结构
complex_structure:
  users:
    - name: John
      age: 30
      hobbies:
        - reading
        - swimming
    - name: Jane
      age: 25
      hobbies:
        - painting
        - dancing
  settings:
    theme: dark
    notifications: true
    language: en-US
```

## 实验2：字符串类型示例

```yaml
# string_examples.yml
# 各种字符串类型示例
---
# 单行字符串
simple_string: Hello World
quoted_string: "Hello, World!"
special_chars: "Special chars: !@#$%^&*()"

# 多行字符串
block_string: |
  This is a block string
  that preserves line breaks
  and indentation.

folded_string: >
  This is a folded string
  that converts line breaks
  to spaces, creating a
  single paragraph.

# 特殊字符串
empty_string: ""
null_string: null
unicode_string: "Unicode: 中文测试"

# 转义字符
escaped_chars: "This contains a \"quote\" and a \\ backslash"
```

## 实验3：数字类型示例

```yaml
# number_examples.yml
# 各种数字类型示例
---
# 整数
positive_integer: 42
negative_integer: -17
zero: 0

# 其他进制
octal: 0o755
hexadecimal: 0xFF
binary: 0b1010

# 浮点数
positive_float: 3.14
negative_float: -2.71
scientific: 1.23e-4
negative_scientific: -4.56e+7

# 特殊值
infinity: .inf
negative_infinity: -.inf
not_a_number: .NaN
```

## 实验4：布尔值示例

```yaml
# boolean_examples.yml
# 各种布尔值表示方式
---
# 标准布尔值
standard_true: true
standard_false: false

# 其他表示方式
yes_true: yes
no_false: no
on_true: on
off_false: off

# 注意：这些会被解析为字符串，不是布尔值
string_true: "true"
string_false: "false"
string_yes: "yes"
string_no: "no"
```

## 实验5：日期和时间示例

```yaml
# datetime_examples.yml
# 各种日期和时间格式
---
# 日期
date_only: 2023-05-15

# 时间
time_only: 14:30:00

# 日期和时间
datetime: 2023-05-15T14:30:00

# 带时区的日期时间
datetime_with_timezone: 2023-05-15T14:30:00+08:00
datetime_utc: 2023-05-15T14:30:00Z

# 日期范围
date_range: 2023-05-01/2023-05-31
```

## 实验6：序列类型示例

```yaml
# sequence_examples.yml
# 各种序列类型示例
---
# 简单序列
fruits:
  - apple
  - banana
  - orange

# 内联序列
vegetables: [carrot, broccoli, spinach]

# 混合类型序列
mixed_list:
  - "string"
  - 42
  - true
  - null

# 嵌套序列
nested_sequences:
  - - item1
    - item2
  - - item3
    - item4
    - item5

# 序列中的映射
sequence_of_mappings:
  - name: John
    age: 30
  - name: Jane
    age: 25

# 多行序列
long_sequence:
  - first item
  - second item
  - third item
  - fourth item
  - fifth item
```

## 实验7：映射类型示例

```yaml
# mapping_examples.yml
# 各种映射类型示例
---
# 简单映射
person:
  name: John Doe
  age: 30
  city: New York

# 内联映射
inline_mapping: {name: Jane, age: 25, city: Boston}

# 嵌套映射
company:
  name: Tech Corp
  address:
    street: 123 Business Ave
    city: San Francisco
    state: CA
    zip: 94105
  contact:
    phone: 555-1234
    email: info@techcorp.com

# 复杂结构
complex_structure:
  users:
    - name: John
      age: 30
      hobbies:
        - reading
        - swimming
    - name: Jane
      age: 25
      hobbies:
        - painting
        - dancing
  settings:
    theme: dark
    notifications: true
    language: en-US
```

## 实验8：高级数据类型示例

```yaml
# advanced_types.yml
# 高级数据类型示例
---
# 集合（无序、唯一元素）
set_example: !!set
  ? apple
  ? banana
  ? orange

# 有序映射（保持键的顺序）
ordered_map: !!omap
  - name: John
  - age: 30
  - city: New York

# 二进制数据（Base64编码）
binary_data: !!binary R0lGODlhDAAMAIQAAP//9/X17unp5WZmZgAAAOfn515eXvPz7Y6OjuDg4J+fn5OTk6enp56enmleECcgggoBADs=

# 显式类型指定
string_number: !!str 123
integer_string: !!int "456"
float_string: !!float "3.14"
boolean_string: !!bool "true"
```

## Python验证代码

```python
# validate_data_types.py
import yaml
import json
from datetime import datetime, date

def analyze_yaml_structure(data, prefix=""):
    """分析YAML数据结构"""
    if isinstance(data, dict):
        print(f"{prefix}映射 (字典) - {len(data)} 个键:")
        for key, value in data.items():
            print(f"{prefix}  {key}: ", end="")
            analyze_yaml_structure(value, prefix + "  ")
    elif isinstance(data, list):
        print(f"{prefix}序列 (列表) - {len(data)} 个元素:")
        for i, item in enumerate(data):
            print(f"{prefix}  [{i}]: ", end="")
            analyze_yaml_structure(item, prefix + "  ")
    elif isinstance(data, str):
        print(f"字符串: '{data}'")
    elif isinstance(data, int):
        print(f"整数: {data}")
    elif isinstance(data, float):
        print(f"浮点数: {data}")
    elif isinstance(data, bool):
        print(f"布尔值: {data}")
    elif isinstance(data, datetime):
        print(f"日期时间: {data}")
    elif isinstance(data, date):
        print(f"日期: {data}")
    elif data is None:
        print("null值")
    else:
        print(f"未知类型: {type(data).__name__}")

def validate_yaml_file(file_path):
    """验证YAML文件并分析其结构"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            print(f"\n=== {file_path} ===")
            analyze_yaml_structure(data)
            return data
    except yaml.YAMLError as e:
        print(f"\n=== {file_path} ===")
        print(f"YAML解析错误: {e}")
        return None

def compare_types(file1, file2):
    """比较两个YAML文件的数据类型"""
    data1 = validate_yaml_file(file1)
    data2 = validate_yaml_file(file2)
    
    if data1 and data2:
        print("\n=== 类型比较 ===")
        print(f"{file1} 顶级类型: {type(data1).__name__}")
        print(f"{file2} 顶级类型: {type(data2).__name__}")

def test_explicit_types():
    """测试显式类型指定"""
    yaml_content = """
string_number: !!str 123
integer_string: !!int "456"
float_string: !!float "3.14"
boolean_string: !!bool "true"
"""
    
    data = yaml.safe_load(yaml_content)
    print("\n=== 显式类型指定测试 ===")
    for key, value in data.items():
        print(f"{key}: {type(value).__name__} = {value}")

def test_special_values():
    """测试特殊值"""
    yaml_content = """
infinity: .inf
negative_infinity: -.inf
not_a_number: .NaN
null_value: null
"""
    
    data = yaml.safe_load(yaml_content)
    print("\n=== 特殊值测试 ===")
    for key, value in data.items():
        print(f"{key}: {type(value).__name__} = {value}")

# 验证所有YAML文件
yaml_files = [
    'data_types.yml',
    'string_examples.yml',
    'number_examples.yml',
    'boolean_examples.yml',
    'datetime_examples.yml',
    'sequence_examples.yml',
    'mapping_examples.yml',
    'advanced_types.yml'
]

for yaml_file in yaml_files:
    validate_yaml_file(yaml_file)

# 测试显式类型指定
test_explicit_types()

# 测试特殊值
test_special_values()

# 将YAML转换为JSON以查看结构
with open('data_types.yml', 'r', encoding='utf-8') as file:
    data = yaml.safe_load(file)
    json_str = json.dumps(data, ensure_ascii=False, indent=2, default=str)
    print("\n=== JSON表示 ===")
    print(json_str)
```

## 实验9：类型推断与转换示例

```yaml
# type_inference.yml
# 类型推断与转换示例
---
# 自动类型推断
auto_inference:
  string_like_number: "123"        # 推断为字符串
  number_like_string: 456           # 推断为整数
  boolean_like_string: "true"       # 推断为字符串
  date_like_string: "2023-05-15"    # 推断为字符串

# 显式类型转换
explicit_conversion:
  string_to_int: !!int "789"        # 字符串转整数
  int_to_string: !!str 123          # 整数转字符串
  string_to_float: !!float "3.14"    # 字符串转浮点数
  string_to_bool: !!bool "false"     # 字符串转布尔值

# 复杂类型转换
complex_conversion:
  binary_data: !!binary "SGVsbG8gV29ybGQ="  # Base64编码
  set_data: !!set
    ? apple
    ? banana
    ? orange
  ordered_map: !!omap
    - first: value1
    - second: value2
    - third: value3

# 边界情况
edge_cases:
  empty_string: ""
  zero: 0
  negative_zero: -0
  infinity: .inf
  negative_infinity: -.inf
  not_a_number: .NaN
```

## 实验10：类型验证与错误处理示例

```yaml
# type_validation.yml
# 类型验证与错误处理示例
---
# 有效类型定义
valid_types:
  required_string: !!str "required"
  required_int: !!int 42
  required_float: !!float 3.14
  required_bool: !!bool true
  required_date: 2023-05-15

# 类型错误示例（这些会导致解析错误）
type_errors:
  invalid_int: !!int "not_a_number"
  invalid_float: !!float "not_a_float"
  invalid_bool: !!bool "not_a_boolean"
  invalid_date: "not_a_date"

# 自定义类型验证
custom_validation:
  email_pattern: "user@example.com"
  phone_pattern: "+1-555-123-4567"
  url_pattern: "https://example.com"
  ip_address: "192.168.1.1"
```

## 实验11：语法解析与类型系统验证代码

```python
# type_system_parser.py
import yaml
import re
from typing import Dict, List, Any, Union
from datetime import datetime, date

class YAMLTypeSystemParser:
    """YAML类型系统解析器"""
    
    def __init__(self):
        self.type_errors = []
        self.warnings = []
    
    def analyze_type_inference(self, data: Any, path: str = "") -> Dict[str, Any]:
        """分析类型推断结果"""
        result = {
            'path': path,
            'type': type(data).__name__,
            'value': data,
            'children': []
        }
        
        if isinstance(data, dict):
            for key, value in data.items():
                child_path = f"{path}.{key}" if path else key
                result['children'].append(self.analyze_type_inference(value, child_path))
        elif isinstance(data, list):
            for i, item in enumerate(data):
                child_path = f"{path}[{i}]"
                result['children'].append(self.analyze_type_inference(item, child_path))
        
        return result
    
    def validate_explicit_types(self, data: Any, path: str = "") -> List[str]:
        """验证显式类型指定"""
        errors = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                child_path = f"{path}.{key}" if path else key
                
                # 检查显式类型转换
                if isinstance(value, str):
                    # 检查字符串是否可以转换为其他类型
                    if key.endswith('_to_int'):
                        try:
                            int(value)
                        except ValueError:
                            errors.append(f"{child_path}: 无法将字符串转换为整数")
                    
                    elif key.endswith('_to_float'):
                        try:
                            float(value)
                        except ValueError:
                            errors.append(f"{child_path}: 无法将字符串转换为浮点数")
                    
                    elif key.endswith('_to_bool'):
                        if value.lower() not in ('true', 'false', 'yes', 'no', 'on', 'off'):
                            errors.append(f"{child_path}: 无法将字符串转换为布尔值")
                
                # 递归检查子元素
                errors.extend(self.validate_explicit_types(value, child_path))
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                child_path = f"{path}[{i}]"
                errors.extend(self.validate_explicit_types(item, child_path))
        
        return errors
    
    def detect_type_anomalies(self, data: Any, path: str = "") -> List[str]:
        """检测类型异常"""
        anomalies = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                child_path = f"{path}.{key}" if path else key
                
                # 检查混合类型
                if isinstance(value, (list, dict)):
                    child_types = set()
                    if isinstance(value, list):
                        for item in value:
                            child_types.add(type(item).__name__)
                    elif isinstance(value, dict):
                        for v in value.values():
                            child_types.add(type(v).__name__)
                    
                    if len(child_types) > 1:
                        anomalies.append(f"{child_path}: 混合类型 {child_types}")
                
                # 递归检查子元素
                anomalies.extend(self.detect_type_anomalies(value, child_path))
        
        elif isinstance(data, list):
            # 检查列表元素类型一致性
            if len(data) > 0:
                first_type = type(data[0]).__name__
                for i, item in enumerate(data[1:], 1):
                    if type(item).__name__ != first_type:
                        anomalies.append(f"{path}[{i}]: 类型不一致 ({first_type} vs {type(item).__name__})")
            
            for i, item in enumerate(data):
                child_path = f"{path}[{i}]"
                anomalies.extend(self.detect_type_anomalies(item, child_path))
        
        return anomalies
    
    def comprehensive_type_analysis(self, file_path: str) -> Dict[str, Any]:
        """综合类型分析"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
            
            analysis = {
                'file': file_path,
                'type_inference': self.analyze_type_inference(data),
                'explicit_type_errors': self.validate_explicit_types(data),
                'type_anomalies': self.detect_type_anomalies(data),
                'raw_data': data
            }
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def print_type_analysis(self, file_path: str):
        """打印类型分析结果"""
        print(f"\n类型分析: {file_path}")
        print("=" * 60)
        
        analysis = self.comprehensive_type_analysis(file_path)
        
        if 'error' in analysis:
            print(f"分析失败: {analysis['error']}")
            return
        
        # 打印类型推断结果
        print("\n类型推断结果:")
        self._print_type_tree(analysis['type_inference'])
        
        # 打印显式类型错误
        if analysis['explicit_type_errors']:
            print("\n显式类型错误:")
            for error in analysis['explicit_type_errors']:
                print(f"  ✗ {error}")
        else:
            print("\n显式类型错误: ✓ 无错误")
        
        # 打印类型异常
        if analysis['type_anomalies']:
            print("\n类型异常:")
            for anomaly in analysis['type_anomalies']:
                print(f"  ⚠ {anomaly}")
        else:
            print("\n类型异常: ✓ 无异常")
    
    def _print_type_tree(self, node: Dict, indent: int = 0):
        """打印类型树"""
        prefix = "  " * indent
        print(f"{prefix}{node['path']}: {node['type']} = {repr(node['value'])}")
        
        for child in node['children']:
            self._print_type_tree(child, indent + 1)

# 高级类型验证函数
def validate_yaml_schema(file_path: str, schema: Dict[str, Any]) -> List[str]:
    """根据模式验证YAML结构"""
    errors = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        
        def validate_recursive(actual: Any, expected: Any, path: str = "") -> List[str]:
            local_errors = []
            
            if isinstance(expected, dict):
                if not isinstance(actual, dict):
                    local_errors.append(f"{path}: 期望映射，实际为 {type(actual).__name__}")
                    return local_errors
                
                for key, expected_type in expected.items():
                    if key not in actual:
                        local_errors.append(f"{path}.{key}: 缺少必需字段")
                    else:
                        child_path = f"{path}.{key}" if path else key
                        local_errors.extend(validate_recursive(actual[key], expected_type, child_path))
            
            elif isinstance(expected, list):
                if not isinstance(actual, list):
                    local_errors.append(f"{path}: 期望序列，实际为 {type(actual).__name__}")
                    return local_errors
                
                if len(expected) > 0:
                    expected_type = expected[0]
                    for i, item in enumerate(actual):
                        child_path = f"{path}[{i}]"
                        local_errors.extend(validate_recursive(item, expected_type, child_path))
            
            elif callable(expected):
                # 期望是类型检查函数
                if not expected(actual):
                    local_errors.append(f"{path}: 类型验证失败")
            
            return local_errors
        
        errors = validate_recursive(data, schema)
        
    except Exception as e:
        errors.append(f"验证失败: {e}")
    
    return errors

# 使用示例
if __name__ == "__main__":
    parser = YAMLTypeSystemParser()
    
    # 分析所有YAML文件
    test_files = [
        'data_types.yml',
        'string_examples.yml',
        'number_examples.yml',
        'boolean_examples.yml',
        'datetime_examples.yml',
        'sequence_examples.yml',
        'mapping_examples.yml',
        'advanced_types.yml',
        'type_inference.yml',
        'type_validation.yml'
    ]
    
    for test_file in test_files:
        parser.print_type_analysis(test_file)
        print("-" * 60)
    
    # 模式验证示例
    schema = {
        'users': [{
            'name': str,
            'age': lambda x: isinstance(x, int) and x > 0,
            'hobbies': [str]
        }],
        'settings': {
            'theme': lambda x: x in ['dark', 'light'],
            'notifications': bool,
            'language': str
        }
    }
    
    print("\n模式验证示例:")
    errors = validate_yaml_schema('data_types.yml', schema)
    if errors:
        print("模式验证错误:")
        for error in errors:
            print(f"  ✗ {error}")
    else:
        print("✓ 模式验证通过")

# 类型转换工具函数
def convert_yaml_types(data: Any, conversion_rules: Dict[str, Any]) -> Any:
    """根据规则转换YAML类型"""
    if isinstance(data, dict):
        return {k: convert_yaml_types(v, conversion_rules) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_yaml_types(item, conversion_rules) for item in data]
    elif isinstance(data, str):
        # 应用字符串转换规则
        for pattern, converter in conversion_rules.items():
            if re.match(pattern, data):
                return converter(data)
        return data
    else:
        return data

# 运行类型转换示例
with open('type_inference.yml', 'r', encoding='utf-8') as file:
    data = yaml.safe_load(file)

conversion_rules = {
    r'^\\d+$': int,           # 数字字符串转整数
    r'^\\d+\\.\\d+$': float,     # 浮点数字符串转浮点数
    r'^(true|false)$': lambda x: x.lower() == 'true'  # 布尔字符串转布尔值
}

converted_data = convert_yaml_types(data, conversion_rules)
print("\n类型转换结果:")
print(yaml.dump(converted_data, allow_unicode=True, indent=2))
```

## 实验说明

1. **data_types.yml**: 包含各种数据类型的综合示例
2. **string_examples.yml**: 各种字符串类型示例，包括单行、多行、特殊字符等
3. **number_examples.yml**: 各种数字类型示例，包括整数、浮点数、科学计数法等
4. **boolean_examples.yml**: 各种布尔值表示方式
5. **datetime_examples.yml**: 各种日期和时间格式
6. **sequence_examples.yml**: 各种序列类型示例
7. **mapping_examples.yml**: 各种映射类型示例
8. **advanced_types.yml**: 高级数据类型示例，包括集合、有序映射、二进制数据等
9. **type_inference.yml**: 类型推断与转换示例
10. **type_validation.yml**: 类型验证与错误处理示例
11. **validate_data_types.py**: 基础验证代码
12. **type_system_parser.py**: 高级类型系统解析和验证代码

运行验证代码：
```bash
# 基础验证
python validate_data_types.py

# 高级类型系统分析
python type_system_parser.py
```

这将验证所有YAML文件的语法，进行深度类型系统分析，检测类型异常，并支持模式验证和类型转换。