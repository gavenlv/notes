# 第2章：测试类型与方法 - 示例代码

## 实验1：黑盒测试与白盒测试

### 1.1 黑盒测试示例

```python
# black_box_test_example.py
"""
黑盒测试示例
演示如何在不了解内部实现的情况下进行测试
"""

# 被测试的函数（假设我们不知道其内部实现）
def calculate_discount(price, customer_type, years_as_customer):
    """
    计算折扣价格（黑盒测试，我们不知道内部实现）
    
    参数:
        price: 原始价格
        customer_type: 客户类型 ("regular", "silver", "gold")
        years_as_customer: 成为客户的年数
        
    返回:
        折扣后的价格
    """
    # 实际实现（黑盒测试时我们看不到这部分代码）
    discount = 0
    
    if customer_type == "silver":
        discount = 0.05
    elif customer_type == "gold":
        discount = 0.1
    
    # 长期客户额外折扣
    if years_as_customer > 5:
        discount += 0.05
    
    # 应用折扣
    discounted_price = price * (1 - discount)
    
    # 确保折扣不超过50%
    if discounted_price < price * 0.5:
        discounted_price = price * 0.5
    
    return discounted_price

# 黑盒测试用例
def test_calculate_discount_black_box():
    """折扣计算函数的黑盒测试"""
    print("运行折扣计算函数的黑盒测试...")
    
    # 测试用例1：普通客户，短期客户
    result = calculate_discount(100, "regular", 2)
    assert result == 100, "普通客户短期应该没有折扣"
    
    # 测试用例2：银卡客户，短期客户
    result = calculate_discount(100, "silver", 2)
    assert result == 95, "银卡客户短期应该有5%折扣"
    
    # 测试用例3：金卡客户，短期客户
    result = calculate_discount(100, "gold", 2)
    assert result == 90, "金卡客户短期应该有10%折扣"
    
    # 测试用例4：普通客户，长期客户
    result = calculate_discount(100, "regular", 6)
    assert result == 95, "普通客户长期应该有5%折扣"
    
    # 测试用例5：银卡客户，长期客户
    result = calculate_discount(100, "silver", 6)
    assert result == 90, "银卡客户长期应该有10%折扣"
    
    # 测试用例6：金卡客户，长期客户
    result = calculate_discount(100, "gold", 6)
    assert result == 85, "金卡客户长期应该有15%折扣"
    
    # 测试用例7：边界情况 - 高价格，最大折扣
    result = calculate_discount(1000, "gold", 10)
    assert result == 500, "最大折扣应该是50%"
    
    # 测试用例8：边界情况 - 零价格
    result = calculate_discount(0, "gold", 10)
    assert result == 0, "零价格应该保持零"
    
    print("✓ 折扣计算函数的黑盒测试通过")

# 等价类划分法示例
def test_calculate_discount_equivalence_classes():
    """使用等价类划分法测试折扣计算函数"""
    print("\n使用等价类划分法测试折扣计算函数...")
    
    # 客户类型等价类
    # 有效等价类: "regular", "silver", "gold"
    # 无效等价类: 其他字符串
    
    # 客户年限等价类
    # 有效等价类: 0-5年, >5年
    # 无效等价类: 负数
    
    # 价格等价类
    # 有效等价类: >0
    # 无效等价类: 负数
    
    # 测试有效等价类
    assert calculate_discount(100, "regular", 3) == 100, "普通客户3年无折扣"
    assert calculate_discount(100, "silver", 3) == 95, "银卡客户3年5%折扣"
    assert calculate_discount(100, "gold", 3) == 90, "金卡客户3年10%折扣"
    assert calculate_discount(100, "regular", 6) == 95, "普通客户6年5%折扣"
    assert calculate_discount(100, "silver", 6) == 90, "银卡客户6年10%折扣"
    assert calculate_discount(100, "gold", 6) == 85, "金卡客户6年15%折扣"
    
    print("✓ 等价类划分法测试通过")

# 边界值分析法示例
def test_calculate_discount_boundary_values():
    """使用边界值分析法测试折扣计算函数"""
    print("\n使用边界值分析法测试折扣计算函数...")
    
    # 客户年限边界值: 5年
    assert calculate_discount(100, "regular", 4) == 100, "普通客户4年无折扣"
    assert calculate_discount(100, "regular", 5) == 100, "普通客户5年无折扣"
    assert calculate_discount(100, "regular", 6) == 95, "普通客户6年有折扣"
    
    # 价格边界值
    assert calculate_discount(0.01, "gold", 10) == 0.005, "最小价格边界测试"
    assert calculate_discount(1, "gold", 10) == 0.5, "单位价格边界测试"
    
    print("✓ 边界值分析法测试通过")

if __name__ == "__main__":
    test_calculate_discount_black_box()
    test_calculate_discount_equivalence_classes()
    test_calculate_discount_boundary_values()
```

### 1.2 白盒测试示例

