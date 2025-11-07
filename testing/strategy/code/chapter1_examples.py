# 第1章：测试基础概念 - 示例代码

## 实验1：基本测试概念验证

### 1.1 简单断言测试

```python
# simple_assertion_test.py
"""
简单断言测试示例
演示最基本的测试断言概念
"""

def add(a, b):
    """简单的加法函数"""
    return a + b

def subtract(a, b):
    """简单的减法函数"""
    return a - b

def multiply(a, b):
    """简单的乘法函数"""
    return a * b

def divide(a, b):
    """简单的除法函数"""
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b

# 手动测试函数
def test_arithmetic_operations():
    """测试算术运算函数"""
    # 测试加法
    assert add(2, 3) == 5, "2 + 3 应该等于 5"
    assert add(-1, 1) == 0, "-1 + 1 应该等于 0"
    assert add(0, 0) == 0, "0 + 0 应该等于 0"
    
    # 测试减法
    assert subtract(5, 3) == 2, "5 - 3 应该等于 2"
    assert subtract(1, 1) == 0, "1 - 1 应该等于 0"
    
    # 测试乘法
    assert multiply(3, 4) == 12, "3 * 4 应该等于 12"
    assert multiply(0, 5) == 0, "0 * 5 应该等于 0"
    
    # 测试除法
    assert divide(10, 2) == 5, "10 / 2 应该等于 5"
    assert divide(1, 4) == 0.25, "1 / 4 应该等于 0.25"
    
    # 测试异常
    try:
        divide(5, 0)
        assert False, "除数为零时应该抛出异常"
    except ValueError:
        pass  # 预期的异常
    
    print("所有算术运算测试通过!")

if __name__ == "__main__":
    test_arithmetic_operations()
```

### 1.2 测试边界条件

```python
# boundary_test.py
"""
边界条件测试示例
演示如何测试边界条件和极端情况
"""

def is_adult(age):
    """判断是否成年（18岁及以上）"""
    if age < 0:
        raise ValueError("年龄不能为负数")
    return age >= 18

def calculate_grade(score):
    """根据分数计算等级（0-100分）"""
    if score < 0 or score > 100:
        raise ValueError("分数必须在0-100之间")
    
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"

def test_boundary_conditions():
    """测试边界条件"""
    # 测试is_adult函数的边界条件
    print("测试is_adult函数...")
    
    # 边界值测试
    assert is_adult(18) == True, "18岁应该算成年"
    assert is_adult(17) == False, "17岁不应该算成年"
    
    # 极端值测试
    assert is_adult(0) == False, "0岁不应该算成年"
    assert is_adult(100) == True, "100岁应该算成年"
    
    # 异常测试
    try:
        is_adult(-1)
        assert False, "负年龄应该抛出异常"
    except ValueError:
        print("负年龄异常测试通过")
    
    print("is_adult函数测试通过!")
    
    # 测试calculate_grade函数的边界条件
    print("\n测试calculate_grade函数...")
    
    # 边界值测试
    assert calculate_grade(90) == "A", "90分应该是A级"
    assert calculate_grade(89) == "B", "89分应该是B级"
    assert calculate_grade(80) == "B", "80分应该是B级"
    assert calculate_grade(79) == "C", "79分应该是C级"
    assert calculate_grade(70) == "C", "70分应该是C级"
    assert calculate_grade(69) == "D", "69分应该是D级"
    assert calculate_grade(60) == "D", "60分应该是D级"
    assert calculate_grade(59) == "F", "59分应该是F级"
    assert calculate_grade(0) == "F", "0分应该是F级"
    assert calculate_grade(100) == "A", "100分应该是A级"
    
    # 异常测试
    try:
        calculate_grade(-1)
        assert False, "负分数应该抛出异常"
    except ValueError:
        print("负分数异常测试通过")
    
    try:
        calculate_grade(101)
        assert False, "超过100的分数应该抛出异常"
    except ValueError:
        print("超范围分数异常测试通过")
    
    print("calculate_grade函数测试通过!")

if __name__ == "__main__":
    test_boundary_conditions()
```

### 1.3 测试驱动开发(TDD)入门示例

```python
# tdd_intro_example.py
"""
测试驱动开发入门示例
演示先写测试再写代码的TDD基本流程
"""

# 阶段1：先写测试（此时函数尚未实现）
def test_string_calculator():
    """字符串计算器测试"""
    # 测试1：空字符串应返回0
    assert string_calculator("") == 0, "空字符串应返回0"
    
    # 测试2：单个数字应返回该数字
    assert string_calculator("1") == 1, "字符串'1'应返回1"
    assert string_calculator("5") == 5, "字符串'5'应返回5"
    
    # 测试3：两个数字用逗号分隔应返回它们的和
    assert string_calculator("1,2") == 3, "字符串'1,2'应返回3"
    assert string_calculator("10,20") == 30, "字符串'10,20'应返回30"
    
    # 测试4：多个数字用逗号分隔应返回它们的和
    assert string_calculator("1,2,3") == 6, "字符串'1,2,3'应返回6"
    assert string_calculator("10,20,30,40") == 100, "字符串'10,20,30,40'应返回100"
    
    # 测试5：处理换行符
    assert string_calculator("1\n2,3") == 6, "字符串'1\\n2,3'应返回6"
    
    # 测试6：处理自定义分隔符
    assert string_calculator("//;\n1;2") == 3, "自定义分隔符测试失败"
    
    # 测试7：处理负数应抛出异常
    try:
        string_calculator("1,-2,3")
        assert False, "负数应抛出异常"
    except ValueError as e:
        assert "负数不被允许" in str(e), "异常消息应包含负数信息"
    
    print("所有字符串计算器测试通过!")

# 阶段2：实现函数以满足测试需求
def string_calculator(numbers_str):
    """
    字符串计算器函数
    根据字符串中的数字计算它们的和
    
    参数:
        numbers_str: 包含数字的字符串，数字之间可以用逗号或换行符分隔
        
    返回:
        数字的总和
        
    异常:
        ValueError: 当字符串包含负数时抛出
    """
    # 处理空字符串
    if not numbers_str:
        return 0
    
    # 检查是否有自定义分隔符
    delimiter = ","
    if numbers_str.startswith("//"):
        # 提取自定义分隔符
        delimiter_line_end = numbers_str.find("\n")
        delimiter = numbers_str[2:delimiter_line_end]
        numbers_str = numbers_str[delimiter_line_end + 1:]
    
    # 替换换行符为默认分隔符，然后分割
    numbers_str = numbers_str.replace("\n", delimiter)
    numbers = numbers_str.split(delimiter)
    
    # 转换为整数并检查负数
    total = 0
    negatives = []
    for num_str in numbers:
        if num_str:  # 忽略空字符串
            num = int(num_str)
            if num < 0:
                negatives.append(num)
            total += num
    
    # 如果有负数，抛出异常
    if negatives:
        raise ValueError(f"负数不被允许: {', '.join(map(str, negatives))}")
    
    return total

if __name__ == "__main__":
    # 运行测试
    test_string_calculator()
```

