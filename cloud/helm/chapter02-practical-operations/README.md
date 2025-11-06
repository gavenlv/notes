# 第二章：Helm实践操作

## 创建第一个Chart

在本章中，我们将学习如何创建、定制和安装自己的Chart。

### Chart的目录结构

一个典型的Chart目录结构如下：
```
mychart/
├── Chart.yaml
├── values.yaml
├── charts/
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   └── _helpers.tpl
└── README.md
```

### Chart.yaml
包含Chart的元数据信息。

### values.yaml
包含Chart的默认配置值。

### templates/
包含Kubernetes资源定义的模板文件。

### _helpers.tpl
包含Chart的模板辅助函数。

## 本章实验：创建和部署自定义Chart

在本章中，我们将创建一个简单的Web应用Chart，并学习如何定制和部署它。