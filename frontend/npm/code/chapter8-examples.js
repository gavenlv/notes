// NPM生态系统与工具代码示例

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 示例1：包管理器比较分析
function comparePackageManagers() {
  const managers = {
    npm: {
      installCommand: 'npm install',
      addCommand: 'npm add',
      lockFile: 'package-lock.json',
      features: ['默认安装', '最大兼容性', '简单易用'],
      performance: '中等',
      diskUsage: '高'
    },
    yarn: {
      installCommand: 'yarn install',
      addCommand: 'yarn add',
      lockFile: 'yarn.lock',
      features: ['并行下载', '确定性安装', '离线模式'],
      performance: '快',
      diskUsage: '中等'
    },
    pnpm: {
      installCommand: 'pnpm install',
      addCommand: 'pnpm add',
      lockFile: 'pnpm-lock.yaml',
      features: ['硬链接共享', '严格依赖管理', '节省磁盘空间'],
      performance: '最快',
      diskUsage: '低'
    }
  };
  
  return managers;
}

// 示例2：镜像源管理
function manageRegistryMirrors() {
  const mirrors = {
    npm: {
      name: 'NPM官方',
      url: 'https://registry.npmjs.org/',
      location: '全球'
    },
    taobao: {
      name: '淘宝镜像',
      url: 'https://registry.npmmirror.com/',
      location: '中国'
    },
    cnpm: {
      name: 'CNPM',
      url: 'https://r.cnpmjs.org/',
      location: '中国'
    },
    yarn: {
      name: 'Yarn官方',
      url: 'https://registry.yarnpkg.com/',
      location: '全球'
    }
  };
  
  // 模拟测试镜像速度
  const testMirrorSpeed = (mirrorUrl) => {
    // 模拟网络延迟（毫秒）
    const baseDelay = mirrorUrl.includes('cnpm') ? 50 : 
                    mirrorUrl.includes('taobao') ? 80 : 
                    mirrorUrl.includes('npmjs') ? 150 : 120;
    
    // 添加随机波动
    const variation = Math.random() * 40 - 20;
    return Math.max(10, baseDelay + variation);
  };
  
  // 为每个镜像添加速度测试结果
  Object.keys(mirrors).forEach(key => {
    const mirror = mirrors[key];
    mirror.speed = testMirrorSpeed(mirror.url);
    mirror.status = mirror.speed < 100 ? '快速' : mirror.speed < 150 ? '正常' : '较慢';
  });
  
  return mirrors;
}

// 示例3：包信息获取
async function getPackageInfo(packageName) {
  // 模拟从NPM API获取包信息
  const mockPackageData = {
    name: packageName,
    version: '1.0.0',
    description: `这是一个模拟的${packageName}包`,
    author: '示例作者',
    license: 'MIT',
    homepage: `https://github.com/example/${packageName}`,
    repository: {
      type: 'git',
      url: `https://github.com/example/${packageName}.git`
    },
    keywords: ['npm', 'package', 'example'],
    dependencies: {
      'lodash': '^4.17.21',
      'express': '^4.18.0'
    },
    devDependencies: {
      'jest': '^27.0.0',
      'eslint': '^8.0.0'
    },
    downloads: {
      lastDay: Math.floor(Math.random() * 10000),
      lastWeek: Math.floor(Math.random() * 50000),
      lastMonth: Math.floor(Math.random() * 200000)
    },
    publishedAt: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString()
  };
  
  return mockPackageData;
}

