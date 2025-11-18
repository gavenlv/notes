// NPM性能优化与调试示例代码

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 示例1：NPM性能监控器
class NPMPerformanceMonitor {
  constructor() {
    this.metrics = {
      installTime: 0,
      downloadSpeed: 0,
      cacheHitRate: 0,
      diskUsage: 0,
      networkLatency: 0
    };
  }

  // 监控npm install性能
  monitorInstallPerformance(packageName = '.') {
    console.log(`开始监控安装性能: ${packageName}`);
    
    const startTime = Date.now();
    
    try {
      // 执行npm install并捕获输出
      const output = execSync(`npm install ${packageName} --verbose`, { 
        encoding: 'utf8',
        stdio: 'pipe'
      });
      
      const endTime = Date.now();
      this.metrics.installTime = endTime - startTime;
      
      // 分析输出获取性能指标
      this.analyzeNPMOutput(output);
      
      console.log('安装完成，性能指标:');
      console.log(JSON.stringify(this.metrics, null, 2));
      
      return this.metrics;
    } catch (error) {
      console.error('安装失败:', error.message);
      throw error;
    }
  }

  // 分析NPM输出获取性能指标
  analyzeNPMOutput(output) {
    // 解析下载速度
    const speedMatch = output.match(/speed: ([\d.]+)kB\/s/);
    if (speedMatch) {
      this.metrics.downloadSpeed = parseFloat(speedMatch[1]);
    }
    
    // 解析缓存命中率
    const cacheMatches = output.match(/cache hit: (\d+)/g) || [];
    const totalMatches = output.match(/cache: (\d+)/g) || [];
    
    if (cacheMatches.length > 0 && totalMatches.length > 0) {
      const cacheHits = cacheMatches.reduce((sum, match) => {
        return sum + parseInt(match.match(/cache hit: (\d+)/)[1]);
      }, 0);
      
      const totalCache = totalMatches.reduce((sum, match) => {
        return sum + parseInt(match.match(/cache: (\d+)/)[1]);
      }, 0);
      
      this.metrics.cacheHitRate = totalCache > 0 ? (cacheHits / totalCache) * 100 : 0;
    }
    
    // 解析磁盘使用
    const diskMatch = output.match(/added (\d+) packages in ([\d.]+)s/);
    if (diskMatch) {
      this.metrics.diskUsage = parseInt(diskMatch[1]);
    }
  }

  // 生成性能报告
  generateReport() {
    const report = {
      timestamp: new Date().toISOString(),
      metrics: this.metrics,
      recommendations: this.getRecommendations()
    };
    
    return report;
  }

  // 获取性能优化建议
  getRecommendations() {
    const recommendations = [];
    
    if (this.metrics.installTime > 60000) {
      recommendations.push('安装时间较长，建议使用更快的镜像源或增加并发数');
    }
    
    if (this.metrics.downloadSpeed < 100) {
      recommendations.push('下载速度较慢，建议检查网络连接或使用镜像源');
    }
    
    if (this.metrics.cacheHitRate < 50) {
      recommendations.push('缓存命中率较低，建议优化缓存配置');
    }
    
    return recommendations;
  }
}

// 示例2：NPM缓存优化器
class NPMCacheOptimizer {
  constructor() {
    this.cachePath = this.getCachePath();
    this.cacheConfig = this.getCacheConfig();
  }

  // 获取NPM缓存路径
  getCachePath() {
    try {
      return execSync('npm config get cache', { encoding: 'utf8' }).trim();
    } catch (error) {
      return path.join(os.homedir(), '.npm');
    }
  }

  // 获取缓存配置
  getCacheConfig() {
    try {
      const maxSize = execSync('npm config get cache-max', { encoding: 'utf8' }).trim();
      const minTime = execSync('npm config get cache-min', { encoding: 'utf8' }).trim();
      
      return {
        maxSize: maxSize ? parseInt(maxSize) : 1024, // MB
        minTime: minTime ? parseInt(minTime) : 3600   // seconds
      };
    } catch (error) {
      return {
        maxSize: 1024,
        minTime: 3600
      };
    }
  }

  // 分析缓存使用情况
  analyzeCacheUsage() {
    console.log('分析缓存使用情况...');
    
    try {
      // 获取缓存统计信息
      const cacheInfo = execSync('npm cache verify', { encoding: 'utf8' });
      
      // 解析缓存大小
      const sizeMatch = cacheInfo.match(/Cache verified and compressed \(([\d.]+) MB\)/);
      const cacheSize = sizeMatch ? parseFloat(sizeMatch[1]) : 0;
      
      // 计算缓存使用率
      const usageRate = (cacheSize / this.cacheConfig.maxSize) * 100;
      
      return {
        path: this.cachePath,
        size: cacheSize,
        maxSize: this.cacheConfig.maxSize,
        usageRate: usageRate,
        config: this.cacheConfig
      };
    } catch (error) {
      console.error('获取缓存信息失败:', error.message);
      return null;
    }
  }

  // 优化缓存配置
  optimizeCacheConfig() {
    console.log('优化缓存配置...');
    
    const usage = this.analyzeCacheUsage();
    if (!usage) return false;
    
    // 根据使用情况调整配置
    let newMaxSize = usage.maxSize;
    let newMinTime = usage.config.minTime;
    
    if (usage.usageRate > 80) {
      newMaxSize = Math.floor(usage.size * 1.5);
      console.log(`缓存使用率过高(${usage.usageRate.toFixed(2)}%)，建议增加缓存大小到 ${newMaxSize}MB`);
    } else if (usage.usageRate < 30) {
      newMaxSize = Math.max(512, Math.floor(usage.size * 0.8));
      console.log(`缓存使用率较低(${usage.usageRate.toFixed(2)}%)，可以减少缓存大小到 ${newMaxSize}MB`);
    }
    
    // 应用新配置
    try {
      execSync(`npm config set cache-max ${newMaxSize}`);
      console.log(`已更新缓存最大大小为 ${newMaxSize}MB`);
      
      return true;
    } catch (error) {
      console.error('更新缓存配置失败:', error.message);
      return false;
    }
  }

  // 清理缓存
  cleanCache(options = {}) {
    const { force = false, olderThan = null } = options;
    
    console.log('清理缓存...');
    
    try {
      if (olderThan) {
        // 清理指定时间之前的缓存
        console.log(`清理 ${olderThan} 之前的缓存`);
        // 这里需要实现更复杂的逻辑来按时间清理缓存
        // 由于npm cache clean不支持按时间清理，这是一个简化实现
      }
      
      if (force) {
        // 强制清理所有缓存
        execSync('npm cache clean --force');
        console.log('已清理所有缓存');
      } else {
        // 验证并清理无效缓存
        execSync('npm cache verify');
        console.log('已验证并清理无效缓存');
      }
      
      return true;
    } catch (error) {
      console.error('清理缓存失败:', error.message);
      return false;
    }
  }
}

