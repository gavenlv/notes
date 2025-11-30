"""
第3章：工厂方法模式 - 示例代码

本文件包含了第3章中提到的所有示例代码，用于演示工厂方法模式的各种实现方式和应用场景。
"""

print("=== 工厂方法模式示例 ===\n")

# 1. 基本实现
print("1. 工厂方法模式的基本实现:")

from abc import ABC, abstractmethod

# 抽象产品
class Product(ABC):
    @abstractmethod
    def operation(self):
        pass

# 具体产品A
class ConcreteProductA(Product):
    def operation(self):
        return "具体产品A的操作"

# 具体产品B
class ConcreteProductB(Product):
    def operation(self):
        return "具体产品B的操作"

# 抽象工厂
class Creator(ABC):
    @abstractmethod
    def factory_method(self):
        pass
    
    def some_operation(self):
        product = self.factory_method()
        return f"工厂操作: {product.operation()}"

# 具体工厂A
class ConcreteCreatorA(Creator):
    def factory_method(self):
        return ConcreteProductA()

# 具体工厂B
class ConcreteCreatorB(Creator):
    def factory_method(self):
        return ConcreteProductB()

# 客户端代码
def client_code(creator):
    print(creator.some_operation())

# 测试
creator_a = ConcreteCreatorA()
client_code(creator_a)  # 输出: 工厂操作: 具体产品A的操作

creator_b = ConcreteCreatorB()
client_code(creator_b)  # 输出: 工厂操作: 具体产品B的操作

# 2. 简单的工厂方法实现
print("\n2. 简单的工厂方法实现:")

# 动物产品
class Animal:
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "汪汪汪"

class Cat(Animal):
    def speak(self):
        return "喵喵喵"

# 动物工厂
class AnimalFactory:
    @staticmethod
    def create_animal(animal_type):
        if animal_type == "dog":
            return Dog()
        elif animal_type == "cat":
            return Cat()
        else:
            raise ValueError(f"未知的动物类型: {animal_type}")

# 测试
factory = AnimalFactory()
dog = factory.create_animal("dog")
cat = factory.create_animal("cat")

print(dog.speak())  # 输出: 汪汪汪
print(cat.speak())  # 输出: 喵喵喵

# 3. 使用注册表的工厂方法
print("\n3. 使用注册表的工厂方法:")

class ProductRegistry:
    _registry = {}
    
    @classmethod
    def register(cls, product_type, product_class):
        cls._registry[product_type] = product_class
    
    @classmethod
    def create(cls, product_type, *args, **kwargs):
        if product_type not in cls._registry:
            raise ValueError(f"未注册的产品类型: {product_type}")
        return cls._registry[product_type](*args, **kwargs)

# 产品类
class ProductA:
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return f"产品A: {self.name}"

class ProductB:
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return f"产品B: {self.name}"

# 注册产品
ProductRegistry.register("A", ProductA)
ProductRegistry.register("B", ProductB)

# 使用注册表创建产品
product_a = ProductRegistry.create("A", "产品A实例")
product_b = ProductRegistry.create("B", "产品B实例")

print(product_a)  # 输出: 产品A: 产品A实例
print(product_b)  # 输出: 产品B: 产品B实例

# 4. 日志记录器工厂
print("\n4. 日志记录器工厂:")

from datetime import datetime

# 抽象日志记录器
class Logger(ABC):
    @abstractmethod
    def log(self, message):
        pass

# 控制台日志记录器
class ConsoleLogger(Logger):
    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] CONSOLE: {message}")

# 文件日志记录器
class FileLogger(Logger):
    def __init__(self, filename):
        self.filename = filename
    
    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.filename, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] FILE: {message}\n")

# 数据库日志记录器
class DatabaseLogger(Logger):
    def __init__(self, db_connection):
        self.db_connection = db_connection
    
    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 实际应用中会执行数据库插入操作
        print(f"[{timestamp}] DATABASE: {message} (保存到数据库 {self.db_connection})")

# 抽象日志工厂
class LoggerFactory(ABC):
    @abstractmethod
    def create_logger(self):
        pass