// 示例4：依赖分析工具
function analyzeDependencies(packageJson) {
  const analysis = {
    total: 0,
    direct: 0,
    indirect: 0,
    dev: 0,
    peer: 0,
    optional: 0,
    categories: {},
    outdated: [],
    vulnerabilities: []
  };
  
  // 分析直接依赖
  if (packageJson.dependencies) {
    analysis.direct += Object.keys(packageJson.dependencies).length;
    analysis.categories.production = Object.keys(packageJson.dependencies);
  }
  
  // 分析开发依赖
  if (packageJson.devDependencies) {
    analysis.dev += Object.keys(packageJson.devDependencies).length;
    analysis.categories.development = Object.keys(packageJson.devDependencies);
  }
  
  // 分析对等依赖
  if (packageJson.peerDependencies) {
    analysis.peer += Object.keys(packageJson.peerDependencies).length;
    analysis.categories.peer = Object.keys(packageJson.peerDependencies);
  }
  
  // 分析可选依赖
  if (packageJson.optionalDependencies) {
    analysis.optional += Object.keys(packageJson.optionalDependencies).length;
    analysis.categories.optional = Object.keys(packageJson.optionalDependencies);
  }
  
  // 计算总依赖数
  analysis.total = analysis.direct + analysis.dev + analysis.peer + analysis.optional;
  
  // 模拟间接依赖（每个直接依赖平均有3-10个间接依赖）
  analysis.indirect = analysis.direct * (Math.floor(Math.random() * 8) + 3);
  
  // 模拟过时依赖检查
  const checkOutdated = (depName, version) => {
    if (Math.random() > 0.7) { // 30%概率有过时版本
      const currentVersion = version.replace(/^[\^~]/, '');
      const parts = currentVersion.split('.');
      const patchVersion = parseInt(parts[2]) + 1;
      const latestVersion = `${parts[0]}.${parts[1]}.${patchVersion}`;
      
      return {
        name: depName,
        current: version,
        latest: `^${latestVersion}`,
        type: 'patch'
      };
    }
    return null;
  };
  
  // 检查所有依赖是否过时
  if (packageJson.dependencies) {
    for (const [name, version] of Object.entries(packageJson.dependencies)) {
      const outdated = checkOutdated(name, version);
      if (outdated) analysis.outdated.push(outdated);
    }
  }
  
  // 模拟安全漏洞检查
  const checkVulnerability = (depName, version) => {
    if (Math.random() > 0.8) { // 20%概率有漏洞
      const severities = ['low', 'moderate', 'high', 'critical'];
      return {
        name: depName,
        version,
        severity: severities[Math.floor(Math.random() * severities.length)],
        title: '模拟安全漏洞',
        patchedIn: '>=1.0.1'
      };
    }
    return null;
  };
  
  // 检查所有依赖的安全漏洞
  if (packageJson.dependencies) {
    for (const [name, version] of Object.entries(packageJson.dependencies)) {
      const vulnerability = checkVulnerability(name, version);
      if (vulnerability) analysis.vulnerabilities.push(vulnerability);
    }
  }
  
  return analysis;
}

// 示例5：私有仓库配置
function configurePrivateRegistry() {
  const registries = {
    verdaccio: {
      name: 'Verdaccio',
      type: '轻量级',
      url: 'http://localhost:4873',
      config: `
# Verdaccio配置
registry=http://localhost:4873/
//localhost:4873/:_authToken=\${VERDACCIO_TOKEN}

# 作用域包配置
@mycompany:registry=http://localhost:4873/
`
    },
    nexus: {
      name: 'Sonatype Nexus',
      type: '企业级',
      url: 'https://nexus.mycompany.com/repository/npm-public/',
      config: `
# Nexus配置
registry=https://nexus.mycompany.com/repository/npm-public/
//nexus.mycompany.com/repository/npm-public/:_authToken=\${NEXUS_TOKEN}

# 作用域包配置
@mycompany:registry=https://nexus.mycompany.com/repository/npm-private/
`
    },
    gitlab: {
      name: 'GitLab Package Registry',
      type: '集成式',
      url: 'https://gitlab.com/api/v4/packages/npm/',
      config: `
# GitLab配置
registry=https://gitlab.com/api/v4/packages/npm/
//gitlab.com/api/v4/packages/npm/:_authToken=\${GITLAB_TOKEN}

# 作用域包配置
@mygroup:registry=https://gitlab.com/api/v4/projects/\${PROJECT_ID}/packages/npm/
`
    },
    artifactory: {
      name: 'JFrog Artifactory',
      type: '企业级',
      url: 'https://mycompany.jfrog.io/artifactory/api/npm/npm-virtual/',
      config: `
# Artifactory配置
registry=https://mycompany.jfrog.io/artifactory/api/npm/npm-virtual/
//mycompany.jfrog.io/artifactory/api/npm/npm-virtual/:_authToken=\${ARTIFACTORY_TOKEN}

# 作用域包配置
@mycompany:registry=https://mycompany.jfrog.io/artifactory/api/npm/npm-local/
`
    }
  };
  
  return registries;
}

// 示例6：NPM API使用
async function useNpmApi() {
  // 模拟NPM API调用
  
  // 获取包信息
  const getPackage = async (packageName) => {
    // 模拟API延迟
    await new Promise(resolve => setTimeout(resolve, 100));
    
    return {
      name: packageName,
      version: '1.0.0',
      description: `模拟的${packageName}包信息`,
      author: '模拟作者',
      license: 'MIT'
    };
  };
  
  // 搜索包
  const searchPackages = async (query, limit = 10) => {
    // 模拟API延迟
    await new Promise(resolve => setTimeout(resolve, 200));
    
    const results = [];
    for (let i = 0; i < limit; i++) {
      results.push({
        name: `${query}-package-${i}`,
        version: '1.0.0',
        description: `与${query}相关的包${i}`,
        author: `作者${i}`,
        date: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString()
      });
    }
    
    return {
      objects: results,
      total: results.length
    };
  };
  
  // 获取下载统计
  const getDownloads = async (packageName, period = 'last-week') => {
    // 模拟API延迟
    await new Promise(resolve => setTimeout(resolve, 150));
    
    const days = period === 'last-day' ? 1 : 
                 period === 'last-week' ? 7 : 
                 period === 'last-month' ? 30 : 7;
    
    const downloads = [];
    const today = new Date();
    
    for (let i = days - 1; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      
      downloads.push({
        day: date.toISOString().split('T')[0],
        downloads: Math.floor(Math.random() * 1000) + 100
      });
    }
    
    return {
      package: packageName,
      downloads
    };
  };
  
  return {
    getPackage,
    searchPackages,
    getDownloads
  };
}

