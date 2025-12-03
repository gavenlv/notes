"""
解释器模式 (Interpreter Pattern) 示例代码

解释器模式给定一个语言，定义它的文法的一种表示，并定义一个解释器，这个解释器使用该表示来解释语言中的句子。
"""

from abc import ABC, abstractmethod
from typing import Dict, List


class Expression(ABC):
    """抽象表达式类"""
    
    @abstractmethod
    def interpret(self, context: Dict) -> int:
        """解释方法"""
        pass


class Number(Expression):
    """终结符表达式 - 数字"""
    
    def __init__(self, value: int):
        self._value = value
    
    def interpret(self, context: Dict) -> int:
        return self._value
    
    def __str__(self):
        return str(self._value)


class Variable(Expression):
    """终结符表达式 - 变量"""
    
    def __init__(self, name: str):
        self._name = name
    
    def interpret(self, context: Dict) -> int:
        if self._name in context:
            return context[self._name]
        else:
            raise KeyError(f"变量 '{self._name}' 未定义")
    
    def __str__(self):
        return self._name


class Add(Expression):
    """非终结符表达式 - 加法"""
    
    def __init__(self, left: Expression, right: Expression):
        self._left = left
        self._right = right
    
    def interpret(self, context: Dict) -> int:
        return self._left.interpret(context) + self._right.interpret(context)
    
    def __str__(self):
        return f"({self._left} + {self._right})"


class Subtract(Expression):
    """非终结符表达式 - 减法"""
    
    def __init__(self, left: Expression, right: Expression):
        self._left = left
        self._right = right
    
    def interpret(self, context: Dict) -> int:
        return self._left.interpret(context) - self._right.interpret(context)
    
    def __str__(self):
        return f"({self._left} - {self._right})"


class Multiply(Expression):
    """非终结符表达式 - 乘法"""
    
    def __init__(self, left: Expression, right: Expression):
        self._left = left
        self._right = right
    
    def interpret(self, context: Dict) -> int:
        return self._left.interpret(context) * self._right.interpret(context)
    
    def __str__(self):
        return f"({self._left} * {self._right})"


class Divide(Expression):
    """非终结符表达式 - 除法"""
    
    def __init__(self, left: Expression, right: Expression):
        self._left = left
        self._right = right
    
    def interpret(self, context: Dict) -> int:
        denominator = self._right.interpret(context)
        if denominator == 0:
            raise ValueError("除数不能为零")
        return self._left.interpret(context) // denominator
    
    def __str__(self):
        return f"({self._left} / {self._right})"


# 测试基础解释器模式
def test_basic_interpreter():
    """测试基础解释器模式"""
    print("=== 解释器模式测试 - 基础示例 ===\n")
    
    # 创建上下文（变量环境）
    context = {"x": 10, "y": 5, "z": 2}
    
    # 构建表达式: (x + y) * z
    expression = Multiply(
        Add(Variable("x"), Variable("y")),
        Variable("z")
    )
    
    print(f"表达式: {expression}")
    print(f"上下文: {context}")
    
    # 解释执行
    result = expression.interpret(context)
    print(f"结果: {result}")
    
    print("\n---")
    
    # 构建更复杂的表达式: ((x * y) - z) / 2
    complex_expression = Divide(
        Subtract(
            Multiply(Variable("x"), Variable("y")),
            Variable("z")
        ),
        Number(2)
    )
    
    print(f"复杂表达式: {complex_expression}")
    result2 = complex_expression.interpret(context)
    print(f"结果: {result2}")


