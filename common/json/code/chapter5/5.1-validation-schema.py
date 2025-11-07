#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JSON验证与模式示例
此文件演示了如何使用Python验证JSON数据结构和内容
"""

import json
import re
import datetime
from typing import Dict, Any, List, Union, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# ==================== 基本JSON验证 ====================

def validate_json_string(json_string: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
    """
    验证JSON字符串是否有效
    
    Args:
        json_string: 要验证的JSON字符串
        
    Returns:
        Tuple[是否有效, 解析后的对象, 错误信息]
    """
    try:
        parsed_json = json.loads(json_string)
        return True, parsed_json, None
    except json.JSONDecodeError as e:
        return False, None, f"JSON解析错误: {e.msg} (行 {e.lineno}, 列 {e.colno})"
    except Exception as e:
        return False, None, f"其他错误: {str(e)}"

def validate_json_file(file_path: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
    """
    验证JSON文件是否有效
    
    Args:
        file_path: JSON文件路径
        
    Returns:
        Tuple[是否有效, 解析后的对象, 错误信息]
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            parsed_json = json.load(file)
        return True, parsed_json, None
    except FileNotFoundError:
        return False, None, f"文件不存在: {file_path}"
    except json.JSONDecodeError as e:
        return False, None, f"JSON解析错误: {e.msg} (行 {e.lineno}, 列 {e.colno})"
    except Exception as e:
        return False, None, f"其他错误: {str(e)}"

# ==================== 数据类型验证 ====================

class DataType(Enum):
    """支持的数据类型"""
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    NULL = "null"

def validate_type(value: Any, expected_type: DataType) -> bool:
    """
    验证值是否符合期望的数据类型
    
    Args:
        value: 要验证的值
        expected_type: 期望的数据类型
        
    Returns:
        是否符合期望的数据类型
    """
    if expected_type == DataType.STRING:
        return isinstance(value, str)
    elif expected_type == DataType.NUMBER:
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    elif expected_type == DataType.INTEGER:
        return isinstance(value, int) and not isinstance(value, bool)
    elif expected_type == DataType.BOOLEAN:
        return isinstance(value, bool)
    elif expected_type == DataType.ARRAY:
        return isinstance(value, list)
    elif expected_type == DataType.OBJECT:
        return isinstance(value, dict)
    elif expected_type == DataType.NULL:
        return value is None
    
    return False