// 示例7：包发布流程
function createPublishWorkflow() {
  const workflow = {
    name: 'Package Publish Workflow',
    on: {
      push: {
        branches: ['main']
      }
    },
    jobs: {
      test: {
        'runs-on': 'ubuntu-latest',
        steps: [
          {
            name: 'Checkout',
            uses: 'actions/checkout@v3'
          },
          {
            name: 'Setup Node.js',
            uses: 'actions/setup-node@v3',
            with: {
              'node-version': '18',
              'cache': 'npm'
            }
          },
          {
            name: 'Install dependencies',
            run: 'npm ci'
          },
          {
            name: 'Run tests',
            run: 'npm test'
          },
          {
            name: 'Run linting',
            run: 'npm run lint'
          }
        ]
      },
      publish: {
        'runs-on': 'ubuntu-latest',
        needs: 'test',
        if: "startsWith(github.ref, 'refs/tags/')",
        steps: [
          {
            name: 'Checkout',
            uses: 'actions/checkout@v3'
          },
          {
            name: 'Setup Node.js',
            uses: 'actions/setup-node@v3',
            with: {
              'node-version': '18',
              'cache': 'npm',
              'registry-url': 'https://registry.npmjs.org/'
            }
          },
          {
            name: 'Install dependencies',
            run: 'npm ci'
          },
          {
            name: 'Build package',
            run: 'npm run build'
          },
          {
            name: 'Publish to NPM',
            run: 'npm publish',
            env: {
              NODE_AUTH_TOKEN: '${{ secrets.NPM_TOKEN }}'
            }
          }
        ]
      }
    }
  };
  
  return workflow;
}

// 示例8：NPM插件开发
function createNpmPlugin() {
  const pluginCode = `
#!/usr/bin/env node

const { program } = require('commander');
const chalk = require('chalk');
const inquirer = require('inquirer');

program
  .name('npm-plugin-example')
  .description('示例NPM插件')
  .version('1.0.0');

program
  .command('analyze')
  .description('分析项目依赖')
  .option('-d, --depth <number>', '分析深度', '3')
  .action(async (options) => {
    console.log(chalk.blue('分析项目依赖...'));
    
    // 模拟分析过程
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    console.log(chalk.green('依赖分析完成'));
    console.log('直接依赖: 15');
    console.log('间接依赖: 127');
    console.log('开发依赖: 23');
  });

program
  .command('optimize')
  .description('优化项目配置')
  .action(async () => {
    console.log(chalk.blue('优化项目配置...'));
    
    const answers = await inquirer.prompt([
      {
        type: 'checkbox',
        name: 'optimizations',
        message: '选择要应用的优化',
        choices: [
          { name: '移除未使用的依赖', value: 'remove-unused' },
          { name: '更新过时的依赖', value: 'update-outdated' },
          { name: '优化构建配置', value: 'optimize-build' },
          { name: '添加安全检查', value: 'add-security' }
        ]
      }
    ]);
    
    console.log(chalk.green('将应用以下优化:'));
    answers.optimizations.forEach(opt => {
      console.log(\`- \${opt}\`);
    });
  });

program.parse();
`;
  
  const packageJson = {
    name: 'npm-plugin-example',
    version: '1.0.0',
    description: '示例NPM插件',
    main: 'index.js',
    bin: {
      'npm-plugin-example': './index.js'
    },
    scripts: {
      test: 'echo "Error: no test specified" && exit 1'
    },
    keywords: ['npm', 'plugin', 'cli'],
    author: '示例作者',
    license: 'MIT',
    dependencies: {
      'commander': '^9.0.0',
      'chalk': '^5.0.0',
      'inquirer': '^9.0.0'
    }
  };
  
  return {
    pluginCode,
    packageJson
  };
}

