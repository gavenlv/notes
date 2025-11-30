"""
第6章：适配器模式 - 示例代码

本文件包含了第6章中提到的所有示例代码，用于演示适配器模式的各种实现方式和应用场景。
"""

print("=== 适配器模式示例 ===\n")

# 1. 对象适配器
print("1. 对象适配器示例:")

# 目标接口
class Target:
    def request(self):
        return "目标接口的标准请求"

# 适配者
class Adaptee:
    def specific_request(self):
        return "适配者的特殊请求"

# 适配器
class Adapter(Target):
    def __init__(self, adaptee):
        self._adaptee = adaptee
    
    def request(self):
        # 调用适配者的方法，并转换格式
        return f"适配器转换: {self._adaptee.specific_request()}"

# 客户端代码
def client_code(target):
    print(f"客户端收到: {target.request()}")

# 使用示例
adaptee = Adaptee()
adapter = Adapter(adaptee)
client_code(adapter)  # 输出: 客户端收到: 适配器转换: 适配者的特殊请求

# 2. 类适配器
print("\n2. 类适配器示例:")

from abc import ABC, abstractmethod

# 目标接口
class TargetInterface(ABC):
    @abstractmethod
    def request(self):
        pass

# 适配者
class AdapteeClass:
    def specific_request(self):
        return "适配者的特殊请求"

# 适配器
class AdapterClass(AdapteeClass, TargetInterface):
    def request(self):
        # 调用父类的特定方法
        return f"适配器转换: {self.specific_request()}"

# 使用示例
adapter = AdapterClass()
client_code(adapter)  # 输出: 客户端收到: 适配器转换: 适配者的特殊请求

# 3. 第三方库接口适配
print("\n3. 第三方库接口适配示例:")

# 第三方邮件服务
class ThirdPartyEmailService:
    def send_email(self, to, subject, body):
        print(f"第三方邮件服务: 发送邮件到 {to}")
        print(f"主题: {subject}")
        print(f"内容: {body}")
        return True

# 我们系统中的邮件接口
class EmailService(ABC):
    @abstractmethod
    def send_message(self, recipient, title, content):
        pass

# 适配器
class EmailServiceAdapter(EmailService):
    def __init__(self, third_party_service):
        self._service = third_party_service
    
    def send_message(self, recipient, title, content):
        # 将我们的接口调用转换为第三方服务的接口调用
        return self._service.send_email(recipient, title, content)

# 客户端代码
class NotificationSystem:
    def __init__(self, email_service):
        self._email_service = email_service
    
    def send_welcome_email(self, user_email, user_name):
        subject = f"欢迎 {user_name}"
        content = f"亲爱的 {user_name}，欢迎使用我们的系统！"
        return self._email_service.send_message(user_email, subject, content)

# 使用示例
third_party_service = ThirdPartyEmailService()
email_service = EmailServiceAdapter(third_party_service)
notification_system = NotificationSystem(email_service)

result = notification_system.send_welcome_email("user@example.com", "张三")
print(f"邮件发送结果: {result}")

# 4. 不同数据格式适配
print("\n4. 不同数据格式适配示例:")

# XML数据处理器
class XMLDataProcessor:
    def process_xml_data(self, xml_data):
        # 模拟XML解析
        data = {
            "name": self._extract_tag(xml_data, "name"),
            "age": int(self._extract_tag(xml_data, "age")),
            "email": self._extract_tag(xml_data, "email")
        }
        print(f"XML处理器处理数据: {data}")
        return data
    
    def _extract_tag(self, xml, tag):
        # 简化的XML解析
        start = xml.find(f"<{tag}>") + len(f"<{tag}>")
        end = xml.find(f"</{tag}>")
        return xml[start:end]

# JSON数据处理器
class JSONDataProcessor:
    def process_json_data(self, json_data):
        import json
        data = json.loads(json_data)
        print(f"JSON处理器处理数据: {data}")
        return data

# 我们系统中的标准数据处理器接口
class StandardDataProcessor(ABC):
    @abstractmethod
    def process_data(self, data):
        pass

# XML适配器
class XMLDataProcessorAdapter(StandardDataProcessor):
    def __init__(self, xml_processor):
        self._processor = xml_processor
    
    def process_data(self, data):
        # 假设传入的是XML数据
        return self._processor.process_xml_data(data)

# JSON适配器
class JSONDataProcessorAdapter(StandardDataProcessor):
    def __init__(self, json_processor):
        self._processor = json_processor
    
    def process_data(self, data):
        # 假设传入的是JSON数据
        return self._processor.process_json_data(data)

# 客户端代码
class DataAnalysisSystem:
    def __init__(self, data_processor):
        self._processor = data_processor
    
    def analyze_data(self, data):
        processed_data = self._processor.process_data(data)
        print(f"数据分析系统分析后的数据: {processed_data}")
        return processed_data