```python
# white_box_test_example.py
"""
白盒测试示例
演示如何基于代码内部结构设计测试用例
"""

# 被测试的函数（我们可以看到内部实现）
def classify_triangle(a, b, c):
    """
    根据三边长度分类三角形（白盒测试，我们可以看到内部实现）
    
    参数:
        a, b, c: 三角形的三边长度
        
    返回:
        三角形类型: "等边三角形", "等腰三角形", "一般三角形", "不是三角形"
    """
    # 检查是否能构成三角形
    if a + b <= c or a + c <= b or b + c <= a:
        return "不是三角形"
    
    # 检查是否为等边三角形
    if a == b == c:
        return "等边三角形"
    
    # 检查是否为等腰三角形
    if a == b or a == c or b == c:
        return "等腰三角形"
    
    # 一般三角形
    return "一般三角形"

# 白盒测试用例
def test_classify_triangle_white_box():
    """三角形分类函数的白盒测试"""
    print("运行三角形分类函数的白盒测试...")
    
    # 路径1: 不是三角形 (a + b <= c)
    assert classify_triangle(1, 2, 3) == "不是三角形", "1,2,3不能构成三角形"
    assert classify_triangle(1, 1, 2) == "不是三角形", "1,1,2不能构成三角形"
    
    # 路径2: 等边三角形 (a == b == c)
    assert classify_triangle(3, 3, 3) == "等边三角形", "3,3,3是等边三角形"
    assert classify_triangle(5, 5, 5) == "等边三角形", "5,5,5是等边三角形"
    
    # 路径3: 等腰三角形 (a == b or a == c or b == c)
    assert classify_triangle(3, 3, 4) == "等腰三角形", "3,3,4是等腰三角形"
    assert classify_triangle(3, 4, 3) == "等腰三角形", "3,4,3是等腰三角形"
    assert classify_triangle(4, 3, 3) == "等腰三角形", "4,3,3是等腰三角形"
    
    # 路径4: 一般三角形
    assert classify_triangle(3, 4, 5) == "一般三角形", "3,4,5是一般三角形"
    assert classify_triangle(4, 5, 6) == "一般三角形", "4,5,6是一般三角形"
    
    print("✓ 三角形分类函数的白盒测试通过")

# 语句覆盖测试
def test_classify_triangle_statement_coverage():
    """语句覆盖测试"""
    print("\n运行语句覆盖测试...")
    
    # 为了覆盖所有语句，我们需要确保每个分支都被执行
    
    # 覆盖第一个if语句 (a + b <= c)
    assert classify_triangle(1, 2, 3) == "不是三角形"
    
    # 覆盖第二个if语句 (a == b == c)
    assert classify_triangle(3, 3, 3) == "等边三角形"
    
    # 覆盖第三个if语句 (a == b or a == c or b == c)
    assert classify_triangle(3, 3, 4) == "等腰三角形"
    
    # 覆盖else分支 (一般三角形)
    assert classify_triangle(3, 4, 5) == "一般三角形"
    
    print("✓ 语句覆盖测试通过")

# 分支覆盖测试
def test_classify_triangle_branch_coverage():
    """分支覆盖测试"""
    print("\n运行分支覆盖测试...")
    
    # 分支1: a + b <= c (True)
    assert classify_triangle(1, 2, 3) == "不是三角形"
    
    # 分支1: a + b <= c (False)
    assert classify_triangle(3, 4, 5) == "一般三角形"
    
    # 分支2: a == b == c (True)
    assert classify_triangle(3, 3, 3) == "等边三角形"
    
    # 分支2: a == b == c (False)
    assert classify_triangle(3, 3, 4) == "等腰三角形"
    
    # 分支3: a == b or a == c or b == c (True)
    assert classify_triangle(3, 3, 4) == "等腰三角形"
    
    # 分支3: a == b or a == c or b == c (False)
    assert classify_triangle(3, 4, 5) == "一般三角形"
    
    print("✓ 分支覆盖测试通过")

# 路径覆盖测试
def test_classify_triangle_path_coverage():
    """路径覆盖测试"""
    print("\n运行路径覆盖测试...")
    
    # 路径1: a + b <= c → return "不是三角形"
    assert classify_triangle(1, 2, 3) == "不是三角形"
    
    # 路径2: a + b > c → a == b == c → return "等边三角形"
    assert classify_triangle(3, 3, 3) == "等边三角形"
    
    # 路径3: a + b > c → a == b == c (False) → a == b or a == c or b == c → return "等腰三角形"
    assert classify_triangle(3, 3, 4) == "等腰三角形"
    
    # 路径4: a + b > c → a == b == c (False) → a == b or a == c or b == c (False) → return "一般三角形"
    assert classify_triangle(3, 4, 5) == "一般三角形"
    
    print("✓ 路径覆盖测试通过")

if __name__ == "__main__":
    test_classify_triangle_white_box()
    test_classify_triangle_statement_coverage()
    test_classify_triangle_branch_coverage()
    test_classify_triangle_path_coverage()
```

## 实验2：测试用例设计方法

### 2.1 决策表测试法

