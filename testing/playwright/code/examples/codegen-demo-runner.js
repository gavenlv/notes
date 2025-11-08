// examples/codegen-demo-runner.js
/**
 * CodeGen演示运行器
 * 统一运行所有CodeGen示例和演示
 */

const { CodegenDemo } = require('./codegen-demo');
const { CodegenAdvancedDemo } = require('./codegen-advanced-demo');
const { CodegenWorkflowManager } = require('./codegen-workflow');
const { CodegenIntegrationManager } = require('./codegen-integration-demo');
const { CodegenBestPracticesManager, demonstrateBestPractices } = require('./codegen-best-practices');
const { CodegenTroubleshootingManager, demonstrateTroubleshooting } = require('./codegen-troubleshooting');

/**
 * CodeGen演示运行器
 */
class CodegenDemoRunner {
  constructor(options = {}) {
    this.options = {
      verbose: options.verbose || false,
      runAll: options.runAll || false,
      demoCategories: options.demoCategories || ['basic', 'advanced', 'workflow', 'integration', 'best-practices', 'troubleshooting'],
      ...options
    };
    
    this.results = {
      basic: null,
      advanced: null,
      workflow: null,
      integration: null,
      bestPractices: null,
      troubleshooting: null
    };
  }

  /**
   * 运行所有演示
   */
  async runAllDemos() {
    console.log('🚀 开始运行CodeGen完整演示...\n');

    const startTime = Date.now();

    try {
      // 1. 基础演示
      if (this.shouldRunDemo('basic')) {
        console.log('📚 运行基础演示...');
        this.results.basic = await this.runBasicDemo();
        console.log('✅ 基础演示完成\n');
      }

      // 2. 高级演示
      if (this.shouldRunDemo('advanced')) {
        console.log('🔧 运行高级演示...');
        this.results.advanced = await this.runAdvancedDemo();
        console.log('✅ 高级演示完成\n');
      }

      // 3. 工作流演示
      if (this.shouldRunDemo('workflow')) {
        console.log('⚙️ 运行工作流演示...');
        this.results.workflow = await this.runWorkflowDemo();
        console.log('✅ 工作流演示完成\n');
      }

      // 4. 集成演示
      if (this.shouldRunDemo('integration')) {
        console.log('🔗 运行集成演示...');
        this.results.integration = await this.runIntegrationDemo();
        console.log('✅ 集成演示完成\n');
      }

      // 5. 最佳实践演示
      if (this.shouldRunDemo('best-practices')) {
        console.log('⭐ 运行最佳实践演示...');
        this.results.bestPractices = await demonstrateBestPractices();
        console.log('✅ 最佳实践演示完成\n');
      }

      // 6. 故障排除演示
      if (this.shouldRunDemo('troubleshooting')) {
        console.log('🔍 运行故障排除演示...');
        this.results.troubleshooting = await demonstrateTroubleshooting();
        console.log('✅ 故障排除演示完成\n');
      }

      const endTime = Date.now();
      const duration = endTime - startTime;

      console.log(`🎉 所有演示完成！总耗时: ${(duration / 1000).toFixed(2)}秒`);
      
      this.generateSummaryReport();
      
      return this.results;
    } catch (error) {
      console.error('❌ 演示运行失败:', error.message);
      throw error;
    }
  }

  /**
   * 运行基础演示
   */
  async runBasicDemo() {
    try {
      // 这里可以调用具体的演示函数
      const demo = new CodegenDemo();
      return await demo.runAllDemos();
    } catch (error) {
      console.warn('基础演示运行失败:', error.message);
      return { error: error.message };
    }
  }

  /**
   * 运行高级演示
   */
  async runAdvancedDemo() {
    try {
      const demo = new CodegenAdvancedDemo();
      return await demo.runAllDemos();
    } catch (error) {
      console.warn('高级演示运行失败:', error.message);
      return { error: error.message };
    }
  }

