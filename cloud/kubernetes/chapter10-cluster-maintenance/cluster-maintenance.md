# 第10章：集群维护和升级

## 本章概要
本章将详细介绍 Kubernetes 集群的维护和升级操作。我们将学习如何进行节点维护、集群备份与恢复、版本升级等关键操作，以及如何确保在维护过程中业务的连续性和数据的安全性。

## 目标
- 掌握 Kubernetes 集群的日常维护操作
- 学会安全地进行集群版本升级
- 了解节点维护和替换流程
- 掌握集群备份与恢复技术
- 学会处理升级过程中的常见问题

## 10.1 集群维护概述

### 10.1.1 维护类型
Kubernetes 集群维护主要包括以下几种类型：
1. **预防性维护**：定期检查、清理和优化集群
2. **纠正性维护**：修复集群中的问题和故障
3. **适应性维护**：根据业务需求调整集群配置
4. **完善性维护**：升级集群版本和功能

### 10.1.2 维护窗口
为了减少对业务的影响，建议在维护窗口期进行集群维护操作：
- 选择业务低峰期
- 提前通知相关团队
- 准备回滚方案
- 确保有足够的资源冗余

## 10.2 节点维护

### 10.2.1 节点安全停机
在对节点进行维护之前，需要安全地将节点上的 Pod 迁移到其他节点。

#### 驱逐节点上的 Pod
```bash
# 标记节点为不可调度
kubectl cordon <node-name>

# 驱逐节点上的 Pod
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# 等待所有 Pod 被重新调度到其他节点
```

#### 节点维护完成后恢复
```bash
# 标记节点为可调度
kubectl uncordon <node-name>
```

### 10.2.2 节点替换
当需要替换故障节点或升级硬件时，可以按以下步骤操作：

1. 安全停机节点（如上所述）
2. 从集群中删除节点
```bash
kubectl delete node <node-name>
```
3. 在新节点上安装 Kubernetes 组件
4. 将新节点加入集群
```bash
# 在新节点上执行 kubeadm join 命令
kubeadm join <control-plane-host>:<port> --token <token> --discovery-token-ca-cert-hash sha256:<hash>
```

### 10.2.3 节点监控和健康检查
```bash
# 查看节点状态
kubectl get nodes

# 查看节点详细信息
kubectl describe node <node-name>

# 查看节点资源使用情况
kubectl top nodes

# 检查节点上的 Pod
kubectl get pods -o wide --field-selector spec.nodeName=<node-name>
```

## 10.3 集群备份与恢复

### 10.3.1 etcd 备份
etcd 是 Kubernetes 的核心数据存储，必须定期备份。

#### 手动备份 etcd
```bash
# 获取 etcd Pod 名称
ETCD_POD=$(kubectl get pods -n kube-system | grep etcd | awk '{print $1}')

# 执行 etcd 备份
kubectl exec -n kube-system $ETCD_POD -- \
  etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  snapshot save /tmp/etcd-snapshot.db

# 将备份文件复制到本地
kubectl cp kube-system/$ETCD_POD:/tmp/etcd-snapshot.db ./etcd-snapshot-$(date +%Y%m%d).db
```

#### 自动备份 etcd
可以使用 CronJob 定期自动备份 etcd：

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: etcd-backup
  namespace: kube-system
spec:
  schedule: "0 2 * * *"  # 每天凌晨2点执行
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: etcd-backup
            image: bitnami/etcd:3.5.0
            command:
            - /bin/sh
            - -c
            - |
              etcdctl --endpoints=https://etcd:2379 \
              --cacert=/etc/kubernetes/pki/etcd/ca.crt \
              --cert=/etc/kubernetes/pki/etcd/server.crt \
              --key=/etc/kubernetes/pki/etcd/server.key \
              snapshot save /backup/etcd-snapshot-$(date +%Y%m%d).db
            volumeMounts:
            - name: etcd-certs
              mountPath: /etc/kubernetes/pki/etcd
              readOnly: true
            - name: backup
              mountPath: /backup
          volumes:
          - name: etcd-certs
            hostPath:
              path: /etc/kubernetes/pki/etcd
          - name: backup
            hostPath:
              path: /var/backups/etcd
          restartPolicy: OnFailure
