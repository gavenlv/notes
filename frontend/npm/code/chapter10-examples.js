/**
 * NPM企业级应用与实战 - 代码示例
 * 第10章：NPM企业级应用与实战
 */

// 示例1: 私有仓库配置与管理
const privateRegistryManager = {
  // 配置私有仓库
  configurePrivateRegistry(registryUrl, auth) {
    console.log(`配置私有仓库: ${registryUrl}`);
    
    // 模拟.npmrc配置
    const npmrcConfig = `
# 私有仓库配置
registry=${registryUrl}
//${registryUrl.replace('https://', '')}/:_authToken=${auth.token}
//${registryUrl.replace('https://', '')}/:always-auth=true
    `;
    
    console.log('生成的.npmrc配置:');
    console.log(npmrcConfig);
    
    return {
      registryUrl,
      auth: {
        type: auth.type || 'token',
        token: auth.token.replace(/./g, '*') // 隐藏实际token
      },
      configured: true
    };
  },
  
  // 包发布到私有仓库
  publishToPrivateRegistry(packageInfo, registryUrl) {
    console.log(`发布包 ${packageInfo.name}@${packageInfo.version} 到私有仓库`);
    
    // 模拟发布过程
    const publishSteps = [
      '验证包信息',
      '检查依赖关系',
      '构建包',
      '上传到私有仓库',
      '更新包索引'
    ];
    
    publishSteps.forEach((step, index) => {
      setTimeout(() => {
        console.log(`步骤 ${index + 1}/${publishSteps.length}: ${step}`);
      }, index * 200);
    });
    
    return {
      success: true,
      package: `${packageInfo.name}@${packageInfo.version}`,
      registry: registryUrl,
      publishedAt: new Date().toISOString()
    };
  },
  
  // 从私有仓库安装包
  installFromPrivateRegistry(packageName, registryUrl) {
    console.log(`从私有仓库安装包: ${packageName}`);
    
    // 模拟安装过程
    return {
      package: packageName,
      registry: registryUrl,
      version: '1.0.0', // 模拟版本
      installedAt: new Date().toISOString(),
      dependencies: ['lodash', 'axios'] // 模拟依赖
    };
  }
};

// 示例2: 企业级包管理策略
const enterprisePackageStrategy = {
  // 分析依赖关系
  analyzeDependencies(packageJson) {
    console.log('分析项目依赖关系...');
    
    const dependencies = packageJson.dependencies || {};
    const devDependencies = packageJson.devDependencies || {};
    
    // 模拟依赖分析
    const analysis = {
      totalDependencies: Object.keys(dependencies).length + Object.keys(devDependencies).length,
      productionDependencies: Object.keys(dependencies).length,
      developmentDependencies: Object.keys(devDependencies).length,
      outdatedPackages: [], // 模拟过时包
      securityVulnerabilities: [], // 模拟安全漏洞
      licenseIssues: [] // 模拟许可证问题
    };
    
    // 模拟一些问题
    if (dependencies.express) {
      analysis.outdatedPackages.push({
        name: 'express',
        current: dependencies.express,
        latest: '4.18.2',
        type: 'minor'
      });
    }
    
    if (dependencies.request) {
      analysis.securityVulnerabilities.push({
        name: 'request',
        severity: 'high',
        description: '请求库存在安全漏洞'
      });
    }
    
    console.log('依赖分析结果:', analysis);
    return analysis;
  },
  
  // 生成依赖报告
  generateDependencyReport(analysis) {
    console.log('生成依赖报告...');
    
    const report = {
      summary: {
        total: analysis.totalDependencies,
        production: analysis.productionDependencies,
        development: analysis.developmentDependencies
      },
      issues: {
        outdated: analysis.outdatedPackages.length,
        vulnerabilities: analysis.securityVulnerabilities.length,
        license: analysis.licenseIssues.length
      },
      recommendations: []
    };
    
    // 生成建议
    if (analysis.outdatedPackages.length > 0) {
      report.recommendations.push('建议更新过时的依赖包');
    }
    
    if (analysis.securityVulnerabilities.length > 0) {
      report.recommendations.push('立即修复安全漏洞');
    }
    
    if (analysis.licenseIssues.length > 0) {
      report.recommendations.push('解决许可证兼容性问题');
    }
    
    console.log('依赖报告:', report);
    return report;
  },
  
  // 版本锁定策略
  lockDependencies(packageJson, strategy = 'exact') {
    console.log(`应用版本锁定策略: ${strategy}`);
    
    const lockedPackageJson = { ...packageJson };
    
    switch (strategy) {
      case 'exact':
        // 精确版本锁定
        Object.keys(lockedPackageJson.dependencies || {}).forEach(pkg => {
          const version = lockedPackageJson.dependencies[pkg];
          lockedPackageJson.dependencies[pkg] = version.replace(/[~^]/g, '');
        });
        break;
        
      case 'minor':
        // 锁定主版本
        Object.keys(lockedPackageJson.dependencies || {}).forEach(pkg => {
          const version = lockedPackageJson.dependencies[pkg];
          lockedPackageJson.dependencies[pkg] = `^${version.replace(/[~^]/g, '')}`;
        });
        break;
        
      case 'patch':
        // 锁定主次版本
        Object.keys(lockedPackageJson.dependencies || {}).forEach(pkg => {
          const version = lockedPackageJson.dependencies[pkg];
          lockedPackageJson.dependencies[pkg] = `~${version.replace(/[~^]/g, '')}`;
        });
        break;
    }
    
    console.log('版本锁定后的package.json:', lockedPackageJson.dependencies);
    return lockedPackageJson;
  }
};

