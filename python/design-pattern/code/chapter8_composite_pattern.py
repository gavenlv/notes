"""
组合模式 (Composite Pattern) 示例代码

组合模式将对象组合成树形结构以表示"部分-整体"的层次结构，使得用户对单个对象和组合对象的使用具有一致性。
"""

from abc import ABC, abstractmethod
from typing import List


class FileSystemComponent(ABC):
    """文件系统组件抽象类"""
    
    def __init__(self, name):
        self.name = name
    
    @abstractmethod
    def display(self, indent=0):
        """显示组件信息"""
        pass
    
    @abstractmethod
    def get_size(self):
        """获取组件大小"""
        pass
    
    def add(self, component):
        """添加子组件（默认实现，叶子节点会重写）"""
        raise NotImplementedError("叶子节点不支持添加操作")
    
    def remove(self, component):
        """移除子组件（默认实现，叶子节点会重写）"""
        raise NotImplementedError("叶子节点不支持移除操作")
    
    def get_child(self, index):
        """获取子组件（默认实现，叶子节点会重写）"""
        raise NotImplementedError("叶子节点没有子组件")


class File(FileSystemComponent):
    """叶子节点 - 文件"""
    
    def __init__(self, name, size):
        super().__init__(name)
        self._size = size
    
    def display(self, indent=0):
        print("  " * indent + f"📄 {self.name} ({self._size} bytes)")
    
    def get_size(self):
        return self._size


class Directory(FileSystemComponent):
    """组合节点 - 目录"""
    
    def __init__(self, name):
        super().__init__(name)
        self._children: List[FileSystemComponent] = []
    
    def display(self, indent=0):
        print("  " * indent + f"📁 {self.name}/ (总大小: {self.get_size()} bytes)")
        for child in self._children:
            child.display(indent + 1)
    
    def get_size(self):
        total_size = 0
        for child in self._children:
            total_size += child.get_size()
        return total_size
    
    def add(self, component):
        self._children.append(component)
    
    def remove(self, component):
        self._children.remove(component)
    
    def get_child(self, index):
        return self._children[index]


# 测试组合模式
def test_composite_pattern():
    """测试组合模式"""
    print("=== 组合模式测试 - 文件系统示例 ===\n")
    
    # 创建根目录
    root = Directory("根目录")
    
    # 创建子目录
    documents = Directory("文档")
    pictures = Directory("图片")
    music = Directory("音乐")
    
    # 创建文件
    resume = File("简历.pdf", 1024)
    report = File("报告.docx", 2048)
    photo1 = File("照片1.jpg", 5120)
    photo2 = File("照片2.jpg", 6144)
    song1 = File("歌曲1.mp3", 4096)
    song2 = File("歌曲2.mp3", 5120)
    
    # 构建目录结构
    documents.add(resume)
    documents.add(report)
    
    pictures.add(photo1)
    pictures.add(photo2)
    
    music.add(song1)
    music.add(song2)
    
    root.add(documents)
    root.add(pictures)
    root.add(music)
    
    # 显示整个文件系统
    root.display()
    
    print(f"\n根目录总大小: {root.get_size()} bytes")
    print(f"文档目录大小: {documents.get_size()} bytes")
    print(f"图片目录大小: {pictures.get_size()} bytes")
    print(f"音乐目录大小: {music.get_size()} bytes")


