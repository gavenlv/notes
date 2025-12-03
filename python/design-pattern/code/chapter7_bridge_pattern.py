"""
桥接模式 (Bridge Pattern) 示例代码

桥接模式将抽象部分与它的实现部分分离，使它们都可以独立地变化。
"""

from abc import ABC, abstractmethod


class DrawingAPI(ABC):
    """实现部分接口 - 绘制API"""
    
    @abstractmethod
    def draw_circle(self, x, y, radius):
        pass

    @abstractmethod
    def draw_rectangle(self, x, y, width, height):
        pass


class WindowsAPI(DrawingAPI):
    """Windows系统的绘制实现"""
    
    def draw_circle(self, x, y, radius):
        print(f"Windows: 在位置({x}, {y})绘制半径为{radius}的圆")
    
    def draw_rectangle(self, x, y, width, height):
        print(f"Windows: 在位置({x}, {y})绘制{width}x{height}的矩形")


class LinuxAPI(DrawingAPI):
    """Linux系统的绘制实现"""
    
    def draw_circle(self, x, y, radius):
        print(f"Linux: 在位置({x}, {y})绘制半径为{radius}的圆")
    
    def draw_rectangle(self, x, y, width, height):
        print(f"Linux: 在位置({x}, {y})绘制{width}x{height}的矩形")


class Shape(ABC):
    """抽象部分 - 形状类"""
    
    def __init__(self, drawing_api: DrawingAPI):
        self._drawing_api = drawing_api
    
    @abstractmethod
    def draw(self):
        pass
    
    @abstractmethod
    def resize(self, factor):
        pass


class Circle(Shape):
    """具体抽象 - 圆形"""
    
    def __init__(self, x, y, radius, drawing_api: DrawingAPI):
        super().__init__(drawing_api)
        self._x = x
        self._y = y
        self._radius = radius
    
    def draw(self):
        self._drawing_api.draw_circle(self._x, self._y, self._radius)
    
    def resize(self, factor):
        self._radius *= factor
        print(f"圆形大小调整为原来的{factor}倍，新半径为{self._radius}")


class Rectangle(Shape):
    """具体抽象 - 矩形"""
    
    def __init__(self, x, y, width, height, drawing_api: DrawingAPI):
        super().__init__(drawing_api)
        self._x = x
        self._y = y
        self._width = width
        self._height = height
    
    def draw(self):
        self._drawing_api.draw_rectangle(self._x, self._y, self._width, self._height)
    
    def resize(self, factor):
        self._width *= factor
        self._height *= factor
        print(f"矩形大小调整为原来的{factor}倍，新尺寸为{self._width}x{self._height}")


# 测试代码
def test_bridge_pattern():
    """测试桥接模式"""
    print("=== 桥接模式测试 ===")
    
    # 创建不同的绘制API
    windows_api = WindowsAPI()
    linux_api = LinuxAPI()
    
    # 创建圆形，使用Windows绘制API
    circle1 = Circle(10, 10, 5, windows_api)
    circle1.draw()
    circle1.resize(2)
    circle1.draw()
    
    print("\n---")
    
    # 创建圆形，使用Linux绘制API
    circle2 = Circle(20, 20, 3, linux_api)
    circle2.draw()
    circle2.resize(1.5)
    circle2.draw()
    
    print("\n---")
    
    # 创建矩形，使用Windows绘制API
    rectangle1 = Rectangle(5, 5, 8, 6, windows_api)
    rectangle1.draw()
    rectangle1.resize(0.5)
    rectangle1.draw()
    
    print("\n---")
    
    # 创建矩形，使用Linux绘制API
    rectangle2 = Rectangle(15, 15, 10, 8, linux_api)
    rectangle2.draw()
    rectangle2.resize(2)
    rectangle2.draw()


# 实际应用示例：不同数据库连接和不同ORM框架的桥接
class DatabaseConnection(ABC):
    """数据库连接接口"""
    
    @abstractmethod
    def connect(self):
        pass
    
    @abstractmethod
    def execute(self, query):
        pass


class MySQLConnection(DatabaseConnection):
    """MySQL数据库连接"""
    
    def connect(self):
        print("连接到MySQL数据库")
    
    def execute(self, query):
        print(f"MySQL执行查询: {query}")


class PostgreSQLConnection(DatabaseConnection):
    """PostgreSQL数据库连接"""
    
    def connect(self):
        print("连接到PostgreSQL数据库")
    
    def execute(self, query):
        print(f"PostgreSQL执行查询: {query}")


class ORMFramework(ABC):
    """ORM框架抽象类"""
    
    def __init__(self, connection: DatabaseConnection):
        self._connection = connection
    
    @abstractmethod
    def save(self, entity):
        pass
    
    @abstractmethod
    def find(self, id):
        pass


class DjangoORM(ORMFramework):
    """Django ORM实现"""
    
    def save(self, entity):
        self._connection.connect()
        self._connection.execute(f"INSERT INTO {entity.__class__.__name__} VALUES (...)")
        print("Django ORM: 保存实体")
    
    def find(self, id):
        self._connection.connect()
        self._connection.execute(f"SELECT * FROM table WHERE id = {id}")
        print("Django ORM: 查找实体")


class SQLAlchemyORM(ORMFramework):
    """SQLAlchemy ORM实现"""
    
    def save(self, entity):
        self._connection.connect()
        self._connection.execute(f"SAVE {entity.__class__.__name__}")
        print("SQLAlchemy ORM: 保存实体")
    
    def find(self, id):
        self._connection.connect()
        self._connection.execute(f"FIND BY ID {id}")
        print("SQLAlchemy ORM: 查找实体")


def test_database_bridge():
    """测试数据库桥接示例"""
    print("\n=== 数据库桥接示例 ===")
    
    # 创建不同的数据库连接
    mysql_conn = MySQLConnection()
    postgres_conn = PostgreSQLConnection()
    
    # 创建Django ORM，使用MySQL连接
    django_mysql = DjangoORM(mysql_conn)
    django_mysql.save("user")
    django_mysql.find(1)
    
    print("\n---")
    
    # 创建Django ORM，使用PostgreSQL连接
    django_postgres = DjangoORM(postgres_conn)
    django_postgres.save("product")
    django_postgres.find(2)
    
    print("\n---")
    
    # 创建SQLAlchemy ORM，使用MySQL连接
    sqlalchemy_mysql = SQLAlchemyORM(mysql_conn)
    sqlalchemy_mysql.save("order")
    sqlalchemy_mysql.find(3)


if __name__ == "__main__":
    test_bridge_pattern()
    test_database_bridge()
    
    print("\n=== 桥接模式总结 ===")
    print("优点：")
    print("- 分离抽象和实现，提高系统灵活性")
    print("- 符合开闭原则，可以独立扩展抽象和实现")
    print("- 实现细节对客户透明")
    print("\n适用场景：")
    print("- 不希望抽象和实现之间有固定的绑定关系")
    print("- 抽象和实现都可以通过子类化来扩展")
    print("- 对抽象的实现部分的修改应对客户不产生影响")
    print("- 想在多个对象间共享实现，但同时要求客户代码不知道这一点")
