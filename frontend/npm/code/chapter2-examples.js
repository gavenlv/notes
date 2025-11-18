// 第2章：NPM包管理与基本命令 - 代码示例

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log("=== 第2章：NPM包管理与基本命令 - 代码示例 ===\n");

// 示例1：模拟包安装过程
console.log("=== 示例1：模拟包安装过程 ===");

function simulatePackageInstall(packageName, version, type = 'dependencies') {
  console.log(`正在安装 ${packageName}@${version}...`);
  
  // 模拟安装过程
  setTimeout(() => {
    console.log(`+ ${packageName}@${version}`);
    console.log(`added ${version} in ${Math.floor(Math.random() * 5) + 1}s`);
    
    // 模拟更新package.json
    const packageJsonPath = path.join(__dirname, 'package.json');
    if (fs.existsSync(packageJsonPath)) {
      const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
      
      if (!packageJson[type]) {
        packageJson[type] = {};
      }
      
      packageJson[type][packageName] = version;
      
      fs.writeFileSync(packageJsonPath, JSON.stringify(packageJson, null, 2));
      console.log(`已更新 ${type} 中的 ${packageName}`);
    }
  }, 1000);
}

// 模拟安装lodash
simulatePackageInstall('lodash', '^4.17.21');

// 模拟安装jest作为开发依赖
setTimeout(() => {
  simulatePackageInstall('jest', '^29.6.1', 'devDependencies');
}, 2000);

// 示例2：模拟包卸载过程
console.log("\n=== 示例2：模拟包卸载过程 ===");

function simulatePackageUninstall(packageName, type = 'dependencies') {
  console.log(`正在卸载 ${packageName}...`);
  
  // 模拟卸载过程
  setTimeout(() => {
    console.log(`removed ${packageName} in ${Math.floor(Math.random() * 3) + 1}s`);
    
    // 模拟更新package.json
    const packageJsonPath = path.join(__dirname, 'package.json');
    if (fs.existsSync(packageJsonPath)) {
      const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
      
      if (packageJson[type] && packageJson[type][packageName]) {
        delete packageJson[type][packageName];
        
        fs.writeFileSync(packageJsonPath, JSON.stringify(packageJson, null, 2));
        console.log(`已从 ${type} 中移除 ${packageName}`);
      }
    }
  }, 1000);
}

// 模拟卸载express
setTimeout(() => {
  simulatePackageUninstall('express');
}, 3000);

// 示例3：版本范围解析
console.log("\n=== 示例3：版本范围解析 ===");

function parseVersionRange(range) {
  const versionRanges = {
    '*': '任何版本',
    '1.x': '1.x.x的最新版本',
    '1.2.x': '1.2.x的最新版本',
    '~1.2.3': '>=1.2.3且<1.3.0',
    '^1.2.3': '>=1.2.3且<2.0.0',
    '>=1.2.3': '>=1.2.3',
    '<=1.2.3': '<=1.2.3',
    '>1.2.3': '>1.2.3',
    '<1.2.3': '<1.2.3',
    '1.2.3 - 2.3.4': '>=1.2.3且<=2.3.4',
    '1.2.3 || 2.3.4': '1.2.3或2.3.4'
  };
  
  return versionRanges[range] || '未知版本范围';
}

const versionRanges = ['*', '1.x', '1.2.x', '~1.2.3', '^1.2.3', '>=1.2.3', '1.2.3 - 2.3.4', '1.2.3 || 2.3.4'];

versionRanges.forEach(range => {
  console.log(`${range} => ${parseVersionRange(range)}`);
});

// 示例4：模拟包信息查看
console.log("\n=== 示例4：模拟包信息查看 ===");

function getPackageInfo(packageName) {
  const mockPackages = {
    lodash: {
      name: 'lodash',
      version: '4.17.21',
      description: 'Lodash modular utilities.',
      author: 'John-David Dalton <john.david.dalton@gmail.com>',
      homepage: 'https://lodash.com/',
      repository: {
        type: 'git',
        url: 'git+https://github.com/lodash/lodash.git'
      },
      keywords: ['modules', 'utilities', 'functional'],
      license: 'MIT',
      dependencies: {},
      devDependencies: {
        'benchmark': '^2.1.4',
        'coveralls': '^3.0.0',
        'docdown': '^0.7.2'
      }
    },
    express: {
      name: 'express',
      version: '4.18.2',
      description: 'Fast, unopinionated, minimalist web framework',
      author: 'TJ Holowaychuk <tj@vision-media.ca>',
      homepage: 'http://expressjs.com/',
      repository: {
        type: 'git',
        url: 'git+https://github.com/expressjs/express.git'
      },
      keywords: ['express', 'framework', 'web', 'http', 'rest', 'restful', 'api'],
      license: 'MIT',
      dependencies: {
        'accepts': '~1.3.8',
        'array-flatten': '1.1.1',
        'body-parser': '1.20.1'
      },
      devDependencies: {
        'after': '0.8.2',
        'connect-redis': '3.4.2'
      }
    }
  };
  
  return mockPackages[packageName] || null;
}

const packagesToCheck = ['lodash', 'express', 'nonexistent-package'];

packagesToCheck.forEach(pkg => {
  const info = getPackageInfo(pkg);
  if (info) {
    console.log(`\n包名: ${info.name}`);
    console.log(`版本: ${info.version}`);
    console.log(`描述: ${info.description}`);
    console.log(`作者: ${info.author}`);
    console.log(`主页: ${info.homepage}`);
    console.log(`关键词: ${info.keywords.join(', ')}`);
    console.log(`许可证: ${info.license}`);
    console.log(`依赖数量: ${Object.keys(info.dependencies).length}`);
    console.log(`开发依赖数量: ${Object.keys(info.devDependencies).length}`);
  } else {
    console.log(`\n包 ${pkg} 不存在`);
  }
});

