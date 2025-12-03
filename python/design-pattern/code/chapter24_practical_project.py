"""
第24章：设计模式实战项目 - 在线书店系统

这个实战项目展示了如何在实际应用中综合使用多种设计模式。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from enum import Enum
import time

# ========== 基础架构模式 ==========

# 1. 单例模式 - 数据库连接池
class DatabaseConnectionPool:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connections = []
            cls._instance._max_connections = 10
        return cls._instance
    
    def get_connection(self):
        if len(self._connections) < self._max_connections:
            connection = f"Connection_{len(self._connections)+1}"
            self._connections.append(connection)
            return connection
        raise Exception("Connection pool exhausted")

# 2. 装饰器模式 - 日志记录器
class Logger:
    def __init__(self, name):
        self.name = name
    
    def log(self, message):
        print(f"[{self.name}] {message}")

def log_decorator(logger):
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.log(f"Calling {func.__name__}")
            result = func(*args, **kwargs)
            logger.log(f"{func.__name__} completed")
            return result
        return wrapper
    return decorator

# ========== 图书管理 ==========

# 3. 工厂方法模式 - 图书工厂
class Book(ABC):
    def __init__(self, title, author, price):
        self.title = title
        self.author = author
        self.price = price
    
    @abstractmethod
    def get_description(self):
        pass

class PhysicalBook(Book):
    def get_description(self):
        return f"Physical Book: {self.title} by {self.author} - ${self.price}"

class EBook(Book):
    def get_description(self):
        return f"E-Book: {self.title} by {self.author} - ${self.price}"

class BookFactory:
    @staticmethod
    def create_book(book_type, title, author, price):
        if book_type == "physical":
            return PhysicalBook(title, author, price)
        elif book_type == "ebook":
            return EBook(title, author, price)
        else:
            raise ValueError("Invalid book type")

# 4. 原型模式 - 图书克隆
class PrototypeBook(Book):
    def __init__(self, title, author, price, category):
        super().__init__(title, author, price)
        self.category = category
    
    def clone(self):
        return PrototypeBook(self.title, self.author, self.price, self.category)
    
    def get_description(self):
        return f"{self.title} by {self.author} - ${self.price} ({self.category})"

# ========== 用户管理 ==========

# 5. 适配器模式 - 认证系统
class LegacyAuthSystem:
    def authenticate_legacy(self, username, password):
        # 模拟旧的认证系统
        return username == "admin" and password == "password"

class ModernAuthSystem:
    def authenticate(self, credentials):
        return credentials.get("username") == "admin" and credentials.get("password") == "password"

class AuthAdapter:
    def __init__(self, legacy_system):
        self.legacy_system = legacy_system
    
    def authenticate(self, credentials):
        return self.legacy_system.authenticate_legacy(
            credentials.get("username"),
            credentials.get("password")
        )

# ========== 购物车 ==========

# 6. 组合模式 - 购物车
class CartItem(ABC):
    @abstractmethod
    def get_price(self):
        pass
    
    @abstractmethod
    def display(self):
        pass

class SingleItem(CartItem):
    def __init__(self, book, quantity=1):
        self.book = book
        self.quantity = quantity
    
    def get_price(self):
        return self.book.price * self.quantity
    
    def display(self):
        return f"{self.quantity} x {self.book.get_description()}"

class CartComposite(CartItem):
    def __init__(self, name):
        self.name = name
        self.items: List[CartItem] = []
    
    def add_item(self, item):
        self.items.append(item)
    
    def remove_item(self, item):
        self.items.remove(item)
    
    def get_price(self):
        return sum(item.get_price() for item in self.items)
    
    def display(self):
        result = f"{self.name}:\n"
        for item in self.items:
            result += f"  {item.display()}\n"
        return result

# 7. 装饰器模式 - 购物车折扣
class CartDecorator(CartItem):
    def __init__(self, cart_item):
        self.cart_item = cart_item
    
    def get_price(self):
        return self.cart_item.get_price()
    
    def display(self):
        return self.cart_item.display()

class PercentageDiscountDecorator(CartDecorator):
    def __init__(self, cart_item, percentage):
        super().__init__(cart_item)
        self.percentage = percentage
    
    def get_price(self):
        original_price = self.cart_item.get_price()
        return original_price * (1 - self.percentage / 100)
    
    def display(self):
        return f"{self.cart_item.display()} (-{self.percentage}% discount)"

# ========== 订单处理 ==========

# 8. 建造者模式 - 订单构建
class Order:
    def __init__(self):
        self.items = []
        self.shipping_address = None
        self.payment_method = None
        self.discount = 0

class OrderBuilder:
    def __init__(self):
        self.order = Order()
    
    def add_item(self, book, quantity=1):
        self.order.items.append((book, quantity))
        return self
    
    def set_shipping_address(self, address):
        self.order.shipping_address = address
        return self
    
    def set_payment_method(self, method):
        self.order.payment_method = method
        return self
    
    def set_discount(self, discount):
        self.order.discount = discount
        return self
    
    def build(self):
        return self.order

# 9. 状态模式 - 订单状态
class OrderState(ABC):
    @abstractmethod
    def process(self, order):
        pass

class PendingState(OrderState):
    def process(self, order):
        print("Order is pending payment")
        return PaidState()

class PaidState(OrderState):
    def process(self, order):
        print("Order is paid, preparing for shipping")
        return ShippedState()

class ShippedState(OrderState):
    def process(self, order):
        print("Order has been shipped")
        return DeliveredState()

class DeliveredState(OrderState):
    def process(self, order):
        print("Order has been delivered")
        return self

class OrderContext:
    def __init__(self):
        self.state: OrderState = PendingState()
    
    def process(self):
        self.state = self.state.process(self)

# ========== 支付处理 ==========

# 10. 策略模式 - 支付方式
class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount):
        pass

class CreditCardPayment(PaymentStrategy):
    def pay(self, amount):
        print(f"Paid ${amount} using Credit Card")
        return True

class PayPalPayment(PaymentStrategy):
    def pay(self, amount):
        print(f"Paid ${amount} using PayPal")
        return True

class PaymentProcessor:
    def __init__(self):
        self.strategy = None
    
    def set_strategy(self, strategy):
        self.strategy = strategy
    
    def process_payment(self, amount):
        if self.strategy:
            return self.strategy.pay(amount)
        raise ValueError("No payment strategy set")

# ========== 事件通知 ==========

# 11. 观察者模式 - 订单通知
class OrderObserver(ABC):
    @abstractmethod
    def update(self, order, event):
        pass

class EmailNotification(OrderObserver):
    def update(self, order, event):
        print(f"Email: Order {event} - {order}")

class SMSNotification(OrderObserver):
    def update(self, order, event):
        print(f"SMS: Order {event} - {order}")

class OrderNotifier:
    def __init__(self):
        self._observers: List[OrderObserver] = []
    
    def attach(self, observer):
        self._observers.append(observer)
    
    def detach(self, observer):
        self._observers.remove(observer)
    
    def notify(self, order, event):
        for observer in self._observers:
            observer.update(order, event)

# ========== 系统接口 ==========

# 12. 外观模式 - 书店系统外观
class BookStoreFacade:
    def __init__(self):
        self.db_pool = DatabaseConnectionPool()
        self.logger = Logger("BookStore")
        self.book_factory = BookFactory()
        self.payment_processor = PaymentProcessor()
        self.order_notifier = OrderNotifier()
        
        # 添加通知观察者
        self.order_notifier.attach(EmailNotification())
        self.order_notifier.attach(SMSNotification())
    
    @log_decorator(Logger("BookStore"))
    def purchase_book(self, book_type, title, author, price, payment_method):
        # 创建图书
        book = self.book_factory.create_book(book_type, title, author, price)
        
        # 设置支付策略
        if payment_method == "credit_card":
            self.payment_processor.set_strategy(CreditCardPayment())
        elif payment_method == "paypal":
            self.payment_processor.set_strategy(PayPalPayment())
        
        # 处理支付
        self.payment_processor.process_payment(price)
        
        # 发送通知
        self.order_notifier.notify(book, "purchased")
        
        return book

# ========== 测试代码 ==========

def test_design_patterns():
    """测试所有设计模式的功能"""
    
    print("=== Python设计模式实战项目测试 ===\n")
    
    # 1. 测试单例模式
    print("1. 测试单例模式 - 数据库连接池")
    db1 = DatabaseConnectionPool()
    db2 = DatabaseConnectionPool()
    print(f"两个实例是否相同: {db1 is db2}")
    connection = db1.get_connection()
    print(f"获取连接: {connection}")
    print()
    
    # 2. 测试工厂方法模式
    print("2. 测试工厂方法模式 - 图书创建")
    physical_book = BookFactory.create_book("physical", "Design Patterns", "GoF", 49.99)
    ebook = BookFactory.create_book("ebook", "Python Programming", "Guido", 29.99)
    print(physical_book.get_description())
    print(ebook.get_description())
    print()
    
    # 3. 测试原型模式
    print("3. 测试原型模式 - 图书克隆")
    original_book = PrototypeBook("Original Book", "Author", 39.99, "Technology")
    cloned_book = original_book.clone()
    print(f"原书: {original_book.get_description()}")
    print(f"克隆: {cloned_book.get_description()}")
    print(f"是否为不同对象: {original_book is not cloned_book}")
    print()
    
    # 4. 测试组合模式
    print("4. 测试组合模式 - 购物车")
    cart = CartComposite("购物车")
    cart.add_item(SingleItem(physical_book, 2))
    cart.add_item(SingleItem(ebook, 1))
    print(cart.display())
    print(f"总价: ${cart.get_price()}")
    print()
    
    # 5. 测试装饰器模式
    print("5. 测试装饰器模式 - 购物车折扣")
    discounted_cart = PercentageDiscountDecorator(cart, 10)
    print(discounted_cart.display())
    print(f"折扣后价格: ${discounted_cart.get_price():.2f}")
    print()
    
    # 6. 测试状态模式
    print("6. 测试状态模式 - 订单状态")
    order = OrderContext()
    order.process()  # 待支付 -> 已支付
    order.process()  # 已支付 -> 已发货
    order.process()  # 已发货 -> 已送达
    print()
    
    # 7. 测试策略模式
    print("7. 测试策略模式 - 支付方式")
    processor = PaymentProcessor()
    processor.set_strategy(CreditCardPayment())
    processor.process_payment(100)
    processor.set_strategy(PayPalPayment())
    processor.process_payment(50)
    print()
    
    # 8. 测试外观模式
    print("8. 测试外观模式 - 完整购买流程")
    bookstore = BookStoreFacade()
    purchased_book = bookstore.purchase_book(
        "physical", "Complete Bookstore", "Author", 59.99, "credit_card"
    )
    print(f"购买成功: {purchased_book.get_description()}")
    print()
    
    print("=== 所有测试完成 ===")

if __name__ == "__main__":
    test_design_patterns()