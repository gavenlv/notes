# 第6章：Vite生产环境部署与CI/CD

本章将深入探讨如何将Vite项目从开发环境顺利过渡到生产环境，包括构建优化、多环境配置、部署策略以及CI/CD自动化流程的实现。通过本章学习，你将能够掌握企业级应用的完整发布流程。

## 6.1 生产环境构建基础

### 6.1.1 构建命令与配置

Vite提供了简单的构建命令来生成生产环境代码：

```bash
# 使用npm
npm run build

# 使用yarn
yarn build

# 使用pnpm
pnpm build
```

构建命令会执行`vite build`，根据vite.config.js中的配置生成优化后的静态资源。

### 6.1.2 构建输出目录

默认情况下，构建产物会输出到`dist`目录。可以通过配置修改输出目录：

```javascript
// vite.config.js
import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    outDir: 'build', // 修改输出目录为build
  }
})
```

### 6.1.3 构建产物分析

构建后的产物结构通常如下：

```
dist/
├── assets/
│   ├── index.xxxx.js        # 主入口JS文件（带哈希值，用于缓存控制）
│   ├── vendor.xxxx.js       # 第三方依赖包
│   ├── index.xxxx.css       # 样式文件
│   └── some-image.xxxx.png  # 图片等静态资源
├── index.html               # HTML入口文件
└── favicon.ico              # 网站图标
```

## 6.2 构建优化配置

### 6.2.1 资源优化配置

```javascript
// vite.config.js
import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    // 生成map文件，用于调试
    sourcemap: false,
    // 自定义底层的Rollup打包配置
    rollupOptions: {
      // 输出配置
      output: {
        // 静态资源分类打包
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]'
      },
      // 手动分割代码
      manualChunks: {
        // 将React相关库打包成单独的chunk
        react: ['react', 'react-dom'],
        // 将组件库打包成单独的chunk
        ui: ['antd', 'element-plus'],
        // 将工具库打包成单独的chunk
        utils: ['lodash', 'axios']
      }
    },
    // 小于此阈值的资源内联为base64
    assetsInlineLimit: 4096,
    // 启用CSS代码分割
    cssCodeSplit: true,
    // 生产环境是否启用CSS的sourcemap
    cssSourceMap: false,
    // 浏览器兼容性目标
    target: 'es2015'
  }
})
```

### 6.2.2 压缩配置

Vite默认使用ESbuild进行代码压缩，但也支持配置Terser：

```javascript
// vite.config.js
import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    // 禁用ESbuild压缩，使用Terser
    minify: 'terser',
    terserOptions: {
      // Terser配置选项
      compress: {
        drop_console: true, // 移除console
        drop_debugger: true, // 移除debugger
      },
      format: {
        comments: false, // 移除注释
      },
    },
  }
})
```

### 6.2.3 多页面应用配置

对于多页面应用，可以这样配置：

```javascript
// vite.config.js
import { defineConfig } from 'vite'
import { resolve } from 'path'

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        admin: resolve(__dirname, 'admin/index.html'),
        user: resolve(__dirname, 'user/index.html'),
      },
    },
  },
})
```

## 6.3 环境变量管理

### 6.3.1 环境变量类型

Vite支持多种环境变量文件：

- `.env`: 所有环境通用
- `.env.local`: 所有环境通用，但不会提交到Git
- `.env.development`: 开发环境专用
- `.env.production`: 生产环境专用
- `.env.[mode].local`: 特定模式专用，不会提交到Git

### 6.3.2 环境变量定义

在环境变量文件中定义变量，变量名必须以`VITE_`开头：

```env
# .env.production
VITE_API_BASE_URL=https://api.example.com
VITE_APP_ENV=production
```

### 6.3.3 在代码中使用环境变量

在代码中可以通过`import.meta.env`访问环境变量：

```javascript
// 使用环境变量
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;
const appEnv = import.meta.env.VITE_APP_ENV;

console.log(`API Base URL: ${apiBaseUrl}`);
console.log(`App Environment: ${appEnv}`);
```

