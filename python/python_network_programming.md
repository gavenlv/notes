# Python网络编程高级指南

## 1. 高级Socket编程与自定义协议

### 1.1 非阻塞Socket与多路复用

```python
import socket
import select
import queue
import struct
import json
import time
import threading
from typing import Dict, List, Tuple, Optional, Callable

class NonBlockingServer:
    """非阻塞Socket服务器，使用select实现多路复用"""
    
    def __init__(self, host='127.0.0.1', port=9000):
        self.host = host
        self.port = port
        self.server_socket = None
        self.inputs = []  # 监控可读的socket
        self.outputs = []  # 监控可写的socket
        self.message_queues = {}  # 客户端消息队列
        self.client_data = {}  # 存储客户端数据
        self.running = False
        self.handlers = {}  # 消息处理器
    
    def start(self):
        """启动服务器"""
        # 创建服务器socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.setblocking(False)  # 设置为非阻塞
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        # 添加到监控列表
        self.inputs = [self.server_socket]
        self.running = True
        
        print(f"非阻塞服务器启动: {self.host}:{self.port}")
        
        try:
            self.serve()
        except KeyboardInterrupt:
            print("服务器停止")
        finally:
            self.server_socket.close()
    
    def serve(self):
        """主服务循环"""
        while self.inputs and self.running:
            # 使用select监控socket状态
            readable, writable, exceptional = select.select(
                self.inputs, self.outputs, self.inputs, 1.0
            )
            
            # 处理可读socket
            for s in readable:
                if s is self.server_socket:
                    # 新连接
                    self.accept_connection()
                else:
                    # 客户端数据
                    self.read_client_data(s)
            
            # 处理可写socket
            for s in writable:
                self.send_pending_data(s)
            
            # 处理异常socket
            for s in exceptional:
                self.handle_exception(s)
    
    def accept_connection(self):
        """接受新连接"""
        try:
            connection, client_address = self.server_socket.accept()
            print(f"新连接: {client_address}")
            
            connection.setblocking(False)  # 设置为非阻塞
            
            # 添加到监控列表
            self.inputs.append(connection)
            
            # 为客户端创建消息队列
            self.message_queues[connection] = queue.Queue()
            self.client_data[connection] = {'addr': client_address, 'buffer': b''}
            
        except BlockingIOError:
            # 没有连接可接受
            pass
    
    def read_client_data(self, sock):
        """读取客户端数据"""
        try:
            data = sock.recv(1024)
            if data:
                print(f"收到数据: {len(data)} 字节")
                
                # 解析消息
                self.parse_message(sock, data)
            else:
                # 连接关闭
                self.close_connection(sock)
                
        except ConnectionResetError:
            self.close_connection(sock)
        except BlockingIOError:
            # 没有数据可读
            pass
    
    def parse_message(self, sock, data):
        """解析消息（假设消息格式：长度(4字节) + JSON）"""
        client_data = self.client_data[sock]
        client_data['buffer'] += data
        
        buffer = client_data['buffer']
        
        # 尝试解析完整消息
        while len(buffer) >= 4:
            # 获取消息长度
            length = struct.unpack('!I', buffer[:4])[0]
            
            # 检查是否有完整消息
            if len(buffer) >= 4 + length:
                # 提取消息内容
                message_data = buffer[4:4+length]
                buffer = buffer[4+length:]
                
                # 解析JSON
                try:
                    message = json.loads(message_data.decode('utf-8'))
                    self.handle_message(sock, message)
                except json.JSONDecodeError:
                    print("无效的JSON消息")
                
                # 更新缓冲区
                client_data['buffer'] = buffer
            else:
                # 消息不完整，等待更多数据
                break
    
    def handle_message(self, sock, message):
        """处理客户端消息"""
        msg_type = message.get('type')
        handler = self.handlers.get(msg_type)
        
        if handler:
            try:
                response = handler(sock, message)
                if response:
                    self.queue_message(sock, response)
            except Exception as e:
                print(f"处理消息 {msg_type} 时出错: {e}")
                self.queue_message(sock, {'type': 'error', 'message': str(e)})
    
    def queue_message(self, sock, message):
        """将消息加入发送队列"""
        if sock in self.message_queues:
            # 序列化消息
            message_str = json.dumps(message)
            message_bytes = message_str.encode('utf-8')
            
            # 添加长度前缀
            length_data = struct.pack('!I', len(message_bytes))
            
            # 添加到队列
            self.message_queues[sock].put(length_data + message_bytes)
            
            # 如果socket不在输出列表中，添加进去
            if sock not in self.outputs:
                self.outputs.append(sock)
    
    def send_pending_data(self, sock):
        """发送待发送的数据"""
        try:
            next_msg = self.message_queues[sock].get_nowait()
        except queue.Empty:
            # 没有待发送数据，从输出列表中移除
            self.outputs.remove(sock)
        else:
            try:
                sock.sendall(next_msg)
            except ConnectionResetError:
                self.close_connection(sock)
    
    def handle_exception(self, sock):
        """处理异常socket"""
        print(f"处理异常socket")
        self.close_connection(sock)
    
    def close_connection(self, sock):
        """关闭连接"""
        if sock in self.outputs:
            self.outputs.remove(sock)
        if sock in self.inputs:
            self.inputs.remove(sock)
        
        sock.close()
        
        # 清理客户端数据
        if sock in self.message_queues:
            del self.message_queues[sock]
        
        if sock in self.client_data:
            addr = self.client_data[sock]['addr']
            del self.client_data[sock]
            print(f"连接关闭: {addr}")
    
    def register_handler(self, message_type: str, handler: Callable):
        """注册消息处理器"""
        self.handlers[message_type] = handler
        print(f"注册处理器: {message_type}")

# 自定义协议实现示例
class CustomProtocolServer(NonBlockingServer):
    """实现自定义协议的服务器"""
    
    def __init__(self, host='127.0.0.1', port=9000):
        super().__init__(host, port)
        self.rooms = {}  # 聊天室
        self.clients = {}  # 客户端信息
    
    def register_handlers(self):
        """注册消息处理器"""
        self.register_handler('join', self.handle_join)
        self.register_handler('message', self.handle_message)
        self.register_handler('leave', self.handle_leave)
        self.register_handler('list_rooms', self.handle_list_rooms)
        self.register_handler('create_room', self.handle_create_room)
    
    def handle_join(self, sock, message):
        """处理加入聊天室"""
        room = message.get('room', 'default')
        username = message.get('username', f'user_{id(sock)}')
        
        if room not in self.rooms:
            self.rooms[room] = []
        
        self.clients[sock] = {'username': username, 'room': room}
        self.rooms[room].append(sock)
        
        # 通知客户端
        response = {
            'type': 'join_response',
            'success': True,
            'room': room,
            'users': [self.clients[s]['username'] for s in self.rooms[room] if s in self.clients]
        }
        self.queue_message(sock, response)
        
        # 广播用户加入
        broadcast = {
            'type': 'user_joined',
            'username': username
        }
        self.broadcast_to_room(room, broadcast, exclude=sock)
    
    def handle_message(self, sock, message):
        """处理聊天消息"""
        if sock not in self.clients:
            return
        
        client = self.clients[sock]
        room = client['room']
        username = client['username']
        text = message.get('text', '')
        
        # 广播消息
        broadcast = {
            'type': 'message',
            'username': username,
            'text': text,
            'timestamp': time.time()
        }
        self.broadcast_to_room(room, broadcast)
    
    def handle_leave(self, sock, message):
        """处理离开聊天室"""
        if sock not in self.clients:
            return
        
        client = self.clients[sock]
        room = client['room']
        username = client['username']
        
        # 从聊天室移除
        if room in self.rooms and sock in self.rooms[room]:
            self.rooms[room].remove(sock)
        
        # 通知其他用户
        broadcast = {
            'type': 'user_left',
            'username': username
        }
        self.broadcast_to_room(room, broadcast, exclude=sock)
        
        # 清理客户端信息
        del self.clients[sock]
    
    def handle_list_rooms(self, sock, message):
        """处理获取聊天室列表"""
        rooms_info = [
            {'name': name, 'users': len(self.rooms[name])} 
            for name in self.rooms
        ]
        
        response = {
            'type': 'rooms_list',
            'rooms': rooms_info
        }
        self.queue_message(sock, response)
    
    def handle_create_room(self, sock, message):
        """处理创建聊天室"""
        room_name = message.get('room_name', '')
        
        if room_name and room_name not in self.rooms:
            self.rooms[room_name] = []
            
            response = {
                'type': 'create_room_response',
                'success': True,
                'room': room_name
            }
            self.queue_message(sock, response)
        else:
            response = {
                'type': 'create_room_response',
                'success': False,
                'message': '聊天室名称无效或已存在'
            }
            self.queue_message(sock, response)
    
    def broadcast_to_room(self, room, message, exclude=None):
        """向聊天室广播消息"""
        if room in self.rooms:
            for sock in self.rooms[room]:
                if sock != exclude:
                    self.queue_message(sock, message)

# 客户端实现
class CustomProtocolClient:
    """自定义协议客户端"""
    
    def __init__(self, host='127.0.0.1', port=9000):
        self.host = host
        self.port = port
        self.socket = None
        self.message_handlers = {}
        self.connected = False
        self.response_handlers = {}  # 用于处理响应
        self.message_id = 0
    
    def connect(self):
        """连接到服务器"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            
            # 启动接收线程
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
            print(f"连接到服务器 {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        self.connected = False
        if self.socket:
            self.socket.close()
            self.socket = None
        print("已断开连接")
    
    def send_message(self, message, expect_response=True):
        """发送消息到服务器"""
        if not self.connected:
            return False
        
        # 添加消息ID
        if expect_response:
            self.message_id += 1
            message['id'] = self.message_id
            
            # 创建等待响应的事件
            response_event = threading.Event()
            response_data = {}
            self.response_handlers[self.message_id] = (response_event, response_data)
        
        # 序列化消息
        message_str = json.dumps(message)
        message_bytes = message_str.encode('utf-8')
        length_data = struct.pack('!I', len(message_bytes))
        
        # 发送消息
        try:
            self.socket.sendall(length_data + message_bytes)
            
            if expect_response:
                # 等待响应
                if response_event.wait(timeout=10.0):
                    return response_data
                else:
                    print(f"消息 {message['id']} 超时")
                    if message['id'] in self.response_handlers:
                        del self.response_handlers[message['id']]
                    return None
            return True
        except Exception as e:
            print(f"发送消息失败: {e}")
            return False
    
    def receive_messages(self):
        """接收消息的线程"""
        buffer = b''
        
        while self.connected and self.socket:
            try:
                # 接收数据
                data = self.socket.recv(4096)
                if not data:
                    break
                
                buffer += data
                
                # 解析消息
                while len(buffer) >= 4:
                    # 获取消息长度
                    length = struct.unpack('!I', buffer[:4])[0]
                    
                    # 检查是否有完整消息
                    if len(buffer) >= 4 + length:
                        # 提取消息
                        message_data = buffer[4:4+length]
                        buffer = buffer[4+length:]
                        
                        # 解析JSON
                        try:
                            message = json.loads(message_data.decode('utf-8'))
                            self.handle_server_message(message)
                        except json.JSONDecodeError:
                            print("无效的JSON消息")
                    else:
                        # 消息不完整，等待更多数据
                        break
            except Exception as e:
                print(f"接收消息时出错: {e}")
                break
        
        # 通知连接断开
        self.connected = False
    
    def handle_server_message(self, message):
        """处理服务器消息"""
        msg_id = message.get('id')
        
        # 处理响应
        if msg_id and msg_id in self.response_handlers:
            response_event, response_data = self.response_handlers.pop(msg_id)
            response_data.update(message)
            response_event.set()
            return
        
        # 处理服务器推送的消息
        msg_type = message.get('type')
        handler = self.message_handlers.get(msg_type)
        
        if handler:
            handler(message)
        else:
            print(f"未处理的消息类型: {msg_type}, 内容: {message}")
    
    def register_handler(self, message_type: str, handler: Callable):
        """注册消息处理器"""
        self.message_handlers[message_type] = handler
    
    # 便捷方法
    def join_room(self, room, username):
        """加入聊天室"""
        return self.send_message({
            'type': 'join',
            'room': room,
            'username': username
        })
    
    def send_chat_message(self, text):
        """发送聊天消息"""
        return self.send_message({
            'type': 'message',
            'text': text
        }, expect_response=False)
    
    def leave_room(self):
        """离开聊天室"""
        return self.send_message({
            'type': 'leave'
        })
    
    def list_rooms(self):
        """获取聊天室列表"""
        return self.send_message({
            'type': 'list_rooms'
        })
    
    def create_room(self, room_name):
        """创建聊天室"""
        return self.send_message({
            'type': 'create_room',
            'room_name': room_name
        })

# 演示自定义协议
def demo_custom_protocol():
    """演示自定义协议服务器和客户端"""
    print("=== 自定义协议演示 ===")
    
    # 启动服务器（在实际使用中，这会在单独线程中运行）
    # server = CustomProtocolServer()
    # server.register_handlers()
    # server_thread = threading.Thread(target=server.start)
    # server_thread.daemon = True
    # server_thread.start()
    #
    # time.sleep(1)  # 等待服务器启动
    #
    # # 创建客户端
    # client = CustomProtocolClient()
    # if client.connect():
    #     # 注册消息处理器
    #     def handle_message(message):
    #         username = message.get('username', 'Unknown')
    #         text = message.get('text', '')
    #         print(f"[消息] {username}: {text}")
    #
    #     def handle_user_joined(message):
    #         username = message.get('username', 'Unknown')
    #         print(f"{username} 加入了聊天室")
    #
    #     def handle_user_left(message):
    #         username = message.get('username', 'Unknown')
    #         print(f"{username} 离开了聊天室")
    #
    #     def handle_join_response(message):
    #         if message.get('success'):
    #             room = message.get('room')
    #             users = message.get('users', [])
    #             print(f"成功加入聊天室 '{room}'，当前用户: {', '.join(users)}")
    #         else:
    #             print("加入聊天室失败")
    #
    #     client.register_handler('message', handle_message)
    #     client.register_handler('user_joined', handle_user_joined)
    #     client.register_handler('user_left', handle_user_left)
    #     client.register_handler('join_response', handle_join_response)
    #
    #     # 交互式聊天
    #     try:
    #         # 加入聊天室
    #         client.join_room("general", "Alice")
    #         time.sleep(0.5)
    #
    #         # 发送消息
    #         client.send_chat_message("大家好！")
    #         time.sleep(0.5)
    #
    #         # 列出聊天室
    #         rooms = client.list_rooms()
    #         if rooms:
    #             print("聊天室列表:", rooms)
    #             rooms_list = rooms.get('rooms', [])
    #             for room in rooms_list:
    #                 print(f"  {room['name']}: {room['users']} 位用户")
    #
    #         # 保持连接一段时间
    #         time.sleep(5)
    #     finally:
    #         client.leave_room()
    #         client.disconnect()

demo_custom_protocol()
```

