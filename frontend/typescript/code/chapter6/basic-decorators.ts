// 基本装饰器示例
import "reflect-metadata";

// 基本类装饰器
function ClassDecorator(constructor: Function) {
    console.log("ClassDecorator called for:", constructor.name);
    
    // 可以修改类
    constructor.prototype.newProperty = "Added by decorator";
}

@ClassDecorator
class MyClass {
    constructor() {
        console.log("MyClass instantiated");
    }
    
    greet(): string {
        return "Hello from MyClass!";
    }
}

const myClass = new MyClass();
console.log("Greeting:", myClass.greet());
console.log("New property:", (myClass as any).newProperty);

// 类装饰器返回值可以替换类构造函数
function ClassReplacer<T extends { new(...args: any[]): {} }>(constructor: T) {
    return class extends constructor {
        newProperty = "New property from replacer";
        greeting = "override from replacer";
        
        greet(): string {
            return "Overridden greeting from replacer";
        }
    };
}

@ClassReplacer
class Greeter {
    property = "original property";
    greeting = "original greeting";
    
    greet(): string {
        return "Hello from original Greeter";
    }
}

const greeter = new Greeter();
console.log("Greeting:", greeter.greet());
console.log("New property:", greeter.newProperty);
console.log("Greeting property:", greeter.greeting);

// 基本方法装饰器
function MethodDecorator(
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor
) {
    console.log("MethodDecorator called on:", target.constructor.name, propertyKey);
    console.log("Method descriptor:", descriptor);
}

class MethodExample {
    @MethodDecorator
    greet(name: string): string {
        return `Hello, ${name}!`;
    }
}

const methodExample = new MethodExample();
console.log(methodExample.greet("TypeScript"));

// 基本访问器装饰器
function AccessorDecorator(
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor
) {
    console.log("AccessorDecorator called on:", target.constructor.name, propertyKey);
    
    const originalGetter = descriptor.get;
    const originalSetter = descriptor.set;
    
    if (originalGetter) {
        descriptor.get = function() {
            console.log(`Getting ${propertyKey}`);
            return originalGetter!.apply(this);
        };
    }
    
    if (originalSetter) {
        descriptor.set = function(value: any) {
            console.log(`Setting ${propertyKey} to:`, value);
            return originalSetter!.apply(this, [value]);
        };
    }
    
    return descriptor;
}

class AccessorExample {
    private _name: string = "";
    
    @AccessorDecorator
    get name(): string {
        return this._name;
    }
    
    set name(value: string) {
        this._name = value;
    }
}

const accessorExample = new AccessorExample();
accessorExample.name = "Alice";
console.log(accessorExample.name);

// 基本属性装饰器
function PropertyDecorator(target: any, propertyKey: string) {
    console.log("PropertyDecorator called on:", target.constructor.name, propertyKey);
    
    // 可以添加元数据
    Reflect.defineMetadata("required", true, target, propertyKey);
}

class PropertyExample {
    @PropertyDecorator
    id: number = 0;
    
    @PropertyDecorator
    name: string = "";
}

const propertyExample = new PropertyExample();
console.log("ID required:", Reflect.getMetadata("required", propertyExample, "id"));
console.log("Name required:", Reflect.getMetadata("required", propertyExample, "name"));

// 基本参数装饰器
function ParameterDecorator(
    target: any,
    methodName: string,
    parameterIndex: number
) {
    console.log("ParameterDecorator called on:", target.constructor.name, methodName, parameterIndex);
    
    // 可以添加参数验证
    const existingRequiredParameters = Reflect.getMetadata("requiredParameters", target) || [];
    existingRequiredParameters.push(parameterIndex);
    Reflect.defineMetadata("requiredParameters", existingRequiredParameters, target);
}

class ParameterExample {
    greet(
        @ParameterDecorator name: string,
        @ParameterDecorator age: number
    ): string {
        return `Hello, ${name}! You are ${age} years old.`;
    }
}

const parameterExample = new ParameterExample();
console.log(parameterExample.greet("Alice", 30));