# 3. Spark安装与环境配置

## 3.1 安装要求

在安装Spark之前，需要确保系统满足以下基本要求：

### 3.1.1 硬件要求

| 场景 | CPU | 内存 | 存储 | 网络 |
|------|-----|------|------|------|
| 本地学习 | 2核+ | 4GB+ | 10GB+ | - |
| 开发测试 | 4核+ | 8GB+ | 50GB+ | 1Gbps |
| 生产环境 | 8核+ | 16GB+ | 100GB+ | 10Gbps |

### 3.1.2 软件要求

| 平台 | 组件 | 最低版本 | 推荐版本 |
|------|------|---------|---------|
| 通用 | Java | JDK 8 | JDK 11 |
| Linux | Python | 3.6 | 3.8+ |
| Windows | Python | 3.6 | 3.8+ |
| macOS | Python | 3.6 | 3.8+ |
| 通用 | Scala | 2.11 | 2.12/2.13 |
| 通用 | Hadoop | 2.7 | 3.x |
| Windows | WSL | - | 最新版 |
| Windows | Git | 2.x | 最新版 |

### 3.1.3 Windows环境额外要求

Windows环境下安装Spark需要额外考虑以下几点：

1. **Windows Subsystem for Linux (WSL)**：推荐安装WSL 2，提供更好的Linux兼容性
2. **Java Development Kit (JDK)**：确保Java正确安装并配置环境变量
3. **Python环境**：可通过Anaconda、Python官方安装包或包管理器安装
4. **Hadoop依赖**：Windows下需要特殊的winutils.exe工具

| 组件 | 说明 | 下载地址 |
|------|------|---------|
| JDK 11 | Java开发环境 | https://adoptium.net |
| Python 3.8+ | Python运行环境 | https://python.org |
| Anaconda | Python发行版 | https://anaconda.com |
| winutils.exe | Hadoop Windows工具 | https://github.com/cdarlint/winutils |
| WSL 2 | Windows Linux子系统 | https://learn.microsoft.com/windows/wsl |

## 3.2 本地模式安装

本地模式是最简单的安装方式，适合学习和开发。

### 3.2.1 Linux/macOS下载和解压Spark

```bash
# code/installation/download_spark.sh
#!/bin/bash

# 下载Spark
cd /opt
wget https://archive.apache.org/dist/spark/spark-3.4.0/spark-3.4.0-bin-hadoop3.tgz

# 解压
tar -xzf spark-3.4.0-bin-hadoop3.tgz
ln -s spark-3.4.0-bin-hadoop3 spark

# 设置权限
chmod -R 755 spark
```

### 3.2.2 Windows下载和解压Spark

#### 3.2.2.1 直接下载和安装

```powershell
# code/installation/download_spark_windows.ps1
# 使用PowerShell下载和安装Spark

# 创建安装目录
$sparkInstallDir = "C:\spark"
if (!(Test-Path -Path $sparkInstallDir)) {
    New-Item -ItemType Directory -Path $sparkInstallDir
}

# 下载Spark
$sparkVersion = "3.4.0"
$sparkUrl = "https://archive.apache.org/dist/spark/spark-$sparkVersion/spark-$sparkVersion-bin-hadoop3.tgz"
$sparkZip = "$sparkInstallDir\spark-$sparkVersion-bin-hadoop3.tgz"

Invoke-WebRequest -Uri $sparkUrl -OutFile $sparkZip

# 解压Spark (需要7-Zip或使用PowerShell扩展功能)
# 如果已安装7-Zip，可以使用:
# & "C:\Program Files\7-Zip\7z.exe" x $sparkZip -o"$sparkInstallDir"

# 使用PowerShell解压 (需要.NET Framework 4.5+)
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::ExtractToDirectory($sparkZip, $sparkInstallDir)

# 创建软链接或重命名目录
$extractedFolder = "$sparkInstallDir\spark-$sparkVersion-bin-hadoop3"
if (!(Test-Path -Path "$sparkInstallDir\spark")) {
    if (Test-Path -Path $extractedFolder) {
        Rename-Item -Path $extractedFolder -NewName "spark"
    }
}

Write-Host "Spark installed successfully at $sparkInstallDir\spark"
```

#### 3.2.2.2 使用包管理器安装

```powershell
# 使用Chocolatey安装 (需要先安装Chocolatey)
choco install spark

# 使用Scoop安装 (需要先安装Scoop)
scoop install spark
```

#### 3.2.2.3 Windows环境配置