// 示例3: CI/CD集成
const cicdIntegration = {
  // 生成CI配置
  generateCIConfig(platform, options = {}) {
    console.log(`生成${platform} CI配置...`);
    
    let config = '';
    
    switch (platform.toLowerCase()) {
      case 'github':
        config = this.generateGitHubActionsConfig(options);
        break;
      case 'gitlab':
        config = this.generateGitLabCIConfig(options);
        break;
      case 'jenkins':
        config = this.generateJenkinsConfig(options);
        break;
      default:
        config = '# 不支持的CI平台';
    }
    
    return config;
  },
  
  // GitHub Actions配置
  generateGitHubActionsConfig(options) {
    const { nodeVersion = '16', registryUrl, installCommand = 'npm ci', testCommand = 'npm test' } = options;
    
    return `
name: Node.js CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        node-version: [${nodeVersion}]
        
    steps:
    - uses: actions/checkout@v3
    
    - name: Use Node.js \${{ matrix.node-version }}
      uses: actions/setup-node@v3
      with:
        node-version: \${{ matrix.node-version }}
        ${registryUrl ? `registry-url: ${registryUrl}` : ''}
        
    - name: Install dependencies
      run: ${installCommand}
      ${registryUrl ? `env:\n        NODE_AUTH_TOKEN: \${{ secrets.NPM_TOKEN }}` : ''}
        
    - name: Run tests
      run: ${testCommand}
      
    - name: Build application
      run: npm run build
      
    ${options.publish ? `
    - name: Publish to registry
      run: npm publish
      ${registryUrl ? `env:\n        NODE_AUTH_TOKEN: \${{ secrets.NPM_TOKEN }}` : ''}
    ` : ''}
`;
  },
  
  // GitLab CI配置
  generateGitLabCIConfig(options) {
    const { nodeVersion = '16', registryUrl } = options;
    
    return `
stages:
  - install
  - test
  - build
  - deploy

variables:
  NODE_VERSION: "${nodeVersion}"
  ${registryUrl ? `NPM_REGISTRY: "${registryUrl}"` : ''}

install_dependencies:
  stage: install
  image: node:\${NODE_VERSION}
  script:
    - npm ci
  cache:
    paths:
      - node_modules/
  artifacts:
    paths:
      - node_modules/

run_tests:
  stage: test
  image: node:\${NODE_VERSION}
  script:
    - npm test
  dependencies:
    - install_dependencies

build_application:
  stage: build
  image: node:\${NODE_VERSION}
  script:
    - npm run build
  dependencies:
    - install_dependencies
  artifacts:
    paths:
      - dist/

${options.publish ? `
publish_package:
  stage: deploy
  image: node:\${NODE_VERSION}
  script:
    - npm publish
  dependencies:
    - build_application
  only:
    - main
` : ''}
`;
  },
  
  // Jenkins配置
  generateJenkinsConfig(options) {
    const { nodeVersion = '16', registryUrl } = options;
    
    return `
pipeline {
    agent any
    
    tools {
        nodejs "NodeJS ${nodeVersion}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Install Dependencies') {
            steps {
                sh 'npm ci'
            }
        }
        
        stage('Run Tests') {
            steps {
                sh 'npm test'
            }
        }
        
        stage('Build Application') {
            steps {
                sh 'npm run build'
            }
        }
        
        ${options.publish ? `
        stage('Publish Package') {
            steps {
                ${registryUrl ? `sh 'npm config set registry ${registryUrl}'` : ''}
                sh 'npm publish'
            }
        }
        ` : ''}
    }
    
    post {
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
`;
  }
};

// 示例4: 微服务架构中的NPM管理
const microserviceNpmManagement = {
  // 分析微服务依赖
  analyzeMicroserviceDependencies(services) {
    console.log('分析微服务架构中的依赖关系...');
    
    const dependencyMap = new Map();
    const sharedDependencies = new Map();
    
    services.forEach(service => {
      const { name, dependencies = {} } = service;
      
      Object.keys(dependencies).forEach(dep => {
        if (!dependencyMap.has(dep)) {
          dependencyMap.set(dep, []);
        }
        
        dependencyMap.get(dep).push({
          service: name,
          version: dependencies[dep]
        });
        
        // 统计共享依赖
        if (dependencyMap.get(dep).length > 1) {
          if (!sharedDependencies.has(dep)) {
            sharedDependencies.set(dep, new Set());
          }
          
          dependencyMap.get(dep).forEach(item => {
            sharedDependencies.get(dep).add(item.service);
          });
        }
      });
    });
    
    // 转换为数组格式
    const result = {
      totalDependencies: dependencyMap.size,
      sharedDependencies: Array.from(sharedDependencies.entries()).map(([dep, services]) => ({
        name: dep,
        usedBy: Array.from(services),
        versions: dependencyMap.get(dep).map(item => item.version)
      })),
      uniqueDependencies: Array.from(dependencyMap.entries())
        .filter(([dep]) => !sharedDependencies.has(dep))
        .map(([dep, services]) => ({
          name: dep,
          usedBy: services.map(s => s.service),
          versions: services.map(s => s.version)
        }))
    };
    
    console.log('微服务依赖分析结果:', result);
    return result;
  },
  
  // 生成共享库建议
  generateSharedLibraryRecommendations(dependencyAnalysis) {
    console.log('生成共享库建议...');
    
    const recommendations = [];
    
    // 分析共享依赖
    dependencyAnalysis.sharedDependencies.forEach(dep => {
      // 检查版本一致性
      const uniqueVersions = [...new Set(dep.versions)];
      
      if (uniqueVersions.length > 1) {
        recommendations.push({
          type: 'version-consistency',
          dependency: dep.name,
          issue: `版本不一致: ${uniqueVersions.join(', ')}`,
          recommendation: '统一所有微服务中的版本',
          priority: 'high'
        });
      }
      
      // 检查是否适合提取为共享库
      if (dep.usedBy.length >= 3) {
        recommendations.push({
          type: 'shared-library',
          dependency: dep.name,
          usedBy: dep.usedBy,
          recommendation: '考虑将此依赖提取为共享库',
          priority: 'medium'
        });
      }
    });
    
    // 分析重复功能
    const functionalGroups = this.groupDependenciesByFunction(dependencyAnalysis);
    functionalGroups.forEach(group => {
      if (group.dependencies.length > 2 && group.services.length > 2) {
        recommendations.push({
          type: 'functional-group',
          groupName: group.name,
          dependencies: group.dependencies,
          usedBy: group.services,
          recommendation: `考虑将${group.name}相关功能提取为共享模块`,
          priority: 'medium'
        });
      }
    });
    
    console.log('共享库建议:', recommendations);
    return recommendations;
  },
  
  // 按功能分组依赖
  groupDependenciesByFunction(dependencyAnalysis) {
    // 简化的功能分组逻辑
    const functionalGroups = [
      {
        name: 'HTTP客户端',
        keywords: ['axios', 'request', 'fetch', 'got'],
        dependencies: [],
        services: new Set()
      },
      {
        name: '数据库',
        keywords: ['mongoose', 'sequelize', 'prisma', 'knex'],
        dependencies: [],
        services: new Set()
      },
      {
        name: '日志',
        keywords: ['winston', 'bunyan', 'pino', 'log4js'],
        dependencies: [],
        services: new Set()
      },
      {
        name: '验证',
        keywords: ['joi', 'yup', 'validator', 'express-validator'],
        dependencies: [],
        services: new Set()
      }
    ];
    
    // 将依赖分组
    [...dependencyAnalysis.sharedDependencies, ...dependencyAnalysis.uniqueDependencies].forEach(dep => {
      functionalGroups.forEach(group => {
        if (group.keywords.some(keyword => dep.name.includes(keyword))) {
          group.dependencies.push(dep.name);
          dep.usedBy.forEach(service => group.services.add(service));
        }
      });
    });
    
    // 转换Set为数组
    return functionalGroups.map(group => ({
      ...group,
      services: Array.from(group.services)
    })).filter(group => group.dependencies.length > 0);
  }
};