# XML数据
xml_data = """
<person>
    <name>李四</name>
    <age>28</age>
    <email>lisi@example.com</email>
</person>
"""

# JSON数据
json_data = """
{
    "name": "王五",
    "age": 32,
    "email": "wangwu@example.com"
}
"""

# 使用XML处理器
xml_processor = XMLDataProcessor()
xml_adapter = XMLDataProcessorAdapter(xml_processor)
xml_analysis_system = DataAnalysisSystem(xml_adapter)
xml_analysis_system.analyze_data(xml_data)

# 使用JSON处理器
json_processor = JSONDataProcessor()
json_adapter = JSONDataProcessorAdapter(json_processor)
json_analysis_system = DataAnalysisSystem(json_adapter)
json_analysis_system.analyze_data(json_data)

# 5. 多媒体播放器适配
print("\n5. 多媒体播放器适配示例:")

# 现有的高级媒体播放器接口
class AdvancedMediaPlayer(ABC):
    @abstractmethod
    def play_vlc(self, file_name):
        pass
    
    @abstractmethod
    def play_mp4(self, file_name):
        pass

# VLC播放器实现
class VlcPlayer(AdvancedMediaPlayer):
    def play_vlc(self, file_name):
        print(f"正在播放VLC文件: {file_name}")
    
    def play_mp4(self, file_name):
        # VLC不支持MP4
        pass

# MP4播放器实现
class Mp4Player(AdvancedMediaPlayer):
    def play_vlc(self, file_name):
        # MP4不支持VLC
        pass
    
    def play_mp4(self, file_name):
        print(f"正在播放MP4文件: {file_name}")

# 媒体播放器接口（客户端期望的接口）
class MediaPlayer(ABC):
    @abstractmethod
    def play(self, audio_type, file_name):
        pass

# 适配器
class MediaAdapter(MediaPlayer):
    def __init__(self):
        self._vlc_player = VlcPlayer()
        self._mp4_player = Mp4Player()
    
    def play(self, audio_type, file_name):
        if audio_type.lower() == "vlc":
            self._vlc_player.play_vlc(file_name)
        elif audio_type.lower() == "mp4":
            self._mp4_player.play_mp4(file_name)
        else:
            print(f"不支持的媒体格式: {audio_type}")

# 实际的媒体播放器实现
class AudioPlayer(MediaPlayer):
    def __init__(self):
        self._media_adapter = MediaAdapter()
    
    def play(self, audio_type, file_name):
        # 内置支持MP3
        if audio_type.lower() == "mp3":
            print(f"正在播放MP3文件: {file_name}")
        # 其他格式使用适配器
        elif audio_type.lower() in ["vlc", "mp4"]:
            self._media_adapter.play(audio_type, file_name)
        else:
            print(f"不支持的媒体格式: {audio_type}")

# 使用示例
player = AudioPlayer()
player.play("mp3", "song.mp3")
player.play("mp4", "movie.mp4")
player.play("vlc", "video.vlc")
player.play("avi", "movie.avi")  # 不支持的格式

# 6. 双向适配器
print("\n6. 双向适配器示例:")

# 接口A
class InterfaceA:
    def method_a(self):
        return "接口A的方法"

# 接口B
class InterfaceB:
    def method_b(self):
        return "接口B的方法"

# 双向适配器
class BidirectionalAdapter(InterfaceA, InterfaceB):
    def __init__(self):
        self._interface_a = InterfaceA()
        self._interface_b = InterfaceB()
    
    def method_a(self):
        return f"适配器转换: {self._interface_b.method_b()}"
    
    def method_b(self):
        return f"适配器转换: {self._interface_a.method_a()}"

# 使用示例
adapter = BidirectionalAdapter()
print(f"调用method_a: {adapter.method_a()}")  # 实际调用接口B的方法
print(f"调用method_b: {adapter.method_b()}")  # 实际调用接口A的方法

# 7. 默认适配器
print("\n7. 默认适配器示例:")

# 复杂接口
class ComplexInterface(ABC):
    @abstractmethod
    def method1(self):
        pass
    
    @abstractmethod
    def method2(self):
        pass
    
    @abstractmethod
    def method3(self):
        pass
    
    @abstractmethod
    def method4(self):
        pass

# 默认适配器
class DefaultAdapter(ComplexInterface):
    def method1(self):
        print("默认实现: method1")
    
    def method2(self):
        print("默认实现: method2")
    
    def method3(self):
        print("默认实现: method3")
    
    def method4(self):
        print("默认实现: method4")

# 客户端只需重写感兴趣的方法
class ClientImplementation(DefaultAdapter):
    def method2(self):
        print("客户端重写: method2")
    
    def method4(self):
        print("客户端重写: method4")

