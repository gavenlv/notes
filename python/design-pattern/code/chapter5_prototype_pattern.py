"""
第5章：原型模式 - 示例代码

本文件包含了第5章中提到的所有示例代码，用于演示原型模式的各种实现方式和应用场景。
"""

print("=== 原型模式示例 ===\n")

import copy

# 1. 基本实现
print("1. 原型模式的基本实现:")

from abc import ABC, abstractmethod

# 抽象原型
class Prototype(ABC):
    @abstractmethod
    def clone(self):
        pass

# 具体原型
class ConcretePrototype(Prototype):
    def __init__(self, field):
        self.field = field
    
    def clone(self):
        # 创建新对象并复制字段
        return ConcretePrototype(self.field)
    
    def __str__(self):
        return f"ConcretePrototype(field={self.field})"

# 客户端代码
prototype = ConcretePrototype("初始值")
clone = prototype.clone()

print(f"原对象: {prototype}")
print(f"克隆对象: {clone}")
print(f"原对象ID: {id(prototype)}")
print(f"克隆对象ID: {id(clone)}")
print(f"是同一个对象: {prototype is clone}")

# 2. 浅拷贝实现
print("\n2. 浅拷贝和深拷贝对比:")

# 可变对象的类
class Person:
    def __init__(self, name, address):
        self.name = name
        self.address = address  # address是一个可变对象
    
    def __str__(self):
        return f"Person(name={self.name}, address={self.address})"

# 实现原型接口
class PersonPrototype:
    def __init__(self, person):
        self.person = person
    
    def clone_shallow(self):
        # 浅拷贝：只复制对象本身，不复制引用的对象
        return copy.copy(self.person)
    
    def clone_deep(self):
        # 深拷贝：复制对象及其引用的所有对象
        return copy.deepcopy(self.person)

# 测试浅拷贝和深拷贝
address = {"city": "北京", "street": "朝阳区"}
person = Person("张三", address)
prototype = PersonPrototype(person)

# 浅拷贝
shallow_clone = prototype.clone_shallow()
print("浅拷贝测试:")
print(f"原对象: {person}")
print(f"克隆对象: {shallow_clone}")
print(f"是同一个对象: {person is shallow_clone}")
print(f"地址是同一个对象: {person.address is shallow_clone.address}")

# 修改原对象的地址
person.address["city"] = "上海"
print(f"修改原对象地址后，克隆对象的地址: {shallow_clone.address}")

# 深拷贝
deep_clone = prototype.clone_deep()
print("\n深拷贝测试:")
print(f"原对象: {person}")
print(f"克隆对象: {deep_clone}")
print(f"是同一个对象: {person is deep_clone}")
print(f"地址是同一个对象: {person.address is deep_clone.address}")

# 修改原对象的地址
person.address["city"] = "广州"
print(f"修改原对象地址后，克隆对象的地址: {deep_clone.address}")

# 3. 使用注册表的实现
print("\n3. 使用注册表的实现:")

class PrototypeRegistry:
    _registry = {}
    
    @classmethod
    def register(cls, key, prototype):
        cls._registry[key] = prototype
    
    @classmethod
    def unregister(cls, key):
        if key in cls._registry:
            del cls._registry[key]
    
    @classmethod
    def clone(cls, key, **kwargs):
        if key not in cls._registry:
            raise ValueError(f"未注册的原型: {key}")
        
        prototype = cls._registry[key]
        clone = copy.deepcopy(prototype)
        
        # 更新克隆对象的属性
        for attr, value in kwargs.items():
            if hasattr(clone, attr):
                setattr(clone, attr, value)
        
        return clone
    
    @classmethod
    def list_prototypes(cls):
        return list(cls._registry.keys())

# 定义可克隆的类
class Shape:
    def __init__(self, x=0, y=0, color="black"):
        self.x = x
        self.y = y
        self.color = color
    
    def clone(self):
        return copy.deepcopy(self)
    
    def __str__(self):
        return f"{self.__class__.__name__}(x={self.x}, y={self.y}, color={self.color})"

class Circle(Shape):
    def __init__(self, x=0, y=0, color="black", radius=1):
        super().__init__(x, y, color)
        self.radius = radius
    
    def __str__(self):
        return f"Circle(x={self.x}, y={self.y}, color={self.color}, radius={self.radius})"

class Rectangle(Shape):
    def __init__(self, x=0, y=0, color="black", width=1, height=1):
        super().__init__(x, y, color)
        self.width = width
        self.height = height
    
    def __str__(self):
        return f"Rectangle(x={self.x}, y={self.y}, color={self.color}, width={self.width}, height={self.height})"

# 注册原型
PrototypeRegistry.register("circle", Circle(x=10, y=20, color="red", radius=5))
PrototypeRegistry.register("rectangle", Rectangle(x=5, y=15, color="blue", width=10, height=8))

# 使用注册表创建对象
print("使用注册表克隆原型:")
circle1 = PrototypeRegistry.clone("circle")
circle2 = PrototypeRegistry.clone("circle", color="green", radius=10)
rectangle1 = PrototypeRegistry.clone("rectangle")
rectangle2 = PrototypeRegistry.clone("rectangle", x=20, y=30, width=15)