# 具体控制台日志工厂
class ConsoleLoggerFactory(LoggerFactory):
    def create_logger(self):
        return ConsoleLogger()

# 具体文件日志工厂
class FileLoggerFactory(LoggerFactory):
    def __init__(self, filename):
        self.filename = filename
    
    def create_logger(self):
        return FileLogger(self.filename)

# 具体数据库日志工厂
class DatabaseLoggerFactory(LoggerFactory):
    def __init__(self, db_connection):
        self.db_connection = db_connection
    
    def create_logger(self):
        return DatabaseLogger(self.db_connection)

# 客户端代码
def client_code(logger_factory):
    logger = logger_factory.create_logger()
    logger.log("这是一条测试日志消息")

# 测试
print("控制台日志:")
console_factory = ConsoleLoggerFactory()
client_code(console_factory)

print("\n文件日志:")
file_factory = FileLoggerFactory("app.log")
client_code(file_factory)

print("\n数据库日志:")
db_factory = DatabaseLoggerFactory("localhost:3306")
client_code(db_factory)

# 清理文件
import os
if os.path.exists("app.log"):
    os.remove("app.log")

# 5. 支付处理工厂
print("\n5. 支付处理工厂:")

# 抽象支付处理器
class PaymentProcessor(ABC):
    @abstractmethod
    def process_payment(self, amount):
        pass

# 信用卡支付处理器
class CreditCardProcessor(PaymentProcessor):
    def __init__(self, card_number, cvv):
        self.card_number = card_number
        self.cvv = cvv
    
    def process_payment(self, amount):
        print(f"使用信用卡 {self.card_number} 支付 ¥{amount:.2f}")
        return {"status": "success", "transaction_id": f"CC_{hash(self.card_number)}"}

# 支付宝支付处理器
class AlipayProcessor(PaymentProcessor):
    def __init__(self, account_id):
        self.account_id = account_id
    
    def process_payment(self, amount):
        print(f"使用支付宝账号 {self.account_id} 支付 ¥{amount:.2f}")
        return {"status": "success", "transaction_id": f"ALI_{hash(self.account_id)}"}

# 微信支付处理器
class WeChatPayProcessor(PaymentProcessor):
    def __init__(self, openid):
        self.openid = openid
    
    def process_payment(self, amount):
        print(f"使用微信账号 {self.openid} 支付 ¥{amount:.2f}")
        return {"status": "success", "transaction_id": f"WX_{hash(self.openid)}"}

# 支付工厂
class PaymentProcessorFactory:
    @staticmethod
    def create_processor(payment_type, **kwargs):
        if payment_type == "credit_card":
            return CreditCardProcessor(kwargs.get("card_number"), kwargs.get("cvv"))
        elif payment_type == "alipay":
            return AlipayProcessor(kwargs.get("account_id"))
        elif payment_type == "wechat":
            return WeChatPayProcessor(kwargs.get("openid"))
        else:
            raise ValueError(f"不支持的支付方式: {payment_type}")

# 测试
payment_configs = [
    {"type": "credit_card", "card_number": "1234-5678-9012-3456", "cvv": "123"},
    {"type": "alipay", "account_id": "user@example.com"},
    {"type": "wechat", "openid": "ox123456789"}
]

for config in payment_configs:
    payment_type = config["type"]
    params = {k: v for k, v in config.items() if k != "type"}
    
    processor = PaymentProcessorFactory.create_processor(payment_type, **params)
    result = processor.process_payment(100.00)
    print(f"支付结果: {result}")

# 6. 参数化工厂方法
print("\n6. 参数化工厂方法:")

class ShapeFactory:
    @staticmethod
    def create_shape(shape_type, *args):
        if shape_type == "circle":
            return Circle(*args)
        elif shape_type == "rectangle":
            return Rectangle(*args)
        elif shape_type == "triangle":
            return Triangle(*args)
        else:
            raise ValueError(f"不支持的形状类型: {shape_type}")

