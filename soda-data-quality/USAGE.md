# 快速使用指南

## 🚀 最简单的开始方式

### Windows 用户
```batch
# 双击运行或命令行执行
quick_start.bat
```

### Linux/macOS 用户
```bash
# 给脚本执行权限并运行
chmod +x quick_start.sh
./quick_start.sh
```

## 📊 数据质量检查演示

运行 `quick_start.bat` 或 `./quick_start.sh` 后，你会看到：

```
================================================================================
DATA QUALITY CHECK RESULTS
================================================================================
Timestamp: 2025-08-29T00:39:26.086291
Total Checks: 10
Passed: 3
Failed: 7
--------------------------------------------------------------------------------
 1. ✅ Users table has data
 2. ✅ No duplicate emails
 3. ❌ Name is required
 4. ❌ Valid email format
 5. ❌ No future registration dates
 6. ✅ Orders table has data
 7. ❌ Valid user references
 8. ❌ Positive quantity
 9. ❌ Non-negative price
10. ❌ Product name is required

Overall Status: ⚠️  ISSUES FOUND
================================================================================
```

## 🗄️ 数据库初始化

### 只初始化 PostgreSQL（推荐）
```batch
# Windows
run_app.bat init-pg

# Linux/macOS
./run_app.sh init-pg
```

### 初始化所有数据库
```batch
# Windows
run_app.bat init

# Linux/macOS
./run_app.sh init
```

## 🔌 测试数据库连接
```batch
# Windows
run_app.bat test

# Linux/macOS
./run_app.sh test
```

## 📈 运行完整应用
```batch
# Windows
run_app.bat app

# Linux/macOS
./run_app.sh app
```

## 🧪 运行演示（无需数据库）
```batch
# Windows
run_app.bat demo

# Linux/macOS
./run_app.sh demo
```

## ⚙️ 虚拟环境管理

### 首次设置
```batch
# Windows
setup_venv.bat

# Linux/macOS
./setup_venv.sh
```

### 手动激活虚拟环境
```batch
# Windows
venv\Scripts\activate.bat

# Linux/macOS
source venv/bin/activate
```

### 退出虚拟环境
```bash
deactivate
```

## 📁 项目文件说明

- `quick_start.bat/sh` - 快速启动脚本（推荐）
- `run_app.bat/sh` - 高级运行脚本
- `setup_venv.bat/sh` - 虚拟环境设置
- `environment.env` - 数据库配置
- `reports/` - 生成的报告目录

## 🎯 使用建议

1. **首次使用**: 运行 `quick_start.bat` 或 `./quick_start.sh`
2. **有 PostgreSQL**: 运行 `run_app.bat init-pg` 初始化数据库
3. **测试连接**: 运行 `run_app.bat test` 检查数据库连接
4. **查看报告**: 检查 `reports/` 目录中的 JSON 报告文件

## 🚨 常见问题

### 虚拟环境问题
- 如果提示找不到模块，确保虚拟环境已激活
- 运行 `setup_venv.bat` 重新创建虚拟环境

### 数据库连接问题
- 检查 `environment.env` 中的数据库配置
- 确保数据库服务正在运行
- 使用 `run_app.bat test` 测试连接

### 权限问题（Linux/macOS）
- 给脚本执行权限: `chmod +x *.sh`



