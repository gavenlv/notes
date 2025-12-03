"""
代理模式 (Proxy Pattern) 示例代码

代理模式为其他对象提供一种代理以控制对这个对象的访问。
"""

from abc import ABC, abstractmethod
import time


class Subject(ABC):
    """抽象主题接口"""
    
    @abstractmethod
    def request(self):
        pass


class RealSubject(Subject):
    """真实主题类"""
    
    def request(self):
        print("真实主题: 处理请求")
        # 模拟耗时操作
        time.sleep(1)
        return "处理结果"


class Proxy(Subject):
    """代理类"""
    
    def __init__(self):
        self._real_subject = None
        self._cache = None
        self._cache_time = 0
        self._cache_ttl = 5  # 缓存5秒
    
    def request(self):
        """代理请求，包含访问控制、缓存等功能"""
        
        # 访问控制
        if not self._check_access():
            return "访问被拒绝"
        
        # 缓存检查
        current_time = time.time()
        if (self._cache is not None and 
            current_time - self._cache_time < self._cache_ttl):
            print("代理: 从缓存返回结果")
            return self._cache
        
        # 懒加载真实主题
        if self._real_subject is None:
            print("代理: 创建真实主题")
            self._real_subject = RealSubject()
        
        # 调用真实主题
        print("代理: 转发请求到真实主题")
        result = self._real_subject.request()
        
        # 缓存结果
        self._cache = result
        self._cache_time = current_time
        
        # 日志记录
        self._log_access()
        
        return result
    
    def _check_access(self):
        """检查访问权限"""
        # 模拟权限检查
        print("代理: 检查访问权限")
        return True
    
    def _log_access(self):
        """记录访问日志"""
        print("代理: 记录访问日志")


# 测试基础代理模式
def test_basic_proxy():
    """测试基础代理模式"""
    print("=== 代理模式测试 - 基础示例 ===\n")
    
    proxy = Proxy()
    
    # 第一次请求（会创建真实主题）
    print("第一次请求:")
    result1 = proxy.request()
    print(f"结果: {result1}\n")
    
    # 第二次请求（使用缓存）
    print("第二次请求（5秒内）:")
    result2 = proxy.request()
    print(f"结果: {result2}\n")
    
    # 第三次请求（缓存过期后）
    print("等待6秒让缓存过期...")
    time.sleep(6)
    print("第三次请求（缓存过期后）:")
    result3 = proxy.request()
    print(f"结果: {result3}")


# 实际应用示例：虚拟代理（图片加载）
def test_virtual_proxy():
    """测试虚拟代理模式"""
    print("\n=== 代理模式应用 - 虚拟代理（图片加载）示例 ===\n")
    
    class Image:
        """图片接口"""
        
        def display(self):
            pass
    
    class RealImage(Image):
        """真实图片类"""
        
        def __init__(self, filename):
            self._filename = filename
            self._load_from_disk()
        
        def _load_from_disk(self):
            print(f"真实图片: 从磁盘加载图片 {self._filename}")
            time.sleep(2)  # 模拟加载耗时
            print(f"真实图片: 图片 {self._filename} 加载完成")
        
        def display(self):
            print(f"真实图片: 显示图片 {self._filename}")
    
    class ImageProxy(Image):
        """图片代理类"""
        
        def __init__(self, filename):
            self._filename = filename
            self._real_image = None
        
        def display(self):
            if self._real_image is None:
                print("图片代理: 创建真实图片（延迟加载）")
                self._real_image = RealImage(self._filename)
            
            print("图片代理: 转发显示请求")
            self._real_image.display()
    
    # 测试虚拟代理
    print("创建图片代理（不会立即加载图片）:")
    image_proxy = ImageProxy("photo.jpg")
    
    print("\n第一次显示图片（会触发加载）:")
    image_proxy.display()
    
    print("\n第二次显示图片（使用已加载的图片）:")
    image_proxy.display()


