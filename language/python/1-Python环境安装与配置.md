# 第1章：Python环境安装与配置

> **学习时长**: 2-3小时  
> **难度**: ⭐  
> **前置知识**: 无

## 本章目标

学完本章后,你将能够:

- ✅ 了解Python的历史和应用领域
- ✅ 在Windows/macOS/Linux上成功安装Python
- ✅ 配置Python开发环境(VS Code/PyCharm/Jupyter)
- ✅ 使用pip安装第三方库
- ✅ 创建和管理虚拟环境
- ✅ 编写并运行第一个Python程序

---

## 1.1 Python简介

### 1.1.1 Python是什么?

**Python**是一种**解释型、面向对象、动态类型**的高级编程语言,由Guido van Rossum于1991年创建。

**核心特点**:
- 🎯 **简单易学**: 语法简洁优雅,接近自然语言
- 🚀 **功能强大**: 标准库丰富,第三方库生态完善
- 🌐 **跨平台**: Windows、macOS、Linux均可运行
- 🔧 **应用广泛**: Web开发、数据分析、人工智能、自动化等

### 1.1.2 Python应用领域

| 领域 | 应用 | 常用库 |
|------|------|--------|
| **Web开发** | 网站、API、后端服务 | Django, Flask, FastAPI |
| **数据分析** | 数据处理、可视化 | Pandas, NumPy, Matplotlib |
| **机器学习** | AI模型、深度学习 | TensorFlow, PyTorch, Scikit-learn |
| **自动化** | 脚本、爬虫、测试 | Selenium, requests, pytest |
| **游戏开发** | 2D游戏 | Pygame |
| **科学计算** | 数值计算、仿真 | SciPy, SymPy |

### 1.1.3 为什么学习Python?

✅ **就业前景好**: Python开发岗位需求量大  
✅ **薪资水平高**: 数据科学、AI方向薪资可观  
✅ **学习曲线平缓**: 相比C++/Java更易上手  
✅ **社区活跃**: 遇到问题容易找到解决方案

---

## 1.2 Python版本选择

### 1.2.1 Python 2 vs Python 3

| 特性 | Python 2 | Python 3 |
|------|---------|---------|
| 官方支持 | ❌ 已停止(2020年) | ✅ 持续更新 |
| print语法 | `print "hello"` | `print("hello")` |
| 除法 | `5/2=2` | `5/2=2.5` |
| 字符串 | ASCII | Unicode |
| **推荐** | ❌ 不推荐 | ✅ **强烈推荐** |

**⚠️ 重要**: 本教程基于**Python 3.8+**,不兼容Python 2.x

### 1.2.2 选择哪个版本?

- **推荐**: Python 3.10 或 3.11 (最新稳定版)
- **最低要求**: Python 3.8

---

## 1.3 Python安装

### 1.3.1 Windows安装

**方式1: 官方安装包(推荐)**

