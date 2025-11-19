import java.io.*;
import java.net.*;
import java.nio.*;
import java.nio.channels.*;
import java.nio.charset.*;
import java.util.*;
import java.util.concurrent.*;

/**
 * 第八章：Java网络编程 - 完整示例代码
 * 
 * 本文件包含了Java网络编程的主要概念和实用示例，涵盖了：
 * 1. TCP Socket编程（客户端和服务端）
 * 2. UDP编程
 * 3. URL和URLConnection使用
 * 4. HTTP客户端编程
 * 5. NIO网络编程
 * 6. 综合示例：简单的聊天室系统
 */

// 示例1：TCP Socket服务端
class TCPServer {
    private ServerSocket serverSocket;
    private final int port;
    
    public TCPServer(int port) {
        this.port = port;
    }
    
    public void start() {
        try {
            serverSocket = new ServerSocket(port);
            System.out.println("TCP服务器启动，监听端口: " + port);
            
            while (true) {
                Socket clientSocket = serverSocket.accept();
                System.out.println("客户端连接: " + clientSocket.getInetAddress());
                
                // 为每个客户端创建一个新线程处理
                new ClientHandler(clientSocket).start();
            }
        } catch (IOException e) {
            System.err.println("服务器错误: " + e.getMessage());
        } finally {
            stop();
        }
    }
    
    public void stop() {
        try {
            if (serverSocket != null && !serverSocket.isClosed()) {
                serverSocket.close();
            }
        } catch (IOException e) {
            System.err.println("关闭服务器时出错: " + e.getMessage());
        }
    }
    
    // 客户端处理器
    private static class ClientHandler extends Thread {
        private Socket clientSocket;
        private PrintWriter out;
        private BufferedReader in;
        
        public ClientHandler(Socket socket) {
            this.clientSocket = socket;
        }
        
        public void run() {
            try {
                out = new PrintWriter(clientSocket.getOutputStream(), true);
                in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
                
                String inputLine;
                while ((inputLine = in.readLine()) != null) {
                    System.out.println("收到客户端消息: " + inputLine);
                    
                    // 回显消息
                    out.println("服务器回复: " + inputLine);
                    
                    // 如果客户端发送"bye"则断开连接
                    if ("bye".equals(inputLine)) {
                        break;
                    }
                }
            } catch (IOException e) {
                System.err.println("处理客户端时出错: " + e.getMessage());
            } finally {
                try {
                    in.close();
                    out.close();
                    clientSocket.close();
                    System.out.println("客户端连接已关闭");
                } catch (IOException e) {
                    System.err.println("关闭客户端连接时出错: " + e.getMessage());
                }
            }
        }
    }
    
