"""
装饰器模式 (Decorator Pattern) 示例代码

装饰器模式动态地给一个对象添加一些额外的职责。就增加功能来说，装饰器模式相比生成子类更为灵活。
"""

from abc import ABC, abstractmethod


class Coffee(ABC):
    """咖啡抽象类"""
    
    @abstractmethod
    def get_description(self):
        """获取咖啡描述"""
        pass
    
    @abstractmethod
    def get_cost(self):
        """获取咖啡价格"""
        pass


class SimpleCoffee(Coffee):
    """简单咖啡（具体组件）"""
    
    def get_description(self):
        return "简单咖啡"
    
    def get_cost(self):
        return 5.0


class CoffeeDecorator(Coffee):
    """咖啡装饰器抽象类"""
    
    def __init__(self, coffee: Coffee):
        self._coffee = coffee
    
    def get_description(self):
        return self._coffee.get_description()
    
    def get_cost(self):
        return self._coffee.get_cost()


class MilkDecorator(CoffeeDecorator):
    """牛奶装饰器"""
    
    def get_description(self):
        return self._coffee.get_description() + ", 牛奶"
    
    def get_cost(self):
        return self._coffee.get_cost() + 1.5


class SugarDecorator(CoffeeDecorator):
    """糖装饰器"""
    
    def get_description(self):
        return self._coffee.get_description() + ", 糖"
    
    def get_cost(self):
        return self._coffee.get_cost() + 0.5


class WhippedCreamDecorator(CoffeeDecorator):
    """奶油装饰器"""
    
    def get_description(self):
        return self._coffee.get_description() + ", 奶油"
    
    def get_cost(self):
        return self._coffee.get_cost() + 2.0


class VanillaDecorator(CoffeeDecorator):
    """香草装饰器"""
    
    def get_description(self):
        return self._coffee.get_description() + ", 香草"
    
    def get_cost(self):
        return self._coffee.get_cost() + 1.0


# 测试装饰器模式
def test_coffee_decorator():
    """测试咖啡装饰器模式"""
    print("=== 装饰器模式测试 - 咖啡店示例 ===\n")
    
    # 简单咖啡
    coffee = SimpleCoffee()
    print(f"咖啡: {coffee.get_description()}")
    print(f"价格: ${coffee.get_cost():.2f}")
    
    print("\n---")
    
    # 加牛奶和糖的咖啡
    coffee_with_milk_and_sugar = SugarDecorator(MilkDecorator(SimpleCoffee()))
    print(f"咖啡: {coffee_with_milk_and_sugar.get_description()}")
    print(f"价格: ${coffee_with_milk_and_sugar.get_cost():.2f}")
    
    print("\n---")
    
    # 豪华咖啡（加牛奶、糖、奶油、香草）
    luxury_coffee = VanillaDecorator(
        WhippedCreamDecorator(
            SugarDecorator(
                MilkDecorator(SimpleCoffee())
            )
        )
    )
    print(f"咖啡: {luxury_coffee.get_description()}")
    print(f"价格: ${luxury_coffee.get_cost():.2f}")
    
    print("\n---")
    
    # 只加奶油的咖啡
    cream_coffee = WhippedCreamDecorator(SimpleCoffee())
    print(f"咖啡: {cream_coffee.get_description()}")
    print(f"价格: ${cream_coffee.get_cost():.2f}")


# 实际应用示例：文本格式化
def test_text_formatting_decorator():
    """测试文本格式化装饰器"""
    print("\n=== 装饰器模式应用 - 文本格式化示例 ===\n")
    
    class TextComponent(ABC):
        """文本组件抽象类"""
        
        @abstractmethod
        def render(self):
            pass
    
    class PlainText(TextComponent):
        """纯文本（具体组件）"""
        
        def __init__(self, content):
            self._content = content
        
        def render(self):
            return self._content
    
    class TextDecorator(TextComponent):
        """文本装饰器抽象类"""
        
        def __init__(self, text_component: TextComponent):
            self._text_component = text_component
        
        def render(self):
            return self._text_component.render()
    
    class BoldDecorator(TextDecorator):
        """粗体装饰器"""
        
        def render(self):
            return f"**{self._text_component.render()}**"
    
    class ItalicDecorator(TextDecorator):
        """斜体装饰器"""
        
        def render(self):
            return f"*{self._text_component.render()}*"
    
    class UnderlineDecorator(TextDecorator):
        """下划线装饰器"""
        
        def render(self):
            return f"<u>{self._text_component.render()}</u>"
    
    class ColorDecorator(TextDecorator):
        """颜色装饰器"""
        
        def __init__(self, text_component: TextComponent, color):
            super().__init__(text_component)
            self._color = color
        
        def render(self):
            return f"<span style='color:{self._color}'>{self._text_component.render()}</span>"
    
    # 测试文本格式化
    text = PlainText("Hello, World!")
    print(f"原始文本: {text.render()}")
    
    bold_text = BoldDecorator(text)
    print(f"粗体文本: {bold_text.render()}")
    
    italic_bold_text = ItalicDecorator(bold_text)
    print(f"斜体粗体文本: {italic_bold_text.render()}")
    
    underlined_italic_bold_text = UnderlineDecorator(italic_bold_text)
    print(f"下划线斜体粗体文本: {underlined_italic_bold_text.render()}")
    
    colored_underlined_italic_bold_text = ColorDecorator(underlined_italic_bold_text, "red")
    print(f"红色下划线斜体粗体文本: {colored_underlined_italic_bold_text.render()}")