```python
# decision_table_test_example.py
"""
决策表测试法示例
演示如何使用决策表设计测试用例
"""

# 被测试的函数
def calculate_loan_eligibility(age, income, credit_score, employment_status):
    """
    计算贷款资格
    
    参数:
        age: 年龄
        income: 年收入（万元）
        credit_score: 信用评分
        employment_status: 就业状态 ("employed", "self_employed", "unemployed")
        
    返回:
        贷款资格: "批准", "拒绝", "需要额外审核"
    """
    # 规则1: 年龄小于18岁，直接拒绝
    if age < 18:
        return "拒绝"
    
    # 规则2: 失业状态，直接拒绝
    if employment_status == "unemployed":
        return "拒绝"
    
    # 规则3: 年龄大于60岁且信用评分低于600，需要额外审核
    if age > 60 and credit_score < 600:
        return "需要额外审核"
    
    # 规则4: 收入低于5万且信用评分低于650，需要额外审核
    if income < 5 and credit_score < 650:
        return "需要额外审核"
    
    # 规则5: 信用评分低于550，直接拒绝
    if credit_score < 550:
        return "拒绝"
    
    # 规则6: 收入高于20万，直接批准
    if income > 20:
        return "批准"
    
    # 规则7: 年龄在18-60岁，收入5-20万，信用评分650以上，就业，批准
    if 18 <= age <= 60 and 5 <= income <= 20 and credit_score >= 650:
        return "批准"
    
    # 默认情况：需要额外审核
    return "需要额外审核"

# 决策表测试
def test_calculate_loan_eligibility_decision_table():
    """使用决策表测试贷款资格计算函数"""
    print("运行决策表测试...")
    
    # 决策表测试用例
    test_cases = [
        # 规则1: 年龄小于18岁
        {"age": 17, "income": 10, "credit_score": 700, "employment_status": "employed", "expected": "拒绝"},
        
        # 规则2: 失业状态
        {"age": 30, "income": 10, "credit_score": 700, "employment_status": "unemployed", "expected": "拒绝"},
        
        # 规则3: 年龄大于60岁且信用评分低于600
        {"age": 65, "income": 10, "credit_score": 550, "employment_status": "employed", "expected": "需要额外审核"},
        
        # 规则4: 收入低于5万且信用评分低于650
        {"age": 30, "income": 4, "credit_score": 600, "employment_status": "employed", "expected": "需要额外审核"},
        
        # 规则5: 信用评分低于550
        {"age": 30, "income": 10, "credit_score": 540, "employment_status": "employed", "expected": "拒绝"},
        
        # 规则6: 收入高于20万
        {"age": 30, "income": 25, "credit_score": 600, "employment_status": "employed", "expected": "批准"},
        
        # 规则7: 标准批准条件
        {"age": 30, "income": 10, "credit_score": 700, "employment_status": "employed", "expected": "批准"},
        
        # 边界情况
        {"age": 18, "income": 5, "credit_score": 650, "employment_status": "employed", "expected": "批准"},
        {"age": 60, "income": 20, "credit_score": 650, "employment_status": "employed", "expected": "批准"},
    ]
    
    # 执行测试用例
    for i, case in enumerate(test_cases):
        result = calculate_loan_eligibility(
            case["age"], 
            case["income"], 
            case["credit_score"], 
            case["employment_status"]
        )
        assert result == case["expected"], f"测试用例{i+1}失败: 期望{case['expected']}, 实际{result}"
        print(f"✓ 测试用例{i+1}通过: {case['expected']}")
    
    print("✓ 决策表测试通过")

if __name__ == "__main__":
    test_calculate_loan_eligibility_decision_table()
```

### 2.2 状态转换测试法

```python
# state_transition_test_example.py
"""
状态转换测试法示例
演示如何使用状态转换图设计测试用例
"""

# 被测试的类
class TrafficLight:
    """交通信号灯类"""
    
    def __init__(self):
        self.state = "red"  # 初始状态为红灯
        self.timer = 0
    
    def transition(self):
        """状态转换"""
        if self.state == "red":
            self.state = "green"
            self.timer = 0
        elif self.state == "green":
            self.state = "yellow"
            self.timer = 0
        elif self.state == "yellow":
            self.state = "red"
            self.timer = 0
        else:
            raise ValueError(f"未知状态: {self.state}")
        
        return self.state
    
    def get_state(self):
        """获取当前状态"""
        return self.state
    
    def emergency_override(self):
        """紧急情况覆盖，强制切换到红灯"""
        self.state = "red"
        self.timer = 0
        return self.state

# 状态转换测试
def test_traffic_light_state_transitions():
    """测试交通信号灯状态转换"""
    print("运行交通信号灯状态转换测试...")
    
    # 初始状态测试
    light = TrafficLight()
    assert light.get_state() == "red", "初始状态应该是红灯"
    
    # 状态转换测试
    # 红灯 -> 绿灯
    state = light.transition()
    assert state == "green", "红灯应该转换为绿灯"
    
    # 绿灯 -> 黄灯
    state = light.transition()
    assert state == "yellow", "绿灯应该转换为黄灯"
    
    # 黄灯 -> 红灯
    state = light.transition()
    assert state == "red", "黄灯应该转换为红灯"
    
    # 完整周期测试
    for i in range(3):
        # 红灯 -> 绿灯 -> 黄灯 -> 红灯
        assert light.transition() == "green", f"第{i+1}周期: 红灯应该转换为绿灯"
        assert light.transition() == "yellow", f"第{i+1}周期: 绿灯应该转换为黄灯"
        assert light.transition() == "red", f"第{i+1}周期: 黄灯应该转换为红灯"
    
    # 紧急情况测试
    light.transition()  # 红灯 -> 绿灯
    assert light.emergency_override() == "red", "紧急情况应该强制切换到红灯"
    
    print("✓ 交通信号灯状态转换测试通过")

# 状态覆盖测试
def test_traffic_light_state_coverage():
    """测试所有状态和转换"""
    print("\n运行状态覆盖测试...")
    
    light = TrafficLight()
    
    # 测试所有状态
    states = ["red", "green", "yellow"]
    visited_states = set()
    
    # 记录初始状态
    visited_states.add(light.get_state())
    
    # 执行多个转换周期，确保访问所有状态
    for i in range(10):
        state = light.transition()
        visited_states.add(state)
        
        # 随机插入紧急情况
        if i % 3 == 0:
            emergency_state = light.emergency_override()
            visited_states.add(emergency_state)
    
    # 验证是否访问了所有状态
    assert visited_states == set(states), f"未访问所有状态，已访问: {visited_states}"
    
    print(f"✓ 状态覆盖测试通过，访问了所有状态: {visited_states}")

# 转换覆盖测试
def test_traffic_light_transition_coverage():
    """测试所有状态转换"""
    print("\n运行转换覆盖测试...")
    
    light = TrafficLight()
    
    # 定义所有可能的转换
    expected_transitions = {
        "red": "green",
        "green": "yellow",
        "yellow": "red"
    }
    
    # 记录实际转换
    actual_transitions = {}
    
    # 执行转换并记录
    for i in range(5):
        current_state = light.get_state()
        next_state = light.transition()
        actual_transitions[current_state] = next_state
    
    # 验证转换是否正确
    for from_state, to_state in expected_transitions.items():
        assert actual_transitions.get(from_state) == to_state, f"转换{from_state}->{to_state}不正确"
    
    print("✓ 转换覆盖测试通过")

if __name__ == "__main__":
    test_traffic_light_state_transitions()
    test_traffic_light_state_coverage()
    test_traffic_light_transition_coverage()
```

