# 第3章：HTTP状态码详解与实战应用

## 本章概述

在前面两章中，我们学习了HTTP协议的基本概念、发展历程以及消息结构。本章我们将深入探讨HTTP状态码体系，这是HTTP协议中非常重要的一部分。状态码不仅告诉客户端请求的处理结果，还能帮助开发者诊断问题、优化应用。

## 学习目标

- 全面理解HTTP状态码的分类和含义
- 掌握常见状态码的实际应用场景
- 学会在开发中正确使用和处理状态码
- 能够根据业务需求选择合适的状态码
- 了解状态码在RESTful API设计中的重要性

## 3.1 HTTP状态码基础概念

HTTP状态码是服务器对客户端请求的响应状态的数字代码，由三位数字组成。第一个数字定义了响应类别，后两个数字没有具体分类作用。

### 3.1.1 状态码结构

HTTP状态码遵循以下格式：
```
HTTP-Version Status-Code Reason-Phrase
```

例如：
```
HTTP/1.1 200 OK
HTTP/2.0 404 Not Found
```

### 3.1.2 状态码分类

HTTP状态码按照第一位数字分为五大类：

#### 1xx 信息性状态码（Informational）
表示请求已被接收，继续处理。

#### 2xx 成功状态码（Success）
表示请求已成功被服务器接收、理解、并接受。

#### 3xx 重定向状态码（Redirection）
表示需要客户端采取进一步的操作才能完成请求。

#### 4xx 客户端错误状态码（Client Error）
表示客户端发送的请求有语法错误或无法完成请求。

#### 5xx 服务器错误状态码（Server Error）
表示服务器在处理请求的过程中发生了错误。

## 3.2 1xx 信息性状态码

1xx状态码表示临时响应，服务器已经接收到请求，客户端应该继续执行操作。

### 3.2.1 100 Continue

**含义**：服务器已经接收到请求头，客户端应该继续发送请求体。

**使用场景**：
- 当客户端发送带有较大请求体的POST请求时
- 客户端在发送请求体之前先发送请求头，并等待服务器确认

**示例**：
```
客户端 -> 服务器: 
POST /upload HTTP/1.1
Host: example.com
Content-Length: 1024000
Expect: 100-continue

服务器 -> 客户端:
HTTP/1.1 100 Continue

客户端 -> 服务器:
[发送1MB的数据]
```

### 3.2.2 101 Switching Protocols

**含义**：服务器同意切换协议。

**使用场景**：
- WebSocket升级
- HTTP/2升级
- 其他协议切换

**示例**：
```
客户端 -> 服务器:
GET /chat HTTP/1.1
Host: example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13

服务器 -> 客户端:
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

## 3.3 2xx 成功状态码

2xx状态码表示请求已成功处理。

### 3.3.1 200 OK

**含义**：请求成功。

**使用场景**：
- GET请求成功获取资源
- POST请求成功创建资源
- PUT请求成功更新资源

**最佳实践**：
- 对于GET请求，响应体应包含请求的资源
- 对于POST/PUT请求，可根据API设计决定是否返回资源表示

### 3.3.2 201 Created

**含义**：请求成功并且服务器创建了新的资源。

**使用场景**：
- POST请求成功创建新资源
- 应在响应的Location头部返回新资源的URI

**示例**：
```
客户端 -> 服务器:
POST /api/users HTTP/1.1
Host: api.example.com
Content-Type: application/json

{
  "name": "张三",
  "email": "zhangsan@example.com"
}

服务器 -> 客户端:
HTTP/1.1 201 Created
Location: https://api.example.com/users/123
Content-Type: application/json

{
  "id": 123,
  "name": "张三",
  "email": "zhangsan@example.com",
  "createdAt": "2023-01-01T12:00:00Z"
}
```

### 3.3.3 202 Accepted

**含义**：服务器已接受请求，但尚未处理完成。

**使用场景**：
- 异步处理请求
- 批量操作
- 需要长时间运行的任务

**最佳实践**：
- 应在响应体中提供任务状态查询的链接
- 可以包含预计完成时间

### 3.3.4 204 No Content

**含义**：请求成功，但响应中没有内容。

**使用场景**：
- DELETE请求成功删除资源
- PUT/PATCH请求成功更新资源但不需要返回内容

**示例**：
```
客户端 -> 服务器:
DELETE /api/users/123 HTTP/1.1
Host: api.example.com

