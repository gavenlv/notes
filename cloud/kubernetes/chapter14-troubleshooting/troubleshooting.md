# 第14章：故障排查和性能优化

## 本章概要
本章将深入探讨 Kubernetes 环境中的故障排查方法和性能优化技巧。我们将从系统性的故障排查方法论开始，逐步介绍各个组件的常见问题诊断方法，包括节点、Pod、网络、存储等层面的问题。同时，我们还将学习如何使用各种工具和技术来分析和优化 Kubernetes 集群的性能，确保应用的稳定运行和高效资源利用。

## 目标
- 掌握 Kubernetes 故障排查的系统性方法
- 学会诊断和解决节点、Pod、网络、存储等常见问题
- 理解性能瓶颈分析和优化方法
- 掌握关键监控指标和调优技巧
- 学会使用专业工具进行深度分析

## 14.1 故障排查方法论

### 14.1.1 系统性排查方法
在 Kubernetes 环境中进行故障排查时，应遵循系统性的方法：

#### 1. 观察和描述问题
- 准确描述问题现象
- 记录问题发生的时间和环境
- 收集相关的错误信息和日志

#### 2. 分层排查
按照 OSI 网络模型和 Kubernetes 架构进行分层排查：
1. **基础设施层**：硬件、网络、存储
2. **Kubernetes 组件层**：API Server、etcd、调度器、控制器管理器
3. **网络层**：CNI 插件、网络策略、服务发现
4. **应用层**：Pod、Deployment、Service 等资源

#### 3. 信息收集
```bash
# 收集集群基本信息
kubectl cluster-info
kubectl get nodes
kubectl get pods --all-namespaces

# 收集事件信息
kubectl get events --all-namespaces --sort-by='.lastTimestamp'

# 收集组件状态
kubectl get componentstatuses
```

#### 4. 假设和验证
- 基于收集的信息提出假设
- 设计实验验证假设
- 根据验证结果调整排查方向

### 14.1.2 常用排查命令
掌握常用的 kubectl 命令对故障排查至关重要：

#### 基础信息查看
```bash
# 查看资源状态
kubectl get nodes
kubectl get pods
kubectl get services
kubectl get deployments

# 查看资源详细信息
kubectl describe node <node-name>
kubectl describe pod <pod-name>
kubectl describe service <service-name>

# 查看资源配置
kubectl get pod <pod-name> -o yaml
```

#### 日志查看
```bash
# 查看 Pod 日志
kubectl logs <pod-name>
kubectl logs <pod-name> -c <container-name>
kubectl logs <pod-name> --previous  # 查看前一个容器实例的日志

# 实时查看日志
kubectl logs -f <pod-name>
```

#### 进入容器调试
```bash
# 进入容器执行命令
kubectl exec -it <pod-name> -- /bin/bash
kubectl exec -it <pod-name> -c <container-name> -- /bin/sh
```

## 14.2 节点问题排查

### 14.2.1 节点状态异常
节点可能出现 NotReady、内存压力、磁盘压力等状态。

#### 检查节点状态
```bash
# 查看节点状态
kubectl get nodes

# 查看节点详细信息
kubectl describe node <node-name>

# 检查节点条件
kubectl get nodes -o jsonpath='{.items[*].status.conditions[*].type}{"\t"}{.items[*].status.conditions[*].status}{"\n"}'
```

#### 常见节点问题及解决方案

1. **节点 NotReady**
```bash
# 检查 kubelet 状态
systemctl status kubelet

# 重启 kubelet
systemctl restart kubelet

# 检查节点日志
journalctl -u kubelet -f
```

2. **内存压力**
```bash
# 检查节点资源使用
kubectl top nodes

# 检查节点资源详情
kubectl describe node <node-name>

# 清理无用镜像
docker image prune -a

# 驱逐低优先级 Pod
kubectl drain <node-name> --ignore-daemonsets --delete-local-data
```

3. **磁盘压力**
```bash
# 检查磁盘使用情况
df -h

# 清理容器日志
find /var/log/pods -name "*.log" -type f -mtime +7 -delete

# 清理已停止的容器
docker container prune -f

# 清理未使用的卷
docker volume prune -f
```

### 14.2.2 kubelet 问题
kubelet 是节点上的关键组件，负责管理 Pod 和容器。

