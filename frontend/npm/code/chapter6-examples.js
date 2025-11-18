// NPM高级配置与优化 - 代码示例

// 示例1：解析.npmrc配置文件
const fs = require('fs');
const path = require('path');

function parseNpmrc(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const config = {};
    
    content.split('\n').forEach(line => {
      // 忽略注释和空行
      if (line.trim() && !line.trim().startsWith('#')) {
        const [key, ...valueParts] = line.split('=');
        if (key && valueParts.length > 0) {
          config[key.trim()] = valueParts.join('=').trim();
        }
      }
    });
    
    return config;
  } catch (error) {
    console.error(`解析.npmrc文件失败: ${error.message}`);
    return {};
  }
}

// 示例2：NPM缓存管理
const { execSync } = require('child_process');

class NpmCacheManager {
  constructor() {
    this.cacheDir = this.getCacheDir();
  }
  
  getCacheDir() {
    try {
      return execSync('npm config get cache', { encoding: 'utf8' }).trim();
    } catch (error) {
      console.error('获取缓存目录失败:', error.message);
      return path.join(process.env.HOME || process.env.USERPROFILE, '.npm');
    }
  }
  
  getCacheSize() {
    try {
      const result = execSync('npm cache verify', { encoding: 'utf8' });
      // 解析输出获取缓存大小
      const match = result.match(/Cache verified and compressed \(([\d.]+) [KMGT]?B\)/);
      return match ? match[1] : '未知';
    } catch (error) {
      console.error('获取缓存大小失败:', error.message);
      return '未知';
    }
  }
  
  cleanCache() {
    try {
      console.log('正在清理NPM缓存...');
      execSync('npm cache clean --force', { stdio: 'inherit' });
      console.log('缓存清理完成');
      return true;
    } catch (error) {
      console.error('清理缓存失败:', error.message);
      return false;
    }
  }
  
  verifyCache() {
    try {
      console.log('正在验证NPM缓存...');
      execSync('npm cache verify', { stdio: 'inherit' });
      console.log('缓存验证完成');
      return true;
    } catch (error) {
      console.error('验证缓存失败:', error.message);
      return false;
    }
  }
}

// 示例3：NPM镜像源管理
class NpmRegistryManager {
  constructor() {
    this.currentRegistry = this.getCurrentRegistry();
  }
  
  getCurrentRegistry() {
    try {
      return execSync('npm config get registry', { encoding: 'utf8' }).trim();
    } catch (error) {
      console.error('获取当前镜像源失败:', error.message);
      return 'https://registry.npmjs.org/';
    }
  }
  
  setRegistry(registryUrl) {
    try {
      execSync(`npm config set registry ${registryUrl}`, { stdio: 'inherit' });
      this.currentRegistry = registryUrl;
      console.log(`镜像源已设置为: ${registryUrl}`);
      return true;
    } catch (error) {
      console.error('设置镜像源失败:', error.message);
      return false;
    }
  }
  
  testRegistrySpeed(registryUrl) {
    return new Promise((resolve) => {
      const startTime = Date.now();
      
      // 使用ping命令测试延迟
      const { spawn } = require('child_process');
      const ping = spawn('ping', ['-n', '1', new URL(registryUrl).hostname]);
      
      ping.on('close', (code) => {
        const endTime = Date.now();
        const responseTime = endTime - startTime;
        
        resolve({
          registry: registryUrl,
          success: code === 0,
          responseTime: responseTime
        });
      });
    });
  }
  
  async compareRegistries(registries) {
    console.log('正在测试镜像源速度...');
    const results = [];
    
    for (const registry of registries) {
      const result = await this.testRegistrySpeed(registry);
      results.push(result);
    }
    
    // 按响应时间排序
    results.sort((a, b) => a.responseTime - b.responseTime);
    
    console.log('镜像源速度测试结果:');
    results.forEach((result, index) => {
      console.log(`${index + 1}. ${result.registry}: ${result.responseTime}ms`);
    });
    
    return results;
  }
}

// 示例4：NPM工作区管理
class NpmWorkspaceManager {
  constructor(rootPath) {
    this.rootPath = rootPath;
    this.packageJsonPath = path.join(rootPath, 'package.json');
    this.workspaces = [];
    this.loadWorkspaces();
  }
  
  loadWorkspaces() {
    try {
      const packageJson = JSON.parse(fs.readFileSync(this.packageJsonPath, 'utf8'));
      
      if (packageJson.workspaces) {
        this.workspaces = packageJson.workspaces.map(pattern => {
          return {
            pattern,
            packages: this.resolveWorkspacePackages(pattern)
          };
        });
      }
    } catch (error) {
      console.error('加载工作区配置失败:', error.message);
    }
  }
  