服务器 -> 客户端:
HTTP/1.1 204 No Content
```

### 3.3.5 206 Partial Content

**含义**：服务器成功处理了部分GET请求。

**使用场景**：
- 断点续传
- 大文件分片下载
- 视频流媒体

**示例**：
```
客户端 -> 服务器:
GET /video.mp4 HTTP/1.1
Host: example.com
Range: bytes=0-1023

服务器 -> 客户端:
HTTP/1.1 206 Partial Content
Content-Range: bytes 0-1023/1048576
Content-Length: 1024

[二进制数据]
```

## 3.4 3xx 重定向状态码

3xx状态码表示客户端需要采取进一步操作才能完成请求。

### 3.4.1 301 Moved Permanently

**含义**：请求的资源已永久移动到新位置。

**使用场景**：
- 网站迁移
- URL结构调整
- 合并重复内容

**最佳实践**：
- 搜索引擎会更新索引到新URL
- 浏览器会自动跳转并缓存重定向

### 3.4.2 302 Found

**含义**：请求的资源临时从不同URI响应请求。

**使用场景**：
- 临时重定向
- 维护页面跳转
- A/B测试

**注意**：与307 Temporary Redirect的区别在于POST可能变为GET。

### 3.4.3 304 Not Modified

**含义**：资源未修改，可以使用缓存版本。

**使用场景**：
- 条件GET请求
- 浏览器缓存验证
- 减少带宽消耗

**示例**：
```
客户端 -> 服务器:
GET /style.css HTTP/1.1
Host: example.com
If-Modified-Since: Wed, 21 Oct 2023 07:28:00 GMT
If-None-Match: "33a64df551425fcc55e4d42a148795d9f25f89d4"

服务器 -> 客户端:
HTTP/1.1 304 Not Modified
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
```

### 3.4.4 307 Temporary Redirect

**含义**：临时重定向，保持请求方法不变。

**使用场景**：
- 临时维护页面
- 负载均衡重定向

**与302的区别**：保证POST等请求方法不会变为GET。

### 3.4.5 308 Permanent Redirect

**含义**：永久重定向，保持请求方法不变。

**使用场景**：
- HTTPS升级
- 域名变更但保持方法

**与301的区别**：保证POST等请求方法不会变为GET。

## 3.5 4xx 客户端错误状态码

4xx状态码表示客户端发送的请求存在问题。

### 3.5.1 400 Bad Request

**含义**：客户端发送的请求有语法错误。

**使用场景**：
- 请求体格式错误
- 缺少必需参数
- 参数值无效

**最佳实践**：
- 在响应体中提供详细的错误信息
- 指明哪个字段有问题

### 3.5.2 401 Unauthorized

**含义**：请求需要身份验证。

**使用场景**：
- 未提供认证信息
- 认证信息无效
- 认证过期

**示例**：
```
服务器 -> 客户端:
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer realm="api"
Content-Type: application/json

{
  "error": "unauthorized",
  "message": "缺少或无效的认证令牌"
}
```

### 3.5.3 403 Forbidden

**含义**：服务器理解请求但拒绝执行。

**使用场景**：
- 权限不足
- IP被限制
- 资源被禁止访问

**与401的区别**：
- 401：未认证，可以通过登录解决
- 403：已认证但无权限，登录也无法解决

### 3.5.4 404 Not Found

**含义**：请求的资源不存在。

**使用场景**：
- URL错误
- 资源被删除
- 资源从未存在

**最佳实践**：
- 提供有用的错误页面
- 返回统一的404页面而非空白页面

### 3.5.5 405 Method Not Allowed

**含义**：请求方法对资源不被允许。

**使用场景**：
- 对只读资源发送POST请求
- API端点不支持某种HTTP方法

**示例**：
```
服务器 -> 客户端:
HTTP/1.1 405 Method Not Allowed
Allow: GET, HEAD
Content-Type: application/json

