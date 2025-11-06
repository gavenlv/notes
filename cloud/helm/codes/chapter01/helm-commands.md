# Helm常用命令示例

## 1. 仓库管理命令

```bash
# 添加仓库
helm repo add stable https://charts.helm.sh/stable
helm repo add bitnami https://charts.bitnami.com/bitnami

# 更新仓库
helm repo update

# 列出已添加的仓库
helm repo list

# 删除仓库
helm repo remove stable
```

## 2. Chart查找命令

```bash
# 搜索Charts
helm search repo nginx

# 查看Chart信息
helm show chart bitnami/nginx

# 查看Chart的默认values
helm show values bitnami/nginx
```

## 3. Release管理命令

```bash
# 安装Release
helm install my-nginx bitnami/nginx

# 列出所有Release
helm list

# 查看Release状态
helm status my-nginx

# 卸载Release
helm uninstall my-nginx
```

## 4. 其他常用命令

```bash
# 创建自己的Chart
helm create my-chart

# 验证Chart格式
helm lint my-chart

# 本地渲染模板（不部署）
helm template my-release ./my-chart

# 升级Release
helm upgrade my-nginx bitnami/nginx --set service.port=8080

# 回滚Release
helm rollback my-nginx 1
```