## 实验3：功能测试与非功能测试

### 3.1 功能测试示例

```python
# functional_test_example.py
"""
功能测试示例
演示如何验证软件功能是否符合需求
"""

# 被测试的类
class UserAuthentication:
    """用户认证类"""
    
    def __init__(self):
        self.users = {}  # 存储用户信息 {username: {password: str, attempts: int, locked: bool}}
        self.logged_in_users = {}  # 存储已登录用户 {username: login_time}
    
    def register_user(self, username, password):
        """注册用户"""
        if not username or not password:
            return False, "用户名和密码不能为空"
        
        if len(username) < 3:
            return False, "用户名长度至少为3个字符"
        
        if len(password) < 6:
            return False, "密码长度至少为6个字符"
        
        if username in self.users:
            return False, "用户名已存在"
        
        self.users[username] = {
            "password": password,
            "attempts": 0,
            "locked": False
        }
        
        return True, "注册成功"
    
    def login(self, username, password):
        """用户登录"""
        if not username or not password:
            return False, "用户名和密码不能为空"
        
        if username not in self.users:
            return False, "用户不存在"
        
        user = self.users[username]
        
        if user["locked"]:
            return False, "账户已被锁定"
        
        if user["password"] != password:
            user["attempts"] += 1
            if user["attempts"] >= 3:
                user["locked"] = True
                return False, "密码错误次数过多，账户已被锁定"
            return False, f"密码错误，还剩{3 - user['attempts']}次尝试机会"
        
        # 登录成功，重置尝试次数
        user["attempts"] = 0
        import time
        self.logged_in_users[username] = time.time()
        
        return True, "登录成功"
    
    def logout(self, username):
        """用户登出"""
        if username in self.logged_in_users:
            del self.logged_in_users[username]
            return True, "登出成功"
        return False, "用户未登录"
    
    def is_logged_in(self, username):
        """检查用户是否已登录"""
        return username in self.logged_in_users
    
    def unlock_account(self, username):
        """解锁账户"""
        if username not in self.users:
            return False, "用户不存在"
        
        self.users[username]["locked"] = False
        self.users[username]["attempts"] = 0
        
        return True, "账户解锁成功"

# 功能测试用例
def test_user_authentication_functional():
    """用户认证功能测试"""
    print("运行用户认证功能测试...")
    
    auth = UserAuthentication()
    
    # 测试用户注册
    success, message = auth.register_user("testuser", "password123")
    assert success == True, "用户注册应该成功"
    assert message == "注册成功", "注册成功消息应该正确"
    
    # 测试重复注册
    success, message = auth.register_user("testuser", "password456")
    assert success == False, "重复注册应该失败"
    assert message == "用户名已存在", "重复注册错误消息应该正确"
    
    # 测试无效用户名
    success, message = auth.register_user("ab", "password123")
    assert success == False, "用户名太短应该注册失败"
    assert message == "用户名长度至少为3个字符", "用户名太短错误消息应该正确"
    
    # 测试无效密码
    success, message = auth.register_user("testuser2", "12345")
    assert success == False, "密码太短应该注册失败"
    assert message == "密码长度至少为6个字符", "密码太短错误消息应该正确"
    
    # 测试空用户名和密码
    success, message = auth.register_user("", "password123")
    assert success == False, "空用户名应该注册失败"
    assert message == "用户名和密码不能为空", "空用户名错误消息应该正确"
    
    success, message = auth.register_user("testuser3", "")
    assert success == False, "空密码应该注册失败"
    assert message == "用户名和密码不能为空", "空密码错误消息应该正确"
    
    # 测试用户登录
    success, message = auth.login("testuser", "password123")
    assert success == True, "正确用户名和密码应该登录成功"
    assert message == "登录成功", "登录成功消息应该正确"
    assert auth.is_logged_in("testuser") == True, "用户应该处于登录状态"
    
    # 测试错误密码
    success, message = auth.login("testuser", "wrongpassword")
    assert success == False, "错误密码应该登录失败"
    assert "密码错误" in message, "错误密码消息应该包含'密码错误'"
    
    # 测试账户锁定
    auth.register_user("locktest", "password123")
    for i in range(3):
        success, message = auth.login("locktest", "wrongpassword")
    
    assert success == False, "3次错误后应该登录失败"
    assert "账户已被锁定" in message, "账户锁定消息应该正确"
    
    # 测试解锁账户
    success, message = auth.unlock_account("locktest")
    assert success == True, "账户解锁应该成功"
    assert message == "账户解锁成功", "解锁成功消息应该正确"
    
    # 测试解锁后登录
    success, message = auth.login("locktest", "password123")
    assert success == True, "解锁后正确密码应该登录成功"
    
    # 测试用户登出
    success, message = auth.logout("testuser")
    assert success == True, "用户登出应该成功"
    assert message == "登出成功", "登出成功消息应该正确"
    assert auth.is_logged_in("testuser") == False, "用户应该处于未登录状态"
    
    # 测试重复登出
    success, message = auth.logout("testuser")
    assert success == False, "重复登出应该失败"
    assert message == "用户未登录", "重复登出错误消息应该正确"
    
    print("✓ 用户认证功能测试通过")

if __name__ == "__main__":
    test_user_authentication_functional()
```

