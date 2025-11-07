#!/bin/bash

# kubectl 命令别名配置
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgd='kubectl get deployments'
alias kgs='kubectl get services'
alias kgn='kubectl get nodes'
alias kctx='kubectl config current-context'
alias kns='kubectl config set-context --current --namespace'

# 常用的 kubectl 命令组合
alias kdp='kubectl describe pod'
alias kdd='kubectl describe deployment'
alias kds='kubectl describe service'
alias kdn='kubectl describe node'

# 快速创建资源
alias kaf='kubectl apply -f'
alias kcf='kubectl create -f'

# 快速删除资源
alias kdf='kubectl delete -f'

# 日志查看
alias kl='kubectl logs'
alias klf='kubectl logs -f'

# 进入容器
alias ke='kubectl exec -it'

echo "kubectl aliases loaded successfully!"