### 6.3.4 自定义环境模式

除了默认的`development`和`production`，还可以定义自定义模式：

```bash
# 构建时指定模式
vite build --mode staging
```

然后创建对应的环境变量文件`.env.staging`。

## 6.4 静态网站部署

### 6.4.1 部署到GitHub Pages

1. 安装gh-pages工具：

```bash
npm install -D gh-pages
```

2. 添加部署脚本到package.json：

```json
{
  "scripts": {
    "build": "vite build",
    "deploy": "gh-pages -d dist"
  }
}
```

3. 配置vite.config.js中的base路径：

```javascript
// vite.config.js
import { defineConfig } from 'vite'

export default defineConfig({
  base: '/your-repo-name/', // GitHub Pages仓库路径
})
```

4. 执行部署：

```bash
npm run build && npm run deploy
```

### 6.4.2 部署到Vercel

1. 登录[Vercel](https://vercel.com)，连接GitHub仓库。

2. 创建新的Vercel项目，选择你的仓库。

3. Vercel会自动检测到Vite项目并配置正确的构建命令。

4. 点击Deploy进行部署。

Vercel配置示例：
- 构建命令: `npm run build`
- 输出目录: `dist`
- 环境变量: 可以在Vercel项目设置中配置

### 6.4.3 部署到Netlify

1. 登录[Netlify](https://www.netlify.com)，连接GitHub仓库。

2. 配置部署设置：
   - 构建命令: `npm run build`
   - 发布目录: `dist`

3. 点击Deploy site进行部署。

### 6.4.4 部署到传统服务器

1. 构建项目：

```bash
npm run build
```

2. 将dist目录下的文件上传到服务器的web目录，如Nginx的默认目录：

```bash
scp -r dist/* user@server:/var/www/html/
```

3. 配置Nginx：

```nginx
server {
    listen 80;
    server_name example.com;

    root /var/www/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

## 6.5 Docker容器化部署

### 6.5.1 创建Dockerfile

```dockerfile
# 第一阶段：构建
FROM node:16-alpine as build

WORKDIR /app

# 复制package.json和package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制源代码
COPY . .

# 构建生产版本
RUN npm run build

# 第二阶段：使用Nginx提供服务
FROM nginx:alpine

# 复制构建产物到Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# 复制自定义Nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露80端口
EXPOSE 80

# 启动Nginx
CMD ["nginx", "-g", "daemon off;"]
```

### 6.5.2 创建Nginx配置文件

```nginx
# nginx.conf
server {
    listen 80;
    server_name localhost;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # 配置API代理
    location /api {
        proxy_pass http://api-server:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 6.5.3 构建和运行Docker容器

```bash
# 构建Docker镜像
docker build -t my-vite-app .

# 运行Docker容器
docker run -d -p 8080:80 my-vite-app
```

### 6.5.4 使用Docker Compose

创建docker-compose.yml：

```yaml
version: '3'

services:
  frontend:
    build: .
    ports:
      - "8080:80"
    depends_on:
      - api
    environment:
      - VITE_API_BASE_URL=http://api:3000

  api:
    image: node:16-alpine
    working_dir: /app
    volumes:
      - ./api:/app
    ports:
      - "3000:3000"
    command: sh -c "npm install && npm start"
    environment:
      - NODE_ENV=production
```

运行：

```bash
docker-compose up -d
```

## 6.6 CI/CD配置

### 6.6.1 GitHub Actions配置

创建`.github/workflows/deploy.yml`：

```yaml
name: Deploy Vite App

on:
  push:
    branches: [ main, master ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '16'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm test
      
      - name: Build
        run: npm run build
        env:
          VITE_API_BASE_URL: ${{ secrets.VITE_API_BASE_URL }}
      
      # 部署到GitHub Pages
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./dist
      
      # 部署到Vercel（可选）
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
```

### 6.6.2 GitLab CI/CD配置

创建`.gitlab-ci.yml`：

```yaml
stages:
  - test
  - build
  - deploy

variables:
  NODE_ENV: production

cache:
  paths:
    - node_modules/

test:
  stage: test
  image: node:16-alpine
  script:
    - npm ci
    - npm test

build:
  stage: build
  image: node:16-alpine
  script:
    - npm ci
    - npm run build
    - echo "Build completed successfully"
  artifacts:
    paths:
      - dist/
    expire_in: 1 week

# 部署到GitLab Pages
deploy-pages:
  stage: deploy
  dependencies:
    - build
  script:
    - mkdir -p public
    - cp -r dist/* public/
  artifacts:
    paths:
      - public
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

# 部署到服务器（通过SSH）
deploy-server:
  stage: deploy
  image: alpine:latest
  dependencies:
    - build
  before_script:
    - apk add --no-cache openssh-client rsync
    - mkdir -p ~/.ssh
    - echo "$SSH_PRIVATE_KEY" > ~/.ssh/id_rsa
    - chmod 600 ~/.ssh/id_rsa
    - echo -e "Host *\n\tStrictHostKeyChecking no\n\n" > ~/.ssh/config
  script:
    - rsync -avz --delete ./dist/ user@server:/var/www/html/
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

### 6.6.3 环境变量管理

在CI/CD系统中配置环境变量：

- **GitHub Actions**：在仓库 Settings > Secrets > Actions 中添加
- **GitLab CI**：在项目 Settings > CI/CD > Variables 中添加

## 6.7 构建监控与分析

### 6.7.1 构建大小分析

使用`rollup-plugin-visualizer`来分析构建产物：

```bash
npm install -D rollup-plugin-visualizer
```

配置vite.config.js：

```javascript
// vite.config.js
import { defineConfig } from 'vite'
import { visualizer } from 'rollup-plugin-visualizer'

export default defineConfig({
  plugins: [
    // 其他插件...
    visualizer({
      open: true,
      filename: 'stats.html',
      gzipSize: true,
      brotliSize: true
    })
  ]
})
```

### 6.7.2 性能预算设置

可以配置构建过程中的性能预算，当资源超过预算时发出警告或错误：

```javascript
// vite.config.js
import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          // 确保每个chunk不超过500kb
        }
      }
    },
    chunkSizeWarningLimit: 500, // 块大小警告限制（kb）
  }
})
```

## 6.8 高级部署策略

### 6.8.1 蓝绿部署

蓝绿部署允许我们在切换新版本前完全测试它：

1. 保持当前版本（蓝）正常运行
2. 部署新版本（绿）到隔离环境
3. 对绿环境进行测试
4. 确认绿环境工作正常后，将流量从蓝切换到绿

在Kubernetes中实现：

```yaml
# blue-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vite-app-blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: vite-app
      version: blue
  template:
    metadata:
      labels:
        app: vite-app
        version: blue
    spec:
      containers:
      - name: vite-app
        image: my-vite-app:v1