// 示例3：NPM依赖分析器
class NPMDependencyAnalyzer {
  constructor(projectPath = process.cwd()) {
    this.projectPath = projectPath;
    this.packageJsonPath = path.join(projectPath, 'package.json');
    this.packageLockPath = path.join(projectPath, 'package-lock.json');
  }

  // 分析依赖结构
  analyzeDependencies() {
    console.log('分析项目依赖结构...');
    
    try {
      const packageJson = this.readPackageJson();
      const packageLock = this.readPackageLock();
      
      if (!packageJson) {
        throw new Error('无法读取package.json文件');
      }
      
      const analysis = {
        totalDependencies: 0,
        directDependencies: 0,
        devDependencies: 0,
        optionalDependencies: 0,
        peerDependencies: 0,
        duplicateDependencies: 0,
        outdatedDependencies: 0,
        dependencyTree: this.buildDependencyTree(packageJson, packageLock),
        recommendations: []
      };
      
      // 统计各类依赖数量
      if (packageJson.dependencies) {
        analysis.directDependencies = Object.keys(packageJson.dependencies).length;
      }
      
      if (packageJson.devDependencies) {
        analysis.devDependencies = Object.keys(packageJson.devDependencies).length;
      }
      
      if (packageJson.optionalDependencies) {
        analysis.optionalDependencies = Object.keys(packageJson.optionalDependencies).length;
      }
      
      if (packageJson.peerDependencies) {
        analysis.peerDependencies = Object.keys(packageJson.peerDependencies).length;
      }
      
      analysis.totalDependencies = analysis.directDependencies + 
                                  analysis.devDependencies + 
                                  analysis.optionalDependencies;
      
      // 分析重复依赖
      analysis.duplicateDependencies = this.findDuplicateDependencies(packageLock);
      
      // 检查过时依赖
      analysis.outdatedDependencies = this.checkOutdatedDependencies();
      
      // 生成优化建议
      analysis.recommendations = this.generateRecommendations(analysis);
      
      return analysis;
    } catch (error) {
      console.error('依赖分析失败:', error.message);
      throw error;
    }
  }

  // 读取package.json
  readPackageJson() {
    try {
      const content = fs.readFileSync(this.packageJsonPath, 'utf8');
      return JSON.parse(content);
    } catch (error) {
      console.error('读取package.json失败:', error.message);
      return null;
    }
  }

  // 读取package-lock.json
  readPackageLock() {
    try {
      const content = fs.readFileSync(this.packageLockPath, 'utf8');
      return JSON.parse(content);
    } catch (error) {
      console.error('读取package-lock.json失败:', error.message);
      return null;
    }
  }

  // 构建依赖树
  buildDependencyTree(packageJson, packageLock) {
    const tree = {
      name: packageJson.name || 'project',
      version: packageJson.version || '0.0.0',
      dependencies: {}
    };
    
    // 添加直接依赖
    if (packageJson.dependencies) {
      for (const [name, version] of Object.entries(packageJson.dependencies)) {
        tree.dependencies[name] = {
          version,
          type: 'production',
          children: this.getChildDependencies(name, packageLock)
        };
      }
    }
    
    // 添加开发依赖
    if (packageJson.devDependencies) {
      for (const [name, version] of Object.entries(packageJson.devDependencies)) {
        if (!tree.dependencies[name]) {
          tree.dependencies[name] = {
            version,
            type: 'development',
            children: this.getChildDependencies(name, packageLock)
          };
        }
      }
    }
    
    return tree;
  }

  // 获取子依赖
  getChildDependencies(packageName, packageLock) {
    if (!packageLock || !packageLock.dependencies || !packageLock.dependencies[packageName]) {
      return {};
    }
    
    const packageInfo = packageLock.dependencies[packageName];
    const children = {};
    
    if (packageInfo.requires) {
      for (const [name, version] of Object.entries(packageInfo.requires)) {
        children[name] = {
          version,
          children: this.getChildDependencies(name, packageLock)
        };
      }
    }
    
    return children;
  }

  // 查找重复依赖
  findDuplicateDependencies(packageLock) {
    if (!packageLock || !packageLock.dependencies) {
      return 0;
    }
    
    const versionMap = {};
    let duplicates = 0;
    
    for (const [name, info] of Object.entries(packageLock.dependencies)) {
      if (!versionMap[name]) {
        versionMap[name] = new Set();
      }
      
      versionMap[name].add(info.version);
      
      if (versionMap[name].size > 1) {
        duplicates++;
      }
    }
    
    return duplicates;
  }

  // 检查过时依赖
  checkOutdatedDependencies() {
    try {
      const output = execSync('npm outdated --json', { 
        encoding: 'utf8',
        stdio: 'pipe'
      });
      
      const outdated = JSON.parse(output || '{}');
      return Object.keys(outdated).length;
    } catch (error) {
      // npm outdated在有过时包时会返回非零退出码
      try {
        const output = error.stdout;
        const outdated = JSON.parse(output || '{}');
        return Object.keys(outdated).length;
      } catch (parseError) {
        return 0;
      }
    }
  }

  // 生成优化建议
  generateRecommendations(analysis) {
    const recommendations = [];
    
    if (analysis.duplicateDependencies > 0) {
      recommendations.push(`发现 ${analysis.duplicateDependencies} 个重复依赖，建议使用npm dedupe或使用pnpm`);
    }
    
    if (analysis.outdatedDependencies > 0) {
      recommendations.push(`发现 ${analysis.outdatedDependencies} 个过时依赖，建议使用npm update更新`);
    }
    
    if (analysis.totalDependencies > 500) {
      recommendations.push('依赖数量较多，建议检查并移除不必要的依赖');
    }
    
    if (analysis.devDependencies > analysis.directDependencies) {
      recommendations.push('开发依赖数量较多，建议检查是否都是必要的');
    }
    
    return recommendations;
  }
}

// 示例4：NPM网络优化器
class NPMNetworkOptimizer {
  constructor() {
    this.registry = this.getCurrentRegistry();
    this.mirrors = [
      { name: 'npm官方', url: 'https://registry.npmjs.org/' },
      { name: '淘宝镜像', url: 'https://registry.npmmirror.com/' },
      { name: '腾讯云镜像', url: 'https://mirrors.cloud.tencent.com/npm/' },
      { name: '华为云镜像', url: 'https://repo.huaweicloud.com/repository/npm/' }
    ];
  }

