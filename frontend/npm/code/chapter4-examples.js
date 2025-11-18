/**
 * NPM脚本与自动化示例代码
 * 这些示例展示了如何使用NPM脚本进行各种自动化任务
 */

const fs = require('fs');
const path = require('path');

// 示例1: 解析package.json中的scripts
function parsePackageScripts() {
  console.log('=== 示例1: 解析package.json中的scripts ===');
  
  try {
    const packagePath = path.join(__dirname, 'package.json');
    const packageData = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
    
    console.log('项目名称:', packageData.name);
    console.log('版本:', packageData.version);
    console.log('脚本列表:');
    
    if (packageData.scripts) {
      Object.entries(packageData.scripts).forEach(([name, script]) => {
        console.log(`  ${name}: ${script}`);
      });
    } else {
      console.log('  未定义任何脚本');
    }
    
    return packageData.scripts || {};
  } catch (error) {
    console.error('解析package.json失败:', error.message);
    return {};
  }
}

// 示例2: 模拟NPM脚本执行
function executeScript(scriptName, scripts) {
  console.log(`\n=== 示例2: 执行脚本 "${scriptName}" ===`);
  
  if (!scripts[scriptName]) {
    console.log(`错误: 脚本 "${scriptName}" 不存在`);
    return false;
  }
  
  const command = scripts[scriptName];
  console.log(`执行命令: ${command}`);
  
  // 模拟不同类型的命令
  if (command.includes('echo')) {
    // 模拟echo命令
    const output = command.replace(/echo\s+['"]?([^'"]*)['"]?/, '$1');
    console.log(output);
  } else if (command.includes('node')) {
    // 模拟node命令
    const file = command.match(/node\s+(.+?)($|\s)/);
    if (file) {
      console.log(`模拟执行Node.js文件: ${file[1]}`);
      console.log('Node.js应用已启动');
    }
  } else if (command.includes('npm run')) {
    // 模拟npm run命令
    const nestedScript = command.match(/npm run\s+(.+?)($|\s)/);
    if (nestedScript) {
      console.log(`调用嵌套脚本: ${nestedScript[1]}`);
      executeScript(nestedScript[1], scripts);
    }
  } else if (command.includes('&&')) {
    // 模拟命令链
    const commands = command.split('&&');
    console.log('执行命令链:');
    commands.forEach((cmd, index) => {
      console.log(`  步骤${index + 1}: ${cmd.trim()}`);
    });
    console.log('命令链执行完成');
  } else {
    // 其他命令
    console.log(`模拟执行命令: ${command}`);
  }
  
  return true;
}

// 示例3: 脚本依赖分析
function analyzeScriptDependencies(scripts) {
  console.log('\n=== 示例3: 脚本依赖分析 ===');
  
  const dependencies = {};
  
  // 分析脚本间的依赖关系
  Object.entries(scripts).forEach(([name, command]) => {
    const deps = [];
    
    // 查找npm run调用
    const runMatches = command.matchAll(/npm run ([\w:-]+)/g);
    for (const match of runMatches) {
      deps.push(match[1]);
    }
    
    if (deps.length > 0) {
      dependencies[name] = deps;
    }
  });
  
  console.log('脚本依赖关系:');
  Object.entries(dependencies).forEach(([script, deps]) => {
    console.log(`  ${script} 依赖于: ${deps.join(', ')}`);
  });
  
  return dependencies;
}

// 示例4: 生命周期脚本模拟
function simulateLifecycleScripts(scripts) {
  console.log('\n=== 示例4: 生命周期脚本模拟 ===');
  
  // 定义生命周期顺序
  const lifecycleOrder = [
    'preinstall', 'install', 'postinstall',
    'prepublish', 'prepare', 'prepublishOnly',
    'prepack', 'postpack',
    'publish', 'postpublish',
    'prestart', 'start', 'poststart',
    'prestop', 'stop', 'poststop',
    'prerestart', 'restart', 'postrestart',
    'pretest', 'test', 'posttest',
    'preversion', 'version', 'postversion'
  ];
  
  // 模拟start生命周期
  console.log('模拟start生命周期:');
  ['prestart', 'start', 'poststart'].forEach(phase => {
    if (scripts[phase]) {
      console.log(`执行 ${phase}: ${scripts[phase]}`);
      executeScript(phase, scripts);
    } else {
      console.log(`${phase}: 未定义脚本`);
    }
  });
  
  return lifecycleOrder;
}

