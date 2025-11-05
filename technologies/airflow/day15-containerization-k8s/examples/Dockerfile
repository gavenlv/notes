# 使用官方Airflow基础镜像
FROM apache/airflow:2.7.0

# 设置环境变量
ENV AIRFLOW__CORE__EXECUTOR=LocalExecutor
ENV AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
ENV AIRFLOW__CORE__FERNET_KEY=''
ENV AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=True
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV AIRFLOW__API__AUTH_BACKENDS=airflow.api.auth.backend.basic_auth

# 安装额外的依赖
COPY requirements.txt /
RUN pip install --no-cache -r /requirements.txt

# 复制自定义DAGs
COPY dags/ /opt/airflow/dags/

# 复制自定义插件
COPY plugins/ /opt/airflow/plugins/

# 复制配置文件
COPY config/airflow.cfg /opt/airflow/airflow.cfg

# 设置用户权限
USER root
RUN chown -R airflow: /opt/airflow
USER airflow

# 暴露Web服务器端口
EXPOSE 8080

# 设置默认命令
CMD ["airflow", "webserver"]