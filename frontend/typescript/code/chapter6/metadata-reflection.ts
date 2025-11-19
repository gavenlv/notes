// 元数据反射示例
import "reflect-metadata";

// 定义元数据键
const DESIGN_TYPE = "design:type";
const DESIGN_PARAMTYPES = "design:paramtypes";
const DESIGN_RETURN_TYPE = "design:returntype";

// 自定义元数据键
const VALIDATION_RULES = "validation:rules";
const API_ENDPOINT = "api:endpoint";
const ENTITY_METADATA = "entity:table";
const COLUMN_METADATA = "column:info";

// 定义元数据类型
interface ValidationRule {
    validate: (value: any) => boolean;
    message: string;
}

interface ColumnInfo {
    type?: string;
    length?: number;
    nullable?: boolean;
    primary?: boolean;
    autoIncrement?: boolean;
}

// 添加元数据的装饰器
function AddValidationRule(rule: ValidationRule) {
    return function(target: any, propertyKey: string) {
        const existingRules = Reflect.getMetadata(VALIDATION_RULES, target, propertyKey) || [];
        existingRules.push(rule);
        Reflect.defineMetadata(VALIDATION_RULES, existingRules, target, propertyKey);
    };
}

// API端点装饰器
function ApiEndpoint(endpoint: string) {
    return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
        Reflect.defineMetadata(API_ENDPOINT, endpoint, target, propertyKey);
    };
}

// 实体装饰器
function Entity(tableName: string) {
    return function(constructor: Function) {
        Reflect.defineMetadata(ENTITY_METADATA, tableName, constructor);
    };
}

// 列装饰器
function Column(options: ColumnInfo = {}) {
    return function(target: any, propertyKey: string) {
        const columnInfo: ColumnInfo = options || {};
        
        // 如果没有指定类型，尝试从设计时类型推断
        if (!columnInfo.type) {
            const designType = Reflect.getMetadata(DESIGN_TYPE, target, propertyKey);
            
            if (designType) {
                switch (designType) {
                    case String:
                        columnInfo.type = "string";
                        break;
                    case Number:
                        columnInfo.type = "number";
                        break;
                    case Boolean:
                        columnInfo.type = "boolean";
                        break;
                    case Date:
                        columnInfo.type = "date";
                        break;
                }
            }
        }
        
        Reflect.defineMetadata(COLUMN_METADATA, columnInfo, target, propertyKey);
    };
}

// 主键装饰器
function PrimaryKey(target: any, propertyKey: string) {
    const columnInfo: ColumnInfo = {
        primary: true,
        autoIncrement: true
    };
    Reflect.defineMetadata(COLUMN_METADATA, columnInfo, target, propertyKey);
}

// 自动验证装饰器
function AutoValidate(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;
    
    descriptor.value = function(...args: any[]) {
        const validationRules = Reflect.getMetadata(VALIDATION_RULES, target, propertyKey) || [];
        
        for (const rule of validationRules) {
            for (const arg of args) {
                if (!rule.validate(arg)) {
                    throw new Error(rule.message);
                }
            }
        }
        
        return originalMethod.apply(this, args);
    };
    
    return descriptor;
}

// 实体类示例
@Entity("users")
class User {
    @PrimaryKey
    @Column()
    id: number = 0;
    
    @Column({ type: "string", length: 100, nullable: false })
    name: string = "";
    
    @Column({ type: "string", length: 255, nullable: false })
    email: string = "";
    
    @Column({ type: "number", nullable: true })
    age?: number;
    
    @Column({ type: "boolean", nullable: false, default: true })
    active: boolean = true;
    
    @Column({ type: "date" })
    createdAt: Date = new Date();
    
    constructor() {
        this.createdAt = new Date();
    }
}

// API控制器示例
class UserController {
    @ApiEndpoint("/users")
    @AddValidationRule({
        validate: (value) => typeof value === "object" && value.name && value.email,
        message: "Invalid user data: name and email are required"
    })
    @AutoValidate
    createUser(userData: any): User {
        console.log("Creating user:", userData);
        const user = new User();
        Object.assign(user, userData);
        return user;
    }
    
    @ApiEndpoint("/users/:id")
    @AddValidationRule({
        validate: (value) => typeof value === "string" || typeof value === "number",
        message: "Invalid user ID"
    })
    @AutoValidate
    getUser(userId: any): User | null {
        console.log("Getting user:", userId);
        // 模拟从数据库获取用户
        const user = new User();
        user.id = typeof userId === "number" ? userId : parseInt(userId);
        user.name = "Sample User";
        user.email = "user@example.com";
        return user;
    }
}

