# 第1章练习题

## 基础练习

### 练习1：验证Docker安装

**目标**：确认Docker在你的系统上正确安装和运行

**任务**：
1. 打开终端/命令行
2. 运行以下命令并记录输出：
   ```bash
   docker --version
   docker version
   docker info
   ```
3. 截图保存输出结果

**检查点**：
- [ ] Docker版本显示正常
- [ ] Client和Server都能正常连接
- [ ] 没有权限错误

---

### 练习2：运行第一个容器

**目标**：理解容器的基本运行流程

**任务**：
1. 运行hello-world容器：
   ```bash
   docker run hello-world
   ```
2. 回答以下问题：
   - 这个命令做了什么？
   - 镜像从哪里下载？
   - 容器运行后发生了什么？

**检查点**：
- [ ] 成功看到"Hello from Docker!"消息
- [ ] 理解了容器的运行流程
- [ ] 明白了镜像和容器的关系

---

### 练习3：启动Web服务器

**目标**：学习端口映射和后台运行

**任务**：
1. 启动Nginx容器：
   ```bash
   docker run -d -p 8080:80 --name my-web nginx
   ```
2. 在浏览器访问 http://localhost:8080
3. 查看容器状态：
   ```bash
   docker ps
   ```
4. 查看容器日志：
   ```bash
   docker logs my-web
   ```
5. 停止并删除容器：
   ```bash
   docker stop my-web
   docker rm my-web
   ```

**检查点**：
- [ ] 浏览器能看到Nginx欢迎页面
- [ ] 理解了-d参数（后台运行）
- [ ] 理解了-p参数（端口映射）
- [ ] 理解了--name参数（容器命名）

---

## 进阶练习

### 练习4：交互式容器

**目标**：学习交互式容器的使用

**任务**：
1. 启动Ubuntu容器并进入bash：
   ```bash
   docker run -it --name ubuntu-test ubuntu bash
   ```
2. 在容器内执行以下操作：
   ```bash
   # 查看系统信息
   cat /etc/os-release
   
   # 查看当前目录
   pwd
   
   # 创建一个文件
   echo "Hello Docker" > test.txt
   cat test.txt
   
   # 查看环境变量
   env
   
   # 退出容器
   exit
   ```
3. 再次启动这个容器：
   ```bash
   docker start ubuntu-test
   docker attach ubuntu-test
   ```
4. 检查之前创建的文件是否还在

**检查点**：
- [ ] 成功进入容器内部
- [ ] 理解了-it参数的作用
- [ ] 明白了容器的持久性
- [ ] 理解了attach和exec的区别

---

### 练习5：运行不同的服务

**目标**：熟悉常见服务的容器化运行

**任务1 - Redis**：
```bash
# 启动Redis
docker run -d --name my-redis -p 6379:6379 redis

# 使用redis-cli连接
docker exec -it my-redis redis-cli

# 在redis-cli中测试
SET mykey "Hello Redis"
GET mykey
exit

# 清理
docker stop my-redis
docker rm my-redis
```

**任务2 - MySQL**：
```bash
# 启动MySQL
docker run -d \
  --name my-mysql \
  -e MYSQL_ROOT_PASSWORD=mypassword \
  -p 3306:3306 \
  mysql:8.0

# 等待MySQL启动完成（约30秒）
docker logs my-mysql

# 连接到MySQL
docker exec -it my-mysql mysql -uroot -pmypassword

# 在MySQL中测试
SHOW DATABASES;
exit

# 清理
docker stop my-mysql
docker rm my-mysql
```

**检查点**：
- [ ] 成功运行Redis和MySQL
- [ ] 理解了环境变量的使用（-e参数）
- [ ] 能够进入容器执行命令

---

### 练习6：镜像管理

**目标**：掌握镜像的基本管理操作

**任务**：
1. 搜索Python镜像：
   ```bash
   docker search python
   ```
2. 拉取不同版本的Python镜像：
   ```bash
   docker pull python:3.9
   docker pull python:3.10
   docker pull python:3.11
   ```
3. 查看本地镜像：
   ```bash
   docker images
   docker images python
   ```
4. 查看镜像详细信息：
   ```bash
   docker inspect python:3.11
   ```
5. 删除不需要的镜像：
   ```bash
   docker rmi python:3.9
   ```

**检查点**：
- [ ] 理解了镜像的标签（tag）
- [ ] 能够管理本地镜像
- [ ] 知道如何查看镜像详细信息

---

### 练习7：容器资源限制

**目标**：学习如何限制容器资源

**任务**：
1. 限制内存运行容器：
   ```bash
   docker run -d --name nginx-limited \
     -m 256m \
     --memory-swap 256m \
     nginx
   ```
2. 查看容器资源使用：
   ```bash
   docker stats nginx-limited --no-stream
   ```
3. 限制CPU运行容器：
   ```bash
   docker run -d --name nginx-cpu \
     --cpus="0.5" \
     nginx
   ```
