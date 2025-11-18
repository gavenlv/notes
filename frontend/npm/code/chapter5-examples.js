/**
 * NPM版本管理与发布示例代码
 * 这些示例展示了如何使用NPM进行版本管理和包发布
 */

const fs = require('fs');
const path = require('path');
const semver = require('semver');

// 示例1: 解析和比较语义化版本
function parseAndCompareVersions() {
  console.log('=== 示例1: 解析和比较语义化版本 ===');
  
  // 解析版本号
  const versions = [
    '1.0.0',
    '1.2.3-alpha.1',
    '2.0.0-beta.2',
    '1.2.3+build.123',
    '1.2.3-alpha.1+build.456'
  ];
  
  console.log('版本解析结果:');
  versions.forEach(version => {
    const parsed = semver.parse(version);
    console.log(`  ${version}:`);
    console.log(`    主版本: ${parsed.major}`);
    console.log(`    次版本: ${parsed.minor}`);
    console.log(`    修订号: ${parsed.patch}`);
    if (parsed.prerelease.length > 0) {
      console.log(`    预发布: ${parsed.prerelease.join('.')}`);
    }
    if (parsed.build.length > 0) {
      console.log(`    构建信息: ${parsed.build.join('.')}`);
    }
  });
  
  // 比较版本
  console.log('\n版本比较:');
  const comparisons = [
    ['1.0.0', '1.0.1'],
    ['1.0.0', '1.1.0'],
    ['1.0.0', '2.0.0'],
    ['1.0.0-alpha', '1.0.0'],
    ['1.0.0-alpha', '1.0.0-alpha.1'],
    ['1.0.0-alpha.1', '1.0.0-beta.1'],
    ['1.0.0-beta', '1.0.0']
  ];
  
  comparisons.forEach(([v1, v2]) => {
    const result = semver.compare(v1, v2);
    let comparison;
    if (result < 0) comparison = '<';
    else if (result > 0) comparison = '>';
    else comparison = '=';
    
    console.log(`  ${v1} ${comparison} ${v2}`);
  });
  
  return versions;
}

// 示例2: 版本范围解析
function parseVersionRanges() {
  console.log('\n=== 示例2: 版本范围解析 ===');
  
  const ranges = [
    '1.0.0',          // 精确版本
    '~1.0.0',         // 波浪号范围
    '^1.0.0',         // 插入号范围
    '>1.0.0',         // 大于
    '>=1.0.0',        // 大于等于
    '<2.0.0',         // 小于
    '<=2.0.0',        // 小于等于
    '1.0.0 - 2.0.0',  // 连字符范围
    '1.0.0 || 2.0.0', // 或范围
    '1.0.*',          // 通配符
    '*',              // 任意版本
    '1.0.0-alpha',    // 预发布版本
    '1.x.x'           // x通配符
  ];
  
  const testVersions = [
    '0.9.9',
    '1.0.0',
    '1.0.1',
    '1.2.0',
    '1.2.3',
    '2.0.0',
    '2.1.0',
    '1.0.0-alpha',
    '1.0.0-alpha.1',
    '1.0.0-beta'
  ];
  
  console.log('版本范围匹配结果:');
  ranges.forEach(range => {
    console.log(`\n范围: ${range}`);
    testVersions.forEach(version => {
      const satisfies = semver.satisfies(version, range);
      console.log(`  ${version}: ${satisfies ? '✓' : '✗'}`);
    });
  });
  
  return { ranges, testVersions };
}

