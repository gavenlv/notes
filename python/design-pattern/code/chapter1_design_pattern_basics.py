"""
第1章：设计模式基础概念 - 示例代码

本文件包含了第1章中提到的所有示例代码，用于演示设计模式的基本原则。
"""

# 示例1：单一职责原则
print("=== 单一职责原则示例 ===")

# 违反单一职责原则的例子
class UserManagement:
    def save_user_to_database(self, user):
        print(f"保存用户 {user} 到数据库")
        # 实际应用中会有数据库操作代码
        pass
    
    def generate_report(self, user_data):
        print(f"为用户数据 {user_data} 生成报告")
        # 实际应用中会有报告生成代码
        pass

# 遵循单一职责原则的例子
class UserRepository:
    def save_user_to_database(self, user):
        print(f"保存用户 {user} 到数据库")
        pass

class ReportGenerator:
    def generate_report(self, user_data):
        print(f"为用户数据 {user_data} 生成报告")
        pass

# 测试
print("违反单一职责原则的示例：")
user_mgmt = UserManagement()
user_mgmt.save_user_to_database("张三")
user_mgmt.generate_report({"name": "张三", "age": 30})

print("\n遵循单一职责原则的示例：")
user_repo = UserRepository()
report_gen = ReportGenerator()
user_repo.save_user_to_database("李四")
report_gen.generate_report({"name": "李四", "age": 25})

# 示例2：开闭原则
print("\n\n=== 开闭原则示例 ===")

# 违反开闭原则的例子
class AreaCalculatorViolatingOCP:
    def calculate_area(self, shape_type, dimensions):
        if shape_type == "rectangle":
            return dimensions[0] * dimensions[1]
        elif shape_type == "circle":
            return 3.14 * dimensions[0] ** 2
        # 添加新形状需要修改此方法，违反开闭原则
        raise ValueError(f"未知的形状类型: {shape_type}")

# 遵循开闭原则的例子
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def calculate_area(self):
        pass

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def calculate_area(self):
        return self.width * self.height

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def calculate_area(self):
        return 3.14 * self.radius ** 2

# 新增三角形形状，不需要修改AreaCalculator
class Triangle(Shape):
    def __init__(self, base, height):
        self.base = base
        self.height = height
    
    def calculate_area(self):
        return 0.5 * self.base * self.height

class AreaCalculator:
    def calculate_area(self, shape):
        return shape.calculate_area()

# 测试
print("违反开闭原则的示例：")
area_calculator_violating = AreaCalculatorViolatingOCP()
rectangle_area = area_calculator_violating.calculate_area("rectangle", [5, 4])
circle_area = area_calculator_violating.calculate_area("circle", [3])
print(f"矩形面积: {rectangle_area}")
print(f"圆形面积: {circle_area}")

print("\n遵循开闭原则的示例：")
shapes = [
    Rectangle(5, 4),
    Circle(3),
    Triangle(4, 6)
]

area_calculator = AreaCalculator()
for shape in shapes:
    area = area_calculator.calculate_area(shape)
    print(f"{shape.__class__.__name__}的面积: {area}")

# 示例3：里氏替换原则
print("\n\n=== 里氏替换原则示例 ===")

# 违反里氏替换原则的例子
class BirdViolatingLSP:
    def fly(self):
        print("鸟儿在飞翔")

class PenguinViolatingLSP(BirdViolatingLSP):
    def fly(self):
        raise Exception("企鹅不会飞")
    # 子类不能替换父类，违反里氏替换原则

# 遵循里氏替换原则的例子
class Bird:
    def move(self):
        print("鸟儿在移动")

class FlyingBird(Bird):
    def move(self):
        self.fly()
    
    def fly(self):
        print("鸟儿在飞翔")

class Penguin(Bird):
    def move(self):
        self.swim()
    
    def swim(self):
        print("企鹅在游泳")

# 测试
print("违反里氏替换原则的示例（会抛出异常）:")
try:
    penguin = PenguinViolatingLSP()
    penguin.fly()
