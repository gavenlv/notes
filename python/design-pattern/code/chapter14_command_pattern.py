"""
命令模式 (Command Pattern) 示例代码

命令模式将一个请求封装为一个对象，从而使你可用不同的请求对客户进行参数化，对请求排队或记录请求日志，以及支持可撤销的操作。
"""

from abc import ABC, abstractmethod
from typing import List


class Command(ABC):
    """命令抽象类"""
    
    @abstractmethod
    def execute(self):
        """执行命令"""
        pass
    
    @abstractmethod
    def undo(self):
        """撤销命令"""
        pass


class Receiver:
    """接收者类 - 实际执行操作的对象"""
    
    def action_a(self):
        print("接收者: 执行操作A")
    
    def action_b(self):
        print("接收者: 执行操作B")
    
    def action_c(self):
        print("接收者: 执行操作C")


class ConcreteCommandA(Command):
    """具体命令A"""
    
    def __init__(self, receiver: Receiver):
        self._receiver = receiver
    
    def execute(self):
        self._receiver.action_a()
    
    def undo(self):
        print("撤销操作A")


class ConcreteCommandB(Command):
    """具体命令B"""
    
    def __init__(self, receiver: Receiver):
        self._receiver = receiver
    
    def execute(self):
        self._receiver.action_b()
    
    def undo(self):
        print("撤销操作B")


class ConcreteCommandC(Command):
    """具体命令C"""
    
    def __init__(self, receiver: Receiver):
        self._receiver = receiver
    
    def execute(self):
        self._receiver.action_c()
    
    def undo(self):
        print("撤销操作C")


class Invoker:
    """调用者类 - 负责调用命令"""
    
    def __init__(self):
        self._history: List[Command] = []
    
    def execute_command(self, command: Command):
        """执行命令"""
        command.execute()
        self._history.append(command)
    
    def undo_last_command(self):
        """撤销最后一个命令"""
        if self._history:
            command = self._history.pop()
            command.undo()
        else:
            print("没有可撤销的命令")
    
    def show_history(self):
        """显示命令历史"""
        print(f"命令历史: {len(self._history)} 个命令")
        for i, cmd in enumerate(self._history, 1):
            print(f"  {i}. {cmd.__class__.__name__}")


# 测试基础命令模式
def test_basic_command():
    """测试基础命令模式"""
    print("=== 命令模式测试 - 基础示例 ===\n")
    
    # 创建接收者
    receiver = Receiver()
    
    # 创建命令
    command_a = ConcreteCommandA(receiver)
    command_b = ConcreteCommandB(receiver)
    command_c = ConcreteCommandC(receiver)
    
    # 创建调用者
    invoker = Invoker()
    
    # 执行命令
    print("执行命令A:")
    invoker.execute_command(command_a)
    
    print("\n执行命令B:")
    invoker.execute_command(command_b)
    
    print("\n执行命令C:")
    invoker.execute_command(command_c)
    
    # 显示历史
    print("\n命令历史:")
    invoker.show_history()
    
    # 撤销命令
    print("\n撤销最后一个命令:")
    invoker.undo_last_command()
    
    print("\n再撤销一个命令:")
    invoker.undo_last_command()
    
    print("\n最终命令历史:")
    invoker.show_history()


