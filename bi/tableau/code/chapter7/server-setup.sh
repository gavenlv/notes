#!/bin/bash
# Tableau Server在Linux上的安装和配置脚本
# 适用于CentOS/RHEL 7.x或更高版本

# 设置变量
TABLEAU_VERSION="2023-1"
TABLEAU_PKG="tableau-server-${TABLEAU_VERSION}.x86_64.rpm"
TABLEAU_URL="https://downloads.tableau.com/esdalt/${TABLEAU_PKG}"

# 创建目录
mkdir -p /opt/tableau
cd /opt/tableau

# 下载Tableau Server
echo "下载Tableau Server..."
wget ${TABLEAU_URL}

# 安装Tableau Server
echo "安装Tableau Server..."
sudo yum install -y ${TABLEAU_PKG}

# 初始化Tableau Server
echo "初始化Tableau Server"
sudo /opt/tableau/tableau_server/bin/tsm initialize --start --accept-eula

# 等待服务器启动
echo "等待Tableau Server启动..."
sleep 60

# 设置管理员账户
echo "设置管理员账户..."
sudo /opt/tableau/tableau_server/bin/tabcmd initialuser --server localhost:80 --username "admin" --password "TableauAdmin123!" --complete

# 激活许可证（替换为实际许可证密钥）
echo "激活Tableau Server许可证..."
sudo /opt/tableau/tableau_server/bin/tsm licenses activate -k "XXXX-XXXX-XXXX-XXXX-XXXX"

# 配置服务器
echo "配置Tableau Server..."
sudo /opt/tableau/tableau_server/bin/tsm configuration set -k wgserver.authentication.enabled -v true
sudo /opt/tableau/tableau_server/bin/tsm configuration set -k wgserver.session.idle.timeout -v "240"  # 4小时
sudo /opt/tableau/tableau_server/bin/tsm configuration set -k backgrounder.querylimit -v "25"

# 应用配置
sudo /opt/tableau/tableau_server/bin/tsm pending-changes apply

# 启动Tableau Server
echo "启动Tableau Server..."
sudo /opt/tableau/tableau_server/bin/tsm start

# 等待服务器完全启动
echo "等待服务器完全启动..."
sleep 120

# 验证安装
echo "验证Tableau Server安装..."
sudo /opt/tableau/tableau_server/bin/tsm status -v

# 设置防火墙规则
echo "配置防火墙规则..."
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload

echo "Tableau Server安装完成!"
echo "访问地址: http://your-server-name"
echo "管理员用户名: admin"
echo "管理员密码: TableauAdmin123!"

# 创建备份脚本
cat > /opt/tableau/backup-tableau.sh << 'EOF'
#!/bin/bash
# Tableau Server备份脚本

BACKUP_DIR="/opt/tableau/backups"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="tableau-backup-${DATE}.tsbak"

# 创建备份目录
mkdir -p ${BACKUP_DIR}

# 执行备份
/opt/tableau/tableau_server/bin/tsm maintenance backup -f ${BACKUP_DIR}/${BACKUP_FILE} -d

# 清理旧备份（保留最近5个）
cd ${BACKUP_DIR}
ls -t tableau-backup-*.tsbak | tail -n +6 | xargs -r rm

echo "Tableau Server备份完成: ${BACKUP_DIR}/${BACKUP_FILE}"
EOF

chmod +x /opt/tableau/backup-tableau.sh

# 设置每日备份任务
echo "0 2 * * * /opt/tableau/backup-tableau.sh >> /var/log/tableau-backup.log 2>&1" | sudo crontab -

echo "备份脚本已设置，将在每天凌晨2点自动执行备份。"