# 实际应用示例：保护代理（权限控制）
def test_protection_proxy():
    """测试保护代理模式"""
    print("\n=== 代理模式应用 - 保护代理（权限控制）示例 ===\n")
    
    class Database:
        """数据库接口"""
        
        def query(self, sql):
            pass
        
        def update(self, sql):
            pass
        
        def delete(self, sql):
            pass
    
    class RealDatabase(Database):
        """真实数据库类"""
        
        def query(self, sql):
            print(f"真实数据库: 执行查询: {sql}")
            return f"查询结果: {sql}"
        
        def update(self, sql):
            print(f"真实数据库: 执行更新: {sql}")
            return f"更新结果: {sql}"
        
        def delete(self, sql):
            print(f"真实数据库: 执行删除: {sql}")
            return f"删除结果: {sql}"
    
    class User:
        """用户类"""
        
        def __init__(self, username, role):
            self.username = username
            self.role = role  # 'admin', 'user', 'guest'
    
    class DatabaseProxy(Database):
        """数据库保护代理"""
        
        def __init__(self, user: User):
            self._user = user
            self._real_database = RealDatabase()
        
        def query(self, sql):
            # 所有用户都可以查询
            print(f"数据库代理: 用户 {self._user.username} 请求查询")
            return self._real_database.query(sql)
        
        def update(self, sql):
            # 只有管理员和普通用户可以更新
            if self._user.role in ['admin', 'user']:
                print(f"数据库代理: 用户 {self._user.username} 请求更新")
                return self._real_database.update(sql)
            else:
                print(f"数据库代理: 用户 {self._user.username} 没有更新权限")
                return "权限不足"
        
        def delete(self, sql):
            # 只有管理员可以删除
            if self._user.role == 'admin':
                print(f"数据库代理: 用户 {self._user.username} 请求删除")
                return self._real_database.delete(sql)
            else:
                print(f"数据库代理: 用户 {self._user.username} 没有删除权限")
                return "权限不足"
    
    # 测试保护代理
    admin = User("admin", "admin")
    user = User("user", "user") 
    guest = User("guest", "guest")
    
    print("管理员操作:")
    admin_db = DatabaseProxy(admin)
    print(admin_db.query("SELECT * FROM users"))
    print(admin_db.update("UPDATE users SET name='John'"))
    print(admin_db.delete("DELETE FROM users WHERE id=1"))
    
    print("\n普通用户操作:")
    user_db = DatabaseProxy(user)
    print(user_db.query("SELECT * FROM products"))
    print(user_db.update("UPDATE products SET price=100"))
    print(user_db.delete("DELETE FROM products WHERE id=1"))
    
    print("\n访客操作:")
    guest_db = DatabaseProxy(guest)
    print(guest_db.query("SELECT * FROM categories"))
    print(guest_db.update("UPDATE categories SET name='New'"))
    print(guest_db.delete("DELETE FROM categories WHERE id=1"))