```powershell
# code/installation/setup_env_windows.ps1
# Windows环境变量设置

# 设置Spark环境变量
$sparkHome = "C:\spark"
[Environment]::SetEnvironmentVariable("SPARK_HOME", $sparkHome, "User")

# 将Spark添加到PATH
$path = [Environment]::GetEnvironmentVariable("PATH", "User")
$newPath = "$path;$sparkHome\bin"
[Environment]::SetEnvironmentVariable("PATH", $newPath, "User")

# 设置Hadoop环境变量（Windows下需要）
$hadoopHome = "$sparkHome"
[Environment]::SetEnvironmentVariable("HADOOP_HOME", $hadoopHome, "User")

# 设置Python环境
$pythonPath = (Get-Command python).Source
[Environment]::SetEnvironmentVariable("PYSPARK_PYTHON", $pythonPath, "User")

Write-Host "Environment variables set. Please restart PowerShell to apply changes."
```

#### 3.2.2.4 安装winutils

```powershell
# code/installation/install_winutils.ps1
# 下载和安装winutils (Hadoop Windows工具)

# 创建Hadoop bin目录
$hadoopBinDir = "C:\spark\hadoop\bin"
if (!(Test-Path -Path $hadoopBinDir)) {
    New-Item -ItemType Directory -Path $hadoopBinDir -Force
}

# 下载winutils.exe
$winutilsUrl = "https://github.com/cdarlint/winutils/raw/master/hadoop-3.0.0/bin/winutils.exe"
$winutilsPath = "$hadoopBinDir\winutils.exe"

Invoke-WebRequest -Uri $winutilsUrl -OutFile $winutilsPath

# 下载hadoop.dll
$hadoopDllUrl = "https://github.com/cdarlint/winutils/raw/master/hadoop-3.0.0/bin/hadoop.dll"
$hadoopDllPath = "$hadoopBinDir\hadoop.dll"

Invoke-WebRequest -Uri $hadoopDllUrl -OutFile $hadoopDllPath

Write-Host "winutils installed successfully at $hadoopBinDir"
```

### 3.2.3 配置环境变量 (Linux/macOS)

```bash
# code/installation/setup_env.sh

```bash
# code/installation/download_spark.sh
#!/bin/bash

# 下载Spark
cd /opt
wget https://archive.apache.org/dist/spark/spark-3.4.0/spark-3.4.0-bin-hadoop3.tgz

# 解压
tar -xzf spark-3.4.0-bin-hadoop3.tgz
ln -s spark-3.4.0-bin-hadoop3 spark

# 设置权限
chmod -R 755 spark
```

### 3.2.2 配置环境变量

```bash
# code/installation/setup_env.sh
#!/bin/bash

# 设置环境变量
echo 'export SPARK_HOME=/opt/spark' >> ~/.bashrc
echo 'export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin' >> ~/.bashrc
echo 'export PYSPARK_PYTHON=/usr/bin/python3' >> ~/.bashrc

# 应用环境变量
source ~/.bashrc
```

### 3.2.5 验证安装 (Linux/macOS)

```bash
# code/installation/verify_installation.sh
#!/bin/bash

# 验证Spark版本
spark-submit --version

# 运行示例程序
spark-submit $SPARK_HOME/examples/src/main/python/pi.py 10

# 启动Spark Shell
spark-shell --version
pyspark --version
```

### 3.2.6 验证安装 (Windows)

```powershell
# code/installation/verify_installation_windows.ps1
# Windows环境验证Spark安装

# 验证Spark版本
C:\spark\bin\spark-submit.cmd --version

# 运行示例程序
C:\spark\bin\spark-submit.cmd C:\spark\examples\src\main\python\pi.py 10

# 验证Spark Shell
C:\spark\bin\spark-shell.cmd --version
C:\spark\bin\pyspark.cmd --version

Write-Host "Spark installation verified successfully!"
```

### 3.2.7 使用WSL 2安装Spark (Windows推荐方法)

对于Windows用户，使用WSL 2可以提供更接近原生Linux的体验，避免了Windows环境下的许多兼容性问题。

#### 3.2.7.1 安装WSL 2

```powershell
# 以管理员身份运行PowerShell，执行以下命令安装WSL
wsl --install

# 重启计算机后，配置Ubuntu (或其他Linux发行版)
# 在WSL终端中执行:
sudo apt update && sudo apt upgrade -y
sudo apt install -y openjdk-11-jdk python3 python3-pip scala wget curl
```

#### 3.2.7.2 在WSL中安装Spark

```bash
# code/installation/install_spark_wsl.sh
#!/bin/bash