{
  "error": "method_not_allowed",
  "message": "此端点只支持GET和HEAD方法"
}
```

### 3.5.6 409 Conflict

**含义**：请求与服务器当前状态冲突。

**使用场景**：
- 并发修改冲突
- 资源状态不允许执行操作
- 唯一约束违反

### 3.5.7 410 Gone

**含义**：请求的资源已永久删除。

**使用场景**：
- 已删除的内容
- 不再提供的API端点

### 3.5.8 415 Unsupported Media Type

**含义**：服务器不支持请求体的媒体类型。

**使用场景**：
- Content-Type不被支持
- 请求体格式不符合要求

### 3.5.9 422 Unprocessable Entity

**含义**：请求格式正确但语义错误。

**使用场景**：
- 数据验证失败
- 业务逻辑错误
- 字段值超出范围

### 3.5.10 429 Too Many Requests

**含义**：客户端发送了太多请求。

**使用场景**：
- API速率限制
- 防止滥用
- DDOS防护

**最佳实践**：
- 在Retry-After头部指明重试时间
- 提供清晰的限流说明

## 3.6 5xx 服务器错误状态码

5xx状态码表示服务器在处理请求时发生错误。

### 3.6.1 500 Internal Server Error

**含义**：服务器遇到了未知错误。

**使用场景**：
- 未处理的异常
- 服务器配置错误
- 数据库连接失败

**最佳实践**：
- 记录详细的错误日志
- 不要在响应中暴露敏感信息

### 3.6.2 501 Not Implemented

**含义**：服务器不支持请求的功能。

**使用场景**：
- 未实现的HTTP方法
- 不支持的功能特性

### 3.6.3 502 Bad Gateway

**含义**：作为网关或代理的服务器从上游服务器收到无效响应。

**使用场景**：
- 反向代理错误
- 微服务间通信失败
- 负载均衡器故障

### 3.6.4 503 Service Unavailable

**含义**：服务器暂时无法处理请求。

**使用场景**：
- 服务器维护
- 过载保护
- 依赖服务不可用

**最佳实践**：
- 在Retry-After头部指明恢复时间
- 提供维护页面

### 3.6.5 504 Gateway Timeout

**含义**：作为网关或代理的服务器未能及时从上游服务器获得响应。

**使用场景**：
- 上游服务响应超时
- 网络连接问题
- 上游服务繁忙

## 3.7 状态码在RESTful API设计中的应用

### 3.7.1 RESTful API状态码选择原则

1. **一致性**：整个API应保持状态码使用的一致性
2. **准确性**：选择最准确描述操作结果的状态码
3. **丰富性**：充分利用HTTP状态码表达不同场景

### 3.7.2 常见REST操作的状态码

| 操作 | 成功状态码 | 常见错误状态码 |
|------|------------|----------------|
| GET | 200 (OK) | 404 (Not Found), 401 (Unauthorized) |
| POST | 201 (Created) | 400 (Bad Request), 409 (Conflict) |
| PUT | 200 (OK) / 204 (No Content) | 400 (Bad Request), 404 (Not Found) |
| PATCH | 200 (OK) / 204 (No Content) | 400 (Bad Request), 404 (Not Found) |
| DELETE | 200 (OK) / 204 (No Content) | 404 (Not Found), 409 (Conflict) |

### 3.7.3 错误响应格式设计

```json
{
  "error": "validation_failed",
  "message": "数据验证失败",
  "details": [
    {
      "field": "email",
      "code": "invalid_email",
      "message": "邮箱格式不正确"
    },
    {
      "field": "password",
      "code": "too_short",
      "message": "密码长度至少8位"
    }
  ]
}
```

## 3.8 实战案例分析

### 3.8.1 用户管理系统状态码设计

让我们看一个用户管理系统的状态码使用示例：

```python
# 用户注册
# POST /api/users
# 成功: 201 Created
# 邮箱已存在: 409 Conflict
# 数据验证失败: 422 Unprocessable Entity

