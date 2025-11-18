// 第3章：package.json详解 - 代码示例

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log("=== 第3章：package.json详解 - 代码示例 ===\n");

// 示例1：解析package.json文件
console.log("=== 示例1：解析package.json文件 ===");

function parsePackageJson(filePath) {
  try {
    const packageJsonContent = fs.readFileSync(filePath, 'utf8');
    const packageJson = JSON.parse(packageJsonContent);
    return packageJson;
  } catch (error) {
    console.error(`解析package.json失败: ${error.message}`);
    return null;
  }
}

const packageJsonPath = path.join(__dirname, 'package.json');
const packageJson = parsePackageJson(packageJsonPath);

if (packageJson) {
  console.log("项目名称:", packageJson.name);
  console.log("版本:", packageJson.version);
  console.log("描述:", packageJson.description);
  console.log("作者:", packageJson.author);
  console.log("许可证:", packageJson.license);
  console.log("依赖数量:", Object.keys(packageJson.dependencies || {}).length);
  console.log("开发依赖数量:", Object.keys(packageJson.devDependencies || {}).length);
  console.log("脚本数量:", Object.keys(packageJson.scripts || {}).length);
}

// 示例2：验证package.json字段
console.log("\n=== 示例2：验证package.json字段 ===");

function validatePackageJson(packageJson) {
  const errors = [];
  const warnings = [];
  
  // 必需字段检查
  if (!packageJson.name) {
    errors.push("缺少必需字段: name");
  } else {
    // 名称验证
    if (packageJson.name.length > 214) {
      errors.push("name字段长度超过214个字符");
    }
    if (!/^[a-z0-9-_\.]+$/.test(packageJson.name)) {
      errors.push("name字段包含非法字符，只能包含小写字母、数字、连字符、下划线和点");
    }
    if (/^[._]/.test(packageJson.name)) {
      errors.push("name字段不能以点或下划线开头");
    }
  }
  
  if (!packageJson.version) {
    errors.push("缺少必需字段: version");
  } else {
    // 版本验证
    if (!/^\d+\.\d+\.\d+/.test(packageJson.version)) {
      errors.push("version字段不符合语义化版本规范");
    }
  }
  
  // 推荐字段检查
  if (!packageJson.description) {
    warnings.push("缺少推荐字段: description");
  }
  
  if (!packageJson.license) {
    warnings.push("缺少推荐字段: license");
  }
  
  if (!packageJson.author) {
    warnings.push("缺少推荐字段: author");
  }
  
  // 依赖检查
  if (packageJson.dependencies) {
    Object.entries(packageJson.dependencies).forEach(([name, version]) => {
      if (typeof version !== 'string') {
        errors.push(`依赖 ${name} 的版本不是字符串`);
      }
    });
  }
  
  return { errors, warnings };
}

const validation = validatePackageJson(packageJson || {});
console.log("验证结果:");
if (validation.errors.length > 0) {
  console.log("错误:");
  validation.errors.forEach(error => console.log(`  - ${error}`));
}
if (validation.warnings.length > 0) {
  console.log("警告:");
  validation.warnings.forEach(warning => console.log(`  - ${warning}`));
}
if (validation.errors.length === 0 && validation.warnings.length === 0) {
  console.log("package.json验证通过!");
}

// 示例3：版本范围解析
console.log("\n=== 示例3：版本范围解析 ===");

function parseVersionRange(range) {
  const match = range.match(/^(\^|~|>=|<=|>|<)?(\d+\.\d+\.\d+)$/);
  if (!match) return null;
  
  const operator = match[1] || '';
  const version = match[2].split('.').map(Number);
  
  const [major, minor, patch] = version;
  
  switch (operator) {
    case '^':
      return {
        min: `${major}.${minor}.${patch}`,
        max: `${major + 1}.0.0`,
        description: `兼容主版本${major}的所有版本`
      };
    case '~':
      return {
        min: `${major}.${minor}.${patch}`,
        max: `${major}.${minor + 1}.0`,
        description: `兼容次版本${major}.${minor}的所有版本`
      };
    case '>=':
      return {
        min: `${major}.${minor}.${patch}`,
        max: '∞',
        description: `大于等于${major}.${minor}.${patch}的所有版本`
      };
    case '<=':
      return {
        min: '0.0.0',
        max: `${major}.${minor}.${patch}`,
        description: `小于等于${major}.${minor}.${patch}的所有版本`
      };
    case '>':
      return {
        min: `${major}.${minor}.${patch}`,
        max: '∞',
        description: `大于${major}.${minor}.${patch}的所有版本`
      };
    case '<':
      return {
        min: '0.0.0',
        max: `${major}.${minor}.${patch}`,
        description: `小于${major}.${minor}.${patch}的所有版本`
      };
    default:
      return {
        min: `${major}.${minor}.${patch}`,
        max: `${major}.${minor}.${patch}`,
        description: `仅版本${major}.${minor}.${patch}`
      };
  }
}