// 示例5: 环境变量处理
function processEnvironmentVariables() {
  console.log('\n=== 示例5: 环境变量处理 ===');
  
  // 模拟NPM内置环境变量
  const npmEnvVars = {
    'npm_config_root': '/usr/local',
    'npm_config_prefix': '/usr/local',
    'npm_package_name': 'npm-tutorial',
    'npm_package_version': '1.0.0',
    'npm_package_description': 'NPM教程示例',
    'npm_lifecycle_event': 'start',
    'npm_lifecycle_script': 'echo "Starting application"'
  };
  
  console.log('NPM内置环境变量:');
  Object.entries(npmEnvVars).forEach(([key, value]) => {
    console.log(`  ${key}: ${value}`);
  });
  
  // 模拟处理环境变量替换
  const command = 'echo "Starting $npm_package_name v$npm_package_version"';
  let processedCommand = command;
  
  Object.entries(npmEnvVars).forEach(([key, value]) => {
    const regex = new RegExp(`\\$${key}`, 'g');
    processedCommand = processedCommand.replace(regex, value);
  });
  
  console.log(`\n原始命令: ${command}`);
  console.log(`处理后命令: ${processedCommand}`);
  
  return npmEnvVars;
}

// 示例6: 脚本参数处理
function processScriptArguments() {
  console.log('\n=== 示例6: 脚本参数处理 ===');
  
  // 模拟命令行参数
  const processArgv = ['node', 'npm', 'run', 'build', '--', '--mode', 'production', '--analyze'];
  
  console.log('命令行参数:', processArgv.join(' '));
  
  // 解析npm run命令
  if (processArgv[2] === 'run' && processArgv[3]) {
    const scriptName = processArgv[3];
    console.log(`脚本名: ${scriptName}`);
    
    // 查找参数分隔符
    const separatorIndex = processArgv.indexOf('--');
    
    if (separatorIndex !== -1) {
      const args = processArgv.slice(separatorIndex + 1);
      console.log(`脚本参数: ${args.join(' ')}`);
      
      // 解析键值对参数
      const parsedArgs = {};
      for (let i = 0; i < args.length; i += 2) {
        if (args[i].startsWith('--') && i + 1 < args.length) {
          const key = args[i].substring(2);
          const value = args[i + 1];
          parsedArgs[key] = value;
        }
      }
      
      console.log('解析后的参数:');
      Object.entries(parsedArgs).forEach(([key, value]) => {
        console.log(`  ${key}: ${value}`);
      });
      
      return parsedArgs;
    }
  }
  
  return {};
}

// 示例7: 并行和顺序执行模拟
function simulateScriptExecution(scripts) {
  console.log('\n=== 示例7: 并行和顺序执行模拟 ===');
  
  // 顺序执行示例
  console.log('顺序执行示例:');
  const sequentialScript = 'npm run clean && npm run build && npm run test';
  console.log(`命令: ${sequentialScript}`);
  
  const commands = sequentialScript.split('&&').map(cmd => cmd.trim());
  commands.forEach((cmd, index) => {
    console.log(`  步骤${index + 1}: ${cmd}`);
    if (cmd.startsWith('npm run')) {
      const scriptName = cmd.replace('npm run ', '');
      console.log(`    执行脚本: ${scriptName}`);
    }
  });
  
  // 并行执行示例
  console.log('\n并行执行示例:');
  const parallelScript = 'npm run watch:js & npm run watch:css';
  console.log(`命令: ${parallelScript}`);
  
  const parallelCommands = parallelScript.split('&').map(cmd => cmd.trim());
  console.log('并行启动以下进程:');
  parallelCommands.forEach((cmd, index) => {
    console.log(`  进程${index + 1}: ${cmd}`);
    if (cmd.startsWith('npm run')) {
      const scriptName = cmd.replace('npm run ', '');
      console.log(`    执行脚本: ${scriptName}`);
    }
  });
  
  return { sequential: commands, parallel: parallelCommands };
}

