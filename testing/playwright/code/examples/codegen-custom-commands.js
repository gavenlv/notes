// examples/codegen-custom-commands.js
/**
 * CodeGen自定义命令和工具函数
 * 提供CodeGen相关的自定义命令和实用工具
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

/**
 * CodeGen命令构建器类
 */
class CodegenCommandBuilder {
  constructor() {
    this.baseCommand = 'npx playwright codegen';
    this.options = new Map();
  }

  /**
   * 设置目标URL
   */
  url(targetUrl) {
    this.options.set('url', targetUrl);
    return this;
  }

  /**
   * 设置浏览器类型
   */
  browser(browserType) {
    this.options.set('browser', browserType);
    return this;
  }

  /**
   * 设置设备模拟
   */
  device(deviceName) {
    this.options.set('device', deviceName);
    return this;
  }

  /**
   * 设置视口大小
   */
  viewport(width, height) {
    this.options.set('viewport', `${width},${height}`);
    return this;
  }

  /**
   * 设置地理位置
   */
  geolocation(latitude, longitude) {
    this.options.set('geolocation', `"${latitude},${longitude}"`);
    return this;
  }

  /**
   * 设置本地化
   */
  locale(localeCode) {
    this.options.set('locale', localeCode);
    return this;
  }

  /**
   * 设置时区
   */
  timezone(timezoneId) {
    this.options.set('timezone', timezoneId);
    return this;
  }

  /**
   * 设置输出文件
   */
  output(outputPath) {
    this.options.set('output', outputPath);
    return this;
  }

  /**
   * 设置无头模式
   */
  headless(enabled = true) {
    if (enabled) {
      this.options.set('headless', '');
    } else {
      this.options.delete('headless');
    }
    return this;
  }

  /**
   * 设置调试模式
   */
  debug(enabled = true) {
    if (enabled) {
      this.options.set('debug', '');
      this.options.set('devtools', '');
    } else {
      this.options.delete('debug');
      this.options.delete('devtools');
    }
    return this;
  }

  /**
   * 设置慢动作
   */
  slowMo(milliseconds) {
    this.options.set('slow-mo', milliseconds);
    return this;
  }

  /**
   * 设置忽略HTTPS错误
   */
  ignoreHTTPSErrors(enabled = true) {
    if (enabled) {
      this.options.set('ignore-https-errors', '');
    } else {
      this.options.delete('ignore-https-errors');
    }
    return this;
  }

  /**
   * 设置保存存储状态
   */
  saveStorage(storagePath) {
    this.options.set('save-storage', storagePath);
    return this;
  }

  /**
   * 设置加载存储状态
   */
  loadStorage(storagePath) {
    this.options.set('load-storage', storagePath);
    return this;
  }

  /**
   * 设置代理
   */
  proxy(proxyServer) {
    this.options.set('proxy-server', proxyServer);
    return this;
  }

  /**
   * 设置用户代理
   */
  userAgent(userAgentString) {
    this.options.set('user-agent', `"${userAgentString}"`);
    return this;
  }

  /**
   * 设置颜色方案
   */
  colorScheme(scheme) {
    this.options.set('color-scheme', scheme);
    return this;
  }

  /**
   * 设置是否接受下载
   */
  acceptDownloads(enabled = true) {
    if (enabled) {
      this.options.set('accept-downloads', '');
    } else {
      this.options.delete('accept-downloads');
    }
    return this;
  }

  /**
   * 构建最终命令
   */
  build() {
    let command = this.baseCommand;
    
    // 添加URL（如果有）
    if (this.options.has('url')) {
      command += ` ${this.options.get('url')}`;
      this.options.delete('url');
    }

    // 添加其他选项
    for (const [key, value] of this.options) {
      command += ` --${key}`;
      if (value !== '') {
        command += `=${value}`;
      }
    }

    return command;
  }

  /**
   * 执行命令
   */
  execute() {
    const command = this.build();
    console.log(`执行命令: ${command}`);
    
    try {
      const output = execSync(command, { 
        stdio: 'inherit',
        cwd: process.cwd()
      });
      return { success: true, output };
    } catch (error) {
      console.error('命令执行失败:', error.message);
      return { success: false, error: error.message };
    }
  }
}

/**
 * 预设的CodeGen配置
 */
const codegenPresets = {
  // 桌面端配置
  desktop: {
    browser: 'chromium',
    viewport: '1920,1080',
    headless: false
  },

  // 移动端配置
  mobile: {
    browser: 'chromium',
    device: 'iPhone 12',
    headless: false
  },

  // 平板端配置
  tablet: {
    browser: 'chromium',
    device: 'iPad (gen 7)',
    headless: false
  },

  // 调试配置
  debug: {
    browser: 'chromium',
    headless: false,
    debug: '',
    devtools: '',
    slowMo: 1000
  },

  // 性能测试配置
  performance: {
    browser: 'chromium',
    headless: true,
    viewport: '1920,1080'
  },

  // 跨浏览器配置
  crossBrowser: {
    browser: 'chromium', // 可以改为 firefox 或 webkit
    headless: false,
    viewport: '1920,1080'
  }
};

/**
 * 批量CodeGen执行器
 */
class BatchCodegenExecutor {
  constructor() {
    this.configs = [];
  }

  /**
   * 添加配置
   */
  addConfig(name, builderOrConfig) {
    this.configs.push({
      name,
      builder: builderOrConfig instanceof CodegenCommandBuilder 
        ? builderOrConfig 
        : this.configToBuilder(builderOrConfig)
    });
    return this;
  }