const versionRanges = ['1.2.3', '^1.2.3', '~1.2.3', '>=1.2.3', '<=1.2.3', '>1.2.3', '<1.2.3'];

versionRanges.forEach(range => {
  const parsed = parseVersionRange(range);
  if (parsed) {
    console.log(`${range}: ${parsed.description} (最小: ${parsed.min}, 最大: ${parsed.max})`);
  }
});

// 示例4：依赖树分析
console.log("\n=== 示例4：依赖树分析 ===");

function analyzeDependencies(packageJson) {
  const analysis = {
    totalDependencies: 0,
    totalDevDependencies: 0,
    totalPeerDependencies: 0,
    totalOptionalDependencies: 0,
    dependencyTypes: {},
    outdatedDependencies: []
  };
  
  // 分析生产依赖
  if (packageJson.dependencies) {
    analysis.totalDependencies = Object.keys(packageJson.dependencies).length;
    analysis.dependencyTypes.dependencies = packageJson.dependencies;
  }
  
  // 分析开发依赖
  if (packageJson.devDependencies) {
    analysis.totalDevDependencies = Object.keys(packageJson.devDependencies).length;
    analysis.dependencyTypes.devDependencies = packageJson.devDependencies;
  }
  
  // 分析对等依赖
  if (packageJson.peerDependencies) {
    analysis.totalPeerDependencies = Object.keys(packageJson.peerDependencies).length;
    analysis.dependencyTypes.peerDependencies = packageJson.peerDependencies;
  }
  
  // 分析可选依赖
  if (packageJson.optionalDependencies) {
    analysis.totalOptionalDependencies = Object.keys(packageJson.optionalDependencies).length;
    analysis.dependencyTypes.optionalDependencies = packageJson.optionalDependencies;
  }
  
  return analysis;
}

if (packageJson) {
  const dependencyAnalysis = analyzeDependencies(packageJson);
  console.log("依赖分析结果:");
  console.log(`  生产依赖数量: ${dependencyAnalysis.totalDependencies}`);
  console.log(`  开发依赖数量: ${dependencyAnalysis.totalDevDependencies}`);
  console.log(`  对等依赖数量: ${dependencyAnalysis.totalPeerDependencies}`);
  console.log(`  可选依赖数量: ${dependencyAnalysis.totalOptionalDependencies}`);
  console.log(`  总依赖数量: ${dependencyAnalysis.totalDependencies + dependencyAnalysis.totalDevDependencies}`);
}

// 示例5：脚本分析
console.log("\n=== 示例5：脚本分析 ===");

function analyzeScripts(packageJson) {
  if (!packageJson.scripts) return null;
  
  const scripts = packageJson.scripts;
  const analysis = {
    totalScripts: Object.keys(scripts).length,
    lifecycleScripts: {},
    customScripts: {},
    scriptCategories: {
      build: [],
      test: [],
      dev: [],
      lint: [],
      other: []
    }
  };
  
  // 生命周期脚本
  const lifecyclePatterns = [
    'preinstall', 'install', 'postinstall',
    'prepublish', 'publish', 'postpublish',
    'preuninstall', 'uninstall', 'postuninstall',
    'prestart', 'start', 'poststart',
    'prestop', 'stop', 'poststop',
    'prerestart', 'restart', 'postrestart',
    'pretest', 'test', 'posttest'
  ];
  
  Object.entries(scripts).forEach(([name, command]) => {
    if (lifecyclePatterns.includes(name)) {
      analysis.lifecycleScripts[name] = command;
    } else {
      analysis.customScripts[name] = command;
    }
    
    // 脚本分类
    if (name.includes('build')) {
      analysis.scriptCategories.build.push({ name, command });
    } else if (name.includes('test')) {
      analysis.scriptCategories.test.push({ name, command });
    } else if (name.includes('dev') || name.includes('serve')) {
      analysis.scriptCategories.dev.push({ name, command });
    } else if (name.includes('lint')) {
      analysis.scriptCategories.lint.push({ name, command });
    } else {
      analysis.scriptCategories.other.push({ name, command });
    }
  });
  
  return analysis;
}