// 示例5: 大型项目依赖管理
const largeProjectDependencyManagement = {
  // 依赖图分析
  analyzeDependencyGraph(packageLock) {
    console.log('分析项目依赖图...');
    
    // 模拟依赖图分析
    const analysis = {
      totalPackages: 0,
      maxDepth: 0,
      circularDependencies: [],
      duplicateDependencies: [],
      sizeAnalysis: {
        totalSize: 0,
        largestPackages: []
      },
      licenseAnalysis: {
        allowed: 0,
        restricted: 0,
        unknown: 0
      }
    };
    
    // 模拟一些分析结果
    analysis.totalPackages = 542;
    analysis.maxDepth = 8;
    analysis.circularDependencies = [
      {
        cycle: ['package-a', 'package-b', 'package-c', 'package-a'],
        severity: 'medium'
      }
    ];
    analysis.duplicateDependencies = [
      {
        name: 'lodash',
        versions: ['4.17.20', '4.17.21'],
        dependents: ['dep1', 'dep2', 'dep3']
      }
    ];
    analysis.sizeAnalysis.totalSize = '256MB';
    analysis.sizeAnalysis.largestPackages = [
      { name: 'webpack', size: '45MB' },
      { name: 'react-dom', size: '38MB' },
      { name: 'babel-core', size: '32MB' }
    ];
    analysis.licenseAnalysis = {
      allowed: 480,
      restricted: 2,
      unknown: 60
    };
    
    console.log('依赖图分析结果:', analysis);
    return analysis;
  },
  
  // 优化依赖
  optimizeDependencies(analysis, options = {}) {
    console.log('优化项目依赖...');
    
    const optimizations = [];
    
    // 处理重复依赖
    if (analysis.duplicateDependencies.length > 0) {
      analysis.duplicateDependencies.forEach(dep => {
        const latestVersion = dep.versions.sort((a, b) => {
          // 简化版本比较
          return b.localeCompare(a);
        })[0];
        
        optimizations.push({
          type: 'deduplication',
          dependency: dep.name,
          action: `统一版本到 ${latestVersion}`,
          impact: '减少包大小，避免潜在冲突',
          effort: 'low'
        });
      });
    }
    
    // 处理循环依赖
    if (analysis.circularDependencies.length > 0) {
      analysis.circularDependencies.forEach(circular => {
        optimizations.push({
          type: 'circular-dependency',
          dependency: circular.cycle.join(' -> '),
          action: '重构代码以消除循环依赖',
          impact: '提高构建性能，避免潜在问题',
          effort: 'high'
        });
      });
    }
    
    // 处理大包
    if (options.optimizeSize && analysis.sizeAnalysis.largestPackages.length > 0) {
      analysis.sizeAnalysis.largestPackages.forEach(pkg => {
        optimizations.push({
          type: 'size-optimization',
          dependency: pkg.name,
          action: '检查是否可以替换为更轻量级的替代方案',
          impact: '显著减少包大小',
          effort: 'medium'
        });
      });
    }
    
    // 处理许可证问题
    if (options.checkLicenses && analysis.licenseAnalysis.restricted > 0) {
      optimizations.push({
        type: 'license-compliance',
        dependency: '受限许可证包',
        action: '替换为具有兼容许可证的替代方案',
        impact: '确保法律合规性',
        effort: 'high'
      });
    }
    
    console.log('依赖优化建议:', optimizations);
    return optimizations;
  },
  
  // 生成依赖管理策略
  generateDependencyManagementStrategy(analysis, optimizations) {
    console.log('生成依赖管理策略...');
    
    const strategy = {
      governance: {
        approvalProcess: '所有新依赖需要团队审批',
        reviewFrequency: '每月进行依赖审查',
        updatePolicy: '自动补丁更新，手动次版本和主版本更新'
      },
      tools: [
        {
          name: 'npm audit',
          purpose: '安全漏洞扫描',
          frequency: '每次CI/CD运行'
        },
        {
          name: 'depcheck',
          purpose: '检测未使用的依赖',
          frequency: '每周'
        },
        {
          name: 'bundlephobia',
          purpose: '分析包大小影响',
          frequency: '添加新依赖时'
        }
      ],
      policies: [
        {
          name: '版本锁定',
          description: '生产环境使用精确版本锁定'
        },
        {
          name: '许可证检查',
          description: '只允许MIT、Apache-2.0、BSD-3-Clause等许可证'
        },
        {
          name: '大小限制',
          description: '单个依赖不超过50MB，总依赖不超过500MB'
        }
      ],
      implementation: {
        immediate: optimizations.filter(opt => opt.effort === 'low'),
        shortTerm: optimizations.filter(opt => opt.effort === 'medium'),
        longTerm: optimizations.filter(opt => opt.effort === 'high')
      }
    };
    
    console.log('依赖管理策略:', strategy);
    return strategy;
  }
};