1. 访问 [python.org](https://www.python.org/downloads/)
2. 下载最新版Python 3.x (例如: python-3.11.5-amd64.exe)
3. 运行安装程序

**⚠️ 重要**: 勾选 **"Add Python to PATH"**

```
安装选项:
☑ Install launcher for all users
☑ Add Python 3.11 to PATH  ← 必须勾选!
```

4. 选择"Install Now"或"Customize installation"
5. 等待安装完成

**方式2: Microsoft Store**

```
1. 打开Microsoft Store
2. 搜索"Python 3.11"
3. 点击"获取"安装
```

**验证安装**:

```cmd
# 打开命令提示符(CMD)或PowerShell
python --version
# 输出: Python 3.11.5

pip --version
# 输出: pip 23.2.1 from ...
```

### 1.3.2 macOS安装

**方式1: Homebrew(推荐)**

```bash
# 1. 安装Homebrew(如果未安装)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. 安装Python
brew install python3

# 3. 验证
python3 --version
pip3 --version
```

**方式2: 官方安装包**

1. 访问 [python.org](https://www.python.org/downloads/macos/)
2. 下载macOS安装包
3. 双击.pkg文件安装
4. 按提示完成安装

**验证安装**:

```bash
python3 --version
pip3 --version
```

**⚠️ 注意**: macOS系统自带Python 2.7,使用`python3`而非`python`

### 1.3.3 Linux安装

**Ubuntu/Debian**:

```bash
# 更新包列表
sudo apt update

# 安装Python 3
sudo apt install python3 python3-pip

# 验证
python3 --version
pip3 --version
```

**CentOS/RHEL**:

```bash
# 安装Python 3
sudo yum install python3 python3-pip

# 验证
python3 --version
pip3 --version
```

**从源码编译**(高级用户):

```bash
# 下载源码
wget https://www.python.org/ftp/python/3.11.5/Python-3.11.5.tgz
tar xzf Python-3.11.5.tgz
cd Python-3.11.5

# 编译安装
./configure --enable-optimizations
make -j$(nproc)
sudo make altinstall

# 验证
python3.11 --version
```

---

## 1.4 开发环境配置

### 1.4.1 选择编辑器/IDE

| 工具 | 特点 | 适合人群 |
|------|------|---------|
| **VS Code** | 轻量、插件丰富、免费 | ✅ 推荐初学者 |
| **PyCharm** | 功能强大、专业IDE | 专业开发者 |
| **Jupyter Notebook** | 交互式、可视化 | 数据分析 |
| **Sublime Text** | 轻量快速 | 简单脚本 |

### 1.4.2 配置VS Code(推荐)

**1. 安装VS Code**

访问 [code.visualstudio.com](https://code.visualstudio.com/) 下载安装

**2. 安装Python扩展**

```
1. 打开VS Code
2. 点击左侧扩展图标(Ctrl+Shift+X)
3. 搜索"Python"
4. 安装Microsoft官方Python扩展
```

**3. 配置Python解释器**

```
1. 打开命令面板(Ctrl+Shift+P)
2. 输入"Python: Select Interpreter"
3. 选择已安装的Python版本
```

**4. 推荐扩展**

- **Python** (Microsoft)
- **Pylance** (语法检查)
- **Python Indent** (自动缩进)
- **autoDocstring** (文档字符串)

### 1.4.3 配置PyCharm

**1. 下载安装**

访问 [jetbrains.com/pycharm](https://www.jetbrains.com/pycharm/)

- **Community Edition**: 免费,功能够用
- **Professional Edition**: 付费,功能更全

**2. 创建项目**

```
1. File → New Project
2. Location: 选择项目路径
3. Interpreter: 选择Python解释器
4. Create
```

### 1.4.4 配置Jupyter Notebook

**安装**:

```bash
pip install jupyter
```

**启动**:

```bash
jupyter notebook
```

浏览器会自动打开 http://localhost:8888

**基本使用**:

```
1. New → Python 3 (创建新笔记本)
2. 在单元格中输入代码
3. Shift+Enter 运行
```

---

## 1.5 包管理工具pip

### 1.5.1 pip基础

**pip**是Python的包管理工具,用于安装、卸载、管理第三方库。

**常用命令**:

```bash
# 安装包
pip install package_name

# 安装指定版本
pip install package_name==1.2.3

# 升级包
pip install --upgrade package_name

# 卸载包
pip uninstall package_name

# 列出已安装的包
pip list

# 查看包信息
pip show package_name

# 导出依赖列表
pip freeze > requirements.txt

# 从文件安装依赖
pip install -r requirements.txt
```

### 1.5.2 配置国内镜像(加速下载)

**临时使用**:

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple package_name
```

**永久配置**:

**Windows**:

在`%APPDATA%\pip\pip.ini`中添加:

```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
[install]
trusted-host = pypi.tuna.tsinghua.edu.cn
```

**macOS/Linux**:

在`~/.pip/pip.conf`中添加:

```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
[install]
trusted-host = pypi.tuna.tsinghua.edu.cn
```

**常用国内镜像**:

```
清华: https://pypi.tuna.tsinghua.edu.cn/simple
阿里云: https://mirrors.aliyun.com/pypi/simple/
豆瓣: https://pypi.douban.com/simple
```

---

## 1.6 虚拟环境管理

### 1.6.1 为什么需要虚拟环境?

**问题**: 不同项目可能需要同一个库的不同版本

```
项目A需要: Django 3.2
项目B需要: Django 4.0
```

**解决**: 使用虚拟环境隔离每个项目的依赖

### 1.6.2 使用venv(内置)

**创建虚拟环境**:

```bash
# Windows
python -m venv myenv

# macOS/Linux
python3 -m venv myenv
```

**激活虚拟环境**:

```bash
# Windows CMD
myenv\Scripts\activate.bat

# Windows PowerShell
myenv\Scripts\Activate.ps1

# macOS/Linux
source myenv/bin/activate
```

**激活后**,命令提示符会显示`(myenv)`:

```bash
(myenv) C:\Users\你的用户名>
```

**退出虚拟环境**:

```bash
deactivate
```

**删除虚拟环境**:

```bash
# 直接删除文件夹
rm -rf myenv  # macOS/Linux
rmdir /s myenv  # Windows
```

### 1.6.3 使用virtualenv

**安装**:

```bash
pip install virtualenv
```

**使用**:

```bash
# 创建
virtualenv myenv

# 激活(同venv)
source myenv/bin/activate  # macOS/Linux
myenv\Scripts\activate  # Windows

# 退出
deactivate
```

### 1.6.4 使用conda(Anaconda)

**安装Anaconda**:

访问 [anaconda.com](https://www.anaconda.com/products/distribution) 下载安装

**常用命令**:

```bash
# 创建环境
conda create -n myenv python=3.11

# 激活
conda activate myenv

# 退出
conda deactivate

# 删除
conda remove -n myenv --all

# 列出所有环境
conda env list
```

---

## 1.7 第一个Python程序

### 1.7.1 Hello World (交互式)

**打开Python交互式解释器**:

```bash
python  # Windows
python3  # macOS/Linux
```

**输入代码**:

```python
>>> print("Hello, World!")
Hello, World!

>>> 1 + 1
2

>>> name = "Python"
>>> print(f"Hello, {name}!")
Hello, Python!

>>> exit()  # 退出
```

### 1.7.2 Hello World (脚本文件)

**创建文件** `hello.py`:

```python
# hello.py - 我的第一个Python程序

print("Hello, World!")
print("欢迎来到Python世界!")

name = input("请输入你的名字: ")
print(f"你好, {name}!")
```

**运行**:

```bash
python hello.py
# 输出:
# Hello, World!
# 欢迎来到Python世界!
# 请输入你的名字: 张三
# 你好, 张三!
```

### 1.7.3 简单计算器

**创建文件** `calculator.py`:

```python
# calculator.py - 简单计算器

print("=== 简单计算器 ===")

# 输入两个数字
num1 = float(input("请输入第一个数字: "))
num2 = float(input("请输入第二个数字: "))

# 执行四则运算
print(f"\n{num1} + {num2} = {num1 + num2}")
print(f"{num1} - {num2} = {num1 - num2}")
print(f"{num1} × {num2} = {num1 * num2}")
print(f"{num1} ÷ {num2} = {num1 / num2}")
```

**运行**:

```bash
python calculator.py
# === 简单计算器 ===
# 请输入第一个数字: 10
# 请输入第二个数字: 3
#
# 10.0 + 3.0 = 13.0
# 10.0 - 3.0 = 7.0
# 10.0 × 3.0 = 30.0
# 10.0 ÷ 3.0 = 3.3333333333333335
```

---

## 1.8 环境检查工具

**创建文件** `env_check.py`:

```python
# env_check.py - 检查Python环境配置

import sys
import platform

print("=" * 50)
print("Python环境信息")
print("=" * 50)

print(f"Python版本: {sys.version}")
print(f"Python路径: {sys.executable}")
print(f"操作系统: {platform.system()} {platform.release()}")
print(f"架构: {platform.machine()}")

print("\n" + "=" * 50)
print("已安装的常用库")
print("=" * 50)

libraries = ['pip', 'numpy', 'pandas', 'requests', 'flask']

for lib in libraries:
    try:
        module = __import__(lib)
        version = getattr(module, '__version__', '未知')
        print(f"✓ {lib:15s} {version}")
    except ImportError:
        print(f"✗ {lib:15s} 未安装")

print("=" * 50)
```

**运行**:

```bash
python env_check.py
```

**输出示例**:

```
==================================================
Python环境信息
==================================================
Python版本: 3.11.5 (main, Aug 24 2023, 15:09:32)
Python路径: C:\Python311\python.exe
操作系统: Windows 10
架构: AMD64

==================================================
已安装的常用库
==================================================
✓ pip            23.2.1
✓ numpy          1.25.2
✓ pandas         2.1.0
✗ requests       未安装
✗ flask          未安装
==================================================
```

---

## 1.9 常见问题

### Q1: "python不是内部或外部命令"

**原因**: Python未添加到系统PATH

**解决方案**:

**Windows**:
1. 搜索"环境变量"
2. 编辑系统环境变量
3. 在PATH中添加Python安装路径
4. 例如: `C:\Python311\` 和 `C:\Python311\Scripts\`

**macOS/Linux**:
在`~/.bashrc`或`~/.zshrc`中添加:

```bash
export PATH="/usr/local/bin/python3:$PATH"
```

### Q2: pip安装很慢

**解决**: 使用国内镜像(见1.5.2节)

### Q3: VSCode无法识别Python

**解决**: 
1. `Ctrl+Shift+P`
2. 输入"Python: Select Interpreter"
3. 选择正确的Python版本

### Q4: 虚拟环境激活失败(PowerShell)

**错误**: 
```
无法加载文件 xxx\Scripts\Activate.ps1,因为在此系统上禁止运行脚本
```

**解决**: 以管理员身份运行PowerShell:

```powershell
Set-ExecutionPolicy RemoteSigned
```

---

## 1.10 课后练习

### 练习1: 环境验证

编写脚本检查:
1. Python版本 ≥ 3.8
2. pip是否可用
3. 能否创建虚拟环境

### 练习2: 个人信息卡片

编写程序输入姓名、年龄、城市,然后打印格式化的信息卡片:

```
===================
   个人信息卡片
===================
姓名: 张三
年龄: 25岁
城市: 北京
===================
```

### 练习3: BMI计算器

编写BMI(身体质量指数)计算器:

```
BMI = 体重(kg) / 身高(m)²
```

输出结果和健康建议。

---

## 1.11 本章小结

### 核心知识点

✅ **Python简介**: 解释型、面向对象、应用广泛

✅ **版本选择**: Python 3.8+ (推荐3.10/3.11)

✅ **安装方式**: Windows/macOS/Linux不同平台安装

✅ **开发环境**: VS Code/PyCharm/Jupyter

✅ **pip**: 包管理工具,配置国内镜像加速

✅ **虚拟环境**: venv/virtualenv/conda隔离项目依赖

✅ **第一个程序**: Hello World, 计算器

### 下一章预告

**第2章 - Python基础语法**,将学习:
- 📝 代码规范(PEP 8)
- 💬 注释与文档
- 🔢 变量与运算符
- ⌨️ 输入输出
- 🎯 编写简单程序

---

**🎉 恭喜!** 你已经完成了Python环境搭建,准备好开始编程之旅了!

[← 返回目录](./README.md) | [下一章: Python基础语法 →](./2-Python基础语法.md)
