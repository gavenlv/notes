# Java设计模式详解

本项目包含了Java中常见的23种设计模式的详细说明和代码示例。

## 创建型模式 (Creational Patterns)

1. [单例模式 (Singleton Pattern)](2-单例模式详解.md) - 确保一个类只有一个实例，并提供全局访问点
2. [工厂方法模式 (Factory Method Pattern)](3-工厂方法模式详解.md) - 定义一个创建对象的接口，让子类决定实例化哪个类
3. [抽象工厂模式 (Abstract Factory Pattern)](4-抽象工厂模式详解.md) - 提供一个创建一系列相关或相互依赖对象的接口，而无需指定它们具体的类
4. [建造者模式 (Builder Pattern)](5-建造者模式详解.md) - 将一个复杂对象的构建与它的表示分离，使得同样的构建过程可以创建不同的表示
5. [原型模式 (Prototype Pattern)](6-原型模式详解.md) - 用原型实例指定创建对象的种类，并且通过拷贝这些原型创建新的对象

## 结构型模式 (Structural Patterns)

6. [适配器模式 (Adapter Pattern)](7-适配器模式详解.md) - 将一个类的接口转换成客户希望的另外一个接口
7. [桥接模式 (Bridge Pattern)](8-桥接模式详解.md) - 将抽象部分与它的实现部分分离，使它们都可以独立地变化
8. [装饰器模式 (Decorator Pattern)](9-装饰器模式详解.md) - 动态地给一个对象添加一些额外的职责
9. [外观模式 (Facade Pattern)](10-外观模式详解.md) - 为子系统中的一组接口提供一个一致的界面
10. [享元模式 (Flyweight Pattern)](11-享元模式详解.md) - 运用共享技术有效地支持大量细粒度的对象
11. [代理模式 (Proxy Pattern)](12-代理模式详解.md) - 为其他对象提供一种代理以控制对这个对象的访问

## 行为型模式 (Behavioral Patterns)

12. [责任链模式 (Chain of Responsibility Pattern)](13-责任链模式详解.md) - 使多个对象都有机会处理请求，从而避免请求的发送者和接收者之间的耦合关系
13. [命令模式 (Command Pattern)](14-命令模式详解.md) - 将一个请求封装为一个对象，从而使你可用不同的请求对客户进行参数化
14. [解释器模式 (Interpreter Pattern)](15-解释器模式详解.md) - 给定一个语言，定义它的文法的一种表示，并定义一个解释器
15. [迭代器模式 (Iterator Pattern)](16-迭代器模式详解.md) - 提供一种方法顺序访问一个聚合对象中各个元素，而又不需暴露该对象的内部表示
16. [中介者模式 (Mediator Pattern)](17-中介者模式详解.md) - 用一个中介对象来封装一系列的对象交互
17. [备忘录模式 (Memento Pattern)](18-备忘录模式详解.md) - 在不破坏封装性的前提下，捕获一个对象的内部状态，并在该对象之外保存这个状态
18. [观察者模式 (Observer Pattern)](19-观察者模式详解.md) - 定义对象间的一种一对多的依赖关系，当一个对象的状态发生改变时，所有依赖于它的对象都得到通知并被自动更新
19. [状态模式 (State Pattern)](20-状态模式详解.md) - 允许一个对象在其内部状态改变时改变它的行为
20. [策略模式 (Strategy Pattern)](21-策略模式详解.md) - 定义一系列的算法，把它们一个个封装起来，并且使它们可相互替换
21. [模板方法模式 (Template Method Pattern)](22-模板方法模式详解.md) - 定义一个操作中的算法的骨架，而将一些步骤延迟到子类中
22. [访问者模式 (Visitor Pattern)](23-访问者模式详解.md) - 表示一个作用于某对象结构中的各元素的操作

## 代码示例

每个设计模式都有对应的Java代码示例，可以直接运行查看效果：
- [Chapter1Example.java](code/Chapter1Example.java) - 设计模式基础概念示例
- [Chapter2Example.java](code/Chapter2Example.java) - 单例模式示例
- [Chapter3Example.java](code/Chapter3Example.java) - 工厂方法模式示例
- [Chapter4Example.java](code/Chapter4Example.java) - 抽象工厂模式示例
- [Chapter5Example.java](code/Chapter5Example.java) - 建造者模式示例
- [Chapter6Example.java](code/Chapter6Example.java) - 原型模式示例
- [Chapter7Example.java](code/Chapter7Example.java) - 适配器模式示例
- [Chapter8Example.java](code/Chapter8Example.java) - 桥接模式示例
- [Chapter9Example.java](code/Chapter9Example.java) - 装饰器模式示例
- [Chapter10Example.java](code/Chapter10Example.java) - 外观模式示例
- [Chapter11Example.java](code/Chapter11Example.java) - 享元模式示例
- [Chapter12Example.java](code/Chapter12Example.java) - 代理模式示例
- [Chapter13Example.java](code/Chapter13Example.java) - 责任链模式示例
- [Chapter14Example.java](code/Chapter14Example.java) - 命令模式示例
- [Chapter15Example.java](code/Chapter15Example.java) - 解释器模式示例
- [Chapter16Example.java](code/Chapter16Example.java) - 迭代器模式示例
- [Chapter17Example.java](code/Chapter17Example.java) - 中介者模式示例
- [Chapter18Example.java](code/Chapter18Example.java) - 备忘录模式示例
- [Chapter19Example.java](code/Chapter19Example.java) - 观察者模式示例
- [Chapter20Example.java](Chapter20Example.java) - 状态模式示例
- [Chapter21Example.java](Chapter21Example.java) - 策略模式示例
- [Chapter22Example.java](Chapter22Example.java) - 模板方法模式示例

## 使用说明

1. 克隆或下载本项目
2. 使用任意Java IDE打开项目
3. 编译并运行相应的示例代码
4. 查看详细的文档了解设计模式的原理和应用场景

## 学习建议

1. 先理解每种设计模式的概念和适用场景
2. 阅读代码示例，理解其实现方式
3. 尝试修改示例代码，加深理解
4. 在实际项目中寻找应用设计模式的机会