# 实际应用示例：组织架构
def test_organization_composite():
    """测试组织架构组合模式"""
    print("\n=== 组合模式应用 - 组织架构示例 ===\n")
    
    class Employee(ABC):
        """员工抽象类"""
        
        def __init__(self, name, position):
            self.name = name
            self.position = position
        
        @abstractmethod
        def show_details(self, indent=0):
            pass
        
        @abstractmethod
        def get_salary(self):
            pass
    
    class IndividualEmployee(Employee):
        """个体员工（叶子节点）"""
        
        def __init__(self, name, position, salary):
            super().__init__(name, position)
            self._salary = salary
        
        def show_details(self, indent=0):
            print("  " * indent + f"👤 {self.name} - {self.position} (薪资: ¥{self._salary:,})")
        
        def get_salary(self):
            return self._salary
    
    class Department(Employee):
        """部门（组合节点）"""
        
        def __init__(self, name, manager):
            super().__init__(name, "部门")
            self.manager = manager
            self._employees: List[Employee] = []
        
        def show_details(self, indent=0):
            print("  " * indent + f"🏢 {self.name} (总薪资: ¥{self.get_salary():,})")
            print("  " * (indent + 1) + f"👨‍💼 经理: {self.manager}")
            for employee in self._employees:
                employee.show_details(indent + 1)
        
        def get_salary(self):
            total_salary = 0
            for employee in self._employees:
                total_salary += employee.get_salary()
            return total_salary
        
        def add_employee(self, employee):
            self._employees.append(employee)
        
        def remove_employee(self, employee):
            self._employees.remove(employee)
    
    # 创建员工
    ceo = IndividualEmployee("张三", "CEO", 100000)
    cto = IndividualEmployee("李四", "CTO", 80000)
    dev1 = IndividualEmployee("王五", "高级开发", 50000)
    dev2 = IndividualEmployee("赵六", "开发工程师", 40000)
    tester = IndividualEmployee("钱七", "测试工程师", 35000)
    
    # 创建部门
    tech_department = Department("技术部", "李四")
    tech_department.add_employee(cto)
    tech_department.add_employee(dev1)
    tech_department.add_employee(dev2)
    tech_department.add_employee(tester)
    
    # 显示组织架构
    print("🏢 公司组织架构:")
    ceo.show_details(1)
    tech_department.show_details(1)
    
    print(f"\n💰 薪资统计:")
    print(f"CEO薪资: ¥{ceo.get_salary():,}")
    print(f"技术部总薪资: ¥{tech_department.get_salary():,}")
    print(f"公司总薪资: ¥{ceo.get_salary() + tech_department.get_salary():,}")


# 图形界面组件示例
def test_gui_composite():
    """测试GUI组件组合模式"""
    print("\n=== 组合模式应用 - GUI组件示例 ===\n")
    
    class GUIComponent(ABC):
        """GUI组件抽象类"""
        
        def __init__(self, name):
            self.name = name
        
        @abstractmethod
        def render(self, indent=0):
            pass
    
    class Button(GUIComponent):
        """按钮组件（叶子节点）"""
        
        def __init__(self, name, text):
            super().__init__(name)
            self.text = text
        
        def render(self, indent=0):
            print("  " * indent + f"🔘 [{self.text}]")
    
    class TextField(GUIComponent):
        """文本框组件（叶子节点）"""
        
        def __init__(self, name, placeholder):
            super().__init__(name)
            self.placeholder = placeholder
        
        def render(self, indent=0):
            print("  " * indent + f"📝 [{self.placeholder}] _____")
    
    class Panel(GUIComponent):
        """面板组件（组合节点）"""
        
        def __init__(self, name):
            super().__init__(name)
            self._components: List[GUIComponent] = []
        
        def render(self, indent=0):
            print("  " * indent + f"📦 {self.name}")
            for component in self._components:
                component.render(indent + 1)
        
        def add_component(self, component):
            self._components.append(component)
        
        def remove_component(self, component):
            self._components.remove(component)
    
    # 创建GUI组件
    login_button = Button("登录按钮", "登录")
    register_button = Button("注册按钮", "注册")
    username_field = TextField("用户名", "请输入用户名")
    password_field = TextField("密码", "请输入密码")
    
    # 创建面板
    login_panel = Panel("登录面板")
    button_panel = Panel("按钮面板")
    main_panel = Panel("主面板")
    
    # 组合GUI组件
    login_panel.add_component(username_field)
    login_panel.add_component(password_field)
    
    button_panel.add_component(login_button)
    button_panel.add_component(register_button)
    
    main_panel.add_component(login_panel)
    main_panel.add_component(button_panel)
    
    # 渲染GUI
    print("🎨 GUI界面渲染:")
    main_panel.render()


if __name__ == "__main__":
    test_composite_pattern()
    test_organization_composite()
    test_gui_composite()
    
    print("\n=== 组合模式总结 ===")
    print("优点：")
    print("- 可以清楚地定义分层次的复杂对象")
    print("- 让客户端忽略了层次的差异，方便对整个层次结构进行控制")
    print("- 符合开闭原则，容易增加新的容器构件和叶子构件")
    print("\n缺点：")
    print("- 设计较复杂，客户端需要花更多时间理清类之间的层次关系")
    print("- 不容易限制容器中的构件")
    print("\n适用场景：")
    print("- 需要表示对象的部分-整体层次结构")
    print("- 希望用户忽略组合对象与单个对象的不同")
    print("- 结构可以具有任何级别的复杂性，而且是动态的")
