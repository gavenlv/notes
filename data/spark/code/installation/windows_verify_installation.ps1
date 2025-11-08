# code/installation/windows_verify_installation.ps1
# Windows环境验证Spark安装

# 设置Spark路径
$sparkHome = "C:\spark"
$sparkBin = "$sparkHome\bin"

Write-Host "Verifying Spark installation..."

# 验证Spark版本
Write-Host "1. Checking Spark version..."
try {
    & "$sparkBin\spark-submit.cmd" --version
} catch {
    Write-Host "Error checking Spark version: $_"
    exit 1
}

# 运行示例程序
Write-Host "2. Running Spark Pi example..."
try {
    & "$sparkBin\spark-submit.cmd" --class org.apache.spark.examples.SparkPi "$sparkHome\examples\jars\spark-examples_2.12-3.4.0.jar" 10
} catch {
    Write-Host "Error running Spark Pi example: $_"
    exit 1
}

# 测试PySpark
Write-Host "3. Testing PySpark..."
try {
    & "$sparkBin\pyspark.cmd" -e "
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName('WindowsTest').getOrCreate()
print('PySpark is working correctly!')
spark.stop()
"
} catch {
    Write-Host "Error testing PySpark: $_"
    exit 1
}

Write-Host "Spark installation verified successfully!"