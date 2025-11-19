// 日志接口

/**
 * 日志级别
 */
export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

/**
 * 日志接口
 * 定义了日志记录的基本功能
 */
export interface Logger {
    /**
     * 记录日志
     * @param message 日志消息
     * @param level 日志级别
     */
    log(message: string, level?: LogLevel): void;
    
    /**
     * 记录调试信息
     * @param message 日志消息
     */
    debug(message: string): void;
    
    /**
     * 记录一般信息
     * @param message 日志消息
     */
    info(message: string): void;
    
    /**
     * 记录警告信息
     * @param message 日志消息
     */
    warn(message: string): void;
    
    /**
     * 记录错误信息
     * @param message 日志消息
     */
    error(message: string): void;
}