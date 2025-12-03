"""
享元模式 (Flyweight Pattern) 示例代码

享元模式运用共享技术有效地支持大量细粒度的对象。
"""

from abc import ABC, abstractmethod
from typing import Dict


class TreeType:
    """享元类 - 树的类型（内部状态）"""
    
    def __init__(self, name, color, texture):
        self.name = name
        self.color = color
        self.texture = texture
    
    def display(self, x, y):
        print(f"在位置({x}, {y})绘制一棵{self.color}的{self.name}树，纹理: {self.texture}")
    
    def __repr__(self):
        return f"TreeType(name='{self.name}', color='{self.color}', texture='{self.texture}')"


class TreeFactory:
    """享元工厂类"""
    
    _tree_types: Dict[str, TreeType] = {}
    
    @classmethod
    def get_tree_type(cls, name, color, texture):
        """获取或创建树类型"""
        key = f"{name}_{color}_{texture}"
        
        if key not in cls._tree_types:
            cls._tree_types[key] = TreeType(name, color, texture)
            print(f"创建新的树类型: {key}")
        else:
            print(f"复用现有的树类型: {key}")
        
        return cls._tree_types[key]
    
    @classmethod
    def get_tree_count(cls):
        """获取树类型的数量"""
        return len(cls._tree_types)


class Tree:
    """树类（包含外部状态）"""
    
    def __init__(self, x, y, tree_type: TreeType):
        self.x = x
        self.y = y
        self.tree_type = tree_type
    
    def display(self):
        self.tree_type.display(self.x, self.y)


class Forest:
    """森林类"""
    
    def __init__(self):
        self.trees = []
    
    def plant_tree(self, x, y, name, color, texture):
        """种植树"""
        tree_type = TreeFactory.get_tree_type(name, color, texture)
        tree = Tree(x, y, tree_type)
        self.trees.append(tree)
    
    def display(self):
        """显示森林中的所有树"""
        print(f"\n森林中有 {len(self.trees)} 棵树，但只有 {TreeFactory.get_tree_count()} 种树类型")
        for tree in self.trees:
            tree.display()


# 测试享元模式
def test_forest_simulation():
    """测试森林模拟"""
    print("=== 享元模式测试 - 森林模拟示例 ===\n")
    
    forest = Forest()
    
    # 种植大量树，但只有几种类型
    forest.plant_tree(1, 1, "松树", "绿色", "粗糙")
    forest.plant_tree(2, 3, "松树", "绿色", "粗糙")  # 复用松树类型
    forest.plant_tree(3, 5, "松树", "绿色", "粗糙")  # 复用松树类型
    forest.plant_tree(4, 7, "橡树", "深绿色", "光滑")
    forest.plant_tree(5, 9, "橡树", "深绿色", "光滑")  # 复用橡树类型
    forest.plant_tree(6, 11, "枫树", "红色", "中等")
    forest.plant_tree(7, 13, "松树", "绿色", "粗糙")  # 复用松树类型
    forest.plant_tree(8, 15, "枫树", "红色", "中等")  # 复用枫树类型
    
    forest.display()


# 实际应用示例：文本编辑器
def test_text_editor():
    """测试文本编辑器享元模式"""
    print("\n=== 享元模式应用 - 文本编辑器示例 ===\n")
    
    class CharacterStyle:
        """字符样式（享元类）"""
        
        def __init__(self, font_family, font_size, color, bold=False, italic=False):
            self.font_family = font_family
            self.font_size = font_size
            self.color = color
            self.bold = bold
            self.italic = italic
        
        def apply(self, character, position):
            bold_text = "粗体" if self.bold else ""
            italic_text = "斜体" if self.italic else ""
            print(f"在位置{position}应用样式: {character} - {self.font_family} {self.font_size}pt {self.color} {bold_text} {italic_text}")
        
        def __repr__(self):
            return f"CharacterStyle(font='{self.font_family}', size={self.font_size}, color='{self.color}', bold={self.bold}, italic={self.italic})"


    class CharacterStyleFactory:
        """字符样式工厂"""
        
        _styles: Dict[str, CharacterStyle] = {}
        
        @classmethod
        def get_style(cls, font_family, font_size, color, bold=False, italic=False):
            """获取或创建字符样式"""
            key = f"{font_family}_{font_size}_{color}_{bold}_{italic}"
            
            if key not in cls._styles:
                cls._styles[key] = CharacterStyle(font_family, font_size, color, bold, italic)
                print(f"创建新的字符样式: {key}")
            
            return cls._styles[key]
        
        @classmethod
        def get_style_count(cls):
            """获取样式数量"""
            return len(cls._styles)


    class Character:
        """字符类（包含外部状态）"""
        
        def __init__(self, char, position, style: CharacterStyle):
            self.char = char
            self.position = position
            self.style = style
        
        def display(self):
            self.style.apply(self.char, self.position)


    class Document:
        """文档类"""
        
        def __init__(self):
            self.characters = []
        
        def add_character(self, char, position, font_family, font_size, color, bold=False, italic=False):
            """添加字符"""
            style = CharacterStyleFactory.get_style(font_family, font_size, color, bold, italic)
            character = Character(char, position, style)
            self.characters.append(character)
        
        def display(self):
            """显示文档"""
            print(f"\n文档中有 {len(self.characters)} 个字符，但只有 {CharacterStyleFactory.get_style_count()} 种样式")
            for char in self.characters:
                char.display()


    # 测试文本编辑器
    document = Document()
    
    # 添加大量字符，但只有几种样式
    document.add_character('H', 0, 'Arial', 12, 'black')
    document.add_character('e', 1, 'Arial', 12, 'black')  # 复用样式
    document.add_character('l', 2, 'Arial', 12, 'black')  # 复用样式
    document.add_character('l', 3, 'Arial', 12, 'black')  # 复用样式
    document.add_character('o', 4, 'Arial', 12, 'black')  # 复用样式
    document.add_character(' ', 5, 'Arial', 12, 'black')  # 复用样式
    document.add_character('W', 6, 'Times New Roman', 14, 'blue', bold=True)
    document.add_character('o', 7, 'Times New Roman', 14, 'blue', bold=True)  # 复用样式
    document.add_character('r', 8, 'Times New Roman', 14, 'blue', bold=True)  # 复用样式
    document.add_character('l', 9, 'Times New Roman', 14, 'blue', bold=True)  # 复用样式
    document.add_character('d', 10, 'Times New Roman', 14, 'blue', bold=True)  # 复用样式
    document.add_character('!', 11, 'Courier New', 16, 'red', italic=True)
    
    document.display()