```

### 10.3.2 资源配置备份
除了 etcd 备份，还应该定期备份重要的资源配置：

```bash
# 备份所有命名空间的资源
kubectl get all --all-namespaces -o yaml > cluster-resources-$(date +%Y%m%d).yaml

# 备份特定命名空间的资源
kubectl get all -n <namespace> -o yaml > namespace-resources-$(date +%Y%m%d).yaml

# 备份特定类型的资源
kubectl get deployments,configmaps,secrets -n <namespace> -o yaml > important-resources-$(date +%Y%m%d).yaml
```

### 10.3.3 etcd 恢复
当需要从备份恢复 etcd 时，可以按以下步骤操作：

1. 停止所有 Kubernetes 组件
```bash
systemctl stop kubelet
```

2. 移动现有的 etcd 数据目录
```bash
mv /var/lib/etcd /var/lib/etcd.backup
```

3. 从备份恢复数据
```bash
# 在 master 节点上执行
etcdctl snapshot restore /path/to/etcd-snapshot.db \
  --data-dir=/var/lib/etcd \
  --name=$(hostname) \
  --initial-cluster=$(hostname)=https://<node-ip>:2380 \
  --initial-cluster-token=etcd-cluster-1 \
  --initial-advertise-peer-urls=https://<node-ip>:2380
```

4. 重启 etcd 和 Kubernetes 组件
```bash
systemctl start etcd
systemctl start kubelet
```

## 10.4 集群版本升级

### 10.4.1 升级前准备
在进行集群升级之前，必须做好充分的准备工作：

1. **检查版本兼容性**
```bash
# 检查当前版本
kubectl version

# 查看支持的升级路径
# 参考 Kubernetes 官方文档的版本偏差策略
```

2. **备份集群**
```bash
# 执行 etcd 备份和资源配置备份
```

3. **检查集群状态**
```bash
# 检查集群组件状态
kubectl get componentstatuses

# 检查节点状态
kubectl get nodes

# 检查关键应用状态
kubectl get pods -A
```

4. **阅读发布说明**
仔细阅读新版本的发布说明，了解重要的变更和已知问题。

### 10.4.2 控制平面升级
控制平面升级需要按顺序进行：

1. **升级第一个控制平面节点**
```bash
# 升级 kubeadm
apt-mark unhold kubeadm && \
apt-get update && apt-get install -y kubeadm=<version> && \
apt-mark hold kubeadm

# 验证升级版本
kubeadm version

# 升级控制平面组件
kubeadm upgrade plan
kubeadm upgrade apply v<version>

# 升级 kubelet 和 kubectl
apt-mark unhold kubelet kubectl && \
apt-get update && apt-get install -y kubelet=<version> kubectl=<version> && \
apt-mark hold kubelet kubectl

# 重启 kubelet
systemctl daemon-reload
systemctl restart kubelet
```

2. **升级其他控制平面节点**
在其他控制平面节点上执行：
```bash
# 升级 kubeadm
apt-mark unhold kubeadm && \
apt-get update && apt-get install -y kubeadm=<version> && \
apt-mark hold kubeadm

# 升级控制平面组件
kubeadm upgrade node

# 升级 kubelet 和 kubectl
apt-mark unhold kubelet kubectl && \
apt-get update && apt-get install -y kubelet=<version> kubectl=<version> && \
apt-mark hold kubelet kubectl