  resolveWorkspacePackages(pattern) {
    const glob = require('glob');
    const packages = [];
    
    try {
      const paths = glob.sync(pattern, { cwd: this.rootPath });
      
      paths.forEach(pkgPath => {
        const fullPath = path.join(this.rootPath, pkgPath);
        const packageJsonPath = path.join(fullPath, 'package.json');
        
        if (fs.existsSync(packageJsonPath)) {
          try {
            const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
            packages.push({
              name: packageJson.name,
              path: fullPath,
              packageJson
            });
          } catch (error) {
            console.error(`解析 ${packageJsonPath} 失败:`, error.message);
          }
        }
      });
    } catch (error) {
      console.error(`解析工作区模式 ${pattern} 失败:`, error.message);
    }
    
    return packages;
  }
  
  getWorkspaceGraph() {
    const graph = {};
    
    this.workspaces.forEach(workspace => {
      workspace.packages.forEach(pkg => {
        graph[pkg.name] = {
          name: pkg.name,
          path: pkg.path,
          dependencies: {},
          devDependencies: {}
        };
        
        if (pkg.packageJson.dependencies) {
          graph[pkg.name].dependencies = pkg.packageJson.dependencies;
        }
        
        if (pkg.packageJson.devDependencies) {
          graph[pkg.name].devDependencies = pkg.packageJson.devDependencies;
        }
      });
    });
    
    return graph;
  }
  
  getDependencyOrder() {
    const graph = this.getWorkspaceGraph();
    const visited = {};
    const result = [];
    
    function visit(name) {
      if (visited[name]) return;
      visited[name] = true;
      
      const dependencies = Object.keys(graph[name].dependencies);
      dependencies.forEach(dep => {
        if (graph[dep]) {
          visit(dep);
        }
      });
      
      result.push(name);
    }
    
    Object.keys(graph).forEach(name => visit(name));
    
    return result;
  }
  
  runScriptInWorkspaces(scriptName, options = {}) {
    const { parallel = false, workspace } = options;
    const { spawn } = require('child_process');
    
    if (workspace) {
      // 在特定工作区运行脚本
      const pkg = this.findWorkspace(workspace);
      if (pkg) {
        console.log(`在 ${workspace} 中运行脚本: ${scriptName}`);
        return this.runScriptInPackage(pkg, scriptName);
      } else {
        console.error(`找不到工作区: ${workspace}`);
        return false;
      }
    } else {
      // 在所有工作区运行脚本
      const dependencyOrder = this.getDependencyOrder();
      
      if (parallel) {
        console.log(`并行在所有工作区中运行脚本: ${scriptName}`);
        const promises = dependencyOrder.map(name => {
          const pkg = this.findWorkspaceByName(name);
          return this.runScriptInPackage(pkg, scriptName);
        });
        return Promise.all(promises);
      } else {
        console.log(`按依赖顺序在所有工作区中运行脚本: ${scriptName}`);
        return dependencyOrder.reduce((promise, name) => {
          return promise.then(() => {
            const pkg = this.findWorkspaceByName(name);
            return this.runScriptInPackage(pkg, scriptName);
          });
        }, Promise.resolve());
      }
    }
  }
  
  findWorkspace(workspaceName) {
    for (const workspace of this.workspaces) {
      for (const pkg of workspace.packages) {
        if (pkg.name === workspaceName || pkg.path.includes(workspaceName)) {
          return pkg;
        }
      }
    }
    return null;
  }
  
  findWorkspaceByName(name) {
    for (const workspace of this.workspaces) {
      for (const pkg of workspace.packages) {
        if (pkg.name === name) {
          return pkg;
        }
      }
    }
    return null;
  }
  
  runScriptInPackage(pkg, scriptName) {
    return new Promise((resolve, reject) => {
      if (!pkg.packageJson.scripts || !pkg.packageJson.scripts[scriptName]) {
        console.warn(`${pkg.name} 没有脚本: ${scriptName}`);
        resolve();
        return;
      }
      
      console.log(`在 ${pkg.name} 中运行脚本: ${scriptName}`);
      
      const npm = spawn('npm', ['run', scriptName], {
        cwd: pkg.path,
        stdio: 'inherit'
      });
      
      npm.on('close', (code) => {
        if (code === 0) {
          console.log(`${pkg.name} 中的脚本 ${scriptName} 执行成功`);
          resolve();
        } else {
          console.error(`${pkg.name} 中的脚本 ${scriptName} 执行失败，退出码: ${code}`);
          reject(new Error(`Script execution failed with code ${code}`));
        }
      });
    });
  }
}

