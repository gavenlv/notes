// 第1章：NPM基础入门与环境搭建 - 代码示例

// 示例1：验证Node.js和NPM安装
console.log("=== 验证Node.js和NPM安装 ===");
console.log("Node.js版本:", process.version);
console.log("当前平台:", process.platform);
console.log("当前架构:", process.arch);

// 示例2：使用require加载模块
console.log("\n=== 使用require加载模块 ===");
try {
  const fs = require('fs');
  const path = require('path');
  
  console.log("成功加载fs模块");
  console.log("成功加载path模块");
  
  // 获取当前工作目录
  const currentDir = process.cwd();
  console.log("当前工作目录:", currentDir);
  
  // 检查package.json是否存在
  const packageJsonPath = path.join(currentDir, 'package.json');
  const packageExists = fs.existsSync(packageJsonPath);
  console.log("package.json是否存在:", packageExists);
  
  if (packageExists) {
    const packageJson = require('./package.json');
    console.log("项目名称:", packageJson.name);
    console.log("项目版本:", packageJson.version);
    console.log("项目描述:", packageJson.description);
  }
} catch (error) {
  console.error("加载模块时出错:", error.message);
}

// 示例3：模块路径解析
console.log("\n=== 模块路径解析 ===");
console.log("模块路径:");
console.log("- 当前目录:", __dirname);
console.log("- 当前文件路径:", __filename);
console.log("- Node.js模块路径:", module.paths);

// 示例4：环境变量
console.log("\n=== 环境变量 ===");
console.log("NODE_ENV:", process.env.NODE_ENV || "未设置");
console.log("PATH:", process.env.PATH ? process.env.PATH.split(';')[0] : "未设置");

// 示例5：NPM配置信息
console.log("\n=== NPM配置信息 ===");
try {
  const { execSync } = require('child_process');
  
  // 获取NPM版本
  const npmVersion = execSync('npm -v', { encoding: 'utf8' }).trim();
  console.log("NPM版本:", npmVersion);
  
  // 获取NPM配置
  const npmConfig = execSync('npm config list --json', { encoding: 'utf8' });
  const config = JSON.parse(npmConfig);
  
  console.log("NPM注册表:", config.registry || "默认");
  console.log("NPM缓存目录:", config.cache || "默认");
  console.log("NPM前缀目录:", config.prefix || "默认");
} catch (error) {
  console.error("获取NPM配置时出错:", error.message);
}

// 示例6：模拟package.json解析
console.log("\n=== 模拟package.json解析 ===");
const mockPackageJson = {
  name: "npm-basics-example",
  version: "1.0.0",
  description: "NPM基础入门示例项目",
  main: "index.js",
  scripts: {
    start: "node index.js",
    test: "echo \"Error: no test specified\" && exit 1"
  },
  keywords: ["npm", "node", "javascript"],
  author: "Your Name",
  license: "MIT",
  dependencies: {
    lodash: "^4.17.21"
  },
  devDependencies: {
    jest: "^29.6.1"
  }
};

console.log("模拟package.json内容:");
console.log("- 项目名称:", mockPackageJson.name);
console.log("- 项目版本:", mockPackageJson.version);
console.log("- 主入口文件:", mockPackageJson.main);
console.log("- 脚本命令:", Object.keys(mockPackageJson.scripts));
console.log("- 依赖项:", Object.keys(mockPackageJson.dependencies));
console.log("- 开发依赖项:", Object.keys(mockPackageJson.devDependencies));

// 示例7：模块导出和导入
console.log("\n=== 模块导出和导入 ===");

// 定义一个简单的工具函数
const utils = {
  add: (a, b) => a + b,
  subtract: (a, b) => a - b,
  multiply: (a, b) => a * b,
  divide: (a, b) => b !== 0 ? a / b : "除数不能为零",
  
  // 格式化日期
  formatDate: (date = new Date()) => {
    return date.toISOString().split('T')[0];
  },
  
  // 生成随机ID
  generateId: (length = 8) => {
    let result = '';
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const charactersLength = characters.length;
    for (let i = 0; i < length; i++) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
  }
};

// 使用工具函数
console.log("数学运算:");
console.log("- 5 + 3 =", utils.add(5, 3));
console.log("- 10 - 4 =", utils.subtract(10, 4));
console.log("- 6 * 7 =", utils.multiply(6, 7));
console.log("- 15 / 3 =", utils.divide(15, 3));

console.log("\n其他工具:");
console.log("- 今天日期:", utils.formatDate());
console.log("- 随机ID:", utils.generateId());

// 示例8：模拟NPM脚本执行
console.log("\n=== 模拟NPM脚本执行 ===");

// 模拟npm start
function runScript(scriptName) {
  console.log(`运行脚本: npm run ${scriptName}`);
  
  switch (scriptName) {
    case 'start':
      console.log("启动应用程序...");
      console.log("应用程序已启动，监听端口3000");
      break;
    case 'test':
      console.log("运行测试...");
      console.log("测试通过: 10个测试用例全部通过");
      break;
    case 'build':
      console.log("构建应用程序...");
      console.log("构建完成，输出到dist目录");
      break;
    default:
      console.log(`未知脚本: ${scriptName}`);
  }
}

// 模拟运行不同的脚本
runScript('start');
runScript('test');
runScript('build');

// 示例9：依赖管理模拟
console.log("\n=== 依赖管理模拟 ===");

// 模拟已安装的依赖
const installedDependencies = {
  "lodash": {
    version: "4.17.21",
    description: "Lodash utility library"
  },
  "express": {
    version: "4.18.2",
    description: "Fast, unopinionated, minimalist web framework"
  },
  "moment": {
    version: "2.29.4",
    description: "Parse, validate, manipulate, and display dates"
  }
};

// 显示已安装的依赖
console.log("已安装的依赖:");
Object.entries(installedDependencies).forEach(([name, info]) => {
  console.log(`- ${name}@${info.version}: ${info.description}`);
});

// 模拟检查依赖更新
console.log("\n检查依赖更新...");
console.log("lodash@4.17.21 是最新版本");
console.log("express@4.18.2 有新版本 4.19.0 可用");
console.log("moment@2.29.4 有新版本 2.30.1 可用");

// 示例10：NPM最佳实践提示
console.log("\n=== NPM最佳实践提示 ===");

const bestPractices = [
  "始终使用npm init -y初始化新项目",
  "定期更新依赖: npm update",
  "使用npm audit检查安全漏洞",
  "使用--save-dev安装开发依赖",
  "添加.gitignore忽略node_modules",
  "使用package-lock.json锁定依赖版本",
  "使用npm scripts定义常用命令",
  "使用语义化版本控制",
  "为项目编写清晰的README",
  "使用.npmrc文件管理项目特定配置"
];

console.log("NPM最佳实践:");
bestPractices.forEach((practice, index) => {
  console.log(`${index + 1}. ${practice}`);
});

console.log("\n=== 第1章示例代码结束 ===");