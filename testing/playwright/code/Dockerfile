# Dockerfile
FROM mcr.microsoft.com/playwright:v1.38.0-jammy

WORKDIR /app

# 复制package文件
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制应用代码
COPY . .

# 安装浏览器
RUN npx playwright install --with-deps

# 暴露端口
EXPOSE 3000

# 启动命令
CMD ["npm", "start"]