// 示例5：NPM脚本管理
class NpmScriptManager {
  constructor(packageJsonPath) {
    this.packageJsonPath = packageJsonPath;
    this.packageJson = this.loadPackageJson();
  }
  
  loadPackageJson() {
    try {
      return JSON.parse(fs.readFileSync(this.packageJsonPath, 'utf8'));
    } catch (error) {
      console.error('加载package.json失败:', error.message);
      return { scripts: {} };
    }
  }
  
  savePackageJson() {
    try {
      fs.writeFileSync(this.packageJsonPath, JSON.stringify(this.packageJson, null, 2));
      return true;
    } catch (error) {
      console.error('保存package.json失败:', error.message);
      return false;
    }
  }
  
  addScript(name, command) {
    if (!this.packageJson.scripts) {
      this.packageJson.scripts = {};
    }
    
    this.packageJson.scripts[name] = command;
    return this.savePackageJson();
  }
  
  removeScript(name) {
    if (this.packageJson.scripts && this.packageJson.scripts[name]) {
      delete this.packageJson.scripts[name];
      return this.savePackageJson();
    }
    return false;
  }
  
  getScript(name) {
    return this.packageJson.scripts && this.packageJson.scripts[name];
  }
  
  getAllScripts() {
    return this.packageJson.scripts || {};
  }
  
  analyzeScriptDependencies() {
    const scripts = this.getAllScripts();
    const dependencyGraph = {};
    
    // 简单的依赖分析，查找脚本中调用的其他脚本
    Object.keys(scripts).forEach(scriptName => {
      const command = scripts[scriptName];
      const dependencies = [];
      
      // 查找 "npm run" 调用
      const npmRunMatches = command.match(/npm run ([\w-]+)/g);
      if (npmRunMatches) {
        npmRunMatches.forEach(match => {
          const depScript = match.replace('npm run ', '');
          if (scripts[depScript]) {
            dependencies.push(depScript);
          }
        });
      }
      
      dependencyGraph[scriptName] = {
        command,
        dependencies
      };
    });
    
    return dependencyGraph;
  }
  
  getExecutionOrder(scriptName) {
    const dependencyGraph = this.analyzeScriptDependencies();
    const visited = {};
    const result = [];
    
    function visit(name) {
      if (visited[name]) return;
      visited[name] = true;
      
      if (dependencyGraph[name]) {
        dependencyGraph[name].dependencies.forEach(dep => {
          visit(dep);
        });
      }
      
      result.push(name);
    }
    
    visit(scriptName);
    return result;
  }
  
  runScript(scriptName, args = []) {
    const { spawn } = require('child_process');
    
    return new Promise((resolve, reject) => {
      const command = this.getScript(scriptName);
      if (!command) {
        reject(new Error(`脚本 ${scriptName} 不存在`));
        return;
      }
      
      console.log(`运行脚本: ${scriptName}`);
      console.log(`命令: ${command}`);
      
      // 解析命令和参数
      const [cmd, ...cmdArgs] = command.split(' ');
      const fullArgs = [...cmdArgs, ...args];
      
      const child = spawn(cmd, fullArgs, {
        stdio: 'inherit',
        shell: true
      });
      
      child.on('close', (code) => {
        if (code === 0) {
          console.log(`脚本 ${scriptName} 执行成功`);
          resolve();
        } else {
          console.error(`脚本 ${scriptName} 执行失败，退出码: ${code}`);
          reject(new Error(`Script execution failed with code ${code}`));
        }
      });
    });
  }
}

// 示例6：NPM版本管理
class NpmVersionManager {
  constructor(packageJsonPath) {
    this.packageJsonPath = packageJsonPath;
    this.packageJson = this.loadPackageJson();
  }
  
  loadPackageJson() {
    try {
      return JSON.parse(fs.readFileSync(this.packageJsonPath, 'utf8'));
    } catch (error) {
      console.error('加载package.json失败:', error.message);
      return { version: '1.0.0' };
    }
  }
  
  savePackageJson() {
    try {
      fs.writeFileSync(this.packageJsonPath, JSON.stringify(this.packageJson, null, 2));
      return true;
    } catch (error) {
      console.error('保存package.json失败:', error.message);
      return false;
    }
  }
  
  getCurrentVersion() {
    return this.packageJson.version || '1.0.0';
  }
  