// 示例6: 企业级安全策略
const enterpriseSecurityStrategy = {
  // 生成安全配置
  generateSecurityConfig(options = {}) {
    console.log('生成企业级安全配置...');
    
    const {
      allowedLicenses = ['MIT', 'Apache-2.0', 'BSD-3-Clause', 'ISC'],
      blockedPackages = [],
      vulnerabilitySeverity = 'moderate',
      codeSigning = true
    } = options;
    
    const config = {
      npmrc: `
# 企业级安全配置
# 启用严格SSL
strict-ssl=true

# 禁用Git SSH协议（可能不安全）
git-ssh-protocol=ssh

# 禁用脚本执行（可选，根据企业策略）
# script-shell=false

# 设置超时
fetch-timeout=60000
fetch-retry-mintimeout=20000

# 审计配置
audit-level=${vulnerabilitySeverity}
audit-force=true
      `,
      packageJson: {
        scripts: {
          'security-check': 'npm audit --audit-level moderate',
          'license-check': 'license-checker --onlyAllow \'' + allowedLicenses.join(',') + '\'',
          'outdated-check': 'npm outdated',
          'preinstall': 'npx check-for-blocked-packages',
          'postinstall': 'npm audit --audit-level moderate'
        },
        devDependencies: {
          'license-checker': '^25.0.1',
          'audit-ci': '^6.0.0',
          'check-for-blocked-packages': '^1.0.0'
        }
      },
      blockedPackages,
      allowedLicenses,
      codeSigning
    };
    
    console.log('安全配置:', config);
    return config;
  },
  
  // 安全审计流程
  performSecurityAudit(packageInfo) {
    console.log(`执行安全审计: ${packageInfo.name}@${packageInfo.version}`);
    
    // 模拟安全审计流程
    const auditSteps = [
      '检查已知漏洞数据库',
      '分析依赖传递性漏洞',
      '验证许可证兼容性',
      '检查包完整性',
      '分析代码模式'
    ];
    
    const auditResults = {
      package: `${packageInfo.name}@${packageInfo.version}`,
      timestamp: new Date().toISOString(),
      vulnerabilities: [],
      licenseIssues: [],
      integrityIssues: [],
      codeIssues: [],
      overallScore: 0 // 0-100分
    };
    
    // 模拟一些审计结果
    auditResults.vulnerabilities = [
      {
        id: 'CVE-2021-23424',
        severity: 'moderate',
        title: '正则表达式拒绝服务漏洞',
        url: 'https://github.com/advisories/GHSA-xxxx'
      }
    ];
    
    auditResults.licenseIssues = [
      {
        type: 'restricted',
        license: 'GPL-3.0',
        description: '许可证与企业策略不兼容'
      }
    ];
    
    // 计算安全评分
    let score = 100;
    score -= auditResults.vulnerabilities.length * 20;
    score -= auditResults.licenseIssues.length * 15;
    score -= auditResults.integrityIssues.length * 25;
    score -= auditResults.codeIssues.length * 10;
    
    auditResults.overallScore = Math.max(0, score);
    
    console.log('安全审计结果:', auditResults);
    return auditResults;
  },
  
  // 生成安全报告
  generateSecurityReport(auditResults) {
    console.log('生成安全报告...');
    
    const report = {
      summary: {
        package: auditResults.package,
        timestamp: auditResults.timestamp,
        overallScore: auditResults.overallScore,
        status: auditResults.overallScore >= 80 ? '通过' : '未通过'
      },
      findings: {
        vulnerabilities: auditResults.vulnerabilities.length,
        licenseIssues: auditResults.licenseIssues.length,
        integrityIssues: auditResults.integrityIssues.length,
        codeIssues: auditResults.codeIssues.length
      },
      recommendations: []
    };
    
    // 生成建议
    if (auditResults.vulnerabilities.length > 0) {
      report.recommendations.push({
        priority: 'high',
        action: '修复安全漏洞',
        details: '更新到最新版本或应用补丁'
      });
    }
    
    if (auditResults.licenseIssues.length > 0) {
      report.recommendations.push({
        priority: 'medium',
        action: '解决许可证问题',
        details: '替换为具有兼容许可证的替代方案'
      });
    }
    
    if (auditResults.overallScore < 80) {
      report.recommendations.push({
        priority: 'medium',
        action: '提高包安全性',
        details: '考虑使用更安全的替代方案'
      });
    }
    
    console.log('安全报告:', report);
    return report;
  }
};

// 示例7: 企业级最佳实践
const enterpriseBestPractices = {
  // 生成最佳实践指南
  generateBestPracticesGuide() {
    console.log('生成企业级NPM最佳实践指南...');
    
    const guide = {
      development: [
        {
          practice: '使用精确版本',
          description: '生产环境使用精确版本锁定，避免意外更新',
          example: '"lodash": "4.17.21" 而不是 "^4.17.21"'
        },
        {
          practice: '定期更新依赖',
          description: '建立定期更新机制，平衡安全性和稳定性',
          example: '每月进行依赖审查和更新'
        },
        {
          practice: '最小化依赖',
          description: '只添加必要的依赖，减少攻击面',
          example: '使用功能检测而非完整库'
        }
      ],
      security: [
        {
          practice: '自动化安全扫描',
          description: '在CI/CD流程中集成安全扫描',
          example: 'npm audit --audit-level moderate'
        },
        {
          practice: '许可证合规',
          description: '确保所有依赖许可证与企业策略兼容',
          example: '使用license-checker工具检查许可证'
        },
        {
          practice: '包完整性验证',
          description: '验证包的完整性和来源',
          example: '使用npm签名功能验证包'
        }
      ],
      governance: [
        {
          practice: '依赖审批流程',
          description: '建立新依赖的审批流程',
          example: '所有新依赖需要架构师审批'
        },
        {
          practice: '版本策略',
          description: '制定明确的版本更新策略',
          example: '自动补丁更新，手动次版本和主版本更新'
        },
        {
          practice: '文档维护',
          description: '维护依赖决策文档',
          example: '记录选择特定依赖的原因'
        }
      ],
      operations: [
        {
          practice: '私有仓库',
          description: '使用私有仓库管理内部包',
          example: '设置Verdaccio或NPM Enterprise'
        },
        {
          practice: '缓存策略',
          description: '优化NPM缓存以提高构建速度',
          example: '在CI/CD中缓存node_modules'
        },
        {
          practice: '监控和告警',
          description: '监控依赖安全状态并设置告警',
          example: '使用Dependabot或Snyk监控依赖'
        }
      ]
    };
    
    console.log('最佳实践指南:', guide);
    return guide;
  },
  
  // 评估实践成熟度
  assessPracticeMaturity(currentPractices) {
    console.log('评估企业NPM实践成熟度...');
    
    const maturityLevels = {
      1: '初始级',
      2: '可重复级',
      3: '已定义级',
      4: '已管理级',
      5: '优化级'
    };
    
    // 最佳实践检查清单
    const checklist = {
      versionControl: {
        description: '版本控制策略',
        weight: 10
      },
      securityScanning: {
        description: '自动化安全扫描',
        weight: 15
      },
      dependencyReview: {
        description: '定期依赖审查',
        weight: 10
      },
      privateRegistry: {
        description: '私有仓库使用',
        weight: 10
      },
      licenseCompliance: {
        description: '许可证合规检查',
        weight: 10
      },
      automatedUpdates: {
        description: '自动化更新流程',
        weight: 10
      },
      documentation: {
        description: '依赖决策文档',
        weight: 5
      },
      monitoring: {
        description: '依赖监控和告警',
        weight: 10
      },
      ciIntegration: {
        description: 'CI/CD集成',
        weight: 10
      },
      teamTraining: {
        description: '团队培训',
        weight: 5
      }
    };
    
    // 计算成熟度分数
    let totalScore = 0;
    let maxScore = 0;
    
    Object.keys(checklist).forEach(practice => {
      const weight = checklist[practice].weight;
      maxScore += weight;
      
      if (currentPractices[practice]) {
        totalScore += weight;
      }
    });
    
    const percentage = (totalScore / maxScore) * 100;
    let maturityLevel;
    
    if (percentage >= 90) {
      maturityLevel = 5;
    } else if (percentage >= 70) {
      maturityLevel = 4;
    } else if (percentage >= 50) {
      maturityLevel = 3;
    } else if (percentage >= 30) {
      maturityLevel = 2;
    } else {
      maturityLevel = 1;
    }
    
    const assessment = {
      score: percentage.toFixed(1),
      level: maturityLevel,
      levelName: maturityLevels[maturityLevel],
      strengths: [],
      improvements: []
    };
    
    // 识别优势和改进领域
    Object.keys(checklist).forEach(practice => {
      if (currentPractices[practice]) {
        assessment.strengths.push(checklist[practice].description);
      } else {
        assessment.improvements.push(checklist[practice].description);
      }
    });
    
    console.log('实践成熟度评估:', assessment);
    return assessment;
  }
};

