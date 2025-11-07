# 第6章 存储管理

## 6.1 Kubernetes存储概述

### 6.1.1 存储挑战

在容器化环境中，存储面临以下几个挑战：
1. **数据持久性**：容器重启后数据丢失
2. **数据共享**：多个Pod间共享数据
3. **动态供应**：根据需求动态创建存储
4. **存储隔离**：不同应用的数据隔离

### 6.1.2 Kubernetes存储架构

Kubernetes采用抽象的存储架构，主要包括以下组件：
- **Volume**：Pod级别的存储卷
- **PersistentVolume (PV)**：集群级别的存储资源
- **PersistentVolumeClaim (PVC)**：存储资源申请
- **StorageClass**：存储类别定义，用于动态供应

## 6.2 Volume详解

Volume是定义在Pod上的存储卷，生命周期与Pod相同。

### 6.2.1 常见Volume类型

#### emptyDir

临时存储卷，Pod删除时数据也会丢失：

```yaml
# emptydir-volume.yaml
apiVersion: v1
kind: Pod
metadata:
  name: test-pd
spec:
  containers:
  - image: nginx:1.21
    name: test-container
    volumeMounts:
    - mountPath: /cache
      name: cache-volume
  volumes:
  - name: cache-volume
    emptyDir: {}
```

#### hostPath

挂载宿主机文件系统到Pod中：

```yaml
# hostpath-volume.yaml
apiVersion: v1
kind: Pod
metadata:
  name: test-pd
spec:
  containers:
  - image: nginx:1.21
    name: test-container
    volumeMounts:
    - mountPath: /test-pd
      name: test-volume
  volumes:
  - name: test-volume
    hostPath:
      # 宿主机上的目录位置
      path: /data
      # 类型检查
      type: Directory
```

#### configMap和secret

将配置数据作为文件挂载到Pod中：

```yaml
# configmap-volume.yaml
apiVersion: v1
kind: Pod
metadata:
  name: configmap-pod
spec:
  containers:
    - name: test-container
      image: nginx:1.21
      volumeMounts:
        - name: config-volume
          mountPath: /etc/config
  volumes:
    - name: config-volume
      configMap:
        # 引用现有的configmap名称
        name: special-config
```

### 6.2.2 Volume操作示例

```bash
# 创建使用emptyDir的Pod
kubectl apply -f emptydir-volume.yaml

# 查看Pod状态
kubectl get pods

# 进入Pod验证存储
kubectl exec -it test-pd -- sh
# 在容器内执行
echo "Hello Storage" > /cache/test.txt
cat /cache/test.txt

# 删除Pod后重新创建，数据会丢失
kubectl delete pod test-pd
kubectl apply -f emptydir-volume.yaml
kubectl exec -it test-pd -- cat /cache/test.txt  # 文件不存在
```

## 6.3 PersistentVolume (PV) 和 PersistentVolumeClaim (PVC)

PV和PVC实现了存储的解耦，提供了更灵活的存储管理方式。

### 6.3.1 PersistentVolume (PV)

PV是集群中预配的存储资源，由管理员创建和维护。

```yaml
# pv-example.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: task-pv-volume
  labels:
    type: local
spec:
  storageClassName: manual
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: "/mnt/data"
```

### 6.3.2 PersistentVolumeClaim (PVC)

PVC是用户对存储资源的申请：

```yaml
# pvc-example.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: task-pv-claim
spec:
  storageClassName: manual
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 3Gi
```

### 6.3.3 在Pod中使用PVC

```yaml
# pod-with-pvc.yaml
apiVersion: v1
kind: Pod
metadata:
  name: task-pv-pod
spec:
  volumes:
    - name: task-pv-storage
      persistentVolumeClaim:
        claimName: task-pv-claim
  containers:
    - name: task-pv-container
      image: nginx:1.21
      ports:
        - containerPort: 80
          name: "http-server"
      volumeMounts:
        - mountPath: "/usr/share/nginx/html"
          name: task-pv-storage
```

### 6.3.4 PV和PVC操作示例

```bash
# 1. 创建PV
kubectl apply -f pv-example.yaml

# 2. 创建PVC
kubectl apply -f pvc-example.yaml

# 3. 查看PV和PVC状态
kubectl get pv
kubectl get pvc

# 4. 创建使用PVC的Pod
kubectl apply -f pod-with-pvc.yaml

# 5. 验证存储
kubectl exec -it task-pv-pod -- sh
# 在容器内执行
echo "Hello Persistent Storage" > /usr/share/nginx/html/index.html

# 6. 删除Pod后重新创建，数据仍然存在
kubectl delete pod task-pv-pod
kubectl apply -f pod-with-pvc.yaml
kubectl exec -it task-pv-pod -- cat /usr/share/nginx/html/index.html
```

## 6.4 StorageClass详解

StorageClass用于动态供应存储资源。