def validate_string_constraints(value: str, constraints: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    验证字符串值的约束
    
    Args:
        value: 字符串值
        constraints: 约束条件
        
    Returns:
        Tuple[是否有效, 错误信息]
    """
    # 长度约束
    if "minLength" in constraints and len(value) < constraints["minLength"]:
        return False, f"字符串长度不足，最小长度: {constraints['minLength']}"
    
    if "maxLength" in constraints and len(value) > constraints["maxLength"]:
        return False, f"字符串长度过长，最大长度: {constraints['maxLength']}"
    
    # 模式匹配
    if "pattern" in constraints:
        pattern = re.compile(constraints["pattern"])
        if not pattern.match(value):
            return False, f"字符串不匹配模式: {constraints['pattern']}"
    
    # 枚举值
    if "enum" in constraints and value not in constraints["enum"]:
        return False, f"字符串值不在允许的枚举值中: {constraints['enum']}"
    
    # 格式验证
    if "format" in constraints:
        format_type = constraints["format"]
        if format_type == "email" and not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            return False, "不是有效的邮箱格式"
        elif format_type == "uri" and not re.match(r"https?://.+", value):
            return False, "不是有效的URI格式"
        elif format_type == "date" and not re.match(r"\d{4}-\d{2}-\d{2}", value):
            return False, "不是有效的日期格式 (YYYY-MM-DD)"
        elif format_type == "date-time" and not re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", value):
            return False, "不是有效的日期时间格式 (ISO 8601)"
    
    return True, None

def validate_number_constraints(value: Union[int, float], constraints: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    验证数字值的约束
    
    Args:
        value: 数字值
        constraints: 约束条件
        
    Returns:
        Tuple[是否有效, 错误信息]
    """
    # 范围约束
    if "minimum" in constraints and value < constraints["minimum"]:
        return False, f"数值小于最小值: {constraints['minimum']}"
    
    if "maximum" in constraints and value > constraints["maximum"]:
        return False, f"数值大于最大值: {constraints['maximum']}"
    
    if "exclusiveMinimum" in constraints and value <= constraints["exclusiveMinimum"]:
        return False, f"数值必须大于: {constraints['exclusiveMinimum']}"
    
    if "exclusiveMaximum" in constraints and value >= constraints["exclusiveMaximum"]:
        return False, f"数值必须小于: {constraints['exclusiveMaximum']}"
    
    # 整数约束
    if "type" in constraints and constraints["type"] == "integer" and not isinstance(value, int):
        return False, "值必须是整数"
    
    # 多重约束
    if "multipleOf" in constraints and value % constraints["multipleOf"] != 0:
        return False, f"数值必须是 {constraints['multipleOf']} 的倍数"
    
    return True, None

# ==================== JSON Schema验证 ====================

@dataclass
class ValidationError:
    """验证错误"""
    path: str
    message: str
    value: Any

class JsonValidator:
    """JSON Schema验证器"""
    
    def __init__(self, schema: Dict[str, Any]):
        """
        初始化验证器
        
        Args:
            schema: JSON Schema定义
        """
        self.schema = schema
        self.errors: List[ValidationError] = []
    
    def validate(self, data: Any) -> Tuple[bool, List[ValidationError]]:
        """
        验证数据是否符合schema
        
        Args:
            data: 要验证的数据
            
        Returns:
            Tuple[是否有效, 错误列表]
        """
        self.errors = []
        self._validate_value(data, self.schema, "$")
        
        return len(self.errors) == 0, self.errors
    
    def _validate_value(self, value: Any, schema: Dict[str, Any], path: str) -> None:
        """
        递归验证值
        
        Args:
            value: 要验证的值
            schema: 应用的schema
            path: 当前路径
        """
        # 类型验证
        if "type" in schema:
            if isinstance(schema["type"], list):
                # 多种可能类型
                if not any(validate_type(value, DataType(t.lower())) for t in schema["type"]):
                    self.errors.append(ValidationError(
                        path=path,
                        message=f"值类型不匹配，期望: {', '.join(schema['type'])}",
                        value=value
                    ))
                    return
            else:
                if not validate_type(value, DataType(schema["type"].lower())):
                    self.errors.append(ValidationError(
                        path=path,
                        message=f"值类型不匹配，期望: {schema['type']}",
                        value=value
                    ))
                    return
        
        # 枚举验证
        if "enum" in schema and value not in schema["enum"]:
            self.errors.append(ValidationError(
                path=path,
                message=f"值不在允许的枚举中: {schema['enum']}",
                value=value
            ))
            return
        
        # 字符串约束
        if isinstance(value, str):
            constraints = {k: v for k, v in schema.items() if k in ["minLength", "maxLength", "pattern", "format", "enum"]}
            if constraints:
                is_valid, error = validate_string_constraints(value, constraints)
                if not is_valid:
                    self.errors.append(ValidationError(
                        path=path,
                        message=error,
                        value=value
                    ))
        
        # 数字约束
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            constraints = {k: v for k, v in schema.items() if k in [
                "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", 
                "multipleOf", "type"
            ]}
            if constraints:
                is_valid, error = validate_number_constraints(value, constraints)
                if not is_valid:
                    self.errors.append(ValidationError(
                        path=path,
                        message=error,
                        value=value
                    ))
        
        # 数组验证
        elif isinstance(value, list) and schema.get("type") == "array":
            # 长度约束
            if "minItems" in schema and len(value) < schema["minItems"]:
                self.errors.append(ValidationError(
                    path=path,
                    message=f"数组项数不足，最小项数: {schema['minItems']}",
                    value=value
                ))
            
            if "maxItems" in schema and len(value) > schema["maxItems"]:
                self.errors.append(ValidationError(
                    path=path,
                    message=f"数组项数过多，最大项数: {schema['maxItems']}",
                    value=value
                ))
            
            # 唯一性约束
            if "uniqueItems" in schema and schema["uniqueItems"] and len(set(map(str, value))) != len(value):
                self.errors.append(ValidationError(
                    path=path,
                    message="数组项必须唯一",
                    value=value
                ))
            
            # 验证数组元素
            if "items" in schema:
                if isinstance(schema["items"], dict):
                    # 所有元素使用相同的schema
                    for i, item in enumerate(value):
                        self._validate_value(item, schema["items"], f"{path}[{i}]")
                elif isinstance(schema["items"], list):
                    # 位置特定的schema
                    for i, item in enumerate(value):
                        if i < len(schema["items"]):
                            self._validate_value(item, schema["items"][i], f"{path}[{i}]")
        
        # 对象验证
        elif isinstance(value, dict) and schema.get("type") == "object":
            # 必需属性验证
            required_properties = schema.get("required", [])
            for prop in required_properties:
                if prop not in value:
                    self.errors.append(ValidationError(
                        path=f"{path}.{prop}",
                        message="缺少必需属性",
                        value=None
                    ))
            
            # 额外属性验证
            additional_properties_allowed = schema.get("additionalProperties", True)
            properties = schema.get("properties", {})
            pattern_properties = schema.get("patternProperties", {})
            
            for key in value.keys():
                # 检查是否在properties中定义
                if key in properties:
                    self._validate_value(value[key], properties[key], f"{path}.{key}")
                # 检查是否匹配patternProperties
                else:
                    pattern_matched = False
                    for pattern, pattern_schema in pattern_properties.items():
                        if re.match(pattern, key):
                            self._validate_value(value[key], pattern_schema, f"{path}.{key}")
                            pattern_matched = True
                            break
                    
                    if not pattern_matched and not additional_properties_allowed:
                        self.errors.append(ValidationError(
                            path=f"{path}.{key}",
                            message="不允许的额外属性",
                            value=key
                        ))

# ==================== 实际应用示例 ====================

def validate_user_profile(json_data: Dict) -> Tuple[bool, List[ValidationError]]:
    """
    验证用户档案数据
    
    Args:
        json_data: 用户档案JSON数据
        
    Returns:
        Tuple[是否有效, 错误列表]
    """
    schema = {
        "type": "object",
        "required": ["id", "username", "email", "profile"],
        "properties": {
            "id": {
                "type": "integer",
                "minimum": 1
            },
            "username": {
                "type": "string",
                "minLength": 3,
                "maxLength": 30,
                "pattern": "^[a-zA-Z0-9_]+$"
            },
            "email": {
                "type": "string",
                "format": "email"
            },
            "profile": {
                "type": "object",
                "required": ["firstName", "lastName"],
                "properties": {
                    "firstName": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 50
                    },
                    "lastName": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 50
                    },
                    "age": {
                        "type": "integer",
                        "minimum": 18,
                        "maximum": 120
                    },
                    "bio": {
                        "type": "string",
                        "maxLength": 500
                    },
                    "avatar": {
                        "type": "string",
                        "format": "uri"
                    },
                    "preferences": {
                        "type": "object",
                        "properties": {
                            "theme": {
                                "type": "string",
                                "enum": ["light", "dark"]
                            },
                            "language": {
                                "type": "string",
                                "pattern": "^[a-z]{2}-[A-Z]{2}$"
                            },
                            "notifications": {
                                "type": "object",
                                "properties": {
                                    "email": {"type": "boolean"},
                                    "sms": {"type": "boolean"},
                                    "push": {"type": "boolean"}
                                }
                            }
                        }
                    }
                }
            },
            "roles": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "uniqueItems": True
            },
            "lastLogin": {
                "type": "string",
                "format": "date-time"
            },
            "isActive": {
                "type": "boolean"
            }
        },
        "additionalProperties": False
    }
    
    validator = JsonValidator(schema)
    return validator.validate(json_data)

