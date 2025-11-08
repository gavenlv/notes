#!/bin/bash

# Apache Spark安装脚本
# 适用于Linux/macOS系统

# 设置Spark版本
SPARK_VERSION="3.4.0"
HADOOP_VERSION="3"
SPARK_PACKAGE="spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz"

# 设置安装目录
INSTALL_DIR="/opt"
SPARK_HOME="${INSTALL_DIR}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}"

# 检查是否以root权限运行
if [[ $EUID -ne 0 ]]; then
   echo "此脚本需要root权限运行，请使用sudo" 
   exit 1
fi

# 创建安装目录
mkdir -p ${INSTALL_DIR}

echo "开始安装Apache Spark ${SPARK_VERSION}..."

# 下载Spark
echo "1. 下载Spark..."
cd ${INSTALL_DIR}
wget -q https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/${SPARK_PACKAGE}

if [ $? -ne 0 ]; then
    echo "下载Spark失败，请检查网络连接"
    exit 1
fi

# 解压Spark
echo "2. 解压Spark..."
tar -xzf ${SPARK_PACKAGE}

# 创建软链接
echo "3. 创建软链接..."
ln -sf ${SPARK_HOME} ${INSTALL_DIR}/spark

# 设置权限
chown -R root:root ${SPARK_HOME}
chmod -R 755 ${SPARK_HOME}

# 配置环境变量
echo "4. 配置环境变量..."
cat > /etc/profile.d/spark.sh << EOF
export SPARK_HOME=${INSTALL_DIR}/spark
export PATH=\$PATH:\$SPARK_HOME/bin:\$SPARK_HOME/sbin
export PYSPARK_PYTHON=\$(which python3)
EOF

# 应用环境变量
source /etc/profile.d/spark.sh

# 创建日志目录
mkdir -p /var/log/spark
chown -R root:root /var/log/spark
chmod -R 755 /var/log/spark

# 创建Spark配置目录
mkdir -p ${SPARK_HOME}/conf

# 配置Spark默认属性
echo "5. 配置Spark默认属性..."
cat > ${SPARK_HOME}/conf/spark-defaults.conf << EOF
# 默认配置
spark.master                     local[*]
spark.app.name                   SparkApp
spark.driver.memory              1g
spark.executor.memory            1g
spark.executor.cores              2

# 序列化配置
spark.serializer                 org.apache.spark.serializer.KryoSerializer

# 内存配置
spark.memory.fraction            0.6
spark.memory.storageFraction    0.5

# SQL配置
spark.sql.shuffle.partitions     8

# 事件日志
spark.eventLog.enabled           true
spark.eventLog.dir               hdfs://namenode:8020/spark-logs

# 网络配置
spark.network.timeout            300s
spark.rpc.askTimeout             300s
EOF

# 配置环境变量
echo "6. 配置环境变量..."
cat > ${SPARK_HOME}/conf/spark-env.sh << EOF
#!/bin/bash

# 设置Java Home
export JAVA_HOME=\$(readlink -f /usr/bin/java | sed "s:bin/java::")
export JAVA_HOME=\$(dirname \$(dirname \$JAVA_HOME))

# 设置Scala Home（可选）
export SCALA_HOME=/usr/share/scala

# 设置Spark Home
export SPARK_HOME=${SPARK_HOME}

# 设置Hadoop配置目录（可选）
export HADOOP_CONF_DIR=/etc/hadoop/conf
export YARN_CONF_DIR=/etc/hadoop/conf

# 设置Python
export PYSPARK_PYTHON=\$(which python3)

# 设置Java选项
export SPARK_DRIVER_EXTRA_JAVA_OPTIONS="-Dspark.driver.extraJavaOptions=-XX:+UseG1GC"
export SPARK_EXECUTOR_EXTRA_JAVA_OPTIONS="-XX:+UseG1GC"

# IP绑定
export SPARK_LOCAL_IP="127.0.0.1"
export SPARK_PUBLIC_DNS="localhost"

# 日志配置
export SPARK_LOG_DIR=/var/log/spark
EOF

# 设置权限
chmod +x ${SPARK_HOME}/conf/spark-env.sh

# 创建示例脚本目录
echo "7. 创建示例脚本目录..."
mkdir -p ${INSTALL_DIR}/spark-examples
cd ${INSTALL_DIR}/spark-examples

# 创建示例脚本
cat > run_wordcount.py << 'EOF'
#!/usr/bin/env python3

from pyspark import SparkContext
import sys

if __name__ == "__main__":
    sc = SparkContext(appName="WordCount")
    
    # 创建示例数据
    words = ["hello", "world", "hello", "spark", "python", "spark"]
    rdd = sc.parallelize(words)
    
    # 计算词频
    counts = rdd.map(lambda word: (word, 1)).reduceByKey(lambda a, b: a + b)
    
    # 输出结果
    for word, count in counts.collect():
        print(f"{word}: {count}")
    
    sc.stop()
EOF

chmod +x run_wordcount.py

# 创建运行脚本
cat > run_spark_example.sh << 'EOF'
#!/bin/bash

# 运行Spark示例脚本
cd $(dirname $0)
spark-submit run_wordcount.py
EOF

chmod +x run_spark_example.sh

# 验证安装
echo "8. 验证安装..."
source /etc/profile.d/spark.sh
spark-submit --version > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "Spark安装成功!"
    echo "版本信息:"
    spark-submit --version
    echo ""
    echo "使用方法:"
    echo "1. 运行示例: cd ${INSTALL_DIR}/spark-examples && ./run_spark_example.sh"
    echo "2. 启动Shell: spark-shell 或 pyspark"
    echo "3. 提交应用: spark-submit your_app.py"
    echo ""
    echo "配置文件位置:"
    echo "- Spark配置: ${SPARK_HOME}/conf/"
    echo "- 环境变量: /etc/profile.d/spark.sh"
else
    echo "Spark安装验证失败，请检查错误信息"
    exit 1
fi

echo "Spark安装完成!"