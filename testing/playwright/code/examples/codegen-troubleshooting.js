// examples/codegen-troubleshooting.js
/**
 * CodeGen故障排除和常见问题解决方案
 * 提供CodeGen使用过程中的问题诊断和解决方法
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

/**
 * CodeGen故障排除管理器
 */
class CodegenTroubleshootingManager {
  constructor() {
    this.commonIssues = this.initializeCommonIssues();
    this.diagnosticTools = this.initializeDiagnosticTools();
    this.solutions = this.initializeSolutions();
  }

  initializeCommonIssues() {
    return {
      recordingIssues: [
        {
          id: 'REC001',
          title: 'CodeGen无法启动或录制',
          symptoms: [
            'CodeGen命令无响应',
            '浏览器无法打开',
            '录制界面不显示'
          ],
          causes: [
            'Playwright未正确安装',
            '浏览器依赖缺失',
            '端口冲突',
            '权限问题'
          ],
          diagnosis: this.diagnoseRecordingIssues,
          solutions: this.getRecordingSolutions
        },
        {
          id: 'REC002',
          title: '录制的操作不准确或丢失',
          symptoms: [
            '某些点击或输入未被录制',
            '录制的选择器不稳定',
            '操作顺序不正确'
          ],
          causes: [
            '页面加载时间不足',
            '动态内容加载延迟',
            '选择器策略不当',
            '网络延迟'
          ],
          diagnosis: this.diagnoseRecordingAccuracy,
          solutions: this.getRecordingAccuracySolutions
        }
      ],
      
      selectorIssues: [
        {
          id: 'SEL001',
          title: '生成的选择器不稳定或失败',
          symptoms: [
            '测试运行时找不到元素',
            '选择器在不同环境下失败',
            '选择器过于复杂'
          ],
          causes: [
            '使用自动生成的类名',
            '依赖元素位置',
            '忽略动态属性',
            '选择器过于具体'
          ],
          diagnosis: this.diagnoseSelectorIssues,
          solutions: this.getSelectorSolutions
        },
        {
          id: 'SEL002',
          title: '选择器在不同浏览器中表现不一致',
          symptoms: [
            'Chrome中工作正常，Firefox失败',
            '选择器行为跨浏览器不一致',
            '浏览器特定属性导致问题'
          ],
          causes: [
            '浏览器实现差异',
            'CSS属性支持差异',
            'JavaScript行为差异'
          ],
          diagnosis: this.diagnoseCrossBrowserSelectorIssues,
          solutions: this.getCrossBrowserSelectorSolutions
        }
      ],
      
      timingIssues: [
        {
          id: 'TIM001',
          title: '测试因时间问题失败',
          symptoms: [
            '元素未找到错误',
            '操作在元素就绪前执行',
            '测试在CI环境中失败但在本地通过'
          ],
          causes: [
            '硬编码等待时间',
            '忽略动态内容加载',
            '网络条件差异',
            '资源加载时间变化'
          ],
          diagnosis: this.diagnoseTimingIssues,
          solutions: this.getTimingSolutions
        }
      ],
      
      environmentIssues: [
        {
          id: 'ENV001',
          title: '环境配置问题',
          symptoms: [
            'CodeGen在不同环境中行为不同',
            'CI/CD管道中失败',
            '权限和路径问题'
          ],
          causes: [
            '环境变量配置不当',
            '依赖版本差异',
            '文件路径问题',
            '权限设置'
          ],
          diagnosis: this.diagnoseEnvironmentIssues,
          solutions: this.getEnvironmentSolutions
        }
      ]
    };
  }

  initializeDiagnosticTools() {
    return {
      systemInfo: this.collectSystemInfo,
      playwrightInfo: this.collectPlaywrightInfo,
      browserInfo: this.collectBrowserInfo,
      networkDiagnostics: this.performNetworkDiagnostics,
      performanceAnalysis: this.performPerformanceAnalysis
    };
  }

  initializeSolutions() {
    return {
      quickFixes: this.getQuickFixes(),
      advancedSolutions: this.getAdvancedSolutions(),
      preventionStrategies: this.getPreventionStrategies()
    };
  }

