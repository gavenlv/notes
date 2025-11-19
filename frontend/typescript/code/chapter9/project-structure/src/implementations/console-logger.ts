// 控制台日志实现

import { Logger, LogLevel } from '../interfaces/logger.interface';

/**
 * 控制台日志实现类
 * 将日志输出到控制台
 */
export class ConsoleLogger implements Logger {
    private currentLevel: LogLevel;
    
    /**
     * 构造函数
     * @param level 默认日志级别
     */
    constructor(level: LogLevel = 'info') {
        this.currentLevel = level;
    }
    
    /**
     * 设置日志级别
     * @param level 日志级别
     */
    setLevel(level: LogLevel): void {
        this.currentLevel = level;
    }
    
    /**
     * 获取当前日志级别
     * @returns 当前日志级别
     */
    getLevel(): LogLevel {
        return this.currentLevel;
    }
    
    /**
     * 检查是否应该记录该级别的日志
     * @param level 日志级别
     * @returns 是否应该记录
     */
    private shouldLog(level: LogLevel): boolean {
        const levels: Record<LogLevel, number> = {
            debug: 0,
            info: 1,
            warn: 2,
            error: 3
        };
        
        return levels[level] >= levels[this.currentLevel];
    }
    
    /**
     * 格式化日志消息
     * @param message 原始消息
     * @param level 日志级别
     * @returns 格式化后的消息
     */
    private formatMessage(message: string, level: LogLevel): string {
        const timestamp = new Date().toISOString();
        const paddedLevel = level.toUpperCase().padEnd(5);
        return `[${timestamp}] [${paddedLevel}] ${message}`;
    }
    
    /**
     * 记录日志
     * @param message 日志消息
     * @param level 日志级别
     */
    log(message: string, level: LogLevel = 'info'): void {
        if (!this.shouldLog(level)) return;
        
        const formattedMessage = this.formatMessage(message, level);
        
        switch (level) {
            case 'debug':
            case 'info':
                console.log(formattedMessage);
                break;
            case 'warn':
                console.warn(formattedMessage);
                break;
            case 'error':
                console.error(formattedMessage);
                break;
            default:
                console.log(formattedMessage);
        }
    }
    
    /**
     * 记录调试信息
     * @param message 日志消息
     */
    debug(message: string): void {
        this.log(message, 'debug');
    }
    
    /**
     * 记录一般信息
     * @param message 日志消息
     */
    info(message: string): void {
        this.log(message, 'info');
    }
    
    /**
     * 记录警告信息
     * @param message 日志消息
     */
    warn(message: string): void {
        this.log(message, 'warn');
    }
    
    /**
     * 记录错误信息
     * @param message 日志消息
     */
    error(message: string): void {
        this.log(message, 'error');
    }
}