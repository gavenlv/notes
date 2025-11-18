// Nexus配置代码示例
// 本文件包含多个Nexus配置的实际代码示例，演示如何安全地配置多个Nexus仓库

// 示例1: 基本的多仓库配置
// ==========================
// 作用域配置示例
const basicMultiRepoConfig = `
# 基本的多仓库配置
registry=https://registry.npmjs.org/

# 公司内部包配置
@company:registry=https://nexus.company.com/repository/npm-private/
@company:always-auth=true

# 特定项目包配置
@project:registry=https://nexus.company.com/repository/npm-project/
@project:always-auth=true

# 第三方镜像配置
@thirdparty:registry=https://nexus.company.com/repository/npm-proxy/
`;

// 示例2: 环境变量配置
// ====================
// 使用环境变量的配置示例
const envVarConfig = `
# 使用环境变量的配置
@company:registry=https://nexus.company.com/repository/npm-private/
@company:_authToken=${NEXUS_COMPANY_AUTH_TOKEN}

@project:registry=https://nexus.company.com/repository/npm-project/
@project:_authToken=${NEXUS_PROJECT_AUTH_TOKEN}
`;

// 示例3: 生成认证Token的脚本
// ==========================
/**
 * 生成Base64编码的认证Token
 * @param {string} username - 用户名
 * @param {string} password - 密码
 * @returns {string} Base64编码的认证Token
 */
function generateAuthToken(username, password) {
  const authString = `${username}:${password}`;
  return Buffer.from(authString).toString('base64');
}

// 示例4: 环境变量设置脚本 (Windows PowerShell)
// ============================================
const windowsPowerShellScript = `
# Windows PowerShell环境变量设置脚本
# 设置用户名和密码
$env:NEXUS_COMPANY_USERNAME = "company-user"
$env:NEXUS_COMPANY_PASSWORD = "secure-password"
$env:NEXUS_PROJECT_USERNAME = "project-user"
$env:NEXUS_PROJECT_PASSWORD = "another-secure-password"

# 生成Base64编码的认证Token
$env:NEXUS_COMPANY_AUTH_TOKEN = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("$($env:NEXUS_COMPANY_USERNAME):$($env:NEXUS_COMPANY_PASSWORD)"))
$env:NEXUS_PROJECT_AUTH_TOKEN = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("$($env:NEXUS_PROJECT_USERNAME):$($env:NEXUS_PROJECT_PASSWORD)"))

# 持久化环境变量
[System.Environment]::SetEnvironmentVariable('NEXUS_COMPANY_USERNAME', $env:NEXUS_COMPANY_USERNAME, 'User')
[System.Environment]::SetEnvironmentVariable('NEXUS_COMPANY_PASSWORD', $env:NEXUS_COMPANY_PASSWORD, 'User')
[System.Environment]::SetEnvironmentVariable('NEXUS_PROJECT_USERNAME', $env:NEXUS_PROJECT_USERNAME, 'User')
[System.Environment]::SetEnvironmentVariable('NEXUS_PROJECT_PASSWORD', $env:NEXUS_PROJECT_PASSWORD, 'User')
`;