  bumpVersion(type) {
    const currentVersion = this.getCurrentVersion();
    const [major, minor, patch] = currentVersion.split('.').map(Number);
    
    let newVersion;
    
    switch (type) {
      case 'major':
        newVersion = `${major + 1}.0.0`;
        break;
      case 'minor':
        newVersion = `${major}.${minor + 1}.0`;
        break;
      case 'patch':
        newVersion = `${major}.${minor}.${patch + 1}`;
        break;
      default:
        throw new Error(`无效的版本类型: ${type}，请使用 major、minor 或 patch`);
    }
    
    this.packageJson.version = newVersion;
    this.savePackageJson();
    
    console.log(`版本已从 ${currentVersion} 更新到 ${newVersion}`);
    return newVersion;
  }
  
  setVersion(version) {
    if (!this.isValidVersion(version)) {
      throw new Error(`无效的版本格式: ${version}`);
    }
    
    const currentVersion = this.getCurrentVersion();
    this.packageJson.version = version;
    this.savePackageJson();
    
    console.log(`版本已从 ${currentVersion} 设置为 ${version}`);
    return version;
  }
  
  isValidVersion(version) {
    return /^\d+\.\d+\.\d+(-[\w.]+)?$/.test(version);
  }
  
  compareVersions(v1, v2) {
    const normalize = (v) => {
      const [main, pre] = v.split('-');
      const parts = main.split('.').map(Number);
      return { parts, pre: pre || '' };
    };
    
    const n1 = normalize(v1);
    const n2 = normalize(v2);
    
    // 比较主版本号
    for (let i = 0; i < 3; i++) {
      if (n1.parts[i] > n2.parts[i]) return 1;
      if (n1.parts[i] < n2.parts[i]) return -1;
    }
    
    // 比较预发布版本
    if (n1.pre && !n2.pre) return -1;
    if (!n1.pre && n2.pre) return 1;
    if (n1.pre < n2.pre) return -1;
    if (n1.pre > n2.pre) return 1;
    
    return 0;
  }
  
  isVersionInRange(version, range) {
    // 简化版的版本范围检查
    if (range.startsWith('^')) {
      const minVersion = range.substring(1);
      const [minMajor, minMinor] = minVersion.split('.').map(Number);
      const [major, minor] = version.split('.').map(Number);
      
      // ^1.2.3 匹配 >=1.2.3 且 <2.0.0
      if (major > minMajor) return false;
      if (major === minMajor && minor < minMinor) return false;
      
      return this.compareVersions(version, minVersion) >= 0;
    } else if (range.startsWith('~')) {
      const minVersion = range.substring(1);
      const [minMajor, minMinor] = minVersion.split('.').map(Number);
      const [major, minor] = version.split('.').map(Number);
      
      // ~1.2.3 匹配 >=1.2.3 且 <1.3.0
      if (major !== minMajor) return false;
      if (minor < minMinor) return false;
      
      return this.compareVersions(version, minVersion) >= 0;
    } else if (range.includes(' - ')) {
      // 范围如 "1.2.3 - 2.3.4"
      const [min, max] = range.split(' - ').map(v => v.trim());
      return this.compareVersions(version, min) >= 0 && this.compareVersions(version, max) <= 0;
    } else if (range.includes('||')) {
      // 多个范围，如 "1.2.3 || 2.3.4"
      return range.split('||').some(r => this.isVersionInRange(version, r.trim()));
    } else {
      // 精确匹配
      return version === range;
    }
  }
}

// 示例7：NPM发布管理
class NpmPublishManager {
  constructor(packageJsonPath) {
    this.packageJsonPath = packageJsonPath;
    this.packageJson = this.loadPackageJson();
  }
  
  loadPackageJson() {
    try {
      return JSON.parse(fs.readFileSync(this.packageJsonPath, 'utf8'));
    } catch (error) {
      console.error('加载package.json失败:', error.message);
      return {};
    }
  }
  
  validatePackage() {
    const errors = [];
    
    // 检查必需字段
    if (!this.packageJson.name) {
      errors.push('缺少name字段');
    }
    
    if (!this.packageJson.version) {
      errors.push('缺少version字段');
    }
    
    // 检查包名格式
    if (this.packageJson.name && !/^[a-z0-9-_]+$/.test(this.packageJson.name)) {
      errors.push('包名只能包含小写字母、数字、连字符和下划线');
    }
    
    // 检查版本格式
    if (this.packageJson.version && !/^\d+\.\d+\.\d+/.test(this.packageJson.version)) {
      errors.push('版本号格式不正确，应为x.y.z');
    }
    
    // 检查是否有main字段（对于库）
    if (this.packageJson.main && !fs.existsSync(path.join(path.dirname(this.packageJsonPath), this.packageJson.main))) {
      errors.push(`main字段指定的文件不存在: ${this.packageJson.main}`);
    }
    
    return {
      valid: errors.length === 0,
      errors
    };
  }
  