# 用户登录
# POST /api/auth/login
# 成功: 200 OK
# 密码错误: 401 Unauthorized
# 账户被锁定: 423 Locked

# 获取用户信息
# GET /api/users/{id}
# 成功: 200 OK
# 用户不存在: 404 Not Found
# 无权限查看: 403 Forbidden

# 更新用户信息
# PUT /api/users/{id}
# 成功: 200 OK
# 用户不存在: 404 Not Found
# 数据验证失败: 422 Unprocessable Entity
# 无权限修改: 403 Forbidden

# 删除用户
# DELETE /api/users/{id}
# 成功: 204 No Content
# 用户不存在: 404 Not Found
# 无权限删除: 403 Forbidden
```

### 3.8.2 文件上传系统状态码设计

```python
# 文件上传
# POST /api/files
# 成功: 201 Created
# 文件过大: 413 Payload Too Large
# 不支持的文件类型: 415 Unsupported Media Type
# 存储空间不足: 507 Insufficient Storage

# 文件下载
# GET /api/files/{id}
# 成功: 200 OK 或 206 Partial Content
# 文件不存在: 404 Not Found
# 无权限访问: 403 Forbidden

# 文件删除
# DELETE /api/files/{id}
# 成功: 204 No Content
# 文件不存在: 404 Not Found
```

## 3.9 状态码处理最佳实践

### 3.9.1 客户端状态码处理

```javascript
// JavaScript示例：优雅处理HTTP状态码
async function handleApiResponse(response) {
  switch (response.status) {
    case 200:
    case 201:
      return await response.json();
    
    case 400:
      throw new Error('请求参数错误');
    
    case 401:
      // 重定向到登录页面
      window.location.href = '/login';
      break;
    
    case 403:
      throw new Error('权限不足');
    
    case 404:
      throw new Error('资源不存在');
    
    case 429:
      const retryAfter = response.headers.get('Retry-After');
      throw new Error(`请求过于频繁，请${retryAfter}秒后重试`);
    
    case 500:
      throw new Error('服务器内部错误');
    
    case 503:
      throw new Error('服务暂时不可用');
    
    default:
      throw new Error(`未知错误: ${response.status}`);
  }
}
```

### 3.9.2 服务器端状态码返回

```python
# Python Flask示例：正确返回HTTP状态码
from flask import Flask, jsonify, request

@app.route('/api/users', methods=['POST'])
def create_user():
    try:
        # 验证请求数据
        data = request.get_json()
        if not data or 'email' not in data:
            return jsonify({
                'error': 'missing_field',
                'message': '缺少必需字段: email'
            }), 400
        
        # 检查邮箱是否已存在
        if user_exists(data['email']):
            return jsonify({
                'error': 'duplicate_email',
                'message': '邮箱已被注册'
            }), 409
        
        # 创建用户
        user = create_new_user(data)
        return jsonify(user), 201
        
    except ValidationError as e:
        return jsonify({
            'error': 'validation_failed',
            'message': str(e)
        }), 422
        
    except Exception as e:
        # 记录错误日志
        logger.error(f"创建用户失败: {str(e)}")
        return jsonify({
            'error': 'internal_error',
            'message': '服务器内部错误'
        }), 500
```

### 3.9.3 状态码使用注意事项

1. **不要过度使用500**：应该根据具体错误类型返回更精确的状态码
2. **保持一致性**：同一API中相同类型的错误应该返回相同的状态码
3. **提供有用的信息**：错误响应应该包含足够的信息帮助客户端理解问题
4. **避免信息泄露**：错误响应不应该暴露服务器内部实现细节
5. **考虑缓存影响**：不同的状态码对缓存的影响不同

## 3.10 小结

本章我们深入学习了HTTP状态码体系，包括：

1. 状态码的分类和含义
2. 各类状态码的典型使用场景
3. 状态码在RESTful API设计中的应用
4. 实际开发中状态码的处理最佳实践

正确使用HTTP状态码不仅能提高API的质量，还能改善用户体验。在下一章中，我们将探讨HTTP方法的详细使用和设计原则。