// 示例8: 实战案例 - 大型电商平台NPM管理
const ecommerceCaseStudy = {
  // 项目背景
  projectBackground: {
    name: '大型电商平台',
    description: '支持百万级用户的B2C电商平台',
    architecture: '微服务架构',
    services: 25,
    frontendApps: 8,
    totalDependencies: 1200,
    challenges: [
      '依赖版本一致性',
      '安全漏洞管理',
      '构建性能优化',
      '私有包管理',
      '许可证合规'
    ]
  },
  
  // 解决方案
  solutions: {
    // 私有仓库设置
    privateRegistry: {
      solution: '搭建Verdaccio私有仓库',
      implementation: `
# .npmrc配置
registry=https://npm.company.com
//npm.company.com/:_authToken=\${NPM_TOKEN}
//npm.company.com/:always-auth=true
      `,
      benefits: [
        '统一管理内部包',
        '提高下载速度',
        '增强安全性',
        '减少外部依赖'
      ]
    },
    
    // 依赖管理策略
    dependencyManagement: {
      solution: '实施分层依赖管理策略',
      coreLibraries: {
        description: '核心库统一管理',
        examples: ['@company/ui-components', '@company/utils', '@company/auth'],
        versioning: '严格语义化版本控制'
      },
      thirdPartyLibraries: {
        description: '第三方库定期审查',
        reviewCycle: '每月',
        updateStrategy: '自动补丁，手动次版本'
      },
      benefits: [
        '减少版本冲突',
        '提高安全性',
        '简化维护'
      ]
    },
    
    // CI/CD集成
    cicdIntegration: {
      solution: '全流程CI/CD集成',
      pipeline: [
        '代码检查',
        '安全扫描',
        '单元测试',
        '集成测试',
        '构建',
        '部署到测试环境',
        '自动部署到生产环境（仅主分支）'
      ],
      tools: ['GitHub Actions', 'SonarQube', 'Snyk'],
      benefits: [
        '自动化流程',
        '质量保证',
        '快速反馈'
      ]
    },
    
    // 安全策略
    securityStrategy: {
      solution: '多层次安全策略',
      measures: [
        '自动化漏洞扫描',
        '许可证合规检查',
        '包完整性验证',
        '私有仓库访问控制',
        '定期安全培训'
      ],
      tools: ['npm audit', 'Snyk', 'license-checker'],
      benefits: [
        '降低安全风险',
        '确保合规性',
        '提高安全意识'
      ]
    }
  },
  
  // 实施效果
  results: {
    before: {
      buildTime: '25分钟',
      securityIssues: 45,
      dependencyConflicts: 12,
      licenseViolations: 8,
      deploymentFrequency: '每周'
    },
    after: {
      buildTime: '12分钟',
      securityIssues: 5,
      dependencyConflicts: 0,
      licenseViolations: 0,
      deploymentFrequency: '每日'
    },
    improvements: [
      '构建时间减少52%',
      '安全问题减少89%',
      '消除所有依赖冲突',
      '解决所有许可证问题',
      '部署频率提高7倍'
    ]
  },
  
  // 经验总结
  lessonsLearned: [
    {
      lesson: '依赖管理需要系统性方法',
      detail: '单一工具无法解决所有问题，需要组合多种策略'
    },
    {
      lesson: '自动化是关键',
      detail: '手动流程容易出错，自动化确保一致性和可靠性'
    },
    {
      lesson: '文化变革同样重要',
      detail: '工具和流程需要配合团队文化变革才能发挥最大效果'
    },
    {
      lesson: '持续改进',
      detail: '依赖管理是持续过程，需要定期评估和优化'
    }
  ]
};