  checkIfPackageExists(packageName, registry = 'https://registry.npmjs.org/') {
    const https = require('https');
    const url = new URL(packageName, registry);
    
    return new Promise((resolve) => {
      const request = https.request(url, (response) => {
        resolve(response.statusCode !== 404);
      });
      
      request.on('error', () => {
        resolve(false);
      });
      
      request.end();
    });
  }
  
  async publish(options = {}) {
    const { 
      registry = 'https://registry.npmjs.org/', 
      tag = 'latest',
      access = 'public',
      dryRun = false 
    } = options;
    
    // 验证包
    const validation = this.validatePackage();
    if (!validation.valid) {
      console.error('包验证失败:');
      validation.errors.forEach(error => console.error(`- ${error}`));
      return false;
    }
    
    // 检查包是否已存在
    const packageName = this.packageJson.name;
    const exists = await this.checkIfPackageExists(packageName, registry);
    
    if (exists) {
      console.warn(`包 ${packageName} 已存在于注册表中`);
    }
    
    // 构建发布命令
    const publishArgs = ['publish'];
    
    if (registry !== 'https://registry.npmjs.org/') {
      publishArgs.push(`--registry=${registry}`);
    }
    
    publishArgs.push(`--tag=${tag}`);
    publishArgs.push(`--access=${access}`);
    
    if (dryRun) {
      publishArgs.push('--dry-run');
    }
    
    console.log(`发布命令: npm ${publishArgs.join(' ')}`);
    
    if (!dryRun) {
      const { spawn } = require('child_process');
      
      return new Promise((resolve, reject) => {
        const publish = spawn('npm', publishArgs, {
          cwd: path.dirname(this.packageJsonPath),
          stdio: 'inherit'
        });
        
        publish.on('close', (code) => {
          if (code === 0) {
            console.log(`包 ${packageName} 发布成功`);
            resolve(true);
          } else {
            console.error(`包 ${packageName} 发布失败，退出码: ${code}`);
            reject(new Error(`Publish failed with code ${code}`));
          }
        });
      });
    } else {
      console.log('这是试运行，包未被实际发布');
      return true;
    }
  }
}

// 示例8：NPM依赖分析
class NpmDependencyAnalyzer {
  constructor(packageJsonPath) {
    this.packageJsonPath = packageJsonPath;
    this.packageJson = this.loadPackageJson();
  }
  
  loadPackageJson() {
    try {
      return JSON.parse(fs.readFileSync(this.packageJsonPath, 'utf8'));
    } catch (error) {
      console.error('加载package.json失败:', error.message);
      return { dependencies: {}, devDependencies: {} };
    }
  }
  
  getAllDependencies() {
    const dependencies = this.packageJson.dependencies || {};
    const devDependencies = this.packageJson.devDependencies || {};
    const peerDependencies = this.packageJson.peerDependencies || {};
    const optionalDependencies = this.packageJson.optionalDependencies || {};
    
    return {
      dependencies,
      devDependencies,
      peerDependencies,
      optionalDependencies
    };
  }
  
  analyzeDependencyTypes() {
    const allDeps = this.getAllDependencies();
    const result = {
      production: Object.keys(allDeps.dependencies).length,
      development: Object.keys(allDeps.devDependencies).length,
      peer: Object.keys(allDeps.peerDependencies).length,
      optional: Object.keys(allDeps.optionalDependencies).length,
      total: 0
    };
    
    result.total = result.production + result.development + result.peer + result.optional;
    
    return result;
  }
  
  findOutdatedDependencies() {
    const { execSync } = require('child_process');
    
    try {
      const outdated = execSync('npm outdated --json', { 
        encoding: 'utf8',
        cwd: path.dirname(this.packageJsonPath)
      });
      
      return JSON.parse(outdated);
    } catch (error) {
      // npm outdated 在有过期包时会返回非零退出码
      try {
        return JSON.parse(error.stdout);
      } catch (parseError) {
        console.error('解析过期依赖信息失败:', parseError.message);
        return {};
      }
    }
  }
  
  findSecurityVulnerabilities() {
    const { execSync } = require('child_process');
    
    try {
      const audit = execSync('npm audit --json', { 
        encoding: 'utf8',
        cwd: path.dirname(this.packageJsonPath)
      });
      
      return JSON.parse(audit);
    } catch (error) {
      console.error('执行安全审计失败:', error.message);
      return { vulnerabilities: {} };
    }
  }
  
