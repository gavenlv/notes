#!/usr/bin/env node

// 安装验证脚本
// 用于验证项目依赖是否正确安装

const fs = require('fs');
const path = require('path');

// ANSI颜色代码
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

// 颜色输出函数
function colorLog(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

// 检查文件是否存在
function checkFile(filePath, description) {
  if (fs.existsSync(filePath)) {
    colorLog(`✓ ${description} 存在`, 'green');
    return true;
  } else {
    colorLog(`✗ ${description} 不存在`, 'red');
    return false;
  }
}

// 检查依赖是否安装
function checkDependency(dependencyName) {
  try {
    const dependency = require(dependencyName);
    colorLog(`✓ 依赖 ${dependencyName} 已安装`, 'green');
    return true;
  } catch (error) {
    colorLog(`✗ 依赖 ${dependencyName} 未安装或无法加载`, 'red');
    return false;
  }
}

// 检查package.json
function checkPackageJson() {
  colorLog('\n=== 检查 package.json ===', 'cyan');
  
  const packageJsonPath = path.join(process.cwd(), 'package.json');
  if (checkFile(packageJsonPath, 'package.json')) {
    try {
      const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
      
      colorLog(`✓ 项目名称: ${packageJson.name}`, 'green');
      colorLog(`✓ 项目版本: ${packageJson.version}`, 'green');
      
      if (packageJson.dependencies) {
        const depCount = Object.keys(packageJson.dependencies).length;
        colorLog(`✓ 生产依赖数量: ${depCount}`, 'green');
        
        colorLog('  生产依赖列表:', 'blue');
        Object.keys(packageJson.dependencies).forEach(dep => {
          console.log(`    - ${dep}@${packageJson.dependencies[dep]}`);
        });
      }
      
      if (packageJson.devDependencies) {
        const devDepCount = Object.keys(packageJson.devDependencies).length;
        colorLog(`✓ 开发依赖数量: ${devDepCount}`, 'green');
        
        colorLog('  开发依赖列表:', 'blue');
        Object.keys(packageJson.devDependencies).forEach(dep => {
          console.log(`    - ${dep}@${packageJson.devDependencies[dep]}`);
        });
      }
      
      return true;
    } catch (error) {
      colorLog(`✗ 解析package.json失败: ${error.message}`, 'red');
      return false;
    }
  }
  
  return false;
}

// 检查yarn.lock
function checkYarnLock() {
  colorLog('\n=== 检查 yarn.lock ===', 'cyan');
  
  const yarnLockPath = path.join(process.cwd(), 'yarn.lock');
  if (checkFile(yarnLockPath, 'yarn.lock')) {
    try {
      const yarnLockContent = fs.readFileSync(yarnLockPath, 'utf8');
      const lines = yarnLockContent.split('\n').length;
      colorLog(`✓ yarn.lock 文件大小: ${lines} 行`, 'green');
      
      // 统计锁定的包数量
      const lockEntries = yarnLockContent.match(/^#\s+[^\n]+$/gm) || [];
      colorLog(`✓ 锁定的包数量: ${lockEntries.length}`, 'green');
      
      return true;
    } catch (error) {
      colorLog(`✗ 读取yarn.lock失败: ${error.message}`, 'red');
      return false;
    }
  }
  
  return false;
}

// 检查node_modules目录
function checkNodeModules() {
  colorLog('\n=== 检查 node_modules ===', 'cyan');
  
  const nodeModulesPath = path.join(process.cwd(), 'node_modules');
  if (checkFile(nodeModulesPath, 'node_modules目录')) {
    try {
      const items = fs.readdirSync(nodeModulesPath);
      colorLog(`✓ node_modules目录中的项目数量: ${items.length}`, 'green');
      
      // 检查是否有.bin目录
      const binPath = path.join(nodeModulesPath, '.bin');
      if (fs.existsSync(binPath)) {
        const binItems = fs.readdirSync(binPath);
        colorLog(`✓ 可执行脚本数量: ${binItems.length}`, 'green');
      }
      
      return true;
    } catch (error) {
      colorLog(`✗ 读取node_modules目录失败: ${error.message}`, 'red');
      return false;
    }
  }
  
  return false;
}

// 检查特定依赖
function checkSpecificDependencies() {
  colorLog('\n=== 检查特定依赖 ===', 'cyan');
  
  const packageJsonPath = path.join(process.cwd(), 'package.json');
  if (fs.existsSync(packageJsonPath)) {
    try {
      const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
      let allDepsPassed = true;
      
      // 检查生产依赖
      if (packageJson.dependencies) {
        Object.keys(packageJson.dependencies).forEach(dep => {
          const passed = checkDependency(dep);
          allDepsPassed = allDepsPassed && passed;
        });
      }
      
      // 检查开发依赖
      if (packageJson.devDependencies) {
        Object.keys(packageJson.devDependencies).forEach(dep => {
          const passed = checkDependency(dep);
          allDepsPassed = allDepsPassed && passed;
        });
      }
      
      return allDepsPassed;
    } catch (error) {
      colorLog(`✗ 读取package.json失败: ${error.message}`, 'red');
      return false;
    }
  }
  
  return false;
}

// 运行项目脚本
function testProjectScripts() {
  colorLog('\n=== 测试项目脚本 ===', 'cyan');
  
  const packageJsonPath = path.join(process.cwd(), 'package.json');
  if (fs.existsSync(packageJsonPath)) {
    try {
      const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
      
      if (packageJson.scripts) {
        colorLog('可用脚本:', 'blue');
        Object.keys(packageJson.scripts).forEach(script => {
          console.log(`  - ${script}: ${packageJson.scripts[script]}`);
        });
        
        // 测试build脚本
        if (packageJson.scripts.build) {
          colorLog('\n尝试运行构建脚本...', 'yellow');
          try {
            const { execSync } = require('child_process');
            const result = execSync('yarn build', { encoding: 'utf8', stdio: 'pipe' });
            colorLog('✓ 构建脚本运行成功', 'green');
            
            // 检查构建输出
            const distPath = path.join(process.cwd(), 'dist');
            if (fs.existsSync(distPath)) {
              colorLog('✓ 构建输出目录存在', 'green');
            } else {
              colorLog('⚠ 未找到构建输出目录', 'yellow');
            }
          } catch (error) {
            colorLog(`✗ 构建脚本运行失败: ${error.message}`, 'red');
          }
        }
        
        // 测试start脚本
        if (packageJson.scripts.start) {
          colorLog('\n提示: 可以运行 "yarn start" 来启动项目', 'blue');
        }
      }
    } catch (error) {
      colorLog(`✗ 读取package.json失败: ${error.message}`, 'red');
    }
  }
}

// 主检查函数
function main() {
  colorLog('===== Yarn安装验证工具 =====', 'bright');
  colorLog('此工具验证项目依赖是否正确安装', 'bright');
  
  let allChecksPassed = true;
  
  // 执行各项检查
  const packageJsonCheck = checkPackageJson();
  const yarnLockCheck = checkYarnLock();
  const nodeModulesCheck = checkNodeModules();
  const dependenciesCheck = checkSpecificDependencies();
  
  allChecksPassed = packageJsonCheck && yarnLockCheck && nodeModulesCheck && dependenciesCheck;
  
  // 测试项目脚本
  testProjectScripts();
  
  // 输出结果
  colorLog('\n===== 检查结果 =====', 'bright');
  
  if (allChecksPassed) {
    colorLog('✓ 所有检查通过，项目依赖已正确安装！', 'green');
    colorLog('\n下一步操作:', 'cyan');
    colorLog('- 运行 "yarn start" 启动项目', 'blue');
    colorLog('- 运行 "yarn dev" 进入开发模式', 'blue');
    colorLog('- 运行 "yarn test" 执行测试', 'blue');
  } else {
    colorLog('✗ 存在安装问题，请按照提示解决', 'red');
    colorLog('\n建议:', 'cyan');
    colorLog('- 运行 "yarn install" 重新安装依赖', 'blue');
    colorLog('- 删除 node_modules 和 yarn.lock 后重新安装', 'blue');
    colorLog('- 检查 package.json 是否有语法错误', 'blue');
  }
  
  colorLog('\n了解更多: https://yarnpkg.com', 'cyan');
}

// 运行主函数
main();