  // 获取当前注册表
  getCurrentRegistry() {
    try {
      return execSync('npm config get registry', { encoding: 'utf8' }).trim();
    } catch (error) {
      return 'https://registry.npmjs.org/';
    }
  }

  // 测试镜像速度
  async testMirrorSpeed(mirror) {
    const startTime = Date.now();
    
    try {
      // 使用curl测试镜像响应时间
      const output = execSync(`curl -o /dev/null -s -w "%{time_total}" ${mirror.url}`, { 
        encoding: 'utf8',
        timeout: 10000
      });
      
      const responseTime = parseFloat(output) * 1000; // 转换为毫秒
      const endTime = Date.now();
      
      return {
        name: mirror.name,
        url: mirror.url,
        responseTime: responseTime,
        testTime: endTime - startTime
      };
    } catch (error) {
      return {
        name: mirror.name,
        url: mirror.url,
        responseTime: Infinity,
        error: error.message
      };
    }
  }

  // 测试所有镜像速度
  async testAllMirrors() {
    console.log('测试所有镜像速度...');
    
    const results = [];
    
    for (const mirror of this.mirrors) {
      console.log(`测试 ${mirror.name}...`);
      const result = await this.testMirrorSpeed(mirror);
      results.push(result);
    }
    
    // 按响应时间排序
    results.sort((a, b) => a.responseTime - b.responseTime);
    
    return results;
  }

  // 获取最佳镜像
  async getBestMirror() {
    const results = await this.testAllMirrors();
    return results[0];
  }

  // 设置最佳镜像
  async setBestMirror() {
    console.log('寻找最佳镜像...');
    
    const bestMirror = await this.getBestMirror();
    
    if (bestMirror.responseTime === Infinity) {
      console.error('所有镜像测试失败');
      return false;
    }
    
    try {
      execSync(`npm config set registry ${bestMirror.url}`);
      console.log(`已设置为最佳镜像: ${bestMirror.name} (${bestMirror.url})`);
      console.log(`响应时间: ${bestMirror.responseTime.toFixed(2)}ms`);
      
      this.registry = bestMirror.url;
      return true;
    } catch (error) {
      console.error('设置镜像失败:', error.message);
      return false;
    }
  }

  // 配置代理
  configureProxy(proxyUrl) {
    try {
      execSync(`npm config set proxy ${proxyUrl}`);
      execSync(`npm config set https-proxy ${proxyUrl}`);
      console.log(`已设置代理: ${proxyUrl}`);
      return true;
    } catch (error) {
      console.error('设置代理失败:', error.message);
      return false;
    }
  }

  // 清除代理设置
  clearProxy() {
    try {
      execSync('npm config delete proxy');
      execSync('npm config delete https-proxy');
      console.log('已清除代理设置');
      return true;
    } catch (error) {
      console.error('清除代理失败:', error.message);
      return false;
    }
  }
}

// 示例5：NPM构建优化器
class NPMBuildOptimizer {
  constructor(projectPath = process.cwd()) {
    this.projectPath = projectPath;
    this.packageJsonPath = path.join(projectPath, 'package.json');
  }

  // 分析构建脚本
  analyzeBuildScripts() {
    console.log('分析构建脚本...');
    
    try {
      const packageJson = this.readPackageJson();
      if (!packageJson || !packageJson.scripts) {
        return { error: '没有找到构建脚本' };
      }
      
      const scripts = packageJson.scripts;
      const buildScripts = {};
      
      // 查找构建相关脚本
      for (const [name, script] of Object.entries(scripts)) {
        if (name.includes('build') || name.includes('compile')) {
          buildScripts[name] = {
            command: script,
            parallelizable: this.checkParallelizable(script),
            cacheable: this.checkCacheable(script),
            incremental: this.checkIncremental(script)
          };
        }
      }
      
      return {
        totalBuildScripts: Object.keys(buildScripts).length,
        buildScripts,
        recommendations: this.getBuildRecommendations(buildScripts)
      };
    } catch (error) {
      console.error('分析构建脚本失败:', error.message);
      return { error: error.message };
    }
  }

  // 读取package.json
  readPackageJson() {
    try {
      const content = fs.readFileSync(this.packageJsonPath, 'utf8');
      return JSON.parse(content);
    } catch (error) {
      console.error('读取package.json失败:', error.message);
      return null;
    }
  }

  // 检查脚本是否可并行
  checkParallelizable(script) {
    // 简单检查脚本是否可以并行执行
    return !script.includes('&&') && !script.includes('||');
  }

  // 检查脚本是否可缓存
  checkCacheable(script) {
    // 简单检查脚本是否支持缓存
    return script.includes('--cache') || 
           script.includes('webpack') || 
           script.includes('babel') ||
           script.includes('rollup');
  }

  // 检查脚本是否支持增量构建
  checkIncremental(script) {
    // 简单检查脚本是否支持增量构建
    return script.includes('--incremental') || 
           script.includes('--watch') ||
           script.includes('tsc --incremental');
  }

  // 获取构建优化建议
  getBuildRecommendations(buildScripts) {
    const recommendations = [];
    
    for (const [name, script] of Object.entries(buildScripts)) {
      if (!script.cacheable) {
        recommendations.push(`脚本 "${name}" 不支持缓存，考虑添加缓存选项`);
      }
      
      if (!script.incremental && name.includes('build')) {
        recommendations.push(`脚本 "${name}" 不支持增量构建，考虑添加增量选项`);
      }
      
      if (script.command.includes('npm run') && script.parallelizable) {
        recommendations.push(`脚本 "${name}" 可以并行执行，考虑使用npm-run-all或concurrently`);
      }
    }
    
    if (Object.keys(buildScripts).length > 5) {
      recommendations.push('构建脚本较多，考虑合并或简化构建流程');
    }
    
    return recommendations;
  }

  // 优化构建配置
  optimizeBuildConfig() {
    console.log('优化构建配置...');
    
    const analysis = this.analyzeBuildScripts();
    if (analysis.error) {
      console.error(analysis.error);
      return false;
    }
    
    // 这里可以实现具体的优化逻辑
    // 例如：修改package.json中的脚本、添加构建工具配置等
    
    console.log('构建优化建议:');
    analysis.recommendations.forEach(rec => console.log(`- ${rec}`));
    
    return true;
  }

  // 测试构建性能
  testBuildPerformance(scriptName) {
    console.log(`测试构建性能: ${scriptName}`);
    
    try {
      const startTime = Date.now();
      const output = execSync(`npm run ${scriptName}`, { 
        encoding: 'utf8',
        stdio: 'pipe'
      });
      const endTime = Date.now();
      
      const buildTime = endTime - startTime;
      
      return {
        scriptName,
        buildTime,
        success: true,
        output: output.substring(0, 500) // 只保留前500字符
      };
    } catch (error) {
      return {
        scriptName,
        buildTime: 0,
        success: false,
        error: error.message
      };
    }
  }
}