  generateDependencyReport() {
    const depTypes = this.analyzeDependencyTypes();
    const outdated = this.findOutdatedDependencies();
    const vulnerabilities = this.findSecurityVulnerabilities();
    
    const report = {
      summary: {
        totalDependencies: depTypes.total,
        productionDependencies: depTypes.production,
        developmentDependencies: depTypes.development,
        peerDependencies: depTypes.peer,
        optionalDependencies: depTypes.optional
      },
      outdated: Object.keys(outdated).length,
      vulnerabilities: Object.keys(vulnerabilities.vulnerabilities || {}).length,
      recommendations: []
    };
    
    // 生成建议
    if (report.outdated > 0) {
      report.recommendations.push(`发现 ${report.outdated} 个过期的依赖，建议更新`);
    }
    
    if (report.vulnerabilities > 0) {
      report.recommendations.push(`发现 ${report.vulnerabilities} 个安全漏洞，建议修复`);
    }
    
    if (depTypes.development > depTypes.production * 2) {
      report.recommendations.push('开发依赖数量较多，考虑是否有些依赖可以移至生产依赖');
    }
    
    return report;
  }
}

// 示例9：NPM配置优化建议
class NpmOptimizer {
  constructor(packageJsonPath) {
    this.packageJsonPath = packageJsonPath;
    this.packageJson = this.loadPackageJson();
  }
  
  loadPackageJson() {
    try {
      return JSON.parse(fs.readFileSync(this.packageJsonPath, 'utf8'));
    } catch (error) {
      console.error('加载package.json失败:', error.message);
      return {};
    }
  }
  
  analyzeScripts() {
    const scripts = this.packageJson.scripts || {};
    const recommendations = [];
    
    // 检查是否有预提交钩子
    if (!scripts.prepare && !scripts.precommit) {
      recommendations.push({
        type: 'scripts',
        message: '考虑添加prepare或precommit脚本以自动化代码质量检查',
        example: '"prepare": "husky install"'
      });
    }
    
    // 检查是否有构建脚本
    if (!scripts.build) {
      recommendations.push({
        type: 'scripts',
        message: '建议添加build脚本以构建生产版本',
        example: '"build": "webpack --mode=production"'
      });
    }
    
    // 检查是否有测试脚本
    if (!scripts.test) {
      recommendations.push({
        type: 'scripts',
        message: '建议添加test脚本以运行测试',
        example: '"test": "jest"'
      });
    }
    
    // 检查是否有开发服务器
    if (!scripts.start && !scripts.dev) {
      recommendations.push({
        type: 'scripts',
        message: '建议添加start或dev脚本以启动开发服务器',
        example: '"start": "webpack serve --mode=development"'
      });
    }
    
    return recommendations;
  }
  
  analyzeDependencies() {
    const dependencies = this.packageJson.dependencies || {};
    const devDependencies = this.packageJson.devDependencies || {};
    const recommendations = [];
    
    // 检查是否有常用的开发依赖
    const commonDevDeps = [
      'eslint', 'prettier', 'jest', 'webpack', 'babel', 'typescript'
    ];
    
    commonDevDeps.forEach(dep => {
      if (dependencies[dep]) {
        recommendations.push({
          type: 'dependencies',
          message: `${dep} 应该是开发依赖而不是生产依赖`,
          action: `将 ${dep} 从 dependencies 移至 devDependencies`
        });
      }
    });
    
    // 检查是否有重复的依赖
    const allDeps = { ...dependencies, ...devDependencies };
    const duplicates = Object.keys(allDeps).filter(dep => 
      dependencies[dep] && devDependencies[dep]
    );
    
    if (duplicates.length > 0) {
      recommendations.push({
        type: 'dependencies',
        message: `发现重复的依赖: ${duplicates.join(', ')}`,
        action: '确保每个依赖只存在于一个依赖类别中'
      });
    }
    
    return recommendations;
  }
  
  analyzePackageFields() {
    const recommendations = [];
    
    // 检查是否有描述
    if (!this.packageJson.description) {
      recommendations.push({
        type: 'metadata',
        message: '建议添加description字段以描述包的用途',
        example: '"description": "一个有用的JavaScript库"'
      });
    }
    
    // 检查是否有关键词
    if (!this.packageJson.keywords || this.packageJson.keywords.length === 0) {
      recommendations.push({
        type: 'metadata',
        message: '建议添加keywords字段以提高包的可发现性',
        example: '"keywords": ["javascript", "utility", "library"]'
      });
    }
    
    // 检查是否有仓库信息
    if (!this.packageJson.repository) {
      recommendations.push({
        type: 'metadata',
        message: '建议添加repository字段以指向源代码仓库',
        example: '"repository": "github:username/repo"'
      });
    }
    
    // 检查是否有许可证
    if (!this.packageJson.license) {
      recommendations.push({
        type: 'metadata',
        message: '建议添加license字段以明确许可证',
        example: '"license": "MIT"'
      });
    }
    
    // 检查是否有作者信息
    if (!this.packageJson.author) {
      recommendations.push({
        type: 'metadata',
        message: '建议添加author字段以标识作者',
        example: '"author": "Your Name <your.email@example.com>"'
      });
    }
    
    // 检查是否有主页
    if (!this.packageJson.homepage) {
      recommendations.push({
        type: 'metadata',
        message: '建议添加homepage字段以指向项目主页',
        example: '"homepage": "https://yourproject.com"'
      });
    }
    
    return recommendations;
  }
  
