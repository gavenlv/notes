#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MySQL存储引擎与架构设计示例代码
本章代码演示了MySQL中各种存储引擎的特性、高可用架构设计、分片技术和分布式事务实现。
"""

import mysql.connector
import time
import threading
import random
import json
import logging
import hashlib
from typing import Dict, List, Tuple, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MySQL存储引擎与架构设计")

class StorageEngineDemo:
    """存储引擎演示类"""
    
    def __init__(self, host='localhost', user='root', password='password', database='mysql_tutorial'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
    
    def connect(self):
        """连接到MySQL数据库"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            logger.info("成功连接到MySQL数据库")
            return True
        except mysql.connector.Error as err:
            logger.error(f"连接失败: {err}")
            return False
    
    def demonstrate_engines(self):
        """演示不同存储引擎的特性和用法"""
        if not self.connection:
            logger.error("未连接到数据库")
            return False
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # 1. 查看支持的存储引擎
            cursor.execute("SHOW ENGINES")
            engines = cursor.fetchall()
            
            logger.info("MySQL支持的存储引擎:")
            for engine in engines:
                support = engine['Support']
                if support == 'DEFAULT':
                    support = f"{support}(默认)"
                logger.info(f"  {engine['Engine']}: {support}, {engine['Comment']}")
            
            # 2. 创建不同存储引擎的表
            cursor.execute("DROP TABLE IF EXISTS innodb_demo")
            cursor.execute("DROP TABLE IF EXISTS myisam_demo")
            cursor.execute("DROP TABLE IF EXISTS memory_demo")
            cursor.execute("DROP TABLE IF EXISTS archive_demo")
            
            # InnoDB表
            cursor.execute("""
                CREATE TABLE innodb_demo (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(50) NOT NULL,
                    balance DECIMAL(10, 2) NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB
            """)
            
            # MyISAM表
            cursor.execute("""
                CREATE TABLE myisam_demo (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    title VARCHAR(100) NOT NULL,
                    content TEXT,
                    author VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FULLTEXT KEY(title, content)
                ) ENGINE=MyISAM
            """)
            
            # Memory表
            cursor.execute("""
                CREATE TABLE memory_demo (
                    session_id VARCHAR(40) PRIMARY KEY,
                    user_id INT NOT NULL,
                    data TEXT,
                    last_access TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=Memory
            """)
            
            # Archive表
            cursor.execute("""
                CREATE TABLE archive_demo (
                    id BIGINT UNSIGNED AUTO_INCREMENT,
                    log_time TIMESTAMP NOT NULL,
                    level ENUM('DEBUG', 'INFO', 'WARNING', 'ERROR') NOT NULL,
                    message TEXT,
                    PRIMARY KEY (id)
                ) ENGINE=Archive
            """)
            
            logger.info("成功创建了不同存储引擎的示例表")
            
            # 3. 演示存储引擎特性差异
            # InnoDB事务支持
            cursor.execute("START TRANSACTION")
            cursor.execute("INSERT INTO innodb_demo (name, balance) VALUES (%s, %s)", ("Alice", 1000.00))
            cursor.execute("INSERT INTO innodb_demo (name, balance) VALUES (%s, %s)", ("Bob", 2000.00))
            cursor.execute("COMMIT")
            logger.info("InnoDB事务提交成功")
            
            # MyISAM全文搜索
            cursor.execute("""
                INSERT INTO myisam_demo (title, content, author) 
                VALUES (%s, %s, %s)
            """, ("MySQL教程", "这是一篇关于MySQL存储引擎的详细教程", "管理员"))
            
            cursor.execute("""
                SELECT * FROM myisam_demo 
                WHERE MATCH(title, content) AGAINST(%s IN NATURAL LANGUAGE MODE)
            """, ("MySQL",))
            results = cursor.fetchall()
            logger.info(f"MyISAM全文搜索结果: {len(results)} 条记录")
            
            # Memory表快速访问
            session_id = hashlib.md5(f"session_{time.time()}".encode()).hexdigest()
            cursor.execute("""
                INSERT INTO memory_demo (session_id, user_id, data) 
                VALUES (%s, %s, %s)
            """, (session_id, 123, json.dumps({"cart": ["item1", "item2"], "viewed": ["product1"]})))
            
            start_time = time.time()
            cursor.execute("SELECT * FROM memory_demo WHERE session_id = %s", (session_id,))
            cursor.fetchone()
            elapsed = time.time() - start_time
            logger.info(f"Memory表访问耗时: {elapsed:.6f} 秒")
            
            # Archive表高效插入
            start_time = time.time()
            for i in range(1000):
                level = random.choice(['DEBUG', 'INFO', 'WARNING', 'ERROR'])
                cursor.execute("""
                    INSERT INTO archive_demo (log_time, level, message) 
                    VALUES (%s, %s, %s)
                """, (time.strftime('%Y-%m-%d %H:%M:%S'), level, f"这是一条{level}级别的日志消息"))
            elapsed = time.time() - start_time
            logger.info(f"Archive表插入1000条记录耗时: {elapsed:.6f} 秒")
            
            self.connection.commit()
            cursor.close()
            return True
            
        except mysql.connector.Error as err:
            logger.error(f"演示存储引擎失败: {err}")
            return False
    
    def demonstrate_innodb_features(self):
        """演示InnoDB的高级特性"""
        if not self.connection:
            logger.error("未连接到数据库")
            return False
            
        try:
            cursor = self.connection.cursor()
            
            # 1. 演示事务隔离级别
            logger.info("=== 事务隔离级别演示 ===")
            
            # 查看当前隔离级别
            cursor.execute("SELECT @@global.tx_isolation, @@session.tx_isolation")
            isolation_levels = cursor.fetchone()
            logger.info(f"全局隔离级别: {isolation_levels[0]}, 会话隔离级别: {isolation_levels[1]}")
            
            # 2. 演示外键约束
            cursor.execute("DROP TABLE IF EXISTS orders")
            cursor.execute("DROP TABLE IF EXISTS customers")
            
            # 创建客户表
            cursor.execute("""
                CREATE TABLE customers (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(50) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB
            """)
            
            # 创建订单表
            cursor.execute("""
                CREATE TABLE orders (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    customer_id INT NOT NULL,
                    total_amount DECIMAL(10, 2) NOT NULL,
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
                ) ENGINE=InnoDB
            """)
            
            # 插入测试数据
            cursor.execute("INSERT INTO customers (name, email) VALUES (%s, %s)", ("Alice", "alice@example.com"))
            customer_id = cursor.lastrowid
            cursor.execute("INSERT INTO orders (customer_id, total_amount) VALUES (%s, %s)", (customer_id, 99.99))
            
            logger.info("外键约束测试成功")
            
            # 3. 演示行级锁
            logger.info("=== 行级锁演示 ===")
            
            # 在另一个线程中执行加锁查询
            def lock_row():
                try:
                    conn = mysql.connector.connect(
                        host=self.host,
                        user=self.user,
                        password=self.password,
                        database=self.database
                    )
                    cursor = conn.cursor()
                    cursor.execute("START TRANSACTION")
                    cursor.execute("SELECT * FROM customers WHERE id = %s FOR UPDATE", (customer_id,))
                    result = cursor.fetchone()
                    logger.info(f"线程获取锁成功: {result}")
                    time.sleep(2)  # 持有锁2秒
                    conn.commit()
                    cursor.close()
                    conn.close()
                except Exception as e:
                    logger.error(f"加锁线程出错: {e}")
            
            lock_thread = threading.Thread(target=lock_row)
            lock_thread.start()
            
            time.sleep(0.5)  # 确保锁已经获取
            
            # 尝试获取同一行的锁
            try:
                cursor.execute("START TRANSACTION")
                start_time = time.time()
                cursor.execute("SELECT * FROM customers WHERE id = %s FOR UPDATE", (customer_id,))
                cursor.fetchone()
                elapsed = time.time() - start_time
                logger.info(f"主线程等待锁释放时间: {elapsed:.6f} 秒")
                cursor.execute("COMMIT")
            except mysql.connector.Error as err:
                logger.error(f"获取锁失败: {err}")
            
            lock_thread.join()
            
            # 4. 演示自适应哈希索引
            cursor.execute("SHOW VARIABLES LIKE 'innodb_adaptive_hash_index'")
            result = cursor.fetchone()
            logger.info(f"InnoDB自适应哈希索引: {result[1]}")
            
            cursor.execute("SHOW STATUS LIKE 'Innodb_adaptive_hash%'")
            results = cursor.fetchall()
            for result in results:
                logger.info(f"{result[0]}: {result[1]}")
            
            self.connection.commit()
            cursor.close()
            return True
            
        except mysql.connector.Error as err:
            logger.error(f"演示InnoDB特性失败: {err}")
            return False
    
    def demonstrate_replication_setup(self):
        """演示主从复制设置（模拟）"""
        if not self.connection:
            logger.error("未连接到数据库")
            return False
            
        try:
            cursor = self.connection.cursor()
            
            # 1. 检查二进制日志配置
            cursor.execute("SHOW VARIABLES LIKE 'log_bin'")
            log_bin = cursor.fetchone()
            logger.info(f"二进制日志状态: {log_bin[1]}")
            
            cursor.execute("SHOW VARIABLES LIKE 'binlog_format'")
            binlog_format = cursor.fetchone()
            logger.info(f"二进制日志格式: {binlog_format[1]}")
            
            cursor.execute("SHOW VARIABLES LIKE 'server_id'")
            server_id = cursor.fetchone()
            logger.info(f"服务器ID: {server_id[1]}")
            
            # 2. 查看主服务器状态
            cursor.execute("SHOW MASTER STATUS")
            master_status = cursor.fetchone()
            if master_status:
                logger.info("主服务器状态:")
                logger.info(f"  二进制日志文件: {master_status[0]}")
                logger.info(f"  二进制日志位置: {master_status[1]}")
                logger.info(f"  数据库名: {master_status[4]}")
            else:
                logger.info("当前服务器不是主服务器或未启用二进制日志")
            
            # 3. 创建复制用户（模拟）
            logger.info("=== 创建复制用户（模拟） ===")
            logger.info("CREATE USER 'repl_user'@'%' IDENTIFIED BY 'repl_password';")
            logger.info("GRANT REPLICATION SLAVE ON *.* TO 'repl_user'@'%';")
            
            # 4. 配置从服务器（模拟）
            logger.info("=== 配置从服务器（模拟） ===")
            logger.info("CHANGE MASTER TO")
            logger.info("    MASTER_HOST='master_ip',")
            logger.info("    MASTER_USER='repl_user',")
            logger.info("    MASTER_PASSWORD='repl_password',")
            logger.info("    MASTER_LOG_FILE='mysql-bin.000001',")
            logger.info("    MASTER_LOG_POS=154;")
            logger.info("START SLAVE;")
            
            # 5. 检查GTID配置
            cursor.execute("SHOW VARIABLES LIKE 'gtid_mode'")
            gtid_mode = cursor.fetchone()
            logger.info(f"GTID模式: {gtid_mode[1]}")
            
            cursor.execute("SHOW VARIABLES LIKE 'enforce_gtid_consistency'")
            enforce_gtid = cursor.fetchone()
            logger.info(f"强制GTID一致性: {enforce_gtid[1]}")
            
            # 6. 查看全局事务ID
            if gtid_mode and gtid_mode[1] == 'ON':
                cursor.execute("SHOW GLOBAL VARIABLES LIKE 'gtid_executed'")
                gtid_executed = cursor.fetchone()
                logger.info(f"已执行的GTID: {gtid_executed[1]}")
            
            cursor.close()
            return True
            
        except mysql.connector.Error as err:
            logger.error(f"演示复制设置失败: {err}")
            return False
    
    def demonstrate_sharding(self):
        """演示分片技术"""
        if not self.connection:
            logger.error("未连接到数据库")
            return False
            
        try:
            cursor = self.connection.cursor()
            
            # 1. 创建分片表
            cursor.execute("DROP TABLE IF EXISTS users_shard1")
            cursor.execute("DROP TABLE IF EXISTS users_shard2")
            cursor.execute("DROP TABLE IF EXISTS users_shard3")
            cursor.execute("DROP VIEW IF EXISTS users")
            
            # 创建三个分片表
            for i in range(1, 4):
                cursor.execute(f"""
                    CREATE TABLE users_shard{i} (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        username VARCHAR(50) NOT NULL,
                        email VARCHAR(100) UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB
                """)
            
            # 创建分片视图
            cursor.execute("""
                CREATE VIEW users AS
                SELECT * FROM users_shard1
                UNION ALL
                SELECT * FROM users_shard2
                UNION ALL
                SELECT * FROM users_shard3
            """)
            
            logger.info("成功创建分片表和视图")
            
            # 2. 插入测试数据
            for i in range(30):
                username = f"user{i}"
                email = f"user{i}@example.com"
                
                # 简单的哈希分片算法
                shard_id = (hash(username) % 3) + 1
                
                cursor.execute(f"INSERT INTO users_shard{shard_id} (username, email) VALUES (%s, %s)", (username, email))
            
            self.connection.commit()
            logger.info("成功插入30条测试数据到分片表")
            
            # 3. 查询分片数据
            for i in range(1, 4):
                cursor.execute(f"SELECT COUNT(*) FROM users_shard{i}")
                count = cursor.fetchone()[0]
                logger.info(f"分片{i}中的记录数: {count}")
            
            # 4. 测试分片查询性能
            start_time = time.time()
            cursor.execute("SELECT * FROM users WHERE username = %s", ("user15",))
            result = cursor.fetchone()
            elapsed = time.time() - start_time
            logger.info(f"分片查询耗时: {elapsed:.6f} 秒")
            
            # 5. 创建分片存储过程
            cursor.execute("DROP PROCEDURE IF EXISTS insert_user_shard")
            cursor.execute("""
                CREATE PROCEDURE insert_user_shard(IN user_name VARCHAR(50), IN email_addr VARCHAR(100))
                BEGIN
                    DECLARE shard_id INT;
                    SET shard_id = (CRC32(user_name) % 3) + 1;
                    
                    CASE shard_id
                        WHEN 1 THEN
                            INSERT INTO users_shard1 (username, email) VALUES (user_name, email_addr);
                        WHEN 2 THEN
                            INSERT INTO users_shard2 (username, email) VALUES (user_name, email_addr);
                        WHEN 3 THEN
                            INSERT INTO users_shard3 (username, email) VALUES (user_name, email_addr);
                    END CASE;
                END
            """)
            
            # 使用存储过程插入数据
            cursor.callproc("insert_user_shard", ("test_user1", "test1@example.com"))
            cursor.callproc("insert_user_shard", ("test_user2", "test2@example.com"))
            
            self.connection.commit()
            logger.info("成功使用存储过程插入分片数据")
            
            # 6. 创建垂直分表示例
            cursor.execute("DROP TABLE IF EXISTS user_profiles")
            cursor.execute("DROP TABLE IF EXISTS user_activities")
            
            cursor.execute("""
                CREATE TABLE user_profiles (
                    user_id INT PRIMARY KEY,
                    bio TEXT,
                    avatar_url VARCHAR(255),
                    preferences JSON,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB
            """)
            
            cursor.execute("""
                CREATE TABLE user_activities (
                    activity_id BIGINT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT NOT NULL,
                    activity_type VARCHAR(20) NOT NULL,
                    activity_data JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_user_activity (user_id, activity_type)
                ) ENGINE=InnoDB
            """)
            
            logger.info("成功创建垂直分表示例")
            
            # 7. 插入垂直分片数据
            for i in range(1, 11):
                bio = f"这是用户{i}的个人简介"
                preferences = json.dumps({"theme": "dark", "language": "zh-CN"})
                cursor.execute("INSERT INTO user_profiles (user_id, bio, preferences) VALUES (%s, %s, %s)", (i, bio, preferences))
                
                for activity_type in ["login", "view", "purchase"]:
                    activity_data = json.dumps({"page": f"/page{random.randint(1, 10)}", "duration": random.randint(10, 300)})
                    cursor.execute(
                        "INSERT INTO user_activities (user_id, activity_type, activity_data) VALUES (%s, %s, %s)", 
                        (i, activity_type, activity_data)
                    )
            
            self.connection.commit()
            logger.info("成功插入垂直分片测试数据")
            
            cursor.close()
            return True
            
        except mysql.connector.Error as err:
            logger.error(f"演示分片技术失败: {err}")
            return False
    
    def demonstrate_distributed_transactions(self):
        """演示分布式事务（模拟）"""
        if not self.connection:
            logger.error("未连接到数据库")
            return False
            
        try:
            cursor = self.connection.cursor()
            
            # 1. 创建测试表
            cursor.execute("DROP TABLE IF EXISTS bank_accounts")
            cursor.execute("DROP TABLE IF EXISTS transfer_log")
            
            cursor.execute("""
                CREATE TABLE bank_accounts (
                    id INT PRIMARY KEY,
                    name VARCHAR(50) NOT NULL,
                    balance DECIMAL(10, 2) NOT NULL DEFAULT 0
                ) ENGINE=InnoDB
            """)
            
            cursor.execute("""
                CREATE TABLE transfer_log (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    from_account INT NOT NULL,
                    to_account INT NOT NULL,
                    amount DECIMAL(10, 2) NOT NULL,
                    status ENUM('pending', 'completed', 'failed') NOT NULL DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB
            """)
            
            # 插入测试账户
            cursor.execute("INSERT INTO bank_accounts (id, name, balance) VALUES (%s, %s, %s)", (1, "Alice", 1000.00))
            cursor.execute("INSERT INTO bank_accounts (id, name, balance) VALUES (%s, %s, %s)", (2, "Bob", 500.00))
            
            self.connection.commit()
            logger.info("成功创建分布式事务测试表")
            
            # 2. 模拟XA事务
            logger.info("=== XA事务演示（模拟） ===")
            
            # 开始本地事务
            cursor.execute("START TRANSACTION")
            
            # 记录转账日志
            cursor.execute(
                "INSERT INTO transfer_log (from_account, to_account, amount) VALUES (%s, %s, %s)",
                (1, 2, 200.00)
            )
            
            # 扣款
            cursor.execute("UPDATE bank_accounts SET balance = balance - 200 WHERE id = 1")
            
            # 检查余额是否足够
            cursor.execute("SELECT balance FROM bank_accounts WHERE id = 1")
            balance = cursor.fetchone()[0]
            
            if balance >= 0:
                # 余额足够，继续转账
                cursor.execute("UPDATE bank_accounts SET balance = balance + 200 WHERE id = 2")
                cursor.execute("UPDATE transfer_log SET status = 'completed' WHERE id = LAST_INSERT_ID()")
                cursor.execute("COMMIT")
                logger.info("转账成功完成")
            else:
                # 余额不足，回滚事务
                cursor.execute("UPDATE transfer_log SET status = 'failed' WHERE id = LAST_INSERT_ID()")
                cursor.execute("ROLLBACK")
                logger.info("转账失败，余额不足")
            
            # 3. 查看转账结果
            cursor.execute("SELECT * FROM bank_accounts")
            accounts = cursor.fetchall()
            logger.info("账户余额:")
            for account in accounts:
                logger.info(f"  {account[1]}: {account[2]}")
            
            cursor.execute("SELECT * FROM transfer_log")
            transfers = cursor.fetchall()
            logger.info("转账日志:")
            for transfer in transfers:
                logger.info(f"  从账户{transfer[1]}到账户{transfer[2]}，金额{transfer[3]}，状态{transfer[4]}")
            
            # 4. XA事务命令示例（模拟）
            logger.info("=== XA事务命令示例（模拟） ===")
            logger.info("XA START 'xa_transaction_1';")
            logger.info("UPDATE accounts SET balance = balance - 100 WHERE id = 1;")
            logger.info("UPDATE accounts SET balance = balance + 100 WHERE id = 2;")
            logger.info("XA END 'xa_transaction_1';")
            logger.info("XA PREPARE 'xa_transaction_1';")
            logger.info("XA COMMIT 'xa_transaction_1';")
            
            cursor.close()
            return True
            
        except mysql.connector.Error as err:
            logger.error(f"演示分布式事务失败: {err}")
            return False
    
    def demonstrate_performance_monitoring(self):
        """演示性能监控"""
        if not self.connection:
            logger.error("未连接到数据库")
            return False
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # 1. 查看存储引擎性能指标
            cursor.execute("SHOW ENGINE INNODB STATUS")
            innodb_status = cursor.fetchone()
            status_text = innodb_status['Status']
            
            # 提取关键性能指标
            logger.info("=== InnoDB性能指标 ===")
            
            if "Buffer pool hit rate" in status_text:
                hit_rate_start = status_text.find("Buffer pool hit rate")
                hit_rate_end = status_text.find("\n", hit_rate_start)
                logger.info(status_text[hit_rate_start:hit_rate_end])
            
            if "Mutex spin waits" in status_text:
                mutex_start = status_text.find("Mutex spin waits")
                mutex_end = status_text.find("\n", mutex_start)
                logger.info(status_text[mutex_start:mutex_end])
            
            # 2. 查看锁等待情况
            cursor.execute("SELECT * FROM sys.innodb_lock_waits")
            lock_waits = cursor.fetchall()
            
            if lock_waits:
                logger.info("=== 当前锁等待情况 ===")
                for wait in lock_waits:
                    logger.info(f"  等待中的事务ID: {wait['waiting_trx_id']}")
                    logger.info(f"  阻塞的事务ID: {wait['blocking_trx_id']}")
                    logger.info(f"  等待时间: {wait['wait_time']}秒")
            else:
                logger.info("当前没有锁等待")
            
            # 3. 查看复制状态
            cursor.execute("SELECT * FROM performance_schema.replication_connection_status")
            replication_status = cursor.fetchall()
            
            if replication_status:
                logger.info("=== 复制连接状态 ===")
                for status in replication_status:
                    logger.info(f"  源服务器: {status['SOURCE_HOST']}:{status['SOURCE_PORT']}")
                    logger.info(f"  连接状态: {status['SERVICE_STATE']}")
            else:
                logger.info("当前没有复制连接")
            
            # 4. 查看最近的查询
            cursor.execute("""
                SELECT DIGEST_TEXT, COUNT_STAR, SUM_TIMER_WAIT/1000000000 AS total_time_sec
                FROM performance_schema.events_statements_summary_by_digest
                ORDER BY SUM_TIMER_WAIT DESC
                LIMIT 5
            """)
            
            top_queries = cursor.fetchall()
            logger.info("=== 最耗时的查询 ===")
            for query in top_queries:
                logger.info(f"  查询: {query['DIGEST_TEXT'][:50]}...")
                logger.info(f"  执行次数: {query['COUNT_STAR']}")
                logger.info(f"  总耗时: {query['total_time_sec']:.6f}秒")
            
            # 5. 查看表统计信息
            cursor.execute("SELECT * FROM sys.schema_table_statistics")
            table_stats = cursor.fetchall()
            
            if table_stats:
                logger.info("=== 表统计信息 ===")
                for stat in table_stats[:5]:  # 只显示前5个表
                    logger.info(f"  表: {stat['table_schema']}.{stat['table_name']}")
                    logger.info(f"  读取行数: {stat['rows_read']}")
                    logger.info(f"  更新行数: {stat['rows_updated']}")
                    logger.info(f"  插入行数: {stat['rows_inserted']}")
                    logger.info(f"  删除行数: {stat['rows_deleted']}")
            
            cursor.close()
            return True
            
        except mysql.connector.Error as err:
            logger.error(f"演示性能监控失败: {err}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            logger.info("已关闭数据库连接")


class HighAvailabilityDemo:
    """高可用架构演示类"""
    
    def __init__(self, storage_engine_demo):
        self.storage_engine_demo = storage_engine_demo
    
    def demonstrate_failover_simulation(self):
        """演示故障转移（模拟）"""
        if not self.storage_engine_demo.connection:
            logger.error("未连接到数据库")
            return False
            
        try:
            cursor = self.storage_engine_demo.connection.cursor()
            
            # 1. 模拟主服务器故障
            logger.info("=== 模拟主服务器故障 ===")
            
            # 创建测试表
            cursor.execute("DROP TABLE IF EXISTS failover_test")
            cursor.execute("""
                CREATE TABLE failover_test (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    data VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB
            """)
            
            # 插入数据
            cursor.execute("INSERT INTO failover_test (data) VALUES (%s)", ("主服务器数据",))
            self.storage_engine_demo.connection.commit()
            
            logger.info("在主服务器插入数据成功")
            
            # 2. 模拟从服务器接管
            logger.info("=== 模拟从服务器接管 ===")
            logger.info("检测到主服务器故障，从服务器开始接管...")
            logger.info("停止从服务器的复制进程")
            logger.info("STOP SLAVE;")
            logger.info("将从服务器提升为主服务器")
            logger.info("RESET SLAVE ALL;")
            logger.info("设置应用服务器连接到新的主服务器")
            
            # 3. 测试新主服务器
            cursor.execute("INSERT INTO failover_test (data) VALUES (%s)", ("新主服务器数据",))
            self.storage_engine_demo.connection.commit()
            
            logger.info("在新主服务器插入数据成功")
            
            # 4. 查看数据
            cursor.execute("SELECT * FROM failover_test")
            results = cursor.fetchall()
            logger.info("故障转移后的数据:")
            for result in results:
                logger.info(f"  ID: {result[0]}, 数据: {result[1]}, 时间: {result[2]}")
            
            cursor.close()
            return True
            
        except mysql.connector.Error as err:
            logger.error(f"演示故障转移失败: {err}")
            return False
    
    def demonstrate_read_write_splitting(self):
        """演示读写分离"""
        if not self.storage_engine_demo.connection:
            logger.error("未连接到数据库")
            return False
            
        try:
            cursor = self.storage_engine_demo.connection.cursor()
            
            # 1. 创建测试表
            cursor.execute("DROP TABLE IF EXISTS rw_split_test")
            cursor.execute("""
                CREATE TABLE rw_split_test (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    operation VARCHAR(20) NOT NULL,
                    server_type VARCHAR(20) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB
            """)
            
            self.storage_engine_demo.connection.commit()
            
            # 2. 模拟读写分离
            logger.info("=== 模拟读写分离 ===")
            
            # 模拟写操作（路由到主服务器）
            for i in range(5):
                cursor.execute(
                    "INSERT INTO rw_split_test (operation, server_type) VALUES (%s, %s)",
                    (f"写操作{i+1}", "主服务器")
                )
                time.sleep(0.1)
            
            self.storage_engine_demo.connection.commit()
            logger.info("模拟写操作路由到主服务器完成")
            
            # 模拟读操作（路由到从服务器）
            logger.info("模拟读操作路由到从服务器...")
            cursor.execute("SELECT COUNT(*) FROM rw_split_test WHERE server_type = '主服务器'")
            count = cursor.fetchone()[0]
            logger.info(f"从主服务器读取到 {count} 条记录")
            
            cursor.execute("SELECT * FROM rw_split_test ORDER BY created_at DESC")
            results = cursor.fetchall()
            logger.info("最新5条记录:")
            for result in results[-5:]:
                logger.info(f"  {result[0]}: {result[1]} ({result[2]}) - {result[3]}")
            
            cursor.close()
            return True
            
        except mysql.connector.Error as err:
            logger.error(f"演示读写分离失败: {err}")
            return False
    
    def demonstrate_group_replication(self):
        """演示组复制（模拟）"""
        if not self.storage_engine_demo.connection:
            logger.error("未连接到数据库")
            return False
            
        try:
            cursor = self.storage_engine_demo.connection.cursor()
            
            # 1. 检查组复制插件
            cursor.execute("SELECT * FROM information_schema.plugins WHERE plugin_name = 'group_replication'")
            plugin = cursor.fetchone()
            
            if plugin:
                logger.info("组复制插件已安装")
                logger.info(f"插件状态: {plugin[2]}")
                logger.info(f"插件版本: {plugin[3]}")
            else:
                logger.info("组复制插件未安装")
                logger.info("安装命令: INSTALL PLUGIN group_replication SONAME 'group_replication.so';")
            
            # 2. 模拟组复制配置
            logger.info("=== 模拟组复制配置 ===")
            logger.info("SET GLOBAL group_replication_bootstrap_group=ON;")
            logger.info("START GROUP_REPLICATION;")
            logger.info("SET GLOBAL group_replication_bootstrap_group=OFF;")
            
            # 3. 模拟组复制状态检查
            logger.info("=== 模拟组复制状态检查 ===")
            logger.info("SELECT * FROM performance_schema.replication_group_members;")
            logger.info("SELECT * FROM performance_schema.replication_group_member_stats;")
            
            # 4. 创建测试表
            cursor.execute("DROP TABLE IF EXISTS group_replication_test")
            cursor.execute("""
                CREATE TABLE group_replication_test (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    node_id INT NOT NULL,
                    data VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB
            """)
            
            # 5. 模拟在不同节点插入数据
            for node_id in range(1, 4):
                for i in range(3):
                    cursor.execute(
                        "INSERT INTO group_replication_test (node_id, data) VALUES (%s, %s)",
                        (node_id, f"节点{node_id}数据{i+1}")
                    )
                time.sleep(0.1)  # 模拟网络延迟
            
            self.storage_engine_demo.connection.commit()
            
            # 6. 查看数据
            cursor.execute("SELECT * FROM group_replication_test ORDER BY node_id, created_at")
            results = cursor.fetchall()
            logger.info("组复制测试数据:")
            for result in results:
                logger.info(f"  ID: {result[0]}, 节点ID: {result[1]}, 数据: {result[2]}, 时间: {result[3]}")
            
            cursor.close()
            return True
            
        except mysql.connector.Error as err:
            logger.error(f"演示组复制失败: {err}")
            return False


def main():
    """主函数"""
    # 创建存储引擎演示对象
    storage_demo = StorageEngineDemo()
    
    # 连接到数据库
    if not storage_demo.connect():
        logger.error("无法连接到数据库，退出程序")
        return
    
    try:
        # 1. 演示存储引擎
        logger.info("=== 演示不同存储引擎 ===")
        storage_demo.demonstrate_engines()
        
        # 2. 演示InnoDB特性
        logger.info("\n=== 演示InnoDB特性 ===")
        storage_demo.demonstrate_innodb_features()
        
        # 3. 演示复制设置
        logger.info("\n=== 演示复制设置 ===")
        storage_demo.demonstrate_replication_setup()
        
        # 4. 演示分片技术
        logger.info("\n=== 演示分片技术 ===")
        storage_demo.demonstrate_sharding()
        
        # 5. 演示分布式事务
        logger.info("\n=== 演示分布式事务 ===")
        storage_demo.demonstrate_distributed_transactions()
        
        # 6. 演示性能监控
        logger.info("\n=== 演示性能监控 ===")
        storage_demo.demonstrate_performance_monitoring()
        
        # 7. 演示高可用架构
        ha_demo = HighAvailabilityDemo(storage_demo)
        
        logger.info("\n=== 演示故障转移 ===")
        ha_demo.demonstrate_failover_simulation()
        
        logger.info("\n=== 演示读写分离 ===")
        ha_demo.demonstrate_read_write_splitting()
        
        logger.info("\n=== 演示组复制 ===")
        ha_demo.demonstrate_group_replication()
        
    except Exception as e:
        logger.error(f"执行过程中发生错误: {e}")
    finally:
        # 关闭连接
        storage_demo.close()


if __name__ == "__main__":
    main()