except Exception as e:
    print(f"异常: {e}")

print("\n遵循里氏替换原则的示例:")
birds = [FlyingBird(), Penguin()]
for bird in birds:
    bird.move()  # 子类可以替换父类，不会出错

# 示例4：接口隔离原则
print("\n\n=== 接口隔离原则示例 ===")

# 违反接口隔离原则的例子
class WorkerInterface:
    def work(self):
        pass
    
    def eat(self):
        pass

class RobotViolatingISP(WorkerInterface):
    def work(self):
        print("机器人在工作")
    
    def eat(self):
        raise NotImplementedError("机器人不需要吃饭")

# 遵循接口隔离原则的例子
class WorkableInterface:
    def work(self):
        pass

class EatableInterface:
    def eat(self):
        pass

class Human(WorkableInterface, EatableInterface):
    def work(self):
        print("人类在工作")
    
    def eat(self):
        print("人类在吃饭")

class Robot(WorkableInterface):
    def work(self):
        print("机器人在工作")

# 测试
print("违反接口隔离原则的示例（会抛出异常）:")
try:
    robot = RobotViolatingISP()
    robot.work()
    robot.eat()
except Exception as e:
    print(f"异常: {e}")

print("\n遵循接口隔离原则的示例:")
human = Human()
robot = Robot()

human.work()
human.eat()
robot.work()  # 机器人不需要实现eat方法

# 示例5：依赖倒置原则
print("\n\n=== 依赖倒置原则示例 ===")

# 违反依赖倒置原则的例子
class LightBulb:
    def turn_on(self):
        print("灯泡亮了")

class SwitchViolatingDIP:
    def __init__(self):
        self.bulb = LightBulb()  # 直接依赖具体实现
    
    def operate(self):
        self.bulb.turn_on()

# 遵循依赖倒置原则的例子
from abc import ABC, abstractmethod

class Switchable(ABC):
    @abstractmethod
    def turn_on(self):
        pass

class LightBulb(Switchable):
    def turn_on(self):
        print("灯泡亮了")

class Fan(Switchable):
    def turn_on(self):
        print("风扇转了")

class Switch:
    def __init__(self, device: Switchable):
        self.device = device  # 依赖抽象，不是具体实现
    
    def operate(self):
        self.device.turn_on()

# 测试
print("违反依赖倒置原则的示例:")
switch_violating = SwitchViolatingDIP()
switch_violating.operate()

print("\n遵循依赖倒置原则的示例:")
light_switch = Switch(LightBulb())
light_switch.operate()

fan_switch = Switch(Fan())
fan_switch.operate()

# 示例6：合成/聚合复用原则
print("\n\n=== 合成/聚合复用原则示例 ===")

# 使用继承的例子
class Vehicle:
    def move(self):
        print("移动")

class CarByInheritance(Vehicle):
    def move(self):
        print("汽车在移动")

# 使用组合的例子
class Engine:
    def start(self):
        print("引擎启动")

class Car:
    def __init__(self):
        self.engine = Engine()  # 组合关系，不是继承
    
    def move(self):
        self.engine.start()
        print("汽车在移动")

# 测试
print("使用继承的示例:")
car_by_inheritance = CarByInheritance()
car_by_inheritance.move()

print("\n使用组合的示例:")
car = Car()
car.move()

# 总结
print("\n\n=== 总结 ===")
print("通过以上示例，我们可以看到:")
print("1. 单一职责原则：一个类只做一件事")
print("2. 开闭原则：对扩展开放，对修改关闭")
print("3. 里氏替换原则：子类可以替换父类")
print("4. 接口隔离原则：不要强迫客户端依赖不需要的接口")
print("5. 依赖倒置原则：依赖抽象，不依赖具体实现")
print("6. 合成/聚合复用原则：优先使用组合而不是继承")
print("\n这些原则是设计模式的基础，理解它们有助于更好地学习和应用设计模式。")