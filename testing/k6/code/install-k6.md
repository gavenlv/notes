# k6学习指南 - 环境安装和配置

## k6安装指南

### Windows系统

1. **使用Chocolatey安装（推荐）**
   ```powershell
   # 安装Chocolatey（如果尚未安装）
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   
   # 使用Chocolatey安装k6
   choco install k6
   ```

2. **手动安装**
   - 访问 [k6官网](https://k6.io/docs/getting-started/installation/)
   - 下载Windows安装包
   - 运行安装程序

### macOS系统

1. **使用Homebrew安装（推荐）**
   ```bash
   # 安装Homebrew（如果尚未安装）
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   
   # 使用Homebrew安装k6
   brew install k6
   ```

2. **手动安装**
   ```bash
   # 使用curl下载安装
   curl -L https://github.com/grafana/k6/releases/latest/download/k6-v0.50.0-macos-amd64.zip -o k6.zip
   unzip k6.zip
   sudo mv k6 /usr/local/bin/
   ```

### Linux系统

1. **使用包管理器安装**
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
   echo "deb https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
   sudo apt-get update
   sudo apt-get install k6
   ```
   
   **CentOS/RHEL:**
   ```bash
   sudo dnf install https://dl.k6.io/rpm/repo.rpm
   sudo dnf install k6
   ```

## 验证安装

安装完成后，验证k6是否正确安装：

```bash
k6 version
```

应该显示类似这样的输出：
```
k6 v0.50.0 (2024-01-01T12:00:00Z, go1.21.0)
```

## 运行第一个测试

进入代码目录，运行第一个测试：

```bash
cd testing/k6/code
k6 run chapter1/1-first-test.js
```

## 运行所有测试

### Windows系统
```powershell
cd testing/k6/code
.\run-all-tests.ps1
```

### Linux/macOS系统
```bash
cd testing/k6/code
chmod +x run-all-tests.sh
./run-all-tests.sh
```

## 环境变量配置

### 生产环境测试
```bash
# 设置环境变量
export ENV=production
export BASE_URL=https://your-api.com
export API_KEY=your-api-key

# 运行测试
k6 run chapter4/production-framework.js
```

### 开发环境测试
```bash
# 使用默认环境变量
export ENV=development
export BASE_URL=https://httpbin.test.k6.io

# 运行测试
k6 run chapter2/experiment2-api-scenario.js
```

## 常用命令

### 基本测试
```bash
# 运行单个测试
k6 run script.js

# 运行测试并生成报告
k6 run --out json=results.json script.js

# 运行测试并设置虚拟用户数
k6 run --vus 10 --duration 30s script.js
```

### 性能测试
```bash
# 负载测试
k6 run --vus 50 --duration 5m script.js

# 压力测试
k6 run --vus 100 --duration 10m --rps 100 script.js

# 峰值测试
k6 run --vus 20 --stages 0:20,1m:100,2m:20 script.js
```

### 监控和报告
```bash
# 生成HTML报告
k6 run --out html=report.html script.js

# 实时监控
k6 run --no-summary script.js

# 详细日志
k6 run --verbose script.js
```

## 故障排除

### 常见问题

1. **k6命令未找到**
   - 检查k6是否安装正确
   - 确保k6在PATH环境变量中
   
2. **测试脚本运行失败**
   - 检查脚本语法错误
   - 确保依赖的文件存在
   - 检查网络连接
   
3. **性能测试结果不理想**
   - 检查目标服务器状态
   - 调整虚拟用户数和持续时间
   - 检查网络带宽限制

### 获取帮助

```bash
# 查看帮助文档
k6 --help

# 查看特定命令帮助
k6 run --help

# 查看版本信息
k6 version
```

## 扩展功能

### 安装k6扩展

```bash
# 安装浏览器扩展（用于录制测试）
k6 browser

# 安装云服务集成
k6 cloud

# 安装数据库集成
k6 run --out influxdb=http://localhost:8086/k6 script.js
```

### IDE集成

**VS Code扩展：**
- 安装"k6"扩展
- 支持语法高亮和代码片段

**IntelliJ IDEA：**
- 安装"K6"插件
- 支持运行配置和调试

## 学习资源

- [k6官方文档](https://k6.io/docs/)
- [k6学习指南](./README.md)
- [k6社区论坛](https://community.k6.io/)
- [k6 GitHub仓库](https://github.com/grafana/k6)

---

**注意：** 在生产环境中运行性能测试时，请确保获得相关授权，并遵循适当的测试规范。