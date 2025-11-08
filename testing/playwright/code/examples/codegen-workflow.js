// examples/codegen-workflow.js
/**
 * CodeGen工作流自动化示例
 * 展示如何将CodeGen集成到完整的工作流程中
 */

const { CodegenCommandBuilder, BatchCodegenExecutor, codegenPresets } = require('./codegen-custom-commands');
const fs = require('fs');
const path = require('path');

/**
 * CodeGen工作流管理器
 */
class CodegenWorkflowManager {
  constructor(config = {}) {
    this.config = {
      outputDir: config.outputDir || './generated-tests',
      backupDir: config.backupDir || './test-backups',
      logFile: config.logFile || './codegen-workflow.log',
      ...config
    };
    
    this.executionLog = [];
    this.initDirectories();
  }

  /**
   * 初始化目录结构
   */
  initDirectories() {
    const dirs = [this.config.outputDir, this.config.backupDir];
    dirs.forEach(dir => {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    });
  }

  /**
   * 记录日志
   */
  log(message, type = 'info') {
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] [${type.toUpperCase()}] ${message}`;
    
    console.log(logEntry);
    this.executionLog.push(logEntry);
    
    // 写入日志文件
    fs.appendFileSync(this.config.logFile, logEntry + '\n');
  }

  /**
   * 备份现有测试文件
   */
  backupExistingTests() {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const backupPath = path.join(this.config.backupDir, `backup-${timestamp}`);
    
    if (fs.existsSync(this.config.outputDir)) {
      this.log('备份现有测试文件...');
      
      if (!fs.existsSync(backupPath)) {
        fs.mkdirSync(backupPath, { recursive: true });
      }
      
      // 复制文件到备份目录
      this.copyDirectory(this.config.outputDir, backupPath);
      this.log(`测试文件已备份到: ${backupPath}`);
      
      return backupPath;
    }
    
    return null;
  }

  /**
   * 复制目录
   */
  copyDirectory(src, dest) {
    if (!fs.existsSync(dest)) {
      fs.mkdirSync(dest, { recursive: true });
    }
    
    const files = fs.readdirSync(src);
    files.forEach(file => {
      const srcFile = path.join(src, file);
      const destFile = path.join(dest, file);
      
      if (fs.statSync(srcFile).isDirectory()) {
        this.copyDirectory(srcFile, destFile);
      } else {
        fs.copyFileSync(srcFile, destFile);
      }
    });
  }

  /**
   * 创建完整应用测试套件
   */
  async createFullApplicationTestSuite(appConfig) {
    const {
      name,
      url,
      features = [],
      devices = ['desktop'],
      environments = ['development']
    } = appConfig;

    this.log(`开始为应用 "${name}" 创建完整测试套件...`);
    
    const batchExecutor = new BatchCodegenExecutor();
    const timestamp = Date.now();
    
    // 为每个设备和环境组合创建测试
    for (const device of devices) {
      for (const env of environments) {
        for (const feature of features) {
          const configName = `${name}-${device}-${env}-${feature.name}`;
          const outputFile = `${this.config.outputDir}/${configName}-${timestamp}.spec.js`;
          
          const builder = new CodegenCommandBuilder()
            .url(feature.url || url)
            .output(outputFile);

          // 设置设备
          if (device !== 'desktop') {
            builder.device(device);
          } else {
            builder.viewport(1920, 1080);
          }

          // 设置环境特定的配置
          if (env === 'development') {
            builder.slowMo(500);
          }

          // 添加特征特定的配置
          if (feature.viewport) {
            builder.viewport(feature.viewport.width, feature.viewport.height);
          }

          if (feature.locale) {
            builder.locale(feature.locale);
          }

          if (feature.geolocation) {
            builder.geolocation(feature.geolocation.latitude, feature.geolocation.longitude);
          }

          batchExecutor.addConfig(configName, builder);
        }
      }
    }

    this.log(`创建了 ${batchExecutor.configs.length} 个测试配置`);
    
    // 执行所有配置
    const results = await batchExecutor.executeAll();
    
    // 记录结果
    this.log(`测试套件创建完成。成功: ${results.filter(r => r.success).length}, 失败: ${results.filter(r => !r.success).length}`);
    
    return results;
  }

  /**
   * 创建响应式设计测试
   */
  async createResponsiveDesignTest(url, breakpoints = []) {
    this.log('创建响应式设计测试...');
    
    const defaultBreakpoints = [
      { name: 'mobile', width: 375, height: 667 },
      { name: 'tablet', width: 768, height: 1024 },
      { name: 'desktop', width: 1920, height: 1080 }
    ];

    const testBreakpoints = breakpoints.length > 0 ? breakpoints : defaultBreakpoints;
    const batchExecutor = new BatchCodegenExecutor();
    const timestamp = Date.now();

    testBreakpoints.forEach(breakpoint => {
      const configName = `responsive-${breakpoint.name}`;
      const outputFile = `${this.config.outputDir}/responsive-${breakpoint.name}-${timestamp}.spec.js`;

      const builder = new CodegenCommandBuilder()
        .url(url)
        .viewport(breakpoint.width, breakpoint.height)
        .output(outputFile);

      batchExecutor.addConfig(configName, builder);
    });

    this.log(`创建了 ${batchExecutor.configs.length} 个响应式测试配置`);
    
    const results = await batchExecutor.executeAll();
    
    this.log(`响应式测试创建完成。成功: ${results.filter(r => r.success).length}, 失败: ${results.filter(r => !r.success).length}`);
    
    return results;
  }

  /**
   * 创建跨浏览器兼容性测试
   */
  async createCrossBrowserTest(url, browsers = []) {
    this.log('创建跨浏览器兼容性测试...');
    
    const defaultBrowsers = ['chromium', 'firefox', 'webkit'];
    const testBrowsers = browsers.length > 0 ? browsers : defaultBrowsers;
    
    const batchExecutor = new BatchCodegenExecutor();
    const timestamp = Date.now();

    testBrowsers.forEach(browser => {
      const configName = `cross-browser-${browser}`;
      const outputFile = `${this.config.outputDir}/cross-browser-${browser}-${timestamp}.spec.js`;

      const builder = new CodegenCommandBuilder()
        .url(url)
        .browser(browser)
        .viewport(1920, 1080)
        .output(outputFile);

      batchExecutor.addConfig(configName, builder);
    });

    this.log(`创建了 ${batchExecutor.configs.length} 个跨浏览器测试配置`);
    
    const results = await batchExecutor.executeAll();
    
    this.log(`跨浏览器测试创建完成。成功: ${results.filter(r => r.success).length}, 失败: ${results.filter(r => !r.success).length}`);
    
    return results;
  }

  /**
   * 创建国际化测试
   */
  async createInternationalizationTest(url, locales = []) {
    this.log('创建国际化测试...');
    
    const defaultLocales = [
      { code: 'en-US', name: 'english', timezone: 'America/New_York' },
      { code: 'zh-CN', name: 'chinese', timezone: 'Asia/Shanghai' },
      { code: 'ja-JP', name: 'japanese', timezone: 'Asia/Tokyo' },
      { code: 'ko-KR', name: 'korean', timezone: 'Asia/Seoul' }
    ];

    const testLocales = locales.length > 0 ? locales : defaultLocales;
    const batchExecutor = new BatchCodegenExecutor();
    const timestamp = Date.now();

    testLocales.forEach(locale => {
      const configName = `i18n-${locale.name}`;
      const outputFile = `${this.config.outputDir}/i18n-${locale.name}-${timestamp}.spec.js`;

      const builder = new CodegenCommandBuilder()
        .url(url)
        .locale(locale.code)
        .timezone(locale.timezone)
        .output(outputFile);

      batchExecutor.addConfig(configName, builder);
    });

    this.log(`创建了 ${batchExecutor.configs.length} 个国际化测试配置`);
    
    const results = await batchExecutor.executeAll();
    
    this.log(`国际化测试创建完成。成功: ${results.filter(r => r.success).length}, 失败: ${results.filter(r => !r.success).length}`);
    
    return results;
  }

  /**
   * 生成测试报告
   */
  generateTestReport(results) {
    this.log('生成测试报告...');
    
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        total: results.length,
        successful: results.filter(r => r.success).length,
        failed: results.filter(r => !r.success).length
      },
      details: results.map(result => ({
        name: result.name,
        success: result.success,
        error: result.error || null,
        timestamp: result.timestamp || new Date().toISOString()
      })),
      files: this.getGeneratedFiles()
    };

    // 保存报告到文件
    const reportPath = path.join(this.config.outputDir, 'test-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    
    this.log(`测试报告已保存到: ${reportPath}`);
    
    return report;
  }

  /**
   * 获取生成的文件列表
   */
  getGeneratedFiles() {
    if (!fs.existsSync(this.config.outputDir)) {
      return [];
    }

    const files = [];
    const items = fs.readdirSync(this.config.outputDir);
    
    items.forEach(item => {
      const itemPath = path.join(this.config.outputDir, item);
      const stats = fs.statSync(itemPath);
      
      if (stats.isFile() && item.endsWith('.spec.js')) {
        files.push({
          name: item,
          path: itemPath,
          size: stats.size,
          created: stats.birthtime,
          modified: stats.mtime
        });
      }
    });

    return files;
  }

  /**
   * 清理旧的测试文件
   */
  cleanupOldTests(daysToKeep = 7) {
    this.log(`清理${daysToKeep}天前的旧测试文件...`);
    
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - daysToKeep);
    
    const files = this.getGeneratedFiles();
    let deletedCount = 0;
    
    files.forEach(file => {
      if (file.modified < cutoffDate) {
        fs.unlinkSync(file.path);
        deletedCount++;
      }
    });
    
    this.log(`已删除 ${deletedCount} 个旧测试文件`);
    
    return deletedCount;
  }
}

/**
 * 演示工作流
 */
async function demonstrateWorkflow() {
  console.log('=== CodeGen工作流演示 ===\n');

  // 创建工作流管理器
  const workflowManager = new CodegenWorkflowManager({
    outputDir: './generated-tests',
    backupDir: './test-backups'
  });

  // 备份现有测试
  workflowManager.backupExistingTests();

  // 示例1: 创建电商应用测试套件
  console.log('\n--- 示例1: 电商应用测试套件 ---');
  const ecommerceResults = await workflowManager.createFullApplicationTestSuite({
    name: 'ecommerce',
    url: 'https://demo.ecommerce.com',
    features: [
      { name: 'homepage', url: 'https://demo.ecommerce.com' },
      { name: 'product-list', url: 'https://demo.ecommerce.com/products' },
      { name: 'product-detail', url: 'https://demo.ecommerce.com/product/1' },
      { name: 'cart', url: 'https://demo.ecommerce.com/cart' },
      { name: 'checkout', url: 'https://demo.ecommerce.com/checkout' }
    ],
    devices: ['desktop', 'iPhone 12', 'iPad (gen 7)'],
    environments: ['development', 'staging']
  });

  // 示例2: 创建响应式设计测试
  console.log('\n--- 示例2: 响应式设计测试 ---');
  const responsiveResults = await workflowManager.createResponsiveDesignTest('https://demo.responsive.com', [
    { name: 'mobile-small', width: 320, height: 568 },
    { name: 'mobile-large', width: 414, height: 896 },
    { name: 'tablet-portrait', width: 768, height: 1024 },
    { name: 'tablet-landscape', width: 1024, height: 768 },
    { name: 'desktop-small', width: 1280, height: 720 },
    { name: 'desktop-large', width: 1920, height: 1080 }
  ]);

  // 示例3: 创建跨浏览器测试
  console.log('\n--- 示例3: 跨浏览器测试 ---');
  const crossBrowserResults = await workflowManager.createCrossBrowserTest('https://demo.crossbrowser.com', [
    'chromium', 'firefox', 'webkit'
  ]);

  // 示例4: 创建国际化测试
  console.log('\n--- 示例4: 国际化测试 ---');
  const i18nResults = await workflowManager.createInternationalizationTest('https://demo.i18n.com', [
    { code: 'en-US', name: 'english', timezone: 'America/New_York' },
    { code: 'zh-CN', name: 'chinese', timezone: 'Asia/Shanghai' },
    { code: 'ja-JP', name: 'japanese', timezone: 'Asia/Tokyo' },
    { code: 'de-DE', name: 'german', timezone: 'Europe/Berlin' }
  ]);

  // 生成综合报告
  console.log('\n--- 生成综合报告 ---');
  const allResults = [
    ...ecommerceResults,
    ...responsiveResults,
    ...crossBrowserResults,
    ...i18nResults
  ];

  const report = workflowManager.generateTestReport(allResults);

  // 清理旧文件
  console.log('\n--- 清理旧文件 ---');
  workflowManager.cleanupOldTests(3);

  console.log('\n=== 工作流演示完成 ===');
  
  return {
    ecommerceResults,
    responsiveResults,
    crossBrowserResults,
    i18nResults,
    report
  };
}

// 导出所有功能
module.exports = {
  CodegenWorkflowManager,
  demonstrateWorkflow
};

// 如果直接运行此文件，执行演示
if (require.main === module) {
  demonstrateWorkflow().catch(console.error);
}