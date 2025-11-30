#!/usr/bin/env python3
"""
OAuth 2.0 客户端演示

这个模块演示了如何实现一个 OAuth 2.0 客户端，包括：
1. 授权码流程 (Authorization Code Flow)
2. 隐式流程 (Implicit Flow) - 演示用途
3. 客户端凭据流程 (Client Credentials Flow)
4. 资源所有者密码凭据流程 (Resource Owner Password Credentials Flow)

学习目标：
- 理解 OAuth 2.0 的不同授权流程
- 掌握客户端如何与 OAuth 2.0 授权服务器交互
- 实践 OAuth 2.0 在应用程序中的集成
"""

import requests
import secrets
import base64
import hashlib
import webbrowser
from urllib.parse import urlencode, parse_qs, urlparse
from flask import Flask, request, jsonify, redirect

# 初始化 Flask 应用（用于演示回调处理）
app = Flask(__name__)

# OAuth 2.0 客户端配置
CLIENT_ID = "demo-client-id"
CLIENT_SECRET = "demo-client-secret"
REDIRECT_URI = "http://localhost:5003/callback"
AUTHORIZATION_SERVER_URL = "https://authorization-server.example.com"  # 示例授权服务器
TOKEN_ENDPOINT = f"{AUTHORIZATION_SERVER_URL}/oauth/token"
AUTHORIZATION_ENDPOINT = f"{AUTHORIZATION_SERVER_URL}/oauth/authorize"

# 存储令牌的全局变量（实际应用中应使用安全存储）
access_token = None
refresh_token = None