#### 检查 kubelet 配置
```bash
# 查看 kubelet 配置
cat /var/lib/kubelet/config.yaml

# 查看 kubelet 启动参数
ps -ef | grep kubelet
```

#### 常见 kubelet 问题

1. **证书问题**
```bash
# 检查证书有效期
openssl x509 -in /var/lib/kubelet/pki/kubelet.crt -text -noout

# 重新生成证书
kubeadm init phase kubelet-start
```

2. **CNI 插件问题**
```bash
# 检查 CNI 配置
ls /etc/cni/net.d/

# 重启 CNI 插件
systemctl restart <cni-plugin-service>
```

## 14.3 Pod 问题排查

### 14.3.1 Pod 状态异常
Pod 可能处于 Pending、CrashLoopBackOff、ImagePullBackOff、OOMKilled 等状态。

#### 检查 Pod 状态
```bash
# 查看 Pod 状态
kubectl get pods

# 查看 Pod 详细信息
kubectl describe pod <pod-name>

# 查看 Pod 事件
kubectl get events --field-selector involvedObject.name=<pod-name>
```

#### 常见 Pod 问题及解决方案

1. **Pending 状态**
```bash
# 检查资源请求是否超过节点容量
kubectl describe pod <pod-name>

# 检查节点资源使用
kubectl top nodes

# 检查污点和容忍
kubectl describe nodes | grep Taints
```

2. **CrashLoopBackOff 状态**
```bash
# 查看容器日志
kubectl logs <pod-name> --previous

# 检查启动命令
kubectl get pod <pod-name> -o yaml | grep -A 10 command

# 进入容器调试
kubectl exec -it <pod-name> -- /bin/sh
```

3. **ImagePullBackOff 状态**
```bash
# 检查镜像名称和标签
kubectl get pod <pod-name> -o yaml | grep image

# 手动拉取镜像测试
docker pull <image-name>:<tag>

# 检查镜像仓库认证
kubectl get secret <image-pull-secret> -o yaml
```

4. **OOMKilled 状态**
```bash
# 检查资源限制
kubectl get pod <pod-name> -o yaml | grep -A 5 resources

# 调整资源限制
kubectl set resources deployment <deployment-name> --limits=memory=512Mi
```

### 14.3.2 容器运行时问题
容器运行时（如 Docker、containerd）可能出现问题影响 Pod 运行。

#### 检查容器运行时状态
```bash
# 检查 Docker 状态
systemctl status docker

# 查看容器运行时日志
journalctl -u docker -f

# 列出容器
docker ps -a
```

#### 常见容器运行时问题

1. **容器无法启动**
```bash
# 检查容器日志
docker logs <container-id>

# 检查容器配置
docker inspect <container-id>
```

2. **镜像问题**
```bash
# 列出镜像
docker images

# 删除损坏镜像
docker rmi <image-id>

# 清理未使用镜像
docker image prune -a
```

## 14.4 网络问题排查

### 14.4.1 网络连通性问题
网络问题是 Kubernetes 中最常见的问题之一。

#### 检查网络连通性
```bash
# 测试 Pod 间连通性
kubectl exec -it <pod-name> -- ping <target-ip>

# 测试服务访问
kubectl exec -it <pod-name> -- curl <service-ip>:<port>

# 检查 DNS 解析
kubectl exec -it <pod-name> -- nslookup <service-name>
```

#### 常见网络问题及解决方案

1. **Pod 无法访问外部网络**
```bash
# 检查节点网络配置
ip route show

# 检查 iptables 规则
iptables -L -n -v

# 检查 CNI 插件状态
systemctl status <cni-plugin>
```

2. **Service 无法访问**
```bash
# 检查 Service 配置
kubectl get service <service-name> -o yaml

# 检查 Endpoint
kubectl get endpoints <service-name>

# 检查 kube-proxy 状态
kubectl get daemonset -n kube-system kube-proxy
```

3. **DNS 解析失败**
```bash
# 检查 CoreDNS 部署
kubectl get deployment -n kube-system coredns

# 检查 CoreDNS 配置
kubectl get configmap -n kube-system coredns -o yaml

# 测试 DNS 解析
kubectl exec -it <pod-name> -- nslookup kubernetes.default
```