# 实际应用示例：文本编辑器
def test_text_editor():
    """测试文本编辑器命令模式"""
    print("\n=== 命令模式应用 - 文本编辑器示例 ===\n")
    
    class TextEditor:
        """文本编辑器（接收者）"""
        
        def __init__(self):
            self._text = ""
            self._clipboard = ""
        
        def insert_text(self, text, position):
            """插入文本"""
            if position > len(self._text):
                position = len(self._text)
            self._text = self._text[:position] + text + self._text[position:]
            print(f"插入文本: '{text}' 到位置 {position}")
        
        def delete_text(self, start, length):
            """删除文本"""
            if start >= len(self._text):
                return ""
            deleted = self._text[start:start+length]
            self._text = self._text[:start] + self._text[start+length:]
            print(f"删除文本: 从位置 {start} 删除 {length} 个字符")
            return deleted
        
        def copy_text(self, start, length):
            """复制文本"""
            if start >= len(self._text):
                return ""
            self._clipboard = self._text[start:start+length]
            print(f"复制文本: 从位置 {start} 复制 {length} 个字符到剪贴板")
            return self._clipboard
        
        def paste_text(self, position):
            """粘贴文本"""
            if not self._clipboard:
                return
            self.insert_text(self._clipboard, position)
            print(f"粘贴文本: 从剪贴板粘贴到位置 {position}")
        
        def get_text(self):
            """获取文本"""
            return self._text
        
        def display(self):
            """显示文本"""
            print(f"当前文本: '{self._text}'")
    
    class EditorCommand(ABC):
        """编辑器命令抽象类"""
        
        def __init__(self, editor: TextEditor):
            self._editor = editor
        
        @abstractmethod
        def execute(self):
            pass
        
        @abstractmethod
        def undo(self):
            pass
    
    class InsertCommand(EditorCommand):
        """插入命令"""
        
        def __init__(self, editor: TextEditor, text, position):
            super().__init__(editor)
            self._text = text
            self._position = position
            self._previous_text = ""
        
        def execute(self):
            self._previous_text = self._editor.get_text()
            self._editor.insert_text(self._text, self._position)
        
        def undo(self):
            self._editor._text = self._previous_text
            print(f"撤销插入: 恢复到之前的文本")
    
    class DeleteCommand(EditorCommand):
        """删除命令"""
        
        def __init__(self, editor: TextEditor, start, length):
            super().__init__(editor)
            self._start = start
            self._length = length
            self._deleted_text = ""
            self._previous_text = ""
        
        def execute(self):
            self._previous_text = self._editor.get_text()
            self._deleted_text = self._editor.delete_text(self._start, self._length)
        
        def undo(self):
            self._editor._text = self._previous_text
            print(f"撤销删除: 恢复被删除的文本")
    
    class CopyCommand(EditorCommand):
        """复制命令"""
        
        def __init__(self, editor: TextEditor, start, length):
            super().__init__(editor)
            self._start = start
            self._length = length
        
        def execute(self):
            self._editor.copy_text(self._start, self._length)
        
        def undo(self):
            # 复制操作通常不需要撤销
            print("撤销复制: 清除剪贴板")
            self._editor._clipboard = ""
    
    class PasteCommand(EditorCommand):
        """粘贴命令"""
        
        def __init__(self, editor: TextEditor, position):
            super().__init__(editor)
            self._position = position
            self._previous_text = ""
        
        def execute(self):
            self._previous_text = self._editor.get_text()
            self._editor.paste_text(self._position)
        
        def undo(self):
            self._editor._text = self._previous_text
            print(f"撤销粘贴: 恢复到粘贴前的文本")
    
    # 测试文本编辑器
    editor = TextEditor()
    invoker = Invoker()
    
    print("初始状态:")
    editor.display()
    
    print("\n插入文本'Hello':")
    insert_cmd = InsertCommand(editor, "Hello", 0)
    invoker.execute_command(insert_cmd)
    editor.display()
    
    print("\n插入文本' World':")
    insert_cmd2 = InsertCommand(editor, " World", 5)
    invoker.execute_command(insert_cmd2)
    editor.display()
    
    print("\n复制文本'Hello':")
    copy_cmd = CopyCommand(editor, 0, 5)
    invoker.execute_command(copy_cmd)
    
    print("\n粘贴文本:")
    paste_cmd = PasteCommand(editor, 11)
    invoker.execute_command(paste_cmd)
    editor.display()
    
    print("\n删除部分文本:")
    delete_cmd = DeleteCommand(editor, 0, 6)
    invoker.execute_command(delete_cmd)
    editor.display()
    
    print("\n命令历史:")
    invoker.show_history()
    
    print("\n撤销两次操作:")
    invoker.undo_last_command()
    editor.display()
    invoker.undo_last_command()
    editor.display()


