# 基于Ubuntu基础镜像
FROM mcr.microsoft.com/devcontainers/base:ubuntu

# 设置工作目录
WORKDIR /workspace

# 安装系统工具
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    vim \
    htop \
    tree \
    jq \
    && rm -rf /var/lib/apt/lists/*

# 安装开发工具
RUN curl -fsSL https://get.docker.com | sh

# 设置非root用户
RUN useradd -m -s /bin/bash vscode && \
    usermod -aG docker vscode

# 复制设置脚本
COPY setup.sh /workspace/.devcontainer/setup.sh
RUN chmod +x /workspace/.devcontainer/setup.sh

# 切换用户
USER vscode

# 设置环境变量
ENV PATH="/home/vscode/.local/bin:${PATH}"