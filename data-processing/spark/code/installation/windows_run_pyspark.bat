@echo off
REM code/installation/windows_run_pyspark.bat
REM 启动PySpark的批处理脚本

REM 设置环境
call windows_setup_env.bat

REM 启动PySpark
echo.
echo Starting PySpark...
%pyspark_python% %SPARK_HOME%\python\pyspark\shell.py