// 元数据读取器
class MetadataReader {
    // 获取实体表名
    static getEntityTableName(constructor: Function): string {
        return Reflect.getMetadata(ENTITY_METADATA, constructor) || constructor.name;
    }
    
    // 获取实体所有列信息
    static getEntityColumns(constructor: Function): Record<string, ColumnInfo> {
        const columns: Record<string, ColumnInfo> = {};
        const prototype = constructor.prototype;
        const propertyNames = Object.getOwnPropertyNames(prototype);
        
        for (const propertyName of propertyNames) {
            const columnInfo = Reflect.getMetadata(COLUMN_METADATA, prototype, propertyName);
            if (columnInfo) {
                columns[propertyName] = columnInfo;
            }
        }
        
        return columns;
    }
    
    // 获取实体的主键列名
    static getPrimaryKey(constructor: Function): string | null {
        const columns = this.getEntityColumns(constructor);
        
        for (const [columnName, columnInfo] of Object.entries(columns)) {
            if (columnInfo.primary) {
                return columnName;
            }
        }
        
        return null;
    }
    
    // 获取API端点
    static getApiEndpoint(target: any, propertyKey: string): string | null {
        return Reflect.getMetadata(API_ENDPOINT, target, propertyKey) || null;
    }
    
    // 获取参数类型
    static getParameterTypes(target: any, propertyKey: string): any[] {
        return Reflect.getMetadata(DESIGN_PARAMTYPES, target, propertyKey) || [];
    }
    
    // 获取返回类型
    static getReturnType(target: any, propertyKey: string): any {
        return Reflect.getMetadata(DESIGN_RETURN_TYPE, target, propertyKey);
    }
    
    // 获取验证规则
    static getValidationRules(target: any, propertyKey: string): ValidationRule[] {
        return Reflect.getMetadata(VALIDATION_RULES, target, propertyKey) || [];
    }
}

// 动态表单生成器
class FormBuilder {
    static generateFormForEntity(constructor: Function): any {
        const tableName = MetadataReader.getEntityTableName(constructor);
        const columns = MetadataReader.getEntityColumns(constructor);
        
        console.log(`Generating form for entity: ${tableName}`);
        console.log("Columns:", columns);
        
        const form: any = {
            title: `Create ${tableName.slice(0, -1)}`, // 移除复数s
            fields: []
        };
        
        for (const [name, info] of Object.entries(columns)) {
            // 跳过主键和自动生成的列
            if (info.primary && info.autoIncrement) {
                continue;
            }
            
            const field: any = {
                name,
                label: this.capitalize(name),
                type: info.type || "text",
                required: !info.nullable,
                placeholder: `Enter ${this.capitalize(name)}`
            };
            
            // 特殊处理某些类型
            if (info.type === "boolean") {
                field.type = "checkbox";
            } else if (info.type === "date") {
                field.type = "date";
            } else if (info.length) {
                field.maxLength = info.length;
            }
            
            form.fields.push(field);
        }
        
        return form;
    }
    
    private static capitalize(str: string): string {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
}

// 动态API客户端生成器
class ApiClientGenerator {
    static generateClientForController(controller: any): any {
        const client: any = {};
        const prototype = Object.getPrototypeOf(controller);
        const propertyNames = Object.getOwnPropertyNames(prototype);
        
        for (const propertyKey of propertyNames) {
            // 跳过构造函数和非方法属性
            if (propertyKey === "constructor" || typeof prototype[propertyKey] !== "function") {
                continue;
            }
            
            const endpoint = MetadataReader.getApiEndpoint(prototype, propertyKey);
            const parameterTypes = MetadataReader.getParameterTypes(prototype, propertyKey);
            const returnType = MetadataReader.getReturnType(prototype, propertyKey);
            const validationRules = MetadataReader.getValidationRules(prototype, propertyKey);
            
            if (endpoint) {
                client[propertyKey] = this.createApiMethod(
                    endpoint,
                    parameterTypes,
                    returnType,
                    validationRules
                );
            }
        }
        
        return client;
    }
    