---
# green-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vite-app-green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: vite-app
      version: green
  template:
    metadata:
      labels:
        app: vite-app
        version: green
    spec:
      containers:
      - name: vite-app
        image: my-vite-app:v2
---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: vite-app-service
spec:
  selector:
    app: vite-app
    version: blue  # 切换到green以激活新版本
  ports:
  - port: 80
    targetPort: 80
  type: LoadBalancer
```

### 6.8.2 金丝雀发布

金丝雀发布允许我们将少量流量路由到新版本：

1. 部署新版本，但只接收一小部分流量（如5%）
2. 监控新版本的性能和错误率
3. 如果新版本表现良好，逐步增加流量比例
4. 最终完全切换到新版本

在Kubernetes中使用Istio实现金丝雀发布：

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: vite-app-vs
spec:
  hosts:
  - vite-app-service
  http:
  - route:
    - destination:
        host: vite-app-service
        subset: v1
      weight: 95
    - destination:
        host: vite-app-service
        subset: v2
      weight: 5
---
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: vite-app-dr
spec:
  host: vite-app-service
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

### 6.8.3 A/B测试部署

A/B测试部署允许我们将不同用户群体路由到不同版本，以比较功能效果：

```javascript
// 简化的前端A/B测试逻辑
function getVersion() {
  // 可以基于用户ID、Cookie或其他方式分配版本
  const userId = localStorage.getItem('userId') || generateUserId();
  localStorage.setItem('userId', userId);
  
  // 简单哈希算法确定用户所属组
  const hash = userId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  
  // 50%的用户看到A版本，50%看到B版本
  return hash % 2 === 0 ? 'version-a' : 'version-b';
}

