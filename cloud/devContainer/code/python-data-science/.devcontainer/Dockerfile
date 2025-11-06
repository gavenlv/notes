# 基于官方Python镜像
FROM mcr.microsoft.com/devcontainers/python:3.11

# 设置工作目录
WORKDIR /workspace

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 安装Python包
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 设置Jupyter配置
RUN mkdir -p /home/vscode/.jupyter && \
    echo "c.NotebookApp.ip = '0.0.0.0'" >> /home/vscode/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.port = 8888" >> /home/vscode/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.allow_origin = '*'" >> /home/vscode/.jupyter/jupyter_notebook_config.py

# 设置默认用户
USER vscode