## 实验2：测试金字塔概念验证

### 2.1 单元测试示例

```python
# unit_test_example.py
"""
单元测试示例
演示如何编写独立的单元测试
"""

class Calculator:
    """简单计算器类"""
    
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        """加法运算"""
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def subtract(self, a, b):
        """减法运算"""
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result
    
    def multiply(self, a, b):
        """乘法运算"""
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result
    
    def divide(self, a, b):
        """除法运算"""
        if b == 0:
            raise ValueError("除数不能为零")
        result = a / b
        self.history.append(f"{a} / {b} = {result}")
        return result
    
    def get_history(self):
        """获取计算历史"""
        return self.history
    
    def clear_history(self):
        """清除计算历史"""
        self.history = []

# 单元测试
def test_calculator_unit():
    """计算器单元测试"""
    print("运行计算器单元测试...")
    
    # 创建计算器实例
    calc = Calculator()
    
    # 测试加法
    assert calc.add(2, 3) == 5, "2 + 3 应该等于 5"
    assert calc.add(-1, 1) == 0, "-1 + 1 应该等于 0"
    
    # 测试减法
    assert calc.subtract(5, 3) == 2, "5 - 3 应该等于 2"
    assert calc.subtract(1, 1) == 0, "1 - 1 应该等于 0"
    
    # 测试乘法
    assert calc.multiply(3, 4) == 12, "3 * 4 应该等于 12"
    assert calc.multiply(0, 5) == 0, "0 * 5 应该等于 0"
    
    # 测试除法
    assert calc.divide(10, 2) == 5, "10 / 2 应该等于 5"
    assert calc.divide(1, 4) == 0.25, "1 / 4 应该等于 0.25"
    
    # 测试异常
    try:
        calc.divide(5, 0)
        assert False, "除数为零时应该抛出异常"
    except ValueError:
        pass  # 预期的异常
    
    # 测试历史记录
    history = calc.get_history()
    assert len(history) == 8, f"应该有8条历史记录，实际有{len(history)}条"
    assert "2 + 3 = 5" in history, "历史记录中应包含'2 + 3 = 5'"
    
    # 测试清除历史
    calc.clear_history()
    assert len(calc.get_history()) == 0, "清除历史后应该没有记录"
    
    print("计算器单元测试通过!")

if __name__ == "__main__":
    test_calculator_unit()
```

### 2.2 集成测试示例

```python
# integration_test_example.py
"""
集成测试示例
演示如何测试多个组件之间的交互
"""

# 被测试的组件
class DataStorage:
    """数据存储组件"""
    
    def __init__(self):
        self.data = {}
    
    def save(self, key, value):
        """保存数据"""
        self.data[key] = value
        return True
    
    def load(self, key):
        """加载数据"""
        if key not in self.data:
            raise KeyError(f"键'{key}'不存在")
        return self.data[key]
    
    def delete(self, key):
        """删除数据"""
        if key in self.data:
            del self.data[key]
            return True
        return False
    
    def exists(self, key):
        """检查键是否存在"""
        return key in self.data

class DataProcessor:
    """数据处理组件"""
    
    def __init__(self, storage):
        self.storage = storage
    
    def process_and_save(self, key, data):
        """处理数据并保存"""
        # 简单的数据处理：转换为字符串并添加时间戳
        import time
        processed_data = f"{data}_processed_{int(time.time())}"
        return self.storage.save(key, processed_data)
    
    def load_and_process(self, key):
        """加载数据并处理"""
        raw_data = self.storage.load(key)
        # 简单的处理：移除时间戳
        return raw_data.split('_processed_')[0]
    
    def batch_process(self, data_dict):
        """批量处理数据"""
        results = {}
        for key, value in data_dict.items():
            success = self.process_and_save(key, value)
            results[key] = success
        return results

class DataReporter:
    """数据报告组件"""
    
    def __init__(self, processor):
        self.processor = processor
    
    def generate_report(self, keys):
        """生成报告"""
        report = {}
        for key in keys:
            try:
                data = self.processor.load_and_process(key)
                report[key] = {"status": "success", "data": data}
            except Exception as e:
                report[key] = {"status": "error", "message": str(e)}
        return report
    
    def count_successful_operations(self, keys):
        """统计成功操作数"""
        report = self.generate_report(keys)
        successful = sum(1 for item in report.values() if item["status"] == "success")
        return successful

# 集成测试
def test_data_integration():
    """数据组件集成测试"""
    print("运行数据组件集成测试...")
    
    # 设置测试环境
    storage = DataStorage()
    processor = DataProcessor(storage)
    reporter = DataReporter(processor)
    
    # 测试数据处理和存储的集成
    test_key = "test_data"
    test_value = "sample_value"
    
    # 处理并保存数据
    save_result = processor.process_and_save(test_key, test_value)
    assert save_result == True, "数据保存应该成功"
    assert storage.exists(test_key) == True, "数据应该存在于存储中"
    
    # 加载并处理数据
    loaded_data = processor.load_and_process(test_key)
    assert loaded_data == test_value, f"加载的数据应该是'{test_value}'，实际是'{loaded_data}'"
    
    # 测试批量处理
    batch_data = {
        "item1": "value1",
        "item2": "value2",
        "item3": "value3"
    }
    batch_results = processor.batch_process(batch_data)
    assert all(batch_results.values()) == True, "所有批量操作应该成功"
    
    # 验证所有数据都已保存
    for key in batch_data.keys():
        assert storage.exists(key) == True, f"键'{key}'应该存在于存储中"
    
    # 测试报告生成
    all_keys = [test_key] + list(batch_data.keys())
    report = reporter.generate_report(all_keys)
    
    # 验证报告内容
    assert len(report) == len(all_keys), "报告应该包含所有键"
    assert all(item["status"] == "success" for item in report.values()) == True, "所有操作应该成功"
    
    # 测试成功操作计数
    success_count = reporter.count_successful_operations(all_keys)
    assert success_count == len(all_keys), f"成功操作数应该是{len(all_keys)}，实际是{success_count}"
    
    # 测试错误处理
    invalid_key = "non_existent_key"
    error_report = reporter.generate_report([invalid_key])
    assert error_report[invalid_key]["status"] == "error", "不存在的键应该返回错误"
    
    print("数据组件集成测试通过!")

if __name__ == "__main__":
    test_data_integration()
```