class OAuth2Client:
    """OAuth 2.0 客户端实现"""
    
    def __init__(self, client_id, client_secret, redirect_uri, auth_server_url):
        """
        初始化 OAuth 2.0 客户端
        
        Args:
            client_id (str): 客户端 ID
            client_secret (str): 客户端密钥
            redirect_uri (str): 重定向 URI
            auth_server_url (str): 授权服务器 URL
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_server_url = auth_server_url
        self.token_endpoint = f"{auth_server_url}/oauth/token"
        self.authorization_endpoint = f"{auth_server_url}/oauth/authorize"
    
    def generate_pkce_pair(self):
        """
        生成 PKCE (Proof Key for Code Exchange) 参数对
        
        Returns:
            tuple: (code_verifier, code_challenge)
        """
        # 生成随机的 code_verifier
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8')
        code_verifier = code_verifier.rstrip('=')  # 移除填充字符
        
        # 生成 code_challenge
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8')
        code_challenge = code_challenge.rstrip('=')  # 移除填充字符
        
        return code_verifier, code_challenge
    
    def get_authorization_url(self, scope="read", state=None, pkce_enabled=False):
        """
        生成授权 URL（授权码流程第一步）
        
        Args:
            scope (str): 请求的权限范围
            state (str): 状态参数（推荐用于安全）
            pkce_enabled (bool): 是否启用 PKCE
            
        Returns:
            str: 授权 URL
        """
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": scope
        }
        
        # 添加状态参数（如果提供）
        if state:
            params["state"] = state
        
        # 如果启用 PKCE，添加相关参数
        if pkce_enabled:
            code_verifier, code_challenge = self.generate_pkce_pair()
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"
            # 在实际应用中，需要保存 code_verifier 用于后续步骤
            print(f"PKCE Code Verifier (save securely): {code_verifier}")
        
        # 构建授权 URL
        auth_url = f"{self.authorization_endpoint}?{urlencode(params)}"
        return auth_url
    
    def exchange_code_for_token(self, authorization_code, code_verifier=None):
        """
        使用授权码交换访问令牌（授权码流程第二步）
        
        Args:
            authorization_code (str): 授权服务器返回的授权码
            code_verifier (str): PKCE code_verifier（如果使用了 PKCE）
            
        Returns:
            dict: 包含令牌信息的字典
        """
        # 准备请求参数
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": authorization_code,
            "redirect_uri": self.redirect_uri
        }
        
        # 如果使用了 PKCE，添加 code_verifier
        if code_verifier:
            data["code_verifier"] = code_verifier
        
        # 发送请求到令牌端点
        response = requests.post(self.token_endpoint, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to exchange code for token: {response.text}")
    
    def refresh_access_token(self, refresh_token):
        """
        使用刷新令牌获取新的访问令牌
        
        Args:
            refresh_token (str): 刷新令牌
            
        Returns:
            dict: 包含新令牌信息的字典
        """
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token
        }
        
        response = requests.post(self.token_endpoint, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to refresh token: {response.text}")
    
    def client_credentials_flow(self, scope="read"):
        """
        客户端凭据流程（适用于机器到机器通信）
        
        Args:
            scope (str): 请求的权限范围
            
        Returns:
            dict: 包含令牌信息的字典
        """
        # 准备基本认证头部
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "client_credentials",
            "scope": scope
        }
        
        response = requests.post(self.token_endpoint, headers=headers, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get token via client credentials: {response.text}")
    
    def resource_owner_password_flow(self, username, password, scope="read"):
        """
        资源所有者密码凭据流程（不推荐，仅用于演示）
        
        Args:
            username (str): 用户名
            password (str): 密码
            scope (str): 请求的权限范围
            
        Returns:
            dict: 包含令牌信息的字典
        """
        # 准备基本认证头部
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "password",
            "username": username,
            "password": password,
            "scope": scope
        }
        
        response = requests.post(self.token_endpoint, headers=headers, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get token via password flow: {response.text}")

# 创建 OAuth 2.0 客户端实例
oauth_client = OAuth2Client(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, AUTHORIZATION_SERVER_URL)

@app.route('/')
def home():
    """
    主页路由，提供 OAuth 2.0 流程演示选项
    
    Returns:
        HTML: 包含各种 OAuth 2.0 流程链接的页面
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>OAuth 2.0 Client Demo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            h1 { color: #333; }
            .flow-section { margin: 30px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
            .btn { display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }
            .btn:hover { background-color: #0056b3; }
            pre { background-color: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>OAuth 2.0 Client Demo</h1>
            <p>This demo shows various OAuth 2.0 flows:</p>
            
            <div class="flow-section">
                <h2>1. Authorization Code Flow</h2>
                <p>The most secure flow for web applications.</p>
                <a href="/auth-code" class="btn">Start Authorization Code Flow</a>
            </div>
            
            <div class="flow-section">
                <h2>2. Client Credentials Flow</h2>
                <p>Used for machine-to-machine communication.</p>
                <a href="/client-credentials" class="btn">Get Token via Client Credentials</a>
            </div>
            
            <div class="flow-section">
                <h2>3. Resource Owner Password Flow</h2>
                <p><strong>Note:</strong> This flow is deprecated and not recommended.</p>
                <form action="/password-flow" method="post">
                    <input type="text" name="username" placeholder="Username" required>
                    <input type="password" name="password" placeholder="Password" required>
                    <button type="submit" class="btn">Get Token via Password Flow</button>
                </form>
            </div>
            
            <div class="flow-section">
                <h2>Current Tokens</h2>
                <pre id="tokens-display">No tokens acquired yet</pre>
            </div>
        </div>
        
        <script>
            // 更新令牌显示
            function updateTokensDisplay(tokens) {
                const display = document.getElementById('tokens-display');
                if (tokens) {
                    display.textContent = JSON.stringify(tokens, null, 2);
                } else {
                    display.textContent = 'No tokens acquired yet';
                }
            }
            
            // 页面加载时尝试获取当前令牌状态
            window.onload = function() {
                fetch('/current-tokens')
                    .then(response => response.json())
                    .then(data => updateTokensDisplay(data.tokens));
            }
        </script>
    </body>
    </html>
    """
    return html_content

@app.route('/auth-code')
def auth_code_flow():
    """
    启动授权码流程
    
    Returns:
        Redirect: 重定向到授权服务器
    """
    # 生成状态参数用于安全检查
    state = secrets.token_urlsafe(16)
    
    # 生成授权 URL（启用 PKCE 增强安全性）
    auth_url = oauth_client.get_authorization_url(
        scope="read write", 
        state=state, 
        pkce_enabled=True
    )
    
    print(f"Authorization URL: {auth_url}")
    print(f"State parameter: {state}")
    
    # 在实际应用中，应该将 state 保存在会话中进行验证
    # 这里为了演示简便，直接输出到控制台
    
    # 重定向用户到授权服务器
    return redirect(auth_url)

@app.route('/callback')
def callback():
    """
    授权服务器回调处理
    
    Returns:
        HTML: 显示授权结果的页面
    """
    # 获取授权码和状态参数
    authorization_code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')
    
    # 检查是否有错误
    if error:
        return f"<h1>Authorization Error</h1><p>Error: {error}</p>", 400
    
    # 检查授权码是否存在
    if not authorization_code:
        return "<h1>Authorization Failed</h1><p>No authorization code received</p>", 400
    
    try:
        # 交换授权码获取访问令牌
        # 注意：在实际应用中，需要提供之前生成的 code_verifier
        tokens = oauth_client.exchange_code_for_token(authorization_code)
        
        # 保存令牌（实际应用中应安全存储）
        global access_token, refresh_token
        access_token = tokens.get('access_token')
        refresh_token = tokens.get('refresh_token')
        
        # 显示成功消息
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authorization Successful</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .success {{ color: green; }}
                pre {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1 class="success">Authorization Successful!</h1>
            <p>You have successfully authorized the application.</p>
            <h2>Tokens Received:</h2>
            <pre>{json.dumps(tokens, indent=2)}</pre>
            <p><a href="/">Back to Home</a></p>
        </body>
        </html>
        """
        return html_content
        
    except Exception as e:
        return f"<h1>Token Exchange Failed</h1><p>Error: {str(e)}</p>", 500

@app.route('/client-credentials')
def client_credentials():
    """
    客户端凭据流程演示
    
    Returns:
        JSON: 包含令牌信息的响应
    """
    try:
        # 获取客户端凭据令牌
        tokens = oauth_client.client_credentials_flow(scope="read write")
        
        # 保存令牌
        global access_token, refresh_token
        access_token = tokens.get('access_token')
        refresh_token = tokens.get('refresh_token')
        
        return jsonify({
            "message": "Successfully obtained tokens via client credentials flow",
            "tokens": tokens
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/password-flow', methods=['POST'])
def password_flow():
    """
    资源所有者密码凭据流程演示
    
    Returns:
        JSON: 包含令牌信息的响应
    """
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    try:
        # 获取令牌
        tokens = oauth_client.resource_owner_password_flow(
            username=username, 
            password=password, 
            scope="read"
        )
        
        # 保存令牌
        global access_token, refresh_token
        access_token = tokens.get('access_token')
        refresh_token = tokens.get('refresh_token')
        
        return jsonify({
            "message": "Successfully obtained tokens via password flow",
            "tokens": tokens
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/current-tokens')
def current_tokens():
    """
    获取当前存储的令牌
    
    Returns:
        JSON: 包含当前令牌信息的响应
    """
    tokens = {}
    if access_token:
        tokens['access_token'] = access_token
    if refresh_token:
        tokens['refresh_token'] = refresh_token
    
    return jsonify({"tokens": tokens})

@app.route('/refresh-token')
def refresh_token_endpoint():
    """
    刷新访问令牌
    
    Returns:
        JSON: 包含新令牌信息的响应
    """
    global refresh_token
    
    if not refresh_token:
        return jsonify({"error": "No refresh token available"}), 400
    
    try:
        # 刷新令牌
        new_tokens = oauth_client.refresh_access_token(refresh_token)
        
        # 更新存储的令牌
        global access_token
        access_token = new_tokens.get('access_token')
        # 如果返回了新的刷新令牌，则更新它
        if 'refresh_token' in new_tokens:
            refresh_token = new_tokens['refresh_token']
        
        return jsonify({
            "message": "Token refreshed successfully",
            "tokens": new_tokens
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 模拟资源服务器端点（用于测试访问令牌）
@app.route('/api/resource')
def protected_resource():
    """
    受保护的资源端点（模拟）
    
    Returns:
        JSON: 受保护的资源数据
    """
    # 在实际应用中，这里会验证访问令牌
    # 由于这是一个演示客户端，我们只是模拟这个过程
    
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401
    
    token = auth_header[7:]  # 移除 "Bearer " 前缀
    
    # 模拟令牌验证
    if token == access_token:
        return jsonify({
            "message": "Protected resource accessed successfully",
            "data": {
                "resource_id": "res_12345",
                "content": "This is sensitive data that requires authentication",
                "timestamp": "2023-01-01T00:00:00Z"
            }
        })
    else:
        return jsonify({"error": "Invalid access token"}), 401

if __name__ == '__main__':
    print("Starting OAuth 2.0 Client Demo...")
    print("Server running on http://localhost:5003")
    print("\nOpen your browser and navigate to http://localhost:5003 to start the demo")
    print("\nNote: This demo simulates OAuth 2.0 flows.")
    print("In a real implementation, you would need an actual OAuth 2.0 authorization server.")
    
    app.run(debug=True, port=5003)