# 重启 kubelet
systemctl daemon-reload
systemctl restart kubelet
```

### 10.4.3 工作节点升级
工作节点升级需要逐个进行以确保业务连续性：

```bash
# 1. 驱逐节点上的 Pod
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# 2. 升级 kubeadm
apt-mark unhold kubeadm && \
apt-get update && apt-get install -y kubeadm=<version> && \
apt-mark hold kubeadm

# 3. 升级 kubelet 配置
kubeadm upgrade node

# 4. 升级 kubelet 和 kubectl
apt-mark unhold kubelet kubectl && \
apt-get update && apt-get install -y kubelet=<version> kubectl=<version> && \
apt-mark hold kubelet kubectl

# 5. 重启 kubelet
systemctl daemon-reload
systemctl restart kubelet

# 6. 恢复节点调度
kubectl uncordon <node-name>
```

### 10.4.4 升级验证
升级完成后，需要验证集群是否正常工作：

```bash
# 检查节点版本
kubectl get nodes

# 检查系统组件状态
kubectl get componentstatuses

# 检查关键应用状态
kubectl get pods -A

# 测试基本功能
kubectl run test-pod --image=nginx --restart=Never
kubectl get pod test-pod
kubectl delete pod test-pod
```

## 10.5 使用 kubeadm 进行集群管理

### 10.5.1 kubeadm 升级管理
kubeadm 提供了完整的升级管理功能：

```bash
# 查看升级计划
kubeadm upgrade plan

# 应用升级
kubeadm upgrade apply v<version>

# 升级单个节点
kubeadm upgrade node

# 查看可用版本
kubeadm version -o short
```

### 10.5.2 kubeadm 证书管理
```bash
# 检查证书过期时间
kubeadm certs check-expiration

# 续订证书
kubeadm certs renew all

# 手动生成证书
kubeadm certs generate-csr
```

## 10.6 实验：安全升级 Kubernetes 集群

### 实验目标
在一个测试集群上安全地执行版本升级操作，包括控制平面和工作节点的升级。

### 实验环境准备
1. 准备一个至少包含一个控制平面节点和两个工作节点的 Kubernetes 集群
2. 确保集群当前版本比目标版本低一个小版本号

### 实验步骤

1. **升级前检查**
```bash
# 检查当前版本
kubectl version --short

# 检查节点状态
kubectl get nodes

# 备份 etcd
ETCD_POD=$(kubectl get pods -n kube-system | grep etcd | awk '{print $1}')
kubectl exec -n kube-system $ETCD_POD -- \
  etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  snapshot save /tmp/etcd-snapshot-pre-upgrade.db
```

2. **升级控制平面**
```bash
# 在第一个控制平面节点上执行
# 升级 kubeadm
apt-mark unhold kubeadm && \
apt-get update && apt-get install -y kubeadm=<target-version> && \
apt-mark hold kubeadm

# 查看升级计划
kubeadm upgrade plan

# 执行升级
kubeadm upgrade apply v<target-version>

# 升级 kubelet 和 kubectl
apt-mark unhold kubelet kubectl && \
apt-get update && apt-get install -y kubelet=<target-version> kubectl=<target-version> && \
apt-mark hold kubelet kubectl

# 重启 kubelet
systemctl daemon-reload
systemctl restart kubelet
```

3. **升级其他控制平面节点**
```bash
# 在其他控制平面节点上执行
# 升级 kubeadm
apt-mark unhold kubeadm && \
apt-get update && apt-get install -y kubeadm=<target-version> && \
apt-mark hold kubeadm

# 升级节点
kubeadm upgrade node

# 升级 kubelet 和 kubectl
apt-mark unhold kubelet kubectl && \
apt-get update && apt-get install -y kubelet=<target-version> kubectl=<target-version> && \
apt-mark hold kubelet kubectl

# 重启 kubelet
systemctl daemon-reload
systemctl restart kubelet
```

4. **升级工作节点**
```bash
# 在每个工作节点上逐个执行
# 驱逐节点上的 Pod
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# 升级 kubeadm
apt-mark unhold kubeadm && \
apt-get update && apt-get install -y kubeadm=<target-version> && \
apt-mark hold kubeadm