  /**
   * 将配置转换为构建器
   */
  configToBuilder(config) {
    const builder = new CodegenCommandBuilder();
    
    Object.entries(config).forEach(([key, value]) => {
      switch (key) {
        case 'browser':
          builder.browser(value);
          break;
        case 'device':
          builder.device(value);
          break;
        case 'viewport':
          if (typeof value === 'string' && value.includes(',')) {
            const [width, height] = value.split(',').map(v => parseInt(v.trim()));
            builder.viewport(width, height);
          }
          break;
        case 'headless':
          builder.headless(value === '' || value === true);
          break;
        case 'debug':
          builder.debug(value === '' || value === true);
          break;
        case 'slowMo':
          builder.slowMo(value);
          break;
        case 'output':
          builder.output(value);
          break;
        case 'url':
          builder.url(value);
          break;
        default:
          // 处理其他选项
          if (value === '' || value === true) {
            builder[key]();
          } else {
            builder[key](value);
          }
      }
    });

    return builder;
  }

  /**
   * 执行所有配置
   */
  async executeAll() {
    const results = [];
    
    for (const config of this.configs) {
      console.log(`\n执行配置: ${config.name}`);
      const result = await config.builder.execute();
      results.push({
        name: config.name,
        success: result.success,
        error: result.error
      });
    }

    return results;
  }

  /**
   * 生成报告
   */
  generateReport(results) {
    console.log('\n=== CodeGen批量执行报告 ===');
    
    const successful = results.filter(r => r.success).length;
    const failed = results.filter(r => !r.success).length;
    
    console.log(`总配置数: ${results.length}`);
    console.log(`成功: ${successful}`);
    console.log(`失败: ${failed}`);
    
    if (failed > 0) {
      console.log('\n失败的配置:');
      results.filter(r => !r.success).forEach(r => {
        console.log(`- ${r.name}: ${r.error}`);
      });
    }

    return {
      total: results.length,
      successful,
      failed,
      results
    };
  }
}

/**
 * 实用的CodeGen工具函数
 */
const codegenUtils = {
  /**
   * 创建输出目录
   */
  createOutputDirectory(baseDir, timestamp = true) {
    const dirName = timestamp 
      ? `codegen-output-${Date.now()}`
      : 'codegen-output';
    
    const outputDir = path.join(baseDir, dirName);
    
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    return outputDir;
  },

  /**
   * 生成唯一的测试文件名
   */
  generateTestFilename(prefix = 'generated', extension = '.spec.js') {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    return `${prefix}-${timestamp}${extension}`;
  },

  /**
   * 验证URL格式
   */
  validateUrl(url) {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  },

  /**
   * 获取可用的端口
   */
  async getAvailablePort(startPort = 3000) {
    const net = require('net');
    
    return new Promise((resolve, reject) => {
      const server = net.createServer();
      
      server.listen(startPort, () => {
        const port = server.address().port;
        server.close(() => resolve(port));
      });
      
      server.on('error', (err) => {
        if (err.code === 'EADDRINUSE') {
          resolve(this.getAvailablePort(startPort + 1));
        } else {
          reject(err);
        }
      });
    });
  }
};

// 使用示例和演示函数
async function demonstrateCustomCommands() {
  console.log('=== CodeGen自定义命令演示 ===\n');

  // 示例1: 基本桌面端录制
  console.log('1. 基本桌面端录制:');
  const desktopBuilder = new CodegenCommandBuilder()
    .url('https://example.com')
    .browser('chromium')
    .viewport(1920, 1080)
    .output('desktop-test.spec.js');
  
  console.log(`命令: ${desktopBuilder.build()}`);

  // 示例2: 移动端录制
  console.log('\n2. 移动端录制:');
  const mobileBuilder = new CodegenCommandBuilder()
    .url('https://m.example.com')
    .device('iPhone 12')
    .output('mobile-test.spec.js');
  
  console.log(`命令: ${mobileBuilder.build()}`);

  // 示例3: 地理位置测试
  console.log('\n3. 地理位置测试:');
  const geoBuilder = new CodegenCommandBuilder()
    .url('https://maps.example.com')
    .geolocation(39.9042, 116.4074) // 北京
    .locale('zh-CN')
    .timezone('Asia/Shanghai')
    .output('geolocation-test.spec.js');
  
  console.log(`命令: ${geoBuilder.build()}`);

  // 示例4: 调试模式
  console.log('\n4. 调试模式:');
  const debugBuilder = new CodegenCommandBuilder()
    .url('https://example.com')
    .debug()
    .slowMo(1000)
    .output('debug-test.spec.js');
  
  console.log(`命令: ${debugBuilder.build()}`);

  // 示例5: 认证状态保持
  console.log('\n5. 认证状态保持:');
  const authBuilder = new CodegenCommandBuilder()
    .url('https://app.example.com')
    .loadStorage('auth-state.json')
    .saveStorage('new-auth-state.json')
    .output('auth-test.spec.js');
  
  console.log(`命令: ${authBuilder.build()}`);

  // 示例6: 批量执行
  console.log('\n6. 批量执行配置:');
  const batchExecutor = new BatchCodegenExecutor();
  
  // 添加多个配置
  batchExecutor
    .addConfig('桌面端', codegenPresets.desktop)
    .addConfig('移动端', codegenPresets.mobile)
    .addConfig('平板端', codegenPresets.tablet)
    .addConfig('调试模式', codegenPresets.debug);
  
  console.log(`已添加 ${batchExecutor.configs.length} 个配置`);
  
  // 注意：这里不实际执行，只演示构建过程
  // await batchExecutor.executeAll();
}

// 导出所有功能
module.exports = {
  CodegenCommandBuilder,
  BatchCodegenExecutor,
  codegenPresets,
  codegenUtils,
  demonstrateCustomCommands
};

// 如果直接运行此文件，执行演示
if (require.main === module) {
  demonstrateCustomCommands().catch(console.error);
}