### 6.4.1 StorageClass定义

```yaml
# storageclass-example.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-sc
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp2
  fsType: ext4
reclaimPolicy: Retain
allowVolumeExpansion: true
mountOptions:
  - debug
volumeBindingMode: Immediate
```

### 6.4.2 使用StorageClass的PVC

```yaml
# pvc-with-storageclass.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: fast-claim
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast-sc
  resources:
    requests:
      storage: 30Gi
```

### 6.4.3 StorageClass操作示例

```bash
# 1. 创建StorageClass
kubectl apply -f storageclass-example.yaml

# 2. 查看StorageClass
kubectl get storageclasses

# 3. 创建使用StorageClass的PVC
kubectl apply -f pvc-with-storageclass.yaml

# 4. 查看PVC状态（应该会自动创建PV）
kubectl get pvc
kubectl get pv

# 5. 查看动态创建的PV详细信息
kubectl describe pv <pv-name>
```

## 6.5 访问模式详解

Kubernetes支持多种存储访问模式：

### 6.5.1 ReadWriteOnce (RWO)

卷可以被单个节点以读写方式挂载。

### 6.5.2 ReadOnlyMany (ROX)

卷可以被多个节点以只读方式挂载。

### 6.5.3 ReadWriteMany (RWX)

卷可以被多个节点以读写方式挂载。

### 6.5.4 访问模式示例

```yaml
# pvc-access-modes.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: rwo-claim
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: rox-claim
spec:
  accessModes:
    - ReadOnlyMany
  resources:
    requests:
      storage: 1Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: rwx-claim
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 1Gi
```

## 6.6 回收策略

### 6.6.1 Retain（保留）

手动回收，当PVC被删除时，PV仍然存在，需要管理员手动清理。

### 6.6.2 Recycle（回收）

基础擦除（`rm -rf /thevolume/*`），已被废弃。

### 6.6.3 Delete（删除）

关联的存储资产（如AWS EBS、GCE PD、Azure Disk）也会被删除。

### 6.6.4 回收策略示例

```yaml
# pv-with-reclaim-policy.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-with-retained-data
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  hostPath:
    path: "/mnt/data"
```

## 6.7 卷扩展

Kubernetes支持动态扩展持久化卷的大小。

### 6.7.1 启用卷扩展

```yaml
# storageclass-expandable.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: expandable-sc
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp2
allowVolumeExpansion: true  # 启用卷扩展
```

### 6.7.2 扩展PVC

```bash
# 编辑PVC增加存储大小
kubectl patch pvc <pvc-name> -p '{"spec":{"resources":{"requests":{"storage":"50Gi"}}}}'

# 查看PVC状态
kubectl get pvc

# 查看扩展事件
kubectl describe pvc <pvc-name>
```

## 6.8 存储故障排除

### 6.8.1 常见问题诊断

#### PVC处于Pending状态

```bash
# 查看PVC状态和事件
kubectl describe pvc <pvc-name>

# 常见原因：
# 1. 没有匹配的PV
# 2. StorageClass不存在
# 3. 请求的存储大小超过可用容量
# 4. 访问模式不匹配
```

#### Pod无法启动，挂载卷失败

```bash
# 查看Pod状态和事件
kubectl describe pod <pod-name>

# 常见原因：
# 1. PV不存在或状态异常
# 2. PVC未绑定
# 3. 权限问题
# 4. 存储后端故障
```

### 6.8.2 存储诊断命令

```bash
# 查看所有存储相关资源
kubectl get pv,pvc,storageclasses

# 查看PV详细信息
kubectl describe pv <pv-name>

# 查看PVC详细信息
kubectl describe pvc <pvc-name>

# 查看StorageClass详细信息
kubectl describe storageclass <storageclass-name>

# 查看节点上的存储信息
kubectl describe node <node-name>
```

## 6.9 实验：存储实践操作

### 6.9.1 本地存储实验

```yaml
# local-storage-lab.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: local-pv-1
  labels:
    type: local
spec:
  storageClassName: manual
  capacity:
    storage: 5Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: "/mnt/disks/vol1"
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: local-pv-2
  labels:
    type: local
spec:
  storageClassName: manual
  capacity:
    storage: 5Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: "/mnt/disks/vol2"
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: local-pvc
spec:
  storageClassName: manual
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 3Gi
---
apiVersion: v1
kind: Pod
metadata:
  name: local-storage-pod
spec:
  volumes:
    - name: local-storage
      persistentVolumeClaim:
        claimName: local-pvc
  containers:
    - name: local-storage-container
      image: nginx:1.21
      volumeMounts:
        - mountPath: "/usr/share/nginx/html"
          name: local-storage
```

实验步骤：