# 在WSL环境中安装Spark

# 创建安装目录
sudo mkdir -p /opt/spark
sudo chown $USER:$USER /opt/spark

# 下载Spark
cd /opt/spark
wget https://archive.apache.org/dist/spark/spark-3.4.0/spark-3.4.0-bin-hadoop3.tgz

# 解压
tar -xzf spark-3.4.0-bin-hadoop3.tgz
ln -s spark-3.4.0-bin-hadoop3 spark

# 设置环境变量
echo 'export SPARK_HOME=/opt/spark/spark' >> ~/.bashrc
echo 'export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin' >> ~/.bashrc
echo 'export PYSPARK_PYTHON=/usr/bin/python3' >> ~/.bashrc

# 应用环境变量
source ~/.bashrc

# 验证安装
$SPARK_HOME/bin/spark-submit --version
echo "Spark installed successfully in WSL!"
```

#### 3.2.7.3 配置WSL访问Windows文件系统

```bash
# 在WSL中创建Windows文件访问软链接
ln -s /mnt/c/workspace /workspace

# 测试访问Windows文件系统
ls -la /mnt/c/
```

## 3.3 集群模式安装

集群模式适用于生产环境，支持多种部署方式。

### 3.3.1 Standalone模式

#### 3.3.1.1 Master节点配置

```bash
# code/installation/standalone_master.sh
#!/bin/bash

# Master节点配置
cd $SPARK_HOME/conf

# 复制模板文件
cp spark-env.sh.template spark-env.sh

# 编辑spark-env.sh
cat >> spark-env.sh << EOF

# 设置Java Home
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# 设置Master主机名或IP
export SPARK_MASTER_HOST=master-node-ip

# 设置Master端口
export SPARK_MASTER_PORT=7077

# 设置Master Web UI端口
export SPARK_MASTER_WEBUI_PORT=8080

# 设置Worker内存
export SPARK_WORKER_MEMORY=4g

# 设置Worker核心数
export SPARK_WORKER_CORES=2

# 设置每个节点的Worker实例数
export SPARK_WORKER_INSTANCES=1

EOF

# 复制workers文件模板
cp workers.template workers

# 编辑workers文件，添加Worker节点主机名
cat > workers << EOF
worker1-ip
worker2-ip
worker3-ip
EOF
```

#### 3.3.1.2 Worker节点配置

```bash
# code/installation/standalone_worker.sh
#!/bin/bash

# Worker节点配置
cd $SPARK_HOME/conf

# 复制模板文件
cp spark-env.sh.template spark-env.sh

# 编辑spark-env.sh
cat >> spark-env.sh << EOF

# 设置Java Home
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# 设置Master地址
export SPARK_MASTER_HOST=worker-node-ip

EOF
```

#### 3.3.1.3 启动和停止集群

```bash
# code/installation/cluster_management.sh
#!/bin/bash

# 在Master节点上启动集群
$SPARK_HOME/sbin/start-all.sh

# 在Master节点上停止集群
$SPARK_HOME/sbin/stop-all.sh

# 只启动Master
$SPARK_HOME/sbin/start-master.sh

# 只启动Worker
$SPARK_HOME/sbin/start-slave.sh spark://master-ip:7077
```

### 3.3.2 YARN模式

#### 3.3.2.1 配置Spark与YARN集成

```bash
# code/installation/yarn_config.sh
#!/bin/bash

# 配置Spark与YARN集成
cd $SPARK_HOME/conf

# 复制Hadoop配置文件到Spark conf目录
cp /etc/hadoop/conf/core-site.xml .
cp /etc/hadoop/conf/hdfs-site.xml .
cp /etc/hadoop/conf/yarn-site.xml .

# 编辑spark-env.sh
cat >> spark-env.sh << EOF

# 设置Hadoop配置目录
export HADOOP_CONF_DIR=/etc/hadoop/conf

# 设置YARN配置目录
export YARN_CONF_DIR=/etc/hadoop/conf

EOF
```

#### 3.3.2.2 提交应用到YARN

```bash
# code/installation/yarn_submit.sh
#!/bin/bash

# 提交应用到YARN集群
spark-submit \
  --class org.apache.spark.examples.SparkPi \
  --master yarn \
  --deploy-mode cluster \
  --driver-memory 1g \
  --executor-memory 1g \
  --executor-cores 1 \
  --queue thequeue \
  $SPARK_HOME/examples/jars/spark-examples*.jar \
  10
