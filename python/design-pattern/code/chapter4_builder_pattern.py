"""
第4章：建造者模式 - 示例代码

本文件包含了第4章中提到的所有示例代码，用于演示建造者模式的各种实现方式和应用场景。
"""

print("=== 建造者模式示例 ===\n")

# 1. 基本实现
print("1. 建造者模式的基本实现:")

# 产品类
class Computer:
    def __init__(self):
        self.cpu = None
        self.memory = None
        self.storage = None
        self.graphics = None
    
    def __str__(self):
        return f"电脑配置:\nCPU: {self.cpu}\n内存: {self.memory}\n存储: {self.storage}\n显卡: {self.graphics}"

# 抽象建造者
from abc import ABC, abstractmethod

class ComputerBuilder(ABC):
    @abstractmethod
    def build_cpu(self):
        pass
    
    @abstractmethod
    def build_memory(self):
        pass
    
    @abstractmethod
    def build_storage(self):
        pass
    
    @abstractmethod
    def build_graphics(self):
        pass
    
    @abstractmethod
    def get_computer(self):
        pass

# 具体建造者 - 游戏电脑建造者
class GamingComputerBuilder(ComputerBuilder):
    def __init__(self):
        self.computer = Computer()
    
    def build_cpu(self):
        self.computer.cpu = "Intel i9-12900K"
    
    def build_memory(self):
        self.computer.memory = "32GB DDR5"
    
    def build_storage(self):
        self.computer.storage = "1TB NVMe SSD"
    
    def build_graphics(self):
        self.computer.graphics = "NVIDIA RTX 4080"
    
    def get_computer(self):
        return self.computer

# 具体建造者 - 办公电脑建造者
class OfficeComputerBuilder(ComputerBuilder):
    def __init__(self):
        self.computer = Computer()
    
    def build_cpu(self):
        self.computer.cpu = "Intel i5-12400"
    
    def build_memory(self):
        self.computer.memory = "16GB DDR4"
    
    def build_storage(self):
        self.computer.storage = "512GB SSD"
    
    def build_graphics(self):
        self.computer.graphics = "集成显卡"
    
    def get_computer(self):
        return self.computer

# 指挥者
class ComputerDirector:
    def __init__(self, builder):
        self.builder = builder
    
    def construct_computer(self):
        self.builder.build_cpu()
        self.builder.build_memory()
        self.builder.build_storage()
        self.builder.build_graphics()
        return self.builder.get_computer()

# 客户端代码
print("游戏电脑:")
gaming_builder = GamingComputerBuilder()
director = ComputerDirector(gaming_builder)
gaming_computer = director.construct_computer()
print(gaming_computer)

print("\n办公电脑:")
office_builder = OfficeComputerBuilder()
director = ComputerDirector(office_builder)
office_computer = director.construct_computer()
print(office_computer)

# 2. 流畅接口(Fluent Interface)的实现
print("\n2. 流畅接口(Fluent Interface)的实现:")

# 产品类
class House:
    def __init__(self):
        self.foundation = None
        self.structure = None
        self.roof = None
        self.interior = None
    
    def __str__(self):
        return f"房屋详情:\n地基: {self.foundation}\n结构: {self.structure}\n屋顶: {self.roof}\n室内: {self.interior}"

# 建造者类 - 使用流畅接口
class HouseBuilder:
    def __init__(self):
        self.house = House()
    
    def build_foundation(self, foundation_type):
        self.house.foundation = foundation_type
        return self
    
    def build_structure(self, structure_type):
        self.house.structure = structure_type
        return self
    
    def build_roof(self, roof_type):
        self.house.roof = roof_type
        return self
    
    def build_interior(self, interior_type):
        self.house.interior = interior_type
        return self
    
    def get_house(self):
        return self.house

# 使用示例
print("使用流畅接口建造房屋:")
house = (HouseBuilder()
         .build_foundation("钢筋混凝土")
         .build_structure("钢结构")
         .build_roof("瓦片屋顶")
         .build_interior("现代简约")
         .get_house())
print(house)

# 3. 使用类方法的实现
print("\n3. 使用类方法的实现:")

# 产品类
class User:
    def __init__(self):
        self.username = None
        self.email = None
        self.age = None
        self.address = None
        self.phone = None
    
    def __str__(self):
        return f"用户信息:\n用户名: {self.username}\n邮箱: {self.email}\n年龄: {self.age}\n地址: {self.address}\n电话: {self.phone}"

