# 第7章：Docker网络

## 📚 本章目标

- 理解Docker网络模型和类型
- 掌握容器间的通信方式
- 学会创建和管理自定义网络
- 理解端口映射原理
- 掌握网络故障排查技巧

## 7.1 Docker网络模型

### 7.1.1 网络驱动类型

```
Docker网络驱动：

1. bridge   - 桥接网络（默认）
   └── 适用：单主机容器通信

2. host     - 主机网络
   └── 适用：性能优先，无需隔离

3. none     - 无网络
   └── 适用：完全隔离

4. overlay  - 覆盖网络
   └── 适用：Swarm跨主机通信

5. macvlan  - MAC地址网络
   └── 适用：容器需要物理网络地址
```

## 7.2 Bridge网络（默认）

### 7.2.1 默认bridge网络

```bash
# 查看网络列表
docker network ls

# 查看bridge网络详情
docker network inspect bridge

# 容器默认连接到bridge
docker run -d --name web1 nginx
docker run -d --name web2 nginx

# 容器间通过IP通信
docker exec web1 ping <web2-ip>
```

### 7.2.2 自定义bridge网络

```bash
# 创建自定义网络
docker network create my-network

# 指定子网
docker network create --subnet=172.20.0.0/16 my-net

# 运行容器连接到自定义网络
docker run -d --name app1 --network my-network nginx
docker run -d --name app2 --network my-network nginx

# 容器间通过名称通信
docker exec app1 ping app2  # ✅ 自动DNS解析
```

### 7.2.3 Bridge网络配置

```bash
# 完整配置
docker network create \
  --driver bridge \
  --subnet 172.28.0.0/16 \
  --ip-range 172.28.5.0/24 \
  --gateway 172.28.0.1 \
  my-custom-net

# 指定容器IP
docker run -d \
  --name web \
  --network my-custom-net \
  --ip 172.28.5.10 \
  nginx
```

## 7.3 Host网络

### 7.3.1 使用场景

```bash
# 容器使用主机网络栈
docker run -d --network host nginx

# 特点：
# ✅ 性能最佳（无网络隔离开销）
# ❌ 端口冲突（与主机共享端口）
# ❌ 无网络隔离

# 适用场景：
# - 性能关键应用
# - 网络监控工具
# - 需要访问主机网络服务
```

## 7.4 None网络

### 7.4.1 完全隔离

```bash
# 无网络容器
docker run -d --network none alpine

# 适用场景：
# - 高安全需求
# - 批处理任务
# - 不需要网络的应用
```

## 7.5 容器互联

### 7.5.1 同网络容器通信

```bash
# 创建网络
docker network create app-net

# 启动容器
docker run -d --name db --network app-net mysql
docker run -d --name web --network app-net nginx

# Web容器访问数据库
docker exec web ping db  # ✅ 通过名称
docker exec web ping db.app-net  # ✅ 完整域名
```

### 7.5.2 跨网络通信

```bash
# 容器连接多个网络
docker network create frontend
docker network create backend

docker run -d --name app nginx
docker network connect frontend app
docker network connect backend app

# 查看容器网络
docker inspect app --format '{{json .NetworkSettings.Networks}}'
```

## 7.6 端口映射

### 7.6.1 端口映射方式

```bash
# 映射到指定端口
docker run -d -p 8080:80 nginx

# 映射到随机端口
docker run -d -p 80 nginx
docker port <container>

# 指定协议
docker run -d -p 8080:80/tcp -p 53:53/udp nginx

# 指定IP
docker run -d -p 127.0.0.1:8080:80 nginx

# 多端口映射
docker run -d \
  -p 8080:80 \
  -p 8443:443 \
  nginx
```

### 7.6.2 端口映射原理

```
外部请求 → iptables规则 → Docker bridge → 容器

示例：
客户端:8080 → 主机:8080 → DNAT → 容器IP:80
```

## 7.7 网络别名

### 7.7.1 设置网络别名

```bash
# 为容器设置别名
docker run -d \
  --name db \
  --network my-net \
  --network-alias database \
  --network-alias mysql-server \
  mysql

# 通过别名访问
docker exec app ping database
docker exec app ping mysql-server
```

## 7.8 DNS配置

### 7.8.1 自定义DNS

```bash
# 指定DNS服务器
docker run -d \
  --dns 8.8.8.8 \
  --dns 8.8.4.4 \
  nginx

# 添加DNS搜索域
docker run -d \
  --dns-search example.com \
  nginx

# 添加hosts记录
docker run -d \
  --add-host myhost:192.168.1.100 \
  nginx
```

## 7.9 网络故障排查

### 7.9.1 诊断命令

```bash
# 查看容器网络配置
docker inspect <container> --format '{{.NetworkSettings}}'

# 查看网络详情
docker network inspect <network>

# 容器内网络诊断
docker exec -it <container> bash
apt-get update && apt-get install -y \
  iputils-ping \
  iproute2 \
  net-tools \
  dnsutils \
  curl

# 测试连接
ping <target>
curl <url>
nslookup <hostname>
traceroute <target>
netstat -tulpn
```

### 7.9.2 常见问题

```bash
# 问题1：容器无法通过名称互ping
# 原因：使用默认bridge网络
# 解决：使用自定义网络

# 问题2：端口映射不生效
# 检查端口冲突
netstat -tlnp | grep 8080
# 检查防火墙
sudo ufw status

# 问题3：容器无法访问外网
# 检查NAT配置
iptables -t nat -L -n
# 检查DNS
docker exec <container> cat /etc/resolv.conf
```

## 7.10 实战示例

### 示例1：三层架构

```bash
# 创建网络
docker network create frontend
docker network create backend

# 数据库（仅backend）
docker run -d \
  --name db \
  --network backend \
  mysql

# 应用（frontend + backend）
docker run -d \
  --name app \
  --network frontend \
  myapp
docker network connect backend app

# Nginx（仅frontend）
docker run -d \
  --name nginx \
  --network frontend \
  -p 80:80 \
  nginx
```

### 示例2：微服务网络

```bash
# 创建微服务网络
docker network create microservices

# API Gateway
docker run -d \
  --name gateway \
  --network microservices \
  -p 80:80 \
  api-gateway

# User Service
docker run -d \
  --name user-service \
  --network microservices \
  user-service

# Order Service
docker run -d \
  --name order-service \
  --network microservices \
  order-service

# Gateway可通过服务名访问
# http://user-service:8080
# http://order-service:8080
```

## 7.11 本章总结

### 核心知识点

✅ **网络类型**
- bridge（默认）
- host
- none
- overlay
- macvlan

✅ **容器通信**
- 同网络DNS解析
- 网络别名
- 跨网络连接

✅ **端口映射**
- 静态端口
- 动态端口
- 多端口

✅ **故障排查**
- 诊断工具
- 常见问题

---

**掌握Docker网络，构建复杂应用！🚀**