print(f"圆形1: {circle1}")
print(f"圆形2: {circle2}")
print(f"矩形1: {rectangle1}")
print(f"矩形2: {rectangle2}")

print(f"已注册的原型: {PrototypeRegistry.list_prototypes()}")

# 4. 游戏对象克隆
print("\n4. 游戏对象克隆:")

# 游戏中的角色类
class GameCharacter:
    def __init__(self, name, health, attack, defense, skills):
        self.name = name
        self.health = health
        self.attack = attack
        self.defense = defense
        self.skills = skills
    
    def clone(self):
        return copy.deepcopy(self)
    
    def __str__(self):
        skills_str = ", ".join(self.skills)
        return f"{self.name}(生命值={self.health}, 攻击力={self.attack}, 防御力={self.defense}, 技能=[{skills_str}])"

# 角色原型工厂
class CharacterFactory:
    _prototypes = {}
    
    @classmethod
    def register(cls, name, character):
        cls._prototypes[name] = character
    
    @classmethod
    def create(cls, name, new_name=None):
        if name not in cls._prototypes:
            raise ValueError(f"未注册的角色原型: {name}")
        
        character = cls._prototypes[name].clone()
        if new_name:
            character.name = new_name
        return character

# 注册角色原型
warrior = GameCharacter("战士", 100, 20, 15, ["重击", "防御"])
mage = GameCharacter("法师", 60, 30, 5, ["火球术", "冰冻术", "魔法盾"])
archer = GameCharacter("弓箭手", 80, 25, 10, ["精准射击", "多重箭"])

CharacterFactory.register("warrior", warrior)
CharacterFactory.register("mage", mage)
CharacterFactory.register("archer", archer)

# 创建游戏角色
print("游戏角色克隆:")
warrior1 = CharacterFactory.create("warrior", "勇敢的战士")
warrior2 = CharacterFactory.create("warrior", "强大的战士")
mage1 = CharacterFactory.create("mage", "智慧的法师")
archer1 = CharacterFactory.create("archer", "敏捷的弓箭手")

print(warrior1)
print(warrior2)
print(mage1)
print(archer1)

# 修改克隆对象不会影响原对象
warrior1.health = 80  # 受伤了
print(f"修改后，{warrior1}")
print(f"原型{warrior}")

# 5. 文档模板系统
print("\n5. 文档模板系统:")

# 文档类
class Document:
    def __init__(self, title, content, author, tags):
        self.title = title
        self.content = content
        self.author = author
        self.tags = tags
    
    def clone(self):
        return copy.deepcopy(self)
    
    def __str__(self):
        tags_str = ", ".join(self.tags)
        return f"文档: {self.title}\n作者: {self.author}\n标签: [{tags_str}]\n内容: {self.content}"

# 文档模板工厂
class DocumentTemplateFactory:
    _templates = {}
    
    @classmethod
    def register(cls, name, template):
        cls._templates[name] = template
    
    @classmethod
    def create(cls, name, **kwargs):
        if name not in cls._templates:
            raise ValueError(f"未注册的文档模板: {name}")
        
        document = cls._templates[name].clone()
        
        # 更新文档属性
        for attr, value in kwargs.items():
            if hasattr(document, attr):
                setattr(document, attr, value)
        
        return document

# 注册文档模板
report_template = Document(
    "报告",
    "这是一份报告。第一部分：...\n第二部分：...\n结论：...",
    "系统",
    ["报告", "正式"]
)

memo_template = Document(
    "备忘录",
    "这是一份备忘录。\n主题：...\n内容：...",
    "系统",
    ["备忘录", "内部"]
)

meeting_template = Document(
    "会议记录",
    "会议时间：\n参会人员：\n会议议程：\n1. ...\n2. ...\n会议结论：",
    "系统",
    ["会议", "记录"]
)

DocumentTemplateFactory.register("report", report_template)
DocumentTemplateFactory.register("memo", memo_template)
DocumentTemplateFactory.register("meeting", meeting_template)

# 创建文档
print("文档模板系统:")
weekly_report = DocumentTemplateFactory.create(
    "report", 
    title="周报", 
    content="本周工作总结：...\n下周工作计划：...",
    author="张三"
)

project_memo = DocumentTemplateFactory.create(
    "memo",
    title="项目备忘录",
    content="项目进度：...\n存在问题：...",
    author="李四"
)

team_meeting = DocumentTemplateFactory.create(
    "meeting",
    title="团队会议记录",
    content="会议时间：2023-10-15\n参会人员：张三, 李四, 王五\n会议议程：\n1. 项目进度汇报\n2. 问题讨论\n3. 下一步计划",
    author="王五"
)

print(weekly_report)
print("\n" + "="*50 + "\n")
print(project_memo)
print("\n" + "="*50 + "\n")
print(team_meeting)

# 6. 图形编辑器
print("\n6. 图形编辑器:")

