// 类实现接口示例
function demonstrateClassImplementsInterface(): void {
    console.log("\n=== Class Implements Interface Demo ===");
    
    // 定义接口
    interface ClockInterface {
        currentTime: Date;
        setTime(d: Date): void;
    }
    
    interface Alarm {
        alarmTime: Date;
        setAlarm(time: Date): void;
        ring(): void;
    }
    
    // 实现单个接口
    class DigitalClock implements ClockInterface {
        currentTime: Date = new Date();
        
        setTime(d: Date): void {
            this.currentTime = d;
            console.log(`Time set to: ${this.currentTime}`);
        }
    }
    
    const digitalClock = new DigitalClock();
    digitalClock.setTime(new Date());
    console.log(`Current time: ${digitalClock.currentTime}`);
    
    // 实现多个接口
    class AlarmClock implements ClockInterface, Alarm {
        currentTime: Date = new Date();
        alarmTime: Date = new Date();
        
        setTime(d: Date): void {
            this.currentTime = d;
        }
        
        setAlarm(time: Date): void {
            this.alarmTime = time;
            console.log(`Alarm set for: ${this.alarmTime}`);
        }
        
        ring(): void {
            console.log("Alarm is ringing! Time to wake up!");
        }
    }
    
    const alarmClock = new AlarmClock();
    alarmClock.setTime(new Date());
    alarmClock.setAlarm(new Date(Date.now() + 3600000)); // 1小时后
    alarmClock.ring();
    
    // 定义和实现更复杂的接口
    interface Logger {
        log(message: string): void;
        error(message: string): void;
        warn(message: string): void;
        info(message: string): void;
    }
    
    interface Configurable {
        configure(options: Record<string, any>): void;
        getOptions(): Record<string, any>;
    }
    
    class ConsoleLogger implements Logger, Configurable {
        private options: Record<string, any> = {
            timestamp: true,
            level: "info"
        };
        
        log(message: string): void {
            const prefix = this.options.timestamp ? `[${new Date().toISOString()}] ` : "";
            console.log(`${prefix}[LOG] ${message}`);
        }
        
        error(message: string): void {
            const prefix = this.options.timestamp ? `[${new Date().toISOString()}] ` : "";
            console.error(`${prefix}[ERROR] ${message}`);
        }
        
        warn(message: string): void {
            const prefix = this.options.timestamp ? `[${new Date().toISOString()}] ` : "";
            console.warn(`${prefix}[WARN] ${message}`);
        }
        
        info(message: string): void {
            const prefix = this.options.timestamp ? `[${new Date().toISOString()}] ` : "";
            console.info(`${prefix}[INFO] ${message}`);
        }
        
        configure(options: Record<string, any>): void {
            this.options = { ...this.options, ...options };
            console.log("Logger configured with options:", this.options);
        }
        
        getOptions(): Record<string, any> {
            return { ...this.options };
        }
    }
    
    // 使用实现多个接口的类
    const logger = new ConsoleLogger();
    logger.info("Starting application");
    logger.warn("Low disk space");
    logger.error("Database connection failed");
    
    logger.configure({ timestamp: true, level: "debug" });
    logger.info("Application configuration completed");
    
    // 接口继承和类实现
    interface Vehicle {
        brand: string;
        model: string;
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
    
    class ElectricCar implements Car {
        constructor(
            public brand: string,
            public model: string,
            public engineType: string,
            public fuelType: string,
            public numberOfDoors: number,
            public trunkCapacity: number,
            public batteryCapacity: number
        ) {}
        
        start(): void {
            console.log(`${this.brand} ${this.model} is starting silently...`);
        }
        
        stop(): void {
            console.log(`${this.brand} ${this.model} is stopping...`);
        }
        
        charge(): void {
            console.log(`${this.brand} ${this.model} is charging...`);
        }
        
        getBatteryInfo(): string {
            return `Battery capacity: ${this.batteryCapacity} kWh`;
        }
    }
    
    const tesla = new ElectricCar(
        "Tesla", 
        "Model S", 
        "Electric Motor",
        "Electricity",
        4,
        800,
        100
    );
    
    tesla.start();
    console.log(tesla.getBatteryInfo());
    tesla.charge();
    tesla.stop();
    
    // 接口与类的协作
    interface DataRepository<T> {
        findById(id: number): T | null;
        save(entity: T): T;
        delete(id: number): boolean;
        findAll(): T[];
    }
    
    class InMemoryRepository<T> implements DataRepository<T> {
        private entities: Map<number, T> = new Map();
        private nextId: number = 1;
        
        findById(id: number): T | null {
            return this.entities.get(id) || null;
        }
        
        save(entity: T): T {
            const id = this.nextId++;
            (entity as any).id = id;
            this.entities.set(id, entity);
            return entity;
        }
        
        delete(id: number): boolean {
            return this.entities.delete(id);
        }
        
        findAll(): T[] {
            return Array.from(this.entities.values());
        }
    }
    
    // 用户实体类型
    interface User {
        id?: number;
        name: string;
        email: string;
    }
    
    // 使用泛型接口实现
    const userRepository = new InMemoryRepository<User>();
    
    const user1 = userRepository.save({ name: "Alice", email: "alice@example.com" });
    const user2 = userRepository.save({ name: "Bob", email: "bob@example.com" });
    
    console.log("Saved users:", userRepository.findAll());
    console.log("User with ID 1:", userRepository.findById(1));
    
    userRepository.delete(2);
    console.log("Users after deletion:", userRepository.findAll());
}

demonstrateClassImplementsInterface();