### 2.3 端到端测试示例

```python
# e2e_test_example.py
"""
端到端测试示例
演示如何测试完整的用户场景
"""

# 被测试的系统组件
class User:
    """用户类"""
    
    def __init__(self, username, email):
        self.username = username
        self.email = email
        self.is_authenticated = False
        self.cart = []
    
    def authenticate(self, password):
        """用户认证"""
        # 简化认证逻辑
        self.is_authenticated = (password == "password123")
        return self.is_authenticated
    
    def add_to_cart(self, product_id, quantity=1):
        """添加商品到购物车"""
        if not self.is_authenticated:
            raise PermissionError("用户未认证")
        
        # 检查商品是否已在购物车中
        for item in self.cart:
            if item["product_id"] == product_id:
                item["quantity"] += quantity
                return True
        
        # 添加新商品
        self.cart.append({"product_id": product_id, "quantity": quantity})
        return True
    
    def remove_from_cart(self, product_id):
        """从购物车移除商品"""
        if not self.is_authenticated:
            raise PermissionError("用户未认证")
        
        for i, item in enumerate(self.cart):
            if item["product_id"] == product_id:
                del self.cart[i]
                return True
        return False
    
    def get_cart_items(self):
        """获取购物车商品"""
        if not self.is_authenticated:
            raise PermissionError("用户未认证")
        return self.cart
    
    def clear_cart(self):
        """清空购物车"""
        if not self.is_authenticated:
            raise PermissionError("用户未认证")
        self.cart = []
        return True

class Product:
    """商品类"""
    
    def __init__(self, product_id, name, price, stock):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.stock = stock
    
    def is_available(self, quantity=1):
        """检查商品是否有库存"""
        return self.stock >= quantity
    
    def reduce_stock(self, quantity):
        """减少库存"""
        if self.is_available(quantity):
            self.stock -= quantity
            return True
        return False

class Order:
    """订单类"""
    
    def __init__(self, order_id, user, items):
        self.order_id = order_id
        self.user = user
        self.items = items
        self.status = "pending"
        self.total_amount = 0
    
    def calculate_total(self, products):
        """计算订单总额"""
        total = 0
        for item in self.items:
            product_id = item["product_id"]
            quantity = item["quantity"]
            
            # 找到对应商品
            for product in products:
                if product.product_id == product_id:
                    total += product.price * quantity
                    break
        
        self.total_amount = total
        return total
    
    def process(self, products):
        """处理订单"""
        # 检查所有商品是否有库存
        for item in self.items:
            product_id = item["product_id"]
            quantity = item["quantity"]
            
            # 找到对应商品
            for product in products:
                if product.product_id == product_id:
                    if not product.is_available(quantity):
                        self.status = "failed"
                        return False, f"商品 {product.name} 库存不足"
                    break
        
        # 减少库存
        for item in self.items:
            product_id = item["product_id"]
            quantity = item["quantity"]
            
            for product in products:
                if product.product_id == product_id:
                    product.reduce_stock(quantity)
                    break
        
        # 清空用户购物车
        self.user.clear_cart()
        
        # 更新订单状态
        self.status = "completed"
        return True, "订单处理成功"

class ECommerceSystem:
    """电子商务系统"""
    
    def __init__(self):
        self.users = {}
        self.products = {}
        self.orders = {}
        self.next_order_id = 1
    
    def register_user(self, username, email):
        """注册用户"""
        if username in self.users:
            return False, "用户名已存在"
        
        user = User(username, email)
        self.users[username] = user
        return True, "用户注册成功"
    
    def login_user(self, username, password):
        """用户登录"""
        if username not in self.users:
            return False, "用户不存在"
        
        user = self.users[username]
        if user.authenticate(password):
            return True, user
        else:
            return False, "密码错误"
    
    def add_product(self, product_id, name, price, stock):
        """添加商品"""
        if product_id in self.products:
            return False, "商品ID已存在"
        
        product = Product(product_id, name, price, stock)
        self.products[product_id] = product
        return True, "商品添加成功"
    
    def create_order(self, user):
        """创建订单"""
        if not user.is_authenticated:
            return False, "用户未认证"
        
        cart_items = user.get_cart_items()
        if not cart_items:
            return False, "购物车为空"
        
        order_id = f"order_{self.next_order_id}"
        self.next_order_id += 1
        
        order = Order(order_id, user, cart_items)
        self.orders[order_id] = order
        
        return True, order

# 端到端测试
def test_ecommerce_e2e():
    """电子商务系统端到端测试"""
    print("运行电子商务系统端到端测试...")
    
    # 初始化系统
    system = ECommerceSystem()
    
    # 场景1：用户注册和登录
    print("\n场景1：用户注册和登录")
    
    # 注册用户
    register_result, message = system.register_user("testuser", "test@example.com")
    assert register_result == True, f"用户注册失败: {message}"
    
    # 尝试用错误密码登录
    login_result, _ = system.login_user("testuser", "wrongpassword")
    assert login_result == False, "错误密码不应该登录成功"
    
    # 用正确密码登录
    login_result, user = system.login_user("testuser", "password123")
    assert login_result == True, "正确密码应该登录成功"
    assert user.username == "testuser", "登录用户名应该是'testuser'"
    
    # 场景2：添加商品和购物车操作
    print("\n场景2：添加商品和购物车操作")
    
    # 添加商品
    add_result1, _ = system.add_product("p1", "商品1", 10.0, 100)
    add_result2, _ = system.add_product("p2", "商品2", 20.0, 50)
    add_result3, _ = system.add_product("p3", "商品3", 30.0, 10)
    
    assert add_result1 == True, "商品1添加应该成功"
    assert add_result2 == True, "商品2添加应该成功"
    assert add_result3 == True, "商品3添加应该成功"
    
    # 添加商品到购物车
    user.add_to_cart("p1", 2)
    user.add_to_cart("p2", 1)
    user.add_to_cart("p3", 3)
    
    # 验证购物车内容
    cart_items = user.get_cart_items()
    assert len(cart_items) == 3, f"购物车应该有3种商品，实际有{len(cart_items)}种"
    
    # 验证商品数量
    p1_item = next(item for item in cart_items if item["product_id"] == "p1")
    p2_item = next(item for item in cart_items if item["product_id"] == "p2")
    p3_item = next(item for item in cart_items if item["product_id"] == "p3")
    
    assert p1_item["quantity"] == 2, "商品1数量应该是2"
    assert p2_item["quantity"] == 1, "商品2数量应该是1"
    assert p3_item["quantity"] == 3, "商品3数量应该是3"
    
    # 场景3：创建和处理订单
    print("\n场景3：创建和处理订单")
    
    # 创建订单
    create_result, order = system.create_order(user)
    assert create_result == True, f"订单创建失败"
    assert order.status == "pending", "新订单状态应该是'pending'"
    
    # 计算订单总额
    products = [system.products["p1"], system.products["p2"], system.products["p3"]]
    total = order.calculate_total(products)
    expected_total = 10.0 * 2 + 20.0 * 1 + 30.0 * 3  # 20 + 20 + 90 = 130
    assert total == expected_total, f"订单总额应该是{expected_total}，实际是{total}"
    
    # 处理订单
    process_result, message = order.process(products)
    assert process_result == True, f"订单处理失败: {message}"
    assert order.status == "completed", "处理后的订单状态应该是'completed'"
    
    # 验证库存减少
    assert system.products["p1"].stock == 98, "商品1库存应该是98"
    assert system.products["p2"].stock == 49, "商品2库存应该是49"
    assert system.products["p3"].stock == 7, "商品3库存应该是7"
    
    # 验证购物车已清空
    cart_items_after = user.get_cart_items()
    assert len(cart_items_after) == 0, "订单处理后购物车应该为空"
    
    # 场景4：库存不足的情况
    print("\n场景4：库存不足的情况")
    
    # 添加商品到购物车
    user.add_to_cart("p3", 10)  # 尝试购买10个，但库存只有7个
    
    # 创建订单
    create_result, order2 = system.create_order(user)
    assert create_result == True, "订单创建应该成功"
    
    # 处理订单（应该失败）
    process_result, message = order2.process(products)
    assert process_result == False, "库存不足时订单处理应该失败"
    assert order2.status == "failed", "失败的订单状态应该是'failed'"
    assert "库存不足" in message, "错误消息应该包含'库存不足'"
    
    print("电子商务系统端到端测试通过!")

if __name__ == "__main__":
    test_ecommerce_e2e()
```