# 使用示例
client = ClientImplementation()
client.method1()  # 使用默认实现
client.method2()  # 使用客户端实现
client.method3()  # 使用默认实现
client.method4()  # 使用客户端实现

# 8. Python鸭子类型适配
print("\n8. Python鸭子类型适配示例:")

# 适配者
class LegacySystem:
    def legacy_method(self, data):
        return f"遗留系统处理: {data}"

# 适配器（不需要显式实现接口）
class DuckTypeAdapter:
    def __init__(self, legacy_system):
        self._legacy = legacy_system
    
    # 提供新的方法名
    def new_method(self, data):
        return self._legacy.legacy_method(data)

# 客户端
def duck_type_client_code(adapter, data):
    # 由于鸭子类型，只需要确保对象有所需的方法即可
    return adapter.new_method(data)

# 使用示例
legacy = LegacySystem()
adapter = DuckTypeAdapter(legacy)
result = duck_type_client_code(adapter, "测试数据")
print(result)

# 9. 动态适配器
print("\n9. 动态适配器示例:")

# 动态适配器
def create_adapter(adaptee, target_methods):
    class DynamicAdapter:
        def __init__(self, adaptee_obj):
            self._adaptee = adaptee_obj
        
        def __getattr__(self, name):
            if name in target_methods:
                return getattr(self._adaptee, target_methods[name])
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
    return DynamicAdapter(adaptee)

class Source:
    def method_a(self):
        return "源方法A"
    
    def method_b(self):
        return "源方法B"

# 定义方法映射
method_mapping = {
    "new_method_x": "method_a",
    "new_method_y": "method_b"
}

source = Source()
dynamic_adapter = create_adapter(source, method_mapping)
print(f"调用new_method_x: {dynamic_adapter.new_method_x()}")
print(f"调用new_method_y: {dynamic_adapter.new_method_y()}")

# 10. 实际应用 - 支付系统适配
print("\n10. 实际应用 - 支付系统适配示例:")

# 不同支付网关的接口
class AlipayGateway:
    def pay_with_alipay(self, amount, order_id):
        print(f"支付宝支付: 金额 {amount}, 订单ID {order_id}")
        return {"status": "success", "gateway": "alipay"}

class WechatGateway:
    def wechat_pay(self, amount, order_id):
        print(f"微信支付: 金额 {amount}, 订单ID {order_id}")
        return {"status": "success", "gateway": "wechat"}

# 统一支付接口
class PaymentProcessor(ABC):
    @abstractmethod
    def process_payment(self, amount, order_info):
        pass

# 支付宝适配器
class AlipayAdapter(PaymentProcessor):
    def __init__(self, gateway):
        self._gateway = gateway
    
    def process_payment(self, amount, order_info):
        order_id = order_info.get("order_id")
        return self._gateway.pay_with_alipay(amount, order_id)

# 微信适配器
class WechatAdapter(PaymentProcessor):
    def __init__(self, gateway):
        self._gateway = gateway
    
    def process_payment(self, amount, order_info):
        order_id = order_info.get("order_id")
        return self._gateway.wechat_pay(amount, order_id)

# 支付服务
class PaymentService:
    def __init__(self, processor):
        self._processor = processor
    
    def make_payment(self, amount, order_info):
        result = self._processor.process_payment(amount, order_info)
        print(f"支付结果: {result}")
        return result

# 使用示例
alipay_gateway = AlipayGateway()
alipay_adapter = AlipayAdapter(alipay_gateway)
alipay_service = PaymentService(alipay_adapter)
alipay_service.make_payment(100, {"order_id": "ALI001", "user_id": "user123"})

wechat_gateway = WechatGateway()
wechat_adapter = WechatAdapter(wechat_gateway)
wechat_service = PaymentService(wechat_adapter)
wechat_service.make_payment(200, {"order_id": "WX001", "user_id": "user456"})

# 总结
print("\n=== 总结 ===")
print("适配器模式将一个类的接口转换成客户希望的另一个接口，使得原本由于接口不兼容而不能一起工作的那些类可以一起工作。")
print("适配器模式的主要优点:")
print("1. 解决了接口不兼容的问题，使原本不相关的类可以协同工作")
print("2. 提高了代码的复用性，可以复用现有的类而不需要修改它们的代码")
print("3. 将客户端与具体的实现解耦，提高了系统的灵活性")
print("\n适配器模式的主要实现方式:")
print("1. 对象适配器：使用组合，更加灵活")
print("2. 类适配器：使用继承，实现更直接")
print("3. 双向适配器：使两个接口相互适配")
print("4. 默认适配器：为复杂接口提供默认实现")
print("\n在Python中，可以利用鸭子类型和动态特性实现更灵活的适配器。")