// 根据版本加载不同资源或特性
const version = getVersion();
if (version === 'version-a') {
  // 加载A版本资源或启用A版本特性
  loadFeatureA();
} else {
  // 加载B版本资源或启用B版本特性
  loadFeatureB();
}
```

## 6.9 实验：部署Vite应用到生产环境

### 6.9.1 实验1：构建优化与GitHub Pages部署

**目标**：优化Vite应用的构建配置并部署到GitHub Pages。

**步骤**：

1. 创建一个基本的Vite项目：
```bash
npm create vite@latest deploy-demo -- --template react
cd deploy-demo
npm install
```

2. 优化vite.config.js：
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { visualizer } from 'rollup-plugin-visualizer'

// https://vitejs.dev/config/
export default defineConfig({
  base: '/deploy-demo/', // GitHub仓库名
  plugins: [
    react(),
    visualizer({
      open: true,
      filename: 'stats.html',
      gzipSize: true,
      brotliSize: true
    })
  ],
  build: {
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          // 根据需要分割其他依赖
        }
      }
    },
    chunkSizeWarningLimit: 500,
  }
})
```

3. 添加环境变量文件（.env.production）：
```env
VITE_APP_ENV=production
VITE_API_BASE_URL=https://api.example.com
```

4. 安装gh-pages并配置部署脚本：
```bash
npm install -D gh-pages
```

修改package.json：
```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "deploy": "gh-pages -d dist"
  }
}
```

5. 构建并部署：
```bash
npm run build && npm run deploy
```

### 6.9.2 实验2：Docker容器化部署

**目标**：使用Docker容器化Vite应用并部署。

**步骤**：

1. 在Vite项目根目录创建Dockerfile：
```dockerfile
FROM node:16-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

2. 创建nginx.conf：
```nginx
server {
    listen 80;
    server_name localhost;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

3. 构建Docker镜像：
```bash
docker build -t vite-docker-app .
```

4. 运行Docker容器：
```bash
docker run -d -p 8080:80 vite-docker-app
```

5. 访问http://localhost:8080查看部署结果。

## 6.10 最佳实践总结

1. **构建优化**：
   - 合理配置代码分割，减小单个chunk大小
   - 启用压缩和Tree-shaking
   - 优化静态资源，使用适当的缓存策略

2. **环境变量管理**：
   - 使用`.env`文件管理不同环境的配置
   - 敏感信息避免硬编码，使用环境变量或密钥管理服务

3. **部署策略选择**：
   - 小型项目可以使用GitHub Pages、Vercel等平台
   - 企业级应用考虑容器化部署和Kubernetes管理
   - 根据需求选择合适的部署策略（蓝绿、金丝雀、A/B测试）

4. **CI/CD自动化**：
   - 配置自动化测试和构建流程
   - 实现自动部署和回滚机制
   - 添加构建监控和性能分析

5. **安全性考虑**：
   - 构建过程中移除敏感信息
   - 配置HTTPS
   - 实施内容安全策略(CSP)

通过本章的学习，你应该能够熟练地将Vite项目部署到各种环境，并实现自动化的CI/CD流程。这将极大地提高开发效率和部署可靠性，为团队提供稳定、高效的应用发布渠道。