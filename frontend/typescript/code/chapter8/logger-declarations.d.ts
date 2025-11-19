// 日志库声明文件示例

// 基础日志级别定义
declare namespace Logger {
    type LogLevel = 'DEBUG' | 'INFO' | 'WARN' | 'ERROR' | 'FATAL';
    
    type MetaData = Record<string, any> | string | Error;
    
    interface LogEntry {
        timestamp: Date;
        level: LogLevel;
        message: string;
        logger: string;
        meta?: MetaData;
    }
    
    interface LoggerOptions {
        level?: LogLevel | number;
        format?: 'json' | 'text' | 'custom';
        output?: 'console' | 'file' | 'custom';
        file?: {
            path: string;
            maxSize?: number;
            maxFiles?: number;
        };
        dateFormat?: string;
    }
    
    interface Logger {
        name: string;
        level: LogLevel;
        
        debug(message: string, meta?: MetaData): void;
        info(message: string, meta?: MetaData): void;
        warn(message: string, meta?: MetaData): void;
        error(message: string, meta?: MetaData): void;
        fatal(message: string, meta?: MetaData): void;
        
        isLevelEnabled(level: LogLevel): boolean;
        setLevel(level: LogLevel | number): void;
        
        child(name: string, meta?: MetaData): Logger;
    }
    
    interface LoggerFactory {
        getLogger(name: string, options?: LoggerOptions): Logger;
        
        configure(config: Record<string, LoggerOptions>): void;
        
        setDefaultLevel(level: LogLevel | number): void;
        
        addTransport(name: string, transport: Transport): void;
    }
    
    interface Transport {
        name: string;
        level: LogLevel;
        
        log(entry: LogEntry): void;
    }
    
    interface LogLevels {
        DEBUG: number;
        INFO: number;
        WARN: number;
        ERROR: number;
        FATAL: number;
    }
}

// 模块声明
declare module 'logger' {
    export = LoggerAPI;
}

declare module 'logger/factory' {
    function createLoggerFactory(options?: Logger.LoggerOptions): Logger.LoggerFactory;
    export = createLoggerFactory;
}

declare module 'logger/transports' {
    class ConsoleTransport implements Logger.Transport {
        name: string;
        level: Logger.LogLevel;
        constructor(level?: Logger.LogLevel);
        log(entry: Logger.LogEntry): void;
    }
    
    class FileTransport implements Logger.Transport {
        name: string;
        level: Logger.LogLevel;
        filePath: string;
        
        constructor(filePath: string, level?: Logger.LogLevel);
        log(entry: Logger.LogEntry): void;
    }
    
    class JSONTransport implements Logger.Transport {
        name: string;
        level: Logger.LogLevel;
        filePath: string;
        
        constructor(filePath: string, level?: Logger.LogLevel);
        log(entry: Logger.LogEntry): void;
    }
    
    export { ConsoleTransport, FileTransport, JSONTransport };
}

// 全局声明
declare global {
    interface Window {
        logger?: Logger.LoggerFactory;
        __loggers?: Record<string, Logger.Logger>;
    }
    
    namespace NodeJS {
        interface ProcessEnv {
            LOG_LEVEL?: Logger.LogLevel;
            LOG_FORMAT?: string;
            LOG_OUTPUT?: string;
            LOG_FILE_PATH?: string;
        }
    }
}

// 类型守卫
declare function isLogLevel(value: string): value is Logger.LogLevel;

// 类型别名
declare type LoggerAPI = {
    LOG_LEVELS: Logger.LogLevels;
    createLogger(name: string, options?: Logger.LoggerOptions): Logger.Logger;
    getLogger(name: string, options?: Logger.LoggerOptions): Logger.Logger;
    setDefaultLevel(level: Logger.LogLevel | number): void;
};