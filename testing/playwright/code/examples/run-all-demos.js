/**
 * CodeGen扩展示例 - 运行所有演示
 * 
 * 这个脚本按顺序运行所有CodeGen演示，展示完整的扩展功能
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

class AllDemosRunner {
  constructor() {
    this.demos = [
      {
        name: '基础演示',
        file: 'codegen-demo.js',
        description: 'CodeGen基础功能演示'
      },
      {
        name: '高级演示',
        file: 'codegen-advanced-demo.js',
        description: 'CodeGen高级功能和配置演示'
      },
      {
        name: '工作流演示',
        file: 'codegen-workflow.js',
        description: 'CodeGen工作流自动化演示'
      },
      {
        name: '集成演示',
        file: 'codegen-integration-demo.js',
        description: 'CodeGen与其他工具集成演示'
      },
      {
        name: '最佳实践',
        file: 'codegen-best-practices.js',
        description: 'CodeGen最佳实践和模式演示'
      },
      {
        name: '故障排除',
        file: 'codegen-troubleshooting.js',
        description: 'CodeGen故障排除和常见问题解决'
      }
    ];
    
    this.results = [];
    this.startTime = Date.now();
  }

  /**
   * 检查文件是否存在
   */
  checkFileExists(filePath) {
    return fs.existsSync(filePath);
  }

  /**
   * 运行单个演示
   */
  runDemo(demo) {
    console.log(`\n🚀 运行演示: ${demo.name}`);
    console.log(`📋 描述: ${demo.description}`);
    console.log(`📁 文件: ${demo.file}`);
    console.log('━'.repeat(60));

    const demoPath = path.join(__dirname, demo.file);
    
    if (!this.checkFileExists(demoPath)) {
      console.log(`❌ 文件不存在: ${demo.file}`);
      return { success: false, error: '文件不存在' };
    }

    try {
      // 运行演示脚本
      const output = execSync(`node ${demo.file}`, {
        cwd: __dirname,
        encoding: 'utf8',
        timeout: 30000 // 30秒超时
      });
      
      console.log(output);
      console.log(`✅ ${demo.name} 运行成功`);
      
      return { success: true, output };
    } catch (error) {
      console.log(`❌ ${demo.name} 运行失败:`);
      console.log(error.message);
      
      return { success: false, error: error.message };
    }
  }

  /**
   * 运行所有演示
   */
  async runAllDemos() {
    console.log('🎯 CodeGen扩展专题 - 运行所有演示');
    console.log('═'.repeat(60));
    console.log('这个脚本将按顺序运行所有CodeGen扩展示例');
    console.log('演示包括：基础功能、高级特性、工作流、集成、最佳实践、故障排除');
    console.log('═'.repeat(60));

    for (const demo of this.demos) {
      const result = this.runDemo(demo);
      this.results.push({
        name: demo.name,
        file: demo.file,
        ...result
      });
      
      // 添加间隔，让输出更清晰
      console.log('\n' + '─'.repeat(60) + '\n');
    }

    this.showSummary();
  }

  /**
   * 显示运行总结
   */
  showSummary() {
    const endTime = Date.now();
    const duration = ((endTime - this.startTime) / 1000).toFixed(2);
    
    console.log('📊 运行总结');
    console.log('═'.repeat(60));
    
    const successful = this.results.filter(r => r.success).length;
    const failed = this.results.filter(r => !r.success).length;
    
    console.log(`✅ 成功: ${successful}/${this.results.length}`);
    console.log(`❌ 失败: ${failed}/${this.results.length}`);
    console.log(`⏱️  总耗时: ${duration}秒`);
    
    if (failed > 0) {
      console.log('\n失败的演示:');
      this.results.filter(r => !r.success).forEach(result => {
        console.log(`  ❌ ${result.name}: ${result.error}`);
      });
    }
    
    console.log('\n📁 生成的文件:');
    const outputDirs = [
      'generated-tests',
      'advanced-tests',
      'workflow-tests',
      'integration-tests',
      'best-practice-tests',
      'troubleshooting-tests'
    ];
    
    outputDirs.forEach(dir => {
      const dirPath = path.join(__dirname, dir);
      if (fs.existsSync(dirPath)) {
        const files = fs.readdirSync(dirPath);
        if (files.length > 0) {
          console.log(`  📂 ${dir}/ (${files.length}个文件)`);
          files.slice(0, 5).forEach(file => {
            console.log(`    - ${file}`);
          });
          if (files.length > 5) {
            console.log(`    ... 还有${files.length - 5}个文件`);
          }
        }
      }
    });
    
    console.log('\n🎉 CodeGen扩展专题演示完成！');
    console.log('═'.repeat(60));
    console.log('💡 使用建议:');
    console.log('  - 查看生成的测试文件来学习最佳实践');
    console.log('  - 使用 codegens-demo-runner.js 进行交互式演示');
    console.log('  - 根据项目需求选择合适的配置和模式');
    console.log('  - 参考最佳实践指南优化测试代码');
  }

  /**
   * 清理生成的文件
   */
  cleanup() {
    console.log('\n🧹 清理生成的文件...');
    
    const dirsToClean = [
      'generated-tests',
      'advanced-tests',
      'workflow-tests',
      'integration-tests',
      'best-practice-tests',
      'troubleshooting-tests'
    ];
    
    dirsToClean.forEach(dir => {
      const dirPath = path.join(__dirname, dir);
      if (fs.existsSync(dirPath)) {
        try {
          fs.rmSync(dirPath, { recursive: true, force: true });
          console.log(`  ✅ 已清理: ${dir}/`);
        } catch (error) {
          console.log(`  ❌ 清理失败: ${dir}/ - ${error.message}`);
        }
      }
    });
    
    console.log('🧽 清理完成');
  }
}

// 主函数
async function main() {
  const runner = new AllDemosRunner();
  
  // 检查命令行参数
  const args = process.argv.slice(2);
  
  if (args.includes('--cleanup') || args.includes('-c')) {
    runner.cleanup();
    return;
  }
  
  if (args.includes('--help') || args.includes('-h')) {
    console.log(`
CodeGen扩展示例 - 运行所有演示

用法: node run-all-demos.js [选项]

选项:
  --cleanup, -c    清理所有生成的文件
  --help, -h       显示帮助信息

示例:
  node run-all-demos.js          # 运行所有演示
  node run-all-demos.js --cleanup # 清理生成的文件
`);
    return;
  }
  
  // 运行所有演示
  await runner.runAllDemos();
}

// 运行主函数
if (require.main === module) {
  main().catch(console.error);
}

module.exports = { AllDemosRunner };