// 示例6：NPM调试工具
class NPMDebugger {
  constructor() {
    this.logLevel = 'info';
    this.debugInfo = {};
  }

  // 设置日志级别
  setLogLevel(level) {
    this.logLevel = level;
    try {
      execSync(`npm config set loglevel ${level}`);
      console.log(`已设置日志级别为: ${level}`);
    } catch (error) {
      console.error('设置日志级别失败:', error.message);
    }
  }

  // 运行NPM诊断
  runDoctor() {
    console.log('运行NPM诊断...');
    
    try {
      const output = execSync('npm doctor', { encoding: 'utf8' });
      console.log(output);
      
      // 解析诊断结果
      this.parseDoctorOutput(output);
      
      return this.debugInfo;
    } catch (error) {
      console.error('NPM诊断失败:', error.message);
      return null;
    }
  }

  // 解析诊断输出
  parseDoctorOutput(output) {
    const lines = output.split('\n');
    
    for (const line of lines) {
      if (line.includes('npm ping')) {
        this.debugInfo.network = line.includes('ok') ? '正常' : '异常';
      }
      
      if (line.includes('npm -v')) {
        this.debugInfo.npmVersion = line.trim();
      }
      
      if (line.includes('node -v')) {
        this.debugInfo.nodeVersion = line.trim();
      }
      
      if (line.includes('npm config get registry')) {
        this.debugInfo.registry = line.trim();
      }
      
      if (line.includes('npm config get cache')) {
        this.debugInfo.cachePath = line.trim();
      }
    }
  }

  // 测试网络连接
  testNetworkConnection() {
    console.log('测试网络连接...');
    
    try {
      // 测试ping
      const pingOutput = execSync('npm ping', { encoding: 'utf8' });
      console.log('NPM注册表连接:', pingOutput.trim());
      
      // 测试下载速度
      const startTime = Date.now();
      execSync('npm ping --registry https://registry.npmmirror.com/', { encoding: 'utf8' });
      const endTime = Date.now();
      
      console.log(`淘宝镜像响应时间: ${endTime - startTime}ms`);
      
      return {
        officialRegistry: pingOutput.trim(),
        taobaoRegistry: `${endTime - startTime}ms`
      };
    } catch (error) {
      console.error('网络连接测试失败:', error.message);
      return null;
    }
  }

  // 检查权限
  checkPermissions() {
    console.log('检查NPM权限...');
    
    try {
      // 检查npm全局目录权限
      const globalPath = execSync('npm config get prefix', { encoding: 'utf8' }).trim();
      console.log(`NPM全局目录: ${globalPath}`);
      
      // 尝试创建测试文件
      const testFile = path.join(globalPath, 'npm-permission-test');
      try {
        fs.writeFileSync(testFile, 'test');
        fs.unlinkSync(testFile);
        console.log('NPM全局目录权限正常');
        return { status: '正常', path: globalPath };
      } catch (error) {
        console.log('NPM全局目录权限不足');
        return { status: '权限不足', path: globalPath, error: error.message };
      }
    } catch (error) {
      console.error('权限检查失败:', error.message);
      return null;
    }
  }

  // 检查缓存状态
  checkCacheStatus() {
    console.log('检查缓存状态...');
    
    try {
      const cachePath = execSync('npm config get cache', { encoding: 'utf8' }).trim();
      console.log(`缓存路径: ${cachePath}`);
      
      // 检查缓存是否存在
      if (!fs.existsSync(cachePath)) {
        console.log('缓存目录不存在');
        return { status: '不存在', path: cachePath };
      }
      
      // 检查缓存大小
      const stats = execSync('npm cache verify', { encoding: 'utf8' });
      console.log(stats);
      
      return { status: '正常', path: cachePath, stats };
    } catch (error) {
      console.error('缓存状态检查失败:', error.message);
      return null;
    }
  }

  // 生成调试报告
  generateDebugReport() {
    console.log('生成调试报告...');
    
    const report = {
      timestamp: new Date().toISOString(),
      logLevel: this.logLevel,
      debugInfo: this.debugInfo
    };
    
    // 运行各项检查
    report.doctor = this.runDoctor();
    report.network = this.testNetworkConnection();
    report.permissions = this.checkPermissions();
    report.cache = this.checkCacheStatus();
    
    // 保存报告到文件
    const reportPath = path.join(process.cwd(), 'npm-debug-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`调试报告已保存到: ${reportPath}`);
    
    return report;
  }
}

// 示例7：NPM性能基准测试
class NPMPerformanceBenchmark {
  constructor() {
    this.results = [];
  }

  // 基准测试npm install
  benchmarkInstall(packageName, options = {}) {
    const { clean = true, iterations = 3 } = options;
    
    console.log(`基准测试npm install: ${packageName}`);
    
    const results = {
      packageName,
      iterations: [],
      averageTime: 0,
      minTime: Infinity,
      maxTime: 0
    };
    
    for (let i = 0; i < iterations; i++) {
      console.log(`第 ${i + 1} 次测试...`);
      
      // 清理环境
      if (clean) {
        this.cleanEnvironment();
      }
      
      // 执行安装并测量时间
      const startTime = Date.now();
      try {
        execSync(`npm install ${packageName}`, { stdio: 'pipe' });
        const endTime = Date.now();
        const installTime = endTime - startTime;
        
        results.iterations.push(installTime);
        results.minTime = Math.min(results.minTime, installTime);
        results.maxTime = Math.max(results.maxTime, installTime);
        
        console.log(`安装时间: ${installTime}ms`);
      } catch (error) {
        console.error(`安装失败: ${error.message}`);
        results.iterations.push(-1);
      }
    }
    
    // 计算平均时间
    const validTimes = results.iterations.filter(t => t > 0);
    if (validTimes.length > 0) {
      results.averageTime = validTimes.reduce((sum, time) => sum + time, 0) / validTimes.length;
    }
    
    this.results.push(results);
    return results;
  }