## 实验3：测试生命周期验证

### 3.1 测试计划示例

```python
# test_plan_example.py
"""
测试计划示例
演示如何制定和执行测试计划
"""

class TestPlan:
    """测试计划类"""
    
    def __init__(self, name):
        self.name = name
        self.test_cases = []
        self.results = []
    
    def add_test_case(self, test_case):
        """添加测试用例"""
        self.test_cases.append(test_case)
    
    def execute(self):
        """执行测试计划"""
        print(f"执行测试计划: {self.name}")
        print("=" * 50)
        
        passed = 0
        failed = 0
        
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\n测试用例 {i}: {test_case['description']}")
            try:
                # 执行测试函数
                test_case['test_function']()
                print("✓ 通过")
                self.results.append({
                    'test_case': test_case['description'],
                    'status': 'passed',
                    'error': None
                })
                passed += 1
            except Exception as e:
                print(f"✗ 失败: {str(e)}")
                self.results.append({
                    'test_case': test_case['description'],
                    'status': 'failed',
                    'error': str(e)
                })
                failed += 1
        
        print("\n" + "=" * 50)
        print(f"测试结果: {passed} 通过, {failed} 失败")
        print(f"成功率: {passed/(passed+failed)*100:.1f}%")
        
        return passed, failed

# 示例测试函数
def test_addition():
    """加法测试"""
    assert 2 + 3 == 5, "2 + 3 应该等于 5"

def test_subtraction():
    """减法测试"""
    assert 10 - 5 == 5, "10 - 5 应该等于 5"

def test_multiplication():
    """乘法测试"""
    assert 3 * 4 == 12, "3 * 4 应该等于 12"

def test_division():
    """除法测试"""
    assert 10 / 2 == 5, "10 / 2 应该等于 5"

def test_division_by_zero():
    """除零测试（应该失败）"""
    result = 5 / 0  # 这会抛出异常
    assert result == 0, "这个测试应该失败"

def test_string_concatenation():
    """字符串连接测试"""
    assert "hello" + " " + "world" == "hello world", "字符串连接应该正确"

# 创建并执行测试计划
def create_and_execute_test_plan():
    """创建并执行测试计划"""
    # 创建测试计划
    plan = TestPlan("基础算术和字符串操作测试")
    
    # 添加测试用例
    plan.add_test_case({
        'description': '加法测试',
        'test_function': test_addition
    })
    
    plan.add_test_case({
        'description': '减法测试',
        'test_function': test_subtraction
    })
    
    plan.add_test_case({
        'description': '乘法测试',
        'test_function': test_multiplication
    })
    
    plan.add_test_case({
        'description': '除法测试',
        'test_function': test_division
    })
    
    plan.add_test_case({
        'description': '除零测试（预期失败）',
        'test_function': test_division_by_zero
    })
    
    plan.add_test_case({
        'description': '字符串连接测试',
        'test_function': test_string_concatenation
    })
    
    # 执行测试计划
    passed, failed = plan.execute()
    
    # 返回测试结果
    return {
        'total_tests': len(plan.test_cases),
        'passed': passed,
        'failed': failed,
        'results': plan.results
    }

if __name__ == "__main__":
    results = create_and_execute_test_plan()
```