### 3.2 性能测试示例

```python
# performance_test_example.py
"""
性能测试示例
演示如何测试系统性能
"""

import time
import random
import statistics
from datetime import datetime

# 被测试的类
class DataProcessor:
    """数据处理器类"""
    
    def __init__(self):
        self.data = []
    
    def add_data(self, item):
        """添加数据"""
        self.data.append(item)
    
    def clear_data(self):
        """清空数据"""
        self.data = []
    
    def linear_search(self, target):
        """线性搜索"""
        for i, item in enumerate(self.data):
            if item == target:
                return i
        return -1
    
    def bubble_sort(self):
        """冒泡排序"""
        n = len(self.data)
        for i in range(n):
            for j in range(0, n-i-1):
                if self.data[j] > self.data[j+1]:
                    self.data[j], self.data[j+1] = self.data[j+1], self.data[j]
        return self.data
    
    def quick_sort(self):
        """快速排序"""
        def _quick_sort(arr):
            if len(arr) <= 1:
                return arr
            pivot = arr[len(arr) // 2]
            left = [x for x in arr if x < pivot]
            middle = [x for x in arr if x == pivot]
            right = [x for x in arr if x > pivot]
            return _quick_sort(left) + middle + _quick_sort(right)
        
        self.data = _quick_sort(self.data)
        return self.data
    
    def fibonacci(self, n):
        """斐波那契数列"""
        if n <= 1:
            return n
        return self.fibonacci(n-1) + self.fibonacci(n-2)
    
    def fibonacci_memoized(self, n, memo={}):
        """带记忆化的斐波那契数列"""
        if n in memo:
            return memo[n]
        if n <= 1:
            return n
        memo[n] = self.fibonacci_memoized(n-1, memo) + self.fibonacci_memoized(n-2, memo)
        return memo[n]

# 性能测试工具类
class PerformanceTest:
    """性能测试工具类"""
    
    @staticmethod
    def measure_time(func, *args, **kwargs):
        """测量函数执行时间"""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return result, end_time - start_time
    
    @staticmethod
    def benchmark(func, *args, iterations=100, **kwargs):
        """基准测试"""
        times = []
        for _ in range(iterations):
            _, duration = PerformanceTest.measure_time(func, *args, **kwargs)
            times.append(duration)
        
        return {
            "min": min(times),
            "max": max(times),
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "stdev": statistics.stdev(times) if len(times) > 1 else 0
        }
    
    @staticmethod
    def stress_test(func, *args, max_duration=10, **kwargs):
        """压力测试"""
        start_time = time.time()
        count = 0
        
        while time.time() - start_time < max_duration:
            func(*args, **kwargs)
            count += 1
        
        return {
            "operations": count,
            "duration": max_duration,
            "ops_per_second": count / max_duration
        }

# 性能测试用例
def test_data_processor_performance():
    """数据处理器性能测试"""
    print("运行数据处理器性能测试...")
    
    processor = DataProcessor()
    
    # 准备测试数据
    data_size = 1000
    test_data = [random.randint(1, 1000) for _ in range(data_size)]
    processor.data = test_data.copy()
    
    # 测试线性搜索性能
    target = test_data[data_size // 2]  # 选择中间元素作为搜索目标
    search_stats = PerformanceTest.benchmark(processor.linear_search, target, iterations=100)
    print(f"线性搜索性能: 平均 {search_stats['mean']:.6f}秒")
    
    # 测试冒泡排序性能
    processor.data = test_data.copy()
    sort_stats = PerformanceTest.benchmark(processor.bubble_sort, iterations=10)  # 减少迭代次数，因为冒泡排序很慢
    print(f"冒泡排序性能: 平均 {sort_stats['mean']:.6f}秒")
    
    # 测试快速排序性能
    processor.data = test_data.copy()
    quick_sort_stats = PerformanceTest.benchmark(processor.quick_sort, iterations=100)
    print(f"快速排序性能: 平均 {quick_sort_stats['mean']:.6f}秒")
    
    # 验证快速排序比冒泡排序快
    assert quick_sort_stats['mean'] < sort_stats['mean'], "快速排序应该比冒泡排序快"
    
    # 测试斐波那契数列性能
    fib_stats = PerformanceTest.benchmark(processor.fibonacci, 30, iterations=10)  # 减少迭代次数
    print(f"斐波那契数列性能: 平均 {fib_stats['mean']:.6f}秒")
    
    # 测试记忆化斐波那契数列性能
    fib_memo_stats = PerformanceTest.benchmark(processor.fibonacci_memoized, 30, iterations=100)
    print(f"记忆化斐波那契数列性能: 平均 {fib_memo_stats['mean']:.6f}秒")
    
    # 验证记忆化版本更快
    assert fib_memo_stats['mean'] < fib_stats['mean'], "记忆化斐波那契应该比普通斐波那契快"
    
    # 压力测试
    processor.data = test_data.copy()
    stress_result = PerformanceTest.stress_test(processor.linear_search, target, max_duration=5)
    print(f"线性搜索压力测试: 5秒内完成 {stress_result['operations']} 次操作")
    
    print("✓ 数据处理器性能测试通过")

def test_performance_regression():
    """性能回归测试"""
    print("\n运行性能回归测试...")
    
    processor = DataProcessor()
    
    # 准备测试数据
    data_size = 1000
    test_data = [random.randint(1, 1000) for _ in range(data_size)]
    processor.data = test_data.copy()
    
    # 定义性能基准（假设这些是之前测得的基准值）
    performance_benchmarks = {
        "linear_search": 0.001,  # 1ms
        "quick_sort": 0.01,      # 10ms
        "fibonacci_memoized": 0.001  # 1ms
    }
    
    # 测试线性搜索性能
    target = test_data[data_size // 2]
    search_stats = PerformanceTest.benchmark(processor.linear_search, target, iterations=100)
    assert search_stats['mean'] <= performance_benchmarks["linear_search"], \
        f"线性搜索性能回归: 期望 <= {performance_benchmarks['linear_search']}秒, 实际 {search_stats['mean']:.6f}秒"
    
    # 测试快速排序性能
    processor.data = test_data.copy()
    sort_stats = PerformanceTest.benchmark(processor.quick_sort, iterations=100)
    assert sort_stats['mean'] <= performance_benchmarks["quick_sort"], \
        f"快速排序性能回归: 期望 <= {performance_benchmarks['quick_sort']}秒, 实际 {sort_stats['mean']:.6f}秒"
    
    # 测试记忆化斐波那契数列性能
    fib_stats = PerformanceTest.benchmark(processor.fibonacci_memoized, 30, iterations=100)
    assert fib_stats['mean'] <= performance_benchmarks["fibonacci_memoized"], \
        f"记忆化斐波那契性能回归: 期望 <= {performance_benchmarks['fibonacci_memoized']}秒, 实际 {fib_stats['mean']:.6f}秒"
    
    print("✓ 性能回归测试通过")

def generate_performance_report():
    """生成性能报告"""
    print("\n生成性能报告...")
    
    processor = DataProcessor()
    
    # 准备不同规模的数据
    data_sizes = [100, 500, 1000, 2000]
    report = {
        "timestamp": datetime.now().isoformat(),
        "tests": []
    }
    
    for size in data_sizes:
        test_data = [random.randint(1, 1000) for _ in range(size)]
        
        # 测试线性搜索
        processor.data = test_data.copy()
        target = test_data[size // 2]
        search_stats = PerformanceTest.benchmark(processor.linear_search, target, iterations=100)
        
        # 测试快速排序
        processor.data = test_data.copy()
        sort_stats = PerformanceTest.benchmark(processor.quick_sort, iterations=100)
        
        # 记录结果
        report["tests"].append({
            "data_size": size,
            "linear_search": {
                "mean_time": search_stats['mean'],
                "min_time": search_stats['min'],
                "max_time": search_stats['max']
            },
            "quick_sort": {
                "mean_time": sort_stats['mean'],
                "min_time": sort_stats['min'],
                "max_time": sort_stats['max']
            }
        })
    
    # 打印报告
    print("性能报告:")
    print("=" * 50)
    for test in report["tests"]:
        print(f"数据规模: {test['data_size']}")
        print(f"  线性搜索: 平均 {test['linear_search']['mean']:.6f}秒")
        print(f"  快速排序: 平均 {test['quick_sort']['mean']:.6f}秒")
        print()
    
    return report

if __name__ == "__main__":
    test_data_processor_performance()
    test_performance_regression()
    generate_performance_report()
```