if (packageJson) {
  const scriptAnalysis = analyzeScripts(packageJson);
  if (scriptAnalysis) {
    console.log("脚本分析结果:");
    console.log(`  总脚本数量: ${scriptAnalysis.totalScripts}`);
    console.log(`  生命周期脚本数量: ${Object.keys(scriptAnalysis.lifecycleScripts).length}`);
    console.log(`  自定义脚本数量: ${Object.keys(scriptAnalysis.customScripts).length}`);
    
    console.log("\n脚本分类:");
    Object.entries(scriptAnalysis.scriptCategories).forEach(([category, scripts]) => {
      if (scripts.length > 0) {
        console.log(`  ${category}:`);
        scripts.forEach(script => {
          console.log(`    - ${script.name}: ${script.command}`);
        });
      }
    });
  }
}

// 示例6：生成package.json模板
console.log("\n=== 示例6：生成package.json模板 ===");

function generatePackageJsonTemplate(type = 'basic') {
  const templates = {
    basic: {
      name: "my-project",
      version: "1.0.0",
      description: "A basic Node.js project",
      main: "index.js",
      scripts: {
        start: "node index.js",
        test: "echo \"Error: no test specified\" && exit 1"
      },
      keywords: [],
      author: "",
      license: "ISC"
    },
    webapp: {
      name: "my-web-app",
      version: "1.0.0",
      description: "A modern web application",
      main: "src/index.js",
      scripts: {
        start: "node src/index.js",
        dev: "nodemon src/index.js",
        build: "webpack --mode production",
        test: "jest",
        lint: "eslint src/**/*.js",
        format: "prettier --write src/**/*.js"
      },
      keywords: ["web", "app", "javascript"],
      author: "",
      license: "MIT",
      dependencies: {
        express: "^4.18.2"
      },
      devDependencies: {
        nodemon: "^3.0.1",
        jest: "^29.6.1",
        eslint: "^8.45.0",
        prettier: "^3.0.0",
        webpack: "^5.88.2"
      }
    },
    library: {
      name: "my-library",
      version: "1.0.0",
      description: "A reusable JavaScript library",
      main: "dist/index.js",
      module: "dist/index.esm.js",
      types: "dist/index.d.ts",
      scripts: {
        build: "rollup -c",
        test: "jest",
        test:coverage": "jest --coverage",
        lint: "eslint src/**/*.js",
        prepublishOnly: "npm run build && npm test"
      },
      keywords: ["library", "javascript", "reusable"],
      author: "",
      license: "MIT",
      files: [
        "dist/",
        "README.md",
        "LICENSE"
      ],
      devDependencies: {
        rollup: "^3.26.3",
        jest: "^29.6.1",
        eslint: "^8.45.0"
      }
    },
    cli: {
      name: "my-cli",
      version: "1.0.0",
      description: "A command-line interface tool",
      main: "src/index.js",
      bin: {
        "my-cli": "./bin/cli.js"
      },
      scripts: {
        test: "jest",
        lint: "eslint src/**/*.js bin/**/*.js",
        prepare: "husky install"
      },
      keywords: ["cli", "command-line", "tool"],
      author: "",
      license: "MIT",
      files: [
        "bin/",
        "src/",
        "README.md",
        "LICENSE"
      ],
      dependencies: {
        commander: "^11.0.0",
        chalk: "^5.3.0",
        inquirer: "^9.2.8"
      },
      devDependencies: {
        jest: "^29.6.1",
        eslint: "^8.45.0",
        husky: "^8.0.3"
      }
    }
  };
  
  return templates[type] || templates.basic;
}

const templateTypes = ['basic', 'webapp', 'library', 'cli'];

templateTypes.forEach(type => {
  console.log(`\n${type} 模板:`);
  const template = generatePackageJsonTemplate(type);
  console.log(JSON.stringify(template, null, 2));
});

// 示例7：package.json字段验证器
console.log("\n=== 示例7：package.json字段验证器 ===");