### 3.2 测试报告生成示例

```python
# test_report_example.py
"""
测试报告生成示例
演示如何生成详细的测试报告
"""

import json
from datetime import datetime

class TestReport:
    """测试报告类"""
    
    def __init__(self, title):
        self.title = title
        self.start_time = datetime.now()
        self.test_results = []
        self.end_time = None
        self.summary = {}
    
    def add_test_result(self, test_name, status, duration=None, error=None):
        """添加测试结果"""
        self.test_results.append({
            'test_name': test_name,
            'status': status,  # 'passed' 或 'failed'
            'duration': duration,
            'error': error,
            'timestamp': datetime.now().isoformat()
        })
    
    def finish(self):
        """完成测试并生成摘要"""
        self.end_time = datetime.now()
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['status'] == 'passed')
        failed_tests = total_tests - passed_tests
        
        total_duration = (self.end_time - self.start_time).total_seconds()
        
        self.summary = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'total_duration': total_duration,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat()
        }
    
    def generate_text_report(self):
        """生成文本格式报告"""
        report = f"""
# {self.title}

## 测试摘要

- 开始时间: {self.summary['start_time']}
- 结束时间: {self.summary['end_time']}
- 总测试数: {self.summary['total_tests']}
- 通过测试: {self.summary['passed_tests']}
- 失败测试: {self.summary['failed_tests']}
- 成功率: {self.summary['success_rate']:.2f}%
- 总耗时: {self.summary['total_duration']:.2f}秒

## 测试详情

"""
        
        for result in self.test_results:
            status_icon = "✓" if result['status'] == 'passed' else "✗"
            report += f"### {status_icon} {result['test_name']}\n\n"
            report += f"- 状态: {result['status']}\n"
            
            if result['duration']:
                report += f"- 耗时: {result['duration']:.4f}秒\n"
            
            if result['error']:
                report += f"- 错误: {result['error']}\n"
            
            report += "\n"
        
        return report
    
    def generate_json_report(self):
        """生成JSON格式报告"""
        return json.dumps({
            'title': self.title,
            'summary': self.summary,
            'test_results': self.test_results
        }, indent=2)
    
    def save_report(self, filename, format='text'):
        """保存报告到文件"""
        if format == 'text':
            content = self.generate_text_report()
        elif format == 'json':
            content = self.generate_json_report()
        else:
            raise ValueError(f"不支持的格式: {format}")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"报告已保存到: {filename}")

# 测试运行器和报告生成器
class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.report = None
    
    def create_report(self, title):
        """创建测试报告"""
        self.report = TestReport(title)
        return self.report
    
    def run_test(self, test_name, test_function):
        """运行单个测试并记录结果"""
        start_time = datetime.now()
        status = 'passed'
        error = None
        
        try:
            test_function()
        except Exception as e:
            status = 'failed'
            error = str(e)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.report.add_test_result(test_name, status, duration, error)
    
    def finish_and_save(self, filename, format='text'):
        """完成测试并保存报告"""
        self.report.finish()
        self.report.save_report(filename, format)
        return self.report.summary

# 示例测试函数
def test_addition():
    """加法测试"""
    assert 2 + 3 == 5, "2 + 3 应该等于 5"

def test_subtraction():
    """减法测试"""
    assert 10 - 5 == 5, "10 - 5 应该等于 5"

def test_multiplication():
    """乘法测试"""
    assert 3 * 4 == 12, "3 * 4 应该等于 12"

def test_division():
    """除法测试"""
    assert 10 / 2 == 5, "10 / 2 应该等于 5"

def test_failing_test():
    """失败测试"""
    assert 1 == 2, "这个测试应该失败"

def test_string_operations():
    """字符串操作测试"""
    text = "hello world"
    assert text.upper() == "HELLO WORLD", "字符串大写转换应该正确"
    assert text.title() == "Hello World", "字符串标题化应该正确"

def test_list_operations():
    """列表操作测试"""
    numbers = [1, 2, 3]
    numbers.append(4)
    assert len(numbers) == 4, "添加元素后列表长度应该是4"
    assert 4 in numbers, "4应该在列表中"

# 运行测试并生成报告
def run_tests_and_generate_report():
    """运行测试并生成报告"""
    # 创建测试运行器
    runner = TestRunner()
    
    # 创建测试报告
    report = runner.create_report("基础功能测试报告")
    
    # 运行测试
    runner.run_test("加法测试", test_addition)
    runner.run_test("减法测试", test_subtraction)
    runner.run_test("乘法测试", test_multiplication)
    runner.run_test("除法测试", test_division)
    runner.run_test("失败测试", test_failing_test)
    runner.run_test("字符串操作测试", test_string_operations)
    runner.run_test("列表操作测试", test_list_operations)
    
    # 完成测试并保存报告
    summary = runner.finish_and_save("test_report.txt", "text")
    runner.finish_and_save("test_report.json", "json")
    
    return summary

if __name__ == "__main__":
    summary = run_tests_and_generate_report()
    print(f"测试完成，成功率: {summary['success_rate']:.2f}%")
```

## 实验4：测试原则验证

### 4.1 FIRST原则验证