    public static void demonstrate() {
        System.out.println("=== TCP Socket服务端示例 ===");
        System.out.println("请运行TCPClient示例来测试此服务器");
        System.out.println("按Ctrl+C停止服务器\n");
        
        // 在单独的线程中启动服务器
        TCPServer server = new TCPServer(8080);
        Thread serverThread = new Thread(server::start);
        serverThread.setDaemon(true); // 设为守护线程，便于演示结束后退出
        serverThread.start();
        
        try {
            Thread.sleep(2000); // 等待服务器启动
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}

// 示例2：TCP Socket客户端
class TCPClient {
    private Socket clientSocket;
    private PrintWriter out;
    private BufferedReader in;
    
    public void startConnection(String ip, int port) {
        try {
            clientSocket = new Socket(ip, port);
            out = new PrintWriter(clientSocket.getOutputStream(), true);
            in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
            System.out.println("已连接到服务器: " + ip + ":" + port);
        } catch (IOException e) {
            System.err.println("连接服务器失败: " + e.getMessage());
        }
    }
    
    public String sendMessage(String msg) {
        try {
            out.println(msg);
            return in.readLine();
        } catch (IOException e) {
            System.err.println("发送消息时出错: " + e.getMessage());
            return null;
        }
    }
    
    public void stopConnection() {
        try {
            in.close();
            out.close();
            clientSocket.close();
            System.out.println("客户端连接已关闭");
        } catch (IOException e) {
            System.err.println("关闭客户端连接时出错: " + e.getMessage());
        }
    }
    
    public static void demonstrate() {
        System.out.println("=== TCP Socket客户端示例 ===");
        TCPClient client = new TCPClient();
        client.startConnection("localhost", 8080);
        
        // 发送几条消息
        System.out.println(client.sendMessage("你好，服务器！"));
        System.out.println(client.sendMessage("这是第二条消息"));
        System.out.println(client.sendMessage("bye")); // 发送bye断开连接
        
        client.stopConnection();
        System.out.println();
    }
}

// 示例3：UDP服务端
class UDPServer {
    private DatagramSocket socket;
    private final int port;
    private boolean running;
    
    public UDPServer(int port) {
        this.port = port;
    }
    
    public void start() {
        try {
            socket = new DatagramSocket(port);
            running = true;
            System.out.println("UDP服务器启动，监听端口: " + port);
            
            while (running) {
                byte[] buffer = new byte[1024];
                DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
                
                // 接收数据包
                socket.receive(packet);
                
                String received = new String(packet.getData(), 0, packet.getLength());
                System.out.println("收到UDP消息: " + received);
                
                // 回复客户端
                String response = "服务器回复: " + received;
                byte[] responseData = response.getBytes();
                DatagramPacket responsePacket = new DatagramPacket(
                    responseData, responseData.length,
                    packet.getAddress(), packet.getPort());
                socket.send(responsePacket);
                
                // 如果收到"bye"则停止服务器
                if ("bye".equals(received)) {
                    running = false;
                }
            }
        } catch (IOException e) {
            if (running) {
                System.err.println("UDP服务器错误: " + e.getMessage());
            }
        } finally {
            stop();
        }
    }
    
    public void stop() {
        running = false;
        if (socket != null && !socket.isClosed()) {
            socket.close();
        }
        System.out.println("UDP服务器已停止");
    }
    
    public static void demonstrate() {
        System.out.println("=== UDP服务端示例 ===");
        System.out.println("请运行UDPClient示例来测试此服务器");
        System.out.println("按Ctrl+C停止服务器\n");
        
        // 在单独的线程中启动服务器
        UDPServer server = new UDPServer(8081);
        Thread serverThread = new Thread(server::start);
        serverThread.setDaemon(true); // 设为守护线程，便于演示结束后退出
        serverThread.start();
        
        try {
            Thread.sleep(2000); // 等待服务器启动
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}

// 示例4：UDP客户端
class UDPClient {
    private DatagramSocket socket;
    private InetAddress address;
    private final int port;
    
    public UDPClient(String hostname, int port) throws UnknownHostException, SocketException {
        this.address = InetAddress.getByName(hostname);
        this.port = port;
        this.socket = new DatagramSocket();
    }
    
    public String sendAndReceive(String message) throws IOException {
        byte[] sendData = message.getBytes();
        DatagramPacket sendPacket = new DatagramPacket(sendData, sendData.length, address, port);
        socket.send(sendPacket);
        
        byte[] receiveData = new byte[1024];
        DatagramPacket receivePacket = new DatagramPacket(receiveData, receiveData.length);
        socket.receive(receivePacket);
        
        return new String(receivePacket.getData(), 0, receivePacket.getLength());
    }
    
    public void close() {
        if (socket != null && !socket.isClosed()) {
            socket.close();
        }
    }
    
    public static void demonstrate() {
        System.out.println("=== UDP客户端示例 ===");
        try {
            UDPClient client = new UDPClient("localhost", 8081);
            
            // 发送几条消息
            System.out.println(client.sendAndReceive("你好，UDP服务器！"));
            System.out.println(client.sendAndReceive("这是第二条UDP消息"));
            System.out.println(client.sendAndReceive("bye")); // 发送bye
            
            client.close();
        } catch (IOException e) {
            System.err.println("UDP客户端错误: " + e.getMessage());
        }
        System.out.println();
    }
}

// 示例5：URL和URLConnection使用
class URLExample {
    public static void demonstrate() {
        System.out.println("=== URL和URLConnection示例 ===");
        
        try {
            // 创建URL对象
            URL url = new URL("https://httpbin.org/get");
            
            // 打开连接
            URLConnection connection = url.openConnection();
            
            // 设置请求属性
            connection.setRequestProperty("User-Agent", "Java Network Programming Example");
            
            // 读取响应
            System.out.println("正在获取URL内容...");
            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(connection.getInputStream()))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    System.out.println(line);
                }
            }
        } catch (IOException e) {
            System.err.println("URL操作错误: " + e.getMessage());
        }
        System.out.println();
    }
}

// 示例6：HTTP客户端编程
class HTTPClientExample {
    public static void demonstrate() {
        System.out.println("=== HTTP客户端示例 ===");
        
        try {
            // GET请求
            System.out.println("发送GET请求...");
            URL getUrl = new URL("https://httpbin.org/get?name=Java&version=8");
            HttpURLConnection getConnection = (HttpURLConnection) getUrl.openConnection();
            getConnection.setRequestMethod("GET");
            
            System.out.println("GET响应码: " + getConnection.getResponseCode());
            
            // 读取响应
            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(getConnection.getInputStream()))) {
                String line;
                System.out.println("GET响应内容:");
                while ((line = reader.readLine()) != null) {
                    System.out.println(line);
                }
            }
            
