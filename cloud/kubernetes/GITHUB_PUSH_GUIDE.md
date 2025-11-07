# 如何将Kubernetes学习指南示例代码推送到GitHub

本指南将帮助您将本地的Kubernetes学习指南示例代码推送到GitHub仓库。

## 步骤1：在GitHub上创建新仓库

1. 登录您的GitHub账户
2. 点击右上角的 "+" 号，选择 "New repository"
3. 仓库名称建议使用：`k8s-study-guide` 或 `kubernetes-example-code`
4. 描述可以填写："Kubernetes学习指南示例代码和配置文件"
5. 选择公共（Public）可见性
6. 不要初始化README、.gitignore或license
7. 点击 "Create repository"

## 步骤2：将本地仓库与GitHub仓库关联

在本地仓库目录中执行以下命令：

```bash
# 添加远程仓库地址（将YOUR_USERNAME替换为您的GitHub用户名）
git remote add origin https://github.com/YOUR_USERNAME/k8s-study-guide.git

# 验证远程仓库是否添加成功
git remote -v
```

## 步骤3：推送到GitHub

```bash
# 推送master分支到GitHub
git push -u origin master
```

## 步骤4：验证推送结果

访问您的GitHub仓库页面，确认所有文件都已成功上传。

## 故障排除

### 如果遇到权限问题：

1. 使用GitHub CLI：
   ```bash
   # 安装GitHub CLI（如果尚未安装）
   # Windows: choco install gh
   # macOS: brew install gh
   
   # 登录GitHub
   gh auth login
   
   # 创建仓库
   gh repo create k8s-study-guide --public --source=. --remote=origin
   
   # 推送代码
   git push -u origin master
   ```

2. 或者使用SSH密钥：
   - 生成SSH密钥：`ssh-keygen -t ed25519 -C "your_email@example.com"`
   - 将公钥添加到GitHub账户
   - 使用SSH URL而不是HTTPS URL添加远程仓库：
     ```bash
     git remote set-url origin git@github.com:YOUR_USERNAME/k8s-study-guide.git
     ```

### 如果推送失败：

1. 确保您的本地仓库是最新的：
   ```bash
   git pull origin master --allow-unrelated-histories
   ```

2. 再次尝试推送：
   ```bash
   git push -u origin master
   ```

## 后续维护

当您更新了本地示例代码后，可以通过以下步骤同步到GitHub：

```bash
# 添加更改
git add .

# 提交更改
git commit -m "Update example code"

# 推送到GitHub
git push origin master
```

恭喜！您现在已经成功将Kubernetes学习指南的所有示例代码托管到了GitHub上。