### 14.4.2 网络策略问题
网络策略可能阻止合法的网络流量。

#### 检查网络策略
```bash
# 查看网络策略
kubectl get networkpolicies --all-namespaces

# 查看特定网络策略
kubectl describe networkpolicy <policy-name> -n <namespace>
```

#### 常见网络策略问题

1. **策略过于严格**
```bash
# 临时放宽策略进行测试
kubectl delete networkpolicy <policy-name> -n <namespace>

# 逐步添加规则验证
kubectl apply -f <relaxed-policy>.yaml
```

2. **策略冲突**
```bash
# 检查所有相关策略
kubectl get networkpolicies -n <namespace> -o yaml

# 分析策略规则
kubectl describe networkpolicy <policy-name> -n <namespace>
```

## 14.5 存储问题排查

### 14.5.1 持久化卷问题
持久化卷（PV）和持久化卷声明（PVC）可能出现绑定失败、挂载失败等问题。

#### 检查存储资源
```bash
# 查看 PV 状态
kubectl get pv

# 查看 PVC 状态
kubectl get pvc

# 查看 PVC 详细信息
kubectl describe pvc <pvc-name>
```

#### 常见存储问题及解决方案

1. **PVC 无法绑定**
```bash
# 检查 StorageClass
kubectl get storageclass

# 检查 PV 和 PVC 匹配条件
kubectl get pv <pv-name> -o yaml
kubectl get pvc <pvc-name> -o yaml

# 手动绑定 PV 和 PVC
kubectl patch pv <pv-name> -p '{"spec":{"claimRef":{"namespace":"<namespace>","name":"<pvc-name>"}}}'
```

2. **卷挂载失败**
```bash
# 检查 Pod 挂载信息
kubectl describe pod <pod-name>

# 检查节点挂载点
ls -la /var/lib/kubelet/pods/<pod-uid>/volumes/

# 检查存储插件日志
kubectl logs -n kube-system <storage-plugin-pod>
```

### 14.5.2 存储性能问题
存储性能可能影响应用性能。

#### 监控存储性能
```bash
# 检查卷使用情况
kubectl exec -it <pod-name> -- df -h

# 监控 I/O 性能
kubectl exec -it <pod-name> -- iostat -x 1

# 检查存储类性能
kubectl get storageclass <storageclass-name> -o yaml
```

#### 存储性能优化

1. **选择合适的存储类型**
```yaml
# 使用高性能存储类
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: fast-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: fast-ssd  # 高性能 SSD 存储类
```

2. **优化存储配置**
```yaml
# 配置存储性能参数
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: optimized-storage
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
```

## 14.6 性能优化

### 14.6.1 资源优化
合理配置资源请求和限制对性能至关重要。

#### 资源监控
```bash
# 监控 Pod 资源使用
kubectl top pods

# 监控节点资源使用
kubectl top nodes

# 查看历史资源使用
kubectl get hpa  # 水平 Pod 自动伸缩器状态
```

#### 资源调优

1. **设置合理的资源请求和限制**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: optimized-app
spec:
  template:
    spec:
      containers:
      - name: app
        image: app:latest
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

2. **配置水平自动伸缩**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app-deployment
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### 14.6.2 调度优化
优化调度策略可以提高集群资源利用率和应用性能。

#### 调度器调优
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scheduled-app
spec:
  template:
    spec:
      # 节点选择器
      nodeSelector:
        disktype: ssd
        
      # 亲和性配置
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - scheduled-app
              topologyKey: kubernetes.io/hostname
              
      # 污点容忍
      tolerations:
      - key: "dedicated"
        operator: "Equal"
        value: "app"
        effect: "NoSchedule"
```

### 14.6.3 网络优化
网络性能对应用响应时间有重要影响。

#### 网络插件优化
```bash
# 检查网络插件性能
kubectl get pods -n kube-system -l k8s-app=calico-node

# 监控网络延迟
kubectl exec -it <pod-name> -- ping <target-pod-ip>
```

#### 服务优化
```yaml
apiVersion: v1
kind: Service
metadata:
  name: optimized-service
spec:
  type: ClusterIP
  selector:
    app: app
  ports:
  - port: 80
    targetPort: 8080
  # 启用会话亲和性（根据需要）
  sessionAffinity: ClientIP
