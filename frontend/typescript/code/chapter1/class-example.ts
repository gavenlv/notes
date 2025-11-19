// 类示例
// 1. 基本类定义
class Animal {
    // 属性
    name: string;
    
    // 构造函数
    constructor(name: string) {
        this.name = name;
    }
    
    // 方法
    move(distanceInMeters: number = 0): void {
        console.log(`${this.name} moved ${distanceInMeters}m.`);
    }
}

// 2. 继承
class Dog extends Animal {
    constructor(name: string) {
        // 调用父类构造函数
        super(name);
    }
    
    // 重写父类方法
    move(distanceInMeters = 5): void {
        console.log(`${this.name} is running...`);
        super.move(distanceInMeters);
    }
    
    // 新方法
    bark(): void {
        console.log(`${this.name} barks!`);
    }
}

// 3. 访问修饰符
class Person {
    // public - 公共属性，默认修饰符
    public name: string;
    
    // private - 私有属性，只能在类内部访问
    private age: number;
    
    // protected - 受保护属性，可以在派生类中访问
    protected gender: string;
    
    // readonly - 只读属性
    readonly id: number;
    
    constructor(name: string, age: number, gender: string, id: number) {
        this.name = name;
        this.age = age;
        this.gender = gender;
        this.id = id;
    }
    
    // public方法
    public introduce(): string {
        return `I'm ${this.name}, ${this.age} years old.`;
    }
    
    // private方法
    private calculateBirthYear(): number {
        return new Date().getFullYear() - this.age;
    }
    
    // protected方法
    protected getGender(): string {
        return this.gender;
    }
}

// 4. 存取器（getters/setters）
class Employee {
    private _fullName: string = "";
    
    get fullName(): string {
        return this._fullName;
    }
    
    set fullName(newName: string) {
        if (newName.length > 0) {
            this._fullName = newName;
        } else {
            throw new Error("Name cannot be empty");
        }
    }
}

// 5. 静态属性和方法
class MathHelper {
    // 静态属性
    static PI: number = 3.14159;
    
    // 静态方法
    static calculateCircumference(radius: number): number {
        return 2 * MathHelper.PI * radius;
    }
    
    // 实例方法
    calculateArea(radius: number): number {
        return MathHelper.PI * radius * radius;
    }
}

// 6. 抽象类
abstract class Shape {
    abstract area(): number; // 抽象方法
    
    // 普通方法
    display(): void {
        console.log(`This is a shape with area ${this.area()}`);
    }
}

// 实现抽象类
class Circle extends Shape {
    constructor(private radius: number) {
        super();
    }
    
    // 实现抽象方法
    area(): number {
        return Math.PI * this.radius * this.radius;
    }
}

class Rectangle extends Shape {
    constructor(private width: number, private height: number) {
        super();
    }
    
    area(): number {
        return this.width * this.height;
    }
}

// 7. 类实现接口
interface ClockInterface {
    tick(): void;
}

class DigitalClock implements ClockInterface {
    constructor() {}
    
    tick(): void {
        console.log("beep beep");
    }
}

class AnalogClock implements ClockInterface {
    constructor() {}
    
    tick(): void {
        console.log("tick tock");
    }
}

// 8. 构造函数的参数属性
class Car {
    // 使用参数属性简化代码
    constructor(
        public make: string,
        public model: string,
        public year: number,
        private vin: string
    ) {}
    
    getInfo(): string {
        return `${this.year} ${this.make} ${this.model}`;
    }
    
    getVin(): string {
        return this.vin; // 只能通过方法访问私有属性
    }
}

// 演示所有类特性
function demonstrateClasses(): void {
    console.log("Class Examples:");
    console.log("================");
    
    // 1. 基本类
    const animal = new Animal("Animal");
    animal.move(10);
    
    // 2. 继承
    const dog = new Dog("Buddy");
    dog.bark();
    dog.move(20);
    
    // 3. 访问修饰符
    const person = new Person("Alice", 30, "female", 12345);
    console.log(person.introduce());
    console.log("Person ID:", person.id);
    // person.age; // 错误，age是私有属性
    
    // 4. 存取器
    const employee = new Employee();
    employee.fullName = "John Doe";
    console.log("Employee name:", employee.fullName);
    
    // 5. 静态属性和方法
    console.log("PI value:", MathHelper.PI);
    console.log("Circumference of radius 5:", MathHelper.calculateCircumference(5));
    
    const mathHelper = new MathHelper();
    console.log("Area of radius 5:", mathHelper.calculateArea(5));
    
    // 6. 抽象类
    const circle = new Circle(5);
    circle.display();
    
    const rectangle = new Rectangle(10, 20);
    rectangle.display();
    
    // 7. 接口实现
    const digitalClock = new DigitalClock();
    digitalClock.tick();
    
    const analogClock = new AnalogClock();
    analogClock.tick();
    
    // 8. 参数属性
    const car = new Car("Toyota", "Camry", 2022, "1HGBH41JXMN109186");
    console.log("Car info:", car.getInfo());
    console.log("Car VIN:", car.getVin());
}

// 调用函数
demonstrateClasses();