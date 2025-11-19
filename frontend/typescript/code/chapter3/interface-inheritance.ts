// 接口继承示例
function demonstrateInterfaceInheritance(): void {
    console.log("\n=== Interface Inheritance Demo ===");
    
    // 基本接口
    interface Shape {
        color: string;
    }
    
    // 单继承
    interface Square extends Shape {
        sideLength: number;
    }
    
    const square: Square = {
        color: "blue",
        sideLength: 10
    };
    
    console.log("Square:", square);
    console.log(`Square area: ${square.sideLength * square.sideLength}`);
    
    // 多级继承
    interface ColoredSquare extends Square {
        pattern: string;
    }
    
    const coloredSquare: ColoredSquare = {
        color: "red",
        sideLength: 5,
        pattern: "striped"
    };
    
    console.log("Colored Square:", coloredSquare);
    
    // 多继承
    interface Person {
        name: string;
    }
    
    interface Employee {
        employeeId: string;
    }
    
    interface Manager extends Person, Employee {
        teamSize: number;
    }
    
    const manager: Manager = {
        name: "John",
        employeeId: "EMP123",
        teamSize: 5
    };
    
    console.log("Manager:", manager);
    
    // 接口与类型别名的区别
    interface AnimalInterface {
        name: string;
        age: number;
    }
    
    type AnimalType = {
        name: string;
        age: number;
    };
    
    // 接口可以自动合并
    interface AnimalInterface {
        species: string;
    }
    
    // 类型别名不能合并，但可以通过交叉类型实现类似效果
    type ExtendedAnimalType = AnimalType & {
        species: string;
    };
    
    const animalFromInterface: AnimalInterface = {
        name: "Dog",
        age: 5,
        species: "Canis"
    };
    
    const animalFromType: ExtendedAnimalType = {
        name: "Cat",
        age: 3,
        species: "Felis"
    };
    
    console.log("Animal from interface:", animalFromInterface);
    console.log("Animal from type:", animalFromType);
    
    // 接口继承示例：汽车接口层次结构
    interface Vehicle {
        brand: string;
        model: string;
        year: number;
        start(): void;
        stop(): void;
    }
    
    interface MotorVehicle extends Vehicle {
        engineType: string;
        fuelType: string;
    }
    
    interface Car extends MotorVehicle {
        numberOfDoors: number;
        trunkCapacity: number;
    }
    
    interface ElectricCar extends Car {
        batteryCapacity: number;
        range: number;
        charge(): void;
    }
    
    const tesla: ElectricCar = {
        brand: "Tesla",
        model: "Model S",
        year: 2022,
        start() {
            console.log(`${this.brand} ${this.model} is starting silently...`);
        },
        stop() {
            console.log(`${this.brand} ${this.model} is stopping...`);
        },
        engineType: "Electric Motor",
        fuelType: "Electricity",
        numberOfDoors: 4,
        trunkCapacity: 800,
        batteryCapacity: 100,
        range: 400,
        charge() {
            console.log(`${this.brand} ${this.model} is charging...`);
        }
    };
    
    tesla.start();
    tesla.charge();
    tesla.stop();
}

demonstrateInterfaceInheritance();