// 示例5: 环境变量设置脚本 (Linux/macOS)
// =====================================
const linuxMacOSScript = `
# Linux/macOS环境变量设置脚本
# 设置用户名和密码
export NEXUS_COMPANY_USERNAME="company-user"
export NEXUS_COMPANY_PASSWORD="secure-password"
export NEXUS_PROJECT_USERNAME="project-user"
export NEXUS_PROJECT_PASSWORD="another-secure-password"

# 生成Base64编码的认证Token
export NEXUS_COMPANY_AUTH_TOKEN=$(echo -n "${NEXUS_COMPANY_USERNAME}:${NEXUS_COMPANY_PASSWORD}" | base64)
export NEXUS_PROJECT_AUTH_TOKEN=$(echo -n "${NEXUS_PROJECT_USERNAME}:${NEXUS_PROJECT_PASSWORD}" | base64)

# 添加到 ~/.bashrc 或 ~/.zshrc
echo "export NEXUS_COMPANY_USERNAME=\\"$NEXUS_COMPANY_USERNAME\\"" >> ~/.bashrc
echo "export NEXUS_COMPANY_PASSWORD=\\"$NEXUS_COMPANY_PASSWORD\\"" >> ~/.bashrc
echo "export NEXUS_PROJECT_USERNAME=\\"$NEXUS_PROJECT_USERNAME\\"" >> ~/.bashrc
echo "export NEXUS_PROJECT_PASSWORD=\\"$NEXUS_PROJECT_PASSWORD\\"" >> ~/.bashrc
echo "export NEXUS_COMPANY_AUTH_TOKEN=\\"$NEXUS_COMPANY_AUTH_TOKEN\\"" >> ~/.bashrc
echo "export NEXUS_PROJECT_AUTH_TOKEN=\\"$NEXUS_PROJECT_AUTH_TOKEN\\"" >> ~/.bashrc
`;

// 示例6: .npmrc文件切换脚本
// ==========================
/**
 * 切换不同环境的.npmrc文件
 * @param {string} env - 环境名称 (dev, staging, prod)
 */
function switchNpmrc(env) {
  const fs = require('fs');
  const path = require('path');
  
  const npmrcPath = path.join(process.cwd(), '.npmrc');
  const envNpmrcPath = path.join(process.cwd(), `.npmrc.${env}`);
  
  if (!fs.existsSync(envNpmrcPath)) {
    console.error(`.npmrc.${env} file not found`);
    return false;
  }
  
  try {
    fs.copyFileSync(envNpmrcPath, npmrcPath);
    console.log(`Switched to ${env} npmrc`);
    return true;
  } catch (error) {
    console.error(`Failed to switch npmrc: ${error.message}`);
    return false;
  }
}

// 示例7: Vault集成脚本
// =====================
/**
 * 从Vault获取Nexus认证信息并配置NPM
 */
async function setupNpmWithVault() {
  const https = require('https');
  const fs = require('fs');
  const path = require('path');
  
  // Vault配置
  const vaultUrl = process.env.VAULT_ADDR || 'https://vault.company.com';
  const vaultToken = process.env.VAULT_TOKEN;
  
  if (!vaultToken) {
    console.error('VAULT_TOKEN environment variable is required');
    return false;
  }
  
  try {
    // 从Vault获取公司仓库认证信息
    const companyCreds = await getVaultSecret(vaultUrl, vaultToken, 'secret/nexus/company');
    
    // 从Vault获取项目仓库认证信息
    const projectCreds = await getVaultSecret(vaultUrl, vaultToken, 'secret/nexus/project');
    
    // 生成Base64编码的认证Token
    const companyAuthToken = Buffer.from(`${companyCreds.username}:${companyCreds.password}`).toString('base64');
    const projectAuthToken = Buffer.from(`${projectCreds.username}:${projectCreds.password}`).toString('base64');
    
    // 创建.npmrc内容
    const npmrcContent = `
@company:registry=https://nexus.company.com/repository/npm-private/
@company:_authToken=${companyAuthToken}

@project:registry=https://nexus.company.com/repository/npm-project/
@project:_authToken=${projectAuthToken}
`;
    
    // 写入.npmrc文件
    const npmrcPath = path.join(process.env.HOME, '.npmrc');
    fs.writeFileSync(npmrcPath, npmrcContent.trim());
    
    console.log('NPM authentication configured successfully using Vault');
    return true;
  } catch (error) {
    console.error(`Failed to configure NPM with Vault: ${error.message}`);
    return false;
  }
}

/**
 * 从Vault获取密钥
 * @param {string} vaultUrl - Vault服务器URL
 * @param {string} vaultToken - Vault认证Token
 * @param {string} secretPath - 密钥路径
 * @returns {Promise<Object>} 密钥对象
 */
