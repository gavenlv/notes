// 类型安全的表单验证系统示例
import { ValidationRule } from './interfaces/validation-rule';
import { FormField } from './interfaces/form-field';
import { Form } from './interfaces/form';
import { RequiredRule } from './rules/required-rule';
import { LengthRule } from './rules/length-rule';
import { RegexRule } from './rules/regex-rule';
import { TextField } from './fields/text-field';
import { MyForm } from './models/my-form';

// 模拟导入，实际项目中这些会在单独的文件中

// 定义验证规则接口
interface ValidationRule<T = any> {
    validate(value: T): boolean;
    getErrorMessage(): string;
}

// 表单字段接口
interface FormField<T = any> {
    name: string;
    value: T;
    rules: ValidationRule<T>[];
    errors: string[];
    validate(): boolean;
}

// 表单接口
interface Form {
    fields: Map<string, FormField>;
    addField<T>(field: FormField<T>): void;
    getField(name: string): FormField | undefined;
    validate(): boolean;
    getErrors(): Record<string, string[]>;
}

// 必填验证规则
class RequiredRule implements ValidationRule {
    validate(value: any): boolean {
        return value !== null && value !== undefined && value !== "";
    }
    
    getErrorMessage(): string {
        return "This field is required";
    }
}

// 长度验证规则
class LengthRule implements ValidationRule<string> {
    constructor(
        private minLength: number,
        private maxLength: number
    ) {}
    
    validate(value: string): boolean {
        return value.length >= this.minLength && value.length <= this.maxLength;
    }
    
    getErrorMessage(): string {
        return `Length must be between ${this.minLength} and ${this.maxLength}`;
    }
}

// 正则表达式验证规则
class RegexRule implements ValidationRule<string> {
    constructor(
        private pattern: RegExp,
        private errorMessage: string = "Invalid format"
    ) {}
    
    validate(value: string): boolean {
        return this.pattern.test(value);
    }
    
    getErrorMessage(): string {
        return this.errorMessage;
    }
}

// 表单字段实现
class TextField implements FormField<string> {
    public errors: string[] = [];
    
    constructor(
        public name: string,
        public value: string,
        public rules: ValidationRule<string>[]
    ) {}
    
    validate(): boolean {
        this.errors = [];
        
        for (const rule of this.rules) {
            if (!rule.validate(this.value)) {
                this.errors.push(rule.getErrorMessage());
            }
        }
        
        return this.errors.length === 0;
    }
}

// 表单实现
class MyForm implements Form {
    public fields: Map<string, FormField> = new Map();
    
    addField<T>(field: FormField<T>): void {
        this.fields.set(field.name, field);
    }
    
    getField(name: string): FormField | undefined {
        return this.fields.get(name);
    }
    
    validate(): boolean {
        let isValid = true;
        
        for (const field of this.fields.values()) {
            if (!field.validate()) {
                isValid = false;
            }
        }
        
        return isValid;
    }
    
    getErrors(): Record<string, string[]> {
        const errors: Record<string, string[]> = {};
        
        for (const [name, field] of this.fields.entries()) {
            if (field.errors.length > 0) {
                errors[name] = field.errors;
            }
        }
        
        return errors;
    }
}

// 使用示例
function demonstrateFormValidationSystem(): void {
    console.log("\n=== Form Validation System Demo ===");
    
    // 创建登录表单
    function createLoginForm(): Form {
        const form = new MyForm();
        
        // 添加用户名字段
        const usernameField = new TextField(
            "username",
            "",
            [
                new RequiredRule(),
                new LengthRule(3, 20)
            ]
        );
        form.addField(usernameField);
        
        // 添加密码字段
        const passwordField = new TextField(
            "password",
            "",
            [
                new RequiredRule(),
                new LengthRule(8, 50),
                new RegexRule(
                    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/,
                    "Password must contain at least one uppercase letter, one lowercase letter, and one number"
                )
            ]
        );
        form.addField(passwordField);
        
        // 添加邮箱字段
        const emailField = new TextField(
            "email",
            "",
            [
                new RequiredRule(),
                new RegexRule(
                    /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                    "Please enter a valid email address"
                )
            ]
        );
        form.addField(emailField);
        
        return form;
    }
    
    // 测试表单
    const loginForm = createLoginForm();
    
    // 测试1：空表单
    console.log("\n=== Test 1: Empty Form ===");
    const isValid1 = loginForm.validate();
    const errors1 = loginForm.getErrors();
    console.log("Form is valid:", isValid1);
    console.log("Form errors:", errors1);
    
    // 重置表单字段值
    (loginForm.getField("username") as TextField).value = "user";
    (loginForm.getField("password") as TextField).value = "Password123";
    (loginForm.getField("email") as TextField).value = "user@example.com";
    
    // 测试2：有效数据
    console.log("\n=== Test 2: Valid Data ===");
    const isValid2 = loginForm.validate();
    const errors2 = loginForm.getErrors();
    console.log("Form is valid:", isValid2);
    console.log("Form errors:", errors2);
    
    // 测试3：无效数据
    console.log("\n=== Test 3: Invalid Data ===");
    (loginForm.getField("username") as TextField).value = "u"; // 太短
    (loginForm.getField("password") as TextField).value = "weak"; // 不符合密码规则
    (loginForm.getField("email") as TextField).value = "invalid-email"; // 无效邮箱
    
    const isValid3 = loginForm.validate();
    const errors3 = loginForm.getErrors();
    console.log("Form is valid:", isValid3);
    console.log("Form errors:", errors3);
    
    // 扩展验证系统：添加自定义字段和验证规则
    class NumberField implements FormField<number> {
        public errors: string[] = [];
        
        constructor(
            public name: string,
            public value: number,
            public rules: ValidationRule<number>[]
        ) {}
        
        validate(): boolean {
            this.errors = [];
            
            for (const rule of this.rules) {
                if (!rule.validate(this.value)) {
                    this.errors.push(rule.getErrorMessage());
                }
            }
            
            return this.errors.length === 0;
        }
    }
    
    class RangeRule implements ValidationRule<number> {
        constructor(
            private min: number,
            private max: number
        ) {}
        
        validate(value: number): boolean {
            return value >= this.min && value <= this.max;
        }
        
        getErrorMessage(): string {
            return `Value must be between ${this.min} and ${this.max}`;
        }
    }
    
    // 创建包含数字字段的表单
    function createUserProfileForm(): Form {
        const form = new MyForm();
        
        // 添加年龄字段
        const ageField = new NumberField(
            "age",
            25,
            [
                new RequiredRule() as any, // 类型断言，因为RequiredRule是any类型
                new RangeRule(18, 120)
            ]
        );
        form.addField(ageField);
        
        return form;
    }
    
    console.log("\n=== Test 4: Extended Form with Number Field ===");
    const profileForm = createUserProfileForm();
    
    // 测试有效年龄
    const isValid4 = profileForm.validate();
    const errors4 = profileForm.getErrors();
    console.log("Profile form is valid:", isValid4);
    console.log("Profile form errors:", errors4);
    
    // 测试无效年龄
    (profileForm.getField("age") as NumberField).value = 15; // 太小
    const isValid5 = profileForm.validate();
    const errors5 = profileForm.getErrors();
    console.log("Profile form with invalid age is valid:", isValid5);
    console.log("Profile form with invalid age errors:", errors5);
}

demonstrateFormValidationSystem();