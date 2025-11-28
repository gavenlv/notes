#!/usr/bin/env python3
"""
MySQL第3章：事务处理与锁机制代码示例

这个文件包含了第3章"事务处理与锁机制"的所有代码示例，包括：
- 事务基础演示
- ACID特性验证
- 事务控制示例
- 事务隔离级别演示
- 锁机制示例
- 死锁处理示例
- 分布式事务演示

使用方法：
1. 确保MySQL服务器已安装并运行
2. 修改配置信息（主机、用户名、密码等）
3. 运行脚本：python 3-事务处理与锁机制.py

注意：在生产环境中使用时，请确保数据库凭据的安全。
"""

import mysql.connector
from mysql.connector import Error
import logging
from datetime import datetime, date, timedelta
import threading
import time
import random
import sys
import queue

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'password',  # 修改为你的MySQL密码
    'charset': 'utf8mb4',
    'autocommit': False  # 默认关闭自动提交，以便演示事务
}

class MySQLConnection:
    """MySQL连接管理类"""
    
    def __init__(self, config=None, autocommit=False):
        """初始化连接"""
        self.config = config or DB_CONFIG.copy()
        self.config['autocommit'] = autocommit
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """连接到MySQL服务器"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            self.cursor = self.connection.cursor()
            logger.info(f"成功连接到MySQL服务器: {self.config['host']}:{self.config['port']}")
            return True
        except Error as e:
            logger.error(f"连接MySQL失败: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("MySQL连接已关闭")
    
    def execute_query(self, query, params=None):
        """执行查询（SELECT）"""
        try:
            self.cursor.execute(query, params or ())
            result = self.cursor.fetchall()
            return result
        except Error as e:
            logger.error(f"执行查询失败: {e}")
            return None
    
    def execute_update(self, query, params=None):
        """执行更新（INSERT, UPDATE, DELETE）"""
        try:
            self.cursor.execute(query, params or ())
            affected_rows = self.cursor.rowcount
            if not self.config.get('autocommit', False):
                self.connection.commit()
            logger.debug(f"执行更新成功，影响行数: {affected_rows}")
            return affected_rows
        except Error as e:
            logger.error(f"执行更新失败: {e}")
            if not self.config.get('autocommit', False):
                self.connection.rollback()
            return None
    
    def start_transaction(self):
        """开始事务"""
        try:
            if self.connection:
                self.connection.start_transaction()
            logger.debug("事务已开始")
            return True
        except Error as e:
            logger.error(f"开始事务失败: {e}")
            return False
    
    def commit(self):
        """提交事务"""
        try:
            if self.connection:
                self.connection.commit()
            logger.debug("事务已提交")
            return True
        except Error as e:
            logger.error(f"提交事务失败: {e}")
            return False
    
    def rollback(self):
        """回滚事务"""
        try:
            if self.connection:
                self.connection.rollback()
            logger.debug("事务已回滚")
            return True
        except Error as e:
            logger.error(f"回滚事务失败: {e}")
            return False
    
    def set_isolation_level(self, level):
        """设置事务隔离级别"""
        try:
            query = f"SET SESSION TRANSACTION ISOLATION LEVEL {level}"
            self.cursor.execute(query)
            logger.debug(f"事务隔离级别已设置为: {level}")
            return True
        except Error as e:
            logger.error(f"设置隔离级别失败: {e}")
            return False

class TransactionDemo:
    """事务演示类"""
    
    def __init__(self, config=None):
        self.db_conn = MySQLConnection(config, autocommit=False)
        self.demo_db = "mysql_transaction_demo"
    
    def run_all_demos(self):
        """运行所有演示"""
        logger.info("开始运行MySQL事务处理与锁机制演示")
        
        if not self.db_conn.connect():
            logger.error("无法连接到MySQL服务器，停止演示")
            return
        
        try:
            # 1. 准备测试数据
            self.prepare_test_data()
            
            # 2. 事务基础演示
            self.transaction_basics_demo()
            
            # 3. ACID特性演示
            self.acid_properties_demo()
            
            # 4. 事务控制演示
            self.transaction_control_demo()
            
            # 5. 事务隔离级别演示
            self.isolation_levels_demo()
            
            # 6. 锁机制演示
            self.lock_mechanism_demo()
            
            # 7. 死锁处理演示
            self.deadlock_demo()
            
            # 8. 分布式事务演示
            self.distributed_transaction_demo()
            
            logger.info("所有演示运行完成")
            
        except Exception as e:
            logger.error(f"运行演示时发生错误: {e}")
        finally:
            self.db_conn.disconnect()
    
    def prepare_test_data(self):
        """准备测试数据"""
        logger.info("\n" + "="*50)
        logger.info("准备测试数据")
        logger.info("="*50)
        
        # 创建演示数据库
        self.db_conn.execute_update(f"CREATE DATABASE IF NOT EXISTS {self.demo_db} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        self.db_conn.execute_update(f"USE {self.demo_db}")
        
        # 创建账户表
        logger.info("创建账户表")
        self.db_conn.execute_update("""
            CREATE TABLE IF NOT EXISTS accounts (
                account_id VARCHAR(20) PRIMARY KEY,
                account_name VARCHAR(100) NOT NULL,
                balance DECIMAL(15, 2) NOT NULL DEFAULT 0,
                version INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # 创建订单表
        logger.info("创建订单表")
        self.db_conn.execute_update("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id VARCHAR(20) NOT NULL,
                amount DECIMAL(15, 2) NOT NULL,
                status VARCHAR(20) DEFAULT 'PENDING',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # 创建产品表
        logger.info("创建产品表")
        self.db_conn.execute_update("""
            CREATE TABLE IF NOT EXISTS products (
                product_id VARCHAR(20) PRIMARY KEY,
                product_name VARCHAR(100) NOT NULL,
                stock INT NOT NULL DEFAULT 0,
                price DECIMAL(15, 2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # 创建补偿记录表
        logger.info("创建补偿记录表")
        self.db_conn.execute_update("""
            CREATE TABLE IF NOT EXISTS compensation_logs (
                log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
                transaction_id VARCHAR(50) NOT NULL,
                operation_type ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
                table_name VARCHAR(100) NOT NULL,
                record_id VARCHAR(50),
                old_data TEXT,
                new_data TEXT,
                status ENUM('PENDING', 'COMPLETED', 'COMPENSATED') NOT NULL DEFAULT 'PENDING',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP NULL
            )
        """)
        
        # 清空表
        tables = ['accounts', 'orders', 'products', 'compensation_logs']
        for table in tables:
            self.db_conn.execute_update(f"DELETE FROM {table}")
        
        # 插入测试数据
        logger.info("插入测试数据")
        accounts_data = [
            ('A001', '张三', 10000.00),
            ('A002', '李四', 5000.00),
            ('A003', '王五', 8000.00)
        ]
        self.db_conn.execute_update("""
            INSERT INTO accounts (account_id, account_name, balance) 
            VALUES (%s, %s, %s)
        """, accounts_data)
        
        products_data = [
            ('P001', 'iPhone 13', 100, 5999.00),
            ('P002', 'MacBook Pro', 50, 12999.00),
            ('P003', 'AirPods', 200, 999.00)
        ]
        self.db_conn.execute_update("""
            INSERT INTO products (product_id, product_name, stock, price) 
            VALUES (%s, %s, %s, %s)
        """, products_data)
        
        logger.info("测试数据准备完成")
    
    def transaction_basics_demo(self):
        """事务基础演示"""
        logger.info("\n" + "="*50)
        logger.info("1. 事务基础演示")
        logger.info("="*50)
        
        # 1. 自动提交模式演示
        logger.info("\n1.1 自动提交模式演示")
        
        # 创建新连接，使用自动提交
        auto_conn = MySQLConnection(config=DB_CONFIG, autocommit=True)
        auto_conn.connect()
        auto_conn.execute_update(f"USE {self.demo_db}")
        
        logger.info("在自动提交模式下执行操作")
        auto_conn.execute_update("UPDATE accounts SET balance = balance + 1000 WHERE account_id = 'A001'")
        
        # 查询结果
        result = auto_conn.execute_query("SELECT account_id, balance FROM accounts WHERE account_id = 'A001'")
        if result:
            logger.info(f"账户A001余额: {result[0][1]}")
        
        auto_conn.disconnect()
        
        # 2. 手动事务模式演示
        logger.info("\n1.2 手动事务模式演示")
        
        # 开始事务
        self.db_conn.start_transaction()
        logger.info("开始事务")
        
        # 执行更新
        self.db_conn.execute_update("UPDATE accounts SET balance = balance - 1000 WHERE account_id = 'A001'")
        
        # 查询结果
        result = self.db_conn.execute_query("SELECT account_id, balance FROM accounts WHERE account_id = 'A001'")
        if result:
            logger.info(f"事务内账户A001余额: {result[0][1]}")
        
        # 提交事务
        self.db_conn.commit()
        logger.info("提交事务")
        
        # 再次查询结果
        result = self.db_conn.execute_query("SELECT account_id, balance FROM accounts WHERE account_id = 'A001'")
        if result:
            logger.info(f"提交后账户A001余额: {result[0][1]}")
    
    def acid_properties_demo(self):
        """ACID特性演示"""
        logger.info("\n" + "="*50)
        logger.info("2. ACID特性演示")
        logger.info("="*50)
        
        # 2.1 原子性演示
        logger.info("\n2.1 原子性演示")
        
        # 查询初始余额
        result = self.db_conn.execute_query("SELECT account_id, balance FROM accounts WHERE account_id IN ('A001', 'A002')")
        logger.info("转账前账户余额:")
        for row in result:
            logger.info(f"  账户{row[0]}: {row[1]}")
        
        # 开始事务
        self.db_conn.start_transaction()
        
        try:
            # 从A001扣除1000
            self.db_conn.execute_update("UPDATE accounts SET balance = balance - 1000 WHERE account_id = 'A001'")
            
            # 向A002增加1000
            self.db_conn.execute_update("UPDATE accounts SET balance = balance + 1000 WHERE account_id = 'A002'")
            
            # 查询事务内余额
            result = self.db_conn.execute_query("SELECT account_id, balance FROM accounts WHERE account_id IN ('A001', 'A002')")
            logger.info("事务内账户余额:")
            for row in result:
                logger.info(f"  账户{row[0]}: {row[1]}")
            
            # 提交事务
            self.db_conn.commit()
            logger.info("转账事务已提交")
            
            # 查询最终余额
            result = self.db_conn.execute_query("SELECT account_id, balance FROM accounts WHERE account_id IN ('A001', 'A002')")
            logger.info("转账后账户余额:")
            for row in result:
                logger.info(f"  账户{row[0]}: {row[1]}")
                
        except Exception as e:
            logger.error(f"转账失败: {e}")
            self.db_conn.rollback()
            logger.info("事务已回滚")
        
        # 2.2 一致性演示
        logger.info("\n2.2 一致性演示")
        
        # 查询总金额
        result = self.db_conn.execute_query("SELECT SUM(balance) as total_balance FROM accounts")
        if result:
            total_before = result[0][0]
            logger.info(f"转账前总金额: {total_before}")
        
        self.db_conn.start_transaction()
        
        try:
            # 执行转账
            self.db_conn.execute_update("UPDATE accounts SET balance = balance - 500 WHERE account_id = 'A001'")
            self.db_conn.execute_update("UPDATE accounts SET balance = balance + 500 WHERE account_id = 'A003'")
            
            self.db_conn.commit()
            
            # 查询总金额
            result = self.db_conn.execute_query("SELECT SUM(balance) as total_balance FROM accounts")
            if result:
                total_after = result[0][0]
                logger.info(f"转账后总金额: {total_after}")
                
                if total_before == total_after:
                    logger.info("一致性验证通过：转账前后总金额相同")
                else:
                    logger.error("一致性验证失败：转账前后总金额不同")
        
        except Exception as e:
            logger.error(f"转账失败: {e}")
            self.db_conn.rollback()
    
    def transaction_control_demo(self):
        """事务控制演示"""
        logger.info("\n" + "="*50)
        logger.info("3. 事务控制演示")
        logger.info("="*50)
        
        # 3.1 使用保存点的事务
        logger.info("\n3.1 使用保存点的事务")
        
        self.db_conn.start_transaction()
        logger.info("开始事务")
        
        # 操作1：创建订单
        self.db_conn.execute_update("INSERT INTO orders (customer_id, amount) VALUES ('C001', 500.00)")
        order_id = self.db_conn.cursor.lastrowid
        logger.info(f"创建订单，订单ID: {order_id}")
        
        # 设置保存点
        self.db_conn.execute_update("SAVEPOINT sp_order_created")
        logger.info("设置保存点: sp_order_created")
        
        # 操作2：减少库存
        self.db_conn.execute_update("UPDATE products SET stock = stock - 1 WHERE product_id = 'P001'")
        
        # 检查库存
        result = self.db_conn.execute_query("SELECT stock FROM products WHERE product_id = 'P001'")
        if result:
            stock = result[0][0]
            logger.info(f"产品P001库存: {stock}")
            
            if stock < 0:
                # 库存不足，回滚到保存点
                logger.warning("库存不足，回滚到保存点")
                self.db_conn.execute_update("ROLLBACK TO SAVEPOINT sp_order_created")
                self.db_conn.commit()
                logger.info("订单创建失败，库存不足")
            else:
                # 操作3：创建发票（模拟）
                logger.info("库存充足，继续处理")
                self.db_conn.execute_update("UPDATE orders SET status = 'COMPLETED' WHERE order_id = %s", (order_id,))
                self.db_conn.commit()
                logger.info("订单处理完成")
        
        # 查询最终状态
        result = self.db_conn.execute_query("SELECT order_id, customer_id, status FROM orders WHERE order_id = %s", (order_id,))
        if result:
            logger.info(f"最终订单状态: {result[0]}")
    
    def isolation_levels_demo(self):
        """事务隔离级别演示"""
        logger.info("\n" + "="*50)
        logger.info("4. 事务隔离级别演示")
        logger.info("="*50)
        
        # 创建独立连接模拟并发事务
        conn1 = MySQLConnection(config=DB_CONFIG, autocommit=False)
        conn2 = MySQLConnection(config=DB_CONFIG, autocommit=False)
        
        if not conn1.connect() or not conn2.connect():
            logger.error("无法建立多个连接，跳过隔离级别演示")
            return
        
        conn1.execute_update(f"USE {self.demo_db}")
        conn2.execute_update(f"USE {self.demo_db}")
        
        try:
            # 查询当前隔离级别
            result = conn1.execute_query("SELECT @@transaction_isolation")
            if result:
                current_level = result[0][0]
                logger.info(f"当前隔离级别: {current_level}")
            
            # 4.1 READ COMMITTED隔离级别演示
            logger.info("\n4.1 READ COMMITTED隔离级别演示")
            
            # 设置隔离级别
            conn1.set_isolation_level("READ COMMITTED")
            conn2.set_isolation_level("READ COMMITTED")
            
            # 重置A001余额
            conn1.execute_update("UPDATE accounts SET balance = 10000 WHERE account_id = 'A001'")
            conn1.commit()
            
            # 事务1开始
            conn1.start_transaction()
            
            # 事务2开始
            conn2.start_transaction()
            
            # 事务1读取A001余额
            result = conn1.execute_query("SELECT balance FROM accounts WHERE account_id = 'A001'")
            if result:
                balance1 = result[0][0]
                logger.info(f"事务1读取A001余额: {balance1}")
            
            # 事务2更新A001余额并提交
            conn2.execute_update("UPDATE accounts SET balance = balance - 1000 WHERE account_id = 'A001'")
            conn2.commit()
            logger.info("事务2更新A001余额并提交")
            
            # 事务1再次读取A001余额（在READ COMMITTED下会读到已提交的修改）
            result = conn1.execute_query("SELECT balance FROM accounts WHERE account_id = 'A001'")
            if result:
                balance2 = result[0][0]
                logger.info(f"事务1再次读取A001余额: {balance2}")
                logger.info(f"不可重复读演示: 第一次{balance1}, 第二次{balance2}")
            
            conn1.commit()
            
            # 4.2 REPEATABLE READ隔离级别演示
            logger.info("\n4.2 REPEATABLE READ隔离级别演示")
            
            # 重置A001余额
            conn1.execute_update("UPDATE accounts SET balance = 10000 WHERE account_id = 'A001'")
            conn1.commit()
            
            # 设置隔离级别
            conn1.set_isolation_level("REPEATABLE READ")
            conn2.set_isolation_level("REPEATABLE READ")
            
            # 事务1开始
            conn1.start_transaction()
            
            # 事务2开始
            conn2.start_transaction()
            
            # 事务1读取A001余额
            result = conn1.execute_query("SELECT balance FROM accounts WHERE account_id = 'A001'")
            if result:
                balance1 = result[0][0]
                logger.info(f"事务1读取A001余额: {balance1}")
            
            # 事务2更新A001余额并提交
            conn2.execute_update("UPDATE accounts SET balance = balance - 1000 WHERE account_id = 'A001'")
            conn2.commit()
            logger.info("事务2更新A001余额并提交")
            
            # 事务1再次读取A001余额（在REPEATABLE READ下不会读到已提交的修改）
            result = conn1.execute_query("SELECT balance FROM accounts WHERE account_id = 'A001'")
            if result:
                balance2 = result[0][0]
                logger.info(f"事务1再次读取A001余额: {balance2}")
                logger.info(f"可重复读演示: 第一次{balance1}, 第二次{balance2}")
            
            conn1.commit()
            
        except Exception as e:
            logger.error(f"隔离级别演示出错: {e}")
        finally:
            conn1.disconnect()
            conn2.disconnect()
    
    def lock_mechanism_demo(self):
        """锁机制演示"""
        logger.info("\n" + "="*50)
        logger.info("5. 锁机制演示")
        logger.info("="*50)
        
        # 5.1 共享锁与排他锁演示
        logger.info("\n5.1 共享锁与排他锁演示")
        
        # 创建两个连接
        conn1 = MySQLConnection(config=DB_CONFIG, autocommit=False)
        conn2 = MySQLConnection(config=DB_CONFIG, autocommit=False)
        
        if not conn1.connect() or not conn2.connect():
            logger.error("无法建立多个连接，跳过锁机制演示")
            return
        
        conn1.execute_update(f"USE {self.demo_db}")
        conn2.execute_update(f"USE {self.demo_db}")
        
        try:
            # 事务1开始
            conn1.start_transaction()
            
            # 事务1获取共享锁
            conn1.execute_update("SELECT * FROM accounts WHERE account_id = 'A001' LOCK IN SHARE MODE")
            logger.info("事务1获取A001的共享锁")
            
            # 事务2开始
            conn2.start_transaction()
            
            # 事务2尝试获取排他锁（应该被阻塞）
            # 使用单独的线程执行，避免主线程阻塞
            def try_get_exclusive_lock():
                try:
                    conn2.execute_update("SELECT * FROM accounts WHERE account_id = 'A001' FOR UPDATE")
                    logger.info("事务2成功获取A001的排他锁")
                except Exception as e:
                    logger.info(f"事务2获取排他锁失败或被阻塞: {e}")
                finally:
                    conn2.commit()
            
            # 启动线程
            thread = threading.Thread(target=try_get_exclusive_lock)
            thread.daemon = True
            thread.start()
            
            # 等待一段时间
            time.sleep(2)
            
            # 事务1释放锁（提交事务）
            conn1.commit()
            logger.info("事务1提交事务，释放共享锁")
            
            # 等待线程完成
            thread.join(timeout=5)
            
        except Exception as e:
            logger.error(f"锁机制演示出错: {e}")
        finally:
            conn1.disconnect()
            conn2.disconnect()
    
    def deadlock_demo(self):
        """死锁演示"""
        logger.info("\n" + "="*50)
        logger.info("6. 死锁演示")
        logger.info("="*50)
        
        # 重置账户余额
        self.db_conn.execute_update("UPDATE accounts SET balance = 10000 WHERE account_id = 'A001'")
        self.db_conn.execute_update("UPDATE accounts SET balance = 10000 WHERE account_id = 'A002'")
        self.db_conn.commit()
        
        # 创建两个连接
        conn1 = MySQLConnection(config=DB_CONFIG, autocommit=False)
        conn2 = MySQLConnection(config=DB_CONFIG, autocommit=False)
        
        if not conn1.connect() or not conn2.connect():
            logger.error("无法建立多个连接，跳过死锁演示")
            return
        
        conn1.execute_update(f"USE {self.demo_db}")
        conn2.execute_update(f"USE {self.demo_db}")
        
        # 创建结果队列
        result_queue = queue.Queue()
        
        def transaction1():
            """事务1：按A001->A002顺序操作"""
            try:
                conn1.start_transaction()
                logger.info("事务1开始")
                
                # 锁定A001
                conn1.execute_update("SELECT * FROM accounts WHERE account_id = 'A001' FOR UPDATE")
                logger.info("事务1锁定A001")
                
                time.sleep(1)  # 等待让事务2锁定A002
                
                # 尝试锁定A002（可能导致死锁）
                try:
                    conn1.execute_update("SELECT * FROM accounts WHERE account_id = 'A002' FOR UPDATE")
                    logger.info("事务1锁定A002")
                    
                    # 执行转账
                    conn1.execute_update("UPDATE accounts SET balance = balance - 1000 WHERE account_id = 'A001'")
                    conn1.execute_update("UPDATE accounts SET balance = balance + 1000 WHERE account_id = 'A002'")
                    
                    conn1.commit()
                    result_queue.put("事务1成功完成")
                except Exception as e:
                    logger.warning(f"事务1出错: {e}")
                    result_queue.put(f"事务1失败: {e}")
                    
            except Exception as e:
                logger.error(f"事务1异常: {e}")
                result_queue.put(f"事务1异常: {e}")
        
        def transaction2():
            """事务2：按A002->A001顺序操作（与事务1相反，可能导致死锁）"""
            try:
                conn2.start_transaction()
                logger.info("事务2开始")
                
                # 锁定A002
                conn2.execute_update("SELECT * FROM accounts WHERE account_id = 'A002' FOR UPDATE")
                logger.info("事务2锁定A002")
                
                time.sleep(1)  # 等待让事务1锁定A001
                
                # 尝试锁定A001（可能导致死锁）
                try:
                    conn2.execute_update("SELECT * FROM accounts WHERE account_id = 'A001' FOR UPDATE")
                    logger.info("事务2锁定A001")
                    
                    # 执行转账
                    conn2.execute_update("UPDATE accounts SET balance = balance - 500 WHERE account_id = 'A002'")
                    conn2.execute_update("UPDATE accounts SET balance = balance + 500 WHERE account_id = 'A001'")
                    
                    conn2.commit()
                    result_queue.put("事务2成功完成")
                except Exception as e:
                    logger.warning(f"事务2出错: {e}")
                    result_queue.put(f"事务2失败: {e}")
                    
            except Exception as e:
                logger.error(f"事务2异常: {e}")
                result_queue.put(f"事务2异常: {e}")
        
        try:
            # 启动两个线程，模拟并发事务
            thread1 = threading.Thread(target=transaction1)
            thread2 = threading.Thread(target=transaction2)
            
            thread1.start()
            thread2.start()
            
            # 等待两个线程完成
            thread1.join(timeout=10)
            thread2.join(timeout=10)
            
            # 获取结果
            results = []
            while not result_queue.empty():
                results.append(result_queue.get())
            
            logger.info("死锁演示结果:")
            for result in results:
                logger.info(f"  {result}")
            
            # 查询最终状态
            result = self.db_conn.execute_query("SELECT account_id, balance FROM accounts WHERE account_id IN ('A001', 'A002')")
            if result:
                logger.info("最终账户余额:")
                for row in result:
                    logger.info(f"  账户{row[0]}: {row[1]}")
                
        except Exception as e:
            logger.error(f"死锁演示出错: {e}")
        finally:
            conn1.disconnect()
            conn2.disconnect()
    
    def distributed_transaction_demo(self):
        """分布式事务演示"""
        logger.info("\n" + "="*50)
        logger.info("7. 分布式事务演示")
        logger.info("="*50)
        
        # 7.1 事务补偿机制演示
        logger.info("\n7.1 事务补偿机制演示")
        
        self.db_conn.start_transaction()
        
        try:
            # 记录原始数据
            result = self.db_conn.execute_query("SELECT stock FROM products WHERE product_id = 'P001'")
            if result:
                old_stock = result[0][0]
                logger.info(f"原始库存: {old_stock}")
            
            # 执行操作1：减少库存
            self.db_conn.execute_update("UPDATE products SET stock = stock - 1 WHERE product_id = 'P001'")
            
            # 记录补偿日志
            self.db_conn.execute_update("""
                INSERT INTO compensation_logs (
                    transaction_id, operation_type, table_name, record_id, 
                    old_data, new_data, status
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                'TXN001', 'UPDATE', 'products', 'P001',
                str({'stock': old_stock}),
                str({'stock': old_stock - 1}),
                'COMPLETED'
            ))
            
            # 模拟操作失败
            # 这里我们手动触发补偿
            logger.info("模拟操作失败，执行补偿")
            
            # 执行相反操作：恢复库存
            self.db_conn.execute_update("UPDATE products SET stock = stock + 1 WHERE product_id = 'P001'")
            
            # 更新补偿日志状态
            self.db_conn.execute_update("""
                UPDATE compensation_logs 
                SET status = 'COMPENSATED', processed_at = CURRENT_TIMESTAMP 
                WHERE transaction_id = 'TXN001'
            """)
            
            self.db_conn.commit()
            logger.info("事务补偿完成")
            
            # 查询最终库存
            result = self.db_conn.execute_query("SELECT stock FROM products WHERE product_id = 'P001'")
            if result:
                final_stock = result[0][0]
                logger.info(f"最终库存: {final_stock}")
                
                if final_stock == old_stock:
                    logger.info("补偿成功，库存已恢复")
                else:
                    logger.error("补偿失败，库存未恢复")
            
        except Exception as e:
            logger.error(f"分布式事务演示出错: {e}")
            self.db_conn.rollback()

class DeadlockPreventionDemo:
    """死锁预防演示"""
    
    def __init__(self, config=None):
        self.db_conn = MySQLConnection(config, autocommit=False)
        self.demo_db = "mysql_transaction_demo"
    
    def run_demo(self):
        """运行死锁预防演示"""
        logger.info("\n" + "="*50)
        logger.info("7.2 死锁预防演示")
        logger.info("="*50)
        
        if not self.db_conn.connect():
            logger.error("无法连接到MySQL服务器，跳过死锁预防演示")
            return
        
        self.db_conn.execute_update(f"USE {self.demo_db}")
        
        # 重置账户余额
        self.db_conn.execute_update("UPDATE accounts SET balance = 10000 WHERE account_id IN ('A001', 'A002')")
        self.db_conn.commit()
        
        # 创建结果队列
        result_queue = queue.Queue()
        
        def safe_transaction1():
            """安全的事务1：按固定顺序访问资源"""
            conn1 = MySQLConnection(config=DB_CONFIG, autocommit=False)
            try:
                conn1.connect()
                conn1.execute_update(f"USE {self.demo_db}")
                conn1.start_transaction()
                logger.info("安全事务1开始")
                
                # 按固定顺序（ID较小先访问）
                # 先访问A001（ID较小）
                conn1.execute_update("SELECT * FROM accounts WHERE account_id = 'A001' FOR UPDATE")
                logger.info("安全事务1锁定A001")
                
                time.sleep(1)  # 等待让另一个事务锁定A002
                
                # 再访问A002（ID较大）
                conn1.execute_update("SELECT * FROM accounts WHERE account_id = 'A002' FOR UPDATE")
                logger.info("安全事务1锁定A002")
                
                # 执行转账
                conn1.execute_update("UPDATE accounts SET balance = balance - 1000 WHERE account_id = 'A001'")
                conn1.execute_update("UPDATE accounts SET balance = balance + 1000 WHERE account_id = 'A002'")
                
                conn1.commit()
                result_queue.put("安全事务1成功完成")
                
            except Exception as e:
                logger.warning(f"安全事务1出错: {e}")
                result_queue.put(f"安全事务1失败: {e}")
            finally:
                conn1.disconnect()
        
        def safe_transaction2():
            """安全的事务2：按固定顺序访问资源"""
            conn2 = MySQLConnection(config=DB_CONFIG, autocommit=False)
            try:
                conn2.connect()
                conn2.execute_update(f"USE {self.demo_db}")
                conn2.start_transaction()
                logger.info("安全事务2开始")
                
                # 按固定顺序（ID较小先访问）
                # 先访问A001（ID较小）
                conn2.execute_update("SELECT * FROM accounts WHERE account_id = 'A001' FOR UPDATE")
                logger.info("安全事务2锁定A001")
                
                time.sleep(1)  # 等待让另一个事务锁定A002
                
                # 再访问A002（ID较大）
                conn2.execute_update("SELECT * FROM accounts WHERE account_id = 'A002' FOR UPDATE")
                logger.info("安全事务2锁定A002")
                
                # 执行转账
                conn2.execute_update("UPDATE accounts SET balance = balance - 500 WHERE account_id = 'A002'")
                conn2.execute_update("UPDATE accounts SET balance = balance + 500 WHERE account_id = 'A001'")
                
                conn2.commit()
                result_queue.put("安全事务2成功完成")
                
            except Exception as e:
                logger.warning(f"安全事务2出错: {e}")
                result_queue.put(f"安全事务2失败: {e}")
            finally:
                conn2.disconnect()
        
        try:
            # 启动两个线程，模拟并发事务
            thread1 = threading.Thread(target=safe_transaction1)
            thread2 = threading.Thread(target=safe_transaction2)
            
            thread1.start()
            thread2.start()
            
            # 等待两个线程完成
            thread1.join(timeout=10)
            thread2.join(timeout=10)
            
            # 获取结果
            results = []
            while not result_queue.empty():
                results.append(result_queue.get())
            
            logger.info("死锁预防演示结果:")
            for result in results:
                logger.info(f"  {result}")
            
            # 查询最终状态
            result = self.db_conn.execute_query("SELECT account_id, balance FROM accounts WHERE account_id IN ('A001', 'A002')")
            if result:
                logger.info("最终账户余额:")
                for row in result:
                    logger.info(f"  账户{row[0]}: {row[1]}")
                
        except Exception as e:
            logger.error(f"死锁预防演示出错: {e}")
        finally:
            self.db_conn.disconnect()

def main():
    """主函数"""
    logger.info("MySQL第3章：事务处理与锁机制")
    logger.info("=" * 50)
    
    # 检查MySQL连接
    try:
        conn = MySQLConnection()
        if not conn.connect():
            logger.error("无法连接到MySQL服务器，请检查配置")
            logger.error("请确保MySQL服务器已启动，并修改配置中的连接参数")
            sys.exit(1)
        conn.disconnect()
    except Error as e:
        logger.error(f"MySQL连接测试失败: {e}")
        logger.error("请确保已安装mysql-connector-python库: pip install mysql-connector-python")
        sys.exit(1)
    
    try:
        # 运行事务演示
        transaction_demo = TransactionDemo()
        transaction_demo.run_all_demos()
        
        # 运行死锁预防演示
        deadlock_demo = DeadlockPreventionDemo()
        deadlock_demo.run_demo()
        
        logger.info("所有演示运行完成")
        
    except Exception as e:
        logger.error(f"运行演示时发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()