  /**
   * 运行工作流演示
   */
  async runWorkflowDemo() {
    try {
      const workflowManager = new CodegenWorkflowManager();
      return await workflowManager.demonstrateAllWorkflows();
    } catch (error) {
      console.warn('工作流演示运行失败:', error.message);
      return { error: error.message };
    }
  }

  /**
   * 运行集成演示
   */
  async runIntegrationDemo() {
    try {
      const integrationManager = new CodegenIntegrationManager();
      return await integrationManager.demonstrateAllIntegrations();
    } catch (error) {
      console.warn('集成演示运行失败:', error.message);
      return { error: error.message };
    }
  }

  /**
   * 检查是否应该运行特定演示
   */
  shouldRunDemo(category) {
    if (this.options.runAll) {
      return true;
    }
    
    return this.options.demoCategories.includes(category);
  }

  /**
   * 生成汇总报告
   */
  generateSummaryReport() {
    console.log('\n📊 CodeGen演示汇总报告');
    console.log('=' .repeat(50));

    const categories = Object.keys(this.results);
    
    categories.forEach(category => {
      const result = this.results[category];
      const status = result && !result.error ? '✅ 成功' : '❌ 失败';
      const details = result?.error ? ` (${result.error})` : '';
      
      console.log(`${category.padEnd(20)} ${status}${details}`);
    });

    // 统计信息
    const successful = Object.values(this.results).filter(r => r && !r.error).length;
    const total = categories.length;
    
    console.log(`\n成功率: ${successful}/${total} (${((successful/total) * 100).toFixed(1)}%)`);
    
    // 生成建议
    this.generateRecommendations();
  }

  /**
   * 生成建议
   */
  generateRecommendations() {
    console.log('\n💡 建议:');
    
    const recommendations = [];
    
    // 基于结果生成建议
    if (!this.results.basic || this.results.basic.error) {
      recommendations.push('建议先学习CodeGen的基础用法');
    }
    
    if (!this.results.bestPractices || this.results.bestPractices.error) {
      recommendations.push('建议了解CodeGen的最佳实践');
    }
    
    if (!this.results.troubleshooting || this.results.troubleshooting.error) {
      recommendations.push('建议学习CodeGen的故障排除方法');
    }
    
    if (recommendations.length === 0) {
      recommendations.push('您已经掌握了CodeGen的核心概念！');
      recommendations.push('建议在实际项目中应用这些知识。');
    }
    
    recommendations.forEach(rec => {
      console.log(`  - ${rec}`);
    });
  }

  /**
   * 生成详细报告
   */
  generateDetailedReport() {
    return {
      timestamp: new Date().toISOString(),
      results: this.results,
      options: this.options,
      summary: {
        totalDemos: Object.keys(this.results).length,
        successfulDemos: Object.values(this.results).filter(r => r && !r.error).length,
        failedDemos: Object.values(this.results).filter(r => r && r.error).length
      },
      recommendations: this.generateRecommendationsList()
    };
  }

  /**
   * 生成建议列表
   */
  generateRecommendationsList() {
    const recommendations = [];
    
    // 基于演示结果生成具体建议
    if (this.results.bestPractices) {
      recommendations.push({
        category: '最佳实践',
        priority: 'high',
        description: '实施页面对象模式和数据驱动测试',
        actionItems: [
          '使用data-testid属性定位元素',
          '将测试数据与测试逻辑分离',
          '定期重构测试代码'
        ]
      });
    }
    
    if (this.results.troubleshooting) {
      recommendations.push({
        category: '故障排除',
        priority: 'medium',
        description: '建立测试稳定性保障机制',
        actionItems: [
          '监控测试执行趋势',
          '建立快速问题诊断流程',
          '维护测试环境一致性'
        ]
      });
    }
    
    if (this.results.integration) {
      recommendations.push({
        category: '集成',
        priority: 'medium',
        description: '将CodeGen集成到开发工作流',
        actionItems: [
          '配置CI/CD集成',
          '建立测试报告机制',
          '集成测试管理工具'
        ]
      });
    }
    
    return recommendations;
  }