def validate_product_catalog(json_data: Dict) -> Tuple[bool, List[ValidationError]]:
    """
    验证产品目录数据
    
    Args:
        json_data: 产品目录JSON数据
        
    Returns:
        Tuple[是否有效, 错误列表]
    """
    schema = {
        "type": "object",
        "required": ["catalog", "metadata"],
        "properties": {
            "catalog": {
                "type": "object",
                "required": ["categories", "products"],
                "properties": {
                    "categories": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "object",
                            "required": ["id", "name"],
                            "properties": {
                                "id": {
                                    "type": "string",
                                    "pattern": "^cat_[a-z0-9_]+$"
                                },
                                "name": {
                                    "type": "string",
                                    "minLength": 1
                                },
                                "parentId": {
                                    "type": ["string", "null"],
                                    "pattern": "^cat_[a-z0-9_]+$"
                                },
                                "level": {
                                    "type": "integer",
                                    "minimum": 1
                                }
                            }
                        }
                    },
                    "products": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "object",
                            "required": ["id", "name", "price", "category"],
                            "properties": {
                                "id": {
                                    "type": "string",
                                    "pattern": "^prod_[a-z0-9_]+$"
                                },
                                "name": {
                                    "type": "string",
                                    "minLength": 1
                                },
                                "description": {
                                    "type": "string"
                                },
                                "price": {
                                    "type": "number",
                                    "minimum": 0,
                                    "multipleOf": 0.01
                                },
                                "category": {
                                    "type": "string",
                                    "pattern": "^cat_[a-z0-9_]+$"
                                },
                                "images": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "required": ["url"],
                                        "properties": {
                                            "url": {
                                                "type": "string",
                                                "format": "uri"
                                            },
                                            "alt": {
                                                "type": "string"
                                            },
                                            "isPrimary": {
                                                "type": "boolean"
                                            }
                                        }
                                    }
                                },
                                "specs": {
                                    "type": "object",
                                    "patternProperties": {
                                        "^[a-zA-Z_][a-zA-Z0-9_]*$": {}
                                    }
                                },
                                "stock": {
                                    "type": "object",
                                    "properties": {
                                        "quantity": {
                                            "type": "integer",
                                            "minimum": 0
                                        },
                                        "location": {
                                            "type": "string"
                                        }
                                    }
                                },
                                "tags": {
                                    "type": "array",
                                    "items": {
                                        "type": "string"
                                    },
                                    "uniqueItems": True
                                }
                            }
                        }
                    }
                }
            },
            "metadata": {
                "type": "object",
                "required": ["version", "generatedAt"],
                "properties": {
                    "version": {
                        "type": "string",
                        "pattern": "^\\d+\\.\\d+\\.\\d+$"
                    },
                    "generatedAt": {
                        "type": "string",
                        "format": "date-time"
                    }
                }
            }
        }
    }
    
    validator = JsonValidator(schema)
    is_valid, errors = validator.validate(json_data)
    
    # 自定义验证逻辑：确保产品中的category在categories中存在
    if is_valid:
        category_ids = {cat["id"] for cat in json_data["catalog"]["categories"]}
        for product in json_data["catalog"]["products"]:
            if product["category"] not in category_ids:
                errors.append(ValidationError(
                    path=f"$.catalog.products[].category",
                    message=f"产品类别 '{product['category']}' 不在类别列表中",
                    value=product["category"]
                ))
    
    return len(errors) == 0, errors