### 1.2 SSL/TLS安全通信

```python
import ssl
import socket
import os
import time
from typing import Optional, Callable, Dict

# 生成自签名证书的辅助函数（仅用于演示）
def generate_self_signed_cert():
    """
    生成自签名证书（仅用于演示，实际生产环境应使用正式CA签发的证书）
    
    实际使用中应该:
    1. 使用openssl命令生成证书:
       openssl req -new -x509 -days 365 -nodes -out cert.pem -keyout key.pem
    
    2. 或使用Python的cryptography库生成证书
    """
    cert_file = "server.crt"
    key_file = "server.key"
    
    # 检查证书文件是否存在
    if not os.path.exists(cert_file) or not os.path.exists(key_file):
        print(f"请生成证书文件 {cert_file} 和 {key_file}")
        print("可以使用以下命令:")
        print("openssl req -new -x509 -days 365 -nodes -out server.crt -keyout server.key")
        return False
    
    return True

# SSL服务器
class SSLServer:
    """SSL/TLS服务器"""
    
    def __init__(self, host='127.0.0.1', port=8443, cert_file='server.crt', key_file='server.key'):
        self.host = host
        self.port = port
        self.cert_file = cert_file
        self.key_file = key_file
        self.context = None
        self.socket = None
        self.running = False
        self.clients = {}
    
    def create_ssl_context(self):
        """创建SSL上下文"""
        # 创建SSL上下文
        self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        
        # 加载证书和私钥
        try:
            self.context.load_cert_chain(certfile=self.cert_file, keyfile=self.key_file)
            print("证书和私钥加载成功")
            
            # 可选：配置更严格的SSL设置
            self.context.minimum_version = ssl.TLSVersion.TLSv1_2
            self.context.set_ciphers('ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384')
            
            return True
        except Exception as e:
            print(f"加载证书失败: {e}")
            return False
    
    def start(self):
        """启动SSL服务器"""
        if not self.create_ssl_context():
            print("无法创建SSL上下文，退出")
            return
        
        # 创建TCP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        
        self.running = True
        print(f"SSL服务器启动: https://{self.host}:{self.port}")
        
        try:
            self.serve()
        except KeyboardInterrupt:
            print("服务器停止")
        finally:
            self.socket.close()
    
    def serve(self):
        """主服务循环"""
        while self.running:
            try:
                # 接受连接
                client_socket, client_address = self.socket.accept()
                
                # 包装为SSL连接
                try:
                    ssl_socket = self.context.wrap_socket(
                        client_socket, 
                        server_side=True
                    )
                    
                    print(f"SSL连接建立: {client_address}")
                    print(f"SSL版本: {ssl_socket.version()}")
                    print(f"加密套件: {ssl_socket.cipher()}")
                    
                    # 处理客户端连接
                    self.handle_client(ssl_socket, client_address)
                    
                except ssl.SSLError as e:
                    print(f"SSL握手失败: {e}")
                    client_socket.close()
                    
            except Exception as e:
                print(f"接受连接时出错: {e}")
    
    def handle_client(self, ssl_socket, client_address):
        """处理客户端连接"""
        try:
            # 发送欢迎消息
            welcome = "欢迎连接到SSL服务器!\n"
            ssl_socket.send(welcome.encode('utf-8'))
            
            # 简单的回显服务
            while self.running:
                data = ssl_socket.recv(1024)
                if not data:
                    break
                
                print(f"收到数据: {data.decode('utf-8')}")
                
                # 回显数据
                ssl_socket.send(data)
            
        except ssl.SSLError as e:
            print(f"SSL通信错误: {e}")
        finally:
            ssl_socket.close()
            print(f"连接关闭: {client_address}")

# SSL客户端
class SSLClient:
    """SSL/TLS客户端"""
    
    def __init__(self, host='127.0.0.1', port=8443):
        self.host = host
        self.port = port
        self.context = None
        self.socket = None
    
    def create_ssl_context(self, verify_cert=True, ca_file=None):
        """创建SSL上下文"""
        # 创建SSL上下文
        self.context = ssl.create_default_context()
        
        if not verify_cert:
            # 禁用证书验证（仅用于测试）
            self.context.check_hostname = False
            self.context.verify_mode = ssl.CERT_NONE
            print("警告: 证书验证已禁用")
        elif ca_file:
            # 加载自定义CA证书
            self.context.load_verify_locations(cafile=ca_file)
        
        return True
    
    def connect(self):
        """连接到SSL服务器"""
        if not self.create_ssl_context():
            return False
        
        try:
            # 创建TCP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # 包装为SSL连接
            self.socket = self.context.wrap_socket(
                sock, 
                server_hostname=self.host,
                do_handshake_on_connect=True
            )
            
            # 连接服务器
            self.socket.connect((self.host, self.port))
            
            print(f"SSL连接建立: {self.host}:{self.port}")
            print(f"SSL版本: {self.socket.version()}")
            print(f"加密套件: {self.socket.cipher()}")
            print(f"服务器证书: {self.socket.getpeercert()}")
            
            return True
            
        except Exception as e:
            print(f"连接失败: {e}")
            return False
    
    def send_message(self, message):
        """发送消息"""
        if not self.socket:
            return False
        
        try:
            self.socket.send(message.encode('utf-8'))
            
            # 接收响应
            response = self.socket.recv(1024)
            print(f"服务器响应: {response.decode('utf-8')}")
            return True
        except Exception as e:
            print(f"发送消息失败: {e}")
            return False
    
    def close(self):
        """关闭连接"""
        if self.socket:
            self.socket.close()
            self.socket = None
            print("连接已关闭")

# 演示SSL通信
def demo_ssl_communication():
    """演示SSL安全通信"""
    
    # 首先检查证书文件
    if not generate_self_signed_cert():
        print("SSL演示需要证书文件，跳过此演示")
        return
    
    print("=== SSL/TLS安全通信演示 ===")
    
    # 在实际使用中，这会在不同线程中运行
    # server_thread = threading.Thread(target=lambda: SSLServer().start())
    # server_thread.daemon = True
    # server_thread.start()
    #
    # time.sleep(1)  # 等待服务器启动
    #
    # # 创建客户端
    # client = SSLClient()
    # if client.connect():
    #     try:
    #         # 发送测试消息
    #         client.send_message("Hello, SSL Server!")
    #         time.sleep(1)
    #         client.send_message("这是一个安全通信测试")
    #         time.sleep(1)
    #     finally:
    #         client.close()

# HTTPS服务器实现
class HTTPSServer:
    """简单HTTPS服务器"""
    
    def __init__(self, host='127.0.0.1', port=8443, cert_file='server.crt', key_file='server.key'):
        self.host = host
        self.port = port
        self.cert_file = cert_file
        self.key_file = key_file
        self.context = None
        self.socket = None
        self.running = False
        self.routes = {}
    
    def create_ssl_context(self):
        """创建SSL上下文"""
        self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        try:
            self.context.load_cert_chain(certfile=self.cert_file, keyfile=self.key_file)
            return True
        except Exception as e:
            print(f"加载证书失败: {e}")
            return False
    
    def route(self, path):
        """装饰器：注册路由"""
        def decorator(handler):
            self.routes[path] = handler
            return handler
        return decorator
    
    def start(self):
        """启动HTTPS服务器"""
        if not self.create_ssl_context():
            return
        
        # 创建TCP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        
        self.running = True
        print(f"HTTPS服务器启动: https://{self.host}:{self.port}")
        
        try:
            self.serve()
        except KeyboardInterrupt:
            print("服务器停止")
        finally:
            self.socket.close()
    
    def serve(self):
        """主服务循环"""
        while self.running:
            try:
                # 接受连接
                client_socket, client_address = self.socket.accept()
                
                # 包装为SSL连接
                try:
                    ssl_socket = self.context.wrap_socket(
                        client_socket, 
                        server_side=True
                    )
                    
                    print(f"HTTPS连接建立: {client_address}")
                    
                    # 处理请求
                    threading.Thread(
                        target=self.handle_request, 
                        args=(ssl_socket, client_address)
                    ).start()
                    
                except ssl.SSLError as e:
                    print(f"SSL握手失败: {e}")
                    client_socket.close()
                    
            except Exception as e:
                print(f"接受连接时出错: {e}")
    
    def handle_request(self, ssl_socket, client_address):
        """处理HTTP请求"""
        try:
            # 读取请求行
            request_line = ssl_socket.recv(1024).decode('utf-8').split('\n')[0]
            if not request_line:
                return
            
            # 解析请求
            parts = request_line.split(' ')
            if len(parts) < 2:
                return
            
            method, path = parts[0], parts[1]
            print(f"请求: {method} {path}")
            
            # 查找路由处理器
            handler = self.routes.get(path)
            if handler:
                response = handler(method, path)
            else:
                # 默认响应
                response = self.default_response(method, path)
            
            # 发送响应
            ssl_socket.send(response.encode('utf-8'))
            
        except Exception as e:
            print(f"处理请求时出错: {e}")
        finally:
            ssl_socket.close()
            print(f"连接关闭: {client_address}")
    
    def default_response(self, method, path):
        """默认响应"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>HTTPS服务器</title>
        </head>
        <body>
            <h1>欢迎访问HTTPS安全服务器</h1>
            <p>您的请求: {method} {path}</p>
            <p>这是一个加密连接</p>
            <ul>
                <li><a href="/secure">安全页面</a></li>
                <li><a href="/info">连接信息</a></li>
            </ul>
        </body>
        </html>
        """
        
        return f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(html)}\r\n\r\n{html}"

# 演示HTTPS服务器
def demo_https_server():
    """演示HTTPS服务器"""
    
    if not generate_self_signed_cert():
        print("HTTPS演示需要证书文件，跳过此演示")
        return
    
    print("=== HTTPS安全服务器演示 ===")
    
    # 在实际使用中:
    # server = HTTPSServer()
    #
    # @server.route("/secure")
    # def secure_page(method, path):
    #     html = """
    #     <!DOCTYPE html>
    #     <html>
    #     <head>
    #         <title>安全页面</title>
    #     </head>
    #     <body>
    #         <h1>这是一个安全页面</h1>
    #         <p>所有通信都通过SSL/TLS加密</p>
    #         <p>可以安全传输敏感信息</p>
    #     </body>
    #     </html>
    #     """
    #     return f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(html)}\r\n\r\n{html}"
    #
    # @server.route("/info")
    # def info_page(method, path):
    #     html = """
    #     <!DOCTYPE html>
    #     <html>
    #     <head>
    #         <title>连接信息</title>
    #     </head>
    #     <body>
    #         <h1>连接信息</h1>
    #         <p>这是一个加密连接，所有数据都通过SSL/TLS保护</p>
    #         <p>您的浏览器地址栏应该有一个锁图标</p>
    #     </body>
    #     </html>
    #     """
    #     return f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(html)}\r\n\r\n{html}"
    #
    # server.start()

demo_ssl_communication()
demo_https_server()
```

