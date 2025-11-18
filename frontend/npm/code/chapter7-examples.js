// NPM安全与最佳实践代码示例

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 示例1：解析npm audit输出
function parseAuditOutput(auditOutput) {
  const lines = auditOutput.split('\n');
  const vulnerabilities = [];
  let currentVuln = null;
  
  for (const line of lines) {
    if (line.includes('│') && !line.includes('─')) {
      const parts = line.split('│').map(p => p.trim()).filter(p => p);
      if (parts.length >= 2) {
        const key = parts[0];
        const value = parts[1];
        
        if (key === 'Moderate' || key === 'High' || key === 'Low' || key === 'Critical') {
          if (currentVuln) vulnerabilities.push(currentVuln);
          currentVuln = { severity: key, title: value };
        } else if (currentVuln && key) {
          currentVuln[key.toLowerCase()] = value;
        }
      }
    }
  }
  
  if (currentVuln) vulnerabilities.push(currentVuln);
  return vulnerabilities;
}

// 示例2：模拟安全审计
function simulateSecurityAudit(packageJson) {
  const vulnerabilities = [];
  const checkVulnerability = (name, version, severity, title, patchedIn) => {
    if (Math.random() > 0.7) { // 30%概率存在漏洞
      vulnerabilities.push({
        package: name,
        version,
        severity,
        title,
        patchedIn
      });
    }
  };
  
  // 检查常见依赖包的漏洞
  if (packageJson.dependencies) {
    for (const [name, version] of Object.entries(packageJson.dependencies)) {
      if (name === 'lodash') {
        checkVulnerability(name, version, 'high', 'Prototype Pollution', '>=4.17.19');
      } else if (name === 'request') {
        checkVulnerability(name, version, 'moderate', 'Server-Side Request Forgery', '>=2.88.0');
      } else if (name === 'axios') {
        checkVulnerability(name, version, 'low', 'Denial of Service', '>=0.21.1');
      }
    }
  }
  
  return vulnerabilities;
}

// 示例3：生成安全报告
function generateSecurityReport(vulnerabilities) {
  const severityCounts = {
    low: 0,
    moderate: 0,
    high: 0,
    critical: 0
  };
  
  vulnerabilities.forEach(vuln => {
    severityCounts[vuln.severity.toLowerCase()]++;
  });
  
  const report = {
    summary: {
      total: vulnerabilities.length,
      ...severityCounts
    },
    vulnerabilities
  };
  
  return report;
}

// 示例4：包完整性验证
function verifyPackageIntegrity(packageName, expectedShasum) {
  try {
    // 模拟包下载和校验
    const actualShasum = Math.random().toString(36).substring(2); // 模拟校验和
    const isValid = actualShasum === expectedShasum;
    
    return {
      package: packageName,
      expectedShasum,
      actualShasum,
      isValid,
      timestamp: new Date().toISOString()
    };
  } catch (error) {
    return {
      package: packageName,
      error: error.message,
      isValid: false
    };
  }
}

// 示例5：依赖树分析
function analyzeDependencyTree(packageJson) {
  const directDeps = Object.keys(packageJson.dependencies || {});
  const devDeps = Object.keys(packageJson.devDependencies || {});
  const peerDeps = Object.keys(packageJson.peerDependencies || {});
  
  // 模拟获取间接依赖
  const getIndirectDeps = (depName) => {
    const indirectCount = Math.floor(Math.random() * 10) + 1;
    const indirectDeps = [];
    
    for (let i = 0; i < indirectCount; i++) {
      indirectDeps.push(`${depName}-dep-${i}@${Math.floor(Math.random() * 5) + 1}.0.0`);
    }
    
    return indirectDeps;
  };
  
  const dependencyTree = {
    direct: directDeps,
    dev: devDeps,
    peer: peerDeps,
    indirect: {}
  };
  
  directDeps.forEach(dep => {
    dependencyTree.indirect[dep] = getIndirectDeps(dep);
  });
  
  return dependencyTree;
}

// 示例6：安全评分计算
function calculateSecurityScore(securityReport) {
  const { total, low, moderate, high, critical } = securityReport.summary;
  
  if (total === 0) return 100; // 无漏洞，满分
  
  // 根据漏洞严重程度计算扣分
  const deductions = {
    low: low * 1,
    moderate: moderate * 5,
    high: high * 10,
    critical: critical * 25
  };
  
  const totalDeductions = Object.values(deductions).reduce((sum, val) => sum + val, 0);
  const score = Math.max(0, 100 - totalDeductions);
  
  return {
    score,
    grade: score >= 90 ? 'A' : score >= 80 ? 'B' : score >= 70 ? 'C' : score >= 60 ? 'D' : 'F',
    deductions,
    recommendations: getRecommendations(securityReport)
  };
}

