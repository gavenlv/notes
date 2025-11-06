# 第一章：Helm基础概念

## 什么是Helm？

Helm是Kubernetes的包管理器，类似于Linux系统中的APT或YUM，或者Node.js中的NPM。它帮助您定义、安装和管理Kubernetes应用的复杂性。

## Helm的核心概念

### 1. Chart
Chart是Helm的打包格式，包含了一组Kubernetes资源定义。可以将其理解为一个预配置的Kubernetes资源包。

### 2. Release
Release是Chart在Kubernetes集群中的运行实例。一个Chart可以被安装多次，每次安装都会创建一个新的Release。

### 3. Repository
Repository是存储和分享Charts的地方，类似于Docker Hub存储Docker镜像。

### 4. Config
Config包含可以合并到Chart中的配置信息，用于创建一个可发布的对象。

## Helm架构

Helm有两个主要组件：
1. **Helm Client** - 用户使用的命令行客户端
2. **Helm Library** - 提供执行所有Helm操作的逻辑

在Helm 3中，移除了Tiller组件，直接与Kubernetes API交互。

## 本章实验：安装Helm并验证

在本章中，我们将安装Helm并验证其基本功能。