  generateOptimizationReport() {
    const scriptRecommendations = this.analyzeScripts();
    const dependencyRecommendations = this.analyzeDependencies();
    const fieldRecommendations = this.analyzePackageFields();
    
    const report = {
      package: this.packageJson.name || '未知',
      version: this.packageJson.version || '0.0.0',
      recommendations: [
        ...scriptRecommendations,
        ...dependencyRecommendations,
        ...fieldRecommendations
      ],
      summary: {
        total: scriptRecommendations.length + dependencyRecommendations.length + fieldRecommendations.length,
        scripts: scriptRecommendations.length,
        dependencies: dependencyRecommendations.length,
        metadata: fieldRecommendations.length
      }
    };
    
    return report;
  }
}

// 示例10：NPM最佳实践检查器
class NpmBestPracticesChecker {
  constructor(packageJsonPath) {
    this.packageJsonPath = packageJsonPath;
    this.packageJson = this.loadPackageJson();
  }
  
  loadPackageJson() {
    try {
      return JSON.parse(fs.readFileSync(this.packageJsonPath, 'utf8'));
    } catch (error) {
      console.error('加载package.json失败:', error.message);
      return {};
    }
  }
  
  checkVersioning() {
    const checks = [];
    const version = this.packageJson.version;
    
    if (!version) {
      checks.push({
        check: 'version-exists',
        status: 'fail',
        message: '缺少version字段'
      });
    } else if (!/^\d+\.\d+\.\d+/.test(version)) {
      checks.push({
        check: 'version-format',
        status: 'fail',
        message: '版本号格式不正确，应为语义化版本x.y.z'
      });
    } else {
      checks.push({
        check: 'version-format',
        status: 'pass',
        message: '版本号格式正确'
      });
    }
    
    return checks;
  }
  
  checkDependencies() {
    const checks = [];
    const dependencies = this.packageJson.dependencies || {};
    const devDependencies = this.packageJson.devDependencies || {};
    
    // 检查是否有未指定版本的依赖
    const unspecifiedVersions = [
      ...Object.keys(dependencies).filter(dep => !dependencies[dep]),
      ...Object.keys(devDependencies).filter(dep => !devDependencies[dep])
    ];
    
    if (unspecifiedVersions.length > 0) {
      checks.push({
        check: 'unspecified-versions',
        status: 'fail',
        message: `以下依赖未指定版本: ${unspecifiedVersions.join(', ')}`
      });
    } else {
      checks.push({
        check: 'unspecified-versions',
        status: 'pass',
        message: '所有依赖都指定了版本'
      });
    }
    
    // 检查是否使用了最新版本的依赖
    // 这里简化处理，实际应该调用npm outdated
    checks.push({
      check: 'outdated-dependencies',
      status: 'warning',
      message: '建议定期检查并更新依赖版本'
    });
    
    return checks;
  }
  
  checkScripts() {
    const checks = [];
    const scripts = this.packageJson.scripts || {};
    
    // 检查是否有基本脚本
    const basicScripts = ['start', 'test', 'build'];
    const missingScripts = basicScripts.filter(script => !scripts[script]);
    
    if (missingScripts.length > 0) {
      checks.push({
        check: 'basic-scripts',
        status: 'warning',
        message: `缺少基本脚本: ${missingScripts.join(', ')}`
      });
    } else {
      checks.push({
        check: 'basic-scripts',
        status: 'pass',
        message: '包含所有基本脚本'
      });
    }
    
    // 检查是否有安全相关脚本
    const securityScripts = ['audit', 'lint'];
    const missingSecurityScripts = securityScripts.filter(script => !scripts[script]);
    
    if (missingSecurityScripts.length > 0) {
      checks.push({
        check: 'security-scripts',
        status: 'warning',
        message: `建议添加安全相关脚本: ${missingSecurityScripts.join(', ')}`
      });
    } else {
      checks.push({
        check: 'security-scripts',
        status: 'pass',
        message: '包含安全相关脚本'
      });
    }
    
    return checks;
  }
  
