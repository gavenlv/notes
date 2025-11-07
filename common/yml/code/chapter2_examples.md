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

## 实验说明

1. **data_types.yml**: 包含各种数据类型的综合示例
2. **string_examples.yml**: 各种字符串类型示例，包括单行、多行、特殊字符等
3. **number_examples.yml**: 各种数字类型示例，包括整数、浮点数、科学计数法等
4. **boolean_examples.yml**: 各种布尔值表示方式
5. **datetime_examples.yml**: 各种日期和时间格式
6. **sequence_examples.yml**: 各种序列类型示例
7. **mapping_examples.yml**: 各种映射类型示例
8. **advanced_types.yml**: 高级数据类型示例，包括集合、有序映射、二进制数据等
9. **validate_data_types.py**: Python验证代码，用于分析和验证YAML数据类型

运行验证代码：
```bash
python validate_data_types.py
```

这将验证所有YAML文件的语法，分析它们的数据类型结构，并展示类型转换和特殊值的处理。