```python
# first_principles_test.py
"""
FIRST原则验证示例
演示测试的FIRST原则：Fast、Independent、Repeatable、Self-Validating、Timely
"""

import time
import random

class FIRSTPrinciplesDemo:
    """FIRST原则演示类"""
    
    def __init__(self):
        self.data = []
        self.counter = 0
    
    def add_item(self, item):
        """添加项目"""
        self.data.append(item)
        self.counter += 1
        return self.counter
    
    def get_item(self, index):
        """获取项目"""
        if 0 <= index < len(self.data):
            return self.data[index]
        return None
    
    def get_count(self):
        """获取计数"""
        return self.counter
    
    def reset(self):
        """重置"""
        self.data = []
        self.counter = 0

# Fast原则：测试应该快速运行
def test_fast_principle():
    """快速原则测试"""
    print("运行Fast原则测试...")
    
    demo = FIRSTPrinciplesDemo()
    
    # 快速操作测试
    start_time = time.time()
    
    for i in range(1000):
        demo.add_item(f"item_{i}")
    
    end_time = time.time()
    duration = end_time - start_time
    
    assert duration < 1.0, f"测试应该在1秒内完成，实际耗时{duration:.4f}秒"
    assert demo.get_count() == 1000, "计数应该是1000"
    
    print(f"✓ Fast原则测试通过，耗时{duration:.4f}秒")

# Independent原则：测试应该独立运行
def test_independent_principle():
    """独立原则测试"""
    print("运行Independent原则测试...")
    
    # 测试1：独立测试添加功能
    demo1 = FIRSTPrinciplesDemo()
    result1 = demo1.add_item("item1")
    assert result1 == 1, "第一个项目添加后计数应该是1"
    assert demo1.get_count() == 1, "计数应该是1"
    
    # 测试2：独立测试获取功能
    demo2 = FIRSTPrinciplesDemo()
    demo2.add_item("item1")
    demo2.add_item("item2")
    item = demo2.get_item(0)
    assert item == "item1", "第一个项目应该是'item1'"
    
    # 测试3：独立测试重置功能
    demo3 = FIRSTPrinciplesDemo()
    demo3.add_item("item1")
    demo3.add_item("item2")
    demo3.reset()
    assert demo3.get_count() == 0, "重置后计数应该是0"
    assert len(demo3.data) == 0, "重置后数据应该为空"
    
    print("✓ Independent原则测试通过")

# Repeatable原则：测试应该可重复运行
def test_repeatable_principle():
    """可重复原则测试"""
    print("运行Repeatable原则测试...")
    
    # 多次运行相同的测试
    for i in range(5):
        demo = FIRSTPrinciplesDemo()
        
        # 添加项目
        demo.add_item("item1")
        demo.add_item("item2")
        demo.add_item("item3")
        
        # 验证结果
        assert demo.get_count() == 3, f"第{i+1}次运行，计数应该是3"
        assert demo.get_item(0) == "item1", f"第{i+1}次运行，第一个项目应该是'item1'"
        assert demo.get_item(1) == "item2", f"第{i+1}次运行，第二个项目应该是'item2'"
        assert demo.get_item(2) == "item3", f"第{i+1}次运行，第三个项目应该是'item3'"
    
    print("✓ Repeatable原则测试通过")

# Self-Validating原则：测试应该有明确的通过/失败结果
def test_self_validating_principle():
    """自验证原则测试"""
    print("运行Self-Validating原则测试...")
    
    demo = FIRSTPrinciplesDemo()
    
    # 测试1：验证添加功能
    result = demo.add_item("item1")
    assert result == 1, "添加第一个项目后返回值应该是1"
    
    # 测试2：验证计数功能
    count = demo.get_count()
    assert count == 1, "计数应该是1"
    
    # 测试3：验证获取功能
    item = demo.get_item(0)
    assert item == "item1", "获取的项目应该是'item1'"
    
    # 测试4：验证边界条件
    invalid_item = demo.get_item(10)
    assert invalid_item is None, "获取不存在的项目应该返回None"
    
    print("✓ Self-Validating原则测试通过")

# Timely原则：测试应该及时编写
def test_timely_principle():
    """及时原则测试"""
    print("运行Timely原则测试...")
    
    # 这个测试本身就是一个及时原则的示例
    # 我们在实现功能后立即编写测试
    
    demo = FIRSTPrinciplesDemo()
    
    # 测试基本功能
    assert demo.get_count() == 0, "初始计数应该是0"
    
    # 测试添加功能
    result = demo.add_item("item1")
    assert result == 1, "添加后返回值应该是1"
    assert demo.get_count() == 1, "添加后计数应该是1"
    
    # 测试重置功能
    demo.reset()
    assert demo.get_count() == 0, "重置后计数应该是0"
    
    print("✓ Timely原则测试通过")

# 运行所有FIRST原则测试
def run_first_principles_tests():
    """运行所有FIRST原则测试"""
    print("=" * 50)
    print("FIRST原则验证测试")
    print("=" * 50)
    
    test_fast_principle()
    test_independent_principle()
    test_repeatable_principle()
    test_self_validating_principle()
    test_timely_principle()
    
    print("=" * 50)
    print("所有FIRST原则测试通过!")
    print("=" * 50)

if __name__ == "__main__":
    run_first_principles_tests()
```

### 4.2 测试覆盖率示例

