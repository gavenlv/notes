"""
第18章：备忘录模式 (Memento Pattern)

备忘录模式是一种行为设计模式，它允许在不破坏封装性的前提下捕获并外部化一个对象的内部状态，
以便以后可以将该对象恢复到先前的状态。
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any


class Memento(ABC):
    """备忘录接口"""
    
    @abstractmethod
    def get_name(self) -> str:
        """获取备忘录名称"""
        pass
    
    @abstractmethod
    def get_date(self) -> str:
        """获取创建日期"""
        pass


class ConcreteMemento(Memento):
    """具体备忘录类"""
    
    def __init__(self, state: Dict[str, Any]):
        self._state = state.copy()  # 深拷贝状态
        self._date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def get_state(self) -> Dict[str, Any]:
        """获取状态"""
        return self._state.copy()
    
    def get_name(self) -> str:
        """获取备忘录名称"""
        return f"Memento @ {self._date}"
    
    def get_date(self) -> str:
        """获取创建日期"""
        return self._date


class Originator:
    """原发器类"""
    
    def __init__(self, state: Dict[str, Any] = None):
        self._state = state or {}
    
    def set_state(self, state: Dict[str, Any]) -> None:
        """设置状态"""
        self._state = state.copy()
    
    def get_state(self) -> Dict[str, Any]:
        """获取状态"""
        return self._state.copy()
    
    def save(self) -> Memento:
        """保存状态到备忘录"""
        return ConcreteMemento(self._state)
    
    def restore(self, memento: Memento) -> None:
        """从备忘录恢复状态"""
        if isinstance(memento, ConcreteMemento):
            self._state = memento.get_state()
    
    def __str__(self) -> str:
        return f"Originator state: {self._state}"


class Caretaker:
    """负责人类"""
    
    def __init__(self, originator: Originator):
        self._originator = originator
        self._mementos: List[Memento] = []
    
    def backup(self) -> None:
        """备份状态"""
        print("Caretaker: 保存状态...")
        self._mementos.append(self._originator.save())
    
    def undo(self) -> None:
        """撤销操作"""
        if not self._mementos:
            print("Caretaker: 没有可撤销的状态")
            return
        
        memento = self._mementos.pop()
        print(f"Caretaker: 恢复状态: {memento.get_name()}")
        self._originator.restore(memento)
    
    def show_history(self) -> None:
        """显示历史记录"""
        print("Caretaker: 以下是备忘录历史:")
        for memento in self._mementos:
            print(f" - {memento.get_name()}")


# 示例1：文本编辑器撤销功能
class TextEditor:
    """文本编辑器"""
    
    def __init__(self):
        self._content = ""
        self._cursor_position = 0
        self._font_size = 12
        self._font_family = "Arial"
    
    def type_text(self, text: str) -> None:
        """输入文本"""
        self._content += text
        self._cursor_position += len(text)
        print(f"输入文本: '{text}'，当前内容: '{self._content}'")
    
    def set_font(self, size: int, family: str) -> None:
        """设置字体"""
        self._font_size = size
        self._font_family = family
        print(f"设置字体: {family} {size}pt")
    
    def save_state(self) -> Memento:
        """保存状态"""
        state = {
            'content': self._content,
            'cursor_position': self._cursor_position,
            'font_size': self._font_size,
            'font_family': self._font_family
        }
        return ConcreteMemento(state)
    
    def restore_state(self, memento: Memento) -> None:
        """恢复状态"""
        if isinstance(memento, ConcreteMemento):
            state = memento.get_state()
            self._content = state['content']
            self._cursor_position = state['cursor_position']
            self._font_size = state['font_size']
            self._font_family = state['font_family']
            print(f"恢复状态: 内容='{self._content}'，字体={self._font_family} {self._font_size}pt")
    
    def display(self) -> None:
        """显示当前状态"""
        print(f"内容: {self._content}")
        print(f"光标位置: {self._cursor_position}")
        print(f"字体: {self._font_family} {self._font_size}pt")


# 示例2：游戏存档系统
class GameCharacter:
    """游戏角色"""
    
    def __init__(self, name: str):
        self.name = name
        self.level = 1
        self.health = 100
        self.mana = 50
        self.position = (0, 0)
        self.inventory = []
    
    def level_up(self) -> None:
        """升级"""
        self.level += 1
        self.health += 20
        self.mana += 10
        print(f"{self.name} 升级到 {self.level} 级!")
    
    def take_damage(self, damage: int) -> None:
        """受到伤害"""
        self.health = max(0, self.health - damage)
        print(f"{self.name} 受到 {damage} 点伤害，剩余生命值: {self.health}")
    
    def move(self, x: int, y: int) -> None:
        """移动"""
        self.position = (x, y)
        print(f"{self.name} 移动到位置 ({x}, {y})")
    
    def add_item(self, item: str) -> None:
        """添加物品"""
        self.inventory.append(item)
        print(f"{self.name} 获得物品: {item}")
    
    def save_game(self) -> Memento:
        """保存游戏"""
        state = {
            'name': self.name,
            'level': self.level,
            'health': self.health,
            'mana': self.mana,
            'position': self.position,
            'inventory': self.inventory.copy()
        }
        return ConcreteMemento(state)
    
    def load_game(self, memento: Memento) -> None:
        """加载游戏"""
        if isinstance(memento, ConcreteMemento):
            state = memento.get_state()
            self.level = state['level']
            self.health = state['health']
            self.mana = state['mana']
            self.position = state['position']
            self.inventory = state['inventory'].copy()
            print(f"加载存档: {self.name} Lv.{self.level} HP:{self.health}")
    
    def display_status(self) -> None:
        """显示状态"""
        print(f"角色: {self.name}")
        print(f"等级: {self.level}")
        print(f"生命值: {self.health}")
        print(f"魔法值: {self.mana}")
        print(f"位置: {self.position}")
        print(f"物品: {', '.join(self.inventory) if self.inventory else '无'}")


# 示例3：配置管理系统
class SystemConfig:
    """系统配置"""
    
    def __init__(self):
        self._config = {
            'theme': 'light',
            'language': 'zh-CN',
            'auto_save': True,
            'notifications': True,
            'font_size': 14
        }
    
    def set_config(self, key: str, value: Any) -> None:
        """设置配置项"""
        if key in self._config:
            old_value = self._config[key]
            self._config[key] = value
            print(f"配置已更新: {key} = {old_value} -> {value}")
        else:
            print(f"未知配置项: {key}")
    
    def get_config(self, key: str) -> Any:
        """获取配置项"""
        return self._config.get(key)
    
    def save_config(self) -> Memento:
        """保存配置"""
        return ConcreteMemento(self._config.copy())
    
    def restore_config(self, memento: Memento) -> None:
        """恢复配置"""
        if isinstance(memento, ConcreteMemento):
            self._config = memento.get_state().copy()
            print("配置已恢复到之前的状态")
    
    def display_config(self) -> None:
        """显示配置"""
        print("当前系统配置:")
        for key, value in self._config.items():
            print(f"  {key}: {value}")


def test_text_editor():
    """测试文本编辑器撤销功能"""
    print("=== 测试文本编辑器撤销功能 ===")
    
    editor = TextEditor()
    caretaker = Caretaker(editor)
    
    # 初始状态
    editor.type_text("Hello")
    caretaker.backup()
    
    # 继续编辑
    editor.type_text(" World")
    editor.set_font(16, "Times New Roman")
    caretaker.backup()
    
    # 再编辑
    editor.type_text("!")
    editor.set_font(18, "Courier New")
    print("\n当前状态:")
    editor.display()
    
    # 撤销一次
    print("\n撤销一次:")
    caretaker.undo()
    editor.display()
    
    # 再撤销一次
    print("\n再撤销一次:")
    caretaker.undo()
    editor.display()


def test_game_save():
    """测试游戏存档系统"""
    print("\n=== 测试游戏存档系统 ===")
    
    character = GameCharacter("勇士")
    
    # 初始状态
    character.display_status()
    save1 = character.save_game()
    
    # 游戏进程
    character.level_up()
    character.move(10, 5)
    character.add_item("宝剑")
    character.add_item("药水")
    save2 = character.save_game()
    
    # 继续游戏
    character.level_up()
    character.take_damage(30)
    character.move(15, 8)
    character.add_item("盾牌")
    print("\n当前状态:")
    character.display_status()
    
    # 加载存档2
    print("\n加载存档2:")
    character.load_game(save2)
    character.display_status()
    
    # 加载存档1
    print("\n加载存档1:")
    character.load_game(save1)
    character.display_status()


def test_config_management():
    """测试配置管理系统"""
    print("\n=== 测试配置管理系统 ===")
    
    config = SystemConfig()
    caretaker = Caretaker(config)
    
    # 初始配置
    config.display_config()
    caretaker.backup()
    
    # 修改配置
    config.set_config('theme', 'dark')
    config.set_config('font_size', 16)
    config.set_config('auto_save', False)
    caretaker.backup()
    
    # 再次修改
    config.set_config('language', 'en-US')
    config.set_config('notifications', False)
    print("\n当前配置:")
    config.display_config()
    
    # 撤销修改
    print("\n撤销一次:")
    caretaker.undo()
    config.display_config()
    
    # 再撤销一次
    print("\n再撤销一次:")
    caretaker.undo()
    config.display_config()


def test_advanced_memento():
    """测试高级备忘录功能"""
    print("\n=== 测试高级备忘录功能 ===")
    
    originator = Originator({"value": 0})
    caretaker = Caretaker(originator)
    
    # 创建多个快照
    for i in range(1, 6):
        originator.set_state({"value": i * 10})
        caretaker.backup()
        print(f"状态 {i}: {originator.get_state()}")
    
    # 显示历史
    caretaker.show_history()
    
    # 逐步撤销
    for i in range(3):
        caretaker.undo()
        print(f"撤销后状态: {originator.get_state()}")


if __name__ == "__main__":
    # 运行所有测试
    test_text_editor()
    test_game_save()
    test_config_management()
    test_advanced_memento()
    
    print("\n=== 备忘录模式测试完成 ===")
    print("\n备忘录模式总结：")
    print("1. 保存对象状态而不破坏封装性")
    print("2. 实现撤销/重做功能")
    print("3. 支持状态快照和恢复")
    print("4. 适用于需要历史记录的系统")
    print("5. 注意内存使用，及时清理无用备忘录")