            // POST请求
            System.out.println("\n发送POST请求...");
            URL postUrl = new URL("https://httpbin.org/post");
            HttpURLConnection postConnection = (HttpURLConnection) postUrl.openConnection();
            postConnection.setRequestMethod("POST");
            postConnection.setDoOutput(true);
            postConnection.setRequestProperty("Content-Type", "application/json");
            
            // 发送POST数据
            String jsonInputString = "{\"name\": \"Java\", \"type\": \"Network Programming\"}";
            try (OutputStream os = postConnection.getOutputStream()) {
                byte[] input = jsonInputString.getBytes("utf-8");
                os.write(input, 0, input.length);
            }
            
            System.out.println("POST响应码: " + postConnection.getResponseCode());
            
            // 读取POST响应
            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(postConnection.getInputStream(), "utf-8"))) {
                StringBuilder response = new StringBuilder();
                String responseLine;
                while ((responseLine = reader.readLine()) != null) {
                    response.append(responseLine.trim());
                }
                System.out.println("POST响应内容:");
                System.out.println(response.toString());
            }
            
        } catch (IOException e) {
            System.err.println("HTTP客户端错误: " + e.getMessage());
        }
        System.out.println();
    }
}

// 示例7：NIO TCP服务端
class NIOServer {
    private Selector selector;
    private ServerSocketChannel serverChannel;
    private final int port;
    
    public NIOServer(int port) {
        this.port = port;
    }
    
    public void start() {
        try {
            // 创建Selector
            selector = Selector.open();
            
            // 创建ServerSocketChannel
            serverChannel = ServerSocketChannel.open();
            serverChannel.configureBlocking(false);
            serverChannel.bind(new InetSocketAddress(port));
            
            // 注册感兴趣的事件
            serverChannel.register(selector, SelectionKey.OP_ACCEPT);
            
            System.out.println("NIO服务器启动，监听端口: " + port);
            
            // 事件循环
            while (true) {
                // 等待事件
                selector.select();
                
                // 处理事件
                Set<SelectionKey> selectedKeys = selector.selectedKeys();
                Iterator<SelectionKey> iter = selectedKeys.iterator();
                
                while (iter.hasNext()) {
                    SelectionKey key = iter.next();
                    
                    if (key.isAcceptable()) {
                        handleAccept(key);
                    } else if (key.isReadable()) {
                        handleRead(key);
                    }
                    
                    iter.remove();
                }
            }
        } catch (IOException e) {
            System.err.println("NIO服务器错误: " + e.getMessage());
        }
    }
    
    private void handleAccept(SelectionKey key) throws IOException {
        ServerSocketChannel serverChannel = (ServerSocketChannel) key.channel();
        SocketChannel clientChannel = serverChannel.accept();
        clientChannel.configureBlocking(false);
        
        System.out.println("NIO客户端连接: " + clientChannel.getRemoteAddress());
        
        // 注册读事件
        clientChannel.register(selector, SelectionKey.OP_READ);
    }
    