# 实际应用示例：远程代理（网络服务）
def test_remote_proxy():
    """测试远程代理模式"""
    print("\n=== 代理模式应用 - 远程代理（网络服务）示例 ===\n")
    
    class BankService:
        """银行服务接口"""
        
        def get_balance(self, account_id):
            pass
        
        def transfer(self, from_account, to_account, amount):
            pass
    
    class RemoteBankService(BankService):
        """远程银行服务（模拟）"""
        
        def __init__(self, server_address):
            self._server_address = server_address
            print(f"远程银行服务: 连接到服务器 {server_address}")
        
        def get_balance(self, account_id):
            print(f"远程银行服务: 从服务器获取账户 {account_id} 余额")
            # 模拟网络延迟
            time.sleep(1)
            return 1000.0  # 模拟余额
        
        def transfer(self, from_account, to_account, amount):
            print(f"远程银行服务: 在服务器执行转账 {from_account} -> {to_account}, 金额: {amount}")
            # 模拟网络延迟
            time.sleep(2)
            return True  # 模拟成功
    
    class BankServiceProxy(BankService):
        """银行服务代理（本地缓存）"""
        
        def __init__(self, server_address):
            self._server_address = server_address
            self._remote_service = None
            self._balance_cache = {}
            self._cache_ttl = 30  # 缓存30秒
            self._last_access = {}
        
        def _get_remote_service(self):
            """获取远程服务（懒加载）"""
            if self._remote_service is None:
                print("银行服务代理: 创建远程服务连接")
                self._remote_service = RemoteBankService(self._server_address)
            return self._remote_service
        
        def get_balance(self, account_id):
            """获取余额（带缓存）"""
            current_time = time.time()
            
            # 检查缓存
            if (account_id in self._balance_cache and 
                account_id in self._last_access and
                current_time - self._last_access[account_id] < self._cache_ttl):
                print(f"银行服务代理: 从缓存获取账户 {account_id} 余额")
                return self._balance_cache[account_id]
            
            # 从远程服务获取
            print(f"银行服务代理: 从远程服务获取账户 {account_id} 余额")
            remote_service = self._get_remote_service()
            balance = remote_service.get_balance(account_id)
            
            # 更新缓存
            self._balance_cache[account_id] = balance
            self._last_access[account_id] = current_time
            
            return balance
        
        def transfer(self, from_account, to_account, amount):
            """执行转账（无缓存）"""
            print(f"银行服务代理: 通过远程服务执行转账")
            remote_service = self._get_remote_service()
            
            # 清除相关缓存（因为余额可能变化）
            if from_account in self._balance_cache:
                del self._balance_cache[from_account]
            if to_account in self._balance_cache:
                del self._balance_cache[to_account]
            
            return remote_service.transfer(from_account, to_account, amount)
    
    # 测试远程代理
    bank_proxy = BankServiceProxy("bank.example.com:8080")
    
    print("第一次获取余额（会连接远程服务）:")
    balance1 = bank_proxy.get_balance("12345")
    print(f"余额: {balance1}\n")
    
    print("第二次获取余额（使用缓存）:")
    balance2 = bank_proxy.get_balance("12345")
    print(f"余额: {balance2}\n")
    
    print("执行转账（会清除缓存）:")
    result = bank_proxy.transfer("12345", "67890", 100)
    print(f"转账结果: {result}\n")
    
    print("转账后获取余额（缓存已清除，重新获取）:")
    balance3 = bank_proxy.get_balance("12345")
    print(f"余额: {balance3}")


# Python属性代理示例
def test_python_property_proxy():
    """测试Python属性代理"""
    print("\n=== Python属性代理示例 ===\n")
    
    class LazyProperty:
        """惰性属性代理"""
        
        def __init__(self, func):
            self._func = func
            self._value = None
            self._computed = False
        
        def __get__(self, instance, owner):
            if not self._computed:
                print(f"惰性属性: 计算属性值")
                self._value = self._func(instance)
                self._computed = True
            else:
                print(f"惰性属性: 使用缓存值")
            return self._value
    
    class Person:
        """人员类"""
        
        def __init__(self, name, age):
            self.name = name
            self.age = age
        
        @LazyProperty
        def birth_year(self):
            """出生年份（惰性计算）"""
            import datetime
            current_year = datetime.datetime.now().year
            return current_year - self.age
        
        @LazyProperty
        def description(self):
            """描述信息（惰性计算）"""
            return f"{self.name}, {self.age}岁, 出生于{self.birth_year}年"
    
    # 测试惰性属性
    person = Person("张三", 30)
    
    print("第一次访问出生年份:")
    print(f"出生年份: {person.birth_year}\n")
    
    print("第二次访问出生年份（使用缓存）:")
    print(f"出生年份: {person.birth_year}\n")
    
    print("第一次访问描述信息:")
    print(f"描述: {person.description}\n")
    
    print("第二次访问描述信息（使用缓存）:")
    print(f"描述: {person.description}")


if __name__ == "__main__":
    test_basic_proxy()
    test_virtual_proxy()
    test_protection_proxy()
    test_remote_proxy()
    test_python_property_proxy()
    
    print("\n=== 代理模式总结 ===")
    print("优点：")
    print("- 代理模式在客户端与目标对象之间起到一个中介作用和保护目标对象的作用")
    print("- 代理对象可以扩展目标对象的功能")
    print("- 代理模式能将客户端与目标对象分离，在一定程度上降低了系统的耦合度")
    print("\n缺点：")
    print("- 在客户端和目标对象之间增加一个代理对象，会造成请求处理速度变慢")
    print("- 增加了系统的复杂度")
    print("\n适用场景：")
    print("- 远程代理：为一个对象在不同的地址空间提供局部代表")
    print("- 虚拟代理：需要创建开销很大的对象时")
    print("- 安全代理：控制对原始对象的访问")
    print("- 智能指引：取代简单的指针，提供对对象访问时的附加操作")