  // 基准测试不同镜像
  benchmarkMirrors(packageName) {
    console.log(`基准测试不同镜像: ${packageName}`);
    
    const mirrors = [
      { name: 'npm官方', url: 'https://registry.npmjs.org/' },
      { name: '淘宝镜像', url: 'https://registry.npmmirror.com/' }
    ];
    
    const results = {
      packageName,
      mirrors: {}
    };
    
    for (const mirror of mirrors) {
      console.log(`测试 ${mirror.name}...`);
      
      // 设置镜像
      try {
        execSync(`npm config set registry ${mirror.url}`);
        
        // 测试安装
        const installResult = this.benchmarkInstall(packageName, { clean: true, iterations: 1 });
        results.mirrors[mirror.name] = {
          url: mirror.url,
          installTime: installResult.averageTime
        };
      } catch (error) {
        console.error(`${mirror.name} 测试失败: ${error.message}`);
        results.mirrors[mirror.name] = {
          url: mirror.url,
          error: error.message
        };
      }
    }
    
    // 恢复默认镜像
    try {
      execSync('npm config set registry https://registry.npmjs.org/');
    } catch (error) {
      console.error('恢复默认镜像失败:', error.message);
    }
    
    this.results.push(results);
    return results;
  }

  // 基准测试缓存效果
  benchmarkCache(packageName) {
    console.log(`基准测试缓存效果: ${packageName}`);
    
    const results = {
      packageName,
      withoutCache: 0,
      withCache: 0,
      cacheSpeedup: 0
    };
    
    // 测试无缓存安装
    console.log('测试无缓存安装...');
    this.cleanCache();
    this.cleanEnvironment();
    
    const startTime1 = Date.now();
    try {
      execSync(`npm install ${packageName}`, { stdio: 'pipe' });
      const endTime1 = Date.now();
      results.withoutCache = endTime1 - startTime1;
      console.log(`无缓存安装时间: ${results.withoutCache}ms`);
    } catch (error) {
      console.error(`无缓存安装失败: ${error.message}`);
    }
    
    // 测试有缓存安装
    console.log('测试有缓存安装...');
    this.cleanEnvironment();
    
    const startTime2 = Date.now();
    try {
      execSync(`npm install ${packageName}`, { stdio: 'pipe' });
      const endTime2 = Date.now();
      results.withCache = endTime2 - startTime2;
      console.log(`有缓存安装时间: ${results.withCache}ms`);
    } catch (error) {
      console.error(`有缓存安装失败: ${error.message}`);
    }
    
    // 计算缓存加速比
    if (results.withoutCache > 0 && results.withCache > 0) {
      results.cacheSpeedup = results.withoutCache / results.withCache;
      console.log(`缓存加速比: ${results.cacheSpeedup.toFixed(2)}x`);
    }
    
    this.results.push(results);
    return results;
  }

  // 清理环境
  cleanEnvironment() {
    try {
      // 删除node_modules和package-lock.json
      if (fs.existsSync('node_modules')) {
        execSync('rm -rf node_modules', { stdio: 'pipe' });
      }
      
      if (fs.existsSync('package-lock.json')) {
        fs.unlinkSync('package-lock.json');
      }
    } catch (error) {
      console.error('清理环境失败:', error.message);
    }
  }

  // 清理缓存
  cleanCache() {
    try {
      execSync('npm cache clean --force', { stdio: 'pipe' });
    } catch (error) {
      console.error('清理缓存失败:', error.message);
    }
  }

  // 生成基准测试报告
  generateBenchmarkReport() {
    console.log('生成基准测试报告...');
    
    const report = {
      timestamp: new Date().toISOString(),
      results: this.results,
      summary: this.generateSummary()
    };
    
    // 保存报告到文件
    const reportPath = path.join(process.cwd(), 'npm-benchmark-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`基准测试报告已保存到: ${reportPath}`);
    
    return report;
  }

  // 生成摘要
  generateSummary() {
    const summary = {
      totalTests: this.results.length,
      recommendations: []
    };
    
    // 分析结果并生成建议
    for (const result of this.results) {
      if (result.packageName && result.averageTime > 60000) {
        summary.recommendations.push(`${result.packageName} 安装时间过长，建议优化`);
      }
      
      if (result.mirrors) {
        const mirrorTimes = Object.entries(result.mirrors)
          .filter(([name, data]) => data.installTime)
          .map(([name, data]) => ({ name, time: data.installTime }))
          .sort((a, b) => a.time - b.time);
        
        if (mirrorTimes.length > 1) {
          summary.recommendations.push(
            `对于 ${result.packageName}，${mirrorTimes[0].name} 镜像最快`
          );
        }
      }
      
      if (result.cacheSpeedup && result.cacheSpeedup < 1.5) {
        summary.recommendations.push('缓存效果不明显，建议检查缓存配置');
      }
    }
    
    return summary;
  }
}

// 示例8：NPM配置优化器
class NPMConfigOptimizer {
  constructor() {
    this.currentConfig = this.getCurrentConfig();
    this.recommendedConfig = this.getRecommendedConfig();
  }

  // 获取当前配置
  getCurrentConfig() {
    try {
      const output = execSync('npm config list --json', { encoding: 'utf8' });
      return JSON.parse(output);
    } catch (error) {
      console.error('获取当前配置失败:', error.message);
      return {};
    }
  }

  // 获取推荐配置
  getRecommendedConfig() {
    return {
      registry: 'https://registry.npmmirror.com/',
      cache: path.join(os.homedir(), '.npm'),
      'cache-max': 2048,
      'cache-min': 3600,
      maxsockets: 10,
      'fetch-retry-mintimeout': 20000,
      'fetch-retry-maxtimeout': 120000,
      'fetch-timeout': 60000,
      loglevel: 'warn',
      progress: true,
      'strict-ssl': true,
      'package-lock': true,
      'save-exact': false
    };
  }

  // 分析配置差异
  analyzeConfigDifferences() {
    console.log('分析配置差异...');
    
    const differences = {
      missing: [],
      different: [],
      extra: []
    };
    
    // 检查缺失和不同的配置
    for (const [key, recommendedValue] of Object.entries(this.recommendedConfig)) {
      if (!(key in this.currentConfig)) {
        differences.missing.push({ key, recommendedValue });
      } else if (this.currentConfig[key] !== recommendedValue) {
        differences.different.push({
          key,
          currentValue: this.currentConfig[key],
          recommendedValue
        });
      }
    }
    
    // 检查额外的配置
    for (const key of Object.keys(this.currentConfig)) {
      if (!(key in this.recommendedConfig)) {
        differences.extra.push({ key, value: this.currentConfig[key] });
      }
    }
    
    return differences;
  }