## 2. 高级HTTP服务器实现

### 2.1 基于asyncio的高性能HTTP服务器

```python
import asyncio
import ssl
import json
import os
import mimetypes
import urllib.parse
from typing import Dict, List, Optional, Tuple, Callable, Any
from datetime import datetime
import time

# HTTP状态码和描述
HTTP_STATUS_CODES = {
    100: "Continue",
    101: "Switching Protocols",
    200: "OK",
    201: "Created",
    202: "Accepted",
    203: "Non-Authoritative Information",
    204: "No Content",
    301: "Moved Permanently",
    302: "Found",
    303: "See Other",
    304: "Not Modified",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    408: "Request Timeout",
    500: "Internal Server Error",
    501: "Not Implemented",
    503: "Service Unavailable"
}

# HTTP响应类
class HTTPResponse:
    """HTTP响应对象"""
    
    def __init__(self, status_code=200, headers=None, body=b''):
        self.status_code = status_code
        self.headers = headers or {}
        self.body = body if isinstance(body, bytes) else str(body).encode('utf-8')
        
        # 设置默认头部
        if 'Content-Type' not in self.headers:
            self.headers['Content-Type'] = 'text/html; charset=utf-8'
        
        if 'Content-Length' not in self.headers:
            self.headers['Content-Length'] = str(len(self.body))
        
        if 'Date' not in self.headers:
            self.headers['Date'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        if 'Server' not in self.headers:
            self.headers['Server'] = 'AsyncHTTPServer/1.0'
    
    def to_bytes(self):
        """将响应转换为字节"""
        status_text = HTTP_STATUS_CODES.get(self.status_code, 'Unknown')
        status_line = f"HTTP/1.1 {self.status_code} {status_text}\r\n"
        
        headers_lines = []
        for name, value in self.headers.items():
            headers_lines.append(f"{name}: {value}")
        
        headers_str = "\r\n".join(headers_lines)
        
        return f"{status_line}{headers_str}\r\n\r\n".encode('utf-8') + self.body

# HTTP请求类
class HTTPRequest:
    """HTTP请求对象"""
    
    def __init__(self, method, path, headers=None, query_params=None, body=b''):
        self.method = method
        self.path = path
        self.headers = headers or {}
        self.query_params = query_params or {}
        self.body = body
        self._json = None
    
    @property
    def json(self):
        """获取JSON格式的请求体"""
        if self._json is None and self.body:
            try:
                self._json = json.loads(self.body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
        return self._json
    
    @property
    def form(self):
        """获取表单数据"""
        content_type = self.headers.get('Content-Type', '')
        if 'application/x-www-form-urlencoded' in content_type and self.body:
            try:
                form_data = self.body.decode('utf-8')
                return urllib.parse.parse_qs(form_data)
            except UnicodeDecodeError:
                pass
        return {}
    
    @property
    def cookies(self):
        """获取Cookie"""
        cookie_header = self.headers.get('Cookie', '')
        cookies = {}
        if cookie_header:
            for cookie in cookie_header.split(';'):
                if '=' in cookie:
                    name, value = cookie.strip().split('=', 1)
                    cookies[name] = value
        return cookies

# 高级异步HTTP服务器
class AsyncHTTPServer:
    """基于asyncio的高性能HTTP服务器"""
    
    def __init__(self, host='127.0.0.1', port=8000, ssl_context=None):
        self.host = host
        self.port = port
        self.ssl_context = ssl_context
        self.routes = {}  # 路由表 (method, path) -> handler
        self.middleware = []  # 中间件
        self.static_dirs = {}  # 静态文件目录
        self.running = False
        self.server = None
        self.session_store = {}  # 简单的会话存储
    
    def add_route(self, method, path, handler):
        """添加路由"""
        self.routes[(method.upper(), path)] = handler
        print(f"添加路由: {method} {path}")
    
    def route(self, path, methods=['GET']):
        """装饰器：注册路由"""
        def decorator(handler):
            for method in methods:
                self.add_route(method, path, handler)
            return handler
        return decorator
    
    def add_middleware(self, middleware):
        """添加中间件"""
        self.middleware.append(middleware)
    
    def add_static_dir(self, url_prefix, dir_path):
        """添加静态文件目录"""
        self.static_dirs[url_prefix] = dir_path
        print(f"添加静态目录: {url_prefix} -> {dir_path}")
    
    async def start(self):
        """启动服务器"""
        self.running = True
        
        # 创建服务器
        self.server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port,
            ssl=self.ssl_context
        )
        
        protocol = "HTTPS" if self.ssl_context else "HTTP"
        print(f"{protocol}服务器启动: {protocol.lower()}://{self.host}:{self.port}")
        
        async with self.server:
            await self.server.serve_forever()
    
    async def stop(self):
        """停止服务器"""
        self.running = False
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        print("服务器已停止")
    
    async def handle_client(self, reader, writer):
        """处理客户端连接"""
        try:
            # 读取请求
            request = await self.read_request(reader)
            if not request:
                return
            
            # 应用中间件
            for middleware in self.middleware:
                request = await middleware(request)
                if not request:  # 中间件可能中断请求处理
                    return
            
            # 处理请求
            response = await self.handle_request(request)
            
            # 发送响应
            writer.write(response.to_bytes())
            await writer.drain()
            
        except Exception as e:
            print(f"处理请求时出错: {e}")
            try:
                error_response = HTTPResponse(
                    status_code=500,
                    body=b'<h1>Internal Server Error</h1>'
                )
                writer.write(error_response.to_bytes())
                await writer.drain()
            except:
                pass
        finally:
            writer.close()
            await writer.wait_closed()
    
    async def read_request(self, reader):
        """读取HTTP请求"""
        try:
            # 读取请求行
            request_line = await reader.readline()
            if not request_line:
                return None
            
            # 解析请求行
            request_line = request_line.decode('utf-8').strip()
            parts = request_line.split(' ')
            if len(parts) < 2:
                return None
            
            method, path = parts[0], parts[1]
            
            # 解析查询参数
            parsed_path = urllib.parse.urlparse(path)
            query_params = urllib.parse.parse_qs(parsed_path.query)
            
            # 读取请求头
            headers = {}
            while True:
                header_line = await reader.readline()
                if not header_line or header_line == b'\r\n':
                    break
                
                header_line = header_line.decode('utf-8').strip()
                if ':' in header_line:
                    name, value = header_line.split(':', 1)
                    headers[name.strip().lower()] = value.strip()
            
            # 读取请求体
            content_length = int(headers.get('content-length', 0))
            body = b''
            if content_length > 0:
                body = await reader.readexactly(content_length)
            
            # 创建请求对象
            request = HTTPRequest(method, parsed_path.path, headers, query_params, body)
            return request
            
        except Exception as e:
            print(f"读取请求时出错: {e}")
            return None
    
    async def handle_request(self, request):
        """处理HTTP请求"""
        method = request.method
        path = request.path
        
        # 查找路由
        handler = self.routes.get((method, path))
        if not handler:
            # 尝试查找静态文件
            for url_prefix, dir_path in self.static_dirs.items():
                if path.startswith(url_prefix):
                    file_path = os.path.join(dir_path, path[len(url_prefix):])
                    return await self.serve_static_file(file_path)
            
            # 404响应
            return HTTPResponse(
                status_code=404,
                body=b'<h1>404 Not Found</h1>'
            )
        
        # 调用路由处理器
        try:
            if asyncio.iscoroutinefunction(handler):
                return await handler(request)
            else:
                return handler(request)
        except Exception as e:
            print(f"处理路由时出错: {e}")
            return HTTPResponse(
                status_code=500,
                body=b'<h1>Internal Server Error</h1>'
            )
    
    async def serve_static_file(self, file_path):
        """提供静态文件"""
        # 安全检查，防止路径遍历
        normalized_path = os.path.normpath(file_path)
        if normalized_path.startswith('..'):
            return HTTPResponse(
                status_code=403,
                body=b'<h1>Forbidden</h1>'
            )
        
        try:
            # 检查文件是否存在
            if not os.path.exists(normalized_path):
                return HTTPResponse(
                    status_code=404,
                    body=b'<h1>File Not Found</h1>'
                )
            
            # 检查是否为目录
            if os.path.isdir(normalized_path):
                # 尝试提供index.html
                index_path = os.path.join(normalized_path, 'index.html')
                if os.path.exists(index_path):
                    normalized_path = index_path
                else:
                    return HTTPResponse(
                        status_code=403,
                        body=b'<h1>Forbidden</h1>'
                    )
            
            # 读取文件
            with open(normalized_path, 'rb') as f:
                body = f.read()
            
            # 确定内容类型
            content_type, _ = mimetypes.guess_type(normalized_path)
            if content_type is None:
                content_type = 'application/octet-stream'
            
            # 构建响应
            headers = {
                'Content-Type': content_type,
                'Cache-Control': 'public, max-age=3600'  # 缓存1小时
            }
            
            return HTTPResponse(
                status_code=200,
                headers=headers,
                body=body
            )
            
        except Exception as e:
            print(f"提供静态文件时出错: {e}")
            return HTTPResponse(
                status_code=500,
                body=b'<h1>Internal Server Error</h1>'
            )

# WebSocket支持
class WebSocketFrame:
    """WebSocket帧"""
    
    OPCODE_CONTINUATION = 0x0
    OPCODE_TEXT = 0x1
    OPCODE_BINARY = 0x2
    OPCODE_CLOSE = 0x8
    OPCODE_PING = 0x9
    OPCODE_PONG = 0xa
    
    def __init__(self, opcode, payload=b'', fin=True):
        self.fin = fin
        self.opcode = opcode
        self.payload = payload
    
    @classmethod
    def parse(cls, data):
        """解析WebSocket帧"""
        if len(data) < 2:
            return None
        
        first_byte = data[0]
        second_byte = data[1]
        
        fin = bool(first_byte & 0x80)
        opcode = first_byte & 0x0f
        masked = bool(second_byte & 0x80)
        payload_length = second_byte & 0x7f
        
        offset = 2
        
        # 扩展载荷长度
        if payload_length == 126:
            if len(data) < offset + 2:
                return None
            payload_length = int.from_bytes(data[offset:offset+2], byteorder='big')
            offset += 2
        elif payload_length == 127:
            if len(data) < offset + 8:
                return None
            payload_length = int.from_bytes(data[offset:offset+8], byteorder='big')
            offset += 8
        
        # 掩码
        if masked:
            if len(data) < offset + 4:
                return None
            mask = data[offset:offset+4]
            offset += 4
        
        # 载荷
        if len(data) < offset + payload_length:
            return None
        
        payload = data[offset:offset+payload_length]
        
        # 解掩码
        if masked:
            payload = bytes([b ^ mask[i % 4] for i, b in enumerate(payload)])
        
        return cls(opcode, payload, fin)
    
    def serialize(self):
        """序列化WebSocket帧"""
        frame = bytearray()
        
        # 第一个字节
        first_byte = (0x80 if self.fin else 0x00) | (self.opcode & 0x0f)
        frame.append(first_byte)
        
        # 载荷长度
        payload_length = len(self.payload)
        if payload_length < 126:
            frame.append(payload_length)
        elif payload_length < 65536:
            frame.append(126)
            frame.extend(payload_length.to_bytes(2, byteorder='big'))
        else:
            frame.append(127)
            frame.extend(payload_length.to_bytes(8, byteorder='big'))
        
        # 载荷
        frame.extend(self.payload)
        
        return bytes(frame)

class WebSocketConnection:
    """WebSocket连接"""
    
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.closed = False
        self.send_queue = asyncio.Queue()
        self.receive_task = None
        self.send_task = None
    
    async def start(self):
        """启动WebSocket处理"""
        self.receive_task = asyncio.create_task(self._receive_loop())
        self.send_task = asyncio.create_task(self._send_loop())
    
    async def close(self, code=1000, reason=''):
        """关闭WebSocket连接"""
        if self.closed:
            return
        
        self.closed = True
        
        # 发送关闭帧
        close_frame = WebSocketFrame(
            WebSocketFrame.OPCODE_CLOSE,
            code.to_bytes(2, byteorder='big') + reason.encode('utf-8')
        )
        await self._send_frame(close_frame)
        
        # 停止任务
        if self.receive_task:
            self.receive_task.cancel()
            try:
                await self.receive_task
            except asyncio.CancelledError:
                pass
        
        if self.send_task:
            self.send_task.cancel()
            try:
                await self.send_task
            except asyncio.CancelledError:
                pass
        
        # 关闭连接
        self.writer.close()
        await self.writer.wait_closed()
    
    async def send_text(self, text):
        """发送文本消息"""
        if self.closed:
            return False
        
        frame = WebSocketFrame(
            WebSocketFrame.OPCODE_TEXT,
            text.encode('utf-8')
        )
        await self.send_queue.put(frame)
        return True
    
    async def send_binary(self, data):
        """发送二进制消息"""
        if self.closed:
            return False
        
        frame = WebSocketFrame(
            WebSocketFrame.OPCODE_BINARY,
            data
        )
        await self.send_queue.put(frame)
        return True
    
    async def _receive_loop(self):
        """接收循环"""
        try:
            while not self.closed:
                # 读取帧头
                header = await self.reader.read(2)
                if not header:
                    break
                
                # 读取剩余数据
                first_byte, second_byte = header[0], header[1]
                payload_length = second_byte & 0x7f
                
                if payload_length == 126:
                    length_bytes = await self.reader.read(2)
                    payload_length = int.from_bytes(length_bytes, byteorder='big')
                elif payload_length == 127:
                    length_bytes = await self.reader.read(8)
                    payload_length = int.from_bytes(length_bytes, byteorder='big')
                
                # 读取掩码
                masked = bool(second_byte & 0x80)
                if masked:
                    mask = await self.reader.read(4)
                
                # 读取载荷
                payload = await self.reader.read(payload_length)
                
                # 解掩码
                if masked:
                    payload = bytes([b ^ mask[i % 4] for i, b in enumerate(payload)])
                
                # 解析帧
                frame = WebSocketFrame(first_byte & 0x0f, payload, bool(first_byte & 0x80))
                
                # 处理帧
                await self._handle_frame(frame)
        
        except Exception as e:
            print(f"WebSocket接收错误: {e}")
        
        finally:
            if not self.closed:
                await self.close()
    
    async def _send_loop(self):
        """发送循环"""
        try:
            while not self.closed:
                frame = await self.send_queue.get()
                if frame:
                    await self._send_frame(frame)
        
        except Exception as e:
            print(f"WebSocket发送错误: {e}")
        
        finally:
            if not self.closed:
                await self.close()
    
    async def _send_frame(self, frame):
        """发送帧"""
        data = frame.serialize()
        self.writer.write(data)
        await self.writer.drain()
    
    async def _handle_frame(self, frame):
        """处理接收到的帧"""
        if frame.opcode == WebSocketFrame.OPCODE_TEXT:
            text = frame.payload.decode('utf-8')
            await self.on_message(text, "text")
        elif frame.opcode == WebSocketFrame.OPCODE_BINARY:
            await self.on_message(frame.payload, "binary")
        elif frame.opcode == WebSocketFrame.OPCODE_PING:
            # 响应ping
            pong_frame = WebSocketFrame(WebSocketFrame.OPCODE_PONG, frame.payload)
            await self._send_frame(pong_frame)
        elif frame.opcode == WebSocketFrame.OPCODE_CLOSE:
            await self.close()
    
    async def on_message(self, data, msg_type):
        """处理接收到的消息（子类应重写）"""
        pass

# 演示高级HTTP服务器
async def demo_advanced_http_server():
    """演示高级HTTP服务器"""
    
    # 创建SSL上下文（如果有证书）
    ssl_context = None
    if generate_self_signed_cert():
        try:
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(certfile='server.crt', keyfile='server.key')
        except:
            print("无法加载证书，使用HTTP而非HTTPS")
    
    # 创建服务器
    server = AsyncHTTPServer(host='127.0.0.1', port=8443 if ssl_context else 8000, ssl_context=ssl_context)
    
    # 添加日志中间件
    async def logging_middleware(request):
        start_time = time.time()
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {request.method} {request.path}")
        return request
    
    # 添加CORS中间件
    async def cors_middleware(request):
        # 这只是一个简单的CORS处理，实际应用中需要更复杂
        return request
    
    server.add_middleware(logging_middleware)
    server.add_middleware(cors_middleware)
    
    # 添加静态文件目录（如果存在）
    static_dir = "static"
    if os.path.exists(static_dir):
        server.add_static_dir("/static", static_dir)
    
    # 定义路由
    @server.route('/')
    async def home(request):
        """首页"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>高级HTTP服务器</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
                .method { font-weight: bold; color: #0077cc; }
            </style>
        </head>
        <body>
            <h1>欢迎访问高级HTTP服务器</h1>
            <p>这是一个基于asyncio实现的高性能HTTP服务器</p>
            
            <h2>API端点</h2>
            <div class="endpoint">
                <span class="method">GET</span> /hello?name=World - 问候API
            </div>
            <div class="endpoint">
                <span class="method">GET</span> /api/data - 获取JSON数据
            </div>
            <div class="endpoint">
                <span class="method">POST</span> /api/data - 创建数据
            </div>
            <div class="endpoint">
                <span class="method">GET</span> /ws - WebSocket连接点
            </div>
        </body>
        </html>
        """
        return HTTPResponse(body=html)
    
    @server.route('/hello')
    async def hello(request):
        """问候API"""
        name = request.query_params.get('name', ['World'])[0]
        message = f"Hello, {name}!"
        return HTTPResponse(
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'message': message}).encode('utf-8')
        )
    
    @server.route('/api/data', methods=['GET'])
    async def get_data(request):
        """获取数据API"""
        await asyncio.sleep(0.1)  # 模拟数据库查询
        
        data = {
            'items': [
                {'id': 1, 'name': 'Item 1', 'value': 100},
                {'id': 2, 'name': 'Item 2', 'value': 200},
                {'id': 3, 'name': 'Item 3', 'value': 300}
            ],
            'total': 3,
            'timestamp': time.time()
        }
        
        return HTTPResponse(
            headers={'Content-Type': 'application/json'},
            body=json.dumps(data).encode('utf-8')
        )
    
    @server.route('/api/data', methods=['POST'])
    async def create_data(request):
        """创建数据API"""
        data = request.json
        if not data or 'name' not in data:
            return HTTPResponse(
                status_code=400,
                headers={'Content-Type': 'application/json'},
                body=json.dumps({'error': 'Missing name field'}).encode('utf-8')
            )
        
        # 模拟数据库插入
        await asyncio.sleep(0.1)
        new_item = {
            'id': 4,
            'name': data['name'],
            'value': data.get('value', 0)
        }
        
        return HTTPResponse(
            status_code=201,
            headers={'Content-Type': 'application/json'},
            body=json.dumps(new_item).encode('utf-8')
        )
    
    # WebSocket连接点
    async def websocket_handler(reader, writer):
        """WebSocket处理函数"""
        try:
            # 读取HTTP请求头
            request_lines = []
            while True:
                line = await reader.readline()
                if not line or line == b'\r\n':
                    break
                request_lines.append(line.decode('utf-8').strip())
            
            # 提取Sec-WebSocket-Key
            ws_key = None
            for line in request_lines:
                if line.lower().startswith('sec-websocket-key:'):
                    ws_key = line.split(':', 1)[1].strip()
                    break
            
            if not ws_key:
                writer.close()
                return
            
            # 构建握手响应
            import base64
            import hashlib
            
            magic_string = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
            accept_key = base64.b64encode(
                hashlib.sha1((ws_key + magic_string).encode()).digest()
            ).decode('utf-8')
            
            response = (
                "HTTP/1.1 101 Switching Protocols\r\n"
                "Upgrade: websocket\r\n"
                "Connection: Upgrade\r\n"
                f"Sec-WebSocket-Accept: {accept_key}\r\n"
                "\r\n"
            )
            
            writer.write(response.encode('utf-8'))
            await writer.drain()
            
            # 创建WebSocket连接
            class ChatWebSocket(WebSocketConnection):
                def __init__(self, reader, writer):
                    super().__init__(reader, writer)
                    self.id = str(int(time.time()))
                
                async def on_message(self, data, msg_type):
                    if msg_type == "text":
                        message = json.loads(data)
                        message_type = message.get('type')
                        
                        if message_type == 'chat':
                            # 广播消息
                            chat_message = {
                                'type': 'chat',
                                'id': self.id,
                                'text': message.get('text', ''),
                                'timestamp': time.time()
                            }
                            
                            # 简单的广播实现（实际应用中应该使用连接池）
                            for conn_id, conn in websocket_connections.items():
                                if conn_id != self.id:
                                    await conn.send_text(json.dumps(chat_message))
                                    
                                    # 回发送给自己
                                    await self.send_text(json.dumps(chat_message))
            
            # 存储WebSocket连接
            if not hasattr(websocket_handler, 'connections'):
                websocket_handler.connections = {}
            
            websocket = ChatWebSocket(reader, writer)
            websocket_handler.connections[websocket.id] = websocket
            
            # 启动WebSocket处理
            await websocket.start()
            
        except Exception as e:
            print(f"WebSocket处理错误: {e}")
        finally:
            if 'websocket' in locals():
                websocket_handler.connections.pop(websocket.id, None)
                await websocket.close()
    
    # 添加WebSocket路由（这是一个简化的实现）
    async def websocket_route(request):
        """WebSocket路由"""
        # 这里只是一个占位符，实际的WebSocket处理在websocket_handler中
        return HTTPResponse(
            status_code=426,  # Upgrade Required
            headers={'Upgrade': 'websocket'},
            body=b'WebSocket required'
        )
    
    server.add_route('GET', '/ws', websocket_route)
    
    # 启动服务器
    protocol = "HTTPS" if ssl_context else "HTTP"
    print(f"启动{protocol}服务器演示...")
    
    # 在实际使用中:
    # try:
    #     await server.start()
    # except KeyboardInterrupt:
    #     await server.stop()
    #     print("服务器已停止")

asyncio.run(demo_advanced_http_server())
```

