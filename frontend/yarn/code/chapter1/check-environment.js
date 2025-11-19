#!/usr/bin/env node

// 环境检查脚本
// 用于验证Node.js和Yarn环境是否正确安装和配置

const { execSync } = require('child_process');
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

// 执行命令并返回结果
function runCommand(command) {
  try {
    const result = execSync(command, { encoding: 'utf8' }).trim();
    return { success: true, output: result };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

// 检查Node.js
function checkNodeJs() {
  colorLog('\n=== 检查Node.js环境 ===', 'cyan');
  
  const nodeVersion = runCommand('node --version');
  if (nodeVersion.success) {
    colorLog(`✓ Node.js版本: ${nodeVersion.output}`, 'green');
    
    const majorVersion = parseInt(nodeVersion.output.slice(1).split('.')[0]);
    if (majorVersion >= 14) {
      colorLog('✓ Node.js版本满足要求 (>=14.0.0)', 'green');
    } else {
      colorLog('⚠ Node.js版本较旧，建议升级到14.0.0或更高版本', 'yellow');
    }
  } else {
    colorLog('✗ 未找到Node.js，请先安装Node.js', 'red');
    return false;
  }
  
  return true;
}

// 检查npm
function checkNpm() {
  colorLog('\n=== 检查NPM环境 ===', 'cyan');
  
  const npmVersion = runCommand('npm --version');
  if (npmVersion.success) {
    colorLog(`✓ NPM版本: ${npmVersion.output}`, 'green');
  } else {
    colorLog('✗ 未找到NPM', 'red');
    return false;
  }
  
  return true;
}

// 检查Yarn
function checkYarn() {
  colorLog('\n=== 检查Yarn环境 ===', 'cyan');
  
  const yarnVersion = runCommand('yarn --version');
  if (yarnVersion.success) {
    colorLog(`✓ Yarn版本: ${yarnVersion.output}`, 'green');
    
    const majorVersion = parseInt(yarnVersion.output.split('.')[0]);
    if (majorVersion === 1) {
      colorLog('✓ Yarn 1.x (Classic) 版本', 'green');
    } else if (majorVersion >= 2) {
      colorLog('✓ Yarn 2.x/3.x (Berry) 版本', 'green');
    }
  } else {
    colorLog('✗ 未找到Yarn，请先安装Yarn', 'red');
    return false;
  }
  
  return true;
}

// 检查Corepack
function checkCorepack() {
  colorLog('\n=== 检查Corepack支持 ===', 'cyan');
  
  const corepackEnabled = runCommand('corepack --version');
  if (corepackEnabled.success) {
    colorLog(`✓ Corepack已启用: ${corepackEnabled.output}`, 'green');
    
    const yarnStatus = runCommand('corepack which yarn');
    if (yarnStatus.success) {
      colorLog(`✓ Yarn由Corepack管理: ${yarnStatus.output}`, 'green');
    } else {
      colorLog('⚠ Yarn不是由Corepack管理', 'yellow');
    }
  } else {
    colorLog('⚠ Corepack未启用 (Node.js 16.10+支持)', 'yellow');
  }
}

// 检查全局配置
function checkGlobalConfig() {
  colorLog('\n=== 检查Yarn全局配置 ===', 'cyan');
  
  const config = runCommand('yarn config list');
  if (config.success) {
    colorLog('✓ Yarn配置:', 'green');
    console.log(config.output);
  } else {
    colorLog('⚠ 无法获取Yarn配置', 'yellow');
  }
}

// 检查网络连接
function checkNetworkConnectivity() {
  colorLog('\n=== 检查网络连接 ===', 'cyan');
  
  const registry = runCommand('yarn config get registry');
  if (registry.success) {
    colorLog(`✓ 当前registry: ${registry.output}`, 'green');
    
    // 这里应该添加实际的ping测试，但为了简化示例，只检查配置
    if (registry.output.includes('taobao.org')) {
      colorLog('✓ 使用淘宝镜像，国内访问速度较快', 'green');
    } else if (registry.output.includes('npmjs.org')) {
      colorLog('⚠ 使用官方registry，国内可能访问较慢', 'yellow');
    } else {
      colorLog(`✓ 使用自定义registry: ${registry.output}`, 'blue');
    }
  }
}

// 检查缓存
function checkCache() {
  colorLog('\n=== 检查Yarn缓存 ===', 'cyan');
  
  const cacheDir = runCommand('yarn cache dir');
  if (cacheDir.success) {
    colorLog(`✓ 缓存目录: ${cacheDir.output}`, 'green');
    
    // 检查缓存目录是否存在且可访问
    if (fs.existsSync(cacheDir.output)) {
      colorLog('✓ 缓存目录可访问', 'green');
    } else {
      colorLog('⚠ 缓存目录不存在，首次安装包时会自动创建', 'yellow');
    }
  }
}

// 主检查函数
function main() {
  colorLog('===== Yarn环境检查工具 =====', 'bright');
  colorLog('此工具检查您的Node.js和Yarn环境配置是否正确', 'bright');
  
  let allChecksPassed = true;
  
  // 执行各项检查
  allChecksPassed = checkNodeJs() && allChecksPassed;
  allChecksPassed = checkNpm() && allChecksPassed;
  allChecksPassed = checkYarn() && allChecksPassed;
  
  // 可选检查
  checkCorepack();
  checkGlobalConfig();
  checkNetworkConnectivity();
  checkCache();
  
  // 输出结果
  colorLog('\n===== 检查结果 =====', 'bright');
  
  if (allChecksPassed) {
    colorLog('✓ 所有必需检查通过，您的Yarn环境配置正确！', 'green');
    colorLog('\n建议:', 'cyan');
    colorLog('- 使用 "yarn init -y" 创建新项目', 'blue');
    colorLog('- 使用 "yarn add <package>" 添加依赖', 'blue');
    colorLog('- 使用 "yarn install" 安装项目依赖', 'blue');
  } else {
    colorLog('✗ 存在环境问题，请按照提示解决后再使用Yarn', 'red');
    colorLog('\n建议:', 'cyan');
    colorLog('- 确保已安装Node.js和Yarn', 'blue');
    colorLog('- 检查PATH环境变量是否包含Node.js和Yarn', 'blue');
    colorLog('- 考虑使用Node.js版本管理器(nvm, n等)', 'blue');
  }
  
  colorLog('\n了解更多: https://yarnpkg.com', 'cyan');
}

// 运行主函数
main();