```python
# test_coverage_example.py
"""
测试覆盖率示例
演示如何分析和提高测试覆盖率
"""

class BankAccount:
    """银行账户类"""
    
    def __init__(self, account_number, owner_name, initial_balance=0):
        self.account_number = account_number
        self.owner_name = owner_name
        self.balance = initial_balance
        self.is_active = True
        self.transaction_history = []
    
    def deposit(self, amount):
        """存款"""
        if amount <= 0:
            raise ValueError("存款金额必须大于零")
        
        if not self.is_active:
            raise PermissionError("账户未激活，无法存款")
        
        self.balance += amount
        self.transaction_history.append({
            'type': 'deposit',
            'amount': amount,
            'balance_after': self.balance
        })
        return self.balance
    
    def withdraw(self, amount):
        """取款"""
        if amount <= 0:
            raise ValueError("取款金额必须大于零")
        
        if not self.is_active:
            raise PermissionError("账户未激活，无法取款")
        
        if amount > self.balance:
            raise ValueError("余额不足")
        
        self.balance -= amount
        self.transaction_history.append({
            'type': 'withdraw',
            'amount': amount,
            'balance_after': self.balance
        })
        return self.balance
    
    def get_balance(self):
        """获取余额"""
        return self.balance
    
    def deactivate(self):
        """停用账户"""
        self.is_active = False
    
    def activate(self):
        """激活账户"""
        self.is_active = True
    
    def get_transaction_history(self):
        """获取交易历史"""
        return self.transaction_history.copy()
    
    def transfer(self, target_account, amount):
        """转账"""
        if amount <= 0:
            raise ValueError("转账金额必须大于零")
        
        if not self.is_active:
            raise PermissionError("账户未激活，无法转账")
        
        if not target_account.is_active:
            raise PermissionError("目标账户未激活，无法转账")
        
        if amount > self.balance:
            raise ValueError("余额不足")
        
        # 从当前账户扣款
        self.withdraw(amount)
        
        # 向目标账户存款
        target_account.deposit(amount)
        
        # 记录转账交易
        self.transaction_history.append({
            'type': 'transfer_out',
            'amount': amount,
            'target_account': target_account.account_number,
            'balance_after': self.balance
        })
        
        target_account.transaction_history.append({
            'type': 'transfer_in',
            'amount': amount,
            'source_account': self.account_number,
            'balance_after': target_account.balance
        })
        
        return True

# 测试用例
def test_bank_account_basic_operations():
    """银行账户基本操作测试"""
    print("运行银行账户基本操作测试...")
    
    # 创建账户
    account = BankAccount("123456", "张三", 1000)
    
    # 测试初始状态
    assert account.get_balance() == 1000, "初始余额应该是1000"
    assert account.is_active == True, "账户应该是激活状态"
    
    # 测试存款
    new_balance = account.deposit(500)
    assert new_balance == 1500, "存款后余额应该是1500"
    assert account.get_balance() == 1500, "获取的余额应该是1500"
    
    # 测试取款
    new_balance = account.withdraw(300)
    assert new_balance == 1200, "取款后余额应该是1200"
    assert account.get_balance() == 1200, "获取的余额应该是1200"
    
    print("✓ 银行账户基本操作测试通过")

def test_bank_account_edge_cases():
    """银行账户边界情况测试"""
    print("运行银行账户边界情况测试...")
    
    account = BankAccount("123456", "张三", 1000)
    
    # 测试存款边界情况
    try:
        account.deposit(0)
        assert False, "存款金额为零应该抛出异常"
    except ValueError:
        pass  # 预期的异常
    
    try:
        account.deposit(-100)
        assert False, "存款金额为负应该抛出异常"
    except ValueError:
        pass  # 预期的异常
    
    # 测试取款边界情况
    try:
        account.withdraw(0)
        assert False, "取款金额为零应该抛出异常"
    except ValueError:
        pass  # 预期的异常
    
    try:
        account.withdraw(-100)
        assert False, "取款金额为负应该抛出异常"
    except ValueError:
        pass  # 预期的异常
    
    try:
        account.withdraw(2000)  # 超过余额
        assert False, "取款超过余额应该抛出异常"
    except ValueError:
        pass  # 预期的异常
    
    print("✓ 银行账户边界情况测试通过")

def test_bank_account_activation():
    """银行账户激活/停用测试"""
    print("运行银行账户激活/停用测试...")
    
    account = BankAccount("123456", "张三", 1000)
    
    # 测试停用账户
    account.deactivate()
    assert account.is_active == False, "账户应该是停用状态"
    
    # 测试停用账户的操作
    try:
        account.deposit(100)
        assert False, "停用账户存款应该抛出异常"
    except PermissionError:
        pass  # 预期的异常
    
    try:
        account.withdraw(100)
        assert False, "停用账户取款应该抛出异常"
    except PermissionError:
        pass  # 预期的异常
    
    # 测试重新激活账户
    account.activate()
    assert account.is_active == True, "账户应该是激活状态"
    
    # 测试激活账户的操作
    new_balance = account.deposit(100)
    assert new_balance == 1100, "激活账户存款应该成功"
    
    print("✓ 银行账户激活/停用测试通过")

def test_bank_account_transfer():
    """银行账户转账测试"""
    print("运行银行账户转账测试...")
    
    # 创建两个账户
    account1 = BankAccount("123456", "张三", 1000)
    account2 = BankAccount("654321", "李四", 500)
    
    # 测试正常转账
    account1.transfer(account2, 300)
    assert account1.get_balance() == 700, "转账后账户1余额应该是700"
    assert account2.get_balance() == 800, "转账后账户2余额应该是800"
    
    # 测试转账边界情况
    try:
        account1.transfer(account2, 0)
        assert False, "转账金额为零应该抛出异常"
    except ValueError:
        pass  # 预期的异常
    
    try:
        account1.transfer(account2, -100)
        assert False, "转账金额为负应该抛出异常"
    except ValueError:
        pass  # 预期的异常
    
    try:
        account1.transfer(account2, 1000)  # 超过余额
        assert False, "转账超过余额应该抛出异常"
    except ValueError:
        pass  # 预期的异常
    
    # 测试停用账户转账
    account1.deactivate()
    try:
        account1.transfer(account2, 100)
        assert False, "停用账户转账应该抛出异常"
    except PermissionError:
        pass  # 预期的异常
    
    account1.activate()
    account2.deactivate()
    try:
        account1.transfer(account2, 100)
        assert False, "向停用账户转账应该抛出异常"
    except PermissionError:
        pass  # 预期的异常
    
    print("✓ 银行账户转账测试通过")

def test_bank_account_transaction_history():
    """银行账户交易历史测试"""
    print("运行银行账户交易历史测试...")
    
    account = BankAccount("123456", "张三", 1000)
    
    # 执行一些操作
    account.deposit(500)
    account.withdraw(200)
    account.deposit(300)
    
    # 获取交易历史
    history = account.get_transaction_history()
    assert len(history) == 3, "应该有3条交易记录"
    
    # 验证交易记录
    assert history[0]['type'] == 'deposit', "第一条记录应该是存款"
    assert history[0]['amount'] == 500, "第一条记录金额应该是500"
    assert history[0]['balance_after'] == 1500, "第一条记录后余额应该是1500"
    
    assert history[1]['type'] == 'withdraw', "第二条记录应该是取款"
    assert history[1]['amount'] == 200, "第二条记录金额应该是200"
    assert history[1]['balance_after'] == 1300, "第二条记录后余额应该是1300"
    
    assert history[2]['type'] == 'deposit', "第三条记录应该是存款"
    assert history[2]['amount'] == 300, "第三条记录金额应该是300"
    assert history[2]['balance_after'] == 1600, "第三条记录后余额应该是1600"
    
    # 测试转账历史记录
    account2 = BankAccount("654321", "李四", 500)
    account.transfer(account2, 100)
    
    history1 = account.get_transaction_history()
    history2 = account2.get_transaction_history()
    
    # 验证转出记录
    transfer_out = next(record for record in history1 if record['type'] == 'transfer_out')
    assert transfer_out['amount'] == 100, "转出金额应该是100"
    assert transfer_out['target_account'] == "654321", "目标账户应该是654321"
    
    # 验证转入记录
    transfer_in = next(record for record in history2 if record['type'] == 'transfer_in')
    assert transfer_in['amount'] == 100, "转入金额应该是100"
    assert transfer_in['source_account'] == "123456", "源账户应该是123456"
    
    print("✓ 银行账户交易历史测试通过")

# 测试覆盖率分析
def analyze_test_coverage():
    """分析测试覆盖率"""
    print("\n测试覆盖率分析:")
    print("-" * 30)
    
    # 银行账户类的方法列表
    methods = [
        '__init__',
        'deposit',
        'withdraw',
        'get_balance',
        'deactivate',
        'activate',
        'get_transaction_history',
        'transfer'
    ]
    
    # 已测试的方法
    tested_methods = [
        '__init__',
        'deposit',
        'withdraw',
        'get_balance',
        'deactivate',
        'activate',
        'get_transaction_history',
        'transfer'
    ]
    
    coverage = len(tested_methods) / len(methods) * 100
    print(f"方法覆盖率: {coverage:.1f}% ({len(tested_methods)}/{len(methods)})")
    
    # 测试场景覆盖
    scenarios = [
        '正常存款',
        '正常取款',
        '存款边界情况',
        '取款边界情况',
        '账户激活',
        '账户停用',
        '正常转账',
        '转账边界情况',
        '交易历史记录'
    ]
    
    print(f"场景覆盖: {len(scenarios)}个测试场景")
    
    # 代码路径覆盖
    paths = [
        '正常流程',
        '异常处理',
        '边界条件'
    ]
    
    print(f"路径覆盖: {len(paths)}种代码路径")
    
    print("\n覆盖率分析完成!")

# 运行所有测试
def run_all_bank_account_tests():
    """运行所有银行账户测试"""
    print("=" * 50)
    print("银行账户测试套件")
    print("=" * 50)
    
    test_bank_account_basic_operations()
    test_bank_account_edge_cases()
    test_bank_account_activation()
    test_bank_account_transfer()
    test_bank_account_transaction_history()
    
    analyze_test_coverage()
    
    print("=" * 50)
    print("所有银行账户测试通过!")
    print("=" * 50)

if __name__ == "__main__":
    run_all_bank_account_tests()
```

