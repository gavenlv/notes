# Day 15: 容器化与Kubernetes集成 - 实践练习

## 练习1: Docker容器化练习

### 目标
构建自定义Airflow Docker镜像，并使用Docker Compose部署一个完整的Airflow环境。

### 步骤
1. 创建Dockerfile，基于官方Airflow镜像，添加自定义依赖
2. 编写requirements.txt文件，包含额外的Python包
3. 创建Docker Compose文件，定义多容器服务（PostgreSQL、Redis、Airflow组件）
4. 构建并启动Docker Compose环境
5. 验证Airflow Web UI是否正常运行

### 验证方法
- 访问http://localhost:8080，确认Airflow登录页面正常显示
- 使用默认账户登录（admin/admin）
- 检查DAG列表是否正常显示
- 查看容器日志，确认各组件正常启动

## 练习2: Helm部署练习

### 目标
使用官方Helm Chart将Airflow部署到Kubernetes集群。

### 步骤
1. 安装Helm工具
2. 添加Apache Airflow Helm仓库
3. 创建自定义values.yaml文件，配置执行器、资源限制等
4. 使用Helm安装Airflow Chart
5. 验证部署状态和服务访问

### 验证方法
- 使用`kubectl get pods`检查所有Pod是否正常运行
- 使用`kubectl get services`查看服务状态
- 通过端口转发访问Airflow Web UI
- 检查Helm release状态

## 练习3: Kubernetes Executor配置

### 目标
配置和测试KubernetesExecutor，观察任务Pod的创建和销毁过程。

### 步骤
1. 修改Airflow配置，启用KubernetesExecutor
2. 配置Kubernetes连接参数
3. 创建测试DAG，包含多个任务
4. 触发DAG运行
5. 观察Kubernetes中任务Pod的创建和销毁过程

### 验证方法
- 使用`kubectl get pods`观察任务Pod的生命周期
- 检查Airflow Web UI中的任务执行状态
- 查看任务Pod的日志
- 确认任务成功完成后Pod被正确清理

## 练习4: KubernetesPodOperator应用

### 目标
创建使用KubernetesPodOperator的任务DAG，执行外部任务。

### 步骤
1. 创建包含KubernetesPodOperator任务的DAG
2. 配置Pod参数，包括镜像、命令、资源限制等
3. 设置环境变量和卷挂载（如需要）
4. 运行DAG并观察Pod执行情况
5. 检查任务结果和日志

### 验证方法
- 确认Pod按预期创建和执行
- 检查Pod日志输出是否符合预期
- 验证任务状态在Airflow中正确显示
- 测试不同配置参数对Pod行为的影响

## 练习5: 安全配置练习

### 目标
配置RBAC和服务账户，实现最小权限原则。

### 步骤
1. 创建专门用于Airflow的ServiceAccount
2. 定义Role和RoleBinding，授予必要权限
3. 配置网络策略，限制Pod网络访问
4. 设置镜像拉取密钥（如使用私有镜像仓库）
5. 验证安全配置的有效性

### 验证方法
- 确认Airflow Pod使用指定的ServiceAccount运行
- 验证权限配置是否按预期工作
- 检查网络策略是否正确应用
- 测试私有镜像拉取是否正常（如配置）

## 练习6: 监控集成练习

### 目标
集成Prometheus和Grafana，配置关键指标监控。

### 步骤
1. 部署Prometheus和Grafana到Kubernetes集群
2. 配置Prometheus抓取Airflow指标
3. 创建Grafana仪表板，展示关键Airflow指标
4. 配置日志收集方案（如EFK）
5. 验证监控和日志系统正常工作

### 验证方法
- 确认Prometheus能正确抓取Airflow指标
- 验证Grafana仪表板显示正确的数据
- 检查日志是否正确收集和展示
- 测试告警机制是否正常工作

## 附加挑战练习

### 挑战1: 多环境部署
配置Helm values文件，支持dev、staging、prod多环境部署，每个环境有不同的资源配置和安全设置。

### 挑战2: 自定义指标
扩展Airflow，添加自定义业务指标，并在Prometheus中展示。

### 挑战3: 自动扩缩容
配置Horizontal Pod Autoscaler，根据任务队列长度自动调整Worker数量。

### 挑战4: 零停机升级
设计并实施Airflow的零停机升级方案，确保在升级过程中不影响正在运行的任务。