function getRecommendations(securityReport) {
  const recommendations = [];
  const { critical, high, moderate, low } = securityReport.summary;
  
  if (critical > 0) {
    recommendations.push('立即修复所有严重漏洞，即使需要破坏性更改');
  }
  
  if (high > 0) {
    recommendations.push('尽快修复高危漏洞，评估影响后实施');
  }
  
  if (moderate > 0) {
    recommendations.push('计划修复中危漏洞，在下次更新周期中处理');
  }
  
  if (low > 0) {
    recommendations.push('可以在下次主要更新时处理低危漏洞');
  }
  
  if (securityReport.vulnerabilities.length > 10) {
    recommendations.push('考虑使用依赖管理工具简化依赖更新');
  }
  
  return recommendations;
}

// 示例7：安全策略检查
function checkSecurityPolicies(packageJson) {
  const policies = {
    hasScripts: !!(packageJson.scripts && Object.keys(packageJson.scripts).length > 0),
    hasEngines: !!(packageJson.engines && Object.keys(packageJson.engines).length > 0),
    hasPrivate: packageJson.private === true,
    hasLicense: !!packageJson.license,
    hasRepository: !!(packageJson.repository && (typeof packageJson.repository === 'string' || packageJson.repository.url)),
    hasDependencies: !!(packageJson.dependencies && Object.keys(packageJson.dependencies).length > 0),
    hasDevDependencies: !!(packageJson.devDependencies && Object.keys(packageJson.devDependencies).length > 0),
    usesExactVersions: checkExactVersions(packageJson.dependencies),
    usesRangeVersions: checkRangeVersions(packageJson.dependencies)
  };
  
  const score = Object.values(policies).filter(Boolean).length;
  const total = Object.keys(policies).length;
  
  return {
    policies,
    score,
    total,
    percentage: Math.round((score / total) * 100)
  };
}

function checkExactVersions(dependencies) {
  if (!dependencies) return false;
  return Object.values(dependencies).every(version => /^[0-9]+\.[0-9]+\.[0-9]+$/.test(version));
}

function checkRangeVersions(dependencies) {
  if (!dependencies) return false;
  return Object.values(dependencies).some(version => /[\^~]/.test(version));
}

// 示例8：安全配置生成
function generateSecurityConfig() {
  const npmrc = `
# 安全配置
audit=true
audit-level=moderate
fund=false

# 注册表配置
registry=https://registry.npmjs.org/

# 认证配置
//registry.npmjs.org/:_authToken=\${NPM_TOKEN}

# 作用域包配置
@mycompany:registry=https://npm.mycompany.com/
//npm.mycompany.com/:_authToken=\${COMPANY_NPM_TOKEN}
`;

  const packageJsonScripts = {
    "audit": "npm audit",
    "audit:fix": "npm audit fix",
    "audit:json": "npm audit --json",
    "security-check": "npm audit --audit-level moderate",
    "deps-check": "npm outdated",
    "deps-update": "npm update",
    "security-report": "npm audit --json > security-report.json"
  };
  
  const ciConfig = `
name: Security Check

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 6 * * 1' # 每周一早上6点

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run security audit
      run: npm audit --audit-level moderate
    
    - name: Run Snyk to check for vulnerabilities
      uses: snyk/actions/node@master
      env:
        SNYK_TOKEN: \${{ secrets.SNYK_TOKEN }}
`;
  
  return {
    npmrc,
    packageJsonScripts,
    ciConfig
  };
}

// 示例9：漏洞修复建议
function suggestVulnerabilityFixes(vulnerabilities) {
  const fixes = {};
  
  vulnerabilities.forEach(vuln => {
    const { package: pkg, severity, patchedIn } = vuln;
    
    if (!fixes[pkg]) {
      fixes[pkg] = {
        currentVersion: vuln.version,
        severity,
        recommendedVersion: patchedIn,
        fixCommand: `npm install ${pkg}@${patchedIn}`,
        autoFixable: severity !== 'critical' && Math.random() > 0.3 // 模拟是否可自动修复
      };
    } else {
      // 如果同一包有多个漏洞，保留最严重的
      if (getSeverityLevel(severity) > getSeverityLevel(fixes[pkg].severity)) {
        fixes[pkg].severity = severity;
        fixes[pkg].recommendedVersion = patchedIn;
        fixes[pkg].fixCommand = `npm install ${pkg}@${patchedIn}`;
      }
    }
  });
  
  return fixes;
}