## 运行指南

### 安装依赖

这些示例代码不需要额外的依赖，只需要Python 3.x环境即可运行。

### 运行单个实验

1. **基本测试概念验证**
   ```
   python simple_assertion_test.py
   python boundary_test.py
   python tdd_intro_example.py
   ```

2. **测试金字塔概念验证**
   ```
   python unit_test_example.py
   python integration_test_example.py
   python e2e_test_example.py
   ```

3. **测试生命周期验证**
   ```
   python test_plan_example.py
   python test_report_example.py
   ```

4. **测试原则验证**
   ```
   python first_principles_test.py
   python test_coverage_example.py
   ```

### 运行所有测试

可以创建一个简单的批处理脚本来运行所有测试：

```python
# run_all_tests.py
import subprocess
import sys

def run_test(script_name):
    """运行单个测试脚本"""
    print(f"\n{'='*50}")
    print(f"运行测试: {script_name}")
    print('='*50)
    
    try:
        result = subprocess.run([sys.executable, script_name], check=True)
        print(f"✓ {script_name} 测试通过")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ {script_name} 测试失败")
        return False

if __name__ == "__main__":
    # 测试脚本列表
    test_scripts = [
        "simple_assertion_test.py",
        "boundary_test.py",
        "tdd_intro_example.py",
        "unit_test_example.py",
        "integration_test_example.py",
        "e2e_test_example.py",
        "test_plan_example.py",
        "test_report_example.py",
        "first_principles_test.py",
        "test_coverage_example.py"
    ]
    
    passed = 0
    failed = 0
    
    # 运行所有测试
    for script in test_scripts:
        if run_test(script):
            passed += 1
        else:
            failed += 1
    
    # 打印总结
    print(f"\n{'='*50}")
    print(f"测试总结")
    print('='*50)
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"总计: {passed + failed}")
    
    if failed == 0:
        print("所有测试通过!")
        sys.exit(0)
    else:
        print("有测试失败!")
        sys.exit(1)
```

### 自定义测试

你可以基于这些示例创建自己的测试：

1. 复制相应的示例文件
2. 修改测试函数和被测试的代码
3. 运行你的自定义测试

### 故障排除

1. **导入错误**：确保所有文件都在同一目录下
2. **语法错误**：检查Python版本兼容性
3. **测试失败**：仔细阅读错误消息，检查断言条件

## 扩展练习

1. 尝试为这些示例添加更多的测试用例
2. 实现更复杂的业务逻辑并编写相应的测试
3. 尝试使用Python的unittest或pytest框架重写这些测试
4. 探索测试覆盖率工具（如coverage.py）来分析你的测试