// 示例9: 企业级NPM工具集
const enterpriseNpmToolset = {
  // 生成工具推荐
  generateToolRecommendations(requirements) {
    console.log('生成企业级NPM工具推荐...');
    
    const tools = {
      security: [
        {
          name: 'npm audit',
          description: 'NPM内置安全审计工具',
          pros: ['免费', '内置', '易于使用'],
          cons: ['功能有限', '误报较多'],
          pricing: '免费',
          recommendation: '基础安全检查'
        },
        {
          name: 'Snyk',
          description: '全面的安全扫描平台',
          pros: ['准确率高', '修复建议详细', '集成广泛'],
          cons: ['付费', '配置复杂'],
          pricing: '免费版 + 付费版',
          recommendation: '企业级安全需求'
        },
        {
          name: 'WhiteSource',
          description: '开源组件安全与合规管理',
          pros: ['全面覆盖', '许可证管理', '报告详细'],
          cons: ['价格较高', '学习曲线陡峭'],
          pricing: '企业订阅',
          recommendation: '大型企业合规需求'
        }
      ],
      dependencyManagement: [
        {
          name: 'Dependabot',
          description: 'GitHub内置依赖更新工具',
          pros: ['免费', '自动PR', '与GitHub集成'],
          cons: ['仅限GitHub', '配置选项有限'],
          pricing: '免费',
          recommendation: 'GitHub项目依赖更新'
        },
        {
          name: 'Renovate',
          description: '自动化依赖更新工具',
          pros: '高度可配置', '多平台支持', '灵活策略'],
          cons: ['配置复杂', '需要自托管'],
          pricing: '免费 + 付费托管',
          recommendation: '复杂依赖更新需求'
        },
        {
          name: 'Greenkeeper',
          description: 'NPM依赖更新服务',
          pros: ['简单易用', '与NPM集成'],
          cons: ['功能有限', '已停止维护'],
          pricing: '免费',
          recommendation: '不推荐，已停止维护'
        }
      ],
      privateRegistry: [
        {
          name: 'Verdaccio',
          description: '轻量级私有NPM代理',
          pros: ['开源', '易于部署', '功能齐全'],
          cons: ['企业功能有限', '需要自行维护'],
          pricing: '免费',
          recommendation: '中小型团队私有仓库'
        },
        {
          name: 'NPM Enterprise',
          description: 'NPM官方企业版',
          pros: ['官方支持', '功能全面', '安全可靠'],
          cons: ['价格昂贵', '供应商锁定'],
          pricing: '企业订阅',
          recommendation: '大型企业关键项目'
        },
        {
          name: 'Artifactory',
          description: '通用制品库管理',
          pros: ['多格式支持', '企业级功能', '高可用'],
          cons: ['复杂', '资源消耗大'],
          pricing: '企业订阅',
          recommendation: '需要管理多种制品格式的大型企业'
        }
      ],
      monitoring: [
        {
          name: 'Bundlephobia',
          description: '包大小分析工具',
          pros: ['免费', '直观', '易于使用'],
          cons: ['仅限大小分析', '数据可能不准确'],
          pricing: '免费',
          recommendation: '包大小优化'
        },
        {
          name: 'Libraries.io',
          description: '开源软件监控服务',
          pros: ['多语言支持', '依赖跟踪', '漏洞通知'],
          cons: ['功能有限', '更新不及时'],
          pricing: '免费 + 付费版',
          recommendation: '基础依赖监控'
        },
        {
          name: 'Sonatype Nexus Lifecycle',
          description: '企业级软件供应链管理',
          pros: ['全面覆盖', '策略管理', '深度集成'],
          cons: ['价格昂贵', '复杂'],
          pricing: '企业订阅',
          recommendation: '大型企业全面供应链管理'
        }
      ]
    };
    
    // 根据需求筛选工具
    const recommendations = {};
    
    Object.keys(requirements).forEach(category => {
      if (requirements[category] && tools[category]) {
        recommendations[category] = tools[category].filter(tool => {
          // 简化的筛选逻辑
          return requirements.budget !== 'free' || tool.pricing.includes('免费');
        });
      }
    });
    
    console.log('工具推荐:', recommendations);
    return recommendations;
  },
  
  // 生成工具集成方案
  generateToolIntegrationPlan(selectedTools) {
    console.log('生成工具集成方案...');
    
    const integrationPlan = {
      phases: [
        {
          name: '准备阶段',
          duration: '2周',
          tasks: [
            '评估当前流程',
            '确定集成需求',
            '选择工具',
            '制定实施计划'
          ],
          deliverables: ['需求文档', '工具选择报告', '实施计划']
        },
        {
          name: '基础设施阶段',
          duration: '3周',
          tasks: [
            '部署私有仓库',
            '配置CI/CD管道',
            '设置监控系统',
            '建立访问控制'
          ],
          deliverables: ['私有仓库', 'CI/CD配置', '监控仪表板']
        },
        {
          name: '安全集成阶段',
          duration: '2周',
          tasks: [
            '集成安全扫描工具',
            '配置漏洞通知',
            '建立安全策略',
            '培训团队'
          ],
          deliverables: ['安全扫描流程', '安全策略文档', '培训材料']
        },
        {
          name: '依赖管理阶段',
          duration: '2周',
          tasks: [
            '配置依赖更新工具',
            '建立审批流程',
            '设置版本策略',
            '文档化决策'
          ],
          deliverables: ['依赖更新流程', '审批工作流', '版本策略']
        },
        {
          name: '优化阶段',
          duration: '持续',
          tasks: [
            '监控效果',
            '收集反馈',
            '调整策略',
            '持续改进'
          ],
          deliverables: ['性能报告', '改进建议', '优化方案']
        }
      ],
      resources: {
        team: [
          {
            role: '项目经理',
            responsibility: '整体协调和进度管理'
          },
          {
            role: 'DevOps工程师',
            responsibility: '基础设施和CI/CD'
          },
          {
            role: '安全专家',
            responsibility: '安全策略和工具配置'
          },
          {
            role: '开发团队代表',
            responsibility: '需求反馈和测试'
          }
        ],
        budget: {
          tools: '根据选择的工具确定',
          infrastructure: '根据规模确定',
          personnel: '根据团队规模确定'
        }
      },
      risks: [
        {
          risk: '工具集成复杂性',
          probability: 'medium',
          impact: 'medium',
          mitigation: '分阶段实施，充分测试'
        },
        {
          risk: '团队接受度',
          probability: 'medium',
          impact: 'high',
          mitigation: '充分培训，展示价值'
        },
        {
          risk: '预算超支',
          probability: 'low',
          impact: 'medium',
          mitigation: '明确需求，选择合适工具'
        }
      ]
    };
    
    console.log('工具集成方案:', integrationPlan);
    return integrationPlan;
  }
};