// 示例5：模拟依赖树
console.log("\n=== 示例5：模拟依赖树 ===");

function generateDependencyTree(packageName, depth = 0) {
  const mockDependencies = {
    'my-project': {
      'lodash': '^4.17.21',
      'express': '^4.18.2',
      'moment': '^2.29.4'
    },
    'express': {
      'accepts': '~1.3.8',
      'array-flatten': '1.1.1',
      'body-parser': '1.20.1',
      'content-disposition': '0.5.4'
    },
    'body-parser': {
      'bytes': '3.1.2',
      'content-type': '~1.0.4',
      'debug': '2.6.9'
    }
  };
  
  const indent = '  '.repeat(depth);
  const deps = mockDependencies[packageName];
  
  if (!deps || depth > 2) return;
  
  Object.entries(deps).forEach(([name, version]) => {
    console.log(`${indent}├─ ${name}@${version}`);
    generateDependencyTree(name, depth + 1);
  });
}

console.log("my-project@1.0.0");
generateDependencyTree('my-project');

// 示例6：模拟包更新检查
console.log("\n=== 示例6：模拟包更新检查 ===");

function checkOutdatedPackages() {
  const currentPackages = {
    'lodash': '4.16.0',
    'express': '4.16.0',
    'moment': '2.24.0'
  };
  
  const latestPackages = {
    'lodash': '4.17.21',
    'express': '4.18.2',
    'moment': '2.29.4'
  };
  
  console.log("Package\t\tCurrent\tWanted\tLatest");
  console.log("-------\t\t-------\t------\t------");
  
  Object.entries(currentPackages).forEach(([name, current]) => {
    const latest = latestPackages[name];
    const wanted = `${current.split('.').slice(0, 2).join('.')}.x`;
    
    if (current !== latest) {
      console.log(`${name}\t\t${current}\t${wanted}\t${latest}`);
    }
  });
}

checkOutdatedPackages();

// 示例7：模拟NPM脚本执行
console.log("\n=== 示例7：模拟NPM脚本执行 ===");

function runNpmScript(scriptName) {
  const scripts = {
    'start': '启动应用程序',
    'dev': '启动开发服务器',
    'build': '构建生产版本',
    'test': '运行测试',
    'lint': '代码检查',
    'format': '代码格式化'
  };
  
  const action = scripts[scriptName];
  
  if (action) {
    console.log(`> npm run ${scriptName}`);
    
    // 模拟执行过程
    const startTime = Date.now();
    setTimeout(() => {
      const duration = (Date.now() - startTime) / 1000;
      console.log(`${action}完成，耗时 ${duration.toFixed(2)} 秒`);
    }, 1000);
  } else {
    console.log(`错误: 脚本 "${scriptName}" 不存在`);
  }
}

['start', 'dev', 'build', 'test', 'lint', 'format', 'unknown'].forEach(script => {
  runNpmScript(script);
});

// 示例8：模拟全局包管理
console.log("\n=== 示例8：模拟全局包管理 ===");

const globalPackages = [
  { name: 'npm', version: '8.19.2', location: '/usr/local/bin/npm' },
  { name: 'node', version: '18.12.1', location: '/usr/local/bin/node' },
  { name: 'yarn', version: '1.22.19', location: '/usr/local/bin/yarn' },
  { name: 'create-react-app', version: '5.0.1', location: '/usr/local/bin/create-react-app' },
  { name: 'typescript', version: '4.9.4', location: '/usr/local/bin/tsc' }
];

console.log("全局安装的包:");
globalPackages.forEach(pkg => {
  console.log(`${pkg.name}@${pkg.version} - ${pkg.location}`);
});

// 示例9：模拟NPM配置
console.log("\n=== 示例9：模拟NPM配置 ===");

const npmConfig = {
  registry: 'https://registry.npmjs.org/',
  prefix: '/usr/local',
  cache: '/Users/user/.npm',
  'init-author-name': 'Your Name',
  'init-author-email': 'your.email@example.com',
  'init-license': 'MIT',
  'init-version': '1.0.0',
  'save-exact': false,
  'package-lock': true
};

console.log("NPM配置:");
Object.entries(npmConfig).forEach(([key, value]) => {
  console.log(`${key} = ${value}`);
});

// 示例10：模拟包搜索
console.log("\n=== 示例10：模拟包搜索 ===");

function searchPackages(keyword) {
  const allPackages = [
    { name: 'lodash', description: 'Lodash modular utilities.', keywords: ['util', 'functional'] },
    { name: 'moment', description: 'Parse, validate, manipulate, and display dates.', keywords: ['date', 'time'] },
    { name: 'express', description: 'Fast, unopinionated, minimalist web framework.', keywords: ['web', 'framework'] },
    { name: 'react', description: 'React is a JavaScript library for building user interfaces.', keywords: ['ui', 'jsx'] },
    { name: 'axios', description: 'Promise based HTTP client for the browser and node.js.', keywords: ['http', 'ajax'] }
  ];
  
  const results = allPackages.filter(pkg => 
    pkg.name.includes(keyword) || 
    pkg.description.includes(keyword) || 
    pkg.keywords.some(k => k.includes(keyword))
  );
  
  return results;
}

const searchKeywords = ['util', 'date', 'http'];

searchKeywords.forEach(keyword => {
  const results = searchPackages(keyword);
  console.log(`\n搜索 "${keyword}" 的结果:`);
  
  results.forEach(pkg => {
    console.log(`${pkg.name} - ${pkg.description}`);
    console.log(`  关键词: ${pkg.keywords.join(', ')}`);
  });
});

console.log("\n=== 第2章示例代码结束 ===");