// 示例3: 版本号递增
function incrementVersions() {
  console.log('\n=== 示例3: 版本号递增 ===');
  
  const baseVersion = '1.2.3';
  const increments = [
    { type: 'patch', desc: '修订号递增' },
    { type: 'minor', desc: '次版本号递增' },
    { type: 'major', desc: '主版本号递增' },
    { type: 'prerelease', desc: '预发布版本递增' },
    { type: 'premajor', desc: '预发布主版本' },
    { type: 'preminor', desc: '预发布次版本' },
    { type: 'prepatch', desc: '预发布修订版本' }
  ];
  
  console.log(`基础版本: ${baseVersion}`);
  console.log('递增结果:');
  
  increments.forEach(({ type, desc }) => {
    const newVersion = semver.inc(baseVersion, type);
    console.log(`  ${desc} (${type}): ${newVersion}`);
  });
  
  // 使用预发布标识符
  console.log('\n使用预发布标识符:');
  const preIds = ['alpha', 'beta', 'rc'];
  preIds.forEach(preId => {
    const newVersion = semver.inc(baseVersion, 'prerelease', preId);
    console.log(`  prerelease (${preId}): ${newVersion}`);
  });
  
  return baseVersion;
}

// 示例4: 模拟package.json版本管理
function managePackageVersion() {
  console.log('\n=== 示例4: 模拟package.json版本管理 ===');
  
  // 创建模拟的package.json
  const packageJson = {
    name: 'example-package',
    version: '1.0.0',
    description: '一个示例包',
    main: 'index.js',
    scripts: {
      test: 'jest',
      start: 'node index.js',
      preversion: 'npm run test',
      version: 'npm run build',
      postversion: 'npm publish'
    },
    dependencies: {
      express: '^4.18.0',
      lodash: '~4.17.21'
    },
    devDependencies: {
      jest: '^29.0.0',
      eslint: '^8.0.0'
    }
  };
  
  console.log('当前package.json:');
  console.log(JSON.stringify(packageJson, null, 2));
  
  // 模拟版本更新
  console.log('\n模拟版本更新:');
  const newVersion = semver.inc(packageJson.version, 'minor');
  console.log(`版本从 ${packageJson.version} 更新到 ${newVersion}`);
  
  // 更新package.json
  packageJson.version = newVersion;
  
  console.log('\n更新后的package.json:');
  console.log(JSON.stringify(packageJson, null, 2));
  
  // 模拟生命周期脚本执行
  console.log('\n模拟生命周期脚本执行:');
  if (packageJson.scripts.preversion) {
    console.log(`执行 preversion: ${packageJson.scripts.preversion}`);
  }
  if (packageJson.scripts.version) {
    console.log(`执行 version: ${packageJson.scripts.version}`);
  }
  if (packageJson.scripts.postversion) {
    console.log(`执行 postversion: ${packageJson.scripts.postversion}`);
  }
  
  return packageJson;
}

// 示例5: 依赖版本检查
function checkDependencyVersions() {
  console.log('\n=== 示例5: 依赖版本检查 ===');
  
  // 模拟当前安装的依赖版本
  const installedDependencies = {
    express: '4.18.2',
    lodash: '4.17.21',
    jest: '29.6.1',
    eslint: '8.45.0'
  };
  
  // 模拟package.json中定义的依赖版本
  const packageDependencies = {
    express: '^4.18.0',
    lodash: '~4.17.21',
    jest: '^29.0.0',
    eslint: '^8.0.0'
  };
  
  console.log('依赖版本检查结果:');
  
  Object.entries(packageDependencies).forEach(([name, range]) => {
    const installed = installedDependencies[name];
    const satisfies = semver.satisfies(installed, range);
    const latest = getLatestVersion(name); // 模拟获取最新版本
    
    console.log(`\n${name}:`);
    console.log(`  定义版本: ${range}`);
    console.log(`  当前版本: ${installed}`);
    console.log(`  满足范围: ${satisfies ? '✓' : '✗'}`);
    console.log(`  最新版本: ${latest}`);
    
    if (!satisfies) {
      console.log(`  ⚠️  当前版本不满足定义的范围`);
    } else if (semver.lt(installed, latest)) {
      console.log(`  ⚠️  有更新可用`);
    }
  });
  
  return { installedDependencies, packageDependencies };
}

// 模拟获取最新版本
function getLatestVersion(packageName) {
  const versions = {
    express: '4.18.2',
    lodash: '4.17.21',
    jest: '29.6.2',
    eslint: '8.47.0'
  };
  return versions[packageName] || '1.0.0';
}

