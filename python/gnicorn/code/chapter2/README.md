# 第2章代码示例

本章包含用于理解Gunicorn核心概念与架构的代码示例，包括Worker类型比较、性能测试和信号处理。

## 文件说明

- `worker_comparison.py` - 用于比较不同Worker类型性能的测试应用
- `async_app.py` - 异步应用示例，用于测试异步Worker的优势
- `benchmark.sh` - 用于测试不同Worker类型性能的脚本
- `signal_test.py` - 用于测试Gunicorn信号处理的示例应用
- `send_signals.sh` - 用于向Gunicorn进程发送信号的脚本
- `requirements.txt` - 项目依赖列表

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### Worker类型比较

1. 启动同步Worker测试：
   ```bash
   gunicorn -w 4 -k sync worker_comparison:application
   ```

2. 启动异步Worker测试：
   ```bash
   gunicorn -w 4 -k gevent worker_comparison:application
   ```

3. 运行基准测试：
   ```bash
   chmod +x benchmark.sh
   ./benchmark.sh
   ```

### 信号处理测试

1. 启动带PID文件的Gunicorn：
   ```bash
   gunicorn -p /tmp/gunicorn_example.pid signal_test:application
   ```

2. 在另一个终端运行信号发送脚本：
   ```bash
   chmod +x send_signals.sh
   ./send_signals.sh
   ```

### 异步应用测试

1. 使用同步Worker启动异步应用：
   ```bash
   gunicorn -w 4 -k sync async_app:application
   ```

2. 使用异步Worker启动异步应用：
   ```bash
   gunicorn -w 4 -k gevent async_app:application
   ```

## 测试说明

### Worker类型性能比较

1. 使用`worker_comparison.py`测试不同Worker类型在CPU密集型和I/O密集型任务上的表现
2. 使用`benchmark.sh`进行自动化性能测试
3. 分析结果，理解不同Worker类型的适用场景

### 信号处理实验

1. 使用`signal_test.py`监控信号接收情况
2. 使用`send_signals.sh`向Gunicorn发送各种信号
3. 观察不同信号对Gunicorn行为的影响

### 异步应用测试

1. 使用`async_app.py`测试异步应用在不同Worker类型下的表现
2. 特别关注`/simultaneous-requests`端点，观察异步Worker的优势
3. 理解为什么异步应用需要异步Worker才能发挥优势

## 常见测试场景

### CPU密集型应用测试

```bash
# 使用sync worker
gunicorn -w 4 -k sync worker_comparison:application
ab -n 1000 -c 10 http://localhost:8000/cpu-intensive

# 使用gevent worker
gunicorn -w 4 -k gevent worker_comparison:application
ab -n 1000 -c 10 http://localhost:8000/cpu-intensive
```

### I/O密集型应用测试

```bash
# 使用sync worker
gunicorn -w 4 -k sync worker_comparison:application
ab -n 1000 -c 10 http://localhost:8000/io-intensive

# 使用gevent worker
gunicorn -w 4 -k gevent worker_comparison:application
ab -n 1000 -c 10 http://localhost:8000/io-intensive
```

### 信号处理测试

```bash
# 启动Gunicorn
gunicorn -p /tmp/gunicorn_example.pid -w 4 signal_test:application

# 发送HUP信号（重新加载配置）
kill -HUP $(cat /tmp/gunicorn_example.pid)

# 发发TERM信号（优雅关闭）
kill -TERM $(cat /tmp/gunicorn_example.pid)
```

## 分析结果

1. **Worker类型比较**：
   - CPU密集型应用：sync worker通常表现更好
   - I/O密集型应用：gevent/eventlet worker表现更好

2. **信号处理**：
   - HUP：优雅重启，不会丢失正在处理的请求
   - TERM：优雅关闭，等待处理完成
   - INT：立即关闭，可能会丢失请求

3. **异步应用**：
   - 即使应用代码是同步的，异步Worker也能提高并发性能
   - 对于真正的异步应用，必须使用异步Worker

## 注意事项

1. 确保系统有足够的资源运行多个Worker进程
2. 在进行性能测试时，关闭不必要的后台进程
3. 多次运行测试以获得更准确的结果
4. 注意监控系统的CPU、内存和网络使用情况
5. 在生产环境中，建议使用Nginx作为反向代理