function getVaultSecret(vaultUrl, vaultToken, secretPath) {
  return new Promise((resolve, reject) => {
    const url = `${vaultUrl}/v1/${secretPath}`;
    const options = {
      headers: {
        'X-Vault-Token': vaultToken
      }
    };
    
    const req = https.get(url, options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const response = JSON.parse(data);
          if (res.statusCode === 200) {
            resolve(response.data.data);
          } else {
            reject(new Error(`Vault API error: ${response.errors ? response.errors.join(', ') : 'Unknown error'}`));
          }
        } catch (error) {
          reject(new Error(`Failed to parse Vault response: ${error.message}`));
        }
      });
    });
    
    req.on('error', (error) => {
      reject(new Error(`Failed to connect to Vault: ${error.message}`));
    });
    
    req.end();
  });
}

// 示例8: AWS Secrets Manager集成
// ==============================
/**
 * 从AWS Secrets Manager获取Nexus认证信息并配置NPM
 */
async function setupNpmWithAWSSecrets() {
  const AWS = require('aws-sdk');
  const fs = require('fs');
  const path = require('path');
  
  // 初始化Secrets Manager客户端
  const secretsManager = new AWS.SecretsManager();
  
  try {
    // 获取公司仓库认证信息
    const companyCreds = await getSecret(secretsManager, 'nexus/company');
    
    // 获取项目仓库认证信息
    const projectCreds = await getSecret(secretsManager, 'nexus/project');
    
    // 生成Base64编码的认证Token
    const companyAuthToken = Buffer.from(`${companyCreds.username}:${companyCreds.password}`).toString('base64');
    const projectAuthToken = Buffer.from(`${projectCreds.username}:${projectCreds.password}`).toString('base64');
    
    // 创建.npmrc内容
    const npmrcContent = `
@company:registry=https://nexus.company.com/repository/npm-private/
@company:_authToken=${companyAuthToken}

@project:registry=https://nexus.company.com/repository/npm-project/
@project:_authToken=${projectAuthToken}
`;
    
    // 写入.npmrc文件
    const npmrcPath = path.join(process.env.HOME, '.npmrc');
    fs.writeFileSync(npmrcPath, npmrcContent.trim());
    
    console.log('NPM authentication configured successfully using AWS Secrets Manager');
    return true;
  } catch (error) {
    console.error(`Failed to configure NPM with AWS Secrets Manager: ${error.message}`);
    return false;
  }
}

/**
 * 从AWS Secrets Manager获取密钥
 * @param {AWS.SecretsManager} secretsManager - Secrets Manager客户端
 * @param {string} secretName - 密钥名称
 * @returns {Promise<Object>} 密钥对象
 */
function getSecret(secretsManager, secretName) {
  return new Promise((resolve, reject) => {
    secretsManager.getSecretValue({ SecretId: secretName }, (err, data) => {
      if (err) {
        reject(err);
      } else {
        if ('SecretString' in data) {
          resolve(JSON.parse(data.SecretString));
        } else {
          const buff = Buffer.from(data.SecretBinary, 'base64');
          resolve(JSON.parse(buff.toString('ascii')));
        }
      }
    });
  });
}

// 示例9: Docker Secrets集成
// ==========================
/**
 * 从Docker Secrets获取Nexus认证信息并配置NPM
 */
