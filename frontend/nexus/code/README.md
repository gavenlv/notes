# Nexus配置示例

本目录包含多个Nexus配置的实际代码示例，演示如何安全地配置多个Nexus仓库。

## 文件说明

### nexus-config-examples.js
包含以下示例代码：

1. **基本的多仓库配置** - 演示如何配置多个Nexus仓库
2. **环境变量配置** - 使用环境变量存储敏感信息
3. **生成认证Token的脚本** - 生成Base64编码的认证Token
4. **环境变量设置脚本** - Windows PowerShell和Linux/macOS环境变量设置
5. **.npmrc文件切换脚本** - 在不同环境间切换配置
6. **Vault集成脚本** - 使用HashiCorp Vault管理密钥
7. **AWS Secrets Manager集成** - 使用AWS Secrets Manager管理密钥
8. **Docker Secrets集成** - 在Docker环境中安全使用密钥
9. **CI/CD配置示例** - GitHub Actions和Jenkins配置示例

## 使用方法

### 基本配置

1. 复制基本配置示例到你的`.npmrc`文件：
```bash
registry=https://registry.npmjs.org/

@company:registry=https://nexus.company.com/repository/npm-private/
@company:always-auth=true

@project:registry=https://nexus.company.com/repository/npm-project/
@project:always-auth=true
```

### 使用环境变量

1. 设置环境变量：
```bash
# Linux/macOS
export NEXUS_COMPANY_USERNAME="company-user"
export NEXUS_COMPANY_PASSWORD="secure-password"
export NEXUS_PROJECT_USERNAME="project-user"
export NEXUS_PROJECT_PASSWORD="another-secure-password"

# 生成Base64编码的认证Token
export NEXUS_COMPANY_AUTH_TOKEN=$(echo -n "${NEXUS_COMPANY_USERNAME}:${NEXUS_COMPANY_PASSWORD}" | base64)
export NEXUS_PROJECT_AUTH_TOKEN=$(echo -n "${NEXUS_PROJECT_USERNAME}:${NEXUS_PROJECT_PASSWORD}" | base64)
```

2. 在`.npmrc`文件中使用环境变量：
```
@company:registry=https://nexus.company.com/repository/npm-private/
@company:_authToken=${NEXUS_COMPANY_AUTH_TOKEN}

@project:registry=https://nexus.company.com/repository/npm-project/
@project:_authToken=${NEXUS_PROJECT_AUTH_TOKEN}
```

### 使用Vault集成

1. 安装依赖：
```bash
npm install
```

2. 设置环境变量：
```bash
export VAULT_ADDR="https://vault.company.com"
export VAULT_TOKEN="your-vault-token"
```

3. 运行脚本：
```bash
node -e "require('./nexus-config-examples.js').setupNpmWithVault()"
```

### 使用AWS Secrets Manager

1. 安装AWS SDK：
```bash
npm install aws-sdk
```

2. 配置AWS凭证：
```bash
aws configure
```

3. 运行脚本：
```bash
node -e "require('./nexus-config-examples.js').setupNpmWithAWSSecrets()"
```

## 安全注意事项

1. **不要将密码硬编码在代码中** - 始终使用环境变量或密钥管理系统
2. **限制.npmrc文件的权限** - 确保只有用户可以读取文件：
   ```bash
   chmod 600 ~/.npmrc
   ```
3. **定期轮换密码** - 定期更新Nexus仓库的密码
4. **使用最小权限原则** - 为每个仓库配置最小必要的权限
5. **审计访问日志** - 定期检查Nexus仓库的访问日志

## 故障排除

### 常见问题

1. **认证失败**
   - 检查用户名和密码是否正确
   - 确认Base64编码是否正确
   - 验证仓库URL是否正确

2. **包安装失败**
   - 检查网络连接
   - 确认仓库中是否存在所需的包
   - 检查.npmrc文件配置是否正确

3. **权限错误**
   - 确认用户有访问仓库的权限
   - 检查.npmrc文件权限设置

### 调试技巧

1. 使用详细日志：
   ```bash
   npm install --verbose
   ```

2. 检查认证：
   ```bash
   npm login --registry=https://nexus.company.com/repository/npm-private/
   ```

3. 测试仓库连接：
   ```bash
   curl -u username:password https://nexus.company.com/repository/npm-private/
   ```

## 参考资源

- [Nexus Repository Manager Documentation](https://help.sonatype.com/repomanager3)
- [NPM Configuration Documentation](https://docs.npmjs.com/misc/config)
- [Vault Documentation](https://www.vaultproject.io/docs)
- [AWS Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/)