// 示例6: 版本标签管理
function manageVersionTags() {
  console.log('\n=== 示例6: 版本标签管理 ===');
  
  // 模拟包的版本和标签
  const packageTags = {
    'latest': '1.2.3',
    'stable': '1.2.2',
    'next': '2.0.0-alpha.1',
    'beta': '2.0.0-beta.2',
    'alpha': '2.0.0-alpha.1'
  };
  
  console.log('当前版本标签:');
  Object.entries(packageTags).forEach(([tag, version]) => {
    console.log(`  ${tag}: ${version}`);
  });
  
  // 模拟添加新标签
  console.log('\n添加新标签:');
  packageTags['rc'] = '2.0.0-rc.1';
  console.log(`  rc: ${packageTags['rc']}`);
  
  // 模拟修改标签
  console.log('\n修改标签:');
  packageTags['latest'] = '2.0.0';
  console.log(`  latest: ${packageTags['latest']}`);
  
  // 模拟删除标签
  console.log('\n删除标签:');
  delete packageTags['alpha'];
  console.log('  已删除 alpha 标签');
  
  console.log('\n更新后的版本标签:');
  Object.entries(packageTags).forEach(([tag, version]) => {
    console.log(`  ${tag}: ${version}`);
  });
  
  return packageTags;
}

// 示例7: 发布流程模拟
function simulatePublishProcess() {
  console.log('\n=== 示例7: 发布流程模拟 ===');
  
  // 模拟发布前的检查
  console.log('1. 发布前检查:');
  
  // 检查是否已登录
  const isLoggedIn = Math.random() > 0.5;
  console.log(`   登录状态: ${isLoggedIn ? '已登录' : '未登录'}`);
  if (!isLoggedIn) {
    console.log('   执行 npm login');
  }
  
  // 检查包名是否可用
  const packageName = 'example-package';
  const isPackageAvailable = Math.random() > 0.5;
  console.log(`   包名可用性: ${isPackageAvailable ? '可用' : '已被占用'}`);
  
  // 检查package.json
  console.log('   检查package.json: ✓');
  
  // 检查.npmignore
  console.log('   检查.npmignore: ✓');
  
  // 运行测试
  console.log('2. 运行测试:');
  const testsPassed = Math.random() > 0.2;
  console.log(`   测试结果: ${testsPassed ? '通过' : '失败'}`);
  
  if (!testsPassed) {
    console.log('   测试失败，发布中止');
    return false;
  }
  
  // 构建项目
  console.log('3. 构建项目:');
  console.log('   执行 npm run build: ✓');
  
  // 更新版本
  console.log('4. 更新版本:');
  const currentVersion = '1.2.3';
  const newVersion = semver.inc(currentVersion, 'patch');
  console.log(`   版本从 ${currentVersion} 更新到 ${newVersion}`);
  
  // 发布包
  console.log('5. 发布包:');
  const publishSuccess = Math.random() > 0.1;
  console.log(`   发布结果: ${publishSuccess ? '成功' : '失败'}`);
  
  if (publishSuccess) {
    console.log('6. 发布后操作:');
    console.log('   推送到Git仓库: ✓');
    console.log('   创建Git标签: ✓');
    console.log('   更新文档: ✓');
  }
  
  return publishSuccess;
}

