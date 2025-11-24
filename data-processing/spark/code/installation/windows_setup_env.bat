@echo off
REM code/installation/windows_setup_env.bat
REM Windows批处理脚本设置Spark环境

REM 设置Spark环境变量
set SPARK_HOME=C:\spark
set HADOOP_HOME=C:\spark\hadoop
set JAVA_HOME=C:\Program Files\Java\jdk-11

REM 设置Python路径
set PYSPARK_PYTHON=python

REM 更新PATH
set PATH=%PATH%;%SPARK_HOME%\bin;%JAVA_HOME%\bin

REM 显示当前环境变量
echo SPARK_HOME: %SPARK_HOME%
echo HADOOP_HOME: %HADOOP_HOME%
echo JAVA_HOME: %JAVA_HOME%
echo PYSPARK_PYTHON: %PYSPARK_PYTHON%

echo.
echo Spark environment has been configured. You can now run:
echo   - pyspark
echo   - spark-shell
echo   - spark-submit