## 实验4：测试自动化

### 4.1 数据驱动测试

```python
# data_driven_test_example.py
"""
数据驱动测试示例
演示如何使用数据驱动方法进行测试
"""

# 被测试的函数
def validate_email(email):
    """验证邮箱格式"""
    import re
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def calculate_bmi(weight, height):
    """计算BMI指数"""
    if height <= 0:
        raise ValueError("身高必须大于零")
    
    bmi = weight / (height ** 2)
    
    if bmi < 18.5:
        return "偏瘦"
    elif 18.5 <= bmi < 24:
        return "正常"
    elif 24 <= bmi < 28:
        return "偏胖"
    else:
        return "肥胖"

# 数据驱动测试框架
class DataDrivenTest:
    """数据驱动测试框架"""
    
    @staticmethod
    def run_test_cases(test_function, test_data):
        """运行测试用例"""
        passed = 0
        failed = 0
        
        for i, case in enumerate(test_data):
            try:
                # 提取测试数据
                inputs = case["inputs"]
                expected = case["expected"]
                description = case.get("description", f"测试用例{i+1}")
                
                # 执行测试函数
                result = test_function(*inputs)
                
                # 验证结果
                if result == expected:
                    print(f"✓ {description}: 通过")
                    passed += 1
                else:
                    print(f"✗ {description}: 失败 - 期望 {expected}, 实际 {result}")
                    failed += 1
            except Exception as e:
                if case.get("expect_exception", False):
                    print(f"✓ {description}: 通过 (预期异常: {str(e)})")
                    passed += 1
                else:
                    print(f"✗ {description}: 失败 - 异常: {str(e)}")
                    failed += 1
        
        print(f"\n测试结果: {passed} 通过, {failed} 失败")
        return passed, failed

# 邮箱验证测试数据
email_test_data = [
    {
        "description": "有效邮箱1",
        "inputs": ["user@example.com"],
        "expected": True
    },
    {
        "description": "有效邮箱2",
        "inputs": ["user.name@example.co.uk"],
        "expected": True
    },
    {
        "description": "有效邮箱3",
        "inputs": ["user+tag@example.org"],
        "expected": True
    },
    {
        "description": "无效邮箱1 - 缺少@",
        "inputs": ["userexample.com"],
        "expected": False
    },
    {
        "description": "无效邮箱2 - 缺少域名",
        "inputs": ["user@"],
        "expected": False
    },
    {
        "description": "无效邮箱3 - 缺少用户名",
        "inputs": ["@example.com"],
        "expected": False
    },
    {
        "description": "无效邮箱4 - 无效字符",
        "inputs": ["user@exa$mple.com"],
        "expected": False
    },
    {
        "description": "无效邮箱5 - 空字符串",
        "inputs": [""],
        "expected": False
    }
]

# BMI计算测试数据
bmi_test_data = [
    {
        "description": "偏瘦BMI",
        "inputs": [50, 1.75],
        "expected": "偏瘦"
    },
    {
        "description": "正常BMI下限",
        "inputs": [57, 1.75],
        "expected": "正常"
    },
    {
        "description": "正常BMI上限",
        "inputs": [73, 1.75],
        "expected": "正常"
    },
    {
        "description": "偏胖BMI下限",
        "inputs": [74, 1.75],
        "expected": "偏胖"
    },
    {
        "description": "偏胖BMI上限",
        "inputs": [85, 1.75],
        "expected": "偏胖"
    },
    {
        "description": "肥胖BMI",
        "inputs": [90, 1.75],
        "expected": "肥胖"
    },
    {
        "description": "边界情况 - 零身高",
        "inputs": [70, 0],
        "expected": None,
        "expect_exception": True
    },
    {
        "description": "边界情况 - 负身高",
        "inputs": [70, -1.75],
        "expected": None,
        "expect_exception": True
    }
]

# 运行数据驱动测试
def run_data_driven_tests():
    """运行数据驱动测试"""
    print("运行邮箱验证数据驱动测试...")
    DataDrivenTest.run_test_cases(validate_email, email_test_data)
    
    print("\n运行BMI计算数据驱动测试...")
    DataDrivenTest.run_test_cases(calculate_bmi, bmi_test_data)

if __name__ == "__main__":
    run_data_driven_tests()
```