# 建造者类
class UserBuilder:
    def __init__(self, username, email):
        self.user = User()
        self.user.username = username
        self.user.email = email
    
    def age(self, age):
        self.user.age = age
        return self
    
    def address(self, address):
        self.user.address = address
        return self
    
    def phone(self, phone):
        self.user.phone = phone
        return self
    
    def build(self):
        return self.user

# 使用示例
print("使用类方法建造用户:")
user = (UserBuilder("john_doe", "john@example.com")
        .age(30)
        .address("北京市朝阳区")
        .phone("13812345678")
        .build())
print(user)

# 4. SQL查询构建器
print("\n4. SQL查询构建器:")

# 产品类 - SQL查询
class SQLQuery:
    def __init__(self):
        self.select_fields = []
        self.from_table = None
        self.where_conditions = []
        self.group_by_fields = []
        self.having_conditions = []
        self.order_by_fields = []
        self.limit_count = None
    
    def __str__(self):
        query = "SELECT "
        query += ", ".join(self.select_fields) if self.select_fields else "*"
        
        if self.from_table:
            query += f" FROM {self.from_table}"
        
        if self.where_conditions:
            query += f" WHERE {' AND '.join(self.where_conditions)}"
        
        if self.group_by_fields:
            query += f" GROUP BY {', '.join(self.group_by_fields)}"
        
        if self.having_conditions:
            query += f" HAVING {' AND '.join(self.having_conditions)}"
        
        if self.order_by_fields:
            query += f" ORDER BY {', '.join(self.order_by_fields)}"
        
        if self.limit_count:
            query += f" LIMIT {self.limit_count}"
        
        return query

# 建造者类
class SQLQueryBuilder:
    def __init__(self):
        self.query = SQLQuery()
    
    def select(self, *fields):
        self.query.select_fields.extend(fields)
        return self
    
    def from_table(self, table):
        self.query.from_table = table
        return self
    
    def where(self, condition):
        self.query.where_conditions.append(condition)
        return self
    
    def group_by(self, *fields):
        self.query.group_by_fields.extend(fields)
        return self
    
    def having(self, condition):
        self.query.having_conditions.append(condition)
        return self
    
    def order_by(self, *fields):
        self.query.order_by_fields.extend(fields)
        return self
    
    def limit(self, count):
        self.query.limit_count = count
        return self
    
    def build(self):
        return self.query

# 使用示例
print("SQL查询构建器:")
query = (SQLQueryBuilder()
         .select("name", "age", "department")
         .from_table("employees")
         .where("age > 18")
         .where("status = 'active'")
         .group_by("department")
         .having("COUNT(*) > 5")
         .order_by("name ASC")
         .limit(10)
         .build())

print(f"生成的SQL查询:\n{query}")

# 5. 文档构建器
print("\n5. 文档构建器:")

# 产品类 - 文档
class Document:
    def __init__(self):
        self.title = None
        self.author = None
        self.sections = []
    
    def add_section(self, title, content):
        self.sections.append({"title": title, "content": content})
    
    def __str__(self):
        doc = f"标题: {self.title}\n作者: {self.author}\n\n"
        for i, section in enumerate(self.sections, 1):
            doc += f"{i}. {section['title']}\n"
            doc += f"   {section['content']}\n\n"
        return doc

# 建造者类
class DocumentBuilder:
    def __init__(self):
        self.document = Document()
    
    def title(self, title):
        self.document.title = title
        return self
    
    def author(self, author):
        self.document.author = author
        return self
    
    def add_section(self, title, content):
        self.document.add_section(title, content)
        return self
    
    def build(self):
        return self.document

# 使用示例
print("文档构建器:")
document = (DocumentBuilder()
            .title("设计模式学习笔记")
            .author("张三")
            .add_section("创建型模式", "包括单例模式、工厂方法模式、建造者模式等")
            .add_section("结构型模式", "包括适配器模式、装饰器模式、外观模式等")
            .add_section("行为型模式", "包括观察者模式、策略模式、模板方法模式等")
            .build())

print(document)

# 6. 配置构建器
print("\n6. 配置构建器:")

# 产品类 - 应用配置
class AppConfig:
    def __init__(self):
        self.database_config = {}
        self.server_config = {}
        self.logging_config = {}
        self.cache_config = {}
    
    def __str__(self):
        return f"应用配置:\n数据库: {self.database_config}\n服务器: {self.server_config}\n日志: {self.logging_config}\n缓存: {self.cache_config}"