class PackageJsonValidator {
  constructor() {
    this.rules = {
      name: {
        required: true,
        type: 'string',
        pattern: /^[a-z0-9-_\.]+$/,
        maxLength: 214,
        description: "包名必须是小写字母、数字、连字符、下划线和点的组合，长度不超过214个字符"
      },
      version: {
        required: true,
        type: 'string',
        pattern: /^\d+\.\d+\.\d+(-[a-zA-Z0-9\-\.]+)?(\+[a-zA-Z0-9\-\.]+)?$/,
        description: "版本必须符合语义化版本规范"
      },
      description: {
        required: false,
        type: 'string',
        description: "项目描述"
      },
      main: {
        required: false,
        type: 'string',
        description: "项目入口文件"
      },
      scripts: {
        required: false,
        type: 'object',
        description: "项目脚本"
      },
      keywords: {
        required: false,
        type: 'array',
        description: "项目关键词"
      },
      author: {
        required: false,
        type: ['string', 'object'],
        description: "项目作者"
      },
      license: {
        required: false,
        type: 'string',
        description: "项目许可证"
      },
      dependencies: {
        required: false,
        type: 'object',
        description: "生产依赖"
      },
      devDependencies: {
        required: false,
        type: 'object',
        description: "开发依赖"
      },
      engines: {
        required: false,
        type: 'object',
        description: "支持的Node.js和NPM版本"
      }
    };
  }
  
  validate(packageJson) {
    const errors = [];
    const warnings = [];
    
    Object.entries(this.rules).forEach(([field, rule]) => {
      const value = packageJson[field];
      
      // 检查必需字段
      if (rule.required && value === undefined) {
        errors.push(`缺少必需字段: ${field}`);
        return;
      }
      
      // 如果字段不存在且不是必需的，跳过验证
      if (value === undefined) return;
      
      // 检查类型
      if (rule.type) {
        if (Array.isArray(rule.type)) {
          if (!rule.type.includes(typeof value)) {
            errors.push(`字段 ${field} 类型错误，期望 ${rule.type.join(' 或 ')}，实际 ${typeof value}`);
          }
        } else if (typeof value !== rule.type) {
          errors.push(`字段 ${field} 类型错误，期望 ${rule.type}，实际 ${typeof value}`);
        }
      }
      
      // 检查模式
      if (rule.pattern && typeof value === 'string' && !rule.pattern.test(value)) {
        errors.push(`字段 ${field} 格式错误: ${rule.description}`);
      }
      
      // 检查长度
      if (rule.maxLength && typeof value === 'string' && value.length > rule.maxLength) {
        errors.push(`字段 ${field} 长度超过限制，最大 ${rule.maxLength} 个字符`);
      }
    });
    
    // 特殊验证
    this.validateSpecialFields(packageJson, errors, warnings);
    
    return { errors, warnings };
  }
  
  validateSpecialFields(packageJson, errors, warnings) {
    // 验证名称不以点或下划线开头
    if (packageJson.name && /^[._]/.test(packageJson.name)) {
      errors.push("包名不能以点或下划线开头");
    }
    
    // 验证名称不是Node.js核心模块
    const coreModules = ['http', 'https', 'fs', 'path', 'os', 'events', 'stream', 'util', 'url', 'querystring'];
    if (packageJson.name && coreModules.includes(packageJson.name)) {
      errors.push(`包名不能是Node.js核心模块名: ${packageJson.name}`);
    }
    
    // 验证依赖版本
    if (packageJson.dependencies) {
      Object.entries(packageJson.dependencies).forEach(([name, version]) => {
        if (typeof version !== 'string') {
          errors.push(`依赖 ${name} 的版本必须是字符串`);
        }
      });
    }
    
    // 验证脚本
    if (packageJson.scripts) {
      Object.entries(packageJson.scripts).forEach(([name, command]) => {
        if (typeof command !== 'string') {
          errors.push(`脚本 ${name} 的命令必须是字符串`);
        }
      });
    }
    
    // 检查是否有私有标记但没有发布相关配置
    if (packageJson.private === true && packageJson.publishConfig) {
      warnings.push("私有包不需要发布配置");
    }
  }
}

const validator = new PackageJsonValidator();
const validationResults = validator.validate(packageJson || {});