// 示例8: 版本回退与撤销
function handleVersionRollback() {
  console.log('\n=== 示例8: 版本回退与撤销 ===');
  
  // 模拟版本历史
  const versionHistory = [
    { version: '1.0.0', date: '2023-01-01', published: true },
    { version: '1.0.1', date: '2023-01-15', published: true },
    { version: '1.1.0', date: '2023-02-01', published: true },
    { version: '1.1.1', date: '2023-02-15', published: true },
    { version: '1.2.0', date: '2023-03-01', published: true },
    { version: '1.2.1', date: '2023-03-15', published: true },
    { version: '2.0.0', date: '2023-04-01', published: true },
    { version: '2.0.1', date: '2023-04-15', published: true }
  ];
  
  console.log('版本历史:');
  versionHistory.forEach(({ version, date, published }) => {
    console.log(`  ${version} (${date}): ${published ? '已发布' : '未发布'}`);
  });
  
  // 模拟版本回退
  console.log('\n版本回退:');
  const currentVersion = '2.0.1';
  const targetVersion = '1.2.1';
  
  console.log(`当前版本: ${currentVersion}`);
  console.log(`回退到版本: ${targetVersion}`);
  
  // 检查是否可以回退
  const targetExists = versionHistory.some(v => v.version === targetVersion);
  console.log(`目标版本存在: ${targetExists ? '是' : '否'}`);
  
  if (targetExists) {
    console.log('执行版本回退...');
    console.log(`版本已回退到 ${targetVersion}`);
    
    // 发布回退后的版本
    const rollbackVersion = semver.inc(targetVersion, 'patch');
    console.log(`发布回退版本: ${rollbackVersion}`);
  }
  
  // 模拟撤销发布
  console.log('\n撤销发布:');
  const versionToUnpublish = '2.0.1';
  const isRecent = true; // 模拟是否是24小时内发布的版本
  
  console.log(`要撤销的版本: ${versionToUnpublish}`);
  console.log(`是否是最近发布: ${isRecent ? '是' : '否'}`);
  
  if (isRecent) {
    console.log('执行撤销发布...');
    console.log(`版本 ${versionToUnpublish} 已撤销`);
  } else {
    console.log('无法撤销超过24小时的版本');
    console.log('可以考虑弃用版本');
  }
  
  return { versionHistory, currentVersion, targetVersion };
}

// 示例9: 依赖版本冲突解决
function resolveDependencyConflicts() {
  console.log('\n=== 示例9: 依赖版本冲突解决 ===');
  
  // 模拟依赖树
  const dependencyTree = {
    'my-app': {
      version: '1.0.0',
      dependencies: {
        'package-a': '^1.0.0',
        'package-b': '^2.0.0'
      }
    },
    'package-a': {
      version: '1.2.3',
      dependencies: {
        'shared-lib': '^1.0.0'
      }
    },
    'package-b': {
      version: '2.3.4',
      dependencies: {
        'shared-lib': '^2.0.0'
      }
    },
    'shared-lib': {
      '1.0.0': {},
      '2.0.0': {}
    }
  };
  
  console.log('依赖树分析:');
  console.log('my-app@1.0.0');
  console.log('├── package-a@^1.0.0 (实际: 1.2.3)');
  console.log('│   └── shared-lib@^1.0.0 (实际: 1.0.0)');
  console.log('└── package-b@^2.0.0 (实际: 2.3.4)');
  console.log('    └── shared-lib@^2.0.0 (实际: 2.0.0)');
  
  console.log('\n检测到冲突:');
  console.log('shared-lib 被安装了两个版本: 1.0.0 和 2.0.0');
  
  // 解决方案1: 更新依赖
  console.log('\n解决方案1: 更新依赖');
  console.log('检查 package-a 是否兼容 shared-lib@2.0.0');
  const isCompatible = Math.random() > 0.5;
  console.log(`兼容性: ${isCompatible ? '兼容' : '不兼容'}`);
  
  if (isCompatible) {
    console.log('更新 package-a 的依赖: shared-lib@^2.0.0');
    console.log('重新安装依赖，消除重复');
  } else {
    // 解决方案2: 使用resolutions
    console.log('\n解决方案2: 使用resolutions');
    console.log('在package.json中添加resolutions字段:');
    console.log(JSON.stringify({
      resolutions: {
        'shared-lib': '1.0.0'
      }
    }, null, 2));
    console.log('强制所有依赖使用shared-lib@1.0.0');
  }
  
  return dependencyTree;
}