```

## 14.7 专业工具使用

### 14.7.1 命令行工具
掌握专业命令行工具可以提高故障排查效率。

#### stern - 多 Pod 日志查看
```bash
# 安装 stern
wget https://github.com/wercker/stern/releases/download/1.22.0/stern_linux_amd64
chmod +x stern_linux_amd64
sudo mv stern_linux_amd64 /usr/local/bin/stern

# 使用 stern 查看日志
stern <pod-name-pattern>
stern -n <namespace> <app-name>
```

#### kubectl 插件
```bash
# 安装 kubectl 插件
kubectl krew install resource-capacity
kubectl krew install view-utilization

# 使用插件查看资源容量
kubectl resource-capacity
kubectl view-utilization
```

### 14.7.2 可视化工具
可视化工具可以更直观地分析集群状态。

#### Kubernetes Dashboard
```bash
# 部署 Kubernetes Dashboard
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml

# 创建管理员用户
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ServiceAccount
metadata:
  name: admin-user
  namespace: kubernetes-dashboard

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-user
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: admin-user
  namespace: kubernetes-dashboard
EOF

# 获取访问令牌
kubectl -n kubernetes-dashboard get secret $(kubectl -n kubernetes-dashboard get sa/admin-user -o jsonpath="{.secrets[0].name}") -o go-template="{{.data.token | base64decode}}"
```

#### Weave Scope
```bash
# 部署 Weave Scope
kubectl apply -f "https://cloud.weave.works/k8s/scope.yaml?k8s-version=$(kubectl version | base64 | tr -d '\n')"

# 访问 Weave Scope
kubectl port-forward -n weave svc/weave-scope-app 4040:80
```

### 14.7.3 监控和分析工具

#### kube-state-metrics
```bash
# 部署 kube-state-metrics
kubectl apply -f https://github.com/kubernetes/kube-state-metrics/releases/download/v2.8.0/kube-state-metrics.yaml

# 查询指标
kubectl port-forward -n kube-system svc/kube-state-metrics 8080:8080
curl http://localhost:8080/metrics
```

#### node-problem-detector
```bash
# 部署 node-problem-detector
kubectl apply -f https://github.com/kubernetes/node-problem-detector/releases/download/v0.8.13/node-problem-detector.yaml

# 查看节点问题
kubectl get events --field-selector involvedObject.kind=Node
```

## 14.8 实验：故障排查和性能优化实践

### 实验目标
通过实际操作掌握 Kubernetes 故障排查和性能优化的方法，包括诊断常见问题、使用专业工具、优化资源配置等。

### 实验环境准备
1. Kubernetes 集群（推荐使用 Kind 或 Minikube）
2. kubectl 命令行工具
3. stern、krew 等辅助工具

### 实验步骤

1. **创建故障场景**
```bash
# 创建一个有问题的 Deployment
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: problematic-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: problematic-app
  template:
    metadata:
      labels:
        app: problematic-app
    spec:
      containers:
      - name: app
        image: nginx:latest
        resources:
          requests:
            memory: "1Gi"  # 故意设置过高的内存请求
            cpu: "1"
          limits:
            memory: "2Gi"
            cpu: "2"
        # 故意配置错误的启动命令
        command: ["/bin/sh"]
        args: ["-c", "echo 'Starting app...'; sleep 3600"]
EOF
```

2. **诊断 Pod 问题**
```bash
# 查看 Pod 状态
kubectl get pods

# 查看详细信息
kubectl describe pod -l app=problematic-app

# 查看日志
kubectl logs -l app=problematic-app

# 使用 stern 查看实时日志
stern problematic-app
```

3. **解决资源问题**
```bash
# 调整资源请求
kubectl patch deployment problematic-app -p '{"spec":{"template":{"spec":{"containers":[{"name":"app","resources":{"requests":{"memory":"64Mi","cpu":"100m"},"limits":{"memory":"128Mi","cpu":"200m"}}}]}}}}'

# 验证修复结果
kubectl get pods
```

4. **优化应用性能**
```bash
# 配置水平自动伸缩
cat <<EOF | kubectl apply -f -
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: problematic-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: problematic-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
EOF