```bash
# 1. 在节点上创建目录
mkdir -p /mnt/disks/vol1 /mnt/disks/vol2

# 2. 创建PV、PVC和Pod
kubectl apply -f local-storage-lab.yaml

# 3. 查看资源状态
kubectl get pv
kubectl get pvc
kubectl get pods

# 4. 验证数据持久性
kubectl exec -it local-storage-pod -- sh
# 在容器内执行
echo "Local Storage Test" > /usr/share/nginx/html/index.html
exit

# 5. 删除Pod并重新创建
kubectl delete pod local-storage-pod
kubectl apply -f local-storage-lab.yaml

# 6. 验证数据仍然存在
kubectl exec -it local-storage-pod -- cat /usr/share/nginx/html/index.html
```

### 6.9.2 动态存储实验

```yaml
# dynamic-storage-lab.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-storage
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: dynamic-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: local-storage
  resources:
    requests:
      storage: 2Gi
---
apiVersion: v1
kind: Pod
metadata:
  name: dynamic-storage-pod
spec:
  volumes:
    - name: dynamic-storage
      persistentVolumeClaim:
        claimName: dynamic-pvc
  containers:
    - name: dynamic-storage-container
      image: nginx:1.21
      volumeMounts:
        - mountPath: "/usr/share/nginx/html"
          name: dynamic-storage
```

实验步骤：

```bash
# 1. 创建StorageClass、PVC和Pod
kubectl apply -f dynamic-storage-lab.yaml

# 2. 查看资源状态
kubectl get storageclasses
kubectl get pvc
kubectl get pods

# 3. 查看动态创建的PV
kubectl get pv

# 4. 验证数据持久性
kubectl exec -it dynamic-storage-pod -- sh
# 在容器内执行
echo "Dynamic Storage Test" > /usr/share/nginx/html/index.html
exit

# 5. 删除Pod并重新创建
kubectl delete pod dynamic-storage-pod
kubectl apply -f dynamic-storage-lab.yaml

# 6. 验证数据仍然存在
kubectl exec -it dynamic-storage-pod -- cat /usr/share/nginx/html/index.html
```

### 6.9.3 卷扩展实验

```yaml
# volume-expansion-lab.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: expandable-local-storage
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: expandable-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: expandable-local-storage
  resources:
    requests:
      storage: 1Gi
---
apiVersion: v1
kind: Pod
metadata:
  name: expansion-test-pod
spec:
  volumes:
    - name: expansion-storage
      persistentVolumeClaim:
        claimName: expandable-pvc
  containers:
    - name: expansion-container
      image: nginx:1.21
      volumeMounts:
        - mountPath: "/usr/share/nginx/html"
          name: expansion-storage
```

实验步骤：

```bash
# 1. 创建可扩展的StorageClass、PVC和Pod
kubectl apply -f volume-expansion-lab.yaml

# 2. 查看初始状态
kubectl get pvc
kubectl get pv

# 3. 扩展PVC大小
kubectl patch pvc expandable-pvc -p '{"spec":{"resources":{"requests":{"storage":"3Gi"}}}}'

# 4. 查看扩展状态
kubectl get pvc
kubectl describe pvc expandable-pvc

# 5. 在Pod中验证存储大小
kubectl exec -it expansion-test-pod -- df -h /usr/share/nginx/html
```

## 6.10 存储最佳实践

### 6.10.1 选择合适的存储类型

1. **临时数据**：使用emptyDir
2. **配置数据**：使用ConfigMap或Secret
3. **持久化数据**：使用PV/PVC
4. **共享数据**：使用支持ReadWriteMany的存储

### 6.10.2 设置资源限制

```yaml
# pvc-with-resource-limits.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: production-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 100Gi
    # 注意：limits在PVC中不常用，但在某些场景下可能有用
```

### 6.10.3 使用StorageClass进行分层存储

```yaml
# storage-class-tiered.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs
parameters:
  type: io1
  iopsPerGB: "50"
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard-hdd
provisioner: kubernetes.io/aws-ebs
parameters:
  type: st1
```

### 6.10.4 数据备份和恢复策略

1. 定期备份重要数据
2. 使用快照功能（如果存储后端支持）
3. 实施灾难恢复计划
4. 测试备份和恢复流程

## 6.11 小结

本章我们深入学习了Kubernetes存储管理的相关概念和技术：

1. **Volume机制**：了解了Pod级别的存储卷及其不同类型
2. **PV和PVC**：掌握了持久化存储的解耦机制
3. **StorageClass**：学习了动态存储供应的方式
4. **访问模式**：理解了不同的存储访问方式
5. **回收策略**：掌握了存储资源的回收机制
6. **卷扩展**：学会了如何动态扩展存储卷大小
7. **故障排除**：掌握了存储相关问题的诊断方法
8. **实践操作**：通过实验加深了对存储概念的理解
9. **最佳实践**：了解了存储使用的最佳实践

下一章我们将学习Kubernetes的配置管理机制，包括ConfigMap和Secret的使用方法。