# 第3章代码示例：Gunicorn配置与部署

本章包含用于演示Gunicorn配置与部署的代码示例，包括生产环境配置、Nginx配置和服务管理脚本。

## 文件说明

- `gunicorn_prod.conf.py` - 生产环境Gunicorn配置
- `gunicorn_dev.conf.py` - 开发环境Gunicorn配置
- `nginx.conf` - Nginx主配置文件
- `site.conf` - Nginx站点配置，包含SSL支持

## 快速开始

### 使用生产配置启动Gunicorn

```bash
# 首先确保配置文件中的路径和用户存在
sudo mkdir -p /var/log/gunicorn
sudo chown www-data:www-data /var/log/gunicorn

# 使用生产配置启动Gunicorn
gunicorn -c gunicorn_prod.conf.py myapp:application
```

### 使用开发配置启动Gunicorn

```bash
# 使用开发配置启动Gunicorn
gunicorn -c gunicorn_dev.conf.py myapp:application
```

### 配置Nginx

1. 将`nginx.conf`复制到`/etc/nginx/nginx.conf`
2. 将`site.conf`复制到`/etc/nginx/sites-available/mysite`
3. 创建符号链接：
   ```bash
   sudo ln -s /etc/nginx/sites-available/mysite /etc/nginx/sites-enabled/
   ```
4. 测试配置：
   ```bash
   sudo nginx -t
   ```
5. 重载配置：
   ```bash
   sudo nginx -s reload
   ```

## 配置说明

### Gunicorn配置

生产环境配置与开发环境配置的主要区别：

1. **Worker数量**：生产环境使用更多Worker（`2 * CPU核心数 + 1`）
2. **日志级别**：生产环境使用`warning`级别，开发环境使用`debug`
3. **守护进程**：生产环境后台运行，开发环境前台运行
4. **用户权限**：生产环境使用`www-data`用户，开发环境使用当前用户
5. **文件位置**：生产环境使用标准位置，开发环境使用临时位置

### Nginx配置

Nginx配置包含以下功能：

1. **负载均衡**：配置了upstream块，支持多台Gunicorn服务器
2. **SSL支持**：配置了HTTPS，包括安全头和SSL优化
3. **静态文件**：配置了静态文件和媒体文件的处理
4. **代理设置**：配置了请求头传递和超时设置

## 注意事项

1. **文件权限**：确保Gunicorn有权限写入日志目录
2. **用户设置**：生产环境中，确保以非特权用户运行Gunicorn
3. **SSL证书**：使用HTTPS前，需要先获取SSL证书
4. **配置测试**：修改Nginx配置后，务必使用`nginx -t`测试配置
5. **日志轮转**：建议配置logrotate管理日志文件

## 扩展配置

### 环境特定配置

可以通过环境变量实现环境特定配置：

```python
# 在gunicorn配置中
import os

# 根据环境变量设置worker数量
env = os.environ.get('APP_ENV', 'development')
if env == 'production':
    workers = multiprocessing.cpu_count() * 2 + 1
    loglevel = "warning"
elif env == 'testing':
    workers = 2
    loglevel = "info"
else:
    workers = 1
    loglevel = "debug"
```

### 系统服务配置

可以创建systemd服务文件管理Gunicorn：

```ini
# /etc/systemd/system/gunicorn.service
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/app
ExecStart=/path/to/venv/bin/gunicorn -c /path/to/gunicorn_prod.conf.py myapp:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```