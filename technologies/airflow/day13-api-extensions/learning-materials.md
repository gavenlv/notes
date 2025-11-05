# Day 13 学习材料

## 1. Airflow REST API概述

### 1.1 API简介
Airflow提供了一套完整的REST API，允许开发者通过HTTP请求来管理DAGs、任务、触发执行、获取状态等。

### 1.2 API端点分类
- DAG管理：创建、更新、删除、列出DAG
- DAG运行管理：触发DAG运行、获取运行状态、停止运行
- 任务实例管理：获取任务状态、修改任务状态
- 配置管理：获取和更新配置信息
- 连接和变量管理：管理连接信息和变量

### 1.3 API文档
官方API文档地址：https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html

## 2. API认证与授权

### 2.1 认证方式
- 基于用户名密码的Basic Auth
- 基于Token的认证
- OAuth集成
- LDAP集成

### 2.2 权限控制
- 基于角色的访问控制(RBAC)
- 资源级别的权限管理
- API端点级别的权限控制

## 3. 插件系统架构

### 3.1 插件概念
Airflow插件允许扩展以下功能：
- 自定义操作符
- 自定义传感器
- 自定义钩子
- 自定义宏
- 自定义视图(Fask web界面)
- 自定义菜单链接
- 自定义蓝调打印(Blueprints)

### 3.2 插件结构
```python
from airflow.plugins_manager import AirflowPlugin

class MyPlugin(AirflowPlugin):
    name = "my_plugin"
    
    # 扩展点
    operators = []
    sensors = []
    hooks = []
    executors = []
    macros = []
    admin_views = []
    flask_blueprints = []
    menu_links = []
    appbuilder_views = []
    appbuilder_menu_items = []
```

## 4. 第三方集成

### 4.1 与外部系统的集成
- CI/CD工具集成
- 监控系统集成
- 数据可视化工具集成
- 消息队列集成

### 4.2 Webhook支持
- 实现自定义触发器
- 与外部系统事件联动