# 实际应用示例：布尔表达式解释器
def test_boolean_interpreter():
    """测试布尔表达式解释器"""
    print("\n=== 解释器模式应用 - 布尔表达式示例 ===\n")
    
    class BooleanExpression(ABC):
        """布尔表达式抽象类"""
        
        @abstractmethod
        def interpret(self, context: Dict) -> bool:
            pass
    
    class BooleanVariable(BooleanExpression):
        """布尔变量"""
        
        def __init__(self, name: str):
            self._name = name
        
        def interpret(self, context: Dict) -> bool:
            if self._name in context:
                return context[self._name]
            else:
                raise KeyError(f"布尔变量 '{self._name}' 未定义")
        
        def __str__(self):
            return self._name
    
    class AndExpression(BooleanExpression):
        """与运算"""
        
        def __init__(self, left: BooleanExpression, right: BooleanExpression):
            self._left = left
            self._right = right
        
        def interpret(self, context: Dict) -> bool:
            return self._left.interpret(context) and self._right.interpret(context)
        
        def __str__(self):
            return f"({self._left} AND {self._right})"
    
    class OrExpression(BooleanExpression):
        """或运算"""
        
        def __init__(self, left: BooleanExpression, right: BooleanExpression):
            self._left = left
            self._right = right
        
        def interpret(self, context: Dict) -> bool:
            return self._left.interpret(context) or self._right.interpret(context)
        
        def __str__(self):
            return f"({self._left} OR {self._right})"
    
    class NotExpression(BooleanExpression):
        """非运算"""
        
        def __init__(self, expression: BooleanExpression):
            self._expression = expression
        
        def interpret(self, context: Dict) -> bool:
            return not self._expression.interpret(context)
        
        def __str__(self):
            return f"NOT {self._expression}"
    
    # 测试布尔表达式
    context = {
        "A": True,
        "B": False,
        "C": True,
        "D": False
    }
    
    print("布尔上下文:", context)
    
    # 构建表达式: (A AND B) OR (C AND NOT D)
    expression = OrExpression(
        AndExpression(BooleanVariable("A"), BooleanVariable("B")),
        AndExpression(BooleanVariable("C"), NotExpression(BooleanVariable("D")))
    )
    
    print(f"布尔表达式: {expression}")
    result = expression.interpret(context)
    print(f"结果: {result}")
    
    print("\n---")
    
    # 构建另一个表达式: NOT (A OR B) AND C
    expression2 = AndExpression(
        NotExpression(OrExpression(BooleanVariable("A"), BooleanVariable("B"))),
        BooleanVariable("C")
    )
    
    print(f"布尔表达式: {expression2}")
    result2 = expression2.interpret(context)
    print(f"结果: {result2}")


# 实际应用示例：SQL WHERE 条件解释器
def test_sql_interpreter():
    """测试SQL WHERE条件解释器"""
    print("\n=== 解释器模式应用 - SQL条件解释器示例 ===\n")
    
    class SQLExpression(ABC):
        """SQL表达式抽象类"""
        
        @abstractmethod
        def interpret(self, record: Dict) -> bool:
            """解释表达式，判断记录是否满足条件"""
            pass
    
    class EqualExpression(SQLExpression):
        """等于表达式"""
        
        def __init__(self, field: str, value):
            self._field = field
            self._value = value
        
        def interpret(self, record: Dict) -> bool:
            return record.get(self._field) == self._value
        
        def __str__(self):
            return f"{self._field} = {self._value}"
    
    class GreaterThanExpression(SQLExpression):
        """大于表达式"""
        
        def __init__(self, field: str, value):
            self._field = field
            self._value = value
        
        def interpret(self, record: Dict) -> bool:
            field_value = record.get(self._field)
            return field_value is not None and field_value > self._value
        
        def __str__(self):
            return f"{self._field} > {self._value}"
    
    class LessThanExpression(SQLExpression):
        """小于表达式"""
        
        def __init__(self, field: str, value):
            self._field = field
            self._value = value
        
        def interpret(self, record: Dict) -> bool:
            field_value = record.get(self._field)
            return field_value is not None and field_value < self._value
        
        def __str__(self):
            return f"{self._field} < {self._value}"
    
    class AndExpression(SQLExpression):
        """AND表达式"""
        
        def __init__(self, left: SQLExpression, right: SQLExpression):
            self._left = left
            self._right = right
        
        def interpret(self, record: Dict) -> bool:
            return self._left.interpret(record) and self._right.interpret(record)
        
        def __str__(self):
            return f"({self._left} AND {self._right})"
    
    class OrExpression(SQLExpression):
        """OR表达式"""
        
        def __init__(self, left: SQLExpression, right: SQLExpression):
            self._left = left
            self._right = right
        
        def interpret(self, record: Dict) -> bool:
            return self._left.interpret(record) or self._right.interpret(record)
        
        def __str__(self):
            return f"({self._left} OR {self._right})"
    
    # 测试SQL条件解释器
    records = [
        {"id": 1, "name": "Alice", "age": 25, "salary": 50000},
        {"id": 2, "name": "Bob", "age": 30, "salary": 60000},
        {"id": 3, "name": "Charlie", "age": 35, "salary": 70000},
        {"id": 4, "name": "David", "age": 28, "salary": 55000}
    ]
    
    # 构建WHERE条件: age > 25 AND salary < 65000
    where_condition = AndExpression(
        GreaterThanExpression("age", 25),
        LessThanExpression("salary", 65000)
    )
    
    print(f"WHERE条件: {where_condition}")
    print("\n符合条件的记录:")
    
    for record in records:
        if where_condition.interpret(record):
            print(f"  {record}")
    
    print("\n---")
    
    # 构建更复杂的条件: (age > 25 AND salary < 65000) OR name = 'Charlie'
    complex_condition = OrExpression(
        where_condition,
        EqualExpression("name", "Charlie")
    )
    
    print(f"复杂WHERE条件: {complex_condition}")
    print("\n符合条件的记录:")
    
    for record in records:
        if complex_condition.interpret(record):
            print(f"  {record}")