  // 应用推荐配置
  applyRecommendedConfig(options = {}) {
    const { interactive = true, skipExtra = true } = options;
    
    console.log('应用推荐配置...');
    
    const differences = this.analyzeConfigDifferences();
    
    // 应用缺失的配置
    for (const { key, recommendedValue } of differences.missing) {
      if (interactive) {
        console.log(`添加配置: ${key} = ${recommendedValue}`);
      }
      
      try {
        execSync(`npm config set ${key} ${recommendedValue}`);
      } catch (error) {
        console.error(`设置配置 ${key} 失败:`, error.message);
      }
    }
    
    // 应用不同的配置
    for (const { key, recommendedValue } of differences.different) {
      if (interactive) {
        console.log(`更新配置: ${key} = ${recommendedValue}`);
      }
      
      try {
        execSync(`npm config set ${key} ${recommendedValue}`);
      } catch (error) {
        console.error(`更新配置 ${key} 失败:`, error.message);
      }
    }
    
    // 处理额外的配置
    if (!skipExtra) {
      for (const { key } of differences.extra) {
        if (interactive) {
          console.log(`移除额外配置: ${key}`);
        }
        
        try {
          execSync(`npm config delete ${key}`);
        } catch (error) {
          console.error(`删除配置 ${key} 失败:`, error.message);
        }
      }
    }
    
    // 更新当前配置
    this.currentConfig = this.getCurrentConfig();
    
    console.log('配置优化完成');
    return true;
  }

  // 重置配置为默认值
  resetToDefaults() {
    console.log('重置配置为默认值...');
    
    try {
      execSync('npm config edit');
      console.log('已打开配置编辑器，请手动重置配置');
      return true;
    } catch (error) {
      console.error('重置配置失败:', error.message);
      return false;
    }
  }

  // 生成配置报告
  generateConfigReport() {
    console.log('生成配置报告...');
    
    const differences = this.analyzeConfigDifferences();
    
    const report = {
      timestamp: new Date().toISOString(),
      currentConfig: this.currentConfig,
      recommendedConfig: this.recommendedConfig,
      differences,
      score: this.calculateConfigScore(differences)
    };
    
    // 保存报告到文件
    const reportPath = path.join(process.cwd(), 'npm-config-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`配置报告已保存到: ${reportPath}`);
    
    return report;
  }

  // 计算配置评分
  calculateConfigScore(differences) {
    const totalRecommended = Object.keys(this.recommendedConfig).length;
    const matched = totalRecommended - differences.missing.length - differences.different.length;
    
    return Math.round((matched / totalRecommended) * 100);
  }
}

// 示例9：NPM性能分析器
class NPMPerformanceAnalyzer {
  constructor() {
    this.metrics = {};
  }

  // 分析项目整体性能
  analyzeProjectPerformance(projectPath = process.cwd()) {
    console.log('分析项目整体性能...');
    
    const analysis = {
      projectPath,
      installPerformance: this.analyzeInstallPerformance(projectPath),
      cachePerformance: this.analyzeCachePerformance(),
      dependencyPerformance: this.analyzeDependencyPerformance(projectPath),
      networkPerformance: this.analyzeNetworkPerformance(),
      buildPerformance: this.analyzeBuildPerformance(projectPath),
      overallScore: 0,
      recommendations: []
    };
    
    // 计算总体评分
    analysis.overallScore = this.calculateOverallScore(analysis);
    
    // 生成优化建议
    analysis.recommendations = this.generateOverallRecommendations(analysis);
    
    return analysis;
  }

  // 分析安装性能
  analyzeInstallPerformance(projectPath) {
    try {
      const originalDir = process.cwd();
      process.chdir(projectPath);
      
      // 清理环境
      this.cleanEnvironment();
      
      // 测量安装时间
      const startTime = Date.now();
      execSync('npm install', { stdio: 'pipe' });
      const endTime = Date.now();
      
      const installTime = endTime - startTime;
      
      // 恢复目录
      process.chdir(originalDir);
      
      return {
        installTime,
        score: this.calculateInstallScore(installTime)
      };
    } catch (error) {
      console.error('分析安装性能失败:', error.message);
      return {
        installTime: -1,
        score: 0,
        error: error.message
      };
    }
  }

  // 分析缓存性能
  analyzeCachePerformance() {
    try {
      // 获取缓存信息
      const cacheInfo = execSync('npm cache verify', { encoding: 'utf8' });
      
      // 解析缓存大小
      const sizeMatch = cacheInfo.match(/Cache verified and compressed \(([\d.]+) MB\)/);
      const cacheSize = sizeMatch ? parseFloat(sizeMatch[1]) : 0;
      
      // 获取缓存配置
      const maxCacheSize = execSync('npm config get cache-max', { encoding: 'utf8' }).trim();
      const maxSize = maxCacheSize ? parseInt(maxCacheSize) : 1024;
      
      const usageRate = (cacheSize / maxSize) * 100;
      
      return {
        cacheSize,
        maxSize,
        usageRate,
        score: this.calculateCacheScore(usageRate)
      };
    } catch (error) {
      console.error('分析缓存性能失败:', error.message);
      return {
        cacheSize: 0,
        maxSize: 0,
        usageRate: 0,
        score: 0,
        error: error.message
      };
    }
  }

  // 分析依赖性能
  analyzeDependencyPerformance(projectPath) {
    try {
      const packageJsonPath = path.join(projectPath, 'package.json');
      const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
      
      // 统计依赖数量
      const prodDeps = packageJson.dependencies ? Object.keys(packageJson.dependencies).length : 0;
      const devDeps = packageJson.devDependencies ? Object.keys(packageJson.devDependencies).length : 0;
      const totalDeps = prodDeps + devDeps;
      
      // 检查过时依赖
      let outdatedDeps = 0;
      try {
        const outdatedOutput = execSync('npm outdated --json', { 
          encoding: 'utf8',
          stdio: 'pipe'
        });
        const outdated = JSON.parse(outdatedOutput || '{}');
        outdatedDeps = Object.keys(outdated).length;
      } catch (error) {
        // npm outdated在有过时包时会返回非零退出码
        try {
          const outdatedOutput = error.stdout;
          const outdated = JSON.parse(outdatedOutput || '{}');
          outdatedDeps = Object.keys(outdated).length;
        } catch (parseError) {
          outdatedDeps = 0;
        }
      }
      
      return {
        totalDeps,
        prodDeps,
        devDeps,
        outdatedDeps,
        score: this.calculateDependencyScore(totalDeps, outdatedDeps)
      };
    } catch (error) {
      console.error('分析依赖性能失败:', error.message);
      return {
        totalDeps: 0,
        prodDeps: 0,
        devDeps: 0,
        outdatedDeps: 0,
        score: 0,
        error: error.message
      };
    }
  }

