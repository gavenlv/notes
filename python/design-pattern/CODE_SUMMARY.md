# 代码示例总结

本文件总结了Python设计模式教程中的所有代码示例，提供了快速参考和运行指南。

## 运行所有示例

要运行所有示例，可以按照以下顺序执行：

```bash
cd code
python chapter1_design_pattern_basics.py
python chapter2_singleton_pattern.py
python chapter3_factory_method_pattern.py
python chapter4_builder_pattern.py
python chapter5_prototype_pattern.py
python chapter6_adapter_pattern.py
# ... 继续运行其他章节的示例
```

## 代码示例概述

### 第1章：设计模式基础概念

文件: `chapter1_design_pattern_basics.py`

主要内容：
- 六大设计原则的实现示例
- 单一职责原则、开闭原则、里氏替换原则等

### 第2章：单例模式

文件: `chapter2_singleton_pattern.py`

主要实现：
- 使用`__new__方法实现单例
- 使用装饰器实现单例
- 使用元类实现单例
- 线程安全的单例实现
- 应用场景：数据库连接池、日志记录器、配置管理器

### 第3章：工厂方法模式

文件: `chapter3_factory_method_pattern.py`

主要实现：
- 基本工厂方法实现
- 注册表工厂
- 应用场景：日志记录器工厂、支付处理工厂、数据库连接工厂
- 参数化工厂方法

### 第4章：建造者模式

文件: `chapter4_builder_pattern.py`

主要实现：
- 基本建造者模式
- 流畅接口(Fluent Interface)
- 应用场景：电脑配置、SQL查询构建、文档构建、配置管理
- 使用@dataclass的建造者

### 第5章：原型模式

文件: `chapter5_prototype_pattern.py`

主要实现：
- 浅拷贝和深拷贝
- 注册表原型
- 应用场景：游戏对象克隆、文档模板、图形编辑器
- Python特殊的克隆实现

### 第6章：适配器模式

文件: `chapter6_adapter_pattern.py`

主要实现：
- 对象适配器和类适配器
- 双向适配器和默认适配器
- 应用场景：第三方库适配、数据格式适配、多媒体播放器
- Python鸭子类型适配

### 第7章：桥接模式

文件: `chapter7_bridge_pattern.py`

主要实现：
- 抽象和实现分离
- 设备与遥控器的桥接示例
- 应用场景：跨平台UI、数据库连接

### 第8章：组合模式

文件: `chapter8_composite_pattern.py`

主要实现：
- 树形结构管理
- 文件系统示例
- 应用场景：菜单系统、组织结构

### 第9章：装饰器模式

文件: `chapter9_decorator_pattern.py`

主要实现：
- Python装饰器语法
- 函数装饰器和类装饰器
- 应用场景：日志记录、权限检查、缓存

### 第10章：外观模式

文件: `chapter10_facade_pattern.py`

主要实现：
- 简化复杂子系统接口
- 多媒体播放器外观
- 应用场景：API封装、系统集成

### 第11章：享元模式

文件: `chapter11_flyweight_pattern.py`

主要实现：
- 对象共享池
- 字符渲染示例
- 应用场景：游戏开发、文本编辑器

### 第12章：代理模式

文件: `chapter12_proxy_pattern.py`

主要实现：
- 虚拟代理、保护代理、远程代理
- 图片加载代理示例
- 应用场景：延迟加载、访问控制

### 第13章：责任链模式

文件: `chapter13_chain_of_responsibility_pattern.py`

主要实现：
- 请求处理链
- 日志级别处理示例
- 应用场景：审批流程、异常处理

### 第14章：命令模式

文件: `chapter14_command_pattern.py`

主要实现：
- 命令封装
- 文本编辑器示例
- 应用场景：撤销/重做、任务队列

### 第15章：解释器模式

文件: `chapter15_interpreter_pattern.py`

主要实现：
- 语法解析树
- 简单计算器示例
- 应用场景：配置文件解析、查询语言

### 第16章：迭代器模式

文件: `chapter16_iterator_pattern.py`

主要实现：
- 自定义迭代器
- 集合遍历示例
- 应用场景：数据结构遍历、分页查询

### 第17章：中介者模式

文件: `chapter17_mediator_pattern.py`

主要实现：
- 对象间通信中介
- 聊天室示例
- 应用场景：GUI组件协调、系统事件处理

### 第18章：备忘录模式

文件: `chapter18_memento_pattern.py`

主要实现：
- 状态保存和恢复
- 文本编辑器撤销功能
- 应用场景：游戏存档、配置管理

### 第19章：观察者模式

文件: `chapter19_observer_pattern.py`

主要实现：
- 发布-订阅机制
- 事件通知系统
- 应用场景：GUI事件处理、数据同步

### 第20章：状态模式

文件: `chapter20_state_pattern.py`

主要实现：
- 状态转换管理
- 电梯状态示例
- 应用场景：工作流管理、游戏状态

### 第21章：策略模式

文件: `chapter21_strategy_pattern.py`

主要实现：
- 算法封装和替换
- 排序策略示例
- 应用场景：支付方式、压缩算法

### 第22章：模板方法模式

文件: `chapter22_template_method_pattern.py`

主要实现：
- 算法骨架定义
- 数据导出示例
- 应用场景：框架设计、流程控制

### 第23章：访问者模式

文件: `chapter23_visitor_pattern.py`

主要实现：
- 对象结构操作分离
- 文档遍历示例
- 应用场景：编译器、数据分析

### 第24章：设计模式实战项目

文件: `chapter24_practical_project.py`

主要模块：
1. **基础架构**: 数据库连接池、日志记录器
2. **图书管理**: 图书工厂、原型模式
3. **用户管理**: 认证适配器
4. **购物车**: 组合模式、装饰器模式
5. **订单处理**: 建造者模式、状态模式
6. **支付处理**: 策略模式、适配器模式
7. **事件通知**: 观察者模式
8. **系统接口**: 外观模式

## 常见代码模式

### 单例模式实现

```python
class Singleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### 工厂方法实现

