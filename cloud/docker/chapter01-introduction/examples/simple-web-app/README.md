# 简单Web应用示例

## 项目介绍

这是一个最简单的Docker Web应用示例，用于演示如何：
- 运行一个Web服务器容器
- 自定义网页内容
- 理解容器的文件系统

## 方式1：使用默认Nginx镜像

### 步骤1：直接运行Nginx

```bash
# 运行Nginx容器
docker run -d -p 8080:80 --name my-web nginx

# 在浏览器访问
# http://localhost:8080
```

你会看到Nginx的默认欢迎页面。

### 步骤2：查看容器内部

```bash
# 进入容器
docker exec -it my-web bash

# 查看网页文件位置
ls /usr/share/nginx/html/

# 查看默认页面
cat /usr/share/nginx/html/index.html

# 退出容器
exit
```

## 方式2：挂载自定义HTML文件

### 步骤1：使用本示例的index.html

```powershell
# Windows PowerShell
cd chapter01-introduction/examples/simple-web-app

docker run -d -p 8080:80 --name my-custom-web `
  -v ${PWD}/index.html:/usr/share/nginx/html/index.html `
  nginx
```

```bash
# Linux/Mac
cd chapter01-introduction/examples/simple-web-app

docker run -d -p 8080:80 --name my-custom-web \
  -v $(pwd)/index.html:/usr/share/nginx/html/index.html \
  nginx
```

### 步骤2：访问自定义页面

打开浏览器访问：http://localhost:8080

你会看到我们自定义的精美页面！

### 步骤3：实时修改页面

1. 编辑 `index.html` 文件
2. 刷新浏览器
3. 立即看到变化！

**原理**：
- `-v` 参数将主机文件挂载到容器
- 容器直接读取主机文件
- 修改主机文件，容器内容同步更新

## 方式3：复制文件到容器

### 步骤1：运行容器

```bash
docker run -d -p 8080:80 --name my-web nginx
```

### 步骤2：复制自定义文件到容器

```bash
# 复制文件到容器
docker cp index.html my-web:/usr/share/nginx/html/index.html

# 重启Nginx使其生效
docker exec my-web nginx -s reload
```

### 步骤3：访问页面

打开浏览器访问：http://localhost:8080

## 实验练习

### 练习1：修改页面标题

1. 编辑 `index.html`
2. 修改 `<h1>` 标签内容
3. 使用方式2运行容器
4. 观察变化

### 练习2：添加动态时间

在HTML中添加以下代码：

```html
<script>
  document.addEventListener('DOMContentLoaded', function() {
    const timeDiv = document.createElement('div');
    timeDiv.style.textAlign = 'center';
    timeDiv.style.marginTop = '20px';
    timeDiv.style.fontSize = '20px';
    
    function updateTime() {
      const now = new Date();
      timeDiv.textContent = '当前时间：' + now.toLocaleString();
    }
    
    updateTime();
    setInterval(updateTime, 1000);
    
    document.querySelector('.container').appendChild(timeDiv);
  });
</script>
```

### 练习3：添加多个页面

**创建about.html**：

```html
<!DOCTYPE html>
<html>
<head>
    <title>关于页面</title>
</head>
<body>
    <h1>关于Docker</h1>
    <p>Docker是一个容器化平台...</p>
    <a href="index.html">返回首页</a>
</body>
</html>
```

**挂载多个文件**：

```bash
docker run -d -p 8080:80 --name my-multi-web \
  -v $(pwd)/index.html:/usr/share/nginx/html/index.html \
  -v $(pwd)/about.html:/usr/share/nginx/html/about.html \
  nginx
```

访问：
- http://localhost:8080/index.html
- http://localhost:8080/about.html

## 常见问题

### Q1: 端口已被占用怎么办？

```bash
# 更换主机端口
docker run -d -p 9090:80 --name my-web nginx
# 访问 http://localhost:9090
```

### Q2: 如何查看容器日志？

```bash
docker logs my-web

# 实时跟踪日志
docker logs -f my-web
```

### Q3: 如何进入容器调试？

```bash
# 进入bash
docker exec -it my-web bash

# 执行单个命令
docker exec my-web ls /usr/share/nginx/html/
```

### Q4: 如何停止和清理容器？

```bash
# 停止容器
docker stop my-web

# 删除容器
docker rm my-web

# 强制删除运行中的容器
docker rm -f my-web
```

## 学习要点

✅ **理解容器的文件系统**
- 容器有自己的文件系统
- 可以通过挂载(-v)访问主机文件
- 可以通过docker cp复制文件

✅ **理解端口映射**
- `-p 主机端口:容器端口`
- 容器内部运行在80端口
- 主机通过映射的端口访问

✅ **理解容器的隔离性**
- 容器内的进程独立运行
- 容器有自己的网络空间
- 容器间互不影响

✅ **掌握基本操作**
- 运行容器
- 进入容器
- 查看日志
- 复制文件

## 下一步

学习完这个示例后，继续学习：
1. [第2章：Docker基础概念](../../chapter02-basic-concepts/README.md)
2. 如何构建自定义镜像
3. 如何使用Dockerfile
4. 如何管理数据卷

---

**动手实践是最好的学习方式！🚀**