# 监控自动伸缩
kubectl get hpa
kubectl get pods -w
```

5. **网络问题排查**
```bash
# 创建网络策略测试问题
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: restrictive-policy
spec:
  podSelector:
    matchLabels:
      app: problematic-app
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: non-existent-app  # 故意设置不存在的标签
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: non-existent-namespace  # 故意设置不存在的命名空间
EOF

# 测试网络连通性
kubectl run debug-pod --image=busybox --rm -it -- sh
# 在调试 Pod 中执行
# wget -qO- <service-ip>:<port>  # 应该失败

# 修复网络策略
kubectl delete networkpolicy restrictive-policy

# 重新测试网络连通性
# wget -qO- <service-ip>:<port>  # 应该成功
```

6. **使用专业工具分析**
```bash
# 安装 krew 插件
kubectl krew install resource-capacity
kubectl krew install view-utilization

# 分析资源使用情况
kubectl resource-capacity
kubectl view-utilization

# 安装并使用 stern
wget https://github.com/wercker/stern/releases/download/1.22.0/stern_linux_amd64
chmod +x stern_linux_amd64
sudo mv stern_linux_amd64 /usr/local/bin/stern

# 实时查看多个 Pod 日志
stern problematic-app
```

7. **性能监控**
```bash
# 监控资源使用
kubectl top nodes
kubectl top pods

# 创建资源使用压力测试
cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: stress-test
spec:
  template:
    spec:
      containers:
      - name: stress
        image: progrium/stress
        args:
        - --cpu
        - "2"
        - --timeout
        - "60s"
      restartPolicy: Never
  backoffLimit: 4
EOF

# 监控压力测试期间的资源使用
kubectl top nodes -w
```

## 14.9 故障排查最佳实践

### 14.9.1 建立监控告警体系
```yaml
# 配置关键指标告警
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: cluster-alerts
spec:
  groups:
  - name: cluster-alerts
    rules:
    - alert: NodeDown
      expr: up{job="node-exporter"} == 0
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "Node is down"
        description: "Node {{ $labels.instance }} has been down for more than 5 minutes"
        
    - alert: PodCrashLooping
      expr: rate(kube_pod_container_status_restarts_total[5m]) > 0.1
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "Pod is crash looping"
        description: "Pod {{ $labels.pod }} in namespace {{ $labels.namespace }} is crash looping"
```

### 14.9.2 建立应急响应流程
1. **问题发现**：通过监控告警或用户反馈发现问题
2. **问题评估**：评估问题影响范围和严重程度
3. **问题定位**：使用系统性方法定位问题根源
4. **问题解决**：实施解决方案并验证效果
5. **问题复盘**：分析问题原因，制定预防措施

### 14.9.3 文档和知识管理
1. **故障处理手册**：记录常见问题的处理方法
2. **变更记录**：记录系统变更和影响
3. **经验总结**：定期总结故障处理经验

## 14.10 性能优化最佳实践

### 14.10.1 资源规划和管理
1. **合理的资源请求和限制**：基于应用实际需求设置
2. **资源配额管理**：防止资源滥用
3. **自动伸缩配置**：根据负载动态调整资源

### 14.10.2 应用优化
1. **应用架构优化**：微服务拆分、缓存使用等
2. **容器镜像优化**：使用小基础镜像、多阶段构建
3. **启动时间优化**：减少应用启动时间

### 14.10.3 集群优化
1. **调度优化**：合理使用亲和性、污点容忍等特性
2. **网络优化**：选择合适的 CNI 插件和配置
3. **存储优化**：选择合适的存储类型和配置

## 总结
本章我们深入学习了 Kubernetes 环境中的故障排查方法和性能优化技巧。通过系统性的排查方法论，我们掌握了诊断节点、Pod、网络、存储等常见问题的技能。同时，我们学习了如何使用专业工具进行深度分析，以及性能优化的最佳实践。这些知识和技能对于确保 Kubernetes 集群稳定运行和应用高性能至关重要。在实际工作中，我们需要持续积累经验，建立完善的监控告警体系和应急响应流程，以快速发现和解决各种问题。

至此，我们已经完成了 Kubernetes 学习指南的所有章节内容，从基础概念到高级特性，从日常运维到故障排查，全面覆盖了 Kubernetes 的核心知识点和实践技能。希望这份指南能够帮助读者深入理解和掌握 Kubernetes，为在生产环境中成功应用 Kubernetes 打下坚实基础。