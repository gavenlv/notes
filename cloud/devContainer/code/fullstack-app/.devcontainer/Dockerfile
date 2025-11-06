# 基于Node.js镜像
FROM mcr.microsoft.com/devcontainers/javascript-node:18

# 设置工作目录
WORKDIR /workspace

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制package.json
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制源代码
COPY . .

# 设置健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# 暴露端口
EXPOSE 5000

# 设置默认用户
USER node