  /**
   * 诊断录制问题
   */
  async diagnoseRecordingIssues() {
    const diagnostics = {
      system: await this.collectSystemInfo(),
      playwright: await this.collectPlaywrightInfo(),
      browsers: await this.collectBrowserInfo()
    };

    const issues = [];

    // 检查Playwright安装
    if (!diagnostics.playwright.isInstalled) {
      issues.push('Playwright未正确安装');
    }

    // 检查浏览器安装
    if (diagnostics.browsers.missing.length > 0) {
      issues.push(`缺少浏览器: ${diagnostics.browsers.missing.join(', ')}`);
    }

    // 检查端口冲突
    if (await this.checkPortConflict()) {
      issues.push('端口冲突');
    }

    // 检查权限
    if (!await this.checkPermissions()) {
      issues.push('权限不足');
    }

    return {
      issues,
      diagnostics,
      recommendations: this.getRecommendationsForIssues(issues)
    };
  }

  /**
   * 收集系统信息
   */
  async collectSystemInfo() {
    try {
      const platform = process.platform;
      const arch = process.arch;
      const nodeVersion = process.version;
      const memory = process.memoryUsage();
      
      return {
        platform,
        arch,
        nodeVersion,
        memory,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      return { error: error.message };
    }
  }

  /**
   * 收集Playwright信息
   */
  async collectPlaywrightInfo() {
    try {
      const packageJson = JSON.parse(
        fs.readFileSync('./package.json', 'utf8')
      );
      
      const playwrightVersion = packageJson.dependencies?.['@playwright/test'] || 
                               packageJson.devDependencies?.['@playwright/test'] ||
                               'unknown';

      // 检查安装状态
      let isInstalled = false;
      try {
        execSync('npx playwright --version', { stdio: 'ignore' });
        isInstalled = true;
      } catch {
        isInstalled = false;
      }

      return {
        version: playwrightVersion,
        isInstalled,
        browsersInstalled: await this.checkBrowsersInstalled()
      };
    } catch (error) {
      return { error: error.message };
    }
  }

  /**
   * 检查浏览器安装状态
   */
  async checkBrowsersInstalled() {
    try {
      const result = execSync('npx playwright install --dry-run', { encoding: 'utf8' });
      return {
        installed: result.includes('already installed'),
        missing: this.extractMissingBrowsers(result)
      };
    } catch (error) {
      return { error: error.message, installed: false, missing: [] };
    }
  }

  extractMissingBrowsers(output) {
    const missing = [];
    if (output.includes('chromium')) missing.push('chromium');
    if (output.includes('firefox')) missing.push('firefox');
    if (output.includes('webkit')) missing.push('webkit');
    return missing;
  }

  /**
   * 检查端口冲突
   */
  async checkPortConflict() {
    // 简化的端口检查
    const commonPorts = [3000, 8080, 9000, 9323]; // Playwright常用端口
    
    for (const port of commonPorts) {
      try {
        const result = execSync(`netstat -an | findstr :${port}`, { encoding: 'utf8' });
        if (result.includes('LISTENING')) {
          return true; // 端口被占用
        }
      } catch {
        // 命令失败，继续检查其他端口
      }
    }
    
    return false;
  }

  /**
   * 检查权限
   */
  async checkPermissions() {
    try {
      // 检查当前目录写入权限
      fs.accessSync('.', fs.constants.W_OK);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * 获取录制问题的解决方案
   */
  getRecordingSolutions(issues) {
    const solutions = [];

    issues.forEach(issue => {
      switch (issue) {
        case 'Playwright未正确安装':
          solutions.push({
            title: '安装Playwright',
            steps: [
              '运行: npm install -D @playwright/test',
              '运行: npx playwright install',
              '验证安装: npx playwright --version'
            ],
            priority: 'high'
          });
          break;

        case '缺少浏览器':
          solutions.push({
            title: '安装缺失的浏览器',
            steps: [
              '运行: npx playwright install chromium',
              '或安装所有浏览器: npx playwright install',
              '检查安装状态: npx playwright install --dry-run'
            ],
            priority: 'high'
          });
          break;

        case '端口冲突':
          solutions.push({
            title: '解决端口冲突',
            steps: [
              '关闭占用端口的应用程序',
              '使用不同端口: --port 指定端口',
              '检查端口使用情况: netstat -an'
            ],
            priority: 'medium'
          });
          break;

        case '权限不足':
          solutions.push({
            title: '解决权限问题',
            steps: [
              '以管理员身份运行终端',
              '检查目录权限',
              '使用: chmod 755 . (Unix系统)'
            ],
            priority: 'medium'
          });
          break;
      }
    });

    return solutions;
  }

  /**
   * 诊断选择器问题
   */
  async diagnoseSelectorIssues(testCode) {
    const issues = [];

    // 分析测试代码中的选择器
    const selectors = this.extractSelectors(testCode);
    
    selectors.forEach(selector => {
      if (this.isUnstableSelector(selector)) {
        issues.push({
          type: 'unstable_selector',
          selector,
          reason: '使用自动生成的类名或位置'
        });
      }
      
      if (this.isOverlySpecificSelector(selector)) {
        issues.push({
          type: 'overly_specific',
          selector,
          reason: '选择器过于具体，容易受页面变化影响'
        });
      }
      
      if (this.isBrowserSpecificSelector(selector)) {
        issues.push({
          type: 'browser_specific',
          selector,
          reason: '使用浏览器特定的属性'
        });
      }
    });

    return {
      issues,
      selectors,
      recommendations: this.getSelectorRecommendations(issues)
    };
  }

  /**
   * 提取选择器
   */
  extractSelectors(testCode) {
    const selectorPatterns = [
      /locator\(['"`]([^'"`]+)['"`]/g,
      /page\.(?:click|fill|select)\.apply\(.*?['"`]([^'"`]+)['"`]/g,
      /waitForSelector\(['"`]([^'"`]+)['"`]/g
    ];

    const selectors = [];
    selectorPatterns.forEach(pattern => {
      let match;
      while ((match = pattern.exec(testCode)) !== null) {
        selectors.push(match[1]);
      }
    });

    return [...new Set(selectors)]; // 去重
  }

  /**
   * 检查选择器稳定性
   */
  isUnstableSelector(selector) {
    const unstablePatterns = [
      /^\..*-\d+$/, // 自动生成的类名
      /^\..*_\d+$/, // 带数字的类名
      /:nth-child\(/, // 位置依赖
      /^#/ // ID选择器（通常不稳定）
    ];

    return unstablePatterns.some(pattern => pattern.test(selector));
  }

  /**
   * 检查选择器是否过于具体
   */
  isOverlySpecificSelector(selector) {
    // 计算选择器的复杂度
    const complexity = selector.split(' ').length + 
                      selector.split('>').length +
                      selector.split('.').length - 1 +
                      selector.split('#').length - 1;
    
    return complexity > 5; // 复杂度阈值
  }

  /**
   * 获取选择器推荐
   */
  getSelectorRecommendations(issues) {
    const recommendations = [];

    issues.forEach(issue => {
      switch (issue.type) {
        case 'unstable_selector':
          recommendations.push({
            original: issue.selector,
            improved: this.improveSelector(issue.selector),
            reason: '使用data-testid或更稳定的属性'
          });
          break;

        case 'overly_specific':
          recommendations.push({
            original: issue.selector,
            improved: this.simplifySelector(issue.selector),
            reason: '简化选择器，减少依赖'
          });
          break;
      }
    });

    return recommendations;
  }

  /**
   * 改进选择器
   */
  improveSelector(selector) {
    // 将不稳定的类名替换为data-testid
    if (selector.startsWith('.') && selector.includes('-')) {
      const elementName = selector.substring(1).split('-')[0];
      return `[data-testid="${elementName}"]`;
    }
    
    // 移除位置依赖
    return selector.replace(/:nth-child\(\d+\)/, '');
  }

  /**
   * 简化选择器
   */
  simplifySelector(selector) {
    // 移除不必要的层级
    return selector.split(' ').slice(-2).join(' ');
  }

  /**
   * 获取快速修复方案
   */
  getQuickFixes() {
    return {
      recording: [
        {
          problem: 'CodeGen无法启动',
          solution: '运行: npx playwright install && npx playwright codegen'
        },
        {
          problem: '浏览器打不开',
          solution: '检查端口冲突，使用: --port 指定端口'
        },
        {
          problem: '录制不准确',
          solution: '增加等待时间: --slow-mo 1000'
        }
      ],
      
      selectors: [
        {
          problem: '选择器不稳定',
          solution: '使用data-testid属性替换CSS类名'
        },
        {
          problem: '选择器太复杂',
          solution: '简化选择器，使用更少的层级'
        },
        {
          problem: '跨浏览器问题',
          solution: '使用标准属性，避免浏览器特定选择器'
        }
      ],
      
      timing: [
        {
          problem: '测试因等待时间失败',
          solution: '使用waitForSelector替代固定等待'
        },
        {
          problem: '元素未找到',
          solution: '增加超时时间: page.setDefaultTimeout(10000)'
        }
      ]
    };
  }

  /**
   * 获取高级解决方案
   */
  getAdvancedSolutions() {
    return {
      recording: [
        {
          title: '自定义CodeGen配置',
          description: '创建自定义配置文件以解决复杂录制问题',
          steps: [
            '创建codegen.config.js文件',
            '配置自定义选择器策略',
            '设置适当的等待策略',
            '定义浏览器启动参数'
          ],
          example: `
// codegen.config.js
module.exports = {
  use: {
    browserName: 'chromium',
    viewport: { width: 1280, height: 720 },
    ignoreHTTPSErrors: true,
    slowMo: 100,
    selectorAttribute: 'data-testid'
  },
  codegen: {
    outputDir: './tests',
    preserveOutput: true,
    generateTests: true
  }
};
          `
        }
      ],
      
      debugging: [
        {
          title: '启用详细日志记录',
          description: '启用Playwright的详细日志以诊断问题',
          steps: [
            '设置环境变量: DEBUG=pw:api',
            '运行CodeGen时添加--debug标志',
            '分析生成的日志文件',
            '使用浏览器开发者工具'
          ]
        }
      ]
    };
  }

  /**
   * 获取预防策略
   */
  getPreventionStrategies() {
    return {
      recording: [
        '始终使用稳定的测试环境',
        '定期更新Playwright和浏览器',
        '使用版本控制管理测试代码',
        '建立测试数据管理策略',
        '实施代码审查流程'
      ],
      
      maintenance: [
        '定期重构测试代码',
        '监控测试执行趋势',
        '维护选择器库',
        '更新测试文档',
        '培训团队成员'
      ],
      
      quality: [
        '实施测试代码质量标准',
        '使用静态代码分析',
        '建立测试覆盖率目标',
        '定期审查测试有效性',
        '优化测试执行时间'
      ]
    };
  }

  /**
   * 生成故障排除报告
   */
  generateTroubleshootingReport(issues) {
    const report = {
      timestamp: new Date().toISOString(),
      systemInfo: this.collectSystemInfo(),
      issues: issues,
      solutions: this.getSolutionsForIssues(issues),
      recommendations: this.getGeneralRecommendations(),
      resources: this.getHelpfulResources()
    };

    return report;
  }

  /**
   * 获取问题解决方案
   */
  getSolutionsForIssues(issues) {
    const solutions = [];

    issues.forEach(issue => {
      const solutionsForIssue = this.solutions.quickFixes[issue.category] ||
                               this.solutions.advancedSolutions[issue.category];
      
      if (solutionsForIssue) {
        solutions.push({
          issue,
          solutions: solutionsForIssue.filter(s => 
            s.problem?.toLowerCase().includes(issue.description.toLowerCase())
          )
        });
      }
    });

    return solutions;
  }

  /**
   * 获取一般性建议
   */
  getGeneralRecommendations() {
    return [
      '始终保持Playwright和浏览器为最新版本',
      '使用版本控制管理测试代码和配置',
      '建立清晰的测试环境和数据管理策略',
      '定期审查和重构测试代码',
      '培训团队成员使用最佳实践',
      '建立测试失败时的快速响应机制',
      '维护测试文档和知识库'
    ];
  }

  /**
   * 获取有用资源
   */
  getHelpfulResources() {
    return {
      documentation: [
        {
          title: 'Playwright官方文档',
          url: 'https://playwright.dev/docs/intro',
          description: '完整的Playwright使用指南'
        },
        {
          title: 'CodeGen指南',
          url: 'https://playwright.dev/docs/codegen',
          description: 'CodeGen的详细使用说明'
        }
      ],
      
      community: [
        {
          title: 'Playwright GitHub',
          url: 'https://github.com/microsoft/playwright',
          description: '报告问题和获取支持'
        },
        {
          title: 'Stack Overflow',
          url: 'https://stackoverflow.com/questions/tagged/playwright',
          description: '社区问答和支持'
        }
      ],
      
      tools: [
        {
          title: 'Playwright Inspector',
          description: 'Playwright提供的调试工具'
        },
        {
          title: '浏览器开发者工具',
          description: '用于调试选择器和网络问题'
        }
      ]
    };
  }
}

/**
 * 故障排除演示
 */
async function demonstrateTroubleshooting() {
  console.log('=== CodeGen故障排除演示 ===\n');

  const troubleshootingManager = new CodegenTroubleshootingManager();

  // 演示系统诊断
  console.log('1. 系统信息诊断:');
  const systemInfo = await troubleshootingManager.collectSystemInfo();
  console.log(`   平台: ${systemInfo.platform}`);
  console.log(`   架构: ${systemInfo.arch}`);
  console.log(`   Node.js版本: ${systemInfo.nodeVersion}`);

  // 演示Playwright信息收集
  console.log('\n2. Playwright信息:');
  const playwrightInfo = await troubleshootingManager.collectPlaywrightInfo();
  console.log(`   安装状态: ${playwrightInfo.isInstalled ? '已安装' : '未安装'}`);
  console.log(`   版本: ${playwrightInfo.version}`);

  // 演示选择器分析
  console.log('\n3. 选择器问题分析:');
  const testCode = `
    await page.click('.button-12345');
    await page.fill('#input-field');
    await page.locator('div.container > div.row:nth-child(3) > div.col-md-6 > button.btn').click();
  `;
  
  const selectorAnalysis = await troubleshootingManager.diagnoseSelectorIssues(testCode);
  console.log(`   发现的选择器数量: ${selectorAnalysis.selectors.length}`);
  console.log(`   问题数量: ${selectorAnalysis.issues.length}`);
  
  selectorAnalysis.issues.forEach(issue => {
    console.log(`   - ${issue.selector}: ${issue.reason}`);
  });

  // 显示改进建议
  console.log('\n4. 选择器改进建议:');
  selectorAnalysis.recommendations.forEach(rec => {
    console.log(`   原始: ${rec.original}`);
    console.log(`   改进: ${rec.improved}`);
    console.log(`   原因: ${rec.reason}\n`);
  });

  // 显示快速修复方案
  console.log('5. 快速修复方案:');
  const quickFixes = troubleshootingManager.getQuickFixes();
  
  Object.entries(quickFixes).forEach(([category, fixes]) => {
    console.log(`   ${category}:`);
    fixes.forEach(fix => {
      console.log(`     - ${fix.problem}: ${fix.solution}`);
    });
  });

  // 生成故障排除报告
  console.log('\n6. 生成故障排除报告...');
  const sampleIssues = [
    { category: 'recording', description: 'CodeGen无法启动' },
    { category: 'selectors', description: '选择器不稳定' }
  ];
  
  const report = troubleshootingManager.generateTroubleshootingReport(sampleIssues);
  console.log(`   报告生成时间: ${report.timestamp}`);
  console.log(`   发现问题数量: ${report.issues.length}`);
  console.log(`   解决方案数量: ${report.solutions.length}`);

  console.log('\n=== 故障排除演示完成 ===');
  
  return {
    troubleshootingManager,
    systemInfo,
    playwrightInfo,
    selectorAnalysis,
    report
  };
}

// 导出所有功能
module.exports = {
  CodegenTroubleshootingManager,
  demonstrateTroubleshooting
};

// 如果直接运行此文件，执行演示
if (require.main === module) {
  demonstrateTroubleshooting().catch(console.error);
}