// 示例10: 企业级NPM综合评估工具
const enterpriseNpmAssessment = {
  // 全面评估企业NPM实践
  assessEnterpriseNpmPractices(enterpriseData) {
    console.log('执行企业级NPM实践全面评估...');
    
    const assessment = {
      company: enterpriseData.companyName,
      date: new Date().toISOString(),
      dimensions: {
        strategy: {
          score: 0,
          maxScore: 100,
          details: {}
        },
        governance: {
          score: 0,
          maxScore: 100,
          details: {}
        },
        security: {
          score: 0,
          maxScore: 100,
          details: {}
        },
        operations: {
          score: 0,
          maxScore: 100,
          details: {}
        },
        culture: {
          score: 0,
          maxScore: 100,
          details: {}
        }
      },
      overallScore: 0,
      recommendations: []
    };
    
    // 评估策略维度
    assessment.dimensions.strategy = this.assessStrategy(enterpriseData);
    
    // 评估治理维度
    assessment.dimensions.governance = this.assessGovernance(enterpriseData);
    
    // 评估安全维度
    assessment.dimensions.security = this.assessSecurity(enterpriseData);
    
    // 评估运营维度
    assessment.dimensions.operations = this.assessOperations(enterpriseData);
    
    // 评估文化维度
    assessment.dimensions.culture = this.assessCulture(enterpriseData);
    
    // 计算总分
    const dimensionScores = Object.values(assessment.dimensions).map(dim => dim.score);
    assessment.overallScore = dimensionScores.reduce((sum, score) => sum + score, 0) / dimensionScores.length;
    
    // 生成建议
    assessment.recommendations = this.generateRecommendations(assessment);
    
    console.log('企业NPM实践评估结果:', assessment);
    return assessment;
  },
  
  // 评估策略维度
  assessStrategy(data) {
    const criteria = {
      versionStrategy: {
        weight: 25,
        score: data.hasVersionStrategy ? 100 : 0,
        description: '是否有明确的版本管理策略'
      },
      dependencyPolicy: {
        weight: 25,
        score: data.hasDependencyPolicy ? 100 : 0,
        description: '是否有依赖管理政策'
      },
      toolSelection: {
        weight: 20,
        score: data.hasToolSelectionCriteria ? 100 : 0,
        description: '是否有工具选择标准'
      },
      roadmap: {
        weight: 30,
        score: data.hasRoadmap ? 100 : 0,
        description: '是否有NPM管理路线图'
      }
    };
    
    let totalScore = 0;
    let totalWeight = 0;
    
    Object.keys(criteria).forEach(criterion => {
      const weight = criteria[criterion].weight;
      const score = criteria[criterion].score;
      
      totalScore += (score * weight) / 100;
      totalWeight += weight;
    });
    
    return {
      score: totalScore,
      maxScore: 100,
      details: criteria
    };
  },
  
  // 评估治理维度
  assessGovernance(data) {
    const criteria = {
      approvalProcess: {
        weight: 25,
        score: data.hasApprovalProcess ? 100 : 0,
        description: '是否有依赖审批流程'
      },
      documentation: {
        weight: 20,
        score: data.hasDocumentation ? 100 : 0,
        description: '是否有充分的文档'
      },
      compliance: {
        weight: 25,
        score: data.hasComplianceChecks ? 100 : 0,
        description: '是否有合规性检查'
      },
      reviewFrequency: {
        weight: 30,
        score: data.reviewFrequency ? (data.reviewFrequency === 'monthly' ? 100 : data.reviewFrequency === 'quarterly' ? 70 : 40) : 0,
        description: '依赖审查频率'
      }
    };
    
    let totalScore = 0;
    let totalWeight = 0;
    
    Object.keys(criteria).forEach(criterion => {
      const weight = criteria[criterion].weight;
      const score = criteria[criterion].score;
      
      totalScore += (score * weight) / 100;
      totalWeight += weight;
    });
    
    return {
      score: totalScore,
      maxScore: 100,
      details: criteria
    };
  },
  
  // 评估安全维度
  assessSecurity(data) {
    const criteria = {
      vulnerabilityScanning: {
        weight: 30,
        score: data.hasVulnerabilityScanning ? 100 : 0,
        description: '是否有漏洞扫描'
      },
      licenseCompliance: {
        weight: 25,
        score: data.hasLicenseCompliance ? 100 : 0,
        description: '是否有许可证合规检查'
      },
      privateRegistry: {
        weight: 20,
        score: data.hasPrivateRegistry ? 100 : 0,
        description: '是否使用私有仓库'
      },
      accessControl: {
        weight: 25,
        score: data.hasAccessControl ? 100 : 0,
        description: '是否有访问控制'
      }
    };
    
    let totalScore = 0;
    let totalWeight = 0;
    
    Object.keys(criteria).forEach(criterion => {
      const weight = criteria[criterion].weight;
      const score = criteria[criterion].score;
      
      totalScore += (score * weight) / 100;
      totalWeight += weight;
    });
    
    return {
      score: totalScore,
      maxScore: 100,
      details: criteria
    };
  },
  
  // 评估运营维度
  assessOperations(data) {
    const criteria = {
      automation: {
        weight: 30,
        score: data.automationLevel ? (data.automationLevel === 'high' ? 100 : data.automationLevel === 'medium' ? 70 : 40) : 0,
        description: '自动化程度'
      },
      cicdIntegration: {
        weight: 25,
        score: data.hasCicdIntegration ? 100 : 0,
        description: '是否与CI/CD集成'
      },
      monitoring: {
        weight: 25,
        score: data.hasMonitoring ? 100 : 0,
        description: '是否有监控和告警'
      },
      performanceOptimization: {
        weight: 20,
        score: data.hasPerformanceOptimization ? 100 : 0,
        description: '是否有性能优化措施'
      }
    };
    
    let totalScore = 0;
    let totalWeight = 0;
    
    Object.keys(criteria).forEach(criterion => {
      const weight = criteria[criterion].weight;
      const score = criteria[criterion].score;
      
      totalScore += (score * weight) / 100;
      totalWeight += weight;
    });
    
    return {
      score: totalScore,
      maxScore: 100,
      details: criteria
    };
  },
  
  // 评估文化维度
  assessCulture(data) {
    const criteria = {
      training: {
        weight: 25,
        score: data.hasTraining ? 100 : 0,
        description: '是否有团队培训'
      },
      knowledgeSharing: {
        weight: 25,
        score: data.hasKnowledgeSharing ? 100 : 0,
        description: '是否有知识分享机制'
      },
      communityParticipation: {
        weight: 20,
        score: data.hasCommunityParticipation ? 100 : 0,
        description: '是否参与开源社区'
      },
      continuousImprovement: {
        weight: 30,
        score: data.hasContinuousImprovement ? 100 : 0,
        description: '是否有持续改进机制'
      }
    };
    
    let totalScore = 0;
    let totalWeight = 0;
    
    Object.keys(criteria).forEach(criterion => {
      const weight = criteria[criterion].weight;
      const score = criteria[criterion].score;
      
      totalScore += (score * weight) / 100;
      totalWeight += weight;
    });
    
    return {
      score: totalScore,
      maxScore: 100,
      details: criteria
    };
  },
  
  // 生成改进建议
  generateRecommendations(assessment) {
    const recommendations = [];
    
    // 基于各维度得分生成建议
    Object.keys(assessment.dimensions).forEach(dimension => {
      const dimScore = assessment.dimensions[dimension].score;
      const details = assessment.dimensions[dimension].details;
      
      if (dimScore < 70) {
        // 找出得分最低的几个标准
        const lowScoreCriteria = Object.keys(details)
          .filter(criteria => details[criteria].score < 70)
          .sort((a, b) => details[a].score - details[b].score)
          .slice(0, 2);
        
        lowScoreCriteria.forEach(criteria => {
          recommendations.push({
            dimension,
            criteria,
            description: details[criteria].description,
            priority: dimScore < 50 ? 'high' : 'medium',
            effort: this.estimateEffort(dimension, criteria)
          });
        });
      }
    });
    
    // 添加总体建议
    if (assessment.overallScore < 60) {
      recommendations.push({
        dimension: 'overall',
        criteria: 'comprehensive',
        description: '需要全面改进NPM管理实践',
        priority: 'high',
        effort: 'high'
      });
    } else if (assessment.overallScore >= 80) {
      recommendations.push({
        dimension: 'overall',
        criteria: 'optimization',
        description: '当前实践良好，可考虑进一步优化',
        priority: 'low',
        effort: 'low'
      });
    }
    
    return recommendations;
  },
  
  // 估算改进工作量
  estimateEffort(dimension, criteria) {
    const effortMatrix = {
      strategy: {
        versionStrategy: 'medium',
        dependencyPolicy: 'medium',
        toolSelection: 'low',
        roadmap: 'high'
      },
      governance: {
        approvalProcess: 'medium',
        documentation: 'medium',
        compliance: 'high',
        reviewFrequency: 'low'
      },
      security: {
        vulnerabilityScanning: 'medium',
        licenseCompliance: 'medium',
        privateRegistry: 'high',
        accessControl: 'medium'
      },
      operations: {
        automation: 'high',
        cicdIntegration: 'medium',
        monitoring: 'medium',
        performanceOptimization: 'medium'
      },
      culture: {
        training: 'medium',
        knowledgeSharing: 'low',
        communityParticipation: 'low',
        continuousImprovement: 'medium'
      }
    };
    
    return effortMatrix[dimension] && effortMatrix[dimension][criteria] 
      ? effortMatrix[dimension][criteria] 
      : 'medium';
  }
};