console.log("验证结果:");
if (validationResults.errors.length > 0) {
  console.log("错误:");
  validationResults.errors.forEach(error => console.log(`  - ${error}`));
}
if (validationResults.warnings.length > 0) {
  console.log("警告:");
  validationResults.warnings.forEach(warning => console.log(`  - ${warning}`));
}
if (validationResults.errors.length === 0 && validationResults.warnings.length === 0) {
  console.log("package.json验证通过!");
}

// 示例8：依赖版本更新检查
console.log("\n=== 示例8：依赖版本更新检查 ===");

function checkDependencyUpdates(packageJson) {
  if (!packageJson.dependencies) return null;
  
  // 模拟获取最新版本
  const latestVersions = {
    express: '4.18.2',
    lodash: '4.17.21',
    moment: '2.29.4',
    axios: '1.4.0',
    react: '18.2.0',
    'react-dom': '18.2.0'
  };
  
  const updates = {
    outdated: [],
    upToDate: []
  };
  
  Object.entries(packageJson.dependencies).forEach(([name, currentVersion]) => {
    const latestVersion = latestVersions[name];
    if (!latestVersion) {
      updates.outdated.push({
        name,
        current: currentVersion,
        latest: '未知',
        status: 'unknown'
      });
      return;
    }
    
    // 简单版本比较（实际应用中应使用semver库）
    const current = currentVersion.replace(/[\^~]/g, '').split('.').map(Number);
    const latest = latestVersion.split('.').map(Number);
    
    let isOutdated = false;
    for (let i = 0; i < 3; i++) {
      if (current[i] < latest[i]) {
        isOutdated = true;
        break;
      } else if (current[i] > latest[i]) {
        break;
      }
    }
    
    if (isOutdated) {
      updates.outdated.push({
        name,
        current: currentVersion,
        latest: latestVersion,
        status: 'outdated'
      });
    } else {
      updates.upToDate.push({
        name,
        current: currentVersion,
        latest: latestVersion,
        status: 'up-to-date'
      });
    }
  });
  
  return updates;
}

if (packageJson && packageJson.dependencies) {
  const updateCheck = checkDependencyUpdates(packageJson);
  if (updateCheck) {
    console.log("依赖更新检查结果:");
    
    if (updateCheck.outdated.length > 0) {
      console.log("\n过时的依赖:");
      updateCheck.outdated.forEach(dep => {
        console.log(`  - ${dep.name}: ${dep.current} → ${dep.latest}`);
      });
    }
    
    if (updateCheck.upToDate.length > 0) {
      console.log("\n最新的依赖:");
      updateCheck.upToDate.forEach(dep => {
        console.log(`  - ${dep.name}: ${dep.current} (最新)`);
      });
    }
  }
}

// 示例9：package.json生成器
console.log("\n=== 示例9：package.json生成器 ===");

class PackageJsonGenerator {
  constructor() {
    this.template = {
      name: '',
      version: '1.0.0',
      description: '',
      main: 'index.js',
      scripts: {
        start: 'node index.js',
        test: 'echo \"Error: no test specified\" && exit 1'
      },
      keywords: [],
      author: '',
      license: 'ISC',
      dependencies: {},
      devDependencies: {}
    };
  }
  
  setName(name) {
    this.template.name = name;
    return this;
  }
  
  setDescription(description) {
    this.template.description = description;
    return this;
  }
  
  setMain(main) {
    this.template.main = main;
    return this;
  }
  
  setAuthor(author) {
    this.template.author = author;
    return this;
  }
  
  setLicense(license) {
    this.template.license = license;
    return this;
  }
  
  addScript(name, command) {
    this.template.scripts[name] = command;
    return this;
  }
  
  addKeyword(keyword) {
    if (!this.template.keywords.includes(keyword)) {
      this.template.keywords.push(keyword);
    }
    return this;
  }
  
  addDependency(name, version) {
    this.template.dependencies[name] = version;
    return this;
  }
  
  addDevDependency(name, version) {
    this.template.devDependencies[name] = version;
    return this;
  }
  
  setPrivate(isPrivate) {
    if (isPrivate) {
      this.template.private = true;
    } else {
      delete this.template.private;
    }
    return this;
  }
  