## 3. 网络协议处理与实现

### 3.1 实现自定义网络协议

```python
import struct
import asyncio
import json
import time
import uuid
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple

# 协议定义
class ProtocolCommand(Enum):
    """协议命令枚举"""
    # 基本命令
    PING = 0x01
    PONG = 0x02
    ECHO = 0x03
    
    # 认证命令
    AUTH_REQUEST = 0x10
    AUTH_RESPONSE = 0x11
    AUTH_CHALLENGE = 0x12
    
    # 数据命令
    DATA_REQUEST = 0x20
    DATA_RESPONSE = 0x21
    DATA_PUSH = 0x22
    
    # 控制命令
    ERROR = 0xF0
    DISCONNECT = 0xFF

class ProtocolMessage:
    """协议消息类"""
    
    # 消息头格式: 命令(1字节) + 标志(1字节) + 消息ID(4字节) + 长度(4字节)
    HEADER_FORMAT = '!BBII'
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
    
    def __init__(self, command: ProtocolCommand, payload: bytes = b'', flags: int = 0, msg_id: int = None):
        self.command = command
        self.payload = payload
        self.flags = flags
        self.msg_id = msg_id or uuid.uuid4().int & 0xFFFFFFFF
        self.timestamp = time.time()
    
    def serialize(self) -> bytes:
        """序列化消息"""
        # 构建消息头
        header = struct.pack(
            self.HEADER_FORMAT,
            self.command.value,
            self.flags,
            self.msg_id,
            len(self.payload)
        )
        
        # 返回头+载荷
        return header + self.payload
    
    @classmethod
    def deserialize(cls, data: bytes):
        """反序列化消息"""
        if len(data) < cls.HEADER_SIZE:
            return None
        
        # 解析消息头
        header = data[:cls.HEADER_SIZE]
        command_value, flags, msg_id, length = struct.unpack(cls.HEADER_FORMAT, header)
        
        # 验证长度
        if len(data) < cls.HEADER_SIZE + length:
            return None
        
        # 提取载荷
        payload = data[cls.HEADER_SIZE:cls.HEADER_SIZE+length]
        
        # 查找命令枚举
        try:
            command = ProtocolCommand(command_value)
        except ValueError:
            command = None
        
        return cls(command, payload, flags, msg_id)
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON格式"""
        return {
            'command': self.command.name if self.command else f'UNKNOWN({self.command})',
            'msg_id': self.msg_id,
            'flags': self.flags,
            'payload_length': len(self.payload),
            'timestamp': self.timestamp
        }

# 协议处理器
class ProtocolHandler:
    """协议处理器基类"""
    
    def __init__(self):
        self.pending_requests = {}  # 等待响应的请求
    
    async def handle_message(self, message: ProtocolMessage, sender_id: str = None):
        """处理接收到的消息"""
        if not message.command:
            # 未知命令，返回错误
            return self.create_error_response(message.msg_id, "Unknown command")
        
        # 获取处理方法
        handler_name = f"handle_{message.command.name.lower()}"
        handler = getattr(self, handler_name, None)
        
        if handler:
            try:
                return await handler(message, sender_id)
            except Exception as e:
                return self.create_error_response(message.msg_id, str(e))
        else:
            return self.create_error_response(message.msg_id, "Handler not found")
    
    async def handle_ping(self, message: ProtocolMessage, sender_id: str = None):
        """处理PING命令"""
        return ProtocolMessage(ProtocolCommand.PONG, b'', msg_id=message.msg_id)
    
    async def handle_echo(self, message: ProtocolMessage, sender_id: str = None):
        """处理ECHO命令"""
        return ProtocolMessage(ProtocolCommand.ECHO, message.payload, msg_id=message.msg_id)
    
    def create_error_response(self, msg_id: int, error_msg: str):
        """创建错误响应"""
        error_data = json.dumps({'error': error_msg}).encode('utf-8')
        return ProtocolMessage(ProtocolCommand.ERROR, error_data, msg_id=msg_id)

# 协议服务器
class ProtocolServer:
    """自定义协议服务器"""
    
    def __init__(self, host='127.0.0.1', port=9000, handler: ProtocolHandler = None):
        self.host = host
        self.port = port
        self.handler = handler or ProtocolHandler()
        self.clients = {}  # 客户端连接
        self.running = False
        self.server = None
    
    async def start(self):
        """启动服务器"""
        self.running = True
        self.server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port
        )
        
        print(f"协议服务器启动: {self.host}:{self.port}")
        
        async with self.server:
            await self.server.serve_forever()
    
    async def stop(self):
        """停止服务器"""
        self.running = False
        
        # 关闭所有客户端连接
        for client_id, (reader, writer) in list(self.clients.items()):
            try:
                writer.close()
                await writer.wait_closed()
            except:
                pass
        
        self.clients.clear()
        
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        print("协议服务器已停止")
    
    async def handle_client(self, reader, writer):
        """处理客户端连接"""
        client_id = f"{writer.get_extra_info('peername')}"
        self.clients[client_id] = (reader, writer)
        print(f"新客户端连接: {client_id}")
        
        try:
            while self.running:
                # 读取消息头
                header_data = await reader.read(ProtocolMessage.HEADER_SIZE)
                if not header_data:
                    break
                
                # 解析消息头获取长度
                try:
                    _, _, _, length = struct.unpack(ProtocolMessage.HEADER_FORMAT, header_data)
                except struct.error:
                    print(f"无效的消息头: {header_data}")
                    break
                
                # 读取载荷
                if length > 0:
                    payload = await reader.read(length)
                    if not payload:
                        break
                else:
                    payload = b''
                
                # 构建完整消息
                message_data = header_data + payload
                message = ProtocolMessage.deserialize(message_data)
                
                if not message:
                    print(f"无法解析消息: {message_data}")
                    continue
                
                # 处理消息
                print(f"收到消息: {message.to_json()}")
                response = await self.handler.handle_message(message, client_id)
                
                # 发送响应（如果有的话）
                if response:
                    response_data = response.serialize()
                    writer.write(response_data)
                    await writer.drain()
        
        except asyncio.IncompleteReadError:
            print(f"客户端连接断开: {client_id}")
        except Exception as e:
            print(f"处理客户端 {client_id} 时出错: {e}")
        finally:
            if client_id in self.clients:
                del self.clients[client_id]
            
            try:
                writer.close()
                await writer.wait_closed()
            except:
                pass
            
            print(f"客户端断开: {client_id}")
    
    async def broadcast(self, message: ProtocolMessage, exclude_client: str = None):
        """广播消息给所有客户端"""
        message_data = message.serialize()
        
        for client_id, (reader, writer) in self.clients.items():
            if client_id != exclude_client:
                try:
                    writer.write(message_data)
                    await writer.drain()
                except Exception as e:
                    print(f"向客户端 {client_id} 广播失败: {e}")

# 协议客户端
class ProtocolClient:
    """自定义协议客户端"""
    
    def __init__(self, host='127.0.0.1', port=9000):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None
        self.handler = ProtocolHandler()
        self.pending_requests = {}  # 等待响应的请求
        self.connected = False
        self.message_id = 1
    
    async def connect(self):
        """连接到服务器"""
        try:
            self.reader, self.writer = await asyncio.open_connection(
                self.host, self.port
            )
            self.connected = True
            
            # 启动消息处理任务
            self.receive_task = asyncio.create_task(self.receive_messages())
            
            print(f"连接到协议服务器: {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"连接失败: {e}")
            return False
    
    async def disconnect(self):
        """断开连接"""
        self.connected = False
        
        if self.receive_task:
            self.receive_task.cancel()
            try:
                await self.receive_task
            except asyncio.CancelledError:
                pass
        
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
        
        print("已断开连接")
    
    async def send_message(self, message: ProtocolCommand, payload: bytes = b'', flags: int = 0, expect_response=True):
        """发送消息"""
        if not self.connected:
            return None
        
        # 生成消息ID
        msg_id = self.message_id
        self.message_id = (self.message_id + 1) & 0xFFFFFFFF
        
        # 创建消息
        protocol_msg = ProtocolMessage(message, payload, flags, msg_id)
        
        if expect_response:
            # 创建等待响应的事件
            response_future = asyncio.Future()
            self.pending_requests[msg_id] = response_future
        
        # 发送消息
        message_data = protocol_msg.serialize()
        self.writer.write(message_data)
        await self.writer.drain()
        
        if expect_response:
            # 等待响应
            try:
                response = await asyncio.wait_for(response_future, timeout=10.0)
                return response
            except asyncio.TimeoutError:
                print(f"消息 {msg_id} 超时")
                if msg_id in self.pending_requests:
                    del self.pending_requests[msg_id]
                return None
        
        return True
    
    async def receive_messages(self):
        """接收消息的任务"""
        buffer = b''
        
        while self.connected:
            try:
                # 接收数据
                data = await self.reader.read(4096)
                if not data:
                    break
                
                buffer += data
                
                # 解析消息
                while len(buffer) >= ProtocolMessage.HEADER_SIZE:
                    # 尝试解析消息头
                    header = buffer[:ProtocolMessage.HEADER_SIZE]
                    try:
                        _, _, _, length = struct.unpack(ProtocolMessage.HEADER_FORMAT, header)
                    except struct.error:
                        print(f"无效的消息头: {header}")
                        break
                    
                    # 检查是否有完整消息
                    if len(buffer) >= ProtocolMessage.HEADER_SIZE + length:
                        # 提取完整消息
                        message_data = buffer[:ProtocolMessage.HEADER_SIZE+length]
                        buffer = buffer[ProtocolMessage.HEADER_SIZE+length:]
                        
                        # 解析消息
                        message = ProtocolMessage.deserialize(message_data)
                        if message:
                            await self.handle_received_message(message)
                    else:
                        # 消息不完整，等待更多数据
                        break
        
            except Exception as e:
                print(f"接收消息时出错: {e}")
                break
        
        # 通知连接断开
        self.connected = False
    
    async def handle_received_message(self, message: ProtocolMessage):
        """处理接收到的消息"""
        # 检查是否是对请求的响应
        if message.msg_id in self.pending_requests:
            response_future = self.pending_requests.pop(message.msg_id)
            response_future.set_result(message)
        else:
            # 处理服务器推送的消息
            await self.handler.handle_message(message)
    
    # 便捷方法
    async def ping(self):
        """发送PING"""
        return await self.send_message(ProtocolCommand.PING)
    
    async def echo(self, data):
        """发送ECHO"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return await self.send_message(ProtocolCommand.ECHO, data)
    
    async def data_request(self, params):
        """发送数据请求"""
        data = json.dumps(params).encode('utf-8')
        return await self.send_message(ProtocolCommand.DATA_REQUEST, data)

# 实现一个具体的协议处理器 - 认证和数据交换
class AuthDataExchangeProtocol(ProtocolHandler):
    """认证与数据交换协议处理器"""
    
    def __init__(self):
        super().__init__()
        self.authenticated_clients = set()
        self.data_store = {}
    
    async def handle_auth_request(self, message: ProtocolMessage, sender_id: str = None):
        """处理认证请求"""
        try:
            # 解析认证数据
            auth_data = json.loads(message.payload.decode('utf-8'))
            username = auth_data.get('username')
            password = auth_data.get('password')
            
            # 简单的认证逻辑（实际应用中应该更复杂）
            if username and password and len(password) >= 6:
                # 认证成功
                self.authenticated_clients.add(sender_id)
                token = f"token_{int(time.time())}_{uuid.uuid4().hex[:8]}"
                
                response_data = json.dumps({
                    'success': True,
                    'token': token,
                    'user': username
                }).encode('utf-8')
                
                return ProtocolMessage(
                    ProtocolCommand.AUTH_RESPONSE,
                    response_data,
                    msg_id=message.msg_id
                )
            else:
                # 认证失败
                response_data = json.dumps({
                    'success': False,
                    'error': 'Invalid credentials'
                }).encode('utf-8')
                
                return ProtocolMessage(
                    ProtocolCommand.AUTH_RESPONSE,
                    response_data,
                    msg_id=message.msg_id
                )
        
        except (json.JSONDecodeError, UnicodeDecodeError):
            return self.create_error_response(message.msg_id, "Invalid auth data")
    
    async def handle_data_request(self, message: ProtocolMessage, sender_id: str = None):
        """处理数据请求"""
        if sender_id not in self.authenticated_clients:
            return self.create_error_response(message.msg_id, "Not authenticated")
        
        try:
            # 解析请求数据
            request_data = json.loads(message.payload.decode('utf-8'))
            action = request_data.get('action')
            
            if action == 'get':
                key = request_data.get('key')
                value = self.data_store.get(key)
                
                response_data = json.dumps({
                    'key': key,
                    'value': value,
                    'found': value is not None
                }).encode('utf-8')
                
            elif action == 'set':
                key = request_data.get('key')
                value = request_data.get('value')
                
                if key is not None and value is not None:
                    self.data_store[key] = value
                    response_data = json.dumps({
                        'success': True,
                        'key': key
                    }).encode('utf-8')
                else:
                    response_data = json.dumps({
                        'success': False,
                        'error': 'Key or value missing'
                    }).encode('utf-8')
                
            elif action == 'list':
                keys = list(self.data_store.keys())
                response_data = json.dumps({
                    'keys': keys,
                    'count': len(keys)
                }).encode('utf-8')
                
            else:
                response_data = json.dumps({
                    'error': f'Unknown action: {action}'
                }).encode('utf-8')
            
            return ProtocolMessage(
                ProtocolCommand.DATA_RESPONSE,
                response_data,
                msg_id=message.msg_id
            )
        
        except (json.JSONDecodeError, UnicodeDecodeError):
            return self.create_error_response(message.msg_id, "Invalid request data")

# 演示自定义协议
async def demo_custom_protocol():
    """演示自定义协议"""
    
    print("=== 自定义协议演示 ===")
    
    # 创建服务器
    handler = AuthDataExchangeProtocol()
    server = ProtocolServer(port=9000, handler=handler)
    
    # 在实际使用中，这会在单独线程中运行
    # server_task = asyncio.create_task(server.start())
    # await asyncio.sleep(1)  # 等待服务器启动
    #
    # # 创建客户端
    # client = ProtocolClient(port=9000)
    # if await client.connect():
    #     try:
    #         # 测试未认证的数据请求
    #         print("测试未认证的数据请求")
    #         response = await client.data_request({'action': 'get', 'key': 'test'})
    #         if response and response.command == ProtocolCommand.ERROR:
    #             error_data = json.loads(response.payload.decode('utf-8'))
    #             print(f"错误: {error_data.get('error')}")
    #
    #         # 认证
    #         print("\n进行认证")
    #         auth_data = json.dumps({
    #             'username': 'user1',
    #             'password': 'password123'
    #         }).encode('utf-8')
    #
    #         response = await client.send_message(
    #             ProtocolCommand.AUTH_REQUEST,
    #             auth_data
    #         )
    #
    #         if response and response.command == ProtocolCommand.AUTH_RESPONSE:
    #             auth_result = json.loads(response.payload.decode('utf-8'))
    #             if auth_result.get('success'):
    #                 print(f"认证成功，令牌: {auth_result.get('token')}")
    #
    #                 # 测试认证后的数据操作
    #                 print("\n设置数据")
    #                 response = await client.data_request({
    #                     'action': 'set',
    #                     'key': 'test_key',
    #                     'value': {'name': 'Test Value', 'timestamp': time.time()}
    #                 })
    #
    #                 if response and response.command == ProtocolCommand.DATA_RESPONSE:
    #                     result = json.loads(response.payload.decode('utf-8'))
    #                     print(f"设置结果: {result}")
    #
    #                 print("\n获取数据")
    #                 response = await client.data_request({
    #                     'action': 'get',
    #                     'key': 'test_key'
    #                 })
    #
    #                 if response and response.command == ProtocolCommand.DATA_RESPONSE:
    #                     result = json.loads(response.payload.decode('utf-8'))
    #                     print(f"获取结果: {result}")
    #
    #                 print("\n列出所有键")
    #                 response = await client.data_request({'action': 'list'})
    #
    #                 if response and response.command == ProtocolCommand.DATA_RESPONSE:
    #                     result = json.loads(response.payload.decode('utf-8'))
    #                     print(f"键列表: {result.get('keys')}")
    #
    #         # 测试ping/echo
    #         print("\n测试PING")
    #         response = await client.ping()
    #         if response and response.command == ProtocolCommand.PONG:
    #             print("PING/PONG 成功")
    #
    #         print("\n测试ECHO")
    #         test_data = "Hello, Protocol!"
    #         response = await client.echo(test_data)
    #         if response and response.command == ProtocolCommand.ECHO:
    #             echo_data = response.payload.decode('utf-8')
    #             print(f"ECHO响应: {echo_data}")
    #
    #     finally:
    #         await client.disconnect()
    #         await server.stop()

asyncio.run(demo_custom_protocol())
```

这份Python网络编程高级指南涵盖了非阻塞Socket与多路复用、SSL/TLS安全通信、基于asyncio的高性能HTTP服务器以及自定义网络协议实现等高级主题。通过这份指南，您可以掌握构建高性能、安全网络应用程序的核心技能，设计和实现自定义网络协议，为分布式系统、微服务架构或网络应用提供坚实的网络编程基础。