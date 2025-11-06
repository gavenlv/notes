# Helm常用命令

## 添加仓库
```bash
# 添加官方仓库
helm repo add stable https://charts.helm.sh/stable

# 更新仓库
helm repo update

# 查看已添加的仓库
helm repo list
```

## 查找Chart
```bash
# 搜索Chart
helm search repo nginx

# 查看Chart详细信息
helm show chart stable/nginx-ingress
helm show values stable/nginx-ingress
```

## 安装和管理Release
```bash
# 安装Chart
helm install my-nginx stable/nginx-ingress

# 查看Release
helm list

# 查看Release状态
helm status my-nginx

# 卸载Release
helm uninstall my-nginx
```