  // 分析网络性能
  analyzeNetworkPerformance() {
    try {
      // 测试官方注册表
      const startTime1 = Date.now();
      execSync('npm ping', { stdio: 'pipe' });
      const endTime1 = Date.now();
      const officialTime = endTime1 - startTime1;
      
      // 测试淘宝镜像
      const startTime2 = Date.now();
      execSync('npm ping --registry https://registry.npmmirror.com/', { stdio: 'pipe' });
      const endTime2 = Date.now();
      const taobaoTime = endTime2 - startTime2;
      
      // 获取当前注册表
      const currentRegistry = execSync('npm config get registry', { encoding: 'utf8' }).trim();
      
      return {
        currentRegistry,
        officialTime,
        taobaoTime,
        bestTime: Math.min(officialTime, taobaoTime),
        score: this.calculateNetworkScore(officialTime, taobaoTime)
      };
    } catch (error) {
      console.error('分析网络性能失败:', error.message);
      return {
        currentRegistry: '',
        officialTime: -1,
        taobaoTime: -1,
        bestTime: -1,
        score: 0,
        error: error.message
      };
    }
  }

  // 分析构建性能
  analyzeBuildPerformance(projectPath) {
    try {
      const packageJsonPath = path.join(projectPath, 'package.json');
      const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
      
      if (!packageJson.scripts) {
        return {
          buildScripts: 0,
          score: 100,
          message: '没有构建脚本'
        };
      }
      
      // 查找构建脚本
      const buildScripts = Object.keys(packageJson.scripts).filter(name => 
        name.includes('build') || name.includes('compile')
      );
      
      if (buildScripts.length === 0) {
        return {
          buildScripts: 0,
          score: 100,
          message: '没有构建脚本'
        };
      }
      
      // 测试构建性能
      const originalDir = process.cwd();
      process.chdir(projectPath);
      
      const buildResults = [];
      
      for (const script of buildScripts) {
        try {
          const startTime = Date.now();
          execSync(`npm run ${script}`, { stdio: 'pipe' });
          const endTime = Date.now();
          
          buildResults.push({
            script,
            buildTime: endTime - startTime,
            success: true
          });
        } catch (error) {
          buildResults.push({
            script,
            buildTime: -1,
            success: false,
            error: error.message
          });
        }
      }
      
      process.chdir(originalDir);
      
      // 计算平均构建时间
      const successfulBuilds = buildResults.filter(r => r.success);
      const avgBuildTime = successfulBuilds.length > 0 
        ? successfulBuilds.reduce((sum, r) => sum + r.buildTime, 0) / successfulBuilds.length 
        : -1;
      
      return {
        buildScripts: buildScripts.length,
        buildResults,
        avgBuildTime,
        score: this.calculateBuildScore(avgBuildTime)
      };
    } catch (error) {
      console.error('分析构建性能失败:', error.message);
      return {
        buildScripts: 0,
        score: 0,
        error: error.message
      };
    }
  }

  // 计算安装评分
  calculateInstallScore(installTime) {
    if (installTime < 0) return 0;
    if (installTime < 10000) return 100;  // < 10s
    if (installTime < 30000) return 80;   // < 30s
    if (installTime < 60000) return 60;   // < 1min
    if (installTime < 120000) return 40;  // < 2min
    return 20;  // > 2min
  }

  // 计算缓存评分
  calculateCacheScore(usageRate) {
    if (usageRate < 50) return 60;  // 使用率低
    if (usageRate < 80) return 100; // 使用率适中
    return 80;  // 使用率高
  }

  // 计算依赖评分
  calculateDependencyScore(totalDeps, outdatedDeps) {
    const outdatedRate = totalDeps > 0 ? (outdatedDeps / totalDeps) * 100 : 0;
    
    if (totalDeps > 1000) return 20;  // 依赖过多
    if (totalDeps > 500) return 40;   // 依赖较多
    
    if (outdatedRate > 50) return 20;  // 过时依赖太多
    if (outdatedRate > 20) return 40;  // 过时依赖较多
    
    return 100;  // 依赖健康
  }

  // 计算网络评分
  calculateNetworkScore(officialTime, taobaoTime) {
    if (officialTime < 0 || taobaoTime < 0) return 0;
    
    const bestTime = Math.min(officialTime, taobaoTime);
    
    if (bestTime < 500) return 100;  // < 500ms
    if (bestTime < 1000) return 80;  // < 1s
    if (bestTime < 2000) return 60;  // < 2s
    if (bestTime < 5000) return 40;  // < 5s
    return 20;  // > 5s
  }

  // 计算构建评分
  calculateBuildScore(avgBuildTime) {
    if (avgBuildTime < 0) return 0;
    if (avgBuildTime < 10000) return 100;  // < 10s
    if (avgBuildTime < 30000) return 80;   // < 30s
    if (avgBuildTime < 60000) return 60;   // < 1min
    if (avgBuildTime < 120000) return 40;  // < 2min
    return 20;  // > 2min
  }

  // 计算总体评分
  calculateOverallScore(analysis) {
    const weights = {
      install: 0.25,
      cache: 0.15,
      dependency: 0.2,
      network: 0.2,
      build: 0.2
    };
    
    const score = 
      analysis.installPerformance.score * weights.install +
      analysis.cachePerformance.score * weights.cache +
      analysis.dependencyPerformance.score * weights.dependency +
      analysis.networkPerformance.score * weights.network +
      analysis.buildPerformance.score * weights.build;
    
    return Math.round(score);
  }

  // 生成总体优化建议
  generateOverallRecommendations(analysis) {
    const recommendations = [];
    
    // 安装性能建议
    if (analysis.installPerformance.score < 60) {
      recommendations.push('安装性能较差，建议使用更快的镜像源或增加并发数');
    }
    
    // 缓存性能建议
    if (analysis.cachePerformance.score < 80) {
      recommendations.push('缓存使用率不理想，建议优化缓存配置');
    }
    
    // 依赖性能建议
    if (analysis.dependencyPerformance.score < 60) {
      recommendations.push('依赖管理需要改进，建议减少依赖数量或更新过时依赖');
    }
    
    // 网络性能建议
    if (analysis.networkPerformance.score < 60) {
      recommendations.push('网络性能较差，建议使用更快的镜像源或检查网络连接');
    }
    
    // 构建性能建议
    if (analysis.buildPerformance.score < 60) {
      recommendations.push('构建性能较差，建议优化构建脚本或使用增量构建');
    }
    
    return recommendations;
  }