# 实际应用示例：简单规则引擎
def test_rule_engine():
    """测试规则引擎解释器"""
    print("\n=== 解释器模式应用 - 规则引擎示例 ===\n")
    
    class RuleExpression(ABC):
        """规则表达式抽象类"""
        
        @abstractmethod
        def evaluate(self, facts: Dict) -> bool:
            pass
    
    class FactExpression(RuleExpression):
        """事实表达式"""
        
        def __init__(self, fact_name: str, expected_value):
            self._fact_name = fact_name
            self._expected_value = expected_value
        
        def evaluate(self, facts: Dict) -> bool:
            return facts.get(self._fact_name) == self._expected_value
    
    class ComparisonExpression(RuleExpression):
        """比较表达式"""
        
        def __init__(self, fact_name: str, operator: str, value):
            self._fact_name = fact_name
            self._operator = operator
            self._value = value
        
        def evaluate(self, facts: Dict) -> bool:
            fact_value = facts.get(self._fact_name)
            if fact_value is None:
                return False
            
            if self._operator == "==":
                return fact_value == self._value
            elif self._operator == "!=":
                return fact_value != self._value
            elif self._operator == ">":
                return fact_value > self._value
            elif self._operator == "<":
                return fact_value < self._value
            elif self._operator == ">=":
                return fact_value >= self._value
            elif self._operator == "<=":
                return fact_value <= self._value
            else:
                return False
    
    class AndRule(RuleExpression):
        """与规则"""
        
        def __init__(self, *expressions: RuleExpression):
            self._expressions = expressions
        
        def evaluate(self, facts: Dict) -> bool:
            return all(expr.evaluate(facts) for expr in self._expressions)
    
    class OrRule(RuleExpression):
        """或规则"""
        
        def __init__(self, *expressions: RuleExpression):
            self._expressions = expressions
        
        def evaluate(self, facts: Dict) -> bool:
            return any(expr.evaluate(facts) for expr in self._expressions)
    
    class NotRule(RuleExpression):
        """非规则"""
        
        def __init__(self, expression: RuleExpression):
            self._expression = expression
        
        def evaluate(self, facts: Dict) -> bool:
            return not self._expression.evaluate(facts)
    
    class Rule:
        """规则类"""
        
        def __init__(self, name: str, condition: RuleExpression, action: str):
            self.name = name
            self.condition = condition
            self.action = action
        
        def fire(self, facts: Dict) -> bool:
            """触发规则"""
            if self.condition.evaluate(facts):
                print(f"规则 '{self.name}' 触发: {self.action}")
                return True
            return False
    
    # 测试规则引擎
    facts = {
        "age": 25,
        "income": 50000,
        "credit_score": 700,
        "employment_status": "employed",
        "loan_amount": 20000
    }
    
    print("事实数据:", facts)
    
    # 定义规则
    rules = [
        Rule(
            "高信用贷款",
            AndRule(
                ComparisonExpression("credit_score", ">=", 750),
                ComparisonExpression("income", ">", 40000)
            ),
            "批准高额度贷款"
        ),
        Rule(
            "中等信用贷款",
            AndRule(
                ComparisonExpression("credit_score", ">=", 650),
                ComparisonExpression("income", ">", 30000),
                FactExpression("employment_status", "employed")
            ),
            "批准中等额度贷款"
        ),
        Rule(
            "高风险拒绝",
            OrRule(
                ComparisonExpression("credit_score", "<", 600),
                ComparisonExpression("income", "<", 20000)
            ),
            "拒绝贷款申请"
        )
    ]
    
    print("\n执行规则引擎:")
    for rule in rules:
        rule.fire(facts)