### 4.2 关键字驱动测试

```python
# keyword_driven_test_example.py
"""
关键字驱动测试示例
演示如何使用关键字驱动方法进行测试
"""

# 被测试的应用
class CalculatorApp:
    """计算器应用"""
    
    def __init__(self):
        self.result = 0
        self.memory = 0
    
    def add(self, value):
        """加法"""
        self.result += value
        return self.result
    
    def subtract(self, value):
        """减法"""
        self.result -= value
        return self.result
    
    def multiply(self, value):
        """乘法"""
        self.result *= value
        return self.result
    
    def divide(self, value):
        """除法"""
        if value == 0:
            raise ValueError("除数不能为零")
        self.result /= value
        return self.result
    
    def clear(self):
        """清除"""
        self.result = 0
        return self.result
    
    def memory_store(self):
        """存储到内存"""
        self.memory = self.result
        return self.memory
    
    def memory_recall(self):
        """从内存中读取"""
        self.result = self.memory
        return self.result
    
    def memory_clear(self):
        """清除内存"""
        self.memory = 0
        return self.memory
    
    def get_result(self):
        """获取结果"""
        return self.result

# 关键字驱动测试框架
class KeywordDrivenTest:
    """关键字驱动测试框架"""
    
    def __init__(self, app):
        self.app = app
        self.keywords = {
            "ADD": self.add,
            "SUBTRACT": self.subtract,
            "MULTIPLY": self.multiply,
            "DIVIDE": self.divide,
            "CLEAR": self.clear,
            "MEMORY_STORE": self.memory_store,
            "MEMORY_RECALL": self.memory_recall,
            "MEMORY_CLEAR": self.memory_clear,
            "VERIFY_RESULT": self.verify_result,
            "VERIFY_MEMORY": self.verify_memory
        }
    
    def execute_test_case(self, test_case):
        """执行测试用例"""
        try:
            for step in test_case["steps"]:
                keyword = step["keyword"]
                params = step.get("params", [])
                description = step.get("description", "")
                
                if keyword not in self.keywords:
                    raise ValueError(f"未知关键字: {keyword}")
                
                # 执行关键字
                self.keywords[keyword](*params)
            
            print(f"✓ {test_case['description']}: 通过")
            return True
        except Exception as e:
            print(f"✗ {test_case['description']}: 失败 - {str(e)}")
            return False
    
    def execute_test_suite(self, test_suite):
        """执行测试套件"""
        passed = 0
        failed = 0
        
        for test_case in test_suite:
            if self.execute_test_case(test_case):
                passed += 1
            else:
                failed += 1
        
        print(f"\n测试结果: {passed} 通过, {failed} 失败")
        return passed, failed
    
    # 关键字实现
    def add(self, value):
        """加法关键字"""
        return self.app.add(value)
    
    def subtract(self, value):
        """减法关键字"""
        return self.app.subtract(value)
    
    def multiply(self, value):
        """乘法关键字"""
        return self.app.multiply(value)
    
    def divide(self, value):
        """除法关键字"""
        return self.app.divide(value)
    
    def clear(self):
        """清除关键字"""
        return self.app.clear()
    
    def memory_store(self):
        """存储到内存关键字"""
        return self.app.memory_store()
    
    def memory_recall(self):
        """从内存中读取关键字"""
        return self.app.memory_recall()
    
    def memory_clear(self):
        """清除内存关键字"""
        return self.app.memory_clear()
    
    def verify_result(self, expected):
        """验证结果关键字"""
        actual = self.app.get_result()
        if actual != expected:
            raise AssertionError(f"结果验证失败: 期望 {expected}, 实际 {actual}")
        return True
    
    def verify_memory(self, expected):
        """验证内存关键字"""
        actual = self.app.memory
        if actual != expected:
            raise AssertionError(f"内存验证失败: 期望 {expected}, 实际 {actual}")
        return True

# 测试用例定义
calculator_test_cases = [
    {
        "description": "基本加法测试",
        "steps": [
            {"keyword": "CLEAR", "description": "清除计算器"},
            {"keyword": "ADD", "params": [5], "description": "加5"},
            {"keyword": "ADD", "params": [3], "description": "加3"},
            {"keyword": "VERIFY_RESULT", "params": [8], "description": "验证结果为8"}
        ]
    },
    {
        "description": "基本减法测试",
        "steps": [
            {"keyword": "CLEAR", "description": "清除计算器"},
            {"keyword": "ADD", "params": [10], "description": "加10"},
            {"keyword": "SUBTRACT", "params": [4], "description": "减4"},
            {"keyword": "VERIFY_RESULT", "params": [6], "description": "验证结果为6"}
        ]
    },
    {
        "description": "基本乘法测试",
        "steps": [
            {"keyword": "CLEAR", "description": "清除计算器"},
            {"keyword": "ADD", "params": [5], "description": "加5"},
            {"keyword": "MULTIPLY", "params": [3], "description": "乘以3"},
            {"keyword": "VERIFY_RESULT", "params": [15], "description": "验证结果为15"}
        ]
    },
    {
        "description": "基本除法测试",
        "steps": [
            {"keyword": "CLEAR", "description": "清除计算器"},
            {"keyword": "ADD", "params": [20], "description": "加20"},
            {"keyword": "DIVIDE", "params": [4], "description": "除以4"},
            {"keyword": "VERIFY_RESULT", "params": [5], "description": "验证结果为5"}
        ]
    },
    {
        "description": "内存功能测试",
        "steps": [
            {"keyword": "CLEAR", "description": "清除计算器"},
            {"keyword": "ADD", "params": [10], "description": "加10"},
            {"keyword": "MEMORY_STORE", "description": "存储到内存"},
            {"keyword": "CLEAR", "description": "清除计算器"},
            {"keyword": "ADD", "params": [5], "description": "加5"},
            {"keyword": "VERIFY_RESULT", "params": [5], "description": "验证结果为5"},
            {"keyword": "MEMORY_RECALL", "description": "从内存中读取"},
            {"keyword": "VERIFY_RESULT", "params": [10], "description": "验证结果为10"},
            {"keyword": "VERIFY_MEMORY", "params": [10], "description": "验证内存为10"}
        ]
    },
    {
        "description": "复合运算测试",
        "steps": [
            {"keyword": "CLEAR", "description": "清除计算器"},
            {"keyword": "ADD", "params": [5], "description": "加5"},
            {"keyword": "MULTIPLY", "params": [2], "description": "乘以2"},
            {"keyword": "ADD", "params": [10], "description": "加10"},
            {"keyword": "DIVIDE", "params": [4], "description": "除以4"},
            {"keyword": "VERIFY_RESULT", "params": [5], "description": "验证结果为5"}
        ]
    }
]

# 运行关键字驱动测试
def run_keyword_driven_tests():
    """运行关键字驱动测试"""
    print("运行计算器关键字驱动测试...")
    
    app = CalculatorApp()
    test_framework = KeywordDrivenTest(app)
    test_framework.execute_test_suite(calculator_test_cases)

if __name__ == "__main__":
    run_keyword_driven_tests()
```

## 运行指南

### 安装依赖

这些示例代码不需要额外的依赖，只需要Python 3.x环境即可运行。

### 运行单个实验

1. **黑盒测试与白盒测试**
   ```
   python black_box_test_example.py
   python white_box_test_example.py
   ```

2. **测试用例设计方法**
   ```
   python decision_table_test_example.py
   python state_transition_test_example.py
   ```

3. **功能测试与非功能测试**
   ```
   python functional_test_example.py
   python performance_test_example.py
   ```

4. **测试自动化**
   ```
   python data_driven_test_example.py
   python keyword_driven_test_example.py
   ```

### 运行所有测试

可以创建一个简单的批处理脚本来运行所有测试：

```python
# run_all_chapter2_tests.py
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
        "black_box_test_example.py",
        "white_box_test_example.py",
        "decision_table_test_example.py",
        "state_transition_test_example.py",
        "functional_test_example.py",
        "performance_test_example.py",
        "data_driven_test_example.py",
        "keyword_driven_test_example.py"
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
5. 尝试结合不同的测试方法设计更全面的测试用例