// 示例8: 脚本最佳实践检查
function checkScriptBestPractices(scripts) {
  console.log('\n=== 示例8: 脚本最佳实践检查 ===');
  
  const recommendations = [];
  
  // 检查是否有lint脚本
  if (!scripts.lint) {
    recommendations.push('建议添加lint脚本来检查代码质量');
  }
  
  // 检查是否有测试脚本
  if (!scripts.test) {
    recommendations.push('建议添加test脚本来运行测试');
  }
  
  // 检查是否有构建脚本
  if (!scripts.build) {
    recommendations.push('建议添加build脚本来构建项目');
  }
  
  // 检查是否有清理脚本
  if (!scripts.clean) {
    recommendations.push('建议添加clean脚本来清理构建文件');
  }
  
  // 检查脚本命名
  Object.keys(scripts).forEach(name => {
    if (name.includes(' ') || name.includes('_')) {
      recommendations.push(`脚本名"${name}"建议使用连字符(-)代替空格或下划线`);
    }
  });
  
  // 检查是否有预脚本
  if (scripts.test && !scripts.pretest) {
    recommendations.push('建议为test脚本添加pretest钩子，在测试前运行lint');
  }
  
  // 检查是否有后脚本
  if (scripts.build && !scripts.postbuild) {
    recommendations.push('可以考虑为build脚本添加postbuild钩子，在构建后执行额外任务');
  }
  
  if (recommendations.length > 0) {
    console.log('脚本最佳实践建议:');
    recommendations.forEach((rec, index) => {
      console.log(`  ${index + 1}. ${rec}`);
    });
  } else {
    console.log('脚本配置符合最佳实践！');
  }
  
  return recommendations;
}

// 示例9: 生成脚本文档
function generateScriptDocumentation(scripts) {
  console.log('\n=== 示例9: 生成脚本文档 ===');
  
  let documentation = '# NPM脚本文档\n\n';
  documentation += '本文档自动生成，包含项目中所有NPM脚本的说明。\n\n';
  
  // 按类别分组脚本
  const categories = {
    '开发脚本': ['start', 'dev', 'serve', 'watch'],
    '构建脚本': ['build', 'clean', 'prebuild', 'postbuild'],
    '测试脚本': ['test', 'test:watch', 'test:coverage', 'pretest', 'posttest'],
    '代码质量': ['lint', 'lint:fix', 'format', 'format:check'],
    '部署脚本': ['deploy', 'deploy:staging', 'deploy:prod'],
    '版本管理': ['version', 'release', 'preversion', 'postversion']
  };
  
  // 为每个类别生成文档
  Object.entries(categories).forEach(([category, keywords]) => {
    const categoryScripts = Object.keys(scripts).filter(name => 
      keywords.some(keyword => name.includes(keyword))
    );
    
    if (categoryScripts.length > 0) {
      documentation += `## ${category}\n\n`;
      documentation += '| 脚本名 | 命令 |\n';
      documentation += '|--------|------|\n';
      
      categoryScripts.forEach(name => {
        documentation += `| \`${name}\` | \`${scripts[name]}\` |\n`;
      });
      
      documentation += '\n';
    }
  });
  
  // 添加未分类的脚本
  const uncategorizedScripts = Object.keys(scripts).filter(name => 
    !Object.values(categories).flat().some(keyword => name.includes(keyword))
  );
  
  if (uncategorizedScripts.length > 0) {
    documentation += '## 其他脚本\n\n';
    documentation += '| 脚本名 | 命令 |\n';
    documentation += '|--------|------|\n';
    
    uncategorizedScripts.forEach(name => {
      documentation += `| \`${name}\` | \`${scripts[name]}\` |\n`;
    });
  }
  
  // 保存文档
  const docPath = path.join(__dirname, 'scripts-documentation.md');
  fs.writeFileSync(docPath, documentation);
  
  console.log(`脚本文档已生成: ${docPath}`);
  console.log('文档预览:');
  console.log(documentation.substring(0, 500) + '...');
  
  return documentation;
}