  generate() {
    // 移除空的关键词数组
    if (this.template.keywords.length === 0) {
      delete this.template.keywords;
    }
    
    // 移除空的依赖对象
    if (Object.keys(this.template.dependencies).length === 0) {
      delete this.template.dependencies;
    }
    
    if (Object.keys(this.template.devDependencies).length === 0) {
      delete this.template.devDependencies;
    }
    
    return JSON.stringify(this.template, null, 2);
  }
  
  save(filePath) {
    const content = this.generate();
    fs.writeFileSync(filePath, content, 'utf8');
    return this;
  }
}

// 使用生成器创建package.json
const generator = new PackageJsonGenerator();
const packageJsonContent = generator
  .setName('my-generated-project')
  .setDescription('使用生成器创建的项目')
  .setMain('src/index.js')
  .setAuthor('Generated User <user@example.com>')
  .setLicense('MIT')
  .addScript('dev', 'nodemon src/index.js')
  .addScript('build', 'webpack --mode production')
  .addKeyword('generated')
  .addKeyword('example')
  .addDependency('express', '^4.18.2')
  .addDependency('lodash', '^4.17.21')
  .addDevDependency('nodemon', '^3.0.1')
  .addDevDependency('webpack', '^5.88.2')
  .setPrivate(true)
  .generate();

console.log("生成的package.json:");
console.log(packageJsonContent);

// 示例10：package.json比较工具
console.log("\n=== 示例10：package.json比较工具 ===");

function comparePackageJson(package1, package2) {
  const comparison = {
    added: {},
    removed: {},
    updated: {},
    unchanged: {}
  };
  
  // 比较所有可能的字段
  const allFields = new Set([
    ...Object.keys(package1 || {}),
    ...Object.keys(package2 || {})
  ]);
  
  allFields.forEach(field => {
    const value1 = package1 ? package1[field] : undefined;
    const value2 = package2 ? package2[field] : undefined;
    
    if (value1 === undefined && value2 !== undefined) {
      comparison.added[field] = value2;
    } else if (value1 !== undefined && value2 === undefined) {
      comparison.removed[field] = value1;
    } else if (JSON.stringify(value1) !== JSON.stringify(value2)) {
      comparison.updated[field] = {
        old: value1,
        new: value2
      };
    } else {
      comparison.unchanged[field] = value1;
    }
  });
  
  return comparison;
}

// 创建两个package.json进行比较
const packageJson1 = {
  name: "my-project",
  version: "1.0.0",
  description: "我的项目",
  main: "index.js",
  scripts: {
    start: "node index.js",
    test: "jest"
  },
  dependencies: {
    express: "^4.17.0",
    lodash: "^4.16.0"
  },
  devDependencies: {
    jest: "^26.0.0"
  }
};

const packageJson2 = {
  name: "my-project",
  version: "1.1.0",
  description: "我的项目（更新版）",
  main: "src/index.js",
  scripts: {
    start: "node src/index.js",
    test: "jest",
    build: "webpack --mode production"
  },
  dependencies: {
    express: "^4.18.2",
    lodash: "^4.17.21",
    axios: "^1.4.0"
  },
  devDependencies: {
    jest: "^29.6.1",
    eslint: "^8.45.0"
  },
  keywords: ["updated", "project"]
};

const comparison = comparePackageJson(packageJson1, packageJson2);

console.log("package.json比较结果:");

if (Object.keys(comparison.added).length > 0) {
  console.log("\n新增字段:");
  Object.entries(comparison.added).forEach(([field, value]) => {
    console.log(`  ${field}: ${JSON.stringify(value)}`);
  });
}

if (Object.keys(comparison.removed).length > 0) {
  console.log("\n删除字段:");
  Object.entries(comparison.removed).forEach(([field, value]) => {
    console.log(`  ${field}: ${JSON.stringify(value)}`);
  });
}

if (Object.keys(comparison.updated).length > 0) {
  console.log("\n更新字段:");
  Object.entries(comparison.updated).forEach(([field, change]) => {
    console.log(`  ${field}:`);
    console.log(`    旧值: ${JSON.stringify(change.old)}`);
    console.log(`    新值: ${JSON.stringify(change.new)}`);
  });
}

if (Object.keys(comparison.unchanged).length > 0) {
  console.log("\n未变字段:");
  Object.keys(comparison.unchanged).forEach(field => {
    console.log(`  ${field}`);
  });
}

console.log("\n=== 第3章示例代码结束 ===");