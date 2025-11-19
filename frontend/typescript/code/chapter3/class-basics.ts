// 类基础示例
function demonstrateClassBasics(): void {
    console.log("\n=== Class Basics Demo ===");
    
    // 基本类定义
    class Person {
        // 属性
        public name: string;          // 公共属性，默认值
        private age: number;          // 私有属性
        protected gender: string;     // 受保护属性
        readonly id: number;          // 只读属性
        
        // 静态属性
        static species: string = "Homo sapiens";
        
        // 构造函数
        constructor(name: string, age: number, gender: string, id: number) {
            this.name = name;
            this.age = age;
            this.gender = gender;
            this.id = id;
        }
        
        // 公共方法
        public getInfo(): string {
            return `${this.name} is ${this.age} years old.`;
        }
        
        // 私有方法
        private calculateBirthYear(): number {
            return new Date().getFullYear() - this.age;
        }
        
        // 受保护方法
        protected getGender(): string {
            return this.gender;
        }
        
        // 静态方法
        static getSpecies(): string {
            return Person.species;
        }
        
        // 获取私有信息的公共方法
        public getBirthYear(): number {
            return this.calculateBirthYear();
        }
    }
    
    // 创建实例
    const person = new Person("Alice", 30, "female", 12345);
    
    // 访问公共成员
    console.log(person.name);       // 可以访问公共属性
    console.log(person.getInfo());   // 可以调用公共方法
    console.log(person.id);         // 可以访问只读属性
    
    // 访问静态成员
    console.log(Person.species);    // 访问静态属性
    console.log(Person.getSpecies()); // 调用静态方法
    
    // 访问受保护信息的方法
    console.log(person.getBirthYear()); // 1993 (假设当前是2023年)
    
    // 不能访问私有成员
    // console.log(person.age);      // 错误，无法访问私有属性
    // console.log(person.calculateBirthYear()); // 错误，无法调用私有方法
    
    // 参数属性简化写法
    class Employee {
        constructor(
            public employeeId: string,  // 自动创建公共属性并初始化
            private department: string,  // 自动创建私有属性并初始化
            protected position: string   // 自动创建受保护属性并初始化
        ) {}
        
        public getDepartment(): string {
            return this.department;
        }
    }
    
    const employee = new Employee("EMP123", "Engineering", "Developer");
    console.log(`Employee ID: ${employee.employeeId}`);
    console.log(`Department: ${employee.getDepartment()}`);
    // console.log(employee.department); // 错误，department是私有属性
    
    // 使用readonly参数属性
    class Product {
        constructor(
            public readonly productId: number,
            public name: string,
            private _price: number
        ) {}
        
        public get price(): number {
            return this._price;
        }
        
        public set price(newPrice: number) {
            if (newPrice >= 0) {
                this._price = newPrice;
            } else {
                throw new Error("Price cannot be negative");
            }
        }
    }
    
    const product = new Product(1, "Laptop", 999.99);
    console.log(`Product: ${product.name}, Price: $${product.price}`);
    
    // product.productId = 2; // 错误，productId是只读属性
    product.price = 899.99;
    console.log(`Updated price: $${product.price}`);
    
    // 类作为类型
    let person2: Person; // Person是类的类型
    person2 = new Person("Bob", 25, "male", 67890);
    console.log(person2.getInfo());
    
    // 类的构造函数类型
    let PersonConstructor: typeof Person = Person;
    let person3 = new PersonConstructor("Charlie", 35, "male", 11111);
    console.log(person3.getInfo());
}

demonstrateClassBasics();