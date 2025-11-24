# code/installation/windows_install_spark.ps1
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

Write-Host "Downloading Spark from $sparkUrl..."
Invoke-WebRequest -Uri $sparkUrl -OutFile $sparkZip

# 解压Spark
Write-Host "Extracting Spark..."
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::ExtractToDirectory($sparkZip, $sparkInstallDir)

# 创建软链接或重命名目录
$extractedFolder = "$sparkInstallDir\spark-$sparkVersion-bin-hadoop3"
if (!(Test-Path -Path "$sparkInstallDir\spark")) {
    if (Test-Path -Path $extractedFolder) {
        Rename-Item -Path $extractedFolder -NewName "spark"
    }
}

# 创建hadoop目录（用于winutils）
$hadoopDir = "$sparkInstallDir\hadoop"
if (!(Test-Path -Path $hadoopDir)) {
    New-Item -ItemType Directory -Path $hadoopDir
}
$hadoopBinDir = "$hadoopDir\bin"
if (!(Test-Path -Path $hadoopBinDir)) {
    New-Item -ItemType Directory -Path $hadoopBinDir
}

Write-Host "Spark installed successfully at $sparkInstallDir\spark"

# 设置环境变量
$sparkHome = "$sparkInstallDir\spark"
[Environment]::SetEnvironmentVariable("SPARK_HOME", $sparkHome, "User")

# 将Spark添加到PATH
$path = [Environment]::GetEnvironmentVariable("PATH", "User")
$newPath = "$path;$sparkHome\bin"
[Environment]::SetEnvironmentVariable("PATH", $newPath, "User")

# 设置Hadoop环境变量（Windows下需要）
[Environment]::SetEnvironmentVariable("HADOOP_HOME", $hadoopDir, "User")

Write-Host "Environment variables set. Please restart PowerShell to apply changes."