function setupNpmWithDockerSecrets() {
  const fs = require('fs');
  const path = require('path');
  
  // Docker Secrets路径
  const secretsDir = '/run/secrets';
  
  try {
    // 从Docker Secrets读取认证信息
    const companyUsername = fs.readFileSync(path.join(secretsDir, 'nexus_company_username'), 'utf8').trim();
    const companyPassword = fs.readFileSync(path.join(secretsDir, 'nexus_company_password'), 'utf8').trim();
    const projectUsername = fs.readFileSync(path.join(secretsDir, 'nexus_project_username'), 'utf8').trim();
    const projectPassword = fs.readFileSync(path.join(secretsDir, 'nexus_project_password'), 'utf8').trim();
    
    // 生成Base64编码的认证Token
    const companyAuthToken = Buffer.from(`${companyUsername}:${companyPassword}`).toString('base64');
    const projectAuthToken = Buffer.from(`${projectUsername}:${projectPassword}`).toString('base64');
    
    // 创建.npmrc内容
    const npmrcContent = `
@company:registry=https://nexus.company.com/repository/npm-private/
@company:_authToken=${companyAuthToken}

@project:registry=https://nexus.company.com/repository/npm-project/
@project:_authToken=${projectAuthToken}
`;
    
    // 写入.npmrc文件
    const npmrcPath = path.join(process.env.HOME, '.npmrc');
    fs.writeFileSync(npmrcPath, npmrcContent.trim());
    
    console.log('NPM authentication configured successfully using Docker Secrets');
    return true;
  } catch (error) {
    console.error(`Failed to configure NPM with Docker Secrets: ${error.message}`);
    return false;
  }
}

// 示例10: CI/CD配置示例
// ======================
// GitHub Actions配置示例
const githubActionsConfig = `
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '16'
          
      - name: Configure NPM
        run: |
          echo "@company:registry=https://nexus.company.com/repository/npm-private/" >> ~/.npmrc
          echo "@company:_authToken=\${{ secrets.NEXUS_COMPANY_AUTH_TOKEN }}" >> ~/.npmrc
          echo "@project:registry=https://nexus.company.com/repository/npm-project/" >> ~/.npmrc
          echo "@project:_authToken=\${{ secrets.NEXUS_PROJECT_AUTH_TOKEN }}" >> ~/.npmrc
          
      - name: Install dependencies
        run: npm ci
        
      - name: Run tests
        run: npm test
`;

// Jenkins配置示例
const jenkinsConfig = `
// Jenkinsfile
pipeline {
    agent any
    
    environment {
        NEXUS_COMPANY_AUTH_TOKEN = credentials('nexus-company-auth-token')
        NEXUS_PROJECT_AUTH_TOKEN = credentials('nexus-project-auth-token')
    }
    
    stages {
        stage('Setup') {
            steps {
                sh '''
                    echo "@company:registry=https://nexus.company.com/repository/npm-private/" >> ~/.npmrc
                    echo "@company:_authToken=${NEXUS_COMPANY_AUTH_TOKEN}" >> ~/.npmrc
                    echo "@project:registry=https://nexus.company.com/repository/npm-project/" >> ~/.npmrc
                    echo "@project:_authToken=${NEXUS_PROJECT_AUTH_TOKEN}" >> ~/.npmrc
                '''
            }
        }
        
        stage('Install') {
            steps {
                sh 'npm ci'
            }
        }
        
        stage('Test') {
            steps {
                sh 'npm test'
            }
        }
    }
}
`;

// 导出所有示例
module.exports = {
  basicMultiRepoConfig,
  envVarConfig,
  generateAuthToken,
  windowsPowerShellScript,
  linuxMacOSScript,
  switchNpmrc,
  setupNpmWithVault,
  getVaultSecret,
  setupNpmWithAWSSecrets,
  getSecret,
  setupNpmWithDockerSecrets,
  githubActionsConfig,
  jenkinsConfig
};

// 使用示例
// ========
// 1. 生成认证Token
// const token = generateAuthToken('username', 'password');
// console.log(token);

// 2. 切换环境配置
// switchNpmrc('dev');

// 3. 使用Vault配置
// setupNpmWithVault().then(success => {
//   console.log(success ? 'Success' : 'Failed');
// });

// 4. 使用AWS Secrets Manager配置
// setupNpmWithAWSSecrets().then(success => {
//   console.log(success ? 'Success' : 'Failed');
// });

// 5. 使用Docker Secrets配置
// setupNpmWithDockerSecrets();