# 图形基类
class Graphic:
    def __init__(self, x=0, y=0, color="black"):
        self.x = x
        self.y = y
        self.color = color
    
    def clone(self):
        return copy.deepcopy(self)
    
    def move(self, dx, dy):
        self.x += dx
        self.y += dy
    
    def __str__(self):
        return f"{self.__class__.__name__}(x={self.x}, y={self.y}, color={self.color})"

# 具体图形类
class Line(Graphic):
    def __init__(self, x1=0, y1=0, x2=10, y2=10, color="black"):
        super().__init__(x1, y1, color)
        self.x2 = x2
        self.y2 = y2
    
    def move(self, dx, dy):
        super().move(dx, dy)
        self.x2 += dx
        self.y2 += dy
    
    def __str__(self):
        return f"Line(({self.x}, {self.y}) to ({self.x2}, {self.y2}), color={self.color})"

class Circle(Graphic):
    def __init__(self, x=0, y=0, radius=10, color="black"):
        super().__init__(x, y, color)
        self.radius = radius
    
    def __str__(self):
        return f"Circle(center=({self.x}, {self.y}), radius={self.radius}, color={self.color})"

class Rectangle(Graphic):
    def __init__(self, x=0, y=0, width=20, height=10, color="black"):
        super().__init__(x, y, color)
        self.width = width
        self.height = height
    
    def move(self, dx, dy):
        super().move(dx, dy)
    
    def __str__(self):
        return f"Rectangle(top-left=({self.x}, {self.y}), width={self.width}, height={self.height}, color={self.color})"

# 图形编辑器
class GraphicEditor:
    def __init__(self):
        self.graphics = []
        self.clipboard = None
    
    def add_graphic(self, graphic):
        self.graphics.append(graphic)
    
    def remove_graphic(self, index):
        if 0 <= index < len(self.graphics):
            return self.graphics.pop(index)
        return None
    
    def copy_graphic(self, index):
        if 0 <= index < len(self.graphics):
            self.clipboard = self.graphics[index].clone()
    
    def paste_graphic(self):
        if self.clipboard:
            # 创建一个偏移的副本，避免完全重叠
            new_graphic = self.clipboard.clone()
            new_graphic.move(10, 10)
            self.add_graphic(new_graphic)
            return new_graphic
        return None
    
    def list_graphics(self):
        for i, graphic in enumerate(self.graphics):
            print(f"{i}: {graphic}")

# 使用图形编辑器
print("图形编辑器:")
editor = GraphicEditor()

# 添加图形
editor.add_graphic(Line(0, 0, 20, 20, "red"))
editor.add_graphic(Circle(50, 50, 15, "blue"))
editor.add_graphic(Rectangle(100, 0, 30, 20, "green"))

print("初始图形:")
editor.list_graphics()

# 复制第一个图形
print("\n复制第一个图形:")
editor.copy_graphic(0)
editor.paste_graphic()

print("复制后的图形:")
editor.list_graphics()

# 复制第二个图形并多次粘贴
print("\n复制第二个图形并多次粘贴:")
editor.copy_graphic(1)
editor.paste_graphic()
editor.paste_graphic()

print("最终图形:")
editor.list_graphics()

# 7. Python特殊的克隆实现方式
print("\n7. Python特殊的克隆实现方式:")

# 使用__dict__实现克隆
class SpecialCloneObject:
    def __init__(self, value, data):
        self.value = value
        self.data = data
    
    def clone(self):
        # 创建新实例
        clone_obj = self.__class__.__new__(self.__class__)
        # 复制属性字典
        clone_obj.__dict__ = copy.deepcopy(self.__dict__)
        return clone_obj
    
    def __str__(self):
        return f"SpecialCloneObject(value={self.value}, data={self.data})"

# 测试特殊克隆方式
original = SpecialCloneObject("原始", {"key": "value"})
cloned = original.clone()

print("使用__dict__实现克隆:")
print(f"原对象: {original}")
print(f"克隆对象: {cloned}")
print(f"是同一个对象: {original is cloned}")
print(f"数据是同一个对象: {original.data is cloned.data}")

# 修改原对象的数据
original.data["key"] = "modified_value"
print(f"修改原对象数据后，克隆对象的数据: {cloned.data}")

# 总结
print("\n=== 总结 ===")
print("原型模式使用原型实例指定创建对象的种类，并通过复制这些原型创建新的对象。")
print("原型模式的主要优点:")
print("1. 通过复制已有对象创建新对象，提高性能")
print("2. 简化对象的创建过程，避免复杂的初始化")
print("3. 可以在运行时动态创建和修改对象")
print("4. 隐藏了对象创建的细节")
print("\n在Python中，可以使用多种方式实现原型模式:")
print("1. 基本的clone方法实现")
print("2. 使用copy模块的copy()和deepcopy()函数")
print("3. 使用原型注册表管理多个原型")
print("4. 使用__dict__实现自定义克隆逻辑")
print("\n浅拷贝和深拷贝的选择:")
print("- 浅拷贝：只复制对象本身，不复制引用的对象")
print("- 深拷贝：复制对象及其引用的所有对象")
print("- 对于包含可变引用的对象，应使用深拷贝确保完整性")