function getSeverityLevel(severity) {
  const levels = { low: 1, moderate: 2, high: 3, critical: 4 };
  return levels[severity.toLowerCase()] || 0;
}

// 示例10：安全监控设置
function setupSecurityMonitoring() {
  const monitoringScript = `
const { execSync } = require('child_process');
const fs = require('fs');

// 运行安全审计
function runSecurityAudit() {
  try {
    const auditOutput = execSync('npm audit --json', { encoding: 'utf8' });
    const auditResult = JSON.parse(auditOutput);
    
    if (auditResult.vulnerabilities && Object.keys(auditResult.vulnerabilities).length > 0) {
      // 发送警报
      sendAlert(auditResult);
      
      // 记录到日志
      logSecurityIssue(auditResult);
    }
    
    return auditResult;
  } catch (error) {
    console.error('Security audit failed:', error);
    return null;
  }
}

// 发送警报
function sendAlert(auditResult) {
  // 实现警报逻辑，如发送邮件、Slack通知等
  console.log('SECURITY ALERT:', JSON.stringify(auditResult, null, 2));
}

// 记录安全问题
function logSecurityIssue(auditResult) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    vulnerabilities: auditResult.vulnerabilities
  };
  
  fs.appendFileSync('security-log.json', JSON.stringify(logEntry) + '\\n');
}

// 定期执行安全检查
setInterval(runSecurityAudit, 24 * 60 * 60 * 1000); // 每天执行一次

// 立即执行一次
runSecurityAudit();
`;
  
  const dockerfile = `
FROM node:18-alpine

# 安装安全工具
RUN npm install -g snyk
RUN npm install -g npm-audit-resolver

# 设置工作目录
WORKDIR /app

# 复制package文件
COPY package*.json ./

# 安装依赖
RUN npm ci --only=production

# 运行安全扫描
RUN snyk test || true
RUN npm audit --audit-level moderate || true

# 复制应用代码
COPY . .

# 创建非root用户
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# 暴露端口
EXPOSE 3000

# 启动应用
CMD ["node", "server.js"]
`;
  
  return {
    monitoringScript,
    dockerfile
  };
}

// 导出所有示例函数
module.exports = {
  parseAuditOutput,
  simulateSecurityAudit,
  generateSecurityReport,
  verifyPackageIntegrity,
  analyzeDependencyTree,
  calculateSecurityScore,
  checkSecurityPolicies,
  generateSecurityConfig,
  suggestVulnerabilityFixes,
  setupSecurityMonitoring
};

// 示例使用
if (require.main === module) {
  // 模拟一个package.json
  const samplePackageJson = {
    name: "secure-app",
    version: "1.0.0",
    dependencies: {
      "express": "^4.17.1",
      "lodash": "^4.17.15", // 有漏洞的版本
      "axios": "^0.21.0"     // 有漏洞的版本
    },
    devDependencies: {
      "jest": "^27.0.0"
    },
    scripts: {
      "start": "node server.js",
      "test": "jest"
    },
    engines: {
      "node": ">=14.0.0"
    },
    private: true,
    license: "MIT"
  };
  
  // 运行安全审计
  const vulnerabilities = simulateSecurityAudit(samplePackageJson);
  console.log("发现的安全漏洞:", vulnerabilities);
  
  // 生成安全报告
  const securityReport = generateSecurityReport(vulnerabilities);
  console.log("\n安全报告:", JSON.stringify(securityReport, null, 2));
  
  // 计算安全评分
  const securityScore = calculateSecurityScore(securityReport);
  console.log("\n安全评分:", securityScore);
  
  // 检查安全策略
  const securityPolicies = checkSecurityPolicies(samplePackageJson);
  console.log("\n安全策略检查:", securityPolicies);
  
  // 获取修复建议
  const fixes = suggestVulnerabilityFixes(vulnerabilities);
  console.log("\n修复建议:", JSON.stringify(fixes, null, 2));
}