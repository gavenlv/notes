// JavaScript库的声明文件示例

// 简单工具库声明
declare module "simple-math" {
    export function add(a: number, b: number): number;
    export function subtract(a: number, b: number): number;
    export function multiply(a: number, b: number): number;
    export function divide(a: number, b: number): number;
    export function power(base: number, exponent: number): number;
    export function sqrt(value: number): number;
    export const PI: number;
    export const E: number;
}

// HTTP客户端库声明
declare module "http-client" {
    interface RequestOptions {
        method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
        headers?: Record<string, string>;
        params?: Record<string, any>;
        data?: any;
        timeout?: number;
        retries?: number;
    }

    interface Response<T = any> {
        data: T;
        status: number;
        statusText: string;
        headers: Record<string, string>;
        config: RequestOptions;
        request?: any;
    }

    interface ApiError {
        message: string;
        code: string;
        details?: any;
        response?: Response;
    }

    interface Interceptor {
        request?: (config: RequestOptions) => RequestOptions;
        response?: (response: Response) => Response;
        error?: (error: ApiError) => ApiError;
    }

    class HttpClient {
        constructor(baseURL?: string, defaultOptions?: RequestOptions);
        
        get<T = any>(url: string, options?: RequestOptions): Promise<Response<T>>;
        post<T = any>(url: string, data?: any, options?: RequestOptions): Promise<Response<T>>;
        put<T = any>(url: string, data?: any, options?: RequestOptions): Promise<Response<T>>;
        patch<T = any>(url: string, data?: any, options?: RequestOptions): Promise<Response<T>>;
        delete<T = any>(url: string, options?: RequestOptions): Promise<Response<T>>;
        
        request<T = any>(config: RequestOptions): Promise<Response<T>>;
        
        setHeader(name: string, value: string): void;
        removeHeader(name: string): void;
        
        addRequestInterceptor(interceptor: (config: RequestOptions) => RequestOptions): number;
        addResponseInterceptor(interceptor: (response: Response) => Response): number;
        addErrorInterceptor(interceptor: (error: ApiError) => ApiError): number;
        
        removeInterceptor(id: number): void;
    }

    export default HttpClient;
}

// 日期处理库声明
declare namespace DateUtils {
    type DateInput = Date | string | number;
    type DateFormat = string;
    type Locale = string;
    
    interface DateFormatterOptions {
        format?: DateFormat;
        locale?: Locale;
        timezone?: string;
    }
    
    interface RelativeTimeOptions {
        locale?: Locale;
        addSuffix?: boolean;
        numeric?: 'auto' | 'always';
    }
    
    function format(date: DateInput, options?: DateFormatterOptions): string;
    function format(date: DateInput, formatString: DateFormat, locale?: Locale): string;
    
    function parse(dateString: string, format?: DateFormat, locale?: Locale): Date;
    
    function isBefore(date1: DateInput, date2: DateInput): boolean;
    function isAfter(date1: DateInput, date2: DateInput): boolean;
    function isSame(date1: DateInput, date2: DateInput, unit?: 'year' | 'month' | 'day' | 'hour' | 'minute' | 'second'): boolean;
    
    function add(date: DateInput, amount: number, unit: 'year' | 'month' | 'day' | 'hour' | 'minute' | 'second'): Date;
    function subtract(date: DateInput, amount: number, unit: 'year' | 'month' | 'day' | 'hour' | 'minute' | 'second'): Date;
    
    function diff(date1: DateInput, date2: DateInput, unit?: 'year' | 'month' | 'day' | 'hour' | 'minute' | 'second'): number;
    
    function relativeTime(date: DateInput, options?: RelativeTimeOptions): string;
    
    const now: () => Date;
}

// 表单验证库声明
declare namespace FormValidation {
    interface ValidationRule {
        required?: boolean;
        minLength?: number;
        maxLength?: number;
        pattern?: RegExp;
        custom?: (value: any) => boolean | string;
        message?: string;
    }
    
    interface ValidationSchema {
        [field: string]: ValidationRule | ValidationRule[];
    }
    
    interface ValidationError {
        field: string;
        rule: string;
        message: string;
        value: any;
    }
    
    interface ValidationResult {
        isValid: boolean;
        errors: ValidationError[];
        data: Record<string, any>;
    }
    
    class Validator {
        constructor(schema: ValidationSchema);
        
        validate(data: Record<string, any>): ValidationResult;
        validateField(field: string, value: any): boolean | string;
        
        addRule(field: string, rule: ValidationRule): void;
        removeRule(field: string, ruleName: string): void;
        
        updateSchema(schema: ValidationSchema): void;
        
        static create(schema: ValidationSchema): Validator;
    }
    
    type BuiltInValidators = {
        required: ValidationRule;
        email: ValidationRule;
        url: ValidationRule;
        creditCard: ValidationRule;
        phone: ValidationRule;
    };
    
    const validators: BuiltInValidators;
}