# 简单的表达式解析器（简化版）
def test_expression_parser():
    """测试表达式解析器"""
    print("\n=== 简单表达式解析器示例 ===\n")
    
    class Parser:
        """简单表达式解析器"""
        
        def __init__(self, expression: str):
            self._tokens = self._tokenize(expression)
            self._current_token = 0
        
        def _tokenize(self, expression: str) -> List[str]:
            """将表达式分词"""
            # 简化版分词，只处理空格分隔的表达式
            return expression.split()
        
        def parse(self) -> Expression:
            """解析表达式"""
            return self._parse_expression()
        
        def _parse_expression(self) -> Expression:
            """解析表达式"""
            token = self._get_next_token()
            
            if token == "(":
                # 解析括号表达式
                left = self._parse_expression()
                operator = self._get_next_token()
                right = self._parse_expression()
                self._get_next_token()  # 消耗右括号
                
                if operator == "+":
                    return Add(left, right)
                elif operator == "-":
                    return Subtract(left, right)
                elif operator == "*":
                    return Multiply(left, right)
                elif operator == "/":
                    return Divide(left, right)
                else:
                    raise ValueError(f"未知操作符: {operator}")
            else:
                # 解析数字或变量
                if token.isdigit():
                    return Number(int(token))
                else:
                    return Variable(token)
        
        def _get_next_token(self) -> str:
            """获取下一个token"""
            if self._current_token < len(self._tokens):
                token = self._tokens[self._current_token]
                self._current_token += 1
                return token
            else:
                return ""
    
    # 测试表达式解析器
    expressions = [
        "( x + y ) * z",
        "( ( x * y ) - z ) / 2"
    ]
    
    context = {"x": 10, "y": 5, "z": 2}
    
    for expr_str in expressions:
        print(f"解析表达式: {expr_str}")
        parser = Parser(expr_str)
        expression = parser.parse()
        
        print(f"抽象语法树: {expression}")
        result = expression.interpret(context)
        print(f"计算结果: {result}\n")


if __name__ == "__main__":
    test_basic_interpreter()
    test_boolean_interpreter()
    test_sql_interpreter()
    test_rule_engine()
    test_expression_parser()
    
    print("\n=== 解释器模式总结 ===")
    print("优点：")
    print("- 易于改变和扩展文法：由于在解释器模式中使用类来表示语言的文法规则，因此可以通过继承等机制来改变或扩展文法")
    print("- 易于实现文法：定义抽象语法树中各个节点的类的实现大体类似，这些类都易于直接编写")
    print("- 增加了新的解释表达式的方式：解释器模式可以方便地实现新的表达式")
    print("\n缺点：")
    print("- 对于复杂文法难以维护：在解释器模式中，每一条规则至少需要定义一个类")
    print("- 执行效率较低：由于在解释器模式中使用了大量的循环和递归调用")
    print("- 应用场景很有限：解释器模式只适用于那些文法比较简单、且对效率要求不高的场景")
    print("\n适用场景：")
    print("- 可以将一个需要解释执行的语言中的句子表示为一个抽象语法树")
    print("- 一些重复出现的问题可以用一种简单的语言来进行表达")
    print("- 一个语言的文法较为简单")
    print("- 执行效率不是关键问题")
