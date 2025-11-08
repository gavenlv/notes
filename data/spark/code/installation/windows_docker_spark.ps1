# code/installation/windows_docker_spark.ps1
# 在Windows上使用Docker运行Spark

# 检查Docker Desktop是否运行
$dockerRunning = docker info 2>$null
if (-not $?) {
    Write-Host "Error: Docker Desktop is not running. Please start Docker Desktop."
    exit 1
}

Write-Host "Setting up Spark with Docker on Windows..."

# 创建工作目录
$workspaceDir = "$pwd\spark-workspace"
if (!(Test-Path -Path $workspaceDir)) {
    New-Item -ItemType Directory -Path $workspaceDir
}

# 创建docker-compose.yml文件
$dockerComposeContent = @"
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
      - $workspaceDir:/opt/data
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
      - $workspaceDir:/opt/data
    depends_on:
      - spark-master
    networks:
      - spark-network
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
"@

Set-Content -Path "$workspaceDir\docker-compose.yml" -Value $dockerComposeContent

# 创建Spark日志目录
$logDir = "$pwd\spark-logs"
if (!(Test-Path -Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir
}

Write-Host "Docker Compose configuration created."

# 启动Docker集群
Write-Host "Starting Spark cluster with Docker..."
Set-Location $workspaceDir
docker-compose up -d

# 检查服务状态
Write-Host "Checking service status..."
Start-Sleep -Seconds 10
docker-compose ps

# 创建示例Python脚本
$pythonScript = @"
from pyspark.sql import SparkSession

# 创建Spark会话
spark = SparkSession.builder \
    .appName("Docker Windows Test") \
    .master("spark://spark-master:7077") \
    .getOrCreate()

# 创建示例数据
data = [(1, "Windows"), (2, "Docker"), (3, "Spark")]
df = spark.createDataFrame(data, ["id", "platform"])

# 显示数据
print("Sample DataFrame:")
df.show()

# 执行简单的SQL查询
df.createOrReplaceTempView("platforms")
result = spark.sql("SELECT * FROM platforms WHERE id > 1")
print("SQL Query Result:")
result.show()

# 停止Spark会话
spark.stop()
print("Spark job completed successfully!")
"@

Set-Content -Path "$workspaceDir\docker_test.py" -Value $pythonScript

Write-Host "Sample Python script created at: $workspaceDir\docker_test.py"

# 提交测试作业到Docker集群
Write-Host "Submitting test job to Docker cluster..."
docker run --rm --network spark_spark-network -v "$workspaceDir:/app" bitnami/spark:3.4 /opt/bitnami/spark/bin/spark-submit --master spark://spark-master:7077 /app/docker_test.py

Write-Host "Spark cluster with Docker is running!"
Write-Host "Spark Master UI: http://localhost:8080"
Write-Host "Spark History Server UI: http://localhost:18080"
Write-Host "To stop the cluster, run: docker-compose down in $workspaceDir"