// 示例10: 自动化版本管理
function automateVersionManagement() {
  console.log('\n=== 示例10: 自动化版本管理 ===');
  
  // 模拟Git提交信息
  const commits = [
    { message: 'feat: add new feature', hash: 'abc123' },
    { message: 'fix: resolve bug in authentication', hash: 'def456' },
    { message: 'docs: update README', hash: 'ghi789' },
    { message: 'refactor: improve code structure', hash: 'jkl012' },
    { message: 'BREAKING CHANGE: change API interface', hash: 'mno345' }
  ];
  
  console.log('Git提交历史:');
  commits.forEach(({ message, hash }) => {
    console.log(`  ${hash}: ${message}`);
  });
  
  // 分析提交类型
  console.log('\n分析提交类型:');
  const commitTypes = {
    feat: 0,
    fix: 0,
    docs: 0,
    refactor: 0,
    breaking: 0
  };
  
  commits.forEach(({ message }) => {
    if (message.includes('BREAKING CHANGE')) {
      commitTypes.breaking++;
    } else if (message.startsWith('feat:')) {
      commitTypes.feat++;
    } else if (message.startsWith('fix:')) {
      commitTypes.fix++;
    } else if (message.startsWith('docs:')) {
      commitTypes.docs++;
    } else if (message.startsWith('refactor:')) {
      commitTypes.refactor++;
    }
  });
  
  Object.entries(commitTypes).forEach(([type, count]) => {
    console.log(`  ${type}: ${count}`);
  });
  
  // 根据提交类型确定版本递增
  console.log('\n确定版本递增:');
  let incrementType;
  if (commitTypes.breaking > 0) {
    incrementType = 'major';
    console.log('  检测到破坏性变更，递增主版本号');
  } else if (commitTypes.feat > 0) {
    incrementType = 'minor';
    console.log('  检测到新功能，递增次版本号');
  } else if (commitTypes.fix > 0) {
    incrementType = 'patch';
    console.log('  检测到修复，递增修订号');
  } else {
    console.log('  没有检测到需要版本变更的提交');
    return;
  }
  
  // 计算新版本号
  const currentVersion = '1.2.3';
  const newVersion = semver.inc(currentVersion, incrementType);
  console.log(`  版本从 ${currentVersion} 更新到 ${newVersion}`);
  
  // 生成变更日志
  console.log('\n生成变更日志:');
  console.log(`## [${newVersion}] - ${new Date().toISOString().split('T')[0]}`);
  
  if (commitTypes.breaking > 0) {
    console.log('\n### BREAKING CHANGES');
    commits
      .filter(({ message }) => message.includes('BREAKING CHANGE'))
      .forEach(({ message, hash }) => {
        console.log(`- ${message} (${hash})`);
      });
  }
  
  if (commitTypes.feat > 0) {
    console.log('\n### Features');
    commits
      .filter(({ message }) => message.startsWith('feat:'))
      .forEach(({ message, hash }) => {
        console.log(`- ${message.replace('feat: ', '')} (${hash})`);
      });
  }
  
  if (commitTypes.fix > 0) {
    console.log('\n### Bug Fixes');
    commits
      .filter(({ message }) => message.startsWith('fix:'))
      .forEach(({ message, hash }) => {
        console.log(`- ${message.replace('fix: ', '')} (${hash})`);
      });
  }
  
  return { commits, incrementType, newVersion };
}

// 主函数
function main() {
  console.log('NPM版本管理与发布示例');
  console.log('========================');
  
  // 执行各种示例
  parseAndCompareVersions();
  parseVersionRanges();
  incrementVersions();
  managePackageVersion();
  checkDependencyVersions();
  manageVersionTags();
  simulatePublishProcess();
  handleVersionRollback();
  resolveDependencyConflicts();
  automateVersionManagement();
  
  console.log('\n所有示例执行完成！');
}

// 运行主函数
if (require.main === module) {
  main();
}

module.exports = {
  parseAndCompareVersions,
  parseVersionRanges,
  incrementVersions,
  managePackageVersion,
  checkDependencyVersions,
  manageVersionTags,
  simulatePublishProcess,
  handleVersionRollback,
  resolveDependencyConflicts,
  automateVersionManagement
};