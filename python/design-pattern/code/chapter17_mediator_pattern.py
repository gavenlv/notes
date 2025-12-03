"""
第17章：中介者模式 (Mediator Pattern)

中介者模式是一种行为设计模式，它通过引入一个中介者对象来减少对象之间的直接依赖，
使对象之间不直接交互，而是通过中介者进行通信。
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class Mediator(ABC):
    """中介者接口"""
    
    @abstractmethod
    def notify(self, sender: object, event: Dict) -> None:
        """通知方法"""
        pass


class Colleague(ABC):
    """同事类基类"""
    
    def __init__(self, mediator: Mediator):
        self._mediator = mediator
    
    def set_mediator(self, mediator: Mediator) -> None:
        """设置中介者"""
        self._mediator = mediator


# 示例1：聊天室系统（中介者模式经典应用）
class ChatRoomMediator(Mediator):
    """聊天室中介者"""
    
    def __init__(self):
        self._users: List[User] = []
        self._message_history: List[str] = []
    
    def register_user(self, user) -> None:
        """注册用户"""
        self._users.append(user)
    
    def notify(self, sender: object, event: Dict) -> None:
        """处理消息通知"""
        if isinstance(sender, User) and 'type' in event:
            if event['type'] == 'message':
                self._handle_message(sender, event)
            elif event['type'] == 'private_message':
                self._handle_private_message(sender, event)
            elif event['type'] == 'user_list':
                self._handle_user_list(sender)
    
    def _handle_message(self, sender, event) -> None:
        """处理公共消息"""
        content = event['content']
        message = f"[{sender.name}]: {content}"
        self._message_history.append(message)
        
        # 广播给所有用户
        for user in self._users:
            if user != sender:
                user.receive_message(message)
    
    def _handle_private_message(self, sender, event) -> None:
        """处理私聊消息"""
        target_name = event['target']
        content = event['content']
        
        for user in self._users:
            if user.name == target_name:
                private_msg = f"[私聊] {sender.name} -> {user.name}: {content}"
                user.receive_message(private_msg)
                break
    
    def _handle_user_list(self, sender) -> None:
        """处理用户列表请求"""
        user_list = [user.name for user in self._users]
        sender.receive_message(f"在线用户: {', '.join(user_list)}")


class User(Colleague):
    """用户类（同事类）"""
    
    def __init__(self, mediator: Mediator, name: str):
        super().__init__(mediator)
        self.name = name
    
    def send(self, content: str) -> None:
        """发送公共消息"""
        self._mediator.notify(self, {
            'type': 'message',
            'content': content
        })
    
    def send_private(self, target: str, content: str) -> None:
        """发送私聊消息"""
        self._mediator.notify(self, {
            'type': 'private_message',
            'target': target,
            'content': content
        })
    
    def request_user_list(self) -> None:
        """请求用户列表"""
        self._mediator.notify(self, {'type': 'user_list'})
    
    def receive_message(self, message: str) -> None:
        """接收消息"""
        print(f"{self.name} 收到消息: {message}")


# 示例2：飞机交通管制系统
class AirTrafficControl(Mediator):
    """空中交通管制中心"""
    
    def __init__(self):
        self._aircrafts: Dict[str, Aircraft] = {}
        self._runways: List[str] = ['Runway1', 'Runway2']
        self._occupied_runways: Dict[str, Aircraft] = {}
    
    def register_aircraft(self, aircraft) -> None:
        """注册飞机"""
        self._aircrafts[aircraft.flight_number] = aircraft
    
    def notify(self, sender: object, event: Dict) -> None:
        """处理飞机请求"""
        if isinstance(sender, Aircraft) and 'type' in event:
            if event['type'] == 'landing_request':
                self._handle_landing_request(sender)
            elif event['type'] == 'takeoff_request':
                self._handle_takeoff_request(sender)
            elif event['type'] == 'position_report':
                self._handle_position_report(sender, event)
    
    def _handle_landing_request(self, aircraft) -> None:
        """处理着陆请求"""
        available_runway = self._get_available_runway()
        if available_runway:
            self._occupied_runways[available_runway] = aircraft
            aircraft.receive_clearance(f"允许着陆，使用跑道 {available_runway}")
            print(f"ATC: 飞机 {aircraft.flight_number} 获准在 {available_runway} 着陆")
        else:
            aircraft.receive_clearance("请等待，所有跑道都在使用中")
            print(f"ATC: 飞机 {aircraft.flight_number} 需要等待跑道")
    
    def _handle_takeoff_request(self, aircraft) -> None:
        """处理起飞请求"""
        available_runway = self._get_available_runway()
        if available_runway:
            self._occupied_runways[available_runway] = aircraft
            aircraft.receive_clearance(f"允许起飞，使用跑道 {available_runway}")
            print(f"ATC: 飞机 {aircraft.flight_number} 获准从 {available_runway} 起飞")
        else:
            aircraft.receive_clearance("请等待，所有跑道都在使用中")
    
    def _handle_position_report(self, aircraft, event) -> None:
        """处理位置报告"""
        altitude = event.get('altitude', 0)
        speed = event.get('speed', 0)
        print(f"ATC: 收到 {aircraft.flight_number} 位置报告 - 高度: {altitude}ft, 速度: {speed}kts")
    
    def _get_available_runway(self) -> Optional[str]:
        """获取可用跑道"""
        for runway in self._runways:
            if runway not in self._occupied_runways:
                return runway
        return None
    
    def release_runway(self, runway: str) -> None:
        """释放跑道"""
        if runway in self._occupied_runways:
            del self._occupied_runways[runway]
            print(f"ATC: 跑道 {runway} 已释放")


class Aircraft(Colleague):
    """飞机类（同事类）"""
    
    def __init__(self, mediator: Mediator, flight_number: str):
        super().__init__(mediator)
        self.flight_number = flight_number
    
    def request_landing(self) -> None:
        """请求着陆"""
        self._mediator.notify(self, {'type': 'landing_request'})
    
    def request_takeoff(self) -> None:
        """请求起飞"""
        self._mediator.notify(self, {'type': 'takeoff_request'})
    
    def report_position(self, altitude: int, speed: int) -> None:
        """报告位置"""
        self._mediator.notify(self, {
            'type': 'position_report',
            'altitude': altitude,
            'speed': speed
        })
    
    def receive_clearance(self, clearance: str) -> None:
        """接收指令"""
        print(f"飞机 {self.flight_number}: 收到指令 - {clearance}")


# 示例3：组件通信系统（UI组件）
class UIMediator(Mediator):
    """UI组件中介者"""
    
    def __init__(self):
        self._components: Dict[str, UIComponent] = {}
    
    def register_component(self, component) -> None:
        """注册组件"""
        self._components[component.name] = component
    
    def notify(self, sender: object, event: Dict) -> None:
        """处理组件事件"""
        if isinstance(sender, UIComponent) and 'type' in event:
            if event['type'] == 'button_click':
                self._handle_button_click(sender, event)
            elif event['type'] == 'text_change':
                self._handle_text_change(sender, event)
            elif event['type'] == 'selection_change':
                self._handle_selection_change(sender, event)
    
    def _handle_button_click(self, sender, event) -> None:
        """处理按钮点击"""
        if sender.name == 'save_button':
            # 保存按钮被点击，更新状态和文本框
            text_field = self._components.get('text_field')
            if text_field:
                text_field.set_text("内容已保存")
        elif sender.name == 'clear_button':
            # 清空按钮被点击
            text_field = self._components.get('text_field')
            if text_field:
                text_field.set_text("")
    
    def _handle_text_change(self, sender, event) -> None:
        """处理文本变化"""
        if sender.name == 'text_field':
            # 文本框内容变化，更新按钮状态
            save_button = self._components.get('save_button')
            clear_button = self._components.get('clear_button')
            text = event.get('text', '')
            
            if save_button:
                save_button.set_enabled(bool(text))
            if clear_button:
                clear_button.set_enabled(bool(text))
    
    def _handle_selection_change(self, sender, event) -> None:
        """处理选择变化"""
        print(f"选择器 {sender.name} 选择了: {event.get('selection', '')}")


class UIComponent(Colleague):
    """UI组件基类"""
    
    def __init__(self, mediator: Mediator, name: str):
        super().__init__(mediator)
        self.name = name
        self._enabled = True
    
    def set_enabled(self, enabled: bool) -> None:
        """设置启用状态"""
        self._enabled = enabled
        print(f"组件 {self.name} 启用状态: {enabled}")


class Button(UIComponent):
    """按钮组件"""
    
    def click(self) -> None:
        """点击按钮"""
        if self._enabled:
            self._mediator.notify(self, {'type': 'button_click'})


class TextField(UIComponent):
    """文本框组件"""
    
    def __init__(self, mediator: Mediator, name: str):
        super().__init__(mediator, name)
        self._text = ""
    
    def set_text(self, text: str) -> None:
        """设置文本"""
        self._text = text
        print(f"文本框 {self.name} 内容: {text}")
    
    def text_changed(self) -> None:
        """文本变化"""
        self._mediator.notify(self, {
            'type': 'text_change',
            'text': self._text
        })


def test_chat_room():
    """测试聊天室系统"""
    print("=== 测试聊天室系统 ===")
    
    chat_room = ChatRoomMediator()
    
    # 创建用户
    alice = User(chat_room, "Alice")
    bob = User(chat_room, "Bob")
    charlie = User(chat_room, "Charlie")
    
    # 注册用户
    chat_room.register_user(alice)
    chat_room.register_user(bob)
    chat_room.register_user(charlie)
    
    # 测试消息发送
    alice.send("大家好！")
    bob.send("你好 Alice！")
    
    # 测试私聊
    alice.send_private("Bob", "这是私聊消息")
    
    # 测试用户列表
    alice.request_user_list()


def test_air_traffic_control():
    """测试空中交通管制系统"""
    print("\n=== 测试空中交通管制系统 ===")
    
    atc = AirTrafficControl()
    
    # 创建飞机
    flight1 = Aircraft(atc, "UA123")
    flight2 = Aircraft(atc, "DL456")
    flight3 = Aircraft(atc, "AA789")
    
    # 注册飞机
    atc.register_aircraft(flight1)
    atc.register_aircraft(flight2)
    atc.register_aircraft(flight3)
    
    # 测试着陆请求
    flight1.request_landing()
    flight2.request_landing()
    flight3.request_landing()  # 应该需要等待
    
    # 测试位置报告
    flight1.report_position(5000, 250)
    
    # 释放跑道后再次测试
    atc.release_runway("Runway1")
    flight3.request_landing()


def test_ui_components():
    """测试UI组件系统"""
    print("\n=== 测试UI组件系统 ===")
    
    ui_mediator = UIMediator()
    
    # 创建组件
    save_button = Button(ui_mediator, "save_button")
    clear_button = Button(ui_mediator, "clear_button")
    text_field = TextField(ui_mediator, "text_field")
    
    # 注册组件
    ui_mediator.register_component(save_button)
    ui_mediator.register_component(clear_button)
    ui_mediator.register_component(text_field)
    
    # 初始状态（按钮应该禁用）
    save_button.set_enabled(False)
    clear_button.set_enabled(False)
    
    # 测试文本变化
    text_field.set_text("Hello World")
    text_field.text_changed()  # 按钮应该启用
    
    # 测试按钮点击
    save_button.click()
    clear_button.click()


if __name__ == "__main__":
    # 运行所有测试
    test_chat_room()
    test_air_traffic_control()
    test_ui_components()
    
    print("\n=== 中介者模式测试完成 ===")
    print("\n中介者模式总结：")
    print("1. 减少对象间的直接耦合")
    print("2. 集中控制逻辑")
    print("3. 简化对象间的通信")
    print("4. 提高系统的可维护性")
    print("5. 适用于复杂交互的系统")