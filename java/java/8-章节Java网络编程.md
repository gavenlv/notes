# 第八章：Java网络编程

## 目录
1. [网络编程概述](#网络编程概述)
2. [TCP/IP协议基础](#tcpip协议基础)
3. [Socket编程](#socket编程)
4. [ServerSocket与Socket](#serversocket与socket)
5. [UDP编程](#udp编程)
6. [URL与URLConnection](#url与urlconnection)
7. [HTTP客户端编程](#http客户端编程)
8. [NIO与网络编程](#nio与网络编程)
9. [WebSocket编程](#websocket编程)
10. [网络安全](#网络安全)
11. [最佳实践](#最佳实践)
12. [常见陷阱与解决方案](#常见陷阱与解决方案)
12. [总结](#总结)

---

## 网络编程概述

### 什么是网络编程
网络编程是指编写程序使计算机能够通过网络进行通信的技术。在现代软件开发中，网络编程是构建分布式系统、Web应用、微服务等的基础。

### Java网络编程的特点
Java提供了丰富的API来支持网络编程，主要包括：
- 基于TCP/IP协议的Socket编程
- 基于UDP协议的数据报通信
- HTTP客户端和服务端编程
- NIO（New I/O）非阻塞I/O模型
- WebSocket实时双向通信

### 网络编程的基本概念
1. **IP地址**：网络中设备的唯一标识
2. **端口号**：应用程序的逻辑标识
3. **协议**：通信规则和约定
4. **套接字（Socket）**：网络通信的端点

---

## TCP/IP协议基础

### TCP协议特点
TCP（Transmission Control Protocol）是一种面向连接的、可靠的传输层协议：
- 面向连接：通信前需要建立连接
- 可靠性：保证数据完整性和顺序
- 流量控制：防止发送方发送过快
- 拥塞控制：避免网络拥塞

### UDP协议特点
UDP（User Datagram Protocol）是一种无连接的传输层协议：
- 无连接：无需建立连接即可发送数据
- 不可靠：不保证数据完整性
- 高效：开销小，传输速度快
- 支持广播和多播

---

## Socket编程

### Socket简介
Socket是网络编程的基础，它是对TCP/IP协议的封装，提供了应用程序间的网络通信接口。

### Socket类型
1. **流式Socket（SOCK_STREAM）**：基于TCP协议，提供可靠的数据传输
2. **数据报Socket（SOCK_DGRAM）**：基于UDP协议，提供无连接的数据传输

### Socket通信过程
#### TCP通信过程
1. 服务器创建ServerSocket并绑定端口
2. 服务器调用accept()方法等待客户端连接
3. 客户端创建Socket并连接到服务器
4. 服务器接受连接，返回Socket对象
5. 双方通过Socket的输入输出流进行数据交换
6. 关闭连接

#### UDP通信过程
1. 发送方创建DatagramSocket
2. 构造DatagramPacket数据包
3. 发送数据包
4. 接收方创建DatagramSocket并绑定端口
5. 接收数据包
6. 处理数据

---

## ServerSocket与Socket

### ServerSocket类
ServerSocket用于服务器端监听客户端连接请求：

```java
// 创建服务器Socket，绑定端口
ServerSocket serverSocket = new ServerSocket(port);

// 等待客户端连接
Socket clientSocket = serverSocket.accept();

// 获取输入输出流
InputStream inputStream = clientSocket.getInputStream();
OutputStream outputStream = clientSocket.getOutputStream();

// 关闭连接
clientSocket.close();
serverSocket.close();
```

### Socket类
Socket用于客户端连接服务器或服务器与客户端通信：

```java
// 创建客户端Socket，连接服务器
Socket socket = new Socket(serverAddress, port);

// 获取输入输出流
InputStream inputStream = socket.getInputStream();
OutputStream outputStream = socket.getOutputStream();

// 关闭连接
socket.close();
```

### Socket常用方法
- `getInputStream()`：获取输入流
- `getOutputStream()`：获取输出流
- `getInetAddress()`：获取远程主机地址
- `getPort()`：获取远程端口
- `getLocalPort()`：获取本地端口
- `close()`：关闭连接

---

## UDP编程

### DatagramSocket类
DatagramSocket是UDP编程的核心类，用于发送和接收数据报：

```java
// 创建DatagramSocket
DatagramSocket socket = new DatagramSocket();

// 发送数据
byte[] data = "Hello UDP".getBytes();
DatagramPacket packet = new DatagramPacket(data, data.length, InetAddress.getByName("localhost"), 8888);
socket.send(packet);

// 接收数据
byte[] buffer = new byte[1024];
DatagramPacket receivePacket = new DatagramPacket(buffer, buffer.length);
socket.receive(receivePacket);
```

### DatagramPacket类
DatagramPacket表示UDP数据包，包含数据、长度、目标地址和端口等信息。

---

## URL与URLConnection

### URL类
URL（Uniform Resource Locator）表示统一资源定位符：

```java
// 创建URL对象
URL url = new URL("http://www.example.com/index.html");

// 获取URL各部分信息
String protocol = url.getProtocol();
String host = url.getHost();
int port = url.getPort();
String path = url.getPath();
String query = url.getQuery();
```

### URLConnection类
URLConnection用于访问URL指向的资源：

```java
// 打开连接
URLConnection connection = url.openConnection();

// 设置请求属性
connection.setRequestProperty("User-Agent", "Mozilla/5.0");

// 获取输入流读取内容
InputStream inputStream = connection.getInputStream();
BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream));
String line;
while ((line = reader.readLine()) != null) {
    System.out.println(line);
}
reader.close();
```

---

## HTTP客户端编程

### 使用HttpURLConnection
HttpURLConnection是专门用于HTTP协议的URLConnection子类：

```java
URL url = new URL("http://httpbin.org/get");
HttpURLConnection connection = (HttpURLConnection) url.openConnection();

// 设置请求方法
connection.setRequestMethod("GET");

// 设置请求头
connection.setRequestProperty("Accept", "application/json");

// 读取响应
int responseCode = connection.getResponseCode();
if (responseCode == HttpURLConnection.HTTP_OK) {
    BufferedReader reader = new BufferedReader(
        new InputStreamReader(connection.getInputStream()));
    String line;
    while ((line = reader.readLine()) != null) {
        System.out.println(line);
    }
    reader.close();
}
connection.disconnect();
```

### POST请求示例
```java
URL url = new URL("http://httpbin.org/post");
HttpURLConnection connection = (HttpURLConnection) url.openConnection();

// 设置POST请求
connection.setRequestMethod("POST");
connection.setDoOutput(true);
connection.setRequestProperty("Content-Type", "application/json");

// 发送数据
String jsonInputString = "{\"name\": \"John\", \"age\": 30}";
try (OutputStream os = connection.getOutputStream()) {
    byte[] input = jsonInputString.getBytes("utf-8");
    os.write(input, 0, input.length);
}

// 读取响应
BufferedReader br = new BufferedReader(
    new InputStreamReader(connection.getInputStream(), "utf-8"));
StringBuilder response = new StringBuilder();
String responseLine;
while ((responseLine = br.readLine()) != null) {
    response.append(responseLine.trim());
}
System.out.println(response.toString());
```

---

## NIO与网络编程

### NIO简介
NIO（New I/O 或 Non-blocking I/O）是从Java 1.4开始引入的一套新的I/O API，可以替代标准的Java I/O API。

### 核心组件
1. **Channels（通道）**：表示到实体（如硬件设备、文件、网络套接字）的开放连接
2. **Buffers（缓冲区）**：包含数据并提供如何访问这些数据的信息
3. **Selectors（选择器）**：允许单个线程处理多个Channel

### ServerSocketChannel示例
```java
// 创建ServerSocketChannel
ServerSocketChannel serverChannel = ServerSocketChannel.open();
serverChannel.bind(new InetSocketAddress(8080));
serverChannel.configureBlocking(false);

// 创建Selector
Selector selector = Selector.open();
serverChannel.register(selector, SelectionKey.OP_ACCEPT);

// 监听事件
while (true) {
    selector.select();
    Set<SelectionKey> selectedKeys = selector.selectedKeys();
    Iterator<SelectionKey> iter = selectedKeys.iterator();
    
    while (iter.hasNext()) {
        SelectionKey key = iter.next();
        
        if (key.isAcceptable()) {
            // 接受新连接
            SocketChannel client = serverChannel.accept();
            client.configureBlocking(false);
            client.register(selector, SelectionKey.OP_READ);
        } else if (key.isReadable()) {
            // 读取数据
            SocketChannel client = (SocketChannel) key.channel();
            ByteBuffer buffer = ByteBuffer.allocate(1024);
            client.read(buffer);
            // 处理数据...
        }
        iter.remove();
    }
}
```

---

## WebSocket编程

### WebSocket简介
WebSocket是一种在单个TCP连接上进行全双工通信的协议，允许服务器主动向客户端推送数据。

### Java WebSocket API
Java EE提供了WebSocket API（javax.websocket）：

```java
// WebSocket服务器端点
@ServerEndpoint("/websocket")
public class WebSocketServer {
    
    @OnOpen
    public void onOpen(Session session) {
        System.out.println("连接打开: " + session.getId());
    }
    
    @OnMessage
    public void onMessage(String message, Session session) {
        System.out.println("收到消息: " + message);
        try {
            session.getBasicRemote().sendText("Echo: " + message);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    
    @OnClose
    public void onClose(Session session) {
        System.out.println("连接关闭: " + session.getId());
    }
    
    @OnError
    public void onError(Session session, Throwable throwable) {
        System.out.println("发生错误: " + throwable.getMessage());
    }
}
```

---

## 网络安全

### SSL/TLS加密
Java通过SSL/TLS协议提供安全的网络通信：

```java
// 创建SSL Socket
SSLContext sslContext = SSLContext.getInstance("TLS");
sslContext.init(keyManagers, trustManagers, new SecureRandom());
SSLSocketFactory factory = sslContext.getSocketFactory();
SSLSocket socket = (SSLSocket) factory.createSocket(host, port);
```

### 防火墙穿透
在企业环境中，可能需要处理防火墙和代理服务器：

```java
// 设置代理
Proxy proxy = new Proxy(Proxy.Type.HTTP, new InetSocketAddress("proxy.company.com", 8080));
URL url = new URL("http://www.example.com");
URLConnection connection = url.openConnection(proxy);
```

---

## 最佳实践

### 1. 连接管理
- 使用连接池管理Socket连接
- 及时关闭不再使用的连接
- 设置合适的超时时间

### 2. 异常处理
- 处理网络异常（ConnectException、SocketTimeoutException等）
- 实现重连机制
- 记录详细的错误日志

### 3. 性能优化
- 使用NIO提高并发处理能力
- 合理设置缓冲区大小
- 避免频繁创建和销毁连接

### 4. 数据序列化
- 选择高效的序列化方式（JSON、Protocol Buffers等）
- 注意数据格式的兼容性

### 5. 安全考虑
- 验证输入数据
- 使用HTTPS加密传输
- 实施身份认证和授权机制

---

## 常见陷阱与解决方案

### 1. 连接泄露
**问题**：忘记关闭Socket连接导致资源泄露
**解决方案**：使用try-with-resources语句确保资源正确释放

```java
try (Socket socket = new Socket(host, port);
     PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
     BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()))) {
    // 使用Socket进行通信
} catch (IOException e) {
    e.printStackTrace();
}
```

### 2. 阻塞操作
**问题**：默认的I/O操作是阻塞的，影响并发性能
**解决方案**：使用NIO或异步I/O

### 3. 编码问题
**问题**：不同平台的字符编码差异导致乱码
**解决方案**：明确指定字符编码

```java
// 指定UTF-8编码
BufferedReader reader = new BufferedReader(
    new InputStreamReader(inputStream, StandardCharsets.UTF_8));
```

### 4. 线程安全
**问题**：多个线程同时访问Socket可能导致数据混乱
**解决方案**：使用同步机制保护共享资源

---

## 总结

Java网络编程为我们提供了强大的功能来构建各种网络应用。从基本的Socket编程到高级的NIO和WebSocket技术，Java都有相应的API支持。

关键要点：
1. 理解TCP和UDP协议的区别和适用场景
2. 掌握Socket编程的基本模式
3. 学会使用NIO提高并发处理能力
4. 注意网络安全和性能优化
5. 遵循最佳实践，避免常见陷阱

通过本章的学习，你应该能够：
- 实现基本的TCP/UDP客户端和服务器
- 使用HTTP协议进行Web服务调用
- 应用NIO技术处理高并发场景
- 构建安全可靠的网络应用

在实际开发中，建议根据具体需求选择合适的技术方案，并结合框架（如Netty、OkHttp等）提高开发效率。