  checkSecurity() {
    const checks = [];
    
    // 检查是否有私有字段
    if (this.packageJson.private !== true) {
      checks.push({
        check: 'private-flag',
        status: 'info',
        message: '如果不是要发布的包，建议设置"private": true'
      });
    } else {
      checks.push({
        check: 'private-flag',
        status: 'pass',
        message: '已设置为私有包'
      });
    }
    
    // 检查是否有引擎限制
    if (!this.packageJson.engines) {
      checks.push({
        check: 'engine-requirements',
        status: 'warning',
        message: '建议添加engines字段以指定Node.js和npm版本要求'
      });
    } else {
      checks.push({
        check: 'engine-requirements',
        status: 'pass',
        message: '已指定引擎版本要求'
      });
    }
    
    return checks;
  }
  
  checkDocumentation() {
    const checks = [];
    
    // 检查是否有README文件
    const readmeExists = fs.existsSync(
      path.join(path.dirname(this.packageJsonPath), 'README.md')
    );
    
    if (readmeExists) {
      checks.push({
        check: 'readme-exists',
        status: 'pass',
        message: '存在README.md文件'
      });
    } else {
      checks.push({
        check: 'readme-exists',
        status: 'fail',
        message: '缺少README.md文件'
      });
    }
    
    // 检查是否有许可证文件
    const licenseExists = fs.existsSync(
      path.join(path.dirname(this.packageJsonPath), 'LICENSE')
    );
    
    if (licenseExists) {
      checks.push({
        check: 'license-file-exists',
        status: 'pass',
        message: '存在LICENSE文件'
      });
    } else {
      checks.push({
        check: 'license-file-exists',
        status: 'warning',
        message: '建议添加LICENSE文件'
      });
    }
    
    return checks;
  }
  
  runAllChecks() {
    const versioningChecks = this.checkVersioning();
    const dependencyChecks = this.checkDependencies();
    const scriptChecks = this.checkScripts();
    const securityChecks = this.checkSecurity();
    const documentationChecks = this.checkDocumentation();
    
    const allChecks = [
      ...versioningChecks,
      ...dependencyChecks,
      ...scriptChecks,
      ...securityChecks,
      ...documentationChecks
    ];
    
    const summary = {
      total: allChecks.length,
      pass: allChecks.filter(check => check.status === 'pass').length,
      fail: allChecks.filter(check => check.status === 'fail').length,
      warning: allChecks.filter(check => check.status === 'warning').length,
      info: allChecks.filter(check => check.status === 'info').length
    };
    
    return {
      package: this.packageJson.name || '未知',
      version: this.packageJson.version || '0.0.0',
      summary,
      checks: allChecks
    };
  }
}

// 导出所有类
module.exports = {
  parseNpmrc,
  NpmCacheManager,
  NpmRegistryManager,
  NpmWorkspaceManager,
  NpmScriptManager,
  NpmVersionManager,
  NpmPublishManager,
  NpmDependencyAnalyzer,
  NpmOptimizer,
  NpmBestPracticesChecker
};

// 使用示例
if (require.main === module) {
  console.log('NPM高级配置与优化示例');
  
  // 示例1：解析.npmrc文件
  console.log('\n1. 解析.npmrc文件:');
  const npmrcPath = path.join(process.env.HOME || process.env.USERPROFILE, '.npmrc');
  const npmrcConfig = parseNpmrc(npmrcPath);
  console.log('当前NPM配置:', npmrcConfig);
  
  // 示例2：NPM缓存管理
  console.log('\n2. NPM缓存管理:');
  const cacheManager = new NpmCacheManager();
  console.log('缓存目录:', cacheManager.cacheDir);
  console.log('缓存大小:', cacheManager.getCacheSize());
  
  // 示例3：NPM镜像源管理
  console.log('\n3. NPM镜像源管理:');
  const registryManager = new NpmRegistryManager();
  console.log('当前镜像源:', registryManager.currentRegistry);
  
  // 示例4：NPM脚本管理
  console.log('\n4. NPM脚本管理:');
  const packageJsonPath = path.join(__dirname, 'package.json');
  const scriptManager = new NpmScriptManager(packageJsonPath);
  console.log('所有脚本:', scriptManager.getAllScripts());
  
  // 示例5：NPM最佳实践检查
  console.log('\n5. NPM最佳实践检查:');
  const bestPracticesChecker = new NpmBestPracticesChecker(packageJsonPath);
  const checkResults = bestPracticesChecker.runAllChecks();
  console.log('检查结果:', checkResults.summary);
}