def validate_api_response(json_data: Dict, expected_schema: Dict) -> Tuple[bool, List[ValidationError]]:
    """
    验证API响应数据
    
    Args:
        json_data: API响应JSON数据
        expected_schema: 期望的响应schema
        
    Returns:
        Tuple[是否有效, 错误列表]
    """
    validator = JsonValidator(expected_schema)
    return validator.validate(json_data)

# ==================== 示例数据 ====================

# 有效的用户档案
valid_user_profile = {
    "id": 123,
    "username": "john_doe",
    "email": "john.doe@example.com",
    "profile": {
        "firstName": "John",
        "lastName": "Doe",
        "age": 30,
        "bio": "Software developer interested in JSON.",
        "avatar": "https://example.com/avatar.jpg",
        "preferences": {
            "theme": "dark",
            "language": "en-US",
            "notifications": {
                "email": True,
                "sms": False,
                "push": True
            }
        }
    },
    "roles": ["user", "developer"],
    "lastLogin": "2023-04-22T14:30:45Z",
    "isActive": True
}

# 无效的用户档案
invalid_user_profile = {
    "id": -1,  # 错误：ID不能为负数
    "username": "ab",  # 错误：用户名太短
    "email": "invalid-email",  # 错误：无效的邮箱格式
    "profile": {
        "firstName": "John",
        # 错误：缺少必需的lastName字段
        "age": 150  # 错误：年龄超出范围
    },
    "roles": ["user", "user"],  # 错误：重复的角色
    "extraProperty": "value"  # 错误：不允许的额外属性
}