  /**
   * 保存报告到文件
   */
  saveReportToFile(filename = 'codegen-demo-report.json') {
    const report = this.generateDetailedReport();
    const fs = require('fs');
    
    try {
      fs.writeFileSync(filename, JSON.stringify(report, null, 2));
      console.log(`\n📄 详细报告已保存到: ${filename}`);
      return true;
    } catch (error) {
      console.error('保存报告失败:', error.message);
      return false;
    }
  }
}

/**
 * 交互式演示运行器
 */
class InteractiveCodegenDemoRunner extends CodegenDemoRunner {
  constructor(options = {}) {
    super(options);
    this.readline = require('readline');
  }

  /**
   * 运行交互式演示
   */
  async runInteractiveDemo() {
    console.log('🎮 CodeGen交互式演示');
    console.log('=' .repeat(30));
    
    const choices = [
      '基础演示 (基本CodeGen用法)',
      '高级演示 (复杂场景和配置)',
      '工作流演示 (自动化工作流)',
      '集成演示 (与其他工具集成)',
      '最佳实践演示 (测试模式)',
      '故障排除演示 (问题解决)',
      '运行所有演示',
      '退出'
    ];

    const selectedChoice = await this.promptUser('请选择要运行的演示:', choices);
    
    if (selectedChoice === choices.length - 1) {
      console.log('感谢使用CodeGen演示！');
      return;
    }

    if (selectedChoice === choices.length - 2) {
      await this.runAllDemos();
      return;
    }

    // 运行选定的演示
    const demoMap = {
      0: () => this.runBasicDemo(),
      1: () => this.runAdvancedDemo(),
      2: () => this.runWorkflowDemo(),
      3: () => this.runIntegrationDemo(),
      4: () => demonstrateBestPractices(),
      5: () => demonstrateTroubleshooting()
    };

    const selectedDemo = demoMap[selectedChoice];
    if (selectedDemo) {
      console.log(`\n运行: ${choices[selectedChoice]}`);
      await selectedDemo();
    }

    // 询问是否继续
    const continueDemo = await this.promptUser('\n是否继续运行其他演示?', ['是', '否']);
    if (continueDemo === 0) {
      await this.runInteractiveDemo();
    }
  }

  /**
   * 提示用户选择
   */
  async promptUser(question, choices) {
    return new Promise((resolve) => {
      const rl = this.readline.createInterface({
        input: process.stdin,
        output: process.stdout
      });

      console.log(`\n${question}`);
      choices.forEach((choice, index) => {
        console.log(`${index + 1}. ${choice}`);
      });

      rl.question('\n请输入选项编号: ', (answer) => {
        rl.close();
        const choiceIndex = parseInt(answer) - 1;
        resolve(choiceIndex >= 0 && choiceIndex < choices.length ? choiceIndex : 0);
      });
    });
  }
}

/**
 * 演示运行函数
 */
async function runDemo(options = {}) {
  const runner = new CodegenDemoRunner(options);
  
  try {
    const results = await runner.runAllDemos();
    runner.saveReportToFile();
    
    return results;
  } catch (error) {
    console.error('演示运行失败:', error);
    throw error;
  }
}

/**
 * 交互式演示运行函数
 */
async function runInteractiveDemo(options = {}) {
  const runner = new InteractiveCodegenDemoRunner(options);
  
  try {
    await runner.runInteractiveDemo();
    runner.saveReportToFile('codegen-interactive-demo-report.json');
  } catch (error) {
    console.error('交互式演示运行失败:', error);
    throw error;
  }
}

// 导出所有功能
module.exports = {
  CodegenDemoRunner,
  InteractiveCodegenDemoRunner,
  runDemo,
  runInteractiveDemo
};

// 如果直接运行此文件，执行演示
if (require.main === module) {
  // 检查命令行参数
  const args = process.argv.slice(2);
  const isInteractive = args.includes('--interactive') || args.includes('-i');
  
  if (isInteractive) {
    runInteractiveDemo().catch(console.error);
  } else {
    runDemo({ verbose: true }).catch(console.error);
  }
}