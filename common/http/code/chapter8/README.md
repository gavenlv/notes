# HTTP认证与授权机制代码示例

## 概述
本目录包含了HTTP认证与授权机制相关的代码示例，展示了基本认证、摘要认证、Bearer Token、OAuth 2.0、JWT等核心概念的实际应用。

## 代码示例文件列表

1. `basic_auth_server.py` - 基本认证服务器示例
   - 实现HTTP基本认证机制
   - 演示401状态码和WWW-Authenticate头部使用

2. `digest_auth_server.py` - 摘要认证服务器示例
   - 实现HTTP摘要认证机制
   - 展示nonce生成和响应验证过程

3. `jwt_auth_server.py` - JWT认证服务器示例
   - 实现基于JWT的认证系统
   - 演示令牌生成、验证和刷新流程

4. `oauth2_server.py` - OAuth 2.0服务器示例
   - 实现OAuth 2.0授权码流程
   - 展示授权端点和令牌端点

5. `auth_middleware.py` - 认证中间件示例
   - 实现通用认证中间件
   - 支持多种认证方式集成

6. `rbac_authorization.py` - RBAC授权示例
   - 实现基于角色的访问控制
   - 演示权限检查和访问控制

## 环境要求
- Python 3.7+
- Flask==2.3.2
- requests==2.31.0
- PyJWT==2.8.0
- cryptography==41.0.3

## 运行说明

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 运行各个示例文件：
   ```bash
   python basic_auth_server.py
   python digest_auth_server.py
   python jwt_auth_server.py
   python oauth2_server.py
   python auth_middleware.py
   python rbac_authorization.py
   ```

## 代码实现细节

### 1. 基本认证服务器 (`basic_auth_server.py`)
实现了HTTP基本认证机制：
- Base64解码用户名和密码
- 用户凭证验证逻辑
- 401响应和WWW-Authenticate头部生成
- 安全注意事项和HTTPS强制使用

### 2. 摘要认证服务器 (`digest_auth_server.py`)
实现了HTTP摘要认证机制：
- nonce生成和管理
- HA1、HA2和response计算
- qop（quality of protection）支持
- 重放攻击防护机制

### 3. JWT认证服务器 (`jwt_auth_server.py`)
实现了基于JWT的认证系统：
- JWT令牌生成（包含声明）
- 令牌签名和验证
- 刷新令牌机制实现
- 令牌撤销和黑名单管理

### 4. OAuth 2.0服务器 (`oauth2_server.py`)
实现了OAuth 2.0授权码流程：
- 授权端点实现
- 令牌端点实现
- 客户端凭证验证
- 授权码生成和交换流程

### 5. 认证中间件 (`auth_middleware.py`)
实现了通用认证中间件：
- 多种认证方式支持（Basic、Bearer、API Key等）
- 认证失败处理和错误响应
- 用户信息注入到请求上下文
- 可配置的认证规则

### 6. RBAC授权示例 (`rbac_authorization.py`)
实现了基于角色的访问控制系统：
- 用户、角色、权限数据模型
- 角色分配和权限检查
- 访问控制决策逻辑
- 细粒度权限控制示例

## 学习建议

1. 先运行`basic_auth_server.py`理解最简单的认证机制
2. 通过`digest_auth_server.py`学习更安全的认证方式
3. 研究`jwt_auth_server.py`掌握现代API认证方法
4. 学习`oauth2_server.py`了解第三方授权流程
5. 查看`auth_middleware.py`理解认证系统的架构设计
6. 通过`rbac_authorization.py`掌握授权控制机制

## 注意事项

- 这些示例主要用于学习目的，在生产环境中使用时需要根据具体需求进行调整
- 认证和授权是安全敏感的功能，务必在HTTPS环境下使用
- 密码和密钥管理需要特别注意，不应硬编码在代码中
- 建议参考OWASP等安全标准来实现生产级的认证授权系统