// 示例10: 脚本性能分析
function analyzeScriptPerformance(scripts) {
  console.log('\n=== 示例10: 脚本性能分析 ===');
  
  // 模拟脚本执行时间
  const scriptTimes = {};
  
  Object.entries(scripts).forEach(([name, command]) => {
    // 根据命令复杂度估算执行时间
    let time = 0;
    
    if (command.includes('test')) {
      time = 5 + Math.random() * 10; // 测试: 5-15秒
    } else if (command.includes('build')) {
      time = 10 + Math.random() * 20; // 构建: 10-30秒
    } else if (command.includes('lint')) {
      time = 2 + Math.random() * 3; // 代码检查: 2-5秒
    } else if (command.includes('clean')) {
      time = 1 + Math.random() * 2; // 清理: 1-3秒
    } else {
      time = 1 + Math.random() * 5; // 其他: 1-6秒
    }
    
    scriptTimes[name] = time;
  });
  
  // 排序并显示
  const sortedScripts = Object.entries(scriptTimes)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5); // 只显示前5个最耗时的脚本
  
  console.log('最耗时的5个脚本:');
  sortedScripts.forEach(([name, time], index) => {
    console.log(`  ${index + 1}. ${name}: ${time.toFixed(2)}秒`);
  });
  
  // 分析优化建议
  console.log('\n性能优化建议:');
  
  // 检查是否有并行执行的机会
  const parallelizable = Object.keys(scripts).filter(name => 
    scripts[name].includes('&&') && 
    !scripts[name].includes('npm run')
  );
  
  if (parallelizable.length > 0) {
    console.log('  以下脚本可能可以并行执行以提升性能:');
    parallelizable.forEach(name => {
      console.log(`    - ${name}: ${scripts[name]}`);
    });
  }
  
  // 检查是否有缓存机会
  const cacheable = Object.keys(scripts).filter(name => 
    name.includes('build') || name.includes('compile')
  );
  
  if (cacheable.length > 0) {
    console.log('  以下脚本可能可以添加缓存以提升性能:');
    cacheable.forEach(name => {
      console.log(`    - ${name}: ${scripts[name]}`);
    });
  }
  
  return scriptTimes;
}

// 主函数
function main() {
  console.log('NPM脚本与自动化示例');
  console.log('====================');
  
  // 解析package.json中的scripts
  const scripts = parsePackageScripts();
  
  // 如果没有脚本，创建一些示例脚本
  if (Object.keys(scripts).length === 0) {
    console.log('\n创建示例脚本...');
    scripts.start = 'echo "Starting application"';
    scripts.dev = 'nodemon src/index.js';
    scripts.build = 'webpack --mode production';
    scripts.test = 'jest';
    scripts.lint = 'eslint src/**/*.js';
    scripts.clean = 'rimraf dist';
    scripts.deploy = 'npm run build && npm run upload';
  }
  
  // 执行各种示例
  executeScript('start', scripts);
  analyzeScriptDependencies(scripts);
  simulateLifecycleScripts(scripts);
  processEnvironmentVariables();
  processScriptArguments();
  simulateScriptExecution(scripts);
  checkScriptBestPractices(scripts);
  generateScriptDocumentation(scripts);
  analyzeScriptPerformance(scripts);
  
  console.log('\n所有示例执行完成！');
}

// 运行主函数
if (require.main === module) {
  main();
}

module.exports = {
  parsePackageScripts,
  executeScript,
  analyzeScriptDependencies,
  simulateLifecycleScripts,
  processEnvironmentVariables,
  processScriptArguments,
  simulateScriptExecution,
  checkScriptBestPractices,
  generateScriptDocumentation,
  analyzeScriptPerformance
};