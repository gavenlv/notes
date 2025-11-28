# PostgreSQL教程第7章：事务管理与并发控制 - Python示例

import psycopg2
import psycopg2.extras
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from contextlib import contextmanager
from typing import Optional, Dict, Any, List
import json
import random

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PostgreSQLTransactionDemo:
    """PostgreSQL事务管理和并发控制演示类"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.setup_database()
    
    @contextmanager
    def get_connection(self, autocommit: bool = False):
        """获取数据库连接的上下文管理器"""
        conn = None
        try:
            conn = psycopg2.connect(self.connection_string)
            conn.autocommit = autocommit
            yield conn
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"数据库错误: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def setup_database(self):
        """初始化数据库表结构"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # 创建测试表
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS accounts (
                        account_id SERIAL PRIMARY KEY,
                        account_number VARCHAR(20) UNIQUE NOT NULL,
                        account_holder VARCHAR(100) NOT NULL,
                        balance DECIMAL(15,2) NOT NULL DEFAULT 0.00,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        transaction_id SERIAL PRIMARY KEY,
                        from_account_id INTEGER REFERENCES accounts(account_id),
                        to_account_id INTEGER REFERENCES accounts(account_id),
                        amount DECIMAL(15,2) NOT NULL,
                        transaction_type VARCHAR(20) NOT NULL,
                        status VARCHAR(20) DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        completed_at TIMESTAMP
                    )
                """)
                
                # 创建库存表
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS products (
                        product_id SERIAL PRIMARY KEY,
                        product_name VARCHAR(100) NOT NULL,
                        stock_quantity INTEGER NOT NULL DEFAULT 0,
                        reserved_quantity INTEGER NOT NULL DEFAULT 0,
                        version INTEGER NOT NULL DEFAULT 1,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 创建订单表
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS orders (
                        order_id SERIAL PRIMARY KEY,
                        customer_id INTEGER,
                        product_id INTEGER REFERENCES products(product_id),
                        quantity INTEGER NOT NULL,
                        order_status VARCHAR(20) DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 清空并插入测试数据
                cur.execute("TRUNCATE TABLE accounts CASCADE")
                cur.execute("TRUNCATE TABLE products CASCADE")
                cur.execute("TRUNCATE TABLE transactions CASCADE")
                cur.execute("TRUNCATE TABLE orders CASCADE")
                
                # 插入账户数据
                accounts_data = [
                    ('ACC001', '张三', 10000.00),
                    ('ACC002', '李四', 8000.00),
                    ('ACC003', '王五', 12000.00),
                    ('ACC004', '赵六', 6000.00),
                    ('ACC005', '钱七', 15000.00)
                ]
                
                cur.executemany(
                    "INSERT INTO accounts (account_number, account_holder, balance) VALUES (%s, %s, %s)",
                    accounts_data
                )
                
                # 插入产品数据
                products_data = [
                    ('iPhone 14', 100, 0),
                    ('MacBook Pro', 50, 0),
                    ('iPad', 75, 0),
                    ('AirPods', 200, 0),
                    ('Apple Watch', 150, 0)
                ]
                
                cur.executemany(
                    "INSERT INTO products (product_name, stock_quantity, reserved_quantity) VALUES (%s, %s, %s)",
                    products_data
                )
                
                logger.info("数据库表结构初始化完成")

    def basic_transaction_demo(self):
        """演示基础事务操作"""
        logger.info("=== 基础事务演示 ===")
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # 开启事务
                    cur.execute("BEGIN")
                    
                    try:
                        # 查询账户余额
                        cur.execute("SELECT account_holder, balance FROM accounts WHERE account_number = %s", ('ACC001',))
                        result = cur.fetchone()
                        logger.info(f"账户余额查询: {result}")
                        
                        # 执行转账操作
                        cur.execute("UPDATE accounts SET balance = balance - 500 WHERE account_number = %s", ('ACC001',))
                        cur.execute("UPDATE accounts SET balance = balance + 500 WHERE account_number = %s", ('ACC002',))
                        
                        # 记录交易
                        cur.execute("""
                            INSERT INTO transactions (from_account_id, to_account_id, amount, transaction_type, status)
                            SELECT a1.account_id, a2.account_id, 500.00, 'transfer', 'completed'
                            FROM accounts a1, accounts a2 
                            WHERE a1.account_number = %s AND a2.account_number = %s
                        """, ('ACC001', 'ACC002'))
                        
                        # 提交事务
                        conn.commit()
                        logger.info("事务提交成功")
                        
                    except Exception as e:
                        # 回滚事务
                        conn.rollback()
                        logger.error(f"事务回滚: {e}")
                        
        except Exception as e:
            logger.error(f"基础事务演示失败: {e}")

    def savepoint_demo(self):
        """演示保存点功能"""
        logger.info("=== 保存点演示 ===")
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("BEGIN")
                    
                    try:
                        # 设置保存点
                        cur.execute("SAVEPOINT before_update")
                        
                        # 执行第一个更新
                        cur.execute("UPDATE accounts SET balance = balance - 200 WHERE account_number = %s", ('ACC003',))
                        logger.info("执行第一次更新操作")
                        
                        # 创建保存点
                        cur.execute("SAVEPOINT before_rollback")
                        
                        # 执行第二个更新
                        cur.execute("UPDATE accounts SET balance = balance + 100 WHERE account_number = %s", ('ACC004',))
                        logger.info("执行第二次更新操作")
                        
                        # 回滚到第二个保存点
                        cur.execute("ROLLBACK TO before_rollback")
                        logger.info("回滚到第二个保存点")
                        
                        # 提交第一个保存点后的操作
                        conn.commit()
                        logger.info("事务提交成功（部分操作已回滚）")
                        
                    except Exception as e:
                        conn.rollback()
                        logger.error(f"保存点演示失败: {e}")
                        
        except Exception as e:
            logger.error(f"保存点演示异常: {e}")

    def isolation_level_demo(self):
        """演示事务隔离级别"""
        logger.info("=== 事务隔离级别演示 ===")
        
        def read_repeatable_read():
            """在REPEATABLE READ级别下读取数据"""
            try:
                with self.get_connection() as conn:
                    with conn.cursor() as cur:
                        # 设置隔离级别
                        cur.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
                        cur.execute("BEGIN")
                        
                        # 第一次读取
                        cur.execute("SELECT balance FROM accounts WHERE account_number = %s", ('ACC001',))
                        first_read = cur.fetchone()[0]
                        logger.info(f"REPEATABLE READ 第一次读取: {first_read}")
                        
                        # 等待一段时间
                        time.sleep(2)
                        
                        # 第二次读取
                        cur.execute("SELECT balance FROM accounts WHERE account_number = %s", ('ACC001',))
                        second_read = cur.fetchone()[0]
                        logger.info(f"REPEATABLE READ 第二次读取: {second_read}")
                        
                        conn.commit()
                        
            except Exception as e:
                logger.error(f"REPEATABLE READ读取失败: {e}")
        
        def write_in_middle():
            """在中间执行写操作"""
            try:
                time.sleep(1)  # 等待读取开始
                
                with self.get_connection() as conn:
                    with conn.cursor() as cur:
                        # 执行更新
                        cur.execute("UPDATE accounts SET balance = balance + 1000 WHERE account_number = %s", ('ACC001',))
                        conn.commit()
                        logger.info("执行了写操作")
                        
            except Exception as e:
                logger.error(f"写操作失败: {e}")
        
        # 启动两个线程
        thread1 = threading.Thread(target=read_repeatable_read)
        thread2 = threading.Thread(target=write_in_middle)
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()

    def deadlock_simulation(self):
        """模拟死锁情况"""
        logger.info("=== 死锁模拟 ===")
        
        def transaction1():
            """事务1：先锁A再锁B"""
            try:
                with self.get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("BEGIN")
                        
                        # 先锁定账户ACC001
                        cur.execute("SELECT * FROM accounts WHERE account_number = %s FOR UPDATE", ('ACC001',))
                        logger.info("事务1: 锁定ACC001")
                        
                        time.sleep(1)  # 等待事务2先锁B
                        
                        # 尝试锁定账户ACC002
                        cur.execute("SELECT * FROM accounts WHERE account_number = %s FOR UPDATE", ('ACC002',))
                        logger.info("事务1: 锁定ACC002")
                        
                        conn.commit()
                        logger.info("事务1: 提交成功")
                        
            except psycopg2.Error as e:
                logger.error(f"事务1: {e}")
                if conn:
                    conn.rollback()
        
        def transaction2():
            """事务2：先锁B再锁A"""
            try:
                time.sleep(0.5)  # 稍微延后启动
                
                with self.get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("BEGIN")
                        
                        # 先锁定账户ACC002
                        cur.execute("SELECT * FROM accounts WHERE account_number = %s FOR UPDATE", ('ACC002',))
                        logger.info("事务2: 锁定ACC002")
                        
                        time.sleep(1)  # 等待事务1锁A
                        
                        # 尝试锁定账户ACC001
                        cur.execute("SELECT * FROM accounts WHERE account_number = %s FOR UPDATE", ('ACC001',))
                        logger.info("事务2: 锁定ACC001")
                        
                        conn.commit()
                        logger.info("事务2: 提交成功")
                        
            except psycopg2.Error as e:
                logger.error(f"事务2: {e}")
                if conn:
                    conn.rollback()
        
        # 启动两个可能死锁的事务
        thread1 = threading.Thread(target=transaction1)
        thread2 = threading.Thread(target=transaction2)
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()

    def optimistic_locking_demo(self):
        """演示乐观锁"""
        logger.info("=== 乐观锁演示 ===")
        
        def update_with_version_check(product_id: int, price_change: float):
            """使用版本检查进行乐观更新"""
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    with self.get_connection() as conn:
                        with conn.cursor() as cur:
                            # 开启事务
                            cur.execute("BEGIN")
                            
                            # 读取当前版本和价格
                            cur.execute("""
                                SELECT stock_quantity, version, price 
                                FROM products 
                                WHERE product_id = %s
                            """, (product_id,))
                            
                            result = cur.fetchone()
                            if not result:
                                logger.error(f"产品 {product_id} 不存在")
                                return
                            
                            stock_qty, current_version, current_price = result
                            new_price = current_price + price_change if current_price else (1000 + price_change)
                            
                            # 执行乐观更新
                            cur.execute("""
                                UPDATE products 
                                SET price = %s,
                                    version = version + 1,
                                    updated_at = CURRENT_TIMESTAMP
                                WHERE product_id = %s AND version = %s
                            """, (new_price, product_id, current_version))
                            
                            if cur.rowcount == 0:
                                # 版本不匹配，重试
                                retry_count += 1
                                logger.warning(f"版本冲突，重试第 {retry_count} 次")
                                conn.rollback()
                                time.sleep(0.1)
                                continue
                            
                            conn.commit()
                            logger.info(f"产品 {product_id} 价格更新成功: {new_price}")
                            return
                            
                except Exception as e:
                    logger.error(f"更新失败: {e}")
                    if 'conn' in locals():
                        conn.rollback()
                    break
            
            logger.error(f"产品 {product_id} 更新失败，已达到最大重试次数")

        # 创建带价格的列
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS price DECIMAL(10,2) DEFAULT 1000.00")
                conn.commit()
        
        # 模拟并发更新
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for i in range(6):
                future = executor.submit(update_with_version_check, 1, 100.0)
                futures.append(future)
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                except Exception as e:
                    logger.error(f"更新任务失败: {e}")

    def inventory_reservation_demo(self):
        """演示库存预订并发控制"""
        logger.info("=== 库存预订演示 ===")
        
        def reserve_inventory(customer_id: int, product_id: int, quantity: int):
            """预订库存"""
            try:
                with self.get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("BEGIN")
                        
                        # 锁定产品行
                        cur.execute("""
                            SELECT stock_quantity, reserved_quantity 
                            FROM products 
                            WHERE product_id = %s 
                            FOR UPDATE
                        """, (product_id,))
                        
                        result = cur.fetchone()
                        if not result:
                            logger.error(f"产品 {product_id} 不存在")
                            conn.rollback()
                            return False
                        
                        stock_qty, reserved_qty = result
                        available_qty = stock_qty - reserved_qty
                        
                        if available_qty < quantity:
                            logger.warning(f"客户 {customer_id}: 库存不足，可用 {available_qty}, 需要 {quantity}")
                            conn.rollback()
                            return False
                        
                        # 创建订单
                        cur.execute("""
                            INSERT INTO orders (customer_id, product_id, quantity, order_status)
                            VALUES (%s, %s, %s, 'reserved')
                        """, (customer_id, product_id, quantity))
                        
                        # 更新预订数量
                        cur.execute("""
                            UPDATE products 
                            SET reserved_quantity = reserved_quantity + %s,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE product_id = %s
                        """, (quantity, product_id))
                        
                        conn.commit()
                        logger.info(f"客户 {customer_id}: 成功预订 {quantity} 个产品 {product_id}")
                        return True
                        
            except Exception as e:
                logger.error(f"预订失败: {e}")
                if 'conn' in locals():
                    conn.rollback()
                return False
        
        # 模拟并发预订
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            # 模拟10个客户同时预订iPhone 14 (product_id=1)
            for i in range(1, 11):
                customer_id = i
                quantity = random.randint(1, 5)
                future = executor.submit(reserve_inventory, customer_id, 1, quantity)
                futures.append(future)
            
            results = []
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"预订任务失败: {e}")
            
            success_count = sum(results)
            logger.info(f"预订结果: {success_count}/10 成功")

    def money_transfer_with_locks(self):
        """演示带锁的转账操作"""
        logger.info("=== 带锁转账演示 ===")
        
        def transfer_money(from_account: str, to_account: str, amount: float, transfer_id: int):
            """执行转账操作"""
            try:
                with self.get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("BEGIN")
                        
                        # 按照一致的顺序锁定账户（避免死锁）
                        accounts = sorted([from_account, to_account])
                        
                        for account in accounts:
                            cur.execute("""
                                SELECT balance FROM accounts 
                                WHERE account_number = %s 
                                FOR UPDATE
                            """, (account,))
                        
                        # 检查余额
                        cur.execute("""
                            SELECT balance FROM accounts 
                            WHERE account_number = %s
                        """, (from_account,))
                        
                        from_balance = cur.fetchone()[0]
                        
                        if from_balance < amount:
                            logger.warning(f"转账 {transfer_id}: 余额不足")
                            conn.rollback()
                            return False
                        
                        # 执行转账
                        cur.execute("""
                            UPDATE accounts 
                            SET balance = balance - %s, 
                                updated_at = CURRENT_TIMESTAMP
                            WHERE account_number = %s
                        """, (amount, from_account))
                        
                        cur.execute("""
                            UPDATE accounts 
                            SET balance = balance + %s, 
                                updated_at = CURRENT_TIMESTAMP
                            WHERE account_number = %s
                        """, (amount, to_account))
                        
                        # 记录交易
                        cur.execute("""
                            INSERT INTO transactions (from_account_id, to_account_id, amount, transaction_type, status)
                            SELECT a1.account_id, a2.account_id, %s, 'transfer', 'completed'
                            FROM accounts a1, accounts a2 
                            WHERE a1.account_number = %s AND a2.account_number = %s
                        """, (amount, from_account, to_account))
                        
                        conn.commit()
                        logger.info(f"转账 {transfer_id}: {from_account} -> {to_account}, 金额 {amount}")
                        return True
                        
            except Exception as e:
                logger.error(f"转账 {transfer_id} 失败: {e}")
                if 'conn' in locals():
                    conn.rollback()
                return False
        
        # 模拟多个并发转账
        transfers = [
            ('ACC001', 'ACC002', 500.0, 1),
            ('ACC002', 'ACC003', 300.0, 2),
            ('ACC003', 'ACC001', 200.0, 3),
            ('ACC001', 'ACC003', 400.0, 4),
            ('ACC004', 'ACC005', 600.0, 5)
        ]
        
        with ThreadPoolExecutor(max_workers=len(transfers)) as executor:
            futures = []
            for from_acc, to_acc, amount, transfer_id in transfers:
                future = executor.submit(transfer_money, from_acc, to_acc, amount, transfer_id)
                futures.append(future)
            
            results = []
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"转账任务失败: {e}")
            
            success_count = sum(results)
            logger.info(f"转账结果: {success_count}/{len(transfers)} 成功")

    def monitor_locks(self):
        """监控锁情况"""
        logger.info("=== 锁监控 ===")
        
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    # 查询锁等待情况
                    cur.execute("""
                        SELECT 
                            blocked_locks.pid AS blocked_pid,
                            blocked_activity.usename AS blocked_user,
                            blocking_locks.pid AS blocking_pid,
                            blocking_activity.usename AS blocking_user,
                            blocked_activity.query AS blocked_query,
                            blocking_activity.query AS blocking_query
                        FROM pg_catalog.pg_locks blocked_locks
                        JOIN pg_catalog.pg_stat_activity blocked_activity 
                            ON blocked_activity.pid = blocked_locks.pid
                        JOIN pg_catalog.pg_locks blocking_locks 
                            ON blocking_locks.relation = blocked_locks.relation
                            AND blocking_locks.pid != blocked_locks.pid
                        JOIN pg_catalog.pg_stat_activity blocking_activity 
                            ON blocking_activity.pid = blocking_locks.pid
                        WHERE NOT blocked_locks.granted
                    """)
                    
                    waiters = cur.fetchall()
                    if waiters:
                        logger.info("发现锁等待:")
                        for waiter in waiters:
                            logger.info(f"  被阻塞PID: {waiter['blocked_pid']}, 阻塞PID: {waiter['blocking_pid']}")
                    else:
                        logger.info("没有发现锁等待")
                    
                    # 查询当前锁统计
                    cur.execute("""
                        SELECT 
                            locktype,
                            mode,
                            COUNT(*) as lock_count
                        FROM pg_locks
                        GROUP BY locktype, mode
                        ORDER BY lock_count DESC
                    """)
                    
                    lock_stats = cur.fetchall()
                    logger.info("锁统计:")
                    for stat in lock_stats:
                        logger.info(f"  {stat['locktype']} - {stat['mode']}: {stat['lock_count']}")
                        
        except Exception as e:
            logger.error(f"锁监控失败: {e}")

    def transaction_performance_test(self):
        """事务性能测试"""
        logger.info("=== 事务性能测试 ===")
        
        def simple_transaction():
            """简单事务"""
            try:
                with self.get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("BEGIN")
                        cur.execute("SELECT COUNT(*) FROM accounts")
                        count = cur.fetchone()[0]
                        cur.execute("COMMIT")
                        return True
            except:
                return False
        
        def update_transaction():
            """更新事务"""
            try:
                with self.get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("BEGIN")
                        cur.execute("UPDATE accounts SET balance = balance + 0.01 WHERE account_id = 1")
                        cur.execute("COMMIT")
                        return True
            except:
                return False
        
        # 测试简单事务性能
        start_time = time.time()
        simple_success = 0
        for _ in range(100):
            if simple_transaction():
                simple_success += 1
        simple_time = time.time() - start_time
        
        # 测试更新事务性能
        start_time = time.time()
        update_success = 0
        for _ in range(100):
            if update_transaction():
                update_success += 1
        update_time = time.time() - start_time
        
        logger.info(f"简单事务: {simple_success}/100 成功, 耗时 {simple_time:.2f}秒")
        logger.info(f"更新事务: {update_success}/100 成功, 耗时 {update_time:.2f}秒")
        logger.info(f"简单事务 TPS: {simple_success/simple_time:.1f}")
        logger.info(f"更新事务 TPS: {update_success/update_time:.1f}")

    def cleanup_test_data(self):
        """清理测试数据"""
        logger.info("=== 清理测试数据 ===")
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # 重置账户余额
                    balances = {
                        'ACC001': 10000.00,
                        'ACC002': 8000.00,
                        'ACC003': 12000.00,
                        'ACC004': 6000.00,
                        'ACC005': 15000.00
                    }
                    
                    for account, balance in balances.items():
                        cur.execute("""
                            UPDATE accounts 
                            SET balance = %s, updated_at = CURRENT_TIMESTAMP
                            WHERE account_number = %s
                        """, (balance, account))
                    
                    # 重置库存
                    cur.execute("""
                        UPDATE products 
                        SET stock_quantity = CASE 
                            WHEN product_name = 'iPhone 14' THEN 100
                            WHEN product_name = 'MacBook Pro' THEN 50
                            WHEN product_name = 'iPad' THEN 75
                            WHEN product_name = 'AirPods' THEN 200
                            WHEN product_name = 'Apple Watch' THEN 150
                        END,
                        reserved_quantity = 0,
                        updated_at = CURRENT_TIMESTAMP
                    """)
                    
                    # 清空交易和订单记录
                    cur.execute("TRUNCATE TABLE transactions CASCADE")
                    cur.execute("TRUNCATE TABLE orders CASCADE")
                    
                    conn.commit()
                    logger.info("测试数据清理完成")
                    
        except Exception as e:
            logger.error(f"清理测试数据失败: {e}")

    def run_all_demos(self):
        """运行所有演示"""
        logger.info("开始运行PostgreSQL事务管理和并发控制演示")
        
        demos = [
            ("基础事务", self.basic_transaction_demo),
            ("保存点", self.savepoint_demo),
            ("隔离级别", self.isolation_level_demo),
            ("死锁模拟", self.deadlock_simulation),
            ("乐观锁", self.optimistic_locking_demo),
            ("库存预订", self.inventory_reservation_demo),
            ("转账操作", self.money_transfer_with_locks),
            ("锁监控", self.monitor_locks),
            ("性能测试", self.transaction_performance_test)
        ]
        
        for name, demo_func in demos:
            logger.info(f"\n{'='*50}")
            logger.info(f"运行演示: {name}")
            logger.info(f"{'='*50}")
            
            try:
                demo_func()
                logger.info(f"演示 {name} 完成")
            except Exception as e:
                logger.error(f"演示 {name} 失败: {e}")
            
            # 清理数据以便下次测试
            if name != "锁监控":
                self.cleanup_test_data()
                time.sleep(1)  # 短暂停顿
        
        logger.info("\n所有演示完成！")

def main():
    """主函数"""
    # 连接字符串 - 请根据实际情况修改
    connection_string = "postgresql://user:password@localhost:5432/postgres"
    
    try:
        demo = PostgreSQLTransactionDemo(connection_string)
        demo.run_all_demos()
    except Exception as e:
        logger.error(f"演示运行失败: {e}")

if __name__ == "__main__":
    main()