// 导出所有示例
module.exports = {
  privateRegistryManager,
  enterprisePackageStrategy,
  cicdIntegration,
  microserviceNpmManagement,
  largeProjectDependencyManagement,
  enterpriseSecurityStrategy,
  enterpriseBestPractices,
  ecommerceCaseStudy,
  enterpriseNpmToolset,
  enterpriseNpmAssessment
};

// 使用示例
console.log('===== NPM企业级应用与实战示例 =====');

// 示例1: 私有仓库配置
console.log('\n1. 私有仓库配置与管理:');
const registryConfig = privateRegistryManager.configurePrivateRegistry(
  'https://npm.company.com',
  { type: 'token', token: 'abc123xyz' }
);
console.log('配置结果:', registryConfig);

// 示例2: 企业级包管理策略
console.log('\n2. 企业级包管理策略:');
const packageJson = {
  name: 'enterprise-app',
  version: '1.0.0',
  dependencies: {
    express: '^4.17.1',
    lodash: '^4.17.20',
    request: '^2.88.2'
  },
  devDependencies: {
    jest: '^27.0.0',
    eslint: '^7.32.0'
  }
};
const dependencyAnalysis = enterprisePackageStrategy.analyzeDependencies(packageJson);
const dependencyReport = enterprisePackageStrategy.generateDependencyReport(dependencyAnalysis);
console.log('依赖报告:', dependencyReport);

// 示例3: CI/CD集成
console.log('\n3. CI/CD集成:');
const githubConfig = cicdIntegration.generateCIConfig('github', {
  nodeVersion: '16',
  registryUrl: 'https://npm.company.com',
  publish: true
});
console.log('GitHub Actions配置已生成');

// 示例4: 微服务架构中的NPM管理
console.log('\n4. 微服务架构中的NPM管理:');
const microservices = [
  {
    name: 'user-service',
    dependencies: {
      express: '^4.17.1',
      mongoose: '^5.12.0',
      jsonwebtoken: '^8.5.1',
      bcrypt: '^5.0.1'
    }
  },
  {
    name: 'product-service',
    dependencies: {
      express: '^4.17.1',
      mongoose: '^5.12.0',
      axios: '^0.21.1'
    }
  },
  {
    name: 'order-service',
    dependencies: {
      express: '^4.18.0',
      mongoose: '^5.13.0',
      axios: '^0.21.1',
      jsonwebtoken: '^8.5.1'
    }
  }
];
const microserviceAnalysis = microserviceNpmManagement.analyzeMicroserviceDependencies(microservices);
const sharedLibraryRecommendations = microserviceNpmManagement.generateSharedLibraryRecommendations(microserviceAnalysis);
console.log('共享库建议:', sharedLibraryRecommendations);

// 示例5: 大型项目依赖管理
console.log('\n5. 大型项目依赖管理:');
const packageLockAnalysis = largeProjectDependencyManagement.analyzeDependencyGraph({});
const optimizations = largeProjectDependencyManagement.optimizeDependencies(packageLockAnalysis, {
  optimizeSize: true,
  checkLicenses: true
});
const strategy = largeProjectDependencyManagement.generateDependencyManagementStrategy(packageLockAnalysis, optimizations);
console.log('依赖管理策略已生成');

// 示例6: 企业级安全策略
console.log('\n6. 企业级安全策略:');
const securityConfig = enterpriseSecurityStrategy.generateSecurityConfig({
  allowedLicenses: ['MIT', 'Apache-2.0', 'BSD-3-Clause'],
  vulnerabilitySeverity: 'moderate'
});
const securityAudit = enterpriseSecurityStrategy.performSecurityAudit({
  name: 'example-package',
  version: '1.0.0'
});
const securityReport = enterpriseSecurityStrategy.generateSecurityReport(securityAudit);
console.log('安全报告:', securityReport);

// 示例7: 企业级最佳实践
console.log('\n7. 企业级最佳实践:');
const bestPracticesGuide = enterpriseBestPractices.generateBestPracticesGuide();
const currentPractices = {
  versionControl: true,
  securityScanning: true,
  dependencyReview: true,
  privateRegistry: true,
  licenseCompliance: true,
  automatedUpdates: false,
  documentation: true,
  monitoring: true,
  ciIntegration: true,
  teamTraining: false
};
const maturityAssessment = enterpriseBestPractices.assessPracticeMaturity(currentPractices);
console.log('实践成熟度评估:', maturityAssessment);

// 示例8: 实战案例
console.log('\n8. 实战案例 - 大型电商平台NPM管理:');
console.log('项目背景:', ecommerceCaseStudy.projectBackground);
console.log('解决方案:', ecommerceCaseStudy.solutions);
console.log('实施效果:', ecommerceCaseStudy.results);
console.log('经验总结:', ecommerceCaseStudy.lessonsLearned);

// 示例9: 企业级NPM工具集
console.log('\n9. 企业级NPM工具集:');
const toolRequirements = {
  security: true,
  dependencyManagement: true,
  privateRegistry: true,
  monitoring: true,
  budget: 'enterprise'
};
const toolRecommendations = enterpriseNpmToolset.generateToolRecommendations(toolRequirements);
const integrationPlan = enterpriseNpmToolset.generateToolIntegrationPlan({
  security: ['Snyk'],
  dependencyManagement: ['Renovate'],
  privateRegistry: ['Verdaccio'],
  monitoring: ['Libraries.io']
});
console.log('工具集成方案已生成');

// 示例10: 企业级NPM综合评估
console.log('\n10. 企业级NPM综合评估:');
const enterpriseData = {
  companyName: '示例公司',
  hasVersionStrategy: true,
  hasDependencyPolicy: false,
  hasToolSelectionCriteria: true,
  hasRoadmap: false,
  hasApprovalProcess: true,
  hasDocumentation: true,
  hasComplianceChecks: true,
  reviewFrequency: 'monthly',
  hasVulnerabilityScanning: true,
  hasLicenseCompliance: true,
  hasPrivateRegistry: true,
  hasAccessControl: true,
  automationLevel: 'medium',
  hasCicdIntegration: true,
  hasMonitoring: true,
  hasPerformanceOptimization: false,
  hasTraining: false,
  hasKnowledgeSharing: true,
  hasCommunityParticipation: false,
  hasContinuousImprovement: true
};
const enterpriseAssessment = enterpriseNpmAssessment.assessEnterpriseNpmPractices(enterpriseData);
console.log('企业NPM实践评估结果:', enterpriseAssessment);

console.log('\n===== 示例执行完成 =====');