# 实际应用示例：数据压缩和加密
def test_data_processing_decorator():
    """测试数据处理装饰器"""
    print("\n=== 装饰器模式应用 - 数据处理示例 ===\n")
    
    class DataSource(ABC):
        """数据源抽象类"""
        
        @abstractmethod
        def write_data(self, data):
            pass
        
        @abstractmethod
        def read_data(self):
            pass
    
    class FileDataSource(DataSource):
        """文件数据源（具体组件）"""
        
        def __init__(self, filename):
            self._filename = filename
            self._data = None
        
        def write_data(self, data):
            self._data = data
            print(f"写入数据到文件 {self._filename}: {data}")
        
        def read_data(self):
            print(f"从文件 {self._filename} 读取数据: {self._data}")
            return self._data
    
    class DataSourceDecorator(DataSource):
        """数据源装饰器抽象类"""
        
        def __init__(self, data_source: DataSource):
            self._data_source = data_source
        
        def write_data(self, data):
            self._data_source.write_data(data)
        
        def read_data(self):
            return self._data_source.read_data()
    
    class EncryptionDecorator(DataSourceDecorator):
        """加密装饰器"""
        
        def write_data(self, data):
            encrypted_data = f"[ENCRYPTED]{data}[ENCRYPTED]"
            self._data_source.write_data(encrypted_data)
        
        def read_data(self):
            data = self._data_source.read_data()
            if data and data.startswith("[ENCRYPTED]") and data.endswith("[ENCRYPTED]"):
                return data[11:-11]  # 移除加密标记
            return data
    
    class CompressionDecorator(DataSourceDecorator):
        """压缩装饰器"""
        
        def write_data(self, data):
            compressed_data = f"[COMPRESSED]{data}[COMPRESSED]"
            self._data_source.write_data(compressed_data)
        
        def read_data(self):
            data = self._data_source.read_data()
            if data and data.startswith("[COMPRESSED]") and data.endswith("[COMPRESSED]"):
                return data[12:-12]  # 移除压缩标记
            return data
    
    # 测试数据处理
    print("1. 普通文件写入:")
    file_source = FileDataSource("data.txt")
    file_source.write_data("Hello World")
    file_source.read_data()
    
    print("\n2. 加密文件写入:")
    encrypted_source = EncryptionDecorator(FileDataSource("encrypted.txt"))
    encrypted_source.write_data("Secret Message")
    encrypted_source.read_data()
    
    print("\n3. 压缩文件写入:")
    compressed_source = CompressionDecorator(FileDataSource("compressed.txt"))
    compressed_source.write_data("Large Data Content")
    compressed_source.read_data()
    
    print("\n4. 压缩并加密文件写入:")
    encrypted_compressed_source = EncryptionDecorator(
        CompressionDecorator(FileDataSource("secure.txt"))
    )
    encrypted_compressed_source.write_data("Very Important Data")
    encrypted_compressed_source.read_data()


# Python装饰器语法示例
def test_python_decorator_syntax():
    """测试Python装饰器语法"""
    print("\n=== Python装饰器语法示例 ===\n")
    
    def timer_decorator(func):
        """计时装饰器"""
        import time
        
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            print(f"函数 {func.__name__} 执行时间: {end_time - start_time:.4f}秒")
            return result
        return wrapper
    
    def cache_decorator(func):
        """缓存装饰器"""
        cache = {}
        
        def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            if key in cache:
                print(f"从缓存中获取 {func.__name__} 的结果")
                return cache[key]
            result = func(*args, **kwargs)
            cache[key] = result
            print(f"计算 {func.__name__} 的结果并缓存")
            return result
        return wrapper
    
    def log_decorator(func):
        """日志装饰器"""
        def wrapper(*args, **kwargs):
            print(f"调用函数: {func.__name__}, 参数: {args}, {kwargs}")
            result = func(*args, **kwargs)
            print(f"函数 {func.__name__} 执行完成，结果: {result}")
            return result
        return wrapper
    
    # 使用装饰器
    @log_decorator
    @timer_decorator
    @cache_decorator
    def fibonacci(n):
        """计算斐波那契数列"""
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)
    
    # 测试装饰器
    print("计算斐波那契数列（带装饰器）:")
    result = fibonacci(5)
    print(f"fibonacci(5) = {result}")
    
    print("\n再次计算（应该从缓存获取）:")
    result2 = fibonacci(5)
    print(f"fibonacci(5) = {result2}")


if __name__ == "__main__":
    test_coffee_decorator()
    test_text_formatting_decorator()
    test_data_processing_decorator()
    test_python_decorator_syntax()
    
    print("\n=== 装饰器模式总结 ===")
    print("优点：")
    print("- 比继承更灵活，可以动态地给对象添加功能")
    print("- 可以避免在层次结构高层的类有太多的特征")
    print("- 装饰器类和被装饰的类可以独立发展，不会相互耦合")
    print("\n缺点：")
    print("- 会产生很多小对象，增加了系统的复杂性")
    print("- 排错困难，调试时可能需要逐级排查")
    print("\n适用场景：")
    print("- 在不影响其他对象的情况下，以动态、透明的方式给单个对象添加职责")
    print("- 处理那些可以撤销的职责")
    print("- 当不能采用生成子类的方法进行扩充时")