    private void handleRead(SelectionKey key) throws IOException {
        SocketChannel clientChannel = (SocketChannel) key.channel();
        ByteBuffer buffer = ByteBuffer.allocate(1024);
        
        int bytesRead = clientChannel.read(buffer);
        if (bytesRead > 0) {
            buffer.flip();
            byte[] data = new byte[buffer.remaining()];
            buffer.get(data);
            String message = new String(data).trim();
            
            System.out.println("收到NIO消息: " + message);
            
            // 回复客户端
            String response = "NIO服务器回复: " + message + "\n";
            ByteBuffer responseBuffer = ByteBuffer.wrap(response.getBytes());
            clientChannel.write(responseBuffer);
        } else if (bytesRead < 0) {
            // 客户端断开连接
            System.out.println("NIO客户端断开连接: " + clientChannel.getRemoteAddress());
            clientChannel.close();
        }
    }
    
    public static void demonstrate() {
        System.out.println("=== NIO服务端示例 ===");
        System.out.println("请使用telnet localhost 8082或其他TCP客户端测试此服务器");
        System.out.println("按Ctrl+C停止服务器\n");
        
        // 在单独的线程中启动服务器
        NIOServer server = new NIOServer(8082);
        Thread serverThread = new Thread(server::start);
        serverThread.setDaemon(true); // 设为守护线程，便于演示结束后退出
        serverThread.start();
        
        try {
            Thread.sleep(2000); // 等待服务器启动
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}

// 综合示例：简单的聊天室系统
class ChatRoomSystem {
    // 聊天室服务端
    static class ChatServer {
        private ServerSocket serverSocket;
        private final Set<ClientHandler> clients = ConcurrentHashMap.newKeySet();
        private final int port;
        private boolean running = true;
        
        public ChatServer(int port) {
            this.port = port;
        }
        
        public void start() {
            try {
                serverSocket = new ServerSocket(port);
                System.out.println("聊天室服务器启动，监听端口: " + port);
                
                while (running) {
                    Socket clientSocket = serverSocket.accept();
                    ClientHandler clientHandler = new ClientHandler(clientSocket, this);
                    clients.add(clientHandler);
                    new Thread(clientHandler).start();
                }
            } catch (IOException e) {
                if (running) {
                    System.err.println("聊天室服务器错误: " + e.getMessage());
                }
            }
        }
        
        public void broadcastMessage(String message, ClientHandler sender) {
            for (ClientHandler client : clients) {
                if (client != sender) {
                    client.sendMessage(message);
                }
            }
        }
        
        public void removeClient(ClientHandler client) {
            clients.remove(client);
        }
        
        public void stop() {
            running = false;
            try {
                if (serverSocket != null && !serverSocket.isClosed()) {
                    serverSocket.close();
                }
            } catch (IOException e) {
                System.err.println("关闭聊天室服务器时出错: " + e.getMessage());
            }
        }
    }
    
    // 客户端处理器
    static class ClientHandler implements Runnable {
        private Socket clientSocket;
        private ChatServer server;
        private PrintWriter out;
        private BufferedReader in;
        private String clientName;
        
        public ClientHandler(Socket socket, ChatServer server) {
            this.clientSocket = socket;
            this.server = server;
        }
        
        @Override
        public void run() {
            try {
                out = new PrintWriter(clientSocket.getOutputStream(), true);
                in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
                
                // 获取客户端名称
                out.println("欢迎来到聊天室！请输入您的昵称:");
                clientName = in.readLine();
                
                if (clientName == null || clientName.trim().isEmpty()) {
                    clientName = "匿名用户";
                }
                
                System.out.println(clientName + " 加入了聊天室");
                server.broadcastMessage(clientName + " 加入了聊天室", this);
                out.println("您已加入聊天室，输入 'bye' 退出");
                
                String inputLine;
                while ((inputLine = in.readLine()) != null) {
                    if ("bye".equals(inputLine)) {
                        break;
                    }
                    
                    String message = clientName + ": " + inputLine;
                    System.out.println("广播消息: " + message);
                    server.broadcastMessage(message, this);
                }
            } catch (IOException e) {
                System.err.println("处理客户端 " + clientName + " 时出错: " + e.getMessage());
            } finally {
                cleanup();
            }
        }
        
        public void sendMessage(String message) {
            out.println(message);
        }
        
        private void cleanup() {
            try {
                if (in != null) in.close();
                if (out != null) out.close();
                if (clientSocket != null) clientSocket.close();
            } catch (IOException e) {
                System.err.println("清理客户端 " + clientName + " 资源时出错: " + e.getMessage());
            }
            
            if (clientName != null) {
                System.out.println(clientName + " 离开了聊天室");
                server.broadcastMessage(clientName + " 离开了聊天室", this);
            }
            
            server.removeClient(this);
        }
    }
    
    // 聊天室客户端
    static class ChatClient {
        private Socket clientSocket;
        private PrintWriter out;
        private BufferedReader in;
        private BufferedReader stdIn;
        
        public void connect(String host, int port) throws IOException {
            clientSocket = new Socket(host, port);
            out = new PrintWriter(clientSocket.getOutputStream(), true);
            in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
            stdIn = new BufferedReader(new InputStreamReader(System.in));
        }
        
        public void startChat() throws IOException {
            System.out.println("=== 聊天室客户端 ===");
            System.out.println("连接到服务器，请按照提示操作");
            
            // 启动接收消息的线程
            Thread receiverThread = new Thread(() -> {
                try {
                    String serverMessage;
                    while ((serverMessage = in.readLine()) != null) {
                        System.out.println(serverMessage);
                    }
                } catch (IOException e) {
                    if (!clientSocket.isClosed()) {
                        System.err.println("接收消息时出错: " + e.getMessage());
                    }
                }
            });
            receiverThread.start();
            
            // 发送用户输入的消息
            String userInput;
            while ((userInput = stdIn.readLine()) != null) {
                out.println(userInput);
                if ("bye".equals(userInput)) {
                    break;
                }
            }
        }
        
        public void disconnect() throws IOException {
            if (stdIn != null) stdIn.close();
            if (in != null) in.close();
            if (out != null) out.close();
            if (clientSocket != null) clientSocket.close();
        }
    }
    
    public static void demonstrate() {
        System.out.println("=== 综合示例：聊天室系统 ===");
        System.out.println("这是一个简单的聊天室系统示例");
        System.out.println("由于需要交互式输入，这里仅展示代码结构");
        System.out.println("实际使用时，需要分别运行服务器和客户端\n");
        
        // 展示服务器代码的使用方式
        System.out.println("服务器启动代码:");
        System.out.println("ChatServer server = new ChatServer(8083);");
        System.out.println("server.start(); // 在单独线程中运行");
        System.out.println();
        
        // 展示客户端代码的使用方式
        System.out.println("客户端连接代码:");
        System.out.println("ChatClient client = new ChatClient();");
        System.out.println("client.connect(\"localhost\", 8083);");
        System.out.println("client.startChat();");
        System.out.println();
    }
}

// 主类 - 运行所有示例
public class Chapter8Example {
    public static void main(String[] args) {
        System.out.println("第八章：Java网络编程 - 完整示例");
        System.out.println("=====================================");
        
        // 注意：为了演示效果，一些服务端示例会在单独的线程中运行
        // 并设置为守护线程，这样在演示完成后程序可以正常退出
        
        // 运行各个示例
        TCPServer.demonstrate();
        
        // 等待一下让服务器启动
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        // 运行TCP客户端示例
        TCPClient.demonstrate();
        
        // 运行UDP示例
        UDPServer.demonstrate();
        
        // 等待一下让服务器启动
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        // 运行UDP客户端示例
        UDPClient.demonstrate();
        
        // 运行URL示例
        URLExample.demonstrate();
        
        // 运行HTTP客户端示例
        HTTPClientExample.demonstrate();
        
        // 运行NIO示例
        NIOServer.demonstrate();
        
        // 等待一下让服务器启动
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        // 运行聊天室系统示例
        ChatRoomSystem.demonstrate();
        
        System.out.println("所有示例演示完成!");
        System.out.println("\n注意：TCP、UDP和NIO服务器示例已在后台线程启动");
        System.out.println("您可以使用telnet或其他TCP客户端连接到相应端口进行测试：");
        System.out.println("- TCP服务器: telnet localhost 8080");
        System.out.println("- UDP服务器: 需要编写UDP客户端测试");
        System.out.println("- NIO服务器: telnet localhost 8082");
        System.out.println("- 聊天室服务器: 需要运行ChatClient进行测试，端口8083");
    }
}