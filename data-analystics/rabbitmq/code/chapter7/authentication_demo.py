"""
第7章：安全与认证 - 身份认证机制演示
演示用户名密码、LDAP、JWT、证书等多种认证方式
"""

import pika
import jwt
import datetime
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os


class BasicAuthDemo:
    """基础用户名密码认证演示"""
    
    def __init__(self, host='localhost', port=5672, username='admin', password='admin123'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
    
    def create_connection(self):
        """创建基础认证连接"""
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            connection_parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials,
                connection_attempts=3,
                retry_delay=5
            )
            connection = pika.BlockingConnection(connection_parameters)
            print(f"✅ 基础认证连接成功 - 用户: {self.username}")
            return connection
        except Exception as e:
            print(f"❌ 基础认证连接失败: {e}")
            return None
    
    def demonstrate_auth_flow(self):
        """演示认证流程"""
        print("🔐 基础认证演示")
        print("-" * 50)
        
        # 创建连接
        connection = self.create_connection()
        if not connection:
            return
        
        try:
            channel = connection.channel()
            
            # 声明队列
            channel.queue_declare(queue='auth_demo_queue', durable=True)
            
            # 发布测试消息
            message = {
                'type': 'auth_test',
                'user': self.username,
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            channel.basic_publish(
                exchange='',
                routing_key='auth_demo_queue',
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
            
            print(f"📤 发布认证测试消息: {message}")
            
            # 消费消息
            def consume_callback(ch, method, properties, body):
                data = json.loads(body)
                print(f"📥 接收认证测试消息: {data}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
            
            channel.basic_consume(
                queue='auth_demo_queue',
                on_message_callback=consume_callback,
                auto_ack=False
            )
            
            # 开始消费
            channel.start_consuming()
            
        except Exception as e:
            print(f"❌ 消息处理失败: {e}")
        finally:
            connection.close()


class JWTAuthProvider:
    """JWT Token认证提供器"""
    
    def __init__(self, secret_key='your-secret-key'):
        self.secret_key = secret_key
        self.valid_tokens = set()
    
    def generate_token(self, user_id, permissions, expires_hours=24):
        """生成JWT Token"""
        payload = {
            'user_id': user_id,
            'permissions': permissions,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=expires_hours),
            'iat': datetime.datetime.utcnow(),
            'iss': 'rabbitmq_auth_service'
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        self.valid_tokens.add(token)
        return token
    
    def verify_token(self, token):
        """验证JWT Token"""
        try:
            if token not in self.valid_tokens:
                raise Exception("Token已失效")
            
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            self.valid_tokens.discard(token)
            raise Exception("Token已过期")
        except jwt.InvalidTokenError:
            raise Exception("无效的Token")
        except Exception as e:
            raise Exception(f"Token验证失败: {str(e)}")
    
    def revoke_token(self, token):
        """撤销Token"""
        self.valid_tokens.discard(token)


class JWTAuthDemo:
    """JWT认证演示"""
    
    def __init__(self, host='localhost', port=5672):
        self.host = host
        self.port = port
        self.auth_provider = JWTAuthProvider()
    
    def create_jwt_connection(self, token):
        """创建JWT认证连接"""
        try:
            # 注意：RabbitMQ原生不支持JWT，需要自定义认证插件
            # 这里演示JWT认证流程
            
            # 验证Token
            payload = self.auth_provider.verify_token(token)
            print(f"✅ JWT Token验证成功 - 用户ID: {payload['user_id']}")
            print(f"📋 权限: {payload['permissions']}")
            
            # 创建连接（这里使用基础认证作为示例）
            # 实际实现需要自定义认证后端
            credentials = pika.PlainCredentials('jwt_user', 'temp_password')
            connection_parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials
            )
            connection = pika.BlockingConnection(connection_parameters)
            return connection, payload
            
        except Exception as e:
            print(f"❌ JWT认证失败: {e}")
            return None, None
    
    def demonstrate_jwt_flow(self):
        """演示JWT认证流程"""
        print("\n🎫 JWT认证演示")
        print("-" * 50)
        
        # 生成Token
        permissions = ['publish', 'consume']
        token = self.auth_provider.generate_token(
            user_id='user123',
            permissions=permissions,
            expires_hours=1
        )
        
        print(f"🔑 生成JWT Token: {token[:50]}...")
        
        # 使用Token认证
        connection, payload = self.create_jwt_connection(token)
        if not connection:
            return
        
        try:
            channel = connection.channel()
            
            # 声明队列
            channel.queue_declare(queue='jwt_demo_queue', durable=True)
            
            # 发布消息
            message = {
                'type': 'jwt_auth_test',
                'user_id': payload['user_id'],
                'permissions': payload['permissions'],
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            channel.basic_publish(
                exchange='',
                routing_key='jwt_demo_queue',
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json',
                    headers={'jwt_token': token}
                )
            )
            
            print(f"📤 发布JWT认证测试消息")
            
            # 消费消息
            def consume_callback(ch, method, properties, body):
                data = json.loads(body)
                jwt_token = properties.headers.get('jwt_token', '')
                
                try:
                    # 验证消息中的Token
                    token_payload = self.auth_provider.verify_token(jwt_token)
                    print(f"📥 接收JWT认证消息: 用户{ token_payload['user_id'] }")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    print(f"❌ 消息Token验证失败: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
            channel.basic_consume(
                queue='jwt_demo_queue',
                on_message_callback=consume_callback,
                auto_ack=False
            )
            
            # 开始消费
            channel.start_consuming()
            
        except Exception as e:
            print(f"❌ 消息处理失败: {e}")
        finally:
            connection.close()


class MessageEncryption:
    """消息内容加密"""
    
    def __init__(self, encryption_key=None):
        if encryption_key:
            self.cipher = Fernet(encryption_key)
        else:
            encryption_key = Fernet.generate_key()
            self.cipher = Fernet(encryption_key)
            print(f"🔐 生成加密密钥: {encryption_key.decode()}")
    
    def encrypt_message(self, message_data):
        """加密消息"""
        if isinstance(message_data, dict):
            message_data = json.dumps(message_data)
        
        if isinstance(message_data, str):
            message_data = message_data.encode('utf-8')
        
        encrypted_data = self.cipher.encrypt(message_data)
        return base64.b64encode(encrypted_data).decode('utf-8')
    
    def decrypt_message(self, encrypted_message):
        """解密消息"""
        encrypted_data = base64.b64decode(encrypted_message.encode('utf-8'))
        decrypted_data = self.cipher.decrypt(encrypted_data)
        return decrypted_data.decode('utf-8')


class CertificateAuthDemo:
    """证书认证演示"""
    
    def __init__(self, host='localhost', port=5671, ca_cert=None, cert_file=None, key_file=None):
        self.host = host
        self.port = port
        self.ca_cert = ca_cert or '/path/to/ca.pem'
        self.cert_file = cert_file or '/path/to/client.pem'
        self.key_file = key_file or '/path/to/client.key'
    
    def create_ssl_context(self):
        """创建SSL上下文"""
        try:
            import ssl
            
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            context.load_verify_locations(self.ca_cert)
            context.load_cert_chain(self.cert_file, self.key_file)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_REQUIRED
            
            # 强制TLS 1.2+
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            
            return context
        except Exception as e:
            print(f"❌ SSL上下文创建失败: {e}")
            return None
    
    def create_certificate_connection(self):
        """创建证书认证连接"""
        try:
            ssl_context = self.create_ssl_context()
            if not ssl_context:
                return None
            
            connection_parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                ssl_options=pika.SSLOptions(ssl_context)
            )
            
            connection = pika.BlockingConnection(connection_parameters)
            print(f"✅ 证书认证连接成功")
            return connection
            
        except Exception as e:
            print(f"❌ 证书认证连接失败: {e}")
            return None
    
    def demonstrate_certificate_flow(self):
        """演示证书认证流程"""
        print("\n🔒 证书认证演示")
        print("-" * 50)
        
        # 创建SSL连接
        connection = self.create_certificate_connection()
        if not connection:
            print("⚠️ 证书认证连接失败，请检查证书配置")
            return
        
        try:
            channel = connection.channel()
            
            # 声明队列
            channel.queue_declare(queue='cert_demo_queue', durable=True)
            
            # 加密消息演示
            encryption = MessageEncryption()
            
            # 创建测试消息
            test_message = {
                'type': 'certificate_auth_test',
                'content': '这是使用证书认证的加密消息',
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            # 加密消息
            encrypted_message = encryption.encrypt_message(test_message)
            
            # 发布加密消息
            channel.basic_publish(
                exchange='',
                routing_key='cert_demo_queue',
                body=encrypted_message,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json',
                    headers={'encrypted': True}
                )
            )
            
            print(f"📤 发布证书认证加密消息")
            
            # 消费并解密消息
            def consume_callback(ch, method, properties, body):
                try:
                    encrypted_data = body.decode('utf-8')
                    decrypted_data = encryption.decrypt_message(encrypted_data)
                    data = json.loads(decrypted_data)
                    
                    print(f"📥 接收并解密证书认证消息: {data['content']}")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    print(f"❌ 消息解密失败: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
            channel.basic_consume(
                queue='cert_demo_queue',
                on_message_callback=consume_callback,
                auto_ack=False
            )
            
            # 开始消费
            channel.start_consuming()
            
        except Exception as e:
            print(f"❌ 消息处理失败: {e}")
        finally:
            connection.close()


class SecureMessageHandler:
    """安全消息处理器"""
    
    def __init__(self, host='localhost', port=5672):
        self.host = host
        self.port = port
        self.encryption = MessageEncryption()
        self.auth_provider = JWTAuthProvider()
    
    def secure_publish(self, exchange, routing_key, message_data, token=None):
        """安全发布消息"""
        try:
            # Token认证
            if token:
                payload = self.auth_provider.verify_token(token)
                user_id = payload['user_id']
                permissions = payload['permissions']
            else:
                user_id = 'anonymous'
                permissions = ['read']
            
            # 权限检查
            if 'write' not in permissions:
                raise PermissionError("没有发布权限")
            
            # 加密消息
            encrypted_message = self.encryption.encrypt_message(message_data)
            
            # 创建连接
            credentials = pika.PlainCredentials('user', 'password')
            connection_parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials
            )
            
            connection = pika.BlockingConnection(connection_parameters)
            channel = connection.channel()
            
            # 发布加密消息
            channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=encrypted_message,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json',
                    headers={
                        'encrypted': True,
                        'user_id': user_id,
                        'jwt_token': token
                    }
                )
            )
            
            print(f"✅ 安全发布消息成功 - 用户: {user_id}")
            connection.close()
            return True
            
        except Exception as e:
            print(f"❌ 安全发布失败: {e}")
            return False
    
    def secure_consume(self, queue, callback, token=None):
        """安全消费消息"""
        try:
            # Token认证
            if token:
                payload = self.auth_provider.verify_token(token)
                user_id = payload['user_id']
                permissions = payload['permissions']
            else:
                user_id = 'anonymous'
                permissions = ['read']
            
            # 权限检查
            if 'read' not in permissions:
                raise PermissionError("没有消费权限")
            
            # 创建连接
            credentials = pika.PlainCredentials('user', 'password')
            connection_parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials
            )
            
            connection = pika.BlockingConnection(connection_parameters)
            channel = connection.channel()
            
            # 创建消费回调
            def secure_callback(ch, method, properties, body):
                try:
                    # 获取消息头
                    encrypted = properties.headers.get('encrypted', False)
                    message_user_id = properties.headers.get('user_id', 'unknown')
                    
                    # 解密消息
                    if encrypted:
                        decrypted_data = self.encryption.decrypt_message(body.decode('utf-8'))
                        message_data = json.loads(decrypted_data)
                    else:
                        message_data = json.loads(body.decode('utf-8'))
                    
                    # 调用用户回调
                    callback(message_data, message_user_id, properties)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    
                except Exception as e:
                    print(f"❌ 消息处理失败: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
            # 开始消费
            channel.basic_consume(
                queue=queue,
                on_message_callback=secure_callback,
                auto_ack=False
            )
            
            print(f"✅ 开始安全消费 - 用户: {user_id}")
            channel.start_consuming()
            connection.close()
            
        except Exception as e:
            print(f"❌ 安全消费失败: {e}")
            return False


class AuthenticationDemo:
    """认证演示主类"""
    
    def __init__(self, host='localhost', port=5672):
        self.host = host
        self.port = port
        self.demos = {
            'basic': BasicAuthDemo(host, port),
            'jwt': JWTAuthDemo(host, port),
            'certificate': CertificateAuthDemo(host, port),
            'secure': SecureMessageHandler(host, port)
        }
    
    def run_all_demos(self):
        """运行所有认证演示"""
        print("🔐 RabbitMQ 安全认证演示")
        print("=" * 60)
        
        demos_to_run = ['basic', 'jwt', 'secure']
        
        for demo_name in demos_to_run:
            try:
                print(f"\n🚀 运行 {demo_name.upper()} 认证演示:")
                self.run_single_demo(demo_name)
                print(f"✅ {demo_name.upper()} 演示完成")
            except KeyboardInterrupt:
                print(f"\n⏹️ 用户中断，跳过剩余演示")
                break
            except Exception as e:
                print(f"❌ {demo_name.upper()} 演示失败: {e}")
                continue
        
        print(f"\n🏁 所有认证演示完成")
    
    def run_single_demo(self, demo_name):
        """运行单个认证演示"""
        if demo_name not in self.demos:
            print(f"❌ 未知的演示类型: {demo_name}")
            return
        
        demo = self.demos[demo_name]
        
        try:
            if demo_name == 'basic':
                demo.demonstrate_auth_flow()
            elif demo_name == 'jwt':
                demo.demonstrate_jwt_flow()
            elif demo_name == 'secure':
                self.demonstrate_secure_handler()
        except KeyboardInterrupt:
            print(f"\n⏹️ 用户中断演示")
        except Exception as e:
            print(f"❌ 演示执行失败: {e}")
    
    def demonstrate_secure_handler(self):
        """演示安全消息处理器"""
        print("\n🔐 安全消息处理器演示")
        print("-" * 50)
        
        # 生成测试Token
        token = self.demos['jwt'].auth_provider.generate_token(
            user_id='secure_user',
            permissions=['read', 'write'],
            expires_hours=1
        )
        
        # 安全发布测试
        test_message = {
            'type': 'secure_message_test',
            'content': '这是安全处理的消息',
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        success = self.demos['secure'].secure_publish(
            exchange='',
            routing_key='secure_test_queue',
            message_data=test_message,
            token=token
        )
        
        if success:
            print("📤 安全消息发布成功")
        
        # 安全消费演示
        def secure_callback(message_data, user_id, properties):
            print(f"📥 安全消息消费: {message_data['content']} (用户: {user_id})")
        
        # 注意：这里简化处理，实际需要消费者逻辑
        print("📥 安全消息消费准备就绪")


if __name__ == "__main__":
    # 运行认证演示
    demo = AuthenticationDemo(host='localhost', port=5672)
    
    try:
        demo.run_all_demos()
    except KeyboardInterrupt:
        print("\n👋 认证演示已结束")
    except Exception as e:
        print(f"❌ 演示运行失败: {e}")