    private static createApiMethod(
        endpoint: string,
        parameterTypes: any[],
        returnType: any,
        validationRules: ValidationRule[]
    ): any {
        return async function(...args: any[]) {
            console.log(`API call to ${endpoint} with args:`, args);
            
            // 在实际应用中，这里会发送HTTP请求
            const response = {
                status: 200,
                data: `Mock response from ${endpoint}`
            };
            
            // 模拟JSON解析
            let data;
            try {
                data = JSON.parse(response.data as string);
            } catch {
                data = response.data;
            }
            
            return data;
        };
    }
}

// 测试元数据反射
function testMetadataReflection() {
    console.log("=== Testing Metadata Reflection ===");
    
    // 测试实体元数据
    const tableName = MetadataReader.getEntityTableName(User);
    console.log("Table name:", tableName);
    
    const columns = MetadataReader.getEntityColumns(User);
    console.log("Columns:", columns);
    
    const primaryKey = MetadataReader.getPrimaryKey(User);
    console.log("Primary key:", primaryKey);
    
    // 测试API控制器元数据
    const controller = new UserController();
    const prototype = Object.getPrototypeOf(controller);
    
    const createUserEndpoint = MetadataReader.getApiEndpoint(prototype, "createUser");
    console.log("Create user endpoint:", createUserEndpoint);
    
    const createUserParamTypes = MetadataReader.getParameterTypes(prototype, "createUser");
    console.log("Create user parameter types:", createUserParamTypes);
    
    const createUserReturnType = MetadataReader.getReturnType(prototype, "createUser");
    console.log("Create user return type:", createUserReturnType);
    
    const createUserValidationRules = MetadataReader.getValidationRules(prototype, "createUser");
    console.log("Create user validation rules:", createUserValidationRules);
    
    // 测试表单生成器
    console.log("\n=== Testing Form Builder ===");
    const userForm = FormBuilder.generateFormForEntity(User);
    console.log("Generated form:", userForm);
    
    // 测试API客户端生成器
    console.log("\n=== Testing API Client Generator ===");
    const apiClient = ApiClientGenerator.generateClientForController(controller);
    console.log("Generated API client:", Object.keys(apiClient));
    
    // 使用生成的API客户端
    apiClient.createUser({ name: "John Doe", email: "john@example.com" })
        .then(result => console.log("Create user result:", result))
        .catch(error => console.error("Create user error:", error));
    
    apiClient.getUser("1")
        .then(result => console.log("Get user result:", result))
        .catch(error => console.error("Get user error:", error));
}

// 元数据驱动的验证器
class MetadataValidator {
    static validate<T>(instance: T): { isValid: boolean; errors: Record<string, string[]> } {
        const errors: Record<string, string[]> = {};
        let isValid = true;
        
        const constructor = (instance as any).constructor;
        const columns = MetadataReader.getEntityColumns(constructor);
        
        for (const [propertyName, columnInfo] of Object.entries(columns)) {
            const propertyErrors: string[] = [];
            const value = (instance as any)[propertyName];
            
            // 检查必需性
            if (!columnInfo.nullable && (value === undefined || value === null)) {
                propertyErrors.push(`${propertyName} is required`);
            }
            
            // 检查类型
            if (value !== undefined && value !== null) {
                switch (columnInfo.type) {
                    case "string":
                        if (typeof value !== "string") {
                            propertyErrors.push(`${propertyName} must be a string`);
                        }
                        break;
                    case "number":
                        if (typeof value !== "number") {
                            propertyErrors.push(`${propertyName} must be a number`);
                        }
                        break;
                    case "boolean":
                        if (typeof value !== "boolean") {
                            propertyErrors.push(`${propertyName} must be a boolean`);
                        }
                        break;
                    case "date":
                        if (!(value instanceof Date) && isNaN(Date.parse(value))) {
                            propertyErrors.push(`${propertyName} must be a valid date`);
                        }
                        break;
                }
            }
            
            // 检查长度
            if (value && columnInfo.type === "string" && columnInfo.length && 
                typeof value === "string" && value.length > columnInfo.length) {
                propertyErrors.push(`${propertyName} must not exceed ${columnInfo.length} characters`);
            }
            
            if (propertyErrors.length > 0) {
                errors[propertyName] = propertyErrors;
                isValid = false;
            }
        }
        
        return { isValid, errors };
    }
}

// 测试元数据驱动验证器
function testMetadataValidator() {
    console.log("\n=== Testing Metadata Validator ===");
    
    const validUser = new User();
    validUser.name = "John Doe";
    validUser.email = "john@example.com";
    validUser.age = 30;
    
    const validResult = MetadataValidator.validate(validUser);
    console.log("Valid user validation result:", validResult);
    
    const invalidUser = new User();
    invalidUser.name = ""; // 空字符串，但列不允许null
    invalidUser.email = "not-an-email"; // 类型正确
    invalidUser.age = "not a number"; // 类型错误
    
    const invalidResult = MetadataValidator.validate(invalidUser);
    console.log("Invalid user validation result:", invalidResult);
}

// 执行测试
testMetadataReflection();
testMetadataValidator();

console.log("\nMetadata and reflection demo completed!");