# 有效的产品目录
valid_product_catalog = {
    "catalog": {
        "categories": [
            {"id": "cat_electronics", "name": "电子产品", "level": 1},
            {"id": "cat_phones", "name": "手机", "parentId": "cat_electronics", "level": 2},
            {"id": "cat_laptops", "name": "笔记本电脑", "parentId": "cat_electronics", "level": 2}
        ],
        "products": [
            {
                "id": "prod_phone_001",
                "name": "智能手机",
                "description": "高性能智能手机",
                "price": 3999.99,
                "category": "cat_phones",
                "images": [
                    {"url": "https://example.com/phone1.jpg", "alt": "智能手机正面", "isPrimary": True},
                    {"url": "https://example.com/phone2.jpg", "alt": "智能手机背面"}
                ],
                "specs": {
                    "brand": "TechBrand",
                    "model": "X100",
                    "screen": "6.1英寸"
                },
                "stock": {
                    "quantity": 100,
                    "location": "仓库A"
                },
                "tags": ["新品", "热卖"]
            }
        ]
    },
    "metadata": {
        "version": "1.0.0",
        "generatedAt": "2023-04-22T14:30:45Z"
    }
}

# 无效的产品目录
invalid_product_catalog = {
    "catalog": {
        "categories": [],  # 错误：至少需要一个类别
        "products": [
            {
                "id": "prod_invalid",  # 错误：不符合ID模式
                "name": "产品",  # 错误：缺少必需字段
                "price": -100,  # 错误：价格不能为负
                "category": "cat_nonexistent"  # 错误：类别不存在
            }
        ]
    },
    "metadata": {
        "version": "1.0",  # 错误：版本格式不正确
        # 错误：缺少generatedAt字段
    }
}

# ==================== 演示函数 ====================

def demo_validation():
    """演示JSON验证功能"""
    print("========== JSON验证演示 ==========")
    
    # 基本JSON字符串验证
    print("\n1. 基本JSON字符串验证:")
    valid_json = '{"name": "张三", "age": 30, "isActive": true}'
    invalid_json = '{"name": "张三", "age": 30, "isActive": true,}'  # 尾随逗号
    
    is_valid, data, error = validate_json_string(valid_json)
    print(f"有效JSON: {is_valid}, 数据: {data}")
    
    is_valid, data, error = validate_json_string(invalid_json)
    print(f"无效JSON: {is_valid}, 错误: {error}")
    
    # 用户档案验证
    print("\n2. 用户档案验证:")
    is_valid, errors = validate_user_profile(valid_user_profile)
    print(f"有效用户档案: {is_valid}")
    if not is_valid:
        for error in errors:
            print(f"  错误: {error.path} - {error.message}")
    
    is_valid, errors = validate_user_profile(invalid_user_profile)
    print(f"无效用户档案: {is_valid}")
    if not is_valid:
        for error in errors:
            print(f"  错误: {error.path} - {error.message}")
    
    # 产品目录验证
    print("\n3. 产品目录验证:")
    is_valid, errors = validate_product_catalog(valid_product_catalog)
    print(f"有效产品目录: {is_valid}")
    if not is_valid:
        for error in errors:
            print(f"  错误: {error.path} - {error.message}")
    
    is_valid, errors = validate_product_catalog(invalid_product_catalog)
    print(f"无效产品目录: {is_valid}")
    if not is_valid:
        for error in errors:
            print(f"  错误: {error.path} - {error.message}")
    
    print("\n========== 验证演示结束 ==========")

