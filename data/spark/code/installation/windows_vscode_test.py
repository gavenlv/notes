# code/installation/windows_vscode_test.py
# VS Code中测试Spark环境的简单脚本

import os
import sys

def setup_spark_environment():
    """设置Spark环境"""
    # 添加Spark路径
    spark_home = os.environ.get('SPARK_HOME', 'C:\\spark')
    if not os.path.exists(spark_home):
        print(f"Error: SPARK_HOME directory not found: {spark_home}")
        return False
    
    sys.path.insert(0, os.path.join(spark_home, 'python'))
    
    # 添加Py4J路径
    import glob
    py4j_files = glob.glob(os.path.join(spark_home, 'python', 'lib', 'py4j-*.jar'))
    if not py4j_files:
        print("Error: Py4J JAR files not found")
        return False
    
    sys.path.insert(0, py4j_files[0])
    return True

def test_spark():
    """测试Spark功能"""
    try:
        from pyspark.sql import SparkSession
        
        # 创建临时目录
        import tempfile
        temp_dir = tempfile.mkdtemp()
        warehouse_dir = f"file:///{temp_dir.replace(chr(92), '/')}"
        
        # 创建Spark会话
        spark = SparkSession.builder \
            .appName("VS Code Windows Test") \
            .config("spark.driver.memory", "1g") \
            .config("spark.sql.warehouse.dir", warehouse_dir) \
            .config("spark.master", "local[2]") \
            .getOrCreate()
        
        # 测试创建DataFrame
        print("1. Creating DataFrame...")
        data = [(1, "Windows", "Test"), (2, "Spark", "Environment")]
        df = spark.createDataFrame(data, ["id", "word1", "word2"])
        df.show()
        
        # 测试SQL查询
        print("2. Running SQL query...")
        df.createOrReplaceTempView("test_data")
        result = spark.sql("SELECT * FROM test_data WHERE id > 1")
        result.show()
        
        # 测试RDD操作
        print("3. Testing RDD operations...")
        rdd = spark.sparkContext.parallelize(range(1, 11))
        even_numbers = rdd.filter(lambda x: x % 2 == 0).collect()
        print(f"Even numbers: {even_numbers}")
        
        # 停止Spark会话
        spark.stop()
        return True
        
    except Exception as e:
        print(f"Error testing Spark: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("Testing Spark installation in Windows VS Code environment...")
    
    # 检查Java
    print("0. Checking Java installation...")
    try:
        import subprocess
        java_version = subprocess.check_output(["java", "-version"], stderr=subprocess.STDOUT, text=True)
        print(f"Java version: {java_version}")
    except:
        print("Error: Java not found. Please install Java JDK.")
        return False
    
    # 设置Spark环境
    print("1. Setting up Spark environment...")
    if not setup_spark_environment():
        return False
    
    # 测试Spark
    print("2. Testing Spark functionality...")
    if test_spark():
        print("Spark is working correctly in VS Code!")
        return True
    else:
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)