// 示例9：包质量评估
function assessPackageQuality(packageInfo) {
  const criteria = {
    name: {
      weight: 10,
      score: 0,
      description: '包名是否清晰、唯一'
    },
    description: {
      weight: 15,
      score: 0,
      description: '是否有清晰的描述'
    },
    readme: {
      weight: 20,
      score: 0,
      description: '是否有完整的README文档'
    },
    license: {
      weight: 10,
      score: 0,
      description: '是否有明确的许可证'
    },
    tests: {
      weight: 20,
      score: 0,
      description: '是否有足够的测试'
    },
    downloads: {
      weight: 10,
      score: 0,
      description: '下载量是否足够'
    },
    maintenance: {
      weight: 15,
      score: 0,
      description: '是否积极维护'
    }
  };
  
  // 评估各项标准
  criteria.name.score = packageInfo.name && packageInfo.name.length > 3 ? 10 : 5;
  criteria.description.score = packageInfo.description && packageInfo.description.length > 20 ? 15 : 5;
  criteria.readme.score = Math.random() > 0.3 ? 20 : 0; // 70%概率有README
  criteria.license.score = packageInfo.license ? 10 : 0;
  criteria.tests.score = Math.random() > 0.4 ? 20 : 10; // 60%概率有测试
  criteria.downloads.score = packageInfo.downloads && packageInfo.downloads.lastMonth > 1000 ? 10 : 5;
  criteria.maintenance.score = Math.random() > 0.3 ? 15 : 5; // 70%概率积极维护
  
  // 计算总分
  let totalScore = 0;
  let totalWeight = 0;
  
  Object.values(criteria).forEach(criterion => {
    totalScore += criterion.score * criterion.weight;
    totalWeight += criterion.weight;
  });
  
  const overallScore = Math.round(totalScore / totalWeight);
  
  // 确定评级
  let grade;
  if (overallScore >= 90) grade = 'A';
  else if (overallScore >= 80) grade = 'B';
  else if (overallScore >= 70) grade = 'C';
  else if (overallScore >= 60) grade = 'D';
  else grade = 'F';
  
  return {
    criteria,
    overallScore,
    grade,
    recommendation: overallScore >= 70 ? '推荐使用' : '需要改进'
  };
}

// 示例10：生态系统趋势分析
function analyzeEcosystemTrends() {
  const trends = {
    packageManagers: {
      npm: {
        current: 65,
        previous: 70,
        change: -5,
        description: 'NPM市场份额略有下降'
      },
      yarn: {
        current: 20,
        previous: 18,
        change: 2,
        description: 'Yarn使用率小幅增长'
      },
      pnpm: {
        current: 15,
        previous: 12,
        change: 3,
        description: 'pnpm增长迅速，受性能优势驱动'
      }
    },
    packageTypes: {
      frameworks: {
        current: 25,
        description: '前端框架包占比'
      },
      utilities: {
        current: 30,
        description: '工具库包占比'
      },
      devtools: {
        current: 20,
        description: '开发工具包占比'
      },
      others: {
        current: 25,
        description: '其他类型包占比'
      }
    },
    security: {
      vulnerabilities: {
        current: 1200,
        previous: 1500,
        change: -300,
        description: '漏洞数量减少，安全性提升'
      },
      audits: {
        current: 5000000,
        previous: 3000000,
        change: 2000000,
        description: '安全审计次数大幅增加'
      }
    },
    performance: {
      installTime: {
        npm: 45,
        yarn: 30,
        pnpm: 20,
        unit: '秒',
        description: '平均安装时间'
      },
      diskUsage: {
        npm: 850,
        yarn: 650,
        pnpm: 350,
        unit: 'MB',
        description: '平均磁盘使用量'
      }
    }
  };
  
  return trends;
}

// 导出所有示例函数
module.exports = {
  comparePackageManagers,
  manageRegistryMirrors,
  getPackageInfo,
  analyzeDependencies,
  configurePrivateRegistry,
  useNpmApi,
  createPublishWorkflow,
  createNpmPlugin,
  assessPackageQuality,
  analyzeEcosystemTrends
};

// 示例使用
if (require.main === module) {
  // 比较包管理器
  const managers = comparePackageManagers();
  console.log("包管理器比较:", managers);
  
  // 管理镜像源
  const mirrors = manageRegistryMirrors();
  console.log("\n镜像源管理:", mirrors);
  
  // 获取包信息
  getPackageInfo("express").then(info => {
    console.log("\n包信息:", info);
    
    // 分析依赖
    const packageJson = {
      dependencies: {
        "express": "^4.18.0",
        "lodash": "^4.17.21"
      },
      devDependencies: {
        "jest": "^27.0.0",
        "eslint": "^8.0.0"
      }
    };
    
    const analysis = analyzeDependencies(packageJson);
    console.log("\n依赖分析:", analysis);
    
    // 评估包质量
    const quality = assessPackageQuality(info);
    console.log("\n包质量评估:", quality);
  });
  
  // 分析生态系统趋势
  const trends = analyzeEcosystemTrends();
  console.log("\n生态系统趋势:", trends);
}