def save_schemas_to_files():
    """保存schema定义到文件"""
    schemas = {
        "user_profile_schema.json": {
            "type": "object",
            "required": ["id", "username", "email", "profile"],
            "properties": {
                "id": {"type": "integer", "minimum": 1},
                "username": {
                    "type": "string",
                    "minLength": 3,
                    "maxLength": 30,
                    "pattern": "^[a-zA-Z0-9_]+$"
                },
                "email": {"type": "string", "format": "email"},
                "profile": {
                    "type": "object",
                    "required": ["firstName", "lastName"],
                    "properties": {
                        "firstName": {"type": "string", "minLength": 1, "maxLength": 50},
                        "lastName": {"type": "string", "minLength": 1, "maxLength": 50},
                        "age": {"type": "integer", "minimum": 18, "maximum": 120},
                        "bio": {"type": "string", "maxLength": 500},
                        "avatar": {"type": "string", "format": "uri"},
                        "preferences": {
                            "type": "object",
                            "properties": {
                                "theme": {"type": "string", "enum": ["light", "dark"]},
                                "language": {"type": "string", "pattern": "^[a-z]{2}-[A-Z]{2}$"},
                                "notifications": {
                                    "type": "object",
                                    "properties": {
                                        "email": {"type": "boolean"},
                                        "sms": {"type": "boolean"},
                                        "push": {"type": "boolean"}
                                    }
                                }
                            }
                        }
                    }
                },
                "roles": {"type": "array", "items": {"type": "string"}, "uniqueItems": True},
                "lastLogin": {"type": "string", "format": "date-time"},
                "isActive": {"type": "boolean"}
            },
            "additionalProperties": False
        },
        "product_catalog_schema.json": {
            "type": "object",
            "required": ["catalog", "metadata"],
            "properties": {
                "catalog": {
                    "type": "object",
                    "required": ["categories", "products"],
                    "properties": {
                        "categories": {
                            "type": "array",
                            "minItems": 1,
                            "items": {
                                "type": "object",
                                "required": ["id", "name"],
                                "properties": {
                                    "id": {"type": "string", "pattern": "^cat_[a-z0-9_]+$"},
                                    "name": {"type": "string", "minLength": 1},
                                    "parentId": {"type": ["string", "null"], "pattern": "^cat_[a-z0-9_]+$"},
                                    "level": {"type": "integer", "minimum": 1}
                                }
                            }
                        },
                        "products": {
                            "type": "array",
                            "minItems": 1,
                            "items": {
                                "type": "object",
                                "required": ["id", "name", "price", "category"],
                                "properties": {
                                    "id": {"type": "string", "pattern": "^prod_[a-z0-9_]+$"},
                                    "name": {"type": "string", "minLength": 1},
                                    "description": {"type": "string"},
                                    "price": {"type": "number", "minimum": 0, "multipleOf": 0.01},
                                    "category": {"type": "string", "pattern": "^cat_[a-z0-9_]+$"},
                                    "images": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "required": ["url"],
                                            "properties": {
                                                "url": {"type": "string", "format": "uri"},
                                                "alt": {"type": "string"},
                                                "isPrimary": {"type": "boolean"}
                                            }
                                        }
                                    },
                                    "specs": {"type": "object"},
                                    "stock": {
                                        "type": "object",
                                        "properties": {
                                            "quantity": {"type": "integer", "minimum": 0},
                                            "location": {"type": "string"}
                                        }
                                    },
                                    "tags": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "uniqueItems": True
                                    }
                                }
                            }
                        }
                    }
                },
                "metadata": {
                    "type": "object",
                    "required": ["version", "generatedAt"],
                    "properties": {
                        "version": {"type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$"},
                        "generatedAt": {"type": "string", "format": "date-time"}
                    }
                }
            }
        }
    }
    
    for filename, schema in schemas.items():
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)
    
    print("Schema文件已保存")

if __name__ == "__main__":
    demo_validation()
    save_schemas_to_files()