  // 清理环境
  cleanEnvironment() {
    try {
      if (fs.existsSync('node_modules')) {
        execSync('rm -rf node_modules', { stdio: 'pipe' });
      }
      
      if (fs.existsSync('package-lock.json')) {
        fs.unlinkSync('package-lock.json');
      }
    } catch (error) {
      console.error('清理环境失败:', error.message);
    }
  }
}

// 示例10：NPM性能优化综合工具
class NPMPerformanceSuite {
  constructor(projectPath = process.cwd()) {
    this.projectPath = projectPath;
    this.monitor = new NPMPerformanceMonitor();
    this.cacheOptimizer = new NPMCacheOptimizer();
    this.dependencyAnalyzer = new NPMDependencyAnalyzer(projectPath);
    this.networkOptimizer = new NPMNetworkOptimizer();
    this.buildOptimizer = new NPMBuildOptimizer(projectPath);
    this.debugger = new NPMDebugger();
    this.benchmark = new NPMPerformanceBenchmark();
    this.configOptimizer = new NPMConfigOptimizer();
    this.analyzer = new NPMPerformanceAnalyzer();
  }

  // 运行完整性能优化流程
  async runFullOptimization(options = {}) {
    const { 
      analyzeOnly = false, 
      includeBenchmark = false,
      autoApply = false 
    } = options;
    
    console.log('开始NPM性能优化流程...');
    
    const results = {
      timestamp: new Date().toISOString(),
      projectPath: this.projectPath,
      phases: {},
      overallScore: 0,
      recommendations: []
    };
    
    // 阶段1：性能分析
    console.log('\n=== 阶段1: 性能分析 ===');
    results.phases.analysis = this.analyzer.analyzeProjectPerformance(this.projectPath);
    results.overallScore = results.phases.analysis.overallScore;
    
    if (analyzeOnly) {
      console.log('仅分析模式，跳过优化步骤');
      return results;
    }
    
    // 阶段2：配置优化
    console.log('\n=== 阶段2: 配置优化 ===');
    const configDifferences = this.configOptimizer.analyzeConfigDifferences();
    results.phases.config = {
      differences: configDifferences,
      optimized: false
    };
    
    if (autoApply || configDifferences.missing.length > 0 || configDifferences.different.length > 0) {
      console.log('应用配置优化...');
      results.phases.config.optimized = this.configOptimizer.applyRecommendedConfig({ interactive: !autoApply });
    }
    
    // 阶段3：网络优化
    console.log('\n=== 阶段3: 网络优化 ===');
    const bestMirror = await this.networkOptimizer.getBestMirror();
    results.phases.network = {
      bestMirror,
      optimized: false
    };
    
    if (autoApply || (bestMirror && bestMirror.url !== this.networkOptimizer.registry)) {
      console.log('应用网络优化...');
      results.phases.network.optimized = await this.networkOptimizer.setBestMirror();
    }
    
    // 阶段4：缓存优化
    console.log('\n=== 阶段4: 缓存优化 ===');
    const cacheUsage = this.cacheOptimizer.analyzeCacheUsage();
    results.phases.cache = {
      usage: cacheUsage,
      optimized: false
    };
    
    if (autoApply || (cacheUsage && (cacheUsage.usageRate > 80 || cacheUsage.usageRate < 30))) {
      console.log('应用缓存优化...');
      results.phases.cache.optimized = this.cacheOptimizer.optimizeCacheConfig();
    }
    
    // 阶段5：依赖优化
    console.log('\n=== 阶段5: 依赖优化 ===');
    const dependencyAnalysis = this.dependencyAnalyzer.analyzeDependencies();
    results.phases.dependencies = {
      analysis: dependencyAnalysis,
      optimized: false
    };
    
    if (autoApply && dependencyAnalysis.outdatedDependencies > 0) {
      console.log('应用依赖优化...');
      try {
        execSync('npm update', { stdio: 'pipe' });
        results.phases.dependencies.optimized = true;
        console.log('已更新过时依赖');
      } catch (error) {
        console.error('更新依赖失败:', error.message);
      }
    }
    
    // 阶段6：构建优化
    console.log('\n=== 阶段6: 构建优化 ===');
    const buildAnalysis = this.buildOptimizer.analyzeBuildScripts();
    results.phases.build = {
      analysis: buildAnalysis,
      optimized: false
    };
    
    if (buildAnalysis.recommendations && buildAnalysis.recommendations.length > 0) {
      console.log('构建优化建议:');
      buildAnalysis.recommendations.forEach(rec => console.log(`- ${rec}`));
    }
    
    // 阶段7：基准测试（可选）
    if (includeBenchmark) {
      console.log('\n=== 阶段7: 基准测试 ===');
      const packageJson = JSON.parse(fs.readFileSync(
        path.join(this.projectPath, 'package.json'), 'utf8'
      ));
      
      if (packageJson.dependencies && Object.keys(packageJson.dependencies).length > 0) {
        const testPackage = Object.keys(packageJson.dependencies)[0];
        results.phases.benchmark = this.benchmark.benchmarkInstall(testPackage, { 
          clean: true, 
          iterations: 3 
        });
      }
    }
    
    // 重新评估性能
    console.log('\n=== 重新评估性能 ===');
    const finalAnalysis = this.phases.analysis = this.analyzer.analyzeProjectPerformance(this.projectPath);
    results.finalScore = finalAnalysis.overallScore;
    results.improvement = results.finalScore - results.overallScore;
    
    // 生成综合建议
    results.recommendations = this.generateComprehensiveRecommendations(results);
    
    // 保存报告
    const reportPath = path.join(this.projectPath, 'npm-performance-optimization-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(results, null, 2));
    console.log(`\n优化报告已保存到: ${reportPath}`);
    
    console.log(`\n性能优化完成! 初始评分: ${results.overallScore}, 最终评分: ${results.finalScore}, 提升: ${results.improvement}`);
    
    return results;
  }

  // 生成综合优化建议
  generateComprehensiveRecommendations(results) {
    const recommendations = [];
    
    // 从各阶段收集建议
    if (results.phases.analysis && results.phases.analysis.recommendations) {
      recommendations.push(...results.phases.analysis.recommendations);
    }
    
    if (results.phases.build && results.phases.build.analysis && results.phases.build.analysis.recommendations) {
      recommendations.push(...results.phases.build.analysis.recommendations);
    }
    
    // 添加基于结果的建议
    if (results.improvement < 10) {
      recommendations.push('性能提升不明显，建议考虑更深入的优化或检查硬件环境');
    }
    
    if (results.finalScore < 60) {
      recommendations.push('整体性能仍需改进，建议考虑使用更快的包管理器如pnpm');
    }
    
    // 去重
    return [...new Set(recommendations)];
  }
}

// 导出所有类
module.exports = {
  NPMPerformanceMonitor,
  NPMCacheOptimizer,
  NPMDependencyAnalyzer,
  NPMNetworkOptimizer,
  NPMBuildOptimizer,
  NPMDebugger,
  NPMPerformanceBenchmark,
  NPMConfigOptimizer,
  NPMPerformanceAnalyzer,
  NPMPerformanceSuite
};