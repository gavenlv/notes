# code/installation/windows_install_winutils.ps1
# 下载和安装winutils (Hadoop Windows工具)

# 创建Hadoop bin目录
$hadoopBinDir = "C:\spark\hadoop\bin"
if (!(Test-Path -Path $hadoopBinDir)) {
    New-Item -ItemType Directory -Path $hadoopBinDir -Force
}

# 下载winutils.exe
$winutilsUrl = "https://github.com/cdarlint/winutils/raw/master/hadoop-3.0.0/bin/winutils.exe"
$winutilsPath = "$hadoopBinDir\winutils.exe"

Write-Host "Downloading winutils.exe..."
Invoke-WebRequest -Uri $winutilsUrl -OutFile $winutilsPath

# 下载hadoop.dll
$hadoopDllUrl = "https://github.com/cdarlint/winutils/raw/master/hadoop-3.0.0/bin/hadoop.dll"
$hadoopDllPath = "$hadoopBinDir\hadoop.dll"

Write-Host "Downloading hadoop.dll..."
Invoke-WebRequest -Uri $hadoopDllUrl -OutFile $hadoopDllPath

# 创建/tmp目录（Hadoop需要）
$tmpDir = "C:\tmp"
if (!(Test-Path -Path $tmpDir)) {
    New-Item -ItemType Directory -Path $tmpDir
}

# 设置/tmp目录权限
& "$hadoopBinDir\winutils.exe" chmod 777 /tmp

Write-Host "winutils installed successfully at $hadoopBinDir"
Write-Host "Created temporary directory: $tmpDir"