class Shape:
    def area(self):
        pass

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        return 3.14 * self.radius ** 2
    
    def __str__(self):
        return f"圆形(半径={self.radius})"

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height
    
    def __str__(self):
        return f"矩形(宽={self.width}, 高={self.height})"

class Triangle(Shape):
    def __init__(self, base, height):
        self.base = base
        self.height = height
    
    def area(self):
        return 0.5 * self.base * self.height
    
    def __str__(self):
        return f"三角形(底={self.base}, 高={self.height})"

# 测试
shapes = [
    ShapeFactory.create_shape("circle", 5),
    ShapeFactory.create_shape("rectangle", 4, 6),
    ShapeFactory.create_shape("triangle", 3, 4)
]

for shape in shapes:
    print(f"{shape}的面积: {shape.area()}")

# 7. 使用类注册的工厂
print("\n7. 使用类注册的工厂:")

class ServiceFactory:
    _services = {}
    
    @classmethod
    def register(cls, service_name, service_class):
        cls._services[service_name] = service_class
    
    @classmethod
    def create(cls, service_name, *args, **kwargs):
        if service_name not in cls._services:
            raise ValueError(f"未注册的服务: {service_name}")
        return cls._services[service_name](*args, **kwargs)
    
    @classmethod
    def list_services(cls):
        return list(cls._services.keys())

# 定义服务类
class UserService:
    def __init__(self, db_connection):
        self.db_connection = db_connection
    
    def get_user(self, user_id):
        return f"从数据库{self.db_connection}获取用户{user_id}"

class NotificationService:
    def __init__(self, email_provider):
        self.email_provider = email_provider
    
    def send_notification(self, user, message):
        return f"通过{self.email_provider}向用户{user}发送通知: {message}"

class CacheService:
    def __init__(self, cache_type):
        self.cache_type = cache_type
    
    def cache_data(self, key, value):
        return f"将数据{key}:{value}缓存到{self.cache_type}"

# 注册服务
ServiceFactory.register("user", UserService)
ServiceFactory.register("notification", NotificationService)
ServiceFactory.register("cache", CacheService)

# 使用工厂创建服务
user_service = ServiceFactory.create("user", "localhost:3306")
notification_service = ServiceFactory.create("notification", "Gmail")
cache_service = ServiceFactory.create("cache", "Redis")

# 测试服务
print(user_service.get_user("123"))
print(notification_service.send_notification("张三", "欢迎注册"))
print(cache_service.cache_data("session:123", "user_data"))

print(f"已注册的服务: {ServiceFactory.list_services()}")

# 8. 使用反射的工厂
print("\n8. 使用反射的工厂:")

def create_class_by_name(class_name, *args, **kwargs):
    # 在实际应用中，这需要从正确的模块导入类
    # 这里使用当前模块的类作为示例
    if class_name in globals():
        return globals()[class_name](*args, **kwargs)
    else:
        raise ValueError(f"未找到类: {class_name}")

# 测试
try:
    circle = create_class_by_name("Circle", 3)
    print(f"通过反射创建的圆形: {circle}, 面积: {circle.area()}")
    
    rectangle = create_class_by_name("Rectangle", 5, 4)
    print(f"通过反射创建的矩形: {rectangle}, 面积: {rectangle.area()}")
except ValueError as e:
    print(e)

# 总结
print("\n=== 总结 ===")
print("工厂方法模式定义了一个创建对象的接口，但让子类决定实例化哪一个类。")
print("工厂方法模式的主要优点:")
print("1. 将对象的创建和使用分离，降低系统的耦合度")
print("2. 符合开闭原则，对扩展开放，对修改关闭")
print("3. 隐藏了产品类的实现细节，对调用者透明")
print("4. 提高了系统的灵活性和可扩展性")
print("\n在Python中，我们可以利用动态语言的特性，使工厂方法的实现更加灵活。")
print("常见的实现方式包括:")
print("1. 使用抽象基类和具体实现类")
print("2. 使用注册表模式")
print("3. 使用参数化工厂方法")
print("4. 使用反射动态创建对象")