# 建造者类
class ConfigBuilder:
    def __init__(self):
        self.config = AppConfig()
    
    def database(self, host, port, username, password, db_name):
        self.config.database_config = {
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "database": db_name
        }
        return self
    
    def server(self, host, port, workers):
        self.config.server_config = {
            "host": host,
            "port": port,
            "workers": workers
        }
        return self
    
    def logging(self, level, file_path):
        self.config.logging_config = {
            "level": level,
            "file_path": file_path
        }
        return self
    
    def cache(self, backend, ttl):
        self.config.cache_config = {
            "backend": backend,
            "ttl": ttl
        }
        return self
    
    def build(self):
        return self.config

# 使用示例
print("配置构建器:")
app_config = (ConfigBuilder()
              .database("localhost", 3306, "root", "123456", "myapp")
              .server("0.0.0.0", 8080, 4)
              .logging("INFO", "/var/log/app.log")
              .cache("redis", 3600)
              .build())

print(app_config)

# 7. 使用@dataclass的建造者
print("\n7. 使用@dataclass的建造者:")

from dataclasses import dataclass, field
from typing import Optional

# 产品类
@dataclass
class Car:
    make: str = ""
    model: str = ""
    year: int = 0
    color: str = ""
    engine: str = ""
    transmission: str = ""
    features: list = field(default_factory=list)

# 建造者类
class CarBuilder:
    def __init__(self):
        self.car = Car()
    
    def make(self, make):
        self.car.make = make
        return self
    
    def model(self, model):
        self.car.model = model
        return self
    
    def year(self, year):
        self.car.year = year
        return self
    
    def color(self, color):
        self.car.color = color
        return self
    
    def engine(self, engine):
        self.car.engine = engine
        return self
    
    def transmission(self, transmission):
        self.car.transmission = transmission
        return self
    
    def add_feature(self, feature):
        self.car.features.append(feature)
        return self
    
    def build(self):
        return self.car

# 使用示例
print("使用@dataclass的汽车建造者:")
car = (CarBuilder()
       .make("Toyota")
       .model("Camry")
       .year(2023)
       .color("蓝色")
       .engine("2.5L V6")
       .transmission("自动")
       .add_feature("导航系统")
       .add_feature("倒车影像")
       .add_feature("蓝牙音响")
       .build())

print(car)

# 8. 使用函数式编程的建造者
print("\n8. 使用函数式编程的建造者:")

# 产品类
class Meal:
    def __init__(self):
        self.main_course = None
        self.side_dish = None
        self.drink = None
        self.dessert = None
    
    def __str__(self):
        return f"套餐:\n主菜: {self.main_course}\n配菜: {self.side_dish}\n饮料: {self.drink}\n甜点: {self.dessert}"

# 建造者函数
def create_meal():
    meal = Meal()
    
    def main_course(course):
        meal.main_course = course
        return builder
    
    def side_dish(dish):
        meal.side_dish = dish
        return builder
    
    def drink(drink):
        meal.drink = drink
        return builder
    
    def dessert(dessert):
        meal.dessert = dessert
        return builder
    
    def build():
        return meal
    
    builder = {
        'main_course': main_course,
        'side_dish': side_dish,
        'drink': drink,
        'dessert': dessert,
        'build': build
    }
    
    return builder

# 使用示例
print("使用函数式编程的餐食建造者:")
meal_builder = create_meal()
meal_builder['main_course']('牛排')
meal_builder['side_dish']('薯条')
meal_builder['drink']('可乐')
meal_builder['dessert']('冰淇淋')
meal = meal_builder['build']()

print(meal)

# 总结
print("\n=== 总结 ===")
print("建造者模式将一个复杂对象的构建与其表示分离，使得同样的构建过程可以创建不同的表示。")
print("建造者模式的主要优点:")
print("1. 可以分步骤创建复杂对象")
print("2. 提高了代码的可读性和可维护性")
print("3. 可以使用相同的构建过程创建不同的表示")
print("4. 可以在构建过程中验证参数的有效性")
print("\n在Python中，常见的实现方式包括:")
print("1. 基本建造者模式（指挥者+建造者）")
print("2. 流畅接口(Fluent Interface)")
print("3. 使用类方法的实现")
print("4. 使用@dataclass的建造者")
print("5. 函数式编程的建造者")