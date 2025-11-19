// 类继承示例
function demonstrateClassInheritance(): void {
    console.log("\n=== Class Inheritance Demo ===");
    
    // 基类
    class Animal {
        protected name: string;
        
        constructor(name: string) {
            this.name = name;
        }
        
        public move(distance: number = 0): void {
            console.log(`${this.name} moved ${distance}m.`);
        }
        
        public makeSound(): void {
            console.log(`${this.name} makes a generic animal sound`);
        }
    }
    
    // 派生类
    class Dog extends Animal {
        constructor(name: string) {
            // 调用父类构造函数
            super(name);
        }
        
        public bark(): void {
            console.log(`${this.name} barks!`);
        }
        
        // 重写父类方法
        public move(distance: number = 5): void {
            console.log(`${this.name} is running...`);
            super.move(distance); // 调用父类方法
        }
        
        public makeSound(): void {
            this.bark();
        }
    }
    
    // 多级继承
    class Puppy extends Dog {
        constructor(name: string) {
            super(name);
        }
        
        public move(distance: number = 2): void {
            console.log(`${this.name} is waddling...`);
            super.move(distance);
        }
        
        public play(): void {
            console.log(`${this.name} is playing with a ball`);
        }
    }
    
    // 使用继承的类
    const animal = new Animal("Generic Animal");
    animal.move(10);
    animal.makeSound();
    
    const dog = new Dog("Buddy");
    dog.bark();
    dog.move(20);
    dog.makeSound();
    
    const puppy = new Puppy("Tiny");
    puppy.move(5);
    puppy.makeSound();
    puppy.play();
    
    // 抽象类示例
    abstract class Shape {
        protected color: string;
        
        constructor(color: string) {
            this.color = color;
        }
        
        // 抽象方法，没有实现
        abstract area(): number;
        
        // 普通方法，有实现
        display(): void {
            console.log(`This is a ${this.color} shape with area ${this.area()}`);
        }
        
        // 受保护的抽象方法
        protected abstract perimeter(): number;
        
        // 使用受保护抽象方法的方法
        public getInfo(): string {
            return `Area: ${this.area()}, Perimeter: ${this.perimeter()}`;
        }
    }
    
    // 实现抽象类
    class Circle extends Shape {
        constructor(color: string, private radius: number) {
            super(color);
        }
        
        // 实现抽象方法
        area(): number {
            return Math.PI * this.radius * this.radius;
        }
        
        // 实现受保护的抽象方法
        protected perimeter(): number {
            return 2 * Math.PI * this.radius;
        }
    }
    
    class Rectangle extends Shape {
        constructor(color: string, private width: number, private height: number) {
            super(color);
        }
        
        area(): number {
            return this.width * this.height;
        }
        
        protected perimeter(): number {
            return 2 * (this.width + this.height);
        }
    }
    
    // 使用抽象类和具体类
    const circle = new Circle("red", 5);
    circle.display();
    console.log(`Circle info: ${circle.getInfo()}`);
    
    const rectangle = new Rectangle("blue", 10, 20);
    rectangle.display();
    console.log(`Rectangle info: ${rectangle.getInfo()}`);
    
    // 多态示例
    const shapes: Shape[] = [
        new Circle("green", 3),
        new Rectangle("yellow", 4, 6),
        new Circle("purple", 2)
    ];
    
    shapes.forEach(shape => {
        shape.display();
        console.log(shape.getInfo());
    });
    
    // protected成员的访问
    class ShapeCalculator {
        public static calculateTotalArea(shapes: Shape[]): number {
            return shapes.reduce((total, shape) => total + shape.area(), 0);
        }
        
        public static printPerimeters(shapes: Shape[]): void {
            shapes.forEach(shape => {
                // 不能直接访问受保护的perimeter方法
                console.log(shape.getInfo()); // 使用公共方法获取周长
            });
        }
    }
    
    console.log(`Total area: ${ShapeCalculator.calculateTotalArea(shapes)}`);
    ShapeCalculator.printPerimeters(shapes);
}

demonstrateClassInheritance();