```

### 3.3.3 Kubernetes模式

#### 3.3.3.1 准备Docker镜像

```bash
# code/installation/kubernetes/dockerfile
FROM openjdk:11-jre-slim

# 安装Python
RUN apt-get update && apt-get install -y python3 python3-pip python3-dev && \
    rm -rf /var/lib/apt/lists/*

# 设置Spark用户
RUN useradd spark && \
    mkdir -p /opt/spark && \
    chown -R spark:spark /opt/spark

# 安装Spark
COPY spark-3.4.0-bin-hadoop3.tgz /opt/
RUN tar -xzf /opt/spark-3.4.0-bin-hadoop3.tgz -C /opt/ && \
    ln -s /opt/spark-3.4.0-bin-hadoop3 /opt/spark && \
    rm /opt/spark-3.4.0-bin-hadoop3.tgz && \
    chown -R spark:spark /opt/spark

# 设置环境变量
ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin
ENV PYTHONPATH=$SPARK_HOME/python:$PYTHONPATH

USER spark
WORKDIR /opt/spark

# 端口暴露
EXPOSE 8080 7077

# 启动脚本
CMD ["/bin/bash"]
```

#### 3.3.3.2 构建和推送镜像

```bash
# code/installation/kubernetes/build_push.sh
#!/bin/bash

# 构建镜像
docker build -t spark:3.4.0 .

# 推送到镜像仓库
docker tag spark:3.4.0 your-registry/spark:3.4.0
docker push your-registry/spark:3.4.0
```

#### 3.3.3.3 提交应用到Kubernetes

```bash
# code/installation/kubernetes/k8s_submit.sh
#!/bin/bash

# 提交应用到Kubernetes
$SPARK_HOME/bin/spark-submit \
  --master k8s://https://<k8s-master>:6443 \
  --deploy-mode cluster \
  --name spark-pi \
  --class org.apache.spark.examples.SparkPi \
  --conf spark.executor.instances=3 \
  --conf spark.kubernetes.container.image=your-registry/spark:3.4.0 \
  --conf spark.kubernetes.namespace=spark \
  local:///opt/spark/examples/jars/spark-examples_2.12-3.4.0.jar \
  10
```

## 3.4 Windows开发环境配置

### 3.4.1 Windows PowerShell配置

```powershell
# code/installation/windows/powershell_config.ps1
# PowerShell配置文件 ($PROFILE)

# 创建Profile文件
if (!(Test-Path -Path $PROFILE)) {
    New-Item -ItemType File -Path $PROFILE -Force
}

# 添加Spark环境变量
@"
# Spark Environment Variables
`$env:SPARK_HOME = "C:\spark"
`$env:HADOOP_HOME = "C:\spark"
`$env:PYSPARK_PYTHON = "python"
`$env:JAVA_HOME = (Get-Command java).Source | Split-Path -Parent
`$env:PATH = "`$env:PATH;`$env:SPARK_HOME\bin;`$env:JAVA_HOME\bin"

# Spark Aliases
function Run-PySpark { & "$env:SPARK_HOME\bin\pyspark.cmd" $args }
function Run-SparkShell { & "$env:SPARK_HOME\bin\spark-shell.cmd" $args }
function Run-SparkSubmit { & "$env:SPARK_HOME\bin\spark-submit.cmd" $args }

Set-Alias -Name pyspark -Value Run-PySpark
Set-Alias -Name spark-shell -Value Run-SparkShell
Set-Alias -Name spark-submit -Value Run-SparkSubmit
"@ | Out-File -FilePath $PROFILE -Append

Write-Host "PowerShell profile configured. Restart PowerShell to apply changes."
```

### 3.4.2 Windows Anaconda配置

```powershell
# code/installation/windows/anaconda_config.ps1
# Anaconda环境配置

# 创建Spark专用的Conda环境
conda create -n pyspark python=3.8 -y

# 激活环境
conda activate pyspark

# 安装PySpark及相关依赖
pip install pyspark=3.4.0
pip install pyarrow findspark jupyterlab

# 配置环境变量
$condaEnvPath = conda info --envs | Select-String "pyspark" | ForEach-Object { ($_ -split '\s+')[1] }
@"
# Spark Environment Variables for Anaconda
`$env:SPARK_HOME = "C:\spark"
`$env:PYSPARK_PYTHON = "$condaEnvPath\python.exe"
`$env:JAVA_HOME = (Get-Command java).Source | Split-Path -Parent
`$env:PATH = "`$env:PATH;`$env:SPARK_HOME\bin;`$env:JAVA_HOME\bin"
"@ | Out-File -FilePath "$condaEnvPath\etc\conda\activate.d\env_vars.bat" -Encoding Ascii

Write-Host "Anaconda environment for PySpark configured successfully."
```

### 3.4.3 Windows Jupyter Notebook配置

```python
# code/installation/windows/jupyter_config.py
# Windows Jupyter Notebook Spark配置

import os
import sys
import subprocess

# 设置Spark路径
spark_home = r"C:\spark"
os.environ['SPARK_HOME'] = spark_home

# 查找Python路径
python_path = sys.executable
os.environ['PYSPARK_PYTHON'] = python_path

# 添加PySpark到Python路径
pyspark_path = os.path.join(spark_home, 'python')
sys.path.insert(0, pyspark_path)

# 查找Py4J JAR文件
import glob
py4j_files = glob.glob(os.path.join(pyspark_path, 'lib', 'py4j-*.jar'))
if py4j_files:
    sys.path.insert(0, py4j_files[0])

# 创建Jupyter内核配置
kernel_name = "pyspark"
kernel_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "jupyter", "kernels", kernel_name)

if not os.path.exists(kernel_dir):
    os.makedirs(kernel_dir)

kernel_json = {
    "argv": [
        python_path, "-m", "ipykernel_launcher",
        "-f", "{connection_file}"
    ],
    "display_name": "PySpark (Spark 3.4)",
    "language": "python",
    "env": {
        "SPARK_HOME": spark_home,
        "PYSPARK_PYTHON": python_path,
        "PYTHONPATH": os.pathsep.join([pyspark_path] + py4j_files),
        "JAVA_HOME": subprocess.check_output(["where", "java"], text=True).split("
")[0].strip()
    }
}

import json
with open(os.path.join(kernel_dir, "kernel.json"), "w") as f:
    json.dump(kernel_json, f, indent=2)

print("Jupyter kernel for PySpark configured successfully!")
print(f"Kernel installed at: {kernel_dir}")
print("Restart Jupyter to use the new kernel.")
```

### 3.4.4 Windows VS Code配置

```json
// code/installation/windows/vscode_settings.json
// VS Code工作区设置

{
    "python.defaultInterpreterPath": "C:\\path\\to\\your\\python\\env\\python.exe",
    "python.terminal.activateEnvironment": true,
    "python.envFile": "${workspaceFolder}/.env",
    "files.associations": {
        "*.py": "python"
    },
    "python.analysis.typeCheckingMode": "basic",
    "jupyter.askForKernelRestart": false,
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false
}
```

```python
# code/installation/windows/test_spark.py
# VS Code中测试Spark环境的简单脚本

import os
import sys

# 添加Spark路径
spark_home = os.environ.get('SPARK_HOME', 'C:\\spark')
sys.path.insert(0, os.path.join(spark_home, 'python'))

# 添加Py4J路径
import glob
py4j_files = glob.glob(os.path.join(spark_home, 'python', 'lib', 'py4j-*.jar'))
if py4j_files:
    sys.path.insert(0, py4j_files[0])

try:
    from pyspark.sql import SparkSession
    
    # 创建Spark会话
    spark = SparkSession.builder \
        .appName("VS Code Test") \
        .config("spark.driver.memory", "1g") \
        .config("spark.sql.warehouse.dir", "file:///C:/temp/spark-warehouse") \
        .getOrCreate()
    
    # 测试创建DataFrame
    df = spark.createDataFrame([(1, "test1"), (2, "test2")], ["id", "value"])
    df.show()
    
    # 停止Spark会话
    spark.stop()
    
    print("Spark is working correctly in VS Code!")
    
except Exception as e:
    print(f"Error setting up Spark in VS Code: {e}")
```

### 3.4.5 Windows批处理脚本

```batch
@echo off
REM code/installation/windows/spark_env.bat
REM Windows批处理脚本设置Spark环境

REM 设置Spark环境变量
set SPARK_HOME=C:\spark
set HADOOP_HOME=C:\spark
set JAVA_HOME=C:\Program Files\Java\jdk-11

REM 设置Python路径
set PYSPARK_PYTHON=python

REM 更新PATH
set PATH=%PATH%;%SPARK_HOME%\bin;%JAVA_HOME%\bin

REM 显示当前环境变量
echo SPARK_HOME: %SPARK_HOME%
echo JAVA_HOME: %JAVA_HOME%
echo PYSPARK_PYTHON: %PYSPARK_PYTHON%
```

```batch
@echo off
REM code/installation/windows/run_pyspark.bat
REM 启动PySpark的批处理脚本

REM 设置环境
call spark_env.bat

REM 启动PySpark
%SPARK_HOME%\bin\pyspark.cmd
```

## 3.5 开发环境配置

### 3.5.1 IntelliJ IDEA配置

#### 3.4.1.1 Scala开发环境

```scala
// code/installation/ide/build.sbt
name := "spark-learning"
version := "1.0"
scalaVersion := "2.12.17"

libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-core" % "3.4.0" % "provided",
  "org.apache.spark" %% "spark-sql" % "3.4.0" % "provided",
  "org.apache.spark" %% "spark-streaming" % "3.4.0" % "provided",
  "org.apache.spark" %% "spark-mllib" % "3.4.0" % "provided"
)
```

#### 3.4.1.2 Python开发环境

```python
# code/installation/ide/requirements.txt
pyspark==3.4.0
py4j==0.10.9.5
jupyter==1.0.0
```

### 3.4.2 PyCharm配置

#### 3.4.2.1 配置Spark解释器

1. 打开PyCharm
2. 进入File > Settings > Project: [project_name] > Python Interpreter
3. 添加新的解释器，指向包含PySpark的Python环境
4. 添加环境变量：
   - SPARK_HOME: /path/to/spark
   - PYSPARK_PYTHON: /path/to/python

### 3.4.3 Jupyter Notebook配置

```bash
# code/installation/jupyter/setup_jupyter.sh
#!/bin/bash

# 安装Jupyter
pip install jupyter

# 设置环境变量
export SPARK_HOME=/opt/spark
export PYSPARK_PYTHON=python3

# 启动Jupyter
jupyter notebook --notebook-dir=/workspace
```

```python
# code/installation/jupyter/spark_config.py
# Jupyter Notebook中的Spark配置
import os
import sys

# 设置Spark路径
os.environ['SPARK_HOME'] = '/opt/spark'
os.environ['PYSPARK_PYTHON'] = sys.executable

# 添加PySpark到Python路径
sys.path.insert(0, os.path.join(os.environ['SPARK_HOME'], 'python'))
sys.path.insert(0, os.path.join(os.environ['SPARK_HOME'], 'python', 'lib', 'py4j-0.10.9.5-src.zip'))

# 初始化Spark
from pyspark.sql import SparkSession
spark = SparkSession.builder \
    .appName("JupyterSpark") \
    .config("spark.driver.memory", "2g") \
    .config("spark.executor.memory", "2g") \
    .getOrCreate()

print("Spark initialized successfully!")
print(f"Spark version: {spark.version}")
```

## 3.5 Spark配置详解

### 3.5.1 核心配置参数

```bash
# code/installation/conf/spark-defaults.conf
# Spark默认配置

# Master URL
spark.master                     local[*]

# 应用程序名称
spark.app.name                   SparkLearning

# Driver内存
spark.driver.memory              1g

# Executor内存
spark.executor.memory            1g

# 每个Executor的核心数
spark.executor.cores              2

# 默认并行度
spark.default.parallelism        8

# 动态分配
spark.dynamicAllocation.enabled  true
spark.dynamicAllocation.minExecutors  1
spark.dynamicAllocation.maxExecutors  10
spark.dynamicAllocation.initialExecutors  2

# 序列化
spark.serializer                 org.apache.spark.serializer.KryoSerializer

# 存储级别
spark.storage.memoryFraction     0.6

# Shuffle配置
spark.shuffle.compress           true
spark.shuffle.spill.compress     true

# SQL配置
spark.sql.shuffle.partitions     8

# 事件日志
spark.eventLog.enabled           true
spark.eventLog.dir               hdfs://namenode:8020/spark-logs
```

### 3.5.2 高级配置参数

```bash
# code/installation/conf/spark-advanced.conf
# Spark高级配置

# 网络配置
spark.network.timeout            300s
spark.rpc.askTimeout             300s
spark.rpc.lookupTimeout          300s

# 内存配置
spark.memory.fraction            0.6
spark.memory.storageFraction    0.5
spark.memory.useLegacyMode       false

# 垃圾回收配置
spark.executor.extraJavaOptions  -XX:+UseG1GC -XX:+UnlockExperimentalVMOptions -XX:MaxGCPauseMillis=200

# 动态分配配置
spark.shuffle.service.enabled    true

# SQL优化配置
spark.sql.autoBroadcastJoinThreshold  10MB
spark.sql.adaptive.enabled       true
spark.sql.adaptive.shuffle.targetPostShuffleInputSize  64MB

# 监控配置
spark.metrics.conf               metrics.properties
```

### 3.5.3 环境变量配置

```bash
# code/installation/conf/spark-env.sh
#!/bin/bash

# Spark环境变量配置

# Java Home
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Scala Home
export SCALA_HOME=/usr/share/scala

# Spark Home
export SPARK_HOME=/opt/spark

# Hadoop配置目录
export HADOOP_CONF_DIR=/etc/hadoop/conf

# YARN配置目录
export YARN_CONF_DIR=/etc/hadoop/conf

# Spark公共库
export SPARK_DIST_CLASSPATH=$(hadoop classpath)

# Driver额外Java选项
export SPARK_DRIVER_EXTRA_JAVA_OPTIONS="-Dspark.driver.extraJavaOptions=-XX:+UseG1GC"

# Executor额外Java选项
export SPARK_EXECUTOR_EXTRA_JAVA_OPTIONS="-XX:+UseG1GC"

# IP绑定
export SPARK_LOCAL_IP="127.0.0.1"
export SPARK_PUBLIC_DNS="localhost"

# 日志配置
export SPARK_LOG_DIR=$SPARK_HOME/logs
```

## 3.6 Docker部署

### 3.6.1 单节点Docker部署

```yaml
# code/installation/docker/docker-compose.yml
version: '3'

services:
  spark-master:
    image: bitnami/spark:3.4
    environment:
      - SPARK_MODE=master
      - SPARK_RPC_AUTHENTICATION_ENABLED=no
      - SPARK_RPC_ENCRYPTION_ENABLED=no
      - SPARK_LOCAL_STORAGE_ENCRYPTION_ENABLED=no
      - SPARK_SSL_ENABLED=no
    ports:
      - '8080:8080'
      - '7077:7077'
    volumes:
      - ./data:/opt/data
    networks:
      - spark-network

  spark-worker:
    image: bitnami/spark:3.4
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://spark-master:7077
      - SPARK_WORKER_MEMORY=2G
      - SPARK_WORKER_CORES=2
      - SPARK_RPC_AUTHENTICATION_ENABLED=no
      - SPARK_RPC_ENCRYPTION_ENABLED=no
      - SPARK_LOCAL_STORAGE_ENCRYPTION_ENABLED=no
      - SPARK_SSL_ENABLED=no
    volumes:
      - ./data:/opt/data
    depends_on:
      - spark-master
    networks:
      - spark-network

  spark-history-server:
    image: bitnami/spark:3.4
    environment:
      - SPARK_MODE=history-server
      - SPARK_RPC_AUTHENTICATION_ENABLED=no
      - SPARK_RPC_ENCRYPTION_ENABLED=no
      - SPARK_LOCAL_STORAGE_ENCRYPTION_ENABLED=no
      - SPARK_SSL_ENABLED=no
    ports:
      - '18080:18080'
    volumes:
      - ./spark-logs:/opt/bitnami/spark/logs
    networks:
      - spark-network

networks:
  spark-network:
    driver: bridge
```

### 3.6.2 启动Docker集群

```bash
# code/installation/docker/start_cluster.sh
#!/bin/bash

# 启动Docker集群
docker-compose up -d

# 检查服务状态
docker-compose ps

# 查看日志
docker-compose logs -f spark-master

# 停止集群
docker-compose down
```

### 3.6.3 提交应用到Docker集群

```bash
# code/installation/docker/submit_app.sh
#!/bin/bash

# 提交Python应用到Docker集群
docker run --rm \
  --network spark_spark-network \
  bitnami/spark:3.4 \
  /opt/bitnami/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  --name spark-pi \
  /opt/bitnami/spark/examples/src/main/python/pi.py 10
```

## 3.7 验证安装

### 3.7.1 基础验证

```python
# code/installation/verification/spark_test.py
from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession

def test_spark_core():
    """测试Spark Core"""
    conf = SparkConf().setAppName("SparkTest").setMaster("local[*]")
    sc = SparkContext(conf=conf)
    
    # 测试RDD操作
    data = range(1, 1001)
    rdd = sc.parallelize(data)
    
    # 计算总和
    total = rdd.sum()
    print(f"RDD sum test: {total}")
    
    sc.stop()
    return True

def test_spark_sql():
    """测试Spark SQL"""
    spark = SparkSession.builder.appName("SQLTest").getOrCreate()
    
    # 创建测试数据
    data = [("Alice", 34), ("Bob", 45), ("Charlie", 29)]
    columns = ["name", "age"]
    df = spark.createDataFrame(data, columns)
    
    # 测试SQL操作
    df.createOrReplaceTempView("people")
    result = spark.sql("SELECT * FROM people WHERE age > 30")
    
    print("Spark SQL test:")
    result.show()
    
    spark.stop()
    return True

if __name__ == "__main__":
    print("Testing Spark installation...")
    
    core_test = test_spark_core()
    sql_test = test_spark_sql()
    
    if core_test and sql_test:
        print("Spark installation test passed!")
    else:
        print("Spark installation test failed!")
```

### 3.7.2 性能验证

```python
# code/installation/verification/performance_test.py
import time
from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession

def performance_test():
    """性能测试"""
    spark = SparkSession.builder.appName("PerformanceTest").getOrCreate()
    
    # 创建大数据集
    data = spark.range(1, 10000000)
    
    # 执行复杂计算
    start_time = time.time()
    
    # 转换操作
    transformed = data.filter("id % 2 == 0") \
                     .withColumn("squared", data.id * data.id) \
                     .filter("squared > 1000")
    
    # 行动操作
    count = transformed.count()
    
    end_time = time.time()
    
    print(f"Performance test result:")
    print(f"Total records: {count}")
    print(f"Execution time: {end_time - start_time:.2f} seconds")
    
    spark.stop()

if __name__ == "__main__":
    performance_test()
```

## 3.8 故障排查

### 3.8.1 常见问题与解决方案

#### 问题1: 内存不足错误

```
java.lang.OutOfMemoryError: Java heap space
```

**解决方案:**
```bash
# 增加Driver内存
spark-submit --driver-memory 2g ...

# 增加Executor内存
spark-submit --executor-memory 4g ...

# 或者修改配置文件
spark.driver.memory 2g
spark.executor.memory 4g
```

#### 问题2: 连接超时

```
org.apache.spark.SparkException: Job aborted due to stage failure
```

**解决方案:**
```bash
# 增加超时时间
spark-submit --conf spark.network.timeout=300s ...
spark-submit --conf spark.rpc.askTimeout=300s ...

# 或者修改配置文件
spark.network.timeout 300s
spark.rpc.askTimeout 300s
```

#### 问题3: Python路径问题

```
python: command not found
```

**解决方案:**
```bash
# 设置Python路径
export PYSPARK_PYTHON=/usr/bin/python3
spark-submit --conf spark.pyspark.python=/usr/bin/python3 ...

# 或者修改配置文件
spark.pyspark.python /usr/bin/python3
```

### 3.8.2 日志分析

```bash
# code/installation/troubleshooting/analyze_logs.sh
#!/bin/bash

# 查看Spark应用程序日志
echo "分析Spark应用程序日志..."

# 查找最近的日志文件
APP_ID=$(ls -t $SPARK_HOME/logs/ | grep application_ | head -1 | cut -d'_' -f2-)

echo "应用程序ID: $APP_ID"

# 查看Executor日志
echo "Executor日志:"
tail -n 50 $SPARK_HOME/logs/worker-$HOSTNAME.out

# 查看Driver日志
echo "Driver日志:"
tail -n 50 $SPARK_HOME/logs/spark-$USER-org.apache.spark.deploy.master.Master-1-$HOSTNAME.out
```

## 3.9 小结

本章详细介绍了Spark的安装和环境配置，包括本地模式、Standalone集群模式、YARN模式和Kubernetes模式的部署方法，以及开发环境的配置。我们还介绍了Docker部署和故障排查的基本方法。正确配置Spark环境是高效使用Spark的基础，也是后续学习和实践的前提。

## 实验与练习

1. 在本地安装Spark单机版，并运行示例程序
2. 搭建Spark Standalone集群，提交测试应用
3. 配置Spark与YARN集成，提交应用到YARN集群
4. 使用Docker部署Spark集群，测试集群功能
5. 针对常见错误进行排查和解决

## 参考资源

- [Spark官方安装指南](https://spark.apache.org/docs/latest/spark-standalone.html)
- [Spark运行模式详解](https://spark.apache.org/docs/latest/submitting-applications.html)