# 升级节点配置
kubeadm upgrade node

# 升级 kubelet 和 kubectl
apt-mark unhold kubelet kubectl && \
apt-get update && apt-get install -y kubelet=<target-version> kubectl=<target-version> && \
apt-mark hold kubelet kubectl

# 重启 kubelet
systemctl daemon-reload
systemctl restart kubelet

# 恢复节点调度
kubectl uncordon <node-name>
```

5. **验证升级结果**
```bash
# 检查节点版本
kubectl get nodes

# 检查系统组件状态
kubectl get componentstatuses

# 部署测试应用验证功能
kubectl create deployment nginx --image=nginx
kubectl expose deployment nginx --port=80 --type=NodePort
kubectl get svc nginx

# 清理测试资源
kubectl delete deployment nginx
kubectl delete svc nginx
```

## 10.7 故障排除

### 10.7.1 升级失败处理
如果升级过程中出现故障，可以按以下步骤处理：

1. **检查升级状态**
```bash
# 查看升级状态
kubeadm upgrade node --dry-run

# 检查组件状态
kubectl get componentstatuses
```

2. **回滚操作**
```bash
# 如果是控制平面升级失败，可能需要手动恢复
# 从备份恢复 etcd
# 重新安装旧版本的组件
```

3. **节点无法加入集群**
```bash
# 检查节点状态
kubectl get nodes

# 重新生成加入令牌
kubeadm token create --print-join-command

# 在节点上重新执行加入命令
```

### 10.7.2 节点维护问题
1. **Pod 无法驱逐**
```bash
# 强制删除 Pod
kubectl delete pod <pod-name> --force --grace-period=0

# 检查是否有 PDB 阻止驱逐
kubectl get pdb -A
```

2. **节点状态异常**
```bash
# 检查节点详细信息
kubectl describe node <node-name>

# 检查节点上的事件
kubectl get events --field-selector involvedObject.name=<node-name>
```

### 10.7.3 备份恢复问题
1. **etcd 备份失败**
```bash
# 检查 etcd 状态
kubectl exec -n kube-system <etcd-pod> -- etcdctl endpoint health

# 检查证书权限
ls -la /etc/kubernetes/pki/etcd/
```

2. **恢复后集群异常**
```bash
# 检查集群组件状态
kubectl get componentstatuses

# 检查节点状态
kubectl get nodes

# 检查关键应用状态
kubectl get pods -A
```

## 10.8 最佳实践

### 10.8.1 维护最佳实践
1. **制定维护计划**：定期执行维护操作，避免临时性维护
2. **灰度发布**：先在测试环境验证，再推广到生产环境
3. **监控告警**：建立完善的监控告警体系，及时发现异常
4. **文档记录**：详细记录每次维护操作的过程和结果

### 10.8.2 升级最佳实践
1. **逐步升级**：按照小版本逐步升级，避免跨多个版本升级
2. **备份先行**：升级前必须完成完整的备份
3. **测试验证**：在测试环境中充分验证后再升级生产环境
4. **回滚准备**：准备完整的回滚方案和操作步骤

### 10.8.3 备份最佳实践
1. **定期备份**：建立自动化的定期备份机制
2. **多地存储**：将备份数据存储在不同地理位置
3. **验证恢复**：定期验证备份数据的完整性和可恢复性
4. **加密保护**：对敏感备份数据进行加密保护

## 总结
本章我们深入学习了 Kubernetes 集群的维护和升级技术。我们掌握了节点维护、集群备份与恢复、版本升级等关键操作，通过实验演练了安全升级集群的完整流程。这些技能对于保障 Kubernetes 集群的稳定运行和持续发展至关重要。在实际工作中，我们应该遵循最佳实践，制定完善的维护计划，确保在维护过程中业务的连续性和数据的安全性。