4. 查看容器详细配置：
   ```bash
   docker inspect nginx-limited
   docker inspect nginx-cpu
   ```

**检查点**：
- [ ] 理解了内存限制参数
- [ ] 理解了CPU限制参数
- [ ] 能够监控容器资源使用

---

## 综合练习

### 练习8：容器生命周期管理

**目标**：完整理解容器的生命周期

**任务**：
1. 创建一个Nginx容器但不启动：
   ```bash
   docker create --name nginx-lifecycle -p 8888:80 nginx
   ```
2. 查看容器状态：
   ```bash
   docker ps -a
   ```
3. 启动容器：
   ```bash
   docker start nginx-lifecycle
   ```
4. 暂停容器：
   ```bash
   docker pause nginx-lifecycle
   ```
5. 恢复容器：
   ```bash
   docker unpause nginx-lifecycle
   ```
6. 重启容器：
   ```bash
   docker restart nginx-lifecycle
   ```
7. 停止容器：
   ```bash
   docker stop nginx-lifecycle
   ```
8. 删除容器：
   ```bash
   docker rm nginx-lifecycle
   ```

**记录每一步的容器状态变化**

**检查点**：
- [ ] 理解created状态
- [ ] 理解running状态
- [ ] 理解paused状态
- [ ] 理解stopped状态

---

### 练习9：多容器协作

**目标**：理解容器间的通信

**任务**：
1. 创建自定义网络：
   ```bash
   docker network create my-network
   ```
2. 启动MySQL容器：
   ```bash
   docker run -d \
     --name db \
     --network my-network \
     -e MYSQL_ROOT_PASSWORD=rootpass \
     -e MYSQL_DATABASE=testdb \
     mysql:8.0
   ```
3. 启动Web应用连接MySQL：
   ```bash
   docker run -d \
     --name webapp \
     --network my-network \
     -e DB_HOST=db \
     -e DB_PASSWORD=rootpass \
     -p 8080:80 \
     nginx
   ```
4. 测试容器间通信：
   ```bash
   docker exec webapp ping db -c 3
   ```

**检查点**：
- [ ] 理解了Docker网络
- [ ] 容器能通过名称互相访问
- [ ] 理解了环境变量的作用

---

### 练习10：系统清理

**目标**：学习清理Docker资源

**任务**：
1. 查看磁盘使用：
   ```bash
   docker system df
   ```
2. 清理停止的容器：
   ```bash
   docker container prune
   ```
3. 清理未使用的镜像：
   ```bash
   docker image prune
   ```
4. 清理未使用的网络：
   ```bash
   docker network prune
   ```
5. 清理所有未使用的资源：
   ```bash
   docker system prune -a
   ```

**检查点**：
- [ ] 理解了Docker的磁盘占用
- [ ] 知道如何清理资源
- [ ] 理解了-a参数的区别

---

## 思考题

1. **容器和虚拟机的本质区别是什么？**
   - 提示：从隔离级别、启动速度、资源占用等方面思考

2. **为什么Docker容器停止后，再次启动还能看到之前的数据？**
   - 提示：思考容器的分层结构

3. **如果不指定镜像标签，Docker会拉取哪个版本？**
   - 提示：默认标签是什么

4. **容器删除后，数据会怎样？**
   - 提示：思考数据持久化问题

5. **为什么需要端口映射？**
   - 提示：思考容器网络隔离

---

## 实战挑战

### 挑战1：一键启动开发环境

**任务**：编写一个脚本，一键启动包含以下服务的开发环境：
- Nginx (端口8080)
- MySQL (端口3306)
- Redis (端口6379)

**要求**：
- 所有服务在同一网络
- 可以优雅停止和清理
- 显示所有服务状态

### 挑战2：容器健康检查

**任务**：运行一个带健康检查的容器
```bash
docker run -d \
  --name nginx-health \
  --health-cmd="curl -f http://localhost/ || exit 1" \
  --health-interval=30s \
  --health-timeout=3s \
  --health-retries=3 \
  -p 8080:80 \
  nginx
```

观察健康状态的变化：
```bash
docker ps
docker inspect nginx-health --format='{{.State.Health.Status}}'
```

---

## 练习答案检查

完成每个练习后，在这里打勾：

- [ ] 练习1：验证Docker安装
- [ ] 练习2：运行第一个容器
- [ ] 练习3：启动Web服务器
- [ ] 练习4：交互式容器
- [ ] 练习5：运行不同的服务
- [ ] 练习6：镜像管理
- [ ] 练习7：容器资源限制
- [ ] 练习8：容器生命周期管理
- [ ] 练习9：多容器协作
- [ ] 练习10：系统清理

完成所有练习后，你应该能够：
✅ 熟练使用Docker基本命令
✅ 理解容器的生命周期
✅ 管理镜像和容器
✅ 配置容器网络和资源
✅ 运行常见的服务容器

**继续前往第2章学习更深入的内容！**