# 实际应用示例：游戏中的粒子系统
def test_particle_system():
    """测试粒子系统享元模式"""
    print("\n=== 享元模式应用 - 游戏粒子系统示例 ===\n")
    
    class ParticleType:
        """粒子类型（享元类）"""
        
        def __init__(self, texture, color, size, lifetime):
            self.texture = texture
            self.color = color
            self.size = size
            self.lifetime = lifetime
        
        def render(self, x, y, velocity, age):
            print(f"在({x}, {y})渲染粒子: {self.texture}, 颜色: {self.color}, 大小: {self.size}, 速度: {velocity}, 年龄: {age}/{self.lifetime}")
        
        def __repr__(self):
            return f"ParticleType(texture='{self.texture}', color='{self.color}', size={self.size}, lifetime={self.lifetime})"


    class ParticleTypeFactory:
        """粒子类型工厂"""
        
        _particle_types: Dict[str, ParticleType] = {}
        
        @classmethod
        def get_particle_type(cls, texture, color, size, lifetime):
            """获取或创建粒子类型"""
            key = f"{texture}_{color}_{size}_{lifetime}"
            
            if key not in cls._particle_types:
                cls._particle_types[key] = ParticleType(texture, color, size, lifetime)
                print(f"创建新的粒子类型: {key}")
            
            return cls._particle_types[key]
        
        @classmethod
        def get_type_count(cls):
            """获取类型数量"""
            return len(cls._particle_types)


    class Particle:
        """粒子类（包含外部状态）"""
        
        def __init__(self, x, y, velocity, particle_type: ParticleType):
            self.x = x
            self.y = y
            self.velocity = velocity
            self.particle_type = particle_type
            self.age = 0
        
        def update(self):
            """更新粒子状态"""
            self.x += self.velocity[0]
            self.y += self.velocity[1]
            self.age += 1
        
        def is_alive(self):
            """检查粒子是否存活"""
            return self.age < self.particle_type.lifetime
        
        def render(self):
            """渲染粒子"""
            self.particle_type.render(self.x, self.y, self.velocity, self.age)


    class ParticleSystem:
        """粒子系统"""
        
        def __init__(self):
            self.particles = []
        
        def emit(self, x, y, velocity, texture, color, size, lifetime):
            """发射粒子"""
            particle_type = ParticleTypeFactory.get_particle_type(texture, color, size, lifetime)
            particle = Particle(x, y, velocity, particle_type)
            self.particles.append(particle)
        
        def update(self):
            """更新所有粒子"""
            # 移除死亡的粒子
            self.particles = [p for p in self.particles if p.is_alive()]
            
            # 更新存活的粒子
            for particle in self.particles:
                particle.update()
        
        def render(self):
            """渲染所有粒子"""
            print(f"\n粒子系统中有 {len(self.particles)} 个粒子，但只有 {ParticleTypeFactory.get_type_count()} 种粒子类型")
            for particle in self.particles:
                particle.render()


    # 测试粒子系统
    particle_system = ParticleSystem()
    
    # 发射大量粒子，但只有几种类型
    particle_system.emit(0, 0, (1, 1), "火花", "红色", 2, 10)
    particle_system.emit(5, 5, (0, 2), "火花", "红色", 2, 10)  # 复用类型
    particle_system.emit(10, 10, (-1, 1), "火花", "红色", 2, 10)  # 复用类型
    particle_system.emit(15, 15, (2, 0), "烟雾", "灰色", 5, 20)
    particle_system.emit(20, 20, (1, -1), "烟雾", "灰色", 5, 20)  # 复用类型
    particle_system.emit(25, 25, (0, -2), "水滴", "蓝色", 3, 15)
    
    print("第一次更新:")
    particle_system.update()
    particle_system.render()
    
    print("\n第二次更新:")
    particle_system.update()
    particle_system.render()


if __name__ == "__main__":
    test_forest_simulation()
    test_text_editor()
    test_particle_system()
    
    print("\n=== 享元模式总结 ===")
    print("优点：")
    print("- 极大减少内存中对象的数量")
    print("- 相同或相似对象内存中只存一份，极大地节约资源")
    print("- 外部状态相对独立，不会影响内部状态")
    print("\n缺点：")
    print("- 需要分离出内部状态和外部状态，增加了系统的复杂性")
    print("- 读取外部状态使得运行时间稍微变长")
    print("\n适用场景：")
    print("- 一个系统有大量相同或者相似的对象，造成内存的大量耗费")
    print("- 对象的大部分状态都可以外部化，可以将这些外部状态传入对象中")
    print("- 需要缓冲池的场景")