```python
from abc import ABC, abstractmethod

class Creator(ABC):
    @abstractmethod
    def factory_method(self):
        pass

class ConcreteCreator(Creator):
    def factory_method(self):
        return ConcreteProduct()
```

### 建造者模式实现

```python
class Builder:
    def __init__(self):
        self.product = Product()
    
    def set_feature(self, value):
        self.product.feature = value
        return self
    
    def build(self):
        return self.product
```

### 适配器模式实现

```python
class Adapter(Target):
    def __init__(self, adaptee):
        self._adaptee = adaptee
    
    def request(self):
        return self._adaptee.specific_request()
```

## 调试技巧

1. **使用print语句**: 在关键位置添加print语句，观察程序执行流程
2. **使用调试器**: 使用Python的pdb或其他IDE调试器
3. **日志记录**: 使用logging模块记录程序执行信息
4. **单元测试**: 编写单元测试验证代码的正确性

## 扩展练习

1. **修改示例**: 尝试修改示例代码，添加新功能
2. **组合模式**: 尝试组合多种设计模式解决问题
3. **实际应用**: 将设计模式应用到自己的项目中
4. **性能测试**: 比较使用设计模式前后的性能差异

## 常见问题

### Q: 如何选择合适的设计模式？

A: 首先理解问题场景，然后查看每种模式的应用场景，选择最匹配的模式。不要为了使用模式而使用模式。

### Q: 设计模式会使代码变得复杂吗？

A: 适当使用设计模式会提高代码的可维护性和扩展性，但过度使用会增加复杂性。需要权衡利弊。

### Q: Python中的设计模式实现与Java有什么不同？

A: Python是动态语言，有鸭子类型、装饰器等特性，使得某些模式的实现更加简洁和灵活。

### Q: 是否需要记住所有设计模式？

A: 不需要死记硬背，理解模式的本质和适用场景更重要。随着经验积累，自然会掌握常用模式。

## 下一步

1. 深入研究每种模式的变种和应用
2. 阅读其他设计模式相关书籍和文章
3. 在实际项目中尝试应用设计模式
4. 学习Python特有的设计模式实现方式

希望这些代码示例能帮助你更好地理解和使用Python设计模式！