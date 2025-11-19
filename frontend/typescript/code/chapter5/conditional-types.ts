// 条件类型示例
function demonstrateConditionalTypes(): void {
    console.log("\n=== Conditional Types Demo ===");
    
    // 基本条件类型
    type IsString<T> = T extends string ? true : false;
    
    type Test1 = IsString<string>; // true
    type Test2 = IsString<number>; // false
    
    // 使用条件类型创建函数返回类型
    function process<T>(value: T): T extends string ? string : number {
        if (typeof value === "string") {
            return value.toUpperCase() as any;
        }
        return value as any;
    }
    
    const result1 = process("hello"); // string
    const result2 = process(42);      // number
    
    console.log(`process("hello"): ${result1} (type: ${typeof result1})`);
    console.log(`process(42): ${result2} (type: ${typeof result2})`);
    
    // 条件类型与泛型约束结合
    type NonNullable<T> = T extends null | undefined ? never : T;
    
    function filterNullable<T>(value: T): NonNullable<T> {
        return value as NonNullable<T>;
    }
    
    const filtered1 = filterNullable("hello"); // string
    console.log(`filterNullable("hello"): ${filtered1}`);
    
    // 分布式条件类型
    type ToArray<T> = T extends any ? T[] : never;
    
    type StringOrNumberArray = ToArray<string | number>;
    // 结果: string[] | number[]
    
    // 提取字符串类型
    type ExtractString<T> = T extends string ? T : never;
    
    type StringTypes = ExtractString<string | number | boolean>;
    // 结果: string
    
    // 使用infer关键字进行类型推断
    type ReturnType<T> = T extends (...args: any[]) => infer R ? R : any;
    
    function greet(name: string): string {
        return `Hello, ${name}`;
    }
    
    type GreetReturnType = ReturnType<typeof greet>; // string
    
    // 提取函数参数类型
    type Parameters<T> = T extends (...args: infer P) => any ? P : never;
    
    type GreetParameters = Parameters<typeof greet>; // [string]
    
    // 提取数组元素类型
    type ElementOf<T> = T extends (infer U)[] ? U : never;
    
    type StringArrayElement = ElementOf<string[]>; // string
    
    // 提取Promise的值类型
    type UnpackPromise<T> = T extends Promise<infer U> ? U : never;
    
    type PromiseValue = UnpackPromise<Promise<string>>; // string
    
    // 条件类型中的递归
    type DeepPartial<T> = {
        [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
    };
    
    interface TreeNode {
        value: string;
        left?: TreeNode;
        right?: TreeNode;
    }
    
    type PartialTreeNode = DeepPartial<TreeNode>;
    
    // 高级条件类型：创建类型安全的事件系统
    interface Event {
        type: string;
        timestamp: number;
    }
    
    interface ClickEvent extends Event {
        type: "click";
        x: number;
        y: number;
    }
    
    interface KeyboardEvent extends Event {
        type: "keydown" | "keyup";
        key: string;
        code: string;
    }
    
    interface EventTypeMap {
        click: ClickEvent;
        keydown: KeyboardEvent;
        keyup: KeyboardEvent;
    }
    
    function createEventListener<T extends keyof EventTypeMap>(
        eventType: T,
        handler: (event: EventTypeMap[T]) => void
    ): void {
        console.log(`Event listener for ${eventType} created`);
        
        // 模拟事件触发
        setTimeout(() => {
            let mockEvent: Event;
            
            switch (eventType) {
                case "click":
                    mockEvent = {
                        type: "click",
                        timestamp: Date.now(),
                        x: 100,
                        y: 200
                    } as EventTypeMap[T];
                    break;
                case "keydown":
                case "keyup":
                    mockEvent = {
                        type: eventType,
                        timestamp: Date.now(),
                        key: "Enter",
                        code: "Enter"
                    } as EventTypeMap[T];
                    break;
                default:
                    return;
            }
            
            handler(mockEvent as EventTypeMap[T]);
        }, 1000);
    }
    
    createEventListener("click", (event) => {
        console.log(`Click at (${event.x}, ${event.y})`);
    });
    
    createEventListener("keydown", (event) => {
        console.log(`Key pressed: ${event.key} (${event.code})`);
    });
    
    console.log("Event listeners will be triggered in 1 second...");
    
    // 条件类型用于函数重载
    interface ValidationRule<T> {
        validate(value: T): boolean;
        getErrorMessage(): string;
    }
    
    type ValidationResult<T> = T extends string 
        ? string 
        : T extends number 
            ? number 
            : T extends boolean 
                ? boolean
                : T extends Array<any>
                    ? Array<any>
                    : any;
    
    function validateAndTransform<T>(value: T, rule: ValidationRule<T>): ValidationResult<T> {
        if (rule.validate(value)) {
            return value as ValidationResult<T>;
        }
        
        // 根据类型返回默认值
        if (typeof value === "string") {
            return "" as ValidationResult<T>;
        } else if (typeof value === "number") {
            return 0 as ValidationResult<T>;
        } else if (typeof value === "boolean") {
            return false as ValidationResult<T>;
        } else if (Array.isArray(value)) {
            return [] as ValidationResult<T>;
        }
        
        return value as ValidationResult<T>;
    }
    
    // 实现一些验证规则
    const stringRule: ValidationRule<string> = {
        validate(value) {
            return value.length > 0;
        },
        getErrorMessage() {
            return "String cannot be empty";
        }
    };
    
    const numberRule: ValidationRule<number> = {
        validate(value) {
            return value >= 0;
        },
        getErrorMessage() {
            return "Number must be non-negative";
        }
    };
    
    const booleanRule: ValidationRule<boolean> = {
        validate(value) {
            return value === true;
        },
        getErrorMessage() {
            return "Boolean must be true";
        }
    };
    
    const arrayRule: ValidationRule<Array<any>> = {
        validate(value) {
            return value.length > 0;
        },
        getErrorMessage() {
            return "Array cannot be empty";
        }
    };
    
    // 测试验证函数
    const validStringResult = validateAndTransform("Hello", stringRule);
    const invalidStringResult = validateAndTransform("", stringRule);
    
    const validNumberResult = validateAndTransform(42, numberRule);
    const invalidNumberResult = validateAndTransform(-5, numberRule);
    
    const validBooleanResult = validateAndTransform(true, booleanRule);
    const invalidBooleanResult = validateAndTransform(false, booleanRule);
    
    const validArrayResult = validateAndTransform([1, 2, 3], arrayRule);
    const invalidArrayResult = validateAndTransform([], arrayRule);
    
    console.log("Validation results:");
    console.log(`Valid string: ${validStringResult}`);
    console.log(`Invalid string: ${invalidStringResult}`);
    console.log(`Valid number: ${validNumberResult}`);
    console.log(`Invalid number: ${invalidNumberResult}`);
    console.log(`Valid boolean: ${validBooleanResult}`);
    console.log(`Invalid boolean: ${invalidBooleanResult}`);
    console.log(`Valid array: ${validArrayResult}`);
    console.log(`Invalid array: ${invalidArrayResult}`);
}

demonstrateConditionalTypes();