# 实际应用示例：智能家居系统
def test_smart_home():
    """测试智能家居命令模式"""
    print("\n=== 命令模式应用 - 智能家居系统示例 ===\n")
    
    class Light:
        """灯光设备"""
        
        def __init__(self, location):
            self._location = location
            self._is_on = False
            self._brightness = 50
        
        def on(self):
            self._is_on = True
            print(f"{self._location}灯: 打开")
        
        def off(self):
            self._is_on = False
            print(f"{self._location}灯: 关闭")
        
        def set_brightness(self, level):
            self._brightness = max(0, min(100, level))
            print(f"{self._location}灯: 设置亮度为 {self._brightness}%")
        
        def get_status(self):
            status = "开" if self._is_on else "关"
            return f"{self._location}灯: {status}, 亮度: {self._brightness}%"
    
    class Thermostat:
        """温控器"""
        
        def __init__(self):
            self._temperature = 22
            self._mode = "制冷"
        
        def set_temperature(self, temp):
            self._temperature = temp
            print(f"温控器: 设置温度为 {temp}°C")
        
        def set_mode(self, mode):
            self._mode = mode
            print(f"温控器: 设置模式为 {mode}")
        
        def get_status(self):
            return f"温控器: 温度 {self._temperature}°C, 模式: {self._mode}"
    
    class SmartHomeCommand(ABC):
        """智能家居命令抽象类"""
        
        @abstractmethod
        def execute(self):
            pass
        
        @abstractmethod
        def undo(self):
            pass
    
    class LightOnCommand(SmartHomeCommand):
        """开灯命令"""
        
        def __init__(self, light: Light):
            self._light = light
            self._previous_state = None
        
        def execute(self):
            self._previous_state = self._light._is_on
            self._light.on()
        
        def undo(self):
            if not self._previous_state:
                self._light.off()
            print("撤销开灯操作")
    
    class LightOffCommand(SmartHomeCommand):
        """关灯命令"""
        
        def __init__(self, light: Light):
            self._light = light
            self._previous_state = None
        
        def execute(self):
            self._previous_state = self._light._is_on
            self._light.off()
        
        def undo(self):
            if self._previous_state:
                self._light.on()
            print("撤销关灯操作")
    
    class SetTemperatureCommand(SmartHomeCommand):
        """设置温度命令"""
        
        def __init__(self, thermostat: Thermostat, temperature):
            self._thermostat = thermostat
            self._temperature = temperature
            self._previous_temp = None
        
        def execute(self):
            self._previous_temp = self._thermostat._temperature
            self._thermostat.set_temperature(self._temperature)
        
        def undo(self):
            if self._previous_temp is not None:
                self._thermostat.set_temperature(self._previous_temp)
            print("撤销温度设置")
    
    class MacroCommand(SmartHomeCommand):
        """宏命令 - 执行多个命令"""
        
        def __init__(self, commands: List[SmartHomeCommand]):
            self._commands = commands
        
        def execute(self):
            for command in self._commands:
                command.execute()
        
        def undo(self):
            # 按相反顺序撤销
            for command in reversed(self._commands):
                command.undo()
    
    # 测试智能家居系统
    living_room_light = Light("客厅")
    bedroom_light = Light("卧室")
    thermostat = Thermostat()
    
    invoker = Invoker()
    
    print("初始状态:")
    print(living_room_light.get_status())
    print(bedroom_light.get_status())
    print(thermostat.get_status())
    
    print("\n执行单个命令:")
    light_on_cmd = LightOnCommand(living_room_light)
    invoker.execute_command(light_on_cmd)
    
    temp_cmd = SetTemperatureCommand(thermostat, 24)
    invoker.execute_command(temp_cmd)
    
    print("\n创建并执行宏命令（回家场景）:")
    home_scenario = MacroCommand([
        LightOnCommand(living_room_light),
        LightOnCommand(bedroom_light),
        SetTemperatureCommand(thermostat, 25)
    ])
    invoker.execute_command(home_scenario)
    
    print("\n当前状态:")
    print(living_room_light.get_status())
    print(bedroom_light.get_status())
    print(thermostat.get_status())
    
    print("\n撤销宏命令:")
    invoker.undo_last_command()
    
    print("\n最终状态:")
    print(living_room_light.get_status())
    print(bedroom_light.get_status())
    print(thermostat.get_status())


# Python函数式命令模式
def test_functional_command():
    """测试函数式命令模式"""
    print("\n=== Python函数式命令模式示例 ===\n")
    
    def create_command(execute_func, undo_func):
        """创建命令的工厂函数"""
        class FunctionalCommand:
            def execute(self):
                execute_func()
            
            def undo(self):
                undo_func()
        
        return FunctionalCommand()
    
    # 使用函数创建命令
    counter = 0
    
    def increment():
        global counter
        counter += 1
        print(f"计数器增加: {counter}")
    
    def decrement():
        global counter
        counter -= 1
        print(f"计数器减少: {counter}")
    
    def reset_counter():
        global counter
        counter = 0
        print(f"计数器重置: {counter}")
    
    def restore_counter():
        global counter
        counter = 0
        print(f"计数器恢复: {counter}")
    
    # 创建命令
    inc_cmd = create_command(increment, decrement)
    reset_cmd = create_command(reset_counter, restore_counter)
    
    invoker = Invoker()
    
    print("初始计数器:", counter)
    
    print("\n执行增加命令:")
    invoker.execute_command(inc_cmd)
    invoker.execute_command(inc_cmd)
    
    print("\n执行重置命令:")
    invoker.execute_command(reset_cmd)
    
    print("\n撤销操作:")
    invoker.undo_last_command()
    
    print("\n最终计数器:", counter)


if __name__ == "__main__":
    test_basic_command()
    test_text_editor()
    test_smart_home()
    test_functional_command()
    
    print("\n=== 命令模式总结 ===")
    print("优点：")
    print("- 降低系统的耦合度：命令模式将调用操作的对象与知道如何实现该操作的对象解耦")
    print("- 新的命令可以很容易地加入到系统中：增加新的具体命令类很容易")
    print("- 可以比较容易地设计一个命令队列和宏命令（组合命令）")
    print("- 可以方便地实现对请求的撤销和重做")
    print("\n缺点：")
    print("- 使用命令模式可能会导致某些系统有过多的具体命令类")
    print("- 增加了系统的复杂性")
    print("\n适用场景：")
    print("- 需要将请求调用者和请求接收者解耦")
    print("- 需要在不同的时间指定请求、将请求排队和执行请求")
    print("- 需要支持命令的撤销（Undo）操作和恢复（Redo）操作")
    print("- 需要将一组操作组合在一起，即支持宏命令")
